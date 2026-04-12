"""
StatusReactionController — OpenAB-style emoji reactions with debounce and stall detection.

State machine: 👀(queued) → 🤔(thinking) → 🔥/👨‍💻/⚡(tool) → 🆗+😊(done) → 😱(error)
Plus stall detection: 10s → 🥱, 30s → 😨
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, Awaitable, Callable, Optional

from .config import ReactionEmojis, ReactionTiming

logger = logging.getLogger(__name__)

# ── Tool classification tokens ────────────────────────────────────

CODING_TOKENS = ["exec", "process", "read", "write", "edit", "bash", "shell"]
WEB_TOKENS = ["web_search", "web_fetch", "web-search", "web-fetch", "browser"]

# Random mood faces applied on successful completion
MOOD_FACES = ["😊", "😎", "🫡", "🤓", "😏", "✌️", "💪", "🦾"]


def classify_tool(name: str, emojis: ReactionEmojis) -> str:
    """Classify a tool name and return the appropriate emoji.

    Args:
        name: Tool name/title (e.g. "exec: git status", "web_search", etc.)
        emojis: Emoji configuration.

    Returns:
        The emoji string for this tool category.
    """
    n = name.lower()
    if any(tok in n for tok in WEB_TOKENS):
        return emojis.web
    elif any(tok in n for tok in CODING_TOKENS):
        return emojis.coding
    else:
        return emojis.tool


class StatusReactionController:
    """Manages emoji reactions on a Discord message with debounce and stall detection.

    Args:
        add_reaction: async callable(emoji) -> None — adds a reaction to the message.
        remove_reaction: async callable(emoji) -> None — removes a reaction from the message.
        emojis: Emoji configuration (defaults from OpenAB).
        timing: Timing thresholds (defaults from OpenAB).
        enabled: If False, all operations are no-ops.
    """

    def __init__(
        self,
        add_reaction: Callable[[str], Awaitable[None]],
        remove_reaction: Callable[[str], Awaitable[None]],
        emojis: ReactionEmojis = None,
        timing: ReactionTiming = None,
        enabled: bool = True,
    ):
        self.add_reaction = add_reaction
        self.remove_reaction = remove_reaction
        self.emojis = emojis or ReactionEmojis()
        self.timing = timing or ReactionTiming()
        self.enabled = enabled

        self.current_emoji: str = ""
        self.finished: bool = False

        self._debounce_task: Optional[asyncio.Task] = None
        self._stall_soft_task: Optional[asyncio.Task] = None
        self._stall_hard_task: Optional[asyncio.Task] = None

    # ── Public state transitions ──────────────────────────────────

    async def set_queued(self) -> None:
        """Immediately set 👀 (queued). No debounce."""
        await self._apply_immediate(self.emojis.queued)

    async def set_thinking(self) -> None:
        """Set 🤔 with debounce (700ms default)."""
        await self._schedule_debounced(self.emojis.thinking)

    async def set_tool(self, tool_name: str) -> None:
        """Classify tool and set appropriate emoji with debounce."""
        emoji = classify_tool(tool_name, self.emojis)
        await self._schedule_debounced(emoji)

    async def set_done(self) -> None:
        """Set 🆗 + a random mood face. Immediate."""
        await self._finish(self.emojis.done)
        face = random.choice(MOOD_FACES)
        try:
            await self.add_reaction(face)
        except Exception:
            logger.debug("Failed to add mood face reaction")

    async def set_error(self) -> None:
        """Set 😱. Immediate."""
        await self._finish(self.emojis.error)

    # ── Cleanup ───────────────────────────────────────────────────

    async def cleanup(self) -> None:
        """Cancel all pending timers and reset state."""
        self.finished = True
        self._cancel_all_timers()

    # ── Internal: immediate apply ─────────────────────────────────

    async def _apply_immediate(self, emoji: str) -> None:
        if self.finished or emoji == self.current_emoji:
            return
        self._cancel_debounce()
        old = self.current_emoji
        self.current_emoji = emoji
        try:
            await self.add_reaction(emoji)
        except Exception:
            logger.debug("Failed to add reaction %s", emoji)
        if old and old != emoji:
            try:
                await self.remove_reaction(old)
            except Exception:
                logger.debug("Failed to remove reaction %s", old)
        self._reset_stall_timers()

    # ── Internal: debounced apply ─────────────────────────────────

    async def _schedule_debounced(self, emoji: str) -> None:
        if self.finished:
            return
        if emoji == self.current_emoji:
            self._reset_stall_timers()
            return
        self._cancel_debounce()
        self._debounce_task = asyncio.create_task(self._debounce_apply(emoji))

    async def _debounce_apply(self, emoji: str) -> None:
        try:
            await asyncio.sleep(self.timing.debounce_ms / 1000)
        except asyncio.CancelledError:
            return
        if self.finished:
            return
        old = self.current_emoji
        self.current_emoji = emoji
        try:
            await self.add_reaction(emoji)
        except Exception:
            logger.debug("Failed to add reaction %s", emoji)
        if old and old != emoji:
            try:
                await self.remove_reaction(old)
            except Exception:
                logger.debug("Failed to remove reaction %s", old)
        self._reset_stall_timers()

    # ── Internal: finish ──────────────────────────────────────────

    async def _finish(self, emoji: str) -> None:
        self.finished = True
        self._cancel_all_timers()
        old = self.current_emoji
        self.current_emoji = emoji
        try:
            await self.add_reaction(emoji)
        except Exception:
            logger.debug("Failed to add finish reaction %s", emoji)
        if old and old != emoji:
            try:
                await self.remove_reaction(old)
            except Exception:
                logger.debug("Failed to remove old reaction %s", old)

    # ── Internal: stall timers ────────────────────────────────────

    def _reset_stall_timers(self) -> None:
        self._cancel_stall_timers()
        self._stall_soft_task = asyncio.create_task(
            self._stall_timeout(self.timing.stall_soft_ms / 1000, self.emojis.stall_soft)
        )
        self._stall_hard_task = asyncio.create_task(
            self._stall_timeout(self.timing.stall_hard_ms / 1000, self.emojis.stall_hard)
        )

    async def _stall_timeout(self, delay: float, emoji: str) -> None:
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return
        if self.finished:
            return
        old = self.current_emoji
        self.current_emoji = emoji
        try:
            await self.add_reaction(emoji)
        except Exception:
            logger.debug("Failed to add stall reaction %s", emoji)
        if old and old != emoji:
            try:
                await self.remove_reaction(old)
            except Exception:
                logger.debug("Failed to remove old reaction %s", old)

    # ── Internal: timer cancellation ──────────────────────────────

    def _cancel_debounce(self) -> None:
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        self._debounce_task = None

    def _cancel_stall_timers(self) -> None:
        for task in (self._stall_soft_task, self._stall_hard_task):
            if task and not task.done():
                task.cancel()
        self._stall_soft_task = None
        self._stall_hard_task = None

    def _cancel_all_timers(self) -> None:
        self._cancel_debounce()
        self._cancel_stall_timers()


class StreamingReactionController:
    """Convenience wrapper: builds a StatusReactionController from a Hermes
    Discord adapter and a raw message object.

    The adapter's ``_add_reaction(message, emoji)`` and
    ``_remove_reaction(message, emoji)`` signatures differ from
    StatusReactionController's single-arg callables.  This class
    binds the ``message`` so the resulting interface matches.

    Usage::

        reactions = StreamingReactionController(
            adapter=discord_adapter,
            raw_message=msg,
            emojis=config.reactions,
            timing=config.timing,
        )
        await reactions.set_thinking()
    """

    def __init__(
        self,
        adapter: Any,
        raw_message: Any,
        emojis: Optional["ReactionEmojis"] = None,
        timing: Optional["ReactionTiming"] = None,
        enabled: bool = True,
    ):
        # Bind message into the adapter methods so they become (emoji) -> None
        async def _add(emoji: str) -> None:
            await adapter._add_reaction(raw_message, emoji)

        async def _remove(emoji: str) -> None:
            await adapter._remove_reaction(raw_message, emoji)

        self._inner = StatusReactionController(
            add_reaction=_add,
            remove_reaction=_remove,
            emojis=emojis,
            timing=timing,
            enabled=enabled,
        )

    # ── Delegate public interface ────────────────────────────────

    async def set_queued(self) -> None:
        await self._inner.set_queued()

    async def set_thinking(self) -> None:
        await self._inner.set_thinking()

    async def set_tool(self, tool_name: str) -> None:
        await self._inner.set_tool(tool_name)

    async def set_done(self) -> None:
        await self._inner.set_done()

    async def set_error(self) -> None:
        await self._inner.set_error()

    async def cleanup(self) -> None:
        await self._inner.cleanup()

    @property
    def finished(self) -> bool:
        return self._inner.finished

    @property
    def current_emoji(self) -> str:
        return self._inner.current_emoji
