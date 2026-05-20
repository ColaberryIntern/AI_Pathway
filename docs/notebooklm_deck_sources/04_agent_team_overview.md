# QA agent package overview

_Package docstring describing all five QA agents and how they collaborate._

Source file in the repo: `04/agent_team_overview.py` (numeric prefix added for NotebookLM upload order).

```python
"""Multi-agent QA team for pre-demo verification.

Five agents collaborate on every persona pass:

  A - Customer Voice Reasoner: reads customer emails + quotes; surfaces
      standing constraints and persona-specific assertions
  B - Skill Curator: independent rubric scoring; pushes back on
      engine-engine output disagreements
  C - Path Coherence Auditor: deterministic DB-level invariant checks
  D - Chapter Reviewer: per-chapter identity + content sanity (mix of
      deterministic + LLM judgment on prose)
  E - Demo-Readiness Gate: synthesizes A through D into a single
      GREEN/YELLOW/RED verdict + a readable dossier

Each agent emits a structured Verdict (see verdict.py) with reasoning
grounded in customer quotes when possible. Agents can BLOCK (RED) or
WARN (YELLOW). The Demo Gate refuses to declare a persona demo-ready
if any agent returned RED.

Usage:
  py -3.12 backend/scripts/run_qa_team.py <persona_id>

This runs against the live production deployment via the existing
sweep + preflight infrastructure plus new LLM-based checks.
"""

```
