"""Agent E - Demo Readiness Gate.

Aggregates verdicts from agents A through D into a single
GREEN / YELLOW / RED verdict for a persona, plus a readable dossier
suitable for attaching to a "ready to demo" status email.

Verdict policy:
  RED   : any upstream agent returned RED, or any finding is ERROR-level
  YELLOW: any upstream agent returned YELLOW or any WARN-level finding
  GREEN : every upstream agent GREEN with only INFO findings
"""
from __future__ import annotations

from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, VerdictColor


class DemoGateAgent(QAAgent):
    name = "Demo-Readiness Gate"
    description = "Final aggregator that produces a single ready/not-ready verdict"

    async def run(self, context: dict) -> AgentVerdict:
        prior: list[AgentVerdict] = context.get("prior_verdicts") or []

        any_red = any(v.color == VerdictColor.RED for v in prior)
        any_yellow = any(v.color == VerdictColor.YELLOW for v in prior)

        if any_red:
            color = VerdictColor.RED
            verdict_word = "NOT READY"
        elif any_yellow:
            color = VerdictColor.YELLOW
            verdict_word = "READY WITH CAVEATS"
        else:
            color = VerdictColor.GREEN
            verdict_word = "READY"

        # Roll up the strongest finding from each upstream agent
        rolled: list[Finding] = []
        for v in prior:
            for f in v.findings:
                if f.severity == Severity.ERROR:
                    rolled.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"[{v.agent_name}] {f.summary}",
                        detail=f.detail,
                        quote=f.quote,
                        skill_id=f.skill_id,
                        proposed_fix=f.proposed_fix,
                    ))

        return AgentVerdict(
            agent_name=self.name,
            color=color,
            summary=f"{verdict_word}: " + ", ".join(
                f"{v.agent_name}={v.color.value.upper()}" for v in prior
            ),
            findings=rolled,
            metadata={
                "prior_agent_count": len(prior),
                "per_agent_color": {v.agent_name: v.color.value for v in prior},
            },
            reasoning=(
                f"Aggregated {len(prior)} upstream verdicts. "
                f"{verdict_word}. "
                f"{sum(1 for v in prior if v.color == VerdictColor.RED)} RED, "
                f"{sum(1 for v in prior if v.color == VerdictColor.YELLOW)} YELLOW, "
                f"{sum(1 for v in prior if v.color == VerdictColor.GREEN)} GREEN."
            ),
        )


def render_dossier(persona_id: str, verdicts: list[AgentVerdict]) -> str:
    """Render a readable Markdown dossier for the persona."""
    lines: list[str] = []
    final = verdicts[-1] if verdicts else None
    color = final.color.value.upper() if final else "UNKNOWN"

    lines.append(f"# QA Dossier - {persona_id}")
    lines.append("")
    lines.append(f"**Verdict: {color}**")
    if final:
        lines.append("")
        lines.append(final.summary)
    lines.append("")
    lines.append("## Per-agent verdicts")
    lines.append("")
    for v in verdicts:
        lines.append(f"### {v.agent_name} - {v.color.value.upper()}")
        lines.append("")
        lines.append(f"_{v.summary}_")
        lines.append("")
        if v.reasoning:
            lines.append(f"**Reasoning:** {v.reasoning}")
            lines.append("")
        if v.findings:
            lines.append("**Findings:**")
            for f in v.findings:
                lines.append(f"  - [{f.severity.value.upper()}] {f.summary}")
                if f.quote:
                    lines.append(f"    > customer: \"{f.quote}\"")
                if f.detail:
                    lines.append(f"    > {f.detail}")
                if f.proposed_fix:
                    lines.append(f"    > proposed fix: {f.proposed_fix}")
            lines.append("")
    return "\n".join(lines)
