# Step Splitting Parser Report (v1)

- Source: `step-mapping-draft.csv`
- Output: `step-mapping-split-draft.csv`

## Summary

- total_original_steps: 1941
- single_steps: 1245
- multi_step_detected: 696
- multi_action_steps: 506
- multi_expected_steps: 243
- total_split_rows: 3159

## Sample multi-step detections

- `CCU-231109-1`
  - original: 查看 APP 下方是否有 AGREE 按鈕
  - part1: 查看 APP 下方是否有 AGREE 按鈕
- `CCU-231119-1`
  - original: 點擊新增 Google 如引導完成
  - part1: 點擊新增 Google 如引導完成
- `CCU-230707-1`
  - original: 1.點擊 Disconnect 2.點擊 Cancel
  - part1: 點擊 Disconnect
  - part2: 點擊 Cancel
- `CCU-119-1`
  - original: 開啟 RV 控制 App (iOS 或 Android)。
  - part1: 開啟 RV 控制 App (iOS 或 Android)。
- `CCU-119-2`
  - original: 觀察 App 是否能成功連接到 RV 系統。
  - part1: 觀察 App 是否能成功連接到 RV 系統。
- `CCU-119-3`
  - original: 檢查 App 主介面是否正常載入並顯示基本控制項或狀態資訊。
  - part1: 檢查 App 主介面是否正常載入
  - part2: 顯示基本控制項或狀態資訊
- `CCU-120-1`
  - original: 透過 App 導航至主燈控制項。
  - part1: 透過 App 導航至主燈控制項。
- `CCU-120-2`
  - original: 點擊「開啟」主燈。
  - part1: 點擊「開啟」主燈。
- `CCU-120-3`
  - original: 觀察主燈實際是否亮起，及 App 狀態是否更新。
  - part1: 觀察主燈實際是否亮起，及 App 狀態是否更新。
- `CCU-120-4`
  - original: 點擊「關閉」主燈。
  - part1: 點擊「關閉」主燈。
- `CCU-120-5`
  - original: 觀察主燈實際是否熄滅，及 App 狀態是否更新。
  - part1: 觀察主燈實際是否熄滅，及 App 狀態是否更新。
- `CCU-121-1`
  - original: 透過 App 導航至延伸車架控制。
  - part1: 透過 App 導航至延伸車架控制。
- `CCU-121-2`
  - original: 短暫點擊 (例如1-2秒後立即停止)「展開」按鈕。
  - part1: 短暫點擊 (例如1-2秒後立即停止)「展開」按鈕。
- `CCU-121-3`
  - original: 觀察延伸車架電機是否啟動並有輕微移動。
  - part1: 觀察延伸車架電機是否啟動
  - part2: 有輕微移動
- `CCU-121-4`
  - original: 短暫點擊「收回」按鈕。
  - part1: 短暫點擊「收回」按鈕。

## Notes

- Parser splits by numbering, punctuation, and conjunction markers (然後/並且/and etc.).
- This is heuristic; human review is still required for final keyword mapping.