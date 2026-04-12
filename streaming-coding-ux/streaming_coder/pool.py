"""
Session pool — manages thread_id → acpx session mappings.

Tracks active acpx subprocess sessions keyed by Discord thread ID,
with TTL-based cleanup and max-session limits.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class PoolExhaustedError(Exception):
    """Raised when the session pool has reached max capacity."""


@dataclass
class SessionInfo:
    """Metadata about an active session."""
    thread_id: str
    process: Any  # asyncio.subprocess.Process
    session_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    stdin: Any = None  # asyncio.StreamWriter

    def alive(self) -> bool:
        """Check if the subprocess is still running."""
        return self.process.returncode is None

    def touch(self) -> None:
        """Update last active timestamp."""
        self.last_active = time.time()


class SessionPool:
    """Manages per-thread acpx sessions.

    Args:
        max_sessions: Maximum concurrent sessions (default 10).
        session_ttl_hours: Hours before idle sessions are reaped (default 24).
        cleanup_interval_secs: Seconds between cleanup sweeps (default 60).
    """

    def __init__(
        self,
        max_sessions: int = 10,
        session_ttl_hours: int = 24,
        cleanup_interval_secs: int = 60,
    ):
        self._sessions: Dict[str, SessionInfo] = {}
        self._lock = asyncio.Lock()
        self.max_sessions = max_sessions
        self.session_ttl_secs = session_ttl_hours * 3600
        self.cleanup_interval_secs = cleanup_interval_secs
        self._cleanup_task: Optional[asyncio.Task] = None

    async def get_or_create(
        self,
        thread_id: str,
        factory: Callable[..., Any],
    ) -> SessionInfo:
        """Get existing session or create a new one via factory.

        Args:
            thread_id: Discord thread ID (or channel ID).
            factory: async callable() -> SessionInfo — creates a new session.

        Returns:
            SessionInfo for this thread.
        Raises:
            PoolExhaustedError: If max_sessions reached.
        """
        # Fast path: existing alive session (no lock needed for dict read)
        session = self._sessions.get(thread_id)
        if session and session.alive():
            session.touch()
            return session

        async with self._lock:
            # Double-check after acquiring lock
            session = self._sessions.get(thread_id)
            if session and session.alive():
                session.touch()
                return session

            # Evict dead sessions first
            self._evict_dead()

            if len(self._sessions) >= self.max_sessions:
                raise PoolExhaustedError(
                    f"Session pool exhausted ({self.max_sessions} sessions). "
                    "Please wait for one to finish."
                )

            session = await factory()
            session.thread_id = thread_id
            self._sessions[thread_id] = session
            logger.info("Created session for thread %s", thread_id)
            return session

    async def get(self, thread_id: str) -> Optional[SessionInfo]:
        """Get an existing session (no creation)."""
        session = self._sessions.get(thread_id)
        if session and session.alive():
            session.touch()
            return session
        return None

    async def close(self, thread_id: str) -> None:
        """Close and remove a specific session."""
        async with self._lock:
            session = self._sessions.pop(thread_id, None)
        if session and session.alive():
            try:
                session.process.terminate()
                await asyncio.wait_for(session.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                session.process.kill()
            except Exception:
                logger.exception("Error closing session %s", thread_id)

    async def cleanup_idle(self) -> int:
        """Reap sessions that have been idle longer than TTL.

        Returns:
            Number of sessions reaped.
        """
        now = time.time()
        to_reap = []
        for tid, session in self._sessions.items():
            if not session.alive() or (now - session.last_active) > self.session_ttl_secs:
                to_reap.append(tid)

        for tid in to_reap:
            await self.close(tid)

        if to_reap:
            logger.info("Reaped %d idle sessions", len(to_reap))
        return len(to_reap)

    def _evict_dead(self) -> None:
        """Remove dead sessions from pool (must hold lock)."""
        dead = [tid for tid, s in self._sessions.items() if not s.alive()]
        for tid in dead:
            del self._sessions[tid]
            logger.debug("Evicted dead session %s", tid)

    def start_cleanup_loop(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def stop_cleanup_loop(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(self.cleanup_interval_secs)
            try:
                await self.cleanup_idle()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in cleanup loop")

    async def shutdown(self) -> None:
        """Close all sessions and stop cleanup loop."""
        self.stop_cleanup_loop()
        thread_ids = list(self._sessions.keys())
        for tid in thread_ids:
            await self.close(tid)
        logger.info("Session pool shut down (%d sessions closed)", len(thread_ids))

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.alive())

    @property
    def session_ids(self) -> list:
        return list(self._sessions.keys())
