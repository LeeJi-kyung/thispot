"""In-memory session store."""

_sessions: dict[str, dict] = {}


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def set_session(session_id: str, data: dict) -> None:
    _sessions[session_id] = data
