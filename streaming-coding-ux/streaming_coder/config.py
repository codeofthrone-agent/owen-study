"""
Configuration for the streaming coder module.

Defaults match OpenAB's config.toml exactly for cross-project compatibility.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ReactionEmojis:
    """Emoji mapping for each reaction state."""
    queued: str = "👀"
    thinking: str = "🤔"
    tool: str = "🔥"       # generic tool
    coding: str = "👨‍💻"    # exec/read/write/bash/edit/shell
    web: str = "⚡"         # web_search/web_fetch/browser
    done: str = "🆗"
    error: str = "😱"
    stall_soft: str = "🥱"  # 10s no events
    stall_hard: str = "😨"  # 30s no events

    def as_dict(self) -> Dict[str, str]:
        return {
            "queued": self.queued,
            "thinking": self.thinking,
            "tool": self.tool,
            "coding": self.coding,
            "web": self.web,
            "done": self.done,
            "error": self.error,
        }


@dataclass
class ReactionTiming:
    """Timing thresholds for reaction state transitions (milliseconds)."""
    debounce_ms: int = 700
    stall_soft_ms: int = 10_000   # 10s → 🥱
    stall_hard_ms: int = 30_000   # 30s → 😨
    done_hold_ms: int = 1_500
    error_hold_ms: int = 2_500


@dataclass
class PoolConfig:
    """Session pool settings."""
    max_sessions: int = 10
    session_ttl_hours: int = 24
    cleanup_interval_secs: int = 60


@dataclass
class EditorConfig:
    """Streaming editor settings."""
    update_interval_ms: int = 1_500
    max_display_chars: int = 1_900
    max_message_chars: int = 2_000


@dataclass
class Config:
    """Top-level streaming coder configuration.

    Defaults match OpenAB's config.toml (v0.7.1).
    """
    enabled: bool = True
    reactions: ReactionEmojis = field(default_factory=ReactionEmojis)
    timing: ReactionTiming = field(default_factory=ReactionTiming)
    pool: PoolConfig = field(default_factory=PoolConfig)
    editor: EditorConfig = field(default_factory=EditorConfig)

    # ACP / acpx settings
    acpx_command: str = "acpx"
    acpx_timeout_secs: int = 120
    approve_all: bool = True
    default_model: Optional[str] = None

    # Auth
    # Uses CLAUDE_CODE_OAUTH_TOKEN env var by default
    # (NOT ANTHROPIC_API_KEY — that doesn't work with ACP adapter)

    @classmethod
    def from_env(cls) -> "Config":
        """Build config from environment variables with sensible defaults."""
        cfg = cls()
        if os.environ.get("STREAMING_CODER_DISABLED"):
            cfg.enabled = False
        if val := os.environ.get("STREAMING_CODER_MAX_SESSIONS"):
            cfg.pool.max_sessions = int(val)
        if val := os.environ.get("STREAMING_CODER_TTL_HOURS"):
            cfg.pool.session_ttl_hours = int(val)
        if val := os.environ.get("STREAMING_CODER_UPDATE_MS"):
            cfg.editor.update_interval_ms = int(val)
        if val := os.environ.get("STREAMING_CODER_ACPX_CMD"):
            cfg.acpx_command = val
        if val := os.environ.get("STREAMING_CODER_TIMEOUT"):
            cfg.acpx_timeout_secs = int(val)
        if val := os.environ.get("STREAMING_CODER_MODEL"):
            cfg.default_model = val
        return cfg

    def build_acpx_argv(self, prompt: str, cwd: str = ".") -> list[str]:
        """Build the acpx command-line arguments."""
        argv = [self.acpx_command]
        argv += ["--format", "json", "--json-strict"]
        if self.approve_all:
            argv.append("--approve-all")
        argv += ["--timeout", str(self.acpx_timeout_secs)]
        if self.default_model:
            argv += ["--model", self.default_model]
        argv += ["--cwd", cwd]
        argv += ["claude", "exec", prompt]
        return argv
