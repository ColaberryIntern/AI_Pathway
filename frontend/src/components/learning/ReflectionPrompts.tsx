import { useState } from 'react'
import { Sparkles, ChevronDown, Bot } from 'lucide-react'
import type { ReflectionQuestion } from '../../types'

interface ReflectionPromptsProps {
  questions: ReflectionQuestion[]
}

export default function ReflectionPrompts({ questions }: ReflectionPromptsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  return (
    <section className="card border border-amber-200 bg-gradient-to-br from-amber-50/30 to-white">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-amber-100">
          <Sparkles className="h-5 w-5 text-amber-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Reflection</h2>
      </div>

      <div className="space-y-2">
        {questions.map((q, i) => {
          const isExpanded = expandedIndex === i
          return (
            <div
              key={i}
              className="border border-amber-100 rounded-lg overflow-hidden"
            >
              <button
                onClick={() => setExpandedIndex(isExpanded ? null : i)}
                className="w-full flex items-center gap-3 p-3 text-left hover:bg-amber-50/50 transition-colors"
              >
                <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center flex-shrink-0 font-medium text-xs">
                  {i + 1}
                </span>
                <span className="flex-1 text-sm font-medium text-gray-800">
                  {q.question}
                </span>
                <ChevronDown
                  className={`h-4 w-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                />
              </button>
              {isExpanded && q.prompt_for_deeper_thinking && (
                <div className="px-4 pb-3 pt-0 space-y-2">
                  <div className="bg-amber-50 rounded-lg p-3 border border-amber-100">
                    <p className="text-xs font-medium text-amber-600 mb-1">Go deeper:</p>
                    <p className="text-sm text-gray-700 italic">
                      {q.prompt_for_deeper_thinking}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      window.dispatchEvent(
                        new CustomEvent('open-mentor', {
                          detail: { message: q.prompt_for_deeper_thinking },
                        })
                      )
                    }}
                    className="flex items-center gap-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 border border-indigo-200"
                  >
                    <Bot className="h-3.5 w-3.5" />
                    Ask AI Mentor
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
