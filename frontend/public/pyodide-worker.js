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
      // Pre-load common scientific packages so code examples work immediately
      await pyodide.loadPackage(['numpy', 'pandas', 'scipy', 'matplotlib', 'scikit-learn'])
      // Install requests via micropip (pure-python package, not in Pyodide built-ins)
      const micropip = pyodide.pyimport('micropip')
      await micropip.install('requests')
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

      // Set matplotlib to non-interactive backend and redirect stdout/stderr
      pyodide.runPython(`
import sys
from io import StringIO
__stdout_capture = StringIO()
__stderr_capture = StringIO()
sys.stdout = __stdout_capture
sys.stderr = __stderr_capture
import matplotlib
matplotlib.use('agg')
`)
      // Execute user code
      await pyodide.runPythonAsync(code)

      const stdout = pyodide.runPython('__stdout_capture.getvalue()')
      const stderr = pyodide.runPython('__stderr_capture.getvalue()')

      // Extract any matplotlib figures as base64 PNG images
      const imagesJson = pyodide.runPython(`
import matplotlib.pyplot as _plt
import base64 as _b64, io as _io, json as _json
_figures = []
for _fig_num in _plt.get_fignums():
    _buf = _io.BytesIO()
    _plt.figure(_fig_num).savefig(_buf, format='png', bbox_inches='tight', dpi=100)
    _buf.seek(0)
    _figures.append(_b64.b64encode(_buf.read()).decode())
_plt.close('all')
_json.dumps(_figures)
`)
      const images = JSON.parse(imagesJson)

      // Restore standard streams
      pyodide.runPython(`
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
`)
      self.postMessage({ type: 'result', stdout, stderr, images, id })
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
