# AI-Native Learning Platform Blueprint

> A complete, portable specification for building a personalized, AI-powered learning platform that generates adaptive curricula from skill gap analysis.
>
> **Version:** 1.0
> **Last Updated:** 2026-03-05
> **License:** Proprietary — for internal use and authorized implementations only

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Skill Ontology](#2-skill-ontology)
3. [Proficiency Scale](#3-proficiency-scale)
4. [Learner Profile Schema](#4-learner-profile-schema)
5. [Skill Gap Analysis Engine](#5-skill-gap-analysis-engine)
6. [Learning Path Generation](#6-learning-path-generation)
7. [Module & Lesson Structure](#7-module--lesson-structure)
8. [Lesson Content Schema](#8-lesson-content-schema)
9. [Content Generation System](#9-content-generation-system)
10. [AI Mentor System](#10-ai-mentor-system)
11. [Skill Genome (Mastery Tracking)](#11-skill-genome-mastery-tracking)
12. [Confusion Recovery System](#12-confusion-recovery-system)
13. [Assessment & Knowledge Checks](#13-assessment--knowledge-checks)
14. [LLM Integration (Run Prompts)](#14-llm-integration-run-prompts)
15. [API Endpoints Reference](#15-api-endpoints-reference)
16. [Frontend Component Architecture](#16-frontend-component-architecture)
17. [Database Models Reference](#17-database-models-reference)
18. [Agent Orchestration Pipeline](#18-agent-orchestration-pipeline)
19. [Quality Standards & Validation](#19-quality-standards--validation)
20. [Implementation Checklist](#20-implementation-checklist)

---

## 1. Platform Overview

### What This Platform Does

This platform generates **personalized, AI-native learning paths** that close the gap between a learner's current skills and their target role. It is designed for professionals transitioning into AI-adjacent roles (product managers, marketers, consultants, educators, etc.) who need to learn how to **work WITH AI**, not just learn about it.

### Core Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LEARNER PROFILE                            │
│  Current role, skills, experience, target job description    │
└──────────────┬───────────────────────────┬───────────────────┘
               │                           │
    ┌──────────▼──────────┐     ┌──────────▼──────────┐
    │  PROFILE ANALYZER   │     │    JD PARSER         │
    │  Extracts State A   │     │  Extracts State B    │
    │  (current skills)   │     │  (required skills)   │
    └──────────┬──────────┘     └──────────┬───────────┘
               │                           │
               └──────────┬────────────────┘
                          │
               ┌──────────▼──────────┐
               │   GAP ANALYZER      │
               │  Prioritized skill  │
               │  gaps with scoring  │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │  PATH GENERATOR     │
               │  5-chapter learning │
               │  path (deterministic│
               │  scaffold + LLM     │
               │  enrichment)        │
               └──────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │Module 1 │      │Module 2 │      │Module N │
   │3-5      │      │3-5      │      │3-5      │
   │lessons  │      │lessons  │      │lessons  │
   └────┬────┘      └────┬────┘      └────┬────┘
        │                │                │
   ┌────▼────────────────▼────────────────▼────┐
   │         ON-DEMAND LESSON GENERATION        │
   │  Content generated when learner opens      │
   │  lesson, then cached in database           │
   └───────────────────┬───────────────────────┘
                       │
   ┌───────────────────▼───────────────────────┐
   │            LEARNING EXPERIENCE             │
   │  Concept → Strategy → Prompt Lab →        │
   │  Implementation → Reflection → Quiz       │
   │  + AI Mentor + Confusion Recovery         │
   └───────────────────────────────────────────┘
```

### Design Principles

1. **AI-native pedagogy**: Lessons teach learners to work WITH AI, not just about AI
2. **Deterministic scaffolding + LLM enrichment**: The path structure is algorithmically determined (repeatable), content is enriched by LLM
3. **On-demand generation**: Lesson content is generated when the learner opens the lesson, then cached
4. **Skill ontology-driven**: All skills map to a formal ontology with prerequisites, domains, and proficiency levels
5. **Evidence-based mastery**: Skill mastery is tracked via multiple evidence types (quizzes, projects, lessons, mentor interactions)
6. **Socratic AI mentoring**: The AI mentor guides, never gives direct answers

---

## 2. Skill Ontology

The ontology is the backbone of the platform. Every skill, gap, path, and assessment maps to it.

### Structure

```
Ontology
  ├── Layers (7 categories)
  │   └── Domains (18 knowledge areas)
  │       └── Skills (150+ individual skills)
  │           └── Prerequisites (directed acyclic graph)
```

### Layers

| Layer ID | Label | Color | Purpose |
|----------|-------|-------|---------|
| `L.FOUNDATION` | Foundation | `#22c55e` | Digital literacy, critical thinking |
| `L.THEORY` | Theory | `#6366f1` | AI/ML fundamentals |
| `L.APPLICATION` | Application | `#06b6d4` | Prompting, RAG, agents, evaluation |
| `L.TOOLS` | Tools | `#10b981` | Frameworks and platforms |
| `L.TECH_PREREQ` | Technical Prerequisites | `#f59e0b` | Programming, data, APIs |
| `L.DOMAIN` | Domain | `#ec4899` | Governance, industry-specific |
| `L.SOFT` | Soft/Strategy | `#8b5cf6` | Product, communication, learning |

### Domains (18)

| Domain ID | Label | Layer | Example Skills |
|-----------|-------|-------|----------------|
| `D.DIG` | Digital Literacy | Foundation | File management, search, privacy |
| `D.CTIC` | Critical Thinking | Foundation | Source evaluation, bias detection |
| `D.FND` | AI Literacy & Foundations | Theory | LLM fundamentals, hallucinations, model types |
| `D.PRM` | Prompting & HITL Workflows | Application | Structured prompts, chain-of-thought, JSON output |
| `D.RAG` | Retrieval & RAG Systems | Application | Embedding, vector search, chunking |
| `D.AGT` | Agents & Orchestration | Application | Tool use, multi-agent, planning |
| `D.MOD` | Model Adaptation | Application | Fine-tuning, RLHF, LoRA |
| `D.MUL` | Multimodal AI | Application | Vision, audio, video generation |
| `D.EVL` | Evaluation & Observability | Application | Metrics, A/B testing, monitoring |
| `D.SEC` | Safety & Security | Application | Prompt injection, guardrails |
| `D.OPS` | LLMOps & Deployment | Application | Serving, scaling, cost management |
| `D.TOOL` | Tools & Frameworks | Tools | LangChain, OpenAI SDK, HuggingFace |
| `D.PRQ` | Technical Prerequisites | Tech | Python, APIs, SQL, Git |
| `D.GOV` | Governance & Compliance | Domain | AI policy, regulation, auditing |
| `D.DOM` | Domain Applications | Domain | Industry-specific AI use cases |
| `D.PRD` | Product & UX | Soft | AI product roadmaps, user research |
| `D.COM` | Communication & Collaboration | Soft | Explaining AI to stakeholders |
| `D.LRN` | Learning & Adaptation | Soft | Staying current, experimentation |

### Skill Definition Format

```json
{
  "id": "SK.PRM.001",
  "name": "Instructions + constraints + format",
  "domain": "D.PRM",
  "level": 2,
  "prerequisites": ["SK.PRM.000", "SK.FND.001"]
}
```

**Field definitions:**
- `id`: Unique identifier in format `SK.{DOMAIN_SHORT}.{NUMBER}`
- `name`: Human-readable skill name
- `domain`: Which knowledge domain this belongs to
- `level`: Ontology-defined baseline difficulty (1-5)
- `prerequisites`: Skill IDs that must be learned before this skill (depth-1 only)

### Mandatory Domain Coverage

Every learning path MUST include at least one skill from each of these categories:

| Category | Domains | Rationale |
|----------|---------|-----------|
| Foundation | `D.FND` | Every learner needs AI literacy basics |
| Applied AI | `D.PRM`, `D.RAG`, `D.AGT`, `D.MOD`, `D.MUL`, `D.OPS`, `D.TOOL` | At least one applied skill |
| Evaluation | `D.EVL` | Must know how to measure AI quality |
| Safety | `D.SEC`, `D.GOV` | Must understand AI risks |

---

## 3. Proficiency Scale

All skill levels use a 0-5 scale:

| Level | Label | Definition | Example |
|-------|-------|-----------|---------|
| **0** | Unaware | Has not heard of it | "What is prompt engineering?" |
| **1** | Aware | Can explain basics | "Prompt engineering means writing better instructions for AI" |
| **2** | User | Can apply with help | Uses ChatGPT with templates, follows guides |
| **3** | Practitioner | Adapts independently | Designs own prompt strategies, debugs failures |
| **4** | Builder | Ships solutions | Builds prompt pipelines, automated workflows |
| **5** | Architect | Designs systems | Designs multi-agent architectures, trains teams |

### Calibration for Job Descriptions

When parsing a job description, map language to levels:

| JD Language | Mapped Level |
|-------------|-------------|
| "Familiarity with", "Awareness of" | L1 (Aware) |
| "Experience with", "Can apply" | L2 (User) |
| "Strong understanding", "Deep knowledge" | L3 (Practitioner) |
| "Hands-on building", "Implement", "Develop" | L4 (Builder) |
| "Design systems", "Lead architecture", "Define strategy" | L5 (Architect) |

### Role-Based Calibration

| Role Seniority | Typical Level Range |
|---------------|-------------------|
| Entry-level | L1-L3 for core skills |
| Mid-level | L2-L4 for core skills |
| Senior/Lead/Staff | L3-L5 for core skills |

---

## 4. Learner Profile Schema

A learner profile captures everything needed to compute skill gaps and personalize content.

```json
{
  "id": "unique-id",
  "name": "Alex Rivera",
  "current_role": "Marketing Manager",
  "target_role": "AI Product Manager",
  "industry": "Consumer Goods / Retail Marketing",
  "location": "U.S.",
  "experience_years": 10,
  "ai_exposure_level": "None | Basic | Intermediate | Advanced",
  "tools_used": ["ChatGPT", "Claude", "Canva AI"],
  "technical_background": "Basic scripting (Excel macros), no formal ML experience",
  "archetype": "Career Switcher | Upskiller | Explorer",

  "current_profile": {
    "summary": "Marketing Manager with 10 years of experience in consumer goods. Led digital transformation of campaign analytics. Regular ChatGPT user for content creation.",
    "technical_skills": ["SQL (basic)", "Analytics dashboards", "A/B testing", "Excel macros"],
    "soft_skills": ["Stakeholder management", "Team leadership", "Cross-functional collaboration"],
    "ai_experience": "Regular user of ChatGPT for content drafts and brainstorming. No systems built, no API experience."
  },

  "learning_intent": "Pivot into AI product work. Want to understand how to define AI product requirements, evaluate models, and collaborate with engineering teams.",

  "target_jd": {
    "title": "AI Product Manager (GenAI features)",
    "requirements": [
      "Own AI product roadmap for customer-facing features",
      "Define evaluation criteria for LLM outputs",
      "Work with ML engineers on prompt engineering and model selection",
      "Design human-in-the-loop review workflows",
      "Strong understanding of LLM capabilities and limitations"
    ]
  },

  "estimated_current_skills": {
    "SK.DIG.001": 3,
    "SK.FND.000": 1,
    "SK.PRM.000": 2,
    "SK.COM.001": 3
  }
}
```

### Required Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | Yes | |
| `current_role` | string | Yes | |
| `target_role` | string | Yes | |
| `industry` | string | Yes | Used for content personalization |
| `experience_years` | integer | Yes | Affects proficiency floors |
| `ai_exposure_level` | enum | Yes | `None`, `Basic`, `Intermediate`, `Advanced` |
| `tools_used` | string[] | No | AI tools already in use |
| `technical_background` | string | Yes | Free text |
| `current_profile.summary` | string | Yes | 2-3 paragraph background |
| `current_profile.technical_skills` | string[] | Yes | |
| `current_profile.soft_skills` | string[] | No | |
| `current_profile.ai_experience` | string | Yes | |
| `learning_intent` | string | Yes | What they want to achieve |
| `target_jd.title` | string | Yes | Target job title |
| `target_jd.requirements` | string[] | Yes | Job requirements (3-10 items) |
| `estimated_current_skills` | object | No | Pre-assessed skill levels `{skill_id: level}` |

---

## 5. Skill Gap Analysis Engine

The gap analysis engine computes the delta between what a learner knows (State A) and what their target role requires (State B), then prioritizes gaps for learning.

### Pipeline

```
Profile → Profile Analyzer Agent → State A (current skill levels)
JD Text → JD Parser Agent        → State B (required skill levels)
(State A, State B) → Gap Engine  → Prioritized gap list
```

### State A Extraction (Profile Analyzer Agent)

**System prompt directives:**
- Map the learner's profile to ontology skills with proficiency levels
- Consider: tools used, technical background, years of experience, AI exposure
- Return top 10 current skills with rationale
- Apply proficiency scale strictly

**Output:**
```json
{
  "state_a_skills": {
    "SK.DIG.001": 3,
    "SK.PRM.000": 2,
    "SK.FND.001": 1
  },
  "top_10_current_skills": [
    {
      "rank": 1,
      "skill_id": "SK.PRM.000",
      "skill_name": "Writing clear requests to AI",
      "domain": "D.PRM",
      "current_level": 2,
      "rationale": "Uses ChatGPT daily with structured prompts for content creation"
    }
  ],
  "profile_summary": "Marketing professional with basic AI tool usage...",
  "recommended_focus_domains": ["D.FND", "D.PRM", "D.EVL"]
}
```

### State B Extraction (JD Parser Agent)

**System prompt directives:**
- Extract required skills from job description text
- Map to ontology skills with required proficiency levels
- Use calibration rules (see Section 3)
- Return top 10 target skills with importance ranking

**Output:**
```json
{
  "state_b_skills": {
    "SK.PRM.010": 3,
    "SK.EVL.001": 2,
    "SK.FND.002": 3
  },
  "top_10_target_skills": [
    {
      "rank": 1,
      "skill_id": "SK.PRM.010",
      "skill_name": "JSON/schema outputs",
      "domain": "D.PRM",
      "required_level": 3,
      "importance": "high",
      "rationale": "JD requires structured prompt engineering for API integrations"
    }
  ]
}
```

### Gap Scoring Formula

```
priority_score = (3 × delta) + (2 × role_relevance) - (0.5 × skill_level)
```

| Weight | Factor | Description |
|--------|--------|-------------|
| **3** | `delta` | `target_level - current_level` — strongest signal |
| **2** | `role_relevance` | 1 if skill domain is in target role's focus domains, else 0 |
| **-0.5** | `skill_level` | Ontology baseline level — mild penalty for architect-tier skills |

### Proficiency Floors

Before computing gaps, apply these floors to State A to avoid underestimating experienced learners:

| Floor | Rule | Example |
|-------|------|---------|
| **Professional floor** | If learner has ANY skill at L2+, unknown skills start at L1 | Marketing manager with L3 in digital literacy → all unknown skills start at L1 |
| **Domain floor** | If learner knows ANY skill in a domain, others in that domain start at `max(1, domain_max - 1)` | Knows SK.PRM.000 at L2 → other prompting skills start at L1 |
| **Skill-level floor** | If learner has ANY skill at L3+, unknown intermediate+ skills start at L2 | Senior professional → intermediate ontology skills assumed at L2 |

### Gap Output

```json
{
  "gaps": [
    {
      "skill_id": "SK.FND.001",
      "skill_name": "LLM fundamentals (tokens, context, prediction)",
      "domain": "D.FND",
      "current_level": 0,
      "required_level": 3,
      "delta": 3,
      "priority_score": 10.5,
      "prerequisites": ["SK.FND.000"]
    }
  ],
  "summary": {
    "total_gaps": 18,
    "primary_domains": ["D.FND", "D.PRM", "D.EVL"],
    "estimated_learning_time": "40-60 hours"
  }
}
```

---

## 6. Learning Path Generation

Path generation is a **two-phase** process: deterministic scaffold + LLM enrichment.

### Phase 1: Deterministic Scaffold (No LLM)

This phase is fully algorithmic and repeatable. Same inputs always produce the same output.

```
Step 0: Expand State A with inferred prerequisites
  → Fill missing skills using prerequisite DAG
  → Apply proficiency floors

Step 0.5: Ensure mandatory domain coverage in State B
  → Inject lowest-level skills from missing mandatory domains (D.FND, D.EVL, D.SEC/D.GOV)

Step 1: Select top 5 primary skills from ranked gaps
  → Highest priority_score first

Step 2: Resolve prerequisites with back-pressure
  → For each primary skill, find missing depth-1 prerequisites
  → If total skills > MAX_CHAPTERS (5), drop lowest-priority primary
  → Place prerequisites immediately before dependent skill

Step 3: Enforce domain diversity
  → Max 2 chapters from same domain
  → Replace duplicates with next-best gaps

Step 4: Post-enforce mandatory categories
  → If any mandatory category missing, swap in skills

Step 5: Top-up remaining slots to 5 chapters
  → Fill with highest-priority remaining gaps
```

**Rules:**
- Maximum 5 chapters per path
- One skill per chapter
- Each chapter advances exactly +1 proficiency level
- Prerequisites must appear before dependent skills

**Output: Chapter scaffold**
```json
{
  "total_chapters": 5,
  "chapters": [
    {
      "chapter_number": 1,
      "skill_id": "SK.FND.001",
      "skill_name": "LLM fundamentals (tokens, context, prediction)",
      "current_level": 0,
      "target_level": 1
    },
    {
      "chapter_number": 2,
      "skill_id": "SK.PRM.001",
      "skill_name": "Instructions + constraints + format",
      "current_level": 1,
      "target_level": 2
    }
  ]
}
```

### Phase 2: LLM Content Enrichment

Takes the locked scaffold and adds pedagogical content. The LLM MUST NOT modify: `chapter_number`, `skill_id`, `skill_name`, `current_level`, `target_level`.

**Enrichment fields per chapter:**

```json
{
  "chapter_number": 1,
  "skill_id": "SK.FND.001",
  "skill_name": "LLM fundamentals",
  "current_level": 0,
  "target_level": 1,

  "title": "Understanding How Large Language Models Work",

  "learning_objectives": [
    "Identify the key components of LLM architecture",
    "Explain how tokens and context windows affect model behavior",
    "Describe the differences between major model families"
  ],

  "introduction": "200-300 word narrative connecting learner's background to this topic...",

  "core_concepts": [
    {
      "title": "Tokens and Tokenization",
      "content": "Tokens are the fundamental units that LLMs process...",
      "examples": ["'Hello world' = 2 tokens", "'ChatGPT' = 1-3 tokens depending on model"]
    }
  ],

  "prompting_examples": [
    {
      "title": "Simple Token-Aware Prompt",
      "description": "Shows how understanding tokens improves prompting",
      "prompt": "Explain tokenization in LLMs. Keep your response under 100 tokens.",
      "expected_output": "Concise explanation within token budget",
      "customization_tips": "Replace 'tokenization' with your specific topic"
    }
  ],

  "agent_examples": [
    {
      "title": "Token Counter Agent",
      "scenario": "Pre-flight cost analysis before API calls",
      "agent_role": "Token estimation assistant",
      "instructions": ["Accept user prompt", "Count tokens", "Estimate cost"],
      "expected_behavior": "Returns token count and cost estimate",
      "use_case": "Budget planning for LLM applications"
    }
  ],

  "exercises": [
    {
      "id": "ex1",
      "title": "Token Counting Exercise",
      "description": "Count tokens in various text samples",
      "type": "hands-on",
      "estimated_time_minutes": 20,
      "instructions": ["Use a tokenizer tool", "Count tokens in 5 texts", "Compare results"],
      "deliverable": "Token count comparison table"
    }
  ],

  "applied_project": {
    "project_title": "Build a Token Cost Calculator",
    "project_description": "Create a tool that estimates API costs based on token counts",
    "deliverable": "Working script + documentation",
    "estimated_time_minutes": 120
  },

  "key_takeaways": [
    "Tokens are subword units; most words = multiple tokens",
    "Context windows limit how much text models can process",
    "Different models have different tokenizers and context sizes",
    "Token awareness directly impacts cost and performance",
    "Understanding tokenization is foundational for prompt engineering"
  ],

  "exact_prompt": {
    "title": "LLM Fundamentals Deep Dive",
    "context": "Teaching a professional new to AI",
    "prompt_text": "Act as a senior ML engineer. Explain how tokenization works...",
    "expected_output": "Clear explanation with concrete examples",
    "how_to_customize": "Replace domain references with your industry"
  },

  "self_assessment_questions": [
    {
      "question": "What is a token in LLM context?",
      "options": ["A word", "A subword unit", "An API call", "A model parameter"],
      "answer": "A subword unit"
    }
  ],

  "industry_context": "In your industry, understanding tokenization helps optimize...",
  "estimated_time_hours": 4.5
}
```

**Quality requirements for enrichment:**
- Learning objectives: 3-5 per chapter, using Bloom's taxonomy verbs
- Bloom's progression across path: early chapters use lower-order verbs (Identify, Describe), later chapters use higher-order (Analyze, Design, Evaluate)
- Each chapter MUST have exactly 1 applied project with a concrete deliverable
- Complexity increases across the path

---

## 7. Module & Lesson Structure

### Hierarchy

```
Learning Path
  └── Module (1 per chapter, max 5)
       ├── skill_id, skill_name
       ├── current_level → target_level
       ├── lesson_outline (generated by Module Outline Agent)
       └── Lessons (3-5 per module)
            ├── lesson_type: concept | practice | assessment
            ├── content (generated on-demand)
            └── status: not_started | in_progress | completed
```

### Module Schema

```json
{
  "id": "uuid",
  "path_id": "uuid",
  "chapter_number": 1,
  "skill_id": "SK.FND.001",
  "skill_name": "LLM fundamentals (tokens, context, prediction)",
  "title": "Understanding Tokens and Context Windows",
  "current_level": 0,
  "target_level": 1,
  "lesson_outline": [
    {
      "lesson_number": 1,
      "title": "What Are Tokens and Why They Matter",
      "type": "concept",
      "focus_area": "Token mechanics and context windows",
      "estimated_minutes": 30
    },
    {
      "lesson_number": 2,
      "title": "Hands-On: Counting Tokens and Estimating Costs",
      "type": "practice",
      "focus_area": "Using tokenizer tools and budgeting",
      "estimated_minutes": 40
    },
    {
      "lesson_number": 3,
      "title": "Assessment: LLM Fundamentals Mastery Check",
      "type": "assessment",
      "focus_area": "Comprehensive knowledge validation",
      "estimated_minutes": 25
    }
  ],
  "total_lessons": 3
}
```

### Lesson Outline Rules

1. Every module MUST end with an `assessment` lesson
2. Start with `concept`, then `practice`, then `assessment`
3. 3-5 lessons total per module (prefer 4)
4. Each lesson has a unique `focus_area` within the module's skill

### Lesson Types

| Type | Purpose | Duration | Contains |
|------|---------|----------|----------|
| `concept` | Theory and explanation | ~30 min | Strong concept_snapshot, explanation, code examples |
| `practice` | Hands-on exercises | ~40 min | Prompt Lab, implementation task, exercises |
| `assessment` | Knowledge validation | ~25 min | Knowledge checks (quiz), reflection |

---

## 8. Lesson Content Schema

Each lesson contains 10 content sections. Content is generated on-demand and cached.

### Complete Schema

```typescript
interface LessonContent {
  // === PRIMARY AI-NATIVE SECTIONS ===
  concept_snapshot: string              // 1. Core concept (4 sentences max)
  ai_strategy: AIStrategy              // 2. When to use AI vs. human
  prompt_template: PromptTemplate      // 3. Copy-pasteable prompt with placeholders
  implementation_task: ImplementationTask // 4. Hands-on task with submission
  reflection_questions: ReflectionQuestion[] // 5. Guided reflection with deeper prompts

  // === SUPPORTING SECTIONS ===
  explanation: string                   // 6. Reference summary (2-3 paragraphs)
  code_examples: CodeExample[]          // 7. Runnable code samples
  knowledge_checks: KnowledgeCheck[]    // 8. Quiz questions
  exercises: Exercise[]                 // 9. Practice exercises
  hands_on_tasks: HandsOnTask[]         // 10. Project-based tasks
}
```

### Section 1: Concept Snapshot

The **primary learning content**. Maximum 4 sentences. No filler.

```json
{
  "concept_snapshot": "Prompt chaining breaks complex tasks into sequential steps where each AI response feeds into the next prompt. This technique reduces token overhead by letting the AI focus on one subtask at a time. Common patterns include context-building chains (gather info, then analyze) and refinement chains (draft, then edit). Effective chains are typically 2-4 steps with clear handoff points between each."
}
```

**Quality rules:**
- Maximum 4 sentences
- No filler, no preamble
- Like "a brilliant colleague giving a 30-second brief"
- Specific to the topic; no generic AI advice

### Section 2: AI Strategy

Teaches the learner WHEN to use AI and what to keep human.

```typescript
interface AIStrategy {
  description: string            // 1-2 paragraph practical explanation
  when_to_use_ai: string[]       // 3-5 concrete scenarios
  human_responsibilities: string[] // 3-5 tasks humans must own
  suggested_prompt: string       // Copy-pasteable prompt to try
}
```

**Example:**
```json
{
  "ai_strategy": {
    "description": "Use AI to explore design variations and generate code scaffolds, but keep humans in control of architecture decisions and testing strategy.",
    "when_to_use_ai": [
      "Generate multiple design variations quickly",
      "Write boilerplate and scaffold code",
      "Explain error messages and debugging steps",
      "Refactor existing code for readability"
    ],
    "human_responsibilities": [
      "Decide which design patterns fit your constraints",
      "Validate that generated code meets performance requirements",
      "Review and test all AI-generated code before shipping",
      "Make final architectural decisions"
    ],
    "suggested_prompt": "Act as a senior software architect. I'm designing a caching layer for a microservices system. What are 3 different caching strategies and the trade-offs between them?"
  }
}
```

**Rendering: Two-column layout**
- Left column: "Delegate to AI" (teal/green) with checkmark list
- Right column: "Keep Human" (amber/orange) with shield list
- Bottom: Suggested prompt in dark code block with "Run in LLM" + "Copy" buttons

### Section 3: Prompt Template

A copy-pasteable prompt with `{{placeholders}}` the learner fills in.

```typescript
interface PromptTemplate {
  template: string                    // Text with {{PLACEHOLDER}} markers
  placeholders: PromptPlaceholder[]   // 2-4 placeholder definitions
  expected_output_shape: string       // What the AI should return
}

interface PromptPlaceholder {
  name: string         // Placeholder name (e.g., "ROLE")
  description: string  // What to fill in (50-100 words)
  example: string      // Concrete example
}
```

**Example:**
```json
{
  "prompt_template": {
    "template": "Act as a senior {{ROLE}}. {{CONTEXT}} Please {{TASK}}, ensuring that {{CONSTRAINT}}. Format your response as {{FORMAT}}.",
    "placeholders": [
      {
        "name": "ROLE",
        "description": "The professional role with domain expertise",
        "example": "data engineer managing a petabyte-scale warehouse"
      },
      {
        "name": "CONTEXT",
        "description": "Business or technical context framing the problem",
        "example": "We're migrating from Spark to DuckDB for interactive analytics"
      },
      {
        "name": "TASK",
        "description": "Specific deliverable you want",
        "example": "create a side-by-side comparison of performance characteristics"
      },
      {
        "name": "CONSTRAINT",
        "description": "Quality bar or constraint",
        "example": "your answer uses only open-source tools"
      },
      {
        "name": "FORMAT",
        "description": "Output structure",
        "example": "a numbered list with code snippets"
      }
    ],
    "expected_output_shape": "A structured comparison with 3-5 categories, each with pros/cons and code examples."
  }
}
```

**Rendering:**
- Dark code block with `{{placeholder}}` highlighted in sky-blue
- "Run in LLM" + "Copy" buttons below prompt
- Collapsible "Show placeholder guide" with expandable definitions

### Section 4: Implementation Task

The hands-on deliverable for the lesson. Learners submit their prompt attempt + strategy reflection.

```typescript
interface ImplementationTask {
  title: string                              // Task name
  description: string                        // What to build (2-3 sentences)
  requirements: string[]                     // 4-6 specific requirements
  deliverable: string                        // What "done" looks like
  requires_prompt_history: boolean           // Submit prompt iterations?
  requires_architecture_explanation: boolean  // Explain design decisions?
  estimated_minutes: number                  // Time estimate
}
```

**Submission flow:**
1. **Step 1:** Learner writes their prompt attempt in a dark-themed textarea
2. **Test button:** "Run in LLM" opens prompt in preferred LLM for testing
3. **Step 2:** Learner explains their prompting strategy in a reflection textarea
4. **Submit:** Backend AI analyzes prompt + strategy and returns:
   - Strengths (2-3 bullet points)
   - Areas to improve (2-3 bullet points)
   - Prompt strategy tips (2-3 actionable tips)
   - Detailed feedback paragraph

### Section 5: Reflection Questions

Open-ended questions with "Go deeper" prompts for the AI Mentor.

```typescript
interface ReflectionQuestion {
  question: string                      // Surface question (1 sentence)
  prompt_for_deeper_thinking: string    // Detailed follow-up (30+ words MINIMUM)
}
```

**Quality rules for `prompt_for_deeper_thinking`:**
- MUST be at least 30 words
- MUST reference the specific skill and lesson topic
- MUST include a concrete scenario or constraint
- MUST be usable as an AI prompt (starts with role instruction)

**Example:**
```json
{
  "reflection_questions": [
    {
      "question": "How did your prompt evolve as you tested it?",
      "prompt_for_deeper_thinking": "Act as a prompt engineering coach. Based on the concept of structured prompting, analyze why iterative refinement improves AI outputs. Walk through a 3-iteration example showing how adding constraints, role instructions, and format specifications each improve the response quality, with before/after comparisons."
    }
  ]
}
```

**Rendering:**
- Accordion-style numbered items
- Click to expand → shows `prompt_for_deeper_thinking` in italic
- "Ask AI Mentor" button sends the deeper prompt to the Mentor Chat

### Section 6: Explanation

Brief reference summary. Secondary to `concept_snapshot`.

```json
{
  "explanation": "Prompt chaining works by decomposing complex problems into sequential subtasks. The output of one prompt becomes the context for the next. This is particularly effective for tasks that naturally have intermediate steps. The main benefit is token efficiency; the downside is latency from multiple LLM calls."
}
```

### Section 7: Code Examples

Runnable code samples with explanations.

```typescript
interface CodeExample {
  title: string       // Example name
  language: string    // "python", "javascript", etc.
  code: string        // Complete, runnable code
  explanation: string // What it demonstrates
}
```

### Section 8: Knowledge Checks (Quiz)

Multiple-choice questions with explanations and AI follow-up prompts.

```typescript
interface KnowledgeCheck {
  question: string           // Quiz question
  options: string[]          // 3-4 choices
  correct_answer: string     // Must match one option exactly
  explanation: string        // Why correct (100-200 words)
  ai_followup_prompt: string // Detailed prompt for deeper learning (30+ words)
}
```

**`ai_followup_prompt` rules:**
- MUST be at least 30 words
- MUST start with a role instruction ("Act as...", "Imagine you are...")
- MUST include the specific concept, a clear task, and at least one constraint
- Displayed as "Dig deeper" option after answering incorrectly

**Rendering:**
- Progress bar (current/total questions)
- One question at a time
- Radio buttons for options
- Green highlight for correct, amber for wrong
- "Dig deeper" section with AI Mentor button if wrong
- Final score display (pass >= 70%)

### Section 9: Exercises

Practice exercises with starter code.

```typescript
interface Exercise {
  id: string
  title: string
  instructions: string
  starter_code: string
  expected_output: string
  hints: string[]
  estimated_minutes: number
}
```

### Section 10: Hands-On Tasks

Project-based tasks (legacy format, similar to Implementation Task).

```typescript
interface HandsOnTask {
  title: string
  description: string
  requirements: string[]
  deliverable: string
  estimated_minutes: number
}
```

---

## 9. Content Generation System

### On-Demand Generation Flow

```
Learner opens lesson
  → Check if lesson.content is null
  → If null: call Lesson Generator Agent
    → Agent receives task context (module, learner, lesson position)
    → LLM generates structured JSON matching LessonContent schema
    → JSON validated and stored in database
    → Returned to frontend
  → If not null: return cached content from database
```

### Lesson Generator Agent

**Input task:**
```json
{
  "module": {
    "skill_id": "SK.PRM.001",
    "skill_name": "Instructions + constraints + format",
    "title": "Structured Prompting",
    "current_level": 0,
    "target_level": 1
  },
  "lesson_number": 2,
  "lesson_title": "Building Your First Structured Prompt",
  "lesson_type": "practice",
  "lesson_focus_area": "Hands-on prompt creation with constraints",
  "learner_context": {
    "industry": "Consumer Goods / Retail Marketing",
    "profile_summary": "Marketing Manager with 10 years experience...",
    "previous_quiz_scores": [75, 80]
  },
  "module_context": {
    "total_lessons": 4,
    "lesson_outline": ["..."],
    "preceding_lesson_titles": ["What is Structured Prompting?"]
  }
}
```

**System prompt directives (key rules):**
1. Concept snapshot is the primary content (4 sentences max, no filler)
2. AI strategy must be practical and skill-specific (NOT generic AI advice)
3. Implementation task requires BOTH code AND prompt strategy documentation
4. Code examples must be complete and runnable
5. Every `ai_followup_prompt` and `prompt_for_deeper_thinking` MUST be 30+ words with role instruction
6. Content complexity adapts to lesson position in module sequence
7. Content is personalized to the learner's industry
8. All suggested prompts follow the same quality rules as the AI Mentor (see Section 10)

### Module Outline Agent

Generates the 3-5 lesson outlines for a module BEFORE any lesson content is generated.

**Rules:**
- Every module MUST end with an assessment lesson
- Start with concept → practice → assessment
- 3-5 lessons (prefer 4)
- Each lesson has a unique focus_area

---

## 10. AI Mentor System

The AI Mentor is a conversational learning coach that appears in a chat panel alongside lesson content.

### Behavior Rules

1. **Socratic method**: Guide with questions, never give direct answers
2. **Break problems down**: If confused, offer a simpler analogy first
3. **Suggest prompts**: Always suggest 1-2 follow-up prompts inline
4. **Keep it concise**: 2-4 paragraphs max per response
5. **Adapt language**: Match the learner's skill level
6. **Be encouraging but honest**: If something is wrong, say so kindly

### Prompt Quality Rules (Critical)

Every suggested prompt (inline and follow-up) MUST:
- Be at least 25 words long
- Start with a role instruction ("Act as a...", "Imagine you are a...")
- Include the specific topic, a clear task, and at least one constraint
- NEVER be short/vague like "Tell me about X" or "Explain Y"

### Response Format

```
[Address the learner's question directly — 2-4 paragraphs]

Try this prompt: "Act as a senior data engineer. Explain how choosing
between open-source and proprietary AI models affects data pipeline
architecture, including 3 specific trade-offs with real-world examples."

Explore further: "Act as a CTO at a mid-size startup. Compare the total
cost of ownership between hosting an open-source LLM versus using a
proprietary API, including compute, maintenance, and scaling considerations."

Explore further: "Imagine you are a machine learning engineer. Describe
how to fine-tune an open-source model for a domain-specific task, covering
dataset preparation, training infrastructure, and evaluation metrics."
```

### Suggested Prompt Extraction (4-Tier Approach)

The system extracts suggested prompts from the LLM's response using a tiered approach that guarantees prompts are always present:

| Tier | Pattern | Example |
|------|---------|---------|
| **1** | Lines prefixed with `"Explore further:"` | Explore further: "Act as..." |
| **2** | Lines prefixed with `"Try this prompt:"` or `"Ask:"` | Try this prompt: "Imagine..." |
| **3** | Any quoted string (30+ chars) with a role instruction | "Act as a senior engineer..." |
| **4** | Context-based fallback (always produces prompts) | Generated from skill + lesson title |

**Tier 4 fallback templates:**
```
"Act as a senior {skill_name} practitioner. Based on the concept of
'{lesson_title}', explain the 3 most common mistakes beginners make
and how to avoid them, with concrete examples from real-world projects."

"Act as a learning coach specializing in {skill_name}. Create a 5-minute
exercise that tests whether I truly understand '{lesson_title}' or just
memorized the surface-level explanation, including a rubric for self-assessment."
```

### Conversation Storage

Messages are stored as JSON in the database:

```json
[
  {"role": "user", "content": "What is prompt chaining?", "timestamp": "..."},
  {
    "role": "mentor",
    "content": "Great question! Let me break this down...",
    "timestamp": "...",
    "suggested_prompts": [
      "Act as a senior ML engineer. Explain how prompt chaining differs from...",
      "Imagine you are building a customer support bot. Walk through..."
    ]
  }
]
```

**Key: `suggested_prompts` are stored alongside the message** so they persist when the chat is reopened.

### Suggested Prompt Chips

At the bottom of the chat, 2 clickable chips display the latest suggested prompts. Clicking a chip opens the prompt in the learner's preferred LLM (see Section 14).

---

## 11. Skill Genome (Mastery Tracking)

The Skill Genome is a global per-user mastery overlay on the ontology. It aggregates evidence from ALL learning paths.

### Entry Schema

```json
{
  "user_id": "uuid",
  "ontology_node_id": "SK.PRM.001",
  "skill_name": "Instructions + constraints + format",
  "domain": "D.PRM",
  "mastery_level": 2.8,
  "evidence_count": 7,
  "last_evidence": "quiz",
  "confidence": 0.7,
  "updated_at": "2026-03-05T12:00:00Z"
}
```

**Unique constraint:** One entry per `(user_id, ontology_node_id)` pair.

### Mastery Update Formula (Exponential Moving Average)

```
new_mastery = (0.7 × current_mastery) + (0.3 × new_signal)
```

### Signal Strength by Evidence Type

| Evidence Type | Signal Calculation |
|--------------|--------------------|
| **Lesson (concept)** | 1.0 |
| **Lesson (practice)** | 2.0 |
| **Lesson (assessment)** | 3.0 |
| **Quiz score** | `(quiz_score / 100) × 4` (so 75% → 3.0) |
| **Project** | `feedback_quality × 4` (quality = strengths / (strengths + improvements)) |

### Confidence

```
confidence = min(1.0, evidence_count / 10)
```

Caps at 1.0 after 10 pieces of evidence.

### Per-Path Skill Mastery

In addition to the global Skill Genome, each path tracks per-skill mastery:

```
current_level = initial_level + (lessons_completed / total_lessons) × (target_level - initial_level)
progress_percentage = ((current_level - initial_level) / (target_level - initial_level)) × 100
```

---

## 12. Confusion Recovery System

When a learner signals confusion, the system generates an alternative explanation.

### Trigger Flow

```
Learner clicks "Confused" reaction on lesson
  → System detects confusion
  → Learner selects which section confused them
  → Backend generates recovery content via LLM
  → Recovery content displayed in slide-out drawer
  → ConfusionEvent stored in database for analytics
```

### Recovery Content Schema

```json
{
  "analogy": "Think of a context window like a desk. A small desk (4K tokens) can only hold a few documents at once, so you have to swap them in and out. A large desk (128K tokens) can hold many documents, but it takes longer to find what you need.",
  "step_by_step": [
    "Step 1: Understand that tokens are the units LLMs read",
    "Step 2: The context window is how many tokens the model can see at once",
    "Step 3: Longer context windows cost more but allow more complex tasks"
  ],
  "real_world_example": "When you write a marketing brief in ChatGPT and it 'forgets' your earlier instructions, that's the context window filling up. The model can't see the beginning of your conversation anymore.",
  "common_misconceptions": [
    "Misconception: Bigger context windows are always better. Reality: They cost more and can dilute focus.",
    "Misconception: Tokens are the same as words. Reality: Most words are 1-3 tokens."
  ],
  "suggested_mentor_prompt": "Act as a patient technical tutor. I'm confused about context windows in LLMs. Explain the concept using a real-world analogy from my industry (marketing), walk me through what happens when a context window fills up, and give me 3 practical tips for managing context window limitations in my daily AI work."
}
```

### Available Sections for Recovery

| Section | What It Covers |
|---------|---------------|
| `concept_snapshot` | The core concept explanation |
| `ai_strategy` | When to use AI vs. keep human |
| `explanation` | The detailed reference text |
| `general` | Overall lesson topic |

---

## 13. Assessment & Knowledge Checks

### Quiz Structure

Each lesson can have 3-5 knowledge check questions. They are displayed one at a time with a progress bar.

### Question Schema

```json
{
  "question": "What is the main benefit of few-shot prompting?",
  "options": [
    "It makes prompts shorter",
    "It helps the model understand the desired format and style",
    "It always improves speed",
    "It eliminates hallucinations completely"
  ],
  "correct_answer": "It helps the model understand the desired format and style",
  "explanation": "Few-shot examples teach the model by demonstration. The primary benefit is clarifying the expected output format and style.",
  "ai_followup_prompt": "Act as an AI expert. Explain why providing 2-3 high-quality examples to an LLM is more effective than writing detailed instructions alone. Include how few-shot learning compares to zero-shot, and provide a concrete scenario where 2-shot succeeds but zero-shot fails."
}
```

### Scoring

- `quiz_score`: 0-100 (percentage correct)
- Pass threshold: 70%
- Score feeds into Skill Genome evidence
- Low scores trigger suggested AI Mentor follow-up questions

### Post-Quiz Flow

After completing a quiz:
1. Score displayed with pass/fail indicator
2. Wrong answers show explanations + "Dig deeper" with AI Mentor
3. Score updates per-path Skill Mastery
4. Score updates global Skill Genome

---

## 14. LLM Integration (Run Prompts)

The platform supports running prompts directly in the learner's preferred LLM platform.

### Supported Platforms

| Key | Name | URL | Strategy |
|-----|------|-----|----------|
| `chatgpt` | ChatGPT | `https://chatgpt.com/` | `?q=` URL parameter |
| `claude` | Claude | `https://claude.ai/new` | `?q=` URL parameter |
| `gemini` | Gemini | `https://gemini.google.com/app` | Clipboard + toast |
| `copilot` | Copilot | `https://copilot.microsoft.com/` | Clipboard + toast |
| `perplexity` | Perplexity | `https://www.perplexity.ai/search` | `?q=` URL parameter |
| `grok` | Grok | `https://x.com/i/grok` | Clipboard + toast |
| `deepseek` | DeepSeek | `https://chat.deepseek.com/` | Clipboard + toast |
| `mistral` | Mistral | `https://chat.mistral.ai/chat` | Clipboard + toast |
| `meta` | Meta AI | `https://www.meta.ai/` | Clipboard + toast |
| `poe` | Poe | `https://poe.com/` | Clipboard + toast |
| `huggingchat` | HuggingChat | `https://huggingface.co/chat/` | Clipboard + toast |

### Two Strategies

1. **URL parameter (`?q=`)**: For platforms that support it (ChatGPT, Claude, Perplexity). The prompt is URL-encoded and appended as `?q=`. The LLM site opens with the prompt pre-filled.

2. **Clipboard + toast**: For all other platforms. The prompt is copied to clipboard, a toast notification tells the learner to paste, and the LLM site opens in a new tab.

### LLM Chooser

A dropdown selector appears in the AI Mentor chat header. Learner selects their preferred LLM, and all "Run in LLM" buttons across the platform use that choice. Preference is saved in `localStorage`.

### Where "Run in LLM" Buttons Appear

- AI Strategy panel (suggested prompt)
- Prompt Template card (template prompt)
- Implementation Task (learner's prompt attempt)
- AI Mentor chat (inline prompt cards)
- AI Mentor chat (bottom suggested prompt chips)

---

## 15. API Endpoints Reference

### Path Generation & Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/paths/generate` | Generate learning path from skill gap |
| `POST` | `/learning/{path_id}/activate` | Create modules and lessons from path |
| `GET` | `/learning/{path_id}/dashboard` | Full learning dashboard |

### Lessons

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/learning/{path_id}/lessons/{lesson_id}` | Get lesson (generates content if needed) |
| `POST` | `/learning/{path_id}/lessons/{lesson_id}/complete` | Mark lesson complete, update mastery |
| `POST` | `/learning/{path_id}/lessons/{lesson_id}/react` | Toggle reaction (helpful, confused, etc.) |
| `POST` | `/learning/{path_id}/lessons/{lesson_id}/confusion-recovery` | Generate recovery content |

### Prompt Lab & Implementation Task

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/learning/{path_id}/prompt-lab/execute` | Execute a prompt in the Prompt Lab |
| `GET` | `/learning/{path_id}/prompt-lab/history` | Get prompt iteration history |
| `POST` | `/learning/{path_id}/implementation-task/submit` | Submit task for AI feedback |

### AI Mentor

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/learning/{path_id}/mentor/chat` | Send message, get response + suggested prompts |
| `GET` | `/learning/{path_id}/mentor/history` | Load conversation history + last suggested prompts |

### Skill Genome

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/genome/{user_id}` | Full skill genome for user |

### Analysis Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analysis` | Run full pipeline: profile → JD → gaps → path |

---

## 16. Frontend Component Architecture

### Lesson Page Layout

```
┌─────────────────────────────────────────────────────────┐
│                    LESSON HEADER                         │
│  Module title > Lesson title  |  Status  |  Progress    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  ⚡ CONCEPT SNAPSHOT                 │                │
│  │  4-sentence core concept             │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  🤖 AI STRATEGY                      │                │
│  │  ┌──────────┐  ┌──────────────┐     │                │
│  │  │Delegate  │  │ Keep Human   │     │                │
│  │  │to AI     │  │              │     │                │
│  │  └──────────┘  └──────────────┘     │                │
│  │  [Suggested Prompt — Run in LLM]    │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  📝 PROMPT TEMPLATE                  │                │
│  │  Dark code block with {{placeholders}}│               │
│  │  [Run in LLM] [Copy]                │                │
│  │  ▼ Show placeholder guide            │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  💻 CODE EXAMPLES                    │                │
│  │  Syntax-highlighted code             │                │
│  │  [Copy]                              │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  🔨 IMPLEMENTATION TASK              │  ┌──────────┐ │
│  │  Step 1: Write your prompt           │  │ AI MENTOR│ │
│  │  [textarea] [Run in LLM]            │  │  Chat    │ │
│  │  Step 2: Reflect on strategy         │  │  Panel   │ │
│  │  [textarea]                          │  │          │ │
│  │  [Submit for Strategy Tips]          │  │  ------  │ │
│  │                                      │  │  chips   │ │
│  │  AI Feedback:                        │  └──────────┘ │
│  │  ✅ Strengths  ⚠️ Improvements       │                │
│  │  💡 Prompt Strategy Tips             │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  ✨ REFLECTION                       │                │
│  │  1. Question (expandable)            │                │
│  │     → Go deeper prompt               │                │
│  │     [Ask AI Mentor]                  │                │
│  │  2. Question (expandable)            │                │
│  │  3. Question (expandable)            │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  📋 KNOWLEDGE CHECK                  │                │
│  │  Progress: 1/5                       │                │
│  │  Question text                       │                │
│  │  ○ Option A                          │                │
│  │  ○ Option B                          │                │
│  │  ○ Option C                          │                │
│  │  ○ Option D                          │                │
│  │  [Check Answer]                      │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  REACTIONS: 👍 🤩 🤯 😕              │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  [← Previous Lesson]        [Complete & Next →]          │
└─────────────────────────────────────────────────────────┘
```

### Component List

| Component | Section | Key Behavior |
|-----------|---------|-------------|
| `ConceptSnapshot` | concept_snapshot | Indigo gradient, Zap icon |
| `AIStrategyPanel` | ai_strategy | Two-column grid, Run in LLM button |
| `PromptTemplateCard` | prompt_template | Dark code block, placeholder highlighting, Run in LLM |
| `CodeBlock` | code_examples | Syntax highlighting, copy button |
| `ImplementationTaskCard` | implementation_task | Two-step form (prompt + reflection), AI feedback |
| `ReflectionPrompts` | reflection_questions | Accordion, Ask AI Mentor button |
| `KnowledgeCheck` | knowledge_checks | Quiz with progress bar, explanations |
| `LessonReactions` | (reactions) | Emoji toggle buttons |
| `ConfusionRecoveryDrawer` | (recovery) | Slide-out with alternative explanation |
| `MentorChat` | (conversation) | Fixed bottom-right chat panel |
| `LLMChooser` | (settings) | Dropdown to select preferred LLM |
| `PromptLab` | (interactive) | Test prompts in real-time with iteration tracking |

### Cross-Component Communication

Components communicate via `CustomEvent`:
- `llm-changed`: When learner changes preferred LLM → all buttons update
- `open-mentor`: When any component wants to open the AI Mentor with a pre-filled message

---

## 17. Database Models Reference

### Core Tables

| Table | Primary Key | Key Fields | Relationships |
|-------|------------|-----------|---------------|
| `users` | `id` (UUID) | `email`, `name` | Has many: profiles, goals, paths |
| `profiles` | `id` (UUID) | `user_id`, `current_role`, `target_role`, `profile_data` (JSON) | Belongs to: user |
| `goals` | `id` (UUID) | `user_id`, `profile_id`, `target_jd_text`, `state_b_skills` (JSON) | Belongs to: user, profile |
| `assessments` | `id` (UUID) | `user_id`, `goal_id`, `quiz_questions` (JSON), `state_a_skills` (JSON) | Belongs to: user, goal |
| `skill_gaps` | `id` (UUID) | `user_id`, `goal_id`, `state_a_skills` (JSON), `state_b_skills` (JSON), `gaps` (JSON) | Belongs to: user, goal |

### Learning Tables

| Table | Primary Key | Key Fields | Relationships |
|-------|------------|-----------|---------------|
| `learning_paths` | `id` (UUID) | `user_id`, `goal_id`, `gap_id`, `title`, `chapters` (JSON), `total_chapters` | Has many: modules, lessons |
| `modules` | `id` (UUID) | `path_id`, `chapter_number`, `skill_id`, `skill_name`, `current_level`, `target_level`, `lesson_outline` (JSON) | Belongs to: path; Has many: lessons |
| `lessons` | `id` (UUID) | `module_id`, `path_id`, `lesson_number`, `title`, `lesson_type`, `content` (JSON, nullable), `status`, `quiz_score` | Belongs to: module, path |

### Mastery & Progress Tables

| Table | Primary Key | Key Fields | Unique Constraint |
|-------|------------|-----------|-------------------|
| `skill_masteries` | `id` (UUID) | `user_id`, `path_id`, `skill_id`, `initial_level`, `current_level` (float), `target_level`, `lessons_completed`, `avg_quiz_score` | — |
| `skill_genome_entries` | `id` (UUID) | `user_id`, `ontology_node_id`, `mastery_level` (float), `evidence_count`, `confidence`, `last_evidence` | `(user_id, ontology_node_id)` |
| `progress` | `id` (UUID) | `user_id`, `path_id`, `current_chapter`, `chapter_status` (JSON), `quiz_scores` (JSON) | — |

### Interaction Tables

| Table | Primary Key | Key Fields | Unique Constraint |
|-------|------------|-----------|-------------------|
| `mentor_conversations` | `id` (UUID) | `user_id`, `path_id`, `lesson_id`, `messages` (JSON array) | — |
| `lesson_reactions` | `id` (UUID) | `user_id`, `lesson_id`, `reaction` | `(user_id, lesson_id, reaction)` |
| `confusion_events` | `id` (UUID) | `user_id`, `lesson_id`, `section`, `recovery_content` (JSON), `resolved` | — |

---

## 18. Agent Orchestration Pipeline

### Full Analysis Pipeline

```
POST /api/analysis
│
├─ Step 1 (parallel):
│   ├─ ProfileAnalyzerAgent → State A (current skills)
│   └─ JDParserAgent → State B (required skills)
│
├─ Step 2:
│   └─ GapAnalyzerAgent → Prioritized gaps
│
├─ Step 3:
│   └─ LearningPathGenerator (deterministic) → Chapter scaffold
│
├─ Step 4:
│   └─ PathGeneratorAgent (LLM, batch-parallel) → Enriched chapters
│
└─ Optional Step 5:
    └─ ContentCuratorAgent → External resources per skill
```

### Agent Inventory

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **ProfileAnalyzerAgent** | Extract current skills from profile | Profile JSON | `state_a_skills`, top 10 current skills |
| **JDParserAgent** | Extract required skills from job description | JD text | `state_b_skills`, top 10 target skills |
| **GapAnalyzerAgent** | Prioritize skill gaps | State A + State B | Ranked gap list with scores |
| **PathGeneratorAgent** | Enrich path scaffold with content | Chapter scaffold + learner context | Enriched chapters with objectives, projects |
| **ModuleOutlineAgent** | Generate lesson outlines per module | Module context | 3-5 lesson outlines per module |
| **LessonGeneratorAgent** | Generate full lesson content | Module + lesson context | Complete LessonContent JSON |
| **MentorAgent** | Socratic learning coach | Message + history + lesson context | Response + 2 suggested prompts |
| **AssessmentAgent** | Generate adaptive quiz questions | Skill context | Quiz questions with explanations |
| **ContentCuratorAgent** | Find external resources | Skills + topics | Curated resource links |

### Base Agent Interface

Every agent implements:
```
class BaseAgent:
  name: str
  description: str
  system_prompt: str

  async execute(task: dict) -> dict
  _start_execution() → timestamp
  _end_execution() → duration_ms
  _log_execution(action, task, result)
  _call_llm(prompt, context?, temperature?) → str
```

---

## 19. Quality Standards & Validation

### Lesson Content Quality

| Section | Requirement |
|---------|------------|
| `concept_snapshot` | Max 4 sentences; no filler; crisp and precise |
| `ai_strategy` | Practical & specific; 3-5 items each for `when_to_use_ai` + `human_responsibilities` |
| `prompt_template` | Copy-pasteable; 2-4 `{{placeholders}}`; examples for each |
| `reflection_questions` | 3-4 questions; `prompt_for_deeper_thinking` MUST be 30+ words |
| `knowledge_checks` | 3-5 questions; `ai_followup_prompt` MUST be 30+ words |
| `code_examples` | 2-3 runnable examples; complete code |
| `implementation_task` | Requires code + prompt strategy + architecture explanation |
| `explanation` | 2-3 paragraphs; 200-400 words |

### Path Quality Evaluation

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| Objective clarity | 2.0 | Count, Bloom's verbs, word length, uniqueness |
| Bloom's progression | 1.5 | Verb tier progression across chapters |
| Project specificity | 2.0 | Concrete deliverable, time estimate, relevance |
| Cross-chapter consistency | 1.5 | No overlap, logical sequence |
| Domain balance | 1.0 | Coverage across mandatory domains |

### Prompt Quality Rules (Universal)

Every suggested prompt in the platform — from AI Strategy, Reflection, Knowledge Check, Mentor, or Implementation Task — MUST follow:

1. At least 25 words long
2. Starts with a role instruction ("Act as a...", "Imagine you are a...")
3. Includes specific topic + clear task + at least one constraint or deliverable
4. Never short/vague ("Tell me about X" is NEVER acceptable)
5. Follow-up prompts must explore new ground (not repeat inline prompts)

---

## 20. Implementation Checklist

### Phase 1: Foundation
- [ ] Define skill ontology (layers, domains, skills, prerequisites)
- [ ] Implement proficiency scale (0-5)
- [ ] Build database models (users, profiles, goals, skill_gaps)
- [ ] Create profile intake form
- [ ] Build JD upload/parsing interface

### Phase 2: Gap Analysis
- [ ] Implement Profile Analyzer Agent
- [ ] Implement JD Parser Agent
- [ ] Build Gap Analysis Engine with scoring formula
- [ ] Implement proficiency floors
- [ ] Build gap visualization (before/after skill chart)

### Phase 3: Path Generation
- [ ] Implement deterministic path scaffold (5-step algorithm)
- [ ] Implement mandatory domain coverage enforcement
- [ ] Build Path Generator Agent (LLM enrichment)
- [ ] Implement Module Outline Agent
- [ ] Build learning path dashboard

### Phase 4: Lesson System
- [ ] Implement Lesson Generator Agent with full content schema
- [ ] Build on-demand generation + caching
- [ ] Build all 10 lesson section components
- [ ] Implement quiz system with scoring
- [ ] Build Implementation Task submission + AI feedback

### Phase 5: AI Mentor
- [ ] Implement Mentor Agent with Socratic prompt
- [ ] Build chat panel UI
- [ ] Implement 4-tier prompt extraction
- [ ] Store suggested_prompts in conversation history
- [ ] Build LLM chooser with 11 platforms

### Phase 6: Mastery Tracking
- [ ] Implement per-path Skill Mastery
- [ ] Implement global Skill Genome with EMA updates
- [ ] Build mastery visualization
- [ ] Connect quiz scores, lesson completions, and project feedback to mastery

### Phase 7: Recovery & Reactions
- [ ] Implement lesson reactions (helpful, interesting, mind_blown, confused)
- [ ] Build Confusion Recovery system
- [ ] Implement recovery content generation
- [ ] Store confusion events for analytics

### Phase 8: Quality & Polish
- [ ] Implement Path Quality Evaluator
- [ ] Add prompt quality validation (25+ words, role instruction)
- [ ] Build progress tracking dashboard
- [ ] Add cross-component communication (llm-changed, open-mentor events)
- [ ] Performance optimization (parallel batch enrichment, caching)

---

## Appendix A: Example Ontology Skills

```json
[
  {"id": "SK.FND.000", "name": "What is AI vs traditional software", "domain": "D.FND", "level": 1, "prerequisites": []},
  {"id": "SK.FND.001", "name": "LLM fundamentals (tokens, context, prediction)", "domain": "D.FND", "level": 1, "prerequisites": ["SK.FND.000"]},
  {"id": "SK.FND.002", "name": "Capabilities vs limitations (hallucinations)", "domain": "D.FND", "level": 1, "prerequisites": ["SK.FND.001"]},
  {"id": "SK.PRM.000", "name": "Writing clear requests to AI", "domain": "D.PRM", "level": 1, "prerequisites": ["SK.FND.001"]},
  {"id": "SK.PRM.001", "name": "Instructions + constraints + format", "domain": "D.PRM", "level": 2, "prerequisites": ["SK.PRM.000"]},
  {"id": "SK.PRM.003", "name": "Prompt debugging & iteration", "domain": "D.PRM", "level": 3, "prerequisites": ["SK.PRM.001"]},
  {"id": "SK.PRM.010", "name": "JSON/schema outputs", "domain": "D.PRM", "level": 3, "prerequisites": ["SK.PRM.001"]},
  {"id": "SK.EVL.001", "name": "Output quality metrics", "domain": "D.EVL", "level": 2, "prerequisites": ["SK.FND.002"]},
  {"id": "SK.SEC.001", "name": "Prompt injection awareness", "domain": "D.SEC", "level": 2, "prerequisites": ["SK.PRM.001"]},
  {"id": "SK.RAG.001", "name": "Embedding fundamentals", "domain": "D.RAG", "level": 2, "prerequisites": ["SK.FND.001"]},
  {"id": "SK.AGT.001", "name": "Tool-use and function calling", "domain": "D.AGT", "level": 3, "prerequisites": ["SK.PRM.003"]}
]
```

## Appendix B: Example Learner Profiles

### Profile 1: Career Switcher (Marketing → AI Product)
```json
{
  "name": "Alex Rivera",
  "current_role": "Marketing Manager",
  "target_role": "AI Product Manager",
  "industry": "Consumer Goods / Retail Marketing",
  "experience_years": 10,
  "ai_exposure_level": "Basic",
  "tools_used": ["ChatGPT", "Claude", "Canva AI"],
  "learning_intent": "Pivot into AI product work",
  "target_jd": {
    "title": "AI Product Manager (GenAI features)",
    "requirements": [
      "Own AI product roadmap",
      "Define evaluation criteria for LLM outputs",
      "Design human-in-the-loop workflows"
    ]
  }
}
```

### Profile 2: Upskiller (Teacher → AI Learning Designer)
```json
{
  "name": "Bethany Chen",
  "current_role": "High School Teacher",
  "target_role": "AI Learning Designer",
  "industry": "Education",
  "experience_years": 8,
  "ai_exposure_level": "Basic",
  "tools_used": ["ChatGPT", "Grammarly"],
  "learning_intent": "Design AI-enhanced curricula",
  "target_jd": {
    "title": "AI Learning Designer",
    "requirements": [
      "Design adaptive learning experiences",
      "Integrate AI tutoring systems",
      "Evaluate AI-generated content quality"
    ]
  }
}
```

### Profile 3: Technical Upskiller (Legal → AI Governance)
```json
{
  "name": "Charles Patel",
  "current_role": "Legal Associate",
  "target_role": "AI Governance Specialist",
  "industry": "Legal / Compliance",
  "experience_years": 5,
  "ai_exposure_level": "Basic",
  "tools_used": ["ChatGPT"],
  "learning_intent": "Specialize in AI policy and compliance",
  "target_jd": {
    "title": "AI Governance / Compliance Data Scientist",
    "requirements": [
      "Develop AI governance frameworks",
      "Audit AI systems for bias and compliance",
      "Create documentation for regulatory requirements"
    ]
  }
}
```

---

*This blueprint provides a complete, project-agnostic specification for building an AI-native learning platform. All schemas, algorithms, quality rules, and architectural patterns are defined independently of any specific technology stack or codebase.*
