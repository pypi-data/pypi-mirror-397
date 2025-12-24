"""
ChatEngine - Core domain logic for chat processing.

This module contains no I/O dependencies - all external
interactions happen through injected ports.
"""

from collections.abc import AsyncIterator
from datetime import datetime

from nostromo_core.models import ChatResponse, Message, MessageRole, Session
from nostromo_core.ports.llm import AbstractLLMProvider
from nostromo_core.ports.memory import AbstractMemoryStore
from nostromo_core.theme.prompts import get_system_prompt


class ChatEngine:
    """
    Core chat engine implementing the business logic.

    Uses dependency injection for LLM provider and memory store,
    enabling different adapters for CLI, API, or embedded use.
    """

    def __init__(
        self,
        llm: AbstractLLMProvider,
        memory: AbstractMemoryStore,
        system_prompt: str | None = None,
    ) -> None:
        """
        Initialize the chat engine.

        Args:
            llm: LLM provider adapter (Anthropic, OpenAI, etc.)
            memory: Memory store adapter (in-memory, file, Redis, etc.)
            system_prompt: Optional custom system prompt. Uses default MU-TH-UR prompt if None.
        """
        self.llm = llm
        self.memory = memory
        self.system_prompt = system_prompt or get_system_prompt()

    async def chat(self, session_id: str, user_input: str) -> ChatResponse:
        """
        Process a chat message and return the full response.

        Args:
            session_id: Unique identifier for the conversation session.
            user_input: The user's message.

        Returns:
            ChatResponse containing the assistant's message and metadata.
        """
        # Get or create session
        session = await self.memory.get_session(session_id)
        if session is None:
            session = Session(id=session_id)
            # Add system prompt as first message
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=self.system_prompt,
            )
            session.add_message(system_message)

        # Add user message
        user_message = Message(
            role=MessageRole.USER,
            content=user_input,
            timestamp=datetime.now(),
        )
        session.add_message(user_message)

        # Generate response
        messages = session.get_api_messages()
        response_content, usage = await self.llm.generate(messages)

        # Add assistant message
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response_content,
            timestamp=datetime.now(),
        )
        session.add_message(assistant_message)

        # Save session
        await self.memory.save_session(session)

        return ChatResponse(
            message=assistant_message,
            session_id=session_id,
            provider=self.llm.provider_name,
            model=self.llm.model_name,
            usage=usage,
        )

    async def chat_stream(
        self, session_id: str, user_input: str
    ) -> AsyncIterator[str]:
        """
        Process a chat message and stream the response token by token.

        Args:
            session_id: Unique identifier for the conversation session.
            user_input: The user's message.

        Yields:
            String tokens as they are generated.
        """
        # Get or create session
        session = await self.memory.get_session(session_id)
        if session is None:
            session = Session(id=session_id)
            # Add system prompt
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=self.system_prompt,
            )
            session.add_message(system_message)

        # Add user message
        user_message = Message(
            role=MessageRole.USER,
            content=user_input,
            timestamp=datetime.now(),
        )
        session.add_message(user_message)

        # Stream response
        messages = session.get_api_messages()
        full_response = ""

        async for token in self.llm.stream(messages):
            full_response += token
            yield token

        # Add assistant message after streaming completes
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=full_response,
            timestamp=datetime.now(),
        )
        session.add_message(assistant_message)

        # Save session
        await self.memory.save_session(session)

    async def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        return await self.memory.get_session(session_id)

    async def list_sessions(self) -> list[str]:
        """List all session IDs."""
        return await self.memory.list_sessions()

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return await self.memory.delete_session(session_id)

    async def clear_session(self, session_id: str) -> bool:
        """Clear messages from a session but keep it."""
        session = await self.memory.get_session(session_id)
        if session is None:
            return False

        # Keep only system message
        session.messages = [
            m for m in session.messages if m.role == MessageRole.SYSTEM
        ]
        session.updated_at = datetime.now()
        await self.memory.save_session(session)
        return True
