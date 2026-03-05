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

/** Get button label for the selected LLM */
export function getRunLabel(key?: string): string {
  const k = key || getPreferredLLM()
  const llm = getLLMOption(k)
  return `Run in ${llm.name}`
}

/**
 * Open the selected LLM with a prompt pre-filled via ?q= URL parameter.
 * All supported LLMs (ChatGPT, Claude, Gemini, Copilot) accept ?q=.
 */
export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())
  const encoded = encodeURIComponent(prompt)
  const separator = llm.url.includes('?') ? '&' : '?'
  window.open(`${llm.url}${separator}q=${encoded}`, '_blank')
}
