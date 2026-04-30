/**
 * ChapterRenderer - Renders a 15-minute interactive chapter from ChapterSpec JSON.
 *
 * 5 sections: Scenario, Concepts, Example 1, Example 2, Agent Build
 * Based on Vivek's chapter format specification.
 */
import { useState, useEffect } from 'react'
import {
  CheckCircle, ChevronRight, Clock, Target, BookOpen,
  Lightbulb, Beaker, Wrench, Copy, Check, ExternalLink,
} from 'lucide-react'
import { openInLLM, getRunLabel, getPreferredLLM } from '../../utils/llm'

// Types matching ChapterSpec schema
interface ChapterMeta {
  chapter_title: string
  chapter_subtitle: string
  skill_id: string
  skill_name: string
  domain_id: string
  domain_name: string
  current_level: number
  target_level: number
  current_level_label: string
  target_level_label: string
  current_level_rubric: string
  target_level_rubric: string
  total_minutes: number
}

interface ConceptCard {
  identifier: string
  word: string
  headline: string
  body: string
  analogy: string
  color_role: string
}

interface PromptExample {
  label: string
  prompt: string
  output: string
  rating: number
  diagnosis: string
}

interface ExampleStep {
  step_number: number
  title: string
  content_type: string
  checklist_items?: Array<{ part: string; status: string; is_broken: boolean }>
  prompt_variant_ref?: string
  log_entries?: Array<{ key: string; value: string }>
  commentary?: string
}

interface ABVariant {
  id: string
  label: string
  prompt: string
  output: string
  rating: number
  why: string
}

interface PersonalizationField {
  key: string
  label: string
  placeholder: string
  input_type: string
}

interface ChapterSpec {
  meta: ChapterMeta
  scenario: {
    minutes: number
    kicker: string
    title: string
    narrative: string
    a_state: { level_display: string; quote: string }
    b_state: { level_display: string; quote: string }
    objectives: string[]
    why_it_matters: string
  }
  concepts: {
    minutes: number
    kicker: string
    title: string
    intro: string
    mnemonic?: string
    cards: ConceptCard[]
    pull_quote: string
  }
  example_1: {
    minutes: number
    kicker: string
    title: string
    setup: string
    original_prompt: PromptExample
    iterated_prompt: PromptExample
    steps: ExampleStep[]
    wrap_up?: string
  }
  example_2: {
    minutes: number
    kicker: string
    title: string
    setup: string
    original_prompt?: PromptExample
    iterated_prompt?: PromptExample
    steps: ExampleStep[]
    comparison: {
      test_question: string
      variants: ABVariant[]
      takeaway: string
    }
    wrap_up?: string
  }
  agent_build: {
    minutes: number
    kicker: string
    title: string
    intro: string
    capability_chips: Array<{ title: string; description: string }>
    personalization_fields: PersonalizationField[]
    system_prompt_template: string
    usage_steps: string[]
    final_affirmation: { rubric_quote: string; tie_back: string }
    next_skill_hint?: string
  }
}

const SECTIONS = [
  { id: 'scenario', label: 'Scenario', icon: Target, minutes: 2 },
  { id: 'concepts', label: 'Concepts', icon: Lightbulb, minutes: 3 },
  { id: 'example_1', label: 'Example 1', icon: BookOpen, minutes: 3 },
  { id: 'example_2', label: 'Example 2', icon: Beaker, minutes: 4 },
  { id: 'agent_build', label: 'Build', icon: Wrench, minutes: 3 },
]

const COLOR_MAP: Record<string, string> = {
  primary: 'bg-indigo-50 border-indigo-200 text-indigo-800',
  secondary: 'bg-sky-50 border-sky-200 text-sky-800',
  tertiary: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  accent: 'bg-amber-50 border-amber-200 text-amber-800',
}

export default function ChapterRenderer({ chapter }: { chapter: ChapterSpec }) {
  const [activeSection, setActiveSection] = useState(0)
  const [completed, setCompleted] = useState<Set<number>>(new Set())
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set())
  const [revealedSteps, setRevealedSteps] = useState<Set<string>>(new Set())
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null)
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({})
  const [copied, setCopied] = useState(false)
  const [llmKey, setLlmKey] = useState(getPreferredLLM)

  useEffect(() => {
    const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
    window.addEventListener('llm-changed', handler)
    return () => window.removeEventListener('llm-changed', handler)
  }, [])

  const TryInLLMButton = ({ prompt }: { prompt: string }) => {
    if (!prompt?.trim()) return null
    return (
      <button
        onClick={(e) => {
          e.stopPropagation()
          openInLLM(prompt, llmKey)
        }}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors px-2.5 py-1 rounded-md bg-indigo-50 hover:bg-indigo-100 border border-indigo-200"
        title={`Send this prompt to ${getRunLabel(llmKey).replace(/^(Run in |Copy & open )/, '')}`}
      >
        <ExternalLink className="h-3 w-3" />
        {getRunLabel(llmKey)}
      </button>
    )
  }

  const completeSection = () => {
    setCompleted(prev => new Set([...prev, activeSection]))
    if (activeSection < SECTIONS.length - 1) {
      setActiveSection(activeSection + 1)
    }
  }

  const renderStars = (rating: number) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating)
  }

  const interpolatePrompt = (template: string) => {
    let result = template
    for (const [key, value] of Object.entries(fieldValues)) {
      result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value || `{${key}}`)
    }
    return result
  }

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // ── Section Renderers ──

  const renderScenario = () => {
    const s = chapter.scenario
    return (
      <div className="space-y-6">
        <p className="text-sm font-medium text-gray-400 uppercase tracking-wider">{s.kicker}</p>
        <h2 className="text-2xl font-bold text-gray-900">{s.title}</h2>
        <p className="text-gray-700 leading-relaxed">{s.narrative}</p>

        {/* A → B Progression */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-xl border-2 border-gray-200">
            <div className="text-xs font-semibold text-gray-400 mb-2">{s.a_state.level_display}</div>
            <p className="text-gray-600 italic">"{s.a_state.quote}"</p>
          </div>
          <div className="p-4 bg-indigo-50 rounded-xl border-2 border-indigo-200">
            <div className="text-xs font-semibold text-indigo-500 mb-2">{s.b_state.level_display}</div>
            <p className="text-indigo-700 italic">"{s.b_state.quote}"</p>
          </div>
        </div>

        {/* Objectives */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">By the end of this chapter, you will:</h3>
          <ul className="space-y-2">
            {s.objectives.map((obj, i) => (
              <li key={i} className="flex items-start gap-2 text-gray-700">
                <CheckCircle className="h-5 w-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                {obj}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-sm text-gray-500 italic">{s.why_it_matters}</p>
      </div>
    )
  }

  const renderConcepts = () => {
    const c = chapter.concepts
    return (
      <div className="space-y-6">
        <p className="text-sm font-medium text-gray-400 uppercase tracking-wider">{c.kicker}</p>
        <h2 className="text-2xl font-bold text-gray-900">{c.title}</h2>
        <p className="text-gray-700">{c.intro}</p>
        {c.mnemonic && (
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 font-medium">
            {c.mnemonic}
          </div>
        )}

        {/* Concept Cards */}
        <div className="space-y-3">
          {c.cards.map((card) => {
            const isExpanded = expandedCards.has(card.identifier)
            const colors = COLOR_MAP[card.color_role] || COLOR_MAP.primary
            return (
              <div
                key={card.identifier}
                onClick={() => setExpandedCards(prev => {
                  const next = new Set(prev)
                  if (next.has(card.identifier)) next.delete(card.identifier)
                  else next.add(card.identifier)
                  return next
                })}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${colors}`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold opacity-60">{card.identifier}</span>
                  <div>
                    <span className="font-bold">{card.word}</span>
                    <span className="text-sm ml-2">{card.headline}</span>
                  </div>
                </div>
                {isExpanded && (
                  <div className="mt-3 pl-10 space-y-2">
                    <p className="text-sm">{card.body}</p>
                    <p className="text-xs italic opacity-70">Analogy: {card.analogy}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <blockquote className="border-l-4 border-indigo-300 pl-4 py-2 text-indigo-700 font-medium italic">
          {c.pull_quote}
        </blockquote>
      </div>
    )
  }

  const renderExample = (example: ChapterSpec['example_1'] | ChapterSpec['example_2'], sectionKey: string) => {
    const hasComparison = 'comparison' in example && (example as ChapterSpec['example_2']).comparison
    return (
      <div className="space-y-6">
        <p className="text-sm font-medium text-gray-400 uppercase tracking-wider">{example.kicker}</p>
        <h2 className="text-2xl font-bold text-gray-900">{example.title}</h2>
        <p className="text-gray-700">{example.setup}</p>

        {/* Original + Iterated Prompts */}
        {example.original_prompt && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-xl border">
              <div className="text-xs font-semibold text-gray-500 mb-2">{example.original_prompt.label}</div>
              <pre className="text-sm bg-white p-3 rounded border font-mono whitespace-pre-wrap mb-2">{example.original_prompt.prompt}</pre>
              <div className="text-sm text-gray-600 bg-white p-3 rounded border mb-2">{example.original_prompt.output}</div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-amber-500">{renderStars(example.original_prompt.rating)}</span>
                <span className="text-xs text-gray-500">{example.original_prompt.diagnosis}</span>
              </div>
              <TryInLLMButton prompt={example.original_prompt.prompt} />
            </div>
          </div>
        )}

        {/* Steps (step-gated reveal) */}
        {example.steps?.map((step) => {
          const stepKey = `${sectionKey}-${step.step_number}`
          const isRevealed = revealedSteps.has(stepKey) || step.step_number === 1
          return (
            <div key={stepKey}>
              {!isRevealed ? (
                <button
                  onClick={() => setRevealedSteps(prev => new Set([...prev, stepKey]))}
                  className="w-full p-3 text-left bg-gray-50 rounded-lg border border-dashed border-gray-300 hover:bg-gray-100 transition-colors"
                >
                  <span className="text-sm text-gray-500">Step {step.step_number}: </span>
                  <span className="text-sm font-medium text-indigo-600">{step.title} →</span>
                </button>
              ) : (
                <div className="p-4 bg-white rounded-xl border-2 border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-3">Step {step.step_number}: {step.title}</h4>
                  {step.content_type === 'diagnosis_checklist' && step.checklist_items && (
                    <div className="space-y-1">
                      {step.checklist_items.map((item, i) => (
                        <div key={i} className={`flex items-center gap-2 text-sm p-2 rounded ${item.is_broken ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                          <span className={item.is_broken ? 'text-red-500' : 'text-green-500'}>{item.is_broken ? '✗' : '✓'}</span>
                          <span className="font-medium">{item.part}:</span>
                          <span>{item.status}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {step.content_type === 'log_entry' && step.log_entries && (
                    <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-xs space-y-1">
                      {step.log_entries.map((entry, i) => (
                        <div key={i}><span className="text-gray-500">{entry.key}:</span> {entry.value}</div>
                      ))}
                    </div>
                  )}
                  {step.content_type === 'commentary' && step.commentary && (
                    <p className="text-gray-700">{step.commentary}</p>
                  )}
                  {step.content_type === 'prompt_variant' && example.iterated_prompt && (
                    <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                      <div className="text-xs font-semibold text-indigo-500 mb-2">{example.iterated_prompt.label}</div>
                      <pre className="text-sm bg-white p-3 rounded border font-mono whitespace-pre-wrap mb-2">{example.iterated_prompt.prompt}</pre>
                      <div className="text-sm text-gray-600 bg-white p-3 rounded border mb-2">{example.iterated_prompt.output}</div>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-amber-500">{renderStars(example.iterated_prompt.rating)}</span>
                        <span className="text-xs text-gray-500">{example.iterated_prompt.diagnosis}</span>
                      </div>
                      <TryInLLMButton prompt={example.iterated_prompt.prompt} />
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}

        {/* A/B Comparison (Example 2 only) */}
        {hasComparison && (
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">{(example as ChapterSpec['example_2']).comparison.test_question}</h3>
            <div className="grid grid-cols-2 gap-3">
              {(example as ChapterSpec['example_2']).comparison.variants.map((v) => (
                <div
                  key={v.id}
                  onClick={() => setSelectedVariant(selectedVariant === v.id ? null : v.id)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    selectedVariant === v.id ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-sm font-semibold mb-2">{v.label}</div>
                  <pre className="text-xs bg-white p-2 rounded border font-mono whitespace-pre-wrap mb-2">{v.prompt}</pre>
                  <div className="mb-2">
                    <TryInLLMButton prompt={v.prompt} />
                  </div>
                  {selectedVariant === v.id && (
                    <>
                      <div className="text-sm bg-white p-2 rounded border mb-2">{v.output}</div>
                      <div className="text-amber-500 text-sm">{renderStars(v.rating)}</div>
                      <p className="text-xs text-gray-600 mt-1">{v.why}</p>
                    </>
                  )}
                </div>
              ))}
            </div>
            {selectedVariant && (
              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-800 text-sm font-medium">
                Takeaway: {(example as ChapterSpec['example_2']).comparison.takeaway}
              </div>
            )}
          </div>
        )}

        {example.wrap_up && (
          <p className="text-gray-600 italic">{example.wrap_up}</p>
        )}
      </div>
    )
  }

  const renderAgentBuild = () => {
    const ab = chapter.agent_build
    const interpolated = interpolatePrompt(ab.system_prompt_template)

    return (
      <div className="space-y-6">
        <p className="text-sm font-medium text-gray-400 uppercase tracking-wider">{ab.kicker}</p>
        <h2 className="text-2xl font-bold text-gray-900">{ab.title}</h2>
        <p className="text-gray-700">{ab.intro}</p>

        {/* Capability Chips */}
        <div className="flex flex-wrap gap-2">
          {ab.capability_chips.map((chip, i) => (
            <div key={i} className="px-3 py-2 bg-indigo-50 rounded-lg border border-indigo-200" title={chip.description}>
              <span className="text-sm font-medium text-indigo-700">{chip.title}</span>
            </div>
          ))}
        </div>

        {/* Personalization Fields */}
        <div className="space-y-4 p-4 bg-gray-50 rounded-xl border">
          <h3 className="font-semibold text-gray-900">Personalize your agent:</h3>
          {ab.personalization_fields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
              {field.input_type === 'textarea' ? (
                <textarea
                  className="w-full p-2 border rounded-lg text-sm"
                  placeholder={field.placeholder}
                  rows={3}
                  value={fieldValues[field.key] || ''}
                  onChange={(e) => setFieldValues(prev => ({ ...prev, [field.key]: e.target.value }))}
                />
              ) : (
                <input
                  type="text"
                  className="w-full p-2 border rounded-lg text-sm"
                  placeholder={field.placeholder}
                  value={fieldValues[field.key] || ''}
                  onChange={(e) => setFieldValues(prev => ({ ...prev, [field.key]: e.target.value }))}
                />
              )}
            </div>
          ))}
        </div>

        {/* System Prompt (interpolated) */}
        <div className="relative">
          <pre className="bg-gray-900 text-green-400 p-4 rounded-xl font-mono text-xs whitespace-pre-wrap leading-relaxed">
            {interpolated}
          </pre>
          <div className="absolute top-2 right-2 flex items-center gap-2">
            <button
              onClick={() => openInLLM(interpolated, llmKey)}
              className="flex items-center gap-1.5 text-xs font-medium text-teal-300 hover:text-teal-200 transition-colors px-2.5 py-1.5 rounded-md bg-gray-700 hover:bg-gray-600 border border-gray-600"
              title={`Send this filled-in prompt to ${getRunLabel(llmKey).replace(/^(Run in |Copy & open )/, '')}`}
            >
              <ExternalLink className="h-3.5 w-3.5" />
              {getRunLabel(llmKey)}
            </button>
            <button
              onClick={() => copyToClipboard(interpolated)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              title="Copy to clipboard"
            >
              {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4 text-gray-300" />}
            </button>
          </div>
        </div>

        {/* Usage Steps */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">How to use it:</h3>
          <ol className="space-y-2">
            {ab.usage_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold">{i + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        {/* Final Affirmation */}
        <div className="p-4 bg-gradient-to-r from-indigo-50 to-sky-50 rounded-xl border border-indigo-200">
          <p className="text-indigo-700 font-medium italic">"{ab.final_affirmation.rubric_quote}"</p>
          <p className="text-sm text-gray-600 mt-2">{ab.final_affirmation.tie_back}</p>
        </div>

        {ab.next_skill_hint && (
          <p className="text-sm text-gray-400">Next up: {ab.next_skill_hint}</p>
        )}
      </div>
    )
  }

  // ── Main Render ──

  const sectionRenderers = [renderScenario, renderConcepts, () => renderExample(chapter.example_1, 'ex1'), () => renderExample(chapter.example_2, 'ex2'), renderAgentBuild]

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
          <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-full text-xs font-medium">{chapter.meta.domain_name}</span>
          <span>{chapter.meta.skill_id}</span>
          <span className="ml-auto flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{chapter.meta.total_minutes} min</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">{chapter.meta.chapter_title}</h1>
        <p className="text-gray-500 italic">{chapter.meta.chapter_subtitle}</p>
        <div className="flex items-center gap-2 mt-2 text-sm">
          <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">L{chapter.meta.current_level} {chapter.meta.current_level_label}</span>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <span className="px-2 py-1 bg-indigo-100 rounded text-indigo-700 font-medium">L{chapter.meta.target_level} {chapter.meta.target_level_label}</span>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="flex gap-1 bg-gray-50 p-1 rounded-xl">
        {SECTIONS.map((s, i) => {
          const Icon = s.icon
          const isActive = activeSection === i
          const isDone = completed.has(i)
          return (
            <button
              key={s.id}
              onClick={() => setActiveSection(i)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 px-2 rounded-lg text-xs font-medium transition-all ${
                isActive ? 'bg-white shadow text-indigo-700' : isDone ? 'text-emerald-600' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {isDone ? <CheckCircle className="h-3.5 w-3.5" /> : <Icon className="h-3.5 w-3.5" />}
              <span className="hidden sm:inline">{s.label}</span>
              <span className="text-[10px] text-gray-400">{s.minutes}m</span>
            </button>
          )
        })}
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 rounded-full transition-all duration-500"
          style={{ width: `${((completed.size + (activeSection > 0 ? 0 : 0)) / SECTIONS.length) * 100}%` }}
        />
      </div>

      {/* Active Section Content */}
      <div className="card border-2 border-gray-100">
        {sectionRenderers[activeSection]()}
      </div>

      {/* Next Button */}
      <div className="flex justify-end">
        <button
          onClick={completeSection}
          className="btn btn-primary flex items-center gap-2"
        >
          {activeSection < SECTIONS.length - 1 ? (
            <>Continue <ChevronRight className="h-4 w-4" /></>
          ) : completed.size >= SECTIONS.length - 1 ? (
            <>Complete Chapter <CheckCircle className="h-4 w-4" /></>
          ) : (
            <>Finish Section <ChevronRight className="h-4 w-4" /></>
          )}
        </button>
      </div>
    </div>
  )
}
