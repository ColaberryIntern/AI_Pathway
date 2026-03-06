"""Base agent class for the multi-agent system."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
import uuid
from app.services.llm import BaseLLMProvider, get_llm_provider
from app.services.rag.retriever import RAGRetriever, get_retriever


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    name: str = "BaseAgent"
    description: str = "Base agent class"
    system_prompt: str = ""

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        rag_retriever: RAGRetriever | None = None,
    ):
        self.llm = llm_provider or get_llm_provider()
        self.rag = rag_retriever or get_retriever()
        self.execution_id = str(uuid.uuid4())
        self.start_time = None
        self.end_time = None

    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """Execute the agent's main task.

        Args:
            task: Dictionary containing task parameters

        Returns:
            Dictionary containing the result
        """
        pass

    async def _call_llm(
        self,
        prompt: str,
        context: list[dict] | None = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        system_prompt: str | None = None,
    ) -> str:
        """Make a call to the LLM."""
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt if system_prompt is not None else self.system_prompt,
            context=context,
            temperature=temperature,
            json_mode=json_mode,
        )
        return response.content

    async def _call_llm_structured(
        self,
        prompt: str,
        output_schema: dict,
        context: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict:
        """Make a call to the LLM with structured JSON output."""
        return await self.llm.generate_structured(
            prompt=prompt,
            output_schema=output_schema,
            system_prompt=self.system_prompt,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _log_execution(self, action: str, input_data: Any, output_data: Any):
        """Log agent execution for debugging."""
        log_entry = {
            "execution_id": self.execution_id,
            "agent_name": self.name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "input_summary": str(input_data)[:500],
            "output_summary": str(output_data)[:500],
        }
        # In production, this would write to database or logging service
        return log_entry

    def _start_execution(self):
        """Mark the start of execution."""
        self.start_time = datetime.utcnow()

    def _end_execution(self):
        """Mark the end of execution and return duration."""
        self.end_time = datetime.utcnow()
        if self.start_time:
            duration = (self.end_time - self.start_time).total_seconds() * 1000
            return int(duration)
        return 0
