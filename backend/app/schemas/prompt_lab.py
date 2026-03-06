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


class ImplementationTaskSubmitRequest(BaseModel):
    lesson_id: str
    prompt_history_summary: str = ""
    strategy_explanation: str = ""
    learner_prompt: str = ""


class ImplementationTaskFeedbackResponse(BaseModel):
    feedback: str
    strengths: list[str] = []
    improvements: list[str] = []
    prompt_strategy_tips: list[str] = []


class ImplementationTaskGradeResponse(BaseModel):
    score: int
    passed: bool
    feedback: str
    strengths: list[str] = []
    improvements: list[str] = []
    attempt_number: int
