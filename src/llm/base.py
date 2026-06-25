from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass