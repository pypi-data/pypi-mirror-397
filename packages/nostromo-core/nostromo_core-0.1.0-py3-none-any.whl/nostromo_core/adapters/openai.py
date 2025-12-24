"""
OpenAI GPT LLM adapter.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from nostromo_core.ports.llm import AbstractLLMProvider
from nostromo_core.theme.errors import NostromoError, format_error

if TYPE_CHECKING:
    from openai import AsyncOpenAI


class OpenAIProvider(AbstractLLMProvider):
    """
    OpenAI GPT LLM provider.

    Supports GPT-4o, GPT-4o-mini, GPT-4 Turbo, etc.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model identifier (default: gpt-4o-mini)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
        """
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install 'nostromo-core[openai]'"
            ) from e

        self._client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self, messages: list[dict[str, str]]
    ) -> tuple[str, dict[str, int]]:
        """Generate a complete response from GPT."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                messages=messages,  # type: ignore
            )

            content = response.choices[0].message.content or ""
            usage = {
                "input": response.usage.prompt_tokens if response.usage else 0,
                "output": response.usage.completion_tokens if response.usage else 0,
            }

            return content, usage

        except Exception as e:
            error_msg = self._map_error(e)
            raise RuntimeError(error_msg) from e

    async def stream(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        """Stream response tokens from GPT."""
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                messages=messages,  # type: ignore
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            error_msg = self._map_error(e)
            raise RuntimeError(error_msg) from e

    def _map_error(self, error: Exception) -> str:
        """Map OpenAI errors to themed messages."""
        error_str = str(error).lower()

        if "authentication" in error_str or "api_key" in error_str:
            return format_error(NostromoError.AUTH_FAILED)
        elif "rate" in error_str or "limit" in error_str:
            return format_error(NostromoError.RATE_LIMITED, seconds="60")
        elif "connection" in error_str or "network" in error_str:
            return format_error(NostromoError.UPLINK_FAILURE)
        else:
            return format_error(NostromoError.PROCESSING_ERROR)
