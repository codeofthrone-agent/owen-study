# 遠端 UART 配置驗證腳本使用指南

## 概述

`validate_remote_uart_config.py` 是一個獨立的 Python 腳本，用於驗證遠端語音助手設備的 UART 配置是否正確。

**版本：** v1.1.0
**最後更新：** 2025-11-11
**更新內容：** 支援重複執行錯誤檢測，改進 sed 修正策略

## 功能特色

✅ **自動檢測** - 檢查 `/etc/init.d/emmc` 配置（支援 4 種錯誤模式）
✅ **自動修正** - 檢測到錯誤時自動修正配置（兩步驟 sed 策略）
✅ **安全備份** - 修正前自動備份原始配置
✅ **重開機提示** - 修正後提供明確的重開機指示
✅ **僅檢查模式** - 可選擇僅檢查，不修正
✅ **詳細日誌** - 支援 DEBUG 級別日誌輸出
✅ **環境變數支援** - 可從 `.env` 讀取配置
✅ **美化輸出** - 清晰的結果顯示
✅ **重複執行修正** - v1.1.0 新增，修正 sed 替換導致的重複執行問題

## 系統需求

```bash
# Python 套件
pip install pyserial loguru python-dotenv

# 或使用專案的 requirements.txt
uv pip install -r requirements.txt
```

## 快速開始

### 基本使用

```bash
# 使用預設值（/dev/ttyUSB0, 115200）
python3 scripts/validate_remote_uart_config.py
```

### 指定串列埠和鮑率

```bash
python3 scripts/validate_remote_uart_config.py --port /dev/ttyUSB1 --baudrate 9600
```

### 僅檢查模式（不自動修正）

```bash
python3 scripts/validate_remote_uart_config.py --check-only
```

### 詳細模式（DEBUG 日誌）

```bash
python3 scripts/validate_remote_uart_config.py --verbose
```

### 使用環境變數

```bash
# 設定環境變數
export UART_PORT=/dev/ttyUSB0

# 執行腳本（會自動讀取環境變數）
python3 scripts/validate_remote_uart_config.py
```

## 命令列參數

| 參數 | 簡寫 | 說明 | 預設值 |
|------|------|------|--------|
| `--port` | `-p` | UART 串列埠路徑 | `/dev/ttyUSB0` 或 `$UART_PORT` |
| `--baudrate` | `-b` | 鮑率 | `115200` |
| `--timeout` | `-t` | 命令執行超時（秒） | `5.0` |
| `--check-only` | `-c` | 僅檢查，不修正 | `False` |
| `--verbose` | `-v` | 詳細模式 | `False` |
| `--help` | `-h` | 顯示幫助訊息 | - |

## 使用範例

### 範例 1：首次設定新設備

```bash
$ python3 scripts/validate_remote_uart_config.py

======================================================================
  遠端 UART 配置驗證工具 v1.0.0
  Remote UART Configuration Validator
======================================================================

📝 配置資訊:
   - UART 端口: /dev/ttyUSB0
   - 鮑率: 115200
   - 命令超時: 5.0 秒
   - 模式: 自動修正

INFO     | 初始化遠端配置驗證器...
INFO     | 開始完整驗證流程（含自動修正）...
INFO     | 驗證遠端系統配置...
INFO     | 嘗試連接串列埠: /dev/ttyUSB0
INFO     | ✓ 串列埠連接成功: /dev/ttyUSB0
INFO     | 等待遠端設備就緒...
INFO     | 檢查遠端配置檔: /etc/init.d/emmc
WARNING  | ⚠️ 檢測到配置錯誤: output_to_null
WARNING  |    錯誤行: /uvoice/start_uvoice.sh > /dev/null
INFO     | 將自動修正為: /uvoice/start_uvoice.sh > /dev/ttyS0 &
INFO     | ==========================================================
INFO     | 正在修正遠端配置...
INFO     | 步驟 1: 備份原始配置
INFO     | ✓ 配置已備份
INFO     | 步驟 2: 修正配置
INFO     | 步驟 3: 驗證修正結果
INFO     | ✓ 配置修正成功
INFO     |    新配置: /uvoice/start_uvoice.sh > /dev/ttyS0 &
INFO     | ==========================================================

======================================================================
  驗證結果摘要
======================================================================

⚠️  配置狀態: 已修正
   配置已自動修正，但需要重開機才能生效

📊 詳細資訊:
   - 配置正確: False
   - 已修正:   True
   - 需要重開機: True

🔍 檢測到的配置問題:
   - 錯誤類型: output_to_null
   - 錯誤行: /uvoice/start_uvoice.sh > /dev/null

======================================================================
⚠️  重要：配置已修正，但需要重開機才能生效
======================================================================

請執行以下步驟：

1. 在遠端設備上執行重開機命令：
   reboot

2. 等待設備重新啟動（約 30-60 秒）

3. 重新執行此驗證腳本確認配置生效

======================================================================
```

**退出碼：** `2`（配置已修正，需要重開機）

---

### 範例 2：驗證配置已正確

設備重開機後，再次執行驗證：

```bash
$ python3 scripts/validate_remote_uart_config.py

======================================================================
  遠端 UART 配置驗證工具 v1.0.0
  Remote UART Configuration Validator
======================================================================

📝 配置資訊:
   - UART 端口: /dev/ttyUSB0
   - 鮑率: 115200
   - 命令超時: 5.0 秒
   - 模式: 自動修正

INFO     | 初始化遠端配置驗證器...
INFO     | 開始完整驗證流程（含自動修正）...
INFO     | 驗證遠端系統配置...
INFO     | 嘗試連接串列埠: /dev/ttyUSB0
INFO     | ✓ 串列埠連接成功: /dev/ttyUSB0
INFO     | 等待遠端設備就緒...
INFO     | 檢查遠端配置檔: /etc/init.d/emmc
INFO     | ✓ 配置已經正確
INFO     | ✓ 遠端配置正確

======================================================================
  驗證結果摘要
======================================================================

✅ 配置狀態: 正確
   遠端設備配置正確，可以開始測試

📊 詳細資訊:
   - 配置正確: True
   - 已修正:   False
   - 需要重開機: False
```

**退出碼：** `0`（配置正確）

---

### 範例 3：僅檢查模式

```bash
$ python3 scripts/validate_remote_uart_config.py --check-only

======================================================================
  遠端 UART 配置驗證工具 v1.0.0
  Remote UART Configuration Validator
======================================================================

📝 配置資訊:
   - UART 端口: /dev/ttyUSB0
   - 鮑率: 115200
   - 命令超時: 5.0 秒
   - 模式: 僅檢查

INFO     | 初始化遠端配置驗證器...
INFO     | 執行僅檢查模式（不會自動修正配置）
INFO     | 嘗試連接串列埠: /dev/ttyUSB0
INFO     | ✓ 串列埠連接成功: /dev/ttyUSB0
INFO     | 等待遠端設備就緒...
INFO     | 檢查遠端配置檔: /etc/init.d/emmc
WARNING  | ⚠️ 檢測到配置錯誤: output_to_null
WARNING  |    錯誤行: /uvoice/start_uvoice.sh > /dev/null

======================================================================
  驗證結果摘要
======================================================================

❌ 配置狀態: 錯誤

📊 詳細資訊:
   - 配置正確: False
   - 已修正:   False
   - 需要重開機: False

🔍 檢測到的配置問題:
   - 錯誤類型: output_to_null
   - 錯誤行: /uvoice/start_uvoice.sh > /dev/null
```

**退出碼：** `1`（驗證失敗）

---

### 範例 4：串列埠不存在

```bash
$ python3 scripts/validate_remote_uart_config.py --port /dev/ttyUSB9

======================================================================
  遠端 UART 配置驗證工具 v1.0.0
  Remote UART Configuration Validator
======================================================================

📝 配置資訊:
   - UART 端口: /dev/ttyUSB9
   - 鮑率: 115200
   - 命令超時: 5.0 秒
   - 模式: 自動修正

ERROR    | 串列埠不存在: /dev/ttyUSB9

💡 提示:
   1. 檢查 UART 轉 USB 模組是否已連接
   2. 執行 'ls /dev/ttyUSB*' 查看可用的串列埠
   3. 確認使用者有權限訪問串列埠（加入 dialout 群組）
```

**退出碼：** `1`（驗證失敗）

---

### 範例 5：權限不足

```bash
$ python3 scripts/validate_remote_uart_config.py

======================================================================
  遠端 UART 配置驗證工具 v1.0.0
  Remote UART Configuration Validator
======================================================================

📝 配置資訊:
   - UART 端口: /dev/ttyUSB0
   - 鮑率: 115200
   - 命令超時: 5.0 秒
   - 模式: 自動修正

ERROR    | 權限不足，無法訪問串列埠: /dev/ttyUSB0

💡 解決方法:
   1. 將使用者加入 dialout 群組:
      sudo usermod -a -G dialout $USER
   2. 登出重新登入
   3. 或臨時修改權限:
      sudo chmod 666 /dev/ttyUSB0
```

**退出碼：** `1`（驗證失敗）

## 退出碼說明

| 退出碼 | 說明 | 情況 |
|--------|------|------|
| `0` | 成功 | 配置正確，無需修正 |
| `1` | 失敗 | 驗證失敗、權限不足、串列埠不存在等 |
| `2` | 需要重開機 | 配置已修正，但需要重開機才能生效 |
| `130` | 使用者中斷 | Ctrl+C 中斷執行 |

## 整合到測試流程

### CI/CD 整合

```bash
#!/bin/bash
# ci_test.sh

echo "步驟 1: 驗證遠端 UART 配置"
python3 scripts/validate_remote_uart_config.py
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 配置正確，繼續測試"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️  配置已修正，需要重開機"
    echo "請手動重開機後重新執行 CI"
    exit 1
else
    echo "✗ 配置驗證失敗"
    exit 1
fi

echo "步驟 2: 執行 Robot Framework 測試"
robot tests/voice_assistant/
```

### Makefile 整合

```makefile
.PHONY: validate-uart test-uart

validate-uart:
	@echo "驗證遠端 UART 配置..."
	@python3 scripts/validate_remote_uart_config.py

test-uart: validate-uart
	@echo "執行 UART 測試..."
	@robot tests/voice_assistant/uart_audio_detection_test.robot
```

使用：
```bash
make validate-uart  # 僅驗證配置
make test-uart      # 驗證配置後執行測試
```

## 故障排除

### 問題 1：找不到模組

**錯誤：**
```
ModuleNotFoundError: No module named 'libraries.multimodal_detection'
```

**解決：**
```bash
# 確保在專案根目錄執行
cd /home/thortron/Tools/robot-multiplatform-automation
python3 scripts/validate_remote_uart_config.py
```

---

### 問題 2：pyserial 未安裝

**錯誤：**
```
ImportError: pyserial 未安裝，無法使用 UART 功能
```

**解決：**
```bash
pip install pyserial
# 或
uv pip install pyserial
```

---

### 問題 3：檢測到重複執行錯誤（duplicate_execution）⭐ v1.1.0

**錯誤訊息：**
```
WARNING  | ⚠️ 檢測到配置錯誤: duplicate_execution
WARNING  |    錯誤行: /uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh
```

**原因：** 之前的 sed 替換操作未正確處理整行，導致配置重複

**解決方法：**

1. **恢復備份（如果修正失敗）：**
   ```bash
   uv run python3 scripts/restore_emmc_backup.py
   ```

2. **重新執行修正（使用新的 sed 策略）：**
   ```bash
   uv run python3 scripts/validate_remote_uart_config.py
   ```

3. **手動驗證配置：**
   ```bash
   uv run python3 scripts/check_current_config.py
   ```

**v1.1.0 改進：**
- ✅ 新增 `duplicate_execution` 錯誤檢測模式
- ✅ 改用兩步驟 sed 策略（刪除 + 插入）
- ✅ 提供 `restore_emmc_backup.py` 恢復工具
- ✅ 提供 `check_current_config.py` 檢查工具

---

### 問題 4：UART 連線逾時

**現象：** 命令執行超時，未收到回應

**解決：**
```bash
# 增加超時時間
python3 scripts/validate_remote_uart_config.py --timeout 10.0

# 或使用詳細模式查看詳細資訊
python3 scripts/validate_remote_uart_config.py --verbose
```

---

### 問題 4：設備回應不正常

**現象：** 讀取到的配置內容為空或亂碼

**解決：**
```bash
# 1. 檢查鮑率是否正確
python3 scripts/validate_remote_uart_config.py --baudrate 9600

# 2. 手動測試 UART 連線
tio /dev/ttyUSB0 -b 115200

# 3. 在 tio 中手動執行命令
> cat /etc/init.d/emmc
```

## 進階用法

### 自訂腳本

基於此腳本建立自訂驗證流程：

```python
#!/usr/bin/env python3
from scripts.validate_remote_uart_config import main as validate_main
import sys

def custom_validation():
    # 執行驗證
    result = validate_main()

    if result == 0:
        print("✓ 配置正確，執行額外檢查...")
        # 執行額外的檢查邏輯
    elif result == 2:
        print("⚠️  等待使用者重開機...")
        # 可以加入自動重試邏輯
    else:
        print("✗ 驗證失敗，中止測試")
        sys.exit(1)

if __name__ == "__main__":
    custom_validation()
```

### Python API 使用

直接在 Python 程式中使用：

```python
import sys
from pathlib import Path

# 加入專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

# 建立驗證器
validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)

# 執行驗證
result = validator.validate_uart_setup()

# 處理結果
if result['config_ok']:
    print("✓ 配置正確")
    # 繼續執行測試
elif result['fixed'] and result['needs_reboot']:
    print(f"⚠️  請重開機: {result['reboot_command']}")
    # 等待重開機
else:
    print(f"✗ 錯誤: {result['error_message']}")
    # 處理錯誤
```

## 最佳實踐

1. **測試前驗證** - 在執行 UART 測試前自動驗證配置
2. **CI/CD 整合** - 整合到持續整合流程，確保環境正確
3. **定期檢查** - 定期執行驗證，確保配置未被意外修改
4. **日誌記錄** - 使用 `--verbose` 模式記錄詳細日誌供故障排除
5. **環境變數** - 使用環境變數管理不同環境的配置

## 相關文檔

- 📖 [RemoteSystemConfigValidator 完整指南](../docs/remote_config_validator_guide.md)
- 📖 [UART 音訊檢測指南](../docs/uart_audio_detection_guide.md)
- 🧪 [UART 測試案例](../tests/voice_assistant/uart_audio_detection_test.robot)

---

**維護者：** Robot Automation Team
**最後更新：** 2025-11-11
**版本：** 1.0.0
