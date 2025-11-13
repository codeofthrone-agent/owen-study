# 移動裝置測試模組

基於 Appium 的跨平台移動裝置自動化測試系統，支援 iOS 和 Android 平台的應用程式測試功能。

## 功能特色

- 📱 **跨平台支援** - 同時支援 iOS 和 Android 測試
- 🚀 **Appium 整合** - 基於 Appium WebDriver 的自動化測試
- 🎯 **元素操作** - 完整的 UI 元素定位與操作功能
- 📊 **應用管理** - 應用安裝、卸載、啟動、關閉
- 🔄 **設備管理** - 多設備連接與切換功能
- 🤖 **Robot Framework 整合** - 完整的中文關鍵字支援

## 系統需求

### 必要套件

```bash
pip install appium-python-client selenium robotframework loguru pyyaml
```

### 平台需求

#### iOS 測試需求
- macOS 系統
- Xcode 和 Xcode Command Line Tools
- iOS Simulator 或真實 iOS 設備
- WebDriverAgent (WDA)
- libimobiledevice

#### Android 測試需求
- Android SDK
- Android Studio (可選)
- Android 模擬器或真實 Android 設備
- USB 偵錯模式已啟用

### Appium 服務器

```bash
# 安裝 Appium
npm install -g appium

# 安裝驅動程式
appium driver install uiautomator2  # Android
appium driver install xcuitest      # iOS

# 啟動 Appium 服務器
appium --port 4723
```

## 快速開始

### 1. 配置設定

編輯 `config/mobile/appium_config.py`：

```python
# iOS 配置
ios_config = {
    "platformName": "iOS",
    "platformVersion": "17.0",
    "deviceName": "iPhone 15 Simulator",
    "automationName": "XCUITest",
    "app": "/path/to/your/app.app",
    "udid": "simulator_udid"
}

# Android 配置
android_config = {
    "platformName": "Android",
    "platformVersion": "14.0",
    "deviceName": "Android Emulator",
    "automationName": "UiAutomator2",
    "appPackage": "com.example.app",
    "appActivity": ".MainActivity"
}

# Appium 服務器配置
appium_config = {
    "command_executor": "http://127.0.0.1:4723",
    "ios": ios_config,
    "android": android_config
}
```

### 2. Python 使用範例

```python
from libraries.mobile_testing.common import CustomAppiumKeywords

# 初始化
mobile = CustomAppiumKeywords()

# 開啟 iOS 應用
mobile.open_application("ios")

# 尋找元素並點擊
element = mobile.find_element("id", "login_button")
mobile.click_element(element)

# 輸入文字
mobile.input_text("id", "username", "testuser")
mobile.input_text("id", "password", "password123")

# 截圖
mobile.capture_screenshot("test_screenshot.png")

# 關閉應用
mobile.close_application()
```

### 3. Robot Framework 使用範例

```robotframework
*** Settings ***
Resource    resources/mobile_keywords.robot

*** Test Cases ***
iOS Safari 測試
    Given 開啟 iOS Safari 應用
    When 導航至網頁    https://www.example.com
    And 等待頁面載入完成
    Then 驗證頁面標題包含    Example Domain
    And 截圖並儲存    safari_test.png
    And 關閉應用程式

Android 應用測試
    Given 開啟 Android 應用    com.example.app
    When 點擊登入按鈕
    And 輸入使用者名稱    testuser
    And 輸入密碼    password123
    And 點擊確認按鈕
    Then 驗證登入成功
    And 關閉應用程式
```

## API 參考

### CustomAppiumKeywords 類別

#### open_application(platform, **kwargs)
開啟指定平台的應用程式。

```python
mobile.open_application("ios")
mobile.open_application("android", app_package="com.example.app")
```

#### close_application()
關閉當前應用程式。

```python
mobile.close_application()
```

#### find_element(by, value)
尋找 UI 元素。

```python
element = mobile.find_element("id", "button_id")
element = mobile.find_element("xpath", "//button[@text='Click']")
```

#### find_elements(by, value)
尋找多個 UI 元素。

```python
elements = mobile.find_elements("class", "button")
```

#### click_element(locator_or_element)
點擊 UI 元素。

```python
mobile.click_element("id", "button_id")
mobile.click_element(element_object)
```

#### input_text(by, value, text)
在輸入框中輸入文字。

```python
mobile.input_text("id", "username", "testuser")
```

#### wait_for_element(by, value, timeout=10)
等待元素出現。

```python
element = mobile.wait_for_element("id", "loading_indicator", timeout=30)
```

#### capture_screenshot(filename="")
截取螢幕截圖。

```python
mobile.capture_screenshot("test_result.png")
```

#### swipe(start_x, start_y, end_x, end_y, duration=1000)
執行滑動手勢。

```python
mobile.swipe(100, 500, 100, 200, duration=1000)  # 向上滑動
```

#### tap(x, y)
在指定座標點擊。

```python
mobile.tap(150, 300)
```

#### get_text(by, value)
取得元素文字內容。

```python
text = mobile.get_text("id", "status_label")
```

#### is_element_visible(by, value)
檢查元素是否可見。

```python
is_visible = mobile.is_element_visible("id", "popup_dialog")
```

#### scroll_to_element(by, value)
滾動至指定元素。

```python
mobile.scroll_to_element("text", "Submit Button")
```

## Robot Framework 關鍵字

### 應用管理

- `開啟 iOS 應用    ${app_path}`
- `開啟 Android 應用    ${app_package}`
- `關閉應用程式`
- `重啟應用程式`
- `切換至應用    ${app_identifier}`

### 元素操作

- `點擊元素    ${locator}    ${value}`
- `輸入文字    ${locator}    ${value}    ${text}`
- `清除文字    ${locator}    ${value}`
- `長按元素    ${locator}    ${value}    duration=${duration}`

### 元素定位

- `等待元素出現    ${locator}    ${value}    timeout=${timeout}`
- `等待元素消失    ${locator}    ${value}    timeout=${timeout}`
- `元素應該存在    ${locator}    ${value}`
- `元素應該可見    ${locator}    ${value}`
- `元素應該包含文字    ${locator}    ${value}    ${expected_text}`

### 手勢操作

- `向上滑動    start_x=${start_x}    start_y=${start_y}`
- `向下滑動    start_x=${start_x}    start_y=${start_y}`
- `向左滑動    start_x=${start_x}    start_y=${start_y}`
- `向右滑動    start_x=${start_x}    start_y=${start_y}`
- `點擊座標    ${x}    ${y}`

### 截圖與驗證

- `截圖並儲存    ${filename}`
- `取得元素文字    ${locator}    ${value}`
- `驗證頁面標題    ${expected_title}`
- `驗證元素文字    ${locator}    ${value}    ${expected_text}`

### 設備操作

- `取得設備方向`
- `設定設備方向    ${orientation}`
- `取得網路連線狀態`
- `設定網路連線    ${connection_type}`

### 等待操作

- `等待 ${duration} 秒鐘`
- `等待頁面載入完成    timeout=${timeout}`
- `等待應用程式啟動    timeout=${timeout}`

## 配置說明

### iOS 設備配置

```python
ios_config = {
    "platformName": "iOS",
    "platformVersion": "17.0",           # iOS 版本
    "deviceName": "iPhone 15 Simulator", # 設備名稱
    "automationName": "XCUITest",        # 自動化引擎
    "app": "/path/to/app.app",           # 應用路徑
    "udid": "device_udid",               # 設備 UDID
    "bundleId": "com.example.app",       # Bundle ID
    "wdaLocalPort": 8100,               # WDA 本地端口
    "useNewWDA": True,                   # 使用新的 WDA
    "resetOnSessionStartOnly": False,    # 重置設定
    "autoAcceptAlerts": True             # 自動接受彈窗
}
```

### Android 設備配置

```python
android_config = {
    "platformName": "Android",
    "platformVersion": "14.0",           # Android 版本
    "deviceName": "Android Emulator",    # 設備名稱
    "automationName": "UiAutomator2",    # 自動化引擎
    "appPackage": "com.example.app",     # 應用包名
    "appActivity": ".MainActivity",      # 主活動
    "udid": "emulator-5554",            # 設備 UDID
    "app": "/path/to/app.apk",          # APK 路徑
    "autoGrantPermissions": True,        # 自動授予權限
    "noReset": False,                    # 不重置應用
    "newCommandTimeout": 300             # 命令逾時
}
```

### 元素定位策略

```python
# 支援的定位方法
LOCATOR_STRATEGIES = {
    "id": AppiumBy.ID,
    "xpath": AppiumBy.XPATH,
    "class": AppiumBy.CLASS_NAME,
    "tag": AppiumBy.TAG_NAME,
    "name": AppiumBy.NAME,
    "css": AppiumBy.CSS_SELECTOR,
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "ios_predicate": AppiumBy.IOS_PREDICATE,
    "ios_class_chain": AppiumBy.IOS_CLASS_CHAIN,
    "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR
}
```

## 測試執行

### 執行所有測試

```bash
robot tests/mobile_testing/mobile_test_suite.robot
```

### 執行平台特定測試

```bash
# iOS 測試
robot --include ios tests/mobile_testing/

# Android 測試
robot --include android tests/mobile_testing/

# Safari 測試
robot --include safari tests/mobile_testing/
```

### 並行測試執行

```bash
# 同時在多個設備上執行測試
pabot --testlevelsplit tests/mobile_testing/
```

## 設備設定

### iOS 設備設定

#### 模擬器設定

```bash
# 列出可用的模擬器
xcrun simctl list devices

# 啟動指定模擬器
xcrun simctl boot "iPhone 15 Simulator"

# 安裝應用至模擬器
xcrun simctl install booted /path/to/app.app
```

#### 真實設備設定

```bash
# 安裝必要工具
brew install libimobiledevice --HEAD
brew install ideviceinstaller

# 取得設備 UDID
idevice_id -l

# 安裝應用至真實設備
ideviceinstaller -i /path/to/app.ipa
```

### Android 設備設定

#### 模擬器設定

```bash
# 列出可用的 AVD
emulator -list-avds

# 啟動模擬器
emulator -avd "Android_14_API_34"

# 安裝 APK
adb install /path/to/app.apk
```

#### 真實設備設定

```bash
# 啟用開發者選項與 USB 偵錯
# 設定 → 關於手機 → 版本號碼（點擊 7 次）
# 設定 → 開發者選項 → USB 偵錯

# 檢查設備連接
adb devices

# 安裝 APK
adb install /path/to/app.apk
```

## 故障排除

### 問題：Appium 連線失敗

**可能原因:**
- Appium 服務器未啟動
- 端口被佔用
- 設備未連接

**解決方法:**
```bash
# 檢查 Appium 服務器狀態
curl http://127.0.0.1:4723/status

# 重新啟動 Appium
pkill -f appium
appium --port 4723

# 檢查端口使用
lsof -i :4723
```

### 問題：iOS 設備無法連接

**可能原因:**
- WebDriverAgent 未正確安裝
- 設備信任問題
- Xcode 設定問題

**解決方法:**
```bash
# 重新安裝 WebDriverAgent
cd /usr/local/lib/node_modules/appium/node_modules/appium-xcuitest-driver/WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'platform=iOS Simulator,name=iPhone 15' test

# 信任開發者憑證
# 設定 → 一般 → VPN 與設備管理 → 開發者 App
```

### 問題：Android 應用啟動失敗

**可能原因:**
- 應用包名或活動名稱錯誤
- 權限不足
- 設備架構不符

**解決方法:**
```bash
# 檢查應用資訊
aapt dump badging /path/to/app.apk | grep package
aapt dump badging /path/to/app.apk | grep activity

# 檢查設備架構
adb shell getprop ro.product.cpu.abi

# 檢查應用權限
adb shell dumpsys package com.example.app | grep permission
```

### 問題：元素定位失敗

**可能原因:**
- 元素 ID 或屬性變更
- 頁面載入未完成
- 定位策略不正確

**解決方法:**
```bash
# 使用 Appium Inspector 檢查元素
# 下載 Appium Inspector: https://github.com/appium/appium-inspector

# 使用 uiautomatorviewer (Android)
uiautomatorviewer

# 檢查頁面源碼
mobile.get_page_source()
```

## 進階使用

### 多設備測試

```python
# 設定多個設備
devices = [
    {"platformName": "iOS", "deviceName": "iPhone 15"},
    {"platformName": "Android", "deviceName": "Pixel 6"}
]

# 並行測試執行
from concurrent.futures import ThreadPoolExecutor

def run_test_on_device(device_config):
    mobile = CustomAppiumKeywords()
    mobile.open_application(device_config)
    # 執行測試...
    mobile.close_application()

with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(run_test_on_device, devices)
```

### 自訂等待條件

```python
from selenium.webdriver.support import expected_conditions as EC

def wait_for_custom_condition(driver, locator, condition_func):
    wait = WebDriverWait(driver, 10)
    return wait.until(lambda d: condition_func(d.find_element(*locator)))
```

### 效能測試整合

```python
import time

def measure_app_startup_time():
    start_time = time.time()
    mobile.open_application("ios")
    mobile.wait_for_element("id", "main_screen")
    startup_time = time.time() - start_time
    print(f"應用啟動時間: {startup_time:.2f} 秒")
```

### 網路模擬

```python
# 設定網路連線類型
mobile.set_network_connection(6)  # Wi-Fi + 數據

# 模擬離線狀態
mobile.set_network_connection(0)  # 飛航模式
```

## 整合範例

### 搭配 CI/CD

```yaml
# GitHub Actions 範例
name: Mobile Testing
on: [push, pull_request]

jobs:
  mobile-test:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        
    - name: Install Appium
      run: |
        npm install -g appium
        appium driver install xcuitest
        
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        appium --port 4723 &
        robot tests/mobile_testing/
```

### 搭配報告系統

```robotframework
*** Test Cases ***
移動應用效能測試
    [Tags]    performance
    Given 開啟應用並記錄時間
    When 執行關鍵操作流程
    Then 驗證操作完成時間
    And 產生效能報告
    And 上傳測試結果至 TestLink
```

## 檔案結構

```
libraries/mobile_testing/
├── common/
│   ├── __init__.py
│   └── CustomAppiumKeywords.py          # 主要 Appium 關鍵字庫
├── ios/
│   ├── __init__.py
│   └── IOSSpecificKeywords.py           # iOS 特定功能
├── android/
│   ├── __init__.py
│   └── AndroidSpecificKeywords.py      # Android 特定功能
└── README.md                            # 本說明文件

config/mobile/
├── appium_config.py                     # Appium 設定檔案
├── ios_config.yaml                      # iOS 設定
└── android_config.yaml                  # Android 設定

resources/
└── mobile_keywords.robot                # Robot Framework 關鍵字

tests/mobile_testing/
├── ios_testing/
│   ├── ios_safari_test.robot           # iOS Safari 測試
│   └── ios_app_test.robot              # iOS 應用測試
├── android_testing/
│   ├── android_app_test.robot          # Android 應用測試
│   └── android_browser_test.robot      # Android 瀏覽器測試
└── common_testing/
    └── cross_platform_test.robot       # 跨平台測試
```

## 效能建議

### 測試優化

1. **元素等待**: 使用明確等待而非隱含等待
2. **截圖節省**: 僅在必要時截圖
3. **應用重置**: 合理使用 `noReset` 選項
4. **並行執行**: 利用多設備並行測試

### 資源管理

1. **記憶體使用**: 定期釋放不需要的變數
2. **設備連接**: 測試完畢後確實關閉連接
3. **日誌大小**: 控制日誌檔案大小
4. **暫存清理**: 定期清理暫存檔案

## 注意事項

1. **設備準備**: 確保測試設備已正確設定
2. **網路穩定**: 測試環境需要穩定網路
3. **版本相容**: 注意 Appium 與設備系統版本相容性
4. **權限管理**: 確保應用有必要的權限
5. **測試隔離**: 確保測試案例間的獨立性

## 授權與貢獻

本模組為 robot-multiplatform-automation 專案的一部分。

## 更新日誌

### v1.0.0 (2025-11-11)
- ✨ 首次發布
- 📱 支援 iOS 和 Android 平台
- 🚀 完整 Appium 整合
- 🎯 豐富的元素操作功能
- 🤖 完整 Robot Framework 整合
- 📝 中文關鍵字支援

## 相關資源

- [Appium 官方文件](https://appium.io/docs/en/about-appium/intro/)
- [Selenium WebDriver 文件](https://selenium-python.readthedocs.io/)
- [iOS 測試指南](https://developer.apple.com/documentation/xctest)
- [Android 測試指南](https://developer.android.com/training/testing)