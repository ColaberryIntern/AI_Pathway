import { useState } from 'react'
import { CheckCircle2, XCircle, ChevronRight, Copy, ClipboardCheck, Bot } from 'lucide-react'
import type { KnowledgeCheck as KnowledgeCheckType } from '../../types'

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
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="mt-3 p-3 bg-sky-50 border border-sky-200 rounded-lg">
      <div className="flex items-start gap-2">
        <Bot className="h-4 w-4 text-sky-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-sky-700 mb-1">Ask your AI assistant:</p>
          <p className="text-sm text-gray-700 italic">{prompt}</p>
        </div>
        <button
          onClick={handleCopy}
          className="p-1 rounded hover:bg-sky-100 transition-colors flex-shrink-0"
        >
          {copied ? (
            <ClipboardCheck className="h-3.5 w-3.5 text-sky-600" />
          ) : (
            <Copy className="h-3.5 w-3.5 text-sky-400" />
          )}
        </button>
      </div>
    </div>
  )
}
