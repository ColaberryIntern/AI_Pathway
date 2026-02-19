import { useState } from 'react'
import { BarChart3, ChevronDown, ChevronUp, Info } from 'lucide-react'
import type { Top10SkillGap } from '../types'

interface UnifiedSkillsChartProps {
  gaps: Top10SkillGap[]
  defaultVisibleCount?: number
}

export default function UnifiedSkillsChart({
  gaps,
  defaultVisibleCount = 5,
}: UnifiedSkillsChartProps) {
  const [showAll, setShowAll] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const sortedGaps = [...gaps]
    .filter(g => g.gap > 0)
    .sort((a, b) => b.gap - a.gap || a.rank - b.rank)

  const visibleGaps = showAll ? sortedGaps : sortedGaps.slice(0, defaultVisibleCount)
  const hasMore = sortedGaps.length > defaultVisibleCount

  const toggleRationale = (skillId: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(skillId)) next.delete(skillId)
      else next.add(skillId)
      return next
    })
  }

  const severityColor = (gap: number) => {
    if (gap >= 3) return { border: 'border-l-red-400', badge: 'bg-red-100 text-red-700' }
    if (gap >= 1) return { border: 'border-l-amber-400', badge: 'bg-amber-100 text-amber-700' }
    return { border: 'border-l-green-400', badge: 'bg-green-100 text-green-700' }
  }

  if (sortedGaps.length === 0) return null

  return (
    <div className="card space-y-4">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 className="h-5 w-5 text-indigo-600" />
          <h2 className="text-xl font-bold text-gray-900">Skills Gap Overview</h2>
        </div>
        <p className="text-sm text-gray-500">
          Your current skills vs. what the target role requires
        </p>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-sky-500" />
          You (Current)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-emerald-500" />
          Target (Required)
        </span>
        <span className="ml-auto text-gray-400">L0 – L5 scale</span>
      </div>

      {/* Skill Rows */}
      <div className="space-y-2">
        {visibleGaps.map((skill) => {
          const colors = severityColor(skill.gap)
          const isExpanded = expandedIds.has(skill.skill_id)
          const currentPct = (skill.current_level / 5) * 100
          const targetPct = (skill.required_level / 5) * 100

          return (
            <div
              key={skill.skill_id}
              className={`p-3 rounded-lg border-l-4 ${colors.border} bg-gray-50`}
            >
              {/* Title row */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-medium text-gray-900 text-sm truncate">
                    {skill.skill_name}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium whitespace-nowrap flex-shrink-0">
                    {skill.domain_label || skill.domain}
                  </span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded font-bold flex-shrink-0 ${colors.badge}`}>
                  Gap: +{skill.gap}
                </span>
              </div>

              {/* Two-row bars */}
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] w-10 font-medium text-gray-500 text-right">You</span>
                  <div className="flex-1 h-3.5 bg-gray-200 rounded overflow-hidden">
                    {currentPct > 0 && (
                      <div
                        className="h-full bg-sky-500 rounded transition-all duration-700 ease-out"
                        style={{ width: `${currentPct}%` }}
                      />
                    )}
                  </div>
                  <span className="text-[10px] font-bold text-sky-600 w-6">L{skill.current_level}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] w-10 font-medium text-gray-500 text-right">Target</span>
                  <div className="flex-1 h-3.5 bg-gray-200 rounded overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded transition-all duration-700 ease-out"
                      style={{ width: `${targetPct}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-bold text-emerald-600 w-6">L{skill.required_level}</span>
                </div>
              </div>

              {/* Expandable rationale */}
              {skill.rationale && (
                <>
                  <button
                    onClick={() => toggleRationale(skill.skill_id)}
                    className="flex items-center gap-1 mt-1.5 text-[11px] text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <Info className="h-3 w-3" />
                    {isExpanded ? 'Hide detail' : 'Why this matters'}
                  </button>
                  {isExpanded && (
                    <p className="text-xs text-gray-600 leading-relaxed mt-1 pl-4 border-l-2 border-gray-200 italic">
                      {skill.rationale}
                    </p>
                  )}
                </>
              )}
            </div>
          )
        })}
      </div>

      {/* Show more / less */}
      {hasMore && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="flex items-center gap-1 mx-auto text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
        >
          {showAll ? (
            <>
              Show fewer <ChevronUp className="h-4 w-4" />
            </>
          ) : (
            <>
              Show all {sortedGaps.length} skills <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      )}
    </div>
  )
}
