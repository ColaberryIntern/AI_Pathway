import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Compass, ArrowLeft, Loader2, Dna, Sparkles, ExternalLink } from 'lucide-react'
import { getCuriosityFeed } from '../services/api'

export default function CuriosityFeedPage() {
  const { userId } = useParams<{ userId: string }>()

  const { data, isLoading, error } = useQuery({
    queryKey: ['curiosity-feed', userId],
    queryFn: () => getCuriosityFeed(userId!),
    enabled: !!userId,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-3">
          <Loader2 className="h-8 w-8 text-amber-500 animate-spin mx-auto" />
          <p className="text-sm text-gray-500">Generating your curiosity feed...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-3">
          <p className="text-sm text-red-600">Failed to load Curiosity Feed.</p>
          <Link to="/" className="text-xs text-indigo-600 hover:underline">Go home</Link>
        </div>
      </div>
    )
  }

  const items = data.items

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50/30 to-white">
      <div className="max-w-4xl mx-auto px-4 py-8">
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
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-white">
                <Compass className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Curiosity Feed</h1>
                <p className="text-sm text-gray-500">Skills unlocked by your learning progress</p>
              </div>
            </div>
          </div>

          <Link
            to={`/genome/${userId}`}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 text-sm font-medium transition-colors"
          >
            <Dna className="h-4 w-4" />
            Skill Genome
          </Link>
        </div>

        {items.length === 0 ? (
          <div className="text-center py-16 space-y-3">
            <div className="mx-auto w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center">
              <Compass className="h-8 w-8 text-amber-500" />
            </div>
            <p className="text-sm text-gray-600">No discoveries yet!</p>
            <p className="text-xs text-gray-400">
              Complete more lessons to unlock new skills in your feed.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div
                key={item.skill_id}
                className="card border border-amber-100 hover:border-amber-200 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-amber-100 flex-shrink-0 mt-0.5">
                    <Sparkles className="h-5 w-5 text-amber-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-semibold text-gray-900">{item.skill_name}</h3>
                      {item.domain_label && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-500">
                          {item.domain_label}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3 leading-relaxed">{item.teaser}</p>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-amber-600 flex items-center gap-1">
                        <Sparkles className="h-3 w-3" />
                        Unlocked by: <span className="font-medium">{item.unlocked_by}</span>
                      </span>
                      <span className="text-xs text-gray-400">
                        Relevance: {Math.round(item.relevance_score * 100)}%
                      </span>
                      {item.has_learning_path && (
                        <span className="text-xs text-emerald-600 flex items-center gap-1">
                          <ExternalLink className="h-3 w-3" />
                          In your path
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
