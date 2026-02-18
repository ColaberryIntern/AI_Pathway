import DomainCard, { type Domain, type DomainState } from './DomainCard'

// 18 domains organized by layer (from ontology_chart.html)
const DOMAINS: Domain[] = [
  // Foundation Layer
  { id: 'D.DIG', label: 'Digital Literacy', layer: 'L.FOUNDATION', skills: 8 },
  { id: 'D.CTIC', label: 'Critical Thinking', layer: 'L.FOUNDATION', skills: 6 },

  // Theory Layer
  { id: 'D.FND', label: 'AI Foundations', layer: 'L.THEORY', skills: 15 },

  // Application Layer
  { id: 'D.PRM', label: 'Prompting & HITL', layer: 'L.APPLICATION', skills: 12 },
  { id: 'D.RAG', label: 'RAG Systems', layer: 'L.APPLICATION', skills: 9 },
  { id: 'D.AGT', label: 'Agents & Orchestration', layer: 'L.APPLICATION', skills: 11 },
  { id: 'D.MOD', label: 'Model Adaptation', layer: 'L.APPLICATION', skills: 6 },
  { id: 'D.MUL', label: 'Multimodal AI', layer: 'L.APPLICATION', skills: 8 },
  { id: 'D.EVL', label: 'Evaluation', layer: 'L.APPLICATION', skills: 8 },
  { id: 'D.SEC', label: 'Safety & Security', layer: 'L.APPLICATION', skills: 7 },
  { id: 'D.OPS', label: 'LLMOps', layer: 'L.APPLICATION', skills: 8 },

  // Tools Layer
  { id: 'D.TOOL', label: 'Tools & Frameworks', layer: 'L.TOOLS', skills: 10 },

  // Tech Prerequisites Layer
  { id: 'D.PRQ', label: 'Tech Prerequisites', layer: 'L.TECH_PREREQ', skills: 12 },

  // Domain Layer
  { id: 'D.GOV', label: 'Governance', layer: 'L.DOMAIN', skills: 6 },
  { id: 'D.DOM', label: 'Domain Apps', layer: 'L.DOMAIN', skills: 8 },

  // Soft/Strategy Layer
  { id: 'D.PRD', label: 'Product & UX', layer: 'L.SOFT', skills: 8 },
  { id: 'D.COM', label: 'Communication', layer: 'L.SOFT', skills: 6 },
  { id: 'D.LRN', label: 'Learning & Adaptation', layer: 'L.SOFT', skills: 5 },
]

interface DomainGridProps {
  highlightedDomains: string[]
  activeDomain: string | null
  completedDomains: string[]
  selectedDomains?: { domainId: string; chapterNum: number }[]
}

export default function DomainGrid({
  highlightedDomains,
  activeDomain,
  completedDomains,
  selectedDomains = [],
}: DomainGridProps) {
  const getDomainState = (domainId: string): DomainState => {
    // Check if selected for learning path (highest priority)
    const selectedEntry = selectedDomains.find(s => s.domainId === domainId)
    if (selectedEntry) {
      return 'selected'
    }

    // Check if currently active (being analyzed)
    if (activeDomain === domainId) {
      return 'active'
    }

    // Check if completed
    if (completedDomains.includes(domainId)) {
      return 'complete'
    }

    // Check if highlighted (part of current scan)
    if (highlightedDomains.includes(domainId)) {
      return 'active'
    }

    // Default: dimmed
    return 'dimmed'
  }

  const getChapterNum = (domainId: string): number | undefined => {
    const entry = selectedDomains.find(s => s.domainId === domainId)
    return entry?.chapterNum
  }

  return (
    <div className="w-full">
      {/* Grid container - 6 columns on large, 3 on medium, 2 on small */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
        {DOMAINS.map((domain) => (
          <DomainCard
            key={domain.id}
            domain={domain}
            state={getDomainState(domain.id)}
            chapterNum={getChapterNum(domain.id)}
          />
        ))}
      </div>

      {/* Legend - updated for light theme */}
      <div className="flex flex-wrap justify-center gap-4 mt-4 text-xs text-gray-600">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded border-2 border-sky-500 bg-sky-50" />
          <span>Analyzing</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded border-2 border-green-500 bg-green-50" />
          <span>Complete</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded border-2 border-indigo-600 bg-gradient-to-br from-indigo-100 to-purple-100 ring-1 ring-indigo-400" />
          <span className="font-medium text-indigo-700">In Your Path</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded border-2 border-gray-200 bg-gray-50 opacity-50" />
          <span>Pending</span>
        </div>
      </div>
    </div>
  )
}

export { DOMAINS }
export type { Domain }
