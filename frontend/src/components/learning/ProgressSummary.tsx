import { BookCheck, TrendingUp, Layers } from 'lucide-react'

interface ProgressSummaryProps {
  lessonsCompleted: number
  totalLessons: number
  estimatedHoursRemaining: number
  overallProgress: number
  totalModules: number
}

export default function ProgressSummary({
  lessonsCompleted,
  totalLessons,
  overallProgress,
  totalModules,
}: ProgressSummaryProps) {
  const stats = [
    {
      icon: BookCheck,
      label: 'Lessons Completed',
      value: `${lessonsCompleted} of ${totalLessons}`,
      color: 'text-emerald-600 bg-emerald-100',
    },
    {
      icon: TrendingUp,
      label: 'Progress',
      value: `${overallProgress.toFixed(0)}%`,
      color: 'text-sky-600 bg-sky-100',
    },
    {
      icon: Layers,
      label: 'Modules',
      value: `${totalModules}`,
      color: 'text-indigo-600 bg-indigo-100',
    },
  ]

  return (
    <div className="grid grid-cols-3 gap-3">
      {stats.map((s) => (
        <div key={s.label} className="card p-3 flex items-center gap-3">
          <div className={`p-2 rounded-lg ${s.color}`}>
            <s.icon className="h-4 w-4" />
          </div>
          <div>
            <p className="text-lg font-bold text-gray-900">{s.value}</p>
            <p className="text-[10px] text-gray-500">{s.label}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
