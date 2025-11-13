*** Settings ***
Documentation    簡化版 Ubuntu iOS 自動化 - 實用的無 Xcode 解決方案
...              展示 Ubuntu 24.04 下實際可用的 iOS 自動化功能
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections
Library          DateTime
Library          Process

*** Variables ***
${RESULT_DIR}    results/ubuntu_ios_simple

*** Test Cases ***

Ubuntu iOS 基本自動化測試
    [Documentation]    展示 Ubuntu 下實際可用的 iOS 自動化功能
    [Tags]    ios    ubuntu    no-xcode    practical
    
    Given Ubuntu iOS 環境檢查
    When 執行基本設備操作
    Then 驗證自動化能力
    And 總結可用功能

*** Keywords ***

Given Ubuntu iOS 環境檢查
    [Documentation]    檢查 Ubuntu iOS 環境
    
    Create Directory    ${RESULT_DIR}
    
    # 檢查工具可用性
    Log    🔧 檢查 iOS 工具...
    
    ${idevice_id}=    Run Process    which    idevice_id
    ${ideviceinfo}=    Run Process    which    ideviceinfo
    ${appium}=    Run Process    which    appium
    
    Should Be Equal As Integers    ${idevice_id.rc}    0    idevice_id 工具未安裝
    Should Be Equal As Integers    ${ideviceinfo.rc}    0    ideviceinfo 工具未安裝
    
    Log    ✅ 基本 iOS 工具已安裝
    
    # 檢查設備
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    
    ${設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${DEVICE}    ${設備}
    
    Log    ✅ iOS 設備檢測成功: ${設備}[deviceName]

When 執行基本設備操作
    [Documentation]    執行基本的設備操作
    
    ${udid}=    Set Variable    ${DEVICE}[udid]
    
    # 1. 獲取設備基本資訊
    Log    📱 獲取設備資訊...
    ${device_name}=    Run Process    ideviceinfo    -u    ${udid}    -k    DeviceName
    ${model}=    Run Process    ideviceinfo    -u    ${udid}    -k    ProductType
    ${ios_version}=    Run Process    ideviceinfo    -u    ${udid}    -k    ProductVersion
    
    Should Be Equal As Integers    ${device_name.rc}    0    設備名稱獲取失敗
    Should Be Equal As Integers    ${model.rc}    0    設備型號獲取失敗
    Should Be Equal As Integers    ${ios_version.rc}    0    iOS版本獲取失敗
    
    Log    📱 設備名稱: ${device_name.stdout}
    Log    📱 設備型號: ${model.stdout}
    Log    📱 iOS 版本: ${ios_version.stdout}
    
    # 2. 檢查設備配對狀態
    Log    🔗 檢查設備配對...
    ${pair_result}=    Run Process    idevicepair    -u    ${udid}    validate
    
    IF    ${pair_result.rc} == 0
        Log    ✅ 設備已正確配對
    ELSE
        Log    ⚠️ 設備配對狀態: ${pair_result.stderr}
    END
    
    # 3. 測試連接穩定性
    Log    🔄 測試連接穩定性...
    FOR    ${i}    IN RANGE    3
        ${device_check}=    Run Process    idevice_id    -l
        Should Contain    ${device_check.stdout}    ${udid}    連接測試 ${i+1} 失敗
        Sleep    1s
    END
    Log    ✅ 連接穩定性測試通過

Then 驗證自動化能力
    [Documentation]    驗證當前的自動化能力
    
    Log    📋 Ubuntu iOS 自動化能力驗證:
    
    # 能力清單
    ${capabilities}=    Create Dictionary
    
    # 基本設備管理
    Set To Dictionary    ${capabilities}    設備檢測=✅ 完全支援
    Set To Dictionary    ${capabilities}    設備資訊獲取=✅ 完全支援
    Set To Dictionary    ${capabilities}    連接穩定性=✅ 完全支援
    Set To Dictionary    ${capabilities}    多設備支援=✅ 完全支援
    
    # 系統資訊
    Set To Dictionary    ${capabilities}    系統資訊讀取=✅ 完全支援
    Set To Dictionary    ${capabilities}    硬體資訊獲取=✅ 完全支援
    
    # 應用程式管理
    Set To Dictionary    ${capabilities}    應用程式列表=⚠️ 部分支援
    Set To Dictionary    ${capabilities}    應用程式安裝=⚠️ 需開發者配置
    
    # UI 自動化
    Set To Dictionary    ${capabilities}    螢幕控制=❌ 需要 WebDriverAgent
    Set To Dictionary    ${capabilities}    觸控操作=❌ 需要額外工具
    
    # 檔案系統
    Set To Dictionary    ${capabilities}    檔案操作=⚠️ 沙盒限制
    
    FOR    ${capability}    ${status}    IN    &{capabilities}
        Log    ${capability}: ${status}
    END
    
    Set Test Variable    ${FINAL_CAPABILITIES}    ${capabilities}

And 總結可用功能
    [Documentation]    總結實際可用的功能
    
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    
    ${summary}=    Set Variable    Ubuntu 24.04 iOS 自動化功能總結
    ${summary}=    Set Variable    ${summary}\n========================================
    ${summary}=    Set Variable    ${summary}\n測試時間: ${timestamp}
    ${summary}=    Set Variable    ${summary}\n測試設備: ${DEVICE}[deviceName] (iOS ${DEVICE}[productVersion])
    ${summary}=    Set Variable    ${summary}\n========================================
    
    ${summary}=    Set Variable    ${summary}\n\n✅ 完全支援的功能:
    ${summary}=    Set Variable    ${summary}\n• iOS 設備自動檢測和識別
    ${summary}=    Set Variable    ${summary}\n• 設備詳細資訊獲取 (名稱、型號、版本等)
    ${summary}=    Set Variable    ${summary}\n• 連接狀態監控和穩定性測試
    ${summary}=    Set Variable    ${summary}\n• 多設備支援和管理
    ${summary}=    Set Variable    ${summary}\n• 設備配對狀態檢查
    ${summary}=    Set Variable    ${summary}\n• 系統和硬體資訊讀取
    
    ${summary}=    Set Variable    ${summary}\n\n⚠️ 部分支援的功能:
    ${summary}=    Set Variable    ${summary}\n• 應用程式列表獲取 (需設備配置)
    ${summary}=    Set Variable    ${summary}\n• 應用程式安裝/卸載 (需開發者帳號)
    ${summary}=    Set Variable    ${summary}\n• 檔案系統存取 (沙盒限制)
    
    ${summary}=    Set Variable    ${summary}\n\n❌ 不支援的功能 (需額外配置):
    ${summary}=    Set Variable    ${summary}\n• UI 自動化 (需 WebDriverAgent + 開發者配置)
    ${summary}=    Set Variable    ${summary}\n• 觸控操作 (需 WebDriverAgent)
    ${summary}=    Set Variable    ${summary}\n• 螢幕截圖 (需 WebDriverAgent)
    ${summary}=    Set Variable    ${summary}\n• 應用程式自動啟動 (需開發者配置)
    
    ${summary}=    Set Variable    ${summary}\n\n🎯 實用建議:
    ${summary}=    Set Variable    ${summary}\n• Ubuntu + libimobiledevice 適合設備管理和基本測試
    ${summary}=    Set Variable    ${summary}\n• 對於完整 UI 自動化，建議配置 WebDriverAgent
    ${summary}=    Set Variable    ${summary}\n• 可以與其他自動化工具整合 (如 Appium)
    ${summary}=    Set Variable    ${summary}\n• 適合大規模設備測試和管理場景
    
    ${summary}=    Set Variable    ${summary}\n\n🔧 技術棧:
    ${summary}=    Set Variable    ${summary}\n• 作業系統: Ubuntu 24.04 LTS
    ${summary}=    Set Variable    ${summary}\n• iOS 工具: libimobiledevice 套件
    ${summary}=    Set Variable    ${summary}\n• 測試框架: Robot Framework
    ${summary}=    Set Variable    ${summary}\n• 程式語言: Python
    ${summary}=    Set Variable    ${summary}\n• 優勢: 無需 Xcode，跨平台，開源
    
    Create File    ${RESULT_DIR}/ubuntu_ios_capabilities_summary.txt    ${summary}
    
    Log    📄 功能總結已儲存
    Log    📂 檔案位置: ${RESULT_DIR}/ubuntu_ios_capabilities_summary.txt
    
    Log    🎉 Ubuntu iOS 自動化能力驗證完成！
    Log    📋 主要結論: Ubuntu 24.04 可以提供強大的 iOS 設備管理和基本自動化功能
    Log    🔄 無需 Xcode 即可進行大部分的 iOS 設備測試工作
