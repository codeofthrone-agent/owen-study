# Claude Review Questions

## Summary

- Review 範圍：`/Users/owen/source/github.com/owen-study` 內主要交付檔（`.md` 20 份、`.csv` 9 份；已忽略 `.git`）。
- 檢查視角：QA orchestrator 一致性（術語、數字口徑、read-only 約束、traceability 欄位完整性、跨檔矛盾）。
- 本次共記錄 **14** 個疑問，含 **3** 個 blocking items。

## Question Log

| ID | 檔案 | 位置 | 疑問 | 風險等級 | 建議確認人 |
|---|---|---|---|---|---|
| Q-001 | `pablo-qa-orchestrator-status.md` | L352-353, L275, L239-241 | 文件同時宣告「本階段 Redmine/TestLink 僅 read-only、禁止 create/update/delete」，但流程與能力描述仍包含「執行與回填」「post-write verify」。這些寫入動作是**下一階段規劃**還是**本階段可執行**？ | **Blocker** | QA Orchestrator Owner / TestLink 管理者 |
| Q-002 | `step-mapping-split-prefill-v2-report.md`, `testcase-step-keyword-alignment-catalog.md`, `step-mapping-split-prefill-v2.csv` | report L12；catalog L125/L190；csv header + status 統計 | 報告使用 `mapped_rate_after_v2=71.45%`，但 schema 定義 `mapping_status` 有 `mapped/unmapped/manual_only`，實際 v2 CSV 僅見 `manual_only/unmapped`（無 `mapped`）。此 71.45% 應稱為 prefill/manual_only rate 還是 mapped rate？ | **Blocker** | Data Owner（Step Mapping） |
| Q-003 | `pablo-qa-orchestrator-status.md`, `testcase-step-keyword-alignment-catalog.md`, `step-mapping-draft.csv` | status L498；catalog L26/L148；draft rows=1941 | 同一工作流同時使用 `testcase steps（去重）=1936` 與 `原始 steps=1941`。覆蓋率與 backlog（如 unmapped）應以哪個分母為準？目前口徑可能被混用。 | **Blocker** | QA Metrics Owner |
| Q-004 | `pablo-soul-template-qa-architect.md`, `pablo-qa-orchestrator-status.md`, `step-mapping-*.csv` | soul L24/L36；status L253-258；CSV header L1 | 治理要求 `issue_id/testcase_id/keyword_id/trace_id/artifact_uri` 追溯鏈，但 step-mapping 系列 CSV 無 `trace_id/artifact_uri`，且多數也未帶 `redmine_issue_id/testlink_case_id`。這些檔是否定位為「前置草稿」，還是應升級為可追溯正式資料集？ | High | QA Data Contract Owner |
| Q-005 | `pablo-qa-orchestrator-status.md`, `testcase-step-keyword-alignment-catalog.md`, `water-tank-*.csv`, `step-mapping-*.csv` | status L237/L253；catalog L83/L117-119；CSV headers | testcase 主鍵命名多版本並存：`testlink_case_id` / `test_case_id` / `test_case_external_id` / `testcase_external_id` / `case_external_id`。是否已有 canonical naming 與欄位映射表？ | High | Schema Owner / TestLink Connector Maintainer |
| Q-006 | `step-mapping-unmapped-top200.csv`, `testcase-step-keyword-alignment-catalog.md` | top200 L1-5（含 `KW-ALIAS-GENERIC-ACTION`）；catalog alias 列表 L173-200 | `suggested_alias_id` 出現 `KW-ALIAS-GENERIC-ACTION` 等 ID，但 catalog 未見對應治理定義。alias ID 是否有權威字典/版本控管？ | Medium | Mapping Rule Maintainer |
| Q-007 | `testlink-terminology-glossary-v1.csv` | L4, L37, L42 | glossary 同時存在 `APP` 與 `app`（且 category 不同）作為 canonical term，大小寫口徑是否需統一，避免統計與對映分裂？ | Medium | Terminology Owner |
| Q-008 | `water-tank-testcases-manual-only.csv` | L93, L132, L221 | 多筆 testcase 名稱為「`iOS 水位在低 [ 查看iOS ]`」，但 external id 分群看起來屬於 `BLACK_2` 序列；是否為命名誤植或來源資料原始命名？ | High | Test Case Librarian |
| Q-009 | `pablo-qa-orchestrator-status.md` 及相關文檔 | status L190/L245/L257 vs 多處 `read-only` | 同一概念出現 `readonly`、`read-only`、`manual-only` 多種寫法。若後續要做規則解析或機器校驗，是否需固定 enum/value？ | Medium | QA Governance Owner |
| Q-010 | `pablo-qa-orchestrator-status.md` | L116, L533 | 文件標註來源 repo 為 `github.com/codeofthrone-agent/owen-study`，但本地倉庫路徑/目前交付上下文為 `/Users/owen/source/github.com/owen-study`。是否為 fork / mirror 關係，哪個是權威來源？ | Medium | Repo Maintainer |
| Q-011 | `README.md` | L5-9 | README 只索引 4 份文件，與目前大量交付檔不一致；是否需要維護「交付索引清單」避免審閱遺漏？ | Medium | Repo Maintainer |
| Q-012 | `testcase-step-keyword-alignment-catalog.md` | L101-109 | `全域 keyword inventory（待補）` 是後續對齊核心前置，但缺 owner/ETA/完成準則。是否需要升級為明確里程碑（例如 P1 gate）？ | Medium | QA Program Manager |
| Q-013 | `android-locator-candidates.csv`, `phoneclaw-to-appium-locator-pipeline.md`, `pablo-soul-template-qa-architect.md` | candidates header L1；pipeline L30-44；soul L24/L36 | locator candidates 有 `source_run_id` 但無 `trace_id/artifact_uri`；與 orchestrator 證據鏈契約是否一致？是否需要最小追溯欄位（run_time/device/app_build）補齊？ | Medium | Mobile Automation Owner |
| Q-014 | `mempalace-llm-wiki-research-report.md` | L19-23, L381-387 | 外部專案 stars/forks、維護者可信度等屬時效資訊；目前只有調查日期，未標示抓取方法/時間戳細節。是否需要統一「外部事實快照欄位」以便日後追溯？ | Low | Research Doc Owner |

## Blocking Items

1. **Q-001（read-only 範圍衝突）**：不先釐清，後續是否可執行回填會直接影響流程合法性與實作邊界。  
2. **Q-002（mapped_rate 定義不清）**：覆蓋率 KPI 可能被誤讀，導致決策依據失真（fake coverage 風險）。  
3. **Q-003（1936 vs 1941 分母口徑）**：所有 coverage/backlog 數字無法穩定對帳，會影響跨報告比較與優先級排序。
