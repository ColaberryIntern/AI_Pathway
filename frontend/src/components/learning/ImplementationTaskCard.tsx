import { Hammer, Clock, FileText, MessageSquare } from 'lucide-react'
import type { ImplementationTask } from '../../types'

interface ImplementationTaskCardProps {
  task: ImplementationTask
}

export default function ImplementationTaskCard({ task }: ImplementationTaskCardProps) {
  return (
    <section className="card border-2 border-purple-200 bg-gradient-to-br from-purple-50/50 to-white">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-purple-100">
          <Hammer className="h-5 w-5 text-purple-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Implementation Task</h2>
      </div>

      <h3 className="font-semibold text-gray-900 text-base mb-2">{task.title}</h3>
      <p className="text-sm text-gray-700 mb-4">{task.description}</p>

      {/* Requirements */}
      {task.requirements && task.requirements.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Requirements
          </p>
          <ul className="space-y-1.5">
            {task.requirements.map((req, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="w-5 h-5 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center flex-shrink-0 font-medium text-xs">
                  {i + 1}
                </span>
                {req}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Deliverable */}
      <div className="bg-purple-50 rounded-lg p-3 mb-4 border border-purple-100">
        <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider mb-1">
          Deliverable
        </p>
        <p className="text-sm text-gray-700">{task.deliverable}</p>
      </div>

      {/* Submission callouts */}
      <div className="flex flex-wrap gap-3 text-xs">
        {task.requires_prompt_history && (
          <div className="flex items-center gap-1.5 bg-sky-50 border border-sky-200 text-sky-700 px-3 py-1.5 rounded-full font-medium">
            <MessageSquare className="h-3.5 w-3.5" />
            Include prompt history
          </div>
        )}
        {task.requires_architecture_explanation && (
          <div className="flex items-center gap-1.5 bg-indigo-50 border border-indigo-200 text-indigo-700 px-3 py-1.5 rounded-full font-medium">
            <FileText className="h-3.5 w-3.5" />
            Include architecture explanation
          </div>
        )}
        {task.estimated_minutes > 0 && (
          <div className="flex items-center gap-1.5 text-gray-500">
            <Clock className="h-3.5 w-3.5" />
            ~{task.estimated_minutes} min
          </div>
        )}
      </div>
    </section>
  )
}
