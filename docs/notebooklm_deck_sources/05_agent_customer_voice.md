# Agent: Customer Voice Reasoner

_LLM agent. Reads the persona's verbatim customer quote + the current engine output. Decides whether the engine satisfies what the customer actually wants. Includes deterministic severity sanity-checks._

Source file in the repo: `05/agent_customer_voice.py` (numeric prefix added for NotebookLM upload order).

```python
"""Agent A - Customer Voice Reasoner.

Reads every customer-facing finding in the persona corpus + memory
files and uses an LLM to identify:
  1. Standing constraints (rules the customer has stated explicitly,
     e.g. "no em-dashes", "dashboard names must match Top 5 page")
  2. Persona-specific assertions grounded in customer quotes
  3. Whether the engine's current output APPEARS to satisfy the
     customer's INTENT (not just the literal words)

The agent's job is to PUSH BACK when a proposed fix addresses the
literal request but misses the deeper concern. Example: Luda on May 19
said "fix the dashboard names" but the underlying complaint was about
ORDER as well - a literal "names fix" would not have closed the issue.

Verdict policy:
  RED   : a clear customer constraint is violated by the current output
  YELLOW: customer intent is partially addressed but a documented quote
          is not yet satisfied
  GREEN : all known customer constraints are satisfied for this persona
"""
from __future__ import annotations

import json
import logging

from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, color_from_findings
from app.services.llm import get_llm_provider


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are the Customer Voice Reasoner agent. Your job is to read \
customer feedback (the verbatim customer_quote field) and the current engine \
output, then judge whether the engine satisfies what the customer ACTUALLY \
wants - not just what they literally asked for.

You are paid to push back when the customer's INTENT is missed even if the \
literal corpus assertion happens to be met (or vice versa). Always ground \
your reasoning in the exact customer_quote - quote it verbatim in the \
'quote' field of any finding. Do NOT use corpus field names or persona \
description text as a 'quote' - that is system metadata, not the customer's \
words.

CRITICAL READING RULES - do not misapply these:

1. expected_top5_includes lists what MUST be in positions #1-5 of the engine \
   output. If a skill is at position #6 or #7, that is NOT in top 5 - it is \
   in top 10. Do not raise an error if an expected skill is in top 10 but \
   below position 5 - raise a WARN instead.

2. forbidden_in_top5 lists what MUST NOT be in positions #1-5. If a forbidden \
   skill appears at position #6 or later, that is FINE - it is below the top \
   5 cutoff. Do not raise an error for forbidden skills appearing in top 10 \
   but below position 5.

3. The skill set, not the persona description, is what you grade. Read the \
   actual top 5 (positions 1-5) and the customer's quote, and judge whether \
   the customer's actual underlying concern is addressed.

You must return a JSON object with exactly this shape:
{
  "color": "green" | "yellow" | "red",
  "summary": "<one sentence>",
  "findings": [
    {
      "severity": "info" | "warn" | "error",
      "summary": "<one sentence>",
      "detail": "<reasoning that does NOT use corpus field names as quotes>",
      "quote": "<verbatim customer_quote text or empty string>",
      "skill_id": "<SK.X.NNN if relevant>",
      "proposed_fix": "<specific actionable change>"
    }
  ],
  "reasoning": "<paragraph of overall reasoning>"
}

severity rules:
  - error  : customer's stated need is concretely NOT met by the actual top 5
  - warn   : customer's intent is partially met; a customer-stated nuance is missed
  - info   : observation about customer context, not a defect

color rules:
  - red    : any error-level finding
  - yellow : any warn-level finding (no errors)
  - green  : only info findings or none

Quote rules:
  - Only the customer_quote field is a real customer quote. Use it verbatim.
  - Anything in CORPUS EXPECTATIONS (expected_top5_includes, forbidden_in_top5,
    expected_develop_count) is system spec, NOT customer words. Never put
    these in the 'quote' field."""


def _build_user_prompt(persona: dict, top_10: list[dict],
                       maintain_skills: list[dict] | None,
                       develop_skills: list[dict] | None) -> str:
    """Compose the user prompt for the Customer Voice agent."""
    top10_lines = []
    for i, s in enumerate(top_10[:10], 1):
        top10_lines.append(
            f"  #{i} {s.get('skill_id')} {s.get('skill_name', '')!r}"
        )

    parts = [
        f"PERSONA: {persona.get('id')}",
        f"ROLE: {persona.get('role')}",
        f"VERTICAL: {persona.get('vertical') or 'none'}",
        f"LEARNER BACKGROUND: {persona.get('learner_technical_background', '')}",
        "",
        "CUSTOMER FEEDBACK SOURCE:",
        f"  {persona.get('source', '')}",
        "",
        "CUSTOMER VERBATIM QUOTE (use this to ground your reasoning):",
        f"  \"{persona.get('customer_quote', '')}\"",
        "",
        "RATIONALE (why this persona has the expectations it has):",
        f"  {persona.get('rationale', '')}",
        "",
        "CORPUS EXPECTATIONS:",
        f"  expected_top5_includes:  {persona.get('expected_top5_includes')}",
        f"  expected_top10_includes: {persona.get('expected_top10_includes')}",
        f"  forbidden_in_top5:       {persona.get('forbidden_in_top5')}",
        f"  expected_develop_count:  {persona.get('expected_develop_count')}",
        "",
        "WHAT THE ENGINE RETURNED (top 10, in rank order):",
        *top10_lines,
    ]

    if maintain_skills is not None:
        parts.extend([
            "",
            f"MAINTAIN bucket ({len(maintain_skills)} skills already at or above target):",
            *[f"  - {s.get('skill_id')} {s.get('skill_name', '')!r} (current L{s.get('current_level')})"
              for s in maintain_skills[:10]],
        ])
    if develop_skills is not None:
        parts.extend([
            "",
            f"DEVELOP bucket ({len(develop_skills)} skills with gap; these become path chapters):",
            *[f"  - {s.get('skill_id')} {s.get('skill_name', '')!r} (L{s.get('current_level')} -> L{s.get('required_level') or s.get('target_level')})"
              for s in develop_skills[:10]],
        ])

    parts.extend([
        "",
        "YOUR TASK:",
        "Read the customer quote and rationale. Then look at what the engine returned.",
        "Decide: does this output address what the customer ACTUALLY wants? Push back ",
        "if the literal corpus assertion is met but a deeper customer intent is missed, ",
        "or if a corpus assertion is violated. Return your verdict as JSON.",
    ])

    return "\n".join(parts)


class CustomerVoiceAgent(QAAgent):
    name = "Customer Voice Reasoner"
    description = "LLM-grounded reasoning over customer quotes vs current engine output"

    async def run(self, context: dict) -> AgentVerdict:
        persona = context.get("persona") or {}
        top_10 = context.get("top_10_skills") or []
        maintain = context.get("maintain_skills")
        develop = context.get("develop_skills")

        if not persona:
            return self._red(
                "no persona supplied",
                findings=[Finding(
                    severity=Severity.ERROR,
                    summary="missing persona in context",
                )],
            )

        # Short-circuit when the engine has not produced output for this
        # persona yet. The agent should not flag absence-of-data as a
        # customer-voice violation - that is a coverage gap, not a
        # qualitative defect. Consistent with the Skill Curator's
        # short-circuit on empty top_10.
        if not top_10:
            return AgentVerdict(
                agent_name=self.name,
                color=color_from_findings([]),
                summary="no engine output to judge; re-run analysis for this persona first",
                findings=[Finding(
                    severity=Severity.INFO,
                    summary="no top_10 returned by the engine yet",
                    detail="Trigger /analysis/full for this profile so the QA "
                           "team has something concrete to grade.",
                )],
                metadata={"persona_id": persona.get("id")},
                reasoning="Customer-voice reasoning requires actual engine output "
                          "to compare against customer feedback. Skipped.",
            )

        prompt = _build_user_prompt(persona, top_10, maintain, develop)

        try:
            llm = get_llm_provider()
            response = await llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.3,
                json_mode=True,
            )
            raw = response.content
        except Exception as exc:
            logger.warning("Customer Voice LLM call failed: %s", exc)
            return AgentVerdict(
                agent_name=self.name,
                color=color_from_findings([]),
                summary=f"LLM unavailable, agent skipped: {exc}",
                findings=[Finding(
                    severity=Severity.INFO,
                    summary="agent skipped due to LLM error",
                )],
                metadata={"persona_id": persona.get("id")},
                reasoning=str(exc),
            )

        # Parse JSON output
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            # Try to recover by finding the first JSON object in the text
            try:
                start = raw.index("{")
                end = raw.rindex("}") + 1
                data = json.loads(raw[start:end])
            except Exception:
                logger.warning("Customer Voice JSON parse failed; raw=%s", raw[:300])
                return AgentVerdict(
                    agent_name=self.name,
                    color=color_from_findings([]),
                    summary="LLM returned non-JSON output",
                    findings=[Finding(
                        severity=Severity.INFO,
                        summary="LLM JSON parse failed",
                        detail=raw[:400],
                    )],
                    metadata={"persona_id": persona.get("id")},
                )

        findings: list[Finding] = []
        # Pre-compute top5 and top10 once for severity sanity-check below
        top5_actual_ids = [s.get("skill_id") for s in top_10[:5]]
        top10_actual_ids = [s.get("skill_id") for s in top_10[:10]]
        forbidden = set(persona.get("forbidden_in_top5") or [])
        expected_top5 = set(persona.get("expected_top5_includes") or [])

        for f in data.get("findings", []):
            try:
                severity = Severity(f.get("severity", "info").lower())
            except ValueError:
                continue
            sid = f.get("skill_id", "")
            detail = f.get("detail", "")
            summary = f.get("summary", "")

            # Deterministic severity sanity-check. The LLM is inconsistent
            # about whether "missing from top 5 but present in top 10"
            # should be ERROR or WARN, and about whether a forbidden skill
            # at position #6+ counts as a violation. Override the LLM's
            # severity when the literal facts make ERROR wrong.
            if severity == Severity.ERROR and sid:
                # Case 1: LLM said ERROR about a forbidden skill, but the
                # skill is NOT in top 5 - that is not a violation per the
                # corpus rules. Downgrade to INFO.
                if sid in forbidden and sid not in top5_actual_ids:
                    severity = Severity.INFO
                    summary = f"[downgraded] {summary}"
                # Case 2: LLM said ERROR about an expected_top5 skill that
                # is missing from top 5 - the engine still has it in the
                # top 10. Downgrade to WARN (real concern, not blocking).
                elif sid in expected_top5 and sid not in top5_actual_ids and sid in top10_actual_ids:
                    severity = Severity.WARN

            findings.append(Finding(
                severity=severity,
                summary=summary,
                detail=detail,
                quote=f.get("quote", ""),
                skill_id=sid,
                proposed_fix=f.get("proposed_fix", ""),
            ))

        # Use the LLM's color but enforce: if any ERROR finding, color is red
        try:
            color = color_from_findings(findings)
        except Exception:
            color = color_from_findings([])

        return AgentVerdict(
            agent_name=self.name,
            color=color,
            summary=data.get("summary", "customer-voice reasoning complete"),
            findings=findings,
            metadata={"persona_id": persona.get("id")},
            reasoning=data.get("reasoning", ""),
        )

```
