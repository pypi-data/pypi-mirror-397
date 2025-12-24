"""
Memory store adapters.

In-memory and file-based implementations.
"""

import json
from pathlib import Path

from nostromo_core.models import Session
from nostromo_core.ports.memory import AbstractMemoryStore


class InMemoryStore(AbstractMemoryStore):
    """
    In-memory session storage.

    Sessions are lost when the process exits.
    Useful for testing and ephemeral sessions.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    async def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def save_session(self, session: Session) -> None:
        self._sessions[session.id] = session

    async def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())


class FileMemoryStore(AbstractMemoryStore):
    """
    File-based session storage.

    Sessions are persisted to JSON files in a directory.
    """

    def __init__(self, storage_dir: str | Path) -> None:
        """
        Initialize file storage.

        Args:
            storage_dir: Directory to store session files
        """
        self._storage_dir = Path(storage_dir).expanduser()
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        """Get path for a session file."""
        # Sanitize session ID for filename
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
        return self._storage_dir / f"{safe_id}.json"

    async def get_session(self, session_id: str) -> Session | None:
        path = self._session_path(session_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Session.model_validate(data)
        except (json.JSONDecodeError, Exception):
            return None

    async def save_session(self, session: Session) -> None:
        path = self._session_path(session.id)
        data = session.model_dump(mode="json")
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    async def delete_session(self, session_id: str) -> bool:
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def list_sessions(self) -> list[str]:
        sessions = []
        for path in self._storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if "id" in data:
                    sessions.append(data["id"])
            except (json.JSONDecodeError, Exception):
                continue
        return sessions
