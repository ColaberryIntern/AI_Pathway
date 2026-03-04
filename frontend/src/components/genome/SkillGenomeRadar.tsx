import { Dna } from 'lucide-react'
import type { SkillGenomeEntry } from '../../types'

interface SkillGenomeRadarProps {
  entries: SkillGenomeEntry[]
}

function getDomainColor(index: number): { bg: string; bar: string; text: string } {
  const colors = [
    { bg: 'bg-indigo-50', bar: 'bg-indigo-500', text: 'text-indigo-700' },
    { bg: 'bg-emerald-50', bar: 'bg-emerald-500', text: 'text-emerald-700' },
    { bg: 'bg-amber-50', bar: 'bg-amber-500', text: 'text-amber-700' },
    { bg: 'bg-rose-50', bar: 'bg-rose-500', text: 'text-rose-700' },
    { bg: 'bg-sky-50', bar: 'bg-sky-500', text: 'text-sky-700' },
    { bg: 'bg-violet-50', bar: 'bg-violet-500', text: 'text-violet-700' },
    { bg: 'bg-orange-50', bar: 'bg-orange-500', text: 'text-orange-700' },
    { bg: 'bg-teal-50', bar: 'bg-teal-500', text: 'text-teal-700' },
  ]
  return colors[index % colors.length]
}

export default function SkillGenomeRadar({ entries }: SkillGenomeRadarProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-12 space-y-3">
        <div className="mx-auto w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
          <Dna className="h-8 w-8 text-gray-400" />
        </div>
        <p className="text-sm text-gray-500">No skills tracked yet.</p>
        <p className="text-xs text-gray-400">Complete lessons to build your Skill Genome.</p>
      </div>
    )
  }

  // Group by domain
  const domainGroups: Record<string, SkillGenomeEntry[]> = {}
  for (const entry of entries) {
    const domain = entry.domain || 'Other'
    if (!domainGroups[domain]) domainGroups[domain] = []
    domainGroups[domain].push(entry)
  }

  // Sort domains by average mastery (highest first)
  const sortedDomains = Object.entries(domainGroups).sort((a, b) => {
    const avgA = a[1].reduce((s, e) => s + e.mastery_level, 0) / a[1].length
    const avgB = b[1].reduce((s, e) => s + e.mastery_level, 0) / b[1].length
    return avgB - avgA
  })

  // Calculate overall stats
  const avgMastery = entries.reduce((s, e) => s + e.mastery_level, 0) / entries.length
  const totalEvidence = entries.reduce((s, e) => s + e.evidence_count, 0)

  return (
    <div className="space-y-6">
      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-indigo-50 rounded-xl">
          <p className="text-2xl font-bold text-indigo-700">{entries.length}</p>
          <p className="text-[10px] text-indigo-500 uppercase tracking-wider">Skills Tracked</p>
        </div>
        <div className="text-center p-3 bg-emerald-50 rounded-xl">
          <p className="text-2xl font-bold text-emerald-700">{avgMastery.toFixed(1)}</p>
          <p className="text-[10px] text-emerald-500 uppercase tracking-wider">Avg Mastery</p>
        </div>
        <div className="text-center p-3 bg-amber-50 rounded-xl">
          <p className="text-2xl font-bold text-amber-700">{totalEvidence}</p>
          <p className="text-[10px] text-amber-500 uppercase tracking-wider">Total Evidence</p>
        </div>
      </div>

      {/* Domain mastery bars */}
      <div className="space-y-4">
        {sortedDomains.map(([domain, skills], domainIdx) => {
          const color = getDomainColor(domainIdx)
          const domainAvg = skills.reduce((s, e) => s + e.mastery_level, 0) / skills.length

          return (
            <div key={domain} className={`${color.bg} rounded-xl p-4`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className={`text-sm font-semibold ${color.text}`}>{domain}</h3>
                <span className="text-xs text-gray-500">{skills.length} skill{skills.length !== 1 ? 's' : ''}</span>
              </div>

              {/* Domain average bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-gray-500">Domain Average</span>
                  <span className="text-xs font-semibold text-gray-700">{domainAvg.toFixed(1)} / 4.0</span>
                </div>
                <div className="h-2.5 bg-white/60 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${color.bar} transition-all duration-700`}
                    style={{ width: `${(domainAvg / 4) * 100}%` }}
                  />
                </div>
              </div>

              {/* Individual skills */}
              <div className="space-y-1.5">
                {skills
                  .sort((a, b) => b.mastery_level - a.mastery_level)
                  .map((skill) => (
                    <div key={skill.ontology_node_id} className="flex items-center gap-2">
                      <span className="text-xs text-gray-600 w-32 truncate">{skill.skill_name}</span>
                      <div className="flex-1 h-1.5 bg-white/60 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${color.bar} opacity-70 transition-all duration-500`}
                          style={{ width: `${(skill.mastery_level / 4) * 100}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-gray-500 w-8 text-right">{skill.mastery_level.toFixed(1)}</span>
                    </div>
                  ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
