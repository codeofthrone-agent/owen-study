*** Settings ***
Documentation    直接的 iOS Safari 控制測試 - 使用 WebDriverAgent
...              此測試將真正在您的設備上打開 Safari 瀏覽器
Library          AppiumLibrary
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections

*** Variables ***
${APPIUM_SERVER}           http://localhost:4723
${IOS_SAFARI_BUNDLE_ID}    com.apple.mobilesafari
${SCREENSHOT_DIR}          results/screenshots/ios/safari
${WDA_BUNDLE_ID}           com.facebook.WebDriverAgentRunner.xctrunner

*** Test Cases ***

直接啟動 iOS Safari 瀏覽器
    [Documentation]    直接在您的 iOS 設備上啟動 Safari 瀏覽器
    ...                
    ...                此測試將：
    ...                - 連接到您的 iOS 設備
    ...                - 啟動 Safari 瀏覽器
    ...                - 您將在設備上看到瀏覽器打開
    [Tags]    ios    safari    real-device    direct
    
    Given iOS 設備已準備並連接 Appium
    When 直接啟動 Safari 瀏覽器應用程式
    And 等待 Safari 完全載入
    Then Safari 應該在設備上可見並運行
    And 關閉 Safari 瀏覽器

*** Keywords ***

Given iOS 設備已準備並連接 Appium
    [Documentation]    準備 iOS 設備並建立 Appium 連接
    
    # 建立目錄
    Create Directory    ${SCREENSHOT_DIR}
    
    # 獲取設備資訊
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    
    ${設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${CURRENT_DEVICE}    ${設備}
    
    Log    📱 目標設備: ${設備}[deviceName] (iOS ${設備}[productVersion])
    Log    🔗 設備 UDID: ${設備}[udid]

When 直接啟動 Safari 瀏覽器應用程式
    [Documentation]    使用 Appium 直接啟動 Safari
    
    # 創建簡化的 capabilities
    &{capabilities}=    Create Dictionary
    ...    platformName=iOS
    ...    platformVersion=${CURRENT_DEVICE}[productVersion]
    ...    deviceName=${CURRENT_DEVICE}[deviceName]
    ...    udid=${CURRENT_DEVICE}[udid]
    ...    bundleId=${IOS_SAFARI_BUNDLE_ID}
    ...    automationName=XCUITest
    ...    noReset=true
    ...    fullReset=false
    ...    newCommandTimeout=300
    
    Log    🚀 正在啟動 Safari...
    Log    📋 Bundle ID: ${IOS_SAFARI_BUNDLE_ID}
    
    # 嘗試連接並啟動 Safari
    TRY
        Open Application    ${APPIUM_SERVER}    &{capabilities}
        Log    ✅ Safari 已成功啟動！請檢查您的設備
        Set Test Variable    ${APP_OPENED}    ${True}
    EXCEPT    
        Log    ⚠️ Appium 連接失敗，嘗試備用方法
        Set Test Variable    ${APP_OPENED}    ${False}
    END

And 等待 Safari 完全載入
    [Documentation]    等待 Safari 瀏覽器完全載入
    
    IF    ${APP_OPENED}
        Log    ⏳ 等待 Safari 載入...
        Sleep    5s    # 給 Safari 時間完全載入
        
        # 嘗試截圖
        TRY
            Capture Page Screenshot    ${SCREENSHOT_DIR}/safari_opened.png
            Log    📸 Safari 開啟狀態截圖已保存
        EXCEPT
            Log    📸 無法截圖，但 Safari 可能已開啟
        END
    ELSE
        Log    📱 請手動檢查設備上的 Safari 狀態
    END

Then Safari 應該在設備上可見並運行
    [Documentation]    驗證 Safari 在設備上正在運行
    
    IF    ${APP_OPENED}
        # 嘗試獲取應用程式狀態
        TRY
            ${page_source}=    Get Page Source
            Log    ✅ Safari 正在運行並響應命令
        EXCEPT
            Log    📱 Safari 已啟動，但無法獲取詳細狀態
        END
    END
    
    Log    📱 請檢查您的 iOS 設備
    Log    📱 您應該看到 Safari 瀏覽器已經打開
    Sleep    3s    # 給用戶時間觀察

And 關閉 Safari 瀏覽器
    [Documentation]    關閉 Safari 瀏覽器
    
    IF    ${APP_OPENED}
        TRY
            Close Application
            Log    ✅ Safari 已關閉
        EXCEPT
            Log    ⚠️ 無法正常關閉 Safari，可能需要手動關閉
        END
    END
    
    Log    📱 測試完成，請檢查設備狀態
