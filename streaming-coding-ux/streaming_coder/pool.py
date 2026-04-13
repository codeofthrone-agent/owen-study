"""
Session pool — manages thread_id → acpx session mappings.

Tracks active acpx subprocess sessions keyed by Discord thread ID,
with TTL-based cleanup and max-session limits.

Also manages acpx named sessions (persistent ACP sessions with context)
via `acpx {agent} sessions` commands.
"""

from __future__ import annotations

import asyncio
import atexit
import logging
import signal
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
    acpx_session_name: Optional[str] = None  # Named session in acpx
    agent_name: str = "claude"
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
        self._thread_agents: Dict[str, str] = {}  # thread_id → agent_name
        self._expired_sessions: Dict[str, str] = {}  # thread_id → session_name
        self._lock = asyncio.Lock()
        self.max_sessions = max_sessions
        self.session_ttl_secs = session_ttl_hours * 3600
        self.cleanup_interval_secs = cleanup_interval_secs
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutting_down = False

        # Register atexit handler for orphan cleanup
        atexit.register(self._emergency_cleanup)

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

    def set_thread_agent(self, thread_id: str, agent: str) -> None:
        """Record which agent a thread is using."""
        self._thread_agents[thread_id] = agent.lower()

    def get_thread_agent(self, thread_id: str) -> Optional[str]:
        """Get the agent name for an active thread session, or None."""
        return self._thread_agents.get(thread_id)

    def clear_thread_agent(self, thread_id: str) -> None:
        """Clear agent mapping when session ends."""
        self._thread_agents.pop(thread_id, None)

    def has_active_session(self, thread_id: str) -> bool:
        """Check if this thread has an active streaming session."""
        return thread_id in self._thread_agents

    def set_session_name(self, thread_id: str, session_name: str) -> None:
        """Record the acpx session name for a thread (for resume)."""
        self._expired_sessions[thread_id] = session_name

    def mark_session_expired(self, thread_id: str) -> None:
        """Mark a session as expired (process dead, named session persists)."""
        if thread_id not in self._expired_sessions:
            self._expired_sessions[thread_id] = self.thread_to_session_name(thread_id)

    def has_expired_session(self, thread_id: str) -> bool:
        """Check if thread has an expired but resumable session."""
        return thread_id in self._expired_sessions

    def get_session_name(self, thread_id: str) -> Optional[str]:
        """Get the acpx session name for a thread."""
        return self._expired_sessions.get(thread_id)

    def resume_session(self, thread_id: str) -> None:
        """Clear expired flag (session is active again)."""
        self._expired_sessions.pop(thread_id, None)

    async def close(self, thread_id: str) -> None:
        """Close and remove a specific session."""
        async with self._lock:
            session = self._sessions.pop(thread_id, None)
        self._thread_agents.pop(thread_id, None)
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
            # Record session name for resume before closing
            session = self._sessions.get(tid)
            if session and session.acpx_session_name:
                self._expired_sessions[tid] = session.acpx_session_name
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
        if self._shutting_down:
            return
        self._shutting_down = True
        self.stop_cleanup_loop()
        thread_ids = list(self._sessions.keys())
        for tid in thread_ids:
            session = self._sessions.get(tid)
            if session and session.alive():
                try:
                    session.process.terminate()
                    try:
                        await asyncio.wait_for(session.process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        logger.warning("Session %s did not terminate in 5s, killing", tid)
                        session.process.kill()
                        await asyncio.wait_for(session.process.wait(), timeout=2)
                except Exception:
                    logger.exception("Error closing session %s during shutdown", tid)
            self._sessions.pop(tid, None)
        logger.info("Session pool shut down (%d sessions closed)", len(thread_ids))

    def _emergency_cleanup(self) -> None:
        """Synchronous atexit handler — kill all remaining subprocesses.

        This is a last resort for orphan process prevention when the
        Gateway crashes or exits without calling async shutdown().
        """
        killed = 0
        for tid, session in list(self._sessions.items()):
            if session and session.alive():
                try:
                    session.process.kill()
                    killed += 1
                except Exception:
                    pass
        if killed:
            logger.warning("Emergency cleanup: killed %d orphan acpx processes", killed)

    @staticmethod
    def thread_to_session_name(thread_id: str) -> str:
        """Convert a Discord thread ID to an acpx session name.

        Args:
            thread_id: Discord thread/channel ID.

        Returns:
            Sanitized session name safe for acpx.
        """
        return f"dc-{thread_id}"

    async def ensure_named_session(
        self,
        thread_id: str,
        agent: str = "claude",
    ) -> str:
        """Ensure an acpx named session exists for this thread.

        Creates a new named session if one doesn't exist.
        Uses `acpx {agent} sessions new --name {name}`.

        Args:
            thread_id: Discord thread ID.
            agent: Agent name (claude/gemini/opencode/codex).

        Returns:
            The acpx session name.
        """
        session_name = self.thread_to_session_name(thread_id)

        # Check if we already have this session tracked
        session = self._sessions.get(thread_id)
        if session and session.acpx_session_name == session_name:
            return session_name

        # Create the named session via acpx
        try:
            proc = await asyncio.create_subprocess_exec(
                "acpx", agent, "sessions", "new", "--name", session_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                logger.info(
                    "Created acpx session %s for thread %s (agent=%s)",
                    session_name, thread_id, agent,
                )
            else:
                logger.warning(
                    "Failed to create acpx session %s: %s",
                    session_name, stderr.decode(errors="replace"),
                )
        except Exception:
            logger.exception("Error creating acpx session %s", session_name)

        return session_name

    async def close_named_session(
        self,
        thread_id: str,
        agent: str = "claude",
    ) -> None:
        """Close an acpx named session for this thread.

        Uses `acpx {agent} sessions close {name}`.

        Args:
            thread_id: Discord thread ID.
            agent: Agent name.
        """
        session_name = self.thread_to_session_name(thread_id)

        try:
            proc = await asyncio.create_subprocess_exec(
                "acpx", agent, "sessions", "close", session_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            logger.info("Closed acpx session %s", session_name)
        except Exception:
            logger.exception("Error closing acpx session %s", session_name)

        # Also close the subprocess tracking
        await self.close(thread_id)

    async def cancel_active_prompt(
        self,
        thread_id: str,
        agent: str = "claude",
    ) -> bool:
        """Cancel the active prompt in an acpx session.

        Uses `acpx {agent} cancel` and also terminates the subprocess.

        Args:
            thread_id: Discord thread ID.
            agent: Agent name.

        Returns:
            True if a session was cancelled, False if no active session.
        """
        session = self._sessions.get(thread_id)
        had_active = session is not None and session.alive()

        # Kill the subprocess if running
        if had_active:
            await self.close(thread_id)

        # Also send acpx cancel (in case there's a queued prompt)
        try:
            proc = await asyncio.create_subprocess_exec(
                "acpx", agent, "cancel",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
        except Exception:
            logger.debug("acpx cancel failed (may be expected)")

        return had_active

    async def new_session(
        self,
        thread_id: str,
        agent: str = "claude",
    ) -> str:
        """Start a fresh session for this thread (close old + create new).

        Equivalent to /new in Discord.

        Args:
            thread_id: Discord thread ID.
            agent: Agent name.

        Returns:
            The new acpx session name.
        """
        # Close old session if any
        old_session = self._sessions.get(thread_id)
        if old_session and old_session.alive():
            await self.close(thread_id)

        # Also close old named session
        await self.close_named_session(thread_id, agent)

        # Create fresh session
        return await self.ensure_named_session(thread_id, agent)

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.alive())

    @property
    def session_ids(self) -> list:
        return list(self._sessions.keys())


class AcpxSessionManager:
    """High-level session manager for Discord thread → acpx session lifecycle.

    Combines SessionPool with acpx named session management.

    Usage::

        mgr = AcpxSessionManager(pool, agent="gemini")
        # First prompt in thread → creates named session
        await mgr.start_task(thread_id, prompt)
        # Follow-up → reuses same session (has context)
        await mgr.start_task(thread_id, follow_up)
        # /new → resets session
        await mgr.reset(thread_id)
        # Cancel running task
        await mgr.cancel(thread_id)
    """

    def __init__(self, pool: SessionPool, agent: str = "claude"):
        self.pool = pool
        self.agent = agent

    async def ensure_session(self, thread_id: str) -> str:
        """Ensure named session exists, return session name."""
        self.pool.set_thread_agent(thread_id, self.agent)
        return await self.pool.ensure_named_session(thread_id, self.agent)

    async def cancel(self, thread_id: str) -> bool:
        """Cancel active prompt in this thread's session."""
        return await self.pool.cancel_active_prompt(thread_id, self.agent)

    async def reset(self, thread_id: str) -> str:
        """Reset session (close + new). Equivalent to /new."""
        return await self.pool.new_session(thread_id, self.agent)

    async def close(self, thread_id: str) -> None:
        """Permanently close this thread's session."""
        await self.pool.close_named_session(thread_id, self.agent)
        self.pool.clear_thread_agent(thread_id)

    def get_session_name(self, thread_id: str) -> str:
        """Get the acpx session name for a thread (no creation)."""
        return self.pool.thread_to_session_name(thread_id)

    def build_acpx_argv(
        self,
        thread_id: str,
        prompt: str,
        cwd: str = ".",
        approve_all: bool = True,
        timeout: int = 120,
    ) -> list[str]:
        """Build acpx argv for a named session prompt.

        Uses `-s session_name` to target the persistent session.

        Args:
            thread_id: Discord thread ID.
            prompt: The user's prompt.
            cwd: Working directory.
            approve_all: Auto-approve all permissions.
            timeout: Timeout in seconds.

        Returns:
            Command argv list.
        """
        session_name = self.get_session_name(thread_id)
        argv = ["acpx", "--format", "json", "--json-strict"]
        if approve_all:
            argv.append("--approve-all")
        argv += ["--timeout", str(timeout)]
        argv += [self.agent, "-s", session_name, prompt]
        return argv
