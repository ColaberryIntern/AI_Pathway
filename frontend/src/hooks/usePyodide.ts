/**
 * React hook for in-browser Python execution via Pyodide (WebAssembly).
 *
 * Uses a singleton Web Worker so Pyodide (~11MB) is loaded once and
 * persists across component mounts/unmounts. The worker is only created
 * the first time `runCode()` is called.
 */

import { useState, useRef, useCallback } from 'react'

export type PyodideStatus = 'idle' | 'loading' | 'ready' | 'running' | 'error'

export interface PyodideResult {
  stdout: string
  stderr: string
}

// Module-scoped singleton — shared across all hook instances
let workerInstance: Worker | null = null
let workerReady = false
let initPromise: Promise<void> | null = null

export function usePyodide() {
  const [status, setStatus] = useState<PyodideStatus>(
    workerReady ? 'ready' : 'idle',
  )
  const [output, setOutput] = useState<PyodideResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const idCounter = useRef(0)

  const ensureWorker = useCallback((): Promise<void> => {
    if (workerReady && workerInstance) {
      setStatus('ready')
      return Promise.resolve()
    }
    if (initPromise) {
      setStatus('loading')
      return initPromise
    }

    setStatus('loading')
    initPromise = new Promise<void>((resolve, reject) => {
      workerInstance = new Worker('/pyodide-worker.js')
      const initId = ++idCounter.current

      const handler = (e: MessageEvent) => {
        if (e.data.id !== initId) return
        workerInstance!.removeEventListener('message', handler)
        if (e.data.type === 'init-complete') {
          workerReady = true
          setStatus('ready')
          resolve()
        } else {
          setStatus('error')
          setError(e.data.error || 'Failed to load Python runtime')
          initPromise = null
          reject(new Error(e.data.error))
        }
      }
      workerInstance.addEventListener('message', handler)
      workerInstance.postMessage({ type: 'init', id: initId })
    })
    return initPromise
  }, [])

  const runCode = useCallback(async (code: string): Promise<PyodideResult | undefined> => {
    setError(null)
    setOutput(null)
    try {
      await ensureWorker()
      setStatus('running')
      const runId = ++idCounter.current
      return new Promise<PyodideResult>((resolve, reject) => {
        const handler = (e: MessageEvent) => {
          if (e.data.id !== runId) return
          workerInstance!.removeEventListener('message', handler)
          if (e.data.type === 'result') {
            const result: PyodideResult = {
              stdout: e.data.stdout,
              stderr: e.data.stderr,
            }
            setOutput(result)
            setStatus('ready')
            resolve(result)
          } else {
            const errMsg = e.data.error || 'Code execution failed'
            setError(errMsg)
            setStatus('ready')
            reject(new Error(errMsg))
          }
        }
        workerInstance!.addEventListener('message', handler)
        workerInstance!.postMessage({ type: 'run', code, id: runId })
      })
    } catch (err) {
      setError((err as Error).message)
      setStatus('error')
      return undefined
    }
  }, [ensureWorker])

  return { status, output, error, runCode }
}
