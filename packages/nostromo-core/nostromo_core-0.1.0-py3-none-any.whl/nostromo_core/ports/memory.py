"""
Abstract Memory Store interface.

All memory/storage adapters must implement this interface.
"""

from abc import ABC, abstractmethod

from nostromo_core.models import Session


class AbstractMemoryStore(ABC):
    """
    Abstract base class for session/memory storage.

    Implementations can use in-memory storage, files,
    Redis, databases, etc.
    """

    @abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """
        Retrieve a session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session if found, None otherwise
        """
        ...

    @abstractmethod
    async def save_session(self, session: Session) -> None:
        """
        Save or update a session.

        Args:
            session: Session to save
        """
        ...

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    @abstractmethod
    async def list_sessions(self) -> list[str]:
        """
        List all session IDs.

        Returns:
            List of session IDs
        """
        ...

    async def clear_all(self) -> int:
        """
        Clear all sessions.

        Returns:
            Number of sessions deleted
        """
        sessions = await self.list_sessions()
        count = 0
        for session_id in sessions:
            if await self.delete_session(session_id):
                count += 1
        return count
