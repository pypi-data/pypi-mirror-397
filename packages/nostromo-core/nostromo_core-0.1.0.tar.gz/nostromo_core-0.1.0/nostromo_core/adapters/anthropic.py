"""
Anthropic Claude LLM adapter.
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from nostromo_core.ports.llm import AbstractLLMProvider
from nostromo_core.theme.errors import NostromoError, format_error

if TYPE_CHECKING:
    from anthropic import AsyncAnthropic


class AnthropicProvider(AbstractLLMProvider):
    """
    Anthropic Claude LLM provider.

    Supports Claude 3.5 Haiku, Claude 3.5 Sonnet, Claude 3 Opus, etc.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-latest",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> None:
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model identifier (default: claude-3-5-haiku-latest)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install 'nostromo-core[anthropic]'"
            ) from e

        self._client: AsyncAnthropic = AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self, messages: list[dict[str, str]]
    ) -> tuple[str, dict[str, int]]:
        """Generate a complete response from Claude."""
        # Extract system message if present
        system_content = None
        api_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                api_messages.append(msg)

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                system=system_content or "",
                messages=api_messages,
            )

            content = response.content[0].text if response.content else ""
            usage = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            }

            return content, usage

        except Exception as e:
            error_msg = self._map_error(e)
            raise RuntimeError(error_msg) from e

    async def stream(
        self, messages: list[dict[str, str]]
    ) -> AsyncIterator[str]:
        """Stream response tokens from Claude."""
        # Extract system message if present
        system_content = None
        api_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                api_messages.append(msg)

        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                system=system_content or "",
                messages=api_messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            error_msg = self._map_error(e)
            raise RuntimeError(error_msg) from e

    def _map_error(self, error: Exception) -> str:
        """Map Anthropic errors to themed messages."""
        error_str = str(error).lower()

        if "authentication" in error_str or "api_key" in error_str:
            return format_error(NostromoError.AUTH_FAILED)
        elif "rate" in error_str or "limit" in error_str:
            return format_error(NostromoError.RATE_LIMITED, seconds="60")
        elif "connection" in error_str or "network" in error_str:
            return format_error(NostromoError.UPLINK_FAILURE)
        else:
            return format_error(NostromoError.PROCESSING_ERROR)
