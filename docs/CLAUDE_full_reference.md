# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個基於 Robot Framework 的綜合性多平台自動化測試系統，整合了移動應用測試（iOS/Android）、語音控制、電源管理（SwitchBot智慧插座）、以及多感官檢測（音訊/視覺）功能。

**主要特色:**
- 📱 iOS/Android 應用程式自動化測試 (Appium)
- 🎤 語音控制與驗證系統 (LocalVoiceVerifyingLibrary)
- 🔊 專業音訊硬體控制 (Scarlett 4i4 四通道獨立輸出)
- 🔌 SwitchBot 智慧插座電源管理
- 🤖 **機器手臂視覺檢測系統 (✅ Phase 1-3 已完成, 2025-11-13)**
  - MyCobot 280 按鈕 LED 顏色檢測（HSV 色彩空間）
  - ROI 互動式校準工具（✅ v5.0.0 增強：panel_section 分組、觀測角度移動）
  - 26 個 BDD 中文關鍵字
  - 17 個完整測試案例（快速測試、功能測試、整合測試）
- 🎯 **本機化視覺檢測系統 (✅ 已完成 - v4.1.1, 2025-11-18)**
  - 影像判定從 Server 遷移至本機端
  - 3 個測試環境（Taipei LAB / Taoyuan LAB / RV Car）
  - 8 種顏色檢測（藍/白/紅/綠/黃/橙/紫/關）
  - 11 級亮度檢測（0-100%，10% 步進）
  - 雙影像源支援（RTSP IP Camera / Socket USB Camera）
  - 32+ BDD 中文關鍵字（Given-When-Then）
  - 環境專屬 YAML 配置管理
  - ROI 互動式校準工具
  - **v4.1.1 修復：共用 Socket 連接（避免重複連接衝突）**
- 👁️ **多感官檢測系統 (✅ 已完成 - v1.0.0, 2025-11-07)**
  - IP Camera 視覺檢測（螢幕亮度變化）
  - RTSP 音訊檢測（提示音檢測）
  - 語音助手完整回應驗證（視覺 AND 聽覺）
- 📋 **TestLink 整合系統 (✅ 已完成 - v1.0.0, 2025-11-10)**
  - 自動回報測試結果到 TestLink
  - 中文 Gherkin 風格關鍵字
  - 批次回報與查詢功能

## 開發環境

**作業系統:** Ubuntu 24.04 (主要開發環境)
**Python 版本:** 3.12
**相依性管理:** uv
**測試框架:** Robot Framework 7.3.1+

## 核心命令

### 環境設置

```bash
# 安裝 uv (若尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境並安裝相依套件
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安裝所有相依套件
uv pip install -r requirements.txt

# 或直接使用 uv run 執行命令（自動管理環境）
uv run robot tests/
```

### 測試執行

```bash
# 執行所有測試
robot tests/

# 執行特定測試檔案
robot tests/physical_interaction/voice_test.robot

# 執行特定測試案例
robot --test "測試案例名稱" tests/path/to/test.robot

# 產生詳細報告
robot --outputdir results --loglevel DEBUG tests/

# 使用特定標籤執行測試
robot --include voice --include tts tests/

# dryrun 檢查語法
robot --dryrun tests/path/to/test.robot
```

### 移動測試相關

```bash
# 啟動 Appium 伺服器（背景執行）
./scripts/start_appium.sh --background

# 停止 Appium 伺服器
./scripts/stop_appium.sh

# 檢查 iOS 設備連接
./scripts/check_ios_device.sh --verbose

# 設置 iOS 測試環境
./scripts/setup_ios_testing.sh --install-deps --verbose

# 設置 Android 測試環境
./scripts/setup_android_testing.sh

# 執行 iOS 測試
robot tests/mobile/ios/ios_real_device_test.robot

# 執行 Android 測試
robot tests/mobile/android/android_app_test.robot
```

### SwitchBot 智慧插座工具

```bash
# 查詢所有 SwitchBot 設備
cd libraries/switchbot_smartplug_control
python get_device_id.py

# 控制插座開關
python plug_control.py on    # 開啟
python plug_control.py off   # 關閉
python plug_control.py status # 查詢狀態

# 檢查設備資訊
python check_device.py
```

### 語音系統測試

```bash
# 執行語音測試（基礎語音驗證）
robot tests/physical_interaction/voice_test.robot

# 單元測試
cd libraries/local_voice_verifying/tests/
python -m pytest . -v
```

### 專業音訊硬體控制 (Scarlett 4i4)

```bash
# 設置 Scarlett 4i4 獨立四通道輸出（每次開機執行）
cd libraries/voice_control
./setup_pipewire_routing_v3.sh

# 設定開機自動執行路由設定
mkdir -p ~/.config/systemd/user
cp pipewire_scarlett_setup.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable pipewire_scarlett_setup.service
systemctl --user start pipewire_scarlett_setup.service

# 播放音訊到指定聲道（1-4）
python3 ultimate_play.py file_example_WAV_2MG.wav 1  # 播放到輸出 1
python3 ultimate_play.py file_example_WAV_2MG.wav 3  # 播放到輸出 3

# 執行 Robot Framework 音訊測試
robot advanced_audio_test.robot

# 執行完整測試腳本
./run_tests.sh

# 診斷音訊系統
./diagnose_audio.sh
```

### TestLink 整合工具

```bash
# 驗證 TestLink 整合模組安裝
python3 scripts/verify_testlink_integration.py

# 執行 TestLink 整合測試
robot tests/testlink_integration/testlink_integration_test.robot

# 執行 TestLink 使用範例
robot libraries/testlink_integration/examples/testlink_example.robot

# 驗證 TestLink 配置
python3 -c "from config.testlink_config import validate_config, get_config_summary; validate_config(); print(get_config_summary())"
```

### 本機化視覺檢測系統 (v4.0.0)

```bash
# === 環境設定與驗證 ===

# 驗證環境配置
python3 -c "
from config.robot_arm.environment_config import EnvironmentConfig
for env in EnvironmentConfig.list_environments():
    config = EnvironmentConfig.get_environment(env)
    print(f'✅ {env}: {config[\"name\"]} - {config[\"image_source\"]}')
"

# 啟動機器手臂 Server (在 Jetson Nano 上)
cd ~/server
./run_server.sh

# 測試機器手臂連接
curl http://10.42.0.180:9000/health

# === ROI 校準工具 ===

# 啟動 ROI 校準工具（互動式網頁介面）
cd scripts
python web_roi_calibrator.py
# 瀏覽器開啟 http://localhost:5000

# === 執行視覺檢測測試 ===

# 執行基礎按鈕測試
robot tests/robot_arm/basic_button_test.robot

# 執行多環境測試
robot tests/robot_arm/multi_environment_test.robot

# 執行多色彩檢測測試
robot tests/robot_arm/multi_color_detection_test.robot

# 執行亮度檢測測試
robot tests/robot_arm/brightness_level_test.robot

# === 單元測試 ===

# 執行 EnvironmentConfig 測試
pytest tests/test_environment_config.py -v

# 執行 LocalVisionAnalyzer 測試
pytest libraries/robot_arm_control/tests/test_local_vision_analyzer.py -v

# 執行 ImageSourceManager 測試
pytest libraries/robot_arm_control/tests/test_image_source_manager.py -v

# === 產生 API 文檔 ===

# 產生 Robot Framework 關鍵字文檔
python -m robot.libdoc libraries/robot_arm_control/RobotArmKeywords.py \
    docs/RobotArmKeywords.html

# 開啟文檔
xdg-open docs/RobotArmKeywords.html

# === 診斷與故障排除 ===

# 驗證完整環境
./scripts/verify_environment.sh

# 測試 RTSP 串流 (taipei_lab)
ffmpeg -i rtsp://10.42.0.100:554/stream1 -frames:v 1 test_frame.jpg

# 檢查 debug 影像
ls -lh output/debug_*.jpg
xdg-open output/debug_latest.jpg

# 查看詳細日誌
tail -f libraries/robot_arm_control/logs/vision_analyzer.log
```

## 架構與關鍵目錄

### 核心架構模式

專案採用**模組化設計**，各子系統可獨立運作或協同配合：

```
Robot Framework 核心
├── 移動應用測試 (Appium)
├── 語音控制系統
│   ├── LocalVoiceVerifyingLibrary (基礎語音驗證)
│   └── AudioKeywords (專業音訊硬體控制)
├── 電源管理 (SwitchBot)
├── 多感官檢測 (✅ 已完成)
├── 本機化視覺檢測 (✅ 已完成 v4.0.0)
│   ├── LocalVisionAnalyzer (本機影像分析)
│   ├── ImageSourceManager (雙影像源管理)
│   ├── EnvironmentConfig (多環境配置)
│   └── RobotArmKeywords (32+ BDD 關鍵字)
└── TestLink 整合 (✅ 已完成)
```

### 目錄結構

```
robot-multiplatform-automation/
├── config/                      # 統一配置管理
│   ├── voice_config.py         # 語音系統配置
│   ├── switchbot_config.py     # SwitchBot 配置
│   ├── testlink_config.py      # TestLink 配置
│   ├── robot_arm/              # 機器手臂視覺檢測配置（✅ v4.0.0）
│   │   ├── environment_config.py      # 環境配置管理
│   │   ├── taipei_lab_buttons.yaml    # 台北實驗室配置
│   │   ├── taoyuan_lab_buttons.yaml   # 桃園實驗室配置
│   │   └── rv_car_buttons.yaml        # RV Car 配置
│   └── mobile/                 # 移動測試配置
│       ├── appium_config.py    # Appium 統一配置
│       └── ios_config.py       # iOS 專屬配置
│
├── libraries/                   # 自定義 Robot Framework Libraries
│   ├── local_voice_verifying/  # 語音驗證庫
│   ├── voice_control/          # 專業音訊硬體控制（Scarlett 4i4）
│   ├── switchbot_smartplug_control/  # SwitchBot 控制
│   ├── testlink_integration/   # TestLink 整合
│   ├── robot_arm_control/      # 機器手臂視覺檢測（✅ v4.0.0）
│   │   ├── RobotArmKeywords.py        # Robot Framework 關鍵字（32+）
│   │   ├── local_vision_analyzer.py   # 本機影像分析
│   │   ├── image_source_manager.py    # 影像源管理
│   │   ├── image_sources/             # 影像源實作
│   │   │   ├── rtsp_source.py         # RTSP IP Camera
│   │   │   └── socket_image_source.py # Socket USB Camera
│   │   └── tests/                     # 單元測試
│   └── mobile_testing/common/  # 移動測試通用庫
│
├── resources/                   # Robot Framework 資源與關鍵字
│   ├── common_keywords.robot   # 通用關鍵字
│   ├── mobile_keywords.robot   # 移動設備關鍵字
│   ├── switchbot_keywords.robot # SwitchBot 關鍵字
│   ├── testlink_keywords.robot # TestLink 關鍵字
│   ├── api_keywords.robot      # API 關鍵字
│   └── web_keywords.robot      # Web 關鍵字
│
├── tests/                       # Robot Framework 測試案例
│   ├── mobile/                 # 移動應用測試
│   │   ├── ios/               # iOS 測試案例
│   │   └── android/           # Android 測試案例
│   ├── robot_arm/              # 機器手臂視覺檢測測試（✅ v4.0.0）
│   │   ├── basic_button_test.robot
│   │   ├── multi_environment_test.robot
│   │   ├── multi_color_detection_test.robot
│   │   └── brightness_level_test.robot
│   ├── physical_interaction/   # 實體互動測試
│   ├── power_management/       # 電源管理測試
│   ├── testlink_integration/   # TestLink 整合測試
│   └── test_environment_config.py  # 環境配置單元測試
│
├── scripts/                     # 輔助腳本
│   ├── web_roi_calibrator.py   # ROI 校準工具（✅ v5.0.0，ruamel.yaml 格式保留）
│   ├── robot_arm_server.py     # 機器手臂 Server（Jetson Nano）
│   └── verify_environment.sh   # 環境驗證腳本
│
├── docs/                        # 文檔
│   ├── vision_detection_local_migration_plan.md    # 遷移計畫（✅ v4.0.0）
│   ├── vision_detection_local_spec.md              # 技術規格
│   ├── vision_detection_tdd_guide.md               # TDD 開發指南
│   ├── vision_detection_deployment_checklist.md    # 部署檢查清單
│   ├── vision_detection_quick_start_guide.md       # 快速上手指南
│   ├── vision_detection_troubleshooting_guide.md   # 故障排除指南
│   └── keyword_design_guidelines.md                # BDD 關鍵字設計規範
│
└── results/                     # 測試結果輸出
```

### 配置系統架構

**重要:** 本專案採用**統一配置管理系統**，所有配置集中在 `config/` 目錄：

- `config/voice_config.py` - 語音系統所有配置
- `config/switchbot_config.py` - SwitchBot 配置（支援多來源：專案根目錄 .env、系統環境變數）
- `config/testlink_config.py` - TestLink 配置（支援 API URL、API Key、專案設定等）
- `config/robot_arm/environment_config.py` - 本機化視覺檢測環境配置（✅ v4.1.0，支援 3 個測試環境 + 多 Camera）
- `config/robot_arm/config_loader.py` - YAML 配置統一載入器（✅ v1.0.0，2025-11-18 新增）
- `config/robot_arm/*.yaml` - 環境專屬按鈕與燈光配置（YAML 格式）
- `config/mobile/appium_config.py` - Appium 統一配置（iOS + Android）
- `config/mobile/ios_config.py` - iOS 專屬配置與設備管理

**配置優先順序:**
1. 系統環境變數 (最高優先)
2. 專案根目錄 `.env` 檔案
3. 配置檔案中的預設值

**機器手臂配置系統（v4.1.0）:**
- **EnvironmentConfig**: 管理環境配置（taipei_lab, taoyuan_lab, rv_car）
  - 支援多 IP Camera 配置（taipei_lab 有 3 個 Camera：level1, level2, motor）
  - 混合模式支援（RTSP + Socket）
  - 環境名稱映射（laboratory ↔ taipei_lab, rv_vehicle ↔ rv_car）
- **ConfigLoader**: 載入環境專屬 YAML 配置
  - 按鈕配置管理（buttons）
  - 環境燈光配置管理（environment_lights）
  - 類別級別快取機制
  - 深拷貝保護（避免外部修改影響原始配置）

**使用範例:**
```python
from config.robot_arm.environment_config import EnvironmentConfig
from config.robot_arm.config_loader import ConfigLoader

# 取得環境配置
config = EnvironmentConfig.get_environment("taipei_lab")
cameras = EnvironmentConfig.get_cameras("taipei_lab")  # 取得 3 個 Camera

# 載入按鈕與燈光配置
loader = ConfigLoader("taipei_lab")
buttons = loader.get_buttons()  # 13 個按鈕
lights = loader.get_environment_lights()  # 1 個燈光陣列（12 燈泡）
light1 = loader.get_button("light1")  # 取得特定按鈕
```

### 移動測試架構

本專案使用 **Appium 2.x** 進行移動應用自動化測試：

**iOS 測試流程:**
1. 使用 `libimobiledevice-utils` 檢測設備
2. 自動獲取 UDID 和設備資訊
3. 透過 XCUITest 驅動執行測試
4. 支援 Ubuntu 24.04 真機測試

**Android 測試流程:**
1. 使用 ADB 檢測設備
2. 透過 UiAutomator2 驅動執行測試
3. 支援真機和模擬器

**關鍵配置檔案:**
- `config/mobile/appium_config.py` - 統一的 Appium 配置（包含 iOS 和 Android）
- `config/mobile/ios_config.py` - iOS 專屬配置和設備管理函數

## 編碼規範與標準

### Robot Framework BDD 設計規範

本專案遵循嚴格的 BDD (Behavior-Driven Development) 設計原則。所有 Robot Framework 關鍵字和測試案例都必須符合以下規範。

#### 核心原則

1. **Gherkin 語法結構** - 所有測試案例必須使用 Gherkin 語法（Given-When-Then-And）
2. **中文關鍵字** - 所有 Robot Framework 關鍵字名稱必須使用中文
3. **業務層級抽象** - 關鍵字應描述「做什麼」(What)，而非「如何做」(How)
4. **單一職責原則** - 每個關鍵字只負責一件核心任務
5. **詳細文檔** - [Documentation] 應包含詳細說明和使用範例
6. **RETURN 語句** - 使用現代 RETURN 語句，避免舊式 [Return]

#### 完整設計指南

⭐ **必讀文檔：**
- 📖 [Keyword 設計規範](docs/keyword_design_guidelines.md) - 最完整的 BDD 設計指南
  - Gherkin / BDD 整合
  - 命名規範與抽象層級
  - Docstring 標準範本
  - 職責劃分與錯誤處理
- 📖 [視覺檢測設計文檔](docs/robot_arm_vision_detection_design.md) - 實際應用範例

⭐ **最佳實踐範本：**
- `libraries/voice_control/VoiceControlKeywords.py` - 語音控制關鍵字（完整 Docstring）
- `libraries/robot_arm_control/RobotArmKeywords.py` - 機器手臂關鍵字（v3.0.0，26 個 BDD 關鍵字）
- `libraries/testlink_integration/TestLinkConnector.py` - TestLink 整合（69 個中文 Gherkin 關鍵字）

#### BDD 關鍵字類型說明

**Given（給定）** - 設定前置條件或系統狀態
- 範例：`Given TTS 引擎已設定為 "gtts"`
- 目的：建立已知的、穩定的測試起點

**When（當）** - 觸發核心業務動作或用戶操作
- 範例：`When 用戶檢測第 "light1" 按鈕的燈光狀態`
- 目的：模擬用戶或系統執行的單一關鍵行為

**Then（那麼）** - 驗證結果或狀態變化
- 範例：`Then 按鈕燈光應該為 "blue" 色`
- 目的：斷言測試的預期結果是否達成
- 要求：驗證失敗時使用 `raise AssertionError("描述性錯誤訊息")`

**And（而且）/ But（但是）** - 串連同類型步驟
- 範例：`And 回應內容應該包含 "${expected_content}"`
- 目的：避免重複使用 Given/When/Then

#### 快速範例

```robotframework
# ✅ 正確範例 - 業務層級抽象
Given 機器手臂已連接到遠端伺服器
When 用戶檢測第 "light1" 按鈕的燈光狀態
Then 按鈕燈光應該為 "blue" 色
And 檢測信心度應該大於 0.9

# ✅ 正確範例 - API 測試
Given API 服務已在端點 "${endpoint}" 運行
When 使用者發送 GET 請求到 "${url}"
Then 回應狀態碼應該為 "${status_code}"
And 回應內容應該包含 "${expected_content}"

# ❌ 錯誤範例 - 技術層級暴露（已棄用）
Given API Service Is Running At Endpoint "${endpoint}"
When User Sends GET Request To "${url}"
Click Button "xpath=//button[@id='submit']"  # 不應暴露技術定位符
```

#### 抽象層級對比

**好的例子（業務層級）：**
- `When 用戶透過機器手臂開啟第 "1" 號燈光`
- `Then 機器手臂操作應該成功完成`
- `When 用戶檢測多個按鈕的燈光狀態`

**壞的例子（技術實現層級）：**
- `Send Angles To Robot [10, 20, 30, 40, 50, 60]` ❌
- `Click Element "xpath=//button[@class='light1']"` ❌
- `HTTP Get Request To "http://10.42.0.180:9000/detect"` ❌

#### 其他重要規範

7. **日期格式** - 寫入日期前須檢查現在日期，格式為 YYYY-MM-DD
8. **中文文檔** - 所有文件和註解都應使用中文
9. **工具使用** - 使用 `robotidy` 格式化，使用 `libdoc` 產生文檔

### Python 程式碼規範

1. **函式級註解:** 所有函式都需要提供詳細的中文註解
2. **模組匯入:** 使用統一配置系統（從 `config` 模組匯入）
3. **錯誤處理:** 完善的異常處理與日誌記錄
4. **日誌系統:** 使用 loguru 進行統一日誌管理

### Shell 指令規範

1. **Ubuntu 相容性:** 終端機指令使用 shell 相容語法
2. **指令分隔:** 使用 `&&` 分隔指令（非換行）
3. **架構建立:** 使用指令方式建立專案架構，勿直接產生

## 語音系統架構說明

本專案包含**完整的語音輸入/輸出與多感官檢測系統**：

### 1. LocalVoiceVerifyingLibrary (`libraries/local_voice_verifying/`)
**用途:** 聲音檢測與驗證（輸入端）
- 音訊錄製
- 聲音檢測與驗證（MFCC + DTW）
- Robot Framework 整合

**重要變更（2025-11-06）：**
- ⚠️ TTS 功能已遷移至 `voice_control` 模組
- ⚠️ `Speak Text`, `Set TTS Language`, `Set TTS Speed` 等關鍵字已移除
- ✅ 專注於聲音檢測功能（核心職責）

**測試案例:** `tests/physical_interaction/voice_test.robot` (需要更新)

### 2. VoiceControlKeywords (`libraries/voice_control/`)
**用途:** 語音輸出控制（Focusrite Scarlett 4i4 第四代）
- **TTS 整合** - Google TTS (gtts) + 離線 TTS (pyttsx3)
- **獨立四通道輸出控制** - 精確控制物理輸出 1, 2, 3, 4
- **PipeWire 路由管理** - 透過 PipeWire 創建虛擬音訊設備
- **Robot Framework 整合** - 提供完整的語音輸出關鍵字

**核心功能:**
- `TTSManager.py` - TTS 引擎管理（從 local_voice_verifying 遷移）
- `AudioPlayer.py` - Scarlett 4i4 聲道控制
- `VoiceControlKeywords.py` - Robot Framework 關鍵字整合
- `setup_pipewire_routing_v3.sh` - PipeWire 路由設定腳本

**主要關鍵字:**
- `播放文字到聲道` - 文字轉語音並播放到指定聲道
- `設定 TTS 引擎` - 切換 gtts/pyttsx3
- `設定 TTS 語言` - 設定語言（en, zh-TW, ja等）
- `設定 TTS 語速` - 設定語速

**測試案例:**
- `tests/voice_control/voice_tts_integration_test.robot` - TTS 整合測試

**系統需求:**
- Focusrite Scarlett 4i4 (第四代) 音訊介面
- PipeWire 音訊系統
- ALSA Scarlett GUI (硬體路由設定)
- Ubuntu 24.04 (主要測試環境)

### 3. IPCamAudioDetection (`libraries/ipcam_light_detection/`)
**用途:** IP Camera 音訊檢測（✅ 新增 v1.2.0, 2025-11-07）
- **RTSP 音訊提取** - 使用 FFmpeg 從 RTSP 串流提取音訊
- **背景錄音** - 非阻塞的背景錄音機制
- **音訊裁切** - 去除開頭雜音
- **聲音檢測** - 整合 SoundDetector (MFCC + DTW)

**核心功能:**
- `start_background_recording()` - 啟動背景錄音
- `stop_background_recording()` - 停止錄音並取得檔案
- `trim_audio_start()` - 裁切音訊開頭
- `detect_sound_in_file()` - 比對音訊與參考聲音

**Robot Framework 關鍵字:**
- `啟動背景錄音` - 開始錄音
- `停止背景錄音` - 停止錄音
- `裁切音訊開頭` - 裁切音訊
- `檢測 RTSP 音訊` - 比對音訊檔案

### 4. VoiceAssistantDetection (`libraries/multimodal_detection/`)
**用途:** 語音助手多感官檢測整合（✅ 新增 v1.0.0, 2025-11-07）
- **視覺檢測** - IPCamLightDetection（螢幕亮度變化）
- **聽覺檢測** - IPCamAudioDetection（提示音檢測）
- **語音觸發** - VoiceControlKeywords（TTS 播放喚醒詞）
- **AND 驗證邏輯** - 視覺和聽覺都要通過

**核心功能:**
- `test_voice_assistant_response()` - 完整的語音助手回應測試
- 自動整合視覺、聽覺檢測
- 詳細的失敗原因診斷

**測試流程:**
```
1. 連接 IP Camera
2. 啟動背景錄音
3. 播放喚醒詞（透過 Scarlett）
4. 視覺檢測（監控亮度變化）
5. 停止錄音並分析音訊
6. AND 驗證：視覺 AND 聽覺
```

**Robot Framework 關鍵字:**
- `測試語音助理回應` - 執行完整測試
- `驗證語音助手回應成功` - 驗證結果
- `記錄語音助手檢測結果` - 記錄詳細結果

**測試案例:** `tests/voice_assistant/multimodal_detection_test.robot` (待建立)

**文檔:**
- `docs/voice_assistant_multimodal_detection_plan.md` - 設計文檔
- `docs/voice_assistant_multimodal_detection_implementation_summary.md` - 實作摘要
- `docs/voice_control_tts_migration.md` - TTS 遷移指南

## 重要設計決策

### 1. 配置管理統一化

**原則:** 所有配置集中管理於 `config/` 目錄，避免重複配置檔案。

**SwitchBot 配置整合範例:**
- 移除 `libraries/switchbot_smartplug_control/switchbot_config.py`
- 統一使用 `config/switchbot_config.py`
- 所有模組透過 `from config.switchbot_config import ...` 匯入

### 2. 移動測試配置架構

**設計考量:**
- `appium_config.py` - 包含 iOS 和 Android 的通用配置
- `ios_config.py` - iOS 專屬配置和設備管理函數
- 自動設備檢測和 UDID 管理
- 支援多設備並行測試架構

### 3. API 認證方式

**SwitchBot API:**
- 改用直接 HTTP API 呼叫
- 移除 `pyswitchbot` 依賴（存在兼容性問題）
- 實作 HTTP 簽名算法（符合官方要求）

### 4. TestLink 整合架構（✅ 新增 2025-11-10）

**設計原則:**
- 無第三方依賴 - 直接使用 Python 內建 `xmlrpc.client`
- 統一配置管理 - 遵循專案配置系統架構
- 中文 Gherkin 風格 - 所有關鍵字使用中文 + Given-When-Then 結構
- 完整錯誤處理 - API 重試機制（3 次，延遲 2 秒）

**TestLink API 選擇:**
- 避免 `python-testlink-api`（參考 SwitchBot 經驗，避免兼容性問題）
- 使用 XML-RPC 直接呼叫（官方支援，穩定可靠）
- 完整的 API 封裝（專案、測試計畫、Build、測試案例、測試結果）

**核心功能:**
- 自動連接與初始化（自動查找或建立 Build）
- 單一/批次測試結果回報
- 測試案例資訊查詢
- 執行結果歷史查詢

**文檔:**
- `libraries/testlink_integration/README.md` - 完整模組文檔
- `docs/testlink_integration_setup_guide.md` - 設置與使用指南

### 5. 機器手臂角色定位

**重要概念:**
- MyCobot 280 定位為**測試工具**（非被測對象）
- 功能驗證與校準存放在 `libraries/` 目錄
- TestLink 測試案例專注於被測產品

## 測試執行注意事項

### Robot Framework 語法陷阱

**Log 關鍵字使用:**
```robotframework
# ❌ 錯誤 - URL 會被誤認為日誌級別
Log    1. Open Application    http://localhost:4723    [capabilities]

# ✅ 正確 - 將 URL 嵌入描述文字
Log    1. Open Application 使用 http://localhost:4723 和 capabilities 字典
```

### 移動測試前置作業

**iOS 測試前:**
1. 確認設備已連接並信任電腦
2. 確認設備已開啟開發者模式
3. 執行 `./scripts/check_ios_device.sh` 驗證連接
4. 啟動 Appium 伺服器

**Android 測試前:**
1. 確認 ADB 可檢測到設備 (`adb devices`)
2. 確認 UiAutomator2 驅動已安裝
3. 啟動 Appium 伺服器

### SwitchBot 測試前置作業

1. 複製 `.env.example` 為 `.env`
2. 填入 `SWITCHBOT_TOKEN` 和 `SWITCHBOT_SECRET`
3. 執行 `get_device_id.py` 取得設備 ID
4. 更新 `.env` 中的 `SWITCHBOT_DEVICE_ID`

### TestLink 測試前置作業（✅ 新增 2025-11-10）

1. 確保 TestLink 服務正在運行
2. 複製 `.env.example` 為 `.env`（如果尚未複製）
3. 在 TestLink 中取得 API Key：
   - 登入 TestLink → My Settings → API interface
   - 勾選 "Enable API key" → Generate a new key
4. 填入 `.env` 中的 TestLink 配置：
   - `TESTLINK_API_URL` - TestLink API 端點
   - `TESTLINK_API_KEY` - API 金鑰
   - `TESTLINK_PROJECT_NAME` - 專案名稱（選填）
   - `TESTLINK_TEST_PLAN_NAME` - 測試計畫名稱（選填）
   - `TESTLINK_BUILD_NAME` - Build 名稱（選填）
5. 執行驗證：`python3 scripts/verify_testlink_integration.py`

## 專案維護準則

### 修改程式碼前

1. **確認 spec.md:** 遵循 `spec.md` 中的系統規格
2. **更新 todo.md:** 任務完成後更新進度
3. **更新 keywords_readme.md:** 修改 Robot 程式碼後更新關鍵字文檔

### 檔案變更規範

1. **避免建立非必要檔案:** 優先編輯現有檔案
2. **禁止主動建立文檔:** 除非明確要求，否則不建立 .md 或 README 檔案
3. **遵循專案結構:** 新檔案需符合既定目錄結構

### 版本控制

**當前狀態 (2026-02-12):**
- Phase 1 基礎架構：✅ 完成
- iOS 真機測試環境：✅ 完成（2025-06-27）
  - 支援 iPhone 13 系列（已測試：iPhone 13 mini, iOS 18.6.2）
  - libimobiledevice 1.3.0 工具鏈完整安裝
  - Appium 2.x + XCUITest 驅動整合
- Android 環境修復：✅ 完成（2025-07-10）
- SwitchBot 電源管理：✅ 完成
- 全面中文關鍵字標準化：✅ 完成
- **語音控制 TTS 整合：✅ 完成（2025-11-06）**
  - TTS 功能遷移至 voice_control 模組
  - 完整的 Scarlett 4i4 + TTS 整合
  - 10+ 測試案例驗證通過
- **多感官檢測系統：✅ 完成（2025-11-07）**
  - IP Camera 音訊檢測（RTSP 串流）
  - 語音助手完整回應驗證（視覺 + 聽覺）
  - AND 驗證邏輯實作
- **TestLink 整合系統：✅ 完成（2025-11-10）**
  - 完整的 TestLink XML-RPC API 封裝
  - 69 個中文 Gherkin 風格關鍵字
  - 單一/批次測試結果回報
  - 完整文檔與 20 個測試案例
- **機器手臂視覺檢測系統：✅ 完成（2025-11-13）**
  - Phase 1: VisionAnalyzer + JSON 命令（HSV 顏色檢測、多幀平均）
  - Phase 2: ROI 校準工具（互動式選擇、YAML 配置）
  - Phase 3: Robot Framework 整合（26 個 BDD 關鍵字、17 個測試案例）
  - RobotArmKeywords v3.0.0（新增 10 個視覺檢測關鍵字）
  - 完整測試文檔與使用指南
- **本機化視覺檢測系統：✅ 完成（2025-11-18, v4.0.0）**
  - Phase 1-2: LocalVisionAnalyzer + ImageSourceManager（影像分析與雙影像源）
  - Phase 3: 環境管理與配置系統（3 環境 + YAML 配置）
  - Phase 5: 完整文檔系統（部署、快速上手、故障排除）
  - RobotArmKeywords v4.0.0（32+ BDD 關鍵字）
  - 8 種顏色 + 11 級亮度檢測
  - 支援 RTSP (taipei_lab) 與 Socket (taoyuan_lab/rv_car) 影像源
- **Socket 連接衝突修復：✅ 完成（2025-11-18, v4.1.1）**
  - **問題：** MyCobotSocketController 與 SocketImageSource 重複連接衝突
  - **解決：** 共用 Socket 連接機制
  - **修改檔案：**
    - `SocketImageSource`: 新增 `shared_socket` 參數支援
    - `ImageSourceManager`: 傳遞共用 Socket
    - `RobotArmKeywords`: 智能檢測並傳遞 `controller.socket`
  - **向後兼容：** 保持獨立模式（無參數調用）
  - **新增功能：** TCP 粘包防護（`time.sleep(0.05)`）
- **ROI 校準工具增強：✅ 完成（2026-02-12, v5.0.0）**
  - **YAML 格式保留：** 使用 `ruamel.yaml` 取代 PyYAML，完整保留 flow style、註解、排序
  - **UI 面板分組：** 按鈕依 `panel_section` 分組顯示（如「面板 3611A」、「面板 3611C」）
  - **觀測角度移動：** 新增 🎯「觀測」按鈕，可移動手臂到按鈕設定的 `observe_angles`
  - **新增 API：** `POST /api/robot/move_to_observe` — 依 button_id 移動手臂至觀測位置
  - **修改檔案：**
    - `scripts/web_roi_calibrator.py`: `load_config`/`save_config` 改用 ruamel.yaml；`get_button_list` 回傳 panel_section/observe_angles；新增 move_to_observe 路由
    - `scripts/templates/roi_annotator.html`: displayButtons 依 panel_section 分組；新增 moveToObservePosition() JS 函式
  - **Socket 控制架構確認：** 整個系統統一透過 TCP Socket (port 9000) 控制，`MyCobotSocketController` → `pymycobot.MyCobot280Socket` → 遠端 `robot_arm_server.py`

**下一階段重點:**
- **v5.1.0: ROI 校準工具進階功能**（規劃中）
  - 觀測角度微調與儲存
  - 即時影像預覽整合
- **v4.2.0: HTTP API Server 重構**（規劃中）
  - Socket (9000) 專注機器手臂控制
  - HTTP API (8000) 專注影像傳輸
  - 職責分離、並發安全、易於擴展
- **Phase 4: 真機測試與調校**（需硬體環境）
- 進階 TestLink 功能（測試案例同步、自動建立 Bug）
- 多感官檢測測試案例完善

## 常見問題與解決方案

### 1. 模組匯入錯誤

**問題:** `ModuleNotFoundError: No module named 'config'`

**解決:**
```bash
# 確保在專案根目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 設定 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 驗證
python -c "from config.voice_config import AUDIO_CONFIG; print('✅ 修復成功')"
```

### 2. Appium 連接失敗

**iOS 問題:**
```bash
# 檢查設備連接
idevice_id -l

# 檢查開發者模式
./scripts/check_ios_device.sh --verbose

# 重啟 usbmuxd
sudo systemctl restart usbmuxd
```

**Android 問題:**
```bash
# 檢查 ADB 連接
adb devices

# 重啟 ADB 服務
adb kill-server && adb start-server
```

### 3. SwitchBot API 認證失敗

**檢查步驟:**
1. 確認 `.env` 檔案中的 TOKEN 和 SECRET 正確
2. 驗證配置載入：`python -c "from config.switchbot_config import SWITCHBOT_TOKEN; print(SWITCHBOT_TOKEN)"`
3. 測試 API 連接：`cd libraries/switchbot_smartplug_control && python check_device.py`

### 4. Scarlett 4i4 音訊問題

**虛擬設備未創建:**
```bash
# 檢查虛擬設備是否存在
wpctl status | grep Scarlett

# 手動執行路由設定
cd libraries/voice_control
./setup_pipewire_routing_v3.sh

# 檢查服務狀態
systemctl --user status pipewire_scarlett_setup.service
```

**音訊播放失敗:**
```bash
# 診斷音訊系統
cd libraries/voice_control
./diagnose_audio.sh

# 檢查硬體是否被識別
aplay -l | grep Scarlett

# 檢查用戶是否在 audio 群組
groups | grep audio
sudo usermod -a -G audio $USER
# 需要登出重新登入
```

**Direct 模式未設定:**
1. 安裝 `alsa-scarlett-gui`
2. 開啟工具設定 Routing 為 Direct 模式
3. 儲存設定並重啟音訊服務

### 5. TestLink 連接問題（✅ 新增 2025-11-10）

**連接失敗:**
```bash
# 錯誤: ConnectionError: 無法連接到 TestLink

# 解決步驟:
# 1. 確認 TestLink 服務正在運行
curl http://your-testlink-server/testlink/

# 2. 檢查 API URL 是否正確
python3 -c "from config.testlink_config import TESTLINK_API_URL; print(TESTLINK_API_URL)"

# 3. 測試連接
python3 scripts/verify_testlink_integration.py
```

**API Key 無效:**
```bash
# 錯誤: RuntimeError: API 呼叫失敗: Invalid API Key

# 解決步驟:
# 1. 確認 API Key 已在 TestLink 中啟用
# 2. 重新產生 API Key（登入 TestLink → My Settings → API interface）
# 3. 更新 .env 檔案中的 TESTLINK_API_KEY
# 4. 驗證配置
python3 -c "from config.testlink_config import validate_config; validate_config()"
```

**找不到專案或測試計畫:**
```bash
# 錯誤: ValueError: 找不到專案: 我的專案

# 解決步驟:
# 1. 確認專案名稱拼寫正確（區分大小寫）
# 2. 確認用戶有權限訪問該專案
# 3. 在 TestLink 介面中確認專案和測試計畫存在
# 4. 列出所有可用專案
python3 -c "from libraries.testlink_integration.api_client import TestLinkAPIClient; client = TestLinkAPIClient(); client.connect(); print(client.get_projects())"
```

**測試案例不存在:**
```bash
# 錯誤: ValueError: 找不到測試案例: TEST-001

# 解決步驟:
# 1. 確認測試案例已加入測試計畫
# 2. 檢查測試案例外部 ID 是否正確
# 3. 確認測試案例未被刪除
```

### 6. Robot Framework 語法錯誤

**常見問題:**
- 使用舊式 `[Return]` 而非 `RETURN`
- Log 關鍵字參數順序錯誤
- 缺少中文關鍵字名稱

**驗證語法:**
```bash
robot --dryrun tests/path/to/test.robot
```

## 技術棧總覽

**核心框架:**
- Robot Framework 7.3.1+
- Python 3.12
- pipenv

**移動測試:**
- Appium 2.0.1
- XCUITest 驅動 v9.9.0 (iOS)
- UiAutomator2 驅動 v4.2.5 (Android)
- libimobiledevice-utils (iOS 設備管理)
- ADB (Android 設備管理)

**語音系統:**
- gTTS (Google TTS)
- pyttsx3 (離線 TTS)
- PyAudio (音訊錄製)

**專業音訊硬體:**
- PipeWire (音訊路由系統)
- ALSA Scarlett GUI (硬體控制)
- pactl / pw-link (音訊設備管理)
- FFmpeg / SoX (音訊處理)

**電源管理:**
- SwitchBot HTTP API
- requests (HTTP 客戶端)

**TestLink 整合:**
- Python 內建 xmlrpc.client（XML-RPC API）
- loguru（日誌管理）
- python-dotenv（環境變數）

**其他工具:**
- pytest (單元測試)
- loguru (日誌管理)
- python-dotenv (環境變數)

## 專案文檔

**核心文檔:**
- `README.md` - 專案說明、安裝與執行方式
- `spec.md` - 系統規格書（流程圖、循序圖、關聯圖等 UML）
- `todo.md` - 任務清單與進度追蹤
- `keywords_readme.md` - Robot Framework 關鍵字說明
- `.github/copilot-instructions.md` - 開發規範與指引

**模組文檔:**
- `libraries/switchbot_smartplug_control/README.md` - SwitchBot 模組說明
- `libraries/local_voice_verifying/README.md` - 語音驗證庫說明
- `libraries/voice_control/README.md` - Scarlett 4i4 音訊控制說明
- `libraries/voice_control/ROBOT_FRAMEWORK_README.md` - Robot Framework 整合指南
- `libraries/robot_arm_control/README.md` - 機器手臂控制模組說明
- `libraries/robot_arm_control/BUTTON_SETUP_GUIDE.md` - 按鈕配置指南
- `libraries/testlink_integration/README.md` - TestLink 整合模組說明
- `docs/ios_device_setup.md` - iOS 設置指南
- `docs/ios_test_execution_guide.md` - iOS 測試執行指南
- `docs/testlink_integration_setup_guide.md` - TestLink 整合設置指南

**機器手臂視覺檢測文檔（✅ 新增 2025-11-13）:**
- `docs/robot_arm_vision_detection_design.md` - 視覺檢測設計文檔（Phase 1-6 完整規劃）
- `docs/robot_arm_vision_calibration_guide.md` - ROI 校準操作指南
- `docs/robot_arm_vision_phase3_completion_summary.md` - Phase 3 完成報告

**本機化視覺檢測文檔（📋 新增 2025-11-16）:**
- `docs/vision_detection_local_migration_plan.md` - 影像判定本機化遷移計畫（完整規劃）
- `docs/vision_detection_local_spec.md` - 技術規格書（含 UML 圖表）
- `docs/vision_detection_tdd_guide.md` - TDD 開發指南（測試驅動開發）
- `tests/robot_arm/VISION_DETECTION_TESTS_README.md` - 測試案例詳細說明
- `docs/keyword_design_guidelines.md` - BDD 關鍵字設計規範（最佳實踐）

## 開發工作流程

### 1. 協調者模式（迴旋標模式）

當使用協調者模式時，需將所有任務完成報告記錄在 `report.md` 中。

### 2. 架構模式

完成架構後需產生：
- `spec.md` - 規格文件（包含 UML 圖）
- `todo.md` - 任務清單，額外將需要人工協助及實體裝置，測試及分析的區塊分別出來

### 3. Code 模式

1. 修改前確認 `spec.md`
2. 遵循編碼規範
3. 完成後更新 `todo.md` 進度
4. 修改 Robot 程式碼後更新 `keywords_readme.md`

### 4. 專案完成後

撰寫或更新 `README.md`，包含：
- 專案描述
- 安裝方式
- 執行方式
- 使用範例

## 結語

本專案遵循**模組化、標準化、文檔化**的開發原則，確保各子系統可獨立運作或協同配合。開發時請務必遵循本文件中的規範與準則，並保持與既有架構的一致性。

## Shell Tools Usage Guidelines
⚠️ **IMPORTANT**: Use the following specialized tools instead of traditional Unix commands: (Install if missing)
| Task Type | Must Use | Do Not Use |
|-----------|----------|------------|
| Find Files | `fd` | `find`, `ls -R` |
| Search Text | `rg` (ripgrep) | `grep`, `ag` |
| Analyze Code Structure | `ast-grep` | `grep`, `sed` |
| Interactive Selection | `fzf` | Manual filtering |
| Process JSON | `jq` | `python -m json.tool` |
| Process YAML/XML | `yq` | Manual parsing |
====