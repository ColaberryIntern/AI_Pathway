"""Pydantic schemas for AI Mentor."""
from pydantic import BaseModel


class MentorChatRequest(BaseModel):
    message: str
    lesson_id: str | None = None
    mode: str | None = None  # "implementation-briefing" for structured task briefing


class MentorChatResponse(BaseModel):
    response: str
    suggested_prompts: list[str] = []
    conversation_id: str


class MentorMessage(BaseModel):
    role: str  # "user" | "mentor"
    content: str
    timestamp: str


class MentorHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[MentorMessage]
    last_suggested_prompts: list[str] = []
