import { useState } from 'react'
import { Info } from 'lucide-react'
import type { ParsedSkill } from '../types'

const DEFAULT_PROFICIENCY_DESCRIPTIONS = [
  { level: 0, label: 'No Experience', description: 'No exposure to this skill area yet.' },
  { level: 1, label: 'Aware', description: 'Can explain the concept. Entry-level familiarity.' },
  { level: 2, label: 'User', description: 'Can apply with guidance. Uses existing tools and frameworks.' },
  { level: 3, label: 'Practitioner', description: 'Adapts independently. Configures, customizes, and troubleshoots.' },
  { level: 4, label: 'Builder', description: 'Ships production solutions. Designs and implements end-to-end.' },
]

const LEVEL_COLORS: Record<number, { bg: string; border: string; text: string; selectedBg: string }> = {
  0: { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-600', selectedBg: 'bg-gray-200' },
  1: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-700', selectedBg: 'bg-blue-200' },
  2: { bg: 'bg-cyan-50', border: 'border-cyan-300', text: 'text-cyan-700', selectedBg: 'bg-cyan-200' },
  3: { bg: 'bg-amber-50', border: 'border-amber-300', text: 'text-amber-700', selectedBg: 'bg-amber-200' },
  4: { bg: 'bg-emerald-50', border: 'border-emerald-300', text: 'text-emerald-700', selectedBg: 'bg-emerald-200' },
}

interface SelfAssessmentProps {
  skills: ParsedSkill[]
  assessments: Record<string, number>
  onAssess: (skillId: string, level: number) => void
}

export default function SelfAssessment({ skills, assessments, onAssess }: SelfAssessmentProps) {
  const [hoveredTooltip, setHoveredTooltip] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Rate Your Current Proficiency
        </h2>
        <p className="text-gray-600">
          For each skill, select the level that best describes your current ability.
          Hover over each level for a description.
        </p>
      </div>

      {skills.map((skill) => {
        const selectedLevel = assessments[skill.skill_id]
        const descriptions = (skill.proficiency_descriptions && skill.proficiency_descriptions.length > 0)
          ? skill.proficiency_descriptions
          : DEFAULT_PROFICIENCY_DESCRIPTIONS

        return (
          <div
            key={skill.skill_id}
            className="card border border-gray-200 bg-white"
          >
            {/* Skill Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900">{skill.skill_name}</h3>
                  <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full border border-primary-200">
                    {skill.domain_label}
                  </span>
                  {skill.importance === 'high' && (
                    <span className="text-xs bg-red-50 text-red-700 px-2 py-0.5 rounded-full border border-red-200">
                      Critical
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-4">
                <span className="text-xs text-gray-400">Target</span>
                <div className="text-sm font-semibold text-primary-700">
                  Level {skill.required_level}
                </div>
              </div>
            </div>

            {/* Proficiency Level Buttons */}
            <div className="flex flex-wrap gap-2 relative">
              {descriptions.map((desc) => {
                const isSelected = selectedLevel === desc.level
                const colors = LEVEL_COLORS[desc.level] || LEVEL_COLORS[0]
                const isTarget = desc.level === skill.required_level
                const tooltipId = `${skill.skill_id}-${desc.level}`

                return (
                  <div key={desc.level} className="relative">
                    <button
                      onClick={() => onAssess(skill.skill_id, desc.level)}
                      onMouseEnter={() => setHoveredTooltip(tooltipId)}
                      onMouseLeave={() => setHoveredTooltip(null)}
                      className={`
                        px-3 py-2 rounded-lg border-2 text-sm font-medium
                        transition-all duration-150 cursor-pointer
                        ${isSelected
                          ? `${colors.selectedBg} ${colors.border} ${colors.text} ring-2 ring-offset-1 ring-${colors.border.replace('border-', '')}`
                          : `${colors.bg} border-gray-200 text-gray-600 hover:${colors.border}`
                        }
                        ${isTarget ? 'ring-1 ring-primary-400' : ''}
                      `}
                    >
                      <div className="flex items-center gap-1">
                        <span className="font-bold">{desc.level}</span>
                        <span className="hidden sm:inline">{desc.label}</span>
                        <Info className="h-3 w-3 text-gray-400" />
                      </div>
                    </button>

                    {/* Tooltip */}
                    {hoveredTooltip === tooltipId && (
                      <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg pointer-events-none">
                        <div className="font-semibold mb-1">
                          Level {desc.level}: {desc.label}
                        </div>
                        <div className="text-gray-300">{desc.description}</div>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 w-2 h-2 bg-gray-900 rotate-45" />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Selected Level Summary */}
            {selectedLevel !== undefined && (
              <div className="mt-3 text-sm">
                <span className="text-gray-500">Your level: </span>
                <span className="font-medium text-gray-700">
                  {selectedLevel} — {descriptions.find(d => d.level === selectedLevel)?.label}
                </span>
                {selectedLevel < skill.required_level && (
                  <span className="ml-2 text-amber-600">
                    (Gap: {skill.required_level - selectedLevel} level{skill.required_level - selectedLevel > 1 ? 's' : ''})
                  </span>
                )}
                {selectedLevel >= skill.required_level && (
                  <span className="ml-2 text-emerald-600">
                    (Meets target)
                  </span>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
