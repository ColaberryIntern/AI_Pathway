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

export async function openInLLM(prompt: string, llmKey?: string): Promise<void> {
  const llm = getLLMOption(llmKey || getPreferredLLM())
  await copyToClipboard(prompt)
  window.open(llm.url, '_blank')
}
