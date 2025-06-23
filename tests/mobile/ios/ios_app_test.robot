*** Settings ***
Documentation    iOS 應用測試範例 - Gherkin 風格
...              使用 Given-When-Then 結構進行行為驅動測試
Suite Setup      Given iOS 測試環境已準備就緒
Suite Teardown   Then iOS 測試環境已清理完成
Resource         ../../resources/mobile_keywords.robot

*** Variables ***
${IOS_BUNDLE_ID}        com.example.app
${IOS_DEVICE_NAME}      iPhone 14
${IOS_PLATFORM_VERSION} 16.0

*** Test Cases ***
Scenario: User Launches iOS Application Successfully
    [Documentation]    情境：用戶成功啟動 iOS 應用程式
    [Tags]    ios    smoke    gherkin
    
    Given 使用者已準備好移動應用程式    ios
    ...    bundleId=${IOS_BUNDLE_ID}
    ...    deviceName=${IOS_DEVICE_NAME}
    ...    platformVersion=${IOS_PLATFORM_VERSION}
    When 使用者擷取螢幕截圖    ios_launch_test.png
    And 使用者等待元素    accessibility_id=main_screen    timeout=30
    Then 元素應該可見    accessibility_id=main_screen
    And 應用程式應該被關閉

Scenario: User Logs Into iOS Application With Valid Credentials
    [Documentation]    情境：用戶使用有效憑證登入 iOS 應用程式
    [Tags]    ios    login    functional    gherkin
    
    Given 使用者已準備好移動應用程式    ios
    ...    bundleId=${IOS_BUNDLE_ID}
    ...    deviceName=${IOS_DEVICE_NAME}
    ...    platformVersion=${IOS_PLATFORM_VERSION}
    And 使用者在登錄畫面    accessibility_id=login_screen
    When 使用者登錄到應用程式
    ...    testuser
    ...    testpass123
    ...    accessibility_id=username_field
    ...    accessibility_id=password_field
    ...    accessibility_id=login_button
    Then 登錄應該成功    accessibility_id=home_screen
    And 元素文字應該為    accessibility_id=welcome_message    歡迎回來
    And 螢幕截圖已擷取    ios_login_success.png
    Then 應用程式應該被關閉

Scenario: User Navigates Through iOS Application Menu
    [Documentation]    情境：用戶在 iOS 應用程式中進行導航
    [Tags]    ios    navigation    functional    gherkin
    
    Given User Has Mobile Application Ready    ios
    ...    bundleId=${IOS_BUNDLE_ID}
    ...    deviceName=${IOS_DEVICE_NAME}
    ...    platformVersion=${IOS_PLATFORM_VERSION}
    And User Waits For Element    accessibility_id=main_screen    timeout=30
    When User Taps On Element    accessibility_id=menu_button
    And User Waits For Element    accessibility_id=settings_option
    And User Taps On Element    accessibility_id=settings_option
    Then Element Should Be Visible    accessibility_id=settings_screen
    And Screenshot Is Taken    ios_settings_screen.png
    When User Taps On Element    accessibility_id=back_button
    Then Element Should Be Visible    accessibility_id=main_screen
*** Keywords ***
Given iOS Test Environment Is Ready
    [Documentation]    前置條件：iOS 測試環境已準備就緒
    [Tags]    given    setup    ios
    
    Log    Given: iOS 測試環境已設置完成
    # 檢查 Appium 伺服器狀態
    # 可以在此處添加環境檢查邏輯

Then iOS Test Environment Is Cleaned Up
    [Documentation]    驗證：iOS 測試環境已清理完成
    [Tags]    then    teardown    ios
    
    Log    Then: iOS 測試環境已清理完成
    # 確保所有應用程式連接都已關閉
    Run Keyword And Ignore Error    Then Application Should Be Closed
