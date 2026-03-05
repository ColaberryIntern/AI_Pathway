import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Hammer, Clock, FileText, MessageSquare, Send, Loader2,
  CheckCircle2, ThumbsUp, ArrowUpCircle, ChevronDown, Bot,
  ExternalLink, Lightbulb,
} from 'lucide-react'
import type { ImplementationTask } from '../../types'
import { submitImplementationTask } from '../../services/api'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

interface PromptHistoryItem {
  iteration: number
  prompt_text: string
  response_text: string
}

interface ImplementationTaskCardProps {
  task: ImplementationTask
  pathId?: string
  lessonId?: string
  promptHistory?: PromptHistoryItem[]
  onSubmit?: () => void
}

/** Render basic markdown: **bold**, numbered lists, paragraphs */
function renderFeedbackMarkdown(text: string) {
  const paragraphs = text.split(/\n\n+/)
  return paragraphs.map((para, pi) => {
    const trimmed = para.trim()
    if (!trimmed) return null

    // Check if paragraph is a numbered list
    const listItems = trimmed.split('\n').filter((l) => /^\d+\.\s/.test(l.trim()))
    if (listItems.length > 1) {
      return (
        <ol key={pi} className="list-decimal list-inside space-y-1 mb-3">
          {listItems.map((item, li) => (
            <li key={li} className="text-sm text-gray-700">
              {renderBold(item.replace(/^\d+\.\s*/, ''))}
            </li>
          ))}
        </ol>
      )
    }

    return (
      <p key={pi} className="text-sm text-gray-700 mb-2 last:mb-0">
        {renderBold(trimmed)}
      </p>
    )
  })
}

/** Replace **text** with <strong> */
function renderBold(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g)
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
  )
}

export default function ImplementationTaskCard({
  task, pathId, lessonId, promptHistory, onSubmit,
}: ImplementationTaskCardProps) {
  const [promptAttempt, setPromptAttempt] = useState('')
  const [strategy, setStrategy] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [feedbackExpanded, setFeedbackExpanded] = useState(false)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  const submitMutation = useMutation({
    mutationFn: () => {
      const historySummary = (promptHistory || [])
        .map((h) => `Iteration ${h.iteration}:\nPrompt: ${h.prompt_text}\nResponse: ${h.response_text.slice(0, 300)}...`)
        .join('\n\n')

      return submitImplementationTask(pathId!, {
        lesson_id: lessonId!,
        prompt_history_summary: historySummary,
        strategy_explanation: strategy,
        learner_prompt: promptAttempt,
      })
    },
    onSuccess: () => {
      setSubmitted(true)
      onSubmit?.()
    },
  })

  const canSubmit = !!pathId && !!lessonId && promptAttempt.trim().length >= 10 && strategy.trim().length >= 20

  return (
    <section className="card border-2 border-purple-200 bg-gradient-to-br from-purple-50/50 to-white">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-purple-100">
          <Hammer className="h-5 w-5 text-purple-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Implementation Task</h2>
        {submitted && (
          <span className="flex items-center gap-1 text-xs text-emerald-600 ml-auto">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Submitted
          </span>
        )}
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

      {/* Info badges */}
      <div className="flex flex-wrap gap-3 text-xs mb-4">
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

      {/* Prompt Attempt + Strategy Submission */}
      {pathId && lessonId && !submitted && (
        <div className="border-t border-purple-100 pt-4 space-y-4">
          {/* Step 1: Write your prompt */}
          <div>
            <label className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              Step 1: Write your prompt for this task
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Craft a prompt that you would use to solve this task with an AI. We'll analyze your prompting strategy and give tips.
            </p>
          </div>

          <div className="bg-gray-900 rounded-xl p-4">
            <textarea
              value={promptAttempt}
              onChange={(e) => setPromptAttempt(e.target.value)}
              rows={4}
              className="w-full bg-gray-800 rounded-lg border border-gray-700 px-4 py-3 text-sm text-gray-100 font-mono focus:border-purple-400 focus:ring-2 focus:ring-purple-400/30 resize-y placeholder-gray-500"
              placeholder="Example: Act as a senior data engineer. Given a dataset of customer transactions, write a Python script that identifies the top 10 customers by revenue, handles missing values, and outputs a clean CSV..."
              disabled={submitMutation.isPending}
            />
            {promptAttempt.trim().length >= 10 && (
              <div className="flex items-center gap-3 mt-3">
                <button
                  onClick={() => openInLLM(promptAttempt, llmKey)}
                  className="flex items-center gap-1.5 text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  {getRunLabel(llmKey)}
                </button>
                <span className="text-xs text-gray-500">Test your prompt before submitting</span>
              </div>
            )}
            {promptAttempt.trim().length > 0 && promptAttempt.trim().length < 10 && (
              <p className="text-xs text-gray-500 mt-2">Write at least 10 characters</p>
            )}
          </div>

          {/* Step 2: Reflect on strategy */}
          <div>
            <label className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-purple-600" />
              Step 2: Reflect on your prompt engineering process
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Explain your thought process and what strategies you used.
            </p>
          </div>

          {/* Prompt History — directly above textarea */}
          {promptHistory && promptHistory.length > 0 && (
            <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
              <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider mb-2">
                Your Prompt Lab History ({promptHistory.length} iteration{promptHistory.length !== 1 ? 's' : ''})
              </p>
              <div className="space-y-1.5 max-h-32 overflow-y-auto">
                {promptHistory.map((h) => (
                  <div key={h.iteration} className="text-xs text-gray-600">
                    <span className="font-medium text-purple-600">v{h.iteration}:</span>{' '}
                    {h.prompt_text.slice(0, 100)}{h.prompt_text.length > 100 ? '...' : ''}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Guided questions */}
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 space-y-1.5">
            <p className="text-xs font-medium text-gray-600 mb-1">Answer these in your reflection:</p>
            <p className="text-xs text-gray-500 flex items-start gap-2">
              <span className="w-4 h-4 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-[10px]">1</span>
              Why did you structure your prompt this way?
            </p>
            <p className="text-xs text-gray-500 flex items-start gap-2">
              <span className="w-4 h-4 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-[10px]">2</span>
              What strategy did you use (chain-of-thought, few-shot, role-play, etc.)?
            </p>
            <p className="text-xs text-gray-500 flex items-start gap-2">
              <span className="w-4 h-4 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-[10px]">3</span>
              What would you change to get a better result?
            </p>
          </div>

          <textarea
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            rows={3}
            className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm text-gray-800 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 resize-y"
            placeholder="Example: I used a role-play approach by assigning the AI a senior engineer persona. I included specific constraints like output format and edge cases to handle..."
            disabled={submitMutation.isPending}
          />
          <div className="flex items-center gap-3">
            <button
              onClick={() => submitMutation.mutate()}
              disabled={!canSubmit || submitMutation.isPending}
              className="btn bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
            >
              {submitMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-1" />
                  Analyzing Strategy...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-1" />
                  Submit for Strategy Tips
                </>
              )}
            </button>
            {promptAttempt.trim().length < 10 && (
              <span className="text-xs text-gray-400">
                Write a prompt above (Step 1) first
              </span>
            )}
            {promptAttempt.trim().length >= 10 && strategy.trim().length > 0 && strategy.trim().length < 20 && (
              <span className="text-xs text-gray-400">
                Write at least 20 characters in your reflection
              </span>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {submitMutation.isError && (
        <div className="mt-3 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
          Failed to get feedback. Please try again.
        </div>
      )}

      {/* AI Feedback */}
      {submitMutation.data && (
        <div className="border-t border-purple-100 pt-4 mt-4 space-y-4">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-100">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            </div>
            <h3 className="font-semibold text-gray-900">AI Feedback</h3>
          </div>

          {/* Strengths */}
          {submitMutation.data.strengths.length > 0 && (
            <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
              <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-2 flex items-center gap-1">
                <ThumbsUp className="h-3.5 w-3.5" />
                Strengths
              </p>
              <ul className="space-y-1">
                {submitMutation.data.strengths.map((s, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-emerald-500 mt-0.5">+</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Improvements */}
          {submitMutation.data.improvements.length > 0 && (
            <div className="bg-amber-50 rounded-lg p-3 border border-amber-200">
              <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-2 flex items-center gap-1">
                <ArrowUpCircle className="h-3.5 w-3.5" />
                Areas to Improve
              </p>
              <ul className="space-y-1">
                {submitMutation.data.improvements.map((imp, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-amber-500 mt-0.5">~</span>
                    {imp}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Prompt Strategy Tips */}
          {submitMutation.data.prompt_strategy_tips.length > 0 && (
            <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
              <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Lightbulb className="h-3.5 w-3.5" />
                Prompt Strategy Tips
              </p>
              <ul className="space-y-1">
                {submitMutation.data.prompt_strategy_tips.map((tip, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-purple-500 mt-0.5 font-bold">&rarr;</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Full Feedback — collapsible */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setFeedbackExpanded(!feedbackExpanded)}
              className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wider flex items-center gap-1">
                <FileText className="h-3.5 w-3.5" />
                Detailed Feedback
              </span>
              <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${feedbackExpanded ? 'rotate-180' : ''}`} />
            </button>
            {feedbackExpanded && (
              <div className="px-4 py-3 max-h-64 overflow-y-auto leading-relaxed">
                {renderFeedbackMarkdown(submitMutation.data.feedback)}
              </div>
            )}
          </div>

          {/* Suggested Mentor Questions — contextual based on task + feedback */}
          <div className="bg-sky-50 rounded-lg p-3 border border-sky-200">
            <p className="text-xs font-semibold text-sky-700 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Bot className="h-3.5 w-3.5" />
              Continue learning with your AI Mentor
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                `I just completed the task "${task.title}" and received feedback. The deliverable was: "${task.deliverable}". Based on this, what are the most common gaps learners have and how can I address them?`,
                `My implementation task required: ${task.requirements.slice(0, 2).join('; ')}. ${submitMutation.data.improvements.length > 0 ? `The feedback said I should improve on: "${submitMutation.data.improvements[0]}".` : ''} Can you help me understand what a stronger approach looks like and walk me through it step by step?`,
                `I'm working on "${task.title}" and want to go deeper. What are the key concepts I should master to excel at this type of task, and what are common misconceptions that hold learners back?`,
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => {
                    window.dispatchEvent(
                      new CustomEvent('open-mentor', { detail: { message: q } })
                    )
                  }}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-indigo-100 text-indigo-700 hover:bg-indigo-200 border border-indigo-200 font-medium transition-colors text-left"
                  title={q}
                >
                  <Bot className="h-3 w-3 flex-shrink-0" />
                  <span className="line-clamp-2">{q}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
