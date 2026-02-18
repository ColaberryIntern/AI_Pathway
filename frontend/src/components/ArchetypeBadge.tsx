type Archetype = 'Career Switcher' | 'Domain Upskiller' | 'Executive' | 'Technical Pivot'

interface ArchetypeBadgeProps {
  archetype: Archetype | undefined
  size?: 'sm' | 'md'
}

const archetypeConfig: Record<Archetype, { bg: string; text: string; description: string }> = {
  'Career Switcher': {
    bg: 'bg-blue-100',
    text: 'text-blue-700',
    description: 'Moving from non-AI field to AI-focused role',
  },
  'Domain Upskiller': {
    bg: 'bg-green-100',
    text: 'text-green-700',
    description: 'Adding AI/data science skills to existing domain expertise',
  },
  'Executive': {
    bg: 'bg-purple-100',
    text: 'text-purple-700',
    description: 'C-level/VP learning AI for strategy and governance',
  },
  'Technical Pivot': {
    bg: 'bg-orange-100',
    text: 'text-orange-700',
    description: 'Technical role transitioning to AI-focused technical role',
  },
}

export default function ArchetypeBadge({ archetype, size = 'md' }: ArchetypeBadgeProps) {
  if (!archetype) return null

  const config = archetypeConfig[archetype]
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-2.5 py-1'

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${config.bg} ${config.text} ${sizeClasses}`}
      title={config.description}
    >
      {archetype}
    </span>
  )
}
