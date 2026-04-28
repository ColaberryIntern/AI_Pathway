# Chapter Generator — Developer Bundle

A pipeline for generating personalized 15-minute interactive lesson chapters from the **GenAI Skills Ontology v2.0**, given a skill ID and a current→target level gap.

## What's in this bundle

| File | Purpose |
|------|---------|
| `chapter-generator-prompt.md` | The system prompt for the LLM. Paste into your API call's `system` field. |
| `chapter-spec.schema.json` | JSON Schema (Draft 2020-12) for the structured output. Validate every generation against this. |
| `example-input.json` | Sample input payload your pipeline sends to the LLM. |
| `example-chapter-spec.json` | Sample structured output — the Jennifer C. chapter for SK.PRM.003 L2→L3. |
| `jennifer-prompt-debugging-chapter.jsx` | Reference JSX render — shows what the JSX side of the output should look like. |

## Pipeline overview

```
┌──────────────────────┐      ┌─────────────────────┐      ┌──────────────────────┐
│ Skill + level gap    │─────▶│ LLM call with       │─────▶│ Two outputs:         │
│ (from ontology +     │      │ chapter-generator   │      │ 1. ChapterSpec JSON  │
│  learner profile)    │      │ prompt as system    │      │ 2. Self-contained JSX│
└──────────────────────┘      └─────────────────────┘      └──────────────────────┘
                                                                      │
                                                                      ▼
                                                           ┌──────────────────────┐
                                                           │ Validate JSON vs.    │
                                                           │ chapter-spec.schema  │
                                                           │ Store both. Render.  │
                                                           └──────────────────────┘
```

## Input contract

The LLM receives a single JSON object:

```json
{
  "skill": {
    "id": "SK.PRM.003",
    "name": "Prompt debugging & iteration",
    "domain_id": "D.PRM",
    "domain_name": "Prompting",
    "rubric_by_level": [
      "Does not iterate on prompts",
      "Knows that prompts can be revised when output is unsatisfactory",
      "Systematically debugs prompts: isolates variables, tests variations, logs results",
      "Uses A/B prompt testing; tracks prompt versions with change notes",
      "Builds prompt debugging and regression testing tools",
      "Designs prompt lifecycle management systems with automated quality gates"
    ]
  },
  "current_level": 2,
  "target_level": 3
}
```

**Required keys:** `skill.id`, `skill.name`, `skill.rubric_by_level` (6-element array), `current_level`, `target_level`.

**Constraint:** `target_level = current_level + 1`. Every chapter teaches exactly one level gap.

## Output contract

The LLM returns **two fenced blocks** in one response:

````
```json
{ ...ChapterSpec... }
```

```jsx
import { useState } from "react";
...
export default function App() { ... }
```
````

Parse both blocks. Validate the JSON. Store both.

## Rendering options

You have two paths:

1. **Render the LLM's JSX directly.** Fastest path to screen. Good for MVP.
2. **Render your own React template fed by the `ChapterSpec` JSON.** Better for consistency, theming, analytics, A/B testing. Use the reference JSX in this bundle as the template base.

Production recommendation: ship path #2. It gives you control, lets you swap aesthetics, and means the LLM doesn't need to stay consistent across generations.

## Calling the LLM (example, Anthropic API)

```javascript
import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";

const client = new Anthropic();
const systemPrompt = fs.readFileSync("chapter-generator-prompt.md", "utf-8");

async function generateChapter(skill, currentLevel, targetLevel) {
  const input = {
    skill,
    current_level: currentLevel,
    target_level: targetLevel,
  };

  const response = await client.messages.create({
    model: "claude-opus-4-7",
    max_tokens: 16000,
    system: systemPrompt,
    messages: [{ role: "user", content: JSON.stringify(input) }],
  });

  const text = response.content[0].text;

  const jsonMatch = text.match(/```json\s*([\s\S]*?)```/);
  const jsxMatch = text.match(/```jsx\s*([\s\S]*?)```/);

  if (!jsonMatch || !jsxMatch) {
    throw new Error("LLM did not return both JSON and JSX blocks.");
  }

  const chapterSpec = JSON.parse(jsonMatch[1]);
  const jsxCode = jsxMatch[1];

  return { chapterSpec, jsxCode };
}
```

## Validation

Always validate the parsed JSON against the schema before storing:

```javascript
import Ajv from "ajv";
import schema from "./chapter-spec.schema.json";

const ajv = new Ajv();
const validate = ajv.compile(schema);

if (!validate(chapterSpec)) {
  console.error("ChapterSpec validation failed:", validate.errors);
  // retry, fall back, or surface to dashboard
}
```

Invalid generations should either be retried (with the validation errors fed back into a follow-up LLM call) or flagged for manual review.

## Design principles encoded in the prompt

- **5-section structure, 15 minutes total.** Non-negotiable. 2+3+3+4+3.
- **A→B framing** in Section 1 quotes the rubric strings verbatim (paraphrased first-person).
- **Examples require the target-level skill**, not the current-level skill.
- **Agent build (Section 5)** produces a takeaway artifact the learner can use the same day.
- **Accessibility defaults** are always on (short paragraphs, visual anchors, step-gated reveals, progress indicator).
- **Aesthetic direction** is picked from a fixed enum and must be consistent across all sections.

## Scaling to the full ontology

Since the input is just skill + levels, you can:

- Pre-generate chapters for the most common level gaps (e.g., L1→L2, L2→L3, L3→L4) for all 183 skills.
- Cache by `(skill_id, current_level, target_level)` key — 183 skills × 5 gaps = 915 chapters max.
- Regenerate on demand for edge cases or when rubric strings update.

## Extending later

If you later want learner-specific personalization (industry, role, target role), add an optional `learner` object to the input schema and a corresponding section to the system prompt — the output contract doesn't need to change. The `meta.generated_for` field is reserved for that purpose.
