"""
Hermes integration bridge — connects streaming_coder to the Hermes Discord gateway.

Provides:
- Trigger detection for "派 Claude" / "丢 codex" style commands
- acpx subprocess management with streaming
- Stream orchestration: editor + reactions + parser integration
- Async-to-sync bridge for running inside Hermes's agent thread pool
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any, Callable, Dict, Optional, Tuple

from .acp_parser import AcpEvent, AcpEventType, parse_acp_line
from .config import Config
from .editor import StreamingEditor
from .pool import SessionInfo, SessionPool, AcpxSessionManager
from .reactions import StatusReactionController

logger = logging.getLogger(__name__)

# ── Trigger detection patterns ────────────────────────────────────

# Matches: "派 Claude ...", "丢 codex ...", "ask gemini ...", "send to claude ..."
TRIGGER_PATTERNS = [
    # Chinese trigger words — handle optional 給/给 after the verb
    re.compile(r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
    # English trigger words
    re.compile(r"(?:ask|send to|tell|have)\s*(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
    # @mention style
    re.compile(r"@(claude|gemini|codex|opencode)\s*(.*)", re.IGNORECASE),
]

SUPPORTED_AGENTS = {"claude", "gemini", "codex", "opencode"}


def detect_agent_trigger(text: str) -> Optional[Tuple[str, str]]:
    """Detect if a message triggers an external coding agent.

    Args:
        text: The message content.

    Returns:
        (agent_name, prompt) if a trigger is detected, None otherwise.
    """
    text = text.strip()
    for pattern in TRIGGER_PATTERNS:
        match = pattern.match(text)
        if match:
            agent = match.group(1).lower()
            prompt = match.group(2).strip()
            if agent in SUPPORTED_AGENTS and prompt:
                return (agent, prompt)
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
            editor.add_text(event.text)
            if on_text:
                on_text(event.text)
            await reactions.set_thinking()

        elif event.event_type == AcpEventType.THOUGHT_CHUNK:
            # Thinking text — don't show in editor, just reaction
            await reactions.set_thinking()

        elif event.event_type == AcpEventType.TOOL_CALL:
            editor.add_tool_start(event.tool_call_id, event.tool_title)
            await reactions.set_tool(event.tool_title or event.tool_kind)

        elif event.event_type == AcpEventType.TOOL_CALL_UPDATE:
            if event.tool_status in ("completed", "failed"):
                editor.set_tool_done(event.tool_call_id, event.tool_title, event.tool_status)
                await reactions.set_thinking()
            else:
                # Running/progress update
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
    """Launch a streaming task on the event loop (thread-safe).

    This is the main entry point from a sync context (Hermes agent thread pool).
    Uses asyncio.run_coroutine_threadsafe to schedule on the gateway's event loop.

    Args:
        loop: The asyncio event loop (from the gateway).
        config: Streaming coder configuration.
        agent: Agent name ("claude", "gemini", "codex").
        prompt: The user's task prompt.
        message: Discord message object to edit.
        edit_fn: async (message, content) — edit message.
        add_reaction_fn: async (emoji) — add reaction.
        remove_reaction_fn: async (emoji) — remove reaction.
        cwd: Working directory for acpx.
        thread_id: Discord thread/channel ID for session pool.
        pool: Optional SessionPool for reuse.

    Returns:
        The asyncio.Task (for cancellation if needed).
    """
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
    """Full async streaming flow.

    Returns a result dict with:
        - success: bool
        - text: str (final text)
        - error: str (if failed)
        - session_id: str
    """
    editor = StreamingEditor(edit_fn=edit_fn, message=message)
    reactions = StatusReactionController(
        add_reaction=add_reaction_fn,
        remove_reaction=remove_reaction_fn,
        emojis=config.reactions,
        timing=config.timing,
    )

    result = {"success": False, "text": "", "error": "", "session_id": ""}

    try:
        # Build acpx command
        argv = config.build_acpx_argv(prompt, cwd=cwd)
        logger.info("Spawning: %s", " ".join(argv[:6]) + " ...")

        # Spawn subprocess
        session = await spawn_acpx(argv)
        if thread_id and pool:
            session.thread_id = thread_id

        # Set initial reaction
        await reactions.set_queued()

        # Start editor loop
        editor.start()

        # Stream output
        final_event = await stream_acpx_output(session, editor, reactions)

        # Stop editor
        editor.stop()

        # Final edit with full content
        chunks = editor.split_final(config.editor.max_message_chars)
        if chunks:
            await edit_fn(message, chunks[0])

        # Send overflow chunks as new messages (via edit_fn returns, or second callback)
        # This is left to the integration layer — we just expose the chunks.

        # Final reaction
        if final_event.event_type == AcpEventType.RESULT:
            await reactions.set_done()
            result["success"] = True
        else:
            await reactions.set_error()
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["session_id"] = session.session_id or ""
        result["chunks"] = chunks

        # Clean up process
        if session.alive():
            try:
                session.process.terminate()
            except Exception:
                pass

    except Exception as e:
        logger.exception("Streaming task failed")
        editor.stop()
        try:
            await reactions.set_error()
        except Exception:
            pass
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
    """Run a streaming coding task using the Hermes adapter API.

    This is the async entry point called directly from the gateway's
    ``_handle_streaming_coding_task`` method.  It uses the adapter's
    ``edit_message(chat_id, message_id, content)`` for live editing
    instead of the older callback-based approach.

    Args:
        agent: Agent name ("claude", "gemini", "codex").
        prompt: The user's task prompt.
        chat_id: Discord channel/thread ID for sending messages.
        message_id: Placeholder message ID to edit in-place.
        adapter: Hermes DiscordAdapter instance (provides edit_message, send).
        reactions: StreamingReactionController for emoji state management.
        workdir: Working directory for acpx subprocess.
        config: Optional Config; uses defaults if None.

    Returns:
        Dict with keys: success (bool), text (str), error (str),
        chunks (list[str]), session_id (str).
    """
    cfg = config or Config()
    editor_cfg = cfg.editor

    # Build the edit callback that the StreamingEditor will invoke
    async def edit_fn(_msg: Any, content: str) -> None:
        await adapter.edit_message(chat_id, message_id, content)

    # Create editor — message=None since we use chat_id/message_id via edit_fn
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
        # Spawn acpx subprocess
        argv = cfg.build_acpx_argv(prompt, cwd=workdir)
        logger.info("Spawning (adapter): %s ...", " ".join(argv[:6]))

        session = await spawn_acpx(argv)

        # Set initial reaction
        await reactions.set_queued()

        # Start editor background loop
        editor.start()

        # Stream output — reuses existing stream_acpx_output which handles
        # all ACP event types, editor updates, and reaction management
        final_event = await stream_acpx_output(session, editor, reactions)

        # Stop editor
        editor.stop()

        # Final edit with composed display
        chunks = editor.split_final(editor_cfg.max_message_chars)
        if chunks:
            await edit_fn(None, chunks[0])

        # Send overflow chunks as follow-up messages in the same channel
        for chunk in chunks[1:]:
            await adapter.send(chat_id, chunk, metadata={"thread_id": chat_id})

        # Build result
        if final_event.event_type == AcpEventType.RESULT:
            result["success"] = True
        else:
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["session_id"] = session.session_id or ""
        result["chunks"] = chunks

        # Clean up process
        if session.alive():
            try:
                session.process.terminate()
            except Exception:
                pass

    except Exception as e:
        logger.exception("Adapter streaming task failed")
        editor.stop()
        try:
            await reactions.set_error()
        except Exception:
            pass
        result["error"] = str(e)

    return result


# ── Named-session entry point (with /new, cancel, follow-up support) ──


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
    """Run a streaming task using a persistent acpx named session.

    Supports:
    - First prompt: auto-creates named session
    - Follow-up prompts: reuses session (has context!)
    - is_new=True: resets session (equivalent to /new)
    - Cancel: call session_mgr.cancel(thread_id) externally

    Args:
        thread_id: Discord thread ID (used as session key).
        agent: Agent name (claude/gemini/opencode/codex).
        prompt: The user's prompt.
        adapter: Hermes DiscordAdapter (edit_message, send).
        reactions: StreamingReactionController.
        session_mgr: AcpxSessionManager for session lifecycle.
        chat_id: Discord channel ID (defaults to thread_id).
        message_id: Placeholder message ID to edit.
        workdir: Working directory.
        config: Optional Config.
        is_new: If True, reset session before running.

    Returns:
        Dict with: success, text, error, chunks, session_name.
    """
    cfg = config or Config()
    editor_cfg = cfg.editor
    if not chat_id:
        chat_id = thread_id

    # Ensure session exists (or reset if /new)
    if is_new:
        session_name = await session_mgr.reset(thread_id)
    else:
        session_name = await session_mgr.ensure_session(thread_id)

    # Build edit callback
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
        # Build acpx argv targeting named session
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

        # Final edit
        chunks = editor.split_final(editor_cfg.max_message_chars)
        if chunks:
            await edit_fn(None, chunks[0])
        for chunk in chunks[1:]:
            await adapter.send(chat_id, chunk, metadata={"thread_id": chat_id})

        # Result
        if final_event.event_type == AcpEventType.RESULT:
            await reactions.set_done()
            result["success"] = True
        else:
            await reactions.set_error()
            result["error"] = final_event.error_message or "Unknown error"

        result["text"] = editor.compose_display()
        result["chunks"] = chunks

        # Don't kill the process — let the named session persist for follow-ups
        # Just let the one-shot subprocess exit naturally

    except Exception as e:
        logger.exception("Session task failed for thread %s", thread_id)
        editor.stop()
        try:
            await reactions.set_error()
        except Exception:
            pass
        result["error"] = str(e)

    return result
