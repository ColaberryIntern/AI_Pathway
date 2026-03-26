# AI-Native Learning System: Complete Architecture & Replication Guide

> A comprehensive reference for building AI-native learning platforms that mirror how modern engineering teams actually work. This document covers the philosophy, technical architecture, content model, AI mentor integration, and step-by-step replication guide.

---

## Table of Contents

1. [Philosophy: AI-Native Learning](#1-philosophy-ai-native-learning)
2. [The Ontology-Driven Skill System](#2-the-ontology-driven-skill-system)
3. [Learner Profiling & Skill Gap Analysis](#3-learner-profiling--skill-gap-analysis)
4. [Curriculum Generation Pipeline](#4-curriculum-generation-pipeline)
5. [Lesson Content Model (7 Sections)](#5-lesson-content-model-7-sections)
6. [AI Mentor Integration](#6-ai-mentor-integration)
7. [Interactive Learning Components](#7-interactive-learning-components)
8. [Progress Tracking & the Skill Genome](#8-progress-tracking--the-skill-genome)
9. [The Curiosity Engine](#9-the-curiosity-engine)
10. [End-to-End Example](#10-end-to-end-example)
11. [Replication Guide](#11-replication-guide-adding-this-to-other-platforms)

---

## 1. Philosophy: AI-Native Learning

### Why Traditional Learning Fails for AI Skills

Traditional training follows a linear model:

```
Lecture --> Memorization --> Quiz --> Project
```

This assumes learners must fully understand something before building. But modern engineering teams do the opposite -- they build while learning. Large language models changed the nature of engineering work. Engineers no longer need to memorize syntax, write every function manually, or read entire documentation sets. Instead, they focus on:

- System design
- Prompting AI effectively
- Evaluating AI output
- Iterating quickly

The skill shifted from **writing everything yourself** to **orchestrating intelligent tools**. Any learning system that teaches AI skills must reflect this reality.

### The AI-Native Learning Model

Every lesson in this system follows a modern engineering cycle:

```
Problem
  --> AI Collaboration
    --> Iteration
      --> Validation
        --> Reflection
```

Expanded into the core learning loop:

```
Understand the concept
       |
Ask AI for an approach
       |
Evaluate the output
       |
Improve the prompt
       |
Implement the solution
       |
Reflect on what happened
```

This loop mirrors the real workflows used by AI product teams at companies like Anthropic, OpenAI, and Google DeepMind. The platform guides learners through this process for every skill.

### Why This Is Better

| Traditional Model | AI-Native Model |
|---|---|
| Learn first, build later | Build while learning |
| Memorize syntax | Orchestrate AI tools |
| Static curriculum | Adaptive, gap-driven paths |
| One assessment at the end | Continuous feedback loop |
| Solo work | AI collaboration as a core skill |

The system encourages experimentation, rapid feedback, and AI collaboration. This dramatically speeds up learning because learners get immediate, contextual feedback on every interaction.

### Multiple Learning Modes

Modern learning works best when people switch between different types of engagement:

| Mode | Description |
|---|---|
| **Structured Learning** | Short concept snapshots to introduce ideas |
| **AI Collaboration** | Prompting and working with the AI mentor to solve problems |
| **Interactive Practice** | Prompt Lab for iterating on prompts with real AI responses |
| **Code Exploration** | Editable, runnable code examples in the browser |
| **Implementation Tasks** | Real-world challenges with AI-powered feedback |
| **Reflection** | Metacognitive questions that deepen understanding |

This mixture prevents the platform from becoming a single-style learning system.

---

## 2. The Ontology-Driven Skill System

Instead of organizing knowledge as a list of courses, the platform uses a **knowledge graph** (ontology) that maps relationships between skills.

### Structure

The ontology has three levels of organization:

```
Layer (8 total)
  --> Domain (22 total)
    --> Skill (186 total)
```

**Layers** represent broad categories of knowledge:

| Layer | Label | Example Domains |
|---|---|---|
| L.FOUNDATION | Foundation & Digital Literacy | D.DIG, D.CTIC |
| L.THEORY | AI Theory & Fundamentals | D.FND |
| L.APPLICATION | Applied AI | D.PRM, D.RAG, D.AGT, D.EVL, D.SEC |
| L.PRODUCT | Product & Strategy | D.PRD |
| L.INFRA | Infrastructure & Ops | D.OPS, D.MOD, D.TOOL, D.PRQ |
| L.SOFT | Strategy & Growth | D.SOF |
| L.GOVERNANCE | Governance & Compliance | D.GOV |
| L.EMERGING | Emerging (2025-26) | D.RSN, D.ACODE, D.COMP, D.PROTO |

**Domains** group related skills:

| Domain | Label | Skill Count |
|---|---|---|
| D.PRM | Prompting & HITL Workflows | 16 skills |
| D.RAG | Retrieval-Augmented Generation | 24 skills |
| D.AGT | Agents & Orchestration | 22 skills |
| D.EVL | Evaluation & Observability | 12 skills |
| D.ACODE | Agentic Coding | 8 skills |
| ... | ... | ... |

**Skills** are the atomic units of knowledge:

```json
{
  "id": "SK.PRM.003",
  "name": "Prompt debugging & iteration",
  "domain": "D.PRM",
  "level": 3,
  "prerequisites": ["SK.PRM.001"]
}
```

### Proficiency Scale (0-5)

Every skill has an inherent complexity level (ontology tier) and every learner has a current proficiency level:

| Level | Label | Meaning |
|---|---|---|
| 0 | Unaware | Has not encountered this skill |
| 1 | Aware | Knows the concept exists, can describe it |
| 2 | User | Can use tools/techniques with guidance |
| 3 | Practitioner | Can apply independently in projects |
| 4 | Builder | Can design and build systems using this skill |
| 5 | Architect | Can teach others, design at scale, innovate |

### Prerequisite Graph

Skills form a Directed Acyclic Graph (DAG) through prerequisites:

```
Prompt Engineering (SK.PRM.001)
       |
Prompt Debugging (SK.PRM.003)
       |
Prompt Chains (SK.PRM.005)
       |
Agent Design (SK.AGT.001)
       |
Multi-Agent Systems (SK.AGT.010)
```

This graph ensures learners never encounter a concept before mastering its foundations. The topological sort algorithm (Kahn's algorithm) enforces this ordering in every generated path.

### Data Schema

```json
{
  "version": "2.0.0",
  "skills": [
    {
      "id": "SK.PRM.003",
      "name": "Prompt debugging & iteration",
      "domain": "D.PRM",
      "level": 3,
      "prerequisites": ["SK.PRM.001"]
    }
  ],
  "domains": [
    {
      "id": "D.PRM",
      "label": "Prompting & HITL Workflows",
      "layer": "L.APPLICATION"
    }
  ],
  "layers": [
    {
      "id": "L.APPLICATION",
      "label": "Applied AI",
      "color": "#3B82F6",
      "domains": ["D.PRM", "D.RAG", "D.AGT", ...]
    }
  ],
  "proficiency_scale": [
    {"level": 0, "label": "Unaware"},
    {"level": 1, "label": "Aware"},
    {"level": 2, "label": "User"},
    {"level": 3, "label": "Practitioner"},
    {"level": 4, "label": "Builder"},
    {"level": 5, "label": "Architect"}
  ],
  "roles": [
    {
      "id": "ROLE.AI_PM",
      "label": "AI Product Manager",
      "focus_domains": ["D.PRM", "D.PRD", "D.EVL", "D.FND"]
    }
  ]
}
```

---

## 3. Learner Profiling & Skill Gap Analysis

### The Two-State Model

The system compares two states to determine what a learner needs:

```
STATE A (Where You Are)          STATE B (Where You're Going)
Current skills + levels    --->  Target skills + levels
                           GAP
```

### State A: Current Skills

State A is built from multiple sources:

1. **LinkedIn/Resume parsing** -- AI extracts skills from uploaded documents
2. **Self-assessment** -- Learner rates their own proficiency
3. **Job description analysis** -- Current JD reveals existing competencies
4. **Prerequisite inference** -- If you know skill X at level 3, the system infers you know its prerequisites at level 2

**State Inference Rules:**

```
If learner has SK.PRM.003 at level 3:
  Infer SK.PRM.001 (prerequisite) at level 2

If learner has ANY skill at L2+:
  Professional floor: All unknown skills start at L1 (not L0)

If learner knows a skill in domain D at level L:
  Domain floor: Other skills in D start at max(1, L-1)
```

**Confidence & Decay:**

Skills have confidence scores that decay over time:

```
effective_level = floor(level * confidence * decay_factor)
decay_factor = max(0.4, 1.0 - 0.05 * months_since_last_validated)
```

A skill validated 12 months ago retains only 40% confidence floor.

### State B: Target Skills

State B comes from two sources, merged together:

**A) Job Description Parsing (LLM-powered):**

The system sends the target JD to an AI agent that extracts required skills and maps them to ontology IDs with proficiency levels.

**B) Role Templates (deterministic):**

Pre-defined mappings of common roles to specific skill requirements:

```python
"AI Product Manager": {
    "SK.FND.001": 1,   # LLM fundamentals -- Aware only (PM doesn't build)
    "SK.PRD.002": 3,   # Workflow mapping -- Practitioner
    "SK.PRM.001": 2,   # Prompt constraints -- User (not Builder)
    "SK.EVL.001": 2,   # Eval types -- User (reads dashboards, doesn't build)
}
```

**Key Design Insight:** Role templates **decouple ontology tier** (inherent complexity) from **role requirement** (what the job actually needs). A PM needs to *read* evaluation dashboards (L2), not *build* them (L4). Without this decoupling, paths for non-technical roles become inappropriately difficult.

### Gap Analysis Engine

The gap engine scores and ranks every skill delta:

```
priority_score = (3 x delta) + (2 x role_relevance) - (0.5 x current_level)
```

Where:
- **delta** = target_level - current_level (bigger gaps rank higher)
- **role_relevance** = 1 if skill domain matches target role's focus domains, else 0
- **current_level** = higher existing skill slightly deprioritizes (learner already has foundation)

**Output:** A ranked list of skill gaps:

```
1. SK.AGT.001 (Tool definitions)       delta=3, score=8.5  -- CRITICAL
2. SK.EVL.001 (Eval frameworks)        delta=3, score=8.5  -- CRITICAL
3. SK.PRD.001 (Use-case selection)     delta=3, score=8.3  -- HIGH
4. SK.PRM.001 (Prompt constraints)     delta=2, score=6.0  -- HIGH
5. SK.SEC.001 (Prompt injection)       delta=2, score=5.8  -- MEDIUM
```

---

## 4. Curriculum Generation Pipeline

### Overview

The path generator is a **deterministic, 5-phase algorithm** that produces exactly 5 chapters from the ranked gap list. No LLM is involved in path structure -- this is pure algorithmic logic.

```
Ranked Gaps
    |
Phase 0: State A Expansion (infer prerequisites)
    |
Phase 0.5: Mandatory Category Injection
    |
Phase 1: Primary Candidate Selection (top 5 gaps)
    |
Phase 2: Prerequisite Resolution (back-pressure)
    |
Phase 3: Domain Diversity Enforcement (max 2 per domain)
    |
Phase 4: Topological Sort (Kahn's algorithm)
    |
Phase 5: Post-enforcement + top-up
    |
Output: 5 chapters with guaranteed properties
```

### Phase Details

**Phase 0.5 -- Mandatory Category Injection:**

Every path must include at least one skill from each of four mandatory categories:

| Category | Domains |
|---|---|
| Foundation | D.FND |
| Applied AI | D.PRM, D.RAG, D.AGT, D.MOD, D.MUL, D.OPS, D.TOOL |
| Evaluation | D.EVL |
| Safety | D.SEC, D.GOV |

This prevents one-dimensional paths (e.g., only prompting skills without understanding evaluation or safety).

**Phase 1 -- Primary Candidates:**

Select the top 5 gaps by priority score.

**Phase 2 -- Prerequisite Resolution (Back-Pressure):**

For each primary candidate, check if its prerequisites are met. If not, add prerequisite skills to the schedule. If total exceeds 5 chapters, drop the lowest-priority primary candidate. Repeat until everything fits.

**Phase 3 -- Domain Diversity:**

Maximum 2 chapters per domain. If a domain has 3+ chapters, replace the lowest-priority one with a skill from an under-represented domain.

**Phase 4 -- Topological Sort:**

Use Kahn's algorithm to order chapters so prerequisites always come before dependents. Tiebreaker: gap engine priority order.

**Phase 5 -- Post-enforcement:**

Verify all mandatory categories are covered. If any are missing, swap in the lowest-cost eligible skill. Fill remaining slots (if under 5) with next-best gaps.

### Output: Learning Path

```json
{
  "total_chapters": 5,
  "chapters": [
    {
      "chapter_number": 1,
      "primary_skill_id": "SK.PRQ.020",
      "primary_skill_name": "REST API basics",
      "current_level": 1,
      "target_level": 2,
      "domain": "D.PRQ"
    },
    {
      "chapter_number": 2,
      "primary_skill_id": "SK.AGT.010",
      "primary_skill_name": "Single-agent loops",
      "current_level": 1,
      "target_level": 2,
      "domain": "D.AGT"
    }
  ]
}
```

### Path Guarantees

| Property | Guarantee |
|---|---|
| Chapter count | Exactly 5 (or fewer if gap space exhausted) |
| Prerequisites | All prerequisites come before dependents |
| Domain diversity | Max 2 chapters per domain |
| Level progression | +1 per chapter (larger gaps close across multiple paths) |
| Category coverage | At least 1 skill from each mandatory category |
| Determinism | Same inputs always produce the same path |

---

## 5. Lesson Content Model (7 Sections)

### Hierarchy

```
Learning Path (1)
  --> Module (5, one per chapter)
    --> Lesson (3-5 per module, ~15-20 total)
      --> Content (7 sections, generated on-demand)
```

### Module Activation

When a learner starts their path, each chapter becomes a **Module** with a lesson outline generated by an AI agent:

```json
{
  "chapter_number": 1,
  "skill_id": "SK.PRM.001",
  "skill_name": "Instructions + constraints + format",
  "current_level": 1,
  "target_level": 2,
  "lesson_outline": [
    {
      "lesson_number": 1,
      "title": "Understanding Instructions and Constraints",
      "type": "concept",
      "focus_area": "Core concepts",
      "estimated_minutes": 30
    },
    {
      "lesson_number": 2,
      "title": "Hands-on Prompt Tuning",
      "type": "practice",
      "focus_area": "Practical application",
      "estimated_minutes": 40
    },
    {
      "lesson_number": 3,
      "title": "Assessment: Debugging Real Prompts",
      "type": "assessment",
      "focus_area": "Knowledge check",
      "estimated_minutes": 20
    }
  ]
}
```

Lesson types: `concept`, `practice`, `assessment`

### On-Demand Lesson Generation

Lesson content is **not** pre-generated. When a learner clicks "Start Lesson," an AI agent generates full content in ~8-15 seconds, personalized to the learner's industry, role, and previous lesson context. The content is then cached in the database so subsequent visits are instant.

### The 7-Section Lesson Structure

Every lesson contains up to 7 sections, each serving a specific pedagogical purpose:

#### Section 1: Concept Snapshot

A crisp 4-sentence explanation of the core concept. No filler, no preamble -- like a brilliant colleague giving a 30-second brief.

```
"Prompt constraints are explicit rules that bound the AI's output space.
By specifying format (JSON, markdown), length (max 200 words), and scope
(only discuss X topic), you dramatically reduce hallucination and increase
output reliability. Think of constraints as guardrails, not restrictions."
```

**Purpose:** Quick orientation. Learner knows what this lesson is about in 15 seconds.

#### Section 2: AI Strategy

How to use AI tools to work with this concept in practice:

```json
{
  "description": "How to use AI to debug and iterate on prompts",
  "when_to_use_ai": [
    "When generating variations of a prompt quickly",
    "When debugging why a prompt isn't producing expected output"
  ],
  "human_responsibilities": [
    "Validating outputs against your actual use case",
    "Deciding which variations to test first"
  ],
  "suggested_prompt": "Act as a senior prompt engineer. Review this prompt and identify 3 specific issues that could cause unreliable outputs: [paste prompt]"
}
```

**Purpose:** Teaches the learner when and how to collaborate with AI on this topic. This is a core differentiator from traditional courses.

#### Section 3: Prompt Template

A reusable, fill-in-the-blanks prompt template with placeholders:

```json
{
  "template": "You are {{ROLE}}. Your task is to {{TASK}}. Provide output in {{FORMAT}}. Constraints: {{CONSTRAINTS}}.",
  "placeholders": [
    {
      "name": "ROLE",
      "description": "The expert persona for the AI to adopt",
      "example": "a senior data analyst at a Fortune 500 company"
    },
    {
      "name": "TASK",
      "description": "The specific task to accomplish",
      "example": "Analyze this sales dataset and identify the top 3 trends"
    },
    {
      "name": "FORMAT",
      "description": "The desired output structure",
      "example": "a JSON object with 'findings' array and 'confidence' score"
    },
    {
      "name": "CONSTRAINTS",
      "description": "Boundaries on the output",
      "example": "Max 200 words. Only use data from Q3 2025. No speculation."
    }
  ],
  "expected_output_shape": "A JSON object with keys: findings (array of strings), confidence (float 0-1), methodology (string)"
}
```

**Purpose:** Gives learners a concrete, reusable tool they can immediately apply. Placeholders teach prompt structure by example. The "Test in Prompt Lab" button lets learners fill in values and see real AI responses.

#### Section 4: Code Examples

Runnable code blocks that demonstrate the concept programmatically:

```json
{
  "title": "Basic prompt with constraints using the Anthropic API",
  "language": "python",
  "code": "import anthropic\n\nclient = anthropic.Anthropic()\nmessage = client.messages.create(\n    model='claude-sonnet-4-20250514',\n    max_tokens=1024,\n    messages=[{\n        'role': 'user',\n        'content': 'Act as a data analyst. Analyze: [data]. Output JSON with keys: findings, confidence.'\n    }]\n)\nprint(message.content[0].text)",
  "explanation": "This example shows how to send a constrained prompt via API. The role instruction ('Act as...') sets context, while the format constraint ('Output JSON...') ensures structured output."
}
```

**Purpose:** Bridges conceptual understanding to real implementation. Code blocks are editable and runnable in the browser via Pyodide (WebAssembly Python).

#### Section 5: Implementation Task

A hands-on challenge where the learner works with an external AI tool and submits their conversation for feedback:

```json
{
  "title": "Debug a Real Prompting Failure",
  "description": "You have a prompt that's producing inconsistent output. Fix it using constraint techniques from this lesson.",
  "requirements": [
    "Show the original failing prompt and your fixed version",
    "Explain what went wrong in the original",
    "Demonstrate at least 2 iterations of refinement"
  ],
  "deliverable": "Your AI conversation history + brief explanation of what you learned",
  "requires_prompt_history": true,
  "requires_architecture_explanation": false,
  "estimated_minutes": 45
}
```

**Purpose:** Forces application of knowledge in a realistic scenario. The learner opens their preferred AI tool (ChatGPT, Claude, etc.), works through the challenge, then pastes their conversation back. An AI reviewer provides structured feedback on their prompting strategy.

**AI Feedback Structure:**

```json
{
  "strengths": ["Clear role instruction", "Good use of format constraints"],
  "improvements": ["Add explicit scope boundaries", "Include error handling instructions"],
  "prompt_strategy_tips": ["Use few-shot examples for complex formats", "Chain prompts for multi-step tasks"],
  "feedback": "Full narrative feedback paragraph..."
}
```

#### Section 6: Knowledge Checks

Quick-fire quiz questions with AI-powered follow-up:

```json
{
  "question": "Which constraint is most likely to improve structured output?",
  "options": [
    "A) 'Please be helpful'",
    "B) 'Output JSON with keys: id, name, score (0-100)'",
    "C) 'Try to be accurate'"
  ],
  "correct_answer": "B",
  "explanation": "Structured constraints (JSON format) are far more effective than vague directives.",
  "ai_followup_prompt": "Explain why JSON schema constraints work better than natural language requirements, covering how transformers process structured format information differently."
}
```

**Purpose:** Quick comprehension check. The `ai_followup_prompt` turns every question into a learning opportunity -- learners can ask the AI mentor to explain the answer in depth.

#### Section 7: Reflection Questions

Metacognitive prompts that encourage deeper thinking:

```json
{
  "question": "How did your understanding of constraints change after this lesson?",
  "prompt_for_deeper_thinking": "Act as a curriculum designer. Explain why well-defined constraints in prompts are as important as the task description itself, including 3 real-world scenarios where missing constraints caused AI output failures."
}
```

**Purpose:** Encourages the learner to step back and synthesize what they've learned. The "Ask AI Mentor" button sends the reflection prompt to the mentor for a guided discussion.

---

## 6. AI Mentor Integration

### Role of the AI Mentor

The AI mentor acts as a **Socratic learning coach** -- not a lecturer. It asks leading questions, suggests prompts to try, and guides learners to discover answers themselves.

### System Prompt (Core Behavior)

```
You are an AI learning mentor -- a warm, supportive, technically precise coach.

YOUR ROLE:
- Help learners understand concepts by asking leading questions (Socratic method)
- Suggest prompts they can try in the Prompt Lab
- Debug code and explain errors clearly
- Encourage AI collaboration -- teach them to work WITH AI, not just learn about it

RULES:
- NEVER give direct answers to exercises or implementation tasks
- Instead, break the problem down and guide the learner to the solution
- When a learner is confused, offer a simpler analogy first
- Always suggest 1-2 follow-up prompts they could try
- Keep responses concise (2-4 paragraphs max)
```

### Context Injection

The mentor receives lesson context automatically, so it knows what the learner is studying:

```json
{
  "lesson_title": "Understanding Instructions and Constraints",
  "skill_name": "Instructions + constraints + format",
  "skill_level": "L1 --> L2",
  "concept_snapshot": "First 200 chars of the lesson concept..."
}
```

This means the learner can say "I don't understand this" without explaining what "this" is -- the mentor already knows.

### Response Format

Every mentor response includes suggested prompts for continued exploration:

```
[Mentor's guidance response -- 2-4 paragraphs, Socratic style]

Try this prompt: "Act as a senior prompt engineer. Show me 3 examples
of how adding format constraints to a vague prompt dramatically
changes the output quality..."

Explore further: "Imagine you are building an AI-powered customer
service bot. What constraints would you add to ensure it never
reveals internal pricing logic?"

Explore further: "Compare the effectiveness of role-based constraints
vs format-based constraints for a code generation task..."
```

### Suggested Prompt Extraction (4-Tier Fallback)

The system guarantees the mentor always returns 2+ suggested prompts, even if the LLM response is malformed:

| Tier | Method | Trigger |
|---|---|---|
| 1 | Extract `"Explore further:"` prefixed lines | Primary |
| 2 | Extract `"Try this prompt:"` / `"Ask:"` lines | If Tier 1 empty |
| 3 | Extract quoted strings 30+ chars with role instructions | If Tier 2 empty |
| 4 | Generate context-based fallback from lesson data | If all empty |

### Conversation Isolation

Each lesson has its own conversation thread. This keeps context focused and prevents cross-lesson confusion:

```
Module 1, Lesson 1: [conversation about prompt constraints]
Module 1, Lesson 2: [separate conversation about prompt debugging]
Module 2, Lesson 1: [separate conversation about RAG basics]
```

### Confusion Recovery

When a learner marks content as "Confusing," the system:

1. Captures the specific text passage that confused them
2. Opens the mentor chat pre-loaded with that context
3. The mentor provides a simpler analogy and 2 exploration prompts

This creates a safety net -- no learner gets permanently stuck.

---

## 7. Interactive Learning Components

### 7.1 Prompt Lab

An interactive prompt iteration environment where learners can:

1. Write or paste a prompt
2. Execute it against a real LLM
3. See the response
4. Refine and iterate (up to 10 iterations per lesson)
5. Review their iteration history

**API Flow:**

```
POST /learn/{path_id}/prompt-lab/execute
{
  "lesson_id": "lesson_789",
  "prompt": "Act as a data analyst...",
  "iteration": 1
}

Response:
{
  "response": "[AI's response]",
  "iteration": 1,
  "execution_time_ms": 2340
}
```

**History Tracking:** Every prompt and response is stored, creating a visible record of the learner's iteration process. This history is available for review and becomes evidence for the Skill Genome.

### 7.2 Prompt Template Card

Displays the lesson's prompt template with syntax highlighting for `{{placeholders}}`. Features:

- **"Test in Prompt Lab" button** -- sends the template to the Prompt Lab
- **Placeholder Fill Modal** -- guided form where learners fill in each placeholder with their own values, seeing the description and example for each
- **Filled prompt execution** -- after filling, the complete prompt is sent to the Prompt Lab for immediate execution

**Flow:**

```
Template: "You are {{ROLE}}. {{TASK}}. Output: {{FORMAT}}."
    |
[Fill Placeholders] button
    |
Modal: ROLE = "senior data analyst"
       TASK = "analyze Q3 sales trends"
       FORMAT = "JSON with findings array"
    |
Filled: "You are senior data analyst. Analyze Q3 sales trends. Output: JSON with findings array."
    |
[Sent to Prompt Lab] --> Execute --> See response
```

### 7.3 Code Execution (Browser-Based Python)

Code examples are editable and runnable directly in the browser using **Pyodide** (CPython compiled to WebAssembly):

- **No server required** -- all execution happens client-side
- **Auto-installs packages** -- detects `import pandas`, `import sklearn`, etc. and installs them automatically
- **Available packages:** numpy, pandas, scikit-learn, matplotlib, scipy, sympy, regex
- **Sandbox:** No network access, no filesystem access

**Architecture:**

```
Browser Main Thread
    |
[Web Worker: pyodide-worker.js]
    |
1. Load Pyodide WASM runtime (~11MB, cached)
2. Pre-load micropip (package installer)
3. On code execution:
   a. loadPackagesFromImports(code) -- auto-install
   b. Redirect stdout/stderr
   c. runPythonAsync(code)
   d. Return captured output
```

### 7.4 Implementation Task Submission & AI Review

When a learner submits their implementation task:

1. **Learner** opens their preferred AI tool (ChatGPT, Claude, etc.)
2. **Learner** works through the task requirements
3. **Learner** pastes their full conversation (both prompts and responses)
4. **AI reviewer** analyzes their prompting strategy and provides structured feedback

**Review Criteria:**

- Does the prompt use a clear role instruction?
- Does it include specific constraints and deliverables?
- Does it provide enough context?
- What prompting techniques (chain-of-thought, few-shot, role-play) would improve it?
- If multi-turn, how effectively did they iterate and refine?

**Post-Submission:**

After receiving feedback, the system generates contextual follow-up questions the learner can ask the AI mentor:

```
"I just completed the task 'Debug a Real Prompting Failure' and received
feedback. The deliverable was: 'conversation history + explanation.'
Based on this, what are the most common gaps learners have?"
```

These questions bridge the implementation task to continued mentored learning.

### 7.5 Knowledge Check Quizzes

Multiple-choice questions with immediate feedback:

- Correct answer + explanation shown after selection
- `ai_followup_prompt` available for deeper exploration
- Quiz scores feed into Skill Mastery progress

---

## 8. Progress Tracking & the Skill Genome

### Skill Mastery (Per-Path)

Each skill in a learning path has a **SkillMastery** record that tracks fractional progress:

```
current_level = initial_level + (
    (target_level - initial_level) * (lessons_completed / total_lessons)
)
```

**Example:**
- Started at L1, targeting L2, 4 total lessons
- After completing 2 lessons: `1 + (2-1) * (2/4) = 1.5`
- After completing all 4: `1 + (2-1) * (4/4) = 2.0`

This provides smooth, visible progress rather than a binary "done/not done."

### The Skill Genome (Global Mastery)

While SkillMastery is per-path, the **Skill Genome** is a global overlay that aggregates evidence across ALL learning paths:

```json
{
  "ontology_node_id": "SK.PRM.001",
  "skill_name": "Instructions + constraints + format",
  "mastery_level": 1.8,
  "evidence_count": 5,
  "last_evidence": "quiz",
  "confidence": 0.82,
  "updated_at": "2025-03-06T14:23:45Z"
}
```

Instead of saying "Course completed," the system tracks:

```
Prompt Engineering      --> 80%
Agent Architecture      --> 60%
Vector Databases        --> 35%
Evaluation Frameworks   --> 45%
```

These scores update as learners complete lessons, experiments, and projects.

**Evidence Weighting:**

| Evidence Type | Weight | Example |
|---|---|---|
| Quiz score | Strongest | 88% on knowledge check |
| Project feedback | Moderate | AI review of implementation task |
| Lesson completion | Weaker | Finished a concept lesson |
| Mentor interaction | Implicit | Asked advanced questions |

**Confidence Decay:**

Like State A inference, genome entries decay over time if not reinforced:

```
confidence decays at 5% per month, with a 40% floor
```

A skill mastered 12 months ago but never practiced retains at most 40% confidence, signaling the system to recommend refresher content.

### Why Genome Is Separate from SkillMastery

| SkillMastery | Skill Genome |
|---|---|
| Per-path, per-skill | Global, per-user |
| Starts at initial_level for that path | Aggregates across ALL paths |
| Resets when starting a new path | Persists forever (with decay) |
| Measures path progress | Measures true mastery |

This allows: multiple concurrent learning paths with independent progress, a global skill portfolio view, and long-term memory of skills learned in previous paths.

---

## 9. The Curiosity Engine

### Lesson Reactions

Learners can react to lesson content:

| Reaction | Icon | Signal |
|---|---|---|
| Interesting | sparkle | Learner wants more of this |
| Helpful | thumbs up | Content was effective |
| Confusing | question mark | Learner needs help |

### How Reactions Drive Adaptation

- **"Confusing"** triggers the confusion recovery flow (mentor chat with context)
- **"Interesting"** signals areas for deeper exploration in future paths
- **"Helpful"** reinforces content quality signals

### Feedback Loop

```
Learner reactions
    |
Aggregated per lesson, per module, per skill
    |
Inform future content generation (LLM context)
    |
Personalize next path's content style
```

This keeps learning engaging and adaptive -- the system learns what works for each learner.

---

## 10. End-to-End Example

**Learner: Sarah, Marketing Manager targeting AI Product Manager**

### Step 1: Profile Creation

Sarah uploads her LinkedIn PDF. The system extracts:

```
Name: Sarah Chen
Current Role: Marketing Manager
Industry: B2B SaaS
Experience: 8 years
AI Knowledge: Basic
Tools Used: ChatGPT, Canva AI
```

She pastes the job description for "AI Product Manager" at a tech startup.

### Step 2: Skill Gap Analysis

```
State A (inferred from profile):
  SK.FND.001: 2  (LLM fundamentals)
  SK.PRM.001: 1  (Prompt basics)
  SK.PRD.001: 1  (Use-case selection)

State B (from JD + role template):
  SK.AGT.001: 3  (Tool definitions)
  SK.PRM.003: 3  (Prompt debugging)
  SK.EVL.001: 2  (Evaluation)
  SK.PRD.002: 3  (Workflow mapping)
  SK.SEC.001: 2  (Prompt injection)

Top gaps by priority:
  1. SK.AGT.001 (delta=3, score=8.5)
  2. SK.PRM.003 (delta=2, score=6.5)
  3. SK.PRD.002 (delta=2, score=6.3)
  4. SK.EVL.001 (delta=2, score=5.8)
  5. SK.SEC.001 (delta=2, score=5.5)
```

### Step 3: Path Generation

```
Phase 1: Top 5 candidates selected
Phase 2: SK.AGT.001 needs prerequisite SK.PRM.010 --> add, drop SK.SEC.001
Phase 3: Domain diversity check passes
Phase 4: Topological sort:
  1. SK.PRM.003 (Prompt debugging -- no prereqs missing)
  2. SK.PRM.010 (JSON/schema outputs -- prereq for agents)
  3. SK.AGT.001 (Tool definitions)
  4. SK.EVL.001 (Evaluation frameworks)
  5. SK.PRD.002 (Workflow mapping)
```

### Step 4: Module Activation

Each chapter gets 3-5 lessons. Sarah sees her dashboard:

```
Module 1: Prompt Debugging & Iteration (4 lessons)
Module 2: Structured Output with JSON (3 lessons)
Module 3: Agent Tool Definitions (4 lessons)
Module 4: Evaluation Frameworks (3 lessons)
Module 5: AI Workflow Mapping (4 lessons)

Total: 18 lessons, ~15 hours estimated
```

### Step 5: Learning a Lesson

Sarah starts Module 1, Lesson 1: "Why Prompts Fail"

1. **Concept Snapshot** -- reads 4 sentences about common prompt failure modes
2. **AI Strategy** -- learns when to use AI for prompt debugging
3. **Prompt Template** -- fills in `{{FAILING_PROMPT}}` and `{{EXPECTED_OUTPUT}}` placeholders
4. **Prompt Lab** -- runs the filled prompt, sees AI identify 3 issues. Iterates 2 more times.
5. **Code Example** -- runs a Python snippet showing API-based prompt with constraints
6. **Knowledge Check** -- scores 75% (1 wrong)
7. **Implementation Task** -- opens Claude, works through debugging a real prompt, pastes conversation
8. **AI Feedback** -- receives: "Strong role instruction, but missing scope constraints. Try adding: 'Only discuss the data provided.'"
9. **Reflection** -- clicks "Ask AI Mentor" on the reflection prompt, has a 3-message Socratic exchange
10. **Completes lesson** -- SkillMastery: 1.0 --> 1.25 (1 of 4 lessons done)

### Step 6: Path Completion

After 18 lessons across 5 modules:

```
Skill Genome updated:
  SK.PRM.003: L2.8, confidence 0.85
  SK.PRM.010: L2.0, confidence 0.90
  SK.AGT.001: L2.0, confidence 0.80
  SK.EVL.001: L2.0, confidence 0.85
  SK.PRD.002: L2.5, confidence 0.88
```

Sarah can generate a new path to continue closing remaining gaps.

---

## 11. Replication Guide: Adding This to Other Platforms

### Minimum Viable Components

To replicate this learning system for a different domain, you need:

#### 1. Skill Ontology (the knowledge graph)

Create a JSON file mapping your domain's skills:

```json
{
  "skills": [
    {"id": "SK.001", "name": "Skill Name", "domain": "D.01", "level": 2, "prerequisites": []}
  ],
  "domains": [
    {"id": "D.01", "label": "Domain Label", "layer": "L.CORE"}
  ],
  "layers": [
    {"id": "L.CORE", "label": "Core Skills", "domains": ["D.01"]}
  ]
}
```

**Guidelines:**
- Start with 30-50 skills (expand later)
- Keep prerequisite chains short (max depth 3-4)
- Use the 0-5 proficiency scale (it maps well to any domain)
- Define 3-5 mandatory categories that every path must cover

#### 2. Gap Engine (deterministic scoring)

Implement the priority scoring formula:

```
priority_score = (3 x delta) + (2 x role_relevance) - (0.5 x current_level)
```

This can be a simple function -- no ML required.

#### 3. Path Generator (5-phase algorithm)

The deterministic path generator ensures consistent, high-quality paths without LLM variability:

1. Select top N gaps
2. Resolve prerequisites (back-pressure)
3. Enforce domain diversity
4. Topological sort
5. Mandatory category enforcement

**Critical:** This must be deterministic. Same inputs = same output. Never use an LLM for path structure.

#### 4. Lesson Content Generator (LLM-powered)

Use an LLM to generate the 7-section lesson content on-demand. Provide:

- Skill name and description
- Current level --> target level
- Learner context (industry, role, previous lessons)
- Required sections (concept snapshot, AI strategy, prompt template, code examples, implementation task, knowledge checks, reflection)

**Cache aggressively.** Generate once, serve forever (with optional regeneration).

#### 5. AI Mentor (Socratic coach)

Key implementation details:

- **System prompt:** Socratic method, never give direct answers, always suggest 2+ follow-up prompts
- **Context injection:** Pass current lesson title, skill name, and concept snapshot
- **Conversation isolation:** Separate thread per lesson
- **Guaranteed suggestions:** 4-tier fallback ensures prompts are always returned
- **Confusion recovery:** "Confusing" reactions auto-open mentor with context

#### 6. Prompt Lab (interactive practice)

Minimum implementation:

- Text editor for prompts
- "Run" button that calls an LLM API
- Response display
- Iteration counter + history
- Rate limiting (10 iterations per lesson)

#### 7. Skill Genome (progress tracking)

Track per-skill mastery with fractional levels:

```
current_level = initial + (target - initial) * (completed / total)
```

Aggregate across paths for a global mastery view. Apply confidence decay over time.

### Integration Checklist

```
[ ] Skill ontology JSON (skills, domains, layers, prerequisites)
[ ] Role templates for common target roles
[ ] Gap engine with priority scoring
[ ] 5-phase deterministic path generator
[ ] Module outline agent (LLM: chapter --> 3-5 lesson outlines)
[ ] Lesson generator agent (LLM: outline --> 7-section content)
[ ] AI mentor agent (LLM: Socratic coaching with context)
[ ] Prompt Lab UI (prompt editor, execute, history)
[ ] Code execution sandbox (Pyodide or server-side)
[ ] Implementation task submission + AI review
[ ] Knowledge check quizzes with AI follow-up
[ ] Skill Mastery tracking (per-path, fractional)
[ ] Skill Genome tracking (global, with decay)
[ ] Lesson reactions (interesting, helpful, confusing)
[ ] Confusion recovery flow (reaction --> mentor chat)
```

### Architecture Diagram

```
                    LEARNER PROFILE
                         |
            +-----------+-----------+
            |                       |
        STATE A                 STATE B
     (current skills)        (target skills)
            |                       |
            +-----------+-----------+
                        |
                   GAP ENGINE
              (priority scoring)
                        |
                PATH GENERATOR
           (5-phase deterministic)
                        |
              5 CHAPTER PATH
                        |
              MODULE ACTIVATION
           (LLM: lesson outlines)
                        |
            +-----+-----+-----+-----+
            |     |     |     |     |
          Mod 1 Mod 2 Mod 3 Mod 4 Mod 5
            |
    LESSON GENERATION (on-demand)
            |
    +-------+-------+-------+-------+-------+-------+-------+
    |       |       |       |       |       |       |       |
  Concept  AI     Prompt   Code   Impl.   Quiz   Reflect
  Snapshot Strat. Template Blocks  Task   Check  Questions
                    |                |       |       |
                    v                v       v       v
              PROMPT LAB       AI REVIEW  GENOME  MENTOR
              (iterate)        (feedback) (track) (coach)
                                                    |
                                              SKILL GENOME
                                          (global mastery map)
```

### Key Design Principles

1. **Deterministic structure, generative content.** Path structure is algorithmic (reproducible). Lesson content is LLM-generated (personalized). Never mix these.

2. **Build while learning.** Every lesson includes hands-on components (Prompt Lab, code, implementation tasks). Theory alone is insufficient.

3. **AI as collaborator, not lecturer.** The mentor coaches via questions. The Prompt Lab lets learners practice with real AI. Implementation tasks require AI collaboration.

4. **Ontology over courses.** Skills are nodes in a graph, not items in a list. This enables gap analysis, prerequisite ordering, and adaptive paths.

5. **Continuous feedback, not end-of-course exams.** Every interaction (quiz, prompt iteration, task submission, mentor chat) generates evidence for the Skill Genome.

6. **Confusion is an input, not a failure.** "Confusing" reactions trigger recovery flows. The system gets stronger from learner struggles.

---

*This document describes the AI-Native Learning System architecture as implemented in the AI Pathway platform. It is designed to be domain-agnostic -- the same architecture can power learning systems for any skill domain by replacing the ontology and adjusting the lesson generation prompts.*
