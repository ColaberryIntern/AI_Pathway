import { useState, useEffect } from 'react'
import {
  Hammer, Bot, ExternalLink, CheckCircle2, Circle,
} from 'lucide-react'
import type { ImplementationTask } from '../../types'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

interface ImplementationTaskCardProps {
  task: ImplementationTask
  pathId?: string
  lessonId?: string
  onSubmit?: () => void
}

const STEPS = [
  { label: 'Review Assignment', description: 'Read the task details above' },
  { label: 'Get AI Mentor Briefing', description: 'Your mentor will prepare a structured plan' },
  { label: 'Open AI Workspace', description: 'Start building with your preferred AI tool' },
]

export default function ImplementationTaskCard({
  task, pathId, lessonId,
}: ImplementationTaskCardProps) {
  // Step 1 is always done (they're reading the card), so start at step 2
  const [completedStep, setCompletedStep] = useState(1)
  const [briefingRequested, setBriefingRequested] = useState(false)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  // Listen for mentor-responded to advance to step 3
  useEffect(() => {
    if (!briefingRequested) return
    const handler = () => {
      setCompletedStep(2)
      setBriefingRequested(false)
    }
    window.addEventListener('mentor-responded', handler)
    return () => window.removeEventListener('mentor-responded', handler)
  }, [briefingRequested])

  const handleGetBriefing = () => {
    if (!pathId || !lessonId) return
    setBriefingRequested(true)

    const taskContext = [
      `I need help with this implementation task:`,
      ``,
      `Title: ${task.title}`,
      `Description: ${task.description}`,
      `Requirements:`,
      ...task.requirements.map((r, i) => `${i + 1}. ${r}`),
      `Deliverable: ${task.deliverable}`,
    ].join('\n')

    window.dispatchEvent(new CustomEvent('open-mentor', {
      detail: { message: taskContext, mode: 'implementation-briefing' },
    }))
  }

  const handleOpenWorkspace = () => {
    const prompt = [
      `Help me build: ${task.title}`,
      ``,
      `Deliverable: ${task.deliverable}`,
      ``,
      `Key requirements:`,
      ...task.requirements.map((r, i) => `${i + 1}. ${r}`),
      ``,
      `Guide me step by step. Start with the first step.`,
    ].join('\n')

    openInLLM(prompt, llmKey)
  }

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
      <div className="bg-purple-50 rounded-lg p-3 mb-6 border border-purple-100">
        <p className="text-xs font-semibold text-purple-700 uppercase tracking-wider mb-1">
          Deliverable
        </p>
        <p className="text-sm text-gray-700">{task.deliverable}</p>
      </div>

      {/* 3-Step Stepper */}
      {pathId && lessonId && (
        <div className="border-t border-purple-100 pt-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Your Workflow
          </p>
          <div className="space-y-3">
            {STEPS.map((step, i) => {
              const stepNum = i + 1
              const isComplete = completedStep >= stepNum
              const isActive = completedStep === stepNum - 1 || (stepNum === 2 && briefingRequested)

              return (
                <div key={stepNum} className="flex items-start gap-3">
                  {/* Step indicator */}
                  <div className="flex flex-col items-center">
                    {isComplete ? (
                      <CheckCircle2 className="h-6 w-6 text-emerald-500 flex-shrink-0" />
                    ) : isActive ? (
                      <div className="h-6 w-6 rounded-full border-2 border-purple-500 bg-purple-50 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-bold text-purple-600">{stepNum}</span>
                      </div>
                    ) : (
                      <Circle className="h-6 w-6 text-gray-300 flex-shrink-0" />
                    )}
                    {/* Connector line */}
                    {stepNum < STEPS.length && (
                      <div className={`w-0.5 h-4 mt-1 ${isComplete ? 'bg-emerald-300' : 'bg-gray-200'}`} />
                    )}
                  </div>

                  {/* Step content */}
                  <div className="flex-1 pb-1">
                    <div className="flex items-center gap-3">
                      <span className={`text-sm font-semibold ${
                        isComplete ? 'text-emerald-700' : isActive ? 'text-gray-900' : 'text-gray-400'
                      }`}>
                        {step.label}
                      </span>

                      {/* Step 2: Briefing button */}
                      {stepNum === 2 && isActive && !briefingRequested && (
                        <button
                          onClick={handleGetBriefing}
                          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-sm"
                        >
                          <Bot className="h-3.5 w-3.5" />
                          Ask AI Mentor
                        </button>
                      )}

                      {/* Step 2: Waiting for briefing */}
                      {stepNum === 2 && briefingRequested && (
                        <span className="text-xs text-purple-600 font-medium animate-pulse">
                          Mentor is preparing your briefing...
                        </span>
                      )}

                      {/* Step 3: Workspace button */}
                      {stepNum === 3 && isActive && (
                        <button
                          onClick={handleOpenWorkspace}
                          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 transition-all shadow-sm"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                          {getRunLabel(llmKey)}
                        </button>
                      )}
                    </div>

                    {/* Description — only for active/future steps */}
                    {!isComplete && (
                      <p className={`text-xs mt-0.5 ${isActive ? 'text-gray-500' : 'text-gray-300'}`}>
                        {step.description}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
