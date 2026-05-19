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
customer feedback emails and current engine output, then judge whether the \
engine satisfies what the customer ACTUALLY wants - not just what they \
literally asked for.

You are paid to push back. If the literal request is met but the customer's \
INTENT is missed, raise an ERROR. Always ground your reasoning in the \
exact customer quote - quote it verbatim in your response.

You must return a JSON object with exactly this shape:
{
  "color": "green" | "yellow" | "red",
  "summary": "<one sentence>",
  "findings": [
    {
      "severity": "info" | "warn" | "error",
      "summary": "<one sentence>",
      "detail": "<reasoning>",
      "quote": "<exact customer quote that informs this finding>",
      "skill_id": "<SK.X.NNN if relevant>",
      "proposed_fix": "<specific actionable change>"
    }
  ],
  "reasoning": "<paragraph of overall reasoning>"
}

severity rules:
  - error  : customer's stated need is NOT met
  - warn   : customer's stated need is partially met or unclear
  - info   : observation about customer context, not a defect

color rules:
  - red    : any error-level finding
  - yellow : any warn-level finding (no errors)
  - green  : only info findings or none

Do not invent quotes. If you don't have a quote, leave the field empty."""


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
        for f in data.get("findings", []):
            try:
                findings.append(Finding(
                    severity=Severity(f.get("severity", "info").lower()),
                    summary=f.get("summary", ""),
                    detail=f.get("detail", ""),
                    quote=f.get("quote", ""),
                    skill_id=f.get("skill_id", ""),
                    proposed_fix=f.get("proposed_fix", ""),
                ))
            except ValueError:
                continue

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
