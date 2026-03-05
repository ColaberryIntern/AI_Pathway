import { useState, useRef, useEffect } from 'react'
import { ChevronDown, ExternalLink } from 'lucide-react'
import { LLM_OPTIONS, getPreferredLLM, setPreferredLLM, getLLMOption } from '../../utils/llm'

export default function LLMChooser() {
  const [selected, setSelected] = useState(getPreferredLLM)
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const current = getLLMOption(selected)

  return (
    <div ref={ref} className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 hover:bg-gray-200 text-xs font-medium text-gray-700 transition-colors border border-gray-200"
      >
        <ExternalLink className="h-3 w-3" />
        <span>Run prompts in: <strong>{current.name}</strong></span>
        <ChevronDown className={`h-3 w-3 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50 min-w-[160px]">
          {LLM_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              onClick={() => {
                setSelected(opt.key)
                setPreferredLLM(opt.key)
                setOpen(false)
                window.dispatchEvent(new CustomEvent('llm-changed', { detail: opt.key }))
              }}
              className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-50 transition-colors flex items-center justify-between ${
                selected === opt.key ? 'text-indigo-600 font-semibold bg-indigo-50' : 'text-gray-700'
              }`}
            >
              {opt.name}
              {selected === opt.key && <span className="text-indigo-500">&#10003;</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
