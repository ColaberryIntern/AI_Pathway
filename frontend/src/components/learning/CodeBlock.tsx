import { useState, useEffect, useRef } from 'react'
import { Copy, Check, Play, Loader2, Terminal, AlertTriangle, RotateCcw } from 'lucide-react'
import { copyToClipboard } from '../../utils/clipboard'
import { usePyodide } from '../../hooks/usePyodide'

interface CodeBlockProps {
  code: string
  language?: string
  title?: string
}

export default function CodeBlock({ code, language = 'python', title }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const [editableCode, setEditableCode] = useState(code)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isPython = language.toLowerCase() === 'python'
  const { status, output, error, runCode } = usePyodide()

  const isModified = editableCode !== code

  // Sync when code prop changes (e.g. navigating to different lesson)
  useEffect(() => {
    setEditableCode(code)
  }, [code])

  // Auto-resize textarea to fit content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [editableCode])

  const handleCopy = async () => {
    await copyToClipboard(editableCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRun = () => {
    runCode(editableCode)
  }

  const handleReset = () => {
    setEditableCode(code)
  }

  const isImportError = error && /ModuleNotFoundError|No module named/i.test(error)

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          {title && <span className="text-sm font-medium text-gray-300">{title}</span>}
          <span className="text-[10px] px-2 py-0.5 rounded bg-gray-700 text-gray-400">{language}</span>
          {isModified && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-900/50 text-amber-400">edited</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Reset button — only when modified */}
          {isModified && (
            <button
              onClick={handleReset}
              className="flex items-center gap-1 text-xs font-medium text-gray-400 hover:text-gray-200 transition-colors px-2 py-1 rounded bg-gray-700 hover:bg-gray-600"
              title="Reset to original"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
          )}
          {/* Run button — Python only */}
          {isPython && (
            <button
              onClick={handleRun}
              disabled={status === 'loading' || status === 'running'}
              className="flex items-center gap-1 text-xs font-medium text-emerald-400 hover:text-emerald-300 disabled:text-gray-500 disabled:cursor-wait transition-colors px-2 py-1 rounded bg-gray-700 hover:bg-gray-600"
              title="Run code in browser"
            >
              {status === 'loading' ? (
                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Loading Python...</>
              ) : status === 'running' ? (
                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Running...</>
              ) : (
                <><Play className="h-3.5 w-3.5" /> Run</>
              )}
            </button>
          )}
          {/* Copy button */}
          <button
            onClick={handleCopy}
            className="text-gray-400 hover:text-gray-200 transition-colors p-1"
            title="Copy code"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Editable code area */}
      <textarea
        ref={textareaRef}
        value={editableCode}
        onChange={(e) => setEditableCode(e.target.value)}
        className="w-full p-4 bg-gray-900 text-sm text-gray-100 font-mono whitespace-pre resize-y border-0 focus:outline-none focus:ring-0 min-h-[80px]"
        spellCheck={false}
        autoCorrect="off"
        autoCapitalize="off"
      />

      {/* Output panel */}
      {(output || error) && (
        <div className="border-t border-gray-700 bg-gray-950 px-4 py-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Terminal className="h-3.5 w-3.5 text-gray-500" />
            <span className="text-[10px] font-medium text-gray-500 uppercase tracking-wider">
              Output
            </span>
          </div>
          {error ? (
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-red-400 mt-0.5 flex-shrink-0" />
                <pre className="text-xs text-red-400 font-mono whitespace-pre-wrap">{error}</pre>
              </div>
              {isImportError && (
                <p className="text-xs text-gray-400 bg-gray-900 rounded p-2 border border-gray-800">
                  This module isn't available in the browser sandbox. You can edit the code above to use
                  available packages (numpy, pandas, scikit-learn, matplotlib, scipy), or copy the code
                  and run it locally.
                </p>
              )}
            </div>
          ) : output ? (
            <>
              {output.stdout && (
                <pre className="text-xs text-emerald-300 font-mono whitespace-pre-wrap">
                  {output.stdout}
                </pre>
              )}
              {output.stderr && (
                <pre className="text-xs text-amber-400 font-mono whitespace-pre-wrap mt-2">
                  {output.stderr}
                </pre>
              )}
              {!output.stdout && !output.stderr && (
                <p className="text-xs text-gray-500 italic">
                  Code executed successfully (no output)
                </p>
              )}
            </>
          ) : null}
        </div>
      )}
    </div>
  )
}
