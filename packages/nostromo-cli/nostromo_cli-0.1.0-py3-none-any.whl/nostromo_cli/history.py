"""
History Manager - Chat history persistence.

Manages saving and loading of chat sessions to disk.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nostromo_core.models import Message, MessageRole, Session


class HistoryManager:
    """
    Manages persistent chat history.

    Stores sessions as JSON files in the history directory.
    """

    def __init__(self, history_dir: str | Path, max_sessions: int = 100) -> None:
        """
        Initialize history manager.

        Args:
            history_dir: Directory to store history files
            max_sessions: Maximum number of sessions to retain
        """
        self._history_dir = Path(history_dir).expanduser()
        self._max_sessions = max_sessions
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure history directory exists."""
        self._history_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        """Get path for a session file."""
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
        return self._history_dir / f"{safe_id}.json"

    def _session_to_dict(self, session: Session) -> dict[str, Any]:
        """Convert session to serializable dictionary."""
        return {
            "id": session.id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "metadata": session.metadata,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
                for msg in session.messages
            ],
        }

    def _dict_to_session(self, data: dict[str, Any]) -> Session:
        """Convert dictionary to Session object."""
        messages = [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                metadata=msg.get("metadata", {}),
            )
            for msg in data.get("messages", [])
        ]

        return Session(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
            messages=messages,
        )

    def save_session(self, session: Session) -> None:
        """
        Save a session to disk.

        Args:
            session: Session to save
        """
        path = self._session_path(session.id)
        data = self._session_to_dict(session)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._cleanup_old_sessions()

    def load_session(self, session_id: str) -> Session | None:
        """
        Load a session from disk.

        Args:
            session_id: Session ID to load

        Returns:
            Session if found, None otherwise
        """
        path = self._session_path(session_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._dict_to_session(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from disk.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_sessions(self) -> list[dict[str, Any]]:
        """
        List all sessions with metadata.

        Returns:
            List of session info dictionaries
        """
        sessions = []
        for path in self._history_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sessions.append(
                    {
                        "id": data["id"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by updated_at, most recent first
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def get_latest_session_id(self) -> str | None:
        """
        Get the most recently updated session ID.

        Returns:
            Session ID or None if no sessions exist
        """
        sessions = self.list_sessions()
        if sessions:
            return sessions[0]["id"]
        return None

    def _cleanup_old_sessions(self) -> None:
        """Remove old sessions if over limit."""
        sessions = self.list_sessions()
        if len(sessions) > self._max_sessions:
            for session_info in sessions[self._max_sessions :]:
                self.delete_session(session_info["id"])

    def clear_all(self) -> int:
        """
        Clear all history.

        Returns:
            Number of sessions deleted
        """
        count = 0
        for path in self._history_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count


# Global instance
_history_manager: HistoryManager | None = None


def get_history_manager(history_dir: str | Path | None = None) -> HistoryManager:
    """Get or create the history manager."""
    global _history_manager
    if _history_manager is None or history_dir:
        from nostromo_cli.config import DATA_DIR

        _history_manager = HistoryManager(history_dir or DATA_DIR / "history")
    return _history_manager
