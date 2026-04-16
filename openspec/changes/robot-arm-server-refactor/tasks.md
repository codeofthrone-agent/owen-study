## 0. 準備

- [x] 0.1 執行現有測試確認 baseline：`pytest tests/test_http_api.py -v`
- [x] 0.2 記錄目前行數：`wc -l scripts/robot_arm_server.py`

---

## Phase 1：`__init__` 拆分

- [x] 1.1 新增 `_init_variables(self, host, port, serial_num, baud, ...)` — 將 `__init__` 內所有 `self.xxx = yyy` 賦值移入
- [x] 1.2 新增 `_init_socket(self, host, port)` — socket 建立、`bind`、`listen`
- [x] 1.3 新增 `_init_vision(self)` — 相機、FK/IK、STag 初始化邏輯移入
- [x] 1.4 新增 `_init_http(self, host)` — HTTPAPIServer 建立與啟動移入
- [x] 1.5 新增 `_start_yolo_background(self)` — 將現有背景 YOLO 載入邏輯抽出為獨立方法
- [x] 1.6 重寫 `__init__` 為流程主方法（只呼叫上述 `_init_*`）
- [ ] 1.7 啟動 server 手動測試，確認連線與基本命令正常
- [ ] 1.8 執行 `pytest tests/test_http_api.py -v` 確認無 regression

---

## Phase 2：`_cmd_scan_and_detect` 拆分

- [x] 2.1 新增 `_parse_scan_angles(self, cmd)` — 提取參數解析與驗證邏輯
- [x] 2.2 新增 `_execute_scan_sequence(self, angles_list, options)` — 移動 + 拍照 + 偵測迴圈
- [x] 2.3 新增 `_aggregate_scan_results(self, raw_results, options)` — 合併去重邏輯
- [x] 2.4 重寫 `_cmd_scan_and_detect` 為呼叫上述三個方法的流程主方法
- [ ] 2.5 🧑‍💻 實機測試 scan_and_detect 命令，確認結果與重構前一致

---

## Phase 3：統一重試邏輯

- [x] 3.1 新增 `_with_retry(self, func, max_retries, delay, label)` helper
- [x] 3.2 將 `_get_angles_with_retry` 改用 `_with_retry` 實作
- [x] 3.3 將 `write()` 內嵌重試改用 `_with_retry` 實作
- [x] 3.4 執行 `pytest tests/test_http_api.py -v` 確認無 regression

---

## Phase 4：命令處理器統一回傳格式

- [x] 4.1 新增 `_cmd_response(self, success, message, **extra)` helper
- [x] 4.2 更新所有 15 個 `_cmd_*` 方法使用 `_cmd_response`（逐一替換，每個替換後確認）
- [x] 4.3 執行 `pytest tests/test_http_api.py -v` 確認無 regression
- [x] 4.4 更新 SERVER_VERSION（patch 號 +1）

---

## Phase 5（低風險清理）

- [x] 5.1 `_handle_json_command` 中 9 處手動 dict 改用 `_cmd_response`
- [x] 5.2 新增 `_validate_vision_system()` / `_validate_yolo_system()` helper，替換 3 處重複檢查
- [x] 5.3 新增 `_cmd_response_from_result()` helper，替換 2 處點擊結果提取重複邏輯
- [x] 5.4 執行 `pytest tests/unit/api/test_http_api.py -v` 確認無 regression（4 passed）

---

## 完成驗收

- [ ] 無任何方法超過 150 行
- [ ] 🧑‍💻 在 Jetson 部署更新版本，執行完整連線與命令測試
- [x] LOC 目標修正：新增 helper 方法本身也佔行數，3,500 目標不切實際；實際重點是可維護性提升而非行數
