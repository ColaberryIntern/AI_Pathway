import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProfiles, parseResume } from '../services/api'
import { User, Upload, Briefcase, Target, ChevronRight, Clock, Sparkles, ChevronDown, FileText, X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import type { Profile } from '../types'
import ArchetypeBadge from '../components/ArchetypeBadge'
import JourneyArrow from '../components/JourneyArrow'
import { getProficiencyLevel } from '../components/ProficiencyLegend'

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

      {/* Section 1: Custom Profile Form */}
      <section className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <Upload className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create Your Custom Profile</h2>
            <p className="text-sm text-gray-500">Tell us about yourself and your goals</p>
          </div>
        </div>

        {/* Resume Upload Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all ${
            isDragOver
              ? 'border-indigo-400 bg-indigo-50'
              : resumeParsed
                ? 'border-green-300 bg-green-50'
                : resumeError
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-200 bg-gray-50 hover:border-gray-300'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleResumeUpload(file)
            }}
          />

          {isParsingResume ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-8 w-8 text-indigo-500 animate-spin" />
              <div>
                <p className="text-sm font-medium text-gray-700">Analyzing {resumeFile?.name}...</p>
                <p className="text-xs text-gray-500 mt-1">Extracting profile information from your resume</p>
              </div>
            </div>
          ) : resumeParsed && resumeFile ? (
            <div className="flex items-center justify-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
              <div className="text-left">
                <p className="text-sm font-medium text-green-700">
                  Extracted from {resumeFile.name}
                </p>
                <p className="text-xs text-gray-500 mt-0.5">Fields have been auto-filled. You can edit them below.</p>
              </div>
              <button
                onClick={clearResume}
                className="ml-2 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div
              className="flex flex-col items-center gap-3 cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                <FileText className="h-6 w-6 text-indigo-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">
                  Upload your LinkedIn Profile PDF to auto-fill
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  PDF or DOCX (max 10 MB) - drag & drop or click to browse
                </p>
              </div>
              {resumeError && (
                <div className="flex items-center gap-1.5 text-red-600 text-sm">
                  <AlertCircle className="h-4 w-4" />
                  {resumeError}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name            </label>
            <input
              type="text"
              className="input"
              value={customProfile.name}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, name: e.target.value })
              }
              placeholder="e.g., John Smith"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Role            </label>
            <input
              type="text"
              className="input"
              value={customProfile.current_role}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, current_role: e.target.value })
              }
              placeholder="e.g., Marketing Manager"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Role            </label>
            <input
              type="text"
              className="input"
              value={customProfile.target_role}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, target_role: e.target.value })
              }
              placeholder="e.g., AI Product Manager"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry            </label>
            <input
              type="text"
              className="input"
              value={customProfile.industry}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, industry: e.target.value })
              }
              placeholder="e.g., Healthcare"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Years of Experience            </label>
            <input
              type="number"
              className="input"
              value={customProfile.experience_years}
              onChange={(e) =>
                setCustomProfile({
                  ...customProfile,
                  experience_years: e.target.value,
                })
              }
              placeholder="e.g., 5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              How would you describe your current AI knowledge?
            </label>
            <select
              className="input"
              value={customProfile.ai_exposure_level}
              onChange={(e) =>
                setCustomProfile({
                  ...customProfile,
                  ai_exposure_level: e.target.value,
                })
              }
            >
              <option value="None">None</option>
              <option value="Basic">Basic</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              What is your technical or coding background?
            </label>
            <select
              className="input"
              value={customProfile.technical_background}
              onChange={(e) =>
                setCustomProfile({
                  ...customProfile,
                  technical_background: e.target.value,
                })
              }
            >
              <option value="">Select...</option>
              <option value="No coding experience">No coding experience</option>
              <option value="Basic scripting (Excel, simple automation)">Basic scripting (Excel, simple automation)</option>
              <option value="Some programming">Some programming</option>
              <option value="Professional developer">Professional developer</option>
            </select>
          </div>
        </div>

        {/* AI Tools Used - Multi-select */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Which AI tools have you used? <span className="text-gray-400 font-normal">(Select all that apply)</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              'ChatGPT / Claude / Gemini',
              'GitHub Copilot',
              'Midjourney / DALL-E',
              'OpenAI API / Anthropic API',
              'None',
            ].map((tool) => {
              const isSelected = customProfile.tools_used.includes(tool)
              const isNone = tool === 'None'
              return (
                <label
                  key={tool}
                  className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    checked={isSelected}
                    onChange={() => {
                      setCustomProfile(prev => {
                        let next: string[]
                        if (isNone) {
                          next = isSelected ? [] : ['None']
                        } else {
                          next = isSelected
                            ? prev.tools_used.filter(t => t !== tool)
                            : [...prev.tools_used.filter(t => t !== 'None'), tool]
                        }
                        return { ...prev, tools_used: next }
                      })
                    }}
                  />
                  <span className="text-sm">{tool}</span>
                </label>
              )
            })}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Learning Intent          </label>
          <textarea
            className="input min-h-[100px]"
            value={customProfile.learning_intent}
            onChange={(e) =>
              setCustomProfile({
                ...customProfile,
                learning_intent: e.target.value,
              })
            }
            placeholder="What do you want to achieve? What skills do you want to develop?"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Job Description          </label>
          <textarea
            className="input min-h-[100px]"
            value={customProfile.current_jd}
            onChange={(e) =>
              setCustomProfile({
                ...customProfile,
                current_jd: e.target.value,
              })
            }
            placeholder="Paste your current job description to help us better understand your existing skills..."
          />
          <p className="text-xs text-gray-500 mt-1">
            Helps us better assess your current skill level.
          </p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Job Description <span className="text-red-500">*</span>
          </label>
          <textarea
            className="input min-h-[150px]"
            value={targetJD}
            onChange={(e) => setTargetJD(e.target.value)}
            placeholder="Paste the job description for your target role here..."
          />
          <p className="text-xs text-gray-500 mt-1">
            The more detailed the JD, the better the skill gap analysis.
          </p>
        </div>

        <div className="flex justify-end pt-4">
          <button
            onClick={handleCustomContinue}
            disabled={!isCustomValid}
            className={`btn flex items-center gap-2 text-lg px-8 py-3 ${
              isCustomValid
                ? 'btn-primary'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continue to Analysis
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
