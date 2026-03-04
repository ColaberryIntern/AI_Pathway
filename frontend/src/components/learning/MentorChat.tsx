import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  X, Send, Loader2, Sparkles, Bot,
} from 'lucide-react'
import { sendMentorMessage, getMentorHistory } from '../../services/api'

interface Message {
  role: string
  content: string
  timestamp: string
}

export default function MentorChat() {
  const { pathId, lessonId } = useParams<{ pathId: string; lessonId?: string }>()
  const queryClient = useQueryClient()
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

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
      }
    }
    window.addEventListener('open-mentor', handler)
    return () => window.removeEventListener('open-mentor', handler)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
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

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-md'
                      : 'bg-gray-100 text-gray-800 rounded-bl-md'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))}

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
            <div className="px-4 py-2 border-t border-gray-100 flex gap-1 flex-wrap">
              {suggestedPrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => setInput(p)}
                  className="text-[10px] px-2 py-1 rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 truncate max-w-[12rem]"
                >
                  {p}
                </button>
              ))}
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
