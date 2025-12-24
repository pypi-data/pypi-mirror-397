"""Tests for ChatEngine."""

import pytest

from nostromo_core import ChatEngine, Message
from nostromo_core.adapters.memory import InMemoryStore
from nostromo_core.models import MessageRole
from nostromo_core.ports.llm import AbstractLLMProvider


class MockLLMProvider(AbstractLLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, response: str = "ACKNOWLEDGED."):
        self._response = response

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-model"

    async def generate(self, messages: list[dict[str, str]]) -> tuple[str, dict[str, int]]:
        return self._response, {"input": 10, "output": 5}

    async def stream(self, messages: list[dict[str, str]]):
        for word in self._response.split():
            yield word + " "


@pytest.fixture
def engine():
    """Create a test engine."""
    return ChatEngine(
        llm=MockLLMProvider(),
        memory=InMemoryStore(),
        system_prompt="You are a test assistant.",
    )


@pytest.mark.asyncio
async def test_chat_creates_session(engine: ChatEngine):
    """Test that chat creates a new session."""
    response = await engine.chat("test-session", "Hello")

    assert response.session_id == "test-session"
    assert response.message.content == "ACKNOWLEDGED."
    assert response.provider == "mock"


@pytest.mark.asyncio
async def test_chat_preserves_history(engine: ChatEngine):
    """Test that chat preserves message history."""
    await engine.chat("test-session", "First message")
    await engine.chat("test-session", "Second message")

    session = await engine.get_session("test-session")
    assert session is not None
    # System + 2 user + 2 assistant = 5 messages
    assert len(session.messages) == 5


@pytest.mark.asyncio
async def test_chat_stream(engine: ChatEngine):
    """Test streaming response."""
    tokens = []
    async for token in engine.chat_stream("stream-session", "Hello"):
        tokens.append(token)

    assert len(tokens) > 0
    assert "".join(tokens).strip() == "ACKNOWLEDGED."


@pytest.mark.asyncio
async def test_delete_session(engine: ChatEngine):
    """Test session deletion."""
    await engine.chat("delete-me", "Hello")
    assert await engine.get_session("delete-me") is not None

    result = await engine.delete_session("delete-me")
    assert result is True
    assert await engine.get_session("delete-me") is None


@pytest.mark.asyncio
async def test_list_sessions(engine: ChatEngine):
    """Test listing sessions."""
    await engine.chat("session-1", "Hello")
    await engine.chat("session-2", "World")

    sessions = await engine.list_sessions()
    assert "session-1" in sessions
    assert "session-2" in sessions


@pytest.mark.asyncio
async def test_clear_session_keeps_system_prompt(engine: ChatEngine):
    """Test that clearing session keeps the system prompt."""
    await engine.chat("clear-me", "Hello")

    result = await engine.clear_session("clear-me")
    assert result is True

    session = await engine.get_session("clear-me")
    assert session is not None
    assert len(session.messages) == 1
    assert session.messages[0].role == MessageRole.SYSTEM
