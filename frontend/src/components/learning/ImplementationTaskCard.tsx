import { useState, useEffect } from 'react'
import {
  Hammer, Bot, Loader2, ExternalLink, CheckSquare, Square,
  Lightbulb, Wrench, FileOutput, ClipboardList, BookOpen,
} from 'lucide-react'
import type { ImplementationTask } from '../../types'
import { sendMentorMessage } from '../../services/api'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

interface ImplementationTaskCardProps {
  task: ImplementationTask
  pathId?: string
  lessonId?: string
  onSubmit?: () => void
}

/** Parse the mentor's structured briefing into 5 sections */
function parseBriefingSections(text: string): Record<string, string> {
  const sections: Record<string, string> = {}
  const headingPattern = /^##\s*\d+\.\s*(.+)$/gm
  const matches = [...text.matchAll(headingPattern)]

  for (let i = 0; i < matches.length; i++) {
    const key = matches[i][1].trim()
    const start = matches[i].index! + matches[i][0].length
    const end = i + 1 < matches.length ? matches[i + 1].index! : text.length
    sections[key] = text.slice(start, end).trim()
  }
  return sections
}

/** Extract bullet/numbered items from a markdown section */
function extractListItems(markdown: string): string[] {
  return markdown
    .split('\n')
    .map((line) => line.replace(/^[\s\-*•]+/, '').replace(/^\d+\.\s*/, '').trim())
    .filter((line) => line.length > 0)
}

/** Section icon mapping */
function getSectionIcon(key: string) {
  const lower = key.toLowerCase()
  if (lower.includes('interpretation')) return <BookOpen className="h-4 w-4" />
  if (lower.includes('built')) return <ClipboardList className="h-4 w-4" />
  if (lower.includes('plan')) return <CheckSquare className="h-4 w-4" />
  if (lower.includes('tools')) return <Wrench className="h-4 w-4" />
  if (lower.includes('artifacts')) return <FileOutput className="h-4 w-4" />
  return <Lightbulb className="h-4 w-4" />
}

/** Section color mapping */
function getSectionColors(key: string) {
  const lower = key.toLowerCase()
  if (lower.includes('interpretation')) return { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: 'text-blue-600' }
  if (lower.includes('built')) return { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: 'text-emerald-600' }
  if (lower.includes('plan')) return { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', icon: 'text-purple-600' }
  if (lower.includes('tools')) return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: 'text-amber-600' }
  if (lower.includes('artifacts')) return { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', icon: 'text-indigo-600' }
  return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', icon: 'text-gray-600' }
}

export default function ImplementationTaskCard({
  task, pathId, lessonId,
}: ImplementationTaskCardProps) {
  const [briefing, setBriefing] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [checkedSteps, setCheckedSteps] = useState<boolean[]>([])
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  const generateBriefing = async () => {
    if (!pathId || !lessonId) return
    setIsGenerating(true)
    setError(null)

    // Build task context message for the mentor
    const taskContext = [
      `Title: ${task.title}`,
      `Description: ${task.description}`,
      `Requirements:\n${task.requirements.map((r, i) => `${i + 1}. ${r}`).join('\n')}`,
      `Deliverable: ${task.deliverable}`,
    ].join('\n\n')

    try {
      const result = await sendMentorMessage(pathId, {
        message: taskContext,
        lesson_id: lessonId,
        mode: 'implementation-briefing',
      })
      setBriefing(result.response)

      // Initialize checkboxes for the implementation plan
      const sections = parseBriefingSections(result.response)
      const planKey = Object.keys(sections).find((k) => k.toLowerCase().includes('plan'))
      if (planKey) {
        const items = extractListItems(sections[planKey])
        setCheckedSteps(new Array(items.length).fill(false))
      }
    } catch {
      setError('Failed to generate briefing. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const openWorkspace = () => {
    const sections = briefing ? parseBriefingSections(briefing) : {}
    const planKey = Object.keys(sections).find((k) => k.toLowerCase().includes('plan'))
    const planSection = planKey ? sections[planKey] : ''

    const prompt = [
      `I need to complete the following implementation task:\n`,
      `## Task: ${task.title}`,
      task.description,
      `\n## Requirements:`,
      task.requirements.map((r, i) => `${i + 1}. ${r}`).join('\n'),
      `\n## Deliverable:`,
      task.deliverable,
      planSection ? `\n## Implementation Plan (from my AI mentor):\n${planSection}` : '',
      `\nPlease help me work through this step by step. Start with step 1 of the implementation plan.`,
    ].join('\n')

    openInLLM(prompt, llmKey)
  }

  const toggleStep = (index: number) => {
    setCheckedSteps((prev) => {
      const next = [...prev]
      next[index] = !next[index]
      return next
    })
  }

  const sections = briefing ? parseBriefingSections(briefing) : {}

  return (
    <section className="card border-2 border-purple-200 bg-gradient-to-br from-purple-50/50 to-white">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-purple-100">
          <Hammer className="h-5 w-5 text-purple-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Implementation Task</h2>
      </div>

      {/* Title & Description */}
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

      {/* AI Mentor Button — shown before briefing is generated */}
      {!briefing && !isGenerating && pathId && lessonId && (
        <button
          onClick={generateBriefing}
          className="btn bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 flex items-center gap-2 w-full justify-center"
        >
          <Bot className="h-4 w-4" />
          AI Mentor — Generate Implementation Briefing
        </button>
      )}

      {/* Loading state */}
      {isGenerating && (
        <div className="flex items-center justify-center gap-3 py-6">
          <Loader2 className="h-5 w-5 text-purple-500 animate-spin" />
          <span className="text-sm text-gray-600">Your AI Mentor is preparing your briefing...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-3 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
          <button
            onClick={generateBriefing}
            className="ml-2 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Briefing Display */}
      {briefing && (
        <div className="border-t border-purple-100 pt-4 mt-4 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 rounded-lg bg-indigo-100">
              <Bot className="h-4 w-4 text-indigo-600" />
            </div>
            <h3 className="font-semibold text-gray-900">AI Mentor Briefing</h3>
          </div>

          {Object.entries(sections).map(([key, content]) => {
            const colors = getSectionColors(key)
            const isPlan = key.toLowerCase().includes('plan')
            const items = extractListItems(content)

            return (
              <div key={key} className={`${colors.bg} rounded-lg p-4 border ${colors.border}`}>
                <p className={`text-xs font-semibold ${colors.text} uppercase tracking-wider mb-2 flex items-center gap-1.5`}>
                  <span className={colors.icon}>{getSectionIcon(key)}</span>
                  {key}
                </p>

                {isPlan ? (
                  // Implementation Plan with checkboxes
                  <ul className="space-y-2">
                    {items.map((item, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <button
                          onClick={() => toggleStep(i)}
                          className="mt-0.5 flex-shrink-0 text-purple-600 hover:text-purple-800 transition-colors"
                        >
                          {checkedSteps[i] ? (
                            <CheckSquare className="h-4 w-4" />
                          ) : (
                            <Square className="h-4 w-4" />
                          )}
                        </button>
                        <span className={`text-sm ${checkedSteps[i] ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                          {item}
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : key.toLowerCase().includes('interpretation') ? (
                  // Paragraphs for interpretation
                  <div className="text-sm text-gray-700 space-y-2">
                    {content.split('\n\n').map((para, i) => (
                      <p key={i}>{para.trim()}</p>
                    ))}
                  </div>
                ) : (
                  // Bullet list for other sections
                  <ul className="space-y-1">
                    {items.map((item, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className={`${colors.text} mt-0.5`}>•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )
          })}

          {/* Open AI Workspace Button */}
          <button
            onClick={openWorkspace}
            className="btn bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 flex items-center gap-2 w-full justify-center text-base py-3"
          >
            <ExternalLink className="h-4 w-4" />
            Open AI Workspace — {getRunLabel(llmKey)}
          </button>
        </div>
      )}
    </section>
  )
}
