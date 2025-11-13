# MyCobot Robot Arm Server - 使用說明

## 概述

這是一個強化版的 MyCobot 機器手臂控制伺服器，提供通過網路 Socket 控制機器手臂的功能。

### 主要改進

相較於原始版本，強化版本包含以下改進：

1. **自動重連機制** - 串口斷開時自動嘗試重新連接
2. **增強錯誤處理** - 完善的異常捕獲和恢復機制
3. **執行緒安全** - 使用鎖保護串口操作
4. **詳細日誌** - 改進的日誌系統，包含函數名稱和更多上下文
5. **優雅關閉** - 支援 Ctrl+C 優雅退出
6. **靈活配置** - 命令列參數支援
7. **健康檢查** - 串口健康狀態監控
8. **GPIO 相容性** - 支援非樹莓派環境運行（禁用 GPIO 功能）

## 系統需求

### 硬體

- MyCobot 280 機器手臂（或其他相容型號）
- 運行 Linux 的控制電腦（樹莓派或 NVIDIA Jetson 等）
- USB 轉串口連接線

### 軟體

```bash
# Python 3.8+
python3 --version

# 必要套件
pip install pyserial

# 可選（樹莓派環境）
pip install RPi.GPIO
```

## 安裝

1. 確保已安裝 `pyserial`：

```bash
pip install pyserial
```

2. 將伺服器腳本複製到目標機器：

```bash
scp scripts/robot_arm_server.py user@robot-host:/path/to/server/
```

3. 確認串口設備路徑：

```bash
# 列出所有串口設備
ls -l /dev/tty*

# 常見設備名稱：
# - NVIDIA Jetson: /dev/ttyTHS1
# - 樹莓派: /dev/ttyAMA0, /dev/ttyUSB0
# - 一般 Linux: /dev/ttyUSB0, /dev/ttyACM0
```

## 使用方式

### 基本啟動

使用預設設定啟動伺服器：

```bash
python3 robot_arm_server.py
```

預設參數：
- 自動偵測網路介面 IP
- Port: 9000
- Serial: /dev/ttyTHS1
- Baud Rate: 1000000

### 自訂參數啟動

```bash
# 指定所有參數
python3 robot_arm_server.py \
    --host 192.168.1.100 \
    --port 9000 \
    --serial /dev/ttyUSB0 \
    --baud 1000000 \
    --reconnect-interval 2 \
    --max-reconnect-attempts 5
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--host` | 伺服器 IP 地址 | 自動偵測 |
| `--port` | 伺服器 Port | 9000 |
| `--serial` | 串口設備路徑 | /dev/ttyTHS1 |
| `--baud` | 串口鮑率 | 1000000 |
| `--interface` | 網路介面（用於自動 IP 偵測） | wlan0 |
| `--reconnect-interval` | 重連間隔（秒） | 2 |
| `--max-reconnect-attempts` | 最大重連次數 | 5 |

### 查看幫助

```bash
python3 robot_arm_server.py --help
```

## 啟動範例

### 1. 樹莓派環境

```bash
python3 robot_arm_server.py \
    --serial /dev/ttyAMA0 \
    --interface wlan0
```

### 2. NVIDIA Jetson 環境

```bash
python3 robot_arm_server.py \
    --serial /dev/ttyTHS1 \
    --interface eth0
```

### 3. 一般 Linux（USB 連接）

```bash
python3 robot_arm_server.py \
    --serial /dev/ttyUSB0 \
    --interface eth0
```

### 4. 指定 IP 和 Port

```bash
python3 robot_arm_server.py \
    --host 0.0.0.0 \
    --port 9000 \
    --serial /dev/ttyTHS1
```

## 系統服務配置

建議將伺服器設置為系統服務，開機自動啟動。

### Systemd 服務配置

創建服務檔案 `/etc/systemd/system/robot-arm-server.service`：

```ini
[Unit]
Description=MyCobot Robot Arm Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/robot-arm-server
ExecStart=/usr/bin/python3 /home/your-username/robot-arm-server/robot_arm_server.py \
    --serial /dev/ttyTHS1 \
    --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟用服務：

```bash
# 重新載入 systemd 配置
sudo systemctl daemon-reload

# 啟用服務（開機自動啟動）
sudo systemctl enable robot-arm-server

# 啟動服務
sudo systemctl start robot-arm-server

# 檢查狀態
sudo systemctl status robot-arm-server

# 查看日誌
sudo journalctl -u robot-arm-server -f
```

## 客戶端連接

### Python 客戶端範例

```python
import socket

# 連接到伺服器
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.1.100', 9000))

# 發送命令（範例：獲取角度）
command = bytes([0xFE, 0xFE, 0x02, 0x20, 0xFA])
client.sendall(command)

# 接收回應
response = client.recv(1024)
print(f"Response: {[hex(b) for b in response]}")

# 關閉連接
client.close()
```

### Robot Framework 整合

使用專案中的 `RobotArmKeywords.py`：

```robot
*** Settings ***
Library    libraries/robot_arm_control/RobotArmKeywords.py

*** Test Cases ***
控制機器手臂
    連接到機器手臂    192.168.1.100    9000
    移動到指定位置    ${x}    ${y}    ${z}
    斷開機器手臂連接
```

## 日誌管理

### 日誌檔案位置

伺服器會在執行目錄下生成 `server.log` 檔案。

### 日誌級別

- **DEBUG** - 詳細的命令和回應數據
- **INFO** - 一般操作資訊（連接、斷開、命令執行）
- **WARNING** - 警告訊息（重試、超時）
- **ERROR** - 錯誤訊息（串口錯誤、連接失敗）

### 日誌輪替

日誌檔案配置：
- 最大大小：10 MB
- 備份數量：3 個

### 查看即時日誌

```bash
# 查看最新日誌
tail -f server.log

# 查看最近 100 行
tail -n 100 server.log

# 搜尋錯誤訊息
grep ERROR server.log
```

## 錯誤處理

### 常見錯誤與解決方案

#### 1. 串口權限錯誤

**錯誤訊息：**
```
PermissionError: [Errno 13] Permission denied: '/dev/ttyTHS1'
```

**解決方案：**
```bash
# 方法 1: 將使用者加入 dialout 群組
sudo usermod -a -G dialout $USER
# 登出後重新登入

# 方法 2: 修改串口權限（臨時）
sudo chmod 666 /dev/ttyTHS1
```

#### 2. 串口設備不存在

**錯誤訊息：**
```
FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyTHS1'
```

**解決方案：**
```bash
# 查找實際的串口設備
ls -l /dev/tty*

# 使用正確的設備路徑
python3 robot_arm_server.py --serial /dev/ttyUSB0
```

#### 3. 串口被占用

**錯誤訊息：**
```
serial.serialutil.SerialException: [Errno 16] Device or resource busy
```

**解決方案：**
```bash
# 查找占用串口的進程
lsof /dev/ttyTHS1

# 終止占用的進程
kill -9 <PID>
```

#### 4. 網路介面不存在

**錯誤訊息：**
```
Warning: Could not find network interface, using localhost
```

**解決方案：**
```bash
# 查看可用的網路介面
ip addr show

# 指定正確的介面
python3 robot_arm_server.py --interface eth0

# 或直接指定 IP
python3 robot_arm_server.py --host 192.168.1.100
```

#### 5. 串口連接失敗後自動重連

伺服器會自動處理串口斷開：

1. 偵測到串口錯誤
2. 記錄錯誤日誌
3. 自動嘗試重新連接（預設最多 5 次）
4. 每次重連間隔 2 秒
5. 重連成功後恢復正常運作

**日誌範例：**
```
2025-11-06 10:48:34,485 - ERROR - [read] - Serial read error: device disconnected
2025-11-06 10:48:34,486 - WARNING - [_reconnect_serial] - Attempting to reconnect serial port (attempt 1/5)
2025-11-06 10:48:36,488 - INFO - [_init_serial] - Serial port /dev/ttyTHS1 opened successfully
2025-11-06 10:48:36,488 - INFO - [_reconnect_serial] - Serial port reconnected successfully
```

## 效能調整

### 1. 調整讀取超時

修改 `_init_serial()` 中的 timeout 參數：

```python
self.mc = serial.Serial(self.serial_num, self.baud, timeout=0.2)  # 增加到 200ms
```

### 2. 調整重連參數

```bash
python3 robot_arm_server.py \
    --reconnect-interval 1 \      # 減少重連間隔
    --max-reconnect-attempts 10   # 增加重連次數
```

### 3. Socket 超時設定

在 `connect()` 方法中調整：

```python
self.s.settimeout(1.0)    # accept 超時
conn.settimeout(30.0)     # recv 超時
```

## 安全注意事項

1. **網路安全**
   - 建議在內網使用
   - 可配置防火牆限制連接來源
   - 使用 VPN 進行遠端訪問

2. **權限管理**
   - 避免使用 root 執行
   - 使用專用使用者帳號
   - 限制串口設備權限

3. **錯誤處理**
   - 客戶端應處理連接失敗
   - 實作命令重試機制
   - 監控伺服器狀態

## 測試

### 1. 基本連接測試

```bash
# 使用 telnet 測試連接
telnet 192.168.1.100 9000

# 使用 nc (netcat)
nc 192.168.1.100 9000
```

### 2. 串口迴路測試

```python
# test_serial_loopback.py
import serial
import time

ser = serial.Serial('/dev/ttyTHS1', 1000000, timeout=0.1)
print(f"Serial port opened: {ser.is_open}")

# 嘗試讀寫
ser.write(b'\xFE\xFE\x02\x20\xFA')
time.sleep(0.1)
response = ser.read(100)
print(f"Response: {response.hex()}")

ser.close()
```

### 3. 壓力測試

```python
# stress_test.py
import socket
import time
import threading

def send_commands(host, port, num_commands):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    for i in range(num_commands):
        command = bytes([0xFE, 0xFE, 0x02, 0x20, 0xFA])
        client.sendall(command)
        response = client.recv(1024)
        print(f"Command {i+1}: OK")
        time.sleep(0.1)

    client.close()

# 執行測試
send_commands('192.168.1.100', 9000, 100)
```

## 疑難排解

### 除錯模式

設置日誌級別為 DEBUG：

```python
# 在 get_logger() 函數中修改
logger.setLevel(logging.DEBUG)
```

### 查看詳細錯誤

```bash
# 以前景模式執行，查看所有輸出
python3 robot_arm_server.py 2>&1 | tee server_debug.log
```

### 串口診斷

```bash
# 檢查串口設備資訊
udevadm info --name=/dev/ttyTHS1

# 監控串口通訊（需要額外工具）
sudo apt-get install interceptty
interceptty -s 'ispeed 1000000 ospeed 1000000' /dev/ttyTHS1 /tmp/ttyV0
```

## 更新日誌

### v2.0 (2025-11-06) - 強化版

- ✅ 新增自動重連機制
- ✅ 增強錯誤處理
- ✅ 執行緒安全保護
- ✅ 改進日誌系統
- ✅ 命令列參數支援
- ✅ 優雅關閉機制
- ✅ GPIO 相容性改進

### v1.0 - 原始版本

- 基本 Socket 伺服器功能
- 串口通訊
- GPIO 控制

## 相關文件

- [機器手臂控制設計文檔](robot_arm_socket_control_design.md)
- [按鈕配置指南](../libraries/robot_arm_control/BUTTON_SETUP_GUIDE.md)
- [Robot Framework 關鍵字](../libraries/robot_arm_control/README.md)

## 支援

如遇到問題，請：

1. 檢查日誌檔案 `server.log`
2. 確認串口設備路徑和權限
3. 驗證網路連接
4. 查看本文件的「錯誤處理」章節

## 授權

本專案遵循專案整體授權協議。
