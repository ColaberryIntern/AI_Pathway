"""Base class for QA agents.

QA agents are intentionally separate from the production app.agents stack
- they exist to verify, not to ship product features. Each QA agent
takes a context dict and returns an AgentVerdict.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import logging

from app.qa_agents.verdict import AgentVerdict, VerdictColor


logger = logging.getLogger(__name__)


class QAAgent(ABC):
    """Base class for every QA agent."""

    # Display name, used in dossiers
    name: str = "QAAgent"
    # One-line description shown in the dossier header
    description: str = ""

    @abstractmethod
    async def run(self, context: dict) -> AgentVerdict:
        """Evaluate the given context and return a structured verdict.

        Context is shared across agents and contains at minimum:
          - persona_id    : str       (matches persona_corpus.PERSONAS)
          - persona       : dict      (the corpus entry)
          - profile_id    : str       (production profile UUID)
          - path_id       : str | None
          - top_10_skills : list[dict] | None  (from /parse-jd-skills)
          - prior_verdicts: list[AgentVerdict] (results from agents that
                            already ran; lets later agents reason about
                            earlier findings)
        """
        ...

    def _green(self, summary: str, **kw) -> AgentVerdict:
        return AgentVerdict(
            agent_name=self.name,
            color=VerdictColor.GREEN,
            summary=summary,
            **kw,
        )

    def _red(self, summary: str, **kw) -> AgentVerdict:
        return AgentVerdict(
            agent_name=self.name,
            color=VerdictColor.RED,
            summary=summary,
            **kw,
        )
