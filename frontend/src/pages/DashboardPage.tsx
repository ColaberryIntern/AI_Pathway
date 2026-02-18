import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getDashboard } from '../services/api'
import {
  BookOpen,
  CheckCircle,
  Trophy,
  ArrowRight,
  Loader2,
  Target,
  TrendingUp,
  Sparkles,
} from 'lucide-react'

export default function DashboardPage() {
  const { userId: rawUserId } = useParams<{ userId: string }>()
  const resolvedUserId = rawUserId === 'latest'
    ? localStorage.getItem('latestUserId')
    : rawUserId

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard', resolvedUserId],
    queryFn: () => getDashboard(resolvedUserId!),
    enabled: !!resolvedUserId,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16 space-y-6">
        <div className="w-24 h-24 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-full flex items-center justify-center mx-auto">
          <Target className="h-12 w-12 text-indigo-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">No Learning Paths Yet</h1>
        <p className="text-gray-600 text-lg">
          Start by selecting a profile and generating your first learning path.
        </p>
        <Link
          to="/profiles"
          className="btn btn-primary inline-flex items-center gap-2 text-lg px-8 py-4"
        >
          Get Started
          <ArrowRight className="h-5 w-5" />
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">My Learning Dashboard</h1>
        <p className="text-gray-600">Track your progress across all learning paths</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center border-l-4 border-l-indigo-500 hover:shadow-lg transition-shadow">
          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <BookOpen className="h-5 w-5 text-indigo-600" />
          </div>
          <div className="text-3xl font-bold text-indigo-600">
            {dashboard.total_paths}
          </div>
          <div className="text-sm text-gray-600">Total Paths</div>
        </div>
        <div className="card text-center border-l-4 border-l-sky-500 hover:shadow-lg transition-shadow">
          <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <TrendingUp className="h-5 w-5 text-sky-600" />
          </div>
          <div className="text-3xl font-bold text-sky-600">
            {dashboard.active_paths.length}
          </div>
          <div className="text-sm text-gray-600">In Progress</div>
        </div>
        <div className="card text-center border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-green-600">
            {dashboard.completed_paths.length}
          </div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
        <div className="card text-center border-l-4 border-l-amber-500 hover:shadow-lg transition-shadow">
          <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <Sparkles className="h-5 w-5 text-amber-600" />
          </div>
          <div className="text-3xl font-bold text-amber-600">
            {dashboard.total_skills_learned}
          </div>
          <div className="text-sm text-gray-600">Skills Learned</div>
        </div>
      </div>

      {/* Active Paths */}
      {dashboard.active_paths.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
              <BookOpen className="h-4 w-4 text-indigo-600" />
            </div>
            Active Learning Paths
          </h2>
          <div className="space-y-4">
            {dashboard.active_paths.map((path) => (
              <Link
                key={path.id}
                to={`/path/${path.id}`}
                className="block p-5 bg-white border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all group"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors">
                    {path.title}
                  </h3>
                  <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-md">
                    {path.completed_chapters}/{path.total_chapters} chapters
                  </span>
                </div>
                <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 transition-all duration-500 rounded-full"
                    style={{ width: `${path.completion_percentage}%` }}
                  />
                </div>
                <div className="mt-3 flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    {path.completion_percentage}% complete
                  </span>
                  <span className="text-indigo-600 flex items-center gap-1 font-medium group-hover:gap-2 transition-all">
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Completed Paths */}
      {dashboard.completed_paths.length > 0 && (
        <div className="card bg-green-50/50">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
              <Trophy className="h-4 w-4 text-amber-600" />
            </div>
            Completed Paths
          </h2>
          <div className="space-y-3">
            {dashboard.completed_paths.map((path) => (
              <Link
                key={path.id}
                to={`/path/${path.id}`}
                className="flex items-center gap-4 p-5 bg-white border border-green-200 rounded-xl hover:shadow-md transition-all group"
              >
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 group-hover:text-green-700 transition-colors">
                    {path.title}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {path.total_chapters} chapters completed
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-500">
                    {new Date(path.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-1 mt-1">
                    <Trophy className="h-4 w-4 text-amber-500" />
                    <span className="text-xs text-amber-600 font-medium">Completed</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* CTA for new path */}
      <div className="text-center py-8 border-t border-gray-100">
        <Link
          to="/profiles"
          className="btn btn-secondary inline-flex items-center gap-2 hover:shadow-md transition-all"
        >
          Start a New Learning Path
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  )
}
