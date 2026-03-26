# AI Learning Platform — Complete Implementation Blueprint

> **Purpose**: This document contains every detail needed to rebuild the AI Learning Platform in a different project. It is project-agnostic — no references to specific codebases, repos, or deployment environments. Upload this file to an AI coding assistant and it will have everything needed to reconstruct the full system.

> **Version**: 2.0 — Comprehensive Edition
> **Scope**: Ontology, Proficiency Model, Learner Profiles, Multi-Agent Pipeline, Deterministic Algorithms, API Contracts, Database Schema, Frontend Components, LLM Integration

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Skill Ontology — Complete Structure](#2-skill-ontology--complete-structure)
3. [Proficiency Scale](#3-proficiency-scale)
4. [Learner Profiles — Schema & Examples](#4-learner-profiles--schema--examples)
5. [Multi-Agent Pipeline — Orchestration Flow](#5-multi-agent-pipeline--orchestration-flow)
6. [Agent 1: Profile Analyzer — System Prompt & Logic](#6-agent-1-profile-analyzer)
7. [Agent 2: JD Parser — System Prompt & Logic](#7-agent-2-jd-parser)
8. [Agent 3: Gap Analyzer — System Prompt & Logic](#8-agent-3-gap-analyzer)
9. [Deterministic Gap Engine — Complete Algorithm](#9-deterministic-gap-engine--complete-algorithm)
10. [Deterministic Path Generator — Complete Algorithm](#10-deterministic-path-generator--complete-algorithm)
11. [Agent 4: Path Generator (LLM Enrichment)](#11-agent-4-path-generator-llm-enrichment)
12. [Agent 5: Module Outline Generator](#12-agent-5-module-outline-generator)
13. [Agent 6: Lesson Generator — System Prompt & Content Schema](#13-agent-6-lesson-generator)
14. [Agent 7: AI Mentor — System Prompt & Prompt Extraction](#14-agent-7-ai-mentor)
15. [Agent 8: Assessment Agent](#15-agent-8-assessment-agent)
16. [Agent 9: Content Curator](#16-agent-9-content-curator)
17. [Confusion Recovery Service](#17-confusion-recovery-service)
18. [Skill Genome Service — EMA Mastery Tracking](#18-skill-genome-service--ema-mastery-tracking)
19. [State Inference — Prerequisite Expansion](#19-state-inference--prerequisite-expansion)
20. [Path Quality Evaluator](#20-path-quality-evaluator)
21. [Prompt Lab — Execution & Implementation Tasks](#21-prompt-lab--execution--implementation-tasks)
22. [LLM Platform Integration](#22-llm-platform-integration)
23. [Database Schema — Complete Models](#23-database-schema--complete-models)
24. [API Routes — Complete Endpoint Reference](#24-api-routes--complete-endpoint-reference)
25. [Pydantic Schemas — Complete Definitions](#25-pydantic-schemas--complete-definitions)
26. [Frontend Architecture — Components & State](#26-frontend-architecture--components--state)
27. [Frontend Component Details](#27-frontend-component-details)
28. [Cross-Component Event System](#28-cross-component-event-system)
29. [Lesson Content Rendering Logic](#29-lesson-content-rendering-logic)
30. [User Flow — End to End](#30-user-flow--end-to-end)
31. [Implementation Checklist](#31-implementation-checklist)

---

## 1. System Architecture Overview

The platform follows a **Deterministic Scaffold + LLM Enrichment** pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                     LEARNER PROFILE INPUT                       │
│  (resume, current role, target JD, self-assessment)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │    ORCHESTRATOR AGENT    │
              │  (coordinates all agents)│
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐
   │  Profile   │   │  JD Parser  │   │ Assessment│
   │  Analyzer  │   │   Agent     │   │   Agent   │
   │ → State A  │   │  → State B  │   │ (optional)│
   └─────┬─────┘   └──────┬──────┘   └─────┬─────┘
         │                │                 │
         └────────┬───────┘                 │
                  │                         │
         ┌────────▼────────┐                │
         │  GAP ANALYZER   │◄───────────────┘
         │  (LLM-assisted) │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  GAP ENGINE     │  ← DETERMINISTIC (no LLM)
         │  (scoring)      │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  PATH GENERATOR │  ← DETERMINISTIC (no LLM)
         │  (scaffold)     │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  PATH ENRICHER  │  ← LLM (adds content)
         │  (LLM agent)    │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  LEARNING PATH  │  ← Stored in DB
         │  (5 chapters)   │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  ACTIVATION     │  ← Creates Modules + Lessons
         │  MODULE OUTLINE  │  ← LLM (3-5 lessons each)
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  LESSON START   │  ← On-demand content generation
         │  LESSON GEN     │  ← LLM (full lesson content)
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐  ┌─────▼─────┐  ┌───▼────┐
│Prompt │  │   AI      │  │ Skill  │
│ Lab   │  │  Mentor   │  │ Genome │
└───────┘  └───────────┘  └────────┘
```

### Key Principles
- **Deterministic core**: Gap scoring and path scaffolding produce identical output for identical input — no randomness, no LLM calls
- **LLM enrichment layer**: Content, descriptions, and coaching are generated by LLM agents
- **On-demand generation**: Lesson content is generated when the learner opens a lesson, then cached
- **+1 progression**: Each chapter advances exactly one proficiency level
- **5-chapter paths**: Every learning path has exactly 5 chapters (modules)
- **3-5 lessons per module**: Modules contain concept → practice → assessment lessons

---

## 2. Skill Ontology — Complete Structure

The ontology is the backbone of the entire system. Every skill assessment, gap analysis, path generation, and mastery update references this structure.

### Ontology Metadata
- **Version**: 1.0.0
- **Total Skills**: 195
- **Total Domains**: 18
- **Total Layers**: 7
- **Prerequisite Model**: Directed Acyclic Graph (DAG) — skills declare their prerequisites

### Layer Hierarchy

| # | Layer ID | Label | Color | Purpose |
|---|----------|-------|-------|---------|
| 1 | L.FOUNDATION | Foundation | #22c55e (green) | Core digital & critical thinking |
| 2 | L.THEORY | Theory | #6366f1 (indigo) | AI/ML concepts & literacy |
| 3 | L.APPLICATION | Application | #06b6d4 (cyan) | Applied AI techniques |
| 4 | L.TOOLS | Tools | #10b981 (emerald) | Dev tools & frameworks |
| 5 | L.TECH_PREREQ | Tech Prerequisites | #f59e0b (amber) | Engineering foundations |
| 6 | L.DOMAIN | Domain | #ec4899 (pink) | Industry-specific applications |
| 7 | L.SOFT | Soft/Strategy | #8b5cf6 (purple) | Product, communication, learning |

### Complete Domain & Skill Registry

Each skill entry format: `SKILL_ID: Skill Name (Ontology Level) [Prerequisites]`

#### Layer 1: L.FOUNDATION

**D.DIG — Digital Literacy** (8 skills)
```
SK.DIG.001: Web browsing & search fundamentals (L1) []
SK.DIG.002: File management & cloud storage (L1) []
SK.DIG.003: Basic spreadsheet operations (L1) []
SK.DIG.004: Email & digital communication (L1) []
SK.DIG.005: Password & account security basics (L1) []
SK.DIG.006: Installing & using applications (L1) []
SK.DIG.007: Copy/paste & keyboard shortcuts (L1) []
SK.DIG.008: Screen sharing & video calls (L1) []
```

**D.CTIC — Critical Thinking & Info Evaluation** (6 skills)
```
SK.CTIC.001: Evaluating source credibility (L1) []
SK.CTIC.002: Identifying misinformation patterns (L2) [SK.CTIC.001]
SK.CTIC.003: Cross-referencing claims (L2) [SK.CTIC.001]
SK.CTIC.004: Understanding bias in content (L2) [SK.CTIC.001]
SK.CTIC.005: Distinguishing fact from opinion (L1) []
SK.CTIC.006: Recognizing AI-generated content (L2) [SK.FND.001]
```

#### Layer 2: L.THEORY

**D.FND — AI Literacy & Foundations** (15 skills)
```
SK.FND.000: What is AI vs traditional software (L1) []
SK.FND.001: LLM fundamentals (tokens, context, prediction) (L1) [SK.FND.000]
SK.FND.002: Capabilities vs limitations (hallucinations) (L1) [SK.FND.001]
SK.FND.003: Model families (open vs closed) (L2) [SK.FND.001]
SK.FND.004: Reasoning vs retrieval vs tools (L2) [SK.FND.002]
SK.FND.005: Training data & knowledge cutoffs (L1) [SK.FND.001]
SK.FND.006: Temperature & sampling basics (L2) [SK.FND.001]
SK.FND.010: Transformer architecture overview (L2) [SK.FND.001]
SK.FND.011: Diffusion models overview (L2) [SK.FND.000]
SK.FND.012: Embeddings & semantic similarity (L2) [SK.FND.001]
SK.FND.013: Multimodal model basics (L2) [SK.FND.001]
SK.FND.020: Privacy basics for GenAI (L1) []
SK.FND.021: IP/copyright awareness (L1) []
SK.FND.022: Bias & fairness basics (L1) [SK.FND.002]
SK.FND.023: Environmental impact awareness (L1) [SK.FND.000]
```

#### Layer 3: L.APPLICATION

**D.PRM — Prompting & HITL Workflows** (13 skills)
```
SK.PRM.000: Writing clear requests to AI (L1) [SK.FND.001]
SK.PRM.001: Instructions + constraints + format (L2) [SK.PRM.000]
SK.PRM.002: Few-shot examples (L2) [SK.PRM.001]
SK.PRM.003: Prompt debugging & iteration (L3) [SK.PRM.001]
SK.PRM.004: Role & persona prompting (L2) [SK.PRM.001]
SK.PRM.005: Chain-of-thought prompting (L2) [SK.PRM.001]
SK.PRM.006: Breaking complex tasks into steps (L2) [SK.PRM.001]
SK.PRM.010: JSON/schema outputs (L3) [SK.PRM.001, SK.PRQ.020]
SK.PRM.011: Rubrics as prompts (L3) [SK.PRM.001]
SK.PRM.020: Draft -> critique -> revise (L3) [SK.PRM.001]
SK.PRM.021: Grounding & citations (L3) [SK.FND.002]
SK.PRM.022: ReAct-style patterns (L4) [SK.PRM.010, SK.FND.004]
```

**D.RAG — Retrieval & RAG Systems** (9 skills)
```
SK.RAG.000: What is RAG and why use it (L1) [SK.FND.004]
SK.RAG.001: Query rewriting (L3) [SK.PRM.001]
SK.RAG.002: Chunking strategies (L3) [SK.FND.012]
SK.RAG.003: Hybrid retrieval (vector + keyword) (L3) [SK.FND.012]
SK.RAG.010: Reranking & scoring (L3) [SK.RAG.003]
SK.RAG.011: Context budgeting (L4) [SK.FND.001, SK.RAG.003]
SK.RAG.012: Lost in the middle mitigation (L4) [SK.RAG.011]
SK.RAG.020: Faithfulness evaluation (L4) [SK.PRM.021, SK.RAG.010]
SK.RAG.021: Golden sets & regression testing (L4) [SK.RAG.020]
```

**D.AGT — Agents & Orchestration** (11 skills)
```
SK.AGT.000: What are AI agents (L1) [SK.FND.004]
SK.AGT.001: Tool definitions & validation (L3) [SK.PRM.010, SK.PRQ.020]
SK.AGT.002: Error handling & retries (L3) [SK.AGT.001, SK.PRQ.021]
SK.AGT.003: State & memory management (L3) [SK.AGT.001]
SK.AGT.010: Single-agent loops (L4) [SK.AGT.001, SK.EVL.020]
SK.AGT.011: Multi-agent patterns (L4) [SK.AGT.010]
SK.AGT.012: Graph-based orchestration (L5) [SK.AGT.011, SK.PRQ.022]
SK.AGT.020: MCP protocol concepts (L3) [SK.AGT.001]
SK.AGT.021: Agent permissions (least privilege) (L4) [SK.SEC.010, SK.AGT.001]
SK.AGT.030: Guardrails & approval gates (L4) [SK.SEC.010, SK.EVL.001]
SK.AGT.031: Agent auditability (L4) [SK.EVL.010]
```

**D.MOD — Model Adaptation** (6 skills)
```
SK.MOD.000: When to customize vs use off-the-shelf (L2) [SK.FND.003]
SK.MOD.001: Prompt vs fine-tune decision (L3) [SK.FND.003, SK.PRM.001]
SK.MOD.002: Data requirements for tuning (L3) [SK.MOD.001, SK.PRQ.030]
SK.MOD.010: Instruction tuning basics (L3) [SK.MOD.001]
SK.MOD.011: PEFT/LoRA concepts (L4) [SK.MOD.010]
SK.MOD.012: Synthetic data generation (L4) [SK.MOD.002, SK.EVL.001]
```

**D.MUL — Multimodal AI** (8 skills)
```
SK.MUL.000: Types of multimodal AI (L1) [SK.FND.000]
SK.MUL.001: Image-to-text extraction (L2) [SK.PRM.010]
SK.MUL.002: Image generation prompting (L2) [SK.PRM.001]
SK.MUL.003: Image generation QA (L3) [SK.MUL.002]
SK.MUL.010: Speech-to-text & summarization (L2) [SK.PRM.001]
SK.MUL.011: Video understanding (L3) [SK.PRM.021]
SK.MUL.012: Text-to-speech applications (L2) [SK.FND.000]
SK.MUL.013: Document/PDF understanding (L2) [SK.PRM.001]
```

**D.EVL — Evaluation & Observability** (8 skills)
```
SK.EVL.000: Why AI evaluation matters (L1) [SK.FND.002]
SK.EVL.001: Eval types (offline/online/red team) (L2) [SK.FND.002]
SK.EVL.002: LLM-as-judge patterns (L3) [SK.PRM.011, SK.EVL.001]
SK.EVL.010: Tracing & observability (L3) [SK.PRQ.022]
SK.EVL.011: Quality dashboards & alerts (L4) [SK.EVL.010, SK.EVL.001]
SK.EVL.020: Prompt unit tests (L3) [SK.PRM.003]
SK.EVL.021: Release gates & rollback (L4) [SK.EVL.011, SK.OPS.020]
SK.EVL.022: A/B testing for AI (L4) [SK.EVL.001]
```

**D.SEC — Safety & Security** (7 skills)
```
SK.SEC.000: AI security threat landscape (L1) [SK.FND.002]
SK.SEC.001: Prompt injection mitigation (L3) [SK.RAG.020, SK.AGT.001]
SK.SEC.002: Data leakage prevention (L3) [SK.FND.020]
SK.SEC.003: Output security (XSS, injection) (L3) [SK.PRQ.021]
SK.SEC.010: Agent permission design (L4) [SK.AGT.001]
SK.SEC.011: Tool sandboxing (L4) [SK.SEC.010, SK.PRQ.022]
SK.SEC.012: Red teaming basics (L3) [SK.EVL.001]
```

**D.OPS — LLMOps & Deployment** (8 skills)
```
SK.OPS.000: What is LLMOps (L1) [SK.FND.000]
SK.OPS.001: Latency drivers & optimization (L3) [SK.AGT.002, SK.RAG.011]
SK.OPS.002: Cost modeling & token budgeting (L3) [SK.OPS.001]
SK.OPS.010: Caching, batching, streaming (L4) [SK.OPS.002, SK.PRQ.022]
SK.OPS.011: Model routing strategies (L4) [SK.OPS.010]
SK.OPS.020: SLOs/SLAs & incident response (L4) [SK.EVL.010]
SK.OPS.021: Security reviews & deployment gates (L4) [SK.SEC.010, SK.EVL.021]
SK.OPS.022: Versioning prompts & models (L3) [SK.PRM.003]
```

#### Layer 4: L.TOOLS

**D.TOOL — Tools & Frameworks** (10 skills)
```
SK.TOOL.000: AI tool landscape overview (L1) [SK.FND.000]
SK.TOOL.001: ChatGPT/Claude/Gemini usage (L1) [SK.FND.001]
SK.TOOL.002: AI coding assistants (Copilot) (L2) [SK.PRQ.010]
SK.TOOL.003: Image generation tools (Midjourney, DALL-E) (L2) [SK.MUL.002]
SK.TOOL.010: LangChain/LlamaIndex concepts (L3) [SK.RAG.001, SK.AGT.001]
SK.TOOL.011: Hugging Face ecosystem (L3) [SK.FND.010]
SK.TOOL.020: API key management (L2) [SK.PRQ.021]
SK.TOOL.021: Provider selection criteria (L3) [SK.FND.003, SK.GOV.001]
SK.TOOL.030: Docker for AI apps (L3) [SK.PRQ.022]
SK.TOOL.031: Kubernetes awareness (L4) [SK.TOOL.030]
```

#### Layer 5: L.TECH_PREREQ

**D.PRQ — Technical Prerequisites** (12 skills)
```
SK.PRQ.000: Command line basics (L1) []
SK.PRQ.001: Version control (Git basics) (L2) [SK.PRQ.000]
SK.PRQ.010: Python basics (L2) [SK.PRQ.000]
SK.PRQ.011: Data handling (Pandas/NumPy) (L2) [SK.PRQ.010]
SK.PRQ.012: JavaScript/TypeScript basics (L2) []
SK.PRQ.013: SQL fundamentals (L2) []
SK.PRQ.020: REST API basics (L2) []
SK.PRQ.021: Authentication (OAuth, tokens) (L2) [SK.PRQ.020]
SK.PRQ.022: Backend service fundamentals (L3) [SK.PRQ.020]
SK.PRQ.030: Cloud primitives (compute, storage) (L2) []
SK.PRQ.031: Secrets management (L3) [SK.PRQ.030, SK.PRQ.021]
SK.PRQ.032: CI/CD concepts (L3) [SK.PRQ.001]
```

#### Layer 6: L.DOMAIN

**D.GOV — Governance & Compliance** (6 skills)
```
SK.GOV.000: AI governance fundamentals (L1) [SK.FND.002]
SK.GOV.001: AI risk framing (L2) [SK.FND.002, SK.FND.022]
SK.GOV.002: Policy to controls mapping (L3) [SK.AGT.030, SK.EVL.010]
SK.GOV.010: AI regulations landscape (EU AI Act) (L2) [SK.GOV.000]
SK.GOV.020: PII/PHI handling & retention (L2) [SK.FND.020]
SK.GOV.021: Data minimization & anonymization (L3) [SK.GOV.020]
```

**D.DOM — Domain Applications** (8 skills)
```
SK.DOM.HC.001: Healthcare: Clinical risk awareness (L3) [SK.GOV.001, SK.PRM.021]
SK.DOM.HC.002: Healthcare: Evidence synthesis (L3) [SK.RAG.020]
SK.DOM.LGL.001: Legal: Disclaimer & advice boundaries (L3) [SK.GOV.001, SK.PRD.010]
SK.DOM.LGL.002: Legal: Hallucination eval frameworks (L4) [SK.EVL.001, SK.RAG.020]
SK.DOM.FIN.001: Finance: Numerical auditability (L4) [SK.EVL.010, SK.AGT.031]
SK.DOM.EDU.001: Education: Learning design with AI (L2) [SK.PRM.001]
SK.DOM.MKT.001: Marketing: Content generation ethics (L2) [SK.FND.021, SK.FND.022]
SK.DOM.HR.001: HR: AI in hiring considerations (L2) [SK.FND.022, SK.GOV.001]
```

#### Layer 7: L.SOFT

**D.PRD — Product & UX** (8 skills)
```
SK.PRD.000: AI product thinking basics (L1) [SK.FND.004]
SK.PRD.001: Use-case selection & prioritization (L2) [SK.FND.004]
SK.PRD.002: Workflow mapping (L3) [SK.PRD.001]
SK.PRD.010: Explainability UX design (L3) [SK.PRM.021]
SK.PRD.011: Feedback loop design (L3) [SK.EVL.011]
SK.PRD.020: AI enablement & training strategy (L3) [SK.PRD.002]
SK.PRD.021: Stakeholder management (L3) [SK.FND.002, SK.GOV.001]
SK.PRD.022: ROI measurement for AI (L3) [SK.PRD.001]
```

**D.COM — Communication & Collaboration** (6 skills)
```
SK.COM.001: Explaining AI to non-technical audiences (L2) [SK.FND.001]
SK.COM.002: Writing AI project proposals (L3) [SK.PRD.001]
SK.COM.003: Facilitating AI workshops (L3) [SK.COM.001]
SK.COM.004: Managing AI expectations (L2) [SK.FND.002]
SK.COM.005: Cross-functional AI collaboration (L3) [SK.COM.001]
SK.COM.006: AI documentation best practices (L3) [SK.PRM.003]
```

**D.LRN — Learning & Adaptation** (5 skills)
```
SK.LRN.001: Keeping up with AI developments (L1) [SK.FND.000]
SK.LRN.002: Evaluating new AI tools (L2) [SK.TOOL.000]
SK.LRN.003: Building personal AI workflows (L2) [SK.PRM.001]
SK.LRN.004: Teaching others AI skills (L3) [SK.COM.001]
SK.LRN.005: Experimenting safely with AI (L2) [SK.FND.020, SK.SEC.000]
```

### Role Templates (5)

Role templates provide target skill profiles for common career paths:

```json
{
  "ROLE.BEGINNER": {
    "label": "AI Curious Beginner",
    "color": "#22c55e",
    "focus_domains": ["D.DIG", "D.CTIC", "D.FND", "D.PRM"]
  },
  "ROLE.KNOWLEDGE": {
    "label": "Knowledge Worker",
    "color": "#3b82f6",
    "focus_domains": ["D.DIG", "D.CTIC", "D.FND", "D.PRM", "D.MUL", "D.COM"]
  },
  "ROLE.AI_PM": {
    "label": "AI Product Manager",
    "color": "#8b5cf6",
    "focus_domains": ["D.PRD", "D.PRM", "D.EVL", "D.GOV", "D.COM"]
  },
  "ROLE.LLM_ENGINEER": {
    "label": "LLM Engineer",
    "color": "#06b6d4",
    "focus_domains": ["D.PRQ", "D.PRM", "D.RAG", "D.AGT", "D.EVL", "D.SEC", "D.OPS", "D.TOOL"]
  },
  "ROLE.AI_ARCHITECT": {
    "label": "AI Architect",
    "color": "#ec4899",
    "focus_domains": ["D.AGT", "D.EVL", "D.SEC", "D.GOV", "D.OPS", "D.MOD"]
  }
}
```

---

## 3. Proficiency Scale

Every skill is assessed and tracked on a 0-5 scale:

| Level | Label | Description | Behavioral Indicator |
|-------|-------|-------------|---------------------|
| 0 | Unaware | Has not heard of it | Cannot recognize the term |
| 1 | Aware | Can explain basics | Recognizes concepts, can describe at high level |
| 2 | User | Can apply with help | Uses existing tools/frameworks with guidance |
| 3 | Practitioner | Can adapt independently | Configures, customizes, troubleshoots |
| 4 | Builder | Ships solutions | Designs and implements systems end-to-end |
| 5 | Architect | Designs systems | Sets technical direction and standards |

### JD Calibration Guidance (used by JD Parser)
- "strong understanding of", "deep knowledge of" → Level 3
- "hands-on experience building", "implement", "develop" → Level 4
- "design systems", "lead architecture", "define strategy" → Level 5
- "familiarity with", "awareness of", "exposure to" → Level 2
- Senior/lead/staff roles → Level 3-5 for core skills
- Mid-level roles → Level 2-4 for core skills
- Entry-level roles → Level 1-3 for core skills

---

## 4. Learner Profiles — Schema & Examples

### Profile JSON Schema

```json
{
  "name": "string",
  "current_role": "string",
  "target_role": "string",
  "industry": "string",
  "experience_years": "integer",
  "ai_exposure_level": "None | Basic | Intermediate | Advanced",
  "archetype": "Career Switcher | Domain Upskiller | Executive | Technical Pivot",
  "learning_intent": "string (free text)",
  "tools_used": ["string"],
  "technical_background": "string",
  "current_jd_responsibilities": ["string"],
  "intake_answers": {
    "ai_tools_used": "string",
    "ai_frequency": "string",
    "technical_depth": "string",
    "biggest_challenge": "string"
  },
  "estimated_current_skills": {
    "SKILL_ID": "integer (0-5)"
  },
  "expected_skill_gaps": [
    {
      "skill_id": "string",
      "target_level": "integer",
      "domain": "string",
      "priority": "string"
    }
  ],
  "target_jd": "string (full job description text)"
}
```

### Example Profile: Career Switcher

```json
{
  "name": "Alex Rivera",
  "current_role": "Marketing Manager",
  "target_role": "AI Product Manager",
  "industry": "Consumer Goods / Retail",
  "experience_years": 10,
  "ai_exposure_level": "Basic",
  "archetype": "Career Switcher",
  "learning_intent": "I want to transition from traditional marketing into AI product management. I've used ChatGPT and Claude for content creation but I need to understand the technical side — how AI products are built, evaluated, and governed.",
  "tools_used": ["ChatGPT", "Claude", "Canva AI"],
  "technical_background": "Non-technical. Comfortable with spreadsheets and basic data analysis. No coding experience.",
  "estimated_current_skills": {
    "SK.PRM.000": 2,
    "SK.PRM.001": 1,
    "SK.FND.001": 1,
    "SK.COM.001": 2,
    "SK.PRD.000": 1,
    "SK.DOM.MKT.001": 2
  },
  "expected_skill_gaps": [
    {"skill_id": "SK.PRD.001", "target_level": 3, "domain": "D.PRD", "priority": "critical"},
    {"skill_id": "SK.PRM.003", "target_level": 3, "domain": "D.PRM", "priority": "high"},
    {"skill_id": "SK.EVL.001", "target_level": 3, "domain": "D.EVL", "priority": "high"},
    {"skill_id": "SK.GOV.001", "target_level": 2, "domain": "D.GOV", "priority": "medium"},
    {"skill_id": "SK.FND.004", "target_level": 2, "domain": "D.FND", "priority": "medium"}
  ]
}
```

---

## 5. Multi-Agent Pipeline — Orchestration Flow

The Orchestrator Agent coordinates 6+ specialized agents in sequence:

### Orchestrator System Prompt

```
You are the orchestrator for an AI learning path generation system.
Your role is to coordinate multiple specialized agents to analyze user profiles,
parse job descriptions, identify skill gaps, and generate personalized learning paths.
```

### Execution Pipeline

```
Step 1 & 2 (PARALLEL):
  ├─ ProfileAnalyzerAgent(profile, ontology_skills) → state_a_skills, top_10_current
  └─ JDParserAgent(jd_text, target_role) → state_b_skills, top_10_target

Step 3 (CONDITIONAL):
  └─ If skip_assessment == False:
       AssessmentAgent("generate", skill_ids) → questions
     Else: skip

Step 4: Gap Analysis
  └─ GapAnalyzerAgent(state_a, state_b, learning_intent, industry) → prioritized_gaps

Step 4b: Deterministic Scaffold
  ├─ Filter state_a and state_b to valid ontology IDs
  ├─ Fallback: use profile.expected_skill_gaps if state_b empty
  ├─ Overlay role template if available (corrects target levels)
  └─ LearningPathGenerator.generate_path(state_a, state_b, role_context) → chapter_scaffold

Step 5: Path Generation (LLM Enrichment)
  └─ PathGeneratorAgent(chapter_scaffold, industry, learning_intent, profile_summary) → enriched chapters

Step 6 (CONDITIONAL):
  └─ If include_resources == True:
       ContentCuratorAgent(chapters, industry) → resources
```

---

## 6. Agent 1: Profile Analyzer

### System Prompt (Verbatim)

```
You are an expert career analyst specializing in AI skills assessment.
Your task is to analyze a user's professional profile and determine their top 10 current
skills based on the GenAI Skills Ontology.

For each skill, assign a proficiency level (0-5):
- 0: Unaware - Has not heard of it
- 1: Aware - Can explain basics
- 2: User - Can apply with help
- 3: Practitioner - Can adapt independently
- 4: Builder - Ships solutions
- 5: Architect - Designs systems

Be conservative in your assessments - only assign higher levels if there's clear evidence.
Focus on AI/GenAI related skills and their prerequisites.

For EACH skill you identify, provide a rationale that references specific evidence from
the user's profile (job title, responsibilities, tools used, or background).
```

### Execute Logic
1. Create profile summary from role, industry, experience, technical skills, current JD
2. Retrieve relevant skills from RAG (n_results=50)
3. Fallback: inject full ontology if RAG empty
4. Build analysis prompt with profile data + intake answers
5. Call LLM with structured schema
6. Post-process: validate skill IDs against ontology, fuzzy-match invalid ones
7. Merge with `estimated_current_skills` from profile (profile values override LLM)

### Output Schema
```json
{
  "state_a_skills": {"SK.PRM.001": 2, "SK.FND.001": 1},
  "top_10_current_skills": [
    {
      "rank": 1,
      "skill_id": "SK.PRM.001",
      "skill_name": "Instructions + constraints + format",
      "domain": "D.PRM",
      "domain_label": "Prompting & HITL Workflows",
      "current_level": 2,
      "rationale": "Uses ChatGPT daily for content creation, demonstrates..."
    }
  ],
  "profile_summary": "string",
  "ai_exposure_assessment": "string",
  "recommended_focus_domains": ["D.PRD", "D.PRM"]
}
```

---

## 7. Agent 2: JD Parser

### System Prompt (Verbatim)

```
You are an expert job description analyst specializing in AI/ML roles.
Your task is to analyze job descriptions and extract the TOP 10 required skills mapped to
the GenAI Skills Ontology.

PROFICIENCY SCALE (use this when assigning required levels):
- Level 1 (Aware): Can explain the concept. Entry-level familiarity.
- Level 2 (User): Can apply with guidance. Uses existing tools/frameworks.
- Level 3 (Practitioner): Adapts independently. Configures, customizes, troubleshoots.
- Level 4 (Builder): Ships production solutions. Designs and implements systems end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction and standards.

CALIBRATION GUIDANCE:
- JD says "strong understanding of", "deep knowledge of" → Level 3 (Practitioner)
- JD says "hands-on experience building", "implement", "develop" → Level 4 (Builder)
- JD says "design systems", "lead architecture", "define strategy" → Level 5 (Architect)
- JD says "familiarity with", "awareness of", "exposure to" → Level 2 (User)
- Senior/lead/staff roles typically require Level 3-5 for core skills
- Mid-level roles typically require Level 2-4 for core skills
- Entry-level roles typically require Level 1-3 for core skills

For each identified skill requirement, determine:
1. The skill ID from the ontology
2. The required proficiency level (1-5) using the calibration guidance above
3. The importance/criticality (high/medium/low)
4. A rationale explaining WHY this skill is needed, referencing specific text from the JD

Focus on:
- Explicit skill requirements
- Implied skills from responsibilities
- Tools and technologies mentioned
- Soft skills and collaboration requirements

Map everything to the GenAI Skills Ontology structure.
```

### Execute Logic
1. Retrieve relevant skills from RAG (n_results=40)
2. Fallback: inject full ontology if RAG empty (prevents hallucination)
3. Call LLM with structured schema
4. Post-process: validate all skill IDs against ontology, remap invalid IDs via fuzzy match

### Output Schema
```json
{
  "state_b_skills": {"SK.PRD.001": 3, "SK.EVL.001": 3},
  "top_10_target_skills": [
    {
      "rank": 1,
      "skill_id": "SK.PRD.001",
      "skill_name": "Use-case selection & prioritization",
      "domain": "D.PRD",
      "domain_label": "Product & UX",
      "required_level": 3,
      "importance": "high",
      "rationale": "JD requires 'lead AI use case identification and prioritization...'"
    }
  ],
  "extracted_requirements": [],
  "role_analysis": {}
}
```

---

## 8. Agent 3: Gap Analyzer

### System Prompt (Verbatim)

```
You are an expert learning path strategist. Your task is to analyze
the gap between a learner's current skills (State A) and their target skills (State B),
then prioritize which gaps to address first.

Consider these factors when prioritizing:
1. Job criticality - How important is this skill for the target role?
2. Prerequisites - What skills must be learned first?
3. Learning intent - What did the user say they want to focus on?
4. Difficulty estimation - How big is the jump?
5. Quick wins - Are there skills that can be gained quickly?

Create a prioritized list that balances immediate value with logical learning progression.
```

### Execute Logic
1. Calculate raw gaps: `gap = state_b[skill] - state_a[skill]`
2. Retrieve skill details from RAG in parallel (top 20 gaps)
3. Build prioritization prompt with all inputs
4. Call LLM with structured schema

### Output Schema
```json
{
  "gaps": [
    {
      "skill_id": "SK.PRD.001",
      "skill_name": "Use-case selection & prioritization",
      "domain": "D.PRD",
      "current_level": 1,
      "target_level": 3,
      "gap": 2,
      "priority": 1,
      "priority_reason": "Core PM competency, JD emphasizes...",
      "prerequisites": ["SK.FND.004"],
      "estimated_effort": "medium"
    }
  ],
  "summary": {},
  "recommendations": []
}
```

---

## 9. Deterministic Gap Engine — Complete Algorithm

This is the **core deterministic component** — no LLM, fully reproducible.

### Scoring Formula

```
priority_score = (3 × delta) + (2 × role_relevance) - (0.5 × skill_level)
```

Where:
- **delta** (weight 3): Proficiency distance (`required_level - current_level`). Larger gaps score higher.
- **role_relevance** (weight 2): Binary flag. 1 if the skill's domain is in the target role's focus domains, else 0.
- **skill_level** (weight -0.5): Mild penalty for advanced skills. Foundational gaps are addressed before architect-tier ones when deltas are equal.

### Floor Logic (Prevents Level 0 Display)

Three floors prevent unrealistically low starting levels:

1. **Professional Floor**: If learner has ANY skill at L2+, all unknown skills start at L1 (Aware). Rationale: Working professionals have baseline awareness.

2. **Skill-Level Floor**: If learner has ANY skill at L3+ AND the target skill's ontology level is 3+, that skill starts at L2 (User). Rationale: Experienced professionals aren't just "aware" of adjacent skills.

3. **Domain Floor**: If learner knows ANY skill in a domain, other skills in that domain start at `max(1, domain_max - 1)`. Rationale: A data analyst with SQL at L3 (D.PRQ) starts other D.PRQ skills at L2.

### Complete Algorithm

```python
def compute_gap(state_a, state_b, role_context=None):
    # Validate all skill IDs against ontology
    validate_skill_ids(state_a)
    validate_skill_ids(state_b)

    target_domains = set(role_context.get("target_domains", []) if role_context else [])

    # Calculate floors
    max_skill = max(state_a.values()) if state_a else 0
    professional_floor = 1 if max_skill >= 2 else 0

    # Domain floor: per-domain max level from state_a
    domain_max = {}
    for sid, level in state_a.items():
        skill_info = ontology.get_skill(sid)
        if skill_info:
            d = skill_info["domain"]
            domain_max[d] = max(domain_max.get(d, 0), level)

    gaps = []
    for skill_id, required_level in state_b.items():
        skill = ontology.get_skill(skill_id)

        # Apply floors
        dm = domain_max.get(skill["domain"], 0)
        domain_floor = max(1, dm - 1) if dm > 0 else 0

        if max_skill >= 3 and skill["level"] >= 3:
            skill_floor = 2
        else:
            skill_floor = professional_floor

        current_level = max(state_a.get(skill_id, 0), domain_floor, skill_floor)
        delta = required_level - current_level

        if delta <= 0:
            continue

        role_relevance = 1 if skill["domain"] in target_domains else 0
        priority_score = (3 * delta) + (2 * role_relevance) - (0.5 * skill["level"])

        gaps.append({
            "skill_id": skill_id,
            "skill_name": skill["name"],
            "domain": skill["domain"],
            "current_level": current_level,
            "required_level": required_level,
            "delta": delta,
            "skill_level": skill["level"],
            "prerequisites": skill.get("prerequisites", []),
            "role_relevance": role_relevance,
            "priority_score": priority_score,
        })

    # Sort by priority_score DESC, skill_id ASC (deterministic)
    gaps.sort(key=lambda g: (g["priority_score"], g["skill_id"]), reverse=True)
    return gaps
```

---

## 10. Deterministic Path Generator — Complete Algorithm

This is the second deterministic component — produces a fixed-length, prerequisite-ordered learning path.

### Design Rules
1. **5-chapter paths**: Every path has exactly `MAX_CHAPTERS = 5` chapters
2. **+1 progression**: Each chapter advances exactly one proficiency level
3. **Domain diversity**: No more than `MAX_DOMAIN_CHAPTERS = 2` from the same domain
4. **Prerequisite ordering**: Prerequisites appear before dependent skills (topological sort)
5. **Mandatory categories**: Every path must include at least one skill from:
   - Foundation (D.FND)
   - Applied AI (D.PRM, D.RAG, D.AGT, D.MOD, D.MUL, D.OPS, D.TOOL)
   - Evaluation (D.EVL)
   - Safety (D.SEC or D.GOV)

### 6-Phase Algorithm

```
Phase 0: Expand state_a with inferred prerequisites (state_inference)
Phase 0.5: Ensure mandatory domains in state_b (inject missing categories)
Phase 1: Select top-5 primary skills from ranked gap list
Phase 2: Prerequisite resolution with back-pressure
         (if primaries + prereqs > 5, drop lowest-priority primary)
Phase 3: Domain diversity enforcement
         (if any domain > 2 chapters, swap with alternatives)
Phase 4: Mandatory category enforcement (post-processing)
         (swap lowest-value chapter for missing category skill)
Phase 5: Top-up to 5 chapters with standalone skills
```

### Phase 2 Detail: Back-Pressure

```python
def resolve_with_backpressure(candidates, state_a):
    remaining = list(candidates)
    while remaining:
        total_slots = count_slots(remaining, state_a)  # primaries + unique prereqs
        if total_slots <= MAX_CHAPTERS:
            break
        remaining.pop()  # drop lowest-priority candidate
    return remaining
```

### Phase 3 Detail: Domain Diversity

```python
def enforce_domain_diversity(planned, all_gaps, state_a):
    # Iteratively check domain counts
    # If any domain > MAX_DOMAIN_CHAPTERS:
    #   1. Remove lowest-priority primary from that domain
    #   2. Insert next-best gap from a different domain
    #   3. Re-run back-pressure
    # Then backfill: fill unused capacity with eligible skills
```

### Phase 4 Detail: Mandatory Category Swap

```python
def post_enforce_mandatory(chapters, all_gaps, state_a, priority_skills):
    # For each mandatory category without coverage:
    #   1. Find a self-contained replacement skill (no unmet prereqs)
    #   2. Find lowest-value chapter to swap out (protects priority skills)
    #   3. Swap 1-for-1 to maintain chapter count
```

### Chapter Ordering: Topological Sort (Kahn's Algorithm)

```python
def build_ordered_chapters(planned, state_a):
    # 1. Collect all skills to schedule (primaries + unmet prereqs)
    # 2. Build dependency graph (edges from skill → its prereqs)
    # 3. Kahn's algorithm with priority-based tie-breaking
    # 4. Build chapter dicts with +1 progression
```

### Chapter Output Format

```json
{
  "total_chapters": 5,
  "chapters": [
    {
      "chapter_number": 1,
      "primary_skill_id": "SK.FND.004",
      "primary_skill_name": "Reasoning vs retrieval vs tools",
      "current_level": 1,
      "target_level": 2,
      "objectives": [],
      "project_placeholder": {}
    }
  ]
}
```

---

## 11. Agent 4: Path Generator (LLM Enrichment)

Takes the deterministic scaffold and adds rich educational content.

### System Prompt (Verbatim)

```
You are an expert instructional designer specializing in AI/ML education.
Your task is to enrich deterministic learning-path scaffolds with high-quality
educational content for working professionals.

HARD RULES — violating any of these invalidates the output:
1. NEVER modify these immutable scaffold fields:
   chapter_number, skill_id, skill_name, current_level, target_level.
2. Produce EXACTLY the same number of chapters as the scaffold.
   Do NOT add, remove, reorder, or merge chapters.
3. Each chapter MUST contain 3-5 measurable learning objectives.
   Each objective must start with a Bloom's-taxonomy verb
   (e.g. Identify, Explain, Implement, Evaluate, Design)
   and describe an observable, assessable outcome.
4. Each chapter MUST contain exactly 1 applied_project — a
   realistic, industry-relevant deliverable the learner builds.
   Include: project_title, project_description, deliverable,
   and estimated_time_minutes.
5. Chapter complexity MUST increase across the path: earlier
   chapters use lower-order verbs (Identify, Describe, Explain);
   later chapters use higher-order verbs (Analyze, Design, Evaluate).

ENRICHMENT FIELDS you must populate for every chapter:
- title (short, descriptive)
- learning_objectives (3-5 measurable objectives)
- introduction (200-300 word personalized narrative)
- core_concepts (2-3, each with title, content, examples)
- prompting_examples (2-3 per chapter, each with: title, description,
  prompt (exact copy-paste text), expected_output, customization_tips)
- agent_examples (1-2 per chapter, each with: title, scenario,
  agent_role, instructions (multi-step list), expected_behavior, use_case)
- exercises (2 practical exercises — one hands-on, one reflection)
- applied_project (1 realistic project with deliverable)
- key_takeaways (5 concise bullet points)
- exact_prompt (1 copy-paste-ready prompt per chapter)
- self_assessment_questions (3, each with question, options, answer)
- industry_context (1 paragraph)
- estimated_time_hours (typically 3-5 hours)
```

### Execute Logic
1. Use chapter_scaffold (preferred) or legacy prioritized_gaps fallback
2. Retrieve learning content from RAG in parallel for each skill
3. Split chapters into batches (BATCH_SIZE=3, BATCH_MAX_TOKENS=22000)
4. Call LLM in parallel for each batch
5. Merge results — must produce EXACTLY num_chapters
6. **Quality Gate** (scaffold only):
   - Evaluate with PathQualityEvaluator
   - If quality < QUALITY_THRESHOLD (2.5): one retry with feedback
   - Second failure accepted (never blocks)

### Enriched Chapter Schema

```json
{
  "chapter_number": 1,
  "skill_id": "SK.FND.004",
  "skill_name": "Reasoning vs retrieval vs tools",
  "current_level": 1,
  "target_level": 2,
  "title": "Understanding AI's Three Superpowers",
  "learning_objectives": [
    "Identify when to use reasoning, retrieval, or tool-use approaches",
    "Explain the trade-offs between each approach"
  ],
  "introduction": "As a marketing manager...",
  "core_concepts": [
    {"title": "Reasoning", "content": "...", "examples": ["..."]}
  ],
  "prompting_examples": [
    {
      "title": "Chain-of-Thought Market Analysis",
      "description": "...",
      "prompt": "Act as a senior marketing analyst...",
      "expected_output": "...",
      "customization_tips": "..."
    }
  ],
  "agent_examples": [
    {
      "title": "Research Assistant Agent",
      "scenario": "...",
      "agent_role": "...",
      "instructions": ["Step 1...", "Step 2..."],
      "expected_behavior": "...",
      "use_case": "..."
    }
  ],
  "exercises": [],
  "applied_project": {
    "project_title": "AI Strategy Brief",
    "project_description": "...",
    "deliverable": "1-page strategy document",
    "estimated_time_minutes": 45
  },
  "key_takeaways": ["...", "...", "...", "...", "..."],
  "exact_prompt": {
    "title": "...",
    "context": "...",
    "prompt_text": "...",
    "expected_output": "...",
    "how_to_customize": "..."
  },
  "self_assessment_questions": [
    {"question": "...", "options": ["A", "B", "C", "D"], "answer": "B"}
  ],
  "industry_context": "In the retail industry...",
  "estimated_time_hours": 4
}
```

---

## 12. Agent 5: Module Outline Generator

### System Prompt (Verbatim)

```
You are an expert instructional designer who breaks learning modules
into sequential lessons for working professionals learning AI/ML skills.

Given a module with its skill, level progression, and learning objectives,
create a lesson outline of 3-5 lessons.

Each lesson must:
1. Build progressively on the previous one
2. Have a clear, specific focus
3. Include an estimated time (15-45 minutes each)
4. Map to the module's learning objectives

Lesson types:
- "concept" — theory and explanation
- "practice" — hands-on exercises and coding
- "assessment" — quiz, knowledge check, or practical evaluation

RULES:
- Every module MUST end with an assessment lesson
- Start with concept lessons, then practice, then assessment
- 3-5 lessons total (prefer 4 for most modules)
- Focus areas should be specific, not generic
```

### Execute Logic
1. Extract skill details, learning objectives, core concepts from chapter
2. Build prompt with level progression (L{current} → L{target})
3. Call LLM with structured schema
4. Post-process: ensure sequential numbering, last lesson is "assessment"

### Output Schema

```json
{
  "lessons": [
    {
      "lesson_number": 1,
      "title": "Understanding AI Reasoning Patterns",
      "type": "concept",
      "focus_area": "Distinguishing reasoning from retrieval",
      "estimated_minutes": 25
    },
    {
      "lesson_number": 2,
      "title": "Hands-On: Building a Retrieval Pipeline",
      "type": "practice",
      "focus_area": "RAG basics with a real dataset",
      "estimated_minutes": 35
    },
    {
      "lesson_number": 3,
      "title": "Tool Integration Patterns",
      "type": "practice",
      "focus_area": "When and how to give AI access to tools",
      "estimated_minutes": 30
    },
    {
      "lesson_number": 4,
      "title": "Assessment: Choose the Right Approach",
      "type": "assessment",
      "focus_area": "Scenario-based evaluation of approach selection",
      "estimated_minutes": 20
    }
  ]
}
```

---

## 13. Agent 6: Lesson Generator

### System Prompt (Verbatim)

```
You are an expert AI-native instructional designer creating lessons
that teach working professionals how to USE AI as a core skill — not just learn about it.

Each lesson must include these sections:

1. CONCEPT_SNAPSHOT — Maximum 4 sentences. Crisp, precise explanation of the core concept.
   No filler, no preamble. Like a brilliant colleague giving a 30-second brief.

2. AI_STRATEGY — How to use AI (LLMs, agents, tools) to solve problems in this topic area.
   Include: when to use AI, what to delegate to AI, what humans must still own.
   Include a suggested prompt the learner can try.

3. PROMPT_TEMPLATE — A ready-to-use prompt the learner can copy and customize.
   Include {{placeholders}} the learner fills in. Describe each placeholder.
   Include the expected shape of the AI output.

4. CODE_EXAMPLES — 2-3 runnable code examples with comments explaining each step.

5. IMPLEMENTATION_TASK — A hands-on task where the learner builds something real.
   Must require: code/deliverable + prompt history + brief architecture explanation.
   Include requirements list, deliverable description, estimated minutes.

6. REFLECTION_QUESTIONS — 3-4 questions that force metacognition about AI usage:
   How did your prompt evolve? What did AI get wrong? What did you improve?
   What would you NOT delegate to AI? Why?
   Each question's prompt_for_deeper_thinking MUST be a detailed, context-rich prompt
   (at least 30 words) that references the specific skill, lesson topic, and a concrete
   scenario.

7. KNOWLEDGE_CHECKS — 3-5 quiz questions testing understanding.
   Each question's ai_followup_prompt MUST be a detailed, self-contained question
   (at least 30 words) that gives the AI Mentor enough context to provide targeted help.

8. EXPLANATION — A brief summary (2-3 paragraphs) for reference.

RULES:
- concept_snapshot is THE primary learning content. 4 sentences max.
- ai_strategy must be practical and specific, not generic AI advice.
- prompt_template must be copy-pasteable with clear {{placeholders}}.
- implementation_task must require BOTH code AND prompt strategy documentation.
- Code examples must be complete and runnable (Python unless otherwise specified).
- For concept lessons: emphasize concept_snapshot, ai_strategy, knowledge_checks.
- For practice lessons: emphasize prompt_template, code_examples, implementation_task.
- For assessment lessons: emphasize knowledge_checks and comprehensive implementation_task.
```

### Max Tokens: 16384

### Lesson Content Output Schema

```json
{
  "concept_snapshot": "string (4 sentences max)",
  "ai_strategy": {
    "description": "string",
    "when_to_use_ai": ["string"],
    "human_responsibilities": ["string"],
    "suggested_prompt": "string"
  },
  "prompt_template": {
    "template": "Act as a {{role}}. Given {{context}}, produce {{deliverable}}...",
    "placeholders": [
      {"name": "role", "description": "...", "example": "senior data analyst"}
    ],
    "expected_output_shape": "string"
  },
  "code_examples": [
    {
      "title": "string",
      "language": "python",
      "code": "string (runnable)",
      "explanation": "string"
    }
  ],
  "implementation_task": {
    "title": "string",
    "description": "string",
    "requirements": ["string"],
    "deliverable": "string",
    "requires_prompt_history": true,
    "requires_architecture_explanation": true,
    "estimated_minutes": 30
  },
  "reflection_questions": [
    {
      "question": "How did your prompt evolve?",
      "prompt_for_deeper_thinking": "Act as a prompt engineering coach... (30+ words)"
    }
  ],
  "knowledge_checks": [
    {
      "question": "Which approach is best for...?",
      "options": ["A. Reasoning", "B. Retrieval", "C. Tool-use", "D. Fine-tuning"],
      "correct_answer": "B",
      "explanation": "Retrieval is best because...",
      "ai_followup_prompt": "Explain why retrieval-augmented generation... (30+ words)"
    }
  ],
  "explanation": "string (2-3 paragraphs)",
  "exercises": [],
  "hands_on_tasks": []
}
```

---

## 14. Agent 7: AI Mentor

### System Prompt (Verbatim)

```
You are an AI learning mentor — a warm, supportive, technically precise coach.

YOUR ROLE:
- Help learners understand concepts by asking leading questions (Socratic method)
- Suggest prompts they can try in the Prompt Lab
- Debug code and explain errors clearly
- Recommend tools and approaches
- Encourage AI collaboration — teach them to work WITH AI, not just learn about it

RULES:
- NEVER give direct answers to exercises or implementation tasks
- Instead, break the problem down and guide the learner to the solution
- When a learner is confused, offer a simpler analogy first
- Always suggest 1-2 follow-up prompts they could try
- Keep responses concise (2-4 paragraphs max)
- Use code examples only when they help clarify a concept
- Adapt your language to the learner's skill level
- Be encouraging but honest — if something is wrong, say so kindly

RESPONSE FORMAT:
- Address the learner's question directly
- Provide guidance (not answers)
- Suggest 1-2 prompts inline (prefixed with "Try this prompt:")
- After your response, add exactly 2 follow-up prompts on new lines prefixed with "Explore further:"
  - These MUST be DIFFERENT from the inline prompts
  - They should expand the topic, offer contrasting perspectives, or go deeper

PROMPT QUALITY RULES (CRITICAL):
- Every suggested prompt MUST be at least 25 words long
- Every prompt MUST start with a role instruction (e.g., "Act as a...", "Imagine you are a...")
- Every prompt MUST include the specific topic, a clear task, and at least one constraint
- NEVER suggest short or vague prompts like "Tell me about X"
- Follow-up prompts must NOT repeat inline prompts — they must explore new ground
```

### 4-Tier Prompt Extraction Logic

The mentor's response is parsed to extract suggested prompts with guaranteed non-empty output:

```python
def extract_suggested_prompts(response_text, lesson_context):
    prompts = []

    # Tier 1: Lines prefixed with "Explore further:"
    for line in response_text.split("\n"):
        if line.strip().startswith("Explore further:"):
            prompt = line.replace("Explore further:", "").strip().strip('"')
            if len(prompt) >= 25:
                prompts.append(prompt)

    # Tier 2: Lines prefixed with "Try this prompt:" or "Ask:"
    if len(prompts) < 2:
        for line in response_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith(("Try this prompt:", "Ask:")):
                prompt = stripped.split(":", 1)[1].strip().strip('"')
                if len(prompt) >= 25 and prompt not in prompts:
                    prompts.append(prompt)

    # Tier 3: Quoted strings 30+ chars with role instruction
    if len(prompts) < 2:
        import re
        quoted = re.findall(r'"([^"]{30,})"', response_text)
        for q in quoted:
            if any(q.lower().startswith(p) for p in ["act as", "imagine you", "as a"]):
                if q not in prompts:
                    prompts.append(q)

    # Tier 4: Context-based fallback (GUARANTEES non-empty)
    if len(prompts) < 2:
        skill = lesson_context.get("skill_name", "AI")
        title = lesson_context.get("lesson_title", "this topic")
        fallbacks = [
            f"Act as an expert in {skill}. Explain the most common mistake beginners make when applying {title} in a real project, and provide a step-by-step correction with examples.",
            f"Imagine you are a senior {skill} practitioner. Compare two different approaches to {title}, highlighting when each is more appropriate with real-world scenarios."
        ]
        for fb in fallbacks:
            if fb not in prompts:
                prompts.append(fb)

    return prompts[:2]  # Always exactly 2
```

### Prompt Persistence

Suggested prompts are stored in the conversation's JSON messages column:

```python
# On chat: store prompts in the message
messages.append({
    "role": "mentor",
    "content": mentor_response,
    "timestamp": datetime.utcnow().isoformat(),
    "suggested_prompts": suggested_prompts,  # ← persisted here
})

# On history: extract from last mentor message
for m in reversed(raw_messages):
    if m.get("role") == "mentor" and m.get("suggested_prompts"):
        last_suggested_prompts = m["suggested_prompts"]
        break
```

---

## 15. Agent 8: Assessment Agent

### System Prompt (Verbatim)

```
You are an expert AI skills assessor. Your task is to generate
assessment questions that accurately measure a person's proficiency level in specific skills.

For each skill, create questions that can distinguish between proficiency levels:
- Level 1 (Aware): Basic concept recognition
- Level 2 (User): Can apply with guidance
- Level 3 (Practitioner): Can adapt independently
- Level 4 (Builder): Ships solutions
- Level 5 (Architect): Designs systems

Generate a mix of:
1. Multiple choice questions for concept understanding
2. Scenario-based questions for practical application
3. Self-assessment questions for experience validation
```

### Two Actions
- **generate**: Takes `skill_ids`, produces assessment questions
- **score**: Takes `responses` + `questions`, produces skill scores and `state_a_skills`

---

## 16. Agent 9: Content Curator

### System Prompt (Verbatim)

```
You are an expert learning resource curator specializing in AI/ML education.
Your task is to recommend high-quality learning resources for specific skills and topics.

For each skill, recommend resources that:
1. Match the target proficiency level
2. Are relevant to the user's industry
3. Come from reputable sources
4. Provide practical, hands-on learning
5. Are current and up-to-date

Include a mix of:
- Articles and blog posts
- Video tutorials
- Interactive courses
- Documentation
- Practice projects
```

---

## 17. Confusion Recovery Service

When a learner clicks "Confused?" on any lesson section, the system generates an alternative explanation.

### System Prompt (Verbatim)

```
You are an expert learning recovery specialist.
A learner is confused about a concept and needs an alternative explanation.
Your job is to explain the same concept in a completely different way than the original lesson.

Respond with VALID JSON matching this exact schema:
{
    "analogy": "A relatable real-world analogy that makes the concept click",
    "step_by_step": ["Step 1...", "Step 2...", "Step 3..."],
    "real_world_example": "A concrete example from industry/daily life",
    "common_misconceptions": ["Misconception 1...", "Misconception 2..."],
    "suggested_mentor_prompt": "A detailed question (at least 30 words) the learner can ask the AI Mentor to go deeper..."
}

Guidelines:
- Use simple, everyday language
- The analogy should be from a completely different domain
- Step-by-step should break down the concept into tiny, digestible pieces
- Include 2-3 common misconceptions
- The suggested_mentor_prompt MUST be detailed and context-rich (at least 30 words)
- Keep total response under 500 words
- Return ONLY valid JSON, no markdown or extra text
```

### Parameters
- Temperature: 0.7
- Max tokens: 1024
- JSON mode: True

---

## 18. Skill Genome Service — EMA Mastery Tracking

The Skill Genome is a **global per-user skill mastery overlay** that persists across learning paths.

### EMA Formula

```
new_mastery = EMA_WEIGHT × current_mastery + (1 - EMA_WEIGHT) × new_signal
```

Where `EMA_WEIGHT = 0.7` (existing mastery is strongly retained).

### Confidence Score

```
confidence = min(1.0, evidence_count / CONFIDENCE_CAP)
```

Where `CONFIDENCE_CAP = 10` (10 evidence signals = 100% confidence).

### Signal Strength by Evidence Type

| Evidence Type | Base Signal | Range |
|--------------|-------------|-------|
| Concept lesson | 1.0 | 0-4 |
| Practice lesson | 2.0 | 0-4 |
| Assessment lesson | 3.0 | 0-4 |
| Quiz score (0-100) | max(base, score/100 × 4.0) | 0-4 |
| Project submission | feedback_quality × 4.0 | 0-4 |

### Complete Algorithm

```python
class SkillGenomeService:
    EMA_WEIGHT = 0.7
    CONFIDENCE_CAP = 10

    async def update_from_lesson(self, db, user_id, skill_id, quiz_score=None, lesson_type="concept"):
        base_signal = {"concept": 1.0, "practice": 2.0, "assessment": 3.0}.get(lesson_type, 1.5)
        if quiz_score is not None:
            base_signal = max(base_signal, quiz_score / 100 * 4.0)
        return await self._upsert(db, user_id, skill_id, base_signal, "lesson")

    async def update_from_project(self, db, user_id, skill_id, feedback_quality=0.5):
        signal = feedback_quality * 4.0
        return await self._upsert(db, user_id, skill_id, signal, "project")

    async def _upsert(self, db, user_id, skill_id, new_signal, evidence_type):
        entry = await self.get_skill_entry(db, user_id, skill_id)

        if entry is None:
            # First evidence — create new entry
            entry = SkillGenomeEntry(
                user_id=user_id,
                ontology_node_id=skill_id,
                skill_name=ontology.get_skill(skill_id)["name"],
                domain=ontology.get_skill(skill_id).get("domain"),
                mastery_level=new_signal,
                evidence_count=1,
                last_evidence=evidence_type,
                confidence=min(1.0, 1 / self.CONFIDENCE_CAP),
            )
        else:
            # EMA update
            entry.mastery_level = (
                self.EMA_WEIGHT * entry.mastery_level
                + (1 - self.EMA_WEIGHT) * new_signal
            )
            entry.mastery_level = max(0.0, min(4.0, entry.mastery_level))  # clamp
            entry.evidence_count += 1
            entry.last_evidence = evidence_type
            entry.confidence = min(1.0, entry.evidence_count / self.CONFIDENCE_CAP)
```

---

## 19. State Inference — Prerequisite Expansion

Before gap computation, `expand_state_a()` infers skills the learner likely has based on prerequisites:

If a learner has Skill X at Level N, and Skill X requires Prerequisite Y, then the learner likely has Prerequisite Y at least at the level declared in the ontology.

This prevents generating chapters for prerequisites the learner has already mastered through experience.

---

## 20. Path Quality Evaluator

After LLM enrichment, chapters are evaluated on quality:

- Each chapter checked for: learning objectives count, introduction word count, core concepts, exercises
- Score 0-5 per chapter
- If average < 2.5: one retry with feedback ("Chapter 3 is missing core_concepts...")
- Second failure accepted (never blocks path generation)

---

## 21. Prompt Lab — Execution & Implementation Tasks

### Prompt Lab Execution

```
System Prompt:
  You are an AI assistant helping a learner practice prompt engineering.
  The learner is working on a lesson and experimenting with prompts.
  Provide helpful, educational responses that demonstrate good AI output.
  Keep responses focused and under 1500 words.

Parameters:
  Temperature: 0.7
  Max tokens: 2048
  Rate limit: 10 iterations per lesson (MAX_ITERATIONS_PER_LESSON = 10)
```

### Implementation Task Review

```
System Prompt:
  You are an expert AI learning coach reviewing a learner's implementation task submission.
  The learner completed a hands-on task and is submitting their prompt engineering strategy.

  Evaluate their work and provide:
  1. Specific strengths (2-3 bullet points, under "Strengths:")
  2. Areas for improvement (2-3 bullet points, under "Improvements:")
  3. Prompt strategy tips (2-3 bullet points, under "Prompt Strategy Tips:")
  4. Brief overall feedback paragraph (2-3 sentences)

  If the learner submitted a prompt attempt, analyze it specifically:
  - Does it use a clear role instruction?
  - Does it include specific constraints and deliverables?
  - Does it provide enough context?
  - What prompting techniques would improve it?

Parameters:
  Temperature: 0.5
  Max tokens: 1024
```

### Two-Step Submission Flow (Frontend)
1. **Step 1**: Write your prompt (min 10 chars) → "Run in LLM" button appears
2. **Step 2**: Reflect on strategy (min 20 chars) → guided questions provided
3. **Submit**: Sends `learner_prompt` + `strategy_explanation` + `prompt_history_summary`
4. **Feedback**: AI returns structured strengths, improvements, and prompt strategy tips

---

## 22. LLM Platform Integration

The platform supports sending prompts to 11 external LLM platforms.

### Platform Registry

```typescript
const LLM_OPTIONS = [
  { key: 'chatgpt',    name: 'ChatGPT',    url: 'https://chatgpt.com/' },
  { key: 'claude',     name: 'Claude',     url: 'https://claude.ai/new' },
  { key: 'gemini',     name: 'Gemini',     url: 'https://gemini.google.com/app' },
  { key: 'copilot',    name: 'Copilot',    url: 'https://copilot.microsoft.com/' },
  { key: 'perplexity', name: 'Perplexity', url: 'https://www.perplexity.ai/search' },
  { key: 'grok',       name: 'Grok',       url: 'https://x.com/i/grok' },
  { key: 'deepseek',   name: 'DeepSeek',   url: 'https://chat.deepseek.com/' },
  { key: 'mistral',    name: 'Mistral',    url: 'https://chat.mistral.ai/chat' },
  { key: 'meta',       name: 'Meta AI',    url: 'https://www.meta.ai/' },
  { key: 'poe',        name: 'Poe',        url: 'https://poe.com/' },
  { key: 'huggingchat',name: 'HuggingChat', url: 'https://huggingface.co/chat/' },
]
```

### Two Injection Strategies

1. **URL Parameter** (`?q=`): ChatGPT, Claude, Perplexity
   - Opens `url + '?q=' + encodeURIComponent(prompt)`
   - Button label: "Run in {LLM Name}"

2. **Clipboard + Toast**: All others
   - Copies prompt to clipboard
   - Opens LLM URL in new tab
   - Shows toast: "Prompt copied! Paste it into {LLM Name}"
   - Button label: "Copy & open {LLM Name}"

### Preference Persistence
- Stored in `localStorage` under key `preferred-llm`
- Default: `chatgpt`
- Cross-component sync via `CustomEvent('llm-changed')`

---

## 23. Database Schema — Complete Models

### Technology Stack
- **Database**: SQLite with async support, WAL mode, 30s timeout
- **ORM**: SQLAlchemy 2.0+ async with `DeclarativeBase`
- **Sessions**: `AsyncSession` via `AsyncSessionLocal`
- **Primary Keys**: UUID strings (auto-generated via `uuid.uuid4()`)

### Model 1: User

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,           -- UUID
    email TEXT UNIQUE,             -- nullable, max 255
    name TEXT,                     -- nullable, max 255
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Relationships: profiles[], goals[], assessments[], skill_gaps[],
--                learning_paths[], progress_records[], skill_masteries[]
```

### Model 2: Profile

```sql
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT REFERENCES users(id),  -- nullable
    source TEXT DEFAULT 'custom',  -- max 50, 'test_profile' or 'custom'
    name TEXT NOT NULL,            -- max 255
    current_role TEXT NOT NULL,    -- max 255
    target_role TEXT,              -- max 255, nullable
    industry TEXT NOT NULL,        -- max 255
    experience_years INTEGER,     -- nullable
    ai_exposure_level TEXT,       -- max 50, nullable (None/Basic/Intermediate/Advanced)
    learning_intent TEXT,         -- nullable
    profile_data JSON,            -- full profile JSON, nullable
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 3: Goal

```sql
CREATE TABLE goals (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    profile_id TEXT REFERENCES profiles(id),  -- nullable
    target_role TEXT NOT NULL,     -- max 255
    target_jd_text TEXT,          -- nullable
    learning_intent TEXT,         -- nullable
    state_b_skills JSON,          -- nullable, {skill_id: level}
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 4: Assessment

```sql
CREATE TABLE assessments (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT REFERENCES goals(id),  -- nullable
    quiz_questions JSON,           -- nullable, list of questions
    responses JSON,                -- nullable, user responses
    state_a_skills JSON,           -- nullable, assessed levels
    completed_at DATETIME,         -- nullable
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 5: SkillGap

```sql
CREATE TABLE skill_gaps (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES goals(id),
    assessment_id TEXT REFERENCES assessments(id),  -- nullable
    state_a_skills JSON,           -- nullable, {skill_id: level}
    state_b_skills JSON,           -- nullable, {skill_id: level}
    gaps JSON,                     -- nullable, prioritized gap list
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 6: LearningPath

```sql
CREATE TABLE learning_paths (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES goals(id),
    gap_id TEXT NOT NULL REFERENCES skill_gaps(id),
    title TEXT,                    -- max 255, nullable
    description TEXT,              -- max 1000, nullable
    chapters JSON,                 -- nullable, 5 enriched chapters
    total_chapters INTEGER DEFAULT 5,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 7: Module

```sql
CREATE TABLE modules (
    id TEXT PRIMARY KEY,           -- UUID
    path_id TEXT NOT NULL REFERENCES learning_paths(id),
    chapter_number INTEGER NOT NULL,
    skill_id TEXT NOT NULL,        -- max 50
    skill_name TEXT NOT NULL,      -- max 255
    title TEXT NOT NULL,           -- max 500
    current_level INTEGER DEFAULT 0,
    target_level INTEGER DEFAULT 1,
    lesson_outline JSON,           -- nullable, [{lesson_number, title, type, focus_area, estimated_minutes}]
    total_lessons INTEGER DEFAULT 3,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 8: Lesson

```sql
CREATE TABLE lessons (
    id TEXT PRIMARY KEY,           -- UUID
    module_id TEXT NOT NULL REFERENCES modules(id),
    path_id TEXT NOT NULL REFERENCES learning_paths(id),
    lesson_number INTEGER NOT NULL,
    title TEXT NOT NULL,           -- max 500
    lesson_type TEXT DEFAULT 'standard',  -- max 50
    content JSON,                  -- nullable, generated on-demand
    status TEXT DEFAULT 'not_started',    -- max 20 (not_started|in_progress|completed)
    quiz_score REAL,               -- nullable
    exercise_attempts INTEGER DEFAULT 0,
    completed_at DATETIME,         -- nullable
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 9: SkillMastery (Path-scoped)

```sql
CREATE TABLE skill_mastery (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    path_id TEXT NOT NULL REFERENCES learning_paths(id),
    skill_id TEXT NOT NULL,        -- max 50
    skill_name TEXT NOT NULL,      -- max 255
    initial_level INTEGER DEFAULT 0,
    current_level REAL DEFAULT 0.0,  -- fractional progress
    target_level INTEGER DEFAULT 1,
    lessons_completed INTEGER DEFAULT 0,
    total_lessons INTEGER DEFAULT 0,
    avg_quiz_score REAL,           -- nullable
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 10: Progress

```sql
CREATE TABLE progress (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    path_id TEXT NOT NULL REFERENCES learning_paths(id),
    current_chapter INTEGER DEFAULT 1,
    chapter_status JSON,           -- nullable, {1: "completed", 2: "in_progress"}
    quiz_scores JSON,              -- nullable, {1: 85, 2: 90}
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 11: LessonReaction

```sql
CREATE TABLE lesson_reactions (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    reaction TEXT NOT NULL,        -- max 20 (helpful|interesting|mind_blown|confused)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, lesson_id, reaction)
);
```

### Model 12: SkillGenomeEntry (Global)

```sql
CREATE TABLE skill_genome (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    ontology_node_id TEXT NOT NULL,  -- max 100
    skill_name TEXT NOT NULL,      -- max 200
    domain TEXT,                   -- max 100, nullable
    mastery_level REAL DEFAULT 0.0,  -- global mastery 0-5
    evidence_count INTEGER DEFAULT 0,
    last_evidence TEXT,            -- max 50 (quiz|lesson|project|mentor), nullable
    confidence REAL DEFAULT 0.0,   -- 0-1
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, ontology_node_id)
);
```

### Model 13: MentorConversation

```sql
CREATE TABLE mentor_conversations (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    path_id TEXT NOT NULL REFERENCES learning_paths(id),
    lesson_id TEXT REFERENCES lessons(id),  -- nullable (null = path-level conversation)
    messages JSON DEFAULT '[]',    -- [{role, content, timestamp, suggested_prompts?}]
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 14: ConfusionEvent

```sql
CREATE TABLE confusion_events (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    skill_id TEXT,                 -- max 100, nullable
    section TEXT,                  -- max 50, nullable
    recovery_content JSON,         -- nullable, generated explanation
    resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 15: PromptHistory

```sql
CREATE TABLE prompt_history (
    id TEXT PRIMARY KEY,           -- UUID
    lesson_id TEXT NOT NULL REFERENCES lessons(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    iteration INTEGER DEFAULT 1,   -- 1-10 per lesson
    prompt_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    execution_time_ms INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Model 16: AgentLog

```sql
CREATE TABLE agent_logs (
    id TEXT PRIMARY KEY,           -- UUID
    user_id TEXT REFERENCES users(id),  -- nullable
    agent_name TEXT NOT NULL,      -- max 100
    action TEXT NOT NULL,          -- max 100
    input_data JSON,               -- nullable
    output_data JSON,              -- nullable
    error TEXT,                    -- max 1000, nullable
    duration_ms INTEGER,           -- nullable
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 24. API Routes — Complete Endpoint Reference

### Base URL: `/api`

### Profiles (`/api/profiles`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/parse-resume` | UploadFile (PDF/DOCX, max 10MB) | Parsed resume fields | |
| POST | `/parse-jd-profile` | `{jd_text, target_role}` | Parsed profile from JD | |
| GET | `/` | — | `Profile[]` | List all profiles |
| GET | `/{profile_id}` | — | `Profile` | Single profile |
| POST | `/upload` | `ProfileUpload` | `{id, user_id, name, message}` | Create profile |
| GET | `/user/{user_id}/profiles` | — | `ProfileSummary[]` | User's profiles |

### Analysis (`/api/analysis`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/full` | `FullAnalysisRequest` | `{user_id, goal_id, skill_gap_id, learning_path_id, result}` | Full pipeline (20-40s) |
| POST | `/parse-jd` | `{jd_text, target_role}` | `{target_role, extracted_skills, state_b_skills}` | JD only |
| POST | `/parse-jd-skills` | `{jd_text, target_role}` | `{target_role, top_10_skills, role_analysis}` | Top 10 with descriptions |
| GET | `/gap/{user_id}` | — | `SkillGapResponse` | Latest gap |
| POST | `/visualization` | `{analysis_result}` | HTML (D3.js SVG) | Self-contained visualization |

### Assessment (`/api/assessment`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/generate` | `{goal_id?, skill_ids?}` | `{assessment_id, questions}` | |
| POST | `/submit` | `{assessment_id, responses}` | `{assessment_id, skill_scores, state_a_skills}` | |
| GET | `/{assessment_id}` | — | `AssessmentResponse` | |

### Learning Paths (`/api/paths`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/generate` | `{gap_id, goal_id}` | `LearningPathResponse` | Scaffold + enrich |
| GET | `/{path_id}` | — | `LearningPathResponse` | |
| GET | `/user/{user_id}` | — | `LearningPathResponse[]` | |

### Learning Execution (`/api/learning`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/{path_id}/activate` | — | `{modules, total_lessons, skill_masteries}` | Creates modules + lessons |
| GET | `/{path_id}/dashboard` | — | `LearningDashboardResponse` | Returns 400 if not activated |
| GET | `/{path_id}/modules` | — | `ModuleResponse[]` | |
| POST | `/{path_id}/lessons/{lesson_id}/start` | — | `LessonResponse` | Generates content on-demand |
| PUT | `/{path_id}/lessons/{lesson_id}/complete` | `{quiz_score?, exercise_completed?}` | `{lesson, module_progress, skill_mastery_update}` | |
| GET | `/{path_id}/skills` | — | `SkillMasteryResponse[]` | |

### Prompt Lab (`/api/learning`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/{path_id}/prompt-lab/execute` | `{lesson_id, prompt, iteration}` | `{response, iteration, tokens_used, execution_time_ms}` | Max 10 per lesson |
| GET | `/{path_id}/prompt-lab/{lesson_id}/history` | — | `{lesson_id, iterations, total_iterations}` | |
| POST | `/{path_id}/implementation-task/submit` | `{lesson_id, prompt_history_summary, strategy_explanation, learner_prompt}` | `{feedback, strengths, improvements, prompt_strategy_tips}` | |

### AI Mentor (`/api/learning`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/{path_id}/mentor/chat` | `{message, lesson_id?}` | `{response, suggested_prompts, conversation_id}` | |
| GET | `/{path_id}/mentor/history` | `?lesson_id=` | `{conversation_id, messages, last_suggested_prompts}` | |

### Reactions & Recovery (`/api/learning`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | `/{path_id}/lessons/{lesson_id}/react` | `{reaction}` | `{reactions, confusion_detected}` | Toggle reaction |
| GET | `/{path_id}/lessons/{lesson_id}/reactions` | — | `{reactions, confusion_detected}` | |
| POST | `/{path_id}/lessons/{lesson_id}/confusion-recovery` | `{section}` | `{analogy, step_by_step, real_world_example, common_misconceptions, suggested_mentor_prompt}` | |

### Skill Genome (`/api/genome`)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| GET | `/{user_id}` | — | `{user_id, entries, total_skills}` | |
| GET | `/{user_id}/{skill_id}` | — | `SkillGenomeEntryResponse` | |
| GET | `/{user_id}/curiosity-feed` | `?limit=` | `{user_id, items, total_items}` | |

### Other

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| GET | `/api/personalization/{user_id}` | — | `PersonalizationResult` | |
| GET | `/api/personalization/{user_id}/path/{path_id}` | — | `PersonalizationResult` | |
| GET | `/api/ontology/` | — | Full ontology | |
| GET | `/api/ontology/skills` | `?domain=&level=` | Filtered skills | |
| GET | `/api/ontology/domains` | — | All domains | |
| GET | `/api/ontology/roles` | — | All role templates | |
| GET | `/api/ontology/proficiency-scale` | — | Scale definition | |
| POST | `/api/deterministic-paths/generate` | `{state_a, state_b}` | Scaffold (no LLM) | |
| GET | `/api/progress/{path_id}` | — | Progress | |
| PUT | `/api/progress/{path_id}` | `{chapter, status, quiz_score}` | Updated progress | |
| GET | `/api/progress/user/{user_id}/dashboard` | — | Dashboard stats | |

---

## 25. Pydantic Schemas — Complete Definitions

All schemas use Pydantic BaseModel with `from_attributes = True` for ORM compatibility.

### Profile Schemas

```python
class ProfileUpload(BaseModel):
    name: str
    current_role: str
    target_role: str | None = None
    industry: str
    experience_years: int | None = None
    ai_exposure_level: Literal["None", "Basic", "Intermediate", "Advanced"] | None = None
    learning_intent: str | None = None
    current_skills: dict | None = None
    target_jd: str | None = None
```

### Analysis Schemas

```python
class FullAnalysisRequest(BaseModel):
    profile_id: str | None = None
    custom_profile: dict | None = None
    target_jd_text: str
    target_role: str | None = None
    skip_assessment: bool = False
    self_assessed_skills: dict | None = None
```

### Learning Schemas

```python
class LessonOutline(BaseModel):
    lesson_number: int
    title: str
    type: Literal["concept", "practice", "assessment"]
    focus_area: str
    estimated_minutes: int

class ModuleResponse(BaseModel):
    id: str
    chapter_number: int
    skill_id: str
    skill_name: str
    title: str
    current_level: int
    target_level: int
    lesson_outline: list[LessonOutline] | None
    total_lessons: int
    completed_lessons: int = 0
    status: Literal["not_started", "in_progress", "completed"] = "not_started"

class SkillMasteryResponse(BaseModel):
    skill_id: str
    skill_name: str
    initial_level: int
    current_level: float
    target_level: int
    lessons_completed: int
    total_lessons: int
    avg_quiz_score: float | None
    progress_percentage: float = 0.0

class LearningDashboardResponse(BaseModel):
    path_id: str
    path_title: str
    target_role: str
    overall_progress: float  # 0-100
    modules: list[ModuleResponse]
    skill_masteries: list[SkillMasteryResponse]
    current_module: ModuleResponse | None
    next_lesson: LessonOutline | None
    next_lesson_id: str | None = None
    total_lessons_completed: int
    total_lessons: int
    estimated_hours_remaining: float

class LessonCompleteRequest(BaseModel):
    quiz_score: float | None = None
    exercise_completed: bool = False
```

### Mentor Schemas

```python
class MentorChatRequest(BaseModel):
    message: str
    lesson_id: str | None = None

class MentorChatResponse(BaseModel):
    response: str
    suggested_prompts: list[str] = []
    conversation_id: str

class MentorHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[MentorMessage]
    last_suggested_prompts: list[str] = []
```

### Prompt Lab Schemas

```python
class PromptExecutionRequest(BaseModel):
    lesson_id: str
    prompt: str
    iteration: int = 1

class ImplementationTaskSubmitRequest(BaseModel):
    lesson_id: str
    prompt_history_summary: str = ""
    strategy_explanation: str
    learner_prompt: str = ""

class ImplementationTaskFeedbackResponse(BaseModel):
    feedback: str
    strengths: list[str] = []
    improvements: list[str] = []
    prompt_strategy_tips: list[str] = []
```

### Confusion Recovery Schemas

```python
class ConfusionRecoveryRequest(BaseModel):
    section: str = "general"

class ConfusionRecoveryResponse(BaseModel):
    analogy: str
    step_by_step: list[str]
    real_world_example: str
    common_misconceptions: list[str]
    suggested_mentor_prompt: str
```

### Personalization Schemas

```python
class PersonalizationResult(BaseModel):
    struggling_skills: list[StrugglingSkill]  # {skill_name, signal}
    strong_skills: list[StrongSkill]  # {skill_name, mastery}
    suggested_review: list[SuggestedReview]  # {lesson_id, title, reason}
    pace_recommendation: Literal["slow_down", "on_track", "can_accelerate"]
    next_focus: NextFocus | None  # {skill_name, reason}
```

---

## 26. Frontend Architecture — Components & State

### Technology Stack
- **Framework**: React with TypeScript
- **Build**: Vite
- **State**: React Query (TanStack Query) for server state, Zustand for local state
- **Styling**: Tailwind CSS
- **HTTP**: Axios
- **Routing**: React Router v6

### Component Hierarchy

```
App
├── DashboardPage
│   ├── Stat Cards (4)
│   ├── Active Paths (clickable cards with progress bars)
│   └── Completed Paths
│
├── LearningDashboardPage
│   ├── Header (path title, target role, progress %)
│   ├── ProgressSummary (4 stats)
│   ├── 3-column layout:
│   │   ├── ModuleSidebar (left)
│   │   ├── Module Detail + NextLessonCard (center)
│   │   └── SkillGapTracker (right)
│   └── Activation CTA (if not activated)
│
├── LessonPage
│   ├── Breadcrumb navigation
│   ├── Lesson header (type badge, status)
│   ├── Content sections (AI-native OR legacy):
│   │   ├── ConceptSnapshot
│   │   ├── AIStrategyPanel
│   │   ├── PromptTemplateCard
│   │   ├── PromptLab (interactive)
│   │   ├── CodeBlock[] (examples)
│   │   ├── ImplementationTaskCard
│   │   ├── ReflectionPrompts
│   │   └── KnowledgeCheck
│   ├── LessonReactions
│   ├── Bottom action buttons
│   └── ConfusionRecoveryDrawer (slide-in)
│
└── MentorChat (floating, global)
    ├── Floating button (bottom-right)
    ├── Chat panel (w-96, h-[32rem])
    ├── Message list with PromptCards
    ├── Suggested prompts (2 chips)
    └── LLMChooser dropdown
```

### Zustand Learning Store

```typescript
interface LearningState {
  pathId: string | null
  modules: LearningModule[]
  currentModuleId: string | null
  currentLessonId: string | null
  skillMasteries: SkillMastery[]
  overallProgress: number
  isActivated: boolean

  // Actions
  setPath(pathId: string): void
  setModules(modules: LearningModule[]): void
  setCurrentLesson(moduleId: string, lessonId: string): void
  updateSkillMastery(mastery: SkillMastery): void
  updateModuleStatus(moduleId: string, status: string, completedLessons: number): void
  setOverallProgress(progress: number): void
  setActivated(activated: boolean): void
  reset(): void
}
```

---

## 27. Frontend Component Details

### ConceptSnapshot
- **Props**: `snapshot: string`
- **Renders**: Single section with Zap icon, indigo gradient border, snapshot text
- **Purpose**: THE primary learning content (4 sentences max)

### AIStrategyPanel
- **Props**: `strategy: AIStrategy`
- **State**: `copied`, `llmKey` (listens to `llm-changed` event)
- **Renders**:
  - Description paragraph
  - 2-column grid: "Delegate to AI" (teal) + "Keep Human" (amber)
  - Suggested prompt in dark code block with Run/Copy buttons
- **Interactions**: `openInLLM()`, copy to clipboard

### PromptTemplateCard
- **Props**: `template: PromptTemplate`
- **State**: `copied`, `showPlaceholders`, `llmKey`
- **Renders**:
  - Dark code block with highlighted `{{placeholders}}`
  - Expected output section
  - Expandable placeholder guide
- **Interactions**: Copy, Run in LLM, toggle placeholder details

### PromptLab (Interactive)
- **Props**: `pathId`, `lessonId`, `template?`
- **State**: `prompt`, `response`, `showHistory`
- **Features**:
  - Textarea prefilled from template
  - Iteration counter (1-10)
  - Execute/Refine/Reset buttons
  - History accordion (collapsible, shows v1, v2...)
  - Response display with execution time
- **API**: `executePrompt()`, `getPromptHistory()`

### ImplementationTaskCard
- **Props**: `task`, `pathId`, `lessonId`, `promptHistory?`, `onSubmit?`
- **State**: `promptAttempt`, `strategy`, `submitted`, `feedbackExpanded`, `llmKey`
- **Two-step submission**:
  1. Write prompt for task (min 10 chars) → Run in LLM button
  2. Reflect on strategy (min 20 chars) → Guided questions
- **Feedback display**: Strengths (green), Improvements (amber), Prompt Strategy Tips (purple)
- **API**: `submitImplementationTask()`

### KnowledgeCheck
- **Props**: `checks: KnowledgeCheck[]`, `onComplete`
- **State**: `currentIndex`, `selectedAnswer`, `showFeedback`, `correctCount`, `finished`
- **Flow**: Single-choice → Immediate feedback → AI followup prompt → Next → Score screen
- **Interaction**: "Ask AI Mentor" button dispatches `open-mentor` event

### LessonReactions
- **Props**: `pathId`, `lessonId`, `onConfused?`
- **UI**: 4 emoji buttons (helpful, interesting, mind_blown, confused)
- **Logic**: If confused toggled + confusion_detected → triggers `onConfused` callback
- **API**: `toggleReaction()`, `getLessonReactions()`

### ConfusionRecoveryDrawer
- **Props**: `isOpen`, `onClose`, `pathId`, `lessonId`, `section?`
- **Renders** (sliding right drawer):
  - Analogy (amber box)
  - Step by Step (numbered list)
  - Real-World Example (emerald box)
  - Common Misconceptions (alert icons)
  - "Ask AI Mentor" button
  - "Did this help?" Yes/No
- **API**: `getConfusionRecovery()`

### ReflectionPrompts
- **Props**: `questions: ReflectionQuestion[]`
- **State**: `expandedIndex`
- **Renders**: Accordion with numbered questions, expandable "Go deeper" prompt
- **Interaction**: "Ask AI Mentor" dispatches `open-mentor` event

### MentorChat (Global Floating)
- **Props**: None (uses `useParams` for pathId/lessonId)
- **State**: `isOpen`, `input`, `autoSendTrigger`, `llmKey`, `savedPrompts`
- **Features**:
  - Floating button (bottom-right) when closed
  - Chat panel (w-96, h-[32rem]) when open
  - Message parsing: extracts embedded prompts (PromptCards)
  - 4-tier suggested prompt persistence
  - Smart scroll: assistant messages → scroll to top, user → scroll to bottom
  - Auto-send from `open-mentor` events
- **Prompt Priority Chain** (frontend):
  1. Mutation data (fresh from POST /chat)
  2. Saved prompts (useState from previous render)
  3. DB prompts (from GET /history `last_suggested_prompts`)
  4. History prompts (text extraction from message content)
- **API**: `sendMentorMessage()`, `getMentorHistory()`

### LLMChooser
- **Props**: None
- **State**: `isOpen`, `selectedLLM`
- **Renders**: Dropdown button showing current LLM name
- **Interaction**: On select, saves to localStorage, dispatches `llm-changed` event
- **Scroll**: `max-h-[280px] overflow-y-auto` for 11 options

---

## 28. Cross-Component Event System

Components communicate via browser CustomEvents:

### Event 1: `llm-changed`
- **Dispatched by**: LLMChooser
- **Detail**: LLM key string (e.g., `"claude"`)
- **Listened by**: AIStrategyPanel, PromptTemplateCard, ImplementationTaskCard, MentorChat
- **Purpose**: Update preferred LLM across all components in real-time

```typescript
// Dispatch
window.dispatchEvent(new CustomEvent('llm-changed', { detail: llmKey }))

// Listen
useEffect(() => {
  const handler = (e: Event) => setLlmKey((e as CustomEvent).detail)
  window.addEventListener('llm-changed', handler)
  return () => window.removeEventListener('llm-changed', handler)
}, [])
```

### Event 2: `open-mentor`
- **Dispatched by**: KnowledgeCheck, ReflectionPrompts, ConfusionRecoveryDrawer, ImplementationTaskCard
- **Detail**: `{ message: string }` (contextual prompt)
- **Listened by**: MentorChat
- **Purpose**: Open mentor panel with pre-filled message, auto-send

```typescript
// Dispatch
window.dispatchEvent(new CustomEvent('open-mentor', {
  detail: { message: "I'm confused about chain-of-thought prompting..." }
}))

// Listen (MentorChat)
useEffect(() => {
  const handler = (e: Event) => {
    const { message } = (e as CustomEvent).detail
    setInput(message)
    autoSendRef.current = message
    setAutoSendTrigger(n => n + 1)
    setIsOpen(true)
  }
  window.addEventListener('open-mentor', handler)
  return () => window.removeEventListener('open-mentor', handler)
}, [])
```

---

## 29. Lesson Content Rendering Logic

### Content Format Detection

```typescript
const content = lesson.content
const isAINative = !!content?.concept_snapshot

if (isAINative) {
  // Render AI-native sections:
  // ConceptSnapshot → AIStrategyPanel → PromptTemplateCard → PromptLab
  // → CodeBlock[] → ImplementationTaskCard → ReflectionPrompts → KnowledgeCheck
} else {
  // Render legacy sections:
  // Explanation → CodeBlock[] → Exercises[] → KnowledgeCheck → HandsOnTasks[]
}
```

### Completion Gating

```typescript
const hasKnowledgeCheck = !!content?.knowledge_checks?.length
const hasImplementationTask = !!content?.implementation_task?.title

const canComplete = !isAINative || (
  (!hasKnowledgeCheck || quizScore !== null) &&
  (!hasImplementationTask || taskSubmitted)
)

// If !canComplete, show gating message:
// "Complete the Knowledge Check and Implementation Task to mark as done"
```

---

## 30. User Flow — End to End

### Phase 1: Profile Creation & Analysis
1. User uploads profile (name, role, industry, experience, AI exposure)
2. User pastes target job description
3. System runs full analysis pipeline (20-40 seconds):
   - Profile Analyzer → State A (current skills)
   - JD Parser → State B (target skills)
   - Gap Analyzer → prioritized gaps
   - Gap Engine → scored & ranked gaps
   - Path Generator → deterministic scaffold
   - Path Enricher → enriched 5-chapter learning path
4. User sees results: top skills, gaps, fit score, journey roadmap

### Phase 2: Path Activation
1. User navigates to learning dashboard
2. If not activated → sees "Ready to Start Learning?" CTA
3. On activation:
   - Module Outline Agent generates 3-5 lessons per chapter (parallel)
   - Module + Lesson + SkillMastery records created
4. Dashboard shows: module sidebar, progress summary, skill gap tracker

### Phase 3: Lesson Execution
1. User selects module → sees lesson list
2. Clicks "Start Lesson" → content generated on-demand (if not cached)
3. Lesson flow:
   a. Read Concept Snapshot (4 sentences)
   b. Review AI Strategy (delegate to AI vs keep human)
   c. Study Prompt Template (copy-pasteable with placeholders)
   d. Practice in Prompt Lab (iterate up to 10 times)
   e. Complete Implementation Task (write prompt + reflect on strategy)
   f. Answer Knowledge Check (multi-choice quiz)
   g. Review Reflection Questions (metacognition)
4. Mark Complete → updates SkillMastery, Skill Genome

### Phase 4: Ongoing Learning
- **AI Mentor**: Available throughout via floating chat button
- **Confusion Recovery**: "Confused?" reaction triggers alternative explanation
- **Skill Genome**: Tracks global mastery across all paths
- **Curiosity Feed**: Suggests adjacent skills based on completed skills
- **Personalization**: Identifies struggling/strong skills, adjusts pace

---

## 31. Implementation Checklist

### Backend Setup
- [ ] Create FastAPI application with async SQLAlchemy
- [ ] Implement SQLite database with WAL mode
- [ ] Create all 16 database models
- [ ] Create all Pydantic schemas
- [ ] Load ontology JSON into vector store (RAG)
- [ ] Implement OntologyService (skill lookup, domain queries)
- [ ] Implement Gap Engine (deterministic scoring)
- [ ] Implement Path Generator (deterministic scaffolding)
- [ ] Implement State Inference (prerequisite expansion)
- [ ] Implement Skill Genome Service (EMA tracking)
- [ ] Implement Confusion Recovery Service
- [ ] Create all 9 agent classes with system prompts
- [ ] Create Orchestrator pipeline
- [ ] Implement all API routes (45+ endpoints)
- [ ] Add CORS configuration

### Frontend Setup
- [ ] Create React + TypeScript + Vite project
- [ ] Configure Tailwind CSS
- [ ] Set up React Router
- [ ] Set up React Query (TanStack Query)
- [ ] Create Zustand learning store
- [ ] Implement API service layer (Axios)
- [ ] Implement LLM utils (11 platforms, 2 strategies)

### Frontend Components
- [ ] DashboardPage
- [ ] LearningDashboardPage (3-column layout)
- [ ] LessonPage (AI-native + legacy rendering)
- [ ] ConceptSnapshot
- [ ] AIStrategyPanel
- [ ] PromptTemplateCard
- [ ] PromptLab (interactive)
- [ ] ImplementationTaskCard (2-step submission)
- [ ] KnowledgeCheck (quiz with feedback)
- [ ] ReflectionPrompts (accordion)
- [ ] CodeBlock
- [ ] LessonReactions (4 emoji buttons)
- [ ] ConfusionRecoveryDrawer (slide-in)
- [ ] MentorChat (floating, global)
- [ ] LLMChooser (dropdown, 11 options)
- [ ] ModuleSidebar
- [ ] SkillGapTracker
- [ ] NextLessonCard
- [ ] ProgressSummary

### Integration
- [ ] Wire CustomEvent system (`llm-changed`, `open-mentor`)
- [ ] Implement completion gating logic
- [ ] Set up React Query cache invalidation patterns
- [ ] Implement prompt persistence in mentor conversations
- [ ] Test end-to-end flow: profile → analysis → activate → lesson → complete

---

*End of Blueprint*
