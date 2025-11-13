# RemoteSystemConfigValidator 使用指南

## 概述

`RemoteSystemConfigValidator` 是一個透過 UART 串列埠連接到遠端語音助手設備，自動檢查並修正系統配置的工具。它確保遠端設備的日誌正確輸出到 UART，為後續的語音檢測功能奠定基礎。

**版本：** v1.1.0
**最後更新：** 2025-11-11
**作者：** Robot Automation Team
**更新內容：** 修正 sed 替換策略，支援重複執行錯誤檢測

---

## 目錄

1. [功能特色](#功能特色)
2. [應用場景](#應用場景)
3. [系統需求](#系統需求)
4. [快速開始](#快速開始)
5. [配置說明](#配置說明)
6. [Python API](#python-api)
7. [Robot Framework 整合](#robot-framework-整合)
8. [工作流程](#工作流程)
9. [錯誤處理](#錯誤處理)
10. [故障排除](#故障排除)
11. [最佳實踐](#最佳實踐)

---

## 功能特色

### 核心功能

✅ **UART 串列埠通訊**
- 透過 `/dev/ttyUSB0` 連接遠端設備
- 支援 115200 鮑率（可配置）
- 穩定的串列埠連線管理

✅ **遠端命令執行**
- 透過 UART 執行 shell 命令
- 標記式回應解析（marker-based response parsing）
- 超時控制與錯誤處理

✅ **配置檢查**
- 自動檢查 `/etc/init.d/emmc` 配置
- 使用正規表達式偵測錯誤模式
- 完整的配置內容讀取

✅ **自動修正**
- 檢測到錯誤配置時自動修正
- 自動備份原始配置檔
- 安全的 sed 替換操作

✅ **重開機提示**
- 修正後提供明確的重開機指示
- 不自動執行重開機（避免意外中斷）

✅ **Robot Framework 整合**
- 提供中文 Gherkin 風格關鍵字
- 完整的測試案例支援
- 自動整合到 SerialLogParser

---

## 應用場景

### 1. 初次設備設定

當新部署語音助手設備時，自動檢查並配置 UART 輸出：

```python
from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
result = validator.validate_uart_setup()

if result['needs_reboot']:
    print(f"配置已修正，請執行: {result['reboot_command']}")
```

### 2. 自動化測試前置準備

在執行 UART 日誌檢測測試前，自動驗證遠端配置：

```robot
*** Test Cases ***
語音助手多模態檢測
    Given 初始化串列埠監控器    /dev/ttyUSB0    115200    auto_validate=True
    When 播放喚醒詞並檢測回應
    Then 應該檢測到視覺和聽覺回應
```

### 3. CI/CD 整合

在持續整合流程中自動驗證測試環境配置：

```bash
# 在測試執行前驗證配置
python3 -c "
from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator
validator = RemoteSystemConfigValidator()
result = validator.validate_uart_setup()
if result['needs_reboot']:
    print('ERROR: Device needs reboot')
    exit(1)
"
```

### 4. 故障排除與診斷

當 UART 日誌檢測失敗時，快速診斷配置問題：

```robot
*** Keywords ***
診斷 UART 配置問題
    ${result}=    驗證遠端系統配置

    Run Keyword If    '${result['error_message']}' != 'None'
    ...    Log    錯誤: ${result['error_message']}    ERROR

    Run Keyword If    ${result['needs_reboot']}
    ...    Fail    配置已修正但需要重開機
```

---

## 系統需求

### 硬體需求

- **UART 轉 USB 轉接器**（如 CP2102, FTDI）
- **連接線**：連接測試主機與語音助手設備的 UART 接腳
- **語音助手設備**：運行 Linux 系統，具備 `/etc/init.d/emmc` 配置

### 軟體需求

- **Python 3.8+**
- **pyserial 3.5+**
- **loguru** （日誌管理）
- **Robot Framework 7.0+**（Robot 測試需要）

### 環境配置

```bash
# 安裝相依套件
pip install pyserial loguru

# 檢查 UART 設備
ls -l /dev/ttyUSB*

# 確認使用者權限（加入 dialout 群組）
sudo usermod -a -G dialout $USER
# 需要登出重新登入生效
```

---

## 快速開始

### Python 獨立使用

```python
#!/usr/bin/env python3
from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

# 1. 建立驗證器實例
validator = RemoteSystemConfigValidator(
    port='/dev/ttyUSB0',
    baudrate=115200,
    command_timeout=5.0
)

# 2. 執行完整驗證流程
result = validator.validate_uart_setup()

# 3. 處理結果
if result['config_ok']:
    print("✓ 配置正確，可以開始測試")
elif result['fixed']:
    print(f"⚠️  配置已修正，請執行: {result['reboot_command']}")
    print("重開機後重新執行測試")
else:
    print(f"✗ 驗證失敗: {result['error_message']}")
```

### Robot Framework 使用

```robot
*** Settings ***
Library    libraries/multimodal_detection/SerialLogParser.py

*** Test Cases ***
測試語音助手回應（自動驗證配置）
    # SerialLogParser 會在連接時自動驗證配置
    ${success}=    初始化串列埠監控器    /dev/ttyUSB0    115200    auto_validate=True
    Should Be True    ${success}    配置驗證失敗或需要重開機

    # 後續測試...
```

### 手動驗證

```robot
*** Test Cases ***
手動驗證遠端配置
    ${result}=    驗證遠端系統配置

    Should Be True    ${result['config_ok']} or ${result['fixed']}
    ...    配置檢查失敗
```

---

## 配置說明

### 環境變數配置

在 `.env` 檔案中設定：

```bash
# UART 串列埠配置
UART_PORT=/dev/ttyUSB0
```

### 錯誤配置模式

RemoteSystemConfigValidator 會檢測以下錯誤模式（v1.1.0 新增重複執行檢測）：

#### 1. 重複執行（duplicate_execution）⭐ v1.1.0 新增

**錯誤配置：**
```bash
/uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh
```

**問題：** 同一行出現兩次 `start_uvoice.sh`，導致程式重複執行或配置錯誤

**原因：** 通常由 sed 替換錯誤造成

**修正為：**
```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

#### 2. 輸出到 /dev/null（output_to_null）

**錯誤配置：**
```bash
/uvoice/start_uvoice.sh > /dev/null
```

**問題：** 日誌被導向黑洞，無法透過 UART 讀取

**修正為：**
```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

#### 3. 沒有重導向（no_redirect）

**錯誤配置：**
```bash
/uvoice/start_uvoice.sh &
```

**問題：** 日誌輸出到標準輸出，未導向 UART

**修正為：**
```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

#### 4. 沒有背景執行（no_background）

**錯誤配置：**
```bash
/uvoice/start_uvoice.sh
```

**問題：** 程式前景執行，阻塞啟動流程

**修正為：**
```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

### 正確配置

```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

**說明：**
- `/uvoice/start_uvoice.sh`：語音助手啟動腳本
- `> /dev/ttyS0`：重導向輸出到 UART 串列埠
- `&`：背景執行，不阻塞啟動

---

## Python API

### 類別：RemoteSystemConfigValidator

#### 初始化

```python
validator = RemoteSystemConfigValidator(
    port='/dev/ttyUSB0',      # UART 串列埠路徑
    baudrate=115200,          # 鮑率
    command_timeout=5.0       # 命令執行超時（秒）
)
```

#### 方法

##### connect() -> bool

連接串列埠。

**返回：**
- `True`：連接成功
- `False`：連接失敗

**範例：**
```python
if validator.connect():
    print("✓ 串列埠連接成功")
else:
    print("✗ 串列埠連接失敗")
```

---

##### disconnect()

關閉串列埠連接。

**範例：**
```python
validator.disconnect()
```

---

##### execute_remote_command(cmd: str, timeout: Optional[float] = None) -> str

透過 UART 執行遠端命令並取得輸出。

**參數：**
- `cmd`：要執行的命令
- `timeout`：超時時間（秒），預設使用 `command_timeout`

**返回：**
- 命令輸出結果（字串）

**範例：**
```python
# 讀取檔案
content = validator.execute_remote_command("cat /etc/init.d/emmc")

# 執行 ls
files = validator.execute_remote_command("ls -la /uvoice")

# 自訂超時
output = validator.execute_remote_command("long_command", timeout=10.0)
```

---

##### check_emmc_config() -> Dict[str, any]

檢查 `/etc/init.d/emmc` 配置。

**返回字典：**
```python
{
    'has_error': bool,          # 是否有錯誤
    'error_type': str,          # 錯誤類型
    'current_content': str,     # 當前配置內容
    'needs_fix': bool,          # 是否需要修正
    'matched_line': str         # 匹配到的錯誤行
}
```

**範例：**
```python
result = validator.check_emmc_config()

if result['has_error']:
    print(f"錯誤類型: {result['error_type']}")
    print(f"錯誤行: {result['matched_line']}")
```

---

##### fix_emmc_config() -> bool

修正 `/etc/init.d/emmc` 配置。

**返回：**
- `True`：修正成功
- `False`：修正失敗

**流程：**
1. 備份原始檔案為 `.backup`
2. 使用 `sed` 修正配置
3. 驗證修正結果

**範例：**
```python
if validator.fix_emmc_config():
    print("✓ 配置修正成功")
else:
    print("✗ 配置修正失敗")
```

---

##### validate_uart_setup() -> Dict[str, any]

完整的 UART 設定驗證流程。

**返回字典：**
```python
{
    'config_ok': bool,          # 配置是否正確
    'fixed': bool,              # 是否已修正
    'needs_reboot': bool,       # 是否需要重開機
    'reboot_command': str,      # 重開機命令
    'error_message': str,       # 錯誤訊息
    'details': dict             # 詳細資訊
}
```

**範例：**
```python
result = validator.validate_uart_setup()

if result['config_ok']:
    print("✓ 配置正確")
elif result['fixed'] and result['needs_reboot']:
    print(f"⚠️  配置已修正，請執行: {result['reboot_command']}")
else:
    print(f"✗ 錯誤: {result['error_message']}")
```

---

## Robot Framework 整合

### 方式一：透過 SerialLogParser（推薦）

SerialLogParser 在連接時會自動驗證配置。

```robot
*** Settings ***
Library    libraries/multimodal_detection/SerialLogParser.py

*** Test Cases ***
自動驗證配置
    # auto_validate=True（預設），會自動驗證
    ${success}=    初始化串列埠監控器    /dev/ttyUSB0    115200
    Should Be True    ${success}
```

**停用自動驗證：**
```robot
${success}=    初始化串列埠監控器    /dev/ttyUSB0    115200    auto_validate=False
```

---

### 方式二：直接使用 RemoteSystemConfigValidator

```robot
*** Settings ***
Library    libraries/multimodal_detection/RemoteSystemConfigValidator.py

*** Test Cases ***
手動驗證配置
    # 1. 連接遠端設備
    ${success}=    連接遠端設備    /dev/ttyUSB0    115200
    Should Be True    ${success}

    # 2. 檢查配置
    ${result}=    檢查遠端配置
    Log    ${result}

    # 3. 修正配置（如果需要）
    Run Keyword If    ${result['needs_fix']}
    ...    修正遠端配置

    # 4. 斷開連接
    斷開遠端連接
```

---

### 方式三：使用一鍵驗證關鍵字

```robot
*** Settings ***
Library    libraries/multimodal_detection/RemoteSystemConfigValidator.py

*** Test Cases ***
一鍵驗證
    ${result}=    驗證並修正遠端配置

    Should Be True    ${result['config_ok']} or ${result['fixed']}

    Run Keyword If    ${result['needs_reboot']}
    ...    Log    請重開機: ${result['reboot_command']}    WARN
```

---

## 工作流程

### 完整驗證流程圖

```
開始
  ↓
連接 UART 串列埠 (/dev/ttyUSB0 @ 115200)
  ↓
等待遠端設備就緒（1秒）
  ↓
發送換行激活 shell
  ↓
執行: cat /etc/init.d/emmc
  ↓
解析配置內容
  ↓
是否包含正確配置？
  ├─ 是 → [返回 config_ok=True]
  └─ 否 ↓
      使用正規表達式檢測錯誤模式
        ↓
      是否匹配錯誤模式？
        ├─ 否 → [返回 has_error=False]
        └─ 是 ↓
            執行自動修正
              ↓
            1. 備份原始檔案
            2. sed 替換錯誤配置
            3. 驗證修正結果
              ↓
            修正成功？
              ├─ 是 → [返回 fixed=True, needs_reboot=True]
              └─ 否 → [返回 error_message]
                ↓
              斷開 UART 連接
                ↓
              結束
```

### 標記式回應解析機制

RemoteSystemConfigValidator 使用獨特的標記式回應解析（Marker-based Response Parsing）來可靠地執行遠端命令：

```python
def execute_remote_command(self, cmd: str, timeout: Optional[float] = None) -> str:
    # 1. 生成唯一標記
    marker = f"__CMD_END_{int(time.time() * 1000)}__"

    # 2. 發送命令 + 標記
    full_cmd = f"{cmd}; echo '{marker}'\n"
    self.serial_conn.write(full_cmd.encode('utf-8'))

    # 3. 讀取輸出直到找到標記
    while time.time() - start_time < timeout:
        line = self.serial_conn.readline()
        if marker in line:
            break  # 命令執行完成
        output_lines.append(line)

    return '\n'.join(output_lines)
```

**優點：**
- 精確判斷命令執行完成
- 避免超時造成的輸出截斷
- 過濾命令回顯和空行

---

## 錯誤處理

### 常見錯誤與解決方法

#### 1. 串列埠連接失敗

**錯誤訊息：**
```
串列埠連接失敗: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**原因：** 使用者沒有串列埠存取權限

**解決方法：**
```bash
# 加入 dialout 群組
sudo usermod -a -G dialout $USER

# 登出重新登入
# 或立即生效（暫時）
newgrp dialout
```

---

#### 2. 無法讀取配置檔

**錯誤訊息：**
```
無法讀取配置檔: /etc/init.d/emmc
```

**原因：**
- 檔案不存在
- UART 連線中斷
- 命令執行超時

**解決方法：**
```python
# 檢查檔案是否存在
output = validator.execute_remote_command("ls -l /etc/init.d/emmc")
print(output)

# 增加超時時間
validator.command_timeout = 10.0
```

---

#### 3. 配置修正失敗

**錯誤訊息：**
```
配置修正失敗
```

**原因：**
- 檔案權限不足
- sed 命令執行失敗
- 磁碟空間不足

**解決方法：**
```bash
# 手動檢查權限
ls -l /etc/init.d/emmc

# 手動執行修正命令
sed -i 's|/uvoice/start_uvoice\.sh[^&]*&|/uvoice/start_uvoice.sh > /dev/ttyS0 &|g' /etc/init.d/emmc
```

---

#### 4. 標記未找到（命令超時）

**錯誤訊息：**
```
命令執行超時 (5.0s)，可能未完成
```

**原因：**
- 命令執行時間過長
- 遠端設備回應緩慢
- UART 連線不穩定

**解決方法：**
```python
# 增加超時時間
result = validator.execute_remote_command("slow_command", timeout=15.0)

# 或全域設定
validator.command_timeout = 10.0
```

---

## 故障排除

### 診斷步驟

#### 步驟 1：檢查 UART 連接

```bash
# 檢查設備是否存在
ls -l /dev/ttyUSB*

# 使用 tio 測試連接
tio /dev/ttyUSB0 -b 115200

# 測試發送命令
> echo "Hello"
```

#### 步驟 2：手動檢查配置

```bash
# 連接到遠端設備
tio /dev/ttyUSB0 -b 115200

# 檢查配置檔
> cat /etc/init.d/emmc | grep start_uvoice

# 預期輸出
/uvoice/start_uvoice.sh > /dev/ttyS0 &
```

#### 步驟 3：執行 Python 測試腳本

```python
# 執行內建測試腳本
cd libraries/multimodal_detection
python3 RemoteSystemConfigValidator.py
```

#### 步驟 4：檢視詳細日誌

```python
from loguru import logger
logger.remove()  # 移除預設處理器
logger.add(sys.stderr, level="DEBUG")  # 啟用 DEBUG 日誌

validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
result = validator.validate_uart_setup()
```

---

### Debug 模式

啟用詳細日誌輸出：

```python
import sys
from loguru import logger

# 設定 DEBUG 級別日誌
logger.remove()
logger.add(sys.stderr, level="DEBUG",
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

# 執行驗證
validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
result = validator.validate_uart_setup()
```

---

## 最佳實踐

### 1. 使用環境變數

```bash
# .env
UART_PORT=/dev/ttyUSB0
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
port = os.getenv('UART_PORT', '/dev/ttyUSB0')
validator = RemoteSystemConfigValidator(port, 115200)
```

### 2. 整合到測試前置準備

```robot
*** Settings ***
Suite Setup    驗證並準備測試環境

*** Keywords ***
驗證並準備測試環境
    ${result}=    驗證遠端系統配置

    Run Keyword If    ${result['needs_reboot']}
    ...    Fail    遠端設備需要重開機: ${result['reboot_command']}

    Should Be True    ${result['config_ok']}
    ...    遠端配置驗證失敗
```

### 3. 錯誤重試機制

```python
def safe_validate(max_retries=3):
    for attempt in range(max_retries):
        try:
            validator = RemoteSystemConfigValidator()
            result = validator.validate_uart_setup()
            return result
        except Exception as e:
            logger.warning(f"嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
            time.sleep(2)

    raise RuntimeError("驗證失敗，已達最大重試次數")
```

### 4. 集中化配置管理

```python
# config/uart_config.py
from dataclasses import dataclass
import os

@dataclass
class UARTConfig:
    port: str = os.getenv('UART_PORT', '/dev/ttyUSB0')
    baudrate: int = 115200
    command_timeout: float = 5.0

uart_config = UARTConfig()
```

### 5. 單元測試覆蓋

```python
# tests/test_remote_validator.py
import pytest
from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

def test_connect():
    validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
    assert validator.connect()

def test_check_config():
    validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
    validator.connect()
    result = validator.check_emmc_config()
    assert 'has_error' in result
```

---

## 進階用法

### sed 修正策略改進（v1.1.0）⭐

**背景問題：**

在 v1.0.0 中，使用單一 sed 替換命令修正配置：

```bash
sed -i 's|^\\([ \\t]*\\)/uvoice/start_uvoice\\.sh.*$|\\1/uvoice/start_uvoice.sh > /dev/ttyS0 &|' /etc/init.d/emmc
```

**問題：** 正規表達式 `.*$` 在某些情況下無法正確匹配整行，導致產生重複執行的錯誤配置：

```bash
/uvoice/start_uvoice.sh > /dev/ttyS0 	/uvoice/start_uvoice.sh
```

**改進策略（v1.1.0）：**

採用**兩步驟 sed 操作**：

```python
# 步驟 1: 刪除所有包含 start_uvoice.sh 的行
delete_cmd = f"sed -i '/\\/uvoice\\/start_uvoice\\.sh/d' {config_path}"

# 步驟 2: 在 bt_gatt_server 之後插入正確配置
insert_cmd = f"sed -i '/bt_gatt_server/a\\\\\\t{correct_config}' {config_path}"
```

**優點：**
- ✅ 徹底移除所有錯誤配置，避免殘留
- ✅ 精確插入位置，保持縮排
- ✅ 不受原配置格式影響
- ✅ 支援重複執行錯誤修正

**測試結果：**
- ✅ 修正 `no_background` 錯誤
- ✅ 修正 `output_to_null` 錯誤
- ✅ 修正 `no_redirect` 錯誤
- ✅ 修正 `duplicate_execution` 錯誤

---

### 自訂錯誤模式

```python
from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

class CustomValidator(RemoteSystemConfigValidator):
    # 擴展錯誤模式
    WRONG_PATTERNS = RemoteSystemConfigValidator.WRONG_PATTERNS + [
        (r'/uvoice/start_uvoice\.sh.*>&2', 'stderr_redirect'),
    ]
```

### 批次驗證多台設備

```python
devices = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']

for device in devices:
    validator = RemoteSystemConfigValidator(device, 115200)
    result = validator.validate_uart_setup()
    print(f"{device}: {'✓' if result['config_ok'] else '✗'}")
```

---

## 總結

RemoteSystemConfigValidator 提供了完整的遠端配置管理解決方案：

✅ **自動化**：自動檢測並修正配置錯誤
✅ **安全性**：自動備份、不自動重開機
✅ **整合性**：無縫整合到 SerialLogParser
✅ **可靠性**：標記式回應解析、完善錯誤處理
✅ **易用性**：Python API + Robot Framework 關鍵字

---

## 相關文檔

- [UART 日誌檢測完整指南](uart_audio_detection_guide.md)
- [SerialLogParser API 文檔](../libraries/multimodal_detection/SerialLogParser.py)
- [多模態檢測實作摘要](voice_assistant_multimodal_detection_implementation_summary.md)

---

**最後更新：** 2025-11-11
**維護者：** Robot Automation Team
