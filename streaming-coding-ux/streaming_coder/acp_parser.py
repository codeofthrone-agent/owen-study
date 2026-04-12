"""
ACP JSON-RPC line parser.

Parses one JSON line from acpx stdout into a typed AcpEvent.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class AcpEventType(Enum):
    """Classification of ACP notification events."""
    TEXT_CHUNK = auto()       # agent_message_chunk — streaming text
    THOUGHT_CHUNK = auto()    # agent_thought_chunk — thinking
    TOOL_CALL = auto()        # tool_call — tool started
    TOOL_CALL_UPDATE = auto() # tool_call_update — tool progress/completed/failed
    USAGE_UPDATE = auto()     # usage_update — token/cost
    AVAILABLE_COMMANDS = auto()  # available_commands_update — initial
    ERROR = auto()            # error response
    RESULT = auto()           # final result response
    SESSION_INIT = auto()     # initialize response
    SESSION_NEW = auto()      # session/new response
    SESSION_PROMPT = auto()   # session/prompt request (outbound)
    RAW = auto()              # unclassified


@dataclass
class AcpEvent:
    """Parsed ACP event from one JSON-RPC line."""
    event_type: AcpEventType
    raw: Dict[str, Any] = field(default_factory=dict)

    # For TEXT_CHUNK / THOUGHT_CHUNK
    text: str = ""

    # For TOOL_CALL / TOOL_CALL_UPDATE
    tool_call_id: str = ""
    tool_title: str = ""
    tool_status: str = ""   # "running", "completed", "failed"
    tool_kind: str = ""     # tool kind string from ACP

    # For USAGE_UPDATE
    token_count: int = 0
    cost_usd: float = 0.0

    # For RESULT / ERROR
    result_type: str = ""   # "end_turn", "error", etc.
    error_message: str = ""
    error_code: int = 0

    # For SESSION_INIT / SESSION_NEW
    session_id: str = ""
    agent_name: str = ""


def _extract_text_from_update(update_obj: Dict[str, Any]) -> str:
    """Extract text from ACP update object content field.

    ACP agent_message_chunk has: update.content = {"type": "text", "text": "..."}
    """
    content = update_obj.get("content", {})
    if isinstance(content, dict):
        return content.get("text", "")
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if isinstance(block, dict))
    if isinstance(content, str):
        return content
    return ""


def _extract_text(data: Dict[str, Any]) -> str:
    """Extract text from content block structures.

    ACP content can be:
    - {"type": "text", "text": "..."}
    - {"text": "..."}  (shorthand)
    - A list of such blocks
    """
    params = data.get("params", data)
    content = params.get("content", params)

    # If content is a list of blocks
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
        return "".join(parts)

    # If content is a single block dict
    if isinstance(content, dict):
        return content.get("text", "")

    # If params itself has text
    if isinstance(params, dict) and "text" in params:
        return params["text"]

    return ""


def parse_acp_line(line: str) -> Optional[AcpEvent]:
    """Parse a single JSON-RPC line into an AcpEvent.

    Returns None for empty/invalid lines.
    """
    line = line.strip()
    if not line:
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        logger.debug("Non-JSON line: %r", line[:100])
        return None

    if not isinstance(data, dict):
        return None

    return classify_message(data)


def classify_message(data: Dict[str, Any]) -> AcpEvent:
    """Classify a parsed JSON-RPC message into an AcpEvent."""

    # --- Responses (have "id" + "result" or "error") ---

    # Error response
    if "error" in data:
        err = data["error"]
        return AcpEvent(
            event_type=AcpEventType.ERROR,
            raw=data,
            error_message=err.get("message", ""),
            error_code=err.get("code", 0),
        )

    # Result response
    if "result" in data and "id" in data:
        result = data["result"]
        resp = AcpEvent(event_type=AcpEventType.RESULT, raw=data)

        # Session/new
        if "sessionId" in result:
            resp.event_type = AcpEventType.SESSION_NEW
            resp.session_id = result["sessionId"]
            return resp

        # Initialize
        if "agentInfo" in result or "serverInfo" in result:
            resp.event_type = AcpEventType.SESSION_INIT
            info = result.get("agentInfo") or result.get("serverInfo") or {}
            resp.agent_name = info.get("name", "")
            return resp

        # Prompt result
        resp.result_type = result.get("type", result.get("stopReason", ""))
        return resp

    # --- Notifications / Requests (have "method") ---

    method = data.get("method", "")

    # session/update notifications
    if method == "session/update":
        params = data.get("params", {})
        # ACP nests sessionUpdate inside params.update, not directly in params
        update_obj = params.get("update", params)
        update_type = update_obj.get("sessionUpdate", "")

        if update_type == "agent_message_chunk":
            return AcpEvent(
                event_type=AcpEventType.TEXT_CHUNK,
                raw=data,
                text=_extract_text_from_update(update_obj),
            )

        if update_type == "agent_thought_chunk":
            return AcpEvent(
                event_type=AcpEventType.THOUGHT_CHUNK,
                raw=data,
                text=_extract_text_from_update(update_obj),
            )

        if update_type == "tool_call":
            tool_id = update_obj.get("toolCallId", "")
            title = update_obj.get("title", update_obj.get("toolName", ""))
            return AcpEvent(
                event_type=AcpEventType.TOOL_CALL,
                raw=data,
                tool_call_id=tool_id,
                tool_title=title,
                tool_status="running",
                tool_kind=update_obj.get("toolName", update_obj.get("kind", "")),
            )

        if update_type == "tool_call_update":
            tool_id = update_obj.get("toolCallId", "")
            title = update_obj.get("title", "")
            status = update_obj.get("status", "completed")
            if isinstance(status, dict):
                status = status.get("kind", status.get("status", "completed"))
            return AcpEvent(
                event_type=AcpEventType.TOOL_CALL_UPDATE,
                raw=data,
                tool_call_id=tool_id,
                tool_title=title,
                tool_status=status,
            )

        if update_type == "usage_update":
            used = update_obj.get("used", 0)
            size = update_obj.get("size", 0)
            cost_obj = update_obj.get("cost", {})
            cost = 0.0
            if isinstance(cost_obj, dict):
                cost = float(cost_obj.get("amount", 0))
            elif isinstance(cost_obj, (int, float)):
                cost = float(cost_obj)
            return AcpEvent(
                event_type=AcpEventType.USAGE_UPDATE,
                raw=data,
                token_count=used,
                cost_usd=cost,
            )

        if update_type == "available_commands_update":
            return AcpEvent(
                event_type=AcpEventType.AVAILABLE_COMMANDS,
                raw=data,
            )

        # Unknown update type
        return AcpEvent(event_type=AcpEventType.RAW, raw=data)

    # session/prompt (outbound request)
    if method == "session/prompt":
        return AcpEvent(event_type=AcpEventType.SESSION_PROMPT, raw=data)

    # session/request_permission
    if method == "session/request_permission":
        # This is handled specially by the connection layer
        return AcpEvent(event_type=AcpEventType.RAW, raw=data)

    # Fallback
    return AcpEvent(event_type=AcpEventType.RAW, raw=data)


def is_tool_event(event: AcpEvent) -> bool:
    """Check if this event represents tool activity."""
    return event.event_type in (
        AcpEventType.TOOL_CALL,
        AcpEventType.TOOL_CALL_UPDATE,
    )


def is_text_event(event: AcpEvent) -> bool:
    """Check if this event is streaming text content."""
    return event.event_type in (
        AcpEventType.TEXT_CHUNK,
        AcpEventType.THOUGHT_CHUNK,
    )
