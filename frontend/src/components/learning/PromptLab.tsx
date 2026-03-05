import { useState, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Play, RotateCcw, Clock, Loader2, ChevronDown, ChevronUp, Sparkles,
} from 'lucide-react'
import { executePrompt, getPromptHistory } from '../../services/api'
import type { PromptTemplate } from '../../types'
import { hasUnfilledPlaceholders } from '../../utils/placeholders'
import PlaceholderFillModal from './PlaceholderFillModal'

interface Props {
  pathId: string
  lessonId: string
  template?: PromptTemplate
}

interface HistoryItem {
  iteration: number
  prompt_text: string
  response_text: string
  execution_time_ms: number
  created_at: string
}

export default function PromptLab({ pathId, lessonId, template }: Props) {
  const queryClient = useQueryClient()
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState<string | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [showFillModal, setShowFillModal] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)

  // Listen for filled prompts sent from PromptTemplateCard
  useEffect(() => {
    const handler = (e: Event) => {
      const incoming = (e as CustomEvent).detail?.prompt
      if (incoming) {
        setPrompt(incoming)
        setResponse(null)
        setTimeout(() => {
          sectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 50)
      }
    }
    window.addEventListener('send-to-prompt-lab', handler)
    return () => window.removeEventListener('send-to-prompt-lab', handler)
  }, [])

  // Load existing history
  const { data: history } = useQuery({
    queryKey: ['prompt-history', pathId, lessonId],
    queryFn: () => getPromptHistory(pathId, lessonId),
    enabled: !!pathId && !!lessonId,
  })

  const iteration = (history?.total_iterations ?? 0) + 1

  // Execute prompt mutation — accepts optional override prompt for post-fill execution
  const executeMutation = useMutation({
    mutationFn: (overridePrompt?: string) => executePrompt(pathId, {
      lesson_id: lessonId,
      prompt: overridePrompt ?? prompt,
      iteration,
    }),
    onSuccess: (data) => {
      setResponse(data.response)
      queryClient.invalidateQueries({ queryKey: ['prompt-history', pathId, lessonId] })
    },
  })

  const handleRun = () => {
    if (!prompt.trim()) return
    if (hasUnfilledPlaceholders(prompt) && template?.placeholders?.length) {
      setShowFillModal(true)
      return
    }
    executeMutation.mutate(undefined)
  }

  const handleFillComplete = (filledPrompt: string) => {
    setShowFillModal(false)
    setPrompt(filledPrompt)
    executeMutation.mutate(filledPrompt)
  }

  const handleRefine = () => {
    setResponse(null)
  }

  const handleLoadTemplate = () => {
    setPrompt(template?.template ?? '')
    setResponse(null)
  }

  const hasPlaceholders = prompt.includes('{{')

  return (
    <section ref={sectionRef} className="space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-violet-600" />
        <h2 className="text-lg font-bold text-gray-900">Prompt Lab</h2>
        <span className="text-xs px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 font-medium">
          Interactive
        </span>
      </div>

      <div className="card border-2 border-violet-200 bg-violet-50/20 space-y-4">
        {/* Prompt editor */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">Your Prompt</label>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>Iteration #{iteration}</span>
              {history && history.total_iterations > 0 && (
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex items-center gap-1 text-violet-600 hover:text-violet-800"
                >
                  History ({history.total_iterations})
                  {showHistory ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>
              )}
            </div>
          </div>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={6}
            className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-mono text-gray-800 focus:border-violet-500 focus:ring-2 focus:ring-violet-200 resize-y"
            placeholder="Try writing your own prompt for this skill. Use the template above as inspiration, or start from scratch..."
            disabled={executeMutation.isPending}
          />

          {/* Placeholder hints */}
          {hasPlaceholders && template?.placeholders && template.placeholders.length > 0 && (
            <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3 space-y-1">
              <p className="font-medium text-gray-600">Fill in the placeholders:</p>
              {template.placeholders.map((p, i) => (
                <p key={i}>
                  <code className="text-violet-600">{`{{${p.name}}}`}</code>
                  {' — '}{p.description}
                  {p.example && <span className="text-gray-400"> (e.g., {p.example})</span>}
                </p>
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {!response ? (
              <button
                onClick={handleRun}
                disabled={!prompt.trim() || executeMutation.isPending}
                className="btn bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-700 hover:to-purple-700 disabled:opacity-50"
              >
                {executeMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-1" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Run Prompt
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleRefine}
                className="btn bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-700 hover:to-purple-700"
              >
                <Sparkles className="h-4 w-4 mr-1" />
                Refine Prompt
              </button>
            )}
            {template?.template && (
              <button
                onClick={handleLoadTemplate}
                className="btn btn-secondary text-xs"
                disabled={executeMutation.isPending}
              >
                <RotateCcw className="h-3.5 w-3.5 mr-1" />
                Load Template
              </button>
            )}
          </div>
        </div>

        {/* Error display */}
        {executeMutation.isError && (
          <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
            {(executeMutation.error as Error)?.message?.includes('429')
              ? 'Maximum prompt iterations reached for this lesson (10). Move on to the next section!'
              : `Error: ${(executeMutation.error as Error)?.message || 'Failed to execute prompt'}`
            }
          </div>
        )}

        {/* Response display */}
        {response && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700">AI Response</p>
              {executeMutation.data?.execution_time_ms && (
                <span className="flex items-center gap-1 text-xs text-gray-400">
                  <Clock className="h-3 w-3" />
                  {(executeMutation.data.execution_time_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-sm text-gray-800 whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
              {response}
            </div>
          </div>
        )}

        {/* Iteration history */}
        {showHistory && history && history.iterations.length > 0 && (
          <div className="border-t border-violet-200 pt-4 space-y-3">
            <p className="text-sm font-medium text-gray-700">Previous Iterations</p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {history.iterations.map((item: HistoryItem) => (
                <details key={item.iteration} className="group">
                  <summary className="flex items-center justify-between cursor-pointer text-sm text-gray-600 hover:text-violet-600 p-2 rounded-lg hover:bg-violet-50">
                    <span className="font-medium">v{item.iteration}</span>
                    <span className="text-xs text-gray-400">
                      {(item.execution_time_ms / 1000).toFixed(1)}s
                    </span>
                  </summary>
                  <div className="mt-1 ml-2 space-y-2 text-xs">
                    <div className="bg-gray-50 rounded p-2">
                      <p className="font-medium text-gray-500 mb-1">Prompt:</p>
                      <p className="font-mono text-gray-700 whitespace-pre-wrap">{item.prompt_text}</p>
                    </div>
                    <div className="bg-violet-50 rounded p-2">
                      <p className="font-medium text-gray-500 mb-1">Response:</p>
                      <p className="text-gray-700 whitespace-pre-wrap">{item.response_text}</p>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </div>
        )}
      </div>

      <PlaceholderFillModal
        isOpen={showFillModal}
        onClose={() => setShowFillModal(false)}
        onSubmit={handleFillComplete}
        templateText={prompt}
        placeholders={template?.placeholders || []}
      />
    </section>
  )
}
