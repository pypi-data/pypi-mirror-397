"""
Abstract LLM Provider interface.

All LLM adapters must implement this interface.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class AbstractLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implementations must provide both synchronous generation
    and streaming capabilities.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'anthropic', 'openai')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name being used."""
        ...

    @abstractmethod
    async def generate(
        self, messages: list[dict[str, str]]
    ) -> tuple[str, dict[str, int]]:
        """
        Generate a complete response.

        Args:
            messages: List of messages in API format [{"role": "...", "content": "..."}]

        Returns:
            Tuple of (response_content, usage_dict)
            usage_dict contains token counts: {"input": N, "output": M}
        """
        ...

    @abstractmethod
    async def stream(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        """
        Stream a response token by token.

        Args:
            messages: List of messages in API format

        Yields:
            String tokens as they are generated
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if the provider is available.

        Returns:
            True if provider is healthy, False otherwise.
        """
        try:
            # Simple test - try to generate with minimal input
            await self.generate([{"role": "user", "content": "ping"}])
            return True
        except Exception:
            return False
