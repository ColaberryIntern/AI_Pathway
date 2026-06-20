import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ChapterRenderer from '../components/chapter/ChapterRenderer'
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

// Coach-voice outro (P3 #3 - second half of the coach pass). Appears
// below the chapter content, above the "Mark Complete" button. Frames
// what the learner just did and what comes next, in coach voice.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CoachOutro({ meta }: { meta: any }) {
  if (!meta || typeof meta !== 'object') return null
  const targetLabel = String((meta as Record<string, unknown>).target_level_label || '')
  const targetRubric = String((meta as Record<string, unknown>).target_level_rubric || '')
  return (
    <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 px-5 py-4 flex items-start gap-3">
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-emerald-500 text-white flex items-center justify-center text-lg font-semibold">
        AI
      </div>
      <div className="flex-1">
        <div className="text-xs font-semibold uppercase tracking-wide text-emerald-700 mb-1">
          Your coach
        </div>
        <div className="text-gray-900">
          Nice work getting through this chapter. The implementation task above is
          where this skill becomes real - take a shot at it before you mark
          complete. Even a rough first version counts.
        </div>
        {(targetLabel || targetRubric) && (
          <div className="text-sm text-gray-700 mt-2">
            Once you submit your task, you&rsquo;ll be at{' '}
            <strong>{targetLabel || 'the next level'}</strong>
            {targetRubric ? (
              <>
                {' '}for this skill - able to <em>{targetRubric.toLowerCase()}</em>.
              </>
            ) : (
              '.'
            )}
          </div>
        )}
        <div className="text-xs text-gray-600 mt-2">
          Stuck on the task? Use the &ldquo;I&rsquo;m confused&rdquo; button on the right - I&rsquo;ll suggest a smaller first step.
        </div>
      </div>
    </div>
  )
}


// Coach-voice intro (P3 #3 - Jennifer C's "make it feel like a coach"
// ask from her May 12 demo). Always sits between the disclosure and
// the chapter content. Reads the chapter meta to greet the learner and
// frame the skill + level progression in plain language. No new data
// fetching - everything is in content.meta already.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CoachIntro({ meta }: { meta: any }) {
  if (!meta || typeof meta !== 'object') return null
  const skillName = String((meta as Record<string, unknown>).skill_name || '')
  const currentLabel = String((meta as Record<string, unknown>).current_level_label || '')
  const targetLabel = String((meta as Record<string, unknown>).target_level_label || '')
  const targetRubric = String((meta as Record<string, unknown>).target_level_rubric || '')
  const chapterTitle = String((meta as Record<string, unknown>).chapter_title || '')
  if (!skillName && !chapterTitle) return null
  return (
    <div className="rounded-lg border border-indigo-200 bg-gradient-to-br from-indigo-50 to-white px-5 py-4 flex items-start gap-3">
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-indigo-500 text-white flex items-center justify-center text-lg font-semibold">
        AI
      </div>
      <div className="flex-1">
        <div className="text-xs font-semibold uppercase tracking-wide text-indigo-700 mb-1">
          Your coach
        </div>
        <div className="text-gray-900">
          Let&rsquo;s work on{' '}
          <strong>{skillName || chapterTitle}</strong>
          {currentLabel && targetLabel ? (
            <>
              {' '}together. We&rsquo;re moving you from <strong>{currentLabel}</strong>{' '}
              to <strong>{targetLabel}</strong>.
            </>
          ) : (
            '.'
          )}
        </div>
        {targetRubric && (
          <div className="text-sm text-gray-700 mt-1">
            By the end you should be able to: <em>{targetRubric.toLowerCase()}</em>.
          </div>
        )}
        <div className="text-xs text-gray-600 mt-2">
          Take about 15 minutes. Work at your own pace. If something feels off, use the &ldquo;I&rsquo;m confused&rdquo; button on the right and I&rsquo;ll help you unstick.
        </div>
      </div>
    </div>
  )
}


// AI disclosure + ontology-grounding panel (P3 #2 - Jennifer C's
// "how do we know AI isn't hallucinating?" ask). One-line banner is
// always visible at the top of every chapter; a collapsible "Sources"
// section underneath lets the curious reader see exactly which ontology
// skill, domain, and rubric strings the chapter was grounded in.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function ChapterDisclosure({ meta }: { meta: any }) {
  const [open, setOpen] = useState(false)
  if (!meta || typeof meta !== 'object') return null
  const {
    skill_id, skill_name, domain_id, domain_name,
    current_level, target_level,
    current_level_label, target_level_label,
    current_level_rubric, target_level_rubric,
  } = meta as Record<string, unknown>
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50/70 px-4 py-3 text-sm">
      <div className="flex items-start gap-2">
        <span className="text-amber-700 mt-0.5">&#9888;</span>
        <div className="flex-1">
          <div className="font-semibold text-amber-900">
            AI-generated lesson, grounded in the GenAI Skills Ontology v2.0
          </div>
          <div className="text-amber-800 text-xs mt-1">
            This 15-minute chapter was written by an AI model from the
            ontology entry for this specific skill and level. The scenario,
            examples, and rubric language below come from your selection -
            not external claims. Verify any third-party tools, statistics,
            or named services before acting on them.
          </div>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="mt-2 text-amber-900 hover:underline text-xs font-semibold flex items-center gap-1"
            aria-expanded={open}
          >
            <span>{open ? '▼' : '▶'}</span>
            <span>{open ? 'Hide sources' : 'Show sources this chapter was grounded in'}</span>
          </button>
        </div>
      </div>
      {open && (
        <div className="mt-3 border-t border-amber-200 pt-3 space-y-2 text-amber-900">
          <div>
            <div className="font-semibold text-xs uppercase tracking-wide opacity-70">Skill</div>
            <div>
              <span className="font-mono text-xs text-amber-700">{String(skill_id || '')}</span>{' '}
              <strong>{String(skill_name || '')}</strong>
            </div>
          </div>
          {(Boolean(domain_id) || Boolean(domain_name)) && (
            <div>
              <div className="font-semibold text-xs uppercase tracking-wide opacity-70">Domain</div>
              <div>
                <span className="font-mono text-xs text-amber-700">{String(domain_id || '')}</span>{' '}
                {String(domain_name || '')}
              </div>
            </div>
          )}
          <div>
            <div className="font-semibold text-xs uppercase tracking-wide opacity-70">Level progression</div>
            <div>
              L{String(current_level ?? '?')} {current_level_label ? `(${String(current_level_label)})` : ''}
              {' → '}
              L{String(target_level ?? '?')} {target_level_label ? `(${String(target_level_label)})` : ''}
            </div>
          </div>
          {current_level_rubric ? (
            <div>
              <div className="font-semibold text-xs uppercase tracking-wide opacity-70">
                Where you are now ({current_level_label ? String(current_level_label) : `L${String(current_level ?? '?')}`}) - exact ontology text
              </div>
              <div className="italic">&ldquo;{String(current_level_rubric)}&rdquo;</div>
            </div>
          ) : null}
          {target_level_rubric ? (
            <div>
              <div className="font-semibold text-xs uppercase tracking-wide opacity-70">
                Where you are headed ({target_level_label ? String(target_level_label) : `L${String(target_level ?? '?')}`}) - exact ontology text
              </div>
              <div className="italic">&ldquo;{String(target_level_rubric)}&rdquo;</div>
            </div>
          ) : null}
          <div className="text-xs text-amber-700 italic pt-1 border-t border-amber-100">
            If the chapter narrative below contradicts the level-rubric text quoted here, that is a defect - please flag it via the Confusion Recovery button.
          </div>
        </div>
      )}
    </div>
  )
}


// eslint-disable-next-line @typescript-eslint/no-explicit-any
function ChapterFormatView({ content, pathId, lessonId, navigate, completeMutation, isLastLesson }: { content: any; pathId: string; lessonId: string; navigate: (path: string) => void; completeMutation: any; isLastLesson: boolean }) {
  const handleComplete = () => {
    completeMutation.mutate(undefined, {
      onSuccess: () => {
        // P3 #4 stickiness: when this completes the final chapter,
        // route to the path summary instead of back to the dashboard.
        if (isLastLesson) {
          navigate(`/learn/${pathId}/complete`)
        } else {
          navigate(`/learn/${pathId}`)
        }
      },
    })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center gap-2 text-sm">
        <button
          onClick={() => navigate(`/learn/${pathId}`)}
          className="flex items-center gap-1 text-gray-500 hover:text-indigo-600 transition-colors"
        >
          &larr; Back to Dashboard
        </button>
      </div>
      <ChapterDisclosure meta={content?.meta} />
      <CoachIntro meta={content?.meta} />
      <ChapterRenderer chapter={content} pathId={pathId} lessonId={lessonId} />
      <CoachOutro meta={content?.meta} />
      <div className="flex justify-center gap-4 pt-4">
        <button
          onClick={() => navigate(`/learn/${pathId}`)}
          className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Back to Dashboard
        </button>
        <button
          onClick={handleComplete}
          disabled={completeMutation.isPending}
          className="btn btn-primary flex items-center gap-2"
        >
          {completeMutation.isPending ? 'Completing...' : 'Mark Chapter Complete'}
        </button>
      </div>
    </div>
  )
}

export default function LessonPage() {
  const { pathId, lessonId } = useParams<{ pathId: string; lessonId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [, setTaskSubmitted] = useState(false)
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
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['learning-dashboard', pathId] })
      await queryClient.refetchQueries({ queryKey: ['learning-dashboard', pathId] })
    },
  })

  // Find the module and next lesson for navigation
  const currentModule = dashboard?.modules.find((m) => m.id === lesson?.module_id)
  const allModuleLessons = currentModule?.lesson_outline || []
  const currentLessonIndex = allModuleLessons.findIndex(
    (l) => l.lesson_number === lesson?.lesson_number
  )
  const hasNextLesson = currentLessonIndex < allModuleLessons.length - 1 ||
    (dashboard?.next_lesson_id != null && dashboard.next_lesson_id !== lessonId)

  const handleComplete = () => {
    completeMutation.mutate()
  }

  const handleNextLesson = () => {
    if (dashboard?.next_lesson_id && dashboard.next_lesson_id !== lessonId) {
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

  // Detect content format
  const isAINative = !!content?.concept_snapshot
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const contentAny = content as any
  const isChapterFormat = !!contentAny?.scenario && !!contentAny?.meta  // Vivek's chapter format

  // Free completion — no gating on knowledge checks or implementation tasks

  // Detect whether completing this lesson finishes the entire path.
  // The dashboard query has per-module lesson outlines + completed counts;
  // every other lesson must already be complete AND this one is not yet
  // (we are about to complete it). The frontend's completeMutation.onSuccess
  // uses this to navigate to the summary page instead of the dashboard.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const modulesArr = (dashboard?.modules as any[] | undefined) || []
  const totalAcrossPath = modulesArr.reduce(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (acc: number, m: any) => acc + (m.total_lessons ?? 1), 0,
  )
  const completedAcrossPath = modulesArr.reduce(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (acc: number, m: any) => acc + (m.completed_lessons ?? 0), 0,
  )
  const isLastLesson = totalAcrossPath > 0 && completedAcrossPath + 1 >= totalAcrossPath

  // Render Vivek's chapter format
  if (isChapterFormat && contentAny) {
    return <ChapterFormatView content={contentAny} pathId={pathId!} lessonId={lessonId!} navigate={navigate} completeMutation={completeMutation} isLastLesson={isLastLesson} />
  }

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
                        validated={example.validated}
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
                        validated={example.validated}
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
            <button
              onClick={handleComplete}
              disabled={completeMutation.isPending}
              className="btn bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {completeMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
              ) : (
                <CheckCircle2 className="h-4 w-4 mr-1" />
              )}
              Mark as Complete
            </button>
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
