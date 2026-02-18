import { useState } from 'react'
import { ChevronDown, ChevronUp, Info } from 'lucide-react'

interface ProficiencyLegendProps {
  defaultExpanded?: boolean
  variant?: 'collapsible' | 'inline' | 'compact' | 'static'
}

const proficiencyLevels = [
  { level: 'L0', name: 'No knowledge', description: 'No exposure to the concept or skill' },
  { level: 'L1', name: 'Awareness', description: 'Basic understanding of concepts' },
  { level: 'L2', name: 'Practical', description: 'Can apply with guidance' },
  { level: 'L3', name: 'Independent', description: 'Can execute independently' },
  { level: 'L4', name: 'Expert', description: 'Can teach and lead others' },
]

export function getProficiencyLevel(aiExposure: string | undefined): string {
  switch (aiExposure) {
    case 'None':
      return 'L0'
    case 'Basic':
      return 'L1'
    case 'Intermediate':
      return 'L2'
    case 'Advanced':
      return 'L3'
    default:
      return 'L0'
  }
}

export function getProficiencyDescription(level: string): string {
  const found = proficiencyLevels.find((p) => p.level === level)
  return found ? found.name : ''
}

export default function ProficiencyLegend({
  defaultExpanded = false,
  variant = 'collapsible',
}: ProficiencyLegendProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  if (variant === 'compact') {
    return (
      <div className="flex items-center gap-1 text-xs text-gray-500" title="Proficiency Framework">
        <Info className="h-3 w-3" />
        <span>L0-L4 scale</span>
      </div>
    )
  }

  if (variant === 'inline') {
    return (
      <div className="flex flex-wrap gap-2 text-xs text-gray-600">
        {proficiencyLevels.map((p) => (
          <span key={p.level} className="whitespace-nowrap">
            <span className="font-semibold">{p.level}</span>: {p.name}
          </span>
        ))}
      </div>
    )
  }

  if (variant === 'static') {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3">
        <div className="flex items-center gap-2 mb-2">
          <Info className="h-4 w-4 text-gray-500" />
          <span className="font-medium text-gray-700">Proficiency Framework</span>
        </div>
        <div className="grid grid-cols-5 gap-3">
          {proficiencyLevels.map((p) => (
            <div key={p.level} className="text-sm">
              <span className="font-semibold text-gray-900">{p.level}</span>
              <span className="text-gray-600">: {p.name}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Skills are rated on a 0-4 scale, from no knowledge to expert/teaching capability.
        </p>
      </div>
    )
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-gray-500" />
          <span className="font-medium text-gray-700">Proficiency Framework</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 py-3 bg-white">
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
            {proficiencyLevels.map((p) => (
              <div key={p.level} className="text-sm">
                <span className="font-semibold text-gray-900">{p.level}</span>
                <span className="text-gray-600">: {p.name}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Skills are rated on a 0-4 scale, from no knowledge to expert/teaching capability.
          </p>
        </div>
      )}
    </div>
  )
}
