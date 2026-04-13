# Streaming Session Life 完整生命週期補齊計畫

> **Status:** READY
> **Created:** 2026-04-13
> **For:** OpenCode 執行
> **Repo:** /Users/owen/.hermes/hermes-agent
> **owen-study repo:** /Users/owen/source/github.com/owen-study/streaming-coding-ux

## Goal

補齊 streaming_coder 的 session 生命週期管理，讓 Discord 使用者可以：
1. 用 trigger 啟動 coding session（已經能用）
2. 在 thread 內直接 follow-up（不打 trigger）→ 自動轉發到同一 session
3. Session 超時後說「繼續」→ resume 同一個 acpx named session
4. 說「結束」→ 提前中止 session

## 現狀分析

### 已完成（hermes-agent 內）
- ✅ `streaming_coder/` v0.2.0 — 8 個模組全數完成
- ✅ Gateway trigger intercept (`run.py:3475-3495`)
- ✅ `_handle_streaming_coding_task` (`run.py:3807-3980`)
- ✅ `detect_trigger()` — 4 種模式 (cancel/session_new/session/one-shot)
- ✅ `dispatch_trigger()` — 路由到正確 handler
- ✅ `run_session_task()` — persistent named session
- ✅ `AcpxSessionManager` — ensure/cancel/reset/close
- ✅ `SessionPool` — TTL cleanup、max sessions
- ✅ Auth validation (`config.py:132` — `validate_agent_auth`)
- ✅ Thread creation for ONE_SHOT

### 缺失（本計畫要補的）
- ❌ Thread follow-up 路由（非 trigger 訊息轉發到 session）
- ❌ Session 超時 resume（named session 存在但 process 死了）
- ❌ 「結束」快捷指令（除了 `派 claude cancel` 之外更自然的寫法）
- ❌ Session 狀態查詢（用戶想知道 session 是否 active）

## Tech Stack & Conventions
- Python 3.11, asyncio
- streaming_coder 模組已在 hermes-agent 根目錄
- Gateway 為 `gateway/run.py`（8880 行）
- Discord adapter API: `edit_message()`, `send()`, `_add_reaction()`, `_remove_reaction()`

## Pre-flight

```bash
cd /Users/owen/.hermes/hermes-agent
git checkout -b feature/streaming-session-lifecycle
source venv/bin/activate
```

---

## Task 1: 在 SessionPool 加入 thread → agent_name 的映射

**Objective:** 追蹤每個 thread 使用的 agent 名稱，讓 follow-up 訊息知道要轉發給誰

**Files:**
- Modify: `streaming_coder/pool.py:100-140` (SessionPool class)

**Step 1: Write failing test**

```python
# tests/streaming_coder/test_pool_session_agent.py
import pytest
from streaming_coder.pool import SessionPool

@pytest.mark.asyncio
async def test_track_agent_per_thread():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    assert pool.get_thread_agent("thread-123") == "claude"
    assert pool.get_thread_agent("thread-456") is None

@pytest.mark.asyncio
async def test_thread_agent_cleared_on_close():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "gemini")
    pool.clear_thread_agent("thread-123")
    assert pool.get_thread_agent("thread-123") is None
```

**Step 2: Run test — Expected: FAIL**

```bash
cd /Users/owen/.hermes/hermes-agent
source venv/bin/activate
python -m pytest tests/streaming_coder/test_pool_session_agent.py -v
```

**Step 3: Implement in `pool.py`**

Add to `SessionPool.__init__`:

```python
self._thread_agents: Dict[str, str] = {}  # thread_id → agent_name
```

Add methods:

```python
def set_thread_agent(self, thread_id: str, agent: str) -> None:
    """Record which agent a thread is using."""
    self._thread_agents[thread_id] = agent.lower()

def get_thread_agent(self, thread_id: str) -> Optional[str]:
    """Get the agent name for an active thread session, or None."""
    return self._thread_agents.get(thread_id)

def clear_thread_agent(self, thread_id: str) -> None:
    """Clear agent mapping when session ends."""
    self._thread_agents.pop(thread_id, None)

def has_active_session(self, thread_id: str) -> bool:
    """Check if this thread has an active streaming session."""
    return thread_id in self._thread_agents
```

Update `close()` to also clear agent mapping:

```python
async def close(self, thread_id: str) -> None:
    async with self._lock:
        session = self._sessions.pop(thread_id, None)
    self._thread_agents.pop(thread_id, None)  # ← Add this
    if session and session.alive():
        # ... existing terminate logic
```

**Step 4: Run test — Expected: PASS**

```bash
python -m pytest tests/streaming_coder/test_pool_session_agent.py -v
```

**Step 5: Commit**

```bash
git add streaming_coder/pool.py tests/streaming_coder/test_pool_session_agent.py
git commit -m "feat(pool): track agent name per thread for follow-up routing"
```

---

## Task 2: 在 AcpxSessionManager 記錄 agent mapping

**Objective:** Session manager 在建立 session 時自動記錄 thread → agent 映射

**Files:**
- Modify: `streaming_coder/pool.py:348-418` (AcpxSessionManager)

**Step 1: Write failing test**

```python
# tests/streaming_coder/test_session_mgr_agent.py
import pytest
from streaming_coder.pool import SessionPool, AcpxSessionManager

@pytest.mark.asyncio
async def test_session_mgr_records_agent():
    pool = SessionPool()
    mgr = AcpxSessionManager(pool, agent="claude")
    await mgr.ensure_session("thread-123")
    assert pool.get_thread_agent("thread-123") == "claude"

@pytest.mark.asyncio
async def test_session_mgr_updates_agent():
    pool = SessionPool()
    mgr = AcpxSessionManager(pool, agent="claude")
    mgr.agent = "gemini"
    name = await mgr.ensure_session("thread-123")
    assert pool.get_thread_agent("thread-123") == "gemini"
```

**Step 2: Run test — Expected: FAIL**

```bash
python -m pytest tests/streaming_coder/test_session_mgr_agent.py -v
```

**Step 3: Implement**

Add `pool.set_thread_agent(thread_id, self.agent)` call in `AcpxSessionManager.ensure_session()`:

```python
async def ensure_session(self, thread_id: str) -> str:
    """Ensure named session exists, return session name."""
    self.pool.set_thread_agent(thread_id, self.agent)  # ← Add this
    return await self.pool.ensure_named_session(thread_id, self.agent)
```

Also add in `cancel()`:

```python
async def cancel(self, thread_id: str) -> bool:
    """Cancel active prompt in this thread's session."""
    result = await self.pool.cancel_active_prompt(thread_id, self.agent)
    # Don't clear agent — session persists for resume
    return result
```

And in `close()`:

```python
async def close(self, thread_id: str) -> None:
    """Permanently close this thread's session."""
    await self.pool.close_named_session(thread_id, self.agent)
    self.pool.clear_thread_agent(thread_id)  # ← Add this
```

**Step 4: Run test — Expected: PASS**

```bash
python -m pytest tests/streaming_coder/test_session_mgr_agent.py -v
```

**Step 5: Commit**

```bash
git add streaming_coder/pool.py tests/streaming_coder/test_session_mgr_agent.py
git commit -m "feat(pool): AcpxSessionManager records thread-agent mapping"
```

---

## Task 3: Gateway — Thread follow-up 路由

**Objective:** 在 thread 內的非 trigger 訊息自動轉發到 active streaming session

**Files:**
- Modify: `gateway/run.py:3475-3495` (streaming intercept block)

**Step 1: Understand current flow**

Current intercept (line 3475):
```python
_trigger = detect_trigger(message_text)
if _trigger:
    # → route to streaming
    ...
# falls through to normal agent
```

**Problem:** If user is in a thread with an active session and sends "把 model 改掉", it doesn't match any trigger pattern → falls through to normal agent.

**Step 2: Implement follow-up detection**

Replace the intercept block at line 3475 with expanded logic:

```python
# === STREAMING CODER INTERCEPT ===
try:
    from streaming_coder.bridge import detect_trigger, TriggerMode

    _trigger = detect_trigger(message_text)

    if _trigger:
        # Explicit trigger — always route to streaming
        _streaming_result = await self._handle_streaming_coding_task(
            event=event, source=source,
            trigger=_trigger, message_text=message_text,
        )
        if _streaming_result is not None:
            return _streaming_result
    else:
        # No explicit trigger — check for active session follow-up
        _follow_up = self._detect_session_follow_up(source, message_text)
        if _follow_up:
            _streaming_result = await self._handle_streaming_coding_task(
                event=event, source=source,
                trigger=_follow_up, message_text=message_text,
            )
            if _streaming_result is not None:
                return _streaming_result

except ImportError:
    pass  # streaming_coder not installed
except Exception as _sc_err:
    logger.warning("Streaming coder intercept failed (non-fatal): %s", _sc_err)
# === END STREAMING CODER INTERCEPT ===
```

**Step 3: Add `_detect_session_follow_up` method**

Add new method in the same class (near `_handle_streaming_coding_task`, around line 3805):

```python
def _detect_session_follow_up(self, source: Any, message_text: str) -> Optional[Any]:
    """Detect if this message is a follow-up in an active streaming session.

    Checks:
    1. Is there an active session pool?
    2. Does this thread/channel have an active session?
    3. Is the message not a system/command message?

    Returns a synthetic TriggerResult for session mode, or None.
    """
    if not hasattr(self, "_streaming_session_pool"):
        return None

    pool = self._streaming_session_pool
    chat_id = source.chat_id

    # Check if thread has active session
    if not pool.has_active_session(chat_id):
        return None

    agent_name = pool.get_thread_agent(chat_id)
    if not agent_name:
        return None

    # Don't route empty messages or pure reactions
    text = (message_text or "").strip()
    if not text or len(text) < 2:
        return None

    # Don't route slash commands
    if text.startswith("/"):
        return None

    # Build synthetic TriggerResult for SESSION mode
    from streaming_coder.bridge import TriggerResult, TriggerMode
    return TriggerResult(
        agent=agent_name,
        mode=TriggerMode.SESSION,
        prompt=text,
        raw=text,
    )
```

**Step 4: Write integration test concept**

```python
# Manual verification:
# 1. In Discord: "派 Claude session 做 auth refactor"
#    → Thread opens, Claude starts working
# 2. In same thread: "把 model 改成 JWT"
#    → Should route to same Claude session (no trigger needed)
# 3. In same thread: "結束"
#    → Should cancel session
```

**Step 5: Commit**

```bash
git add gateway/run.py
git commit -m "feat(gateway): route thread follow-ups to active streaming session"
```

---

## Task 4: Session 超時 Resume 支援

**Objective:** Session 超時（TTL 到期）後，用戶可以說「繼續」resume

**Files:**
- Modify: `streaming_coder/pool.py` (SessionPool — add expired session tracking)
- Modify: `streaming_coder/bridge.py` (add resume detection in detect_trigger)

**Step 1: Write failing test**

```python
# tests/streaming_coder/test_session_resume.py
import pytest
from streaming_coder.pool import SessionPool

@pytest.mark.asyncio
async def test_track_expired_session():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    pool.set_session_name("thread-123", "dc-123456")
    # Simulate TTL expiry
    pool.mark_session_expired("thread-123")
    assert pool.has_expired_session("thread-123") is True
    assert pool.get_session_name("thread-123") == "dc-123456"
    assert pool.get_thread_agent("thread-123") == "claude"

@pytest.mark.asyncio
async def test_resume_clears_expired_flag():
    pool = SessionPool()
    pool.set_thread_agent("thread-123", "claude")
    pool.mark_session_expired("thread-123")
    pool.resume_session("thread-123")
    assert pool.has_expired_session("thread-123") is False
```

**Step 2: Run test — Expected: FAIL**

```bash
python -m pytest tests/streaming_coder/test_session_resume.py -v
```

**Step 3: Implement in pool.py**

Add to `SessionPool`:

```python
def __init__(self, ...):
    # ... existing ...
    self._expired_sessions: Dict[str, str] = {}  # thread_id → session_name

def set_session_name(self, thread_id: str, session_name: str) -> None:
    """Record the acpx session name for a thread (for resume)."""
    self._expired_sessions[thread_id] = session_name

def mark_session_expired(self, thread_id: str) -> None:
    """Mark a session as expired (process dead, named session persists)."""
    session_name = self.thread_to_session_name(thread_id)
    self._expired_sessions[thread_id] = session_name

def has_expired_session(self, thread_id: str) -> bool:
    """Check if thread has an expired but resumable session."""
    return thread_id in self._expired_sessions

def get_session_name(self, thread_id: str) -> Optional[str]:
    """Get the acpx session name for a thread."""
    return self._expired_sessions.get(thread_id)

def resume_session(self, thread_id: str) -> None:
    """Clear expired flag (session is active again)."""
    # Keep the mapping, just the session is active now
    pass  # The session is now tracked in _sessions again
```

Update `cleanup_idle()` to mark sessions as expired instead of just removing:

```python
async def cleanup_idle(self) -> int:
    now = time.time()
    to_reap = []
    for tid, session in self._sessions.items():
        if not session.alive() or (now - session.last_active) > self.session_ttl_secs:
            to_reap.append(tid)

    for tid in to_reap:
        # Record session name for resume before closing
        session = self._sessions.get(tid)
        if session and session.acpx_session_name:
            self._expired_sessions[tid] = session.acpx_session_name
        await self.close(tid)
    # ...
```

**Step 4: Add "繼續" detection to bridge.py**

In `detect_trigger()`, add a RESUME check before the other patterns:

```python
# Resume patterns — "繼續" / "resume" / "go on"
RESUME_PATTERNS = [
    re.compile(r"^(?:繼續|resume|go\s*on|接着?)$", re.IGNORECASE),
]

# In detect_trigger(), add at the top:
# 0. Resume
for pattern in RESUME_PATTERNS:
    m = pattern.match(text)
    if m:
        # Agent is determined by the thread context, use placeholder
        return TriggerResult(
            agent="",  # Will be filled from pool.get_thread_agent()
            mode=TriggerMode.SESSION,
            prompt="請繼續之前的工作",  # Generic resume prompt
            raw=m.group(0),
        )
```

**Step 5: Handle resume in gateway follow-up detection**

In `_detect_session_follow_up()` (from Task 3), also check expired sessions:

```python
# Check if thread has expired session (resumable)
if pool.has_expired_session(chat_id):
    agent_name = pool.get_thread_agent(chat_id) or "claude"
    text = (message_text or "").strip()

    # Resume triggers: 繼續/resume OR any non-empty follow-up
    if text and not text.startswith("/"):
        from streaming_coder.bridge import TriggerResult, TriggerMode
        if text in ("繼續", "resume", "go on"):
            prompt = "請繼續之前的工作"
        else:
            prompt = text
        return TriggerResult(
            agent=agent_name,
            mode=TriggerMode.SESSION,
            prompt=prompt,
            raw=text,
        )
```

**Step 6: Run test — Expected: PASS**

```bash
python -m pytest tests/streaming_coder/test_session_resume.py -v
```

**Step 7: Commit**

```bash
git add streaming_coder/pool.py streaming_coder/bridge.py tests/streaming_coder/test_session_resume.py
git commit -m "feat: session timeout resume — track expired sessions, detect '繼續'"
```

---

## Task 5: 「結束」快捷指令 + Session 狀態查詢

**Objective:** 更自然的 session 結束方式，加上狀態查詢

**Files:**
- Modify: `streaming_coder/bridge.py` (add end/status trigger patterns)
- Modify: `gateway/run.py` (handle status query)

**Step 1: Write failing test**

```python
# tests/streaming_coder/test_end_trigger.py
from streaming_coder.bridge import detect_trigger, TriggerMode

def test_end_trigger_chinese():
    result = detect_trigger("派 Claude 結束")
    assert result is not None
    assert result.mode == TriggerMode.SESSION_CANCEL
    assert result.agent == "claude"

def test_end_trigger_plain():
    result = detect_trigger("結束")
    assert result is None  # Too ambiguous alone — must be in active session

def test_status_trigger():
    result = detect_trigger("派 Claude 狀態")
    assert result is not None
    assert result.mode == TriggerMode.STATUS  # New mode
    assert result.agent == "claude"
```

**Step 2: Run test — Expected: FAIL**

```bash
python -m pytest tests/streaming_coder/test_end_trigger.py -v
```

**Step 3: Add STATUS mode and end patterns**

In `bridge.py`, add to TriggerMode:

```python
class TriggerMode(Enum):
    ONE_SHOT = auto()
    SESSION = auto()
    SESSION_NEW = auto()
    SESSION_CANCEL = auto()
    STATUS = auto()       # ← New: query session status
```

Add end patterns to CANCEL_PATTERNS (already handles `派 claude cancel`):

```python
# Add to CANCEL_PATTERNS:
re.compile(
    r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:結束|end|done|完成)",
    re.IGNORECASE,
),
re.compile(
    r"@(claude|gemini|codex|opencode)\s+(?:結束|end|done|finish)",
    re.IGNORECASE,
),
```

Add STATUS_PATTERNS:

```python
STATUS_PATTERNS = [
    re.compile(
        r"(?:派|叫|丟|丢)\s*(?:給|给)?\s*(claude|gemini|codex|opencode)\s+(?:狀態|status|session\??)",
        re.IGNORECASE,
    ),
    re.compile(
        r"@(claude|gemini|codex|opencode)\s+(?:狀態|status)",
        re.IGNORECASE,
    ),
]
```

In `detect_trigger()`, add status check between cancel and session_new:

```python
# 1.5. Status
for pattern in STATUS_PATTERNS:
    m = pattern.match(text)
    if m:
        agent = m.group(1).lower()
        if agent in SUPPORTED_AGENTS:
            return TriggerResult(
                agent=agent,
                mode=TriggerMode.STATUS,
                prompt="",
                raw=m.group(0),
            )
```

**Step 4: Handle STATUS in dispatch_trigger**

Add to `dispatch_trigger()`:

```python
elif trigger.mode == TriggerMode.STATUS:
    return await _handle_session_status(
        session_mgr=session_mgr,
        chat_id=chat_id,
        agent=trigger.agent,
    )
```

Add helper:

```python
async def _handle_session_status(
    session_mgr: AcpxSessionManager,
    chat_id: str,
    agent: str,
) -> Dict[str, Any]:
    """Return session status for this thread."""
    pool = session_mgr.pool
    session = pool._sessions.get(chat_id)

    if session and session.alive():
        elapsed = time.time() - session.last_active
        status_text = (
            f"🟢 Session 活躍中\n"
            f"Agent: {agent}\n"
            f"Session: `{session.acpx_session_name or 'unnamed'}`\n"
            f"閒置: {int(elapsed)}s"
        )
    elif pool.has_expired_session(chat_id):
        session_name = pool.get_session_name(chat_id)
        status_text = (
            f"🟡 Session 已超時（可 resume）\n"
            f"Agent: {agent}\n"
            f"Session: `{session_name}`\n"
            f"說「繼續」可恢復"
        )
    else:
        status_text = "⚫ 無活躍 session"

    return {"success": True, "text": status_text, "mode": "status"}
```

**Step 5: Run test — Expected: PASS**

```bash
python -m pytest tests/streaming_coder/test_end_trigger.py -v
```

**Step 6: Commit**

```bash
git add streaming_coder/bridge.py tests/streaming_coder/test_end_trigger.py
git commit -m "feat: add STATUS mode and '結束' cancel patterns"
```

---

## Task 6: 端到端整合測試

**Objective:** 驗證完整生命週期

**Files:**
- Create: `tests/streaming_coder/test_e2e_session_lifecycle.py`

**Step 1: Write lifecycle test**

```python
# tests/streaming_coder/test_e2e_session_lifecycle.py
"""End-to-end test for the session lifecycle (mocked acpx)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from streaming_coder.bridge import detect_trigger, dispatch_trigger, TriggerMode
from streaming_coder.pool import SessionPool, AcpxSessionManager

def test_trigger_detection_lifecycle():
    """Verify all trigger patterns work."""
    # One-shot
    r = detect_trigger("派 Claude 修 bug")
    assert r.mode == TriggerMode.ONE_SHOT
    assert r.agent == "claude"

    # Session
    r = detect_trigger("派 Claude session 做 refactor")
    assert r.mode == TriggerMode.SESSION

    # Session new
    r = detect_trigger("派 Claude 新對話")
    assert r.mode == TriggerMode.SESSION_NEW

    # Cancel
    r = detect_trigger("派 Claude 結束")
    assert r.mode == TriggerMode.SESSION_CANCEL

    # Status
    r = detect_trigger("派 Claude 狀態")
    assert r.mode == TriggerMode.STATUS

    # No trigger
    assert detect_trigger("hello world") is None
    assert detect_trigger("把 model 改掉") is None

@pytest.mark.asyncio
async def test_follow_up_detection():
    """Thread follow-up routing."""
    pool = SessionPool()
    pool.set_thread_agent("thread-1", "claude")

    # Has active session → should detect follow-up
    assert pool.has_active_session("thread-1") is True
    assert pool.get_thread_agent("thread-1") == "claude"

    # No active session
    assert pool.has_active_session("thread-999") is False

@pytest.mark.asyncio
async def test_session_resume():
    """Session expiry → resume."""
    pool = SessionPool()
    pool.set_thread_agent("thread-1", "gemini")
    pool.mark_session_expired("thread-1")

    assert pool.has_expired_session("thread-1") is True
    assert pool.get_session_name("thread-1") == "dc-thread-1"
    assert pool.get_thread_agent("thread-1") == "gemini"
```

**Step 2: Run test — Expected: PASS**

```bash
python -m pytest tests/streaming_coder/test_e2e_session_lifecycle.py -v
```

**Step 3: Run full test suite**

```bash
python -m pytest tests/ -q --tb=short
```

**Step 4: Commit**

```bash
git add tests/streaming_coder/test_e2e_session_lifecycle.py
git commit -m "test: e2e session lifecycle — trigger, follow-up, resume"
```

---

## Post-flight

```bash
cd /Users/owen/.hermes/hermes-agent
python -m pytest tests/ -q --tb=short       # All pass
git diff --stat                               # Review changes
git commit -am "feat: complete streaming session lifecycle"
```

## Verification Checklist

- [ ] `派 Claude session 做 refactor` → 開 thread，Claude 開始工作
- [ ] 在 thread 內打 `把 model 改成 JWT` → 自動轉發到 session（不打 trigger）
- [ ] Claude 回應結束後，thread 內打 `加 unit tests` → 繼續 session
- [ ] 等 TTL 到期，打 `繼續` → resume 同一個 acpx session
- [ ] 打 `派 Claude 結束` → session 中止
- [ ] 打 `派 Claude 狀態` → 顯示 session 狀態
- [ ] 不在 thread 內的普通訊息 → 走原有 agent flow，不受影響
- [ ] `streaming_coder` import 失敗時 → gracefully fallback 到正常 flow
- [ ] 既有功能不受影響

## File Change Summary

| File | Action | Lines (approx) |
|------|--------|----------------|
| `streaming_coder/pool.py` | Modify — add thread agent tracking + expired session tracking | +40 |
| `streaming_coder/bridge.py` | Modify — add STATUS mode, 結束 patterns, resume detection | +30 |
| `gateway/run.py` | Modify — expand intercept block + add `_detect_session_follow_up` | +35 |
| `tests/streaming_coder/test_pool_session_agent.py` | Create | +20 |
| `tests/streaming_coder/test_session_mgr_agent.py` | Create | +20 |
| `tests/streaming_coder/test_session_resume.py` | Create | +20 |
| `tests/streaming_coder/test_end_trigger.py` | Create | +15 |
| `tests/streaming_coder/test_e2e_session_lifecycle.py` | Create | +40 |

## Session Life 完整流程圖

```
User: 派 Claude session 做 auth refactor
  ↓ detect_trigger → SESSION mode
  ↓ dispatch_trigger → run_session_task
  ↓ AcpxSessionManager.ensure_session → set_thread_agent("thread-123", "claude")
  ↓ acpx claude -s dc-123456 "做 auth refactor"
  ↓ stream → Discord edit + emoji
  ↓ ✅ done, session persists

User in thread: 把 model 改成 JWT
  ↓ detect_trigger → None (no match)
  ↓ _detect_session_follow_up → pool.has_active_session("thread-123") → True
  ↓ synthetic TriggerResult(agent="claude", mode=SESSION, prompt="把 model 改成 JWT")
  ↓ run_session_task → acpx claude -s dc-123456 "把 model 改成 JWT"
  ↓ ✅ follow-up works

[After TTL timeout]
User in thread: 繼續
  ↓ detect_trigger → None
  ↓ _detect_session_follow_up → pool.has_active_session → False
  ↓ pool.has_expired_session("thread-123") → True
  ↓ synthetic TriggerResult(agent="claude", mode=SESSION, prompt="請繼續之前的工作")
  ↓ run_session_task → ensure_session → acpx session "dc-123456" still exists
  ↓ acpx claude -s dc-123456 "請繼續之前的工作"
  ↓ ✅ resume works

User: 派 Claude 結束
  ↓ detect_trigger → SESSION_CANCEL
  ↓ dispatch_trigger → session_mgr.cancel("thread-123")
  ↓ ✅ session closed
```
