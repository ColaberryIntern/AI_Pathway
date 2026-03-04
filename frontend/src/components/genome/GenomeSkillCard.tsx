import { Dna, TrendingUp, Zap } from 'lucide-react'
import type { SkillGenomeEntry } from '../../types'

interface GenomeSkillCardProps {
  entry: SkillGenomeEntry
}

const MASTERY_LABELS: Record<number, string> = {
  0: 'Novice',
  1: 'Beginner',
  2: 'Intermediate',
  3: 'Advanced',
  4: 'Expert',
}

function getMasteryLabel(level: number): string {
  const rounded = Math.round(level)
  return MASTERY_LABELS[rounded] ?? 'Unknown'
}

function getMasteryColor(level: number): string {
  if (level >= 3.5) return 'text-emerald-600 bg-emerald-100'
  if (level >= 2.5) return 'text-blue-600 bg-blue-100'
  if (level >= 1.5) return 'text-amber-600 bg-amber-100'
  return 'text-gray-600 bg-gray-100'
}

function getBarColor(level: number): string {
  if (level >= 3.5) return 'bg-emerald-500'
  if (level >= 2.5) return 'bg-blue-500'
  if (level >= 1.5) return 'bg-amber-500'
  return 'bg-gray-400'
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High'
  if (confidence >= 0.4) return 'Medium'
  return 'Low'
}

export default function GenomeSkillCard({ entry }: GenomeSkillCardProps) {
  const pct = Math.min(100, (entry.mastery_level / 4) * 100)

  return (
    <div className="card border border-gray-200 hover:border-indigo-200 hover:shadow-md transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg bg-indigo-100 flex-shrink-0">
            <Dna className="h-4 w-4 text-indigo-600" />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 truncate">{entry.skill_name}</h3>
            {entry.domain && (
              <p className="text-[10px] text-gray-400 uppercase tracking-wider">{entry.domain}</p>
            )}
          </div>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${getMasteryColor(entry.mastery_level)}`}>
          {getMasteryLabel(entry.mastery_level)}
        </span>
      </div>

      {/* Mastery bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-gray-500">Mastery</span>
          <span className="text-xs font-semibold text-gray-700">{entry.mastery_level.toFixed(1)} / 4.0</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getBarColor(entry.mastery_level)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Meta info */}
      <div className="flex items-center gap-3 text-[10px] text-gray-500">
        <div className="flex items-center gap-1">
          <TrendingUp className="h-3 w-3" />
          {entry.evidence_count} evidence{entry.evidence_count !== 1 ? 's' : ''}
        </div>
        <div className="flex items-center gap-1">
          <Zap className="h-3 w-3" />
          Confidence: {getConfidenceLabel(entry.confidence)}
        </div>
        {entry.last_evidence && (
          <span className="ml-auto text-gray-400">
            Last: {entry.last_evidence}
          </span>
        )}
      </div>
    </div>
  )
}
