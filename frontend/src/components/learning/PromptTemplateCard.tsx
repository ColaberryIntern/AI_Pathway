import { useState } from 'react'
import { FileCode2, ChevronDown, Sparkles } from 'lucide-react'
import type { PromptTemplate } from '../../types'
import { hasUnfilledPlaceholders } from '../../utils/placeholders'
import PlaceholderFillModal from './PlaceholderFillModal'

interface PromptTemplateCardProps {
  template: PromptTemplate
}

export default function PromptTemplateCard({ template }: PromptTemplateCardProps) {
  const [showPlaceholders, setShowPlaceholders] = useState(false)
  const [showFillModal, setShowFillModal] = useState(false)

  const needsFill = template.placeholders?.length > 0 && hasUnfilledPlaceholders(template.template)

  const sendToLab = (prompt: string) => {
    window.dispatchEvent(
      new CustomEvent('send-to-prompt-lab', { detail: { prompt } })
    )
  }

  const handleTestInLab = () => {
    if (needsFill) {
      setShowFillModal(true)
    } else {
      sendToLab(template.template)
    }
  }

  const handleFillComplete = (filledPrompt: string) => {
    setShowFillModal(false)
    sendToLab(filledPrompt)
  }

  // Highlight {{placeholders}} in the template
  const renderTemplate = (text: string) => {
    const parts = text.split(/({{[^}]+}})/)
    return parts.map((part, i) =>
      part.startsWith('{{') ? (
        <span key={i} className="bg-sky-200/60 text-sky-800 px-1 rounded font-semibold">
          {part}
        </span>
      ) : (
        <span key={i}>{part}</span>
      )
    )
  }

  return (
    <section className="card border border-sky-200 bg-gradient-to-br from-sky-50/50 to-white">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 rounded-lg bg-sky-100">
          <FileCode2 className="h-5 w-5 text-sky-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Prompt Template</h2>
      </div>

      {/* Template display */}
      <div className="bg-gray-900 rounded-xl p-4 mb-4">
        <p className="text-gray-100 text-sm font-mono whitespace-pre-wrap leading-relaxed mb-3">
          {renderTemplate(template.template)}
        </p>
        <button
          onClick={handleTestInLab}
          className="flex items-center gap-1.5 text-xs font-medium text-purple-300 hover:text-purple-200 transition-colors px-3 py-1.5 rounded-lg bg-purple-600/30 hover:bg-purple-600/40 border border-purple-500/40"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Test in Prompt Lab
        </button>
      </div>

      {/* Expected output shape */}
      {template.expected_output_shape && (
        <div className="bg-sky-50 rounded-lg p-3 mb-4 border border-sky-100">
          <p className="text-xs font-semibold text-sky-700 uppercase tracking-wider mb-1">
            Expected Output
          </p>
          <p className="text-sm text-gray-700">{template.expected_output_shape}</p>
        </div>
      )}

      {/* Placeholders */}
      {template.placeholders && template.placeholders.length > 0 && (
        <div>
          <button
            onClick={() => setShowPlaceholders(!showPlaceholders)}
            className="flex items-center gap-1.5 text-sm text-sky-600 hover:text-sky-800 transition-colors"
          >
            <ChevronDown className={`h-4 w-4 transition-transform ${showPlaceholders ? 'rotate-180' : ''}`} />
            {showPlaceholders ? 'Hide' : 'Show'} placeholder guide ({template.placeholders.length})
          </button>
          {showPlaceholders && (
            <div className="mt-3 space-y-2">
              {template.placeholders.map((ph, i) => (
                <div key={i} className="flex items-start gap-3 p-2.5 bg-gray-50 rounded-lg">
                  <span className="bg-sky-200/60 text-sky-800 px-1.5 py-0.5 rounded font-mono text-xs font-semibold whitespace-nowrap">
                    {`{{${ph.name}}}`}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700">{ph.description}</p>
                    {ph.example && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        Example: <span className="italic">{ph.example}</span>
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <PlaceholderFillModal
        isOpen={showFillModal}
        onClose={() => setShowFillModal(false)}
        onSubmit={handleFillComplete}
        templateText={template.template}
        placeholders={template.placeholders || []}
      />
    </section>
  )
}
