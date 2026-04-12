# Streaming Coding UX for Hermes Agent

> OpenAB-style real-time streaming for coding CLI agents in Hermes Discord gateway.

## Overview

This project brings OpenAB's streaming UX to Hermes Agent — real-time Discord message editing, emoji status reactions, tool call visualization, and thread-based multi-turn conversations — all driven by `acpx` ACP JSON-RPC streaming.

```
Discord "派 Claude 修 bug"
    │
    ▼
Hermes Gateway → detect trigger → spawn acpx → stream JSON-RPC
    │
    ├── 👀 → 🤔 → 🔥 → 👍 + 😊 (emoji reactions)
    ├── 🔧 `exec: bash`... → ✅ `exec: bash` (tool status)
    └── Discord message edits every 1.5s (streaming text)
```

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Hermes Discord Gateway                              │
│                                                      │
│  _handle_message_with_agent()                        │
│      │                                               │
│      ├── detect_agent_trigger() ──► streaming_coder  │
│      │                              │                │
│      │                         spawn acpx            │
│      │                              │                │
│      │                    ┌─────────┴─────────┐      │
│      │                    │ ACP JSON-RPC      │      │
│      │                    │ agent_message_chunk│──► StreamingEditor
│      │                    │ tool_call          │    (1.5s edit loop)
│      │                    │ tool_call_update   │──► ReactionsController
│      │                    └───────────────────┘    (👀🤔🔥👍😊)
│      │                              │                │
│      │                    adapter.edit_message()     │
│      │                    adapter._add_reaction()    │
│      │                                               │
│      └── normal flow ──► AIAgent.run_conversation() │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Components

### streaming_coder/

| Module | Purpose |
|--------|---------|
| `config.py` | Config with OpenAB-compatible defaults (emojis, timing, pool) |
| `acp_parser.py` | Parse acpx JSON-RPC stdout into typed `AcpEvent` objects |
| `acp_adapter.py` | Bridge ACP events to `GatewayStreamConsumer` deltas |
| `editor.py` | `StreamingEditor` — 1.5s edit loop, tool line tracking, compose/split |
| `reactions.py` | `StatusReactionController` — debounce (700ms), stall (10s→🥱, 30s→😨), tool classification |
| `bridge.py` | Hermes integration — trigger detection, acpx spawning, streaming orchestration |
| `pool.py` | Session tracking (thread_id → acpx session) |

### gateway/run.py Modifications

- **Trigger intercept** (line ~3470): Checks incoming messages for coding triggers before normal agent loop
- **`_handle_streaming_coding_task()`** (line ~3807): Manages the full streaming lifecycle

## Trigger Patterns

| Input | Agent | Prompt |
|-------|-------|--------|
| `派 Claude 修 bug` | claude | 修 bug |
| `丟給 codex fix auth` | codex | fix auth |
| `叫 gemini review code` | gemini | review code |
| `叫 opencode 寫 test` | opencode | 寫 test |
| `@claude explain this` | claude | explain this |
| `hello world` | — | (no trigger, normal flow) |

## Configuration

Default values (compatible with OpenAB config.toml):

```toml
[reactions.emojis]
queued = "👀"
thinking = "🤔"
tool = "🔥"        # generic tool
coding = "👨‍💻"      # exec/read/write/bash
web = "⚡"         # web_search/browser
done = "🆗"
error = "😱"

[reactions.timing]
debounce_ms = 700
stall_soft_ms = 10000    # 10s → 🥱
stall_hard_ms = 30000    # 30s → 😨

[pool]
max_sessions = 10
session_ttl_hours = 24
```

## Authentication

| Agent | Auth Method | Env Var |
|-------|-------------|---------|
| Claude Code | `claude setup-token` → OAuth | `CLAUDE_CODE_OAUTH_TOKEN` |
| OpenCode | `opencode login` | Built-in |
| Codex | `codex login --device-auth` | `OPENAI_API_KEY` or OAuth |
| Gemini | Google OAuth | `GEMINI_API_KEY` |

**Important:** Claude Code uses `CLAUDE_CODE_OAUTH_TOKEN`, NOT `ANTHROPIC_API_KEY`.

## Dependencies

- Python 3.9+
- `acpx` 0.5.3+ (`npm install -g acpx`)
- Hermes Agent (gateway with Discord adapter)
- At least one authenticated coding CLI

## Verified Agents

| Agent | Version | ACP | Streaming | Auth |
|-------|---------|-----|-----------|------|
| Claude Code | 2.1.89 | adapter | ✅ | `CLAUDE_CODE_OAUTH_TOKEN` |
| OpenCode | 1.4.3 | native | ✅ | `opencode login` |
| Codex | 0.118.0 | adapter | ⚠️ | OAuth/API key |
| Gemini | 0.37.0 | native | ⚠️ | OAuth/API key |

## ACP Protocol Reference

### Notification Types (session/update)

| Type | Event | Description |
|------|-------|-------------|
| `agent_message_chunk` | `TEXT_CHUNK` | Streaming text content |
| `agent_thought_chunk` | `THOUGHT_CHUNK` | Agent thinking |
| `tool_call` | `TOOL_CALL` | Tool execution started |
| `tool_call_update` | `TOOL_CALL_UPDATE` | Tool progress/completed/failed |
| `usage_update` | `USAGE_UPDATE` | Token usage and cost |
| `available_commands_update` | `AVAILABLE_COMMANDS` | Initial setup |

### JSON-RPC Flow

```
→ initialize          (handshake)
← result              (agent info, capabilities)
→ session/new         (create session)
← result              (session ID, models, modes)
→ session/prompt      (send user message)
← update              (streaming notifications)
← update              (streaming notifications)
← result              (final response)
```

## Files

```
streaming-coding-ux/
├── README.md                    ← This file
├── PLAN.md                      ← Implementation plan (OpenAB source analysis)
├── REVIEW.md                    ← Architecture review (Claude evaluation)
├── VALIDATION.md                ← acpx test results
├── INTEGRATION_PLAN.md          ← Hermes gateway integration plan
├── SKILL.md                     ← Skill usage documentation
└── streaming_coder/             ← Python package
    ├── __init__.py
    ├── config.py
    ├── acp_parser.py
    ├── acp_adapter.py
    ├── editor.py
    ├── reactions.py
    ├── bridge.py
    └── pool.py
```

## Research Sources

- [OpenAB](https://github.com/openabdev/openab) — Rust ACP harness (source code analysis)
- [OpenClaw](https://github.com/openclaw/openclaw) — Personal AI assistant (comparison)
- [acpx](https://www.npmjs.com/package/acpx) — ACP CLI client
- [Agent Client Protocol](https://github.com/anthropics/agent-protocol) — Protocol specification

## License

MIT
