import pytest
from streaming_coder.pool import SessionPool


@pytest.mark.asyncio
async def test_track_agent_per_thread():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    assert pool.get_thread_agent("thread-123") == "claude"
    assert pool.get_thread_agent("thread-456") is None


@pytest.mark.asyncio
async def test_thread_agent_cleared_on_close():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "gemini")
    pool.clear_thread_agent("thread-123")
    assert pool.get_thread_agent("thread-123") is None
