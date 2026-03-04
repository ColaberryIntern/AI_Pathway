import { Play, Clock, BookOpen, Code2, ClipboardCheck } from 'lucide-react'
import type { LessonOutline, LearningModule } from '../../types'

interface NextLessonCardProps {
  lesson: LessonOutline
  lessonId: string
  module: LearningModule
  onStart: () => void
}

const typeConfig = {
  concept: { icon: BookOpen, label: 'Concept Lesson', color: 'text-indigo-600 bg-indigo-100' },
  practice: { icon: Code2, label: 'Practice Lesson', color: 'text-emerald-600 bg-emerald-100' },
  assessment: { icon: ClipboardCheck, label: 'Assessment', color: 'text-amber-600 bg-amber-100' },
}

export default function NextLessonCard({ lesson, module, onStart }: NextLessonCardProps) {
  const config = typeConfig[lesson.type] || typeConfig.concept
  const TypeIcon = config.icon

  return (
    <div className="card border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-white">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">Next Lesson</span>
      </div>

      <div className="space-y-3">
        {/* Module context */}
        <div className="text-xs text-gray-500">
          Module {module.chapter_number}: {module.title}
        </div>

        {/* Lesson info */}
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${config.color}`}>
            <TypeIcon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900">{lesson.title}</h4>
            <p className="text-sm text-gray-500 mt-0.5">{lesson.focus_area}</p>
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${config.color}`}>
                {config.label}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {lesson.estimated_minutes} min
              </span>
            </div>
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={onStart}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-indigo-600 to-sky-600 text-white font-medium rounded-lg hover:from-indigo-700 hover:to-sky-700 transition-all shadow-sm hover:shadow-md"
        >
          <Play className="h-4 w-4" />
          Start Lesson
        </button>
      </div>
    </div>
  )
}
