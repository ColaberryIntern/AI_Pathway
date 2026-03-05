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

export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())

  // ChatGPT supports ?q= natively — opens with prompt pre-filled
  if (supportsUrlPrompt(llm.key)) {
    const encoded = encodeURIComponent(prompt)
    window.open(`${llm.url}?q=${encoded}`, '_blank')
    return
  }

  // Claude & Gemini: copy to clipboard + open (no native URL param support)
  await copyToClipboard(prompt)
  window.open(llm.url, '_blank')
}
