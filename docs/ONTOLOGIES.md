# GenAI Skills Ontologies

This document provides a comprehensive reference of all ontology definitions used in the AI Pathway project.

---

## Table of Contents

1. [Overview](#overview)
2. [Primary Ontology (v1.0.0)](#primary-ontology-v100)
   - [Proficiency Scale](#proficiency-scale)
   - [Layers](#layers)
   - [Domains](#domains)
   - [Skills by Domain](#skills-by-domain)
   - [Roles](#roles)
3. [AI Fluency Ontology (V2)](#ai-fluency-ontology-v2)
   - [Clusters](#clusters)
   - [Skills by Cluster](#skills-by-cluster)
4. [Ontology Files Reference](#ontology-files-reference)

---

## Overview

The project contains two complementary ontology systems:

| Ontology | Domains/Clusters | Skills | Focus |
|----------|------------------|--------|-------|
| **Primary (v1.0.0)** | 18 domains, 7 layers | 153+ | Comprehensive GenAI skill mapping |
| **AI Fluency (V2)** | 8 clusters | 95 | Practical AI literacy for LLM applications |

---

## Primary Ontology (v1.0.0)

**Export Date:** 2025-12-28
**Total Domains:** 18
**Total Skills:** 153

### Proficiency Scale

| Level | Label | Description |
|-------|-------|-------------|
| 0 | Unaware | Has not heard of it |
| 1 | Aware | Can explain basics |
| 2 | User | Can apply with help |
| 3 | Practitioner | Can adapt independently |
| 4 | Builder | Ships solutions |
| 5 | Architect | Designs systems |

### Layers

| ID | Label | Color | Domains |
|----|-------|-------|---------|
| L.FOUNDATION | Foundation | #22c55e | D.DIG, D.TIC |
| L.THEORY | Theory | #6366f1 | D.FND |
| L.APPLICATION | Application | #06b6d4 | D.PRM, D.RAG, D.AGT, D.MOD, D.MUL, D.EVL, D.SEC, D.OPS |
| L.TOOLS | Tools | #10b981 | D.TOOL |
| L.TECH_PREREQ | Tech Prerequisites | #f59e0b | D.PRQ |
| L.DOMAIN | Domain | #ec4899 | D.GOV, D.DOM |
| L.SOFT | Soft/Strategy | #8b5cf6 | D.PRD, D.COM, D.LRN |

### Domains

| ID | Label | Description | Layer | Skills |
|----|-------|-------------|-------|--------|
| D.DIG | Digital Literacy | Basic digital skills for everyone | Foundation | 8 |
| D.TIC | Critical Thinking & Info Eval | Evaluating sources and claims | Foundation | 0 |
| D.FND | AI Literacy & Foundations | Core AI/ML concepts | Theory | 15 |
| D.PRM | Prompting & HITL Workflows | Effective AI interaction | Application | 12 |
| D.RAG | Retrieval & RAG Systems | Knowledge-grounded AI | Application | 9 |
| D.AGT | Agents & Orchestration | Autonomous AI systems | Application | 11 |
| D.MOD | Model Adaptation | Fine-tuning & customization | Application | 6 |
| D.MUL | Multimodal AI | Vision, audio, video AI | Application | 8 |
| D.EVL | Evaluation & Observability | Measuring AI quality | Application | 8 |
| D.SEC | Safety & Security | AI risk mitigation | Application | 7 |
| D.OPS | LLMOps & Deployment | Production AI systems | Application | 8 |
| D.TOOL | Tools & Frameworks | AI development tools | Tools | 10 |
| D.PRQ | Technical Prerequisites | Engineering foundations | Tech Prerequisites | 12 |
| D.GOV | Governance & Compliance | Policy and regulation | Domain | 6 |
| D.DOM | Domain Applications | Industry-specific AI | Domain | 8 |
| D.PRD | Product & UX | AI product management | Soft/Strategy | 8 |
| D.COM | Communication & Collaboration | Working with AI teams | Soft/Strategy | 6 |
| D.LRN | Learning & Adaptation | Continuous AI learning | Soft/Strategy | 5 |

### Skills by Domain

#### D.DIG - Digital Literacy

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.DIG.001 | Web browsing & search fundamentals | 1 | - |
| SK.DIG.002 | File management & cloud storage | 1 | - |
| SK.DIG.003 | Basic spreadsheet operations | 1 | - |
| SK.DIG.004 | Email & digital communication | 1 | - |
| SK.DIG.005 | Password & account security basics | 1 | - |
| SK.DIG.006 | Installing & using applications | 1 | - |
| SK.DIG.007 | Copy/paste & keyboard shortcuts | 1 | - |
| SK.DIG.008 | Screen sharing & video calls | 1 | - |

#### D.CTIC - Critical Thinking & Information Evaluation

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.CTIC.001 | Evaluating source credibility | 1 | - |
| SK.CTIC.002 | Identifying misinformation patterns | 2 | SK.CTIC.001 |
| SK.CTIC.003 | Cross-referencing claims | 2 | SK.CTIC.001 |
| SK.CTIC.004 | Understanding bias in content | 2 | SK.CTIC.001 |
| SK.CTIC.005 | Distinguishing fact from opinion | 1 | - |
| SK.CTIC.006 | Recognizing AI-generated content | 2 | SK.FND.001 |

#### D.FND - AI Literacy & Foundations

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.FND.000 | What is AI vs traditional software | 1 | - |
| SK.FND.001 | LLM fundamentals (tokens, context, prediction) | 1 | SK.FND.000 |
| SK.FND.002 | Capabilities vs limitations (hallucinations) | 1 | SK.FND.001 |
| SK.FND.003 | Model families (open vs closed) | 2 | SK.FND.001 |
| SK.FND.004 | Reasoning vs retrieval vs tools | 2 | SK.FND.002 |
| SK.FND.005 | Training data & knowledge cutoffs | 1 | SK.FND.001 |
| SK.FND.006 | Temperature & sampling basics | 2 | SK.FND.001 |
| SK.FND.010 | Transformer architecture overview | 2 | SK.FND.001 |
| SK.FND.011 | Diffusion models overview | 2 | SK.FND.000 |
| SK.FND.012 | Embeddings & semantic similarity | 2 | SK.FND.001 |
| SK.FND.013 | Multimodal model basics | 2 | SK.FND.001 |
| SK.FND.020 | Privacy basics for GenAI | 1 | - |
| SK.FND.021 | IP/copyright awareness | 1 | - |
| SK.FND.022 | Bias & fairness basics | 1 | SK.FND.002 |
| SK.FND.023 | Environmental impact awareness | 1 | SK.FND.000 |

#### D.PRM - Prompting & HITL Workflows

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.PRM.000 | Writing clear requests to AI | 1 | SK.FND.001 |
| SK.PRM.001 | Instructions + constraints + format | 2 | SK.PRM.000 |
| SK.PRM.002 | Few-shot examples | 2 | SK.PRM.001 |
| SK.PRM.003 | Prompt debugging & iteration | 3 | SK.PRM.001 |
| SK.PRM.004 | Role & persona prompting | 2 | SK.PRM.001 |
| SK.PRM.005 | Chain-of-thought prompting | 2 | SK.PRM.001 |
| SK.PRM.006 | Breaking complex tasks into steps | 2 | SK.PRM.001 |
| SK.PRM.010 | JSON/schema outputs | 3 | SK.PRM.001, SK.PRQ.020 |
| SK.PRM.011 | Rubrics as prompts | 3 | SK.PRM.001 |
| SK.PRM.020 | Draft -> critique -> revise | 3 | SK.PRM.001 |
| SK.PRM.021 | Grounding & citations | 3 | SK.FND.002 |
| SK.PRM.022 | ReAct-style patterns | 4 | SK.PRM.010, SK.FND.004 |

#### D.RAG - Retrieval & RAG Systems

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.RAG.000 | What is RAG and why use it | 1 | SK.FND.004 |
| SK.RAG.001 | Query rewriting | 3 | SK.PRM.001 |
| SK.RAG.002 | Chunking strategies | 3 | SK.FND.012 |
| SK.RAG.003 | Hybrid retrieval (vector + keyword) | 3 | SK.FND.012 |
| SK.RAG.010 | Reranking & scoring | 3 | SK.RAG.003 |
| SK.RAG.011 | Context budgeting | 4 | SK.FND.001, SK.RAG.003 |
| SK.RAG.012 | Lost in the middle mitigation | 4 | SK.RAG.011 |
| SK.RAG.020 | Faithfulness evaluation | 4 | SK.PRM.021, SK.RAG.010 |
| SK.RAG.021 | Golden sets & regression testing | 4 | SK.RAG.020 |

#### D.AGT - Agents & Orchestration

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.AGT.000 | What are AI agents | 1 | SK.FND.004 |
| SK.AGT.001 | Tool definitions & validation | 3 | SK.PRM.010, SK.PRQ.020 |
| SK.AGT.002 | Error handling & retries | 3 | SK.AGT.001, SK.PRQ.021 |
| SK.AGT.003 | State & memory management | 3 | SK.AGT.001 |
| SK.AGT.010 | Single-agent loops | 4 | SK.AGT.001, SK.EVL.020 |
| SK.AGT.011 | Multi-agent patterns | 4 | SK.AGT.010 |
| SK.AGT.012 | Graph-based orchestration | 5 | SK.AGT.011, SK.PRQ.022 |
| SK.AGT.020 | MCP protocol concepts | 3 | SK.AGT.001 |
| SK.AGT.021 | Agent permissions (least privilege) | 4 | SK.SEC.010, SK.AGT.001 |
| SK.AGT.030 | Guardrails & approval gates | 4 | SK.SEC.010, SK.EVL.001 |
| SK.AGT.031 | Agent auditability | 4 | SK.EVL.010 |

#### D.MOD - Model Adaptation

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.MOD.000 | When to customize vs use off-the-shelf | 2 | SK.FND.003 |
| SK.MOD.001 | Prompt vs fine-tune decision | 3 | SK.FND.003, SK.PRM.001 |
| SK.MOD.002 | Data requirements for tuning | 3 | SK.MOD.001, SK.PRQ.030 |
| SK.MOD.010 | Instruction tuning basics | 3 | SK.MOD.001 |
| SK.MOD.011 | PEFT/LoRA concepts | 4 | SK.MOD.010 |
| SK.MOD.012 | Synthetic data generation | 4 | SK.MOD.002, SK.EVL.001 |

#### D.MUL - Multimodal AI

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.MUL.000 | Types of multimodal AI | 1 | SK.FND.000 |
| SK.MUL.001 | Image-to-text extraction | 2 | SK.PRM.010 |
| SK.MUL.002 | Image generation prompting | 2 | SK.PRM.001 |
| SK.MUL.003 | Image generation QA | 3 | SK.MUL.002 |
| SK.MUL.010 | Speech-to-text & summarization | 2 | SK.PRM.001 |
| SK.MUL.011 | Video understanding | 3 | SK.PRM.021 |
| SK.MUL.012 | Text-to-speech applications | 2 | SK.FND.000 |
| SK.MUL.013 | Document/PDF understanding | 2 | SK.PRM.001 |

#### D.EVL - Evaluation & Observability

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.EVL.000 | Why AI evaluation matters | 1 | SK.FND.002 |
| SK.EVL.001 | Eval types (offline/online/red team) | 2 | SK.FND.002 |
| SK.EVL.002 | LLM-as-judge patterns | 3 | SK.PRM.011, SK.EVL.001 |
| SK.EVL.010 | Tracing & observability | 3 | SK.PRQ.022 |
| SK.EVL.011 | Quality dashboards & alerts | 4 | SK.EVL.010, SK.EVL.001 |
| SK.EVL.020 | Prompt unit tests | 3 | SK.PRM.003 |
| SK.EVL.021 | Release gates & rollback | 4 | SK.EVL.011, SK.OPS.020 |
| SK.EVL.022 | A/B testing for AI | 4 | SK.EVL.001 |

#### D.SEC - Safety & Security

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.SEC.000 | AI security threat landscape | 1 | SK.FND.002 |
| SK.SEC.001 | Prompt injection mitigation | 3 | SK.RAG.020, SK.AGT.001 |
| SK.SEC.002 | Data leakage prevention | 3 | SK.FND.020 |
| SK.SEC.003 | Output security (XSS, injection) | 3 | SK.PRQ.021 |
| SK.SEC.010 | Agent permission design | 4 | SK.AGT.001 |
| SK.SEC.011 | Tool sandboxing | 4 | SK.SEC.010, SK.PRQ.022 |
| SK.SEC.012 | Red teaming basics | 3 | SK.EVL.001 |

#### D.OPS - LLMOps & Deployment

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.OPS.000 | What is LLMOps | 1 | SK.FND.000 |
| SK.OPS.001 | Latency drivers & optimization | 3 | SK.AGT.002, SK.RAG.011 |
| SK.OPS.002 | Cost modeling & token budgeting | 3 | SK.OPS.001 |
| SK.OPS.010 | Caching, batching, streaming | 4 | SK.OPS.002, SK.PRQ.022 |
| SK.OPS.011 | Model routing strategies | 4 | SK.OPS.010 |
| SK.OPS.020 | SLOs/SLAs & incident response | 4 | SK.EVL.010 |
| SK.OPS.021 | Security reviews & deployment gates | 4 | SK.SEC.010, SK.EVL.021 |
| SK.OPS.022 | Versioning prompts & models | 3 | SK.PRM.003 |

#### D.TOOL - Tools & Frameworks

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.TOOL.000 | AI tool landscape overview | 1 | SK.FND.000 |
| SK.TOOL.001 | ChatGPT/Claude/Gemini usage | 1 | SK.FND.001 |
| SK.TOOL.002 | AI coding assistants (Copilot) | 2 | SK.PRQ.010 |
| SK.TOOL.003 | Image generation tools (Midjourney, DALL-E) | 2 | SK.MUL.002 |
| SK.TOOL.010 | LangChain/LlamaIndex concepts | 3 | SK.RAG.001, SK.AGT.001 |
| SK.TOOL.011 | Hugging Face ecosystem | 3 | SK.FND.010 |
| SK.TOOL.020 | API key management | 2 | SK.PRQ.021 |
| SK.TOOL.021 | Provider selection criteria | 3 | SK.FND.003, SK.GOV.001 |
| SK.TOOL.030 | Docker for AI apps | 3 | SK.PRQ.022 |
| SK.TOOL.031 | Kubernetes awareness | 4 | SK.TOOL.030 |

#### D.PRQ - Technical Prerequisites

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.PRQ.000 | Command line basics | 1 | - |
| SK.PRQ.001 | Version control (Git basics) | 2 | SK.PRQ.000 |
| SK.PRQ.010 | Python basics | 2 | SK.PRQ.000 |
| SK.PRQ.011 | Data handling (Pandas/NumPy) | 2 | SK.PRQ.010 |
| SK.PRQ.012 | JavaScript/TypeScript basics | 2 | - |
| SK.PRQ.013 | SQL fundamentals | 2 | - |
| SK.PRQ.020 | REST API basics | 2 | - |
| SK.PRQ.021 | Authentication (OAuth, tokens) | 2 | SK.PRQ.020 |
| SK.PRQ.022 | Backend service fundamentals | 3 | SK.PRQ.020 |
| SK.PRQ.030 | Cloud primitives (compute, storage) | 2 | - |
| SK.PRQ.031 | Secrets management | 3 | SK.PRQ.030, SK.PRQ.021 |
| SK.PRQ.032 | CI/CD concepts | 3 | SK.PRQ.001 |

#### D.GOV - Governance & Compliance

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.GOV.000 | AI governance fundamentals | 1 | SK.FND.002 |
| SK.GOV.001 | AI risk framing | 2 | SK.FND.002, SK.FND.022 |
| SK.GOV.002 | Policy to controls mapping | 3 | SK.AGT.030, SK.EVL.010 |
| SK.GOV.010 | AI regulations landscape (EU AI Act) | 2 | SK.GOV.000 |
| SK.GOV.020 | PII/PHI handling & retention | 2 | SK.FND.020 |
| SK.GOV.021 | Data minimization & anonymization | 3 | SK.GOV.020 |

#### D.DOM - Domain Applications

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.DOM.HC.001 | Healthcare: Clinical risk awareness | 3 | SK.GOV.001, SK.PRM.021 |
| SK.DOM.HC.002 | Healthcare: Evidence synthesis | 3 | SK.RAG.020 |
| SK.DOM.LGL.001 | Legal: Disclaimer & advice boundaries | 3 | SK.GOV.001, SK.PRD.010 |
| SK.DOM.LGL.002 | Legal: Hallucination eval frameworks | 4 | SK.EVL.001, SK.RAG.020 |
| SK.DOM.FIN.001 | Finance: Numerical auditability | 4 | SK.EVL.010, SK.AGT.031 |
| SK.DOM.EDU.001 | Education: Learning design with AI | 2 | SK.PRM.001 |
| SK.DOM.MKT.001 | Marketing: Content generation ethics | 2 | SK.FND.021, SK.FND.022 |
| SK.DOM.HR.001 | HR: AI in hiring considerations | 2 | SK.FND.022, SK.GOV.001 |

#### D.PRD - Product & UX

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.PRD.000 | AI product thinking basics | 1 | SK.FND.004 |
| SK.PRD.001 | Use-case selection & prioritization | 2 | SK.FND.004 |
| SK.PRD.002 | Workflow mapping | 3 | SK.PRD.001 |
| SK.PRD.010 | Explainability UX design | 3 | SK.PRM.021 |
| SK.PRD.011 | Feedback loop design | 3 | SK.EVL.011 |
| SK.PRD.020 | AI enablement & training strategy | 3 | SK.PRD.002 |
| SK.PRD.021 | Stakeholder management | 3 | SK.FND.002, SK.GOV.001 |
| SK.PRD.022 | ROI measurement for AI | 3 | SK.PRD.001 |

#### D.COM - Communication & Collaboration

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.COM.001 | Explaining AI to non-technical audiences | 2 | SK.FND.001 |
| SK.COM.002 | Writing AI project proposals | 3 | SK.PRD.001 |
| SK.COM.003 | Facilitating AI workshops | 3 | SK.COM.001 |
| SK.COM.004 | Managing AI expectations | 2 | SK.FND.002 |
| SK.COM.005 | Cross-functional AI collaboration | 3 | SK.COM.001 |
| SK.COM.006 | AI documentation best practices | 3 | SK.PRM.003 |

#### D.LRN - Learning & Adaptation

| ID | Skill | Level | Prerequisites |
|----|-------|-------|---------------|
| SK.LRN.001 | Keeping up with AI developments | 1 | SK.FND.000 |
| SK.LRN.002 | Evaluating new AI tools | 2 | SK.TOOL.000 |
| SK.LRN.003 | Building personal AI workflows | 2 | SK.PRM.001 |
| SK.LRN.004 | Teaching others AI skills | 3 | SK.COM.001 |
| SK.LRN.005 | Experimenting safely with AI | 2 | SK.FND.020, SK.SEC.000 |

### Roles

| ID | Label | Focus Domains | Color |
|----|-------|---------------|-------|
| ROLE.BEGINNER | AI Curious Beginner | D.DIG, D.CTIC, D.FND, D.PRM | #22c55e |
| ROLE.KNOWLEDGE | Knowledge Worker | D.DIG, D.CTIC, D.FND, D.PRM, D.MUL, D.COM | #3b82f6 |
| ROLE.AI_PM | AI Product Manager | D.PRD, D.PRM, D.EVL, D.GOV, D.COM | #8b5cf6 |
| ROLE.LLM_ENGINEER | LLM Engineer | D.PRQ, D.PRM, D.RAG, D.AGT, D.EVL, D.SEC, D.OPS, D.TOOL | #06b6d4 |
| ROLE.AI_ARCHITECT | AI Architect | D.AGT, D.EVL, D.SEC, D.GOV, D.OPS, D.MOD | #ec4899 |

---

## AI Fluency Ontology (V2)

A more focused ontology emphasizing practical AI literacy with 8 clusters and 95 skills.

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

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| LLM_Architecture | LLM Architecture (Transformers, Scaling) | transformers, attention, scaling laws | - |
| Tokens_Context | Tokens & Context Windows | tokenization, context window, sliding window | LLM_Architecture |
| Hallucinations_Limits | Hallucinations & failure modes | hallucinations, grounding, staleness | LLM_Architecture |
| Model_Selection | Model Selection (SLM vs LLM, Open vs Closed) | model size, parameter count, benchmark analysis | LLM_Architecture |
| Compute_Economics | Compute Costs & Latency | inference cost, latency, TTFT, TPOT | LLM_Architecture |
| Diffusion_Basics | Diffusion Model Fundamentals | diffusion, noise reduction, stable diffusion | - |

#### Prompting

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Few_Shot_Prompting | Few-Shot & Zero-Shot Prompting | in-context learning, few-shot, zero-shot | Tokens_Context |
| Role_Persona | Role & Persona Engineering | system prompts, persona, instruction tuning | Few_Shot_Prompting |
| Structured_Outputs | Structured outputs (JSON, XML, Schemas) | JSON mode, function calling schemas | Few_Shot_Prompting |
| Iterative_Refinement | Iterative Prompt Refinement | prompt versioning, feedback loops | Few_Shot_Prompting |
| Context_Stuffing | Context Window Management (Long Context) | long context, needle in a haystack | Tokens_Context |
| Prompt_Compression | Prompt Compression & Optimization | token savings, shorthand | Tokens_Context |
| Negative_Prompting | Negative Prompting & Constraints | exclusion, constraints | Few_Shot_Prompting |

#### RAG

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Embeddings_Vectors | Embeddings & Vector Theory | semantic search, cosine similarity, dense retrieval | LLM_Architecture |
| Chunking_Strategies | Semantic & Recursive Chunking | recursive character splitter, overlap | Embeddings_Vectors |
| Vector_Databases | Vector Database Operations | Pinecone, Milvus, indexing, metadata filtering | Embeddings_Vectors |
| Retrieval_Heuristics | Advanced Retrieval (BM25, Hybrid Search) | hybrid search, sparse retrieval | Embeddings_Vectors |
| Reranking | Reranking & Cross-Encoders | cross-encoder, relevance scoring | Retrieval_Heuristics |
| Grounding_Citations | Groundedness & Automated Citations | source attribution, citation accuracy | Retrieval_Heuristics |
| Graph_RAG | Knowledge Graphs & GraphRAG | graph-based retrieval, triples | Retrieval_Heuristics |

#### Agentic

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Tool_Calling | Tool & Function Calling | function call, API integration | Structured_Outputs |
| Agent_Orchestration | Agent Orchestration (Multi-agent) | LangGraph, AutoGen, sequential agents | Tool_Calling |
| Planning_Execution | Planning & Execution Loops | Chain of Thought, ReAct | Agent_Orchestration |
| State_Management | Memory & State Persistence | short-term memory, long-term memory, checkpoints | Agent_Orchestration |
| HITL | Human-In-The-Loop (HITL) Workflows | human approval, manual override | Agent_Orchestration |
| Self_Reflection | Self-Reflection & Error Correction | reflexion, dual check | Planning_Execution |
| Agentic_MCP | Agentic use of MCP Tools | MCP integration | Tool_Calling |

#### MCP

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| MCP_Architecture | MCP Architecture (Clients/Servers) | Model Context Protocol, transport | Tool_Calling |
| MCP_Server_Dev | MCP Server Development | SDK usage, Node/Python servers | MCP_Architecture |
| MCP_Resources | MCP Resources & Prompts | declaring resources, template prompts | MCP_Architecture |
| MCP_Tools | Building Custom MCP Tools | defining tool schemas | MCP_Architecture |
| MCP_Security | MCP Security & Sandboxing | authorized servers, runtime isolation | MCP_Architecture |

#### Eval

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Prompt_Unit_Tests | Prompt Unit Testing | asserts, LLM unit testing | Structured_Outputs |
| LLM_As_Judge | LLM-As-Judge Scoring | automated rubrics, consistency checks | Prompt_Unit_Tests |
| Golden_Datasets | Golden Datasets & Benchmarking | standardized test sets | LLM_As_Judge |
| Monitoring_Drift | Monitoring, Drift, & Logging | Arize, LangSmith, observability | Golden_Datasets |
| AB_Testing | A/B Testing Prompts & Models | side-by-side comparison | LLM_As_Judge |
| Model_Registry | Model & Prompt Version Registry | registry management | Monitoring_Drift |

#### Responsible

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Bias_Fairness | Bias, Fairness, & Toxicity Mitigation | algorithmic bias, safety filters | LLM_Architecture |
| Prompt_Injection_Safety | Prompt Injection & Jailbreak Defense | red teaming, injection prevention | Few_Shot_Prompting |
| Privacy_PII | Data Privacy & PII Scrubbing | anonymization, PII detection | LLM_Architecture |
| AI_Explainability | Explainability & Transparency | decision reasoning, model transparency | LLM_Architecture |
| Copyright_IP | AI Copyright & IP Ethics | fair use, training data ethics | LLM_Architecture |
| Red_Teaming | Adversarial Red Teaming | attack patterns | Prompt_Injection_Safety |

#### Multimodal

| ID | Skill | Synonyms | Prerequisites |
|----|-------|----------|---------------|
| Multimodal_Literacy | Vision/Audio Interaction Literacy | image-to-text, speech-to-text | LLM_Architecture |
| Image_Editing | Image Generation & Inpainting | inpainting, outpainting, DALL-E | Diffusion_Basics |
| Video_Gen | Text-to-Video Generation Literacy | Sora, Runway | Diffusion_Basics |
| Speech_Synthesis | Speech Synthesis & Voice Cloning | ElevenLabs, cloning ethics | Multimodal_Literacy |
| Fine_Tuning_Concepts | Parameter Efficient Fine-Tuning (LoRA) | LoRA, PEFT, fine-tuning | LLM_Architecture |

---

## Ontology Files Reference

| File | Type | Description |
|------|------|-------------|
| [genai-skills-ontology.json](genai-skills-ontology.json) | JSON | Complete primary ontology data (v1.0.0) |
| [genai-ontology-map.tsx](genai-ontology-map.tsx) | React/TSX | Interactive visualization component |
| [ontology_chart.html](ontology_chart.html) | HTML/D3.js | Standalone visualization with D3.js |
| [skillgap-coach/src/lib/ontology.ts](skillgap-coach/src/lib/ontology.ts) | TypeScript | AI Fluency Ontology V2 module |
| [skillgap-coach/dist/lib/ontology.js](skillgap-coach/dist/lib/ontology.js) | JavaScript | Compiled V2 ontology |
