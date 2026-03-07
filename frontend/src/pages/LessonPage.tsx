import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft, Loader2, AlertCircle, CheckCircle2, ChevronRight,
  BookOpen, Code2, Dumbbell, Brain, Wrench,
} from 'lucide-react'
import { startLesson, completeLesson, getLearningDashboard } from '../services/api'
import CodeBlock from '../components/learning/CodeBlock'
import KnowledgeCheck from '../components/learning/KnowledgeCheck'
import ConceptSnapshot from '../components/learning/ConceptSnapshot'
import AIStrategyPanel from '../components/learning/AIStrategyPanel'
import PromptTemplateCard from '../components/learning/PromptTemplateCard'
import PromptLab from '../components/learning/PromptLab'
import ImplementationTaskCard from '../components/learning/ImplementationTaskCard'
import ReflectionPrompts from '../components/learning/ReflectionPrompts'
import LessonReactions from '../components/learning/LessonReactions'
import ConfusionRecoveryDrawer from '../components/learning/ConfusionRecoveryDrawer'

export default function LessonPage() {
  const { pathId, lessonId } = useParams<{ pathId: string; lessonId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [taskSubmitted, setTaskSubmitted] = useState(false)
  const [confusionDrawerOpen, setConfusionDrawerOpen] = useState(false)
  const [regenerating, setRegenerating] = useState(false)

  // Start/load lesson (generates content on-demand if needed)
  const {
    data: lesson,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['lesson', pathId, lessonId],
    queryFn: () => startLesson(pathId!, lessonId!),
    enabled: !!pathId && !!lessonId,
    staleTime: Infinity, // Content doesn't change once generated
  })

  const handleRegenerate = async () => {
    if (!pathId || !lessonId) return
    setRegenerating(true)
    try {
      const freshLesson = await startLesson(pathId, lessonId, true)
      queryClient.setQueryData(['lesson', pathId, lessonId], freshLesson)
    } catch {
      // Refetch will show the error state
      await refetch()
    } finally {
      setRegenerating(false)
    }
  }

  // Load dashboard for breadcrumb context
  const { data: dashboard } = useQuery({
    queryKey: ['learning-dashboard', pathId],
    queryFn: () => getLearningDashboard(pathId!),
    enabled: !!pathId,
  })

  // Complete mutation
  const completeMutation = useMutation({
    mutationFn: () =>
      completeLesson(pathId!, lessonId!, {
        quiz_score: quizScore ?? undefined,
        exercise_completed: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-dashboard', pathId] })
    },
  })

  // Find the module and next lesson for navigation
  const currentModule = dashboard?.modules.find((m) => m.id === lesson?.module_id)
  const allModuleLessons = currentModule?.lesson_outline || []
  const currentLessonIndex = allModuleLessons.findIndex(
    (l) => l.lesson_number === lesson?.lesson_number
  )
  const hasNextLesson = currentLessonIndex < allModuleLessons.length - 1

  const handleComplete = () => {
    completeMutation.mutate()
  }

  const handleNextLesson = () => {
    if (dashboard?.next_lesson_id) {
      navigate(`/learn/${pathId}/lesson/${dashboard.next_lesson_id}`)
    } else {
      navigate(`/learn/${pathId}`)
    }
  }

  // Loading state with generation message
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4 max-w-md">
          <div className="relative mx-auto w-16 h-16">
            <Loader2 className="h-16 w-16 text-indigo-600 animate-spin" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Generating Your Lesson</h3>
            <p className="text-gray-500 mt-1">
              Creating personalized content tailored to your skill level and industry...
            </p>
          </div>
          {/* Skeleton preview */}
          <div className="space-y-3 pt-4">
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
            <div className="h-32 bg-gray-100 rounded-lg animate-pulse mt-4" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="card p-8 space-y-4">
          <AlertCircle className="h-8 w-8 text-amber-500 mx-auto" />
          <p className="text-gray-700 font-medium">Lesson content generation failed</p>
          <p className="text-sm text-gray-500">This is usually a temporary issue. Try again.</p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Wrench className="h-4 w-4" /> Retry
            </button>
            <button onClick={() => navigate(`/learn/${pathId}`)} className="btn btn-secondary">
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!lesson) return null

  const content = lesson.content
  const isCompleted = lesson.status === 'completed' || completeMutation.isSuccess

  // Detect empty content that needs re-generation
  const hasSubstance = !!(
    content?.concept_snapshot ||
    content?.explanation ||
    content?.knowledge_checks?.length
  )

  // Detect AI-native vs legacy content format
  const isAINative = !!content?.concept_snapshot

  // Completion gating: for AI-native lessons, require knowledge check + implementation task
  const hasKnowledgeCheck = !!(content?.knowledge_checks?.length)
  const hasImplementationTask = !!(content?.implementation_task?.title)
  const canComplete = !isAINative || (
    (!hasKnowledgeCheck || quizScore !== null) &&
    (!hasImplementationTask || taskSubmitted)
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <button
          onClick={() => navigate(`/learn/${pathId}`)}
          className="flex items-center gap-1 text-gray-500 hover:text-indigo-600 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </button>
        {currentModule && (
          <>
            <span className="text-gray-300">/</span>
            <span className="text-gray-500">Module {currentModule.chapter_number}: {currentModule.title}</span>
          </>
        )}
        <span className="text-gray-300">/</span>
        <span className="text-gray-900 font-medium">{lesson.title}</span>
      </div>

      {/* Lesson header */}
      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            lesson.lesson_type === 'concept' ? 'bg-indigo-100 text-indigo-700' :
            lesson.lesson_type === 'practice' ? 'bg-emerald-100 text-emerald-700' :
            lesson.lesson_type === 'assessment' ? 'bg-amber-100 text-amber-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {lesson.lesson_type}
          </span>
          <span className="text-xs text-gray-400">Lesson {lesson.lesson_number}</span>
          {isAINative && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-gradient-to-r from-indigo-100 to-sky-100 text-indigo-600 font-medium">
              AI-Native
            </span>
          )}
          {isCompleted && (
            <span className="flex items-center gap-1 text-xs text-emerald-600 ml-auto">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Completed
            </span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
      </div>

      {/* Empty content — offer regeneration */}
      {content && !hasSubstance && (
        <div className="card text-center py-8 space-y-3">
          <AlertCircle className="h-8 w-8 text-amber-500 mx-auto" />
          <p className="text-gray-700 font-medium">Lesson content didn't generate properly</p>
          <p className="text-sm text-gray-500">This can happen due to a temporary LLM issue. Click below to regenerate.</p>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {regenerating ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Regenerating...</>
            ) : (
              <><Wrench className="h-4 w-4" /> Regenerate Lesson</>
            )}
          </button>
        </div>
      )}

      {/* Content sections */}
      {content && hasSubstance ? (
        <div className="space-y-8">
          {isAINative ? (
            <>
              {/* ── AI-NATIVE RENDERING PATH ── */}

              {/* 1. Concept Snapshot */}
              {content.concept_snapshot && (
                <ConceptSnapshot snapshot={content.concept_snapshot} />
              )}

              {/* 2. AI Strategy */}
              {content.ai_strategy && content.ai_strategy.description && (
                <AIStrategyPanel strategy={content.ai_strategy} />
              )}

              {/* 3. Prompt Template */}
              {content.prompt_template && content.prompt_template.template && (
                <PromptTemplateCard template={content.prompt_template} />
              )}

              {/* 3b. Prompt Lab (interactive) */}
              {content.prompt_template && pathId && lessonId && (
                <PromptLab
                  pathId={pathId}
                  lessonId={lessonId}
                  template={content.prompt_template}
                />
              )}

              {/* 4. Code Examples */}
              {content.code_examples && content.code_examples.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Code2 className="h-5 w-5 text-emerald-600" />
                    <h2 className="text-lg font-bold text-gray-900">Code Examples</h2>
                  </div>
                  {content.code_examples.map((example, i) => (
                    <div key={i} className="space-y-2">
                      {example.explanation && (
                        <p className="text-sm text-gray-600">{example.explanation}</p>
                      )}
                      <CodeBlock
                        code={example.code}
                        language={example.language}
                        title={example.title}
                      />
                    </div>
                  ))}
                </section>
              )}

              {/* 5. Implementation Task */}
              {content.implementation_task && content.implementation_task.title && (
                <ImplementationTaskCard
                  task={content.implementation_task}
                  pathId={pathId}
                  lessonId={lessonId}
                  lessonTitle={lesson.title}
                  onSubmit={() => setTaskSubmitted(true)}
                />
              )}

              {/* 6. Reflection */}
              {content.reflection_questions && content.reflection_questions.length > 0 && (
                <ReflectionPrompts questions={content.reflection_questions} />
              )}

              {/* 7. Knowledge Checks (with AI followup prompts) */}
              {content.knowledge_checks && content.knowledge_checks.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-amber-600" />
                    <h2 className="text-lg font-bold text-gray-900">Knowledge Check</h2>
                  </div>
                  <KnowledgeCheck
                    checks={content.knowledge_checks}
                    onComplete={(score) => setQuizScore(score)}
                  />
                </section>
              )}
            </>
          ) : (
            <>
              {/* ── LEGACY RENDERING PATH (backward compat) ── */}

              {/* Explanation */}
              {content.explanation && (
                <section className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="h-5 w-5 text-indigo-600" />
                    <h2 className="text-lg font-bold text-gray-900">Explanation</h2>
                  </div>
                  <div className="prose prose-gray max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {content.explanation}
                  </div>
                </section>
              )}

              {/* Code Examples */}
              {content.code_examples && content.code_examples.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Code2 className="h-5 w-5 text-emerald-600" />
                    <h2 className="text-lg font-bold text-gray-900">Code Examples</h2>
                  </div>
                  {content.code_examples.map((example, i) => (
                    <div key={i} className="space-y-2">
                      {example.explanation && (
                        <p className="text-sm text-gray-600">{example.explanation}</p>
                      )}
                      <CodeBlock
                        code={example.code}
                        language={example.language}
                        title={example.title}
                      />
                    </div>
                  ))}
                </section>
              )}

              {/* Exercises */}
              {content.exercises && content.exercises.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Dumbbell className="h-5 w-5 text-sky-600" />
                    <h2 className="text-lg font-bold text-gray-900">Exercises</h2>
                  </div>
                  {content.exercises.map((exercise, i) => (
                    <div key={i} className="card border-l-4 border-l-sky-400">
                      <h3 className="font-semibold text-gray-900 mb-2">{exercise.title}</h3>
                      <div className="text-sm text-gray-700 whitespace-pre-wrap mb-3">
                        {exercise.instructions}
                      </div>
                      {exercise.starter_code && (
                        <CodeBlock code={exercise.starter_code} title="Starter Code" />
                      )}
                      {exercise.expected_output && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs font-medium text-gray-500 mb-1">Expected Output:</p>
                          <pre className="text-sm text-gray-700 font-mono whitespace-pre-wrap">{exercise.expected_output}</pre>
                        </div>
                      )}
                      {exercise.hints && exercise.hints.length > 0 && (
                        <details className="mt-3">
                          <summary className="text-sm text-indigo-600 cursor-pointer hover:text-indigo-800">
                            Show hints ({exercise.hints.length})
                          </summary>
                          <ul className="mt-2 space-y-1 pl-4">
                            {exercise.hints.map((hint, j) => (
                              <li key={j} className="text-sm text-gray-600 list-disc">{hint}</li>
                            ))}
                          </ul>
                        </details>
                      )}
                    </div>
                  ))}
                </section>
              )}

              {/* Knowledge Checks */}
              {content.knowledge_checks && content.knowledge_checks.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-amber-600" />
                    <h2 className="text-lg font-bold text-gray-900">Knowledge Check</h2>
                  </div>
                  <KnowledgeCheck
                    checks={content.knowledge_checks}
                    onComplete={(score) => setQuizScore(score)}
                  />
                </section>
              )}

              {/* Hands-On Tasks */}
              {content.hands_on_tasks && content.hands_on_tasks.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Wrench className="h-5 w-5 text-purple-600" />
                    <h2 className="text-lg font-bold text-gray-900">Hands-On Task</h2>
                  </div>
                  {content.hands_on_tasks.map((task, i) => (
                    <div key={i} className="card border-2 border-purple-200 bg-purple-50/30">
                      <h3 className="font-semibold text-gray-900 mb-2">{task.title}</h3>
                      <p className="text-sm text-gray-700 mb-3">{task.description}</p>
                      {task.requirements && task.requirements.length > 0 && (
                        <div className="mb-3">
                          <p className="text-xs font-medium text-gray-500 mb-1">Requirements:</p>
                          <ul className="space-y-1 pl-4">
                            {task.requirements.map((req, j) => (
                              <li key={j} className="text-sm text-gray-600 list-disc">{req}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span>Deliverable: {task.deliverable}</span>
                        {task.estimated_minutes && <span>~{task.estimated_minutes} min</span>}
                      </div>
                    </div>
                  ))}
                </section>
              )}
            </>
          )}
        </div>
      ) : !content ? (
        <div className="card text-center py-8 text-gray-500">
          No content available for this lesson.
        </div>
      ) : null}

      {/* Lesson Reactions — at the bottom so students rate after reading */}
      {pathId && lessonId && (
        <div className="card">
          <LessonReactions
            pathId={pathId}
            lessonId={lessonId}
            onConfused={() => setConfusionDrawerOpen(true)}
          />
        </div>
      )}

      {/* Bottom actions */}
      <div className="card flex items-center justify-between">
        <button
          onClick={() => navigate(`/learn/${pathId}`)}
          className="btn btn-secondary"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Dashboard
        </button>

        <div className="flex items-center gap-3">
          {!isCompleted && (
            <div className="flex items-center gap-3">
              {!canComplete && isAINative && (
                <p className="text-xs text-amber-600 max-w-[14rem] text-right">
                  Complete the {hasKnowledgeCheck && quizScore === null ? 'knowledge check' : ''}
                  {hasKnowledgeCheck && quizScore === null && hasImplementationTask && !taskSubmitted ? ' and ' : ''}
                  {hasImplementationTask && !taskSubmitted ? 'implementation task' : ''} first
                </p>
              )}
              <button
                onClick={handleComplete}
                disabled={!canComplete || completeMutation.isPending}
                className="btn bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {completeMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 mr-1" />
                )}
                Mark as Complete
              </button>
            </div>
          )}

          {isCompleted && (
            <button
              onClick={handleNextLesson}
              className="btn bg-gradient-to-r from-indigo-600 to-sky-600 text-white hover:from-indigo-700 hover:to-sky-700"
            >
              {hasNextLesson ? 'Next Lesson' : 'Back to Dashboard'}
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          )}
        </div>
      </div>

      {/* Confusion Recovery Drawer */}
      {pathId && lessonId && (
        <ConfusionRecoveryDrawer
          isOpen={confusionDrawerOpen}
          onClose={() => setConfusionDrawerOpen(false)}
          pathId={pathId}
          lessonId={lessonId}
        />
      )}
    </div>
  )
}
