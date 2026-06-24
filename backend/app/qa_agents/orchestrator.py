"""QA team orchestrator. Runs the 5 agents in dependency order and
returns the assembled verdict list + the Demo Gate's final verdict.

The orchestrator is intentionally simple - sequential where there are
dependencies, otherwise the agents are independent. The CLI runner
(backend/scripts/run_qa_team.py) is what end-users invoke.
"""
from __future__ import annotations

import logging
from typing import Any

from app.qa_agents.base import QAAgent
from app.qa_agents.chapter_breadth_depth_judge import ChapterBreadthDepthJudge
from app.qa_agents.chapter_reviewer import ChapterReviewerAgent
from app.qa_agents.customer_voice import CustomerVoiceAgent
from app.qa_agents.demo_gate import DemoGateAgent
from app.qa_agents.path_coherence import PathCoherenceAgent
from app.qa_agents.skill_curator import SkillCuratorAgent
from app.qa_agents.verdict import AgentVerdict


logger = logging.getLogger(__name__)


# Order matters only insofar as later agents may inspect prior verdicts.
DEFAULT_AGENTS: list[QAAgent] = [
    PathCoherenceAgent(),
    SkillCuratorAgent(),
    CustomerVoiceAgent(),
    ChapterReviewerAgent(),
    ChapterBreadthDepthJudge(),
]


async def run_qa_team(context: dict[str, Any],
                       agents: list[QAAgent] | None = None) -> list[AgentVerdict]:
    """Run every QA agent in order. Returns the full verdict list with
    the Demo Gate's verdict appended.
    """
    agents = agents or DEFAULT_AGENTS
    verdicts: list[AgentVerdict] = []

    for agent in agents:
        ctx = {**context, "prior_verdicts": list(verdicts)}
        try:
            v = await agent.run(ctx)
        except Exception as exc:
            logger.error("Agent %s crashed: %s", agent.name, exc, exc_info=True)
            from app.qa_agents.verdict import AgentVerdict, VerdictColor, Finding, Severity
            v = AgentVerdict(
                agent_name=agent.name,
                color=VerdictColor.RED,
                summary=f"agent crashed: {exc}",
                findings=[Finding(
                    severity=Severity.ERROR,
                    summary=f"unhandled exception in {agent.name}",
                    detail=str(exc),
                )],
            )
        verdicts.append(v)

    # Demo Gate goes last and sees every prior verdict.
    gate = DemoGateAgent()
    gate_v = await gate.run({**context, "prior_verdicts": list(verdicts)})
    verdicts.append(gate_v)
    return verdicts
