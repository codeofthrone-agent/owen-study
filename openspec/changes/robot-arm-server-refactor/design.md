## 設計決策

### 維持單一檔案

`robot_arm_server.py` 部署在 Jetson Nano 的 `~/server/` 目錄，不依賴此 repo 的 `libraries/`。單一檔案讓 Jetson 端的維護與部署更簡單（`scp` 一個檔案即完成更新）。

### 拆分策略：方法內拆分，不建新 class

本次重構只在 `MycobotServer` 內增加 private method，不新增 class。理由：
- 新 class 需要傳遞 `self.mc`、`self.logger` 等共享狀態，增加耦合
- 同一 class 內的 private method 可直接存取所有狀態，無額外複雜度

---

## 重構後結構

```python
# ── 全局常數與協定定義 (行 1-180) ────────────────────────
PROTOCOL_HEADER, CMD_*, has_return = ...

# ── HTTPAPIServer (行 183-756) ── 不動 ──────────────────

# ── CameraCapture (行 757-996) ── 不動 ──────────────────

# ── DiskManager (行 997-1090) ── 不動 ───────────────────

# ── MycobotServer (行 1118+) ─────────────────────────────
class MycobotServer:

    # 初始化（Phase 1）
    def __init__(self, ...)          # ~50 行：只呼叫 _init_* 方法
    def _init_variables(self, ...)   # ~40 行：所有 self.xxx = 賦值
    def _init_socket(self, ...)      # ~15 行：bind + listen
    def _init_vision(self, ...)      # ~60 行：相機 + FK/IK + STag
    def _init_http(self, ...)        # ~30 行：HTTPAPIServer 啟動
    def _start_yolo_background(self) # ~25 行：背景 thread 載入 YOLO

    # 工具 helpers（Phase 3 & 4）
    def _with_retry(self, func, ...)      # ~20 行：統一重試
    def _cmd_response(self, ok, msg, ...) # ~8 行：統一回傳格式

    # Serial 通信（不動）
    def write, read, re_data_2, _cleanup, ...

    # 連線管理（不動）
    def connect, shutdown, _init_serial, _reconnect_serial, ...

    # 運動控制（不動）
    def get_angles, _send_angles_internal, _wait_for_movement, ...

    # 命令分發（Phase 4 調整回傳格式）
    def _handle_json_command(self, cmd)   # 不動（只改子命令）
    def _cmd_power_on/off(self, cmd)      # 使用 _cmd_response
    def _cmd_move_to_angles(self, cmd)    # 使用 _cmd_response
    ... (其他 12 個命令處理器)

    # _cmd_scan_and_detect 拆分（Phase 2）
    def _cmd_scan_and_detect(self, cmd)   # ~30 行：流程主方法
    def _parse_scan_angles(self, cmd)     # ~20 行
    def _execute_scan_sequence(self, ...) # ~50 行
    def _aggregate_scan_results(self, ...) # ~30 行
```

---

## 各 Phase 詳細設計

### Phase 1：`__init__` 拆分

**目前問題：**
- 257 行混合了：socket 初始化、serial 初始化、相機初始化、FK/IK 載入、STag 初始化、YOLO 背景 thread、HTTP server 啟動

**重構後 `__init__`（~50 行）：**
```python
def __init__(self, host, port, serial_num, baud, ...):
    self._init_variables(host, port, serial_num, baud, ...)
    self._init_socket(host, port)
    if not self._init_serial():
        self.shutdown(); sys.exit(1)
    self._init_vision()
    self._init_http(host)
    self._start_yolo_background()
    self.connect()
```

**各子方法職責：**
| 方法 | 職責 | 預計行數 |
|------|------|---------|
| `_init_variables` | 所有 `self.xxx = yyy` 賦值 | ~40 |
| `_init_socket` | `socket.bind` + `listen` | ~15 |
| `_init_vision` | 相機 + FK/IK + STag 初始化 | ~60 |
| `_init_http` | HTTPAPIServer 建立與啟動 | ~30 |
| `_start_yolo_background` | 背景 thread（已實作，抽出來） | ~25 |

---

### Phase 2：`_cmd_scan_and_detect` 拆分

**目前問題：** 311 行同時做：參數解析、移動序列、拍照、YOLO 偵測、結果合併去重

**重構後：**
```python
def _cmd_scan_and_detect(self, cmd):
    """掃描並偵測：移動到多個角度位置，對每個位置執行 YOLO 偵測後合併結果"""
    try:
        angles_list, options = self._parse_scan_angles(cmd)
        raw_results = self._execute_scan_sequence(angles_list, options)
        final = self._aggregate_scan_results(raw_results, options)
        return self._cmd_response(True, f"掃描完成，共偵測到 {len(final)} 個物件", detections=final)
    except Exception as e:
        self.logger.error(f"掃描偵測失敗: {e}")
        return self._cmd_response(False, str(e))
```

---

### Phase 3：統一重試邏輯

**目前重複：**
- `_get_angles_with_retry`：重試讀取角度
- `_detect_with_retry`（HTTPAPIServer）：重試 YOLO 偵測
- `write()` 方法內嵌重試：重試序列寫入

**統一 helper：**
```python
def _with_retry(self, func, max_retries=3, delay=1.0, label="操作"):
    """執行函數，失敗時自動重試"""
    for i in range(max_retries):
        try:
            result = func()
            if result is not None:
                return result
        except Exception as e:
            self.logger.warning(f"{label} 第 {i+1}/{max_retries} 次失敗: {e}")
        if i < max_retries - 1:
            time.sleep(delay)
    self.logger.error(f"{label} 重試 {max_retries} 次後仍失敗")
    return None
```

---

### Phase 4：命令處理器統一回傳格式

**目前重複（每個 `_cmd_*` 都自己組 dict）：**
```python
return {"status": "success", "message": "已完成"}
return {"status": "error", "message": str(e)}
```

**統一 helper：**
```python
def _cmd_response(self, success: bool, message: str, **extra) -> dict:
    return {"status": "success" if success else "error",
            "message": message, **extra}
```

**使用範例：**
```python
def _cmd_power_off(self, cmd):
    try:
        self.write(CMD_POWER_OFF)
        return self._cmd_response(True, "已關閉伺服馬達")
    except Exception as e:
        self.logger.error(f"Power Off 失敗: {e}")
        return self._cmd_response(False, str(e))
```

---

## 測試策略

重構前先確認現有測試可以跑通作為 baseline：
```bash
pytest tests/test_http_api.py -v
```

每個 Phase 完成後執行一次，確保無 regression。
