import { useState, useEffect, useRef, useMemo } from 'react'
import {
  Hammer, Bot, CheckCircle2, Circle, Send, Upload, FileText, Loader2,
  AlertCircle, X, RotateCcw, Eye, EyeOff, Zap, Download, ExternalLink,
} from 'lucide-react'
import type { ImplementationTask, ImplementationGradeResult } from '../../types'
import { submitImplementationTask, simulateImplementationTask } from '../../services/api'

interface ImplementationTaskCardProps {
  task: ImplementationTask
  pathId?: string
  lessonId?: string
  lessonTitle?: string
  onSubmit?: () => void
}

interface UploadSlot {
  id: string
  heading: string
  label: string
}

const STEPS = [
  { label: 'Review Assignment', description: 'Read the task details above' },
  { label: 'Get AI Mentor Briefing', description: 'Your mentor will prepare a plan and open your workspace' },
  { label: 'Submit & Get Graded', description: 'Upload your required artifacts for AI grading' },
]

const ACCEPTED_TYPES = '.pdf,.docx,.doc,.py,.js,.ts,.jsx,.tsx,.json,.yaml,.yml,.md,.txt,.html,.css,.csv,.xml,.sql,.png,.jpg,.jpeg,.gif,.webp,.bmp'

export default function ImplementationTaskCard({
  task, pathId, lessonId, lessonTitle, onSubmit,
}: ImplementationTaskCardProps) {
  // Step 1 is always done (they're reading the card), so start at step 2
  const [completedStep, setCompletedStep] = useState(1)
  const [briefingRequested, setBriefingRequested] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  // Build required upload slots from task data
  const requiredUploads = useMemo<UploadSlot[]>(() => {
    // Use evidence_requirements if available (new lessons)
    if (task.evidence_requirements?.length) {
      return task.evidence_requirements.map((ev, i) => ({
        id: `evidence-${i}`,
        heading: ev.name,
        label: ev.description,
      }))
    }
    // Fallback for legacy lessons
    const slots: UploadSlot[] = [
      { id: 'deliverable', heading: 'Deliverable', label: task.deliverable },
    ]
    if (task.requires_architecture_explanation) {
      slots.push({
        id: 'architecture',
        heading: 'Architecture Explanation',
        label: 'Document explaining your design approach',
      })
    }
    return slots
  }, [task])

  // Per-slot file state
  const [slotFiles, setSlotFiles] = useState<Record<string, File[]>>({})
  const [grading, setGrading] = useState(false)
  const [gradeResult, setGradeResult] = useState<ImplementationGradeResult | null>(null)
  const [gradeError, setGradeError] = useState<string | null>(null)
  const [showSubmission, setShowSubmission] = useState(false)
  const slotInputRefs = useRef<Record<string, HTMLInputElement | null>>({})

  // Listen for mentor-responded to advance to step 3
  useEffect(() => {
    if (!briefingRequested) return
    const handler = () => {
      setCompletedStep(2)
      setBriefingRequested(false)
    }
    window.addEventListener('mentor-responded', handler)
    return () => window.removeEventListener('mentor-responded', handler)
  }, [briefingRequested])

  const handleGetBriefing = () => {
    if (!pathId || !lessonId) return
    setBriefingRequested(true)

    const taskMessage = [
      `I need help with this implementation task:`,
      ``,
      `Title: ${task.title}`,
      `Description: ${task.description}`,
      `Requirements:`,
      ...task.requirements.map((r, i) => `${i + 1}. ${r}`),
      `Deliverable: ${task.deliverable}`,
    ].join('\n')

    window.dispatchEvent(new CustomEvent('open-mentor', {
      detail: {
        message: taskMessage,
        mode: 'implementation-briefing',
        taskContext: {
          title: task.title,
          description: task.description,
          deliverable: task.deliverable,
          requirements: task.requirements,
          lessonTitle,
        },
      },
    }))
  }

  const handleSlotFileSelect = (slotId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const valid = files.filter(f => f.size <= 10 * 1024 * 1024) // 10MB limit
    setSlotFiles(prev => ({ ...prev, [slotId]: [...(prev[slotId] || []), ...valid] }))
    const ref = slotInputRefs.current[slotId]
    if (ref) ref.value = ''
  }

  const removeSlotFile = (slotId: string, index: number) => {
    setSlotFiles(prev => ({
      ...prev,
      [slotId]: (prev[slotId] || []).filter((_, i) => i !== index),
    }))
  }

  const handleSubmitForGrading = async () => {
    if (!pathId || !lessonId) return
    setGrading(true)
    setGradeError(null)
    try {
      const allFiles = Object.values(slotFiles).flat()
      const result = await submitImplementationTask(pathId, {
        lesson_id: lessonId,
        artifact_text: '',
        files: allFiles,
      })
      setGradeResult(result)
      if (result.passed) {
        setSubmitted(true)
        setCompletedStep(3)
        onSubmit?.()
      }
    } catch {
      setGradeError('Grading failed. Please try again.')
    } finally {
      setGrading(false)
    }
  }

  const handleResubmit = () => {
    setGradeResult(null)
    setGradeError(null)
    setSlotFiles({})
    setShowSubmission(false)
  }

  const handleSimulate = async () => {
    if (!pathId || !lessonId) return
    setGrading(true)
    setGradeError(null)
    try {
      const result = await simulateImplementationTask(pathId, { lesson_id: lessonId })
      setGradeResult(result)
      if (result.passed) {
        setSubmitted(true)
        setCompletedStep(3)
        onSubmit?.()
      }
    } catch {
      setGradeError('Simulation failed. Please try again.')
    } finally {
      setGrading(false)
    }
  }

  const allSlotsFilled = requiredUploads.every(slot => (slotFiles[slot.id]?.length ?? 0) > 0)
  const canSubmit = !grading && allSlotsFilled

  return (
    <section className="card border-2 border-purple-200 bg-gradient-to-br from-purple-50/50 to-white">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-purple-100">
          <Hammer className="h-5 w-5 text-purple-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Implementation Task</h2>
        {submitted && (
          <span className="flex items-center gap-1 text-xs text-emerald-600 ml-auto">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Complete
          </span>
        )}
      </div>

      {/* Title & Description */}
      <h3 className="font-semibold text-gray-900 text-base mb-2">{task.title}</h3>
      <p className="text-sm text-gray-700 mb-4">{task.description}</p>

      {/* Requirements */}
      {task.requirements && task.requirements.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Requirements
          </p>
          <ul className="space-y-1.5">
            {task.requirements.map((req, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="w-5 h-5 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center flex-shrink-0 font-medium text-xs">
                  {i + 1}
                </span>
                {req}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tools Needed */}
      {task.tools && task.tools.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Tools Needed
          </p>
          <div className="flex flex-wrap gap-2">
            {task.tools.map((tool, i) => {
              const Tag = tool.url ? 'a' : 'span'
              const linkProps = tool.url
                ? { href: tool.url, target: '_blank' as const, rel: 'noopener noreferrer' }
                : {}
              return (
                <Tag
                  key={i}
                  {...linkProps}
                  className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border font-medium ${
                    tool.is_free
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  } ${tool.url ? 'hover:underline cursor-pointer' : ''}`}
                >
                  {tool.url && <ExternalLink className="h-3 w-3 flex-shrink-0" />}
                  {tool.name}
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                    tool.is_free
                      ? 'bg-emerald-100 text-emerald-600'
                      : 'bg-amber-100 text-amber-600'
                  }`}>
                    {tool.is_free ? 'Free' : 'Paid'}
                  </span>
                </Tag>
              )
            })}
          </div>
        </div>
      )}

      {/* Deliverable */}
      <div className="bg-purple-50 rounded-lg p-3 mb-6 border border-purple-100">
        <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider mb-1">
          Deliverable
        </p>
        <p className="text-sm text-gray-700">{task.deliverable}</p>
      </div>

      {/* 3-Step Stepper */}
      {pathId && lessonId && (
        <div className="border-t border-purple-100 pt-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Your Workflow
          </p>
          <div className="space-y-3">
            {STEPS.map((step, i) => {
              const stepNum = i + 1
              const isComplete = completedStep >= stepNum
              const isActive = completedStep === stepNum - 1 || (stepNum === 2 && briefingRequested)

              return (
                <div key={stepNum}>
                  <div className="flex items-start gap-3">
                    {/* Step indicator */}
                    <div className="flex flex-col items-center">
                      {isComplete ? (
                        <CheckCircle2 className="h-6 w-6 text-emerald-500 flex-shrink-0" />
                      ) : isActive ? (
                        <div className="h-6 w-6 rounded-full border-2 border-purple-500 bg-purple-50 flex items-center justify-center flex-shrink-0">
                          <span className="text-xs font-bold text-purple-600">{stepNum}</span>
                        </div>
                      ) : (
                        <Circle className="h-6 w-6 text-gray-300 flex-shrink-0" />
                      )}
                      {/* Connector line */}
                      {stepNum < STEPS.length && (
                        <div className={`w-0.5 h-4 mt-1 ${isComplete ? 'bg-emerald-300' : 'bg-gray-200'}`} />
                      )}
                    </div>

                    {/* Step content */}
                    <div className="flex-1 pb-1">
                      <div className="flex items-center gap-3">
                        <span className={`text-sm font-semibold ${
                          isComplete ? 'text-emerald-700' : isActive ? 'text-gray-900' : 'text-gray-400'
                        }`}>
                          {step.label}
                        </span>

                        {/* Step 2: Briefing button */}
                        {stepNum === 2 && isActive && !briefingRequested && (
                          <button
                            onClick={handleGetBriefing}
                            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-sm"
                          >
                            <Bot className="h-3.5 w-3.5" />
                            Ask AI Mentor
                          </button>
                        )}

                        {/* Step 2: Waiting for briefing */}
                        {stepNum === 2 && briefingRequested && (
                          <span className="text-xs text-purple-600 font-medium animate-pulse">
                            Mentor is preparing your briefing...
                          </span>
                        )}
                      </div>

                      {/* Description — only for non-complete steps */}
                      {!isComplete && (
                        <p className={`text-xs mt-0.5 ${isActive ? 'text-gray-500' : 'text-gray-300'}`}>
                          {step.description}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Step 3: Named upload slots (renders below the step header) */}
                  {stepNum === 3 && isActive && !submitted && !gradeResult && (
                    <div className="ml-9 mt-3 space-y-4">
                      {requiredUploads.map(slot => {
                        const files = slotFiles[slot.id] || []
                        const filled = files.length > 0

                        return (
                          <div key={slot.id} className={`rounded-lg border-2 p-3 transition-colors ${
                            filled ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200 bg-white'
                          }`}>
                            {/* Slot heading with check */}
                            <div className="flex items-center gap-2 mb-1">
                              {filled ? (
                                <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                              ) : (
                                <Circle className="h-4 w-4 text-gray-300 flex-shrink-0" />
                              )}
                              <span className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
                                {slot.heading}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 mb-2 ml-6">{slot.label}</p>

                            {/* Upload area or file list */}
                            {!filled ? (
                              <div
                                onClick={() => slotInputRefs.current[slot.id]?.click()}
                                className="ml-6 border-2 border-dashed border-gray-300 rounded-lg p-3 text-center cursor-pointer hover:border-purple-400 hover:bg-purple-50/30 transition-colors"
                              >
                                <Upload className="h-4 w-4 text-gray-400 mx-auto mb-1" />
                                <p className="text-xs text-gray-500">Click to upload</p>
                                <p className="text-[10px] text-gray-400 mt-0.5">PDF, DOCX, code files, screenshots (max 10MB)</p>
                                <input
                                  ref={el => { slotInputRefs.current[slot.id] = el }}
                                  type="file"
                                  multiple
                                  accept={ACCEPTED_TYPES}
                                  onChange={e => handleSlotFileSelect(slot.id, e)}
                                  className="hidden"
                                />
                              </div>
                            ) : (
                              <div className="ml-6 space-y-1">
                                {files.map((f, i) => (
                                  <div key={i} className="flex items-center gap-2 text-xs text-gray-600 bg-white rounded-lg px-2.5 py-1.5 border border-emerald-200">
                                    <FileText className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                                    <span className="truncate flex-1">{f.name}</span>
                                    <span className="text-[10px] text-gray-400 flex-shrink-0">
                                      {(f.size / 1024).toFixed(0)}KB
                                    </span>
                                    <button
                                      onClick={() => removeSlotFile(slot.id, i)}
                                      className="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
                                    >
                                      <X className="h-3 w-3" />
                                    </button>
                                  </div>
                                ))}
                                {/* Add more files to this slot */}
                                <button
                                  onClick={() => slotInputRefs.current[slot.id]?.click()}
                                  className="text-[10px] text-purple-600 hover:text-purple-800 font-medium ml-1"
                                >
                                  + Add another file
                                  <input
                                    ref={el => { slotInputRefs.current[slot.id] = el }}
                                    type="file"
                                    multiple
                                    accept={ACCEPTED_TYPES}
                                    onChange={e => handleSlotFileSelect(slot.id, e)}
                                    className="hidden"
                                  />
                                </button>
                              </div>
                            )}
                          </div>
                        )
                      })}

                      {/* Error */}
                      {gradeError && (
                        <p className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">
                          {gradeError}
                        </p>
                      )}

                      {/* Submit button — disabled until all slots filled */}
                      <button
                        onClick={handleSubmitForGrading}
                        disabled={!canSubmit}
                        className="flex items-center justify-center gap-2 w-full text-sm font-medium px-4 py-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
                      >
                        {grading ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Grading your submission...
                          </>
                        ) : (
                          <>
                            <Send className="h-4 w-4" />
                            Submit for AI Grading
                          </>
                        )}
                      </button>

                      {!allSlotsFilled && (
                        <p className="text-[10px] text-gray-400 text-center">
                          Upload all required artifacts to enable submission
                        </p>
                      )}

                      {/* Simulate button for demo/testing */}
                      <button
                        onClick={handleSimulate}
                        disabled={grading}
                        className="flex items-center justify-center gap-2 w-full text-xs font-medium px-4 py-1.5 rounded-lg border border-gray-300 text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        <Zap className="h-3.5 w-3.5" />
                        Simulate Submission (Demo)
                      </button>
                    </div>
                  )}

                  {/* Step 3: Grading results */}
                  {stepNum === 3 && gradeResult && (
                    <div className="ml-9 mt-3">
                      <div className={`rounded-lg p-4 border ${
                        gradeResult.passed
                          ? 'bg-emerald-50 border-emerald-200'
                          : 'bg-amber-50 border-amber-200'
                      }`}>
                        {/* Score + badge */}
                        <div className="flex items-center gap-3 mb-3">
                          <span className={`text-2xl font-bold ${
                            gradeResult.passed ? 'text-emerald-600' : 'text-amber-600'
                          }`}>
                            {gradeResult.score}/100
                          </span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            gradeResult.passed
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}>
                            {gradeResult.passed ? 'PASSED' : 'NOT YET'}
                          </span>
                          <span className="text-[10px] text-gray-400 ml-auto">
                            Attempt #{gradeResult.attempt_number}
                          </span>
                        </div>

                        {/* Feedback */}
                        <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                          {gradeResult.feedback}
                        </p>

                        {/* Strengths */}
                        {gradeResult.strengths.length > 0 && (
                          <div className="mb-2">
                            <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
                              Strengths
                            </p>
                            <ul className="space-y-1">
                              {gradeResult.strengths.map((s, i) => (
                                <li key={i} className="flex items-start gap-1.5 text-sm text-gray-700">
                                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                                  {s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Improvements */}
                        {gradeResult.improvements.length > 0 && (
                          <div className="mb-3">
                            <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-1">
                              Areas to Improve
                            </p>
                            <ul className="space-y-1">
                              {gradeResult.improvements.map((s, i) => (
                                <li key={i} className="flex items-start gap-1.5 text-sm text-gray-700">
                                  <AlertCircle className="h-3.5 w-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
                                  {s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Download files */}
                        {gradeResult.download_urls && gradeResult.download_urls.length > 0 && (
                          <div className="border-t border-gray-200 pt-2 mt-2 mb-2">
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                              Download Files
                            </p>
                            <div className="space-y-1">
                              {gradeResult.download_urls.map((url, i) => {
                                const filename = url.split('/').pop() || `file-${i}`
                                return (
                                  <a
                                    key={i}
                                    href={url}
                                    download
                                    className="flex items-center gap-2 text-xs text-indigo-600 hover:text-indigo-800 bg-indigo-50 rounded-lg px-2.5 py-1.5 border border-indigo-200 transition-colors"
                                  >
                                    <Download className="h-3.5 w-3.5 flex-shrink-0" />
                                    <span className="truncate">{decodeURIComponent(filename)}</span>
                                  </a>
                                )
                              })}
                            </div>
                          </div>
                        )}

                        {/* View Submission toggle */}
                        {gradeResult.extracted_content && (
                          <div className="border-t border-gray-200 pt-2 mt-2">
                            <button
                              onClick={() => setShowSubmission(!showSubmission)}
                              className="flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-700 transition-colors"
                            >
                              {showSubmission ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                              {showSubmission ? 'Hide Submission' : 'View Submission'}
                            </button>
                            {showSubmission && (
                              <div className="mt-2 bg-gray-50 rounded-lg p-3 border border-gray-200 max-h-64 overflow-y-auto">
                                {gradeResult.file_names && gradeResult.file_names.length > 0 && (
                                  <p className="text-xs text-gray-500 mb-2">
                                    Files: {gradeResult.file_names.join(', ')}
                                  </p>
                                )}
                                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                                  {gradeResult.extracted_content}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Resubmit button (only if failed) */}
                        {!gradeResult.passed && (
                          <button
                            onClick={handleResubmit}
                            className="flex items-center gap-1.5 text-xs font-medium text-purple-600 hover:text-purple-800 transition-colors mt-1"
                          >
                            <RotateCcw className="h-3.5 w-3.5" />
                            Revise & Resubmit
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
