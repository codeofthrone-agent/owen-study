# Claude Review 決議清單（可勾選）

> 來源：`claude-review-questions.md`（14 項疑問，3 項 blocker）
> 目的：把疑問轉成可決議、可追蹤的執行清單。

## 使用規則

- 狀態：`[ ]` 未開始 / `[~]` 進行中 / `[x]` 已決議
- 決議欄位需寫明：
  - **Decision**（最終口徑）
  - **Owner**（單一責任人）
  - **Deadline**（YYYY-MM-DD）
  - **Evidence**（連結到文件/commit/報表）

---

## A. Blocking Items（先處理）

| ID | 問題摘要 | 影響 | Decision | Owner | Deadline | Evidence | 狀態 |
|---|---|---|---|---|---|---|---|
| Q-001 | read-only 宣告與「回填/post-write verify」描述衝突 | 流程邊界不清，可能違反階段限制 |  |  |  |  | [ ] |
| Q-002 | `mapped_rate_after_v2` 與實際 `mapping_status` 口徑不一致 | KPI 誤讀，fake coverage 風險 |  |  |  |  | [ ] |
| Q-003 | 1936（去重）vs 1941（原始）分母未統一 | 報表不可對帳，優先級排序失真 |  |  |  |  | [ ] |

---

## B. High Priority

| ID | 問題摘要 | 建議決議方向 | Owner | Deadline | Evidence | 狀態 |
|---|---|---|---|---|---|---|
| Q-004 | 追溯鏈契約要求 vs step-mapping CSV 欄位不足 | 定義「草稿集」與「正式追溯集」最小欄位標準 |  |  |  | [ ] |
| Q-005 | testcase 主鍵命名多版本並存 | 固定 canonical key + 欄位映射表 |  |  |  | [ ] |
| Q-008 | 水位案例名稱疑似誤植（iOS vs BLACK_2 序列） | 回查 TestLink 原始案例命名並標註來源真值 |  |  |  | [ ] |

---

## C. Medium / Low Priority

| ID | 問題摘要 | 建議決議方向 | Owner | Deadline | Evidence | 狀態 |
|---|---|---|---|---|---|---|
| Q-006 | alias ID（如 `KW-ALIAS-GENERIC-ACTION`）缺權威字典 | 建立 alias dictionary v1（id/定義/版本/owner） |  |  |  | [ ] |
| Q-007 | glossary 出現 `APP` / `app` 大小寫分裂 | 定義 canonical normalization 規則 |  |  |  | [ ] |
| Q-009 | `readonly/read-only/manual-only` 寫法不一 | 轉 enum 標準字典（machine-checkable） |  |  |  | [ ] |
| Q-010 | repo 權威來源（codeofthrone-agent vs 本地路徑）不明 | 補「source of truth」聲明 |  |  |  | [ ] |
| Q-011 | README 索引落後，易遺漏交付檔 | 補文件索引章節（含最後更新） |  |  |  | [ ] |
| Q-012 | keyword inventory（待補）缺 owner/ETA/DoD | 升級成里程碑任務（P1 gate） |  |  |  | [ ] |
| Q-013 | locator candidates 缺 trace/evidence 最小欄位 | 補 run metadata + trace linkage 欄位 |  |  |  | [ ] |
| Q-014 | 外部事實快照缺抓取細節 | 加上抓取時間戳與方法欄位 |  |  |  | [ ] |

---

## D. 建議排程（可直接採用）

- **Day 1-2**：完成 Q-001~Q-003（Blocking）
- **Day 3-4**：完成 Q-004~Q-005（Data contract & key naming）
- **Day 5+**：完成其餘 Medium/Low，並更新 README 索引

## E. 驗收標準

- Blocker 全部 `[x]`
- 所有報表數字可用單一分母口徑重算並對帳
- 文件內 testcase key、mapping status、read-only enum 三者一致
- 每個決議都有 Evidence（文件或 commit 連結）
