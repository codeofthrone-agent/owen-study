*** Settings ***
Documentation    基本 iOS 設備連接測試
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          AppiumLibrary

*** Test Cases ***
測試 iOS 設備檢測
    [Documentation]    簡單測試 iOS 設備檢測功能
    [Tags]    ios    basic    device-detection
    
    # 檢測 iOS 設備
    ${設備列表}=    Get Connected iOS Devices
    Log    檢測到的設備: ${設備列表}
    
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    
    # 獲取第一個設備的資訊
    ${設備}=    Set Variable    ${設備列表}[0]
    Log    設備名稱: ${設備}[deviceName]
    Log    UDID: ${設備}[udid]
    Log    iOS 版本: ${設備}[productVersion]
    
    # 驗證環境
    ${環境正常}=    Validate iOS Environment
    Should Be True    ${環境正常}    iOS 環境驗證失敗

測試 iOS Capabilities 生成
    [Documentation]    測試 iOS capabilities 自動生成
    [Tags]    ios    basic    capabilities
    
    # 獲取設備列表
    ${設備列表}=    Get Connected iOS Devices
    ${設備}=    Set Variable    ${設備列表}[0]
    
    # 生成 capabilities
    ${capabilities}=    Get iOS Capabilities    udid=${設備}[udid]
    
    # 驗證必要的 capabilities
    Should Contain    ${capabilities}    platformName
    Should Contain    ${capabilities}    udid
    Should Be Equal    ${capabilities}[platformName]    iOS
    
    Log    生成的 capabilities: ${capabilities}
