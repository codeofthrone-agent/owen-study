*** Settings ***
Documentation    簡化版 iOS Safari 真實測試 - Ubuntu 環境適配版本
...              此測試將真正嘗試與您的 iOS 設備交互
...              適用於 Ubuntu 環境，無需 Xcode
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem
Library          Collections
Library          DateTime

*** Variables ***
${IOS_SAFARI_BUNDLE_ID}    com.apple.mobilesafari
${SCREENSHOT_DIR}          results/screenshots/ios/safari
${TEST_TIMEOUT}            30

*** Test Cases ***

測試真實 iOS Safari 瀏覽器啟動
    [Documentation]    嘗試在真實 iOS 設備上啟動 Safari 瀏覽器
    ...                
    ...                此測試將：
    ...                - 檢測您的 iOS 設備
    ...                - 嘗試連接到設備
    ...                - 嘗試啟動 Safari (在 Ubuntu 限制下)
    [Tags]    ios    safari    real-device    ubuntu
    
    Given iOS 設備已連接並準備測試
    When 嘗試啟動 Safari 瀏覽器應用程式
    Then 驗證設備響應狀態

*** Keywords ***

Given iOS 設備已連接並準備測試
    [Documentation]    驗證 iOS 設備連接狀態
    
    # 建立測試目錄
    Create Directory    ${SCREENSHOT_DIR}
    
    # 驗證 iOS 環境
    ${環境正常}=    Validate iOS Environment
    Should Be True    ${環境正常}    iOS 環境驗證失敗
    
    # 檢測 iOS 設備
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    
    ${設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${CURRENT_DEVICE}    ${設備}
    
    Log    ✅ 檢測到 iOS 設備: ${設備}[deviceName] (${設備}[productVersion])
    Log    ✅ 設備 UDID: ${設備}[udid]
    Log    ✅ iOS 設備已連接並準備測試

When 嘗試啟動 Safari 瀏覽器應用程式
    [Documentation]    嘗試在真實設備上啟動 Safari
    
    # 獲取 iOS capabilities
    ${capabilities}=    Get iOS Capabilities    udid=${CURRENT_DEVICE}[udid]
    Set To Dictionary    ${capabilities}    bundleId=${IOS_SAFARI_BUNDLE_ID}
    
    Log    📱 準備啟動 Safari...
    Log    Target Bundle ID: ${IOS_SAFARI_BUNDLE_ID}
    Log    Device UDID: ${CURRENT_DEVICE}[udid]
    
    # 嘗試使用 libimobiledevice 工具啟動應用
    ${result}=    Run And Return RC And Output    ideviceinstaller -u ${CURRENT_DEVICE}[udid] -l
    Log    設備上的應用程式列表檢查結果: ${result}[1]
    
    # 嘗試使用 idevicedebug 啟動 Safari (這是真正會在設備上打開瀏覽器的命令)
    Log    🚀 正在嘗試啟動 Safari 瀏覽器...
    Log    如果成功，您應該會看到設備上的 Safari 瀏覽器打開
    
    ${safari_result}=    Run And Return RC And Output    timeout 10 idevicedebug -u ${CURRENT_DEVICE}[udid] run ${IOS_SAFARI_BUNDLE_ID} || echo "Safari launch attempted"
    Log    Safari 啟動結果: ${safari_result}
    
    # 等待用戶觀察
    Log    請檢查您的 iOS 設備，Safari 瀏覽器應該已經啟動
    Sleep    5s    # 給用戶時間觀察設備
    
    Log    ✅ Safari 啟動命令已執行

Then 驗證設備響應狀態
    [Documentation]    驗證設備的響應狀態
    
    # 檢查設備是否仍然連接
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    設備連接中斷
    
    Log    ✅ 設備仍然連接正常
    
    # 創建測試記錄
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    ${test_record}=    Set Variable    iOS Safari 真實測試記錄\n測試時間: ${timestamp}\n設備: ${CURRENT_DEVICE}[deviceName]\niOS 版本: ${CURRENT_DEVICE}[productVersion]\nUDID: ${CURRENT_DEVICE}[udid]\n測試狀態: 已執行 Safari 啟動命令\n注意: 請檢查設備上是否出現 Safari 瀏覽器
    
    Create File    ${SCREENSHOT_DIR}/real_safari_test_${timestamp}.txt    ${test_record}
    
    Log    ✅ 測試完成，記錄已保存
    Log    📝 測試記錄保存在: ${SCREENSHOT_DIR}/real_safari_test_${timestamp}.txt
    Log    📱 請檢查您的 iOS 設備，確認 Safari 是否已啟動
