import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { X, Lightbulb, ListOrdered, Globe, AlertTriangle, Bot, Loader2, ThumbsUp, ThumbsDown } from 'lucide-react'
import { getConfusionRecovery } from '../../services/api'
import type { ConfusionRecovery } from '../../types'

interface ConfusionRecoveryDrawerProps {
  isOpen: boolean
  onClose: () => void
  pathId: string
  lessonId: string
  section?: string
}

export default function ConfusionRecoveryDrawer({
  isOpen,
  onClose,
  pathId,
  lessonId,
  section = 'general',
}: ConfusionRecoveryDrawerProps) {
  const [feedback, setFeedback] = useState<'helped' | 'still_confused' | null>(null)

  const recoveryMutation = useMutation({
    mutationFn: () => getConfusionRecovery(pathId, lessonId, section),
  })

  // Auto-fetch when opened
  if (isOpen && !recoveryMutation.data && !recoveryMutation.isPending && !recoveryMutation.isError) {
    recoveryMutation.mutate()
  }

  if (!isOpen) return null

  const recovery: ConfusionRecovery | undefined = recoveryMutation.data

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-[28rem] max-w-full flex flex-col bg-white shadow-2xl border-l border-gray-200 animate-slide-in-right">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5" />
          <div>
            <p className="text-sm font-semibold">Confusion Recovery</p>
            <p className="text-[10px] text-amber-100">Alternative explanation</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1 rounded-lg hover:bg-white/20 transition-colors">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {recoveryMutation.isPending && (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="h-8 w-8 text-amber-500 animate-spin" />
            <p className="text-sm text-gray-500">Generating alternative explanation...</p>
          </div>
        )}

        {recoveryMutation.isError && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
            Failed to generate recovery content. Please try again.
            <button
              onClick={() => recoveryMutation.mutate()}
              className="block mt-2 text-xs font-medium text-red-600 hover:text-red-800 underline"
            >
              Retry
            </button>
          </div>
        )}

        {recovery && (
          <>
            {/* Analogy */}
            <section className="bg-amber-50 rounded-xl p-4 border border-amber-200">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="h-4 w-4 text-amber-600" />
                <h3 className="text-sm font-semibold text-amber-800">Think of it this way...</h3>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">{recovery.analogy}</p>
            </section>

            {/* Step by Step */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <ListOrdered className="h-4 w-4 text-indigo-600" />
                <h3 className="text-sm font-semibold text-gray-900">Step by Step</h3>
              </div>
              <ol className="space-y-2">
                {recovery.step_by_step.map((step, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm">
                    <span className="w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-xs">
                      {i + 1}
                    </span>
                    <span className="text-gray-700 leading-relaxed">{step}</span>
                  </li>
                ))}
              </ol>
            </section>

            {/* Real World Example */}
            <section className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
              <div className="flex items-center gap-2 mb-2">
                <Globe className="h-4 w-4 text-emerald-600" />
                <h3 className="text-sm font-semibold text-emerald-800">Real-World Example</h3>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">{recovery.real_world_example}</p>
            </section>

            {/* Common Misconceptions */}
            {recovery.common_misconceptions.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <h3 className="text-sm font-semibold text-gray-900">Common Misconceptions</h3>
                </div>
                <ul className="space-y-2">
                  {recovery.common_misconceptions.map((m, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span className="text-red-400 mt-0.5 flex-shrink-0">✕</span>
                      <span className="text-gray-700">{m}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Ask AI Mentor */}
            <button
              onClick={() => {
                window.dispatchEvent(
                  new CustomEvent('open-mentor', {
                    detail: { message: recovery.suggested_mentor_prompt },
                  })
                )
                onClose()
              }}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-medium hover:from-indigo-700 hover:to-violet-700 transition-all"
            >
              <Bot className="h-4 w-4" />
              Ask AI Mentor to explain further
            </button>

            {/* Feedback */}
            {!feedback && (
              <div className="flex items-center justify-center gap-3 pt-2">
                <span className="text-xs text-gray-400">Did this help?</span>
                <button
                  onClick={() => setFeedback('helped')}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200"
                >
                  <ThumbsUp className="h-3 w-3" /> Yes
                </button>
                <button
                  onClick={() => setFeedback('still_confused')}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200"
                >
                  <ThumbsDown className="h-3 w-3" /> Still confused
                </button>
              </div>
            )}
            {feedback === 'helped' && (
              <p className="text-center text-xs text-emerald-600">Great! Keep going!</p>
            )}
            {feedback === 'still_confused' && (
              <p className="text-center text-xs text-amber-600">
                Try asking the AI Mentor above for a more personalized explanation.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
