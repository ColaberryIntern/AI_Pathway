import { useState } from 'react'
import { BarChart3, ChevronDown, ChevronUp, Info, GraduationCap } from 'lucide-react'
import type { Top10SkillGap } from '../types'

interface UnifiedSkillsChartProps {
  gaps: Top10SkillGap[]
  allGaps?: Top10SkillGap[]
}

export default function UnifiedSkillsChart({
  gaps,
  allGaps,
}: UnifiedSkillsChartProps) {
  const [showAllGaps, setShowAllGaps] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  // Priority skills (path skills) — always shown in full
  const priorityGaps = [...gaps]
    .filter(g => g.gap > 0)
    .sort((a, b) => b.gap - a.gap || (a.rank ?? 0) - (b.rank ?? 0))

  // Set of path skill IDs for badge identification
  const pathSkillIds = new Set(priorityGaps.map(g => g.skill_id))

  // Remaining gaps (all gaps minus priority, only when expanded)
  const remainingGaps = (allGaps || [])
    .filter(g => g.gap > 0 && !pathSkillIds.has(g.skill_id))
    .sort((a, b) => b.gap - a.gap || a.skill_id.localeCompare(b.skill_id))

  const hasRemaining = remainingGaps.length > 0

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

  if (priorityGaps.length === 0) return null

  return (
    <div className="card space-y-4">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 className="h-5 w-5 text-indigo-600" />
          <h2 className="text-xl font-bold text-gray-900">Skills Gap Overview</h2>
        </div>
        <p className="text-sm text-gray-500">
          Priority skills addressed in your learning path
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

      {/* Priority Skill Rows (always visible) */}
      <div className="space-y-2">
        {priorityGaps.map((skill) => {
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
                    <span className="text-indigo-500 font-mono text-[11px]">{skill.skill_id}</span>{' '}
                    {skill.skill_name}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium whitespace-nowrap flex-shrink-0">
                    {skill.domain_label || skill.domain}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-violet-100 text-violet-700 rounded font-medium whitespace-nowrap flex-shrink-0 flex items-center gap-0.5">
                    <GraduationCap className="h-2.5 w-2.5" />
                    In your path
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

      {/* Expand to show all remaining skill gaps */}
      {hasRemaining && (
        <>
          <button
            onClick={() => setShowAllGaps(!showAllGaps)}
            className="flex items-center gap-1 mx-auto text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
          >
            {showAllGaps ? (
              <>
                Hide remaining gaps <ChevronUp className="h-4 w-4" />
              </>
            ) : (
              <>
                Show all {remainingGaps.length + priorityGaps.length} skill gaps (+{remainingGaps.length} more) <ChevronDown className="h-4 w-4" />
              </>
            )}
          </button>

          {showAllGaps && (
            <div className="space-y-1 pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-400 mb-2">
                Remaining skill gaps — not addressed in this path
              </p>
              {remainingGaps.map((skill) => {
                const colors = severityColor(skill.gap)
                const currentPct = (skill.current_level / 5) * 100
                const targetPct = (skill.required_level / 5) * 100

                return (
                  <div
                    key={skill.skill_id}
                    className="flex items-center gap-2 p-2 rounded bg-gray-50 border-l-2 border-gray-200"
                  >
                    {/* Skill info */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 mb-1">
                        <span className="text-gray-400 font-mono text-[10px]">{skill.skill_id}</span>
                        <span className="text-xs text-gray-700 truncate">{skill.skill_name}</span>
                        <span className="text-[9px] px-1 py-0.5 bg-gray-100 text-gray-500 rounded flex-shrink-0">
                          {skill.domain_label || skill.domain}
                        </span>
                      </div>
                      {/* Compact inline bars */}
                      <div className="flex items-center gap-1.5">
                        <span className="text-[9px] text-gray-400 w-5">L{skill.current_level}</span>
                        <div className="flex-1 h-1.5 bg-gray-200 rounded overflow-hidden relative">
                          {currentPct > 0 && (
                            <div
                              className="absolute inset-y-0 left-0 bg-sky-400 rounded"
                              style={{ width: `${currentPct}%` }}
                            />
                          )}
                          <div
                            className="absolute inset-y-0 left-0 bg-emerald-400/30 rounded"
                            style={{ width: `${targetPct}%` }}
                          />
                        </div>
                        <span className="text-[9px] text-gray-400 w-5">L{skill.required_level}</span>
                      </div>
                    </div>
                    {/* Gap badge */}
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold flex-shrink-0 ${colors.badge}`}>
                      +{skill.gap}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}
