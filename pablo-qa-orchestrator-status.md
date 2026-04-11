# Pablo QA Orchestrator — 現況與下一步

> 建立日期：2026-04-11 | 最後更新：2026-04-11
> 對應 Session：蚵阿麵線神教 Discord thread #1492027003602337913

---

## 一、Pablo 是什麼？

Pablo 是 **Hermes Agent 的專用 QA Orchestrator 分身**（Profile），
部署在 `~/.hermes/profiles/pablo/`，由獨立 gateway 管理。

```
┌─────────────────────────────────────────────────┐
│  歐文 (zero)                                     │
│    │ Discord ping                                │
│    ▼                                             │
│  [Pablo Gateway]  ← HERMES_HOME=~/.hermes/      │
│    │ profiles/pablo                              │
│    │                                            │
│    ├─ #ml        (id: 1108541523630489630)       │
│    ├─ #gpt       (id: 1113289897978114159)       │
│    ├─ #github    (id: 1113328400971612171)       │
│    ├─ #trade     (id: 1270949584205643809)       │
│    └─ +更多頻道…                                   │
└─────────────────────────────────────────────────┘
```

---

## 二、Pablo 目前配置

| 項目 | 值 |
|------|-----|
| Model | `gpt-5.3-codex` |
| Provider | `openai-codex` |
| Profile 路徑 | `~/.hermes/profiles/pablo/` |
| SOUL.md | Default（尚未客製） |
| Skills | 26 個分類已啟用（devops, dogfood, github, mlops, research…） |
| Gateway | 運行中，PID 見 `gateway.pid` |
| Discord 頻道 | 蚵阿麵線神教伺服器，多頻道監聽 |
| Max turns | 90 |
| Gateway timeout | 1800s（30 min） |

---

## 三、架構定位：Pablo 在 HIL QA 系統中的角色

```
         ┌──────────────┐
         │   歐文 (PM)  │
         └──────┬───────┘
                │ 需求、Bug、指令
                ▼
    ┌───────────────────────┐
    │  Pablo (Orchestrator) │  ← 就是這個分身
    │  Profile: pablo       │
    │  Model: gpt-5.3-codex │
    └───┬───┬───┬───┬───────┘
        │   │   │   │
   ┌────▼┐ ┌▼──┐┌▼──┐┌▼────┐
   │Explorer│Automator│Runner│Observer│
   └──────┘└─────┘└─────┘└──────┘
        子代理 (subagent) 分工

    Explorer   → 理解需求、查 spec、走查 UI
    Automator  → 寫測試腳本、tool calling
    Runner     → 執行 pytest/Robot Framework
    Observer   → 收集證據（截圖、log、波形）
```

---

## 四、OpenRouter 免費模型 × Tool Calling 能力

### 為什麼重要？

Pablo 若要降低 API 成本，可以用 OpenRouter 免費模型做輕量任務
（如 Explorer 先行探索、static analysis），但前提是**模型必須支援 tool calling**。

### 查詢方法

```bash
# 靜態查 supported_parameters
curl -s https://openrouter.ai/api/v1/models | \
  python3 -c "import sys,json; ms=json.load(sys.stdin)['data'];
  free=[m for m in ms if ':free' in m['id']];
  [print(f\"{m['id']:50s} tools={'tools' in set(m.get('supported_parameters',[]))}  ctx={m.get('context_length')}\") 
   for m in free]"
```

### 結果（2026-04-11 即時查詢）

共 **24 個免費模型**，其中 **支援 tool calling 的有 15 個**：

| 模型 | tools | tool_choice | Context |
|------|-------|-------------|---------|
| `arcee-ai/trinity-large-preview:free` | ✓ | ✗ | 131K |
| `google/gemma-4-26b-a4b-it:free` | ✓ | ✓ | 262K |
| `google/gemma-4-31b-it:free` | ✓ | ✓ | 262K |
| `meta-llama/llama-3.3-70b-instruct:free` | ✓ | ✓ | 65K |
| `minimax/minimax-m2.5:free` | ✓ | ✗ | 196K |
| `nvidia/nemotron-3-nano-30b-a3b:free` | ✓ | ✓ | 256K |
| `nvidia/nemotron-3-super-120b-a12b:free` | ✓ | ✓ | 262K |
| `nvidia/nemotron-nano-12b-v2-vl:free` | ✓ | ✓ | 128K |
| `nvidia/nemotron-nano-9b-v2:free` | ✓ | ✓ | 128K |
| `openai/gpt-oss-20b:free` | ✓ | ✓ | 131K |
| `openai/gpt-oss-120b:free` | ✓ | ✓ | 131K |
| `qwen/qwen3-coder:free` | ✓ | ✓ | 262K |
| `qwen/qwen3-next-80b-a3b-instruct:free` | ✓ | ✓ | 262K |
| `z-ai/glm-4.5-air:free` | ✓ | ✓ | 131K |

### 動態驗證 Tool Calling（Runtime Probe）

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-oss-20b:free",
    "messages": [{"role":"user","content":"台北現在幾度？"}],
    "tools": [{
      "type":"function",
      "function":{
        "name":"get_weather",
        "description":"Get weather by city",
        "parameters":{
          "type":"object",
          "properties":{"city":{"type":"string"}},
          "required":["city"]
        }
      }
    }],
    "tool_choice":"auto"
  }'
# 回傳有 choices[0].message.tool_calls = 支援
```

---

## 五、Pablo 可用的低成本模型建議

### Tier 1: 強推理 + Tool Calling（主力）
| 模型 | 特色 | 建議用途 |
|------|------|---------|
| `qwen/qwen3-coder:free` | 262K ctx, code 強 | Automator 子代理 |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262K ctx, 工具調用穩定 | Explorer |
| `openai/gpt-oss-120b:free` | 131K ctx, OpenAI 格式 | 通用備援 |

### Tier 2: 輕量 + 快速
| 模型 | 特色 | 建議用途 |
|------|------|---------|
| `google/gemma-4-31b-it:free` | 262K ctx, 多模態 | Observer 快速截圖分析 |
| `nvidia/nemotron-nano-9b-v2:free` | 128K, 低延遲 | 靜態文件解析 |
| `z-ai/glm-4.5-air:free` | 131K, 中文強 | 中文 spec/規格文件分析 |

---

## 六、如何在新 Session 繼續討論

### 方法 A：使用 session_search（本機）
```
# 在新 session 中輸入：
session_search(query="Pablo QA orchestrator OpenRouter free")
# 會回傳這份文件涉及的 session 摘要
```

### 方法 B：直接讀取 owen-study 文件
```
# 這份文件位置：
~/source/github.com/owen-study/pablo-qa-orchestrator-status.md

# 相關背景文件：
~/source/github.com/owen-study/hermes-qa-architecture-report.md    (QA 三層架構)
~/source/github.com/owen-study/web-testing-automation-report.md    (Web 自動化)
~/source/github.com/owen-study/hermes-graphify-integration-plan.md (知識圖譜)
```

### 方法 C：Ping Pablo 直接互動
在蚵阿麵線神教的對應頻道直接 `<@&1478013466886279211>` ping Pablo，
Pablo 會從自己的 session memory 記得上下文。

---

## 七、下一步行動清單

- [ ] **Pablo SOUL.md 客製化**：加入 QA orchestrator 人格定義
- [ ] **OpenRouter 免費模型路由**：在 pablo config 加入 `fallback_providers` 使用免費模型
- [ ] **Explorer 子代理 prompt**：針對 HIL 裝置探索任務優化
- [ ] **TestLink API 整合**：接上 Pablo 做 test case 管理
- [ ] **證據收集 pipeline**：Observer 子代理的截圖/log 收集機制
- [ ] **OpenRouter 免費模型實測**：跑一次完整的 tool calling benchmark

---

## 八、關鍵原則

1. **Pablo 是 Orchestrator，不是 Runner** — 子代理做事，Pablo 做決策
2. **免費模型只做輕量任務** — 複雜推理仍用 gpt-5.3-codex
3. **Tool Calling 是硬門檻** — 不支援的模型連 Explorer 都不行
4. **證據 > 口頭報告** — 每次測試都要附截圖/log/截圖

---

*本文件同步至 `codeofthrone-agent/owen-study`，方便跨 session 繼續討論。*
