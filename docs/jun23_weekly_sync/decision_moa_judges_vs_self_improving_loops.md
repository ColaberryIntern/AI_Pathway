# DECISION: Defer self-improving loops; adopt MOA mixture-of-experts judges

Status: ACCEPTED (Jun 23 weekly sync). Decided by Ram, with Luda and Vivek
concurring. This is the governing decision for how we improve quality.

## Context

There is industry momentum around "self-improving loops" (agents that loop:
discover -> plan -> execute -> verify -> iterate, fixing their own output until a
goal is met). The question on the table: do we build a self-improving loop into
AI Pathway's quality pipeline?

## Decision

**No self-improving loop for now.** Instead:

1. **Crisply define a judge at each step** of the pipeline (JD parse, LinkedIn
   parse, recommendation, chapter content breadth+depth, etc.) and simply **fix
   what the judge does not pass**. If the judges are good, we do not need a
   self-improving loop - we need to fix the specific things the judges flag.
2. **Adopt the MOA (Mixture-of-Agents) / mixture-of-experts pattern** for the
   judges: multiple judges with **defined characters** doing adversarial
   judging. This gives more reliable, directional verdicts and a better
   storytelling surface ("we have these judges with these characters, and they
   provide this feedback").

## Why (Ram's reasoning)

- **Cost / unbounded behavior:** self-improving loops are expensive and hard to
  bound - you do not know when they stop, the context grows every iteration, and
  each loop is larger than the last. Without a crisp, nailed-down method they are
  a money sink.
- **Boundary definition is hard:** "hardening" and the surrounding new concepts
  (hooks, etc.) need a lot of definition before a loop is safe to set running.
- **MOA is proven + tells a story:** mixture-of-experts with distinct characters
  has worked reliably (seen since ~GPT-3-era MoE-style setups); adversarial
  judging with defined characters yields directionality and a defensible
  narrative even if no single judge is ground truth.

## Alignment with Trust-Before-Intelligence (CLAUDE.md)

This decision IS the Trust-Before-Intelligence stance: wrap probabilistic
generation in deterministic verification (judges + gates) instead of trusting an
agent to self-correct unbounded. The judge LLM produces per-item judgments; a
deterministic Python step computes composites, gates, and verdicts. Pin the
judge model; calibrate against a golden reference.

## What this means in practice (phasing)

- **Phase 1 (now):** define how we judge each step. Judges already built/hardened
  under this decision: recommendation judge, chapter reviewer (adversarial),
  customer voice (adversarial), demo gate, **chapter breadth+depth judge (Jun 23)**,
  **LinkedIn parse judge (Jun 23, now pinned-model + deterministic precision)**.
- **Later:** richer pieces (more judge characters, broader MOA panels, possibly
  bounded improvement loops) can be brought in as the detector/eval matures -
  but only with a clear method and hard stop conditions.

## Guardrails if we ever revisit loops

Any future self-improving loop must have, before it runs: a real verifier (a
judge or hard test) as the gate, an explicit stop condition (success AND a hard
iteration/token cap), bounded context growth, and a tracked cost-per-accepted-
change metric. No unbounded loops.

## Governance note

A model-class or judge-model change remains a Strategic Decision (escalate) per
the Autonomy Model. This decision does not authorize changing judge models; it
authorizes the judges-per-step + MOA approach over self-improving loops.
