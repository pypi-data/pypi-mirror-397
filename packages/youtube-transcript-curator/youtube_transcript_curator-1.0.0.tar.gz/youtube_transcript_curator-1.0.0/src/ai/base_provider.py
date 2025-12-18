"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers (Anthropic, OpenAI, Google)."""

    @abstractmethod
    def analyze(self, transcript: str, prompt: str, **kwargs) -> str:
        """
        Send transcript + prompt to LLM, return response.

        Args:
            transcript: The video transcript text
            prompt: The user's question/instruction
            **kwargs: Additional provider-specific options

        Returns:
            LLM response as string

        Raises:
            Exception: If LLM request fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier being used."""
        pass

    def validate_availability(self) -> bool:
        """
        Check if the provider is available (installed, authenticated, etc.).

        Returns:
            True if provider is ready to use, False otherwise
        """
        return True

    def estimate_cost(self, transcript: str, prompt: str) -> Optional[float]:
        """
        Estimate API cost for this request (only for API mode).

        Args:
            transcript: The video transcript text
            prompt: The user's question/instruction

        Returns:
            Estimated cost in USD, or None for local/free providers
        """
        return None
