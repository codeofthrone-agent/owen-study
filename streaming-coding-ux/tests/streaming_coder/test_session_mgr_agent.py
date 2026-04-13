import pytest
from streaming_coder.pool import SessionPool, AcpxSessionManager


@pytest.mark.asyncio
async def test_session_mgr_records_agent():
    pool = SessionPool()
    mgr = AcpxSessionManager(pool, agent="claude")
    await mgr.ensure_session("thread-123")
    assert pool.get_thread_agent("thread-123") == "claude"


@pytest.mark.asyncio
async def test_session_mgr_updates_agent():
    pool = SessionPool()
    mgr = AcpxSessionManager(pool, agent="claude")
    mgr.agent = "gemini"
    name = await mgr.ensure_session("thread-123")
    assert pool.get_thread_agent("thread-123") == "gemini"
