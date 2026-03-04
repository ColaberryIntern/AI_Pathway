"""Pydantic schemas for Prompt Lab."""
from pydantic import BaseModel


class PromptExecutionRequest(BaseModel):
    lesson_id: str
    prompt: str
    iteration: int = 1


class PromptExecutionResponse(BaseModel):
    response: str
    iteration: int
    tokens_used: int = 0
    execution_time_ms: int = 0


class PromptHistoryItem(BaseModel):
    iteration: int
    prompt_text: str
    response_text: str
    execution_time_ms: int
    created_at: str


class PromptHistoryResponse(BaseModel):
    lesson_id: str
    iterations: list[PromptHistoryItem]
    total_iterations: int
