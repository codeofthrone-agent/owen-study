# AI Architecture Review — Streaming Coding UX for Hermes

**Reviewer:** Hermes Agent (AI Architecture Reviewer)  
**Date:** 2026-04-12  
**Scope:** Evaluate PLAN.md + SKILL.md for integrating OpenAB-style streaming UX into Hermes Agent

---

## Executive Summary

**Recommendation: Hybrid of C + D (Conditional D-first, with C as fallback)**

The PLAN.md is remarkably thorough — the OpenAB source analysis is accurate, the Python equivalent code is well-reasoned, and the phased approach is sensible. However, there are several critical blind spots that need addressing before implementation.

---

## 1. Which Option is Best — and Why

### Verdict: **Option D first, with C as safety net**

| | Option A | Option B | Option C | Option D (first) |
|---|---|---|---|---|
| Effort | 0h | ❌ Impossible | 5h | **2h validate + 3h integrate** |
| Keeps Hermes integration | ❌ | ❌ | ✅ | ✅ |
| Keeps decision logic | ❌ | ❌ | ✅ | ✅ |
| Leverages existing code | ✅ Full | ❌ | ❌ | ✅ Partial |
| Risk | Low (but useless) | — | Medium | Low-Medium |

**Why D-first:**
- `acpx` already wraps Claude/Codex/Gemini behind ACP JSON-RPC internally. If its `exec` mode outputs structured JSON-RPC notifications line-by-line, we skip reimplementing the protocol layer entirely.
- `acpx --format json` already exists. The question is just whether the streaming notifications arrive in real-time or are buffered until completion.
- The PLAN's own compatibility table (Section 3.3) shows acpx as "⚠️ partial" — this is precisely what Option D testing resolves.

**Why C as fallback:**
- If acpx buffers output (no real-time stream), Option C gives us the full ACP protocol layer via `claude --acp` / `gemini --acp` directly.
- The `connection.py` + `protocol.py` in the PLAN are the critical pieces — they're the only way to get real-time `agent_message_chunk` and `tool_call` notifications.

**Strategic approach:**
1. **Week 1 (2h):** Validate Option D — run `acpx claude exec` with `--format json --json-strict` and capture real output
2. **If D works:** Build integration layer around acpx JSON output → 3h to wire editor + reactions
3. **If D doesn't work:** Fall back to Option C — implement `connection.py` + `protocol.py` directly → 5h

---

## 2. Architectural Blind Spots

### 2.1 🔴 CRITICAL: Gateway Integration Point is Unclear

The PLAN says "不改 Hermes 核心，只加 skill" (no core changes, skill only). This is **misleading**.

**The existing `GatewayStreamConsumer` already handles LLM token streaming** (stream_consumer.py). The PLAN's `StreamingEditor` would be a **parallel, competing system** for CLI subprocess output. This creates confusion:

| Component | What it streams | Transport |
|---|---|---|
| `GatewayStreamConsumer` (existing) | LLM tokens from AIAgent | `stream_delta_callback` → `on_delta` |
| `StreamingEditor` (PLAN) | ACP JSON-RPC from CLI subprocess | Direct Discord edit |

**The two can coexist**, but the PLAN doesn't clearly explain when each fires:
- Normal Hermes conversation → `GatewayStreamConsumer` (existing)
- "派 Claude" trigger → `StreamingEditor` (new)

**Fix needed:** Define a clear dispatch point in `gateway/run.py` or wherever trigger detection happens. The skill needs to intercept the message *before* the normal agent loop runs, send its own Discord message, and manage the streaming lifecycle independently.

### 2.2 🔴 CRITICAL: Session Lifecycle vs. Agent Loop

Hermes's `AIAgent.run_conversation()` is synchronous and runs in a thread pool. The PLAN's `AcpConnection` is fully async. The PLAN doesn't address how these interact:

```
User sends "派 Claude 修 bug"
    ↓
Gateway dispatches to agent loop (sync, in thread pool)
    ↓
Agent detects trigger → calls streaming skill
    ↓
Skill needs to: spawn CLI (async), stream (async), update Discord (async)
    ↓
But agent loop is sync! How does it await async work?
```

**The answer is probably:** The skill returns immediately with a "starting..." message, and the actual streaming happens as a fire-and-forget asyncio task. But the PLAN doesn't document this pattern.

**Fix needed:** Explicitly document the async bridge pattern. The existing `_step_callback_sync` / `_status_callback_sync` in gateway/run.py (lines 7445-7488) show how: `asyncio.run_coroutine_threadsafe(coro, loop)`.

### 2.3 🟡 MEDIUM: Process Cleanup / Zombie Sessions

The PLAN's `SessionPool` has TTL cleanup, but doesn't address:
- What happens when the Hermes gateway restarts? The pool is in-memory → all CLI subprocesses become orphans.
- What happens when the CLI process crashes mid-stream? The `alive()` check only verifies `returncode is None`, but doesn't detect hung processes.
- OpenAB uses `kill_on_drop` (Rust RAII). Python has no destructor guarantee — `__del__` is unreliable with asyncio.

**Fix needed:**
- Add a `shutdown()` hook registered with `atexit` and/or signal handlers
- Add a heartbeat check (send a lightweight ACP ping, timeout after 30s)
- Consider persisting session IDs to a file so sessions can be recovered after restart

### 2.4 🟡 MEDIUM: Discord Rate Limit Handling is Under-specified

OpenAB's `reactions.rs` handles debounce (700ms), but the PLAN doesn't account for Discord's actual rate limits:
- **Reaction add/remove:** 5 requests per 5 seconds per channel (global rate limit)
- **Message edit:** 5 requests per 5 seconds per channel
- **When both run simultaneously** (editing + reacting), they share the same rate limit bucket

The existing `GatewayStreamConsumer._is_flood_error()` and `_MAX_FLOOD_STRIKES = 3` show that Hermes already has flood control. The PLAN's new `StreamingEditor` should reuse or align with this, not implement its own.

**Fix needed:** Share rate limit state between editor and reactions. Or better: use a single `asyncio.Queue` for all Discord API calls with a rate limiter.

### 2.5 🟡 MEDIUM: The PLAN Underestimates acpx's Role

The PLAN treats acpx as one of 5 agents in the external-coding-cli skill. But `acpx` is the actual ACP adapter layer — it's what makes `claude`, `codex`, `gemini` speak ACP. The PLAN's `connection.py` would bypass acpx entirely and spawn CLIs directly with `--acp` flags.

This means:
- **Option C path:** `connection.py` → `claude --acp` (bypasses acpx, direct ACP)
- **Option D path:** `connection.py` → `acpx claude exec` (uses acpx wrapper)

Both are valid, but they use different protocol layers. The PLAN should explicitly support both and document which CLIs work with which path.

### 2.6 🟢 LOW: Missing Error Boundaries

The PLAN's Python code has `except Exception: pass` in several places (e.g., `_edit_loop`, line 332). In production, this silently swallows errors. OpenAB's Rust code at least logs errors.

**Fix needed:** Replace bare `except` with specific exception handling and logging.

---

## 3. Better Approaches

### 3.1 Consider: Extend GatewayStreamConsumer Instead of Building Parallel System

The existing `GatewayStreamConsumer` already handles:
- Message editing with rate limit awareness
- Flood control with adaptive backoff
- Text truncation and chunking
- MEDIA: directive stripping

Instead of building `StreamingEditor` from scratch, consider extending `GatewayStreamConsumer` to accept an `asyncio.Queue[AcpEvent]` as input source instead of just `stream_delta_callback` text.

```python
# Instead of a new StreamingEditor class:
class AcpStreamAdapter:
    """Wraps AcpConnection notification queue into GatewayStreamConsumer-compatible callbacks."""
    def __init__(self, consumer: GatewayStreamConsumer, event_queue: asyncio.Queue):
        self.consumer = consumer
        self.queue = event_queue
    
    async def run(self):
        while True:
            event = await self.queue.get()
            if isinstance(event, TextChunk):
                self.consumer.on_delta(event.text)
            elif isinstance(event, ToolStart):
                # New: feed tool status into consumer
                self.consumer.on_delta(f"\n🔧 `{event.title}`...")
            elif isinstance(event, ToolDone):
                icon = "✅" if event.completed else "❌"
                self.consumer.on_delta(f"\n{icon} `{event.title}`")
        self.consumer.finish()
```

**Benefit:** Reuses all the flood control, truncation, and error handling code that already works.

### 3.2 Consider: Use Hermes's Existing Reaction System

The PLAN creates a new `StatusReactionController`, but `discord.py` already has:
- `_add_reaction()` / `_remove_reaction()` (lines 719-738)
- `on_processing_start()` → 👀 (line 745)
- `on_processing_complete()` → ✅/❌ (line 753)

Instead of a parallel reaction system, extend the existing adapter's reaction methods with debounce and tool classification.

### 3.3 Consider: Gateway Hook System

Hermes has a hook system (`gateway/hooks.py`). Instead of hardcoding the streaming behavior, register a hook that:
1. Intercepts "派 Claude/X" triggers
2. Returns early with a placeholder
3. Spawns an async task that does the ACP streaming
4. The task updates the placeholder message in real-time

This keeps the streaming logic outside the core gateway loop.

---

## 4. Implementation Risks & Mitigations

### 4.1 Risk: asyncio Subprocess + Gateway Event Loop Conflict

**Risk:** The gateway already runs an asyncio event loop. Spawning `asyncio.create_subprocess_exec` from within a sync callback (the agent thread) may conflict.

**Mitigation:** Use `asyncio.run_coroutine_threadsafe()` to schedule subprocess creation on the gateway's event loop, exactly like the existing `_status_callback_sync` pattern.

### 4.2 Risk: ACP Protocol Version Drift

**Risk:** The PLAN hardcodes `"protocolVersion": 1`. If Claude/Gemini update their ACP implementation, this breaks silently.

**Mitigation:** 
- Log the actual protocol version returned by `initialize` response
- Add a version negotiation check with clear error message
- Pin acpx version in deployment

### 4.3 Risk: Long-Running CLI Process Memory Leaks

**Risk:** A session that stays alive for 24h (the TTL) may accumulate memory in the CLI subprocess, especially Claude Code which maintains conversation context.

**Mitigation:**
- Set a shorter practical TTL (1-2 hours, not 24h)
- Implement session reset: after N prompts, call `session/new` to get a fresh session within the same process
- Monitor RSS of subprocess and kill if above threshold

### 4.4 Risk: Discord Thread Permission Requirements

**Risk:** Creating threads requires `CREATE_PUBLIC_THREADS` or `CREATE_PRIVATE_THREADS` permission. If the bot lacks this, `create_thread_from_message` fails silently.

**Mitigation:** Check bot permissions at startup and fall back to channel mode if threading isn't available. Document required permissions.

### 4.5 Risk: acpx First-Run Download Latency

**Risk:** acpx downloads adapter packages on first use (10-30 seconds). During this time, the streaming UX would show nothing or a timeout.

**Mitigation:** Pre-warm acpx during gateway startup with a no-op command (`acpx --version`). Or accept the one-time latency.

---

## 5. If Option C: Python-Specific Concerns

### 5.1 asyncio vs. tokio

| Aspect | Rust (tokio) | Python (asyncio) |
|---|---|---|
| Subprocess I/O | `tokio::process::Command` | `asyncio.create_subprocess_exec` |
| Channels | `mpsc::UnboundedSender` | `asyncio.Queue` |
| One-shot responses | `oneshot::channel` | `asyncio.Future` |
| Background tasks | `tokio::spawn` | `asyncio.create_task` |
| Locking | `RwLock<HashMap>` | `asyncio.Lock` (no RwLock) |
| Timer/sleep | `tokio::time::sleep` | `asyncio.sleep` |

**Key differences:**
1. **No RwLock in asyncio.** The PLAN's double-check locking pattern uses `RwLock` in Rust. In Python, use `asyncio.Lock` for write operations and `dict` reads (which are atomic in CPython for simple lookups) for the fast path.

2. **No `kill_on_drop`.** Python's `__del__` is unreliable. Use `atexit.register(cleanup)` + `signal.signal()` + explicit `shutdown()` calls.

3. **`readline()` blocking.** `asyncio.StreamReader.readline()` returns bytes and may raise `LimitOverrunError` for very long lines. Add a line length limit and handle the exception.

4. **Thread safety.** The gateway runs async code. The agent runs in a thread pool. The ACP connection needs to bridge both worlds. Use `asyncio.Queue` (thread-safe `put_nowait`) + `loop.call_soon_threadsafe()`.

### 5.2 JSON-RPC Edge Cases

- **Incomplete lines:** The CLI might output partial JSON if stdout buffering is weird. Use a line-based protocol and handle `json.JSONDecodeError` gracefully.
- **Encoding:** Some CLIs may output non-UTF-8 content on stderr. The PLAN redirects stderr to DEVNULL, which is correct.
- **Concurrent requests:** ACP allows multiple in-flight requests. The PLAN's `_pending` dict handles this, but ensure the request ID is monotonically increasing (it is).

---

## 6. If Option D: Validation Checklist

Before committing to Option D, run these tests:

```bash
# Test 1: Does acpx exec output JSON line-by-line in real-time?
timeout 30 acpx claude exec "write a hello world function in python" --format json --json-strict 2>/dev/null
# Expected: Multiple JSON lines appearing over time (not all at once at the end)

# Test 2: What's the structure of each JSON line?
timeout 30 acpx claude exec "write a hello world function" --format json --json-strict 2>/dev/null | jq -r 'type' 
# Expected: Each line should be a valid JSON object

# Test 3: Do we get ACP notification types (agent_message_chunk, tool_call)?
timeout 30 acpx claude exec "read the file README.md then summarize it" --format json --json-strict 2>/dev/null | jq -r '.method // .result.type // empty'
# Expected: Should see "agent_message_chunk", "tool_call", etc.

# Test 4: Does --approve-all work non-interactively?
timeout 30 acpx claude exec "create a file test.txt with hello" --format json --approve-all --json-strict 2>/dev/null
# Expected: Should complete without hanging on permission prompt

# Test 5: Session persistence — does acpx support multi-turn?
# (Check if there's a --session-id or similar flag)
acpx claude --help | grep -i session
```

**Critical question:** If Test 1 shows all JSON arriving at once (buffered), Option D is dead for streaming and you must use Option C.

---

## 7. Overall Recommendations

### Do Now
1. **Run the Option D validation tests** (Section 6) — this takes 10 minutes and determines the entire approach
2. **Document the dispatch point** — where exactly does the skill intercept messages in the gateway loop?
3. **Define the async bridge pattern** — how does the sync agent loop trigger async ACP streaming?

### Do Before Implementation
4. **Extend, don't replace** — build on `GatewayStreamConsumer` and Discord adapter's existing reaction methods rather than creating parallel systems
5. **Add shutdown hooks** — `atexit` + signal handling for subprocess cleanup
6. **Define permission fallback** — what happens when thread creation fails?

### Do During Implementation
7. **Test with real acpx output** early and often
8. **Log ACP protocol version** from `initialize` response
9. **Monitor subprocess RSS** in session pool cleanup

### Nice to Have
10. **Persist session pool to SQLite** — Hermes already uses SQLite for sessions (`hermes_state.py`)
11. **Add metrics** — track streaming latency, edit count, flood control hits
12. **Support multiple CLI backends simultaneously** — one thread per agent type

---

## Appendix: Code Quality Assessment

| Aspect | PLAN.md Rating | Notes |
|---|---|---|
| OpenAB analysis accuracy | ⭐⭐⭐⭐⭐ | Thorough, correct down to field names |
| Python translation quality | ⭐⭐⭐⭐ | Good, minor issues with async patterns |
| Architecture alignment | ⭐⭐⭐ | Doesn't address gateway integration enough |
| Error handling | ⭐⭐ | Too many bare `except: pass` |
| Risk awareness | ⭐⭐⭐ | Good on protocol risks, weak on ops risks |
| Testability | ⭐⭐⭐⭐ | Good test plan, should add integration tests |
| Estimated effort (5h) | ⭐⭐⭐ | Realistic for Option C core, optimistic for full integration |

**Bottom line:** The analysis is excellent. The plan needs 2-3 more hours of integration design before implementation begins. Validate Option D first — it could save 3 hours if it works.
