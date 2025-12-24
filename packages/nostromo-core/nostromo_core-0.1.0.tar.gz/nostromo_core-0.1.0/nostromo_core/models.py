"""
Pydantic models for chat domain.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of a message in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A single message in a conversation."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_api_format(self) -> dict[str, str]:
        """Convert to format expected by LLM APIs."""
        return {"role": self.role.value, "content": self.content}


class ChatResponse(BaseModel):
    """Response from the chat engine."""

    message: Message
    session_id: str
    provider: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """A chat session with message history."""

    id: str
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_api_messages(self, include_system: bool = True) -> list[dict[str, str]]:
        """Get messages in API format."""
        messages = self.messages
        if not include_system:
            messages = [m for m in messages if m.role != MessageRole.SYSTEM]
        return [m.to_api_format() for m in messages]


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str | None = None


class UserConfig(BaseModel):
    """User interface preferences."""

    typing_effect: bool = True
    typing_speed: int = 50  # chars per second
    uppercase_responses: bool = False
    history_enabled: bool = True
    history_path: str = "~/.local/share/nostromo/history.json"
    history_max_entries: int = 1000
