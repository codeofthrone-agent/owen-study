## ADDED Requirements

### Requirement: 藍牙開關控制
系統 SHALL 提供透過 ADB shell 命令控制 Android 實體裝置藍牙開關的能力。系統 SHALL 提供 `開啟藍牙` 與 `關閉藍牙` 兩個 BDD 中文關鍵字。當裝置為 Android 7+ 非 root 時，系統 SHALL 回退至 UI 自動化方式操作 Settings 介面。

#### Scenario: 成功開啟藍牙
- **WHEN** 使用者執行「開啟藍牙」關鍵字
- **THEN** 系統透過 ADB `svc bluetooth enable` 命令開啟藍牙
- **THEN** 藍牙狀態 SHALL 變為已開啟

#### Scenario: 成功關閉藍牙
- **WHEN** 使用者執行「關閉藍牙」關鍵字
- **THEN** 系統透過 ADB `svc bluetooth disable` 命令關閉藍牙
- **THEN** 藍牙狀態 SHALL 變為已關閉

#### Scenario: 非 root 裝置藍牙控制回退
- **WHEN** ADB 藍牙命令執行失敗（權限不足）
- **THEN** 系統 SHALL 自動回退至 UI 自動化方式，開啟 Android Settings 藍牙頁面進行操作
- **THEN** 操作結果 SHALL 記錄於日誌中

### Requirement: WiFi 開關控制
系統 SHALL 提供控制 Android 裝置 WiFi 開關的能力，透過 ADB `svc wifi enable/disable` 命令實現。

#### Scenario: 成功關閉 WiFi
- **WHEN** 使用者執行「關閉 WiFi」關鍵字
- **THEN** 系統透過 ADB `svc wifi disable` 命令關閉 WiFi
- **THEN** 裝置 WiFi 狀態 SHALL 變為已關閉

#### Scenario: 成功開啟 WiFi
- **WHEN** 使用者執行「開啟 WiFi」關鍵字
- **THEN** 系統透過 ADB `svc wifi enable` 命令開啟 WiFi
- **THEN** 裝置 WiFi 狀態 SHALL 變為已開啟

### Requirement: 行動數據控制
系統 SHALL 提供控制 Android 裝置行動數據開關的能力，透過 `io.appium.settings` 實現。

#### Scenario: 成功關閉行動數據
- **WHEN** 使用者執行「關閉行動數據」關鍵字
- **THEN** 系統透過 ADB 啟動 `io.appium.settings` 並傳遞 `data off` 參數
- **THEN** 行動數據 SHALL 變為已關閉

#### Scenario: 成功開啟行動數據
- **WHEN** 使用者執行「開啟行動數據」關鍵字
- **THEN** 系統透過 ADB 啟動 `io.appium.settings` 並傳遞 `data on` 參數
- **THEN** 行動數據 SHALL 變為已開啟

### Requirement: 飛航模式控制
系統 SHALL 提供切換 Android 裝置飛航模式的能力。系統 SHALL 優先使用 ADB 命令，而非 Appium 的 `toggle_airplane_mode()`（因 Android 7+ 不穩定）。

#### Scenario: 開啟飛航模式切斷所有網路
- **WHEN** 使用者執行「開啟飛航模式」關鍵字
- **THEN** 系統透過 ADB `settings put global airplane_mode_on 1` 開啟飛航模式
- **THEN** 系統 SHALL 發送廣播通知系統飛航模式已變更
- **THEN** WiFi 與行動數據 SHALL 同時被關閉

#### Scenario: 關閉飛航模式恢復網路
- **WHEN** 使用者執行「關閉飛航模式」關鍵字
- **THEN** 系統透過 ADB `settings put global airplane_mode_on 0` 關閉飛航模式
- **THEN** 系統 SHALL 發送廣播通知系統飛航模式已變更

### Requirement: 音量控制
系統 SHALL 提供控制 Android 裝置音量的能力，包含音量調高、調低、靜音、以及設定指定媒體音量。

#### Scenario: 調高音量
- **WHEN** 使用者執行「調高音量」關鍵字
- **THEN** 系統透過 `press_keycode(24)` 調高音量一級

#### Scenario: 調低音量
- **WHEN** 使用者執行「調低音量」關鍵字
- **THEN** 系統透過 `press_keycode(25)` 調低音量一級

#### Scenario: 靜音
- **WHEN** 使用者執行「靜音」關鍵字
- **THEN** 系統透過 `press_keycode(164)` 將裝置靜音

#### Scenario: 設定媒體音量到指定值
- **WHEN** 使用者執行「設定媒體音量」關鍵字並傳入音量值（0-15）
- **THEN** 系統透過 ADB `media volume --stream 3 --set {level}` 設定媒體音量
- **THEN** 媒體音量 SHALL 被設為指定值

### Requirement: 應用程式置於背景
系統 SHALL 提供將當前應用程式置於背景並在指定時間後恢復的能力。系統 MUST 使用 `background_app(-1)` + `activate_app()` 組合，避免 Android 上 `background_app(seconds)` 會重啟 App 的問題。

#### Scenario: App 置於背景後恢復
- **WHEN** 使用者執行「將應用程式置於背景」關鍵字並指定等待秒數
- **THEN** 系統使用 `background_app(-1)` 將 App 送入背景
- **THEN** 等待指定秒數後，系統使用 `activate_app(package)` 恢復 App
- **THEN** App SHALL 恢復至前景且保持原有狀態

#### Scenario: App 無限期置於背景
- **WHEN** 使用者執行「將應用程式置於背景」關鍵字且不指定等待秒數
- **THEN** 系統使用 `background_app(-1)` 將 App 送入背景
- **THEN** App SHALL 保持在背景直到使用者手動恢復

### Requirement: 從最近應用清除 App
系統 SHALL 提供從最近應用列表中滑掉（清除）指定 App 的能力。

#### Scenario: 從最近應用滑掉 App
- **WHEN** 使用者執行「從最近應用清除」關鍵字
- **THEN** 系統透過 `press_keycode(187)` 開啟最近應用列表
- **THEN** 系統等待最近應用列表載入完成
- **THEN** 系統透過向上滑動手勢將 App 從列表清除

#### Scenario: 強制停止 App
- **WHEN** 使用者執行「強制停止應用程式」關鍵字並傳入 package name
- **THEN** 系統透過 `terminate_app(package)` 或 ADB `am force-stop` 強制關閉 App

### Requirement: 裝置狀態查詢與驗證
系統 SHALL 提供查詢 Android 裝置各項系統狀態的能力，每個「控制」功能 MUST 有對應的「查詢/驗證」方法，使 Then 關鍵字能以具體手段斷言狀態。系統 SHALL 透過 ADB shell 命令讀取裝置系統設定值作為驗證依據。

#### Scenario: 查詢藍牙狀態
- **WHEN** 使用者執行「藍牙應該為開啟狀態」驗證關鍵字
- **THEN** 系統 SHALL 透過 ADB `settings get global bluetooth_on` 查詢藍牙狀態
- **THEN** 返回值為 `1` 時驗證通過，為 `0` 時 SHALL 拋出 AssertionError（含實際值）

#### Scenario: 查詢 WiFi 狀態
- **WHEN** 使用者執行「WiFi 應該為關閉狀態」驗證關鍵字
- **THEN** 系統 SHALL 透過 ADB `settings get global wifi_on` 查詢 WiFi 狀態
- **THEN** 返回值為 `0` 時驗證通過，為 `1` 時 SHALL 拋出 AssertionError（含實際值）

#### Scenario: 查詢飛航模式狀態
- **WHEN** 使用者執行「飛航模式應該為開啟狀態」驗證關鍵字
- **THEN** 系統 SHALL 透過 ADB `settings get global airplane_mode_on` 查詢飛航模式狀態
- **THEN** 返回值為 `1` 時驗證通過，為 `0` 時 SHALL 拋出 AssertionError

#### Scenario: 查詢媒體音量
- **WHEN** 使用者執行「媒體音量應該為」驗證關鍵字並傳入預期音量值
- **THEN** 系統 SHALL 透過 ADB `media volume --stream 3 --get` 查詢媒體音量
- **THEN** 實際音量與預期值一致時驗證通過，不一致時 SHALL 拋出 AssertionError（含預期值與實際值）

#### Scenario: 查詢 App 運行狀態
- **WHEN** 使用者執行「應用程式應該在前景」驗證關鍵字並傳入 package name
- **THEN** 系統 SHALL 透過 ADB `dumpsys activity activities` 查詢當前前景 Activity
- **THEN** 前景 Activity 的 package 與預期一致時驗證通過，不一致時 SHALL 拋出 AssertionError

#### Scenario: 查詢 App 背景狀態
- **WHEN** 使用者執行「應用程式應該在背景」驗證關鍵字並傳入 package name
- **THEN** 系統 SHALL 透過 ADB `dumpsys activity processes` 查詢 App 狀態
- **THEN** App 存在但不在前景時驗證通過
