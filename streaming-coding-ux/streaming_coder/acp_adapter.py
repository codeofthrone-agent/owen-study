"""
AcpStreamAdapter — bridges ACP event streams to GatewayStreamConsumer deltas.

Reads AcpEvent objects from an asyncio.Queue (produced by acpx subprocess)
and translates them into text deltas and reaction state changes that
GatewayStreamConsumer can process.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .acp_parser import AcpEvent, AcpEventType

logger = logging.getLogger(__name__)


class AcpStreamAdapter:
    """Convert ACP event stream into GatewayStreamConsumer-compatible deltas.

    This adapter reads from an asyncio.Queue of AcpEvent objects
    (produced by the acpx subprocess stdout parser) and feeds text
    deltas into the consumer's on_delta() method while managing
    reaction state transitions via the reactions controller.

    Usage::

        adapter = AcpStreamAdapter(consumer, reactions)
        await adapter.run(event_queue)
    """

    def __init__(self, consumer, reactions_controller):
        """
        Args:
            consumer: GatewayStreamConsumer instance with on_delta(text) and
                      finish() methods.
            reactions_controller: StreamingReactionController for emoji state
                                  transitions (set_thinking, set_tool, etc.).
        """
        self.consumer = consumer
        self.reactions = reactions_controller
        self._tool_seen: set = set()  # Track tool call IDs we've already reacted to

    async def run(self, event_queue: asyncio.Queue) -> None:
        """Read events from the queue until EOF sentinel (None).

        Each event is routed by type:
        - TEXT_CHUNK: fed as a text delta to the consumer
        - THOUGHT_CHUNK: triggers thinking reaction (text NOT shown)
        - TOOL_CALL: triggers tool-classified reaction
        - TOOL_CALL_UPDATE: resets to thinking on completion
        - ERROR: appended as warning text to the consumer

        Args:
            event_queue: asyncio.Queue yielding AcpEvent objects,
                         terminated by a None sentinel.
        """
        while True:
            event = await event_queue.get()
            if event is None:
                # EOF sentinel — stream complete
                break

            try:
                await self._handle_event(event)
            except Exception:
                logger.exception("Error handling ACP event: %s", event.event_type)

        # Signal consumer that the stream is finished
        try:
            self.consumer.finish()
        except Exception:
            logger.debug("Error signaling consumer finish")

    async def _handle_event(self, event: AcpEvent) -> None:
        """Route a single ACP event to the appropriate handler."""
        etype = event.event_type

        if etype == AcpEventType.TEXT_CHUNK:
            # Streaming text — feed directly to consumer
            if event.text:
                self.consumer.on_delta(event.text)

        elif etype == AcpEventType.THOUGHT_CHUNK:
            # Agent is thinking — set reaction but don't show text
            await self.reactions.set_thinking()

        elif etype == AcpEventType.TOOL_CALL:
            # Tool started — classify and set reaction
            tool_name = event.tool_title or event.tool_kind or "tool"
            await self.reactions.set_tool(tool_name)
            self._tool_seen.add(event.tool_call_id)

        elif etype == AcpEventType.TOOL_CALL_UPDATE:
            # Tool progress/completion
            if event.tool_status in ("completed", "failed"):
                # Tool done — back to thinking
                await self.reactions.set_thinking()
            elif event.tool_call_id not in self._tool_seen:
                # First time seeing this tool — show reaction
                tool_name = event.tool_title or event.tool_kind or "tool"
                await self.reactions.set_tool(tool_name)
                self._tool_seen.add(event.tool_call_id)

        elif etype == AcpEventType.ERROR:
            # Error — append warning to display
            if event.error_message:
                self.consumer.on_delta(f"\n⚠️ {event.error_message}")

        # RAW, RESULT, SESSION_NEW, USAGE_UPDATE, etc. — silently ignore
        # (RESULT triggers the None sentinel above via the caller)
