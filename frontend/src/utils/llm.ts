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

/** ChatGPT supports ?q= for native prompt pre-fill; others require clipboard */
export function supportsUrlPrompt(key: string): boolean {
  return key === 'chatgpt'
}

/** Get button label depending on whether the LLM supports URL prompt */
export function getRunLabel(key?: string): string {
  const k = key || getPreferredLLM()
  const llm = getLLMOption(k)
  return supportsUrlPrompt(k) ? `Run in ${llm.name}` : `Copy & open ${llm.name}`
}

/** Show a brief toast notification when prompt is copied to clipboard */
function showCopiedToast(llmName: string): void {
  const toast = document.createElement('div')
  toast.textContent = `Prompt copied! Paste it in ${llmName}`
  toast.style.cssText = [
    'position:fixed',
    'bottom:5rem',
    'right:1.5rem',
    'z-index:9999',
    'padding:0.625rem 1rem',
    'border-radius:0.75rem',
    'background:#312e81',
    'color:#fff',
    'font-size:0.8125rem',
    'font-weight:500',
    'box-shadow:0 4px 12px rgba(0,0,0,0.15)',
    'opacity:0',
    'transition:opacity 0.2s ease',
  ].join(';')

  document.body.appendChild(toast)

  // Fade in
  requestAnimationFrame(() => { toast.style.opacity = '1' })

  // Fade out and remove after 3 seconds
  setTimeout(() => {
    toast.style.opacity = '0'
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}

export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())

  // ChatGPT supports ?q= natively — opens with prompt pre-filled
  if (supportsUrlPrompt(llm.key)) {
    const encoded = encodeURIComponent(prompt)
    window.open(`${llm.url}?q=${encoded}`, '_blank')
    return
  }

  // Claude, Gemini, Copilot: copy to clipboard + open + show toast
  await copyToClipboard(prompt)
  showCopiedToast(llm.name)
  window.open(llm.url, '_blank')
}
