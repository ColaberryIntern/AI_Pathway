import { useState, useEffect, useRef } from 'react'
import { X } from 'lucide-react'
import type { PromptPlaceholder } from '../../types'
import { extractPlaceholders, fillPlaceholders } from '../../utils/placeholders'

interface PlaceholderFillModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (filledPrompt: string) => void
  templateText: string
  placeholders: PromptPlaceholder[]
}

export default function PlaceholderFillModal({
  isOpen,
  onClose,
  onSubmit,
  templateText,
  placeholders,
}: PlaceholderFillModalProps) {
  // Build the list of placeholder names from the actual template text
  const placeholderNames = extractPlaceholders(templateText)

  // Metadata lookup by name
  const metaByName = new Map(placeholders.map(p => [p.name, p]))

  const [values, setValues] = useState<Record<string, string>>({})
  const firstInputRef = useRef<HTMLInputElement>(null)

  // Reset values when modal opens with new placeholders
  useEffect(() => {
    if (isOpen) {
      const init: Record<string, string> = {}
      for (const name of placeholderNames) init[name] = ''
      setValues(init)
      // Focus first input after render
      setTimeout(() => firstInputRef.current?.focus(), 50)
    }
  }, [isOpen, templateText])

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  if (!isOpen || placeholderNames.length === 0) return null

  const allFilled = placeholderNames.every(n => values[n]?.trim())

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!allFilled) return
    const filled = fillPlaceholders(templateText, values)
    onSubmit(filled)
  }

  const formatLabel = (name: string) =>
    name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center animate-modal-backdrop"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40" />

      {/* Panel */}
      <div
        className="relative bg-white rounded-xl shadow-2xl max-w-lg w-full mx-4 animate-modal-panel"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-900">Fill in Placeholders</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit}>
          <div className="px-6 py-4 space-y-4 max-h-[60vh] overflow-y-auto">
            {placeholderNames.map((name, i) => {
              const meta = metaByName.get(name)
              return (
                <div key={name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {formatLabel(name)}
                  </label>
                  {meta?.description && (
                    <p className="text-xs text-gray-500 mb-1.5">{meta.description}</p>
                  )}
                  <input
                    ref={i === 0 ? firstInputRef : undefined}
                    type="text"
                    className="input"
                    placeholder={meta?.example ? `e.g., ${meta.example}` : `Enter ${formatLabel(name).toLowerCase()}...`}
                    value={values[name] || ''}
                    onChange={e => setValues(prev => ({ ...prev, [name]: e.target.value }))}
                    autoComplete="off"
                  />
                </div>
              )
            })}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!allFilled}
              className="btn btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Apply &amp; Continue
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
