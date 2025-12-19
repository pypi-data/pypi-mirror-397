from abc import ABC, abstractmethod
from typing import Any, List, Optional

from beekeeper.core.llms.types import ChatMessage, ChatResponse, GenerateResponse
from beekeeper.core.monitors import BaseMonitor
from pydantic import BaseModel


class BaseLLM(ABC, BaseModel):
    """Abstract base class defining the interface for LLMs."""

    model_config = {"arbitrary_types_allowed": True}
    callback_manager: Optional[BaseMonitor] = None

    @classmethod
    def class_name(cls) -> str:
        return "BaseLLM"

    def text_completion(self, prompt: str, **kwargs: Any) -> str:
        """
        Generates a chat completion for LLM. Using OpenAI's standard endpoint (/completions).

        Args:
            prompt (str): The input prompt to generate a completion for.
            **kwargs (Any): Additional keyword arguments to customize the LLM completion request.
        """
        response = self.completion(prompt=prompt, **kwargs)

        return response.text

    @abstractmethod
    def completion(self, prompt: str, **kwargs: Any) -> GenerateResponse:
        """Generates a completion for LLM."""

    @abstractmethod
    def chat_completion(
        self, messages: List[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Generates a chat completion for LLM."""
