"""
Configuration for the streaming coder module.

Defaults match OpenAB's config.toml exactly for cross-project compatibility.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


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
    host_home: str = "/Users/owen"  # Real machine HOME for auth (keychain, config files)

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

    # ── Auth validation ──────────────────────────────────────────────

    AGENT_AUTH_VARS = {
        "claude": {
            "env_var": "CLAUDE_CODE_OAUTH_TOKEN",
            "guide": "請先執行 `claude setup-token` 設定 OAuth token（格式 sk-ant-oat01-...）",
        },
        "gemini": {
            "env_var": "GEMINI_OAUTH_FILE",
            "default_path": "~/.gemini/oauth_creds.json",
            "guide": "請先執行 `gemini` CLI 完成 OAuth 登入，憑證位於 ~/.gemini/oauth_creds.json",
        },
        "codex": {
            "env_var": "OPENAI_API_KEY",
            "guide": "請先設定 OPENAI_API_KEY 環境變數",
        },
        "opencode": {
            "env_var": "OPENCODE_AUTH",
            "guide": "請先設定 OpenCode 的 Copilot OAuth 憑證",
        },
    }

    def validate_agent_auth(self, agent: str) -> Optional[str]:
        """Check if the agent's auth credentials are available.

        Returns:
            None if auth is OK, or an error message string with guidance.
        """
        agent = agent.lower()
        info = self.AGENT_AUTH_VARS.get(agent)
        if not info:
            return f"⚠️ 未知的 agent: `{agent}`（支援: {', '.join(SUPPORTED_AGENTS) if 'SUPPORTED_AGENTS' in dir() else 'claude, gemini, codex, opencode'}）"

        # Check env var
        env_var = info.get("env_var", "")
        if env_var and os.environ.get(env_var):
            return None  # Auth OK

        # For gemini, also check the default file path
        if agent == "gemini":
            default_path = info.get("default_path", "")
            if default_path and os.path.expanduser(default_path):
                expanded = os.path.expanduser(default_path)
                if os.path.exists(expanded):
                    return None

        # Auth missing — return guidance
        return (
            f"❌ **{agent}** 缺少認證憑證\n"
            f"環境變數 `{env_var}` 未設定。\n"
            f"→ {info.get('guide', '請先完成認證設定')}"
        )

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


# ── Warmup ───────────────────────────────────────────────────────

def warmup_acpx(acpx_command: str = "acpx") -> bool:
    """Pre-execute acpx --version to download adapter on first run.

    Call this at gateway startup to avoid 10-30s delay on first user request.
    Returns True if acpx is available, False if not found.
    """
    import subprocess
    try:
        result = subprocess.run(
            [acpx_command, "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            logger.info("acpx warmup OK: %s", result.stdout.strip())
            return True
        else:
            logger.warning("acpx warmup failed (exit %d): %s", result.returncode, result.stderr.strip())
            return False
    except FileNotFoundError:
        logger.error("acpx not found at '%s' — streaming_coder will not work", acpx_command)
        return False
    except subprocess.TimeoutExpired:
        logger.warning("acpx warmup timed out after 30s — first request may be slow")
        return False
