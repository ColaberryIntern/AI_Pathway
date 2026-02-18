import { useEffect, useRef, useState } from 'react'

// Domain card states
export type DomainState = 'dimmed' | 'active' | 'complete' | 'selected'

// Layer color mapping
const layerColors: Record<string, string> = {
  'L.FOUNDATION': '#22c55e',    // Green
  'L.THEORY': '#6366f1',        // Indigo
  'L.APPLICATION': '#0ea5e9',   // Sky (changed from cyan for light theme)
  'L.TOOLS': '#10b981',         // Emerald
  'L.TECH_PREREQ': '#f59e0b',   // Amber
  'L.DOMAIN': '#ec4899',        // Pink
  'L.SOFT': '#8b5cf6',          // Purple
}

export interface Domain {
  id: string
  label: string
  layer: string
  skills: number
  description?: string
}

interface DomainCardProps {
  domain: Domain
  state: DomainState
  chapterNum?: number
}

export default function DomainCard({ domain, state, chapterNum }: DomainCardProps) {
  const layerColor = layerColors[domain.layer] || '#374151'
  const prevStateRef = useRef<DomainState>(state)
  const [justCompleted, setJustCompleted] = useState(false)

  // Detect when transitioning from active to complete
  useEffect(() => {
    if (prevStateRef.current === 'active' && state === 'complete') {
      setJustCompleted(true)
      const timer = setTimeout(() => setJustCompleted(false), 600)
      return () => clearTimeout(timer)
    }
    prevStateRef.current = state
  }, [state])

  const isActive = state === 'active'
  const isComplete = state === 'complete'
  const isSelected = state === 'selected'

  return (
    <div
      className={`
        domain-card
        bg-white border-2 rounded-xl p-3
        shadow-sm hover:shadow-md
        transition-all duration-500 ease-out
        ${state === 'dimmed' ? 'opacity-40 bg-gray-50 border-gray-200' : ''}
        ${isActive ? 'opacity-100 border-sky-500 bg-gradient-to-br from-sky-50 via-cyan-50 to-blue-50 ring-2 ring-sky-400/50 ring-offset-1 shadow-xl shadow-sky-200/70 scale-[1.03] animate-active-glow' : ''}
        ${isComplete ? `opacity-100 border-green-500 bg-green-50 ${justCompleted ? 'animate-complete-flash' : ''}` : ''}
        ${isSelected ? 'opacity-100 border-indigo-600 bg-gradient-to-br from-indigo-100 to-purple-100 ring-2 ring-indigo-400 ring-offset-2 shadow-lg shadow-indigo-200/50 scale-[1.02]' : ''}
      `}
    >
      {/* Header with layer dot and ID */}
      <div className="flex items-center gap-2 mb-1">
        <div
          className={`w-2 h-2 rounded-full flex-shrink-0 transition-all duration-300 ${isActive ? 'animate-pulse' : ''} ${justCompleted ? 'scale-150' : ''}`}
          style={{ backgroundColor: layerColor }}
        />
        <span className={`text-[10px] font-mono transition-colors duration-300 ${isSelected ? 'text-indigo-600' : isActive ? 'text-sky-600' : isComplete ? 'text-green-600' : 'text-gray-400'}`}>
          {domain.id}
        </span>
      </div>

      {/* Domain label */}
      <h3 className={`text-xs font-semibold leading-tight mb-1 transition-colors duration-300 ${isSelected ? 'text-indigo-900' : isActive ? 'text-sky-900' : isComplete ? 'text-green-900' : 'text-gray-900'}`}>
        {domain.label}
      </h3>

      {/* Skills count */}
      <div className={`text-[10px] transition-colors duration-300 ${isSelected ? 'text-indigo-600' : isActive ? 'text-sky-600' : isComplete ? 'text-green-600' : 'text-gray-500'}`}>
        {domain.skills} skills
      </div>

      {/* Status badge container - always present for smooth transitions */}
      <div className="mt-2 h-5 relative">
        {/* Active badge */}
        <div className={`absolute inset-0 transition-all duration-300 ${isActive ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-1 pointer-events-none'}`}>
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-gradient-to-r from-sky-500 to-cyan-500 text-white rounded-full text-[10px] font-bold shadow-md animate-pulse">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
            </span>
            Scanning...
          </span>
        </div>

        {/* Complete badge */}
        <div className={`absolute inset-0 transition-all duration-300 ${isComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1 pointer-events-none'}`}>
          <span className={`inline-flex items-center gap-1 text-[10px] text-green-600 font-medium ${justCompleted ? 'animate-bounce-in' : ''}`}>
            <svg className={`w-3 h-3 ${justCompleted ? 'animate-check-draw' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            Analyzed
          </span>
        </div>

        {/* Selected badge */}
        <div className={`absolute inset-0 transition-all duration-300 ${isSelected && chapterNum !== undefined ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1 pointer-events-none'}`}>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-indigo-600 text-white rounded-full text-[10px] font-bold shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
            Chapter {chapterNum}
          </span>
        </div>
      </div>
    </div>
  )
}
