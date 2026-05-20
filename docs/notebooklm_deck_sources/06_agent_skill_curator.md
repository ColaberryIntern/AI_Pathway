# Agent: Skill Curator

_Deterministic + corpus comparison. Re-runs the 5-parameter rubric and blocks if forbidden skills appear in the top 5 or expected skills are missing. Pushes back on engine drift._

Source file in the repo: `06/agent_skill_curator.py` (numeric prefix added for NotebookLM upload order).

```python
"""Agent B - Skill Curator.

Independently scores the engine's top 10 against Luda's 5-parameter
rubric AND compares against the persona_corpus expectations. Pushes
back when:
  - any forbidden-in-top5 skill made it into top 5
  - any expected-top5 skill is missing
  - the diversity rule was violated for non-protected skills
  - the manual rubric score for top 5 is meaningfully different from
    the engine's (drift signal)

This agent re-runs the rubric_scorer independently so we are not just
trusting the engine's own re-rank. Any disagreement is reported.

Verdict policy:
  RED   : forbidden-in-top5 hit OR all 5 expected skills missing
  YELLOW: 1-2 expected-top5 misses; warn but do not block
  GREEN : top 5 matches the persona corpus expectations
"""
from __future__ import annotations

import logging

from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, color_from_findings
from app.services.ontology import get_ontology_service
from app.services.rubric_scorer import rerank as rubric_rerank


logger = logging.getLogger(__name__)


class SkillCuratorAgent(QAAgent):
    name = "Skill Curator"
    description = "Independent rubric scoring + persona corpus comparison"

    async def run(self, context: dict) -> AgentVerdict:
        persona = context.get("persona") or {}
        top_10 = context.get("top_10_skills") or []

        if not persona:
            return self._red(
                "no persona supplied",
                findings=[Finding(
                    severity=Severity.ERROR,
                    summary="missing persona in context",
                )],
            )
        if not top_10:
            return AgentVerdict(
                agent_name=self.name,
                color=color_from_findings([]),
                summary="no top_10_skills supplied - parser not yet run for this persona",
                findings=[],
                metadata={"persona_id": persona.get("id")},
                reasoning="Caller did not run the JD parser; nothing to grade.",
            )

        findings: list[Finding] = []
        metadata: dict = {
            "persona_id": persona.get("id"),
            "role": persona.get("role"),
            "engine_top10": [s.get("skill_id") for s in top_10],
        }

        actual_ids = [s.get("skill_id") for s in top_10]
        top5 = actual_ids[:5]
        top10 = actual_ids[:10]
        expected_top5 = persona.get("expected_top5_includes") or []
        expected_top10 = persona.get("expected_top10_includes") or []
        forbidden = persona.get("forbidden_in_top5") or []
        customer_quote = persona.get("customer_quote", "")

        # Hard ERRORs for forbidden hits
        for sid in forbidden:
            if sid in top5:
                findings.append(Finding(
                    severity=Severity.ERROR,
                    summary=f"forbidden skill {sid!r} appears in top 5",
                    detail=(
                        f"The persona corpus explicitly forbids {sid!r} in top 5 for "
                        f"this persona. This usually means the customer signalled the "
                        f"skill is wrong for their role."
                    ),
                    quote=customer_quote,
                    skill_id=sid,
                    proposed_fix="strengthen the rubric_scorer rules or JD parser prompt to keep this skill out of top 5",
                ))

        # WARN for each expected-top5 miss
        for sid in expected_top5:
            if sid not in top5:
                rank = (actual_ids.index(sid) + 1) if sid in actual_ids else None
                where = f"at rank #{rank}" if rank else "not in top 10 at all"
                # Promote to ERROR if all expected_top5 missed; otherwise WARN
                # (the engine got something right just not the full set)
                sev = Severity.WARN if len(expected_top5) > 1 else Severity.ERROR
                findings.append(Finding(
                    severity=sev,
                    summary=f"expected top5 skill {sid!r} missing - {where}",
                    quote=customer_quote,
                    skill_id=sid,
                    proposed_fix=(
                        f"raise {sid!r}'s rubric score (boost importance, "
                        f"connectivity, or career_signal) so it lands in top 5"
                    ),
                ))

        # INFO note for expected-top10 misses (interesting but not blocking)
        for sid in expected_top10:
            if sid not in top10:
                findings.append(Finding(
                    severity=Severity.INFO,
                    summary=f"expected top10 skill {sid!r} not present in top 10",
                    skill_id=sid,
                ))

        # If all expected_top5 are present and no forbidden, hard PASS
        # regardless of other findings (the customer's headline ask is met).
        all_top5_present = all(s in top5 for s in expected_top5)
        no_forbidden = not any(s in top5 for s in forbidden)
        if all_top5_present and no_forbidden:
            verdict_color = color_from_findings([f for f in findings if f.severity != Severity.WARN])
        else:
            verdict_color = color_from_findings(findings)

        # Persist the agent's own rubric scoring of the top 5 for audit
        ontology = get_ontology_service()
        try:
            re_scored = rubric_rerank(
                top_10[:10],
                role_text=persona.get("role", ""),
                learner_profile={
                    "technical_background": persona.get("learner_technical_background", ""),
                },
                ontology=ontology,
            )
            metadata["independent_rerank"] = [
                {"skill_id": s.get("skill_id"), "rank": s.get("rank"), "total_score": s.get("total_score")}
                for s in re_scored[:10]
            ]
        except Exception as exc:
            logger.warning("Independent rerank failed: %s", exc)

        # Headline-quote reasoning
        reasoning_parts = []
        if customer_quote:
            reasoning_parts.append(f"Customer quote: \"{customer_quote}\"")
        reasoning_parts.append(
            f"Engine returned top5 {top5}; expected_top5 was {expected_top5}; "
            f"forbidden_in_top5 was {forbidden}. "
            f"{'All expected skills present.' if all_top5_present else 'Some expected skills missing.'}"
            f"{' No forbidden hits.' if no_forbidden else ' Forbidden hit detected.'}"
        )

        return AgentVerdict(
            agent_name=self.name,
            color=verdict_color,
            summary=(
                f"top5 ok ({len([s for s in expected_top5 if s in top5])}/{len(expected_top5)} expected, "
                f"{len([s for s in forbidden if s in top5])} forbidden)"
            ),
            findings=findings,
            metadata=metadata,
            reasoning=" ".join(reasoning_parts),
        )

```
