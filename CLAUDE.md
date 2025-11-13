# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個基於 Robot Framework 的綜合性多平台自動化測試系統，整合了移動應用測試（iOS/Android）、語音控制、電源管理（SwitchBot智慧插座）、以及多感官檢測（音訊/視覺）功能。

**主要特色:**
- 📱 iOS/Android 應用程式自動化測試 (Appium)
- 🎤 語音控制與驗證系統 (LocalVoiceVerifyingLibrary)
- 🔊 專業音訊硬體控制 (Scarlett 4i4 四通道獨立輸出)
- 🔌 SwitchBot 智慧插座電源管理
- 🤖 機器手臂控制實體面板操作 (計劃中)
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
└── TestLink 整合 (✅ 已完成)
```

### 目錄結構

```
robot-multiplatform-automation/
├── config/                      # 統一配置管理
│   ├── voice_config.py         # 語音系統配置
│   ├── switchbot_config.py     # SwitchBot 配置
│   ├── testlink_config.py      # TestLink 配置（✅ 新增）
│   └── mobile/                 # 移動測試配置
│       ├── appium_config.py    # Appium 統一配置
│       └── ios_config.py       # iOS 專屬配置
│
├── libraries/                   # 自定義 Robot Framework Libraries
│   ├── local_voice_verifying/  # 語音驗證庫（已實現）
│   ├── voice_control/          # 專業音訊硬體控制（Scarlett 4i4）
│   ├── switchbot_smartplug_control/  # SwitchBot 控制（已實現）
│   ├── testlink_integration/   # TestLink 整合（✅ 新增）
│   └── mobile_testing/common/  # 移動測試通用庫
│
├── resources/                   # Robot Framework 資源與關鍵字
│   ├── common_keywords.robot   # 通用關鍵字
│   ├── mobile_keywords.robot   # 移動設備關鍵字
│   ├── switchbot_keywords.robot # SwitchBot 關鍵字
│   ├── testlink_keywords.robot # TestLink 關鍵字（✅ 新增）
│   ├── api_keywords.robot      # API 關鍵字
│   └── web_keywords.robot      # Web 關鍵字
│
├── tests/                       # Robot Framework 測試案例
│   ├── mobile/                 # 移動應用測試
│   │   ├── ios/               # iOS 測試案例
│   │   └── android/           # Android 測試案例
│   ├── physical_interaction/   # 實體互動測試
│   ├── power_management/       # 電源管理測試
│   └── testlink_integration/   # TestLink 整合測試（✅ 新增）
│
├── scripts/                     # 輔助腳本
├── docs/                        # 文檔
└── results/                     # 測試結果輸出
```

### 配置系統架構

**重要:** 本專案採用**統一配置管理系統**，所有配置集中在 `config/` 目錄：

- `config/voice_config.py` - 語音系統所有配置
- `config/switchbot_config.py` - SwitchBot 配置（支援多來源：專案根目錄 .env、系統環境變數）
- `config/testlink_config.py` - TestLink 配置（✅ 新增，支援 API URL、API Key、專案設定等）
- `config/mobile/appium_config.py` - Appium 統一配置（iOS + Android）
- `config/mobile/ios_config.py` - iOS 專屬配置與設備管理

**配置優先順序:**
1. 系統環境變數 (最高優先)
2. 專案根目錄 `.env` 檔案
3. 配置檔案中的預設值

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

### Robot Framework 測試案例規範

**重要規範（來自 .github/copilot-instructions.md）:**

1. **Gherkin 語法結構:** 所有測試案例必須使用 Gherkin 語法（Given-When-Then-And）
2. **中文關鍵字:** 所有 Robot Framework 關鍵字名稱必須使用中文
3. **詳細文檔:** [Documentation] 應包含詳細說明和使用範例
4. **RETURN 語句:** 使用現代 RETURN 語句，避免舊式 [Return]
5. **日期格式:** 寫入日期前須檢查現在日期，格式為 YYYY-MM-DD
6. **中文文檔:** 所有文件和註解都應使用中文

### 關鍵字命名範例

```robotframework
# ✅ 正確範例
Given API 服務已在端點 "${endpoint}" 運行
When 使用者發送 GET 請求到 "${url}"
Then 回應狀態碼應該為 "${status_code}"
And 回應內容應該包含 "${expected_content}"

# ❌ 錯誤範例 (舊格式，已棄用)
Given API Service Is Running At Endpoint "${endpoint}"
When User Sends GET Request To "${url}"
```

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

**當前狀態 (2025-11-10):**
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

**下一階段重點:**
- Phase 2: 設備整合開發（機器手臂控制）
- Phase 3: 多感官檢測測試案例完善
- Phase 4: 進階 TestLink 功能（測試案例同步、自動建立 Bug）

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
- `libraries/testlink_integration/README.md` - TestLink 整合模組說明（✅ 新增）
- `docs/ios_device_setup.md` - iOS 設置指南
- `docs/ios_test_execution_guide.md` - iOS 測試執行指南
- `docs/testlink_integration_setup_guide.md` - TestLink 整合設置指南（✅ 新增）

## 開發工作流程

### 1. 協調者模式（迴旋標模式）

當使用協調者模式時，需將所有任務完成報告記錄在 `report.md` 中。

### 2. 架構模式

完成架構後需產生：
- `spec.md` - 規格文件（包含 UML 圖）
- `todo.md` - 任務清單

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
