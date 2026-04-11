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

## 四、如何在新 Session 繼續討論

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

## 五、下一步行動清單

- [ ] **Pablo SOUL.md 客製化**：加入 QA orchestrator 人格定義
- [ ] **Explorer 子代理 prompt**：針對 HIL 裝置探索任務優化
- [ ] **TestLink API 整合**：接上 Pablo 做 test case 管理
- [ ] **證據收集 pipeline**：Observer 子代理的截圖/log 收集機制

---

## 六、關鍵原則

1. **Pablo 是 Orchestrator，不是 Runner** — 子代理做事，Pablo 做決策
2. **證據 > 口頭報告** — 每次測試都要附截圖/log/截圖

---

*本文件同步至 `codeofthrone-agent/owen-study`，方便跨 session 繼續討論。*
