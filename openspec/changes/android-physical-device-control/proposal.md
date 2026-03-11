## Why

目前專案的移動測試僅支援基礎 UI 操作（點擊、輸入文字、滑動、截圖），缺少對實體裝置系統層級的控制能力。實際測試場景需要控制藍牙、網路、音量、語音輸入等系統功能，才能完整驗證被測應用在各種裝置狀態下的行為。本次開發將以**跨平台架構**補齊這些缺口：BDD 關鍵字層設計為平台無關，底層先完成 Android 實作，iOS 預留 stub 介面，後續可直接擴展而無需重構測試案例。

## What Changes

- **新增跨平台抽象基類**：`libraries/mobile_testing/base/device_control_base.py` 與 `gesture_control_base.py`
  - 定義統一的裝置控制介面（ABC），Android 和 iOS 各自繼承實作
- **新增跨平台統一入口**：`libraries/mobile_testing/DeviceControlKeywords.py` 與 `GestureControlKeywords.py`
  - Robot Framework Library，根據 platform 參數自動分發至 Android/iOS 實作
- **新增 Android 實體裝置控制實作**：`libraries/mobile_testing/android/AndroidDeviceControl.py`
  - 藍牙控制（開啟/關閉），透過 ADB shell 命令實現
  - 語音輸入觸發，透過 Intent 啟動語音搜尋或 UI 自動化點擊麥克風按鈕
  - 音量控制（調高/調低/靜音/設定媒體音量），透過 `press_keycode` 與 ADB shell
  - 滑掉 App（從最近應用清除），透過 `KEYCODE_APP_SWITCH` + 滑動手勢
  - App 置於背景與恢復，使用 `background_app(-1)` + `activate_app()`
  - 關閉網路（WiFi 開關/飛航模式/行動數據），透過 ADB `svc` 命令
- **新增 Android 進階手勢實作**：`libraries/mobile_testing/android/AndroidGestureControl.py`
  - 長按手勢，使用 Appium 2.x `mobile: longClickGesture`
  - 精確滑動，使用 `mobile: swipeGesture` 支援四方向與百分比控制
  - 雙擊、拖曳等進階手勢
- **新增 iOS stub 實作**：`libraries/mobile_testing/ios/IOSDeviceControl.py` 與 `IOSGestureControl.py`
  - 所有方法拋出 `NotImplementedError`，後續逐步補齊
- **新增平台無關 BDD 關鍵字資源檔**：`resources/device_control_keywords.robot`
  - 所有關鍵字使用中文 Given-When-Then 風格，不暴露平台實作細節
- **新增 Android 專屬配置**：`config/mobile/android_config.py`
  - ADB 設定、裝置資訊管理、已連接裝置自動偵測
- **新增測試案例**：`tests/mobile/android/android_device_control_test.robot` 等
  - 覆蓋所有新增功能的驗證測試

## Capabilities

### New Capabilities
- `cross-platform-device-control`: 跨平台裝置系統控制抽象架構（策略模式、抽象基類、平台分發）
- `android-device-control`: Android 實體裝置系統層級控制（藍牙、網路、音量、App 生命週期管理）
- `android-gesture-control`: Android 進階手勢操作（長按、四方向精確滑動、座標點擊）
- `android-voice-input`: Android 語音輸入觸發與 IoT 設備控制驗證

### Modified Capabilities
（無既有 spec 需要修改）

## Impact

**程式碼影響：**
- 新增 `libraries/mobile_testing/base/` — 跨平台抽象基類（2 個檔案）
- 新增 `libraries/mobile_testing/DeviceControlKeywords.py` — 統一入口
- 新增 `libraries/mobile_testing/GestureControlKeywords.py` — 統一手勢入口
- 新增 `libraries/mobile_testing/android/` — Android 實作（2 個檔案）
- 新增 `libraries/mobile_testing/ios/` — iOS stub（2 個檔案）
- 新增 `resources/device_control_keywords.robot` — 平台無關 BDD 關鍵字
- 新增 `config/mobile/android_config.py` — 裝置配置管理
- 新增 `tests/mobile/android/` — 測試案例（3 個檔案）
- 既有 `libraries/mobile_testing/common/CustomAppiumKeywords.py` 保持不變

**依賴影響：**
- Appium 2.x + UiAutomator2 驅動（已有）
- ADB（Android Debug Bridge）必須在測試機器上可用
- `io.appium.settings` APK 需安裝在目標裝置（Appium 自動安裝）
- 部分功能（藍牙控制）在非 root 裝置上有限制

**系統需求：**
- 實體 Android 裝置（目標 Android 16）
- USB 調試模式已開啟、ADB 已授權
- Appium server 需啟用 `--relaxed-security` flag

**已知限制：**
- 藍牙配對需透過 UI 自動化 Settings 介面，無法純 API 完成
- Android 7+ 的飛航模式切換透過 `toggle_airplane_mode()` 不穩定，需使用 ADB 替代方案
- `background_app()` 在 Android 上會重啟 App，使用 `background_app(-1)` + `activate_app()` 組合
- 語音輸入無法直接注入語音辨識結果，僅能觸發語音輸入 UI
- iOS 系統控制本次僅預留 stub，完整實作為後續工作
