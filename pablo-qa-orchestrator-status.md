# Pablo QA Orchestrator — 現況與下一步

> 建立日期：2026-04-10 | 最後更新：2026-04-11
> 對應 Session：蚵阿麵線神教 Discord thread `<@&1478013466886279211> ping` (221 messages)

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
│    └─ #qa (id: 1484369654364246086) — 專屬頻道    │
│       agents-chat 頻道需 mention 才會回應          │
└─────────────────────────────────────────────────┘
```

---

## 二、Pablo 目前配置

| 項目 | 值 |
|------|-----|
| Model | `gpt-5.4` (openai-codex) |
| Profile 路徑 | `~/.hermes/profiles/pablo/` |
| Gateway label | `ai.hermes.gateway-pablo` |
| Gateway 啟動 | `launchctl start ai.hermes.gateway-pablo` |
| SOUL.md | Default（尚未客製） |
| Skills | 26 個分類已啟用（devops, dogfood, github, mlops, research…） |
| Discord 專屬頻道 | `#qa` (1484369654364246086) — 不需 mention |
| Discord 公共頻道 | `#agents-chat` (1442675215888027691) — 需 mention |
| Max turns | 90 |
| Gateway timeout | 1800s（30 min） |

---

## 三、Discord 頻道路由規則（4 個 Agent 一致）

| Agent | 專屬頻道 | agents-chat mention |
|-------|---------|---------------------|
| zero | `#zero` (1489511393332953138), `#owen` (1443033407755124769) | 需要 |
| cary | `#阿竹` (1477683035808727173) | 需要 |
| doh | `#cbas` (1479322285600014457) | 需要 |
| Pablo | `#qa` (1484369654364246086) | 需要 |

**共通規則：** 所有 agent 在 `#agents-chat` 都需 mention。
`DISCORD_ALLOWED_USERS=434010342725648385` 已設定在所有 agent 的 `.env`。

---

## 四、HIL QA 架構定案

### 已定案的設計決策

| 面向 | 決策 |
|------|------|
| 測試管理中心 | **TestLink** — 人類可讀的測試案例管理 |
| 測試執行框架 | **Robot Framework** — executable source |
| Mobile automation | **Appium + 實體 Android/iOS** |
| Lab integrations | Robot arm / camera / sensor / flasher 整合進 RF custom libraries |
| CI/CD 主軸 | firmware + Android + iOS build |
| Backend 模式 | **無 staging/sandbox** — 直接對真實後端驗證 |

### 四者責任分界

```
TestLink   = 管理面（testcase / plan / execution history / requirement trace）
Robot      = 執行面（executable suites / keywords / setup / teardown）
Graph      = 關聯面（requirement-feature-device-test-artifact 關聯與風險分析）
Artifact   = 真相面（證據與真相：截圖 / log / 波形 / 錄影）
```

### 三層圖譜架構

```
┌──────────────────────────────┐
│ Layer 1: Historical Intent   │  ← 舊 spec / 舊流程 / Redmine ticket
│ 回答：原本設計想做什麼？       │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Layer 2: Current Evidence    │  ← code / API / DB / UI / logs / 近期 bug
│ 回答：現在系統實際怎麼運作？   │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Layer 3: QA/Test Knowledge   │  ← test cases / selectors / contracts / fixtures
│ 回答：怎麼測、測哪裡、依據啥？ │
└──────────────────────────────┘
```

**關鍵原則：** 舊 spec + Redmine 是「骨架」，不是真相。
所有圖譜邊必須分級：`confirmed / stale / inferred / conflicted`

---

## 五、已整合的專案

### robot-multiplatform-automation

- **來源：** GitLab `gitlab.com/thortron/tools/robot-multiplatform-automation`
- **本機：** `/Users/owen/source/gitlab/robot-multiplatform-automation`
- **角色：** Robot Framework 測試執行骨架（多平台 + 多裝置 + TestLink 回填）
- **帳號：** GitLab `owen.ke`（glab 1.92.0 已登入）

### owen-study（研究報告倉庫）

- **來源：** `github.com/codeofthrone-agent/owen-study`
- **本機：** `/Users/owen/source/github.com/owen-study/`
- **相關報告：**
  - `hermes-graphify-suitability-report.md` — Graphify 結構化檢索評估
  - `hermes-qa-architecture-report.md` — QA 三層 Agent 架構
  - `web-testing-automation-report.md` — Web 自動化策略
  - `gemini-cli-chrome-mcp-web-automation.md` — Chrome DevTools MCP

---

## 六、Pablo 在 HIL QA 系統中的角色

```
         ┌──────────────┐
         │   歐文 (PM)  │
         └──────┬───────┘
                │ 需求、Bug、指令
                ▼
    ┌───────────────────────┐
    │  Pablo (Orchestrator) │  ← 就是這個分身
    │  Profile: pablo       │
    │  Model: gpt-5.4       │
    └───┬───┬───┬───┬───────┘
        │   │   │   │
   ┌────▼┐ ┌▼──┐┌▼──┐┌▼────┐
   │Explorer│Automator│Runner│Observer│
   └──────┘└─────┘└─────┘└──────┘
        子代理 (subagent) 分工

    Explorer   → 理解需求、查 spec、走查 UI
    Automator  → 寫測試腳本、tool calling
    Runner     → 執行 Robot Framework
    Observer   → 收集證據（截圖、log、波形）
```

### HIL 系統縮圖版

```
Redmine + Legacy Spec
       │
       ▼
    TestLink ─────┐
       │          │
       ▼          │
  Knowledge Graph │
       │          │
       └────► Hermes QA Orchestrator (Pablo)
              │
              ▼
         Robot Framework
    ┌───────────────┼────────────────┬────────────────────┐
    ▼               ▼                ▼                    ▼
  Appium         Flasher/Serial    Robot/Camera        Cloud/API
(Android/iOS)    Device Control     Audio/Sensor        Validation
    │               │                │                    │
    └───────────────┴────────────────┴────────────────────┘
                    │
                    ▼
         Artifact / Evidence Lake
              │
    ┌─────────┴────────┐
    ▼                  ▼
TestLink Update    Graph Feedback
```

---

## 七、風險表

| 風險 | 出現位置 | 建議解法 |
|------|---------|---------|
| TestLink 與 Robot case 漂移 | 管理面與執行面不一致 | 強制 `testlink_case_id` 作為 Robot metadata |
| Graph 過度推論 | 舊 spec / Redmine 造成錯關聯 | 所有邊加 `confirmed/inferred/stale/conflicted` |
| 沒有 sandbox backend | E2E 測試容易污染真實環境 | cloud/API case 分成 readonly / write-safe / destructive |
| 多裝置時序難對齊 | app / device / log / camera / audio 不同步 | 統一 `trace_id` + `station clock` |
| RF library 過度耦合 | 換設備就全壞 | 每種設備獨立 custom library / adapter |
| 實體手機 flaky | Appium + 真機不穩 | 分 smoke / nightly / release-gate 三層執行 |

---

## 八、如何在新 Session 繼續討論

### 方法 A：使用 session_search（本機）
```
session_search(query="Pablo QA orchestrator HIL TestLink Robot Framework")
```

### 方法 B：直接讀取 owen-study 文件
```
~/source/github.com/owen-study/pablo-qa-orchestrator-status.md  ← 本文件
~/source/github.com/owen-study/hermes-qa-architecture-report.md
~/source/github.com/owen-study/web-testing-automation-report.md
~/source/github.com/owen-study/hermes-graphify-suitability-report.md
~/source/github.com/owen-study/gemini-cli-chrome-mcp-web-automation.md
```

### 方法 C：Ping Pablo 直接互動
在蚵阿麵線神教頻道 `<@&1478013466886279211>` ping Pablo。

---

## 九、下一步行動清單

- [ ] **Pablo SOUL.md 客製化**：加入 QA orchestrator 人格定義
- [ ] **Explorer 子代理 prompt**：針對 HIL 裝置探索任務優化
- [ ] **TestLink × Graph × Robot Framework 的 schema 對照表** — 決定資料怎麼串
- [ ] **TestLink 同步模式定案**：單向/雙向，testcase ID 主鍵來源
- [ ] **Graph store 選型**：Neo4j / SQLite / 其他
- [ ] **Artifact store 選型**：存證據的地點與格式
- [ ] **證據收集 pipeline**：Observer 子代理的截圖/log 收集機制
- [ ] **Cloud/API 驗證隔離策略**：因無 sandbox 需特別設計

---

## 十、關鍵原則

1. **Pablo 是 Orchestrator，不是 Runner** — 子代理做事，Pablo 做決策
2. **TestLink 是管理面、Robot Framework 是執行面、Graph 是關聯面、Artifact Lake 是真相面** — 四者分工清楚才可維護
3. **圖譜是導覽，不是真相本體** — 最後仍要回到原始事實來源驗證
4. **證據 > 口頭報告** — 每次測試都要附截圖/log/波形

---

*本文件同步至 `codeofthrone-agent/owen-study`，方便跨 session 繼續討論。*
