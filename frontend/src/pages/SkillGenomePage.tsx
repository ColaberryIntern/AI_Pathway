import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Dna, ArrowLeft, Loader2, Compass } from 'lucide-react'
import { getSkillGenome } from '../services/api'
import SkillGenomeRadar from '../components/genome/SkillGenomeRadar'
import GenomeSkillCard from '../components/genome/GenomeSkillCard'
import { useState } from 'react'

export default function SkillGenomePage() {
  const { userId } = useParams<{ userId: string }>()
  const [domainFilter, setDomainFilter] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['skill-genome', userId],
    queryFn: () => getSkillGenome(userId!),
    enabled: !!userId,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-3">
          <Loader2 className="h-8 w-8 text-indigo-500 animate-spin mx-auto" />
          <p className="text-sm text-gray-500">Loading Skill Genome...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-3">
          <p className="text-sm text-red-600">Failed to load Skill Genome.</p>
          <Link to="/" className="text-xs text-indigo-600 hover:underline">Go home</Link>
        </div>
      </div>
    )
  }

  const entries = data.entries
  const domains = [...new Set(entries.map(e => e.domain).filter(Boolean))] as string[]
  const filteredEntries = domainFilter
    ? entries.filter(e => e.domain === domainFilter)
    : entries

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50/30 to-white">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </Link>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
                <Dna className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Skill Genome</h1>
                <p className="text-sm text-gray-500">Your global mastery profile across all learning paths</p>
              </div>
            </div>
          </div>

          <Link
            to={`/curiosity/${userId}`}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 text-sm font-medium transition-colors"
          >
            <Compass className="h-4 w-4" />
            Curiosity Feed
          </Link>
        </div>

        {/* Radar / Overview */}
        <div className="card mb-8">
          <SkillGenomeRadar entries={entries} />
        </div>

        {/* Domain filter */}
        {domains.length > 1 && (
          <div className="flex items-center gap-2 mb-6 flex-wrap">
            <span className="text-xs text-gray-500">Filter:</span>
            <button
              onClick={() => setDomainFilter(null)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                !domainFilter
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All ({entries.length})
            </button>
            {domains.map(d => (
              <button
                key={d}
                onClick={() => setDomainFilter(d === domainFilter ? null : d)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  domainFilter === d
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {d} ({entries.filter(e => e.domain === d).length})
              </button>
            ))}
          </div>
        )}

        {/* Skill Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEntries
            .sort((a, b) => b.mastery_level - a.mastery_level)
            .map(entry => (
              <GenomeSkillCard key={entry.ontology_node_id} entry={entry} />
            ))}
        </div>
      </div>
    </div>
  )
}
