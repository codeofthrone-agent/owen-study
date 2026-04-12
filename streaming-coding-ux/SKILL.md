---
name: streaming-coding-ux
description: OpenAB-style streaming UX for Hermes — real-time edit-streaming, emoji reactions with debounce/stall detection, tool call visualization, and session pooling via acpx ACP JSON-RPC.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [streaming, discord, coding-cli, ux, openab, reactions, acp, acpx]
    related_skills: [external-coding-cli, claude-code, codex, opencode]
---

# Streaming Coding UX

OpenAB-style real-time streaming for Discord, driven by `acpx` ACP JSON-RPC.

## What It Does

When a user sends a trigger like `派 Claude 修 bug`, this skill:

1. **Detects the trigger** → extracts agent name + prompt
2. **Spawns `acpx`** → runs `acpx --format json --json-strict --approve-all claude exec "..."`
3. **Parses streaming JSON-RPC** → converts to typed `AcpEvent` objects
4. **Edit-streams to Discord** → updates message every 1.5s with tool status + text
5. **Manages emoji reactions** → 👀→🤔→🔥→🆗+😊 with debounce and stall detection

## Architecture

```
streaming_coder/
├── __init__.py        # Package exports
├── config.py          # Config dataclass (OpenAB defaults)
├── acp_parser.py      # JSON-RPC line → AcpEvent parsing
├── editor.py          # StreamingEditor (1.5s edit loop + compose_display)
├── reactions.py       # StatusReactionController (debounce + stall + tool classification)
├── pool.py            # Session pool (thread_id → acpx session)
└── bridge.py          # Hermes integration (trigger detection + orchestration)
```

## Quick Start

```python
import asyncio
from streaming_coder import (
    Config, StreamingEditor, StatusReactionController,
    SessionPool, detect_agent_trigger, AcpEvent, AcpEventType,
)
from streaming_coder.bridge import spawn_acpx, stream_acpx_output

# Detect trigger
result = detect_agent_trigger("派 Claude 修這個 bug")
if result:
    agent, prompt = result  # ("claude", "修這個 bug")

# Configure
config = Config.from_env()  # Reads STREAMING_CODER_* env vars

# Setup editor
async def edit_msg(message, content):
    await message.edit(content=content)

editor = StreamingEditor(edit_fn=edit_msg, message=my_discord_msg)

# Setup reactions
async def add_emoji(emoji):
    await my_discord_msg.add_reaction(emoji)

async def remove_emoji(emoji):
    await my_discord_msg.remove_reaction(emoji)

reactions = StatusReactionController(
    add_reaction=add_emoji,
    remove_reaction=remove_emoji,
)

# Run
argv = config.build_acpx_argv(prompt)
session = await spawn_acpx(argv)
await reactions.set_queued()
editor.start()
final = await stream_acpx_output(session, editor, reactions)
editor.stop()
if final.event_type == AcpEventType.RESULT:
    await reactions.set_done()
else:
    await reactions.set_error()
```

## From Sync Context (Hermes Agent Thread Pool)

```python
from streaming_coder.bridge import run_streaming_task

# This runs on the gateway's event loop from a sync thread
task = run_streaming_task(
    loop=gateway_event_loop,
    config=Config.from_env(),
    agent="claude",
    prompt="fix the login bug",
    message=discord_message,
    edit_fn=my_edit_function,
    add_reaction_fn=my_add_reaction,
    remove_reaction_fn=my_remove_reaction,
    cwd="/Users/owen",
    thread_id="123456789",
    pool=my_session_pool,
)
# task is an asyncio.Task — call task.cancel() if needed
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMING_CODER_DISABLED` | (unset) | Set to disable streaming |
| `STREAMING_CODER_MAX_SESSIONS` | 10 | Max concurrent sessions |
| `STREAMING_CODER_TTL_HOURS` | 24 | Idle session TTL |
| `STREAMING_CODER_UPDATE_MS` | 1500 | Edit interval (ms) |
| `STREAMING_CODER_ACPX_CMD` | acpx | acpx binary path |
| `STREAMING_CODER_TIMEOUT` | 120 | acpx timeout (seconds) |
| `STREAMING_CODER_MODEL` | (unset) | Override model |
| `CLAUDE_CODE_OAUTH_TOKEN` | **required** | Claude auth token (NOT `ANTHROPIC_API_KEY`) |

### Config Object

```python
from streaming_coder import Config, ReactionEmojis, ReactionTiming

config = Config(
    enabled=True,
    reactions=ReactionEmojis(
        queued="👀", thinking="🤔", tool="🔥",
        coding="👨‍💻", web="⚡", done="🆗", error="😱",
    ),
    timing=ReactionTiming(
        debounce_ms=700,
        stall_soft_ms=10_000,   # 10s → 🥱
        stall_hard_ms=30_000,   # 30s → 😨
    ),
    pool=Config().pool,  # max_sessions=10, session_ttl_hours=24
    acpx_command="acpx",
    approve_all=True,
)
```

## Emoji State Machine

| State | Emoji | Trigger |
|-------|-------|---------|
| queued | 👀 | Session request initiated |
| thinking | 🤔 | `agent_thought_chunk` or text chunk |
| tool (coding) | 🔥 | `tool_call` with exec/read/write/bash/edit/shell |
| tool (web) | ⚡ | `tool_call` with web_search/web_fetch/browser |
| tool (generic) | 👨‍💻 | `tool_call` with unknown type |
| done | 🆗 + 😊 | Prompt completed |
| error | 😱 | Error response |
| stall soft | 🥱 | 10s with no new events |
| stall hard | 😨 | 30s with no new events |

## ACP Event Types

```python
from streaming_coder import AcpEventType

AcpEventType.TEXT_CHUNK        # agent_message_chunk — streaming text
AcpEventType.THOUGHT_CHUNK     # agent_thought_chunk — thinking
AcpEventType.TOOL_CALL         # tool_call — tool started
AcpEventType.TOOL_CALL_UPDATE  # tool_call_update — progress/completed/failed
AcpEventType.USAGE_UPDATE      # usage_update — token/cost
AcpEventType.RESULT            # Final prompt result
AcpEventType.ERROR             # Error response
```

## Session Pool

```python
from streaming_coder import SessionPool, SessionInfo

pool = SessionPool(max_sessions=10, session_ttl_hours=24)
pool.start_cleanup_loop()  # Reaps idle sessions every 60s

# Get or create a session for a thread
session = await pool.get_or_create("thread_id", factory=my_spawn_fn)

# Cleanup
await pool.close("thread_id")
await pool.shutdown()  # Close all
```

## Trigger Patterns

The bridge detects these patterns:

| Pattern | Example |
|---------|---------|
| `派 <agent> <task>` | `派 Claude 修 bug` |
| `叫 <agent> <task>` | `叫 gemini 寫 test` |
| `丢 <agent> <task>` | `丢 codex 改 config` |
| `ask <agent> <task>` | `ask claude to review` |
| `@<agent> <task>` | `@claude fix this` |

Supported agents: `claude`, `gemini`, `codex`, `opencode`

Patterns also support `丢給` (verb + 給) and `@mention` style.

## Auth — Per-Agent Reference

Each agent has its own auth path. acpx wraps each CLI in an ACP adapter with independent credentials.

| Agent | ACP Adapter | Auth Env Var | Auth Command | Status |
|-------|------------|-------------|-------------|--------|
| **Claude Code** | `@agentclientprotocol/claude-agent-acp` | `CLAUDE_CODE_OAUTH_TOKEN` | `claude setup-token` | ✅ Verified |
| **Codex** | `@zed-industries/codex-acp` | `OPENAI_API_KEY` or `CODEX_API_KEY` | `codex login` (ChatGPT OAuth) | ❌ Needs auth |
| **Gemini** | native `gemini --acp` | `GEMINI_API_KEY` | `gemini` (Google OAuth) | ❌ Needs auth |
| **OpenCode** | native ACP | built-in | `opencode auth login` | ✅ Verified |

### ⚠️ Critical: OAuth vs API Key

- **Claude Code**: `CLAUDE_CODE_OAUTH_TOKEN` (NOT `ANTHROPIC_API_KEY`). Token from `claude setup-token`, format `sk-ant-oat01-...`
- **Codex**: ChatGPT OAuth via `codex login`, or `OPENAI_API_KEY` / `CODEX_API_KEY`
- **Gemini**: Google OAuth or `GEMINI_API_KEY`
- **OpenCode**: Internal auth, works out of the box

OpenAB uses the same approach: `--set agents.claude.env.CLAUDE_CODE_OAUTH_TOKEN="***"`

### ⚠️ CLI Interactive Auth ≠ ACP Auth

Auth in interactive mode (e.g., `claude` TUI, `codex` REPL) does NOT automatically carry over to ACP mode. Each adapter needs its own credentials.

```bash
# Correct:
export CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-..."
acpx --format json --json-strict claude exec "hello"

# Gemini native ACP:
gemini --acp  # Uses GEMINI_API_KEY or Google OAuth

# OpenCode native ACP:
opencode run "hello"  # Uses built-in auth
```

## acpx Command Reference

```bash
# All top-level flags go BEFORE the subcommand:
acpx --format json --json-strict --approve-all --timeout 25 claude exec "prompt"

# Available top-level flags:
#   --format text|json|quiet
#   --json-strict          # Suppress non-JSON stderr
#   --approve-all          # Auto-approve all permissions
#   --timeout <seconds>
#   --model <id>
#   --allowed-tools <list>
#   --max-turns <count>
#   --cwd <dir>
#   --auth-policy skip|fail

# Session management:
acpx claude sessions new --name mysession
acpx claude sessions list
acpx claude sessions close mysession
```

## ACP Protocol Notes

### JSON Structure

acpx outputs one JSON object per line. Key structure:

```json
// Notification (streaming):
{"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"...","update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":"hello"}}}}

// Response (final):
{"jsonrpc":"2.0","id":2,"result":{"stopReason":"end_turn","usage":{...}}}
```

**⚠️ `sessionUpdate` is nested inside `params.update`, NOT directly in `params`.**

### Notification Types

| sessionUpdate | Meaning |
|--------------|---------|
| `available_commands_update` | Initial setup, list of available slash commands |
| `agent_message_chunk` | Streaming text content (`content.text`) |
| `agent_thought_chunk` | Thinking/reasoning |
| `tool_call` | Tool started (`toolCallId`, `title`) |
| `tool_call_update` | Tool progress/completed/failed (`status`) |
| `usage_update` | Token count and cost (`used`, `cost.amount`) |

## Files

- `PLAN.md` — Full implementation plan with OpenAB source analysis
- `REVIEW.md` — Architecture review (blind spots + recommendations)
- `VALIDATION.md` — acpx test results (all passed)
- `streaming_coder/` — Python modules

## References

- OpenAB source: https://github.com/openabdev/openab
- Core files: `src/discord.rs` (stream_prompt), `src/reactions.rs`, `src/acp/pool.rs`
- acpx: `~/.local/share/fnm/node-versions/v24.4.0/installation/lib/node_modules/acpx/`
