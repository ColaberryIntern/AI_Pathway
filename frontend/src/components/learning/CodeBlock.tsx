import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface CodeBlockProps {
  code: string
  language?: string
  title?: string
}

export default function CodeBlock({ code, language = 'python', title }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          {title && <span className="text-sm font-medium text-gray-300">{title}</span>}
          <span className="text-[10px] px-2 py-0.5 rounded bg-gray-700 text-gray-400">{language}</span>
        </div>
        <button
          onClick={handleCopy}
          className="text-gray-400 hover:text-gray-200 transition-colors p-1"
          title="Copy code"
        >
          {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
        </button>
      </div>
      {/* Code */}
      <pre className="p-4 bg-gray-900 overflow-x-auto">
        <code className="text-sm text-gray-100 font-mono whitespace-pre">{code}</code>
      </pre>
    </div>
  )
}
