import { useState, useRef, useEffect, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  X, Send, Loader2, Sparkles, Bot, ExternalLink, ClipboardCopy, Check,
  Maximize2, Minimize2,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { sendMentorMessage, getMentorHistory } from '../../services/api'
import { openInLLM, getRunLabel, supportsUrlPrompt, getPreferredLLM } from '../../utils/llm'
import { copyToClipboard } from '../../utils/clipboard'
import LLMChooser from './LLMChooser'

interface Message {
  role: string
  content: string
  timestamp: string
}

/**
 * Parse an assistant message to find embedded prompts and strip "Explore further:" lines.
 * Returns segments: text parts and extracted inline prompts.
 * "Explore further:" prompts are removed from display (they appear as bottom chips instead).
 */
function parseMessagePrompts(content: string): Array<{ type: 'text'; value: string } | { type: 'prompt'; value: string }> {
  // First strip "Explore further:" lines — those only belong in the bottom suggested chips
  const cleaned = content.replace(/^[-*•]?\s*(?:\d+\.\s*)?explore further:\s*["''].+?["'']\s*$/gim, '').replace(/\n{3,}/g, '\n\n')

  // Match inline prompts like: "Try this prompt: '...'" or "Ask: '...'"
  const promptPattern = /(?:(?:try|use|run|ask|enter)\s+(?:this\s+)?(?:prompt|question|query)|prompt)\s*:\s*[""''](.+?)[""'']/gi
  const segments: Array<{ type: 'text'; value: string } | { type: 'prompt'; value: string }> = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = promptPattern.exec(cleaned)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', value: cleaned.slice(lastIndex, match.index) })
    }
    segments.push({ type: 'prompt', value: match[1] })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < cleaned.length) {
    segments.push({ type: 'text', value: cleaned.slice(lastIndex) })
  }

  return segments.length > 0 ? segments : [{ type: 'text', value: cleaned }]
}

/** Extract suggested prompts from an assistant message for bottom chips.
 *  Uses 3-tier approach matching backend logic:
 *  1. "Explore further:" prefixed lines
 *  2. "Try this prompt:" / "Ask:" prefixed lines
 *  3. Any quoted string 30+ chars with a role instruction
 */
function extractSuggestedPrompts(content: string): string[] {
  const prompts: string[] = []
  const rolePattern = /\b(?:act as|imagine you|as a|you are|suppose you|pretend you|take the role|playing the role|from the perspective)\b/i

  const cleanLine = (line: string) =>
    line.trim().replace(/^[\s\-*•]+/, '').replace(/^\d+\.\s*/, '').replace(/\*\*/g, '')

  const stripQuotes = (t: string) =>
    t.replace(/^["''\u201c\u2018]+|["''\u201d\u2019]+$/g, '').trim()

  // Tier 1: "Explore further:" prefix
  for (const line of content.split('\n')) {
    const cleaned = cleanLine(line)
    const match = cleaned.match(/^explore\s+further\s*:\s*(.*)/i)
    if (match) {
      const text = stripQuotes(match[1])
      if (text.length >= 20) prompts.push(text)
    }
  }

  // Tier 2: "Try this prompt:" / "Ask:" prefix
  if (!prompts.length) {
    for (const line of content.split('\n')) {
      const cleaned = cleanLine(line)
      const match = cleaned.match(/^(?:try(?:\s+this)?\s+prompt|ask|suggested?\s+prompt)\s*:\s*(.*)/i)
      if (match) {
        const text = stripQuotes(match[1])
        if (text.length >= 20) prompts.push(text)
      }
    }
  }

  // Tier 3: Any quoted string with a role instruction
  if (!prompts.length) {
    const quotePattern = /[""\u201c\u2018]([^""\u201d\u2019]{30,})[""\u201d\u2019]/g
    let m: RegExpExecArray | null
    while ((m = quotePattern.exec(content)) !== null) {
      const candidate = m[1].trim()
      if (rolePattern.test(candidate)) {
        prompts.push(candidate)
        if (prompts.length >= 2) break
      }
    }
  }

  return prompts.slice(0, 2)
}

/** Markdown components for styling mentor messages like ChatGPT */
const markdownComponents = {
  h1: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h1 className="text-base font-bold text-gray-900 mt-3 mb-1" {...props}>{children}</h1>
  ),
  h2: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h2 className="text-sm font-bold text-gray-900 mt-3 mb-1" {...props}>{children}</h2>
  ),
  h3: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className="text-sm font-semibold text-gray-900 mt-2 mb-1" {...props}>{children}</h3>
  ),
  p: ({ children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className="mb-2 last:mb-0 leading-relaxed" {...props}>{children}</p>
  ),
  ul: ({ children, ...props }: React.HTMLAttributes<HTMLUListElement>) => (
    <ul className="list-disc list-inside mb-2 space-y-0.5" {...props}>{children}</ul>
  ),
  ol: ({ children, ...props }: React.HTMLAttributes<HTMLOListElement>) => (
    <ol className="list-decimal list-inside mb-2 space-y-0.5" {...props}>{children}</ol>
  ),
  li: ({ children, ...props }: React.HTMLAttributes<HTMLLIElement>) => (
    <li className="leading-relaxed" {...props}>{children}</li>
  ),
  strong: ({ children, ...props }: React.HTMLAttributes<HTMLElement>) => (
    <strong className="font-semibold text-gray-900" {...props}>{children}</strong>
  ),
  code: ({ children, className, ...props }: React.HTMLAttributes<HTMLElement>) => {
    const isBlock = className?.includes('language-')
    if (isBlock) {
      return (
        <code className="block bg-gray-900 text-green-300 rounded-lg px-3 py-2 my-2 text-xs font-mono overflow-x-auto whitespace-pre" {...props}>
          {children}
        </code>
      )
    }
    return (
      <code className="bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-xs font-mono" {...props}>
        {children}
      </code>
    )
  },
  pre: ({ children, ...props }: React.HTMLAttributes<HTMLPreElement>) => (
    <pre className="my-2" {...props}>{children}</pre>
  ),
  blockquote: ({ children, ...props }: React.HTMLAttributes<HTMLQuoteElement>) => (
    <blockquote className="border-l-3 border-indigo-300 pl-3 my-2 italic text-gray-600" {...props}>{children}</blockquote>
  ),
  table: ({ children, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
    <div className="overflow-x-auto my-2">
      <table className="text-xs border-collapse border border-gray-300" {...props}>{children}</table>
    </div>
  ),
  th: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
    <th className="border border-gray-300 px-2 py-1 bg-gray-100 font-semibold text-left" {...props}>{children}</th>
  ),
  td: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
    <td className="border border-gray-300 px-2 py-1" {...props}>{children}</td>
  ),
}

interface WorkspaceContext {
  title: string
  description: string
  deliverable: string
  requirements: string[]
  lessonTitle?: string
}

/** Build the full workspace system prompt, adapting to whatever the current task is about */
function buildWorkspacePrompt(ctx: WorkspaceContext): string {
  const requirementsList = ctx.requirements.map((r, i) => `${i + 1}. ${r}`).join('\n')
  const lessonLine = ctx.lessonTitle ? `\nLesson: ${ctx.lessonTitle}\n` : ''

  return `You are an AI Implementation Coach helping a learner complete a hands-on assignment.

You are a patient, knowledgeable mentor — not a chatbot. Your job is to guide the learner step-by-step through producing a high-quality deliverable for their current task. You adapt your guidance to the specific subject matter of the assignment.

ASSIGNMENT CONTEXT
${lessonLine}
Task: ${ctx.title}

${ctx.description}

Deliverable:
${ctx.deliverable}

Requirements:
${requirementsList}

HOW YOU GUIDE THE LEARNER

1. Start by helping the learner understand what the assignment is asking and what a strong deliverable looks like.
2. Break the work into clear, manageable steps. Present one step at a time.
3. For each step, briefly explain why it matters, then give a clear action the learner should take.
4. After each step, ask the learner to share their progress before moving on.
5. When the learner completes all steps, help them review their work against the requirements and polish the final deliverable.

RESPONSE FORMAT

Keep responses focused and actionable. For each step, include:

STEP [number] — [Step Name]
Why this matters: A brief explanation connecting this step to the overall goal.
What to do: The specific action for this step.
What good looks like: A short description of the expected result.

After the learner responds, acknowledge their progress, give feedback, and introduce the next step.

At the start and after each step, show a simple progress tracker:
✔ Completed steps
→ Current step
○ Upcoming steps

COACHING PRINCIPLES
- Guide with questions and reasoning, not just answers.
- One step at a time — never dump the full solution.
- Adapt your language and examples to the subject matter of the assignment.
- Keep the focus on producing the deliverable, not on abstract theory.
- If the learner is stuck, offer a hint or reframe the problem rather than giving the answer directly.
- Celebrate progress and keep momentum positive.

START
Begin by greeting the learner, summarizing the assignment in plain language, laying out the steps you'll work through together, and then starting Step 1.`
}

function PromptCard({ prompt, llmKey }: { prompt: string; llmKey: string }) {
  const [copied, setCopied] = useState(false)
  const label = getRunLabel(llmKey)

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation()
    await copyToClipboard(prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className="my-2 text-xs text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg px-2.5 py-2 w-full"
      title={prompt}
    >
      <p className="italic leading-relaxed mb-1.5">{prompt}</p>
      <div className="flex items-center gap-2">
        <button
          onClick={() => openInLLM(prompt, llmKey)}
          className="flex items-center gap-1 text-[10px] font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          <ExternalLink className="h-3 w-3" />
          {label}
        </button>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-[10px] font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          {copied ? <Check className="h-3 w-3 text-emerald-500" /> : <ClipboardCopy className="h-3 w-3" />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
    </div>
  )
}

export default function MentorChat() {
  const { pathId, lessonId } = useParams<{ pathId: string; lessonId?: string }>()
  const queryClient = useQueryClient()
  const [isOpen, setIsOpen] = useState(false)
  const [isFullScreen, setIsFullScreen] = useState(false)
  const [input, setInput] = useState('')
  const [autoSendTrigger, setAutoSendTrigger] = useState(0)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)
  const [savedPrompts, setSavedPrompts] = useState<string[]>([])
  const [showWorkspaceBar, setShowWorkspaceBar] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const lastAssistantRef = useRef<HTMLDivElement>(null)
  const prevMessageCount = useRef(0)
  const autoSendRef = useRef<string | null>(null)
  const autoSendModeRef = useRef<string | undefined>(undefined)
  const taskContextRef = useRef<WorkspaceContext | null>(null)

  // Load existing history
  const { data: historyData } = useQuery({
    queryKey: ['mentor-history', pathId, lessonId],
    queryFn: () => getMentorHistory(pathId!, lessonId),
    enabled: !!pathId && isOpen,
  })

  const messages: Message[] = historyData?.messages ?? []

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: (params: { message: string; mode?: string }) =>
      sendMentorMessage(pathId!, { message: params.message, lesson_id: lessonId, mode: params.mode }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['mentor-history', pathId, lessonId] })
      setInput('')
      if (data.suggested_prompts?.length) {
        setSavedPrompts(data.suggested_prompts)
      }
      // Show workspace bar only for implementation briefings
      if (autoSendModeRef.current === 'implementation-briefing') {
        setShowWorkspaceBar(true)
      }
      // Notify other components (e.g. ImplementationTaskCard) that the mentor responded
      window.dispatchEvent(new CustomEvent('mentor-responded'))
    },
  })

  // Listen for open-mentor events from other components
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail
      setIsOpen(true)
      if (detail?.message) {
        setInput(detail.message)
        autoSendRef.current = detail.message
        autoSendModeRef.current = detail.mode
        // Store task context for workspace button
        if (detail.mode === 'implementation-briefing' && detail.taskContext) {
          taskContextRef.current = detail.taskContext
        } else {
          // Clear stale implementation context when opening from other sources
          taskContextRef.current = null
          setShowWorkspaceBar(false)
        }
        setAutoSendTrigger((n) => n + 1)
      }
    }
    window.addEventListener('open-mentor', handler)
    return () => window.removeEventListener('open-mentor', handler)
  }, [])

  // Re-render prompts when user switches LLM in the chooser
  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  // Auto-send when a message is queued from an external "Ask AI Mentor" click
  useEffect(() => {
    if (autoSendRef.current && !sendMutation.isPending) {
      const msg = autoSendRef.current
      const mode = autoSendModeRef.current
      autoSendRef.current = null
      sendMutation.mutate({ message: msg, mode })
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
    sendMutation.mutate({ message: msg })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleOpenWorkspace = () => {
    const ctx = taskContextRef.current
    if (!ctx) return
    // Include the mentor's briefing response so the external LLM has context
    const lastMentorMsg = [...messages].reverse().find(m => m.role !== 'user')
    const briefing = lastMentorMsg
      ? `\n\nMENTOR BRIEFING:\nYour AI Mentor provided the following guidance:\n${lastMentorMsg.content}`
      : ''
    const prompt = buildWorkspacePrompt(ctx) + briefing
    openInLLM(prompt, llmKey)
  }

  // Suggested prompts: mutation data > persisted state > DB-stored prompts > text extraction
  const dbPrompts = historyData?.last_suggested_prompts ?? []

  const historyPrompts = useMemo(() => {
    const lastAssistant = [...messages].reverse().find(m => m.role !== 'user')
    if (!lastAssistant) return []
    return extractSuggestedPrompts(lastAssistant.content)
  }, [messages])

  const suggestedPrompts = sendMutation.data?.suggested_prompts?.length
    ? sendMutation.data.suggested_prompts
    : savedPrompts.length
      ? savedPrompts
      : dbPrompts.length
        ? dbPrompts
        : historyPrompts

  if (!pathId) return null

  // Panel classes based on mode
  const panelClasses = isFullScreen
    ? 'fixed inset-0 z-50 flex flex-col bg-white'
    : 'fixed bottom-6 right-6 z-50 w-96 h-[32rem] flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden'

  const messageAreaClasses = isFullScreen
    ? 'max-w-3xl mx-auto w-full'
    : ''

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
        <div className={panelClasses}>
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <div>
                <p className="text-sm font-semibold">AI Mentor</p>
                <p className="text-[10px] text-indigo-200">Socratic learning coach</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsFullScreen(!isFullScreen)}
                className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
                title={isFullScreen ? 'Minimize' : 'Full screen'}
              >
                {isFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
              </button>
              <button
                onClick={() => { setIsOpen(false); setIsFullScreen(false) }}
                className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* LLM Chooser strip */}
          <div className={`px-3 py-1.5 border-b border-gray-100 bg-gray-50 flex items-center justify-end ${isFullScreen ? '' : ''}`}>
            <div className={messageAreaClasses}>
              <div className="flex justify-end">
                <LLMChooser />
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className={`${messageAreaClasses} space-y-4`}>
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
                        onClick={() => setInput(suggestion)}
                        className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, i) => {
                const isLastMentor = msg.role !== 'user' &&
                  i === messages.reduce((last, m, idx) => m.role !== 'user' ? idx : last, -1)

                return (
                  <div
                    key={i}
                    ref={isLastMentor ? lastAssistantRef : undefined}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`${isFullScreen ? 'max-w-[70%]' : 'max-w-[85%]'} px-4 py-3 rounded-2xl text-sm ${
                        msg.role === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-md'
                          : 'bg-gray-100 text-gray-800 rounded-bl-md'
                      }`}
                    >
                      {msg.role !== 'user' ? (
                        <div className="leading-relaxed mentor-markdown">
                          {parseMessagePrompts(msg.content).map((seg, j) =>
                            seg.type === 'prompt' ? (
                              <PromptCard key={j} prompt={seg.value} llmKey={llmKey} />
                            ) : (
                              <ReactMarkdown
                                key={j}
                                remarkPlugins={[remarkGfm]}
                                components={markdownComponents}
                              >
                                {seg.value}
                              </ReactMarkdown>
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
          </div>

          {/* Open AI Workspace bar — shown after implementation briefing */}
          {showWorkspaceBar && taskContextRef.current && (
            <div className="px-4 py-2.5 border-t border-indigo-100 bg-indigo-50 flex items-center gap-2">
              <div className={`${messageAreaClasses} flex items-center gap-2 w-full`}>
                <button
                  onClick={handleOpenWorkspace}
                  className="flex-1 flex items-center justify-center gap-2 text-sm font-medium px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 transition-all shadow-sm"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open AI Workspace — {getRunLabel(llmKey)}
                </button>
                <button
                  onClick={() => setShowWorkspaceBar(false)}
                  className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Dismiss"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* Suggested prompts — hidden during implementation task (workspace bar takes priority) */}
          {suggestedPrompts.length > 0 && !showWorkspaceBar && (
            <div className="px-4 py-2 border-t border-gray-100 flex gap-1.5 flex-wrap">
              <div className={`${messageAreaClasses} flex gap-1.5 flex-wrap`}>
                {suggestedPrompts.map((p, i) => {
                  const SIcon = supportsUrlPrompt(llmKey) ? ExternalLink : ClipboardCopy
                  return (
                    <button
                      key={i}
                      onClick={() => openInLLM(p, llmKey)}
                      className={`flex items-center gap-1 text-[10px] px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200 truncate ${isFullScreen ? 'max-w-[20rem]' : 'max-w-[14rem]'}`}
                      title={p}
                    >
                      <SIcon className="h-2.5 w-2.5 flex-shrink-0" />
                      {p}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t border-gray-200">
            <div className={`${messageAreaClasses} flex items-end gap-2`}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Ask your mentor..."
                className={`flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-200 ${isFullScreen ? 'max-h-32' : 'max-h-24'}`}
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
