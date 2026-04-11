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

## 十、需要補齊：TestLink × Robot Framework 對齊矩陣（v1）

> 說明：不是比對自然語言 keyword 字面，而是比對「管理面能力」與「執行面能力」是否對齊。

| 能力面向 | TestLink 需要 | Robot Framework 現況 | 對齊狀態 | 需要補齊 |
|---|---|---|---|---|
| 測試案例識別 | 唯一 testcase external id | 可傳入 `test_case_id` | ⚠️ 部分對齊 | 強制每個 RF test case 綁定 `testlink_case_id`（metadata/tag） |
| Test Plan / Build 綁定 | execution 必須屬於 plan + build | connector 支援初始化 project/plan/build | ⚠️ 部分對齊 | 在 Runner 啟動時固定 plan/build，避免同 run 漂移 |
| 單筆結果回報 | status + notes + duration | 已有回報能力 | ✅ 基本對齊 | notes 結構化（actual/error_code/trace_id） |
| 批次結果回報 | 多案例批次上報 | 已有 batch 回報能力 | ✅ 基本對齊 | 增加批次失敗重試與補償策略 |
| 最後執行狀態查詢 | case last execution 可查 | 已有查詢能力 | ✅ 對齊 | 回報後立即抽查驗證（post-write verify） |
| Requirement trace | testcase 對應需求/缺陷 | 缺少標準欄位規範 | ❌ 缺口 | 導入 `redmine_issue_id` 與 `testlink_case_id` 強制關聯 |
| 證據管理 | execution 可追溯 evidence | 有概念，缺統一 schema | ❌ 缺口 | 統一 evidence schema 與 artifact URI 命名規範 |
| 執行分層 | smoke / nightly / release-gate | 架構已提但未制度化 | ⚠️ 部分對齊 | TestLink 增 `execution_tier`；RF tag 同步 |
| 真實後端風險控管 | readonly/write-safe/destructive | 有風險意識，缺流程 gate | ❌ 缺口 | Orchestrator 依 mode 強制前置檢查與保護策略 |

---

## 十一、需要補齊：欄位與資料契約（v1）

| 類別 | 欄位 | 建議落點 | 用途 |
|---|---|---|---|
| 主鍵 | `testlink_case_id` | RF metadata/tag + Graph node | 管理面與執行面唯一對齊鍵 |
| 需求追蹤 | `redmine_issue_id` | TestLink custom field + RF tag | 串接需求/缺陷與測試案例 |
| 追蹤鏈 | `trace_id` | 每次 run 產生；寫入 notes + artifact | 串接 log/screenshot/video/waveform |
| 執行分類 | `execution_tier` | TestLink case field | 控制 smoke/nightly/release-gate |
| 風險模式 | `backend_mode` | run-time 參數（plan/run metadata） | 區分 readonly/write-safe/destructive |
| 證據索引 | `artifact_uri[]` | TestLink execution notes/附件索引 | 支援快速回查證據 |
| 自動化成熟度 | `automation_status` | TestLink case field | manual / automated / stub 管理 |
| 版本關聯 | `firmware/app/backend_version` | run metadata | 失敗追溯與回歸分析 |

---

## 十二、需要補齊：Redmine → TestLink → Robot Framework 流程（v1）

### 為何需要

目前若只看 TestLink 或只看 Robot，容易缺少需求脈絡。建議把 Redmine issue 變成前置索引，才能看到全貌（需求/缺陷 → 測試案例 → 執行證據）。

### 建議標準流程

1. **讀取 Redmine issue**：抽取需求目標、風險、驗收條件
2. **映射 TestLink testcase**：存在則關聯，不存在則建立候選 case
3. **綁定 Robot Framework 測試**：每個測試帶 `testlink_case_id`（必要）與 `redmine_issue_id`（建議）
4. **執行與回填**：回填 status + notes + `trace_id` + `artifact_uri[]`
5. **圖譜更新**：建立 `Issue -> TestCase -> RF Test -> Artifact` 關聯邊

### 最低可行驗證（MVP Gate）

- Gate-1：若缺 `testlink_case_id`，不可進入自動執行
- Gate-2：若 `backend_mode=destructive` 且未授權，禁止執行
- Gate-3：若無 `trace_id` 或無 evidence，該次結果不得標記為 release-gate 通過

---

## 十三、關鍵原則

1. **Pablo 是 Orchestrator，不是 Runner** — 子代理做事，Pablo 做決策
2. **TestLink 是管理面、Robot Framework 是執行面、Graph 是關聯面、Artifact Lake 是真相面** — 四者分工清楚才可維護
3. **圖譜是導覽，不是真相本體** — 最後仍要回到原始事實來源驗證
4. **證據 > 口頭報告** — 每次測試都要附截圖/log/波形
5. **對齊優先於自動化速度** — 先確保 `issue ↔ testcase ↔ execution ↔ evidence` 可追溯，再擴大覆蓋率

---

## 附錄 A：Redmine 初始盤點（2026-04-11）

- Redmine URL：`https://redmine.thortron.dev`
- Project：`gen-2-5`（GEN 2.5_WF-3511/WF-3611）
- API 讀取確認：✅ 可透過 API 取得 project 與 issues
- 目前 issues 規模：`total_count=739`（本次先抓最新 20 筆）

### 最新 issues 快照（節錄）

| Issue ID | Tracker | Status | Subject |
|---|---|---|---|
| 1926 | Feature | New | [CI][Power Pro] Investigate and Fix Release Pipeline Failure |
| 1840 | Bug | Resolved | APP WiFi 設定密碼輸入錯誤顯示訊息異常 |
| 1826 | Bug | Resolved | 關掉 MIC LED 第一次喚醒仍亮起 |
| 1919 | Feature | In Progress | OTA: Version Restriction Based on User Role |
| 1915 | Bug | In Progress | APP 滑動登入頁至底部會看不見所有欄位 |

### 下一步（與 TestLink/Robot 對齊）

1. 對最新 issues 做 **issue→testcase 對映盤點**（有對應 / 缺 testcase / testcase 過期）
2. 建立 `redmine_issue_id` 欄位規範（TestLink custom field + RF tag）
3. 為高風險 issue（New/In Progress）補齊 `testlink_case_id` 與 `execution_tier`
4. 將 issue 執行結果回填時強制帶入 `trace_id` + `artifact_uri[]`

---

## 附錄 B：TestLink XML-RPC 在 robot repo 的位置（read-only 盤點）

### 主要程式碼與文件位置

- API client（核心）  
  `libraries/testlink_integration/api_client/testlink_api.py`
- Robot 高階連接器  
  `libraries/testlink_integration/TestLinkConnector.py`
- Gherkin 資源關鍵字  
  `resources/testlink_keywords.robot`
- 安裝與設定指南  
  `docs/testlink_integration_setup_guide.md`
- 驗證與除錯腳本  
  `scripts/verify_testlink_integration.py`、`scripts/debug_testlink_api.py`

### 已確認的 API 端點

- UI：`https://testlink.thortron.dev/testlink/`
- XML-RPC：`https://testlink.thortron.dev/testlink/lib/api/xmlrpc/v1/xmlrpc.php`

### 目前觀察（僅讀取，不變更）

- TestLink API 可連通（`tl.about` 回應正常）
- TestLink 專案存在：`GEN2.5`；Test Plan：`Release`
- `GEN2.5/Release` 下約有 `1681` 個 test cases（API 讀取結果）
- Redmine `gen-2-5` 最新 20 筆 issue 中，**尚未發現明確的 TestLink external id（如 `CCU-xxx`）字串**
  - 代表目前 issue → testcase 關聯多半未顯式標註，需補欄位/規範

### 階段限制（治理規則）

- 本階段 Redmine / TestLink 僅允許 **read-only** 操作
- 禁止 create / update / delete

---

## 附錄 C：是否先做「test case 內 keyword 對齊表」— 結論與初版

### 結論

**是，應該先做。**
在 issue ↔ testcase 對齊前，先確認 testcase 在執行面是否有可用 keyword，否則會出現「管理面有 case、執行面跑不起來」的假對齊。

### 初版盤點（目前 repo 現況）

> 更正：`testlink_keywords.robot` 只是**其中一份資源檔**，不是整個專案全部 keyword。

| 指標 | 數量 | 說明 |
|---|---:|---|
| 全 repo `.robot` 檔案數 | 49 | 其中多數含測試/資源 keyword |
| 含 `*** Keywords ***` 的 `.robot` 檔 | 39 | 分散於 resources 與 tests |
| 全 repo Robot keyword 定義總數 | 395 | 包含 domain keywords（mobile/device/api/web/robot arm 等） |
| Python `@keyword` 定義總數 | 115 | 分散於 9 個 library 檔案 |
| `resources/testlink_keywords.robot` 定義關鍵字 | 17 | 僅 TestLink wrapper + helper |
| 其中 stub（含「暫時無法使用」） | 15 | 多數僅 Log WARN，未實際執行 API |
| 其中可用 helper | 2 | `建立測試結果列表`、`添加測試結果` |
| `TestLinkConnector.py` 可執行 library keyword | 7 | 可呼叫 XML-RPC 的核心能力 |

### 對齊建議（先後順序）

1. **先做 Keyword 能力對齊表**（wrapper keyword → library keyword → 狀態）
2. 再做 **Issue ↔ TestCase 對齊**（只用已可執行能力作為 coverage 判斷）
3. 最後做 **Evidence Gate**（trace_id / artifact_uri）

### v1 表格欄位建議

| 欄位 | 說明 |
|---|---|
| keyword_name | Robot/Gherkin keyword 名稱 |
| keyword_layer | `wrapper` / `library` |
| mapped_library_keyword | 對應的 connector keyword（若有） |
| execution_status | `implemented` / `stub` / `partial` |
| api_method | 對應 XML-RPC method（read-only 檢視） |
| related_testlink_case_ids | 目前已引用的 case id（若可解析） |
| notes | 缺口與補強建議 |

---

## 附錄 D：TestLink 對齊子集 v1（keyword capability matrix, read-only）

> 範圍：只看會影響 TestLink testcase 對齊/回填的 keywords。  
> 目的：先判斷「可執行能力」再做 issue ↔ testcase coverage。

### D-1. Wrapper（`resources/testlink_keywords.robot`）對齊表

| keyword_name | mapped_library_keyword | execution_status | api_method（預期） | notes |
|---|---|---|---|---|
| Given TestLink 服務已連接 | 連接到 TestLink | stub | `tl.about` + project/plan/build 查詢 | 目前僅 Log WARN |
| Given TestLink 服務已連接到專案 "${project_name}" | 連接到 TestLink | stub | 同上 | 目前僅 Log WARN |
| Given TestLink 連接狀態為正常 | 檢查 TestLink 連接狀態 | stub | `tl.about` | 目前僅 Log WARN |
| When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}" | 回報測試結果到 TestLink | stub | `getTestCaseIDByName` + `reportTCResult` | 目前僅 Log WARN |
| When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}" 並附註 "${notes}" | 回報測試結果到 TestLink | stub | `getTestCaseIDByName` + `reportTCResult` | 目前僅 Log WARN |
| When 批次回報多個測試結果到 TestLink | 批次回報測試結果到 TestLink | stub | 多次 `reportTCResult` | 目前僅 Log WARN |
| When 查詢測試案例 "${test_case_id}" 的資訊 | 取得測試案例資訊 | stub | `getTestCaseIDByName` | 目前僅 Log WARN |
| Then TestLink 應該記錄測試結果 | （需斷言 keyword） | stub | 查 execution result | 缺可執行斷言 |
| Then 測試案例 "${test_case_id}" 的最後執行狀態應為 "${expected_status}" | 取得最後執行結果 | stub | `getLastExecutionResult` | 目前僅 Log WARN |
| And 測試案例 "${test_case_id}" 的最後執行狀態應為 "${expected_status}" | 取得最後執行結果 | stub | `getLastExecutionResult` | 同上 |
| Then 測試案例 "${test_case_id}" 應該存在於 TestLink | 取得測試案例資訊 | stub | `getTestCaseIDByName` | 目前僅 Log WARN |
| And 測試案例 "${test_case_id}" 應該存在於 TestLink | 取得測試案例資訊 | stub | `getTestCaseIDByName` | 同上 |
| Then 批次回報應該全部成功 | （需斷言 keyword） | stub | 本地統計 + 抽查 | 缺可執行斷言 |
| And 記錄當前 TestLink 專案資訊 | 取得當前專案資訊 | stub | 專案/計畫/build 讀取 | 目前僅 Log WARN |
| And 驗證 TestLink 連接正常 | 檢查 TestLink 連接狀態 | stub | `tl.about` | 目前僅 Log WARN |
| 建立測試結果列表 | （helper） | implemented | N/A | 本地資料結構 helper |
| 添加測試結果 | （helper） | implemented | N/A | 本地資料結構 helper |

### D-2. Library（`TestLinkConnector.py`）可執行能力表

| library keyword | execution_status | api_method（實際/封裝） | 用途 |
|---|---|---|---|
| 連接到 TestLink | implemented | `tl.about` + project/plan/build 讀取 | 建立連線與上下文 |
| 檢查 TestLink 連接狀態 | implemented | `tl.about` | 連線健康檢查 |
| 回報測試結果到 TestLink | implemented* | `getTestCaseIDByName` + `reportTCResult` | 單筆結果回填 |
| 批次回報測試結果到 TestLink | implemented* | 多次 `reportTCResult` | 批次結果回填 |
| 取得測試案例資訊 | implemented | `getTestCaseIDByName` | 讀 testcase 資訊 |
| 取得最後執行結果 | implemented | `getLastExecutionResult` | 讀最後執行狀態 |
| 取得當前專案資訊 | implemented | 連線上下文讀取 | 讀目前 project/plan/build |

\* 註：本文件階段規則為 read-only；此能力在本階段僅做靜態對齊盤點，不執行寫入。

### D-3. 立即可用的對齊判準（用於後續 issue ↔ testcase）

- `coverage=valid`：必須使用 `implemented` library keyword，且可追到 `testlink_case_id`
- `coverage=weak`：只使用 wrapper stub / 無可執行斷言
- `coverage=unknown`：無 TestLink 關鍵字關聯

---

## 附錄 E：Redmine 最新 20 筆 issue 的 coverage 分級（read-only）

> 分級規則沿用附錄 D：`valid / weak / unknown`。
> 本次結果：`valid=0, weak=0, unknown=20`。

| issue_id | tracker | status | testcase_id_in_issue | coverage | 缺口說明 |
|---:|---|---|---|---|---|
| 1926 | Feature | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1840 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1826 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1925 | Feature | Closed | - | unknown | 無 issue→testcase 顯式關聯 |
| 1917 | Feature | In Progress | - | unknown | 無 issue→testcase 顯式關聯 |
| 1884 | Feature | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1906 | Support | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1907 | Support | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1920 | Feature | In Progress | - | unknown | 無 issue→testcase 顯式關聯 |
| 1919 | Feature | In Progress | - | unknown | 無 issue→testcase 顯式關聯 |
| 1918 | Feature | In Progress | - | unknown | 無 issue→testcase 顯式關聯 |
| 1912 | Bug | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1915 | Bug | In Progress | - | unknown | 無 issue→testcase 顯式關聯 |
| 1830 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1913 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1894 | Bug | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1916 | Bug | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1914 | Bug | New | - | unknown | 無 issue→testcase 顯式關聯 |
| 1842 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |
| 1851 | Bug | Resolved | - | unknown | 無 issue→testcase 顯式關聯 |

### 立即建議（不違反 read-only 階段）

1. 先定義欄位契約（文件層）：`redmine_issue_id`、`testlink_case_id`、`trace_id`。
2. 在需求/缺陷模板中加入「對應 TestLink Case」欄位（先流程約束，不動資料）。
3. 先挑前 5 筆 New/In Progress issue 做人工 mapping 草稿（文件內，不寫回系統）。

---

## 附錄 F（修正版）：所有 testcase step × 所有 keyword 差異與補齊表（read-only）

> 你指定的範圍：**TestLink 全部 testcase steps** 對 **repo 內全部既有 keywords**。  
> 比對基準：字串正規化後的 direct/substring match（保守估計）。

### F-1. 全量盤點結果（實際數據）

| 項目 | 數量 | 備註 |
|---|---:|---|
| Robot keyword 定義總數 | 395 | 來源：全部 `.robot` 檔 |
| Python `@keyword` 定義總數 | 115 | 來源：全部 library `.py` |
| 全部 keyword（去重後） | 453 | `395+115` 去重 |
| TestLink 專案/計畫 | GEN2.5 / Release | XML-RPC 讀取 |
| Test cases（計畫內） | 1681 | `getTestCasesForTestPlan` |
| testcase steps（去重後） | 1936 | `getTestCasesForTestSuite(details=full)` 聚合 |
| step.actions 命中任一現有 keyword | 2 | 命中率 `0.1%` |
| step.expected_results 命中任一現有 keyword | 0 | 命中率 `0.0%` |
| 未命中 steps | 1934 | 絕大多數為自然語句 |

### F-2. 實際差異（為何幾乎對不起來）

| 差異面向 | TestLink step 現況 | Keyword 現況 | 造成結果 |
|---|---|---|---|
| 表達型態 | 自然語句/敘述句（如「點擊…」「查看…」） | 指令型 keyword（可執行） | 文字幾乎無法直接對映 |
| 粒度 | step 常混合多個動作與預期 | keyword 通常單一動作 | 一對多/多對一難對齊 |
| 結構品質 | steps 含編號、中英混雜、少量 code-like 內容 | keyword 命名相對規範 | 自動比對命中率極低 |
| 主鍵 | step 內容未帶 keyword id | keyword 無對應 testcase_step_id | 無法建立穩定關聯鍵 |

### F-3. 兩邊要補齊什麼（重點表）

| 方向 | 需補齊項目 | 最小可行規格（MVP） | 產出 |
|---|---|---|---|
| TestLink 端 | step 加入可機讀欄位 | 每個 step 增 `automation_keyword`（或 `keyword_id`） | step 能直接映射到可執行 keyword |
| TestLink 端 | step 拆分規範 | 1 step = 1 action；expected 獨立 | 降低多動作歧義 |
| TestLink 端 | testcase metadata | case 層補 `testlink_case_id`、`execution_tier` | 管理面可追蹤 |
| Robot 端 | 建立 alias 層 | 自然語句模板 → canonical keyword 映射表 | 舊 step 不改也可先對齊 |
| Robot 端 | 補 assert keywords | `驗證最後狀態`、`驗證案例存在` 等可執行斷言 | Then 類步驟可落地 |
| Robot 端 | keyword catalog | 輸出單一清單：name / args / layer / status | 可被 TestLink 反查 |
| 流程層 | 對齊 Gate | 未填 `automation_keyword` 的 step 標記 `manual_only` | 防止假自動化覆蓋 |

### F-4. 建議修正順序（先對齊再擴充）

1. **先定義 keyword catalog（權威清單）**：453 個 keyword 分 `canonical / alias / deprecated`。  
2. **再定義 step 映射欄位**：`automation_keyword`（必要）+ `automation_args`（選填）。  
3. **先處理高頻動作模板**：`點擊/查看/輸入/設定/檢查` 五類。  
4. **最後才做全面 coverage 統計**：以「有映射鍵」而非自然語句比對判定覆蓋率。

---

*本文件同步至 `codeofthrone-agent/owen-study`，方便跨 session 繼續討論。*
