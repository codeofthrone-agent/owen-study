import pytest
from streaming_coder.pool import SessionPool


@pytest.mark.asyncio
async def test_track_expired_session():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    pool.set_session_name("thread-123", "dc-123456")
    # Simulate TTL expiry
    pool.mark_session_expired("thread-123")
    assert pool.has_expired_session("thread-123") is True
    assert pool.get_session_name("thread-123") == "dc-123456"
    assert pool.get_thread_agent("thread-123") == "claude"


@pytest.mark.asyncio
async def test_resume_clears_expired_flag():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    pool.mark_session_expired("thread-123")
    pool.resume_session("thread-123")
    assert pool.has_expired_session("thread-123") is False
