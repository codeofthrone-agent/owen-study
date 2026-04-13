"""
Hermes integration bridge — connects streaming_coder to the Hermes Discord gateway.

Provides:
- Trigger detection for "派 Claude" / "丢 codex" style commands
- Session mode triggers for persistent multi-turn conversations
- acpx subprocess management with streaming
- Stream orchestration: editor + reactions + parser integration
- Async-to-sync bridge for running inside Hermes's agent thread pool
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, Optional, Tuple

from .acp_parser import AcpEvent, AcpEventType, parse_acp_line
from .config import Config
from .editor import StreamingEditor
from .pool import SessionInfo, SessionPool, AcpxSessionManager
from .reactions import StatusReactionController

logger = logging.getLogger(__name__)

# ── Trigger types ─────────────────────────────────────────────────


class TriggerMode(Enum):
    """How the agent should be invoked."""
    ONE_SHOT = auto()    # Fire-and-forget, no context persistence
    SESSION = auto()     # Persistent named session (thread-bound)
    SESSION_NEW = auto() # Reset session (equivalent to /new)
    SESSION_CANCEL = auto()  # Cancel running task
    STATUS = auto()       # Query session status


@dataclass
class TriggerResult:
    """Parsed trigger from a message."""
    agent: str               # e.g. "gemini", "claude"
    mode: TriggerMode        # one-shot or session
    prompt: str              # The user's task (empty for cancel/new without prompt)
    raw: str                 # Original matched text


# ── Agent name ────────────────────────────────────────────────────

SUPPORTED_AGENTS = {"claude", "gemini", "codex", "opencode"}

# ── Resume patterns (continuation after timeout) ──────────────────

RESUME_PATTERNS = [
    re.compile(r"^(?:繼續|resume|go\s*on|接着?)$", re.IGNORECASE),
]

# ── Trigger detection patterns ────────────────────────────────────
#
# Pattern priority (first match wins):
#   1. Session cancel  — "派 gemini cancel" / "ask claude cancel"
#   2. Session new     — "派 gemini session new" / "ask claude new session"
#   3. Session mode    — "派 gemini session xxx" / "ask claude session xxx"
#   4. One-shot        — "派 gemini xxx" / "ask claude xxx"
#
# ── Session Cancel ────────────────────────────────────────────────

CANCEL_PATTERNS = [
    # Chinese: 取消/停/cancel
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:取消|停|cancel)",
        re.IGNORECASE,
    ),
    # Chinese: 結束/end/done/完成
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:結束|end|done|完成)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s+(?:cancel|stop|end|done|finish)",
        re.IGNORECASE,
    ),
    re.compile(
        r"@(claude|gemini|codex|opencode)\s+(?:取消|停|cancel|stop|結束|end|finish)",
        re.IGNORECASE,
    ),
]

# ── Session New (reset) ───────────────────────────────────────────

NEW_SESSION_PATTERNS = [
    # Chinese: 新對話/重來/重新/new session
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:session\s+)?(?:新對話|重來|重新|new)\s*(.*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+session\s+new\s*(.*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s+(?:new session|reset session|start over)\s*(.*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"@(claude|gemini|codex|opencode)\s+(?:新對話|重來|重新|new session|reset)\s*(.*)",
        re.IGNORECASE,
    ),
]

# ── Session Mode (persistent conversation) ────────────────────────

SESSION_PATTERNS = [
    # Chinese: 派 gemini session xxx
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:對話|session)\s*(.*)",
        re.IGNORECASE,
    ),
    # English: ask claude session xxx
    re.compile(
        r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s+session\s*(.*)",
        re.IGNORECASE,
    ),
    # @mention: @gemini session xxx
    re.compile(
        r"@(claude|gemini|codex|opencode)\s+(?:對話|session)\s*(.*)",
        re.IGNORECASE,
    ),
]

# ── Status (query session state) ─────────────────────────────────

STATUS_PATTERNS = [
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:狀態|status|session\?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"@(claude|gemini|codex|opencode)\s+(?:狀態|status)",
        re.IGNORECASE,
    ),
]

# ── One-shot (fire-and-forget) ────────────────────────────────────

ONE_SHOT_PATTERNS = [
    # Chinese trigger words — handle optional 給/给 after the verb
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s*(.*)",
        re.IGNORECASE,
    ),
    # English trigger words
    re.compile(
        r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s*(.*)",
        re.IGNORECASE,
    ),
    # @mention style
    re.compile(
        r"@(claude|gemini|codex|opencode)\s*(.*)",
        re.IGNORECASE,
    ),
]


def detect_trigger(text: str) -> Optional[TriggerResult]:
    """Detect agent trigger mode from a message.

    Scans patterns in priority order:
      cancel → session new → session → one-shot

    Args:
        text: The message content.

    Returns:
        TriggerResult if a valid trigger is detected, None otherwise.
    """
    text = text.strip()

    # 0. Resume
    for pattern in RESUME_PATTERNS:
        m = pattern.match(text)
        if m:
            return TriggerResult(
                agent="",  # Will be filled from pool.get_thread_agent()
                mode=TriggerMode.SESSION,
                prompt="請繼續之前的工作",  # Generic resume prompt
                raw=m.group(0),
            )

    # 1. Cancel
    for pattern in CANCEL_PATTERNS:
        m = pattern.match(text)
        if m:
            agent = m.group(1).lower()
            if agent in SUPPORTED_AGENTS:
                return TriggerResult(
                    agent=agent,
                    mode=TriggerMode.SESSION_CANCEL,
                    prompt="",
                    raw=m.group(0),
                )

    # 1.5. Status
    for pattern in STATUS_PATTERNS:
        m = pattern.match(text)
        if m:
            agent = m.group(1).lower()
            if agent in SUPPORTED_AGENTS:
                return TriggerResult(
                    agent=agent,
                    mode=TriggerMode.STATUS,
                    prompt="",
                    raw=m.group(0),
                )

    # 2. Session New
    for pattern in NEW_SESSION_PATTERNS:
        m = pattern.match(text)
        if m:
            agent = m.group(1).lower()
            prompt = (m.group(2) or "").strip()
            if agent in SUPPORTED_AGENTS:
                return TriggerResult(
                    agent=agent,
                    mode=TriggerMode.SESSION_NEW,
                    prompt=prompt,
                    raw=m.group(0),
                )

    # 3. Session Mode
    for pattern in SESSION_PATTERNS:
        m = pattern.match(text)
        if m:
            agent = m.group(1).lower()
            prompt = (m.group(2) or "").strip()
            if agent in SUPPORTED_AGENTS and prompt:
                return TriggerResult(
                    agent=agent,
                    mode=TriggerMode.SESSION,
                    prompt=prompt,
                    raw=m.group(0),
                )

    # 4. One-shot
    for pattern in ONE_SHOT_PATTERNS:
        m = pattern.match(text)
        if m:
            agent = m.group(1).lower()
            prompt = (m.group(2) or "").strip()
            if agent in SUPPORTED_AGENTS and prompt:
                return TriggerResult(
                    agent=agent,
                    mode=TriggerMode.ONE_SHOT,
                    prompt=prompt,
                    raw=m.group(0),
                )

    return None


# ── Backward compat: old detect_agent_trigger ─────────────────────

# Legacy patterns (kept for backward compat with existing code)
TRIGGER_PATTERNS = [
    re.compile(r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
    re.compile(r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
    re.compile(r"@(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
]


def detect_agent_trigger(text: str) -> Optional[Tuple[str, str]]:
    """Detect if a message triggers an external coding agent (legacy API).

    Args:
        text: The message content.

    Returns:
        (agent_name, prompt) if a trigger is detected, None otherwise.
    """
    result = detect_trigger(text)
    if result and result.mode == TriggerMode.ONE_SHOT and result.prompt:
        return (result.agent, result.prompt)
    return None


# ── acpx subprocess management ────────────────────────────────────


async def spawn_acpx(
    argv: list,
    env: Optional[Dict[str, str]] = None,
) -> SessionInfo:
    """Spawn an acpx subprocess.

    Args:
        argv: Full command line (including "acpx").
        env: Additional environment variables.

    Returns:
        SessionInfo wrapping the subprocess.
    """
    full_env = dict(os.environ)
    if env:
        full_env.update(env)

    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
        env=full_env,
    )
    return SessionInfo(
        thread_id="",  # Will be set by pool
        process=proc,
        stdin=proc.stdin,
    )


# ── Stream orchestration ──────────────────────────────────────────


async def stream_acpx_output(
    session: SessionInfo,
    editor: StreamingEditor,
    reactions: StatusReactionController,
    on_text: Optional[Callable[[str], None]] = None,
) -> AcpEvent:
    """Read acpx stdout line-by-line, parse events, update editor + reactions.

    Args:
        session: Active acpx session.
        editor: StreamingEditor for display composition.
        reactions: StatusReactionController for emoji management.
        on_text: Optional callback for raw text chunks (for logging).

    Returns:
        The final AcpEvent (RESULT or ERROR).
    """
    stdout = session.process.stdout
    final_event = AcpEvent(event_type=AcpEventType.RAW)

    while True:
        try:
            raw_line = await asyncio.wait_for(stdout.readline(), timeout=120)
        except asyncio.TimeoutError:
            logger.warning("acpx stdout timeout — no output for 120s")
            break

        if not raw_line:
            break  # EOF

        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line:
            continue

        event = parse_acp_line(line)
        if event is None:
            continue

        session.touch()

        # Route event to editor + reactions
        if event.event_type == AcpEventType.TEXT_CHUNK:
            # TODO: Scan event.text for "MEDIA:/path/to/file" patterns.
            # If found, extract path and queue for Discord attachment send
            # via adapter.send_file() after streaming completes.
            editor.add_text(event.text)
            if on_text:
                on_text(event.text)
            await reactions.set_thinking()

        elif event.event_type == AcpEventType.THOUGHT_CHUNK:
            await reactions.set_thinking()

        elif event.event_type == AcpEventType.TOOL_CALL:
            editor.add_tool_start(event.tool_call_id, event.tool_title)
            await reactions.set_tool(event.tool_title or event.tool_kind)

        elif event.event_type == AcpEventType.TOOL_CALL_UPDATE:
            if event.tool_status in ("completed", "failed"):
                editor.set_tool_done(event.tool_call_id, event.tool_title, event.tool_status)
                await reactions.set_thinking()
            else:
                editor.add_tool_start(event.tool_call_id, event.tool_title)
                await reactions.set_tool(event.tool_title or event.tool_kind)

        elif event.event_type == AcpEventType.USAGE_UPDATE:
            logger.debug(
                "Usage: %d tokens, $%.4f", event.token_count, event.cost_usd
            )

        elif event.event_type in (AcpEventType.RESULT, AcpEventType.ERROR):
            final_event = event
            break

        elif event.event_type == AcpEventType.SESSION_NEW:
            session.session_id = event.session_id
            logger.info("ACP session: %s", session.session_id)

    return final_event


# ── Dispatcher: route TriggerResult to correct handler ─────────────


async def _handle_session_status(
    session_mgr: AcpxSessionManager,
    chat_id: str,
    agent: str,
) -> Dict[str, Any]:
    """Return session status for this thread."""
    pool = session_mgr.pool
    session = pool._sessions.get(chat_id)

    if session and session.alive():
        elapsed = time.time() - session.last_active
        status_text = (
            f"🟢 Session 活躍中\n"
            f"Agent: {agent}\n"
            f"Session: `{session.acpx_session_name or 'unnamed'}`\n"
            f"閒置: {int(elapsed)}s"
        )
    elif pool.has_expired_session(chat_id):
        session_name = pool.get_session_name(chat_id)
        status_text = (
            f"🟡 Session 已超時（可 resume）\n"
            f"Agent: {agent}\n"
            f"Session: `{session_name}`\n"
            f"說「繼續」可恢復"
        )
    else:
        status_text = "⚫ 無活躍 session"

    return {"success": True, "text": status_text, "mode": "status"}


async def dispatch_trigger(
    trigger: TriggerResult,
    adapter: Any,
    reactions: Any,
    session_mgr: AcpxSessionManager,
    chat_id: str,
    message_id: str,
    workdir: str = ".",
    config: Optional[Config] = None,
) -> Dict[str, Any]:
    """Route a TriggerResult to the correct handler (one-shot / session / cancel).

    Args:
        trigger: Parsed trigger from detect_trigger().
        adapter: Hermes DiscordAdapter.
        reactions: StreamingReactionController.
        session_mgr: AcpxSessionManager for session lifecycle.
        chat_id: Discord channel/thread ID.
        message_id: Placeholder message ID to edit.
        workdir: Working directory.
        config: Optional Config.

    Returns:
        Dict with result info.
    """
    # Auth validation — check before dispatching
    if trigger.mode != TriggerMode.SESSION_CANCEL:
        if config is None:
            config = Config()
        auth_error = config.validate_agent_auth(trigger.agent)
        if auth_error:
            return {
                "success": False,
                "text": auth_error,
                "mode": "auth_error",
            }

    if trigger.mode == TriggerMode.SESSION_CANCEL:
        cancelled = await session_mgr.cancel(chat_id)
        return {
            "success": True,
            "text": "✅ 已取消" if cancelled else "⚠️ 沒有正在執行的任務",
            "mode": "cancel",
        }

    elif trigger.mode == TriggerMode.SESSION_NEW:
        # Reset session, then run prompt if provided
        session_name = await session_mgr.reset(chat_id)
        if trigger.prompt:
            return await run_session_task(
                thread_id=chat_id,
                agent=trigger.agent,
                prompt=trigger.prompt,
                adapter=adapter,
                reactions=reactions,
                session_mgr=session_mgr,
                chat_id=chat_id,
                message_id=message_id,
                workdir=workdir,
                config=config,
                is_new=False,  # Already reset above
            )
        return {
            "success": True,
            "text": f"🔄 已重置 session: `{session_name}`，請開始新的對話",
            "mode": "session_new",
            "session_name": session_name,
        }

    elif trigger.mode == TriggerMode.SESSION:
        return await run_session_task(
            thread_id=chat_id,
            agent=trigger.agent,
            prompt=trigger.prompt,
            adapter=adapter,
            reactions=reactions,
            session_mgr=session_mgr,
            chat_id=chat_id,
            message_id=message_id,
            workdir=workdir,
            config=config,
            is_new=False,
        )

    elif trigger.mode == TriggerMode.STATUS:
        return await _handle_session_status(
            session_mgr=session_mgr,
            chat_id=chat_id,
            agent=trigger.agent,
        )

    else:  # ONE_SHOT
        return await run_streaming_task_adapter(
            agent=trigger.agent,
            prompt=trigger.prompt,
            chat_id=chat_id,
            message_id=message_id,
            adapter=adapter,
            reactions=reactions,
            workdir=workdir,
            config=config,
        )


# ── Legacy entry points ───────────────────────────────────────────


def run_streaming_task(
    loop: asyncio.AbstractEventLoop,
    config: Config,
    agent: str,
    prompt: str,
    message: Any,
    edit_fn: Callable,
    add_reaction_fn: Callable,
    remove_reaction_fn: Callable,
    cwd: str = ".",
    thread_id: str = "",
    pool: Optional[SessionPool] = None,
) -> asyncio.Task:
    """Launch a streaming task on the event loop (thread-safe)."""
    coro = _run_streaming_async(
        config=config,
        agent=agent,
        prompt=prompt,
        message=message,
        edit_fn=edit_fn,
        add_reaction_fn=add_reaction_fn,
        remove_reaction_fn=remove_reaction_fn,
        cwd=cwd,
        thread_id=thread_id,
        pool=pool,
    )
    return asyncio.run_coroutine_threadsafe(coro, loop)


async def _run_streaming_async(
    config: Config,
    agent: str,
    prompt: str,
    message: Any,
    edit_fn: Callable,
    add_reaction_fn: Callable,
    remove_reaction_fn: Callable,
    cwd: str = ".",
    thread_id: str = "",
    pool: Optional[SessionPool] = None,
) -> Dict[str, Any]:
    """Full async streaming flow (legacy)."""
    editor = StreamingEditor(edit_fn=edit_fn, message=message)
    reactions = StatusReactionController(
        add_reaction=add_reaction_fn,
        remove_reaction=remove_reaction_fn,
        emojis=config.reactions,
        timing=config.timing,
    )

    result = {"success": False, "text": "", "error": "", "session_id": ""}

    try:
        argv = config.build_acpx_argv(prompt, cwd=cwd)
        logger.info("Spawning: %s", " ".join(argv[:6]) + " ...")

        session = await spawn_acpx(argv)
        if thread_id and pool:
            session.thread_id = thread_id

        await reactions.set_queued()
        editor.start()

        final_event = await stream_acpx_output(session, editor, reactions)

        editor.stop()

        chunks = editor.split_final(config.editor.max_message_chars)
        if chunks:
            await edit_fn(message, chunks[0])

        if final_event.event_type == AcpEventType.RESULT:
            await reactions.set_done()
            result["success"] = True
        else:
            await reactions.set_error()
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["session_id"] = session.session_id or ""
        result["chunks"] = chunks

        if session.alive():
            try:
                session.process.terminate()
            except Exception as e:
                logger.debug(f"[streaming_coder] non-critical error: {e}")

    except Exception as e:
        logger.exception("Streaming task failed")
        editor.stop()
        try:
            await reactions.set_error()
        except Exception as e:
            logger.debug(f"[streaming_coder] non-critical error: {e}")
        result["error"] = str(e)

    return result


# ── Adapter-based async entry point ─────────────────────────────


async def run_streaming_task_adapter(
    agent: str,
    prompt: str,
    chat_id: str,
    message_id: str,
    adapter: Any,
    reactions: Any,
    workdir: str = ".",
    config: Optional[Config] = None,
) -> Dict[str, Any]:
    """Run a one-shot streaming coding task using the Hermes adapter API."""
    cfg = config or Config()
    editor_cfg = cfg.editor

    async def edit_fn(_msg: Any, content: str) -> None:
        await adapter.edit_message(chat_id, message_id, content)

    editor = StreamingEditor(
        edit_fn=edit_fn,
        message=None,
        interval=editor_cfg.update_interval_ms / 1000.0,
        max_chars=editor_cfg.max_display_chars,
    )

    result: Dict[str, Any] = {
        "success": False,
        "text": "",
        "error": "",
        "session_id": "",
    }

    try:
        argv = cfg.build_acpx_argv(prompt, cwd=workdir)
        logger.info("Spawning (adapter): %s ...", " ".join(argv[:6]))

        session = await spawn_acpx(argv)

        await reactions.set_queued()
        editor.start()

        final_event = await stream_acpx_output(session, editor, reactions)

        editor.stop()

        chunks = editor.split_final(editor_cfg.max_message_chars)
        if chunks:
            await edit_fn(None, chunks[0])
        for chunk in chunks[1:]:
            await adapter.send(chat_id, chunk, metadata={"thread_id": chat_id})

        if final_event.event_type == AcpEventType.RESULT:
            result["success"] = True
        else:
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["session_id"] = session.session_id or ""
        result["chunks"] = chunks

        if session.alive():
            try:
                session.process.terminate()
            except Exception as e:
                logger.debug(f"[streaming_coder] non-critical error: {e}")

    except Exception as e:
        logger.exception("Adapter streaming task failed")
        editor.stop()
        try:
            await reactions.set_error()
        except Exception as e:
            logger.debug(f"[streaming_coder] non-critical error: {e}")
        result["error"] = str(e)

    return result


# ── Session task entry point ──────────────────────────────────────


async def run_session_task(
    thread_id: str,
    agent: str,
    prompt: str,
    adapter: Any,
    reactions: Any,
    session_mgr: AcpxSessionManager,
    chat_id: str = "",
    message_id: str = "",
    workdir: str = ".",
    config: Optional[Config] = None,
    is_new: bool = False,
) -> Dict[str, Any]:
    """Run a streaming task using a persistent acpx named session."""
    cfg = config or Config()
    editor_cfg = cfg.editor
    if not chat_id:
        chat_id = thread_id

    if is_new:
        session_name = await session_mgr.reset(thread_id)
    else:
        session_name = await session_mgr.ensure_session(thread_id)

    async def edit_fn(_msg: Any, content: str) -> None:
        await adapter.edit_message(chat_id, message_id, content)

    editor = StreamingEditor(
        edit_fn=edit_fn,
        message=None,
        interval=editor_cfg.update_interval_ms / 1000.0,
        max_chars=editor_cfg.max_display_chars,
    )

    result: Dict[str, Any] = {
        "success": False,
        "text": "",
        "error": "",
        "session_name": session_name,
    }

    try:
        argv = session_mgr.build_acpx_argv(
            thread_id=thread_id,
            prompt=prompt,
            cwd=workdir,
            approve_all=cfg.approve_all,
            timeout=cfg.acpx_timeout_secs,
        )
        logger.info("Session task: agent=%s session=%s prompt=%s...",
                     agent, session_name, prompt[:40])

        session = await spawn_acpx(argv)
        session.thread_id = thread_id
        session.acpx_session_name = session_name
        session.agent_name = agent

        await reactions.set_queued()
        editor.start()

        final_event = await stream_acpx_output(session, editor, reactions)

        editor.stop()

        chunks = editor.split_final(editor_cfg.max_message_chars)
        if chunks:
            await edit_fn(None, chunks[0])
        for chunk in chunks[1:]:
            await adapter.send(chat_id, chunk, metadata={"thread_id": chat_id})

        if final_event.event_type == AcpEventType.RESULT:
            await reactions.set_done()
            result["success"] = True
        else:
            await reactions.set_error()
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["chunks"] = chunks

    except Exception as e:
        logger.exception("Session task failed for thread %s", thread_id)
        editor.stop()
        try:
            await reactions.set_error()
        except Exception as e:
            logger.debug(f"[streaming_coder] non-critical error: {e}")
        result["error"] = str(e)

    return result
