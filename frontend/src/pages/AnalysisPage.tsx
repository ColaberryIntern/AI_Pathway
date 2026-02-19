import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getProfile, runFullAnalysis, parseJDProfile, getVisualization } from '../services/api'
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
} from 'lucide-react'
import type { AnalysisResult, Profile, Top10CurrentSkill, Top10TargetSkill, Top10SkillGap } from '../types'
import ArchetypeBadge from '../components/ArchetypeBadge'
import JourneyArrow from '../components/JourneyArrow'
import ProficiencyLegend, { getProficiencyLevel } from '../components/ProficiencyLegend'
import DomainGrid from '../components/ontology/DomainGrid'
import AnalysisProgress from '../components/ontology/AnalysisProgress'
import { useAnalysisAnimation } from '../components/ontology/hooks/useAnalysisAnimation'

type AnalysisStep = 'input' | 'analyzing' | 'complete' | 'error'

export default function AnalysisPage() {
  const { profileId } = useParams<{ profileId: string }>()
  const navigate = useNavigate()
  const [step, setStep] = useState<AnalysisStep>('input')
  const [targetJD, setTargetJD] = useState('')
  const [targetRole, setTargetRole] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

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

  const analysisMutation = useMutation({
    mutationFn: runFullAnalysis,
    onSuccess: (data) => {
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
      target_role: targetRole,
      skip_assessment: true,
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

  if (step === 'input') {
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

              {/* Rich JD Breakdown */}
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

              {/* Target Job Description — at bottom so skills align with left panel */}
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
            </div>
          </div>
        </div>

        {/* Proficiency Framework Legend - Always visible */}
        <ProficiencyLegend variant="static" />

        {/* Start Analysis Button */}
        <div className="flex justify-center">
          <button
            onClick={handleStartAnalysis}
            disabled={!targetJD.trim()}
            className={`btn flex items-center justify-center gap-2 text-lg px-8 py-4 ${
              targetJD.trim()
                ? 'btn-primary'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Start Analysis
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
        <button onClick={() => setStep('input')} className="btn btn-primary">
          Try Again
        </button>
      </div>
    )
  }

  // Complete state
  const summary = result?.result.summary
  const gaps = result?.result.gap_analysis.gaps || []
  const top10Current: Top10CurrentSkill[] = result?.result.top_10_current_skills || []
  const top10Target: Top10TargetSkill[] = result?.result.top_10_target_skills || []
  const top10Gaps: Top10SkillGap[] = result?.result.top_10_skill_gaps || []

  // Derive actual chapter-to-domain mapping from learning path
  const chapters = result?.result?.learning_path?.chapters || []

  // Compute robust display values from actual data arrays
  const displayGaps = chapters.length || gaps.length || summary?.total_gaps_identified || 0
  const displayChapters = chapters.length || summary?.total_chapters || 0
  const displayHours =
    result?.result?.learning_path?.total_estimated_hours
    || chapters.reduce((sum: number, ch: { estimated_time_hours?: number }) => sum + (ch.estimated_time_hours || 0), 0)
    || summary?.estimated_learning_hours
    || 0
  const actualSelectedDomains = chapters
    .map((ch: { skill_id?: string; primary_skill_id?: string; chapter_number?: number }) => {
      const sid = ch.skill_id || ch.primary_skill_id || ''
      const parts = sid.split('.')
      const domainId = parts.length >= 3 ? `D.${parts[1]}` : null
      return domainId ? { domainId, chapterNum: ch.chapter_number || 0 } : null
    })
    .filter((x: { domainId: string; chapterNum: number } | null): x is { domainId: string; chapterNum: number } => x !== null)

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="h-10 w-10 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Complete!
        </h1>
        <p className="text-gray-600">
          Your personalized learning path is ready.
        </p>
      </div>

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

      {/* Section 1 & 2: Current Skills vs Target Skills — side by side */}
      {(top10Current.length > 0 || top10Target.length > 0) && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 text-center">
            Skills Assessment
          </h2>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Left: Your Current Skills */}
            {top10Current.length > 0 && (
              <div className="card border-2 border-gray-200">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
                  <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <h3 className="font-bold text-gray-700">Your Current Skills</h3>
                  <span className="text-xs text-gray-400 ml-auto">Top 10</span>
                </div>
                <div className="space-y-2.5">
                  {top10Current.map((skill) => (
                    <div key={skill.skill_id} className="p-2.5 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="flex-shrink-0 w-5 h-5 bg-gray-200 rounded-full flex items-center justify-center text-[10px] font-bold text-gray-600">
                            {skill.rank}
                          </span>
                          <div className="min-w-0">
                            <span className="font-medium text-gray-900 text-sm block truncate">{skill.skill_name}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium">
                            {skill.domain_label || skill.domain}
                          </span>
                          <span className="text-xs px-2 py-0.5 bg-sky-100 text-sky-700 rounded font-bold">
                            L{skill.current_level}
                          </span>
                        </div>
                      </div>
                      <p className="text-[11px] text-gray-500 italic leading-relaxed pl-7">
                        {skill.rationale}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Right: Target Role Skills */}
            {top10Target.length > 0 && (
              <div className="card border-2 border-indigo-200">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-indigo-200">
                  <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                    <Target className="h-4 w-4 text-white" />
                  </div>
                  <h3 className="font-bold text-indigo-700">Target Role Skills</h3>
                  <span className="text-xs text-gray-400 ml-auto">Top 10</span>
                </div>
                <div className="space-y-2.5">
                  {top10Target.map((skill) => (
                    <div key={skill.skill_id} className="p-2.5 bg-indigo-50 rounded-lg">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="flex-shrink-0 w-5 h-5 bg-indigo-200 rounded-full flex items-center justify-center text-[10px] font-bold text-indigo-700">
                            {skill.rank}
                          </span>
                          <div className="min-w-0">
                            <span className="font-medium text-gray-900 text-sm block truncate">{skill.skill_name}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium">
                            {skill.domain_label || skill.domain}
                          </span>
                          <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-bold">
                            L{skill.required_level}
                          </span>
                          {skill.importance && (
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                              skill.importance === 'critical' ? 'bg-red-100 text-red-700' :
                              skill.importance === 'high' ? 'bg-amber-100 text-amber-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {skill.importance}
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-[11px] text-gray-500 italic leading-relaxed pl-7">
                        {skill.rationale}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Section 3: Skills Gap — delta between target and current */}
      {top10Gaps.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 className="h-5 w-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Skills Gap
            </h2>
            <span className="text-sm text-gray-500 ml-auto">Target Skills vs Your Current Level</span>
          </div>

          <div className="space-y-3">
            {top10Gaps.map((skill) => {
              const currentPct = (skill.current_level / 5) * 100
              const gapPct = (skill.gap / 5) * 100
              const remainingPct = ((5 - skill.required_level) / 5) * 100

              return (
                <div key={skill.skill_id}>
                  {/* Skill label row */}
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 rounded-full flex items-center justify-center text-[10px] font-bold text-indigo-600">
                        {skill.rank}
                      </span>
                      <span className="text-sm font-medium text-gray-700 truncate">
                        {skill.skill_name}
                      </span>
                      {skill.importance && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                          skill.importance === 'critical' ? 'bg-red-100 text-red-700' :
                          skill.importance === 'high' ? 'bg-amber-100 text-amber-700' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {skill.importance}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-xs flex-shrink-0 ml-2">
                      <span className="font-semibold text-sky-600">L{skill.current_level}</span>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                      <span className="font-semibold text-green-600">L{skill.required_level}</span>
                      {skill.gap > 0 && (
                        <span className="text-amber-600 font-bold ml-1">+{skill.gap}</span>
                      )}
                      {skill.gap === 0 && (
                        <span className="text-green-600 font-medium ml-1">met</span>
                      )}
                    </div>
                  </div>
                  {/* Bar */}
                  <div className="h-5 bg-gray-100 rounded-full overflow-hidden flex">
                    {currentPct > 0 && (
                      <div
                        className="bg-sky-500 transition-all duration-700 ease-out"
                        style={{ width: `${currentPct}%` }}
                      />
                    )}
                    {gapPct > 0 && (
                      <div
                        className="bg-amber-400 transition-all duration-700 ease-out"
                        style={{ width: `${gapPct}%` }}
                      />
                    )}
                    {remainingPct > 0 && (
                      <div
                        className="bg-gray-200 transition-all duration-700 ease-out"
                        style={{ width: `${remainingPct}%` }}
                      />
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Scale markers */}
          <div className="flex justify-between mt-2 text-[10px] text-gray-400 px-0">
            {['L0', 'L1', 'L2', 'L3', 'L4', 'L5'].map((label) => (
              <span key={label} className="w-6 text-center">{label}</span>
            ))}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-5 mt-4 pt-3 border-t border-gray-100 text-xs text-gray-600">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-sky-500" />
              <span>Current Level</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-amber-400" />
              <span>Gap to Close</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-gray-200 border border-gray-300" />
              <span>Beyond Target</span>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card text-center border-l-4 border-l-indigo-500">
          <div className="text-3xl font-bold text-indigo-600">
            {displayGaps}
          </div>
          <div className="text-gray-600">Skill Gaps Identified</div>
        </div>
        <div className="card text-center border-l-4 border-l-sky-500">
          <div className="text-3xl font-bold text-sky-600">
            {displayChapters}
          </div>
          <div className="text-gray-600">Learning Chapters</div>
        </div>
        <div className="card text-center border-l-4 border-l-amber-500">
          <div className="text-3xl font-bold text-amber-600">
            {Math.round(displayHours)}h
          </div>
          <div className="text-gray-600">Estimated Time</div>
        </div>
      </div>

      {/* Learning Path — concentrated current vs target skills */}
      {chapters.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Your Learning Path
            </h2>
            <span className="text-sm text-gray-500 ml-auto">Current → Target Skill Progression</span>
          </div>
          <div className="space-y-4">
            {chapters.map((ch: { chapter_number?: number; skill_id?: string; primary_skill_id?: string; skill_name?: string; primary_skill_name?: string; title?: string; current_level?: number; target_level?: number; estimated_time_hours?: number }) => {
              const current = ch.current_level ?? 0
              const target = ch.target_level ?? 1
              const gap = Math.max(0, target - current)
              const currentPct = (current / 5) * 100
              const gapPct = (gap / 5) * 100
              const remainingPct = ((5 - target) / 5) * 100

              return (
                <div key={ch.chapter_number} className="p-3 bg-gray-50 rounded-lg">
                  {/* Header: chapter number, title, level progression */}
                  <div className="flex items-center justify-between gap-3 mb-2">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-sm flex-shrink-0">
                        {ch.chapter_number}
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-gray-900 text-sm truncate">{ch.title || ch.skill_name}</div>
                        <div className="text-xs text-gray-500">{ch.primary_skill_name || ch.skill_name}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <span className="text-xs px-2 py-0.5 bg-sky-100 text-sky-700 rounded font-bold">L{current}</span>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-bold">L{target}</span>
                      {ch.estimated_time_hours && (
                        <span className="text-xs text-gray-400 ml-1">{ch.estimated_time_hours}h</span>
                      )}
                    </div>
                  </div>
                  {/* Gap bar */}
                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden flex">
                    {currentPct > 0 && (
                      <div className="bg-sky-500" style={{ width: `${currentPct}%` }} />
                    )}
                    {gapPct > 0 && (
                      <div className="bg-amber-400" style={{ width: `${gapPct}%` }} />
                    )}
                    {remainingPct > 0 && (
                      <div className="bg-gray-200" style={{ width: `${remainingPct}%` }} />
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-5 mt-4 pt-3 border-t border-gray-100 text-xs text-gray-600">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-sky-500" />
              <span>Current Level</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-amber-400" />
              <span>Gap to Close</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm bg-gray-200 border border-gray-300" />
              <span>Beyond Target</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {summary?.recommendations && summary.recommendations.length > 0 && (
        <div className="card bg-indigo-50 border-indigo-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recommendations
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
