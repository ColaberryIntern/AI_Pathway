"""Pydantic schemas for Confusion Recovery."""
from pydantic import BaseModel


class ConfusionRecoveryRequest(BaseModel):
    section: str = "general"  # which section confused the learner


class ConfusionRecoveryResponse(BaseModel):
    analogy: str
    step_by_step: list[str]
    real_world_example: str
    common_misconceptions: list[str]
    suggested_mentor_prompt: str
