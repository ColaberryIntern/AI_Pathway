import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getLearningPath, getProgress, createProgress, updateProgress } from '../services/api'
import {
  CheckCircle,
  Circle,
  PlayCircle,
  ChevronDown,
  Clock,
  Target,
  ExternalLink,
  Loader2,
  BookOpen,
  Lightbulb,
  Code,
  MessageSquare,
  Bot,
  Star,
  Copy,
  ClipboardCheck,
} from 'lucide-react'
import type { Chapter } from '../types'

export default function LearningPathPage() {
  const { pathId } = useParams<{ pathId: string }>()
  const queryClient = useQueryClient()
  const [expandedChapter, setExpandedChapter] = useState<number | null>(1)

  const { data: path, isLoading: pathLoading } = useQuery({
    queryKey: ['path', pathId],
    queryFn: () => getLearningPath(pathId!),
    enabled: !!pathId,
  })

  const { data: progress } = useQuery({
    queryKey: ['progress', pathId],
    queryFn: async () => {
      try {
        return await getProgress(pathId!)
      } catch {
        // Create progress if it doesn't exist
        await createProgress(pathId!)
        return getProgress(pathId!)
      }
    },
    enabled: !!pathId,
  })

  const updateProgressMutation = useMutation({
    mutationFn: (params: { chapter: number; status: 'in_progress' | 'completed' }) =>
      updateProgress(pathId!, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress', pathId] })
    },
  })

  const getChapterStatus = (chapterNum: number): 'completed' | 'in_progress' | 'not_started' => {
    if (!progress?.chapter_status) return 'not_started'
    return (progress.chapter_status[String(chapterNum)] as 'completed' | 'in_progress' | 'not_started') || 'not_started'
  }

  const handleStartChapter = (chapterNum: number) => {
    updateProgressMutation.mutate({ chapter: chapterNum, status: 'in_progress' })
    setExpandedChapter(chapterNum)
  }

  const handleCompleteChapter = (chapterNum: number) => {
    updateProgressMutation.mutate({ chapter: chapterNum, status: 'completed' })
  }

  if (pathLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (!path) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900">Path not found</h1>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="card bg-gradient-to-br from-indigo-50 to-sky-50 border-0">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{path.title}</h1>
            <p className="text-gray-600">{path.description}</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-sky-600 bg-clip-text text-transparent">
              {progress?.completion_percentage || 0}%
            </div>
            <div className="text-sm text-gray-500">Complete</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-6">
          <div className="h-3 bg-white rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 transition-all duration-500 ease-out rounded-full"
              style={{ width: `${progress?.completion_percentage || 0}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>Start</span>
            <span>{path.chapters?.length || 0} Chapters Total</span>
          </div>
        </div>
      </div>

      {/* Chapters */}
      <div className="space-y-4">
        {path.chapters?.map((chapter: Chapter) => {
          const status = getChapterStatus(chapter.chapter_number)
          const isExpanded = expandedChapter === chapter.chapter_number

          return (
            <div
              key={chapter.chapter_number}
              className={`card transition-all duration-300 ${
                isExpanded ? 'shadow-lg ring-1 ring-gray-100' : ''
              } ${status === 'completed' ? 'bg-green-50/50' : ''}`}
            >
              {/* Chapter Header */}
              <div
                className="flex items-center gap-4 cursor-pointer group"
                onClick={() =>
                  setExpandedChapter(isExpanded ? null : chapter.chapter_number)
                }
              >
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all ${
                    status === 'completed'
                      ? 'bg-green-100'
                      : status === 'in_progress'
                      ? 'bg-indigo-100'
                      : 'bg-gray-100 group-hover:bg-gray-200'
                  }`}
                >
                  {status === 'completed' ? (
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  ) : status === 'in_progress' ? (
                    <PlayCircle className="h-6 w-6 text-indigo-600" />
                  ) : (
                    <Circle className="h-6 w-6 text-gray-400" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-500">
                      Chapter {chapter.chapter_number}
                    </span>
                    <span className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full">
                      {chapter.skill_name}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg">{chapter.title}</h3>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {chapter.estimated_time_hours && (
                    <span className="flex items-center gap-1 bg-gray-100 px-2 py-1 rounded-md">
                      <Clock className="h-4 w-4" />
                      {chapter.estimated_time_hours}h
                    </span>
                  )}
                  <div className={`transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                    <ChevronDown className="h-5 w-5" />
                  </div>
                </div>
              </div>

              {/* Chapter Content - Expandable */}
              <div
                className={`overflow-hidden transition-all duration-300 ${
                  isExpanded ? 'max-h-[8000px] opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="mt-6 space-y-6 border-t pt-6">
                  {/* Level Progress */}
                  <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <Target className="h-5 w-5 text-gray-500" />
                    <span className="text-sm text-gray-600">Skill Level Progress:</span>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded font-medium text-sm">
                        Level {chapter.current_level}
                      </span>
                      <span className="text-gray-400">→</span>
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded font-medium text-sm">
                        Level {chapter.target_level}
                      </span>
                    </div>
                  </div>

                  {/* Introduction */}
                  {chapter.introduction && (
                    <div className="bg-gradient-to-r from-indigo-50 to-sky-50 rounded-xl p-5 border border-indigo-100">
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <BookOpen className="h-5 w-5 text-indigo-600" />
                        Chapter Introduction
                      </h4>
                      <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                        {chapter.introduction}
                      </p>
                    </div>
                  )}

                  {/* Learning Objectives */}
                  <div className="bg-indigo-50 rounded-xl p-5">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Target className="h-5 w-5 text-indigo-600" />
                      Learning Objectives
                    </h4>
                    <ul className="space-y-2">
                      {chapter.learning_objectives?.map((obj, i) => (
                        <li key={i} className="flex items-start gap-2 text-gray-700">
                          <CheckCircle className="h-4 w-4 text-indigo-500 flex-shrink-0 mt-0.5" />
                          {obj}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Core Concepts */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-amber-500" />
                      Core Concepts
                    </h4>
                    <div className="space-y-4">
                      {chapter.core_concepts?.map((concept, i) => (
                        <div key={i} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
                          <h5 className="font-medium text-gray-900 mb-2 text-lg">
                            {concept.title}
                          </h5>
                          <p className="text-gray-700">{concept.content}</p>
                          {concept.examples && concept.examples.length > 0 && (
                            <div className="mt-4 pl-4 border-l-4 border-indigo-200 bg-indigo-50/50 p-3 rounded-r-lg">
                              <p className="text-xs font-medium text-indigo-600 mb-2">Examples:</p>
                              {concept.examples.map((ex, j) => (
                                <p key={j} className="text-sm text-gray-600 italic">
                                  {ex}
                                </p>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Prompting Examples */}
                  {chapter.prompting_examples && chapter.prompting_examples.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <MessageSquare className="h-5 w-5 text-violet-500" />
                        Prompting Examples
                      </h4>
                      <div className="space-y-4">
                        {chapter.prompting_examples.map((pe, i) => (
                          <div key={i} className="bg-white border border-violet-200 rounded-xl p-5 shadow-sm">
                            <h5 className="font-medium text-gray-900 mb-1 text-lg">{pe.title}</h5>
                            <p className="text-sm text-gray-600 mb-3">{pe.description}</p>
                            <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap mb-3">
                              {pe.prompt}
                            </div>
                            <div className="grid gap-3 sm:grid-cols-2">
                              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                <p className="text-xs font-medium text-green-700 mb-1">Expected Output</p>
                                <p className="text-sm text-gray-700">{pe.expected_output}</p>
                              </div>
                              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                                <p className="text-xs font-medium text-amber-700 mb-1">Customization Tips</p>
                                <p className="text-sm text-gray-700">{pe.customization_tips}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Agent Examples */}
                  {chapter.agent_examples && chapter.agent_examples.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Bot className="h-5 w-5 text-emerald-500" />
                        AI Agent Examples
                      </h4>
                      <div className="space-y-4">
                        {chapter.agent_examples.map((ae, i) => (
                          <div key={i} className="bg-white border border-emerald-200 rounded-xl p-5 shadow-sm">
                            <h5 className="font-medium text-gray-900 mb-1 text-lg">{ae.title}</h5>
                            <p className="text-sm text-gray-600 mb-3">{ae.scenario}</p>
                            <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 mb-3">
                              <p className="text-xs font-medium text-emerald-700 mb-1">Agent Role</p>
                              <p className="text-sm text-gray-700">{ae.agent_role}</p>
                            </div>
                            {ae.instructions && ae.instructions.length > 0 && (
                              <div className="bg-gray-50 rounded-lg p-4 mb-3">
                                <p className="text-xs font-medium text-gray-600 mb-2">Agent Instructions</p>
                                <ol className="space-y-1.5 text-sm text-gray-700">
                                  {ae.instructions.map((inst, j) => (
                                    <li key={j} className="flex gap-2">
                                      <span className="w-5 h-5 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center flex-shrink-0 font-medium text-xs">
                                        {j + 1}
                                      </span>
                                      <span>{inst}</span>
                                    </li>
                                  ))}
                                </ol>
                              </div>
                            )}
                            <div className="grid gap-3 sm:grid-cols-2">
                              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                <p className="text-xs font-medium text-blue-700 mb-1">Expected Behavior</p>
                                <p className="text-sm text-gray-700">{ae.expected_behavior}</p>
                              </div>
                              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                                <p className="text-xs font-medium text-indigo-700 mb-1">Use Case</p>
                                <p className="text-sm text-gray-700">{ae.use_case}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Exercises */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Code className="h-5 w-5 text-sky-500" />
                      Exercises
                    </h4>
                    <div className="space-y-4">
                      {chapter.exercises?.map((exercise) => (
                        <div
                          key={exercise.id}
                          className="border-2 border-dashed border-gray-200 rounded-xl p-5 hover:border-sky-300 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <span className="text-xs px-2.5 py-1 bg-sky-100 text-sky-700 rounded-full font-medium">
                                {exercise.type}
                              </span>
                              <h5 className="font-medium text-gray-900 mt-2 text-lg">
                                {exercise.title}
                              </h5>
                              <p className="text-sm text-gray-600 mt-1">
                                {exercise.description}
                              </p>
                            </div>
                            {exercise.estimated_time_minutes && (
                              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-md whitespace-nowrap">
                                ~{exercise.estimated_time_minutes} min
                              </span>
                            )}
                          </div>
                          {exercise.instructions && (
                            <ol className="mt-4 space-y-2 text-sm text-gray-700 bg-gray-50 rounded-lg p-4">
                              {exercise.instructions.map((inst, i) => (
                                <li key={i} className="flex gap-3">
                                  <span className="w-6 h-6 bg-sky-100 text-sky-700 rounded-full flex items-center justify-center flex-shrink-0 font-medium text-xs">
                                    {i + 1}
                                  </span>
                                  <span>{inst}</span>
                                </li>
                              ))}
                            </ol>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Takeaways */}
                  {chapter.key_takeaways && chapter.key_takeaways.length > 0 && (
                    <div className="bg-amber-50 rounded-xl p-5 border border-amber-200">
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Star className="h-5 w-5 text-amber-500" />
                        Key Takeaways
                      </h4>
                      <ul className="space-y-2">
                        {chapter.key_takeaways.map((takeaway, i) => (
                          <li key={i} className="flex items-start gap-2 text-gray-700">
                            <CheckCircle className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
                            {takeaway}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Exact Prompt — Copy-Paste Ready */}
                  {chapter.exact_prompt && chapter.exact_prompt.prompt_text && (
                    <div className="bg-gray-900 rounded-xl p-5 text-gray-100">
                      <h4 className="font-semibold text-white mb-1 flex items-center gap-2">
                        <Copy className="h-5 w-5 text-sky-400" />
                        EXACT PROMPT — Copy &amp; Paste Ready
                      </h4>
                      <p className="text-sm text-gray-400 mb-3">{chapter.exact_prompt.title}</p>
                      <p className="text-sm text-gray-300 mb-3">{chapter.exact_prompt.context}</p>
                      <div
                        className="bg-gray-800 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap mb-3 border border-gray-700 cursor-pointer hover:border-sky-500 transition-colors relative group"
                        onClick={() => {
                          navigator.clipboard.writeText(chapter.exact_prompt!.prompt_text)
                        }}
                      >
                        <span className="absolute top-2 right-2 text-xs text-gray-500 group-hover:text-sky-400 flex items-center gap-1">
                          <ClipboardCheck className="h-3 w-3" /> Click to copy
                        </span>
                        {chapter.exact_prompt.prompt_text}
                      </div>
                      <div className="grid gap-3 sm:grid-cols-2">
                        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                          <p className="text-xs font-medium text-green-400 mb-1">Expected Output</p>
                          <p className="text-sm text-gray-300">{chapter.exact_prompt.expected_output}</p>
                        </div>
                        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                          <p className="text-xs font-medium text-amber-400 mb-1">How to Customize</p>
                          <p className="text-sm text-gray-300">{chapter.exact_prompt.how_to_customize}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Resources */}
                  {chapter.resources && chapter.resources.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <BookOpen className="h-5 w-5 text-emerald-500" />
                        Resources
                      </h4>
                      <div className="grid gap-3">
                        {chapter.resources.map((resource, i) => (
                          <a
                            key={i}
                            href={resource.url || '#'}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-xl hover:border-emerald-300 hover:shadow-md transition-all group"
                          >
                            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center group-hover:bg-emerald-200 transition-colors">
                              <ExternalLink className="h-5 w-5 text-emerald-600" />
                            </div>
                            <div className="flex-1">
                              <div className="font-medium text-gray-900 group-hover:text-emerald-700 transition-colors">
                                {resource.title}
                              </div>
                              <div className="text-xs text-gray-500">
                                {resource.type} • {resource.source}
                              </div>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-3 pt-4 border-t">
                    {status === 'not_started' && (
                      <button
                        onClick={() => handleStartChapter(chapter.chapter_number)}
                        className="btn btn-primary flex items-center gap-2"
                      >
                        <PlayCircle className="h-4 w-4" />
                        Start Chapter
                      </button>
                    )}
                    {status === 'in_progress' && (
                      <button
                        onClick={() => handleCompleteChapter(chapter.chapter_number)}
                        className="btn btn-primary flex items-center gap-2"
                      >
                        <CheckCircle className="h-4 w-4" />
                        Mark as Complete
                      </button>
                    )}
                    {status === 'completed' && (
                      <span className="text-green-600 font-medium flex items-center gap-2 bg-green-50 px-4 py-2 rounded-lg">
                        <CheckCircle className="h-5 w-5" />
                        Chapter Completed
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
