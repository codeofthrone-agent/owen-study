"""
streaming_coder — OpenAB-style streaming UX for Hermes.

Provides real-time Discord message editing, emoji reactions with debounce/stall
detection, tool call visualization, and session pooling — all driven by
acpx ACP JSON-RPC streaming.

Quick start:
    from streaming_coder import Config, StreamingEditor, StatusReactionController
    from streaming_coder import SessionPool, AcpEvent, AcpEventType
    from streaming_coder.bridge import detect_agent_trigger, run_streaming_task
"""

from .config import Config, EditorConfig, PoolConfig, ReactionEmojis, ReactionTiming
from .editor import StreamingEditor, ToolLine, ToolState
from .reactions import StatusReactionController, StreamingReactionController, classify_tool
from .pool import SessionInfo, SessionPool, PoolExhaustedError, AcpxSessionManager
from .acp_parser import AcpEvent, AcpEventType, parse_acp_line, classify_message
from .acp_adapter import AcpStreamAdapter
from .bridge import (
    detect_agent_trigger,
    spawn_acpx,
    stream_acpx_output,
    run_streaming_task,
    run_streaming_task_adapter,
    run_session_task,
)

__version__ = "0.1.0"

__all__ = [
    # Config
    "Config",
    "EditorConfig",
    "PoolConfig",
    "ReactionEmojis",
    "ReactionTiming",
    # Editor
    "StreamingEditor",
    "ToolLine",
    "ToolState",
    # Reactions
    "StatusReactionController",
    "StreamingReactionController",
    "classify_tool",
    # Pool
    "SessionInfo",
    "SessionPool",
    "PoolExhaustedError",
    "AcpxSessionManager",
    # Parser
    "AcpEvent",
    "AcpEventType",
    "parse_acp_line",
    "classify_message",
    # ACP Adapter
    "AcpStreamAdapter",
    # Bridge
    "detect_agent_trigger",
    "spawn_acpx",
    "stream_acpx_output",
    "run_streaming_task",
    "run_streaming_task_adapter",
    "run_session_task",
]
