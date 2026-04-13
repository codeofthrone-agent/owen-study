"""End-to-end test for the session lifecycle (mocked acpx)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from streaming_coder.bridge import detect_trigger, dispatch_trigger, TriggerMode
from streaming_coder.pool import SessionPool, AcpxSessionManager


def test_trigger_detection_lifecycle():
    """Verify all trigger patterns work."""
    # One-shot
    r = detect_trigger("派 Claude 修 bug")
    assert r.mode == TriggerMode.ONE_SHOT
    assert r.agent == "claude"

    # Session
    r = detect_trigger("派 Claude session 做 refactor")
    assert r.mode == TriggerMode.SESSION

    # Session new
    r = detect_trigger("派 Claude 新對話")
    assert r.mode == TriggerMode.SESSION_NEW

    # Cancel
    r = detect_trigger("派 Claude 結束")
    assert r.mode == TriggerMode.SESSION_CANCEL

    # Status
    r = detect_trigger("派 Claude 狀態")
    assert r.mode == TriggerMode.STATUS

    # No trigger
    assert detect_trigger("hello world") is None
    assert detect_trigger("把 model 改掉") is None


@pytest.mark.asyncio
async def test_follow_up_detection():
    """Thread follow-up routing."""
    pool = SessionPool()
    pool.set_thread_agent("thread-1", "claude")

    # Has active session → should detect follow-up
    assert pool.has_active_session("thread-1") is True
    assert pool.get_thread_agent("thread-1") == "claude"

    # No active session
    assert pool.has_active_session("thread-999") is False


@pytest.mark.asyncio
async def test_session_resume():
    """Session expiry → resume."""
    pool = SessionPool()
    pool.set_thread_agent("thread-1", "gemini")
    pool.set_session_name("thread-1", "dc-thread-1")
    pool.mark_session_expired("thread-1")

    assert pool.has_expired_session("thread-1") is True
    assert pool.get_session_name("thread-1") == "dc-thread-1"
    assert pool.get_thread_agent("thread-1") == "gemini"
