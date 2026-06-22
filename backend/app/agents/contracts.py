"""Typed boundary contracts for agent entry points (Contract Enforcement Layer).

Per CLAUDE.md, every module boundary exposes an explicit, typed, importable,
testable contract and validates inputs at the boundary. These Pydantic models are
the contracts for the two highest-traffic agent entry points:

  - Orchestrator.execute(task)         -> OrchestratorInput
  - ContentCuratorAgent.execute(task)  -> ContentCuratorInput / ContentCuratorOutput

`extra="allow"` keeps validation NON-BREAKING: unknown keys pass through unchanged
(model_dump preserves them), so existing callers are unaffected while the declared
fields are type-checked and defaulted. A malformed declared field (e.g. a profile
that is not an object) raises a ValidationError at the boundary instead of failing
deep in the call stack.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrchestratorInput(BaseModel):
    """Contract for Orchestrator.execute(task)."""

    model_config = ConfigDict(extra="allow")

    profile: dict = Field(default_factory=dict)
    jd_text: str = ""
    target_role: str = ""
    skip_assessment: bool = True
    # These are read downstream as `task.get(x) or {}/[]`, so None is tolerated.
    self_assessed_skills: dict | None = None
    selected_skill_ids: list[str] | None = None
    include_resources: bool = True


class ContentCuratorInput(BaseModel):
    """Contract for ContentCuratorAgent.execute(task) input."""

    model_config = ConfigDict(extra="allow")

    chapters: list[dict] = Field(default_factory=list)
    industry: str = ""


class ChapterResources(BaseModel):
    """One chapter's curated resources (an item in ContentCuratorOutput)."""

    model_config = ConfigDict(extra="allow")

    chapter_number: int | None = None
    skill_id: str | None = None
    resources: list[dict] = Field(default_factory=list)


class ContentCuratorOutput(BaseModel):
    """Contract for ContentCuratorAgent.execute(task) output."""

    model_config = ConfigDict(extra="allow")

    chapter_resources: list[ChapterResources] = Field(default_factory=list)
    duration_ms: int | None = None
