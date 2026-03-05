import { useState, useEffect } from 'react'
import { Bot, CheckCircle2, Copy, ClipboardCheck, ArrowRight, ExternalLink } from 'lucide-react'
import type { AIStrategy } from '../../types'
import { copyToClipboard } from '../../utils/clipboard'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

interface AIStrategyPanelProps {
  strategy: AIStrategy
}

export default function AIStrategyPanel({ strategy }: AIStrategyPanelProps) {
  const [copied, setCopied] = useState(false)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  const handleCopy = () => {
    copyToClipboard(strategy.suggested_prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="card border border-teal-200 bg-gradient-to-br from-teal-50/50 to-white">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-teal-100">
          <Bot className="h-5 w-5 text-teal-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">AI Strategy</h2>
      </div>

      <p className="text-gray-700 leading-relaxed mb-4">{strategy.description}</p>

      <div className="grid gap-4 sm:grid-cols-2 mb-4">
        {/* When to use AI */}
        <div className="bg-teal-50 rounded-xl p-4 border border-teal-100">
          <p className="text-xs font-semibold text-teal-700 uppercase tracking-wider mb-2">
            Delegate to AI
          </p>
          <ul className="space-y-1.5">
            {strategy.when_to_use_ai.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <ArrowRight className="h-3.5 w-3.5 text-teal-500 flex-shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Human responsibilities */}
        <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
          <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-2">
            Keep Human
          </p>
          <ul className="space-y-1.5">
            {strategy.human_responsibilities.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle2 className="h-3.5 w-3.5 text-amber-500 flex-shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Suggested prompt */}
      {strategy.suggested_prompt && (
        <div className="bg-gray-900 rounded-xl p-4">
          <p className="text-xs font-medium text-teal-400 mb-2">Try this prompt:</p>
          <p className="text-gray-100 text-sm font-mono whitespace-pre-wrap leading-relaxed mb-3">
            {strategy.suggested_prompt}
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={() => openInLLM(strategy.suggested_prompt, llmKey)}
              className="flex items-center gap-1.5 text-xs font-medium text-teal-400 hover:text-teal-300 transition-colors px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              {getRunLabel(llmKey)}
            </button>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs font-medium text-gray-400 hover:text-gray-300 transition-colors px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700"
            >
              {copied ? (
                <><ClipboardCheck className="h-3.5 w-3.5 text-teal-400" /> Copied!</>
              ) : (
                <><Copy className="h-3.5 w-3.5" /> Copy</>
              )}
            </button>
          </div>
        </div>
      )}
    </section>
  )
}
