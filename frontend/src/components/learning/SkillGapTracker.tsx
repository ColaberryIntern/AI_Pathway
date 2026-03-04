import { TrendingUp } from 'lucide-react'
import type { SkillMastery } from '../../types'

interface SkillGapTrackerProps {
  masteries: SkillMastery[]
}

export default function SkillGapTracker({ masteries }: SkillGapTrackerProps) {
  if (!masteries.length) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <TrendingUp className="h-4 w-4 text-emerald-600" />
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Skill Mastery</h3>
      </div>

      {masteries.map((m) => {
        const initialPct = (m.initial_level / 5) * 100
        const currentPct = (m.current_level / 5) * 100
        const targetPct = (m.target_level / 5) * 100

        return (
          <div key={m.skill_id} className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-700 truncate">{m.skill_name}</span>
              <span className="text-[10px] text-gray-400 whitespace-nowrap ml-2">
                L{m.current_level.toFixed(1)} / L{m.target_level}
              </span>
            </div>
            <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
              {/* Target marker */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-emerald-600 z-10"
                style={{ left: `${targetPct}%` }}
                title={`Target: L${m.target_level}`}
              />
              {/* Initial level (faded) */}
              {initialPct > 0 && (
                <div
                  className="absolute top-0 bottom-0 bg-gray-300 rounded-full"
                  style={{ width: `${initialPct}%` }}
                />
              )}
              {/* Current level */}
              <div
                className="absolute top-0 bottom-0 bg-sky-500 rounded-full transition-all duration-700"
                style={{ width: `${currentPct}%` }}
              />
            </div>
            {/* Progress % */}
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-400">
                {m.lessons_completed}/{m.total_lessons} lessons
              </span>
              <span className={`text-[10px] font-medium ${
                m.progress_percentage >= 100 ? 'text-emerald-600' :
                m.progress_percentage > 0 ? 'text-sky-600' : 'text-gray-400'
              }`}>
                {m.progress_percentage.toFixed(0)}%
              </span>
            </div>
          </div>
        )
      })}

      {/* Legend */}
      <div className="flex items-center gap-3 pt-2 border-t border-gray-100 text-[10px] text-gray-400">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-sm bg-sky-500" /> Current
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-0.5 bg-emerald-600" /> Target
        </span>
      </div>
    </div>
  )
}
