*** Settings ***
Documentation    移動應用程式測試 - Gherkin 風格範例
...              展示 Given-When-Then 行為驅動開發 (BDD) 測試結構
...              
...              此文件展示如何使用 Gherkin 風格編寫 Robot Framework 測試案例
...              遵循 BDD 最佳實踐，提高測試可讀性和維護性

Resource         ../../../resources/mobile_keywords.robot

*** Variables ***
# 測試配置變數
${APP_PACKAGE}          com.example.testapp
${APP_ACTIVITY}         .MainActivity
${DEVICE_NAME}          Test Device
${PLATFORM_VERSION}     11

# 測試數據變數
${VALID_USERNAME}       testuser
${VALID_PASSWORD}       password123
${INVALID_USERNAME}     wronguser
${INVALID_PASSWORD}     wrongpass
${WELCOME_MESSAGE}      歡迎回來

# 元素定位器
${LOGIN_SCREEN}         id=login_screen
${USERNAME_FIELD}       id=username_input
${PASSWORD_FIELD}       id=password_input
${LOGIN_BUTTON}         id=login_button
${HOME_SCREEN}          id=home_screen
${WELCOME_TEXT}         id=welcome_message
${ERROR_MESSAGE}        id=error_message

*** Test Cases ***
Scenario: New User Successfully Launches The Application For The First Time
    [Documentation]    情境：新用戶首次成功啟動應用程式
    ...                作為一個新用戶
    ...                我想要啟動應用程式
    ...                以便我可以使用其功能
    [Tags]    smoke    first-launch    positive    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    When 使用者擷取螢幕截圖    first_launch.png
    Then 元素應該可見    ${LOGIN_SCREEN}
    And 使用者可以看到元素    ${USERNAME_FIELD}
    And 使用者可以看到元素    ${PASSWORD_FIELD}
    And 使用者可以看到元素    ${LOGIN_BUTTON}
    Then 應用程式應該被關閉

Scenario: Registered User Logs In With Valid Credentials
    [Documentation]    情境：註冊用戶使用有效憑證登入
    ...                作為一個註冊用戶
    ...                當我輸入正確的用戶名和密碼
    ...                那麼我應該能夠成功登入系統
    [Tags]    login    positive    functional    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    And 使用者在登錄畫面    ${LOGIN_SCREEN}
    When 使用者輸入文字    ${USERNAME_FIELD}    ${VALID_USERNAME}
    And 使用者輸入文字    ${PASSWORD_FIELD}    ${VALID_PASSWORD}
    And 使用者點擊元素    ${LOGIN_BUTTON}
    Then 登錄應該成功    ${HOME_SCREEN}
    And 元素文字應該為    ${WELCOME_TEXT}    ${WELCOME_MESSAGE}
    And 螢幕截圖已擷取    successful_login.png
    Then 應用程式應該被關閉

Scenario: User Attempts To Log In With Invalid Credentials
    [Documentation]    情境：用戶嘗試使用無效憑證登入
    ...                作為一個用戶
    ...                當我輸入錯誤的用戶名或密碼
    ...                那麼我應該看到錯誤訊息而無法登入
    [Tags]    login    negative    security    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    And 使用者在登錄畫面    ${LOGIN_SCREEN}
    When 使用者輸入文字    ${USERNAME_FIELD}    ${INVALID_USERNAME}
    And 使用者輸入文字    ${PASSWORD_FIELD}    ${INVALID_PASSWORD}
    And 使用者點擊元素    ${LOGIN_BUTTON}
    Then 元素應該可見    ${ERROR_MESSAGE}
    And 使用者可以看到元素    ${LOGIN_SCREEN}
    And 螢幕截圖已擷取    failed_login.png
    Then 應用程式應該被關閉

Scenario: User Logs In Successfully And Then Logs Out
    [Documentation]    情境：用戶成功登入後登出
    ...                作為一個登入的用戶
    ...                當我選擇登出功能
    ...                那麼我應該回到登入畫面
    [Tags]    login    logout    functional    user-journey    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    And 使用者在登錄畫面    ${LOGIN_SCREEN}
    When 使用者登錄到應用程式
    ...    ${VALID_USERNAME}
    ...    ${VALID_PASSWORD}
    ...    ${USERNAME_FIELD}
    ...    ${PASSWORD_FIELD}
    ...    ${LOGIN_BUTTON}
    Then 登錄應該成功    ${HOME_SCREEN}
    When 使用者點擊元素    id=menu_button
    And 使用者點擊元素    id=logout_button
    Then 元素應該可見    ${LOGIN_SCREEN}
    And 螢幕截圖已擷取    after_logout.png
    Then 應用程式應該被關閉

Scenario: User Navigates Through Application Main Features
    [Documentation]    情境：用戶瀏覽應用程式主要功能
    ...                作為一個登入的用戶
    ...                我想要瀏覽應用程式的各項功能
    ...                以便了解應用程式的能力
    [Tags]    navigation    exploration    functional    user-journey    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    And 使用者已成功登錄
    When 使用者探索應用程式功能
    Then 使用者應該看到所有主要功能
    And 所有導航應該正常運作
    Then 應用程式應該被關閉

Scenario: Application Handles Network Connectivity Issues Gracefully
    [Documentation]    情境：應用程式優雅地處理網路連接問題
    ...                作為一個使用者
    ...                當網路連接不穩定或中斷時
    ...                應用程式應該顯示適當的錯誤訊息
    [Tags]    network    error-handling    reliability    gherkin
    
    Given 使用者已準備好移動應用程式    android
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    And 使用者在登錄畫面    ${LOGIN_SCREEN}
    When 網路連接被中斷
    And 使用者嘗試登錄    ${VALID_USERNAME}    ${VALID_PASSWORD}
    Then 網路錯誤訊息應該被顯示
    And 使用者應該留在登錄畫面
    When 網路連接已恢復
    And 使用者再次嘗試登錄
    Then 登錄應該成功    ${HOME_SCREEN}
    Then 應用程式應該被關閉

*** Keywords ***
# ============================================================================
# 複合 Gherkin 關鍵字 (Composite Gherkin Keywords)
# ============================================================================

Given 使用者已成功登錄
    [Documentation]    複合前置條件：用戶已成功登入
    [Tags]    given    composite    login
    
    Given 使用者在登錄畫面    ${LOGIN_SCREEN}
    When 使用者登錄到應用程式
    ...    ${VALID_USERNAME}
    ...    ${VALID_PASSWORD}
    ...    ${USERNAME_FIELD}
    ...    ${PASSWORD_FIELD}
    ...    ${LOGIN_BUTTON}
    Then 登錄應該成功    ${HOME_SCREEN}
    Log    Given: 用戶已成功登入應用程式

When 使用者探索應用程式功能
    [Documentation]    複合動作：用戶探索應用程式功能
    [Tags]    when    composite    navigation
    
    When 使用者點擊元素    id=features_tab
    And 使用者等待元素    id=features_list    timeout=10
    And 螢幕截圖已擷取    features_screen.png
    When 使用者滑動螢幕    down    duration=1000
    And 使用者點擊元素    id=settings_tab
    And 使用者等待元素    id=settings_screen    timeout=10
    And 螢幕截圖已擷取    settings_screen.png
    Log    When: 用戶已探索應用程式主要功能

Then 使用者應該看到所有主要功能
    [Documentation]    複合驗證：用戶應該看到所有主要功能
    [Tags]    then    composite    verification
    
    Then 元素應該可見    id=feature_1
    And 元素應該可見    id=feature_2
    And 元素應該可見    id=feature_3
    And 元素應該可見    id=settings_option
    Log    Then: 用戶已看到所有主要功能

And 所有導航應該正常運作
    [Documentation]    複合驗證：所有導航應該正常工作
    [Tags]    and    composite    navigation
    
    When 使用者點擊元素    id=back_button
    Then 元素應該可見    ${HOME_SCREEN}
    And 使用者可以看到元素    id=navigation_menu
    Log    And: 所有導航功能正常工作

When 網路連接被中斷
    [Documentation]    動作：模擬網路連接中斷
    [Tags]    when    network    simulation
    
    # 這裡可以使用實際的網路控制 API 或模擬器控制
    Log    When: 網路連接已中斷 (模擬)
    # 實際實現可能需要：
    # Run Process    adb    shell    svc    wifi    disable
    # Run Process    adb    shell    svc    data    disable

When 使用者嘗試登錄
    [Documentation]    動作：用戶嘗試登入
    [Arguments]    ${username}    ${password}
    [Tags]    when    login    attempt
    
    When 使用者輸入文字    ${USERNAME_FIELD}    ${username}
    And 使用者輸入文字    ${PASSWORD_FIELD}    ${password}
    And 使用者點擊元素    ${LOGIN_BUTTON}
    Log    When: 用戶嘗試使用 ${username} 登入

Then 網路錯誤訊息應該被顯示
    [Documentation]    驗證：應該顯示網路錯誤訊息
    [Tags]    then    network    error
    
    Then 元素應該可見    id=network_error_message
    And 元素文字應該為    id=network_error_message    網路連接失敗，請檢查您的網路設定
    Log    Then: 網路錯誤訊息已正確顯示

And 使用者應該留在登錄畫面
    [Documentation]    驗證：用戶應該保持在登入畫面
    [Tags]    and    login    state
    
    And 元素應該可見    ${LOGIN_SCREEN}
    And 使用者可以看到元素    ${LOGIN_BUTTON}
    Log    And: 用戶仍在登入畫面

When 網路連接已恢復
    [Documentation]    動作：恢復網路連接
    [Tags]    when    network    restoration
    
    # 這裡可以使用實際的網路控制 API 或模擬器控制
    Log    When: 網路連接已恢復 (模擬)
    # 實際實現可能需要：
    # Run Process    adb    shell    svc    wifi    enable
    # Run Process    adb    shell    svc    data    enable

When 使用者再次嘗試登錄
    [Documentation]    動作：用戶再次嘗試登入
    [Tags]    when    login    retry
    
    When 使用者嘗試登錄    ${VALID_USERNAME}    ${VALID_PASSWORD}
    Log    When: 用戶再次嘗試登入
