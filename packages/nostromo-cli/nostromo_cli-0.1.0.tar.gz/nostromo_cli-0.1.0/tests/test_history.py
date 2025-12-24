"""Tests for history manager."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from nostromo_core.models import Message, MessageRole, Session
from nostromo_cli.history import HistoryManager


@pytest.fixture
def temp_history_dir():
    """Create a temporary history directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_session():
    """Create a sample session."""
    return Session(
        id="test-session",
        messages=[
            Message(role=MessageRole.SYSTEM, content="You are a test."),
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi there!"),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_save_and_load_session(temp_history_dir: Path, sample_session: Session):
    """Test saving and loading a session."""
    manager = HistoryManager(temp_history_dir)

    manager.save_session(sample_session)
    loaded = manager.load_session("test-session")

    assert loaded is not None
    assert loaded.id == sample_session.id
    assert len(loaded.messages) == 3


def test_delete_session(temp_history_dir: Path, sample_session: Session):
    """Test deleting a session."""
    manager = HistoryManager(temp_history_dir)

    manager.save_session(sample_session)
    assert manager.load_session("test-session") is not None

    result = manager.delete_session("test-session")
    assert result is True
    assert manager.load_session("test-session") is None


def test_list_sessions(temp_history_dir: Path):
    """Test listing sessions."""
    manager = HistoryManager(temp_history_dir)

    for i in range(3):
        session = Session(id=f"session-{i}")
        manager.save_session(session)

    sessions = manager.list_sessions()
    assert len(sessions) == 3


def test_clear_all(temp_history_dir: Path):
    """Test clearing all history."""
    manager = HistoryManager(temp_history_dir)

    for i in range(5):
        session = Session(id=f"session-{i}")
        manager.save_session(session)

    count = manager.clear_all()
    assert count == 5
    assert len(manager.list_sessions()) == 0


def test_max_sessions_cleanup(temp_history_dir: Path):
    """Test that old sessions are cleaned up."""
    manager = HistoryManager(temp_history_dir, max_sessions=3)

    for i in range(5):
        session = Session(id=f"session-{i}")
        manager.save_session(session)

    sessions = manager.list_sessions()
    assert len(sessions) <= 3
