import pytest


@pytest.fixture(autouse=True)
def clear_gemini_key(monkeypatch):
    """Unit tests use HSV fallback — no real Gemini API calls."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
