import { CheckCircle2, Circle, PlayCircle, BookOpen, Code2, ClipboardCheck } from 'lucide-react'
import type { LearningModule } from '../../types'

interface ModuleSidebarProps {
  modules: LearningModule[]
  currentModuleId: string | null
  onModuleClick: (moduleId: string) => void
}

const typeIcon = {
  concept: BookOpen,
  practice: Code2,
  assessment: ClipboardCheck,
}

export default function ModuleSidebar({ modules, currentModuleId, onModuleClick }: ModuleSidebarProps) {
  return (
    <nav className="space-y-2">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Modules</h3>
      {modules.map((mod) => {
        const isActive = mod.id === currentModuleId
        const StatusIcon =
          mod.status === 'completed' ? CheckCircle2 :
          mod.status === 'in_progress' ? PlayCircle : Circle

        const statusColor =
          mod.status === 'completed' ? 'text-emerald-500' :
          mod.status === 'in_progress' ? 'text-sky-500' : 'text-gray-300'

        return (
          <button
            key={mod.id}
            onClick={() => onModuleClick(mod.id)}
            className={`w-full text-left p-3 rounded-lg border transition-all ${
              isActive
                ? 'border-indigo-300 bg-indigo-50 shadow-sm'
                : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start gap-2.5">
              <StatusIcon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${statusColor}`} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-indigo-500">{mod.skill_id}</span>
                  <span className="text-[10px] text-gray-400">L{mod.current_level}→L{mod.target_level}</span>
                </div>
                <p className={`text-sm font-medium truncate ${isActive ? 'text-indigo-900' : 'text-gray-900'}`}>
                  {mod.title}
                </p>
                {/* Progress bar */}
                <div className="mt-1.5 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${mod.total_lessons > 0 ? (mod.completed_lessons / mod.total_lessons) * 100 : 0}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-gray-400 whitespace-nowrap">
                    {mod.completed_lessons}/{mod.total_lessons}
                  </span>
                </div>
                {/* Lesson type pills */}
                {mod.lesson_outline && (
                  <div className="flex gap-1 mt-1.5 flex-wrap">
                    {mod.lesson_outline.map((lesson, i) => {
                      const Icon = typeIcon[lesson.type] || BookOpen
                      return (
                        <span
                          key={i}
                          className="inline-flex items-center gap-0.5 text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
                          title={lesson.title}
                        >
                          <Icon className="h-2.5 w-2.5" />
                          {lesson.type}
                        </span>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </button>
        )
      })}
    </nav>
  )
}
