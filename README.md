# Robot Framework 多平台自動化測試系統

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Robot Framework](https://img.shields.io/badge/Robot%20Framework-4.1+-green.svg)](https://robotframework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()

## 專案描述

**Robot Framework Multi-Platform Automation Testing System** 是一個基於 Robot Framework 的綜合性自動化測試平台，整合多種測試手段和檢測方式，實現對 **iOS/Android 應用程式**、**硬體設備操作**、**語音控制**和**電源管理**的全方位自動化測試。

### 🎯 主要特色

- 📱 **移動應用測試**: iOS 和 Android 應用程式自動化測試
- 🤖 **硬體操作測試**: MyCobot 280 機器手臂控制實體面板操作  
- 🎤 **語音控制測試**: 本機語音識別和語音命令執行
- 🔌 **電源管理測試**: SwitchBot 智慧插座控制被測設備開關機 ✅ **[已完成]**
- 📹 **IP Camera 燈光檢測**: RTSP 串流影像擷取與燈光狀態智能分析 ✅ **[已完成]**
- 👁️ **多感官檢測**: 麥克風雙向音訊檢測（發音與錄音判斷）和視覺影像判斷（YOLO靜態燈號檢測與動態角度變化分析）
-  **TestLink 整合**: 測試案例管理與執行結果追蹤
- 🔄 **整合式測試**: 多設備協同操作的端到端測試流程

### 🏗️ 系統架構

系統採用模組化設計，各子系統可獨立運作或協同配合：

```mermaid
graph TB
    A[Robot Framework 核心] --> B[移動應用測試]
    A --> C[機器手臂控制]
    A --> D[語音控制系統]
    A --> E[電源管理]
    A --> F[多感官檢測]
    A --> G[TestLink 整合]
    
    B --> H[iOS Testing - Appium]
    B --> I[Android Testing - Appium]
    B --> J[IoT面板]
    
    C --> K[MyCobot 280 - 測試工具]
    C --> L[實體面板操作自動化]
    C --> M[視覺輔助定位]
    
    D --> N[TTS - 英]
    D --> O[高品質錄音 - 48kHz/24bit]
    D --> P[語音識別與環境音檢測]
    
    E --> Q[SwitchBot 智慧插座 ✅]
    E --> R[被測設備電源管理 ✅]
    E --> S[設備狀態監控 ✅]
    
    F --> T[音訊檢測 - 雙向互動]
    F --> U[YOLO 燈號檢測]
    F --> V[動態角度變化追蹤]
    F --> W[多模態數據融合]
    
    G --> X[測試案例管理與同步]
    G --> Y[執行結果自動回報]
    G --> Z[缺陷追蹤整合]
    
    E --> S1[IP Camera 燈光檢測 ✅]

    S1 --> T1[RTSP 串流連線]
    S1 --> T2[影像擷取與分析]
    S1 --> T3[燈光狀態判定]

    subgraph "硬體設備"
        AA[USB 攝影機 - 視覺檢測]
        BB[麥克風/喇叭 - 音訊 I/O]
        CC[SwitchBot - 電源控制]
    end
```

## 專案結構

```
robot-test-project/
├── 📁 config/                               # 系統配置模組
│   ├── __init__.py                         # 配置包初始化
│   ├── ipcam_config.yaml                   # IP Camera 配置
│   ├── ipcam_config.py                     # IP Camera 配置管理
│   ├── voice_config.py                     # 語音系統配置
│   └── migration_report.md                 # 配置重構報告
│
├── 📁 libraries/                            # 自定義 Library 模組
│   ├── 📁 ipcam_light_detection/ ✅         # IP Camera 燈光檢測模組 [已完成]
│   │   ├── IPCamLightDetection.py          # Robot Framework Library
│   │   ├── __init__.py                     # 模組初始化
│   │   └── README.md                       # 完整 API 文檔
│   │
│   ├── 📁 local_voice_verifying/           # 語音驗證庫 (已實現)
│   │   ├── LocalVoiceVerifyingLibrary.py   # 主要 Robot Framework Library
│   │   ├── voice_tts_manager.py            # TTS 管理模組
│   │   ├── voice_audio_recorder.py         # 音訊錄製模組
│   │   ├── voice_sound_detector.py         # 聲音檢測模組
│   │   ├── 📁 audio_samples/               # 音訊檔案
│   │   ├── 📁 logs/                        # 日誌檔案
│   │   └── 📁 tests/                       # 單元測試
│   │
│   ├── 📁 mobile_testing/ (計劃中)          # 移動應用測試模組
│   │   ├── 📁 ios_testing/                 # iOS 測試庫
│   │   ├── 📁 android_testing/             # Android 測試庫
│   │   └── 📁 common/                      # 通用移動測試功能
│   │
│   ├── 📁 robot_arm_control/ (計劃中)       # 機器手臂控制模組 (測試工具)
│   │   ├── mycobot_controller.py           # MyCobot 280 控制器
│   │   ├── arm_movements_library.py        # 運動學庫
│   │   ├── 📁 calibration/                 # 校準數據
│   │   └── 📁 validation/                  # 工具驗證測試 (非TestLink案例)
│   │
│   ├── 📁 switchbot_smartplug_control/ ✅   # SwitchBot 智慧插座控制模組 [已完成]
│   │   ├── SwitchBotSmartPlugLibrary.py    # Robot Framework Library
│   │   ├── switchbot_config.py             # 配置管理模組
│   │   ├── .env.example                    # 環境變數範本
│   │   ├── get_device_id.py               # 設備查詢工具
│   │   ├── plug_control.py                # 命令列控制工具
│   │   ├── check_device.py                # 設備檢查工具
│   │   └── README.md                       # 模組說明文件
│   │
│   ├── 📁 power_management/ (計劃中)        # 電源管理模組
│   │   ├── smart_socket_controller.py      # 智慧插座控制
│   │   └── 📁 network_devices/             # 網路設備支援
│   │
│   ├── 📁 testlink_integration/ (計劃中)   # TestLink 整合模組
│   │   ├── testlink_connector.py           # TestLink API 連接器
│   │   ├── case_synchronizer.py            # 測試案例同步器
│   │   ├── result_reporter.py              # 結果回報器
│   │   ├── 📁 api_client/                  # API 客戶端
│   │   ├── 📁 config/                      # TestLink 配置
│   │   └── 📁 keywords/                    # TestLink 關鍵字
│   │
│   └── 📁 detection_systems/ (計劃中)       # 檢測系統模組
│       ├── 📁 audio_detection/             # 音訊檢測
│       ├── 📁 visual_detection/            # 視覺檢測
│       └── 📁 analysis/                    # 分析與報告
│
├── 📁 tests/                               # Robot Framework 測試案例
│   ├── 📁 ipcam_testing/ ✅                 # IP Camera 測試 [新增]
│   │   └── ipcam_light_detection_test.robot # IP Camera 測試案例
│   ├── 📁 physical_interaction/            # 實體互動測試
│   │   └── voice_test.robot               # 語音測試案例
│   ├── 📁 power_management/ ✅              # 電源管理測試 [新增]
│   │   └── switchbot_smartplug_test.robot # SwitchBot 插座測試案例
│   ├── 📁 mobile/ (計劃中)                 # 移動應用測試
│   ├── 📁 api/ (計劃中)                    # API 測試
│   └── 📁 web/ (計劃中)                    # Web 測試
│
├── 📁 resources/                           # Robot Framework 資源
│   ├── api_keywords.robot                  # API 關鍵字
│   ├── common_keywords.robot               # 通用關鍵字
│   ├── ipcam_keywords.robot ✅              # IP Camera 關鍵字 [新增]
│   ├── mobile_keywords.robot               # 移動設備關鍵字
│   ├── switchbot_keywords.robot ✅          # SwitchBot 智慧插座關鍵字 [新增]
│   └── web_keywords.robot                  # Web 關鍵字
│
├── 📁 variables/                           # 測試變數與資料
│   ├── common_variables.py                 # 通用變數
│   └── users.json                         # 測試用戶資料
│
├── 📄 spec.md                              # 系統規格書
├── 📄 todo.md                              # 任務清單
├── 📄 Pipfile                              # Python 相依性管理
├── 📄 requirements.txt                     # Python 套件需求
└── 📄 README.md                            # 本檔案
```

## 安裝與環境設置

### 🖥️ 系統需求

- **作業系統**: macOS 10.15+ (主要開發平台)
- **Python**: 3.8+ 
- **記憶體**: 8GB RAM (建議 16GB)
- **硬碟空間**: 20GB 可用空間
- **網路**: 穩定的 WiFi 連線

### 📋 硬體需求

#### 基礎配置 (語音系統)
- [x] **麥克風**: 內建或 USB 麥克風
- [x] **喇叭**: 內建或外接音訊輸出

#### 擴展配置 (完整系統)
- [ ] **MyCobot 280**: 機器手臂 (測試工具，用於操作實體面板)
- [x] **智慧插座**: SwitchBot 智慧插座 (被測設備電源管理) ✅ **[已完成]**
- [x] **IP Camera**: 支援 RTSP 的網路攝影機 (已測試 3 台) ✅ **[已完成]**
  - Level 1: 192.168.165.184
  - Level 2: 192.168.165.127
  - Motor: 10.42.0.39
- [ ] **測試設備**: 
  - iPhone/iPad (iOS 應用測試目標)
  - Android 手機/平板 (Android 測試目標)
  - IoT 面板設備 (實體面板操作測試目標)
- [ ] **USB 攝影機**: 視覺檢測用 (YOLO 燈號檢測與動態角度變化分析)

### 🔧 軟體依賴

#### 必要軟體
```bash
# macOS 開發工具
xcode-select --install

# Homebrew (套件管理)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 環境
brew install python@3.11
brew install pipenv
```

#### IP Camera 燈光檢測環境 ✅ **[已完成 - 2025-11-05]**
```bash
# 安裝依賴套件
pipenv install opencv-python numpy loguru pyyaml

# 配置認證資訊
cp .env.example .env
# 編輯 .env 設定 IPCAM_USERNAME 和 IPCAM_PASSWORD

# 測試連線
pipenv run python3 scripts/quick_ipcam_test.py

# 執行測試
pipenv run robot --include smoke tests/ipcam_testing/
```

#### iOS 真機測試環境 ✅ **[已完成 - 2025-06-27]**
```bash
# 一鍵式環境設置（Ubuntu 24.04）
./scripts/setup_ios_testing.sh --install-deps --verbose

# iOS 設備工具安裝
sudo apt install -y libimobiledevice-utils usbmuxd

# Appium 和 iOS 驅動安裝
sudo npm install -g appium@next
appium driver install xcuitest

# 檢查 iOS 設備連接
./scripts/check_ios_device.sh --verbose
```

#### Android 開發環境 (計劃)
```bash
# Android 應用測試需要
brew install --cask android-studio
brew install android-platform-tools
```

### 🚀 快速安裝

1. **克隆專案**
   ```bash
   git clone [repository-url]
   cd robot-test-project
   ```

2. **安裝 Python 相依套件**
   ```bash
   # 使用 pipenv (推薦)
   pipenv install
   pipenv shell
   
   # 或使用 pip
   pip install -r requirements.txt
   ```

3. **驗證基礎安裝**
   ```bash
   # 測試配置載入
   python -c "from config.voice_config import AUDIO_CONFIG, TTS_CONFIG; print('✅ 配置載入成功')"
   
   # 測試語音 Library 初始化
   python -c "from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary; lib = LocalVoiceVerifyingLibrary(); print(f'✅ Library 初始化: {lib.is_initialized}')"
   ```

4. **執行基礎測試**
   ```bash
   # Robot Framework dryrun 測試
   robot --dryrun tests/physical_interaction/voice_test.robot
   
   # 實際語音功能測試
   robot --test "Test TTS Voice execution" tests/physical_interaction/voice_test.robot
   ```

4. **環境設定**
   ```bash
   # 複製環境變數範本
   cp .env.example .env
   
   # 編輯配置檔案 (參考 SETUP_GUIDE.md 詳細說明)
   nano .env
   ```

   📖 **詳細設定指南**: 請參閱 [SETUP_GUIDE.md](SETUP_GUIDE.md) 獲得完整的配置說明

5. **設定 SwitchBot 智慧插座** (如需電源管理功能)
   ```bash
   # 取得設備 ID
   pipenv run python libraries/switchbot_smartplug_control/get_device_id.py
   
   # 測試插座控制
   pipenv run python libraries/switchbot_smartplug_control/plug_control.py status
   ```

## 🚀 快速開始 - IP Camera 燈光檢測

### 5 分鐘設置

1. **安裝依賴**:
   ```bash
   pipenv shell
   pipenv install opencv-python numpy loguru pyyaml
   ```

2. **配置認證**:
   ```bash
   # 編輯 .env 文件
   IPCAM_USERNAME=admin
   IPCAM_PASSWORD=your_password
   ```

3. **驗證配置**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pipenv run python3 scripts/test_ipcam_config.py
   ```

4. **執行測試**:
   ```bash
   pipenv run robot --include smoke tests/ipcam_testing/
   ```

### Python 使用範例

```python
from libraries.ipcam_light_detection import IPCamLightDetection

detector = IPCamLightDetection()
detector.connect_camera('laboratory', 'level1')
brightness = detector.get_current_brightness()
is_on = detector.is_light_on()
print(f"亮度: {brightness}, 燈光: {'開啟' if is_on else '關閉'}")
```

### Robot Framework 使用範例

```robotframework
*** Test Cases ***
檢測燈光狀態
    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態
    And 儲存當前攝影機影像    /tmp/screenshot.jpg
```

詳細文檔請參閱:
- [安裝指南](docs/ipcam_setup_guide.md)
- [快速開始](docs/ipcam_quick_start.md)
- [API 文檔](libraries/ipcam_light_detection/README.md)

### 🔧 進階設置 (各子系統)

#### 機器手臂設置 (MyCobot 280)
```bash
# 安裝 MyCobot 控制庫
pip install pymycobot

# 檢查 USB 連接
ls /dev/tty.usbserial-*

# 權限設置 (如需要)
sudo chmod 666 /dev/tty.usbserial-*
```

#### 智慧插座設置 (被測設備電源管理)
```bash
# SwitchBot 智慧插座支援
pip install switchbot-api

# 檢測 SwitchBot 設備
# 1. 下載 SwitchBot App 並設定智慧插座
# 2. 取得設備 MAC 地址與 API Token
# 3. 配置網路連接 (WiFi 2.4GHz)

# 配置範例 (在 config/voice_config.py 中設定)
SWITCHBOT_CONFIG = {
    "api_key": "your_switchbot_api_key",
    "devices": {
        "test_device_power": {
            "mac": "AA:BB:CC:DD:EE:FF",
            "type": "plug_mini",
            "ip": "192.168.1.100"
        }
    }
}

# 測試 SwitchBot 連接
python -c "
import requests
response = requests.get('https://api.switch-bot.com/v1.1/devices', 
                       headers={'Authorization': 'your_api_key'})
print(response.json())
"
```

#### TestLink 整合設置
```bash
# 安裝 TestLink API 客戶端
pip install python-testlink-api
pip install xmlrpc3

# 配置 TestLink 連接
# 1. 取得 TestLink API Key (從 TestLink 個人設定頁面)
# 2. 設定環境變數 (在專案根目錄 .env 檔案中)

# 首先複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，添加 TestLink 配置
export TESTLINK_URL="http://your-testlink-server/lib/api/xmlrpc/v1/xmlrpc.php"
export TESTLINK_API_KEY="your_api_key_here"

# 3. 配置 TestLink 專案資訊 (在 config/ 統一配置系統中)
```

**TestLink 配置範例** (`config/testlink_config.json`):
```json
{
  "server": {
    "url": "http://testlink.company.com/lib/api/xmlrpc/v1/xmlrpc.php",
    "api_key": "your_api_key_here",
    "timeout": 30
  },
  "project": {
    "id": "ROBOT_AUTO_TEST",
    "name": "Robot Framework Automation Testing",
    "prefix": "RAT"
  },
  "sync_settings": {
    "auto_sync": true,
    "sync_interval": 3600,
    "create_test_plan": true,
    "update_results": true
  }
}
```

#### 移動設備設置
```bash
# iOS 設備檢測
idevice_id -l

# Android 設備檢測

adb devices

# Appium 服務安裝
npm install -g appium
appium driver install uiautomator2
appium driver install xcuitest
```
## 執行方式與使用指南

### 🎯 快速開始

#### 1. 語音系統測試 (已實現)

```bash
# 基礎語音功能測試
robot tests/physical_interaction/voice_test.robot

# 特定測試案例
robot --test "Test TTS Voice execution" tests/physical_interaction/voice_test.robot
robot --test "Test Individual Voice Functions" tests/physical_interaction/voice_test.robot

# 產生詳細報告
robot --outputdir results tests/physical_interaction/voice_test.robot
```

#### 2. 系統整合測試 (計劃中)

```bash
# 完整端到端測試
robot --include integration tests/

# 移動應用測試
robot --include mobile tests/mobile/

# 硬體操作測試  
robot --include hardware tests/physical_interaction/

# 電源管理測試
robot --include power tests/
```

### 📱 移動應用測試 (Appium)

本專案整合了 **Appium** 框架，提供跨平台的移動應用自動化測試能力。

### 支援平台
- **iOS**: 使用 XCUITest 驅動，支援真機和模擬器
- **Android**: 使用 UiAutomator2 驅動，支援真機和模擬器

### 環境需求

#### macOS (推薦，支援 iOS + Android)
```bash
# Node.js 和 Appium
brew install node
npm install -g appium@next
appium driver install xcuitest uiautomator2

# iOS 環境
# 安裝 Xcode (從 App Store)
brew install ios-deploy
brew install wix/brew/applesimutils

# Android 環境
# 安裝 Android Studio
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Java 環境
brew install openjdk
export JAVA_HOME="/opt/homebrew/opt/openjdk"
```

#### Windows/Linux (僅支援 Android)
```bash
# Node.js 和 Appium
npm install -g appium@next
appium driver install uiautomator2

# Android 環境設置
export ANDROID_HOME=/path/to/android-sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Java 環境
export JAVA_HOME=/path/to/java
```

### 快速開始

#### 1. 環境檢查
```bash
# 檢查 Appium 環境
appium-doctor --android --ios

# 檢查設備連接

adb devices                    # Android
xcrun simctl list devices     # iOS
```

#### 2. 啟動 Appium 服務
```bash
# 啟動 Appium (背景執行)
./scripts/start_appium.sh --background

# 或前景執行進行除錯
./scripts/start_appium.sh --debug
```

#### 3. 執行測試
```bash
# iOS 測試
robot -v IOS_BUNDLE_ID:com.example.app tests/mobile/ios/

# Android 測試  
robot -v ANDROID_APP_PACKAGE:com.example.app tests/mobile/android/

# 跨平台測試
robot tests/mobile/common/
```

#### 4. 停止服務
```bash
./scripts/stop_appium.sh
```

### 測試案例範例

#### iOS 應用測試
```robotframework
*** Test Cases ***
iOS App Launch Test
    Open Mobile Application    ios
    ...    bundleId=com.example.app
    ...    deviceName=iPhone 14
    ...    platformVersion=16.0
    
    Wait For Element    accessibility_id=main_screen
    Take Mobile Screenshot    ios_launch.png
    Close Mobile Application
```

#### Android 應用測試
```robotframework
*** Test Cases ***
Android Login Test
    Open Mobile Application    android
    ...    appPackage=com.example.app
    ...    appActivity=.MainActivity
    
    Login To Mobile App
    ...    username=testuser
    ...    password=testpass
    ...    username_field=id=username_input
    ...    password_field=id=password_input
    ...    login_button=id=login_btn
    
    Verify Element Text    id=welcome_text    歡迎回來
    Close Mobile Application
```

### 環境配置

複製 `.env.template` 為 `.env` 並根據你的測試環境修改：

```bash
# Appium 服務設定
APPIUM_HOST=localhost
APPIUM_PORT=4723

# iOS 設定
IOS_DEVICE_NAME=iPhone 14
IOS_PLATFORM_VERSION=16.0
IOS_BUNDLE_ID=com.example.app

# Android 設定
ANDROID_DEVICE_NAME=Android Emulator
ANDROID_PLATFORM_VERSION=11
ANDROID_APP_PACKAGE=com.example.app
ANDROID_APP_ACTIVITY=.MainActivity
```
## 系統功能與特色

### ✅ 已實現功能 (v1.2)

#### 🎤 語音控制系統
- **TTS 語音播放**
  - ✅ Google TTS (gTTS) 線上語音合成
  - ✅ 離線 TTS (pyttsx3) 備援機制
  - ✅ 多語言支援 (中文、英文)
  - ✅ 語速與音量調整

- **音訊錄製功能**
  - ✅ 即時錄音 (支援設定時長)
  - ✅ 高品質 WAV 格式保存
  - ✅ 自動檔案命名與管理
  - ✅ 麥克風權限自動檢測

- **Robot Framework 整合**
  - ✅ 完整關鍵字庫支援
  - ✅ 自動化測試案例
  - ✅ 詳細錯誤處理與日誌
  - ✅ 測試報告生成

#### 📱 移動應用測試模組 ✅ **[2025-06-27 完成並驗證]**
- **iOS 真機測試** ✅ **[完整支援 + 執行驗證通過]**
  - ✅ Appium 2.x + XCUITest 驅動整合
  - ✅ Ubuntu 24.04 環境下 iOS 真機支援
  - ✅ 自動設備檢測和 UDID 管理 (已測試: iPhone 18.5)
  - ✅ 設備資訊獲取 (名稱、版本、型號)
  - ✅ 系統應用自動化測試 (計算機、設定)
  - ✅ 觸控手勢和滑動操作
  - ✅ 設備旋轉和螢幕方向測試
  - ✅ 螢幕截圖和測試結果記錄
  - ✅ 完整的 Gherkin 風格測試案例
  - ✅ **執行驗證**: 3/3 測試案例通過，設備檢測正常

- **Android 應用測試** ✅ **[基礎支援]**
  - ✅ UIAutomator2 + Appium 整合
  - ✅ 基本 UI 元素操作
  - ✅ 測試案例框架建立

#### 💡 配置管理系統
- ✅ 統一配置架構 (`config/voice_config.py`)
- ✅ 模組化設定管理
- ✅ 環境變數支援
- ✅ 動態配置載入

#### 🔌 電源管理系統 ✅ **[完整實現]**
- ✅ SwitchBot 智慧插座 API 整合
- ✅ 設備自動發現與狀態查詢
- ✅ 開關控制與狀態監測
- ✅ 統一配置系統整合
- ✅ Robot Framework 關鍵字庫
- ✅ 完整測試案例與文檔
- ✅ 設備狀態檢測與驗證

## 📹 IP Camera 燈光檢測系統 ✅

### 功能概述

基於 RTSP 串流的 IP Camera 影像分析系統，支援：
- 實時影像擷取（HEVC/H.265 編碼）
- 智能亮度分析（0-255 數值範圍）
- 自動燈光狀態判定（可配置閾值）
- 多攝影機環境管理
- 完整的中文 Robot Framework 關鍵字

### 測試通過的攝影機

| 攝影機 | IP 地址 | 狀態 | 影像尺寸 |
|---|---|---|---|
| Level1 | 192.168.165.184 | ✅ 正常 | 1620×2592 |
| Level2 | 192.168.165.127 | ✅ 正常 | 1620×2592 |
| Motor  | 10.42.0.39      | ✅ 正常 | 1620×2592 |

### 使用範例

#### Python
```python
from libraries.ipcam_light_detection import IPCamLightDetection

detector = IPCamLightDetection()
detector.connect_camera('laboratory', 'level1')
brightness = detector.get_current_brightness()
```

#### Robot Framework
```robotframework
*** Test Cases ***
自動化燈光檢測
    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態
```

### 相關文檔

- [完整 API 文檔](libraries/ipcam_light_detection/README.md)
- [安裝指南](docs/ipcam_setup_guide.md)
- [快速開始](docs/ipcam_quick_start.md)
- [模組摘要](docs/ipcam_module_summary.md)
- [測試案例](tests/ipcam_testing/ipcam_light_detection_test.robot)

**開發完成日期**: 2025-11-05
**測試狀態**: ✅ 生產就緒 (Production Ready)

#### 🌐 測試標準化系統 ✅ **[完整實現]**
- ✅ 全面中文關鍵字標準化
- ✅ Gherkin 風格測試案例 (Given-When-Then)
- ✅ 雙語文檔 (中英文說明)
- ✅ 統一編碼規範和註解標準
- ✅ 完整的使用範例和 [Documentation]

### 🔄 部分實現功能

### 🔄 部分實現功能

#### 🔍 聲音檢測系統
- 🔄 MFCC 特徵提取 (基礎框架已實現)
- 🔄 DTW 比對算法 (需要參考聲音檔案)
- 🔄 信心度計算與閾值調整
- 🔄 環境音分類與識別

### 🚧 計劃中功能 (v2.0+)

#### 📱 移動應用測試模組 - 進階功能
- [ ] **iOS 應用測試 - 進階功能**
  - 多設備並行測試
  - 應用效能監控 (CPU、記憶體、電池)
  - 推播通知和背景處理測試
  - 網路條件模擬和測試

- [ ] **Android 應用測試 - 完整實現**
  - 系統設定與權限管理
  - 硬體功能測試 (感測器、藍牙、NFC)
  - 效能監控 (CPU、記憶體、電池)
  - ADB 進階控制功能

#### 🤖 機器手臂控制模組
- [ ] **MyCobot 280 控制**
  - 6軸關節精確控制
  - 座標系統轉換 (基座/工具/關節)
  - 路徑規劃 (直線/圓弧運動)
  - 安全機制 (碰撞檢測、急停)

- [ ] **實體面板操作**
  - OpenCV 視覺輔助定位
  - 按鈕/開關精確操作
  - 觸控面板多點操作
  - 操作結果驗證

#### 🔌 電源管理模組
- [x] **SwitchBot 智慧插座控制** - ✅ 已完成
  - SwitchBot Smart Plug 完整整合
  - HTTP API 認證與控制
  - 設備自動發現與狀態查詢
  - 開關控制與狀態監測
  - 統一配置管理系統

- [x] **設備電源管理** - ✅ 已完成
  - 自動開關機控制
  - 設備狀態檢測與驗證
  - Robot Framework 中文關鍵字支援
  - Gherkin 風格測試案例
  - 詳細錯誤處理與日誌記錄

#### 👁️ 多感官檢測模組
- [ ] **音訊檢測系統**
  - **雙向音訊互動**:
    - TTS 多語言語音合成（中文、英文、日文）
    - 測試音效產生（標準音頻、警報聲、提示音）
    - 音訊輸出設備管理與控制
  - **高品質錄音分析**:
    - 48kHz/24bit 高品質音訊擷取
    - 語音識別與關鍵字檢測
    - 噪音抑制與回音消除
    - 頻譜分析與音訊特徵提取
  - **環境音檢測**:
    - 機器運轉聲模式識別
    - 警報聲、蜂鳴聲自動檢測
    - 音訊回饋驗證與品質評估

- [ ] **視覺檢測系統**
  - **YOLO 燈號檢測**:
    - YOLOv8 深度學習多色 LED 檢測
    - 燈號狀態分類（亮燈/熄燈/閃爍/半亮）
    - ROI 區域高精度檢測
    - 多燈號同時檢測與狀態分析
  - **動態角度變化檢測**:
    - 高頻影像擷取（30-120 FPS）
    - 標記中心點追蹤（KCF、CSRT、MOSSE）
    - 角度變化計算與旋轉方向判斷
    - 運動軌跡記錄與可視化分析
  - **傳統影像檢測**:
    - 螢幕即時擷取與多螢幕監控
    - 多語言 OCR 文字識別
    - 圖標符號檢測與模板匹配
    - 色彩變化檢測與分析

#### TestLink 整合模組
- [ ] **TestLink API 整合**
  - 測試案例自動匯入/匯出
  - 測試執行結果自動回報
  - 缺陷追蹤與管理整合
  - 測試計劃與需求關聯

- [ ] **報告與分析**
  - 自動化測試報告生成
  - 測試結果趨勢分析
  - 覆蓋率報告與缺陷分析

## 配置管理

### 📋 系統配置結構

系統採用統一配置管理，主要配置檔案位於 `config/voice_config.py`：

```python
# 主要配置區塊
AUDIO_CONFIG = {
    'sample_rate': 44100,      # 音訊取樣率
    'channels': 2,             # 聲道數 (1=單聲道, 2=立體聲)
    'chunk_size': 1024,        # 緩衝區大小
    'format': 'int16'          # 音訊格式
}

TTS_CONFIG = {
    'google_tts': {
        'language': 'zh-TW',   # 預設語言
        'slow': False,         # 語速設定
        'timeout': 10          # 連線逾時
    },
    'pyttsx3': {
        'rate': 200,           # 語速 (words per minute)
        'volume': 0.8,         # 音量 (0.0-1.0)
        'voice_id': 0          # 語音 ID
    }
}

DETECTION_CONFIG = {
    'mfcc_features': 13,       # MFCC 特徵數量
    'frame_length': 2048,      # 框架長度
    'hop_length': 512,         # 跳躍長度
    'default_threshold': 0.75  # 預設檢測閾值
}
```

### 🔧 配置自定義

#### 語音系統配置
```python
# 修改 config/voice_config.py
TTS_CONFIG['google_tts']['language'] = 'en-US'  # 改為英文
TTS_CONFIG['pyttsx3']['rate'] = 150             # 調整語速

# 或在 Robot Framework 中動態調整
Set TTS Language    en-US
Set TTS Speed       1.5
```

#### 音訊錄製配置
```python
# 高品質錄音設定
AUDIO_CONFIG.update({
    'sample_rate': 48000,    # 提高取樣率
    'channels': 2,           # 立體聲錄音
    'chunk_size': 2048       # 增加緩衝區
})
```

#### 檢測系統配置
```python
# 調整檢測靈敏度
DETECTION_CONFIG['default_threshold'] = 0.8  # 提高閾值 (更嚴格)
DETECTION_CONFIG['mfcc_features'] = 20       # 增加特徵數量
```

### 📁 路徑配置

系統自動管理各種檔案路徑：

```python
PATHS = {
    'audio_samples': f"{PROJECT_ROOT}/libraries/local_voice_verifying/audio_samples",
    'recorded_audio': f"{PROJECT_ROOT}/libraries/local_voice_verifying/audio_samples/recorded",
    'reference_sounds': f"{PROJECT_ROOT}/libraries/local_voice_verifying/audio_samples/reference_sounds",
    'temp_audio': f"{PROJECT_ROOT}/libraries/local_voice_verifying/audio_samples/temp",
    'logs': f"{PROJECT_ROOT}/libraries/local_voice_verifying/logs",
    'test_data': f"{PROJECT_ROOT}/libraries/local_voice_verifying/test_data"
}
```

### 📊 日誌配置

詳細的日誌系統支援：

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f"{PATHS['logs']}/voice_library.log",
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    }
}
```

### 🌍 環境變數支援

```bash
# 設定環境變數
export VOICE_TTS_LANGUAGE=en-US
export VOICE_DETECTION_THRESHOLD=0.8
export VOICE_LOG_LEVEL=DEBUG

# Robot Framework 中使用
robot --variable TTS_LANG:%{{VOICE_TTS_LANGUAGE}} tests/
```

## 測試與驗證

### 🔍 單元測試

```bash
# 執行所有單元測試
cd libraries/local_voice_verifying/tests/
python -m pytest . -v

# 特定模組測試
python test_library_init.py           # Library 初始化測試
python test_library_functionality.py  # 功能完整性測試
python test_recording.py              # 音訊錄音測試
python test_recording_detailed.py     # 詳細錄音測試
```

### 🤖 Robot Framework 測試

```bash
# 基本功能驗證
robot --test "Test TTS Voice execution" tests/physical_interaction/voice_test.robot

# 完整功能測試
robot --test "Test Individual Voice Functions" tests/physical_interaction/voice_test.robot

# 產生詳細報告
robot --outputdir results --loglevel DEBUG tests/physical_interaction/voice_test.robot

# 特定標籤測試
robot --include voice --include tts tests/
```

### 📋 系統健康檢查

```bash
# 快速系統檢查腳本
cat > system_check.py << 'EOF'
#!/usr/bin/env python3
"""系統健康檢查腳本"""

def check_system_health():
    try:
        # 1. 配置檢查
        from config.voice_config import AUDIO_CONFIG, TTS_CONFIG
        print("✅ 配置載入成功")
        
        # 2. Library 初始化檢查
        from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        lib = LocalVoiceVerifyingLibrary()
        if lib.is_initialized:
            print("✅ 語音 Library 初始化成功")
        else:
            print("❌ 語音 Library 初始化失敗")
            
        # 3. 音訊設備檢查
        import pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"✅ 檢測到 {device_count} 個音訊設備")
        audio.terminate()
        
        # 4. 必要目錄檢查
        import os
        from config.voice_config import PATHS
        for name, path in PATHS.items():
            if os.path.exists(path):
                print(f"✅ {name} 目錄存在: {path}")
            else:
                print(f"⚠️  {name} 目錄不存在: {path} (請手動建立)")
                
        print("\n🎉 系統健康檢查完成！")
        
    except Exception as e:
        print(f"❌ 系統檢查失敗: {e}")

if __name__ == "__main__":
    check_system_health()
EOF

python system_check.py
```

### 🎤 音訊設備測試

```bash
# 測試麥克風錄音
python -c "
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
lib = LocalVoiceVerifyingLibrary()
print('開始 5 秒測試錄音...')
lib.start_voice_recording(5)
import time; time.sleep(5)
file_path = lib.stop_voice_recording()
print(f'錄音完成: {file_path}')
"

# 測試 TTS 播放
python -c "
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
lib = LocalVoiceVerifyingLibrary()
lib.speak_text('語音系統測試正常')
print('TTS 播放完成')
"
```

## 故障排除與常見問題

### 🚨 常見錯誤解決方案

#### 1. 模組匯入錯誤
```bash
# 錯誤: ModuleNotFoundError: No module named 'config'
# 解決方案:
cd /Users/owenke/source/github.com/robot-test-project  # 確保在專案根目錄
python -c "import sys; print(sys.path)"               # 檢查 Python 路徑
export PYTHONPATH="${PYTHONPATH}:$(pwd)"              # 添加專案路徑

# 驗證修復:
python -c "from config.voice_config import AUDIO_CONFIG; print('✅ 修復成功')"
```

#### 2. 音訊設備問題
```bash
# 錯誤: [Errno -9996] Invalid input device
# macOS 麥克風權限檢查:
# 系統偏好設定 > 安全性與隱私權 > 隱私權 > 麥克風 > 允許終端機/VS Code

# 檢查可用音訊設備:
python -c "
import pyaudio
audio = pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f'Device {i}: {info["name"]} - Inputs: {info["maxInputChannels"]}')
audio.terminate()
"

# 手動指定音訊設備:
# 修改 config/voice_config.py 中的 AUDIO_CONFIG['input_device_index'] = 設備編號
```

#### 3. TTS 播放失敗
```bash
# Google TTS 網路問題:
ping google.com  # 檢查網路連線

# 離線 TTS 備援測試:
python -c "
from libraries.local_voice_verifying.voice_tts_manager import TTSManager
tts = TTSManager()
tts.use_offline_tts = True
result = tts.speak_text('離線測試')
print(f'離線 TTS 結果: {result}')
"

# macOS 語音合成權限:
# 系統偏好設定 > 安全性與隱私權 > 隱私權 > 語音識別
```

#### 4. Robot Framework 執行錯誤
```bash
# 錯誤: No keyword with name 'Speak Text' found
# 檢查 Library 載入:
robot --dryrun --loglevel DEBUG tests/physical_interaction/voice_test.robot

# 手動驗證 Library:
python -c "
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
lib = LocalVoiceVerifyingLibrary()
print(f'Library 方法: {[m for m in dir(lib) if not m.startswith("_")]}')
"
```

#### 5. 檔案權限問題
```bash
# 錯誤: PermissionError: [Errno 13] Permission denied
# 檢查並修復目錄權限:
find libraries/local_voice_verifying/ -type d -exec chmod 755 {} \;
find libraries/local_voice_verifying/ -name "*.py" -exec chmod 644 {} \;
chmod -R 755 libraries/local_voice_verifying/audio_samples/
chmod -R 755 libraries/local_voice_verifying/logs/
```

### 🔧 環境診斷工具

#### 完整系統診斷腳本
```bash
cat > diagnose_system.py << 'EOF'
#!/usr/bin/env python3
"""完整系統診斷工具"""

import os
import sys
import subprocess
import importlib

def run_diagnosis():
    print("🔍 開始系統診斷...\n")
    
    # 1. Python 環境檢查
    print("1️⃣ Python 環境:")
    print(f"   Python 版本: {sys.version}")
    print(f"   Python 路徑: {sys.executable}")
    print(f"   工作目錄: {os.getcwd()}")
    print(f"   PYTHONPATH: {sys.path[:3]}...")
    
    # 2. 必要套件檢查
    print("\n2️⃣ 套件依賴檢查:")
    required_packages = [
        'robotframework', 'gtts', 'pyttsx3', 'pyaudio', 
        'numpy', 'loguru', 'requests'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安裝")
    
    # 3. 配置檔案檢查
    print("\n3️⃣ 配置檔案檢查:")
    try:
        from config.voice_config import AUDIO_CONFIG, TTS_CONFIG, PATHS
        print("   ✅ config.voice_config 載入成功")
        
        # 檢查路徑存在性
        for name, path in PATHS.items():
            if os.path.exists(path):
                print(f"   ✅ {name}: {path}")
            else:
                print(f"   ⚠️  {name}: {path} (不存在)")
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"      📁 已建立目錄: {path}")
                except Exception as e:
                    print(f"      ❌ 無法建立目錄: {e}")
                    
    except Exception as e:
        print(f"   ❌ 配置載入失敗: {e}")
    
    # 4. 音訊設備檢查
    print("\n4️⃣ 音訊設備檢查:")
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"   📻 檢測到 {device_count} 個音訊設備")
        
        # 列出輸入設備
        input_devices = []
        for i in range(device_count):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))
                
        print(f"   🎤 可用輸入設備: {len(input_devices)} 個")
        for idx, name in input_devices[:3]:  # 只顯示前3個
            print(f"      - 設備 {idx}: {name}")
            
        audio.terminate()
    except Exception as e:
        print(f"   ❌ 音訊設備檢查失敗: {e}")
    
    # 5. Library 初始化檢查
    print("\n5️⃣ Library 初始化檢查:")
    try:
        from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        lib = LocalVoiceVerifyingLibrary()
        
        if lib.is_initialized:
            print("   ✅ LocalVoiceVerifyingLibrary 初始化成功")
            print(f"   📋 可用關鍵字: {len([m for m in dir(lib) if not m.startswith('_')])} 個")
        else:
            print("   ❌ LocalVoiceVerifyingLibrary 初始化失敗")
            
    except Exception as e:
        print(f"   ❌ Library 載入失敗: {e}")
    
    # 6. Robot Framework 檢查
    print("\n6️⃣ Robot Framework 檢查:")
    try:
        result = subprocess.run(
            ['robot', '--version'], 
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"   ✅ Robot Framework: {result.stdout.strip()}")
        else:
            print(f"   ❌ Robot Framework 執行失敗: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Robot Framework 檢查失敗: {e}")
    
    print("\n🎉 診斷完成！")
    print("\n📋 建議修復步驟:")
    print("   1. 確保在專案根目錄執行命令")
    print("   2. 檢查 macOS 隱私權設定 (麥克風權限)")  
    print("   3. 安裝缺失的 Python 套件: pip install -r requirements.txt")
    print("   4. 如有 Robot Framework 問題，檢查測試檔案語法")

if __name__ == "__main__":
    run_diagnosis()
EOF

python diagnose_system.py
```

### 📊 效能調整建議

#### 1. 音訊效能最佳化
```python
# 修改 config/voice_config.py 以提升效能
AUDIO_CONFIG.update({
    'chunk_size': 2048,      # 增加緩衝區 (減少延遲)
    'sample_rate': 22050,    # 降低取樣率 (節省資源)
    'channels': 1            # 單聲道 (減少資料量)
})
```

#### 2. TTS 回應速度優化
```python
# 優先使用離線 TTS (更快回應)
TTS_CONFIG['pyttsx3']['rate'] = 250  # 提高語速
TTS_CONFIG['google_tts']['timeout'] = 5  # 減少網路等待時間
```

#### 3. 記憶體使用最佳化
```bash
# 定期清理暫存檔案
find libraries/local_voice_verifying/audio_samples/temp/ -name "*.wav" -mtime +1 -delete

# 限制日誌檔案大小
# 在 LOGGING_CONFIG 中設定 'maxBytes': 5242880  # 5MB
```

### 🆘 技術支援

#### 日誌檔案位置
- **主要日誌**: `libraries/local_voice_verifying/logs/voice_library.log`
- **TTS 日誌**: `libraries/local_voice_verifying/logs/tts_manager.log`  
- **錄音日誌**: `libraries/local_voice_verifying/logs/audio_recorder.log`
- **檢測日誌**: `libraries/local_voice_verifying/logs/sound_detector.log`
- **Robot 報告**: `results/log.html`, `results/report.html`

#### 詳細除錯模式
```bash
# 啟用詳細日誌
export VOICE_LOG_LEVEL=DEBUG

# Robot Framework 詳細模式
robot --loglevel DEBUG --outputdir results tests/

# Python 詳細除錯
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
lib = LocalVoiceVerifyingLibrary()
"
```

#### 系統資訊收集
```bash
# 產生系統報告
cat > system_report.sh << 'EOF'
#!/bin/bash
echo "=== 系統資訊報告 ==="
echo "日期: $(date)"
echo "系統: $(uname -a)"
echo "Python: $(python --version)"
echo "工作目錄: $(pwd)"
echo ""
echo "=== Python 套件 ==="
pip list | grep -E "(robot|gtts|pyaudio|numpy)"
echo ""
echo "=== 音訊設備 ==="
system_profiler SPAudioDataType | grep -A 5 "Input"
echo ""
echo "=== 檔案權限 ==="
ls -la config/
ls -la libraries/local_voice_verifying/
EOF

bash system_report.sh > system_report.txt
echo "報告已產生: system_report.txt"
```

## 開發歷程與版本資訊

### 📈 專案發展時程

#### 🏗️ Phase 1: 基礎架構建設 (✅ 2025-06-27 完成)
- ✅ **配置系統重構**: 統一配置管理至 `config/voice_config.py`
- ✅ **語音核心功能**: TTS 播放、音訊錄製、基礎檢測
- ✅ **Robot Framework 整合**: 完整關鍵字庫、測試案例
- ✅ **文檔建立**: spec.md、todo.md、README.md 完整文檔
- ✅ **測試驗證**: 單元測試、整合測試、dryrun 驗證
- ✅ **移動應用測試模組**: iOS/Android Appium 整合完成 ✅ **[2025-06-27 完成]**
  - ✅ iOS 真機測試環境完整建置 (Ubuntu 24.04)
  - ✅ Appium 2.x + XCUITest 驅動完整配置
  - ✅ 自動設備檢測和管理系統
  - ✅ 完整測試案例和文檔
- ✅ **電源管理系統**: SwitchBot 智慧插座控制與監控 ✅ **[已完成]**
- ✅ **全面中文關鍵字標準化**: Gherkin 風格 + 中文關鍵字 ✅ **[已完成]**

#### 🚧 Phase 2: 設備整合開發 (2025-07 ~ 2025-08)
- [ ] **機器手臂控制**: MyCobot 280 控制系統
- [ ] **進階移動測試**: 效能監控、多設備並行測試

#### 🔮 Phase 3: 檢測系統開發 (2025-09 ~ 2025-10)
- [ ] **多感官檢測**: 音訊/視覺檢測系統
- [ ] **AI 輔助識別**: 機器學習增強檢測
- [ ] **整合測試**: 端到端協同測試

#### v1.0.0 (2025-06-17) - 基礎語音系統
**主要功能**:
- ✅ LocalVoiceVerifyingLibrary 核心實現
- ✅ Google TTS + pyttsx3 雙引擎支援
- ✅ 高品質音訊錄製 (WAV 格式)
- ✅ Robot Framework 完整整合
- ✅ 統一配置管理系統

**技術改進**:
- ✅ 配置檔案重構 (移至 config 目錄)
- ✅ 模組化架構設計
- ✅ 完整錯誤處理與日誌系統
- ✅ 自動化測試覆蓋

**修復問題**:
- ✅ 解決配置檔案重複問題
- ✅ 修復模組匯入路徑問題
- ✅ 改善音訊設備相容性

#### v1.1.0 (計劃中 - 3個月內) - 移動設備整合
**預計功能**:
- [ ] iOS 自動化測試 (Appium + WebDriverAgent)
- [ ] Android 自動化測試 (UIAutomator2)
- [ ] 跨平台測試案例模板
- [ ] 設備管理與監控

**技術目標**:
- 🎯 完成移動設備測試模組
- 🎯 實現設備自動發現與連接
- 🎯 建立跨平台測試架構

#### v2.0.0 (計劃中 - 6個月內) - 硬體操作與電源管理
**預計功能**:
- [ ] MyCobot 280 機器手臂控制 (測試工具)
- [ ] SwitchBot 智慧插座整合 (被測設備電源管理)
- [ ] 實體面板操作自動化
- [ ] 視覺輔助定位系統
- [ ] 精度校準與驗證
- [ ] 設備電源狀態監控與自動化控制

**技術目標**:
- 🎯 實現機器手臂基礎控制
- 🎯 建立電源管理系統
- 🎯 完成實體設備操作能力

#### v3.0.0 (計劃中 - 12個月內) - 多感官檢測系統
**預計功能**:
- [ ] **音訊檢測系統**:
  - TTS 多語言語音合成（中文、英文、日文）
  - 48kHz/24bit 高品質音訊錄製與分析
  - 語音識別、噪音抑制、頻譜分析
  - 環境音檢測與音訊回饋驗證
- [ ] **視覺檢測系統**:
  - YOLOv8 深度學習燈號檢測
  - 動態角度變化檢測 (30-120 FPS)
  - 標記中心點追蹤與旋轉分析
  - 多語言 OCR 與模板匹配
- [ ] **多模態數據融合**:
  - 音訊與視覺數據同步
  - 融合分析與智慧決策
  - 統一時間戳與事件關聯

**技術目標**:
- 🔮 多感官檢測系統成熟
- 🔮 AI 輔助決策整合
- 🔮 自適應檢測閾值

#### v4.0.0 (計劃中 - 18個月內) - TestLink 整合與雲端化
**預計功能**:
- [ ] TestLink 測試案例管理整合
- [ ] 測試結果自動回報與追蹤
- [ ] 雲端測試資源整合
- [ ] CI/CD 自動化流程
- [ ] 測試數據分析與報告

**技術目標**:
- 🔮 完整測試案例管理生態
- 🔮 雲端測試資源整合
- 🔮 企業級 CI/CD 整合

#### v5.0.0 (長期願景 - 24個月內) - 智慧化測試平台
**預計功能**:
- [ ] 智慧型測試案例生成
- [ ] 自適應測試策略
- [ ] 完整自動化測試生態系統
- [ ] 開源社群與商業化支援

**技術目標**:
- 🌟 完整自動化測試生態系統
- 🌟 智慧型測試案例生成
- 🌟 自適應測試策略
- 🌟 開源社群與商業化
- [ ] 預測性故障檢測

### 🛠️ 技術架構演進

#### 當前架構 (v1.0)
```
Robot Framework
├── 語音控制模組 ✅
│   ├── TTS 引擎 (Google + 離線)
│   ├── 音訊錄製與播放
│   └── 基礎聲音檢測
├── 配置管理系統 ✅
└── 測試報告系統 ✅
```

#### 目標架構 (v3.0)
```
Robot Framework 核心
├── 移動應用測試 📱
│   ├── iOS 測試引擎
│   └── Android 測試引擎
├── 硬體操作控制 🤖
│   ├── 機器手臂控制
│   └── 實體設備操作
├── 語音互動系統 🎤
│   ├── 多語言 TTS
│   ├── 語音識別
│   └── 自然語言處理
├── 電源管理系統 🔌
│   ├── 智慧插座控制
│   └── 設備電源監控
├── 多感官檢測 👁️
│   ├── 音訊分析與識別
│   ├── 視覺檢測與 OCR
│   └── AI 輔助判斷
└── 整合分析平台 📊
    ├── 資料融合分析
    ├── 自動化報告
    └── 智慧決策支援
```

### 🎯 技術選型與考量

#### 核心框架選擇
| 技術 | 選擇原因 | 替代方案 |
|---|---|---|
| **Robot Framework** | 關鍵字驅動、易擴展、豐富生態 | Pytest, Selenium |
| **Python 3.8+** | 豐富庫支援、跨平台、易維護 | Java, JavaScript |
| **Appium** | 跨平台移動測試標準 | XCUITest, Espresso |
| **OpenCV** | 強大影像處理能力 | PIL, scikit-image |

#### 設備控制技術
| 設備類型 | 控制技術 | 通訊協議 | 功能角色 |
|---|---|---|---|
| **MyCobot 280** | pymycobot | USB Serial | 測試工具 (實體操作) |
| **SwitchBot 智慧插座** | switchbot-api | WiFi, REST API | 被測設備電源管理 |
| **iOS 設備** | WebDriverAgent + Appium | USB, WiFi | 被測目標 (應用測試) |
| **Android 設備** | UIAutomator2 + Appium | ADB, WiFi | 被測目標 (應用測試) |
| **IoT 面板** | 機器手臂操作 | 實體交互 | 被測目標 (面板功能) |

#### 檢測技術棧
| 檢測類型 | 主要技術 | 進階功能 | 性能規格 |
|---|---|---|---|
| **音訊發音** | gTTS + pyttsx3 | 多語言 TTS (中/英/日) | 語音合成 < 2秒 |
| **音訊錄製** | PyAudio + librosa | 48kHz/24bit 高品質 | 啟動延遲 < 0.5秒 |
| **語音識別** | SpeechRecognition | ASR + 關鍵字檢測 | 識別準確率 > 90% |
| **YOLO 檢測** | YOLOv8 + OpenCV | 燈號狀態識別 | 檢測精度 > 95% |
| **動態追蹤** | OpenCV Trackers | 角度變化分析 | 30-120 FPS |
| **OCR 識別** | Tesseract + PIL | 多語言文字識別 | 識別準確率 > 85% |

#### 測試管理技術棧
| 管理類型 | 主要技術 | 整合方式 | 同步性能 |
|---|---|---|---|
| **TestLink 整合** | python-testlink-api | XML-RPC, REST API | 即時同步 < 5分鐘 |
| **案例管理** | Robot Framework Parser | JSON 數據映射 | 同步成功率 > 99% |
| **結果回報** | xmlrpc.client | 即時狀態更新 | 回報延遲 < 30秒 |
| **任務調度** | APScheduler | 定時同步機制 | 調度精度 ±1秒 |
| **案例同步** | Robot Framework Parser | JSON 數據映射 | 同步成功率 > 99% |