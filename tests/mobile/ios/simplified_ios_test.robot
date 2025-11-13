*** Settings ***
Documentation    簡化版 iOS 真機測試 - 僅測試設備檢測和基本連接
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections

*** Variables ***
${SCREENSHOT_DIR}    results/screenshots/ios

*** Test Cases ***
Scenario: 測試 iOS 設備自動檢測和配置
    [Documentation]    驗證 iOS 設備自動檢測和配置功能
    [Tags]    ios    device-detection    basic
    
    Given iOS 測試環境已驗證
    When 系統自動檢測 iOS 設備
    Then iOS 設備應該被成功檢測
    And 設備資訊應該完整

*** Keywords ***
Given iOS 測試環境已驗證
    [Documentation]    驗證 iOS 測試環境
    
    # 建立必要目錄
    Create Directory    ${SCREENSHOT_DIR}
    
    # 驗證環境
    ${環境正常}=    Validate iOS Environment
    Should Be True    ${環境正常}    iOS 環境驗證失敗
    
    Log    Given: iOS 測試環境已驗證 ✅

When 系統自動檢測 iOS 設備
    [Documentation]    系統自動檢測已連接的 iOS 設備
    
    # 等待設備連接
    ${設備已連接}=    Wait For iOS Device    timeout=30
    Should Be True    ${設備已連接}    30秒內未檢測到 iOS 設備
    
    # 獲取設備列表
    ${設備列表}=    Get Connected iOS Devices
    Set Test Variable    ${檢測到的設備}    ${設備列表}
    
    ${設備數量}=    Get Length    ${設備列表}
    Log    When: 系統已檢測到 ${設備數量} 個 iOS 設備

Then iOS 設備應該被成功檢測
    [Documentation]    驗證 iOS 設備成功檢測
    
    Should Not Be Empty    ${檢測到的設備}    未檢測到任何 iOS 設備
    
    # 獲取主要設備
    ${主要設備}=    Get From List    ${檢測到的設備}    0
    Set Test Variable    ${主要設備資訊}    ${主要設備}
    
    Log    Then: iOS 設備成功檢測 - ${主要設備}[deviceName] ✅

And 設備資訊應該完整
    [Documentation]    驗證設備資訊完整性
    
    # 驗證必要的設備資訊欄位
    Should Contain    ${主要設備資訊}    udid
    Should Contain    ${主要設備資訊}    deviceName
    Should Contain    ${主要設備資訊}    productVersion
    
    # 記錄設備詳細資訊
    Log    設備名稱: ${主要設備資訊}[deviceName]
    Log    UDID: ${主要設備資訊}[udid]
    Log    iOS 版本: ${主要設備資訊}[productVersion]
    
    # 測試 capabilities 生成
    ${capabilities}=    Get iOS Capabilities    udid=${主要設備資訊}[udid]
    Should Contain    ${capabilities}    platformName
    Should Be Equal    ${capabilities}[platformName]    iOS
    
    Log    And: 設備資訊完整且 capabilities 正確生成 ✅
