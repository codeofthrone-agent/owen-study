# Robot Arm Control Library

**MyCobot 280 機器手臂控制庫 - Socket 連接方式 (BDD 風格 v4.0.0)**

本模組提供基於 TCP/IP Socket 的 MyCobot 280 機器手臂控制功能，採用 BDD (Gherkin) 風格關鍵字，用於 Robot Framework 自動化測試中按壓實體面板按鈕，並整合本機化視覺檢測系統。

---

## 📋 目錄

- [專案概述](#專案概述)
- [核心功能](#核心功能)
- [系統架構](#系統架構)
- [安裝與設置](#安裝與設置)
- [配置說明](#配置說明)
- [使用指南](#使用指南)
- [Robot Framework 關鍵字](#robot-framework-關鍵字)
- [程式模組說明](#程式模組說明)
- [測試範例](#測試範例)
- [故障排除](#故障排除)
- [開發指南](#開發指南)

---

## 專案概述

### 目標

建立基於 TCP/IP Socket 的 MyCobot 280 機器手臂控制系統，採用 BDD (Behavior-Driven Development) 風格的 Gherkin 語法，透過 Robot Framework 提供直觀易用的關鍵字介面，用於自動化測試中按壓實體面板按鈕。

### 特色

- ✅ **BDD 風格關鍵字**: 採用 Gherkin 語法（Given-When-Then-And），提供 32+ 個完整測試關鍵字
- ✅ **Socket 連接**: 基於 TCP/IP 網路控制，無需 USB 連接
- ✅ **YAML 配置管理**: 彈性的按鈕位置配置，易於調整和維護
- ✅ **中文關鍵字**: 符合專案規範，所有關鍵字使用中文命名
- ✅ **本機化視覺檢測** ⭐ NEW (v4.0.0):
  - 多環境支援（台北實驗室 / 桃園實驗室 / RV Car）
  - 多色彩檢測（藍/白/紅/綠/黃/橙/紫/關閉）
  - 多級亮度檢測（0-100%，11 級）
  - 雙影像源（RTSP / Socket）
- ✅ **完整的錯誤處理**: 連接檢查、移動超時、電源管理等
- ✅ **支援長按功能**: 可自定義按壓時間（如 Retract/Extend 長按 7 秒）
- ✅ **雙層架構**: 與 Voice Control 模式一致，直接使用 Python Library 中的 @keyword

### 定位

**重要概念**: MyCobot 280 在本專案中定位為**測試工具**（而非被測對象），用於模擬人工按壓面板按鈕的動作。

---

## 核心功能

### 1. 連接管理

- Socket 連接/斷開
- 電源管理（開啟/關閉伺服馬達）
- 連接狀態檢查
- 回到初始位置

### 2. 按鈕控制與視覺檢測

#### BDD 風格關鍵字（v4.0.0: 30+ 個）

**Given 關鍵字（5個）**:
- 機器手臂已正確連接到控制面板
- 控制面板電源狀態為 "指定狀態"
- 機器手臂系統處於待命狀態
- ⭐ 測試環境設定為 "環境名稱" (NEW v4.0.0)
- ⭐ 面板類型設定為 "面板型號" (NEW v4.0.0)

**When 關鍵字（12個）**:
- 用戶透過機器手臂開啟第 "X" 號燈光
- 用戶透過機器手臂切換藍牙連接
- 用戶透過機器手臂啟動 "設備名" 設備
- 用戶透過機器手臂長按 "按鈕類型" 按鈕 "秒數" 秒
- 用戶檢測第 "按鈕ID" 按鈕的燈光狀態
- 用戶檢測多個按鈕的燈光狀態
- 用戶等待按鈕 "按鈕ID" 變為 "顏色" 色
- 用戶連接到機器手臂
- 用戶中斷與機器手臂的連接
- 用戶按壓第 "按鈕ID" 按鈕
- ⭐ 用戶檢測面板按鈕 "按鈕ID" 的顏色 (NEW v4.0.0)
- ⭐ 用戶檢測實體燈光亮度 "燈光ID" (NEW v4.0.0)

**Then 關鍵字（7個）**:
- 機器手臂操作應該成功完成
- 控制面板應該顯示 "預期狀態" 狀態
- 按鈕燈光應該為 "顏色" 色
- 按鈕燈光應該為 "狀態" 狀態
- 上一步操作應該成功
- ⭐ 面板按鈕顏色應該為 "顏色" (NEW v4.0.0)
- ⭐ 實體燈光亮度應該為 "級別" % (NEW v4.0.0)

**And 關鍵字（3個）**:
- 機器手臂應該返回待命位置
- 系統應該記錄完整操作歷程
- 暫存檔案應該正確清理

#### 傳統關鍵字（5個）

**連接管理**:
- 連接機器手臂
- 斷開機器手臂連接  
- 回到初始位置

**Legacy 按鈕操作**:
- 點擊 [按鈕名] 按鈕（向後相容）
- 長按 [按鈕名] 按鈕（向後相容）

### 3. 動作控制

- 發送角度指令
- 等待移動完成
- 讀取當前角度
- 移動狀態檢查

### 4. 本機化視覺檢測 ⭐ NEW (v4.0.0)

#### 4.1 多環境支援

支援 3 個獨立測試環境，每個環境有專屬配置：

| 環境 | 影像源 | 面板類型 | 說明 |
|------|--------|----------|------|
| **taipei_lab** | RTSP | 3510a, 3611a, 3611c | 台北實驗室，使用 IP Camera |
| **taoyuan_lab** | Socket | 3510a, 3611a | 桃園實驗室，使用機器手臂 USB Camera |
| **rv_car** | Socket | 3611c | RV Car 車載環境 |

#### 4.2 多色彩檢測

支援 7+ 種顏色的 LED 按鈕檢測：
- **藍色 (blue)**: HSV 色彩空間檢測
- **白色 (white)**: 高飽和度判定
- **紅色 (red)**: 處理色調環繞問題
- **綠色 (green)**
- **黃色 (yellow)**
- **橙色 (orange)**
- **紫色 (purple)**
- **關閉 (off)**: 低亮度判定

**特性**:
- 多幀平均（5 frames）+ 暖機幀（20 frames）解決 LED PWM 同步問題
- ROI 精確定位
- 信心度評分
- 除錯影像自動儲存

#### 4.3 多級亮度檢測

支援 11 級實體燈光亮度檢測：
- **級別**: 0%, 10%, 20%, ..., 100%
- **誤差容忍**: ±10%
- **應用**: 天花板燈、桌燈、車燈等實體照明

**特性**:
- 原始亮度值 (0-255)
- 燈光狀態判定 (on/off)
- 信心度計算

#### 4.4 雙影像源

**RTSP 影像源**:
- 使用 IP Camera 進行遠端視覺檢測
- 適用於固定場景
- OpenCV + FFmpeg 支援

**Socket 影像源**:
- 使用機器手臂上的 USB Camera (/dev/video0)
- 透過 Socket 協定請求影像
- Base64 編碼傳輸
- 伺服器端多幀平均

---

## 系統架構

### 目錄結構

```
libraries/robot_arm_control/
├── __init__.py                      # 套件初始化
├── README.md                        # 本文件
├── button_config_loader.py          # YAML 配置載入器
├── mycobot_socket_controller.py     # Socket 控制核心
├── RobotArmKeywords.py              # Robot Framework 關鍵字庫 (v4.0.0)
├── local_vision_analyzer.py         # ⭐ 本機視覺分析器 (NEW v4.0.0)
├── image_source_manager.py          # ⭐ 影像源管理器 (NEW v4.0.0)
├── image_sources/                   # ⭐ 影像源模組 (NEW v4.0.0)
│   ├── __init__.py
│   ├── rtsp_source.py               # RTSP 影像源
│   └── socket_image_source.py       # Socket 影像源
└── tests/                           # 單元測試
    ├── conftest.py
    ├── test_local_vision_analyzer.py
    └── test_image_source_manager.py

config/robot_arm/
├── button_positions.yaml            # 按鈕位置配置（舊版）
├── environment_config.py            # ⭐ 環境配置管理 (NEW v4.0.0)
├── taipei_lab_buttons.yaml          # ⭐ 台北實驗室配置 (NEW v4.0.0)
├── taoyuan_lab_buttons.yaml         # ⭐ 桃園實驗室配置 (NEW v4.0.0)
└── rv_car_buttons.yaml              # ⭐ RV Car 配置 (NEW v4.0.0)

tests/robot_arm/
├── basic_button_test.robot          # 基礎測試案例
└── (更多測試案例...)

tests/
└── test_environment_config.py       # ⭐ 環境配置測試 (NEW v4.0.0)

docs/
├── robot_arm_socket_control_design.md
└── vision_detection_local_migration_plan.md  # ⭐ 視覺檢測遷移計畫
```

### 技術棧

| 組件 | 版本/說明 |
|------|----------|
| **通訊協定** | TCP/IP Socket |
| **控制庫** | pymycobot (官方 Python SDK) |
| **配置格式** | YAML (PyYAML) |
| **測試框架** | Robot Framework 7.3.1+ |
| **視覺處理** ⭐ | OpenCV 4.x (cv2) |
| **影像源** ⭐ | RTSP (FFmpeg) / Socket (Base64) |
| **色彩空間** ⭐ | HSV (Hue-Saturation-Value) |
| **測試工具** ⭐ | pytest 9.0.0 |
| **Python 版本** | 3.12 |
| **日誌系統** | loguru |

### 模組關聯圖

```
Robot Framework 測試
        ↓
RobotArmKeywords.py (關鍵字庫)
        ↓
MyCobotSocketController (Socket 控制器)
        ↓
pymycobot.MyCobot280Socket (官方 SDK)
        ↓
MyCobot 280 硬體 (透過 WiFi)
```

```
配置文件載入流程:
button_positions.yaml
        ↓
ButtonConfigLoader (配置載入器)
        ↓
RobotArmKeywords (讀取按鈕配置)
```

---

## 安裝與設置

### 1. 安裝 Python 套件

```bash
# 進入專案根目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 安裝必要套件
pipenv install pymycobot pyyaml loguru
```

### 2. MyCobot 280 硬體設置

#### 方法 A: 使用 MyCobot 280 Jetson Nano (推薦)

1. **在 MyCobot 280 Jetson Nano 上啟動 Socket Server:**

   ```bash
   # SSH 連接到 MyCobot 280 Jetson Nano
   ssh user@<mycobot_ip>

   # 啟動 Server_280.py
   cd ~/mycobot_scripts
   python3 Server_280.py
   ```

2. **設定開機自動啟動** (建議):

   ```bash
   # 創建 systemd 服務
   sudo nano /etc/systemd/system/mycobot-server.service
   ```

   服務文件內容:
   ```ini
   [Unit]
   Description=MyCobot 280 Socket Server
   After=network.target

   [Service]
   Type=simple
   User=user
   WorkingDirectory=/home/user/mycobot_scripts
   ExecStart=/usr/bin/python3 /home/user/mycobot_scripts/Server_280.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   啟用服務:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable mycobot-server.service
   sudo systemctl start mycobot-server.service

   # 檢查狀態
   sudo systemctl status mycobot-server.service
   ```

#### 方法 B: 使用 Jetson Nano

如果 MyCobot 280 直接連接到 Jetson Nano（透過 USB 串口），可以使用串口模式（本模組目前僅支援 Socket 模式，串口模式為未來擴展）。

### 3. 網路設置

確保控制端（執行 Robot Framework 的電腦）與 MyCobot 280 在同一網路：

```bash
# 測試網路連接
ping <mycobot_ip>

# 測試 Socket 端口
telnet <mycobot_ip> 9000
```

### 4. 配置 IP 地址

編輯配置文件 `config/robot_arm/button_positions.yaml`:

```yaml
connection:
  socket:
    host: "10.42.0.180"  # 修改為您的 MyCobot 280 IP
    port: 9000
```

---

## 配置說明

### 配置文件結構

配置文件位於 [config/robot_arm/button_positions.yaml](../../config/robot_arm/button_positions.yaml)

#### 1. 連接配置

```yaml
connection:
  socket:
    host: "10.42.0.180"  # MyCobot 280 IP 地址
    port: 9000           # Socket 端口（預設 9000）

  serial:                # 串口配置（備用，未來擴展）
    port: "/dev/ttyTHS1"
    baudrate: 1000000
```

#### 2. 全局預設值

```yaml
defaults:
  speed: 100            # 移動速度 (1-100)
  press_duration: 1.0   # 按壓保持時間（秒）
  lift_duration: 0.1    # 抬起後等待時間（秒）
  count: 1              # 按壓次數
```

#### 3. 按鈕定義

每個按鈕包含以下參數：

```yaml
buttons:
  bluetooth:
    name: "Bluetooth 按鈕"        # 顯示名稱
    description: "藍牙控制按鈕"    # 功能說明
    down_angles: [16.5, -51, -130, 73.7, 0, 0]  # 按下位置（6 軸角度）
    up_angles: [16.5, -13, -130, 73.7, 0, 0]    # 抬起位置（6 軸角度）
    speed: 100                    # 移動速度
    count: 2                      # 按壓次數
    lift_duration: 0.1            # 抬起等待時間
    press_duration: 1.0           # 按壓時間
```

**參數說明:**

| 參數 | 類型 | 說明 | 範圍/格式 |
|------|------|------|----------|
| `name` | 字串 | 按鈕顯示名稱 | 任意字串 |
| `description` | 字串 | 按鈕功能說明 | 任意字串 |
| `down_angles` | 列表 | 按下位置的 6 軸角度 | `[J1, J2, J3, J4, J5, J6]`（單位：度） |
| `up_angles` | 列表 | 抬起位置的 6 軸角度 | `[J1, J2, J3, J4, J5, J6]`（單位：度） |
| `speed` | 整數 | 移動速度 | 1-100 |
| `count` | 整數 | 按壓次數 | ≥ 1 |
| `press_duration` | 浮點數 | 按壓保持時間（秒） | > 0 |
| `lift_duration` | 浮點數 | 抬起後等待時間（秒） | ≥ 0 |

### 如何修改按鈕位置

#### 步驟 1: 手動示教

使用 MyCobot 280 的示教模式或手動控制工具，移動機器手臂到正確位置：

1. 移動到按鈕**上方位置**（抬起位置）
2. 記錄當前角度 → `up_angles`
3. 移動到**按下按鈕位置**（下壓位置）
4. 記錄當前角度 → `down_angles`

#### 步驟 2: 讀取當前角度

使用以下 Python 腳本讀取角度：

```python
from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController

# 連接機器手臂
controller = MyCobotSocketController("10.42.0.180", 9000)
controller.connect()

# 讀取當前角度
angles = controller.get_angles()
print(f"當前角度: {angles}")

controller.disconnect()
```

#### 步驟 3: 更新配置文件

將讀取的角度更新到 `button_positions.yaml`：

```yaml
buttons:
  my_new_button:
    name: "新按鈕"
    description: "新增的按鈕"
    down_angles: [10.5, -55, -120, 70.0, 0, 0]  # 從步驟 2 獲得
    up_angles: [10.5, -20, -120, 70.0, 0, 0]    # 從步驟 2 獲得
    speed: 100
    press_duration: 1.0
```

#### 步驟 4: 測試新按鈕

```bash
# 執行 dry run 驗證語法
robot --dryrun tests/robot_arm/basic_button_test.robot

# 實際測試（小心！確認機器手臂周圍無障礙物）
robot tests/robot_arm/basic_button_test.robot
```

---

## 使用指南

### 基本使用流程

```robot
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

*** Test Cases ***
測試藍牙按鈕
    # 1. 連接機器手臂
    連接機器手臂

    # 2. 按壓按鈕
    點擊藍牙按鈕

    # 3. 回到初始位置
    回到初始位置

    # 4. 斷開連接
    斷開機器手臂連接
```

### Python 直接使用

```python
from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords

# 初始化
robot_arm = RobotArmKeywords()

# 連接（使用配置文件中的 IP）
robot_arm.connect_robot_arm()

# 點擊按鈕
robot_arm.click_bluetooth_button()
robot_arm.click_light1_button()

# 長按按鈕
robot_arm.long_press_retract_button(秒數=10)

# 回到初始位置並斷開
robot_arm.go_to_home_position()
robot_arm.disconnect_robot_arm()
```

---

## Robot Framework 關鍵字

### BDD 風格關鍵字（推薦使用）

本模組採用雙層架構設計，直接使用 Python Library 中定義的 BDD 關鍵字，與 Voice Control 模式一致。

#### Given 關鍵字（前置條件驗證）

#### 1. Given 機器手臂已正確連接到控制面板

```robot
Given 機器手臂已正確連接到控制面板    [host]    [port]    [speed]
```

**說明**: 確認機器手臂已正確連接到控制面板並處於可操作狀態。

**參數**:
- `host` (選填): MyCobot 280 IP 地址
- `port` (選填): Socket 端口  
- `speed` (選填): 移動速度

**範例**:
```robot
# 使用預設配置
Given 機器手臂已正確連接到控制面板

# 指定連接參數
Given 機器手臂已正確連接到控制面板    192.168.1.100    9000    30
```

#### 2. Given 控制面板電源狀態為 "${power_state}"

```robot
Given 控制面板電源狀態為 "${power_state}"
```

**說明**: 驗證控制面板電源狀態符合預期。

**參數**:
- `power_state`: 電源狀態（"開啟" 或 "關閉"）

**範例**:
```robot
Given 控制面板電源狀態為 "開啟"
Given 控制面板電源狀態為 "關閉"
```

#### 3. Given 機器手臂系統處於待命狀態

```robot
Given 機器手臂系統處於待命狀態
```

**說明**: 確認機器手臂系統處於待命狀態，準備執行操作。

**範例**:
```robot
Given 機器手臂系統處於待命狀態
```

#### When 關鍵字（執行動作）

#### 1. When 用戶透過機器手臂開啟第 "${light_number}" 號燈光

```robot
When 用戶透過機器手臂開啟第 "${light_number}" 號燈光
```

**說明**: 透過機器手臂按壓指定編號的燈光按鈕。

**參數**:
- `light_number`: 燈光編號（1-8）

**範例**:
```robot
When 用戶透過機器手臂開啟第 "1" 號燈光
When 用戶透過機器手臂開啟第 "5" 號燈光
```

#### 2. When 用戶透過機器手臂切換藍牙連接

```robot
When 用戶透過機器手臂切換藍牙連接
```

**說明**: 透過機器手臂按壓藍牙按鈕切換藍牙連接狀態。

**範例**:
```robot
When 用戶透過機器手臂切換藍牙連接
```

#### 3. When 用戶透過機器手臂啟動 "${device_name}" 設備

```robot
When 用戶透過機器手臂啟動 "${device_name}" 設備
```

**說明**: 透過機器手臂按壓指定設備的控制按鈕。

**參數**:
- `device_name`: 設備名稱（熱水器、空調、瓦斯等）

**範例**:
```robot
When 用戶透過機器手臂啟動 "熱水器" 設備
When 用戶透過機器手臂啟動 "空調" 設備
```

#### 4. When 用戶透過機器手臂長按 "${button_type}" 按鈕 "${seconds}" 秒

```robot
When 用戶透過機器手臂長按 "${button_type}" 按鈕 "${seconds}" 秒
```

**說明**: 透過機器手臂長按指定按鈕指定時間。

**參數**:
- `button_type`: 按鈕類型（Retract、Extend 等）
- `seconds`: 按壓秒數

**範例**:
```robot
When 用戶透過機器手臂長按 "Retract" 按鈕 "7" 秒
When 用戶透過機器手臂長按 "Extend" 按鈕 "10" 秒
```

#### Then 關鍵字（結果驗證）

#### 1. Then 機器手臂操作應該成功完成

```robot
Then 機器手臂操作應該成功完成
```

**說明**: 驗證上一步機器手臂操作成功完成。

**範例**:
```robot
Then 機器手臂操作應該成功完成
```

#### 2. Then 控制面板應該顯示 "${expected_state}" 狀態

```robot
Then 控制面板應該顯示 "${expected_state}" 狀態
```

**說明**: 驗證控制面板顯示預期的狀態。

**參數**:
- `expected_state`: 預期狀態

**範例**:
```robot
Then 控制面板應該顯示 "燈光開啟" 狀態
Then 控制面板應該顯示 "藍牙連接" 狀態
```

#### And 關鍵字（附加驗證）

#### 1. And 機器手臂應該返回待命位置

```robot
And 機器手臂應該返回待命位置
```

**說明**: 確認機器手臂已返回待命位置。

**範例**:
```robot
And 機器手臂應該返回待命位置
```

#### 2. And 系統應該記錄完整操作歷程

```robot
And 系統應該記錄完整操作歷程
```

**說明**: 驗證系統已記錄完整的操作歷程。

**範例**:
```robot
And 系統應該記錄完整操作歷程
```

---

### 傳統關鍵字（向後相容）

### 傳統關鍵字（向後相容）

#### 連接管理關鍵字（3個）

#### 1. 連接機器手臂

```robot
連接機器手臂    [host]    [port]
```

**說明**: 連接到機器手臂。如果不提供參數，則從配置文件讀取。

**參數**:
- `host` (選填): MyCobot 280 IP 地址
- `port` (選填): Socket 端口（預設 9000）

**範例**:
```robot
# 使用配置文件中的設定
連接機器手臂

# 指定 IP 地址
連接機器手臂    192.168.1.100

# 指定 IP 和端口
連接機器手臂    192.168.1.100    9000
```

#### 2. 斷開機器手臂連接

```robot
斷開機器手臂連接
```

**說明**: 斷開與機器手臂的連接。

**範例**:
```robot
斷開機器手臂連接
```

#### 3. 回到初始位置

```robot
回到初始位置    [speed]
```

**說明**: 移動機器手臂到初始位置 `[0, 0, 0, 0, 0, 0]`。

**參數**:
- `speed` (選填): 移動速度 (1-100)，預設 30

**範例**:
```robot
# 使用預設速度 30
回到初始位置

# 使用速度 50
回到初始位置    50
```

---

### 點擊按鈕關鍵字（18個）

所有點擊按鈕關鍵字使用方式相同，無需參數。

#### 藍牙與控制（4個）

```robot
點擊藍牙按鈕
點擊AUX1按鈕
點擊AUX2按鈕
點擊Select按鈕
```

#### 燈光控制（8個）

```robot
點擊Light1按鈕
點擊Light2按鈕
點擊Light3按鈕
點擊Light4按鈕
點擊Light5按鈕
點擊Light6按鈕
點擊Light7按鈕
點擊Light8按鈕
```

#### 電器控制（5個）

```robot
點擊TankerHeater按鈕    # 水箱加熱器
點擊Gas按鈕             # 瓦斯
點擊WaterPump按鈕       # 水泵
點擊WaterHeater按鈕     # 熱水器
點擊HVAC按鈕            # 空調
```

#### 門鎖（1個）

```robot
點擊DoorLock按鈕
```

---

### 長按按鈕關鍵字（2個）

#### 1. 長按Retract按鈕

```robot
長按Retract按鈕    [秒數]
```

**說明**: 長按 Retract（縮回）按鈕。

**參數**:
- `秒數` (選填): 按壓時間（秒），預設 7 秒

**範例**:
```robot
# 使用預設 7 秒
長按Retract按鈕

# 自定義 10 秒
長按Retract按鈕    10

# 使用命名參數
長按Retract按鈕    秒數=15
```

#### 2. 長按Extend按鈕

```robot
長按Extend按鈕    [秒數]
```

**說明**: 長按 Extend（伸展）按鈕。

**參數**:
- `秒數` (選填): 按壓時間（秒），預設 7 秒

**範例**:
```robot
# 使用預設 7 秒
長按Extend按鈕

# 自定義 10 秒
長按Extend按鈕    10
```

---

## 程式模組說明

### 1. button_config_loader.py

**功能**: 從 YAML 配置文件載入和管理按鈕位置配置。

**主要類別**: `ButtonConfigLoader`

**主要方法**:

```python
class ButtonConfigLoader:
    def __init__(self, config_path: Optional[str] = None)
    """初始化配置載入器，如果 config_path 為 None，使用預設路徑"""

    def get_button_config(self, button_id: str) -> Dict
    """獲取指定按鈕的完整配置（包含角度、速度等）"""

    def get_socket_config(self) -> Dict
    """獲取 Socket 連接配置（host 和 port）"""

    def list_all_buttons(self) -> List[str]
    """列出所有可用的按鈕 ID"""

    def get_button_info(self, button_id: str) -> Dict
    """獲取按鈕的基本信息（不包含角度數據）"""

    def is_long_press_button(self, button_id: str) -> bool
    """判斷按鈕是否為長按按鈕（press_duration >= 5 秒）"""
```

**使用範例**:

```python
from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader

loader = ButtonConfigLoader()

# 列出所有按鈕
buttons = loader.list_all_buttons()
print(f"可用按鈕: {buttons}")

# 獲取藍牙按鈕配置
config = loader.get_button_config('bluetooth')
print(f"按下角度: {config['down_angles']}")
print(f"抬起角度: {config['up_angles']}")

# 獲取連接配置
socket_config = loader.get_socket_config()
print(f"IP: {socket_config['host']}, Port: {socket_config['port']}")
```

---

### 2. mycobot_socket_controller.py

**功能**: 基於 pymycobot 的 TCP/IP Socket 連接控制機器手臂。

**主要類別**: `MyCobotSocketController`

**主要方法**:

```python
class MyCobotSocketController:
    def __init__(self, host: str, port: int = 9000, timeout: float = 10.0)
    """初始化 Socket 控制器"""

    # 連接管理
    def connect(self) -> bool
    """連接到機器手臂"""

    def disconnect(self) -> None
    """斷開連接"""

    def is_connected(self) -> bool
    """檢查連接狀態"""

    # 運動控制
    def send_angles(self, angles: List[float], speed: int) -> bool
    """發送角度指令"""

    def get_angles(self) -> List[float]
    """讀取當前關節角度"""

    def is_moving(self) -> bool
    """檢查是否正在移動"""

    def wait_for_movement(self, timeout: float = 30.0, check_interval: float = 0.1) -> bool
    """等待移動完成"""

    def go_to_home(self, speed: int = 30) -> bool
    """移動到初始位置 [0, 0, 0, 0, 0, 0]"""

    # 電源管理
    def power_on(self) -> bool
    """開啟伺服馬達電源"""

    def power_off(self) -> bool
    """關閉伺服馬達電源"""

    def is_power_on(self) -> bool
    """檢查電源狀態"""
```

**使用範例**:

```python
from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController

# 創建控制器
controller = MyCobotSocketController("10.42.0.180", 9000)

# 連接
controller.connect()

# 檢查電源
if not controller.is_power_on():
    controller.power_on()

# 發送角度指令
controller.send_angles([0, 0, 0, 0, 0, 0], 50)
controller.wait_for_movement()

# 讀取當前角度
angles = controller.get_angles()
print(f"當前角度: {angles}")

# 斷開連接
controller.disconnect()
```

---

### 3. RobotArmKeywords.py

**功能**: 提供 Robot Framework 關鍵字介面。

**主要類別**: `RobotArmKeywords`

**架構**:

```python
class RobotArmKeywords:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self, config_path: Optional[str] = None)
    """初始化關鍵字庫"""

    # ========== 連接管理關鍵字 ==========
    @keyword("連接機器手臂")
    def connect_robot_arm(self, host: Optional[str] = None, port: Optional[int] = None)

    @keyword("斷開機器手臂連接")
    def disconnect_robot_arm(self)

    @keyword("回到初始位置")
    def go_to_home_position(self, speed: int = 30)

    # ========== 點擊按鈕關鍵字（18個）==========
    @keyword("點擊藍牙按鈕")
    def click_bluetooth_button(self)

    @keyword("點擊Light1按鈕")
    def click_light1_button(self)
    # ... 其他 16 個點擊按鈕關鍵字

    # ========== 長按按鈕關鍵字（2個）==========
    @keyword("長按Retract按鈕")
    def long_press_retract_button(self, 秒數: int = 7)

    @keyword("長按Extend按鈕")
    def long_press_extend_button(self, 秒數: int = 7)

    # ========== 內部輔助方法 ==========
    def _ensure_connected(self)
    """確保機器手臂已連接"""

    def _press_button(self, button_id: str, custom_duration: Optional[float] = None)
    """通用按壓按鈕邏輯"""
```

**關鍵字統計**:
- BDD 關鍵字: 21 個 (Given 3 + When 10 + Then 5 + And 3)
- 傳統關鍵字: 5 個 (連接管理 3 + Legacy 按鈕操作 2)
- **總計: 26 個關鍵字**

---

## 測試範例

### 範例 1: BDD 風格完整測試（推薦）

```robot
*** Settings ***
Documentation    機器手臂控制 - BDD 風格測試案例
Library          libraries.robot_arm_control.RobotArmKeywords

Suite Setup      連接機器手臂
Suite Teardown   清理資源

*** Test Cases ***
Scenario: 測試機器手臂開啟第 1 號燈光
    [Documentation]    驗證機器手臂能夠成功按壓 Light1 按鈕並開啟燈光
    [Tags]    robot_arm    light_control    smoke    bdd

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂開啟第 "1" 號燈光

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "燈光開啟" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程

Scenario: 測試藍牙連接切換
    [Documentation]    驗證機器手臂能夠切換藍牙連接狀態
    [Tags]    robot_arm    bluetooth    bdd

    Given 機器手臂已正確連接到控制面板
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂切換藍牙連接

    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置

Scenario: 測試長按按鈕操作
    [Documentation]    驗證機器手臂長按按鈕功能
    [Tags]    robot_arm    long_press    bdd

    Given 機器手臂已正確連接到控制面板
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂長按 "Retract" 按鈕 "7" 秒

    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置

*** Keywords ***
清理資源
    回到初始位置
    斷開機器手臂連接
```

### 範例 2: 傳統風格測試（向後相容）

```robot
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

Suite Setup      連接機器手臂
Suite Teardown   清理資源

*** Test Cases ***
測試藍牙按鈕
    [Documentation]    測試藍牙按鈕點擊功能
    [Tags]    bluetooth    smoke

    點擊藍牙按鈕

測試燈光控制
    [Documentation]    測試所有燈光按鈕
    [Tags]    lights

    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕
    點擊Light4按鈕
    點擊Light5按鈕
    點擊Light6按鈕
    點擊Light7按鈕
    點擊Light8按鈕

*** Keywords ***
清理資源
    回到初始位置
    斷開機器手臂連接
```

### 範例 2: 長按測試

```robot
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

*** Test Cases ***
測試長按功能
    [Documentation]    測試 Retract 和 Extend 長按按鈕
    [Tags]    long_press

    連接機器手臂

    # 使用預設時間（7 秒）
    長按Retract按鈕

    # 自定義時間（10 秒）
    長按Extend按鈕    10

    回到初始位置
    斷開機器手臂連接
```

### 範例 3: 完整測試流程

完整的測試範例請參考 [tests/robot_arm/basic_button_test.robot](../../tests/robot_arm/basic_button_test.robot)

執行測試:

```bash
# 執行所有測試
robot tests/robot_arm/basic_button_test.robot

# 執行特定標籤的測試
robot --include smoke tests/robot_arm/basic_button_test.robot

# 產生詳細報告
robot --outputdir results/robot_arm --loglevel DEBUG tests/robot_arm/
```

---

## 故障排除

### 問題 1: 連接失敗

**錯誤訊息**:
```
ConnectionError: 無法連接到機器手臂 10.42.0.180:9000
```

**解決方法**:

1. **檢查網路連接**:
   ```bash
   ping 10.42.0.180
   ```

2. **檢查 Server_280.py 是否運行**:
   ```bash
   ssh user@10.42.0.180
   ps aux | grep Server_280.py
   ```

3. **檢查端口是否開放**:
   ```bash
   telnet 10.42.0.180 9000
   ```

4. **檢查配置文件中的 IP 地址**:
   ```yaml
   # config/robot_arm/button_positions.yaml
   connection:
     socket:
       host: "10.42.0.180"  # 確認此 IP 正確
   ```

### 問題 2: 移動超時

**錯誤訊息**:
```
RuntimeError: 移動到初始位置超時
```

**解決方法**:

1. **檢查機器手臂是否卡住或有障礙物**
2. **檢查電源是否開啟**:
   ```python
   controller.is_power_on()
   controller.power_on()
   ```
3. **調整超時時間** (在 `mycobot_socket_controller.py`):
   ```python
   def wait_for_movement(self, timeout: float = 60.0):  # 增加到 60 秒
   ```

### 問題 3: 按鈕位置不準確

**現象**: 機器手臂沒有準確按到按鈕

**解決方法**:

1. **重新示教按鈕位置** (參考 [如何修改按鈕位置](#如何修改按鈕位置))

2. **檢查機器手臂校準**:
   - 確認零位是否正確
   - 檢查關節是否有鬆動

3. **調整按壓深度**:
   ```yaml
   # 調整 down_angles 的 J2 角度（通常是上下移動）
   down_angles: [16.5, -51, -130, 73.7, 0, 0]  # J2 = -51
   down_angles: [16.5, -55, -130, 73.7, 0, 0]  # 增加下壓深度
   ```

### 問題 4: 電源未開啟

**錯誤訊息**:
```
伺服馬達電源未開啟，正在開啟...
```

**解決方法**:

這是正常行為，系統會自動開啟電源。如果持續失敗:

1. **手動檢查電源**:
   ```python
   from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController

   controller = MyCobotSocketController("10.42.0.180", 9000)
   controller.connect()
   print(f"電源狀態: {controller.is_power_on()}")
   controller.power_on()
   ```

2. **檢查硬體**: 確認機器手臂主體電源是否開啟

### 問題 5: pymycobot 未安裝

**錯誤訊息**:
```
ImportError: No module named 'pymycobot'
```

**解決方法**:

```bash
pipenv install pymycobot
```

---

## 開發指南

### 新增按鈕

#### 1. 在配置文件中新增按鈕定義

編輯 `config/robot_arm/button_positions.yaml`:

```yaml
buttons:
  my_new_button:
    name: "新按鈕"
    description: "新增的按鈕功能"
    down_angles: [10.0, -50, -120, 70, 0, 0]
    up_angles: [10.0, -20, -120, 70, 0, 0]
    speed: 100
    press_duration: 1.0
```

#### 2. 在關鍵字庫中新增關鍵字

編輯 `libraries/robot_arm_control/RobotArmKeywords.py`:

```python
@keyword("點擊新按鈕")
def click_my_new_button(self):
    """
    點擊新按鈕

    Examples:
        | 點擊新按鈕 |
    """
    self._press_button('my_new_button')
```

#### 3. 測試新按鈕

```robot
*** Test Cases ***
測試新按鈕
    連接機器手臂
    點擊新按鈕
    回到初始位置
    斷開機器手臂連接
```

### 擴展長按功能

目前僅 `retract` 和 `extend` 支援長按，若要擴展到其他按鈕:

#### 1. 修改配置文件

```yaml
buttons:
  bluetooth:
    press_duration: 5.0  # 改為 5 秒（長按）
```

#### 2. 新增長按關鍵字

```python
@keyword("長按藍牙按鈕")
def long_press_bluetooth_button(self, 秒數: int = 5):
    """長按藍牙按鈕"""
    self._press_button('bluetooth', custom_duration=float(秒數))
```

### 單元測試

```bash
# 測試配置載入器
cd libraries/robot_arm_control
python button_config_loader.py

# 測試 Socket 控制器（需要機器手臂連接）
python mycobot_socket_controller.py

# 列出所有關鍵字
python RobotArmKeywords.py
```

### 日誌除錯

查看詳細日誌:

```bash
robot --loglevel DEBUG tests/robot_arm/basic_button_test.robot
```

日誌會顯示:
- 連接狀態
- 發送的角度指令
- 移動耗時
- 錯誤訊息

---

## 參考資料

### 官方文檔

- [MyCobot 280 官方文檔](https://docs.elephantrobotics.com/docs/mycobot_280_jn_en/)
- [pymycobot TCP/IP 控制指南](https://docs.elephantrobotics.com/docs/mycobot_280_jn_en/3-FunctionsAndApplications/6.developmentGuide/python/7_TCPIP.html)
- [Robot Framework 用戶指南](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)

### 專案文檔

- [專案總覽](../../README.md)
- [專案指引](../../CLAUDE.md)
- [系統規格書](../../spec.md)
- [任務清單](../../todo.md)
- [關鍵字說明](../../keywords_readme.md)
- [設計文檔](../../docs/robot_arm_socket_control_design.md)

### 按鈕映射表

完整的按鈕映射表請參考 [設計文檔 - 第 6 節](../../docs/robot_arm_socket_control_design.md#6-按鈕映射表)

---

## 版本資訊

- **版本**: 2.0.0
- **最後更新**: 2025-11-13
- **作者**: Robot Testing Team
- **Python 版本**: 3.12
- **Robot Framework 版本**: 7.3.1+

### v2.0.0 更新日誌（2025-11-13）

**重大更新 - BDD 風格架構**:
- ✅ **新增 BDD 關鍵字**: 21 個 Gherkin 風格關鍵字（Given 3 + When 10 + Then 5 + And 3）
- ✅ **雙層架構**: 與 Voice Control 模式一致，直接使用 Python Library 中的 @keyword
- ✅ **視覺檢測整合**: 新增燈光狀態檢測、顏色識別功能
- ✅ **完整測試覆蓋**: 包含完整 BDD 測試案例 (test_robot_arm_bdd_complete.robot)
- ✅ **向後相容**: 保留傳統關鍵字，確保現有測試案例可正常運行
- ✅ **文檔完善**: 詳細的 BDD 關鍵字使用說明和範例

**技術改進**:
- 關鍵字總數從 23 個增加到 26 個
- 支援更複雜的測試場景和狀態驗證
- 改善錯誤處理和日誌記錄
- 新增操作歷程記錄功能

---

## 授權聲明

本模組為專案內部使用，請遵循專案整體授權條款。

---

## 聯絡資訊

如有問題或建議，請透過以下方式聯絡:

- 提交 Issue 到專案 Repository
- 參考 [CLAUDE.md](../../CLAUDE.md) 中的專案準則
- 查閱 [todo.md](../../todo.md) 中的任務進度

---

**文檔結束**
