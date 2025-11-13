*** Settings ***
Documentation    移動設備測試通用關鍵字庫 - Mobile Device Testing Keyword Library
...              提供跨平台的移動應用測試關鍵字，支援 iOS 和 Android
...              Provides cross-platform mobile application testing keywords, supporting iOS and Android
...              
...              主要用途 / Main Uses:
...              - iOS 和 Android 應用程式自動化測試 / iOS and Android app automation testing
...              - 跨平台手勢操作 / Cross-platform gesture operations
...              - 移動設備元素定位與操作 / Mobile device element location and operation
...              - 應用程式生命週期管理 / Application lifecycle management
...              
...              支援的操作 / Supported Operations:
...              - 點擊、滑動、輸入文字 / Tap, swipe, text input
...              - 元素等待與驗證 / Element waiting and verification
...              - 螢幕截圖與日誌記錄 / Screenshot and logging
...              
...              使用方式 / Usage:
...              在測試案例中引用此資源檔案，並使用 Given-When-Then-And 格式的關鍵字
...              Import this resource file in test cases and use Given-When-Then-And style keywords


Library          AppiumLibrary
Library          Collections
Library          BuiltIn
Variables        ../variables/common_variables.py
Resource         common_keywords.robot

*** Keywords ***
# ============================================================================
# GIVEN Keywords (Preconditions) - 前置條件關鍵字
# ============================================================================

Given 使用者已準備好移動應用程式
    [Documentation]    用戶已準備好移動應用程式
    ...                User has mobile application ready
    ...                
    ...                參數說明 / Parameters:
    ...                - platform: 平台名稱 (iOS/Android) / Platform name (iOS/Android)
    ...                - capabilities: Appium 功能設定字典 / Appium capabilities dictionary
    ...                
    ...                前置條件 / Prerequisites:
    ...                - Appium 服務器必須已啟動 / Appium server must be running
    ...                - 測試設備或模擬器必須可用 / Test device or emulator must be available
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 使用者已準備好移動應用程式    iOS    app=/path/to/app.ipa
    ...                Given 使用者已準備好移動應用程式    Android    appPackage=com.example.app
    ...                
    ...                執行結果 / Execution Result:
    ...                - 開啟指定平台的應用程式 / Opens application on specified platform
    [Arguments]    ${platform}    &{capabilities}
    [Tags]    given    mobile    setup
    
    Open Application    ${platform}    &{capabilities}
    Log    Given: 移動應用程式 ${platform} 已準備就緒

Given 應用程式已啟動
    [Documentation]    應用程式已啟動
    ...                Application is launched
    ...                
    ...                參數說明 / Parameters:
    ...                - platform: 平台名稱 (iOS/Android) / Platform name (iOS/Android)
    ...                - capabilities: Appium 功能設定字典 / Appium capabilities dictionary
    ...                
    ...                前置條件 / Prerequisites:
    ...                - Appium 服務器必須已啟動 / Appium server must be running
    ...                - 應用程式必須已安裝在設備上 / Application must be installed on device
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 應用程式已啟動    iOS    bundleId=com.example.app
    ...                Given 應用程式已啟動    Android    appActivity=.MainActivity
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 確認應用程式成功啟動 / Confirms application starts successfully
    [Arguments]    ${platform}    &{capabilities}
    [Tags]    given    mobile    setup
    
    Open Application    ${platform}    &{capabilities}
    Log    Given: ${platform} 應用程式已成功啟動

Given 使用者在登入畫面
    [Documentation]    用戶在登入畫面
    ...                User is on login screen
    ...                
    ...                參數說明 / Parameters:
    ...                - login_screen_locator: 登入畫面定位器 / Login screen locator (default: accessibility_id=login_screen)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 應用程式必須已啟動 / Application must be launched
    ...                - 登入畫面必須存在且可訪問 / Login screen must exist and be accessible
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 使用者在登入畫面
    ...                Given 使用者在登入畫面    id=login_page
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 確認登入畫面可見 / Confirms login screen is visible
    ...                - 等待元素載入完成 / Waits for element loading completion
    [Arguments]    ${login_screen_locator}=accessibility_id=login_screen
    [Tags]    given    mobile    precondition
    
    AppiumLibrary.Wait Until Element Is Visible    ${login_screen_locator}    timeout=30
    Log    Given: 用戶已在登入畫面

Given 應用程式載入已完成
    [Documentation]    應用程式載入完成
    ...                Application loading is complete
    ...                
    ...                參數說明 / Parameters:
    ...                - loading_indicator: 載入指示器定位器 / Loading indicator locator
    ...                - timeout: 最大等待時間（秒）/ Maximum wait time (seconds) (default: 30)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 應用程式必須已啟動 / Application must be launched
    ...                - 載入指示器必須存在 / Loading indicator must exist
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 應用程式載入已完成    id=loading_spinner
    ...                Given 應用程式載入已完成    class=loading-indicator    60
    ...                
    ...                執行流程 / Execution Flow:
    ...                1. 等待載入指示器出現 / Wait for loading indicator to appear
    ...                2. 等待載入指示器消失 / Wait for loading indicator to disappear
    [Arguments]    ${loading_indicator}    ${timeout}=30
    [Tags]    given    mobile    precondition
    
    AppiumLibrary.Wait Until Element Is Visible    ${loading_indicator}    timeout=5
    Wait Until Element Is Not Visible    ${loading_indicator}    timeout=${timeout}
    Log    Given: 應用程式載入已完成

# ============================================================================
# WHEN Keywords (Actions) - 動作關鍵字
# ============================================================================

When 使用者點擊元素
    [Documentation]    用戶點擊元素
    ...                User taps on element
    ...                
    ...                參數說明 / Parameters:
    ...                - locator: 元素定位器 / Element locator
    ...                - timeout: 等待超時時間（秒）/ Wait timeout (seconds) (default: 10)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 元素必須存在且可點擊 / Element must exist and be clickable
    ...                - 應用程式必須已啟動 / Application must be launched
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者點擊元素    id=submit_button
    ...                When 使用者點擊元素    xpath=//button[@text='Login']    15
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 元素不存在或不可點擊時會超時 / Times out if element doesn't exist or isn't clickable
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    when    mobile    action
    
    Click Element    ${locator}    timeout=${timeout}
    Log    When: 用戶點擊了元素 ${locator}

When 使用者輸入文字
    [Documentation]    用戶輸入文字
    ...                User enters text
    ...                
    ...                參數說明 / Parameters:
    ...                - locator: 輸入欄位定位器 / Input field locator
    ...                - text: 要輸入的文字 / Text to input
    ...                - timeout: 等待超時時間（秒）/ Wait timeout (seconds) (default: 10)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 輸入欄位必須存在且可編輯 / Input field must exist and be editable
    ...                - 元素必須獲得焦點 / Element must be focused
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者輸入文字    id=username_field    testuser
    ...                When 使用者輸入文字    name=password    secretpassword    20
    ...                
    ...                說明 / Notes:
    ...                - 會清除欄位現有內容後輸入新文字 / Clears existing content before entering new text
    [Arguments]    ${locator}    ${text}    ${timeout}=10
    [Tags]    when    mobile    action
    
    Input Text    ${locator}    ${text}    timeout=${timeout}
    Log    When: 用戶在 ${locator} 輸入了文字 "${text}"

When 使用者滑動螢幕
    [Documentation]    用戶滑動螢幕
    ...                User swipes screen
    ...                
    ...                參數說明 / Parameters:
    ...                - direction: 滑動方向 (up/down) / Swipe direction (up/down)
    ...                - duration: 滑動持續時間（毫秒）/ Swipe duration (milliseconds) (default: 1000)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 應用程式必須已啟動且可滑動 / Application must be launched and scrollable
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者滑動螢幕    up
    ...                When 使用者滑動螢幕    down    1500
    ...                
    ...                支援的方向 / Supported Directions:
    ...                - up: 向上滑動 / Swipe up
    ...                - down: 向下滑動 / Swipe down
    [Arguments]    ${direction}    ${duration}=1000
    [Tags]    when    mobile    action
    
    Run Keyword If    '${direction}' == 'up'        Scroll Up        duration=${duration}
    Run Keyword If    '${direction}' == 'down'      Scroll Down      duration=${duration}
    Log    When: 用戶向 ${direction} 滑動螢幕

When 使用者登入應用程式
    [Documentation]    用戶登入應用程式
    ...                User logs into application
    ...                
    ...                參數說明 / Parameters:
    ...                - username: 使用者名稱 / Username
    ...                - password: 密碼 / Password
    ...                - username_field: 使用者名稱欄位定位器 / Username field locator
    ...                - password_field: 密碼欄位定位器 / Password field locator
    ...                - login_button: 登入按鈕定位器 / Login button locator
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 使用者必須在登入畫面 / User must be on login screen
    ...                - 所有輸入欄位和按鈕必須可見 / All input fields and button must be visible
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者登入應用程式    admin    password123    id=username    id=password    id=login_btn
    ...                
    ...                執行流程 / Execution Flow:
    ...                1. 輸入使用者名稱 / Enter username
    ...                2. 輸入密碼 / Enter password
    ...                3. 點擊登入按鈕 / Click login button
    [Arguments]    ${username}    ${password}    ${username_field}    ${password_field}    ${login_button}
    [Tags]    when    mobile    action
    
    Input Text    ${username_field}    ${username}    timeout=10
    Input Text    ${password_field}    ${password}    timeout=10
    Click Element    ${login_button}    timeout=10
    Log    When: 用戶使用帳號 "${username}" 執行登入操作

When 使用者擷取螢幕截圖
    [Documentation]    用戶擷取螢幕截圖
    ...                User takes screenshot
    ...                
    ...                參數說明 / Parameters:
    ...                - filename: 截圖檔案名稱 / Screenshot filename (optional)
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者擷取螢幕截圖
    ...                When 使用者擷取螢幕截圖    login_screen.png
    ...                
    ...                回傳 / Returns:
    ...                - 截圖檔案路徑 / Screenshot file path
    ...                
    ...                說明 / Notes:
    ...                - 如果未提供檔名，系統會自動生成 / Auto-generates filename if not provided
    [Arguments]    ${filename}=${EMPTY}
    [Tags]    when    mobile    action
    
    ${screenshot_path}=    Run Keyword If    '${filename}' == '${EMPTY}'
    ...    Take Screenshot
    ...    ELSE
    ...    Take Screenshot    filename=${filename}
    
    Log    When: 用戶擷取了螢幕截圖 ${screenshot_path}
    RETURN    ${screenshot_path}

When 使用者等待元素
    [Documentation]    用戶等待元素出現
    ...                User waits for element
    ...                
    ...                參數說明 / Parameters:
    ...                - locator: 元素定位器 / Element locator
    ...                - timeout: 最大等待時間（秒）/ Maximum wait time (seconds) (default: 30)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 元素最終必須會出現 / Element must eventually appear
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者等待元素    id=loading_complete
    ...                When 使用者等待元素    xpath=//button[@text='Continue']    60
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 超時時間內元素未出現會失敗 / Fails if element doesn't appear within timeout
    [Arguments]    ${locator}    ${timeout}=30
    [Tags]    when    mobile    action
    
    AppiumLibrary.Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Log    When: 用戶等待元素 ${locator} 出現

# ============================================================================
# THEN Keywords (Assertions) - 驗證關鍵字
# ============================================================================

Then 元素文字應該是
    [Documentation]    元素文字應該是
    ...                Element text should be
    ...                
    ...                參數說明 / Parameters:
    ...                - locator: 元素定位器 / Element locator
    ...                - expected_text: 預期的文字內容 / Expected text content
    ...                - timeout: 等待超時時間（秒）/ Wait timeout (seconds) (default: 10)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 元素必須存在且包含文字 / Element must exist and contain text
    ...                
    ...                用法範例 / Usage Example:
    ...                Then Element Text Should Be    id=welcome_message    Welcome, User!
    ...                Then Element Text Should Be    class=error_msg    Invalid credentials    15
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查元素文字是否完全匹配預期值 / Checks if element text exactly matches expected value
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=10
    [Tags]    then    mobile    assertion
    
    ${actual_text}=    Get Text    ${locator}    timeout=${timeout}
    Should Be Equal    ${actual_text}    ${expected_text}
    Log    Then: 元素 ${locator} 的文字驗證成功，內容為 "${expected_text}"

Then 元素應該可見
    [Documentation]    驗證：元素應該可見
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    then    mobile    assertion
    
    AppiumLibrary.Element Should Be Visible    ${locator}    timeout=${timeout}
    Log    Then: 元素 ${locator} 已成功驗證為可見

Then 應用程式應該已關閉
    [Documentation]    驗證：應用程式應該已關閉
    [Tags]    then    mobile    assertion
    
    AppiumLibrary.Close Application
    Log    Then: 應用程式已成功關閉

Then 使用者應該看到載入完成
    [Documentation]    驗證：用戶應該看到載入完成
    [Arguments]    ${success_indicator}    ${timeout}=30
    [Tags]    then    mobile    assertion
    
    AppiumLibrary.Wait Until Element Is Visible    ${success_indicator}    timeout=${timeout}
    Log    Then: 用戶已看到載入完成指示器 ${success_indicator}

Then 登入應該成功
    [Documentation]    驗證：登入應該成功
    [Arguments]    ${success_indicator}=accessibility_id=home_screen
    [Tags]    then    mobile    assertion
    
    AppiumLibrary.Wait Until Element Is Visible    ${success_indicator}    timeout=30
    Log    Then: 登入已成功驗證，顯示 ${success_indicator}

# ============================================================================
# AND Keywords (Conjunctions) - 連接關鍵字
# ============================================================================

And 使用者同時點擊元素
    [Documentation]    連接：用戶同時也點擊元素
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    and    mobile    action
    
    Click Element    ${locator}    timeout=${timeout}
    Log    And: 用戶同時也點擊了元素 ${locator}

And 應用程式仍在運行
    [Documentation]    連接：應用程式仍在運行
    [Arguments]    ${indicator}=accessibility_id=main_screen
    [Tags]    and    mobile    verification
    
    AppiumLibrary.Element Should Be Visible    ${indicator}    timeout=10
    Log    And: 應用程式仍在正常運行

And 使用者可以看到元素
    [Documentation]    連接：用戶可以看到元素
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    and    mobile    verification
    
    AppiumLibrary.Element Should Be Visible    ${locator}    timeout=${timeout}
    Log    And: 用戶可以看到元素 ${locator}

And 截圖已擷取
    [Documentation]    連接：截圖已擷取
    [Arguments]    ${filename}=${EMPTY}
    [Tags]    and    mobile    action
    
    ${screenshot_path}=    Run Keyword If    '${filename}' == '${EMPTY}'
    ...    Take Screenshot
    ...    ELSE
    ...    Take Screenshot    filename=${filename}
    
    Log    And: 截圖已擷取並儲存為 ${screenshot_path}
    RETURN    ${screenshot_path}

# ============================================================================
# Legacy Keywords (向後相容) - 舊版關鍵字
# ============================================================================

Open Mobile Application
    [Documentation]    舊版：開啟移動應用程式 (建議使用 Given User Has Mobile Application Ready)
    [Arguments]    ${platform}    &{capabilities}
    [Tags]    legacy    mobile    setup
    
    Given User Has Mobile Application Ready    ${platform}    &{capabilities}

Close Mobile Application
    [Documentation]    舊版：關閉移動應用程式 (建議使用 Then 應用程式應該已關閉)
    [Tags]    legacy    mobile    teardown
    
    Then 應用程式應該已關閉

Tap Element
    [Documentation]    舊版：點擊元素 (建議使用 When User Taps On Element)
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    legacy    mobile    interaction
    
    When User Taps On Element    ${locator}    ${timeout}

Input Text Into Field
    [Documentation]    舊版：輸入文字 (建議使用 When User Enters Text)
    [Arguments]    ${locator}    ${text}    ${timeout}=10
    [Tags]    legacy    mobile    interaction
    
    When User Enters Text    ${locator}    ${text}    ${timeout}

Verify Element Text
    [Documentation]    舊版：驗證元素文字 (建議使用 Then 元素文字應該是)
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=10
    [Tags]    legacy    mobile    verification
    
    Then 元素文字應該是    ${locator}    ${expected_text}    ${timeout}

Wait For Element
    [Documentation]    舊版：等待元素 (建議使用 When User Waits For Element)
    [Arguments]    ${locator}    ${timeout}=30
    [Tags]    legacy    mobile    wait
    
    When User Waits For Element    ${locator}    ${timeout}

Verify Element Visible
    [Documentation]    舊版：驗證元素可見 (建議使用 Then 元素應該可見)
    [Arguments]    ${locator}    ${timeout}=10
    [Tags]    legacy    mobile    verification
    
    Then 元素應該可見    ${locator}    ${timeout}

Swipe Screen
    [Documentation]    舊版：滑動螢幕 (建議使用 When User Swipes Screen)
    [Arguments]    ${direction}    ${duration}=1000
    [Tags]    legacy    mobile    gesture
    
    When User Swipes Screen    ${direction}    ${duration}

Take Mobile Screenshot
    [Documentation]    舊版：擷取截圖 (建議使用 When User Takes Screenshot)
    [Arguments]    ${filename}=${EMPTY}
    [Tags]    legacy    mobile    screenshot
    
    ${screenshot_path}=    When User Takes Screenshot    ${filename}
    RETURN    ${screenshot_path}

Wait For Application To Load
    [Documentation]    舊版：等待應用載入 (建議使用 Given Application Loading Is Complete)
    [Arguments]    ${loading_indicator}    ${timeout}=30
    [Tags]    legacy    mobile    wait
    
    Given Application Loading Is Complete    ${loading_indicator}    ${timeout}

Login To Mobile App
    [Documentation]    舊版：移動應用程式登入流程 (建議使用 When User Logs Into Application)
    [Arguments]    ${username}    ${password}    ${username_field}    ${password_field}    ${login_button}
    [Tags]    legacy    mobile    login
    
    When User Logs Into Application    ${username}    ${password}    ${username_field}    ${password_field}    ${login_button}

# ============================================================================
# 中文關鍵字 (Chinese Keywords) - 向後相容
# ============================================================================

打開行動應用程式
    [Documentation]    中文：開啟移動應用程式 (建議使用 Given User Has Mobile Application Ready)
    [Arguments]    ${platform}    ${app_path}    ${device_name}    ${platform_version}
    [Tags]    chinese    legacy    mobile    setup
    
    ${desired_caps}=    Create Dictionary
    ...    platformName=${platform}
    ...    deviceName=${device_name}
    ...    platformVersion=${platform_version}
    ...    app=${app_path}
    
    # 根據平台設定 automationName
    Run Keyword If    '${platform}' == 'Android'
    ...    Set To Dictionary    ${desired_caps}    automationName=UiAutomator2
    ...    ELSE IF    '${platform}' == 'iOS'
    ...    Set To Dictionary    ${desired_caps}    automationName=XCUITest
    
    Open Application    http://localhost:4723/wd/hub    ${desired_caps}
    Log    已開啟 ${platform} 行動應用程式

關閉行動應用程式
    [Documentation]    中文：關閉移動應用程式 (建議使用 Then Application Should Be Closed)
    [Tags]    chinese    legacy    mobile    teardown
    
    AppiumLibrary.Close Application
    Log    已關閉行動應用程式

輸入文字到行動應用程式元素
    [Documentation]    中文：輸入文字到元素 (建議使用 When User Enters Text)
    [Arguments]    ${locator}    ${text}
    [Tags]    chinese    legacy    mobile    action
    
    Input Text    ${locator}    ${text}
    Log    已在元素 ${locator} 輸入文字: ${text}

點擊行動應用程式元素
    [Documentation]    中文：點擊元素 (建議使用 When User Taps On Element)
    [Arguments]    ${locator}
    [Tags]    chinese    legacy    mobile    action
    
    Click Element    ${locator}
    Log    已點擊行動應用程式元素: ${locator}

等待行動應用程式頁面包含文字
    [Documentation]    中文：等待頁面包含文字 (建議使用 Then Element Text Should Be)
    [Arguments]    ${text}
    [Tags]    chinese    legacy    mobile    wait
    
    Wait Until Page Contains    ${text}
    Log    行動應用程式頁面已包含文字: ${text}

等待行動應用程式頁面包含元素
    [Documentation]    中文：等待頁面包含元素 (建議使用 When User Waits For Element)
    [Arguments]    ${locator}
    [Tags]    chinese    legacy    mobile    wait
    
    Wait Until Page Contains Element    ${locator}
    Log    行動應用程式頁面已包含元素: ${locator}

行動應用程式頁面不包含文字
    [Documentation]    中文：頁面不應包含文字 (建議使用 Then 相關關鍵字)
    [Arguments]    ${text}
    [Tags]    chinese    legacy    mobile    assertion
    
    Page Should Not Contain Text    ${text}
    Log    行動應用程式頁面不包含文字: ${text}

行動應用程式頁面不包含元素
    [Documentation]    中文：頁面不應包含元素 (建議使用 Then 相關關鍵字)
    [Arguments]    ${locator}
    [Tags]    chinese    legacy    mobile    assertion
    
    Page Should Not Contain Element    ${locator}
    Log    行動應用程式頁面不包含元素: ${locator}


