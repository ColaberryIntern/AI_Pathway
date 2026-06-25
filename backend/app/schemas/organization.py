"""Contracts for the Organization admin API (multi-tenancy increment 1)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    domain: str | None = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    domain: str | None = None
    created_at: str
    member_count: int = 0


class AssignMemberRequest(BaseModel):
    user_id: str = Field(min_length=1)


class LearnerSummary(BaseModel):
    user_id: str
    name: str | None = None
    email: str | None = None
    total_paths: int
    active_paths: list[dict]
    completed_paths: list[dict]
    total_skills_learned: int
    overall_completion_percentage: float


class OrgDashboardResponse(BaseModel):
    org_id: str
    org_name: str
    learner_count: int
    learners: list[LearnerSummary]
