## 1. TDD: 架構層單元測試（先寫測試）

- [ ] 1.1 建立 `tests/test_device_control_base.py`：測試抽象基類不可實例化、子類必須實作所有抽象方法
- [ ] 1.2 建立 `tests/test_platform_dispatch.py`：測試 DeviceControlKeywords 平台分發（android → AndroidDeviceControl、ios → IOSDeviceControl、無效平台 → ValueError、未初始化 → RuntimeError）
- [ ] 1.3 建立 `tests/test_gesture_dispatch.py`：測試 GestureControlKeywords 平台分發邏輯
- [ ] 1.4 建立 `tests/test_ios_stub.py`：測試所有 iOS stub 方法拋出 NotImplementedError，且錯誤訊息包含「iOS」+「功能名稱」+「尚未實作」
- [ ] 1.5 執行測試，確認全部 RED（失敗），因為實作尚未建立

## 2. 跨平台基礎架構實作（讓測試變 GREEN）

- [ ] 2.1 建立 `libraries/mobile_testing/base/` 目錄與 `__init__.py`
- [ ] 2.2 建立 `base/device_control_base.py` 抽象基類（ABC），定義裝置控制統一介面（藍牙/WiFi/行動數據/飛航模式/音量/App 生命週期，共 16 個抽象方法）
- [ ] 2.3 建立 `base/gesture_control_base.py` 抽象基類（ABC），定義手勢控制統一介面（長按/滑動/座標點擊/雙擊/拖曳，共 7 個抽象方法）
- [ ] 2.4 建立 `libraries/mobile_testing/DeviceControlKeywords.py` 統一入口（Robot Framework Library），實作 platform 分發邏輯與 `初始化裝置控制` 關鍵字
- [ ] 2.5 建立 `libraries/mobile_testing/GestureControlKeywords.py` 統一手勢入口（Robot Framework Library），實作 platform 分發邏輯
- [ ] 2.6 建立 `libraries/mobile_testing/ios/` 目錄與 `__init__.py`
- [ ] 2.7 建立 `ios/IOSDeviceControl.py`，繼承 `DeviceControlBase`，所有方法統一拋出 `NotImplementedError("iOS {功能名稱} 尚未實作")`
- [ ] 2.8 建立 `ios/IOSGestureControl.py`，繼承 `GestureControlBase`，所有方法統一拋出 `NotImplementedError`
- [ ] 2.9 執行 Step 1 的測試，確認全部 GREEN（通過）

## 3. TDD: Android 實作 mock-based 單元測試（先寫測試）

- [ ] 3.1 建立 `tests/test_android_device_control.py`：使用 mock driver 測試 AndroidDeviceControl 所有方法（驗證 execute_script/press_keycode 呼叫參數正確），包含狀態查詢方法的 mock 測試（驗證 ADB settings get 呼叫與返回值解析）
- [ ] 3.2 建立 `tests/test_android_gesture_control.py`：使用 mock driver 測試 AndroidGestureControl 所有手勢方法（驗證 mobile: 命令參數正確）
- [ ] 3.3 執行測試，確認全部 RED（失敗）

## 4. Android 環境設定 🧑‍💻 人類協作

> ⚠️ 此階段需要實體 Android 裝置與人類操作

- [ ] 4.1 建立 `libraries/mobile_testing/android/` 目錄與 `__init__.py`
- [ ] 4.2 建立 `config/mobile/android_config.py`，包含 ADB 設定、裝置偵測、relaxed security 驗證
- [ ] 4.3 🧑‍💻 更新 Appium 啟動腳本 `scripts/start_appium.sh` 加入 `--relaxed-security` flag，並在實體環境驗證
- [ ] 4.4 🧑‍💻 驗證 Appium UiAutomator2 driver 是否支援 Android 16，必要時升級 driver 版本
- [ ] 4.5 🧑‍💻 連接實體 Android 裝置，確認 ADB 授權與 USB 調試正常

## 5. Android 裝置系統控制實作 🧑‍💻 人類協作

> ⚠️ 此階段需要實體 Android 裝置進行實機驗證

- [ ] 5.1 建立 `android/AndroidDeviceControl.py`，繼承 `DeviceControlBase`，實作基礎框架（__init__、driver 管理、ADB helper）
- [ ] 5.2 實作藍牙控制：`enable_bluetooth()`、`disable_bluetooth()`（ADB svc + UI 回退）
- [ ] 5.3 實作 WiFi 控制：`enable_wifi()`、`disable_wifi()`（ADB svc wifi）
- [ ] 5.4 實作行動數據控制：`enable_mobile_data()`、`disable_mobile_data()`（io.appium.settings）
- [ ] 5.5 實作飛航模式控制：`enable_airplane_mode()`、`disable_airplane_mode()`（ADB settings + broadcast）
- [ ] 5.6 實作音量控制：`volume_up()`、`volume_down()`、`volume_mute()`、`set_media_volume()`（press_keycode + ADB media volume）
- [ ] 5.7 實作 App 背景管理：`background_app()`、`activate_app()`（background_app(-1) + activate_app 組合）
- [ ] 5.8 實作 App 清除：`dismiss_from_recents()`、`force_stop_app()`（keycode 187 + swipe / terminate_app）
- [ ] 5.9 實作狀態查詢方法：`get_bluetooth_state()`（ADB `settings get global bluetooth_on`）、`get_wifi_state()`（ADB `settings get global wifi_on`）、`get_airplane_mode_state()`（ADB `settings get global airplane_mode_on`）、`get_media_volume()`（ADB `media volume --stream 3 --get`）、`get_foreground_app()`（ADB `dumpsys activity activities`）
- [ ] 5.10 實作狀態驗證方法：`assert_bluetooth_on/off()`、`assert_wifi_on/off()`、`assert_airplane_mode_on/off()`、`assert_media_volume(expected)`、`assert_app_in_foreground(package)`、`assert_app_in_background(package)`，斷言失敗時 SHALL 附帶實際值
- [ ] 5.11 執行 Step 3.1 的 mock 測試，確認全部 GREEN
- [ ] 5.12 🧑‍💻 在實體裝置上逐一驗證每個功能與狀態查詢，記錄裝置兼容性結果

## 6. Android 進階手勢實作 🧑‍💻 人類協作

> ⚠️ 此階段需要實體 Android 裝置進行手勢驗證

- [ ] 6.1 建立 `android/AndroidGestureControl.py`，繼承 `GestureControlBase`
- [ ] 6.2 實作長按：`long_press_element()`、`long_press_coordinates()`（mobile: longClickGesture）
- [ ] 6.3 實作精確滑動：`swipe_direction()`、`swipe_in_area()`（mobile: swipeGesture，支援四方向 + 百分比）
- [ ] 6.4 實作座標點擊：`tap_coordinates()`（mobile: clickGesture）
- [ ] 6.5 實作雙擊：`double_tap_element()`（mobile: doubleClickGesture）
- [ ] 6.6 實作拖曳：`drag_element()`（mobile: dragGesture）
- [ ] 6.7 執行 Step 3.2 的 mock 測試，確認全部 GREEN
- [ ] 6.8 🧑‍💻 在實體裝置上驗證手勢操作正確性

## 7. Android 語音輸入實作（IoT 語音控制場景）🧑‍💻 人類協作

> ⚠️ 此階段需要實體裝置 + Scarlett 4i4 音訊硬體

- [ ] 7.1 實作硬體就緒檢查：播放前透過 VoiceControlKeywords 檢查 Scarlett 4i4 連接狀態與 PipeWire 虛擬設備，未就緒時 SHALL 拋出 RuntimeError 附帶診斷訊息
- [ ] 7.2 在 `AndroidDeviceControl.py` 中新增語音輸入方法：`trigger_voice_search()`（ADB am start -a android.intent.action.VOICE_COMMAND）
- [ ] 7.3 在統一入口新增 App 內語音按鈕觸發關鍵字：`點擊語音輸入按鈕`（支援 id/xpath/accessibility_id 定位）
- [ ] 7.4 實作語音觸發與播放同步策略：點擊語音按鈕 → 等待 `mic_ready_delay`（預設 1.5 秒，可配置）→ 確認語音輸入 UI 出現 → 才播放音訊。未出現時重試（`max_retries` 預設 2 次），重試失敗拋出 TimeoutError
- [ ] 7.5 新增語音指令整合關鍵字：整合 VoiceControlKeywords（Scarlett 4i4）播放語音指令（如「開啟燈光」「關閉風扇」）
- [ ] 7.6 新增語音結果等待關鍵字：`等待語音輸入結果`（等待 App UI 元素文字變化，可指定逾時）
- [ ] 7.7 新增語音結果驗證關鍵字：`語音指令結果應包含`（驗證 App 回應包含預期文字如「燈光已開啟」）
- [ ] 7.8 實作語音控制逾時錯誤處理：辨識逾時附帶可能原因診斷（麥克風未接收/辨識失敗/通道不正確）；結果不符附帶建議（音量/距離）
- [ ] 7.9 🧑‍💻 在實體裝置上進行端到端語音控制測試，調校 `mic_ready_delay` 與 `max_retries` 參數

## 8. Robot Framework BDD 關鍵字資源檔（平台無關）

- [ ] 8.1 建立 `resources/device_control_keywords.robot`，封裝所有裝置控制關鍵字為平台無關的中文 BDD 關鍵字
- [ ] 8.2 新增 Given 前置條件關鍵字：`Given 裝置控制已初始化`、`Given 藍牙已開啟`、`Given WiFi 已開啟`
- [ ] 8.3 新增 When 動作關鍵字：`When 使用者開啟藍牙`、`When 使用者關閉 WiFi`、`When 使用者調高音量`、`When 使用者將應用程式置於背景` 等
- [ ] 8.4 新增 Then 驗證關鍵字：`Then 藍牙應該為開啟狀態`（底層呼叫 ADB `settings get global bluetooth_on` 斷言值為 1）、`Then WiFi 應該為關閉狀態`（斷言 `wifi_on` 為 0）、`Then 媒體音量應該為 ${level}`（斷言 `media volume --get`）、`Then 應用程式應該在前景`（斷言 `dumpsys activity`）等
- [ ] 8.5 建立 `resources/gesture_control_keywords.robot`，封裝手勢控制為平台無關的中文 BDD 關鍵字

## 9. 測試案例

- [ ] 9.1 建立 `tests/mobile/android/android_device_control_test.robot`，包含藍牙/WiFi/飛航模式/音量/App 背景測試案例
- [ ] 9.2 建立 `tests/mobile/android/android_gesture_test.robot`，包含長按/精確滑動/雙擊/拖曳測試案例
- [ ] 9.3 建立 `tests/mobile/android/android_voice_input_test.robot`，包含語音輸入觸發與 IoT 設備控制驗證測試案例
- [ ] 9.4 使用 `robot --dryrun` 驗證所有測試案例語法正確
- [ ] 9.5 為 iOS 尚未支援的測試案例加上 `[Tags]  android-only` 標記

## 10. 文件與整合

- [ ] 10.1 更新 `keywords_readme.md`，新增跨平台裝置控制與手勢控制關鍵字清單
- [ ] 10.2 使用 `robot.libdoc` 產生 DeviceControlKeywords 與 GestureControlKeywords API 文件
- [ ] 10.3 更新 `resources/mobile_keywords.robot`，新增 import 引用（如需要）
