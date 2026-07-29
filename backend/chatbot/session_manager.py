"""
session_manager.py

Simple in-memory session store for the chatbot conversation state.
No database, no persistence — suitable for development and demo use.

Session structure:
{
    "answers": {},              # collected answers keyed by question id
    "current_question_id": str  # id of the question currently being asked
}
"""

import uuid
from typing import Optional

_sessions: dict = {}


def create_session(first_question_id: str) -> str:
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "answers": {},
        "current_question_id": first_question_id,
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Return the session dict or None if not found."""
    return _sessions.get(session_id)


def update_session(session_id: str, question_id: str, answer, next_question_id: Optional[str]) -> None:
    """
    Store the answer for question_id and advance current_question_id.
    next_question_id is None when the conversation is complete.
    """
    session = _sessions[session_id]
    session["answers"][question_id] = answer
    session["current_question_id"] = next_question_id


def inject_answer(session_id: str, question_id: str, answer) -> None:
    """Silently inject an answer without changing the current question pointer."""
    _sessions[session_id]["answers"][question_id] = answer
