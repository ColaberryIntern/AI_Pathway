import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  X, Send, Loader2, Sparkles, Bot, ExternalLink, ClipboardCopy,
} from 'lucide-react'
import { sendMentorMessage, getMentorHistory } from '../../services/api'
import { openInLLM, getRunLabel, supportsUrlPrompt } from '../../utils/llm'
import LLMChooser from './LLMChooser'

interface Message {
  role: string
  content: string
  timestamp: string
}

/**
 * Parse an assistant message to find embedded prompts.
 * Returns segments: text parts and extracted prompts.
 */
function parseMessagePrompts(content: string): Array<{ type: 'text'; value: string } | { type: 'prompt'; value: string }> {
  // Match patterns like: "Try this prompt: '...'" or 'Try this prompt: "..."'
  // Also: "Prompt: '...'" or "Ask: '...'"
  const promptPattern = /(?:(?:try|use|run|ask|enter)\s+(?:this\s+)?(?:prompt|question|query)|prompt)\s*:\s*[""''](.+?)[""'']/gi
  const segments: Array<{ type: 'text'; value: string } | { type: 'prompt'; value: string }> = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = promptPattern.exec(content)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', value: content.slice(lastIndex, match.index) })
    }
    segments.push({ type: 'prompt', value: match[1] })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < content.length) {
    segments.push({ type: 'text', value: content.slice(lastIndex) })
  }

  return segments.length > 0 ? segments : [{ type: 'text', value: content }]
}

function PromptCard({ prompt }: { prompt: string }) {
  const label = getRunLabel()
  const Icon = supportsUrlPrompt() ? ExternalLink : ClipboardCopy

  return (
    <button
      onClick={() => openInLLM(prompt)}
      className="my-2 flex items-start gap-1.5 text-xs text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg px-2.5 py-2 cursor-pointer transition-colors text-left w-full"
      title={label}
    >
      <Icon className="h-3 w-3 flex-shrink-0 mt-0.5" />
      <span className="flex-1">
        <span className="italic">{prompt}</span>
        <span className="block text-[10px] text-indigo-400 mt-0.5">{label}</span>
      </span>
    </button>
  )
}

export default function MentorChat() {
  const { pathId, lessonId } = useParams<{ pathId: string; lessonId?: string }>()
  const queryClient = useQueryClient()
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')
  const [autoSendTrigger, setAutoSendTrigger] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const lastAssistantRef = useRef<HTMLDivElement>(null)
  const prevMessageCount = useRef(0)
  const autoSendRef = useRef<string | null>(null)

  // Load existing history
  const { data: historyData } = useQuery({
    queryKey: ['mentor-history', pathId, lessonId],
    queryFn: () => getMentorHistory(pathId!, lessonId),
    enabled: !!pathId && isOpen,
  })

  const messages: Message[] = historyData?.messages ?? []

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: (message: string) =>
      sendMentorMessage(pathId!, { message, lesson_id: lessonId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mentor-history', pathId, lessonId] })
      setInput('')
    },
  })

  // Listen for open-mentor events from other components (e.g. ReflectionPrompts)
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail
      setIsOpen(true)
      if (detail?.message) {
        setInput(detail.message)
        autoSendRef.current = detail.message
        setAutoSendTrigger((n) => n + 1)
      }
    }
    window.addEventListener('open-mentor', handler)
    return () => window.removeEventListener('open-mentor', handler)
  }, [])

  // Auto-send when a message is queued from an external "Ask AI Mentor" click
  useEffect(() => {
    if (autoSendRef.current && !sendMutation.isPending) {
      const msg = autoSendRef.current
      autoSendRef.current = null
      sendMutation.mutate(msg)
    }
  }, [autoSendTrigger]) // eslint-disable-line react-hooks/exhaustive-deps

  // Smart scroll: show start of new AI message, or bottom for user messages/typing
  useEffect(() => {
    const newCount = messages.length
    const lastMsg = messages[newCount - 1]

    if (newCount > prevMessageCount.current && lastMsg?.role !== 'user') {
      // New mentor message — scroll to its start so user reads from the top
      lastAssistantRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      // User message or typing indicator — scroll to bottom
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    prevMessageCount.current = newCount
  }, [messages, sendMutation.isPending])

  const handleSend = () => {
    const msg = input.trim()
    if (!msg || sendMutation.isPending) return
    sendMutation.mutate(msg)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Suggested prompts from last response
  const suggestedPrompts = sendMutation.data?.suggested_prompts ?? []

  if (!pathId) return null

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          <Bot className="h-5 w-5" />
          <span className="text-sm font-medium">AI Mentor</span>
        </button>
      )}

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96 h-[32rem] flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <div>
                <p className="text-sm font-semibold">AI Mentor</p>
                <p className="text-[10px] text-indigo-200">Socratic learning coach</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg hover:bg-white/20 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* LLM Chooser strip */}
          <div className="px-3 py-1.5 border-b border-gray-100 bg-gray-50 flex items-center justify-end">
            <LLMChooser />
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && !sendMutation.isPending && (
              <div className="text-center py-8 space-y-3">
                <div className="mx-auto w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Hi! I'm your AI Mentor</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Ask me anything about the lesson. I'll guide you with questions rather than direct answers.
                  </p>
                </div>
                <div className="space-y-2">
                  {[
                    "I'm confused about this concept",
                    "Can you give me a hint for the exercise?",
                    "How does this apply in the real world?",
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setInput(suggestion)
                      }}
                      className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => {
              // Attach ref to the last mentor message for smart scrolling
              const isLastMentor = msg.role !== 'user' &&
                i === messages.reduce((last, m, idx) => m.role !== 'user' ? idx : last, -1)

              return (
              <div
                key={i}
                ref={isLastMentor ? lastAssistantRef : undefined}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-md'
                      : 'bg-gray-100 text-gray-800 rounded-bl-md'
                  }`}
                >
                  {msg.role !== 'user' ? (
                    <div className="leading-relaxed">
                      {parseMessagePrompts(msg.content).map((seg, j) =>
                        seg.type === 'prompt' ? (
                          <PromptCard key={j} prompt={seg.value} />
                        ) : (
                          <span key={j} className="whitespace-pre-wrap">{seg.value}</span>
                        )
                      )}
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  )}
                </div>
              </div>
              )
            })}

            {/* Typing indicator */}
            {sendMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested prompts */}
          {suggestedPrompts.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-100 flex gap-1.5 flex-wrap">
              {suggestedPrompts.map((p, i) => {
                const SIcon = supportsUrlPrompt() ? ExternalLink : ClipboardCopy
                return (
                  <button
                    key={i}
                    onClick={() => openInLLM(p)}
                    className="flex items-center gap-1 text-[10px] px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200 truncate max-w-[14rem]"
                    title={getRunLabel()}
                  >
                    <SIcon className="h-2.5 w-2.5 flex-shrink-0" />
                    {p}
                  </button>
                )
              })}
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t border-gray-200">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Ask your mentor..."
                className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 max-h-24"
                disabled={sendMutation.isPending}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || sendMutation.isPending}
                className="p-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
              >
                {sendMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          {/* Error */}
          {sendMutation.isError && (
            <div className="px-4 py-2 bg-red-50 text-xs text-red-600 border-t border-red-100">
              Failed to send message. Try again.
            </div>
          )}
        </div>
      )}
    </>
  )
}
