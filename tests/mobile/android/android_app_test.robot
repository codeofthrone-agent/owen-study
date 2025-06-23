*** Settings ***
Documentation    Android 應用測試範例 - Gherkin 風格
...              使用 Given-When-Then 結構進行行為驅動測試
Suite Setup      Given Android 測試環境已準備就緒
Suite Teardown   Then Android 測試環境已清理完成
Resource         ../../resources/mobile_keywords.robot

*** Variables ***
${ANDROID_APP_PACKAGE}      com.example.app
${ANDROID_APP_ACTIVITY}     .MainActivity
${ANDROID_DEVICE_NAME}      Android Emulator
${ANDROID_PLATFORM_VERSION} 11

*** Test Cases ***
Scenario: User Launches Android Application Successfully
    [Documentation]    情境：用戶成功啟動 Android 應用程式
    [Tags]    android    smoke    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${ANDROID_APP_PACKAGE}
    ...    appActivity=${ANDROID_APP_ACTIVITY}
    ...    deviceName=${ANDROID_DEVICE_NAME}
    ...    platformVersion=${ANDROID_PLATFORM_VERSION}
    When 使用者擷取螢幕截圖    android_launch_test.png
    And 使用者等待元素    id=main_layout    timeout=30
    Then 元素應該可見    id=main_layout
    And 應用程式應該被關閉

Scenario: User Logs Into Android Application With Valid Credentials
    [Documentation]    情境：用戶使用有效憑證登入 Android 應用程式
    [Tags]    android    login    functional    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${ANDROID_APP_PACKAGE}
    ...    appActivity=${ANDROID_APP_ACTIVITY}
    ...    deviceName=${ANDROID_DEVICE_NAME}
    ...    platformVersion=${ANDROID_PLATFORM_VERSION}
    And 使用者在登錄畫面    id=login_layout
    When 使用者登錄到應用程式
    ...    testuser
    ...    testpass123
    ...    id=username_input
    ...    id=password_input
    ...    id=login_btn
    Then 登錄應該成功    id=home_layout
    And 元素文字應該為    id=welcome_text    歡迎回來
    And 螢幕截圖已擷取    android_login_success.png
    Then 應用程式應該被關閉
    ...    id=login_btn
Scenario: User Scrolls Through Android Application List
    [Documentation]    情境：用戶在 Android 應用程式中滾動清單
    [Tags]    android    scroll    functional    gherkin
    
    Given User Has Mobile Application Ready    android
    ...    appPackage=${ANDROID_APP_PACKAGE}
    ...    appActivity=${ANDROID_APP_ACTIVITY}
    ...    deviceName=${ANDROID_DEVICE_NAME}
    ...    platformVersion=${ANDROID_PLATFORM_VERSION}
    And User Waits For Element    id=main_layout    timeout=30
    When User Taps On Element    id=list_menu_item
    And User Waits For Element    id=list_view    timeout=30
    And Screenshot Is Taken    android_list_before_scroll.png
    When User Swipes Screen    down    duration=1500
    And User Waits For Application To Load    # Wait 1 second
    And Screenshot Is Taken    android_list_after_scroll_down.png
    When User Swipes Screen    up    duration=1500
    And User Waits For Application To Load    # Wait 1 second
    And Screenshot Is Taken    android_list_after_scroll_up.png
    Then Application Should Be Closed

Scenario: User Uses Android Back Navigation Successfully
    [Documentation]    情境：用戶成功使用 Android 返回鍵導航
    [Tags]    android    navigation    functional    gherkin
    
    Given User Has Mobile Application Ready    android
    ...    appPackage=${ANDROID_APP_PACKAGE}
    ...    appActivity=${ANDROID_APP_ACTIVITY}
    ...    deviceName=${ANDROID_DEVICE_NAME}
    ...    platformVersion=${ANDROID_PLATFORM_VERSION}
    And User Waits For Element    id=main_layout    timeout=30
    When User Taps On Element    id=settings_menu_item
    And User Waits For Element    id=settings_layout    timeout=30
    And Screenshot Is Taken    android_settings_screen.png
    When User Presses Android Back Button
    And User Waits For Element    id=main_layout    timeout=10
    Then Element Should Be Visible    id=main_layout
    And Screenshot Is Taken    android_back_to_main.png
    Then Application Should Be Closed

*** Keywords ***
Given Android Test Environment Is Ready
    [Documentation]    前置條件：Android 測試環境已準備就緒
    [Tags]    given    setup    android
    
    Log    Given: Android 測試環境已設置完成
    # 檢查 ADB 連接狀態
    # 可以在此處添加環境檢查邏輯

Then Android Test Environment Is Cleaned Up
    [Documentation]    驗證：Android 測試環境已清理完成
    [Tags]    then    teardown    android
    
    Log    Then: Android 測試環境已清理完成
    # 確保所有應用程式連接都已關閉
    Run Keyword And Ignore Error    Then Application Should Be Closed

When User Presses Android Back Button
    [Documentation]    動作：用戶按下 Android 返回鍵
    [Tags]    when    android    navigation
    
    Press Keycode    4    # Android 返回鍵
    Log    When: 用戶按下了 Android 返回鍵

When User Waits For Application To Load
    [Documentation]    動作：用戶等待應用程式載入（通用等待）
    [Arguments]    ${duration}=1s
    [Tags]    when    mobile    wait
    
    Sleep    ${duration}
    Log    When: 用戶等待應用程式載入 ${duration}
