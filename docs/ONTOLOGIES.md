# GenAI Skills Ontology

This document is the canonical reference for all ontology definitions used in the AI Pathway project.

---

## Table of Contents

1. [Overview](#overview)
2. [Proficiency Scale](#proficiency-scale)
3. [Architecture  --  Layers & Domains](#architecture--layers--domains)
4. [Skills by Layer and Domain](#skills-by-layer-and-domain)
   - [L.FOUNDATION  --  Foundation](#lfoundation--foundation)
   - [L.THEORY  --  Theory](#ltheory--theory)
   - [L.APPLICATION  --  Application](#lapplication--application)
   - [L.TOOLS  --  Tools](#ltools--tools)
   - [L.TECH_PREREQ  --  Technical Prerequisites](#ltech_prereq--technical-prerequisites)
   - [L.DOMAIN  --  Domain & Governance](#ldomain--domain--governance)
   - [L.SOFT  --  Strategy & Growth](#lsoft--strategy--growth)
   - [L.EMERGING  --  Emerging (2025-26)](#lemerging--emerging-202526)
5. [Roles](#roles)
6. [AI Fluency Ontology (Clusters)](#ai-fluency-ontology-clusters)
7. [Changelog](#changelog)
8. [Files Reference](#files-reference)

---

## Overview

| Version | Layers | Domains | Skills | New in Version |
|---------|--------|---------|--------|----------------|
| **v2.0** (current) | 8 | 22 | **186** | +33 skills, +1 layer, +4 domains |
| v1.0 | 7 | 18 | 153 | Initial release |

> Skills marked **`NEW`** were added in v2.0 (January-March 2026) to reflect the emerging AI capabilities landscape.

---

## Proficiency Scale

All 186 skills are rated on the same 6-level scale:

| Level | Label | Description |
|-------|-------|-------------|
| **0** | Unaware | Has not encountered this skill or concept |
| **1** | Aware | Can explain the concept; knows it exists |
| **2** | User | Can apply with guidance; knows the basics |
| **3** | Practitioner | Applies independently; adapts to context |
| **4** | Builder | Ships solutions; handles edge cases |
| **5** | Architect | Designs systems; sets standards; teaches others |

---

## Architecture  --  Layers & Domains

### Layers

| ID | Label | Color | Domains |
|----|-------|-------|---------|
| `L.FOUNDATION` | Foundation | `#10B981` | D.DIG, D.CTIC |
| `L.THEORY` | Theory | `#6366F1` | D.FND |
| `L.APPLICATION` | Application | `#06B6D4` | D.PRM, D.RAG, D.AGT, D.MOD, D.MUL, D.EVL, D.SEC, D.OPS |
| `L.TOOLS` | Tools | `#8B5CF6` | D.TOOL |
| `L.TECH_PREREQ` | Technical Prerequisites | `#F59E0B` | D.PRQ |
| `L.DOMAIN` | Domain & Governance | `#EC4899` | D.GOV, D.DOM |
| `L.SOFT` | Strategy & Growth | `#10B981` | D.PRD, D.COM, D.LRN |
| `L.EMERGING` | Emerging (2025-26) **`NEW`** | `#EC4899` | D.RSN, D.ACODE, D.COMP, D.PROTO |

### Domains

| ID | Label | Description | Layer | Skills | New |
|----|-------|-------------|-------|--------|-----|
| `D.DIG` | Digital Literacy | Core digital skills for everyone | Foundation | 8 |  --  |
| `D.CTIC` | Critical Thinking & Info Eval | Evaluating sources and claims | Foundation | 6 |  --  |
| `D.FND` | AI Literacy & Foundations | Core AI/ML concepts | Theory | 15 |  --  |
| `D.PRM` | Prompting & HITL Workflows | Effective AI interaction | Application | 12 |  --  |
| `D.RAG` | Retrieval & RAG Systems | Knowledge-grounded AI | Application | 11 | +2 |
| `D.AGT` | Agents & Orchestration | Autonomous AI systems | Application | 11 |  --  |
| `D.MOD` | Model Adaptation | Fine-tuning & customization | Application | 6 |  --  |
| `D.MUL` | Multimodal AI | Vision, audio, video AI | Application | 10 | +2 |
| `D.EVL` | Evaluation & Observability | Measuring AI quality | Application | 8 |  --  |
| `D.SEC` | Safety & Security | AI risk mitigation | Application | 7 |  --  |
| `D.OPS` | LLMOps & Deployment | Production AI systems | Application | 8 |  --  |
| `D.TOOL` | Tools & Frameworks | AI development tools | Tools | 13 | +3 |
| `D.PRQ` | Technical Prerequisites | Engineering foundations | Tech Prerequisites | 12 |  --  |
| `D.GOV` | Governance & Compliance | Policy and regulation | Domain & Governance | 8 | +2 |
| `D.DOM` | Domain Applications | Industry-specific AI | Domain & Governance | 8 |  --  |
| `D.PRD` | Product & UX | AI product management | Strategy & Growth | 8 |  --  |
| `D.COM` | Communication & Collaboration | Working with AI teams | Strategy & Growth | 6 |  --  |
| `D.LRN` | Learning & Adaptation | Continuous AI learning | Strategy & Growth | 5 |  --  |
| `D.RSN` | Extended Reasoning | Reasoning models & deep research | **Emerging** | 6 | **+6** |
| `D.ACODE` | Agentic Coding | Vibe coding, CLI agents, AI IDEs | **Emerging** | 8 | **+8** |
| `D.COMP` | Computer Use Agents | Browser & desktop automation | **Emerging** | 5 | **+5** |
| `D.PROTO` | Agent Protocols | A2A, context engineering, security | **Emerging** | 5 | **+5** |

**Total: 22 domains   186 skills   33 new**

---

## Skills by Layer and Domain

---

### L.FOUNDATION  --  Foundation

> Core digital and critical thinking skills required before engaging with AI tools.

---

#### D.DIG  --  Digital Literacy

*Core digital skills for everyone*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.DIG.001` | Web browsing & search fundamentals | 1 |
| `SK.DIG.002` | File management & cloud storage | 1 |
| `SK.DIG.003` | Basic spreadsheet operations | 1 |
| `SK.DIG.004` | Email & digital communication | 1 |
| `SK.DIG.005` | Password & account security basics | 1 |
| `SK.DIG.006` | Installing & using applications | 1 |
| `SK.DIG.007` | Copy/paste & keyboard shortcuts | 1 |
| `SK.DIG.008` | Screen sharing & video calls | 1 |

---

#### D.CTIC  --  Critical Thinking & Information Evaluation

*Evaluating sources, claims, and AI-generated content*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.CTIC.001` | Evaluating source credibility | 1 |
| `SK.CTIC.002` | Identifying misinformation patterns | 2 |
| `SK.CTIC.003` | Cross-referencing claims | 2 |
| `SK.CTIC.004` | Understanding bias in content | 2 |
| `SK.CTIC.005` | Distinguishing fact from opinion | 1 |
| `SK.CTIC.006` | Recognizing AI-generated content | 2 |

---

### L.THEORY  --  Theory

> Conceptual understanding of how AI systems work.

---

#### D.FND  --  AI Literacy & Foundations

*Core AI/ML concepts*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.FND.000` | What is AI vs traditional software | 1 |
| `SK.FND.001` | LLM fundamentals (tokens, context, prediction) | 1 |
| `SK.FND.002` | Capabilities vs limitations (hallucinations) | 1 |
| `SK.FND.003` | Model families (open vs closed) | 2 |
| `SK.FND.004` | Reasoning vs retrieval vs tools | 2 |
| `SK.FND.005` | Training data & knowledge cutoffs | 1 |
| `SK.FND.006` | Temperature & sampling basics | 2 |
| `SK.FND.010` | Transformer architecture overview | 2 |
| `SK.FND.011` | Diffusion models overview | 2 |
| `SK.FND.012` | Embeddings & semantic similarity | 2 |
| `SK.FND.013` | Multimodal model basics | 2 |
| `SK.FND.020` | Privacy basics for GenAI | 1 |
| `SK.FND.021` | IP/copyright awareness | 1 |
| `SK.FND.022` | Bias & fairness basics | 1 |
| `SK.FND.023` | Environmental impact awareness | 1 |

---

### L.APPLICATION  --  Application

> Applied AI skills for building and operating AI-powered systems.

---

#### D.PRM  --  Prompting & HITL Workflows

*Effective AI interaction and human-in-the-loop design*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.PRM.000` | Writing clear requests to AI | 1 |
| `SK.PRM.001` | Instructions + constraints + format | 2 |
| `SK.PRM.002` | Few-shot examples | 2 |
| `SK.PRM.003` | Prompt debugging & iteration | 3 |
| `SK.PRM.004` | Role & persona prompting | 2 |
| `SK.PRM.005` | Chain-of-thought prompting | 2 |
| `SK.PRM.006` | Breaking complex tasks into steps | 2 |
| `SK.PRM.010` | JSON/schema outputs | 3 |
| `SK.PRM.011` | Rubrics as prompts | 3 |
| `SK.PRM.020` | Draft -> critique -> revise | 3 |
| `SK.PRM.021` | Grounding & citations | 3 |
| `SK.PRM.022` | ReAct-style patterns | 4 |

---

#### D.RAG  --  Retrieval & RAG Systems

*Knowledge-grounded AI and retrieval-augmented generation*

| ID | Skill | Prereq Level | Status |
|----|-------|-------------|--------|
| `SK.RAG.000` | What is RAG and why use it | 1 | |
| `SK.RAG.001` | Query rewriting | 3 | |
| `SK.RAG.002` | Chunking strategies | 3 | |
| `SK.RAG.003` | Hybrid retrieval (vector + keyword) | 3 | |
| `SK.RAG.010` | Reranking & scoring | 3 | |
| `SK.RAG.011` | Context budgeting | 4 | |
| `SK.RAG.012` | Lost in the middle mitigation | 4 | |
| `SK.RAG.020` | Faithfulness evaluation | 4 | |
| `SK.RAG.021` | Golden sets & regression testing | 4 | |
| `SK.RAG.022` | Agentic RAG patterns | 4 | **NEW** |
| `SK.RAG.023` | Temporal & time-aware RAG | 3 | **NEW** |

---

#### D.AGT  --  Agents & Orchestration

*Autonomous AI systems, tool use, and multi-agent patterns*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.AGT.000` | What are AI agents | 1 |
| `SK.AGT.001` | Tool definitions & validation | 3 |
| `SK.AGT.002` | Error handling & retries | 3 |
| `SK.AGT.003` | State & memory management | 3 |
| `SK.AGT.010` | Single-agent loops | 4 |
| `SK.AGT.011` | Multi-agent patterns | 4 |
| `SK.AGT.012` | Graph-based orchestration | 5 |
| `SK.AGT.020` | MCP protocol concepts | 3 |
| `SK.AGT.021` | Agent permissions (least privilege) | 4 |
| `SK.AGT.030` | Guardrails & approval gates | 4 |
| `SK.AGT.031` | Agent auditability | 4 |

---

#### D.MOD  --  Model Adaptation

*Fine-tuning, customization, and synthetic data*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.MOD.000` | When to customize vs use off-the-shelf | 2 |
| `SK.MOD.001` | Prompt vs fine-tune decision | 3 |
| `SK.MOD.002` | Data requirements for tuning | 3 |
| `SK.MOD.010` | Instruction tuning basics | 3 |
| `SK.MOD.011` | PEFT/LoRA concepts | 4 |
| `SK.MOD.012` | Synthetic data generation | 4 |

---

#### D.MUL  --  Multimodal AI

*Vision, audio, video, and document AI*

| ID | Skill | Prereq Level | Status |
|----|-------|-------------|--------|
| `SK.MUL.000` | Types of multimodal AI | 1 | |
| `SK.MUL.001` | Image-to-text extraction | 2 | |
| `SK.MUL.002` | Image generation prompting | 2 | |
| `SK.MUL.003` | Image generation QA | 3 | |
| `SK.MUL.010` | Speech-to-text & summarization | 2 | |
| `SK.MUL.011` | Video understanding | 3 | |
| `SK.MUL.012` | Text-to-speech applications | 2 | |
| `SK.MUL.013` | Document/PDF understanding | 2 | |
| `SK.MUL.014` | Native audio/video generation (Kling, Sora, Veo) | 2 | **NEW** |
| `SK.MUL.015` | Multimodal RAG | 4 | **NEW** |

---

#### D.EVL  --  Evaluation & Observability

*Measuring, testing, and monitoring AI quality*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.EVL.000` | Why AI evaluation matters | 1 |
| `SK.EVL.001` | Eval types (offline/online/red team) | 2 |
| `SK.EVL.002` | LLM-as-judge patterns | 3 |
| `SK.EVL.010` | Tracing & observability | 3 |
| `SK.EVL.011` | Quality dashboards & alerts | 4 |
| `SK.EVL.020` | Prompt unit tests | 3 |
| `SK.EVL.021` | Release gates & rollback | 4 |
| `SK.EVL.022` | A/B testing for AI | 4 |

---

#### D.SEC  --  Safety & Security

*AI threat landscape, prompt injection, and agent security*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.SEC.000` | AI security threat landscape | 1 |
| `SK.SEC.001` | Prompt injection mitigation | 3 |
| `SK.SEC.002` | Data leakage prevention | 3 |
| `SK.SEC.003` | Output security (XSS, injection) | 3 |
| `SK.SEC.010` | Agent permission design | 4 |
| `SK.SEC.011` | Tool sandboxing | 4 |
| `SK.SEC.012` | Red teaming basics | 3 |

---

#### D.OPS  --  LLMOps & Deployment

*Production AI systems, cost, latency, and reliability*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.OPS.000` | What is LLMOps | 1 |
| `SK.OPS.001` | Latency drivers & optimization | 3 |
| `SK.OPS.002` | Cost modeling & token budgeting | 3 |
| `SK.OPS.010` | Caching, batching, streaming | 4 |
| `SK.OPS.011` | Model routing strategies | 4 |
| `SK.OPS.020` | SLOs/SLAs & incident response | 4 |
| `SK.OPS.021` | Security reviews & deployment gates | 4 |
| `SK.OPS.022` | Versioning prompts & models | 3 |

---

### L.TOOLS  --  Tools

> Familiarity with the AI tooling ecosystem.

---

#### D.TOOL  --  Tools & Frameworks

*AI development tools, platforms, and infrastructure*

| ID | Skill | Prereq Level | Status |
|----|-------|-------------|--------|
| `SK.TOOL.000` | AI tool landscape overview | 1 | |
| `SK.TOOL.001` | ChatGPT / Claude / Gemini usage | 1 | |
| `SK.TOOL.002` | AI coding assistants (Copilot, Claude Code) | 2 | |
| `SK.TOOL.003` | Image generation tools (Midjourney, DALL-E) | 2 | |
| `SK.TOOL.010` | LangChain / LlamaIndex concepts | 3 | |
| `SK.TOOL.011` | Hugging Face ecosystem | 3 | |
| `SK.TOOL.020` | API key management | 2 | |
| `SK.TOOL.021` | Provider selection criteria | 3 | |
| `SK.TOOL.030` | Docker for AI apps | 3 | |
| `SK.TOOL.031` | Kubernetes awareness | 4 | |
| `SK.TOOL.032` | Claude Code & CLI coding agents | 3 | **NEW** |
| `SK.TOOL.033` | Agentic IDEs (Cursor, Windsurf) | 2 | **NEW** |
| `SK.TOOL.034` | Deep research tools (Perplexity, ChatGPT DR) | 2 | **NEW** |

---

### L.TECH_PREREQ  --  Technical Prerequisites

> Engineering foundations required for builder and architect roles.

---

#### D.PRQ  --  Technical Prerequisites

*Software engineering fundamentals for AI builders*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.PRQ.000` | Command line basics | 1 |
| `SK.PRQ.001` | Version control (Git basics) | 2 |
| `SK.PRQ.010` | Python basics | 2 |
| `SK.PRQ.011` | Data handling (Pandas/NumPy) | 2 |
| `SK.PRQ.012` | JavaScript/TypeScript basics | 2 |
| `SK.PRQ.013` | SQL fundamentals | 2 |
| `SK.PRQ.020` | REST API basics | 2 |
| `SK.PRQ.021` | Authentication (OAuth, tokens) | 2 |
| `SK.PRQ.022` | Backend service fundamentals | 3 |
| `SK.PRQ.030` | Cloud primitives (compute, storage) | 2 |
| `SK.PRQ.031` | Secrets management | 3 |
| `SK.PRQ.032` | CI/CD concepts | 3 |

---

### L.DOMAIN  --  Domain & Governance

> Policy, compliance, and industry-specific AI application.

---

#### D.GOV  --  Governance & Compliance

*AI regulation, risk, and policy controls*

| ID | Skill | Prereq Level | Status |
|----|-------|-------------|--------|
| `SK.GOV.000` | AI governance fundamentals | 1 | |
| `SK.GOV.001` | AI risk framing | 2 | |
| `SK.GOV.002` | Policy to controls mapping | 3 | |
| `SK.GOV.010` | AI regulations landscape (EU AI Act) | 2 | |
| `SK.GOV.020` | PII/PHI handling & retention | 2 | |
| `SK.GOV.021` | Data minimization & anonymization | 3 | |
| `SK.GOV.022` | AI-generated content disclosure | 2 | **NEW** |
| `SK.GOV.023` | EU AI Act enforcement readiness | 3 | **NEW** |

---

#### D.DOM  --  Domain Applications

*Industry-specific AI risk and design considerations*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.DOM.HC.001` | Healthcare: Clinical risk awareness | 3 |
| `SK.DOM.HC.002` | Healthcare: Evidence synthesis | 3 |
| `SK.DOM.LGL.001` | Legal: Disclaimer & advice boundaries | 3 |
| `SK.DOM.LGL.002` | Legal: Hallucination eval frameworks | 4 |
| `SK.DOM.FIN.001` | Finance: Numerical auditability | 4 |
| `SK.DOM.EDU.001` | Education: Learning design with AI | 2 |
| `SK.DOM.MKT.001` | Marketing: Content generation ethics | 2 |
| `SK.DOM.HR.001` | HR: AI in hiring considerations | 2 |

---

### L.SOFT  --  Strategy & Growth

> Product, communication, and continuous learning skills.

---

#### D.PRD  --  Product & UX

*AI product management and user experience design*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.PRD.000` | AI product thinking basics | 1 |
| `SK.PRD.001` | Use-case selection & prioritization | 2 |
| `SK.PRD.002` | Workflow mapping | 3 |
| `SK.PRD.010` | Explainability UX design | 3 |
| `SK.PRD.011` | Feedback loop design | 3 |
| `SK.PRD.020` | AI enablement & training strategy | 3 |
| `SK.PRD.021` | Stakeholder management | 3 |
| `SK.PRD.022` | ROI measurement for AI | 3 |

---

#### D.COM  --  Communication & Collaboration

*Explaining, documenting, and collaborating on AI work*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.COM.001` | Explaining AI to non-technical audiences | 2 |
| `SK.COM.002` | Writing AI project proposals | 3 |
| `SK.COM.003` | Facilitating AI workshops | 3 |
| `SK.COM.004` | Managing AI expectations | 2 |
| `SK.COM.005` | Cross-functional AI collaboration | 3 |
| `SK.COM.006` | AI documentation best practices | 3 |

---

#### D.LRN  --  Learning & Adaptation

*Keeping pace with rapid AI change*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.LRN.001` | Keeping up with AI developments | 1 |
| `SK.LRN.002` | Evaluating new AI tools | 2 |
| `SK.LRN.003` | Building personal AI workflows | 2 |
| `SK.LRN.004` | Teaching others AI skills | 3 |
| `SK.LRN.005` | Experimenting safely with AI | 2 |

---

### L.EMERGING  --  Emerging (2025-26)

> New skills reflecting the frontier capabilities of 2025-2026: reasoning models, agentic coding, computer-use agents, and agent communication protocols. All skills in this layer are **NEW** in v2.0.

---

#### D.RSN  --  Extended Reasoning

*Reasoning models, test-time compute, and deep research agents*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.RSN.000` | What are reasoning models (o3, R1, extended thinking) | 1 |
| `SK.RSN.001` | Extended thinking & test-time compute | 2 |
| `SK.RSN.002` | Reasoning model selection & routing | 3 |
| `SK.RSN.003` | Deep research agents | 3 |
| `SK.RSN.004` | Chain-of-thought verification | 3 |
| `SK.RSN.005` | Inference cost budgeting for reasoning models | 3 |

---

#### D.ACODE  --  Agentic Coding

*Vibe coding, CLI agents, AI IDEs, and AI-assisted development*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.ACODE.000` | Vibe coding & natural language development | 1 |
| `SK.ACODE.001` | CLI coding agent usage (Claude Code) | 2 |
| `SK.ACODE.002` | Agentic IDE mastery (Cursor, Windsurf) | 2 |
| `SK.ACODE.003` | AI-assisted code review | 2 |
| `SK.ACODE.004` | AI-generated test suites | 3 |
| `SK.ACODE.005` | Autonomous debugging with AI | 3 |
| `SK.ACODE.006` | Code architecture with AI | 4 |
| `SK.ACODE.007` | AI code quality & slop prevention | 3 |

---

#### D.COMP  --  Computer Use Agents

*Browser and desktop automation via AI agents*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.COMP.000` | Computer use agent concepts | 1 |
| `SK.COMP.001` | Browser automation with AI | 3 |
| `SK.COMP.002` | Desktop automation with AI | 3 |
| `SK.COMP.003` | Operator-style task delegation | 3 |
| `SK.COMP.004` | Computer use safety & governance | 3 |

---

#### D.PROTO  --  Agent Protocols

*A2A protocol, context engineering, and multi-protocol agent systems*

| ID | Skill | Prereq Level |
|----|-------|-------------|
| `SK.PROTO.000` | Agent-to-Agent (A2A) protocol | 2 |
| `SK.PROTO.001` | Agent cards & capability discovery | 2 |
| `SK.PROTO.002` | Context engineering | 3 |
| `SK.PROTO.003` | Multi-protocol agent systems (MCP + A2A) | 4 |
| `SK.PROTO.004` | Agent protocol security | 3 |

---

## Roles

Five role archetypes define typical learning paths through the ontology:

| ID | Label | Key Domains |
|----|-------|-------------|
| `ROLE.BEGINNER` | AI-Curious Beginner | D.DIG, D.CTIC, D.FND, D.PRM |
| `ROLE.KNOWLEDGE` | Knowledge Worker | D.DIG, D.CTIC, D.FND, D.PRM, D.MUL, D.COM, D.LRN |
| `ROLE.AI_PM` | AI Product Manager | D.PRD, D.PRM, D.EVL, D.GOV, D.COM, D.DOM |
| `ROLE.LLM_ENGINEER` | LLM Engineer | D.PRQ, D.PRM, D.RAG, D.AGT, D.EVL, D.SEC, D.OPS, D.TOOL, D.ACODE |
| `ROLE.AI_ARCHITECT` | AI Architect | D.AGT, D.EVL, D.SEC, D.GOV, D.OPS, D.MOD, D.RSN, D.PROTO |

---

## AI Fluency Ontology (Clusters)

A secondary, more focused ontology (8 clusters, ~95 skills) targeting practical LLM literacy. Used in the Skill Gap Coach product.

### Clusters

| Cluster | Description |
|---------|-------------|
| Foundations | Core LLM architecture and model fundamentals |
| Prompting | Prompt engineering techniques and optimization |
| RAG | Retrieval-Augmented Generation systems |
| Agentic | AI agents, orchestration, and workflows |
| MCP | Model Context Protocol development |
| Eval | Evaluation, testing, and observability |
| Responsible | Safety, ethics, and responsible AI |
| Multimodal | Vision, audio, video, and specialty models |

### Skills by Cluster

#### Foundations

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `LLM_Architecture` | LLM Architecture (Transformers, Scaling) |  --  |
| `Tokens_Context` | Tokens & Context Windows | LLM_Architecture |
| `Hallucinations_Limits` | Hallucinations & Failure Modes | LLM_Architecture |
| `Model_Selection` | Model Selection (SLM vs LLM, Open vs Closed) | LLM_Architecture |
| `Compute_Economics` | Compute Costs & Latency | LLM_Architecture |
| `Diffusion_Basics` | Diffusion Model Fundamentals |  --  |

#### Prompting

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Few_Shot_Prompting` | Few-Shot & Zero-Shot Prompting | Tokens_Context |
| `Role_Persona` | Role & Persona Engineering | Few_Shot_Prompting |
| `Structured_Outputs` | Structured Outputs (JSON, XML, Schemas) | Few_Shot_Prompting |
| `Iterative_Refinement` | Iterative Prompt Refinement | Few_Shot_Prompting |
| `Context_Stuffing` | Context Window Management (Long Context) | Tokens_Context |
| `Prompt_Compression` | Prompt Compression & Optimization | Tokens_Context |
| `Negative_Prompting` | Negative Prompting & Constraints | Few_Shot_Prompting |

#### RAG

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Embeddings_Vectors` | Embeddings & Vector Theory | LLM_Architecture |
| `Chunking_Strategies` | Semantic & Recursive Chunking | Embeddings_Vectors |
| `Vector_Databases` | Vector Database Operations | Embeddings_Vectors |
| `Retrieval_Heuristics` | Advanced Retrieval (BM25, Hybrid Search) | Embeddings_Vectors |
| `Reranking` | Reranking & Cross-Encoders | Retrieval_Heuristics |
| `Grounding_Citations` | Groundedness & Automated Citations | Retrieval_Heuristics |
| `Graph_RAG` | Knowledge Graphs & GraphRAG | Retrieval_Heuristics |

#### Agentic

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Tool_Calling` | Tool & Function Calling | Structured_Outputs |
| `Agent_Orchestration` | Agent Orchestration (Multi-agent) | Tool_Calling |
| `Planning_Execution` | Planning & Execution Loops | Agent_Orchestration |
| `State_Management` | Memory & State Persistence | Agent_Orchestration |
| `HITL` | Human-In-The-Loop Workflows | Agent_Orchestration |
| `Self_Reflection` | Self-Reflection & Error Correction | Planning_Execution |
| `Agentic_MCP` | Agentic use of MCP Tools | Tool_Calling |

#### MCP

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `MCP_Architecture` | MCP Architecture (Clients/Servers) | Tool_Calling |
| `MCP_Server_Dev` | MCP Server Development | MCP_Architecture |
| `MCP_Resources` | MCP Resources & Prompts | MCP_Architecture |
| `MCP_Tools` | Building Custom MCP Tools | MCP_Architecture |
| `MCP_Security` | MCP Security & Sandboxing | MCP_Architecture |

#### Eval

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Prompt_Unit_Tests` | Prompt Unit Testing | Structured_Outputs |
| `LLM_As_Judge` | LLM-As-Judge Scoring | Prompt_Unit_Tests |
| `Golden_Datasets` | Golden Datasets & Benchmarking | LLM_As_Judge |
| `Monitoring_Drift` | Monitoring, Drift & Logging | Golden_Datasets |
| `AB_Testing` | A/B Testing Prompts & Models | LLM_As_Judge |
| `Model_Registry` | Model & Prompt Version Registry | Monitoring_Drift |

#### Responsible

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Bias_Fairness` | Bias, Fairness & Toxicity Mitigation | LLM_Architecture |
| `Prompt_Injection_Safety` | Prompt Injection & Jailbreak Defense | Few_Shot_Prompting |
| `Privacy_PII` | Data Privacy & PII Scrubbing | LLM_Architecture |
| `AI_Explainability` | Explainability & Transparency | LLM_Architecture |
| `Copyright_IP` | AI Copyright & IP Ethics | LLM_Architecture |
| `Red_Teaming` | Adversarial Red Teaming | Prompt_Injection_Safety |

#### Multimodal

| ID | Skill | Prerequisites |
|----|-------|---------------|
| `Multimodal_Literacy` | Vision/Audio Interaction Literacy | LLM_Architecture |
| `Image_Editing` | Image Generation & Inpainting | Diffusion_Basics |
| `Video_Gen` | Text-to-Video Generation Literacy | Diffusion_Basics |
| `Speech_Synthesis` | Speech Synthesis & Voice Cloning | Multimodal_Literacy |
| `Fine_Tuning_Concepts` | Parameter Efficient Fine-Tuning (LoRA) | LLM_Architecture |

---

## Changelog

### v2.0  --  March 2026

**New Layer:**
- `L.EMERGING`  --  Emerging (2025-26)

**New Domains (4):**
- `D.RSN`  --  Extended Reasoning (6 skills)
- `D.ACODE`  --  Agentic Coding (8 skills)
- `D.COMP`  --  Computer Use Agents (5 skills)
- `D.PROTO`  --  Agent Protocols (5 skills)

**New Skills in Existing Domains (15):**
- `D.RAG`: SK.RAG.022 (Agentic RAG patterns), SK.RAG.023 (Temporal & time-aware RAG)
- `D.MUL`: SK.MUL.014 (Native audio/video generation), SK.MUL.015 (Multimodal RAG)
- `D.TOOL`: SK.TOOL.032 (Claude Code & CLI coding agents), SK.TOOL.033 (Agentic IDEs), SK.TOOL.034 (Deep research tools)
- `D.GOV`: SK.GOV.022 (AI-generated content disclosure), SK.GOV.023 (EU AI Act enforcement readiness)

**Total new skills: 33**

### v1.0  --  December 2025

- Initial release: 7 layers, 18 domains, 153 skills

---

## Files Reference

| File | Description |
|------|-------------|
| [ai-fluency-assessment.html](ai-fluency-assessment.html) | Self-assessment tool  --  all 186 skills with 6-level rubrics, interactive rating UI |
| [ontology_chart_v2.html](ontology_chart_v2.html) | Interactive ontology chart v2.0  --  D3 mind map, force graph, layers, domains, stats |
| [ontology_chart.html](ontology_chart.html) | Original ontology chart v1.0  --  D3 mind map and multi-view visualization |
| [genai-skills-ontology.json](genai-skills-ontology.json) | Machine-readable ontology data (v1.0.0) |
| [genai-ontology-map.tsx](genai-ontology-map.tsx) | React/TSX interactive visualization component |
| [skill-rubrics.js](skill-rubrics.js) | Original rubric definitions (153 skills ?? 6 levels)  --  superseded by inline rubrics in assessment |
| [skillgap-coach/src/lib/full-ontology.ts](skillgap-coach/src/lib/full-ontology.ts) | TypeScript ontology module for Skill Gap Coach |
| [skillgap-coach/genai-skills-ontology.json](skillgap-coach/genai-skills-ontology.json) | Ontology JSON for Skill Gap Coach |
