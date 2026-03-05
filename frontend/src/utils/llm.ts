import { copyToClipboard } from './clipboard'

export interface LLMOption {
  key: string
  name: string
  url: string
}

export const LLM_OPTIONS: LLMOption[] = [
  { key: 'chatgpt', name: 'ChatGPT', url: 'https://chatgpt.com/' },
  { key: 'claude', name: 'Claude', url: 'https://claude.ai/new' },
  { key: 'gemini', name: 'Gemini', url: 'https://gemini.google.com/app' },
  { key: 'copilot', name: 'Copilot', url: 'https://copilot.microsoft.com/' },
]

/** LLMs where ?q= reliably injects the prompt */
const URL_PROMPT_SUPPORTED = new Set(['chatgpt', 'claude'])

const STORAGE_KEY = 'preferred_llm'

export function getPreferredLLM(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || 'chatgpt'
  } catch {
    return 'chatgpt'
  }
}

export function setPreferredLLM(llm: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, llm)
  } catch {
    // localStorage unavailable
  }
}

export function getLLMOption(key: string): LLMOption {
  return LLM_OPTIONS.find((o) => o.key === key) || LLM_OPTIONS[0]
}

/** Whether the selected LLM supports ?q= URL prompt injection */
export function supportsUrlPrompt(key?: string): boolean {
  return URL_PROMPT_SUPPORTED.has(key || getPreferredLLM())
}

/** Get button label for the selected LLM */
export function getRunLabel(key?: string): string {
  const k = key || getPreferredLLM()
  const llm = getLLMOption(k)
  return supportsUrlPrompt(k) ? `Run in ${llm.name}` : `Copy & open ${llm.name}`
}

/** Show a brief toast telling the user to paste */
function showPasteToast(llmName: string): void {
  const el = document.createElement('div')
  el.textContent = `Prompt copied! Press Ctrl+V and Enter in ${llmName}`
  el.style.cssText =
    'position:fixed;bottom:80px;right:24px;z-index:9999;background:#4f46e5;color:#fff;' +
    'padding:12px 20px;border-radius:12px;font-size:13px;font-weight:500;' +
    'box-shadow:0 4px 14px rgba(0,0,0,.18);transition:opacity .3s;opacity:0'
  document.body.appendChild(el)
  requestAnimationFrame(() => { el.style.opacity = '1' })
  setTimeout(() => {
    el.style.opacity = '0'
    setTimeout(() => el.remove(), 300)
  }, 4000)
}

/**
 * Open the selected LLM with a prompt.
 *
 * ChatGPT & Claude  → ?q= URL parameter (prompt pre-filled automatically)
 * Copilot & Gemini  → clipboard copy + open site + toast instructing paste
 */
export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())

  if (supportsUrlPrompt(llm.key)) {
    // Direct URL injection
    const encoded = encodeURIComponent(prompt)
    const separator = llm.url.includes('?') ? '&' : '?'
    window.open(`${llm.url}${separator}q=${encoded}`, '_blank')
  } else {
    // Clipboard strategy for platforms without ?q= support
    await copyToClipboard(prompt)
    showPasteToast(llm.name)
    window.open(llm.url, '_blank')
  }
}
