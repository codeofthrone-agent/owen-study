# Streaming Coding UX — 完整實作計畫 v2

> **目標：** 把 OpenAB 的即時串流 UX 帶進 Hermes，讓 coding CLI 的輸出即時反映到 Discord 訊息上。
>
> **研究基礎：** 完整分析 OpenAB v0.7.1 源碼（Rust, 7 個模組, ~70KB）
>
> **核心需求：**
> 1. Edit-streaming（每 1.5s 更新 Discord message）
> 2. Emoji 狀態反應（👀→🤔→🔥→👍 + random face）
> 3. Tool call 狀態追蹤（🔧 Running → ✅ Completed / ❌ Failed）
> 4. Thread-based 多輪對話（自動開 thread）
> 5. Session 持久化（每 thread 一個 CLI process）

---

## 1. OpenAB 源碼深度解析

### 1.1 模組架構

```
src/
├── main.rs              入口：Config → SessionPool → Discord Handler
├── config.rs            Config 結構（TOML 解析 + env var 展開）
├── discord.rs           Discord EventHandler + stream_prompt（核心）
├── acp/
│   ├── mod.rs           匯出：SessionPool, AcpEvent, ContentBlock
│   ├── pool.rs          SessionPool：thread_id → AcpConnection（每 thread 一個 CLI）
│   ├── connection.rs    AcpConnection：spawn CLI + JSON-RPC over stdin/stdout
│   └── protocol.rs      JSON-RPC 訊息 + ACP notification 分類
├── reactions.rs         StatusReactionController（debounce + stall detection）
├── format.rs            split_message（2000 char 切割）+ truncate_chars
├── error_display.rs     錯誤格式化（coded error + user error）
└── stt.rs               語音轉文字（OpenAI-compatible API）
```

### 1.2 Session Pool（`acp/pool.rs`）

```rust
pub struct SessionPool {
    connections: RwLock<HashMap<String, AcpConnection>>,  // thread_id → conn
    config: AgentConfig,
    max_sessions: usize,  // default: 10
}
```

**關鍵設計：**
- `get_or_create(thread_id)`：Double-check locking（先 read lock 檢查 alive，再 write lock 建立）
- `cleanup_idle(ttl_secs)`：每 60 秒清理超過 TTL 的 session（default 24h）
- `shutdown()`：清除所有 connections，`kill_on_drop` 自動殺子進程
- `with_connection(thread_id, closure)`：提供 mutable access，確保先 call get_or_create

**Python 實作等價：**

```python
class SessionPool:
    def __init__(self, agent_config: dict, max_sessions: int = 10):
        self.connections: dict[str, AcpConnection] = {}  # thread_id → conn
        self.config = agent_config
        self.max_sessions = max_sessions
        self._lock = asyncio.Lock()

    async def get_or_create(self, thread_id: str) -> "AcpConnection":
        # Fast path: existing alive connection
        if thread_id in self.connections and self.connections[thread_id].alive():
            return self.connections[thread_id]

        async with self._lock:
            # Double-check after lock
            if thread_id in self.connections and self.connections[thread_id].alive():
                return self.connections[thread_id]

            if len(self.connections) >= self.max_sessions:
                raise PoolExhaustedError(f"pool exhausted ({self.max_sessions} sessions)")

            conn = await AcpConnection.spawn(
                self.config["command"],
                self.config.get("args", []),
                self.config.get("working_dir", "/tmp"),
                self.config.get("env", {}),
            )
            await conn.initialize()
            await conn.session_new(self.config.get("working_dir", "/tmp"))

            self.connections[thread_id] = conn
            return conn
```

### 1.3 ACP Connection（`acp/connection.rs`）

**這是 OpenAB 最核心的模組。**

```rust
pub struct AcpConnection {
    _proc: Child,                           // 子進程
    stdin: Arc<Mutex<ChildStdin>>,          // 寫入端
    next_id: AtomicU64,                     // JSON-RPC request ID
    pending: Arc<Mutex<HashMap<u64, oneshot::Sender>>>,  // 等待中的 request
    notify_tx: Arc<Mutex<Option<mpsc::UnboundedSender>>>,  // streaming 通知
    acp_session_id: Option<String>,         // ACP session ID
    last_active: Instant,                   // 最後活躍時間
    session_reset: bool,                    // session 過期標記
    _reader_handle: JoinHandle,             // stdout reader task
}
```

**關鍵機制：**

1. **spawn**：`tokio::process::Command` → `kill_on_drop(true)`
2. **stdout reader**（背景 task）：
   - 每行 read_line → parse as JSON-RPC
   - 如果是 `session/request_permission` → 自動回覆 `allow_always`
   - 如果有 `id` → resolve pending（oneshot）+ forward to subscriber（mpsc）
   - 如果是 notification → forward to subscriber
3. **session_prompt(content_blocks)** → 返回 `(mpsc::Receiver, request_id)`
4. **ACP notification 分類**（`protocol.rs`）：

```rust
enum AcpEvent {
    Text(String),              // agent_message_chunk
    Thinking,                  // agent_thought_chunk
    ToolStart { id, title },   // tool_call / tool_call_update (running)
    ToolDone { id, title, status },  // tool_call_update (completed/failed)
    Status,                    // plan
}
```

**Python 實作等價：**

```python
import asyncio
import json
import subprocess

class AcpConnection:
    def __init__(self, proc, stdin, reader_task):
        self._proc = proc
        self._stdin = stdin
        self._reader_task = reader_task
        self._next_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._notify_queue: asyncio.Queue | None = None
        self.session_id: str | None = None
        self.last_active: float = 0
        self.session_reset = False

    @classmethod
    async def spawn(cls, command, args, workdir, env=None):
        proc = await asyncio.create_subprocess_exec(
            command, *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=workdir,
            env={**__import__('os').environ, **(env or {})},
        )
        conn = cls(proc, proc.stdin, None)

        # Background reader task
        conn._reader_task = asyncio.create_task(conn._read_loop(proc.stdout))
        return conn

    async def _read_loop(self, stdout):
        """Background task: read stdout line-by-line, dispatch"""
        while True:
            line = await stdout.readline()
            if not line:
                break  # EOF
            try:
                msg = json.loads(line.decode().strip())
            except json.JSONDecodeError:
                continue

            # Auto-reply session/request_permission
            if msg.get("method") == "session/request_permission":
                req_id = msg.get("id")
                if req_id is not None:
                    reply = {"jsonrpc": "2.0", "id": req_id, "result": {"optionId": "allow_always"}}
                    self._stdin.write((json.dumps(reply) + "\n").encode())
                    await self._stdin.drain()
                continue

            # Response (has id) → resolve pending + forward to subscriber
            if "id" in msg:
                future = self._pending.pop(msg["id"], None)
                if future and not future.done():
                    future.set_result(msg)
                if self._notify_queue:
                    await self._notify_queue.put(msg)
                continue

            # Notification → forward to subscriber
            if self._notify_queue:
                await self._notify_queue.put(msg)

    async def initialize(self):
        resp = await self._send_request("initialize", {
            "protocolVersion": 1,
            "clientCapabilities": {},
            "clientInfo": {"name": "hermes", "version": "1.0.0"},
        })

    async def session_new(self, cwd):
        resp = await self._send_request("session/new", {"cwd": cwd, "mcpServers": []})
        self.session_id = resp["result"]["sessionId"]

    async def session_prompt(self, content_blocks):
        """Send prompt, return (asyncio.Queue for notifications, request_id)"""
        self._notify_queue = asyncio.Queue()
        req_id = self._next_id; self._next_id += 1

        await self._send_raw({
            "jsonrpc": "2.0", "id": req_id,
            "method": "session/prompt",
            "params": {
                "sessionId": self.session_id,
                "prompt": content_blocks,
            }
        })

        return self._notify_queue, req_id

    async def _send_request(self, method, params=None, timeout=30):
        req_id = self._next_id; self._next_id += 1
        future = asyncio.get_event_loop().create_future()
        self._pending[req_id] = future

        await self._send_raw({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})

        return await asyncio.wait_for(future, timeout=timeout)

    async def _send_raw(self, data):
        self._stdin.write((json.dumps(data) + "\n").encode())
        await self._stdin.drain()

    def alive(self):
        return self._proc.returncode is None
```

### 1.4 Streaming（`discord.rs` → `stream_prompt`）

**這是 OpenAB 的靈魂函數。**

```
session_prompt → get notification queue
         │
    spawn edit task（每 1500ms 檢查 buffer 變化 → edit Discord message）
         │
    while rx.recv():
         ├── AcpEvent::Text(t)      → text_buf += t → buf_tx.send(compose_display)
         ├── AcpEvent::Thinking     → reactions.set_thinking()
         ├── AcpEvent::ToolStart    → tool_lines.append() → reactions.set_tool()
         └── AcpEvent::ToolDone     → tool_lines[id].state = Done → reactions.set_thinking()
         │
    conn.prompt_done()
    final edit（split_message if > 2000 chars）
```

**Edit task 細節：**

```rust
// Spawn edit-streaming task
tokio::spawn(async move {
    let mut last_content = String::new();
    loop {
        tokio::time::sleep(Duration::from_millis(1500)).await;
        if buf_rx.has_changed() {
            let content = buf_rx.borrow_and_update().clone();
            if content != last_content {
                let display = if content.chars().count() > 1900 {
                    format::truncate_chars(&content, 1900) + "…"
                } else {
                    content.clone()
                };
                edit(&ctx, channel, msg_id, &display).await;
                last_content = content;
            }
        }
    }
});
```

**compose_display 組合邏輯：**

```rust
fn compose_display(tool_lines: &[ToolEntry], text: &str) -> String {
    let mut out = String::new();
    for entry in tool_lines {
        let icon = match entry.state {
            Running => "🔧",
            Completed => "✅",
            Failed => "❌",
        };
        let suffix = if entry.state == Running { "..." } else { "" };
        out.push_str(&format!("{icon} `{}`{suffix}\n", entry.title));
    }
    if !tool_lines.is_empty() { out.push('\n'); }
    out.push_str(text.trim_end());
    out
}
```

**Python 實作等價：**

```python
class StreamingEditor:
    """每 1.5s 檢查 buffer 變化 → edit Discord message"""

    def __init__(self, edit_fn, message, interval=1.5, max_chars=1900):
        self.edit_fn = edit_fn       # async def edit_fn(message, content)
        self.message = message
        self.interval = interval
        self.max_chars = max_chars
        self.text_buf = ""
        self.tool_lines: list[ToolLine] = []
        self._last_content = ""
        self._task = None

    def start(self):
        self._task = asyncio.create_task(self._edit_loop())

    async def _edit_loop(self):
        while True:
            await asyncio.sleep(self.interval)
            content = self.compose_display()
            if content != self._last_content:
                display = content
                if len(content) > self.max_chars:
                    display = content[:self.max_chars] + "…"
                try:
                    await self.edit_fn(self.message, display)
                except Exception:
                    pass
                self._last_content = content

    def add_text(self, chunk: str):
        self.text_buf += chunk

    def add_tool_start(self, tool_id: str, title: str):
        # Dedupe by tool_id
        for t in self.tool_lines:
            if t.id == tool_id:
                t.title = title
                t.state = "running"
                return
        self.tool_lines.append(ToolLine(id=tool_id, title=title, state="running"))

    def set_tool_done(self, tool_id: str, title: str, status: str):
        for t in self.tool_lines:
            if t.id == tool_id:
                if title:
                    t.title = title
                t.state = "completed" if status == "completed" else "failed"
                return
        self.tool_lines.append(ToolLine(id=tool_id, title=title,
                                         state="completed" if status == "completed" else "failed"))

    def compose_display(self) -> str:
        parts = []
        for t in self.tool_lines:
            icon = {"running": "🔧", "completed": "✅", "failed": "❌"}[t.state]
            suffix = "..." if t.state == "running" else ""
            safe_title = t.title.replace("\n", " ; ").replace("`", "'")
            parts.append(f"{icon} `{safe_title}`{suffix}")
        out = "\n".join(parts)
        if parts:
            out += "\n\n"
        out += self.text_buf.strip()
        return out

    def stop(self):
        if self._task:
            self._task.cancel()

    def split_final(self, limit=2000) -> list[str]:
        """Final message split for long content"""
        content = self.compose_display()
        if len(content) <= limit:
            return [content]
        chunks = []
        current = ""
        for line in content.split("\n"):
            if len(current) + len(line) + 1 > limit:
                chunks.append(current)
                current = ""
            if current:
                current += "\n"
            current += line
        if current:
            chunks.append(current)
        return chunks
```

### 1.5 Reaction 系統（`reactions.rs`）

**這是 OpenAB 的 UX 靈魂。**

```rust
pub struct StatusReactionController {
    inner: Arc<Mutex<Inner>>,
    enabled: bool,
}

struct Inner {
    http, channel, message,
    emojis: ReactionEmojis,
    timing: ReactionTiming,
    current: String,           // 當前 emoji
    finished: bool,
    debounce_handle,           // 防抖 timer
    stall_soft_handle,         // 10s 軟超時 → 🥱
    stall_hard_handle,         // 30s 硬超時 → 😨
}
```

**關鍵機制：**

| 狀態 | Emoji | 觸發時機 | Debounce |
|------|-------|---------|----------|
| queued | 👀 | 收到訊息，排入 session | 立即（apply_immediate） |
| thinking | 🤔 | ACP `agent_thought_chunk` | 700ms debounce |
| tool (coding) | 🔥 | ACP `tool_call` (exec/read/write/bash) | 700ms debounce |
| tool (web) | ⚡ | ACP `tool_call` (web_search/browser) | 700ms debounce |
| tool (generic) | 👨‍💻 | ACP `tool_call` (其他) | 700ms debounce |
| done | 🆗 | prompt 完成 + 隨機 mood face | 立即（finish） |
| error | 😱 | ACP error | 立即（finish） |
| stall_soft | 🥱 | 10s 無新事件 | 自動觸發 |
| stall_hard | 😨 | 30s 無新事件 | 自動觸發 |

**Tool 分類邏輯：**

```python
CODING_TOKENS = ["exec", "process", "read", "write", "edit", "bash", "shell"]
WEB_TOKENS = ["web_search", "web_fetch", "web-search", "web-fetch", "browser"]

def classify_tool(name: str, emojis: dict) -> str:
    n = name.lower()
    if any(t in n for t in WEB_TOKENS):
        return emojis["web"]      # ⚡
    elif any(t in n for t in CODING_TOKENS):
        return emojis["coding"]   # 🔥
    else:
        return emojis["tool"]     # 👨‍💻
```

**Debounce 細節：**

```python
class StatusReactionController:
    def __init__(self, enabled, channel, message, emojis, timing):
        self.enabled = enabled
        self.channel = channel
        self.message = message
        self.emojis = emojis  # {"queued": "👀", "thinking": "🤔", ...}
        self.timing = timing  # {"debounce_ms": 700, "stall_soft_ms": 10000, ...}
        self.current_emoji = ""
        self.finished = False
        self._debounce_task = None
        self._stall_soft_task = None
        self._stall_hard_task = None

    async def set_queued(self):
        """立即設置（不 debounce）"""
        await self._apply_immediate(self.emojis["queued"])

    async def set_thinking(self):
        """700ms debounce"""
        await self._schedule_debounced(self.emojis["thinking"])

    async def set_tool(self, tool_name: str):
        """根據 tool 名稱分類 → 700ms debounce"""
        emoji = classify_tool(tool_name, self.emojis)
        await self._schedule_debounced(emoji)

    async def set_done(self):
        """立即完成 + 隨機 mood face"""
        await self._finish(self.emojis["done"])
        faces = ["😊", "😎", "🫡", "🤓", "😏", "✌️", "💪", "🦾"]
        face = random.choice(faces)
        await self._add_reaction(face)

    async def set_error(self):
        await self._finish(self.emojis["error"])

    async def _apply_immediate(self, emoji):
        if self.finished or emoji == self.current_emoji:
            return
        self._cancel_debounce()
        old = self.current_emoji
        self.current_emoji = emoji
        await self._add_reaction(emoji)
        if old and old != emoji:
            await self._remove_reaction(old)
        self._reset_stall_timers()

    async def _schedule_debounced(self, emoji):
        if self.finished or emoji == self.current_emoji:
            self._reset_stall_timers()
            return
        self._cancel_debounce()
        self._debounce_task = asyncio.create_task(self._debounce_apply(emoji))
        self._reset_stall_timers()

    async def _debounce_apply(self, emoji):
        await asyncio.sleep(self.timing["debounce_ms"] / 1000)
        if self.finished:
            return
        old = self.current_emoji
        self.current_emoji = emoji
        await self._add_reaction(emoji)
        if old and old != emoji:
            await self._remove_reaction(old)

    async def _finish(self, emoji):
        self.finished = True
        self._cancel_all_timers()
        old = self.current_emoji
        self.current_emoji = emoji
        await self._add_reaction(emoji)
        if old and old != emoji:
            await self._remove_reaction(old)

    def _reset_stall_timers(self):
        self._cancel_stall_timers()
        self._stall_soft_task = asyncio.create_task(
            self._stall_timeout(self.timing["stall_soft_ms"] / 1000, "🥱")
        )
        self._stall_hard_task = asyncio.create_task(
            self._stall_timeout(self.timing["stall_hard_ms"] / 1000, "😨")
        )

    async def _stall_timeout(self, delay, emoji):
        await asyncio.sleep(delay)
        if self.finished:
            return
        old = self.current_emoji
        self.current_emoji = emoji
        await self._add_reaction(emoji)
        if old and old != emoji:
            await self._remove_reaction(old)
```

### 1.6 Config 參數對照

```toml
# OpenAB config.toml
[reactions]
enabled = true
remove_after_reply = false

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
stall_soft_ms = 10000     # 10s → 🥱
stall_hard_ms = 30000     # 30s → 😨
done_hold_ms = 1500
error_hold_ms = 2500

[pool]
max_sessions = 10
session_ttl_hours = 24
```

---

## 2. Python 實作計畫

### 2.1 檔案結構

```
~/.hermes/skills/devops/streaming-coding-ux/
├── PLAN.md                         ← 本文件
├── SKILL.md                        ← 使用說明
├── streaming_coder/
│   ├── __init__.py
│   ├── pool.py                     # SessionPool（thread_id → AcpConnection）
│   ├── connection.py               # AcpConnection（spawn CLI + JSON-RPC）
│   ├── protocol.py                 # JSON-RPC 訊息 + ACP notification 分類
│   ├── editor.py                   # StreamingEditor（1.5s edit loop + compose_display）
│   ├── reactions.py                # StatusReactionController（debounce + stall）
│   ├── thread_manager.py           # Thread 建立/復用管理
│   ├── config.py                   # Config 結構 + 預設值
│   └── cli_bridge.py               # 與 Hermes terminal/process tool 的橋接
├── examples/
│   ├── demo_single_task.py
│   ├── demo_multi_agent.py
│   └── demo_multi_turn.py
└── tests/
    ├── test_pool.py
    ├── test_editor.py
    ├── test_reactions.py
    └── test_protocol.py
```

### 2.2 實作順序

#### Phase 1：ACP 協議層（最底層）

**Task 1.1: `protocol.py`** — JSON-RPC 訊息 + ACP notification 分類
- JsonRpcRequest / JsonRpcResponse
- AcpEvent enum + classify_notification()
- 單元測試：解析各類 ACP 通知

**Task 1.2: `connection.py`** — AcpConnection（spawn + read loop + send）
- spawn subprocess（asyncio.create_subprocess_exec）
- _read_loop（asyncio task：readline → JSON parse → dispatch）
- Auto-reply session/request_permission
- session_prompt → return (Queue, req_id)
- 單元測試：mock subprocess 測試 read loop

**Task 1.3: `pool.py`** — SessionPool（thread_id → conn 的管理）
- get_or_create（double-check locking）
- cleanup_idle（TTL-based）
- shutdown（kill all）
- 單元測試：max_sessions 限制、cleanup

#### Phase 2：串流顯示層

**Task 2.1: `editor.py`** — StreamingEditor（核心 UX）
- ToolLine tracking（id dedupe, state machine）
- compose_display（tool lines + text buf）
- 1.5s edit loop（asyncio task）
- truncate_chars / split_message（跟 OpenAB 一致）
- 單元測試：compose_display 各狀態組合

**Task 2.2: `reactions.py`** — StatusReactionController
- Debounce（700ms）
- Stall detection（10s → 🥱, 30s → 😨）
- Tool classification（coding/web/generic）
- Done + random mood face
- 單元測試：debounce 行為、stall timeout

#### Phase 3：整合層

**Task 3.1: `config.py`** — Config 結構
- 預設值（跟 OpenAB config.toml 完全一致）
- YAML 解析
- env var 展開

**Task 3.2: `thread_manager.py`** — Thread 管理
- get_or_create_thread（Discord API）
- shorten_thread_name（GitHub URL 縮短）
- thread_id ↔ session 對應

**Task 3.3: `cli_bridge.py`** — 與 Hermes 的橋接
- detect_agent_trigger（觸發詞檢測）
- build_acpx_command / build_print_command
- stream_prompt 完整流程（spawn → edit loop → reactions → final split）

#### Phase 4：範例與測試

**Task 4.1: 完整使用範例**
- 單任務 streaming
- 多輪 thread 對話
- 並行多 agent

**Task 4.2: 整合測試**
- 端到端：spawn CLI → stream → reactions → done

---

## 3. 與 Hermes 現有架構的整合點

### 3.1 不改 Hermes 核心，只加 skill

```
Hermes Discord Gateway
    │
    │ 收到「派 Claude 修 bug」
    │
    ▼
Hermes Agent（我）
    │
    ├── 檢測觸發詞 → streaming-coding-ux skill
    │
    ├── 建立 SessionPool.get_or_create(thread_id)
    │
    ├── 建立 StatusReactionController
    │   → 👀 (queued)
    │
    ├── conn.session_prompt(content_blocks)
    │   → 🤔 (thinking)
    │
    ├── 啟動 StreamingEditor._edit_loop()
    │   │
    │   ├── while queue.get():
    │   │   ├── Text chunk → editor.add_text()
    │   │   ├── ToolStart → editor.add_tool_start() → 🔥/⚡/👨‍💻
    │   │   ├── ToolDone → editor.set_tool_done() → ✅/❌
    │   │   └── Thinking → reactions.set_thinking() → 🤔
    │   │
    │   └── editor 1.5s loop → edit Discord message
    │
    ├── conn.prompt_done()
    │
    ├── final: editor.split_final(2000)
    │   → edit first chunk, send rest as new messages
    │
    └── reactions.set_done() → 🆗 + random face 😊
```

### 3.2 與 `external-coding-cli` skill 的關係

```
用戶說「派 Claude 修 bug」
    │
    ▼
detect_agent_trigger() → ("claude", "修 bug")
    │
    ▼
分支判斷：
├── 如果 CLI 支援 ACP（claude --acp, gemini --acp）
│   → streaming_coder（本計畫，完整 streaming UX）
│
├── 如果 CLI 只有 print 模式（claude -p, codex exec）
│   → 原有 external-coding-cli 模式（一次性結果）
│
└── 如果用戶沒指定 agent
    → Hermes 自己做（terminal tools）
```

### 3.3 相容策略

| 模式 | streaming_coder 支援？ | 降級方案 |
|------|----------------------|---------|
| Claude Code `--acp` | ✅ 原生 ACP | — |
| Gemini `--acp` | ✅ 原生 ACP | — |
| Claude Code `-p` (print) | ❌ 無 ACP | 用原有模式 |
| Codex `exec` | ❌ 無 ACP | 用原有模式 |
| OpenCode `run` | ❌ 無 ACP | 用原有模式 |
| acpx wrapper | ⚠️ 部分 | 如果 acpx 輸出 ACP stream 就支援 |

---

## 4. 關鍵設計決策

### 4.1 為什麼用 ACP 而不是 print 模式？

```
Print 模式（-p）：
    terminal → CLI → 收集所有 stdout → 回傳
    ❌ 沒有中間串流
    ❌ 沒有 tool call 狀態
    ❌ 沒有 session persistence

ACP 模式（JSON-RPC over stdio）：
    spawn CLI → 雙向 JSON-RPC → 逐 token/逐 event 接收
    ✅ 即時串流（agent_message_chunk）
    ✅ Tool call 狀態追蹤
    ✅ Session persistence（thread 對應 session）
    ✅ 自動 permission reply
```

### 4.2 為什麼不直接 fork OpenAB？

| 維度 | OpenAB (Rust) | 我們 (Python) |
|------|--------------|--------------|
| 語言一致性 | 需學 Rust | 跟 Hermes 一致 |
| 整合方式 | 獨立進程 | 內嵌到 Hermes agent |
| 決策邏輯 | 無（固定模式） | 保留你 6 種模式 + 決策樹 |
| acpx 支援 | 需原生 ACP | 可同時支援 acpx 包裝 |
| 部署 | Docker/k8s | 無需額外部署 |
| Session 管理 | HashMap in memory | 可加 SQLite 持久化 |
| 多 agent | config 切換 | acpx 統一語法 |

### 4.3 ACP vs acpx 的關係

```
Claude Code ─── 原生 MCP (print -p) ─── 不支援 streaming
           └── acpx 包裝 ──────────────── ACP over stdio → 可 streaming

Kiro CLI ─── 原生 ACP ────────────────── 直接可用
Codex ──────── acpx codex adapter ────── ACP over stdio → 可 streaming
Gemini ─────── 原生 ACP (--acp) ──────── 直接可用
```

---

## 5. 驗收標準

1. ✅ `派 Claude 實作 auth middleware` → 自動開 thread → 即時串流
2. ✅ Discord message 上有 👀→🤔→🔥→👍 + random face 反應
3. ✅ Tool call 以 🔧 Running → ✅ Completed / ❌ Failed 狀態顯示
4. ✅ 同一 thread follow-up 不需要再 @
5. ✅ 簡單任務仍用 print 模式（不開 thread、不 streaming）
6. ✅ 最終訊息超過 2000 字元自動 split
7. ✅ Discord rate limit 自動 debounce（700ms）
8. ✅ 10s 無回應 → 🥱，30s → 😨
9. ✅ 不破壞原有 `external-coding-cli` skill 的任何模式
10. ✅ Session pool 超過 max → 顯示「服務忙碌」而非崩潰

---

## 6. 預估工時

| Phase | Task | 時間 |
|-------|------|------|
| 1 | ACP 協議層（protocol + connection + pool） | 2h |
| 2 | 串流層（editor + reactions） | 1.5h |
| 3 | 整合層（config + thread + bridge） | 1h |
| 4 | 範例 + 測試 | 0.5h |
| **總計** | | **5h** |
