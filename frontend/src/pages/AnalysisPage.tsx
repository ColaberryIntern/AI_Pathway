import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getProfile, runFullAnalysis, parseJDProfile, parseJDSkills, getVisualization } from '../services/api'
import {
  Loader2,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Target,
  BarChart3,
  BookOpen,
  User,
  Briefcase,
  Clock,
  Sparkles,
  MapPin,
  Code,
  Users,
  Brain,
  FileText,
  Wrench,
  Award,
  ExternalLink,
  Route,
  Info,
} from 'lucide-react'
import type { AnalysisResult, Profile, Top10TargetSkill, Top10SkillGap, JourneyRoadmap, ParsedSkill } from '../types'
import ArchetypeBadge from '../components/ArchetypeBadge'
import JourneyArrow from '../components/JourneyArrow'
import { getProficiencyLevel } from '../components/ProficiencyLegend'
import DomainGrid from '../components/ontology/DomainGrid'
import AnalysisProgress from '../components/ontology/AnalysisProgress'
import UnifiedSkillsChart from '../components/UnifiedSkillsChart'
import SelfAssessment from '../components/SelfAssessment'
import { useAnalysisAnimation } from '../components/ontology/hooks/useAnalysisAnimation'

type AnalysisStep = 'jd_input' | 'skill_selection' | 'self_assessment' | 'analyzing' | 'complete' | 'error'

export default function AnalysisPage() {
  const { profileId } = useParams<{ profileId: string }>()
  const navigate = useNavigate()
  const [step, setStep] = useState<AnalysisStep>('jd_input')
  const [targetJD, setTargetJD] = useState('')
  const [targetRole, setTargetRole] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

  // JD-first flow state
  const [parsedSkills, setParsedSkills] = useState<ParsedSkill[]>([])
  const [selectedSkillIds, setSelectedSkillIds] = useState<string[]>([])
  const [selfAssessedSkills, setSelfAssessedSkills] = useState<Record<string, number>>({})
  const [isParsingJDSkills, setIsParsingJDSkills] = useState(false)
  const [jdSkillsError, setJdSkillsError] = useState<string | null>(null)
  const [detectedRole, setDetectedRole] = useState('')

  const [jdProfile, setJdProfile] = useState<{
    technical_skills: string[]
    soft_skills: string[]
    ai_requirements?: string
    summary?: string
    seniority_level?: string
    key_tools: string[]
  } | null>(null)
  const [isParsingJD, setIsParsingJD] = useState(false)
  const [jdParseError, setJdParseError] = useState<string | null>(null)

  const isCustom = profileId === 'custom'

  // Load profile if not custom
  const { data: profile } = useQuery({
    queryKey: ['profile', profileId],
    queryFn: () => getProfile(profileId!),
    enabled: !isCustom && !!profileId,
  })

  // Load custom profile from session storage
  const [customProfileData, setCustomProfileData] = useState<Partial<Profile> | null>(null)

  useEffect(() => {
    if (isCustom) {
      const customProfile = sessionStorage.getItem('customProfile')
      const storedJD = sessionStorage.getItem('targetJD')
      if (customProfile) {
        const parsed = JSON.parse(customProfile)
        setCustomProfileData(parsed)
        setTargetRole(parsed.target_role || '')
      }
      if (storedJD) {
        setTargetJD(storedJD)
      }
    } else if (profile) {
      setTargetRole(profile.target_role || '')
      // Pre-fill JD from profile if available
      if (profile.target_jd?.requirements) {
        setTargetJD(profile.target_jd.requirements.join('\n• '))
      }
    }
  }, [isCustom, profile])

  // Track when analysis started for minimum display time
  const [analysisStartTime, setAnalysisStartTime] = useState<number>(0)
  const MINIMUM_DISPLAY_TIME = 8000 // 8 seconds minimum to show the visualization
  const EXPECTED_DURATION = 60000 // typical analysis takes ~45-60 seconds
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [showAllRemaining, setShowAllRemaining] = useState(false)
  const backendDone = useRef(false)

  const analysisMutation = useMutation({
    mutationFn: runFullAnalysis,
    onSuccess: (data) => {
      backendDone.current = true
      // Persist user_id so the dashboard can resolve "/dashboard/latest"
      if (data.user_id) {
        localStorage.setItem('latestUserId', data.user_id)
      }

      // Calculate how long the analysis has been running
      const elapsed = Date.now() - analysisStartTime
      const remainingTime = Math.max(0, MINIMUM_DISPLAY_TIME - elapsed)

      // Delay showing results to ensure minimum visualization time
      setTimeout(() => {
        setResult(data)
        setStep('complete')
      }, remainingTime)
    },
    onError: () => {
      backendDone.current = true
      // Still show error after minimum time for consistency
      const elapsed = Date.now() - analysisStartTime
      const remainingTime = Math.max(0, MINIMUM_DISPLAY_TIME - elapsed)
      setTimeout(() => {
        setStep('error')
      }, remainingTime)
    },
  })

  const analysisSteps = [
    { name: 'Analyzing Profile', icon: Target },
    { name: 'Parsing Job Description', icon: BarChart3 },
    { name: 'Calculating Skill Gaps', icon: BarChart3 },
    { name: 'Generating Learning Path', icon: BookOpen },
  ]

  // Simulate step progress
  useEffect(() => {
    if (step === 'analyzing' && currentStepIndex < analysisSteps.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStepIndex((i) => i + 1)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [step, currentStepIndex])

  // Smooth progress bar animation (exponential ease-out → 95%, jumps to 100% on completion)
  useEffect(() => {
    if (step !== 'analyzing') return
    backendDone.current = false
    setAnalysisProgress(0)
    const start = Date.now()
    const interval = setInterval(() => {
      if (backendDone.current) {
        setAnalysisProgress(100)
        clearInterval(interval)
        return
      }
      const elapsed = Date.now() - start
      const progress = 95 * (1 - Math.exp(-elapsed / (EXPECTED_DURATION / 3)))
      setAnalysisProgress(Math.min(95, Math.round(progress)))
    }, 200)
    return () => clearInterval(interval)
  }, [step])

  const handleAnalyzeJD = useCallback(async (jdText: string, role: string) => {
    if (!jdText.trim() || jdText.trim().length < 50) return
    setIsParsingJD(true)
    setJdParseError(null)
    try {
      const result = await parseJDProfile({ jd_text: jdText, target_role: role })
      setJdProfile(result)
    } catch {
      setJdParseError('Could not analyze job description. You can still run the full analysis.')
    } finally {
      setIsParsingJD(false)
    }
  }, [])

  // Auto-analyze JD with debounce when text changes
  const jdDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  useEffect(() => {
    // Clear any previous parse when JD changes
    if (jdProfile) setJdProfile(null)
    if (jdParseError) setJdParseError(null)

    if (jdDebounceRef.current) clearTimeout(jdDebounceRef.current)

    if (targetJD.trim().length >= 50) {
      jdDebounceRef.current = setTimeout(() => {
        handleAnalyzeJD(targetJD, targetRole)
      }, 1500)
    }

    return () => {
      if (jdDebounceRef.current) clearTimeout(jdDebounceRef.current)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetJD])

  const handleParseJDSkills = async () => {
    if (!targetJD.trim() || targetJD.trim().length < 50) return
    setIsParsingJDSkills(true)
    setJdSkillsError(null)
    try {
      const result = await parseJDSkills({ jd_text: targetJD, target_role: targetRole })
      setParsedSkills(result.top_10_skills)
      setDetectedRole(result.target_role || targetRole)
      if (result.target_role && !targetRole) {
        setTargetRole(result.target_role)
      }
      // Pre-select all parsed skills by rank
      const allSkillIds = result.top_10_skills.map(s => s.skill_id)
      setSelectedSkillIds(allSkillIds)
      setSelfAssessedSkills({})
      setStep('skill_selection')
    } catch {
      setJdSkillsError('Failed to parse job description. Please try again.')
    } finally {
      setIsParsingJDSkills(false)
    }
  }

  const handleStartAnalysis = () => {
    setStep('analyzing')
    setCurrentStepIndex(0)
    setAnalysisStartTime(Date.now())

    const customProfile = isCustom
      ? JSON.parse(sessionStorage.getItem('customProfile') || '{}')
      : null

    analysisMutation.mutate({
      profile_id: isCustom ? undefined : profileId,
      custom_profile: isCustom ? customProfile : undefined,
      target_jd_text: targetJD,
      target_role: detectedRole || targetRole,
      skip_assessment: true,
      self_assessed_skills: Object.keys(selfAssessedSkills).length > 0 ? selfAssessedSkills : undefined,
    })
  }

  const handleViewPath = () => {
    if (result?.learning_path_id) {
      navigate(`/path/${result.learning_path_id}`)
    }
  }

  // Get the active profile (either from API or custom)
  const activeProfile = isCustom ? customProfileData : profile
  const proficiencyLevel = getProficiencyLevel(activeProfile?.ai_exposure_level)

  // Extract profile domains for personalized animation
  const profileDomains = useMemo(() => {
    if (!activeProfile) return undefined

    // Current skill domains from estimated_current_skills
    const currentDomains = [
      ...new Set(
        Object.keys(activeProfile.estimated_current_skills || {})
          .map(sid => { const p = sid.split('.'); return p.length >= 3 ? `D.${p[1]}` : null })
          .filter((d): d is string => d !== null)
      ),
    ]

    // Target gap domains from expected_skill_gaps
    const targetDomains = (activeProfile.expected_skill_gaps || [])
      .map(g => g.domain)
      .filter(Boolean)

    return { currentDomains, targetDomains }
  }, [activeProfile])

  // Animation state for domain grid - must be called before any early returns
  const {
    highlightedDomains,
    activeDomain,
    completedDomains,
    selectedDomains,
  } = useAnalysisAnimation(step === 'analyzing', profileDomains)

  if (step === 'jd_input') {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Define Your Target
          </h1>
          <p className="text-gray-600">
            {isCustom
              ? 'Review your profile and define your target destination'
              : 'Review your profile and customize your target job description'}
          </p>
        </div>

        {/* Side-by-side Journey Layout */}
        <div className="grid lg:grid-cols-[1fr,auto,1fr] gap-6 items-stretch">
          {/* Left Panel: Where You Are */}
          <div className="card bg-gray-50 border-2 border-gray-200">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
              <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center">
                <MapPin className="h-4 w-4 text-white" />
              </div>
              <h2 className="text-lg font-bold text-gray-700">Where You Are</h2>
            </div>

            {activeProfile ? (
              <div className="space-y-4">
                {/* Name and Role */}
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-xl text-gray-900">
                      {activeProfile.name}
                    </h3>
                    <p className="text-gray-600 flex items-center gap-1">
                      <Briefcase className="h-4 w-4" />
                      {activeProfile.current_role}
                    </p>
                    {activeProfile.industry && (
                      <p className="text-sm text-gray-500">{activeProfile.industry}</p>
                    )}
                  </div>
                </div>

                {/* Archetype and Stats Row */}
                <div className="flex flex-wrap items-center gap-3">
                  <ArchetypeBadge archetype={activeProfile.archetype} />
                  {activeProfile.experience_years && (
                    <span className="flex items-center gap-1 text-sm text-gray-600 bg-white px-2 py-1 rounded-md">
                      <Clock className="h-4 w-4" />
                      {activeProfile.experience_years} years experience
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-sm font-medium text-primary-700 bg-primary-50 px-2 py-1 rounded-md">
                    <Sparkles className="h-4 w-4" />
                    {proficiencyLevel} AI Proficiency
                  </span>
                  {activeProfile.technical_background && activeProfile.technical_background !== '' && (
                    <span className="flex items-center gap-1 text-sm text-gray-600 bg-white px-2 py-1 rounded-md">
                      <Code className="h-4 w-4" />
                      {activeProfile.technical_background}
                    </span>
                  )}
                </div>

                {/* Technical Skills */}
                {activeProfile.current_profile?.technical_skills &&
                  activeProfile.current_profile.technical_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Code className="h-4 w-4" />
                        Technical Skills
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {activeProfile.current_profile.technical_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="text-sm bg-white text-gray-700 px-2.5 py-1 rounded-md border border-gray-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Soft Skills */}
                {activeProfile.current_profile?.soft_skills &&
                  activeProfile.current_profile.soft_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        Soft Skills
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {activeProfile.current_profile.soft_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="text-sm bg-white text-gray-600 px-2.5 py-1 rounded-md border border-gray-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                {/* AI Experience */}
                {activeProfile.current_profile?.ai_experience && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <Brain className="h-4 w-4" />
                      AI Experience
                    </h4>
                    <p className="text-sm text-gray-600 bg-white p-2.5 rounded-md border border-gray-200">
                      {activeProfile.current_profile.ai_experience}
                    </p>
                  </div>
                )}

                {/* AI Tools Used */}
                {activeProfile.tools_used &&
                  activeProfile.tools_used.length > 0 &&
                  !(activeProfile.tools_used.length === 1 && activeProfile.tools_used[0] === 'None') && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Wrench className="h-4 w-4" />
                        AI Tools Used
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {activeProfile.tools_used.map((tool, i) => (
                          <span
                            key={i}
                            className="text-sm bg-primary-50 text-primary-700 px-2.5 py-1 rounded-md border border-primary-200"
                          >
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Profile Summary */}
                {activeProfile.current_profile?.summary && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      Summary
                    </h4>
                    <p className="text-sm text-gray-600 bg-white p-2.5 rounded-md border border-gray-200 line-clamp-4">
                      {activeProfile.current_profile.summary}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                Loading profile...
              </div>
            )}
          </div>

          {/* Center: Journey Arrow */}
          <div className="hidden lg:flex items-center justify-center">
            <JourneyArrow variant="horizontal" size="lg" />
          </div>
          <div className="lg:hidden flex justify-center">
            <JourneyArrow variant="vertical" size="lg" />
          </div>

          {/* Right Panel: Where You're Going */}
          <div className="card bg-primary-50 border-2 border-primary-200">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-primary-200">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Target className="h-4 w-4 text-white" />
              </div>
              <h2 className="text-lg font-bold text-primary-700">Where You're Going</h2>
            </div>

            <div className="space-y-4">
              {/* Target Role */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Role
                </label>
                <input
                  type="text"
                  className="input bg-white"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="e.g., AI Product Manager"
                />
              </div>

              {/* Target Job Description — immediately visible */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Job Description
                </label>
                <textarea
                  className="input min-h-[120px] bg-white"
                  value={targetJD}
                  onChange={(e) => setTargetJD(e.target.value)}
                  placeholder="Paste the full job description here. Include requirements, responsibilities, and qualifications."
                />
                <p className="text-xs text-gray-500 mt-1">
                  The more detailed the JD, the better the skill gap analysis.
                </p>
              </div>

              {/* JD Skills Error */}
              {jdSkillsError && (
                <p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200 text-center">
                  {jdSkillsError}
                </p>
              )}

              {/* Analyze JD Button — inside the panel so it's always visible */}
              <button
                onClick={handleParseJDSkills}
                disabled={!targetJD.trim() || targetJD.trim().length < 50 || isParsingJDSkills}
                className={`w-full btn flex items-center justify-center gap-2 text-lg px-8 py-4 ${
                  targetJD.trim() && targetJD.trim().length >= 50 && !isParsingJDSkills
                    ? 'btn-primary'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isParsingJDSkills ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Analyzing JD...
                  </>
                ) : (
                  <>
                    Analyze Job Description
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>

              {/* JD Parsing Loading State */}
              {isParsingJD && (
                <div className="flex items-center justify-center gap-2 py-4 bg-white rounded-md border border-primary-200">
                  <Loader2 className="h-4 w-4 text-primary-500 animate-spin" />
                  <span className="text-sm text-gray-600">Analyzing job description...</span>
                </div>
              )}

              {/* JD Parse Error */}
              {jdParseError && (
                <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded-md">
                  {jdParseError}
                </p>
              )}

              {/* Rich JD Breakdown — shown below button after JD is parsed */}
              {jdProfile && (
                <div className="space-y-3 pt-1">
                  {/* Seniority Badge */}
                  {jdProfile.seniority_level && (
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1 text-sm font-medium text-primary-700 bg-white px-2.5 py-1 rounded-md border border-primary-200">
                        <Award className="h-4 w-4" />
                        {jdProfile.seniority_level}
                      </span>
                    </div>
                  )}

                  {/* Technical Skills */}
                  {jdProfile.technical_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Code className="h-4 w-4" />
                        Technical Skills Required
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {jdProfile.technical_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="text-sm bg-white text-gray-700 px-2.5 py-1 rounded-md border border-primary-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Soft Skills */}
                  {jdProfile.soft_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        Soft Skills Required
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {jdProfile.soft_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="text-sm bg-white text-gray-600 px-2.5 py-1 rounded-md border border-primary-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key Tools & Platforms */}
                  {jdProfile.key_tools.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Wrench className="h-4 w-4" />
                        Key Tools & Platforms
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {jdProfile.key_tools.map((tool, i) => (
                          <span
                            key={i}
                            className="text-sm bg-primary-100 text-primary-700 px-2.5 py-1 rounded-md border border-primary-200"
                          >
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* AI Requirements */}
                  {jdProfile.ai_requirements && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Brain className="h-4 w-4" />
                        AI/ML Requirements
                      </h4>
                      <p className="text-sm text-gray-600 bg-white p-2.5 rounded-md border border-primary-200">
                        {jdProfile.ai_requirements}
                      </p>
                    </div>
                  )}

                  {/* Role Summary */}
                  {jdProfile.summary && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        Role Summary
                      </h4>
                      <p className="text-sm text-gray-600 bg-white p-2.5 rounded-md border border-primary-200 line-clamp-4">
                        {jdProfile.summary}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (step === 'skill_selection') {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Select Skills to Assess
          </h1>
          <p className="text-gray-600">
            We identified {parsedSkills.length} key skills from the job description.
            Select the ones most relevant to your target role.
          </p>
          {detectedRole && (
            <p className="text-sm text-primary-700 mt-1">
              Detected role: <strong>{detectedRole}</strong>
            </p>
          )}
        </div>

        <div className="space-y-3">
          {parsedSkills.map((skill) => {
            const isSelected = selectedSkillIds.includes(skill.skill_id)
            const canSelect = true

            return (
              <div
                key={skill.skill_id}
                onClick={() => {
                  if (isSelected) {
                    setSelectedSkillIds(prev => prev.filter(id => id !== skill.skill_id))
                  } else if (canSelect) {
                    setSelectedSkillIds(prev => [...prev, skill.skill_id])
                  }
                }}
                className={`card cursor-pointer transition-all duration-150 border-2 ${
                  isSelected
                    ? 'border-primary-400 bg-primary-50 shadow-md'
                    : canSelect
                      ? 'border-gray-200 bg-white hover:border-gray-300'
                      : 'border-gray-100 bg-gray-50 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Checkbox */}
                  <div className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-primary-500 border-primary-500' : 'border-gray-300'
                  }`}>
                    {isSelected && (
                      <CheckCircle className="h-4 w-4 text-white" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-gray-400">#{skill.rank}</span>
                      <h3 className="font-semibold text-gray-900">{skill.skill_name}</h3>
                      <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full border border-primary-200">
                        {skill.domain_label}
                      </span>
                      {skill.importance === 'high' && (
                        <span className="text-xs bg-red-50 text-red-700 px-2 py-0.5 rounded-full border border-red-200">
                          Critical
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 line-clamp-2">{skill.rationale}</p>
                    <div className="mt-1 text-xs text-gray-400">
                      Required: Level {skill.required_level}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex items-center justify-between">
          <button
            onClick={() => setStep('jd_input')}
            className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
          >
            Back
          </button>
          <div className="text-sm text-gray-500">
            {selectedSkillIds.length}/{parsedSkills.length} selected
          </div>
          <button
            onClick={() => {
              setSelfAssessedSkills({})
              setStep('self_assessment')
            }}
            disabled={selectedSkillIds.length === 0}
            className={`btn flex items-center gap-2 ${
              selectedSkillIds.length > 0 ? 'btn-primary' : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continue to Self-Assessment
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    )
  }

  if (step === 'self_assessment') {
    const selectedSkills = parsedSkills.filter(s => selectedSkillIds.includes(s.skill_id))
    const allAssessed = selectedSkills.every(s => selfAssessedSkills[s.skill_id] !== undefined)

    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <SelfAssessment
          skills={selectedSkills}
          assessments={selfAssessedSkills}
          onAssess={(skillId, level) => {
            setSelfAssessedSkills(prev => ({ ...prev, [skillId]: level }))
          }}
        />

        <div className="flex items-center justify-between">
          <button
            onClick={() => setStep('skill_selection')}
            className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
          >
            Back
          </button>
          <div className="text-sm text-gray-500">
            {Object.keys(selfAssessedSkills).length}/{selectedSkills.length} assessed
          </div>
          <button
            onClick={handleStartAnalysis}
            disabled={!allAssessed}
            className={`btn flex items-center gap-2 text-lg px-6 py-3 ${
              allAssessed ? 'btn-primary' : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Run Full Analysis
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    )
  }

  if (step === 'analyzing') {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 -mx-4 sm:-mx-6 lg:-mx-8 -mt-6 px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              Analyzing Your Profile
            </h1>
            <p className="text-gray-600">
              Our AI agents are exploring the skills ontology to create your personalized learning path
            </p>
          </div>

          {/* Step Progress Bar */}
          <div className="py-4">
            <AnalysisProgress currentStep={currentStepIndex} />
          </div>

          {/* Overall Progress Bar */}
          <div className="max-w-md mx-auto">
            <div className="text-xs text-gray-500 mb-1.5">Overall progress</div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-sky-400 to-indigo-500 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${analysisProgress}%` }}
              />
            </div>
          </div>

          {/* Domain Grid Visualization */}
          <div className="py-6">
            <DomainGrid
              highlightedDomains={highlightedDomains}
              activeDomain={activeDomain}
              completedDomains={completedDomains}
              selectedDomains={selectedDomains}
            />
          </div>

          {/* Current Activity Indicator */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm">
              <Loader2 className="h-4 w-4 text-sky-500 animate-spin" />
              <span className="text-sm text-gray-700">
                {currentStepIndex === 0 && 'Analyzing your profile skills...'}
                {currentStepIndex === 1 && 'Parsing job description requirements...'}
                {currentStepIndex === 2 && 'Calculating skill gaps across domains...'}
                {currentStepIndex === 3 && 'Generating your personalized learning path...'}
              </span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="max-w-2xl mx-auto text-center space-y-6 py-12">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="h-10 w-10 text-red-500" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Analysis Failed</h1>
        <p className="text-gray-600">
          Something went wrong during the analysis. Please try again.
        </p>
        <button onClick={() => setStep('jd_input')} className="btn btn-primary">
          Try Again
        </button>
      </div>
    )
  }

  // Complete state
  const summary = result?.result.summary
  const gaps = result?.result.gap_analysis.gaps || []
  const top10Target: Top10TargetSkill[] = result?.result.top_10_target_skills || []
  const top10Gaps: Top10SkillGap[] = result?.result.top_10_skill_gaps || []
  const journeyRoadmap: JourneyRoadmap | undefined = result?.result.journey_roadmap
  const fitScore: number = result?.result.fit_score ?? 0
  const executiveIntroduction: string = result?.result.executive_introduction ?? ''
  const roleAnalysis = result?.result.jd_parsing?.role_analysis
  const primaryFunction = roleAnalysis?.primary_function || ''
  const keyDomains = roleAnalysis?.key_domains || []

  // Derive actual chapter-to-domain mapping from learning path
  const chapters = result?.result?.learning_path?.chapters || []

  // Compute robust display values from actual data arrays
  const displayGaps = top10Gaps.filter(g => g.gap > 0).length || gaps.length || summary?.total_gaps_identified || 0
  const displayChapters = chapters.length || summary?.total_chapters || 0
  const displayHours =
    result?.result?.learning_path?.total_estimated_hours
    || chapters.reduce((sum: number, ch: { estimated_time_hours?: number }) => sum + (ch.estimated_time_hours || 0), 0)
    || summary?.estimated_learning_hours
    || 0
  const journeyProgressPct = journeyRoadmap && journeyRoadmap.total_gap_levels > 0
    ? Math.round((journeyRoadmap.path_closes_levels / journeyRoadmap.total_gap_levels) * 100)
    : 0
  const actualSelectedDomains = chapters
    .map((ch: { skill_id?: string; primary_skill_id?: string; chapter_number?: number }) => {
      const sid = ch.skill_id || ch.primary_skill_id || ''
      const parts = sid.split('.')
      const domainId = parts.length >= 3 ? `D.${parts[1]}` : null
      return domainId ? { domainId, chapterNum: ch.chapter_number || 0 } : null
    })
    .filter((x: { domainId: string; chapterNum: number } | null): x is { domainId: string; chapterNum: number } => x !== null)

  // Build domain label lookup for chapter phasing
  const domainLabelMap = new Map<string, string>()
  for (const g of top10Gaps) {
    if (g.domain_label) domainLabelMap.set(g.domain, g.domain_label)
  }
  for (const t of top10Target) {
    if (t.domain_label) domainLabelMap.set(t.domain, t.domain_label)
  }
  const resolveDomainLabel = (domainId: string) => domainLabelMap.get(domainId) || domainId

  // Section 5: Group chapters by domain into phases
  type ChapterEntry = { chapter_number?: number; skill_id?: string; primary_skill_id?: string; skill_name?: string; primary_skill_name?: string; title?: string; current_level?: number; target_level?: number; estimated_time_hours?: number; learning_objectives?: string[]; industry_context?: string }
  const phases = (() => {
    const groups: Array<{ domain: string; domainLabel: string; chapters: ChapterEntry[] }> = []
    for (const ch of chapters as ChapterEntry[]) {
      const sid = ch.skill_id || ch.primary_skill_id || ''
      const parts = sid.split('.')
      const domainId = parts.length >= 3 ? `D.${parts[1]}` : 'unknown'
      const last = groups[groups.length - 1]
      if (last && last.domain === domainId) {
        last.chapters.push(ch)
      } else {
        groups.push({ domain: domainId, domainLabel: resolveDomainLabel(domainId), chapters: [ch] })
      }
    }
    return groups
  })()

  // Helper to render two-row gap bars
  const renderGapBars = (currentLevel: number, targetLevel: number, compact = false) => {
    const currentPct = (currentLevel / 5) * 100
    const targetPct = (targetLevel / 5) * 100
    const h = compact ? 'h-2.5' : 'h-4'
    return (
      <div className={`space-y-${compact ? '0.5' : '1'}`}>
        <div className="flex items-center gap-2">
          <span className={`${compact ? 'text-[9px] w-8' : 'text-[10px] w-10'} font-medium text-gray-500 text-right`}>You</span>
          <div className={`flex-1 ${h} bg-gray-100 rounded overflow-hidden`}>
            {currentPct > 0 && (
              <div className={`h-full bg-sky-500 rounded transition-all duration-700 ease-out`} style={{ width: `${currentPct}%` }} />
            )}
          </div>
          <span className="text-[10px] font-bold text-sky-600 w-6">L{currentLevel}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`${compact ? 'text-[9px] w-8' : 'text-[10px] w-10'} font-medium text-gray-500 text-right`}>Target</span>
          <div className={`flex-1 ${h} bg-gray-100 rounded overflow-hidden`}>
            <div className={`h-full bg-emerald-500 rounded transition-all duration-700 ease-out`} style={{ width: `${targetPct}%` }} />
          </div>
          <span className="text-[10px] font-bold text-emerald-600 w-6">L{targetLevel}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Success Header */}
      <div className="text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="h-10 w-10 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Complete!
        </h1>
        <p className="text-gray-600">
          Your personalized AI skills assessment is ready.
        </p>
      </div>

      {/* Fit Score + Executive Introduction */}
      {fitScore > 0 && (
        <div className="card bg-gradient-to-br from-indigo-600 to-sky-600 text-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold">Role Fit Score</h2>
              <p className="text-sm text-indigo-100">
                How closely your current skills match the target role
              </p>
            </div>
            <div className="text-right">
              <div className="text-5xl font-bold">{Math.round(fitScore * 100)}%</div>
              <div className="text-xs text-indigo-200 mt-1">current match</div>
            </div>
          </div>
          <div className="h-3 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white/80 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${Math.round(fitScore * 100)}%` }}
            />
          </div>
        </div>
      )}

      {executiveIntroduction && (
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            Your Learning Journey
          </h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">
            {executiveIntroduction}
          </p>
        </div>
      )}

      {/* Section 0: Role Context Header */}
      {(summary?.target_role || primaryFunction) && (
        <div className="card bg-gradient-to-r from-indigo-50 to-sky-50 border-indigo-200">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <Briefcase className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                Your Path to: {summary?.target_role || primaryFunction}
              </h2>
              {primaryFunction && summary?.target_role && primaryFunction !== summary.target_role && (
                <p className="text-sm text-gray-600 mt-1">
                  Core Focus: {primaryFunction}
                </p>
              )}
              {keyDomains.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {keyDomains.map((domain, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full font-medium">
                      {domain}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Domain Grid — actual chapter-to-domain mapping */}
      {actualSelectedDomains.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-3 text-center">
            Your Learning Path Across the AI Skills Ontology
          </h2>
          <DomainGrid
            highlightedDomains={[]}
            activeDomain={null}
            completedDomains={actualSelectedDomains.map((d: { domainId: string }) => d.domainId)}
            selectedDomains={actualSelectedDomains}
          />
        </div>
      )}

      {/* ================================================================ */}
      {/* UNIFIED SKILLS GAP OVERVIEW                                      */}
      {/* ================================================================ */}
      {top10Gaps.length > 0 && (
        <UnifiedSkillsChart gaps={top10Gaps} />
      )}

      {/* ================================================================ */}
      {/* JOURNEY ROADMAP — Bridge gap analysis and learning path          */}
      {/* ================================================================ */}
      {journeyRoadmap && journeyRoadmap.total_gap_levels > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Route className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-gray-900">Your Journey Roadmap</h2>
            <span className="text-sm text-gray-500 ml-auto">
              Path {journeyRoadmap.path_number} of ~{journeyRoadmap.estimated_total_paths} estimated
            </span>
          </div>

          {/* Progress bar */}
          <div className="mb-5">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress toward target role</span>
              <span className="font-medium text-indigo-600">
                {journeyRoadmap.path_closes_levels} of {journeyRoadmap.total_gap_levels} gap-levels
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 rounded-full transition-all"
                style={{
                  width: `${Math.round((journeyRoadmap.path_closes_levels / journeyRoadmap.total_gap_levels) * 100)}%`,
                }}
              />
            </div>
            <div className="text-xs text-gray-400 mt-1 text-right">
              {Math.round((journeyRoadmap.path_closes_levels / journeyRoadmap.total_gap_levels) * 100)}% after this path
            </div>
          </div>

          {journeyRoadmap.total_gap_levels === journeyRoadmap.path_closes_levels ? (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 text-sm">
              <CheckCircle className="w-4 h-4 inline mr-1" />
              This path covers all your identified skill gaps!
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {/* Left: what this path covers */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  This Path Covers ({journeyRoadmap.skills_addressed.length} skills, +1 level each)
                </h3>
                <div className="space-y-2">
                  {journeyRoadmap.skills_addressed.map((s) => (
                    <div key={s.skill_id} className="flex items-center justify-between p-2 bg-indigo-50 rounded text-sm">
                      <div className="flex-1 min-w-0">
                        <span className="font-medium text-gray-800 truncate block">
                          <span className="text-indigo-500 font-mono text-[11px]">{s.skill_id}</span>{' '}
                          {s.skill_name}
                        </span>
                        <span className="text-xs text-gray-500">{s.domain_label}</span>
                      </div>
                      <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                        <span className="text-xs font-bold text-sky-600">L{s.current_level}</span>
                        <ArrowRight className="w-3 h-3 text-gray-400" />
                        <span className="text-xs font-bold text-emerald-600">L{s.after_path_level}</span>
                        <span className="text-[10px] text-gray-400 ml-1">(of L{s.required_level})</span>
                        {s.gap_remaining === 0 ? (
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-500 ml-1" />
                        ) : (
                          <span className="text-[10px] px-1 py-0.5 bg-indigo-200 text-indigo-700 rounded ml-1">+1</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right: what remains */}
              <div>
                {(() => {
                  const REMAINING_PREVIEW = 3;
                  const partial = journeyRoadmap.skills_addressed.filter(s => s.gap_remaining > 0);
                  const notStarted = journeyRoadmap.skills_remaining.filter(s => !s.partial);
                  const allRemaining = [
                    ...partial.map(s => ({ ...s, kind: 'partial' as const })),
                    ...notStarted.map(s => ({ ...s, kind: 'not_started' as const })),
                  ];
                  const totalGapLevels = partial.reduce((sum, s) => sum + s.gap_remaining, 0)
                    + notStarted.reduce((sum, s) => sum + s.gap, 0);
                  const visible = showAllRemaining ? allRemaining : allRemaining.slice(0, REMAINING_PREVIEW);
                  const hiddenCount = allRemaining.length - REMAINING_PREVIEW;

                  return (
                    <>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">
                        Remaining ({allRemaining.length} entries, {totalGapLevels} gap-levels)
                      </h3>
                      <div className="space-y-1">
                        {visible.map((s) => (
                          <div key={s.skill_id} className={`flex items-center justify-between p-1.5 rounded text-sm ${s.kind === 'partial' ? 'bg-amber-50' : 'bg-gray-50'}`}>
                            <span className="text-gray-700 truncate flex-1">
                              <span className={`font-mono text-[11px] ${s.kind === 'partial' ? 'text-amber-500' : 'text-gray-400'}`}>{s.skill_id}</span>{' '}
                              {s.skill_name}
                            </span>
                            <span className={`text-xs flex-shrink-0 ml-2 ${s.kind === 'partial' ? 'text-amber-600' : 'text-gray-500'}`}>
                              {s.kind === 'partial'
                                ? `L${s.after_path_level} → L${s.required_level} (${s.gap_remaining} more)`
                                : `L${s.current_level} → L${s.required_level} (+${s.gap})`}
                            </span>
                          </div>
                        ))}
                      </div>
                      {hiddenCount > 0 && (
                        <button
                          onClick={() => setShowAllRemaining(!showAllRemaining)}
                          className="mt-2 w-full text-xs font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 rounded py-1.5 px-3 transition-colors text-center"
                        >
                          {showAllRemaining ? 'Show fewer skills' : `Show all ${allRemaining.length} remaining skills (+${hiddenCount} more)`}
                        </button>
                      )}
                    </>
                  );
                })()}

                {/* CTA */}
                <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700 flex items-start gap-1.5">
                  <Info className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                  <span>Each path builds solid +1 level foundations. Complete this path, then generate your next one to keep progressing.</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="card text-center border-l-4 border-l-red-500">
          <div className="text-3xl font-bold text-red-600">
            {journeyRoadmap ? journeyRoadmap.skills_addressed.length : displayGaps}
          </div>
          <div className="text-gray-600 text-sm">Skills in This Path</div>
          <div className="text-gray-400 text-xs mt-1">+1 level each</div>
        </div>
        <div className="card text-center border-l-4 border-l-indigo-500">
          <div className="text-3xl font-bold text-indigo-600">
            {journeyProgressPct}%
          </div>
          <div className="text-gray-600 text-sm">Journey Progress</div>
          <div className="text-gray-400 text-xs mt-1">
            {journeyRoadmap ? `${journeyRoadmap.path_closes_levels} of ${journeyRoadmap.total_gap_levels} gap-levels` : ''}
          </div>
        </div>
        <div className="card text-center border-l-4 border-l-sky-500">
          <div className="text-3xl font-bold text-sky-600">
            {journeyRoadmap ? `~${journeyRoadmap.estimated_total_paths}` : displayChapters}
          </div>
          <div className="text-gray-600 text-sm">
            {journeyRoadmap ? 'Paths Estimated' : 'Chapters'}
          </div>
          <div className="text-gray-400 text-xs mt-1">
            {journeyRoadmap ? 'to full role readiness' : ''}
          </div>
        </div>
        <div className="card text-center border-l-4 border-l-amber-500">
          <div className="text-3xl font-bold text-amber-600">
            {Math.round(displayHours)}h
          </div>
          <div className="text-gray-600 text-sm">Estimated Time</div>
          <div className="text-gray-400 text-xs mt-1">for this path</div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* LEARNING PATH — Domain-Grouped Phases                            */}
      {/* ================================================================ */}
      {phases.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Recommended Learning Sequence
            </h2>
          </div>

          <div className="space-y-6">
            {phases.map((phase, phaseIdx) => {
              const phaseHours = phase.chapters.reduce((sum, ch) => sum + (ch.estimated_time_hours || 0), 0)
              return (
                <div key={phaseIdx}>
                  {/* Phase header */}
                  <div className="flex items-center gap-3 mb-3 pb-2 border-b border-indigo-100">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                      {phaseIdx + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-indigo-700">Phase {phaseIdx + 1}: {phase.domainLabel}</h3>
                      <p className="text-xs text-gray-500">
                        {phase.chapters.length} chapter{phase.chapters.length > 1 ? 's' : ''}
                        {phaseHours > 0 && ` · ~${Math.round(phaseHours)}h`}
                      </p>
                    </div>
                  </div>

                  {/* Chapters within phase */}
                  <div className="space-y-3 pl-4">
                    {phase.chapters.map((ch) => {
                      const current = ch.current_level ?? 0
                      const target = ch.target_level ?? 1
                      return (
                        <div key={ch.chapter_number} className="p-3 bg-gray-50 rounded-lg">
                          {/* Chapter header */}
                          <div className="flex items-center justify-between gap-3 mb-2">
                            <div className="flex items-center gap-3 min-w-0">
                              <div className="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-xs flex-shrink-0">
                                {ch.chapter_number}
                              </div>
                              <div className="min-w-0">
                                <div className="font-medium text-gray-900 text-sm truncate">{ch.title || ch.skill_name || ch.primary_skill_name}</div>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 flex-shrink-0">
                              <span className="text-[10px] font-bold text-sky-600">L{current}</span>
                              <ArrowRight className="h-3 w-3 text-gray-400" />
                              <span className="text-[10px] font-bold text-emerald-600">L{target}</span>
                              {ch.estimated_time_hours && (
                                <span className="text-[10px] text-gray-400 ml-1">{ch.estimated_time_hours}h</span>
                              )}
                            </div>
                          </div>

                          {/* Two-row bars */}
                          <div className="pl-10 mb-2">
                            {renderGapBars(current, target, true)}
                          </div>

                          {/* Learning objectives */}
                          {ch.learning_objectives && ch.learning_objectives.length > 0 && (
                            <div className="pl-10 mt-2">
                              <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">Learning Objectives</p>
                              <ul className="text-xs text-gray-600 space-y-0.5">
                                {ch.learning_objectives.slice(0, 3).map((obj, i) => (
                                  <li key={i} className="flex items-start gap-1.5">
                                    <span className="text-indigo-400 mt-0.5">•</span>
                                    <span>{obj}</span>
                                  </li>
                                ))}
                                {ch.learning_objectives.length > 3 && (
                                  <li className="text-gray-400 text-[10px]">+{ch.learning_objectives.length - 3} more</li>
                                )}
                              </ul>
                            </div>
                          )}

                          {/* Industry context */}
                          {ch.industry_context && (
                            <p className="pl-10 mt-1.5 text-[11px] text-gray-500 italic line-clamp-2">
                              {ch.industry_context}
                            </p>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-5 mt-4 pt-3 border-t border-gray-100 text-xs text-gray-600">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-sky-500" />
              <span>Your Current Level</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-emerald-500" />
              <span>Target Level Required</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {summary?.recommendations && summary.recommendations.length > 0 && (
        <div className="card bg-indigo-50 border-indigo-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recommended Next Steps
          </h2>
          <ul className="space-y-2">
            {summary.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-gray-700">
                <CheckCircle className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* CTA */}
      <div className="flex justify-center gap-4">
        <button
          onClick={handleViewPath}
          className="btn btn-primary flex items-center gap-2 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-shadow"
        >
          View Your Learning Path
          <ArrowRight className="h-5 w-5" />
        </button>
        <button
          onClick={async () => {
            if (!result?.result) return
            try {
              const html = await getVisualization(result.result as Record<string, unknown>)
              const win = window.open('', '_blank')
              if (win) {
                win.document.write(html)
                win.document.close()
              }
            } catch {
              // Silently fail — the button is a secondary action
            }
          }}
          className="btn btn-secondary flex items-center gap-2 text-lg px-6 py-4"
        >
          View Ontology Path
          <ExternalLink className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}
