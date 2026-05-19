import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, ArrowRight, Calendar } from 'lucide-react'
import { getPathSummary } from '../services/api'


export default function PathSummaryPage() {
  const { pathId } = useParams<{ pathId: string }>()
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['pathSummary', pathId],
    queryFn: () => getPathSummary(pathId!),
    enabled: !!pathId,
  })

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-gray-500">
        Loading your summary...
      </div>
    )
  }
  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-red-600">
        Could not load summary.
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 mb-2">
          <CheckCircle2 className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">
          {data.all_chapters_complete ? 'Pathway complete' : 'Your progress so far'}
        </h1>
        <p className="text-gray-600">
          {data.stats.lessons_completed} of {data.stats.lessons_total} chapter
          {data.stats.lessons_total === 1 ? '' : 's'} done
          {' '}({data.stats.percent_complete}%)
        </p>
      </div>

      {/* Skills mastered card */}
      <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-5">
        <div className="text-xs font-semibold uppercase tracking-wide text-emerald-800 mb-2">
          What you can now do
        </div>
        <ul className="space-y-2">
          {data.skills_completed.map((s) => (
            <li key={s.skill_id} className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-medium text-gray-900">{s.skill_name}</div>
                <div className="text-sm text-gray-600">
                  L{s.current_level} &rarr; L{s.target_level}
                  {s.level_label_target ? ` (${s.level_label_target})` : ''}
                  {' '}<span className="font-mono text-xs text-emerald-700">{s.skill_id}</span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Next steps */}
      {data.next_step_recommendations.length > 0 && (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50/60 p-5">
          <div className="text-xs font-semibold uppercase tracking-wide text-indigo-800 mb-2">
            Where to take this next
          </div>
          <ul className="space-y-3">
            {data.next_step_recommendations.map((n, i) => (
              <li key={i} className="border-l-2 border-indigo-300 pl-3">
                <div className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-indigo-600" />
                  <div className="font-medium text-gray-900">
                    {n.skill_name}{' '}
                    <span className="text-sm text-indigo-700">
                      L{n.from_level} &rarr; L{n.to_level}
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-700 mt-1">{n.rationale}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Retake prompt */}
      <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-5">
        <div className="flex items-start gap-3">
          <Calendar className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-amber-900">Come back in 60 days</div>
            <div className="text-sm text-amber-800 mt-1">{data.retake.message}</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-3 pt-2">
        <button
          onClick={() => navigate(`/learn/${pathId}`)}
          className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Back to Dashboard
        </button>
        <button
          onClick={() => navigate('/profiles')}
          className="btn btn-primary"
        >
          Start another pathway
        </button>
      </div>
    </div>
  )
}
