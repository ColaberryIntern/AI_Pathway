import { BarChart3, ArrowRight } from 'lucide-react'

const MAX_LEVEL = 5
const LEVEL_LABELS = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']

interface SkillsGapChartProps {
  chapters: Array<{
    chapter_number?: number
    skill_id?: string
    skill_name?: string
    title?: string
    current_level?: number
    target_level?: number
  }>
}

export default function SkillsGapChart({ chapters }: SkillsGapChartProps) {
  if (!chapters.length) return null

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-5">
        <BarChart3 className="h-5 w-5 text-indigo-600" />
        <h2 className="text-xl font-bold text-gray-900">
          Skills Gap Overview
        </h2>
      </div>

      <div className="space-y-4">
        {chapters.map((ch) => {
          const current = ch.current_level ?? 0
          const target = ch.target_level ?? 1
          const currentPct = (current / MAX_LEVEL) * 100
          const gapPct = ((target - current) / MAX_LEVEL) * 100
          const remainingPct = ((MAX_LEVEL - target) / MAX_LEVEL) * 100

          return (
            <div key={ch.chapter_number}>
              {/* Skill label row */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-xs flex-shrink-0">
                    {ch.chapter_number}
                  </span>
                  <span className="text-sm font-medium text-gray-700 truncate">
                    {ch.skill_name || ch.title}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-xs flex-shrink-0 ml-2">
                  <span className="font-semibold text-sky-600">L{current}</span>
                  <ArrowRight className="h-3 w-3 text-gray-400" />
                  <span className="font-semibold text-amber-600">L{target}</span>
                </div>
              </div>

              {/* Bar */}
              <div className="h-5 bg-gray-100 rounded-full overflow-hidden flex">
                {currentPct > 0 && (
                  <div
                    className="bg-sky-500 transition-all duration-700 ease-out"
                    style={{ width: `${currentPct}%` }}
                  />
                )}
                <div
                  className="bg-amber-400 transition-all duration-700 ease-out"
                  style={{ width: `${gapPct}%` }}
                />
                {remainingPct > 0 && (
                  <div
                    className="bg-gray-200 transition-all duration-700 ease-out"
                    style={{ width: `${remainingPct}%` }}
                  />
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Scale markers */}
      <div className="flex justify-between mt-2 text-[10px] text-gray-400 px-0">
        {LEVEL_LABELS.map((label) => (
          <span key={label} className="w-6 text-center">{label}</span>
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-5 mt-4 pt-3 border-t border-gray-100 text-xs text-gray-600">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-sky-500" />
          <span>Current Level</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-amber-400" />
          <span>Learning Gap</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gray-200 border border-gray-300" />
          <span>Future Growth</span>
        </div>
      </div>
    </div>
  )
}
