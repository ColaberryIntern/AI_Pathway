import { useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getProfiles, createProfile, deleteProfile, parseResume, parseJDProfile,
  type ProfileListItem,
} from '../services/api'
import {
  User, Upload, Plus, Trash2, ChevronRight, BookOpen,
  Briefcase, Target, BarChart3, Loader2, X, FileText, Crosshair,
} from 'lucide-react'
import CurrentProfilePanel from '../components/profile/CurrentProfilePanel'
import TargetGoalPanel from '../components/profile/TargetGoalPanel'
import JourneyArrow from '../components/JourneyArrow'

export default function ProfileSelectionPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: getProfiles,
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      setDeleteConfirm(null)
    },
  })

  const handleOpenProfile = (p: ProfileListItem) => {
    if (p.has_learning_path && p.learning_path_id) {
      navigate(`/learn/${p.learning_path_id}`)
    } else if (p.has_analysis && p.goal_id) {
      navigate(`/analysis/${p.id}`)
    } else {
      navigate(`/analysis/${p.id}`)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Your Profiles</h1>
          <p className="text-gray-600 mt-1">
            Create and manage learner profiles. Each profile tracks skills, learning paths, and progress.
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          New Profile
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <CreateProfileForm
          onCreated={(id) => {
            setShowCreateForm(false)
            queryClient.invalidateQueries({ queryKey: ['profiles'] })
            navigate(`/analysis/${id}`)
          }}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {/* Profile Grid */}
      {isLoading ? (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-2 text-gray-500">
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading profiles...
          </div>
        </div>
      ) : !profiles?.length && !showCreateForm ? (
        <div className="text-center py-16 space-y-4">
          <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
            <User className="h-8 w-8 text-indigo-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900">No profiles yet</h2>
          <p className="text-gray-500">Create your first profile to get started with personalized AI skill analysis.</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn btn-primary flex items-center gap-2 mx-auto"
          >
            <Plus className="h-4 w-4" />
            Create Profile
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {profiles?.map((p) => (
            <div
              key={p.id}
              className="card hover:shadow-lg hover:-translate-y-0.5 transition-all cursor-pointer"
              onClick={() => handleOpenProfile(p)}
            >
              {/* Status badge */}
              <div className="flex items-center justify-between mb-4">
                <ProfileStatusBadge profile={p} />
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setDeleteConfirm(p.id)
                    }}
                    className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                    title="Delete profile"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Name & avatar */}
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-lg">{p.name}</h3>
                  <p className="text-sm text-gray-500">{p.industry}</p>
                </div>
              </div>

              {/* Journey: current -> target */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs uppercase tracking-wide text-gray-400 mb-1 flex items-center gap-1">
                      <Briefcase className="h-3 w-3" />
                      Current
                    </div>
                    <div className="text-sm font-medium text-gray-700 truncate">{p.current_role}</div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs uppercase tracking-wide text-gray-400 mb-1 flex items-center gap-1">
                      <Target className="h-3 w-3" />
                      Target
                    </div>
                    <div className="text-sm font-medium text-indigo-700 truncate">{p.target_role || 'Not set'}</div>
                  </div>
                </div>
              </div>

              {/* Progress (if learning path exists) */}
              {p.has_learning_path && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-gray-600">{p.lessons_completed} of {p.total_lessons} lessons</span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${p.overall_progress}%` }}
                      />
                    </div>
                  </div>
                  <BookOpen className="h-4 w-4 text-indigo-500 flex-shrink-0" />
                </div>
              )}

              {/* Action buttons */}
              {(p.has_analysis || p.has_learning_path) && (
                <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/analysis/${p.id}`)
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-2 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                  >
                    <Crosshair className="h-3.5 w-3.5" />
                    Skills Profile
                  </button>
                  {p.has_learning_path && p.learning_path_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/learn/${p.learning_path_id}`)
                      }}
                      className="flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-2 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors"
                    >
                      <BookOpen className="h-3.5 w-3.5" />
                      Learning Path
                    </button>
                  )}
                </div>
              )}

              {/* Created date */}
              <div className="text-xs text-gray-400 mt-2">
                Created {p.created_at ? new Date(p.created_at).toLocaleDateString() : 'recently'}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl p-6 max-w-sm mx-4 shadow-2xl">
            <h3 className="font-semibold text-gray-900 mb-2">Delete Profile?</h3>
            <p className="text-sm text-gray-600 mb-4">
              This will permanently delete the profile, analysis results, learning path, and all progress. This cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate(deleteConfirm)}
                disabled={deleteMutation.isPending}
                className="btn bg-red-600 text-white hover:bg-red-700"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ProfileStatusBadge({ profile }: { profile: ProfileListItem }) {
  if (profile.has_learning_path) {
    return (
      <span className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
        <BookOpen className="h-3 w-3" />
        Learning
      </span>
    )
  }
  if (profile.has_analysis) {
    return (
      <span className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
        <BarChart3 className="h-3 w-3" />
        Analyzed
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full bg-gray-50 text-gray-600 border border-gray-200">
      <FileText className="h-3 w-3" />
      New
    </span>
  )
}

function CreateProfileForm({
  onCreated,
  onCancel,
}: {
  onCreated: (id: string) => void
  onCancel: () => void
}) {
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
  const [isSaving, setIsSaving] = useState(false)
  const [isAnalyzingJD, setIsAnalyzingJD] = useState(false)
  const [jdAnalysisComplete, setJdAnalysisComplete] = useState(false)
  const [detectedRole, setDetectedRole] = useState('')
  const [jdAnalysis, setJdAnalysis] = useState<{
    target_role?: string
    technical_skills?: string[]
    soft_skills?: string[]
    ai_requirements?: string
    summary?: string
    seniority_level?: string
    key_tools?: string[]
  } | null>(null)
  const jdDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  // Auto-analyze JD after paste/typing stops (1.5s debounce)
  useEffect(() => {
    if (jdDebounceRef.current) clearTimeout(jdDebounceRef.current)
    if (targetJD.trim().length < 50) {
      setJdAnalysisComplete(false)
      setDetectedRole('')
      setJdAnalysis(null)
      return
    }
    setJdAnalysisComplete(false)
    jdDebounceRef.current = setTimeout(async () => {
      setIsAnalyzingJD(true)
      try {
        const result = await parseJDProfile({ jd_text: targetJD, target_role: customProfile.target_role })
        setJdAnalysis(result)
        // Extract detected role from backend response
        const role = result.target_role || customProfile.target_role || ''
        if (role) {
          setDetectedRole(role)
          setCustomProfile(prev => ({ ...prev, target_role: role }))
        } else {
          // Fallback: mark analysis complete even without role
          setDetectedRole('')
        }
        setJdAnalysisComplete(true)
      } catch {
        setJdAnalysisComplete(true)
      } finally {
        setIsAnalyzingJD(false)
      }
    }, 1500)
    return () => { if (jdDebounceRef.current) clearTimeout(jdDebounceRef.current) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetJD])

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

  const handleProfileChange = (updates: Partial<typeof customProfile>) => {
    setCustomProfile(prev => ({ ...prev, ...updates }))
  }

  const handleSaveAndContinue = async () => {
    if (!customProfile.name.trim() || !targetJD.trim()) return
    setIsSaving(true)
    try {
      const result = await createProfile({
        ...customProfile,
        experience_years: customProfile.experience_years ? parseInt(customProfile.experience_years) : undefined,
        target_jd_text: targetJD,
      })
      onCreated(result.id)
    } catch {
      setResumeError('Failed to save profile. Please try again.')
      setIsSaving(false)
    }
  }

  const isValid = customProfile.name.trim().length > 0 && targetJD.trim().length >= 50 && jdAnalysisComplete && !isAnalyzingJD

  return (
    <section className="card border-2 border-indigo-200 bg-indigo-50/30 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <Upload className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create New Profile</h2>
            <p className="text-sm text-gray-500">
              Upload a resume or fill in manually, then paste the target job description.
            </p>
          </div>
        </div>
        <button
          onClick={onCancel}
          className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
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

        <div className="hidden lg:flex items-center justify-center pt-16">
          <JourneyArrow variant="horizontal" size="lg" />
        </div>

        <TargetGoalPanel
          targetJD={targetJD}
          onTargetJDChange={setTargetJD}
          learningIntent={customProfile.learning_intent}
          onLearningIntentChange={(value) => handleProfileChange({ learning_intent: value })}
          isAnalyzing={isAnalyzingJD}
          analysisComplete={jdAnalysisComplete}
          detectedRole={detectedRole}
          jdAnalysis={jdAnalysis}
        />
      </div>

      {/* Save & Continue button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={handleSaveAndContinue}
          disabled={!isValid || isSaving}
          className={`btn flex items-center gap-2 text-lg px-8 py-3 ${
            isValid && !isSaving
              ? 'btn-primary'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isSaving ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              Save & Continue to Analysis
              <ChevronRight className="h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </section>
  )
}
