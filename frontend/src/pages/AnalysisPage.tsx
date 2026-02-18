import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getProfile, runFullAnalysis } from '../services/api'
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
} from 'lucide-react'
import type { AnalysisResult, Profile } from '../types'
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

              {/* Target Requirements (from profile) */}
              {profile?.target_jd?.requirements && profile.target_jd.requirements.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Target Requirements
                  </h4>
                  <ul className="space-y-1.5 bg-white p-3 rounded-md border border-primary-200">
                    {profile.target_jd.requirements.map((req, i) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-primary-500 mt-0.5">•</span>
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Target Job Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Job Description
                </label>
                <textarea
                  className="input min-h-[200px] bg-white"
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

  // Derive actual chapter-to-domain mapping from learning path
  const chapters = result?.result?.learning_path?.chapters || []

  // Compute robust display values from actual data arrays
  const displayGaps = gaps.length || summary?.total_gaps_identified || 0
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

      {/* Top Gaps */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Top Skill Gaps to Address
        </h2>
        <div className="space-y-3">
          {gaps.slice(0, 5).map((gap, i) => (
            <div
              key={gap.skill_id}
              className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold">
                {i + 1}
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">{gap.skill_name}</div>
                <div className="text-sm text-gray-500">{gap.domain}</div>
              </div>
              <div className="text-sm flex items-center gap-1">
                <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded font-medium">L{gap.current_level}</span>
                <ArrowRight className="h-3 w-3 text-gray-400" />
                <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded font-medium">L{gap.target_level}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

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
      <div className="flex justify-center">
        <button
          onClick={handleViewPath}
          className="btn btn-primary flex items-center gap-2 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-shadow"
        >
          View Your Learning Path
          <ArrowRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}
