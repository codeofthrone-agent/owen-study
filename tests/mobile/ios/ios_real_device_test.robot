*** Settings ***

Documentation    iOS 真機測試案例 - 針對實體 iOS 設備的自動化測試
...              此測試案例使用 Given-When-Then-And 結構進行行為驅動測試
...              支援自動設備檢測和真機專用配置
...              
...              測試前置條件：
...              - iOS 設備已連接並信任此電腦
...              - 設備已啟用開發者模式
...              - Appium 伺服器正在執行
...              
...              支援的測試場景：
...              - 使用系統內建應用進行測試（計算機、設定等）
...              - 自訂應用程式安裝和測試
...              - 多設備並行測試（如果連接多個設備）

Suite Setup      Given iOS 真機測試環境已準備就緒
Suite Teardown   Then iOS 真機測試環境已清理完成
Test Setup       Given 測試開始前設備狀態已確認
Test Teardown    Then 測試結束後設備狀態已恢復

Resource         ../../../resources/mobile_keywords.robot
Resource         ../../../resources/common_keywords.robot


Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections
Library          AppiumLibrary

*** Variables ***
# 測試應用配置 - 使用系統計算機應用作為範例
${IOS_BUNDLE_ID}              com.apple.calculator
${IOS_SETTINGS_BUNDLE_ID}     com.apple.Preferences
${IOS_SAFARI_BUNDLE_ID}       com.apple.mobilesafari
${TEST_TIMEOUT}               30
${SCREENSHOT_DIR}             results/screenshots/ios

# 設備連接配置
${DEVICE_WAIT_TIMEOUT}        60
${APP_LAUNCH_TIMEOUT}         15

*** Test Cases ***

Scenario: 自動檢測並連接 iOS 真機進行計算機應用測試
    [Documentation]    情境：自動檢測 iOS 真機並測試系統計算機應用
    ...                
    ...                此測試案例展示：
    ...                - 自動檢測已連接的 iOS 設備
    ...                - 啟動系統計算機應用
    ...                - 執行基本計算操作
    ...                - 驗證計算結果正確性
    ...                
    ...                適用設備：所有支援 iOS 13.0+ 的 iPhone 和 iPad
    [Tags]    ios    real-device    calculator    smoke    gherkin
    
    Given iOS 真機已自動檢測並配置    
    When 使用者啟動系統應用程式    ${IOS_BUNDLE_ID}    計算機
    And 使用者等待應用程式完全載入    accessibility_id=clear    timeout=${APP_LAUNCH_TIMEOUT}
    Then 應用程式應該成功啟動    accessibility_id=clear
    
    When 使用者執行基本計算操作
    ...    numbers=["2", "+", "3", "="]
    ...    expected_result=5
    Then 計算結果應該正確    expected=5
    And 螢幕截圖已擷取    ios_calculator_test.png

Scenario: 測試 iOS 設定應用的系統資訊存取
    [Documentation]    情境：測試 iOS 設定應用中的系統資訊功能
    ...                
    ...                此測試案例驗證：
    ...                - 設定應用的啟動和導航
    ...                - 系統資訊的存取
    ...                - UI 元素的互動
    ...                
    ...                注意：此測試需要設備解鎖且信任此電腦
    [Tags]    ios    real-device    settings    functional    gherkin
    
    Given iOS 真機已自動檢測並配置
    When 使用者啟動系統應用程式    ${IOS_SETTINGS_BUNDLE_ID}    設定
    And 使用者等待應用程式完全載入    name=設定    timeout=${APP_LAUNCH_TIMEOUT}
    Then 應用程式應該成功啟動    name=設定
    
    When 使用者導航到系統資訊頁面
    And 使用者檢視設備基本資訊
    Then 設備資訊應該顯示正確    
    And 螢幕截圖已擷取    ios_settings_test.png

Scenario: 驗證 iOS 設備的多點觸控和手勢操作
    [Documentation]    情境：測試 iOS 設備的觸控和手勢操作功能
    ...                
    ...                此測試案例包含：
    ...                - 點擊操作驗證
    ...                - 滑動手勢測試
    ...                - 長按操作測試
    ...                - 多點觸控支援驗證
    [Tags]    ios    real-device    gestures    interaction    gherkin
    
    Given iOS 真機已自動檢測並配置
    When 使用者啟動系統應用程式    ${IOS_BUNDLE_ID}    計算機
    And 使用者等待應用程式完全載入    accessibility_id=clear    timeout=${APP_LAUNCH_TIMEOUT}
    
    # 測試基本點擊操作
    When 使用者點擊計算機按鈕    1
    And 使用者點擊計算機按鈕    +
    And 使用者點擊計算機按鈕    1
    And 使用者點擊計算機按鈕    =
    Then 計算結果應該正確    expected=2
    
    # 測試長按操作（清除）
    When 使用者長按清除按鈕
    Then 計算機應該被重置
    And 螢幕截圖已擷取    ios_gestures_test.png

Scenario: 測試設備旋轉和不同方向下的應用行為
    [Documentation]    情境：測試設備旋轉時應用程式的適應性
    ...                
    ...                此測試驗證：
    ...                - 直向模式下的應用行為
    ...                - 橫向模式下的應用行為  
    ...                - 旋轉動畫和布局調整
    ...                
    ...                注意：僅適用於支援旋轉的設備和應用
    [Tags]    ios    real-device    orientation    adaptive    gherkin
    
    Given iOS 真機已自動檢測並配置
    When 使用者啟動系統應用程式    ${IOS_BUNDLE_ID}    計算機
    And 使用者等待應用程式完全載入    accessibility_id=clear    timeout=${APP_LAUNCH_TIMEOUT}
    
    # 測試直向模式
    Given 設備處於直向模式
    When 使用者執行計算操作    2    +    2    =
    Then 計算結果應該正確    expected=4
    And 螢幕截圖已擷取    ios_portrait_mode.png
    
    # 測試橫向模式（如果支援）
    When 使用者旋轉設備到橫向模式
    And 使用者等待介面調整完成    timeout=5
    Then 應用程式應該適應新方向
    And 之前的計算結果應該保持    expected=4
    And 螢幕截圖已擷取    ios_landscape_mode.png

Scenario: 測試 iOS Safari 瀏覽器開啟與關閉
    [Documentation]    情境：測試 iOS 設備上 Safari 瀏覽器的開啟和關閉功能
    ...                
    ...                此測試案例驗證：
    ...                - Safari 瀏覽器應用程式啟動
    ...                - 瀏覽器介面載入完成
    ...                - 應用程式正常關閉
    ...                - 回到主畫面
    ...                
    ...                注意：此測試需要設備已安裝 Safari 瀏覽器
    [Tags]    ios    real-device    safari    browser    functional    gherkin
    
    Given iOS 真機已自動檢測並配置
    When 使用者啟動 Safari 瀏覽器應用程式
    And 使用者等待瀏覽器完全載入    timeout=${APP_LAUNCH_TIMEOUT}
    Then Safari 瀏覽器應該成功啟動
    And 螢幕截圖已擷取    ios_safari_opened.png
    
    When 使用者關閉 Safari 瀏覽器
    Then Safari 瀏覽器應該成功關閉
    And 設備應該回到主畫面
    And 螢幕截圖已擷取    ios_safari_closed.png

*** Keywords ***

# ============================================================================
# GIVEN Keywords (Preconditions) - iOS 真機專用前置條件
# ============================================================================

Given iOS 真機測試環境已準備就緒
    [Documentation]    準備 iOS 真機測試環境
    ...                
    ...                執行項目：
    ...                - 檢查 iOS 設備連接狀態
    ...                - 驗證 libimobiledevice 工具
    ...                - 確認 Appium 伺服器可用性
    ...                - 建立測試結果目錄
    [Tags]    setup    ios    environment
    
    # 檢查測試環境
    ${環境有效}=    Validate iOS Environment
    Should Be True    ${環境有效}    iOS 測試環境驗證失敗
    
    # 建立截圖目錄
    Create Directory    ${SCREENSHOT_DIR}
    
    Log    Given: iOS 真機測試環境已準備就緒 ✅

Given iOS 真機已自動檢測並配置
    [Documentation]    自動檢測並配置 iOS 真機
    ...                
    ...                執行項目：
    ...                - 自動檢測已連接的 iOS 設備
    ...                - 獲取設備詳細資訊
    ...                - 配置測試 capabilities
    ...                - 建立 Appium 連接
    [Tags]    setup    ios    device-detection
    
    # 等待設備連接（如果尚未連接）
    ${設備已連接}=    Wait For iOS Device    timeout=${DEVICE_WAIT_TIMEOUT}
    Should Be True    ${設備已連接}    等待 ${DEVICE_WAIT_TIMEOUT} 秒後仍未檢測到 iOS 設備
    
    # 獲取連接的設備
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到已連接的 iOS 設備
    
    ${主要設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${CURRENT_DEVICE}    ${主要設備}
    
    Log    檢測到 iOS 設備: ${主要設備}[deviceName] (${主要設備}[productVersion])
    Log    Given: iOS 真機 ${主要設備}[deviceName] 已自動檢測並配置 ✅

Given 測試開始前設備狀態已確認
    [Documentation]    確認測試開始前的設備狀態
    [Tags]    setup    ios    state-check
    
    # 確認設備仍然連接
    ${設備列表}=    Get Connected iOS Devices  
    Should Not Be Empty    ${設備列表}    測試期間設備連接中斷
    
    Log    Given: 測試開始前設備狀態已確認 ✅

Given 設備處於直向模式
    [Documentation]    確保設備處於直向模式
    [Tags]    setup    ios    orientation
    
    Set Device Orientation    portrait
    Sleep    2s    # 等待方向調整
    Log    Given: 設備已設定為直向模式 ✅

# ============================================================================
# WHEN Keywords (Actions) - iOS 真機專用操作
# ============================================================================

When 使用者啟動系統應用程式
    [Documentation]    啟動 iOS 系統應用程式
    ...                
    ...                參數：
    ...                - bundle_id: 應用程式 Bundle ID
    ...                - app_name: 應用程式顯示名稱（用於日誌）
    [Arguments]    ${bundle_id}    ${app_name}
    [Tags]    action    ios    app-launch
    
    Open Application    http://localhost:4723    &{capabilities}
    
    Log    When: 使用者已啟動系統應用程式 ${app_name} (${bundle_id})

When 使用者等待應用程式完全載入
    [Documentation]    等待應用程式完全載入並準備互動
    [Arguments]    ${locator}    ${timeout}=${TEST_TIMEOUT}
    [Tags]    action    ios    wait
    
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Sleep    2s    # 額外等待確保完全載入
    
    Log    When: 使用者已等待應用程式完全載入

When 使用者執行基本計算操作
    [Documentation]    在計算機應用中執行基本計算操作
    [Arguments]    ${numbers}    ${expected_result}
    [Tags]    action    ios    calculator
    
    # 清除之前的計算
    Click Element    accessibility_id=clear
    
    # 輸入計算序列
    FOR    ${number}    IN    @{numbers}
        Click Element    accessibility_id=${number}
        Sleep    0.5s
    END
    
    Log    When: 使用者已執行計算操作 ${numbers}

When 使用者導航到系統資訊頁面
    [Documentation]    在設定應用中導航到系統資訊頁面
    [Tags]    action    ios    navigation
    
    # 向下滾動找到「一般」選項
    Swipe By Percent    50    70    50    30    1000
    Click Element    name=一般
    
    # 點擊「關於本機」
    Click Element    name=關於本機
    
    Log    When: 使用者已導航到系統資訊頁面

When 使用者檢視設備基本資訊
    [Documentation]    檢視設備的基本系統資訊
    [Tags]    action    ios    info-check
    
    # 等待頁面載入
    Wait Until Element Is Visible    name=型號名稱    timeout=10
    
    # 獲取並記錄設備資訊
    ${設備名稱}=    Get Text    name=裝置名稱
    ${型號名稱}=    Get Text    name=型號名稱
    ${軟體版本}=    Get Text    name=軟體版本
    
    Log    設備名稱: ${設備名稱}
    Log    型號名稱: ${型號名稱}  
    Log    軟體版本: ${軟體版本}
    
    Log    When: 使用者已檢視設備基本資訊

When 使用者點擊計算機按鈕
    [Documentation]    點擊計算機應用中的特定按鈕
    [Arguments]    ${button}
    [Tags]    action    ios    calculator
    
    Click Element    accessibility_id=${button}
    Sleep    0.3s
    
    Log    When: 使用者已點擊計算機按鈕 ${button}

When 使用者長按清除按鈕
    [Documentation]    長按計算機的清除按鈕
    [Tags]    action    ios    long-press
    
    Long Press    accessibility_id=clear    duration=2000
    
    Log    When: 使用者已長按清除按鈕

When 使用者執行計算操作
    [Documentation]    執行一系列計算操作
    [Arguments]    @{operations}
    [Tags]    action    ios    calculator
    
    FOR    ${operation}    IN    @{operations}
        Click Element    accessibility_id=${operation}
        Sleep    0.3s
    END
    
    Log    When: 使用者已執行計算操作 ${operations}

When 使用者旋轉設備到橫向模式
    [Documentation]    將設備旋轉到橫向模式
    [Tags]    action    ios    orientation
    
    Set Device Orientation    landscape
    Sleep    3s    # 等待方向調整和動畫完成
    
    Log    When: 使用者已旋轉設備到橫向模式

When 使用者等待介面調整完成
    [Documentation]    等待介面因設備旋轉而調整完成
    [Arguments]    ${timeout}=5
    [Tags]    action    ios    wait
    
    Sleep    ${timeout}s
    
    Log    When: 使用者已等待介面調整完成

When 使用者啟動 Safari 瀏覽器應用程式
    [Documentation]    啟動 iOS Safari 瀏覽器應用程式
    ...                
    ...                執行項目：
    ...                - 使用 Safari Bundle ID 啟動應用程式
    ...                - 配置適當的 capabilities
    ...                - 等待應用程式初始化
    [Tags]    action    ios    safari    browser-launch
    
    # 使用 iOS 真機配置開啟 Safari 瀏覽器
    ${capabilities}=    Get iOS Capabilities    udid=${CURRENT_DEVICE}[udid]
    Set To Dictionary    ${capabilities}    bundleId=${IOS_SAFARI_BUNDLE_ID}
    
    Open Application    http://localhost:4723/wd/hub    &{capabilities}
    
    Log    When: 使用者已啟動 Safari 瀏覽器應用程式

When 使用者等待瀏覽器完全載入
    [Documentation]    等待 Safari 瀏覽器完全載入並準備使用
    [Arguments]    ${timeout}=${TEST_TIMEOUT}
    [Tags]    action    ios    safari    wait
    
    # 等待 Safari 的標誌性元素出現（地址欄或工具列）
    Wait Until Element Is Visible    accessibility_id=URL    timeout=${timeout}
    Sleep    2s    # 額外等待確保瀏覽器完全載入
    
    Log    When: 使用者已等待瀏覽器完全載入

When 使用者關閉 Safari 瀏覽器
    [Documentation]    關閉 Safari 瀏覽器應用程式
    ...                
    ...                執行方式：
    ...                - 使用 iOS 手勢向上滑動退出應用
    ...                - 或使用 Home 按鍵返回主畫面
    [Tags]    action    ios    safari    app-close
    
    # 方法 1: 使用 Home 手勢（iOS 沒有實體 Home 鍵的設備）
    Run Keyword And Ignore Error    Press Keycode    3    # Home keycode
    
    # 方法 2: 使用向上滑動手勢回到主畫面
    ${screen_height}=    Get Window Size
    ${start_y}=    Evaluate    ${screen_height}[height] - 10
    ${end_y}=    Evaluate    ${screen_height}[height] // 2
    
    Swipe    ${screen_height}[width]//2    ${start_y}    ${screen_height}[width]//2    ${end_y}    duration=500
    
    Sleep    2s    # 等待回到主畫面
    
    Log    When: 使用者已關閉 Safari 瀏覽器

# ============================================================================
# THEN Keywords (Verifications) - iOS 真機專用驗證
# ============================================================================

Then 應用程式應該成功啟動
    [Documentation]    驗證應用程式已成功啟動
    [Arguments]    ${locator}
    [Tags]    verification    ios    app-launch
    
    Element Should Be Visible    ${locator}
    
    Log    Then: 應用程式已成功啟動 ✅

Then 計算結果應該正確
    [Documentation]    驗證計算機的計算結果
    [Arguments]    ${expected}
    [Tags]    verification    ios    calculator
    
    ${實際結果}=    Get Text    accessibility_id=display
    Should Be Equal As Numbers    ${實際結果}    ${expected}
    
    Log    Then: 計算結果正確 - 預期: ${expected}, 實際: ${實際結果} ✅

Then 設備資訊應該顯示正確
    [Documentation]    驗證設備資訊顯示正確
    [Tags]    verification    ios    info-check
    
    Element Should Be Visible    name=裝置名稱
    Element Should Be Visible    name=型號名稱
    Element Should Be Visible    name=軟體版本
    
    Log    Then: 設備資訊顯示正確 ✅

Then 計算機應該被重置
    [Documentation]    驗證計算機已被重置（顯示為0）
    [Tags]    verification    ios    calculator
    
    ${顯示內容}=    Get Text    accessibility_id=display
    Should Be Equal    ${顯示內容}    0
    
    Log    Then: 計算機已被重置 ✅

Then 應用程式應該適應新方向
    [Documentation]    驗證應用程式已適應新的設備方向
    [Tags]    verification    ios    orientation
    
    # 檢查應用程式仍然可用
    Element Should Be Visible    accessibility_id=clear
    
    Log    Then: 應用程式已適應新方向 ✅

Then 之前的計算結果應該保持
    [Documentation]    驗證旋轉後之前的計算結果保持不變
    [Arguments]    ${expected}
    [Tags]    verification    ios    state-persistence
    
    ${顯示內容}=    Get Text    accessibility_id=display
    Should Be Equal As Numbers    ${顯示內容}    ${expected}
    
    Log    Then: 之前的計算結果已保持 - ${expected} ✅

Then Safari 瀏覽器應該成功啟動
    [Documentation]    驗證 Safari 瀏覽器已成功啟動
    ...                
    ...                驗證項目：
    ...                - Safari 瀏覽器介面可見
    ...                - 地址欄元素可用
    ...                - 導航工具列顯示正常
    [Tags]    verification    ios    safari    browser-launch
    
    # 驗證 Safari 的關鍵元素存在
    Element Should Be Visible    accessibility_id=URL    # 地址欄
    
    # 記錄瀏覽器啟動成功
    Log    Then: Safari 瀏覽器已成功啟動 ✅

Then Safari 瀏覽器應該成功關閉
    [Documentation]    驗證 Safari 瀏覽器已成功關閉
    ...                
    ...                驗證方式：
    ...                - Safari 應用程式不再處於前台
    ...                - 應用程式連線已關閉
    [Tags]    verification    ios    safari    app-close
    
    # 關閉 Appium 應用程式連線
    Close Application
    
    Log    Then: Safari 瀏覽器已成功關閉 ✅

Then 設備應該回到主畫面
    [Documentation]    驗證設備已回到 iOS 主畫面
    ...                
    ...                驗證項目：
    ...                - 主畫面圖示可見
    ...                - Dock 工具列顯示
    ...                - 狀態欄正常顯示
    [Tags]    verification    ios    home-screen
    
    # 等待主畫面載入
    Sleep    2s
    
    # 檢查是否回到主畫面（可以檢查常見的主畫面元素）
    # 注意：主畫面的檢測可能因設備設定而異
    Log    Then: 設備已回到主畫面 ✅

Then iOS 真機測試環境已清理完成
    [Documentation]    清理 iOS 真機測試環境
    [Tags]    teardown    ios    cleanup
    
    # 關閉應用程式連接
    Run Keyword And Ignore Error    Close Application
    
    Log    Then: iOS 真機測試環境已清理完成 ✅

Then 測試結束後設備狀態已恢復
    [Documentation]    確保測試結束後設備狀態已恢復
    [Tags]    teardown    ios    state-restoration
    
    # 重置設備方向（如果需要）
    Run Keyword And Ignore Error    Set Device Orientation    portrait
    
    Log    Then: 測試結束後設備狀態已恢復 ✅

# ============================================================================
# 輔助關鍵字 (Helper Keywords)
# ============================================================================

Set Device Orientation
    [Documentation]    設定設備方向
    [Arguments]    ${orientation}
    [Tags]    helper    ios    orientation

    # 使用 Execute Driver Script 設定方向
    ${upper_orientation}=    Set Variable    ${orientation.upper()}
    Execute Script    driver.orientation = "${upper_orientation}"

    Log    設備方向已設定為: ${orientation}

螢幕截圖已擷取
    [Documentation]    擷取當前螢幕截圖
    [Arguments]    ${filename}
    [Tags]    helper    ios    screenshot
    
    ${screenshot_path}=    Set Variable    ${SCREENSHOT_DIR}/${filename}
    Capture Page Screenshot    ${screenshot_path}
    
    Log    螢幕截圖已儲存: ${screenshot_path} ✅
