import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Hammer, Clock, FileText, Send, Loader2,
  CheckCircle2, ThumbsUp, ArrowUpCircle, ChevronDown, Bot,
  ExternalLink, Lightbulb,
} from 'lucide-react'
import type { ImplementationTask } from '../../types'
import { submitImplementationTask } from '../../services/api'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

interface ImplementationTaskCardProps {
  task: ImplementationTask
  pathId?: string
  lessonId?: string
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
  task, pathId, lessonId, onSubmit,
}: ImplementationTaskCardProps) {
  const [conversation, setConversation] = useState('')
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
      return submitImplementationTask(pathId!, {
        lesson_id: lessonId!,
        prompt_history_summary: '',
        strategy_explanation: '',
        learner_prompt: conversation,
      })
    },
    onSuccess: () => {
      setSubmitted(true)
      onSubmit?.()
    },
  })

  const canSubmit = !!pathId && !!lessonId && conversation.trim().length >= 50

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

      {/* Get Started + Paste Conversation */}
      {pathId && lessonId && !submitted && (
        <div className="border-t border-purple-100 pt-4 space-y-4">
          {/* Open LLM */}
          <div>
            <label className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              Get Started
            </label>
            <p className="text-xs text-gray-500 mt-1 mb-3">
              Open your preferred AI assistant to work on this task. When you're done, paste your conversation below.
            </p>
            <button
              onClick={() => openInLLM('', llmKey)}
              className="flex items-center gap-1.5 text-sm font-medium text-purple-600 hover:text-purple-700 transition-colors px-4 py-2 rounded-lg bg-purple-50 hover:bg-purple-100 border border-purple-200"
            >
              <ExternalLink className="h-4 w-4" />
              {getRunLabel(llmKey)}
            </button>
          </div>

          {/* Paste conversation */}
          <div>
            <label className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="h-4 w-4 text-purple-600" />
              Paste Your AI Conversation
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Include both your prompts and the AI's responses so we can analyze your prompting strategy.
            </p>
          </div>

          <textarea
            value={conversation}
            onChange={(e) => setConversation(e.target.value)}
            rows={6}
            className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm text-gray-800 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 resize-y"
            placeholder="Paste your AI conversation here. Include both your prompts and the AI's responses..."
            disabled={submitMutation.isPending}
          />

          {conversation.trim().length > 0 && conversation.trim().length < 50 && (
            <p className="text-xs text-gray-500">Paste at least 50 characters of your conversation</p>
          )}

          <button
            onClick={() => submitMutation.mutate()}
            disabled={!canSubmit || submitMutation.isPending}
            className="btn bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
          >
            {submitMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
                Analyzing...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-1" />
                Submit for Feedback
              </>
            )}
          </button>
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
