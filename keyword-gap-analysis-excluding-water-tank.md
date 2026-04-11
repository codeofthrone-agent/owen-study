# Keyword Gap Analysis (Water Policy: Only Default Full Level)

> Rule applied（最新）：水箱 testcase 僅保留「預設滿水位 / 水位在高」作為 automation candidate；其餘一律 `manual_only`。
> Data source: `step-mapping-draft.csv` snapshot.

## Summary

- Total water-related testcases identified: 375
- Water cases kept as automation candidate (default full/high): 146
- Water cases forced manual_only: 229
- Total steps in snapshot: 1941
- Water-related steps (all): 330
- Water steps excluded (manual_only): 199
- Water steps kept (default full/high): 131
- Automation-target steps after policy: 1742

## Notes

- 這份統計是「策略口徑更新」用；重點是把水箱域拆成：
  1) **可評估自動化**：預設滿水位（high）
  2) **暫不自動化**：其餘水箱情境
- `mapped_keyword_id` 在 draft 中包含人工 alias 預填，**不可視為真實自動化覆蓋率**（避免 fake coverage）。

## Artifacts

- `water-tank-default-full-allowlist.csv`
- `water-tank-testcases-manual-only.csv` (updated by new policy)
