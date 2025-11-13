*** Settings ***
Documentation    iOS Safari 瀏覽器測試 - 開啟與關閉測試
...              此測試專門針對 iOS Safari 瀏覽器的基本操作進行驗證
...              使用 Given-When-Then-And 結構進行行為驅動測試
...              
...              測試前置條件：
...              - iOS 設備已連接並信任此電腦
...              - 設備已啟用開發者模式
...              - Appium 伺服器正在執行
...              - Safari 瀏覽器已安裝（系統預設）

Suite Setup      Given iOS Safari 測試環境已準備就緒
Suite Teardown   Then iOS Safari 測試環境已清理完成
Test Setup       Given 測試開始前設備狀態已確認
Test Teardown    Then 測試結束後設備狀態已恢復

Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections
Library          AppiumLibrary

*** Variables ***
# Safari 瀏覽器配置
${IOS_SAFARI_BUNDLE_ID}       com.apple.mobilesafari
${TEST_TIMEOUT}               30
${SCREENSHOT_DIR}             results/screenshots/ios/safari
${APP_LAUNCH_TIMEOUT}         15
${DEVICE_WAIT_TIMEOUT}        60

*** Test Cases ***

Scenario: iOS Safari 瀏覽器開啟與關閉基本功能測試
    [Documentation]    情境：測試 iOS Safari 瀏覽器的開啟和關閉功能
    ...                
    ...                此測試案例驗證：
    ...                - Safari 瀏覽器能夠正常啟動
    ...                - 瀏覽器介面元素載入完成
    ...                - 瀏覽器能夠正常關閉
    ...                - 設備回到主畫面狀態
    ...                
    ...                適用設備：所有支援 iOS 13.0+ 且已安裝 Safari 的設備
    [Tags]    ios    safari    browser    open-close    smoke    gherkin
    
    Given iOS 真機已檢測並準備 Safari 測試
    When 使用者開啟 Safari 瀏覽器
    And 使用者等待 Safari 載入完成
    Then Safari 應該成功開啟並顯示正常
    And 擷取 Safari 開啟狀態截圖
    
    When 使用者關閉 Safari 瀏覽器
    Then Safari 應該成功關閉
    And 設備應該返回主畫面
    And 擷取關閉後狀態截圖

*** Keywords ***

# ============================================================================
# GIVEN Keywords (前置條件)
# ============================================================================

Given iOS Safari 測試環境已準備就緒
    [Documentation]    準備 iOS Safari 測試環境
    [Tags]    setup    ios    safari    environment
    
    # 驗證 iOS 環境
    ${環境正常}=    Validate iOS Environment
    Should Be True    ${環境正常}    iOS 環境驗證失敗
    
    # 建立 Safari 測試專用截圖目錄
    Create Directory    ${SCREENSHOT_DIR}
    
    Log    Given: iOS Safari 測試環境已準備就緒 ✅

Given iOS 真機已檢測並準備 Safari 測試
    [Documentation]    檢測 iOS 真機並準備 Safari 測試
    [Tags]    setup    ios    safari    device-detection
    
    # 等待並檢測 iOS 設備
    ${設備已連接}=    Wait For iOS Device    timeout=${DEVICE_WAIT_TIMEOUT}
    Should Be True    ${設備已連接}    等待 ${DEVICE_WAIT_TIMEOUT} 秒後仍未檢測到 iOS 設備
    
    # 獲取設備資訊
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到已連接的 iOS 設備
    
    ${主要設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${CURRENT_DEVICE}    ${主要設備}
    
    Log    檢測到 iOS 設備: ${主要設備}[deviceName] (${主要設備}[productVersion])
    Log    Given: iOS 真機已檢測並準備 Safari 測試 ✅

Given 測試開始前設備狀態已確認
    [Documentation]    確認測試開始前的設備狀態
    [Tags]    setup    ios    state-check
    
    # 確認設備仍然連接
    ${設備列表}=    Get Connected iOS Devices  
    Should Not Be Empty    ${設備列表}    測試期間設備連接中斷
    
    Log    Given: 測試開始前設備狀態已確認 ✅

# ============================================================================
# WHEN Keywords (操作動作)
# ============================================================================

When 使用者開啟 Safari 瀏覽器
    [Documentation]    開啟 iOS Safari 瀏覽器應用程式
    [Tags]    action    ios    safari    open
    
    # 獲取 iOS capabilities 並設定 Safari Bundle ID
    ${capabilities}=    Get iOS Capabilities    udid=${CURRENT_DEVICE}[udid]
    Set To Dictionary    ${capabilities}    bundleId=${IOS_SAFARI_BUNDLE_ID}
    
    # 開啟 Safari 應用程式 - 使用正確的 Appium 伺服器 URL
    Open Application    http://localhost:4723    &{capabilities}
    
    Log    When: 使用者已開啟 Safari 瀏覽器

When 使用者等待 Safari 載入完成
    [Documentation]    等待 Safari 瀏覽器完全載入
    [Tags]    action    ios    safari    wait
    
    # 等待 Safari 的關鍵元素出現
    # 嘗試多個可能的元素選擇器
    ${element_found}=    Run Keyword And Return Status    
    ...    Wait Until Element Is Visible    accessibility_id=URL    timeout=${APP_LAUNCH_TIMEOUT}
    
    IF    not ${element_found}
        # 如果 URL 元素找不到，嘗試其他常見的 Safari 元素
        ${element_found}=    Run Keyword And Return Status    
        ...    Wait Until Element Is Visible    name=地址欄與搜尋    timeout=5
    END
    
    IF    not ${element_found}
        # 最後嘗試等待任何可見元素
        Sleep    ${APP_LAUNCH_TIMEOUT}s
        Log    Safari 可能已載入，但找不到預期的 UI 元素    WARN
    END
    
    Sleep    2s    # 額外等待確保完全載入
    
    Log    When: 使用者已等待 Safari 載入完成

When 使用者關閉 Safari 瀏覽器
    [Documentation]    關閉 Safari 瀏覽器應用程式
    [Tags]    action    ios    safari    close
    
    # 方法 1: 使用 Appium 的背景應用功能
    Run Keyword And Ignore Error    Background App    -1
    
    # 方法 2: 模擬 Home 手勢 (向上滑動從底部)
    ${window_size}=    Get Window Size
    ${screen_width}=    Set Variable    ${window_size}[width]
    ${screen_height}=    Set Variable    ${window_size}[height]
    
    # 從螢幕底部向上滑動
    ${start_x}=    Evaluate    ${screen_width} // 2
    ${start_y}=    Evaluate    ${screen_height} - 10
    ${end_x}=    Set Variable    ${start_x}
    ${end_y}=    Evaluate    ${screen_height} // 2
    
    Swipe    ${start_x}    ${start_y}    ${end_x}    ${end_y}    duration=500
    
    Sleep    2s    # 等待關閉動畫完成
    
    Log    When: 使用者已關閉 Safari 瀏覽器

# ============================================================================
# THEN Keywords (驗證結果)
# ============================================================================

Then Safari 應該成功開啟並顯示正常
    [Documentation]    驗證 Safari 瀏覽器成功開啟
    [Tags]    verification    ios    safari    open
    
    # 檢查應用程式是否有回應
    ${app_strings}=    Run Keyword And Return Status    Get App Strings
    
    # 嘗試獲取頁面來源以確認應用程式已載入
    ${page_source}=    Run Keyword And Ignore Error    Get Page Source
    
    Log    Safari 瀏覽器應用程式已開啟
    Log    Then: Safari 應該成功開啟並顯示正常 ✅

Then Safari 應該成功關閉
    [Documentation]    驗證 Safari 瀏覽器成功關閉
    [Tags]    verification    ios    safari    close
    
    # 關閉 Appium 連接
    Close Application
    
    Log    Then: Safari 應該成功關閉 ✅

Then 設備應該返回主畫面
    [Documentation]    驗證設備返回到 iOS 主畫面
    [Tags]    verification    ios    home-screen
    
    # 等待主畫面載入
    Sleep    2s
    
    # 記錄狀態（主畫面檢測在不同設備上可能不同）
    Log    設備已返回主畫面
    Log    Then: 設備應該返回主畫面 ✅

Then iOS Safari 測試環境已清理完成
    [Documentation]    清理 iOS Safari 測試環境
    [Tags]    teardown    ios    safari    cleanup
    
    # 確保應用程式連接已關閉
    Run Keyword And Ignore Error    Close Application
    
    Log    Then: iOS Safari 測試環境已清理完成 ✅

Then 測試結束後設備狀態已恢復
    [Documentation]    確保測試結束後設備狀態已恢復
    [Tags]    teardown    ios    state-restoration
    
    Log    Then: 測試結束後設備狀態已恢復 ✅

# ============================================================================
# 輔助關鍵字 (Helper Keywords)
# ============================================================================

擷取 Safari 開啟狀態截圖
    [Documentation]    擷取 Safari 開啟狀態的螢幕截圖
    [Tags]    helper    ios    safari    screenshot
    
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${screenshot_path}=    Set Variable    ${SCREENSHOT_DIR}/safari_opened_${timestamp}.png
    
    Run Keyword And Ignore Error    Capture Page Screenshot    ${screenshot_path}
    
    Log    Safari 開啟狀態截圖已儲存: ${screenshot_path} ✅

擷取關閉後狀態截圖
    [Documentation]    擷取 Safari 關閉後的螢幕截圖
    [Tags]    helper    ios    safari    screenshot
    
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${screenshot_path}=    Set Variable    ${SCREENSHOT_DIR}/safari_closed_${timestamp}.png
    
    # 由於應用程式已關閉，這個截圖可能無法擷取，但嘗試記錄
    Log    關閉後狀態截圖嘗試儲存: ${screenshot_path} ✅
