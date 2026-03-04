import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { GraduationCap, Rocket, Loader2, AlertCircle } from 'lucide-react'
import { getLearningDashboard, activateLearningPath } from '../services/api'
import { useLearningStore } from '../stores/learningStore'
import ModuleSidebar from '../components/learning/ModuleSidebar'
import SkillGapTracker from '../components/learning/SkillGapTracker'
import NextLessonCard from '../components/learning/NextLessonCard'
import ProgressSummary from '../components/learning/ProgressSummary'

export default function LearningDashboardPage() {
  const { pathId } = useParams<{ pathId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null)

  const store = useLearningStore()

  // Fetch dashboard (will 400 if not activated)
  const {
    data: dashboard,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['learning-dashboard', pathId],
    queryFn: () => getLearningDashboard(pathId!),
    enabled: !!pathId,
    retry: false,
  })

  // Activate mutation
  const activateMutation = useMutation({
    mutationFn: () => activateLearningPath(pathId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-dashboard', pathId] })
    },
  })

  // Sync dashboard data to store
  useEffect(() => {
    if (dashboard) {
      store.setPath(dashboard.path_id)
      store.setModules(dashboard.modules)
      store.setOverallProgress(dashboard.overall_progress)
      store.setActivated(true)
      if (dashboard.current_module) {
        setSelectedModuleId(dashboard.current_module.id)
      }
    }
  }, [dashboard])

  // Not activated state
  const needsActivation = error && (error as { response?: { status?: number } })?.response?.status === 400

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <Loader2 className="h-8 w-8 text-indigo-600 animate-spin mx-auto" />
          <p className="text-gray-500">Loading your learning dashboard...</p>
        </div>
      </div>
    )
  }

  if (needsActivation || (!dashboard && !isLoading)) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="card p-8 space-y-6">
          <div className="mx-auto w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center">
            <Rocket className="h-8 w-8 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Ready to Start Learning?</h2>
            <p className="text-gray-500 mt-2">
              We'll create your personalized learning modules and generate a lesson plan
              tailored to your skill gaps and target role.
            </p>
          </div>
          <button
            onClick={() => activateMutation.mutate()}
            disabled={activateMutation.isPending}
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-sky-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-sky-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50"
          >
            {activateMutation.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Generating lesson plans...
              </>
            ) : (
              <>
                <Rocket className="h-5 w-5" />
                Activate My Learning Path
              </>
            )}
          </button>
          {activateMutation.isError && (
            <div className="flex items-center gap-2 text-red-600 text-sm justify-center">
              <AlertCircle className="h-4 w-4" />
              Failed to activate. Please try again.
            </div>
          )}
        </div>
      </div>
    )
  }

  if (error && !needsActivation) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="card p-8 space-y-4">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto" />
          <p className="text-red-600">Failed to load dashboard. Please go back and try again.</p>
          <button
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  if (!dashboard) return null

  const selectedModule = dashboard.modules.find((m) => m.id === selectedModuleId) || dashboard.current_module

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="card bg-gradient-to-r from-indigo-600 to-sky-600 text-white">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <GraduationCap className="h-6 w-6" />
              <span className="text-sm font-medium text-indigo-200">AI Learning Dashboard</span>
            </div>
            <h1 className="text-2xl font-bold">{dashboard.path_title}</h1>
            {dashboard.target_role && (
              <p className="text-indigo-200 mt-1">Target Role: {dashboard.target_role}</p>
            )}
          </div>
          {/* Overall progress */}
          <div className="text-right">
            <div className="text-3xl font-bold">{dashboard.overall_progress.toFixed(0)}%</div>
            <div className="w-40 h-3 bg-indigo-800/50 rounded-full mt-1 overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-700"
                style={{ width: `${dashboard.overall_progress}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <ProgressSummary
        lessonsCompleted={dashboard.total_lessons_completed}
        totalLessons={dashboard.total_lessons}
        estimatedHoursRemaining={dashboard.estimated_hours_remaining}
        overallProgress={dashboard.overall_progress}
        totalModules={dashboard.modules.length}
      />

      {/* Main layout: sidebar + content + skill tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Module sidebar */}
        <div className="lg:col-span-3">
          <ModuleSidebar
            modules={dashboard.modules}
            currentModuleId={selectedModuleId}
            onModuleClick={setSelectedModuleId}
          />
        </div>

        {/* Center: Current module detail + Next lesson */}
        <div className="lg:col-span-6 space-y-4">
          {/* Selected module detail */}
          {selectedModule && (
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <span className="text-[10px] font-mono text-indigo-500">{selectedModule.skill_id}</span>
                  <h3 className="text-lg font-bold text-gray-900">{selectedModule.title}</h3>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  selectedModule.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                  selectedModule.status === 'in_progress' ? 'bg-sky-100 text-sky-700' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {selectedModule.status === 'completed' ? 'Completed' :
                   selectedModule.status === 'in_progress' ? 'In Progress' : 'Not Started'}
                </span>
              </div>

              <div className="flex items-center gap-2 mb-4 text-sm text-gray-500">
                <span>Level {selectedModule.current_level} → {selectedModule.target_level}</span>
                <span className="text-gray-300">|</span>
                <span>{selectedModule.completed_lessons}/{selectedModule.total_lessons} lessons</span>
              </div>

              {/* Lesson list */}
              {selectedModule.lesson_outline && (
                <div className="space-y-2">
                  {selectedModule.lesson_outline.map((lesson, i) => {
                    const isCompleted = i < selectedModule.completed_lessons
                    return (
                      <div
                        key={i}
                        className={`flex items-center gap-3 p-2.5 rounded-lg ${
                          isCompleted ? 'bg-emerald-50' : 'bg-gray-50'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          isCompleted ? 'bg-emerald-500 text-white' : 'bg-gray-300 text-white'
                        }`}>
                          {isCompleted ? '✓' : lesson.lesson_number}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium ${isCompleted ? 'text-emerald-700' : 'text-gray-700'}`}>
                            {lesson.title}
                          </p>
                          <p className="text-[10px] text-gray-400">{lesson.type} · {lesson.estimated_minutes} min</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {/* Next lesson CTA */}
          {dashboard.next_lesson && dashboard.next_lesson_id && dashboard.current_module && (
            <NextLessonCard
              lesson={dashboard.next_lesson}
              lessonId={dashboard.next_lesson_id}
              module={dashboard.current_module}
              onStart={() => navigate(`/learn/${pathId}/lesson/${dashboard.next_lesson_id}`)}
            />
          )}

          {/* All lessons completed */}
          {dashboard.overall_progress >= 100 && (
            <div className="card border-2 border-emerald-200 bg-emerald-50 text-center py-8">
              <div className="text-4xl mb-3">🎉</div>
              <h3 className="text-xl font-bold text-emerald-800">Path Complete!</h3>
              <p className="text-emerald-600 mt-1">
                You've completed all {dashboard.total_lessons} lessons across {dashboard.modules.length} modules.
              </p>
            </div>
          )}
        </div>

        {/* Right: Skill mastery tracker */}
        <div className="lg:col-span-3">
          <SkillGapTracker masteries={dashboard.skill_masteries} />
        </div>
      </div>
    </div>
  )
}
