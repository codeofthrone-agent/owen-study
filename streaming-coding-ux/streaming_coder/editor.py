"""
StreamingEditor — OpenAB-style edit-streaming for Discord messages.

Every 1.5s checks if the composed display has changed and edits the
Discord message accordingly. Tracks tool call lines with state icons.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, List, Optional

logger = logging.getLogger(__name__)


class ToolState(Enum):
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class ToolLine:
    """A single tool call display entry."""
    id: str
    title: str
    state: ToolState = ToolState.RUNNING

    @property
    def icon(self) -> str:
        return {
            ToolState.RUNNING: "🔧",
            ToolState.COMPLETED: "✅",
            ToolState.FAILED: "❌",
        }[self.state]

    @property
    def suffix(self) -> str:
        return "..." if self.state == ToolState.RUNNING else ""

    def render(self) -> str:
        safe_title = self.title.replace("\n", " ; ").replace("`", "'")
        return f"{self.icon} `{safe_title}`{self.suffix}"


# Type alias for the edit callback
EditFn = Callable[[Any, str], Awaitable[None]]


class StreamingEditor:
    """Edit-streaming editor: composes tool lines + text and edits Discord message every interval.

    Args:
        edit_fn: async callable(message, content) — performs the Discord message edit.
        message: The Discord message object to edit.
        interval: Seconds between edit checks (default 1.5s).
        max_chars: Truncate display to this many chars (default 1900).
    """

    def __init__(
        self,
        edit_fn: EditFn,
        message: Any,
        interval: float = 1.5,
        max_chars: int = 1900,
    ):
        self.edit_fn = edit_fn
        self.message = message
        self.interval = interval
        self.max_chars = max_chars

        self.text_buf: str = ""
        self.tool_lines: List[ToolLine] = []
        self._last_content: str = ""
        self._task: Optional[asyncio.Task] = None
        self._stopped = False

    def start(self) -> None:
        """Start the background edit-loop task."""
        self._stopped = False
        self._task = asyncio.create_task(self._edit_loop())

    def stop(self) -> None:
        """Cancel the edit-loop task."""
        self._stopped = True
        if self._task and not self._task.done():
            self._task.cancel()

    # ── Mutation methods ──────────────────────────────────────────

    def add_text(self, chunk: str) -> None:
        """Append a text chunk to the display buffer."""
        if chunk:
            self.text_buf += chunk

    def add_tool_start(self, tool_id: str, title: str) -> None:
        """Register a tool call as running. Deduped by tool_id."""
        for tl in self.tool_lines:
            if tl.id == tool_id:
                tl.title = title
                tl.state = ToolState.RUNNING
                return
        self.tool_lines.append(ToolLine(id=tool_id, title=title, state=ToolState.RUNNING))

    def set_tool_done(self, tool_id: str, title: str = "", status: str = "completed") -> None:
        """Mark a tool call as completed or failed."""
        state = ToolState.COMPLETED if status == "completed" else ToolState.FAILED
        for tl in self.tool_lines:
            if tl.id == tool_id:
                if title:
                    tl.title = title
                tl.state = state
                return
        # Tool not found — add it with final state
        self.tool_lines.append(ToolLine(id=tool_id, title=title or tool_id, state=state))

    def clear_text(self) -> None:
        """Reset the text buffer (useful for new-turn resets)."""
        self.text_buf = ""

    def reset(self) -> None:
        """Full reset of editor state."""
        self.text_buf = ""
        self.tool_lines.clear()
        self._last_content = ""

    # ── Compose & display ─────────────────────────────────────────

    def compose_display(self) -> str:
        """Combine tool lines and text buffer into the current display."""
        parts: List[str] = []
        for tl in self.tool_lines:
            parts.append(tl.render())

        out = "\n".join(parts)
        if parts:
            out += "\n\n"
        out += self.text_buf.strip()
        return out

    # TODO: Media output support — when agent generates images or file attachments
    # (detected via "MEDIA:/path/to/file" in stream), extract path and send as
    # Discord attachment via adapter instead of embedding in text display.
    # Requires:
    # 1. Pattern detection in _append_text() for MEDIA: prefix
    # 2. Separate media_queue: List[str] in StreamingEditor
    # 3. adapter.send_file(path) or GatewayStreamConsumer.file_path field

    def truncate_chars(self, text: str, limit: int, ellipsis: str = "…") -> str:
        """Truncate a string to `limit` characters, appending ellipsis if truncated."""
        if len(text) <= limit:
            return text
        return text[:limit] + ellipsis

    def split_final(self, limit: int = 2000) -> List[str]:
        """Split the final composed display into chunks that fit within `limit` chars.

        Used after streaming ends to send any overflow as additional messages.
        """
        content = self.compose_display()
        if len(content) <= limit:
            return [content]

        chunks: List[str] = []
        current = ""
        for line in content.split("\n"):
            # If a single line exceeds limit, hard-split it
            if len(line) > limit:
                if current:
                    chunks.append(current)
                    current = ""
                for i in range(0, len(line), limit):
                    chunks.append(line[i:i + limit])
                continue
            if len(current) + len(line) + 1 > limit:
                if current:
                    chunks.append(current)
                current = ""
            if current:
                current += "\n"
            current += line
        if current:
            chunks.append(current)
        return chunks if chunks else [content[:limit]]

    # ── Internal edit loop ────────────────────────────────────────

    async def _edit_loop(self) -> None:
        """Background task: periodically check for content changes and edit the message."""
        while not self._stopped:
            await asyncio.sleep(self.interval)
            if self._stopped:
                break
            try:
                content = self.compose_display()
                if content == self._last_content:
                    continue
                display = self.truncate_chars(content, self.max_chars)
                await self.edit_fn(self.message, display)
                self._last_content = content
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in edit loop")

    # ── Context manager ───────────────────────────────────────────

    async def __aenter__(self) -> "StreamingEditor":
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
