## Why

`scripts/robot_arm_server.py` 目前有 3,903 行，包含 6 個超大方法（最長 311 行）和 67 處重複的 `except Exception` 模式。雖然功能完整，但隨著版本迭代（v5.6.2）已累積大量技術債：新增命令需要複製大量樣板程式碼、除錯困難（單一方法承載多個職責）、且難以為個別功能補充測試。本次重構**維持單一檔案**原則，透過拆分過長方法與統一重複模式，提升可維護性，而不改變任何對外行為。

## What Changes

- **`MycobotServer.__init__` 拆分**（257 行 → 流程清晰的 ~50 行主方法）
  - 抽出 `_init_variables()`、`_init_socket()`、`_init_vision()`、`_init_http()`
  - 啟動流程一目了然，各階段失敗點獨立
- **`_cmd_scan_and_detect` 拆分**（311 行 → 3 個職責清楚的子方法）
  - `_parse_scan_angles()` — 解析輸入參數
  - `_execute_scan_sequence()` — 移動 + 拍照 + 偵測
  - `_aggregate_scan_results()` — 合併去重結果
- **統一重試邏輯**（3 處各自實作 → 1 個 `_with_retry()` helper）
  - 取代 `_get_angles_with_retry`、`_detect_with_retry`、`write()` 內嵌重試
- **統一命令回傳格式**（15 個命令處理器各自組裝 dict → `_cmd_response()` helper）
  - 確保所有命令處理器回傳一致的 `{status, message}` 結構

## Non-goals

- 不拆分成多個檔案（維持單一檔案管理）
- 不改變任何 JSON 命令的 API 介面（command type、參數名、回傳結構）
- 不改變 pymycobot 二進位協定的處理邏輯
- 不新增功能
- 不升級版本號（由實作後決定）
