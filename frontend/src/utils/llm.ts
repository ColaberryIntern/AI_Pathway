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

/** LLMs that support ?q= URL parameter for prompt pre-fill */
const URL_PROMPT_LLMS = new Set(['chatgpt', 'claude'])

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

/** Whether the given LLM supports ?q= URL param */
export function supportsUrlPrompt(key?: string): boolean {
  return URL_PROMPT_LLMS.has(key || getPreferredLLM())
}

/** Get button label for the selected LLM */
export function getRunLabel(key?: string): string {
  const k = key || getPreferredLLM()
  const llm = getLLMOption(k)
  return supportsUrlPrompt(k) ? `Run in ${llm.name}` : `Copy & open ${llm.name}`
}

/** Show a brief toast notification */
function showCopiedToast(llmName: string): void {
  const el = document.createElement('div')
  el.textContent = `Prompt copied! Paste it in ${llmName}`
  el.style.cssText =
    'position:fixed;bottom:80px;right:24px;z-index:9999;background:#4f46e5;color:#fff;' +
    'padding:10px 18px;border-radius:10px;font-size:13px;font-weight:500;' +
    'box-shadow:0 4px 12px rgba(0,0,0,.15);transition:opacity .3s;opacity:0'
  document.body.appendChild(el)
  requestAnimationFrame(() => { el.style.opacity = '1' })
  setTimeout(() => {
    el.style.opacity = '0'
    setTimeout(() => el.remove(), 300)
  }, 3000)
}

/**
 * Open the selected LLM with a prompt.
 * ChatGPT & Claude: uses ?q= URL parameter for direct pre-fill.
 * Gemini & Copilot: copies prompt to clipboard, shows toast, opens site.
 */
export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())

  if (supportsUrlPrompt(llm.key)) {
    const encoded = encodeURIComponent(prompt)
    const separator = llm.url.includes('?') ? '&' : '?'
    window.open(`${llm.url}${separator}q=${encoded}`, '_blank')
  } else {
    await copyToClipboard(prompt)
    showCopiedToast(llm.name)
    window.open(llm.url, '_blank')
  }
}
