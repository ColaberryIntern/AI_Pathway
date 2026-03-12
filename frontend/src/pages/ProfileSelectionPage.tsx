import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProfiles, parseResume } from '../services/api'
import { User, Upload, Briefcase, Target, ChevronRight, Clock, Sparkles, ChevronDown } from 'lucide-react'
import type { Profile } from '../types'
import ArchetypeBadge from '../components/ArchetypeBadge'
import JourneyArrow from '../components/JourneyArrow'
import { getProficiencyLevel } from '../components/ProficiencyLegend'
import CurrentProfilePanel from '../components/profile/CurrentProfilePanel'
import TargetGoalPanel from '../components/profile/TargetGoalPanel'

export default function ProfileSelectionPage() {
  const navigate = useNavigate()
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null)
  const [customProfile, setCustomProfile] = useState({
    name: '',
    current_role: '',
    target_role: '',
    industry: '',
    experience_years: '',
    ai_exposure_level: 'Basic',
    learning_intent: '',
    current_jd: '',
    tools_used: [] as string[],
    technical_background: '',
    archetype: '' as string,
    current_profile: {
      technical_skills: [] as string[],
      soft_skills: [] as string[],
      ai_experience: '',
      summary: '',
    },
  })
  const [targetJD, setTargetJD] = useState('')
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [isParsingResume, setIsParsingResume] = useState(false)
  const [resumeError, setResumeError] = useState<string | null>(null)
  const [resumeParsed, setResumeParsed] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: getProfiles,
  })

  const handleSelectProfile = (profileId: string) => {
    setSelectedProfile(profileId)
  }

  const handleDoubleClick = (profileId: string) => {
    setSelectedProfile(profileId)
    navigate(`/analysis/${profileId}`)
  }

  const handleResumeUpload = useCallback(async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!ext || !['pdf', 'docx', 'doc'].includes(ext)) {
      setResumeError('Please upload a PDF or DOCX file.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setResumeError('File too large. Maximum size is 10 MB.')
      return
    }
    setResumeFile(file)
    setIsParsingResume(true)
    setResumeError(null)
    setResumeParsed(false)
    try {
      const result = await parseResume(file)
      setCustomProfile(prev => ({
        ...prev,
        ...(result.name && { name: result.name }),
        ...(result.current_role && { current_role: result.current_role }),
        ...(result.industry && { industry: result.industry }),
        ...(result.experience_years && { experience_years: String(result.experience_years) }),
        ...(result.ai_exposure_level && { ai_exposure_level: result.ai_exposure_level }),
        ...(result.archetype && { archetype: result.archetype }),
        ...(result.current_jd && { current_jd: result.current_jd }),
        current_profile: {
          technical_skills: result.technical_skills || prev.current_profile.technical_skills,
          soft_skills: result.soft_skills || prev.current_profile.soft_skills,
          ai_experience: result.ai_experience || prev.current_profile.ai_experience,
          summary: result.summary || prev.current_profile.summary,
        },
      }))
      setResumeParsed(true)
    } catch {
      setResumeError('Could not parse resume. Please fill in the fields manually.')
    } finally {
      setIsParsingResume(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleResumeUpload(file)
  }, [handleResumeUpload])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false)
  }, [])

  const clearResume = () => {
    setResumeFile(null)
    setResumeParsed(false)
    setResumeError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleCustomContinue = () => {
    if (targetJD.trim()) {
      // Store custom profile in session storage for the analysis page
      sessionStorage.setItem('customProfile', JSON.stringify(customProfile))
      sessionStorage.setItem('targetJD', targetJD)
      navigate('/analysis/custom')
    }
  }

  const handleExampleContinue = () => {
    if (selectedProfile) {
      navigate(`/analysis/${selectedProfile}`)
    }
  }

  const scrollToExamples = () => {
    document.getElementById('example-profiles')?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleProfileChange = (updates: Partial<typeof customProfile>) => {
    setCustomProfile(prev => ({ ...prev, ...updates }))
  }

  const isCustomValid = targetJD.trim().length > 0

  return (
    <div className="max-w-6xl mx-auto space-y-12">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
          Choose Your Starting Point
        </h1>
        <p className="text-gray-600 text-lg">
          Create your profile or choose from 12 example profiles
        </p>

        {/* Navigation buttons */}
        <div className="flex justify-center gap-4 pt-4">
          <button className="btn btn-primary flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Custom Profile
          </button>
          <button
            onClick={scrollToExamples}
            className="btn btn-secondary flex items-center gap-2"
          >
            <User className="h-4 w-4" />
            Example Profiles
            <ChevronDown className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Section 1: Custom Profile Form — 2-Panel Layout */}
      <section className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <Upload className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create Your Custom Profile</h2>
            <p className="text-sm text-gray-500">
              Tell us about your current background and your target job so we can analyze your skill gap.
            </p>
          </div>
        </div>

        {/* 2-Panel Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-8 items-start">
          <CurrentProfilePanel
            customProfile={customProfile}
            onProfileChange={handleProfileChange}
            resumeFile={resumeFile}
            isParsingResume={isParsingResume}
            resumeError={resumeError}
            resumeParsed={resumeParsed}
            isDragOver={isDragOver}
            fileInputRef={fileInputRef}
            onResumeUpload={handleResumeUpload}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClearResume={clearResume}
          />

          {/* Arrow — desktop only */}
          <div className="hidden lg:flex items-center justify-center pt-16">
            <JourneyArrow variant="horizontal" size="lg" />
          </div>

          <TargetGoalPanel
            targetJD={targetJD}
            onTargetJDChange={setTargetJD}
            learningIntent={customProfile.learning_intent}
            onLearningIntentChange={(value) => handleProfileChange({ learning_intent: value })}
          />
        </div>

        {/* Continue button — centered */}
        <div className="flex justify-center pt-4">
          <button
            onClick={handleCustomContinue}
            disabled={!isCustomValid}
            className={`btn flex items-center gap-2 text-lg px-8 py-3 ${
              isCustomValid
                ? 'btn-primary'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continue to Skill Gap Analysis
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </section>

      {/* Divider */}
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-gray-400 font-medium px-4">OR</span>
        <div className="flex-1 h-px bg-gray-200" />
      </div>

      {/* Section 2: Example Profiles */}
      <section id="example-profiles" className="scroll-mt-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <User className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Choose an Example Profile</h2>
            <p className="text-sm text-gray-500">Select from pre-defined profiles with realistic backgrounds</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-2 text-gray-500">
              <div className="w-5 h-5 border-2 border-gray-300 border-t-indigo-500 rounded-full animate-spin" />
              Loading profiles...
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {profiles?.map((profile: Profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
                isSelected={selectedProfile === profile.id}
                onSelect={() => handleSelectProfile(profile.id)}
                onDoubleClick={() => handleDoubleClick(profile.id)}
              />
            ))}
          </div>
        )}
      </section>

      {/* Floating Continue button when example selected */}
      {selectedProfile && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <button
            onClick={handleExampleContinue}
            className="btn btn-primary flex items-center gap-2 text-lg px-8 py-4 shadow-xl hover:shadow-2xl transition-all"
          >
            Continue to Analysis
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}

      {/* Bottom padding when floating button is visible */}
      {selectedProfile && <div className="h-24" />}
    </div>
  )
}

interface ProfileCardProps {
  profile: Profile
  isSelected: boolean
  onSelect: () => void
  onDoubleClick: () => void
}

function ProfileCard({ profile, isSelected, onSelect, onDoubleClick }: ProfileCardProps) {
  const proficiencyLevel = getProficiencyLevel(profile.ai_exposure_level)

  return (
    <div
      onClick={onSelect}
      onDoubleClick={onDoubleClick}
      className={`card cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 ${
        isSelected
          ? 'border-2 border-indigo-500 ring-2 ring-indigo-100 shadow-lg'
          : 'hover:border-gray-200'
      }`}
    >
      {/* Header row: Archetype badge, Experience, AI Level */}
      <div className="flex items-center justify-between mb-4">
        <ArchetypeBadge archetype={profile.archetype} />
        <div className="flex items-center gap-3 text-sm text-gray-500">
          {profile.experience_years && (
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {profile.experience_years} yrs
            </span>
          )}
          <span className="flex items-center gap-1 font-medium text-indigo-600">
            <Sparkles className="h-4 w-4" />
            {proficiencyLevel} AI
          </span>
        </div>
      </div>

      {/* Name */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="h-6 w-6 text-indigo-600" />
        </div>
        <h3 className="font-semibold text-gray-900 text-xl">
          {profile.name}
        </h3>
      </div>

      {/* Journey: Point A → Point B */}
      <div className="bg-gray-50 rounded-lg p-4 mb-5">
        <div className="flex items-start gap-4">
          {/* Where You Are */}
          <div className="flex-1">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center gap-1">
              <Briefcase className="h-3.5 w-3.5" />
              Where you are
            </div>
            <div className="text-base font-medium text-gray-700">
              {profile.current_role}
            </div>
          </div>

          {/* Arrow */}
          <div className="pt-6">
            <JourneyArrow variant="icon" size="lg" />
          </div>

          {/* Where You're Going */}
          <div className="flex-1">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center gap-1">
              <Target className="h-3.5 w-3.5" />
              Where you're going
            </div>
            <div className="text-base font-medium text-indigo-700">
              {profile.target_role}
            </div>
          </div>
        </div>
      </div>

      {/* Learning Intent */}
      {profile.learning_intent && (
        <p className="text-sm text-gray-600 italic mb-4 leading-relaxed">
          "{profile.learning_intent}"
        </p>
      )}

      {/* Technical Skills Tags */}
      {profile.current_profile?.technical_skills && profile.current_profile.technical_skills.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {profile.current_profile.technical_skills.map((skill, i) => (
            <span
              key={i}
              className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-md"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {/* Industry */}
      <div className="text-sm text-gray-500 border-t border-gray-100 pt-3 mt-auto">
        {profile.industry}
      </div>

      {/* Selection indicator */}
      {isSelected && (
        <div className="text-xs text-indigo-600 text-center mt-3 font-medium">
          Selected - Double-click or press Continue
        </div>
      )}
    </div>
  )
}
