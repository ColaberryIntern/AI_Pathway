import { useState, useEffect } from 'react'
import { CheckCircle2, XCircle, ChevronRight, Bot, ExternalLink, ClipboardCopy } from 'lucide-react'
import type { KnowledgeCheck as KnowledgeCheckType } from '../../types'
import { openInLLM, getRunLabel, supportsUrlPrompt, getPreferredLLM } from '../../utils/llm'

interface KnowledgeCheckProps {
  checks: KnowledgeCheckType[]
  onComplete: (score: number) => void
}

export default function KnowledgeCheck({ checks, onComplete }: KnowledgeCheckProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [correctCount, setCorrectCount] = useState(0)
  const [finished, setFinished] = useState(false)

  if (!checks.length) return null

  const current = checks[currentIndex]
  const isCorrect = selectedAnswer === current.correct_answer
  const progress = ((currentIndex + (finished ? 1 : 0)) / checks.length) * 100

  const handleSelect = (option: string) => {
    if (showFeedback) return
    setSelectedAnswer(option)
    setShowFeedback(true)
    if (option === current.correct_answer) {
      setCorrectCount((c) => c + 1)
    }
  }

  const handleNext = () => {
    if (currentIndex < checks.length - 1) {
      setCurrentIndex((i) => i + 1)
      setSelectedAnswer(null)
      setShowFeedback(false)
    } else {
      setFinished(true)
      const finalCorrect = correctCount + (isCorrect ? 0 : 0) // already counted
      const score = (finalCorrect / checks.length) * 100
      onComplete(score)
    }
  }

  if (finished) {
    const score = (correctCount / checks.length) * 100
    return (
      <div className="card border-2 border-indigo-200 text-center py-8">
        <div className={`text-4xl font-bold mb-2 ${score >= 70 ? 'text-emerald-600' : 'text-amber-600'}`}>
          {score.toFixed(0)}%
        </div>
        <p className="text-gray-600">
          {correctCount} of {checks.length} correct
        </p>
        <p className="text-sm text-gray-500 mt-2">
          {score >= 70 ? 'Great job! You passed the knowledge check.' : 'Consider reviewing this material before moving on.'}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-gray-400 whitespace-nowrap">
          {currentIndex + 1}/{checks.length}
        </span>
      </div>

      {/* Question */}
      <div className="card">
        <p className="font-medium text-gray-900 mb-4">{current.question}</p>

        <div className="space-y-2">
          {current.options.map((option, i) => {
            let optionStyle = 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            if (showFeedback) {
              if (option === current.correct_answer) {
                optionStyle = 'border-emerald-400 bg-emerald-50'
              } else if (option === selectedAnswer) {
                optionStyle = 'border-red-400 bg-red-50'
              } else {
                optionStyle = 'border-gray-200 opacity-50'
              }
            } else if (option === selectedAnswer) {
              optionStyle = 'border-indigo-400 bg-indigo-50'
            }

            return (
              <button
                key={i}
                onClick={() => handleSelect(option)}
                disabled={showFeedback}
                className={`w-full text-left p-3 rounded-lg border-2 transition-all ${optionStyle}`}
              >
                <div className="flex items-center gap-3">
                  {showFeedback && option === current.correct_answer && (
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
                  )}
                  {showFeedback && option === selectedAnswer && option !== current.correct_answer && (
                    <XCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                  )}
                  <span className="text-sm text-gray-700">{option}</span>
                </div>
              </button>
            )
          })}
        </div>

        {/* Feedback */}
        {showFeedback && (
          <div className={`mt-4 p-3 rounded-lg ${isCorrect ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'}`}>
            <p className={`text-sm font-medium ${isCorrect ? 'text-emerald-700' : 'text-amber-700'}`}>
              {isCorrect ? 'Correct!' : 'Not quite.'}
            </p>
            <p className="text-sm text-gray-600 mt-1">{current.explanation}</p>
          </div>
        )}

        {/* AI followup prompt suggestion */}
        {showFeedback && current.ai_followup_prompt && (
          <AIFollowupPrompt prompt={current.ai_followup_prompt} />
        )}

        {/* Next button */}
        {showFeedback && (
          <button
            onClick={handleNext}
            className="mt-4 flex items-center gap-1 ml-auto text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            {currentIndex < checks.length - 1 ? 'Next Question' : 'See Results'}
            <ChevronRight className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}

function AIFollowupPrompt({ prompt }: { prompt: string }) {
  const [llmOpened, setLlmOpened] = useState(false)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  const handleAskMentor = () => {
    window.dispatchEvent(
      new CustomEvent('open-mentor', {
        detail: { message: prompt },
      })
    )
  }

  const handleRunInLLM = () => {
    openInLLM(prompt, llmKey)
    setLlmOpened(true)
    setTimeout(() => setLlmOpened(false), 3000)
  }

  const LlmIcon = supportsUrlPrompt(llmKey) ? ExternalLink : ClipboardCopy

  return (
    <div className="mt-3 p-3 bg-sky-50 border border-sky-200 rounded-lg">
      <div className="flex items-start gap-2">
        <Bot className="h-4 w-4 text-sky-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-sky-700 mb-1">Dig deeper:</p>
          <p className="text-sm text-gray-700 italic mb-2">{prompt}</p>
          <div className="flex items-center gap-2">
            <button
              onClick={handleAskMentor}
              className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full bg-indigo-100 text-indigo-700 hover:bg-indigo-200 border border-indigo-200 font-medium transition-colors"
            >
              <Bot className="h-3 w-3" />
              Ask AI Mentor
            </button>
            <button
              onClick={handleRunInLLM}
              className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full bg-white text-gray-600 hover:bg-gray-100 border border-gray-200 font-medium transition-colors"
            >
              <LlmIcon className="h-3 w-3" />
              {llmOpened ? 'Opening...' : getRunLabel(llmKey)}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
