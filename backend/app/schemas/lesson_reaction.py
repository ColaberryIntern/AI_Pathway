"""Pydantic schemas for Lesson Reactions."""
from typing import Literal
from pydantic import BaseModel

ReactionType = Literal["helpful", "interesting", "mind_blown", "confused"]


class ToggleReactionRequest(BaseModel):
    reaction: ReactionType


class LessonReactionStateResponse(BaseModel):
    """Current reactions state for a user on a lesson."""
    reactions: list[ReactionType]
    confusion_detected: bool = False
