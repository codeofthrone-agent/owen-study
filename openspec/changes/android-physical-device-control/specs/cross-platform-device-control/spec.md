## ADDED Requirements

### Requirement: 跨平台抽象基類定義
系統 SHALL 提供 `DeviceControlBase` 與 `GestureControlBase` 兩個抽象基類（ABC），定義所有裝置控制與手勢操作的統一介面。Android 和 iOS 實作類別 MUST 繼承對應的基類並實作所有抽象方法。

#### Scenario: 抽象基類定義完整的裝置控制介面
- **WHEN** 開發者查看 `DeviceControlBase` 抽象基類
- **THEN** 基類 SHALL 包含以下抽象方法：藍牙開關、WiFi 開關、行動數據開關、飛航模式開關、音量調高/調低/靜音/設定、App 背景/恢復/清除/強制停止
- **THEN** 每個抽象方法 SHALL 包含中文 docstring 說明

#### Scenario: 抽象基類定義完整的手勢控制介面
- **WHEN** 開發者查看 `GestureControlBase` 抽象基類
- **THEN** 基類 SHALL 包含以下抽象方法：長按元素、長按座標、精確滑動、區域內滑動、座標點擊、雙擊、拖曳
- **THEN** 每個抽象方法 SHALL 包含中文 docstring 說明

### Requirement: 平台分發統一入口
系統 SHALL 提供 `DeviceControlKeywords` 與 `GestureControlKeywords` 作為 Robot Framework Library 統一入口。入口 SHALL 根據初始化時傳入的 platform 參數，自動分發至對應的平台實作類別。

#### Scenario: 初始化 Android 裝置控制
- **WHEN** 使用者呼叫「初始化裝置控制」關鍵字並傳入 platform="android"
- **THEN** 系統 SHALL 建立 `AndroidDeviceControl` 實例作為底層實作
- **THEN** 後續所有裝置控制關鍵字 SHALL 透過 Android 實作執行

#### Scenario: 初始化 iOS 裝置控制
- **WHEN** 使用者呼叫「初始化裝置控制」關鍵字並傳入 platform="ios"
- **THEN** 系統 SHALL 建立 `IOSDeviceControl` 實例作為底層實作
- **THEN** 呼叫尚未實作的功能時 SHALL 拋出 `NotImplementedError` 並附帶功能名稱

#### Scenario: 傳入不支援的平台
- **WHEN** 使用者呼叫「初始化裝置控制」並傳入不支援的 platform 值
- **THEN** 系統 SHALL 拋出 `ValueError` 並說明支援的平台列表

### Requirement: BDD 關鍵字平台無關（裝置控制與手勢控制）
系統 SHALL 提供平台無關的中文 BDD 關鍵字，涵蓋**裝置控制**（device_control_keywords.robot）與**手勢控制**（gesture_control_keywords.robot）兩組資源檔。所有關鍵字名稱 MUST NOT 包含平台特定術語（如 ADB、XCUITest、UiAutomator、press_keycode）。使用者在 Robot Framework 測試案例中使用相同的關鍵字，無論目標平台為 Android 或 iOS。

#### Scenario: 平台無關的 WiFi 控制關鍵字
- **WHEN** 使用者在 Android 環境中呼叫「When 使用者關閉 WiFi」
- **THEN** 系統 SHALL 透過 Android 實作（ADB svc wifi disable）關閉 WiFi
- **WHEN** 使用者在 iOS 環境中呼叫相同的「When 使用者關閉 WiFi」
- **THEN** 系統 SHALL 透過 iOS 實作執行（或拋出 NotImplementedError 若尚未實作）

#### Scenario: 平台無關的手勢控制關鍵字
- **WHEN** 使用者在 Android 環境中呼叫「When 使用者長按元素」
- **THEN** 系統 SHALL 透過 Android 實作（mobile: longClickGesture）執行長按
- **WHEN** 使用者在 iOS 環境中呼叫相同的「When 使用者長按元素」
- **THEN** 系統 SHALL 透過 iOS 實作執行（或拋出 NotImplementedError 若尚未實作）

#### Scenario: 測試案例無需修改即可跨平台執行
- **WHEN** 一個使用裝置控制或手勢控制關鍵字的測試案例從 Android 切換至 iOS 執行
- **THEN** 測試案例的 Robot Framework 原始碼 SHALL 完全不需修改
- **THEN** 僅需在 Suite Setup 中變更 platform 參數

### Requirement: Driver 自動注入
統一入口 Library（DeviceControlKeywords / GestureControlKeywords）SHALL 自動從已載入的 AppiumLibrary 或 CustomAppiumKeywords 取得 WebDriver 實例。使用者在「初始化裝置控制」時 MUST NOT 需要手動傳入 driver 物件，僅需傳入 platform 參數。

#### Scenario: 從 AppiumLibrary 自動取得 driver
- **WHEN** Robot Framework 測試已載入 AppiumLibrary 並開啟應用程式
- **THEN** 呼叫「初始化裝置控制 android」時，系統 SHALL 透過 `BuiltIn().get_library_instance('AppiumLibrary')` 自動取得 driver
- **THEN** 使用者不需在測試案例中接觸 driver 物件

#### Scenario: 未載入 AppiumLibrary 時報錯
- **WHEN** 未載入任何提供 driver 的 Library 就呼叫「初始化裝置控制」
- **THEN** 系統 SHALL 拋出 RuntimeError 並提示「請確保已載入 AppiumLibrary 或 CustomAppiumKeywords，且已開啟應用程式」

### Requirement: iOS Stub 實作
系統 SHALL 提供 `IOSDeviceControl` 與 `IOSGestureControl` 類別，繼承對應的抽象基類。本次所有 iOS 方法 SHALL 統一拋出 `NotImplementedError`，附帶明確的中文錯誤訊息（如「iOS 藍牙控制尚未實作」）。

#### Scenario: iOS stub 方法拋出明確錯誤
- **WHEN** 使用者在 iOS 環境中呼叫「關閉藍牙」關鍵字
- **THEN** 系統 SHALL 拋出 `NotImplementedError`
- **THEN** 錯誤訊息 SHALL 包含「iOS」和「藍牙」和「尚未實作」

#### Scenario: iOS stub 不影響 Android 功能
- **WHEN** iOS stub 類別存在但未被使用（platform="android"）
- **THEN** Android 功能 SHALL 正常運作，不受 iOS stub 影響

### Requirement: TDD 單元測試覆蓋架構層
系統 SHALL 採用 TDD 開發流程（Red → Green → Refactor）開發跨平台架構層。所有架構層程式碼（抽象基類、平台分發、iOS stub）MUST 先編寫測試再實作功能。Android 實作層 SHALL 使用 mock-based 單元測試驗證邏輯正確性，實機驗證由人類協作完成。

#### Scenario: 抽象基類不可直接實例化
- **WHEN** 開發者嘗試直接實例化 `DeviceControlBase`
- **THEN** SHALL 拋出 `TypeError`，因為包含未實作的抽象方法

#### Scenario: 平台分發正確路由至 Android 實作
- **WHEN** 單元測試建立 `DeviceControlKeywords` 並以 platform="android" 初始化
- **THEN** 內部 `_impl` SHALL 為 `AndroidDeviceControl` 的實例

#### Scenario: 平台分發正確路由至 iOS stub
- **WHEN** 單元測試建立 `DeviceControlKeywords` 並以 platform="ios" 初始化
- **THEN** 內部 `_impl` SHALL 為 `IOSDeviceControl` 的實例
- **THEN** 呼叫任意控制方法 SHALL 拋出 `NotImplementedError`

#### Scenario: 未初始化時呼叫關鍵字應報錯
- **WHEN** 單元測試直接呼叫 `DeviceControlKeywords` 的控制方法（未先初始化）
- **THEN** SHALL 拋出 `RuntimeError` 並提示需先呼叫「初始化裝置控制」

#### Scenario: Android 實作 mock-based 單元測試
- **WHEN** 單元測試使用 mock driver 呼叫 `AndroidDeviceControl.disable_wifi()`
- **THEN** SHALL 驗證 `driver.execute_script('mobile: shell', ...)` 被正確呼叫
- **THEN** SHALL 驗證傳入的 ADB 命令參數為 `svc wifi disable`

#### Scenario: Android 手勢 mock-based 單元測試
- **WHEN** 單元測試使用 mock driver 呼叫 `AndroidGestureControl.long_press_element()`
- **THEN** SHALL 驗證 `driver.execute_script('mobile: longClickGesture', ...)` 被正確呼叫
- **THEN** SHALL 驗證傳入的參數包含 elementId 和 duration
