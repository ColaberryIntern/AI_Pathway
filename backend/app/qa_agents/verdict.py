"""Structured verdict types shared across all QA agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Severity ranks for individual findings within a verdict.

    INFO is informational, never blocks.
    WARN does not block but appears in the dossier.
    ERROR blocks - the persona is not demo-ready until resolved.
    """
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class VerdictColor(str, Enum):
    """Overall verdict colors. The Demo Gate aggregates per-agent colors:
       - all GREEN -> demo ready
       - any YELLOW (but no RED) -> ready with caveats; reviewer briefed
       - any RED -> not demo ready, blocker(s) must be resolved
    """
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass
class Finding:
    """One observation within an agent's verdict."""

    severity: Severity
    summary: str            # one-sentence headline
    detail: str = ""        # longer reasoning
    quote: str = ""         # exact customer quote when applicable
    skill_id: str = ""      # specific skill if applicable
    proposed_fix: str = ""  # what would unblock this finding


@dataclass
class AgentVerdict:
    """Structured output every QA agent must return."""

    agent_name: str
    color: VerdictColor
    summary: str
    findings: list[Finding] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    reasoning: str = ""

    def has_errors(self) -> bool:
        return any(f.severity == Severity.ERROR for f in self.findings)

    def has_warnings(self) -> bool:
        return any(f.severity == Severity.WARN for f in self.findings)

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "color": self.color.value,
            "summary": self.summary,
            "findings": [
                {
                    "severity": f.severity.value,
                    "summary": f.summary,
                    "detail": f.detail,
                    "quote": f.quote,
                    "skill_id": f.skill_id,
                    "proposed_fix": f.proposed_fix,
                }
                for f in self.findings
            ],
            "metadata": self.metadata,
            "reasoning": self.reasoning,
        }


def color_from_findings(findings: list[Finding]) -> VerdictColor:
    """Standard rule for deriving a verdict color from a finding list."""
    if any(f.severity == Severity.ERROR for f in findings):
        return VerdictColor.RED
    if any(f.severity == Severity.WARN for f in findings):
        return VerdictColor.YELLOW
    return VerdictColor.GREEN
