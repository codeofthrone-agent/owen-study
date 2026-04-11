# TestCase Step × Keyword 對齊目錄（Catalog v1）

> 建立日期：2026-04-11  
> 來源：`pablo-qa-orchestrator-status.md` 既有盤點結果 + repo/TestLink read-only 實測

---

## 0) 範圍與限制

- 範圍：`GEN2.5 / Release` 的所有 TestLink testcase steps，對齊 robot repo 現有全部 keywords。
- 系統限制：**Redmine / TestLink 僅 read-only**（不可 create/update/delete）。

---

## 1) 現有內容（已同步填入）

### 1.1 全量盤點結果（實際數據）

| 項目 | 數量 | 備註 |
|---|---:|---|
| Robot keyword 定義總數 | 395 | 全部 `.robot` |
| Python `@keyword` 定義總數 | 115 | 全部 library `.py` |
| 全部 keyword（去重後） | 453 | 395+115 去重 |
| TestLink 專案/計畫 | GEN2.5 / Release | XML-RPC 讀取 |
| Test cases（計畫內） | 1681 | `getTestCasesForTestPlan` |
| testcase steps（去重後） | 1936 | `getTestCasesForTestSuite(details=full)` 聚合 |
| step.actions 命中任一現有 keyword | 2 | 0.1% |
| step.expected_results 命中任一現有 keyword | 0 | 0.0% |
| 未命中 steps | 1934 | 近乎全部自然語句 |

### 1.2 現況判讀

| 差異面向 | TestLink step 現況 | Keyword 現況 | 結果 |
|---|---|---|---|
| 表達型態 | 自然語句（點擊/查看/輸入） | 指令型可執行 keyword | 幾乎無法直接對映 |
| 粒度 | 1 step 常有多動作 | keyword 多為單動作 | 需要拆分/映射層 |
| 結構品質 | 有編號、中英混雜、code-like 字串 | keyword 命名相對規範 | 自動比對命中率極低 |
| 關聯鍵 | step 無 keyword id | keyword 無 step id | 無穩定主鍵可追 |

---

## 2) 兩邊要補齊什麼（對齊補完表）

| 方向 | 需補齊項目 | MVP 規格 | 預期產出 |
|---|---|---|---|
| TestLink 端 | step 可機讀欄位 | `automation_keyword`（必要） | 每一步可映射 canonical keyword |
| TestLink 端 | step 拆分規範 | 1 step = 1 action；expected 單獨欄位 | 降低歧義 |
| TestLink 端 | case metadata | `testlink_case_id`, `execution_tier` | 管理面可追蹤 |
| Robot 端 | alias 映射層 | 自然語句模板 → canonical keyword | 舊 case 可逐步對齊 |
| Robot 端 | assert 類 keyword | Then 類可執行斷言（存在、狀態、回填驗證） | 測試可驗證閉環 |
| Robot 端 | keyword catalog | name/args/layer/status/domain | 提供 TestLink 反查字典 |
| 流程層 | 對齊 Gate | 未填 `automation_keyword` = `manual_only` | 防止假自動化覆蓋 |

---

## 3) 對齊資料契約（Catalog Schema）

> 這張表是後續自動比對與統計的權威欄位。

| 欄位 | 類型 | 必填 | 說明 |
|---|---|---|---|
| keyword_id | string | ✅ | 穩定 ID（建議 `KW-xxxx`） |
| canonical_keyword | string | ✅ | Robot 可執行關鍵字名稱 |
| layer | enum | ✅ | `robot_resource` / `python_library` / `alias` |
| domain | enum | ✅ | `testlink/mobile/device/api/web/robot_arm/...` |
| args_signature | string | ❌ | 參數簽章（例如 `${test_case_id} ${status}`） |
| execution_status | enum | ✅ | `implemented` / `stub` / `partial` / `deprecated` |
| mapped_api_method | string | ❌ | 如 `reportTCResult`, `getLastExecutionResult` |
| alias_patterns | string[] | ❌ | 自然語句模板（regex or phrase） |
| owner | string | ❌ | 維護責任人 |
| notes | string | ❌ | 補充說明 |

---

## 4) Catalog Seed（已先填入現有內容）

### 4.1 TestLink 子集（已填）

| keyword_id | canonical_keyword | layer | domain | args_signature | execution_status | mapped_api_method | notes |
|---|---|---|---|---|---|---|---|
| KW-TL-001 | 連接到 TestLink | python_library | testlink | `project_name? test_plan_name? build_name?` | implemented | `about/getProjects/getProjectTestPlans/getBuilds` | 可用 |
| KW-TL-002 | 檢查 TestLink 連接狀態 | python_library | testlink | `-` | implemented | `ping` | 可用 |
| KW-TL-003 | 回報測試結果到 TestLink | python_library | testlink | `test_case_external_id status notes? duration?` | implemented* | `getTestCase + reportTCResult` | *本階段只讀，不執行寫入 |
| KW-TL-004 | 批次回報測試結果到 TestLink | python_library | testlink | `test_results[]` | implemented* | `reportTCResult (multiple)` | 同上 |
| KW-TL-005 | 取得測試案例資訊 | python_library | testlink | `test_case_external_id` | implemented | `getTestCase` | 可用 |
| KW-TL-006 | 取得最後執行結果 | python_library | testlink | `test_plan_id + testcaseid/externalid` | implemented | `getLastExecutionResult` | `id=-1` 代表 not-run |
| KW-TL-007 | 取得當前專案資訊 | python_library | testlink | `-` | implemented | `context read` | 可用 |
| KW-TL-101 | Given TestLink 服務已連接 | robot_resource | testlink | `-` | stub | (planned→KW-TL-001) | wrapper 尚未接通 |
| KW-TL-102 | Given TestLink 服務已連接到專案 | robot_resource | testlink | `${project_name}` | stub | (planned→KW-TL-001) | wrapper 尚未接通 |
| KW-TL-103 | Given TestLink 連接狀態為正常 | robot_resource | testlink | `-` | stub | (planned→KW-TL-002) | wrapper 尚未接通 |
| KW-TL-104 | When 回報測試案例...結果為... | robot_resource | testlink | `${test_case_id} ${status}` | stub | (planned→KW-TL-003) | wrapper 尚未接通 |
| KW-TL-105 | When 回報測試案例...並附註... | robot_resource | testlink | `${test_case_id} ${status} ${notes}` | stub | (planned→KW-TL-003) | wrapper 尚未接通 |
| KW-TL-106 | When 批次回報多個測試結果到 TestLink | robot_resource | testlink | `${test_results}` | stub | (planned→KW-TL-004) | wrapper 尚未接通 |
| KW-TL-107 | When 查詢測試案例...資訊 | robot_resource | testlink | `${test_case_id}` | stub | (planned→KW-TL-005) | wrapper 尚未接通 |
| KW-TL-108 | Then 測試案例...最後執行狀態應為... | robot_resource | testlink | `${test_case_id} ${expected_status}` | stub | (planned→KW-TL-006 + assert) | 缺 assert 邏輯 |
| KW-TL-109 | Then 測試案例...應該存在於 TestLink | robot_resource | testlink | `${test_case_id}` | stub | (planned→KW-TL-005 + assert) | 缺 assert 邏輯 |
| KW-TL-110 | Then 批次回報應該全部成功 | robot_resource | testlink | `${stats}` | stub | (planned assert) | 缺 assert keyword |
| KW-TL-111 | 建立測試結果列表 | robot_resource | testlink | `-` | implemented | N/A | helper |
| KW-TL-112 | 添加測試結果 | robot_resource | testlink | `${results} ${test_case_id} ${status} ...` | implemented | N/A | helper |

### 4.2 全域 keyword inventory（待補）

> 現況已確認存在 453 個 unique keywords。  
> 下一步請用同 schema 將非 TestLink domain 分批補齊（mobile/device/api/web/robot_arm...）。

建議分批：
1. mobile（`resources/mobile_keywords.robot` + `libraries/mobile_testing/*`）  
2. device/common（`device_control_keywords.robot` / `common_keywords.robot`）  
3. api/web/robot_arm/switchbot/ipcam

---

## 5) Step Mapping Schema（給 testcase step 對齊用）

| 欄位 | 必填 | 說明 |
|---|---|---|
| step_uid | ✅ | `case_external_id + step_number` |
| case_external_id | ✅ | 如 `CCU-115` |
| step_number | ✅ | TestLink step number |
| step_action_raw | ✅ | 原始 action |
| step_expected_raw | ❌ | 原始 expected |
| mapped_keyword_id | ❌ | 對應 `KW-xxxx` |
| mapping_confidence | ❌ | `high/medium/low/manual` |
| mapping_notes | ❌ | 為何這樣映射 |
| mapping_status | ✅ | `mapped/unmapped/manual_only` |

---

## 6) Step 1 解析拆分（已完成）

> 針對你提出的「一個 step 可能有多個動作」先做拆分解析，供後續補正。

### 6.1 產出檔案

- `step-mapping-draft.csv`（原始 step 對齊草稿）
- `step-mapping-split-draft.csv`（拆分後子步驟）
- `step-mapping-split-report.md`（拆分統計與樣本）
- `step-mapping-split-prefill-v1.csv`（高頻動作 alias 預填版）
- `step-mapping-split-prefill-report.md`（v1 預填統計）
- `step-mapping-unmapped-top200.csv`（未映射高頻模板 Top 200）
- `step-mapping-split-prefill-v2.csv`（擴充規則後預填版）
- `step-mapping-split-prefill-v2-report.md`（v2 預填統計）

### 6.2 拆分統計

| 指標 | 數量 |
|---|---:|
| 原始 steps | 1941 |
| 單一步驟 | 1245 |
| 多步驟（需拆分） | 696 |
| 其中 action 多段 | 506 |
| 其中 expected 多段 | 243 |
| 拆分後 sub-steps | 3159 |

### 6.3 拆分規則（v1）

- 依序號切分：`1.`、`(1)`、`第X步`
- 依語句連接詞/標點切分：`；`、`。`、`然後`、`並且`、`and` 等
- expected 對齊策略：
  - 長度相等：index 對齊
  - expected 只有 1 段：掛在第一個 sub-step
  - expected 缺失：留空

### 6.4 Alias 預填（v1，已完成）

| 指標 | 數量 |
|---|---:|
| 拆分後 sub-steps | 3159 |
| 預填成功（`manual_only`） | 1315 |
| 仍未映射（`unmapped`） | 1844 |
| 預填率 | 41.63% |

高頻 alias 類別：
- `KW-ALIAS-CLICK`（點擊/按下/長按）
- `KW-ALIAS-CHECK`（查看/觀察/檢查）
- `KW-ALIAS-INPUT`（輸入/填寫）
- `KW-ALIAS-SET`（設定/選擇）
- `KW-ALIAS-OPEN` / `KW-ALIAS-CLOSE`
- `KW-ALIAS-VOICE` / `KW-ALIAS-WAIT`

### 6.5 Alias 預填（v2，已完成）

> 先針對 v1 的 1844 筆 unmapped 做模板聚類，輸出 Top 200（`step-mapping-unmapped-top200.csv`），
> 再加入擴充規則（wiring/navigation/login/bluetooth/wifi/ota/device_state/code-like）。

| 指標 | v1 | v2 |
|---|---:|---:|
| `manual_only` | 1315 | 2257 |
| `unmapped` | 1844 | 902 |
| 覆蓋率 | 41.63% | 71.45% |

v2 新增 alias 類別：
- `KW-ALIAS-DEVICE-WIRING`
- `KW-ALIAS-NAVIGATION`
- `KW-ALIAS-LOGIN-FLOW`
- `KW-ALIAS-BLUETOOTH`
- `KW-ALIAS-WIFI`
- `KW-ALIAS-OTA`
- `KW-ALIAS-DEVICE-STATE`
- `KW-ALIAS-CODE-LIKE-STEP`

## 7) 立刻可執行的下一步（read-only）

1. 以 `step-mapping-split-prefill-v2.csv` 為基礎，人工 review 前 300 筆 `manual_only`（先把信心提升到 `high/medium`）。
2. 針對剩餘 `unmapped=902`，先處理 `step-mapping-unmapped-top200.csv` 的模板並補 alias 規則（v3）。
3. 產出第三版覆蓋率：`mapped / manual_only / unmapped`（以 sub-step 為單位）。
4. 將高頻 `manual_only` 轉為「正式 canonical keyword 候選」，形成新增/重構 backlog。

---

*本文件為對齊工作底稿（Catalog v1）。*