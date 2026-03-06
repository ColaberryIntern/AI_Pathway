/**
 * Pyodide Web Worker — executes Python code in-browser via WebAssembly.
 *
 * Messages:
 *   { type: 'init', id }       → Load Pyodide + micropip from CDN
 *   { type: 'run', code, id }  → Auto-install imports, then execute code
 */

/* global importScripts, loadPyodide */

let pyodide = null

self.onmessage = async function (e) {
  const { type, code, id } = e.data

  if (type === 'init') {
    if (pyodide) {
      self.postMessage({ type: 'init-complete', id })
      return
    }
    try {
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js')
      pyodide = await loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/',
      })
      // Pre-load micropip so we can install pure-python packages on demand
      await pyodide.loadPackage('micropip')
      self.postMessage({ type: 'init-complete', id })
    } catch (err) {
      self.postMessage({ type: 'init-error', error: err.message, id })
    }
    return
  }

  if (type === 'run') {
    if (!pyodide) {
      self.postMessage({ type: 'error', error: 'Python runtime not loaded yet', id })
      return
    }
    try {
      // Auto-detect imports in the code and install required packages
      await pyodide.loadPackagesFromImports(code)

      // Redirect stdout/stderr to capture output
      pyodide.runPython(`
import sys
from io import StringIO
__stdout_capture = StringIO()
__stderr_capture = StringIO()
sys.stdout = __stdout_capture
sys.stderr = __stderr_capture
`)
      // Execute user code
      await pyodide.runPythonAsync(code)

      const stdout = pyodide.runPython('__stdout_capture.getvalue()')
      const stderr = pyodide.runPython('__stderr_capture.getvalue()')

      // Restore standard streams
      pyodide.runPython(`
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
`)
      self.postMessage({ type: 'result', stdout, stderr, id })
    } catch (err) {
      // Restore standard streams on error too
      try {
        pyodide.runPython(`
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
`)
      } catch (_) { /* ignore */ }
      self.postMessage({ type: 'error', error: err.message, id })
    }
  }
}
