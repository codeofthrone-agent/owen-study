---
title: "Hermes Agent 主導測試 — 架構需求分析報告"
author: "Hermes Agent (zero research)"
date: "2026-04-07"
version: "1.0"
tags: [testing, qa, agent-architecture, test-automation, hermes-agent]
---

# Hermes Agent 主導測試 — 架構需求分析報告

> 📅 更新日期：2026-04-07
> 🔍 調查目標：用 Hermes Agent 主導「網頁測試自動化」與「測試案例開發」，還需要哪些開發？是否需要專門 Agent？

---

## 📑 目錄

1. [現有能力盤點](#1-現有能力盤點)
2. [Gap Analysis — 我們缺什麼？](#2-gap-analysis--我們缺什麼)
3. [是否需要專門 Agent？](#3-是否需要專門-agent)
4. [推薦架構 — 三層 Agent 測試體系](#4-推薦架構--三層-agent-測試體系)
5. [開發路線圖](#5-開發路線圖)
6. [ROI 評估](#6-roi-評估)
7. [附錄：現有 Skill 可複用清單](#7-附錄現有-skill-可複用清單)

---

## 1. 現有能力盤點

我們已有的基礎設施：

| 能力 | 狀態 | 說明 |
|------|------|------|
| `agent-browser` CLI | ✅ 已安裝 | Rust 瀏覽器自動化，snapshot/click/fill/screenshot |
| `delegate_task` | ✅ 內建 | 平行委派 subagent，獨立 context |
| `execute_code` | ✅ 內建 | Python 腳本執行，可跑 pytest |
| `terminal` / `file` tools | ✅ 內建 | 指令執行、檔案讀寫、搜尋 |
| TDD skill | ✅ 已安裝 | RED-GREEN-REFACTOR 完整流程 |
| Subagent-Driven Dev skill | ✅ 已安裝 | Implementer + Spec Reviewer + Quality Reviewer |
| Code Review skill | ✅ 已安裝 | 安全/品質審查 checklist |
| Opik Tracer | ✅ 已安裝 | LLM call 追蹤與可觀測性 |
| Cron 排程 (cronman) | ✅ 可用 | 自動定時觸發任務 |
| Profile 機制 | ✅ 可用 | 獨立 config / env / system prompt |

**結論：** 底層工具齊全，但缺少「串接層」—— 將探索、生成、執行、報告串起來的流程。

---

## 2. Gap Analysis — 我們缺什麼？

### Gap 1：測試案例自動生成 (Test Case Generation)

**現狀：** `agent-browser` 只能手動操作流程，不會自動生成可迴歸的測試腳本。

**需要做：**
1. **Recorder 模組**：從 `agent-browser` 操作序列自動轉譯為 pytest + agent-browser CLI 腳本
2. **Assertion 推斷引擎**：分析頁面狀態變化（URL 變化、元素出現/消失）自動生成 `expect()` 判斷式
3. **Test Template**：統一的測試架構（fixture、setup/teardown、reporting）

### Gap 2：測試報告與可視化 (Test Reporting)

**現狀：** `pytest` 輸出文字結果，沒有結構化報告、趨勢追蹤。

**需要做：**
1. **Test Result Parser**：解析 pytest JSON output → 結構化 Markdown/HTML 報告
2. **Trend Tracker**：歷史測試通過率趨勢（存現有 SQLite session DB）
3. **Screenshot Diff**：比對 regression screenshot 與 baseline

### Gap 3：Test Suite 管理 (Test Suite Orchestration)

**現狀：** 沒有 Test Suite 的 CRUD 管理機制。

**需要做：**
1. **Test Catalog (YAML/JSON)**：測試案例清單 + metadata
2. **Tagging 系統**：smoke / regression / e2e / priority 標籤
3. **Smart Selection**：根據程式碼變更或功能模組自動選擇要跑的測試子集

---

## 3. 是否需要專門 Agent？

### 答案：需要，但不是「從零建立」，而是用 **Profile 特化**

不需要重新寫一個全新的 Agent。Hermes 的 profile 機制完全足夠：

```
HERMES_HOME 未設定 → agent:default  (通用助手)
HERMES_HOME=~/.hermes/profiles/qa → agent:qa  (QA 工程師)
```

### 推薦設計：`agent:qa` Profile

```
~/.hermes/profiles/qa/
├── config.yaml          # QA 專用配置（toolset 偏好等）
├── .env                # QA 相關 API keys
├── MEMORY.md           # QA 專用的長期記憶
└── skills_extra/       # QA 專用 skills（未來擴充）
```

### 為什麼要分開？

| 因素 | 通用 Agent (default) | QA Agent (qa) |
|------|------------------------|----------------|
| 主要任務 | "幫我寫功能" | "幫我找 bug、寫測試" |
| Toolset 偏好 | code_execution, delegate_task | agent-browser, terminal, file |
| 輸出格式 | 程式碼 + 說明 | 測試結果 + 報告 + 截圖證據 |
| 迭代策略 | 實作 → 驗證 | 探索 → 記錄 → 自動化 → 迴歸 |
| 錯誤容忍度 | 較高（可以修） | **零容忍**（bug 就是 bug） |
| 記憶需求 | 長期專案上下文 | 測試基線 + historical results |

### QA Agent 的 System Prompt（建議）

```
You are a Senior QA Engineer. Your goals, in priority order:
1. DISCOVER — Explore the application systematically, find bugs
2. AUTOMATE — Convert manual findings into reproducible test scripts
3. VERIFY — Run tests, report results with evidence
4. REPORT — Structure findings with severity ranking and screenshots

PRINCIPLES:
- Always prefer evidence (screenshot, log, network call) over assertion
- A bug without reproduction steps is just an opinion
- Test cases should be readable by non-engineers
- Screenshot every failure, log every pass

TOOLS: Prefer agent-browser for UI interaction, curl for API checks,
       pytest for test execution, delegate_task for parallel test suites.
```

---

## 4. 推薦架構 — 三層 Agent 測試體系

```
┌──────────────────────────────────────────────────────────┐
│                  LAYER 1: QA Orchestrator                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  agent:qa (Hermes profile)                         │  │
│  │  • 接收指令: "測試 X 功能" / "跑 smoke test"       │  │
│  │  • 規劃測試策略 → 生成測試計劃                      │  │
│  │  • delegate_task 到 subagents                       │  │
│  │  • 彙整結果 → 生成報告 → 發送用戶                    │  │
│  └────────────────────────────────────────────────────┘  │
│                           │ delegate_task                 │
│            ┌──────────────┼──────────────┐                │
│            ▼              ▼              ▼                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │  Explorer     │ │  Automator   │ │  Runner      │     │
│  │  Subagent     │ │  Subagent    │ │  Subagent    │     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│  • agent-browser    • 生成 pytest     • 執行測試套件     │
│  • 探索頁面結構     • 生成 Test Case  • 解析結果         │
│  • 產生測試案例     • 寫入測試檔案    • 截圖 + baseline  │
│                           │              │                │
│                           ▼              ▼                │
│  ┌────────────────────────────────────────────────┐     │
│  │              LAYER 2: Artifacts                  │     │
│  │  tests/e2e/         ← pytest 測試程式           │     │
│  │  tests/reports/     ← JSON/HTML 報告            │     │
│  │  tests/baselines/   ← baseline screenshots      │     │
│  │  tests/catalog.yml  ← 測試案例清單 + metadata   │     │
│  └────────────────────────────────────────────────┘     │
│                           │                              │
│                           ▼                              │
│  ┌────────────────────────────────────────────────┐     │
│  │              LAYER 3: Automation                 │     │
│  │  cronman → 每日 smoke test                      │     │
│  │  webhook → PR/commit 觸發相關測試                │     │
│  │  gh issue → 自動提交 bug report                 │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### Subagent 職責詳解

| Subagent | 輸入 | 輸出 | 核心工具 |
|----------|------|------|----------|
| **Explorer** | URL + 測試目標 | 頁面快照 + 測試案例清單 + 截圖 | `agent-browser` |
| **Automator** | Explorer 輸出 | pytest 測試程式碼 + catalog.yml | `file`, `execute_code` |
| **Runner** | 測試程式碼 | 執行結果 + 失敗截圖 + 報告 | `terminal`, `file` |

---

## 5. 開發路線圖

### Phase 1：MVP（今天就能開始，0 額外開發）

**利用現有工具鏈直接運作，只需要建立 QA profile：**

```
User: "測試 https://example.com 的登入功能"
    ↓
Hermes Agent (任一 profile 即可，QA profile 更好)
    ↓  delegate_task
├─ Explorer Subagent
│    agent-browser 探索登入流程
│    截圖記錄每個步驟
│    產出測試案例描述
│
├─ Automator Subagent
│    根據 Explorer 的 snapshot
│    生成 pytest + agent-browser 腳本
│    寫入 tests/e2e/test_login.py
│
└─ Runner Subagent
     執行 pytest tests/e2e/test_login.py
     收集結果與失敗截圖
     ↓
Report → 回覆用戶：✅ 通過 / ❌ 發現 N 個問題
```

**需要的設定（30 分鐘以內）：**
1. 建立 `qa` profile (`hermes -p qa setup`)
2. 設定 QA 專用 `.env` 和 `config.yaml`

### Phase 2：結構化測試管理（1-2 天開發）

1. **建立 Test Generator Skill**
   - 輸入：URL + 測試目標描述
   - 輸出：pytest + agent-browser 測試程式碼
   - Skill 名：`test-case-generator`

2. **Test Catalog YAML 格式**
   ```yaml
   test_cases:
     - id: AUTH-001
       name: "正常登入流程"
       url: "https://example.com/login"
       type: e2e
       priority: P0
       tags: [smoke, auth]
       steps:
         - action: open
           url: "https://example.com/login"
         - action: snapshot
         - action: fill
           ref: "@e1"
           value: "user@example.com"
         - action: fill
           ref: "@e2"
           value: "SecurePass123!"
         - action: click
           ref: "@e3"
       expected:
         - url_contains: "/dashboard"
         - text_visible: "Welcome"
   ```

3. **批量測試執行腳本**
   ```bash
   # 跑指定 tag 的測試
   pytest tests/e2e/ -m "smoke" --tb=short --json-report
   ```

### Phase 3：自動化與 CI/CD 整合（3-5 天開發）

1. **Cron 定時測試** — `cronman` 每日 9:00 跑 smoke test
2. **Webhook 事件驅動** — Git push → 觸發相關測試
3. **Trend Tracking** — 測試通過率歷史趨勢（用現有 sessions DB）
4. **Screenshot Baseline Diff** — 視覺迴歸偵測
5. **Auto GH Issues** — 測試失敗自動開 GitHub Issue

---

## 6. ROI 評估

### 投入 vs 效益

| 階段 | 投入時間 | 立即效益 |
|------|----------|----------|
| **Phase 1 (MVP)** | 30 分鐘 | 即刻能跑手動引導的測試 |
| **Phase 2 (結構化)** | 1-2 天 | 可維護、可迴歸、可追蹤 |
| **Phase 3 (CI/CD)** | 3-5 天 | 全自動，零人工介入 |

### 方法比較

| 方式 | 建立成本 | 維護成本 | 覆蓋率 | 可重複性 |
|------|----------|----------|--------|----------|
| 手寫 Playwright | 高 (每條 1-2hr) | 高 (UI 變就掛) | 中 | ⭐⭐⭐⭐⭐ |
| 純 AI 探索（無腳本） | 低 | 高 (每次重探索) | 高 | ⭐⭐ |
| **AI 生成 + 腳本混合** | 中 (一次生成) | **低 (auto-update)** | **最高** | ⭐⭐⭐⭐⭐ |
| AI 探索 + 腳本執行** | **中** | **低** | **最高** | **⭐⭐⭐⭐⭐** |

---

## 7. 附錄：現有 Skill 可複用清單

| Skill | 用途 | 複用程度 | 調整 |
|-------|------|----------|------|
| `agent-browser` | 瀏覽器操作 | ⭐⭐⭐⭐⭐ | 直接使用 |
| `test-driven-development` | TDD 流程 | ⭐⭐⭐⭐ | 轉為 QA 語氣 |
| `subagent-driven-development` | 多任務委派 | ⭐⭐⭐⭐⭐ | 直接使用架構 |
| `code-review` | 程式碼審查 | ⭐⭐⭐ | 轉為測試審查 |
| `systematic-debugging` | Bug 追蹤 | ⭐⭐⭐⭐ | 直接使用 |
| `opik-tracing` | 可觀測性 | ⭐⭐⭐ | 紀錄測試執行情況 |
| `cronman` | 排程執行 | ⭐⭐⭐⭐ | 定時測試排程 |
| `github-issues` | Bug 回報 | ⭐⭐⭐⭐ | 自動開 issue |

---

## 總結與建議

### 回答核心問題

**Q: 還需要哪些開發？**
- Phase 1 **不需要額外開發**，建立 QA profile 和 system prompt 即可開始
- Phase 2 需要建立 `test-case-generator` skill + test catalog schema
- Phase 3 需要整合 cron + webhook + trend tracking

**Q: 是否需要專門的 Agent？**
- **是，但現有的 profile 機制就夠了**。不需要重新寫 Agent，只需要：
  1. 建立 `qa` profile
  2. 寫一個 QA 專用的 system prompt
  3. 預設啟用 `agent-browser`、`terminal`、`file`、`delegate_task` toolsets

### 推薦行動順序

```
今天 → 建立 agent:qa profile (30 分鐘)
         ↓
    立即用 delegate_task 跑 Explorer → Automator → Runner 流程
         ↓
本週   → 建立 test-case-generator skill
         ↓
    建立 Test Catalog YAML 模板
         ↓
下週   → cronman 定時 smoke test
         ↓
    整合 GitHub Issues 自動回報
```

## Key Principle

> **測試不是「最後一步驗證」，是「第一個使用者」。
>  用 Agent 跑測試 = 讓 Agent 當第一個使用者。
>  在用戶發現 bug 之前，你的 QA Agent 已經找到了。**
