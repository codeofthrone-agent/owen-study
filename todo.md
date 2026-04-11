# todo.md

> Unified TODO list aggregated from docs and tooling reports in this repository.

- Total items: 23

## P0

- [ ] 將 issue 執行結果回填時強制帶入 `trace_id` + `artifact_uri[]`
  - source: `pablo-qa-orchestrator-status.md:317` (next-step)
## P1

- [ ] **TestLink × Graph × Robot Framework 的 schema 對照表** — 決定資料怎麼串
  - source: `pablo-qa-orchestrator-status.md:221` (checkbox)
- [ ] 以 `step-mapping-split-prefill-v2.csv` 為基礎，人工 review 前 300 筆 `manual_only`（先把信心提升到 `high/medium`）。
  - source: `testcase-step-keyword-alignment-catalog.md:204` (next-step)
- [ ] 針對剩餘 `unmapped=902`，先處理 `step-mapping-unmapped-top200.csv` 的模板並補 alias 規則（v3）。
  - source: `testcase-step-keyword-alignment-catalog.md:205` (next-step)
## P2

- [ ] Graphify build + query + update 腳本
  - source: `hermes-graphify-integration-plan.md:194` (checkbox)
- [ ] Hermes tool wrapper（graphify_query / graphify_update）
  - source: `hermes-graphify-integration-plan.md:195` (checkbox)
- [ ] PR merge hook（GitHub Actions / CI）
  - source: `hermes-graphify-integration-plan.md:196` (checkbox)
- [ ] 整合 demo （一個 repo）
  - source: `hermes-graphify-integration-plan.md:197` (checkbox)
- [ ] **Pablo SOUL.md 客製化**：加入 QA orchestrator 人格定義
  - source: `pablo-qa-orchestrator-status.md:219` (checkbox)
- [ ] **Explorer 子代理 prompt**：針對 HIL 裝置探索任務優化
  - source: `pablo-qa-orchestrator-status.md:220` (checkbox)
- [ ] **TestLink 同步模式定案**：單向/雙向，testcase ID 主鍵來源
  - source: `pablo-qa-orchestrator-status.md:222` (checkbox)
- [ ] **Graph store 選型**：Neo4j / SQLite / 其他
  - source: `pablo-qa-orchestrator-status.md:223` (checkbox)
- [ ] **Artifact store 選型**：存證據的地點與格式
  - source: `pablo-qa-orchestrator-status.md:224` (checkbox)
- [ ] **證據收集 pipeline**：Observer 子代理的截圖/log 收集機制
  - source: `pablo-qa-orchestrator-status.md:225` (checkbox)
- [ ] **Cloud/API 驗證隔離策略**：因無 sandbox 需特別設計
  - source: `pablo-qa-orchestrator-status.md:226` (checkbox)
- [ ] 對最新 issues 做 **issue→testcase 對映盤點**（有對應 / 缺 testcase / testcase 過期）
  - source: `pablo-qa-orchestrator-status.md:314` (next-step)
- [ ] 建立 `redmine_issue_id` 欄位規範（TestLink custom field + RF tag）
  - source: `pablo-qa-orchestrator-status.md:315` (next-step)
- [ ] 為高風險 issue（New/In Progress）補齊 `testlink_case_id` 與 `execution_tier`
  - source: `pablo-qa-orchestrator-status.md:316` (next-step)
- [ ] mobile（`resources/mobile_keywords.robot` + `libraries/mobile_testing/*`）
  - source: `testcase-step-keyword-alignment-catalog.md:107` (next-step)
- [ ] device/common（`device_control_keywords.robot` / `common_keywords.robot`）
  - source: `testcase-step-keyword-alignment-catalog.md:108` (next-step)
- [ ] api/web/robot_arm/switchbot/ipcam
  - source: `testcase-step-keyword-alignment-catalog.md:109` (next-step)
- [ ] 產出第三版覆蓋率：`mapped / manual_only / unmapped`（以 sub-step 為單位）。
  - source: `testcase-step-keyword-alignment-catalog.md:206` (next-step)
- [ ] 將高頻 `manual_only` 轉為「正式 canonical keyword 候選」，形成新增/重構 backlog。
  - source: `testcase-step-keyword-alignment-catalog.md:207` (next-step)
