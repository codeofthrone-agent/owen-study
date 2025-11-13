*** Settings ***
Documentation    簡化版 iOS Safari 瀏覽器開啟關閉測試
Library          ../../../config/mobile/ios_config.py
Library          AppiumLibrary
Library          OperatingSystem
Library          Collections

*** Variables ***
${IOS_SAFARI_BUNDLE_ID}    com.apple.mobilesafari
${APPIUM_SERVER_URL}       http://localhost:4723
${SCREENSHOT_DIR}          results/screenshots/ios/safari

*** Test Cases ***
測試 Safari 瀏覽器開啟與關閉
    [Documentation]    測試 iOS Safari 瀏覽器的基本開啟和關閉功能
    [Tags]    ios    safari    basic
    
    # 準備測試環境
    Create Directory    ${SCREENSHOT_DIR}
    
    # 檢測 iOS 設備
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    ${設備}=    Set Variable    ${設備列表}[0]
    
    # 準備 Safari capabilities
    ${capabilities}=    Get iOS Capabilities    udid=${設備}[udid]
    Set To Dictionary    ${capabilities}    bundleId=${IOS_SAFARI_BUNDLE_ID}
    
    Log    準備開啟 Safari on 設備: ${設備}[deviceName]
    
    # 開啟 Safari
    Open Application    ${APPIUM_SERVER_URL}    &{capabilities}
    
    # 等待 Safari 載入
    Sleep    5s
    
    # 嘗試擷取截圖（證明 Safari 已開啟）
    Run Keyword And Ignore Error    Capture Page Screenshot    ${SCREENSHOT_DIR}/safari_opened.png
    
    Log    Safari 瀏覽器已開啟
    
    # 關閉 Safari
    Close Application
    
    Log    Safari 瀏覽器測試完成
