# Streaming Coder × Hermes 整合計畫

> **目標：** 把 `streaming_coder` 模組嵌入 Hermes Discord gateway，實現 OpenAB 風格的即時串流 UX。
>
> **核心原則：** 擴展現有組件，不建立平行系統。

---

## 1. 整合點分析

### 1.1 訊息流程

```
Discord 訊息
    │
    ▼
_handle_message (line 2304)
    │ 認證檢查、指令檢查
    ▼
_handle_message_with_agent (line 3022)
    │ session 建立、context 準備
    │
    ├──► 🔥 新增：檢測 coding trigger
    │    如果命中 → route_to_streaming_coder()
    │    不命中 → 繼續原有流程
    │
    ▼
_run_agent (line 7160) ← 原有 agent loop
```

### 1.2 可重用的現有組件

| 組件 | 位置 | 可重用？ | 用途 |
|------|------|---------|------|
| `GatewayStreamConsumer` | `gateway/stream_consumer.py` | ✅ | 1.5s edit loop、flood control、truncation |
| `DiscordAdapter.send()` | `gateway/platforms/discord.py:765` | ✅ | 發送訊息 |
| `DiscordAdapter.edit_message()` | `gateway/platforms/discord.py:855` | ✅ | 編輯訊息（串流用） |
| `DiscordAdapter._add_reaction()` | `gateway/platforms/discord.py:719` | ✅ | 加 reaction |
| `DiscordAdapter._remove_reaction()` | `gateway/platforms/discord.py:730` | ✅ | 移 reaction |
| `DiscordAdapter._auto_create_thread()` | `gateway/platforms/discord.py:2023` | ✅ | 自動開 thread |
| `DiscordAdapter.on_processing_start()` | `gateway/platforms/discord.py:745` | ✅ | 👀 reaction |
| `DiscordAdapter.on_processing_complete()` | `gateway/platforms/discord.py:753` | ✅ | ✅/❌ reaction |

### 1.3 GatewayStreamConsumer 架構

```
sync thread                         async task
    │                                   │
AIAgent.stream_delta_callback ──► consumer.on_delta(text)
                                      │
                                 queue.Queue (thread-safe)
                                      │
                                 consumer.run() ← asyncio task
                                      │
                                 buffer + rate-limit
                                      │
                                 adapter.edit_message()
```

**我們要做的：** 讓 acpx 的 ACP events 也能走這條路。

---

## 2. 實作計畫

### Task 1: 建立 `AcpStreamAdapter` — 將 ACP events 轉為 GatewayStreamConsumer 可用的 deltas

**檔案：** `streaming_coder/acp_adapter.py`（新建）

這個 adapter 從 acpx 的 asyncio Queue 讀取 AcpEvent，轉換為 text deltas 餵給 GatewayStreamConsumer。

```python
class AcpStreamAdapter:
    """將 ACP event stream 轉為 GatewayStreamConsumer 的 delta callback。"""

    def __init__(self, consumer: GatewayStreamConsumer, reactions_controller):
        self.consumer = consumer
        self.reactions = reactions_controller
        self.tool_lines = []  # ToolLine tracking

    async def run(self, event_queue: asyncio.Queue):
        """從 event_queue 讀取 AcpEvent，轉換為 deltas。"""
        while True:
            event = await event_queue.get()
            if event is None:  # EOF sentinel
                break

            if event.event_type == AcpEventType.TEXT_CHUNK:
                self.consumer.on_delta(event.text)
            elif event.event_type == AcpEventType.THOUGHT_CHUNK:
                await self.reactions.set_thinking()
            elif event.event_type == AcpEventType.TOOL_CALL:
                await self.reactions.set_tool(event.tool_title)
                # 不把 tool lines 作為 delta（會亂掉）
                # 改為在 compose_display 中處理
            elif event.event_type == AcpEventType.TOOL_CALL_UPDATE:
                if event.tool_status in ("completed", "failed"):
                    await self.reactions.set_thinking()
            elif event.event_type == AcpEventType.ERROR:
                self.consumer.on_delta(f"\n⚠️ {event.error_message}")

        self.consumer.finish()
```

### Task 2: 建立 `StreamingReactionController` — 包裝現有的 reaction 方法

**檔案：** `streaming_coder/reactions.py`（擴充）

將 `StatusReactionController` 改為接受 Discord adapter 的 `_add_reaction` / `_remove_reaction` 方法：

```python
class StreamingReactionController:
    """包裝 Discord adapter 的 reaction 方法 + debounce/stall。"""

    def __init__(self, adapter, raw_message, emojis, timing):
        self._add = adapter._add_reaction
        self._remove = adapter._remove_reaction
        self.message = raw_message
        self.emojis = emojis
        self.timing = timing
        # ... debounce/stall 邏輯跟現有 reactions.py 一致
```

### Task 3: 在 `_handle_message_with_agent` 中加入 trigger 檢測

**檔案：** `gateway/run.py`（修改）

在 `_handle_message_with_agent` 方法中，`_run_agent` 調用之前加入：

```python
# === STREAMING CODER INTERCEPT ===
# Check if this message triggers an external coding agent
try:
    from streaming_coder.bridge import detect_agent_trigger
    trigger = detect_agent_trigger(message_text)
    if trigger:
        agent_name, prompt = trigger
        streaming_result = await self._handle_streaming_coding_task(
            event=event,
            source=source,
            agent_name=agent_name,
            prompt=prompt,
            message_text=message_text,
        )
        if streaming_result is not None:
            return streaming_result  # Handled by streaming coder
except ImportError:
    pass  # streaming_coder not installed
# === END INTERCEPT ===
```

### Task 4: 實作 `_handle_streaming_coding_task` 方法

**檔案：** `gateway/run.py`（新增方法）

```python
async def _handle_streaming_coding_task(
    self, event, source, agent_name: str, prompt: str, message_text: str
) -> Optional[str]:
    """處理 coding trigger：spawn acpx → stream → edit message → reactions。"""

    adapter = self.adapters.get(source.platform)
    if not adapter:
        return None

    # 1. 取得原始訊息（用於 reaction）
    raw_message = event.raw_message

    # 2. 👀 reaction（開始處理）
    await adapter.on_processing_start(event)

    # 3. 發送 placeholder 訊息
    placeholder = await adapter.send(source.chat_id, "...")
    if not placeholder.success:
        return None
    placeholder_msg_id = placeholder.message_id

    # 4. 決定是否開 thread（頻道中開，thread 中不開）
    thread_id = None
    chat_id = source.chat_id
    if hasattr(raw_message, 'create_thread'):
        # 在頻道中 → 開 thread
        try:
            thread = await raw_message.create_thread(
                name=prompt[:40],
                auto_archive_duration=1440,
            )
            thread_id = str(thread.id)
            # 把 placeholder 移到 thread 裡（重新發）
            await adapter.edit_message(chat_id, placeholder_msg_id, "...")
            # 在 thread 裡發新的 placeholder
            thread_placeholder = await adapter.send(
                chat_id, "...", metadata={"thread_id": thread_id}
            )
            placeholder_msg_id = thread_placeholder.message_id
            chat_id = thread_id
        except Exception:
            pass  # 開 thread 失敗，繼續在原頻道

    # 5. 啟動 streaming
    from streaming_coder.bridge import run_streaming_task
    from streaming_coder.reactions import StreamingReactionController

    reactions = StreamingReactionController(
        adapter=adapter,
        raw_message=raw_message,
        emojis=...,  # 從 config 讀取
        timing=...,
    )

    result = await run_streaming_task(
        agent=agent_name,
        prompt=prompt,
        chat_id=chat_id,
        message_id=placeholder_msg_id,
        adapter=adapter,
        reactions=reactions,
        workdir=self._get_workdir(source),
    )

    # 6. 完成 reaction
    if result.get("success"):
        await reactions.set_done()
    else:
        await reactions.set_error()

    await adapter.on_processing_complete(
        event,
        ProcessingOutcome.SUCCESS if result.get("success") else ProcessingOutcome.FAILURE
    )

    return result.get("response", "")
```

### Task 5: 更新 `streaming_coder/bridge.py` 的 `run_streaming_task`

**檔案：** `streaming_coder/bridge.py`（修改）

將 `run_streaming_task` 改為接受 adapter 參數，使用 Hermes 的 `edit_message` 而非假設的 Discord message object：

```python
async def run_streaming_task(
    agent: str,
    prompt: str,
    chat_id: str,
    message_id: str,
    adapter,  # DiscordAdapter instance
    reactions: StreamingReactionController,
    workdir: str = ".",
    config: Optional[Config] = None,
) -> dict:
    """
    完整串流任務：
    1. spawn acpx subprocess
    2. 解析 JSON-RPC stream
    3. 每 1.5s edit Discord message
    4. 更新 reactions
    """
    cfg = config or Config()

    # Spawn acpx
    proc = await spawn_acpx(agent, prompt, workdir, cfg)

    # 建立 edit callback（使用 adapter 的 edit_message）
    async def edit_fn(chat_id, msg_id, content):
        await adapter.edit_message(chat_id, msg_id, content)

    # Streaming loop
    editor = StreamingEditor(
        edit_fn=lambda msg, content: edit_fn(chat_id, message_id, content),
        message=None,
        interval=1.5,
    )

    # 啟動 edit loop
    editor.start()

    try:
        # 解析 acpx stdout
        async for event in stream_acpx_output(proc):
            if event.event_type == AcpEventType.TEXT_CHUNK:
                editor.add_text(event.text)
            elif event.event_type == AcpEventType.TOOL_CALL:
                editor.add_tool_start(event.tool_call_id, event.tool_title)
                await reactions.set_tool(event.tool_title)
            elif event.event_type == AcpEventType.TOOL_CALL_UPDATE:
                editor.set_tool_done(
                    event.tool_call_id, event.tool_title, event.tool_status
                )
                if event.tool_status in ("completed", "failed"):
                    await reactions.set_thinking()
            elif event.event_type == AcpEventType.THOUGHT_CHUNK:
                await reactions.set_thinking()
            elif event.event_type == AcpEventType.ERROR:
                editor.add_text(f"\n⚠️ {event.error_message}")
            elif event.event_type == AcpEventType.RESULT:
                break
    finally:
        editor.stop()

    # Final split and send
    chunks = editor.split_final(2000)
    if chunks:
        await edit_fn(chat_id, message_id, chunks[0])
        for chunk in chunks[1:]:
            await adapter.send(chat_id, chunk, metadata={"thread_id": chat_id})

    return {"success": True, "response": editor.text_buf}
```

---

## 3. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `streaming_coder/acp_adapter.py` | 新建 | ACP events → GatewayStreamConsumer deltas |
| `streaming_coder/reactions.py` | 修改 | 接受 adapter 的 reaction 方法 |
| `streaming_coder/bridge.py` | 修改 | `run_streaming_task` 使用 adapter API |
| `gateway/run.py` | 修改 | 加 trigger 檢測 + `_handle_streaming_coding_task` |
| `streaming_coder/config.py` | 小改 | 讀取 hermes config.yaml 中的 streaming 設定 |

**不需要修改的檔案：**
- ❌ `gateway/platforms/discord.py` — 直接使用現有的 send/edit/reaction 方法
- ❌ `gateway/stream_consumer.py` — 參考但不修改
- ❌ `run_agent.py` — 不動 agent loop

---

## 4. 實作順序

| Task | 內容 | 時間 | 依賴 |
|------|------|------|------|
| 1 | `acp_adapter.py` — ACP → deltas 轉換 | 30min | 無 |
| 2 | 修改 `reactions.py` — adapter 包裝 | 20min | 無 |
| 3 | 修改 `bridge.py` — `run_streaming_task` 使用 adapter | 40min | 1, 2 |
| 4 | 修改 `gateway/run.py` — trigger 檢測 + handler | 40min | 3 |
| 5 | 修改 `config.py` — hermes config 整合 | 15min | 無 |
| 6 | 端到端測試 | 30min | 1-5 |
| **總計** | | **~3h** | |

---

## 5. 驗收標準

1. ✅ `派 Claude 實作 auth middleware` → 自動開 thread → 即時串流
2. ✅ Discord message 上有 👀→🤔→🔥→👍 + random face 反應
3. ✅ Tool call 以 🔧 Running → ✅ Completed 狀態顯示
4. ✅ 同一 thread follow-up 不需要再 @
5. ✅ 簡單訊息（非 trigger）走原有 agent loop，不受影響
6. ✅ streaming_coder import 失敗時 gracefully fallback
7. ✅ 不破壞現有任何功能

---

## 6. 風險與對策

| 風險 | 對策 |
|------|------|
| 跟現有 `on_processing_start/complete` reaction 衝突 | streaming handler 自己管理 reaction，不調用原有方法 |
| acpx subprocess 洩漏 | `proc.kill()` 在 finally 中，加 atexit handler |
| Discord rate limit | 複用 GatewayStreamConsumer 的 flood control 邏輯 |
| import 失敗 | try/except ImportError 包裹，fallback 到原有流程 |
| 事件循環衝突 | 使用 `asyncio.create_task`，不阻塞 gateway loop |
