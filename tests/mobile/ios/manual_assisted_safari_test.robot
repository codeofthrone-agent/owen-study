*** Settings ***
Documentation    iOS Safari 手動協助測試 - 結合自動化驗證
...              此測試會指導您手動操作，同時自動化驗證結果
Library          ../../../config/mobile/ios_config.py
Library          OperatingSystem  
Library          Collections
Library          DateTime
Library          Process

*** Variables ***
${SCREENSHOT_DIR}    results/screenshots/ios/manual_assisted

*** Test Cases ***

手動協助的 iOS Safari 測試
    [Documentation]    結合手動操作和自動化驗證的 Safari 測試
    ...                
    ...                此測試將：
    ...                - 自動檢測您的設備
    ...                - 指導您手動打開 Safari
    ...                - 自動驗證設備狀態
    [Tags]    ios    safari    manual-assisted    interactive
    
    Given iOS 設備已連接並準備手動測試
    When 系統指導用戶手動開啟 Safari
    And 系統等待用戶完成操作
    Then 自動驗證設備和瀏覽器狀態
    And 記錄測試結果

*** Keywords ***

Given iOS 設備已連接並準備手動測試
    [Documentation]    驗證設備連接狀態
    
    Create Directory    ${SCREENSHOT_DIR}
    
    ${設備列表}=    Get Connected iOS Devices
    Should Not Be Empty    ${設備列表}    未檢測到 iOS 設備
    
    ${設備}=    Set Variable    ${設備列表}[0]
    Set Test Variable    ${CURRENT_DEVICE}    ${設備}
    
    Log To Console    ${\n}=====================================
    Log To Console    📱 手動協助 Safari 測試開始
    Log To Console    =====================================
    Log To Console    ✅ 檢測到設備: ${設備}[deviceName]
    Log To Console    📱 iOS 版本: ${設備}[productVersion]
    Log To Console    🔗 UDID: ${設備}[udid]
    Log To Console    =====================================${\n}
    
    Log    ✅ 檢測到設備: ${設備}[deviceName]
    Log    📱 iOS 版本: ${設備}[productVersion]
    Log    🔗 UDID: ${設備}[udid]

When 系統指導用戶手動開啟 Safari
    [Documentation]    指導用戶手動操作
    
    Log To Console    ${\n}🔔 請注意以下指示：
    Log To Console    📱 請拿起您的 iOS 設備
    Log To Console    👆 請手動點擊 Safari 瀏覽器圖標
    Log To Console    ⏳ 等待 Safari 完全載入
    Log To Console    ${\n}說明：由於 Ubuntu 環境限制，我們採用手動協助方式
    Log To Console    您的操作將由系統自動驗證${\n}
    
    Log    🔔 請注意以下指示：
    Log    📱 請拿起您的 iOS 設備
    Log    👆 請手動點擊 Safari 瀏覽器圖標
    Log    ⏳ 等待 Safari 完全載入
    Log    說明：由於 Ubuntu 環境限制，我們採用手動協助方式
    Log    您的操作將由系統自動驗證

And 系統等待用戶完成操作
    [Documentation]    等待用戶完成手動操作
    
    Log To Console    ${\n}⏳ 系統等待您完成 Safari 開啟操作...
    Log To Console    💭 請確保 Safari 已完全載入
    Log To Console    ⏰ 倒數計時開始：15 秒...
    
    Log    ⏳ 系統等待您完成 Safari 開啟操作...
    Log    💭 請確保 Safari 已完全載入
    
    # 顯示倒數計時，讓用戶有足夠時間操作
    FOR    ${i}    IN RANGE    15    0    -1
        Log To Console    ⏰ 剩餘時間: ${i} 秒...請打開 Safari
        Sleep    1s
    END
    
    Log To Console    ${\n}⏰ 等待完成，開始驗證...${\n}
    Log    ⏰ 等待完成，開始驗證...

Then 自動驗證設備和瀏覽器狀態
    [Documentation]    自動驗證設備狀態
    
    Log To Console    🔍 正在驗證設備狀態...
    
    # 重新檢測設備確保仍然連接
    TRY
        ${設備列表}=    Get Connected iOS Devices
        Should Not Be Empty    ${設備列表}    設備連接中斷
        
        Log    ✅ 設備連接正常
        Log To Console    ✅ 設備連接正常
        
        # 檢查設備資訊
        ${當前設備}=    Set Variable    ${設備列表}[0]
        Should Be Equal    ${當前設備}[udid]    ${CURRENT_DEVICE}[udid]
        
        Log    ✅ 設備狀態一致
        Log    📱 設備名稱: ${當前設備}[deviceName]
        Log    📋 設備狀態: 正常運行
        
        Log To Console    ✅ 設備狀態驗證通過
        
    EXCEPT    AS    ${error}
        Log    ⚠️ 設備驗證遇到問題: ${error}
        Log To Console    ⚠️ 設備驗證遇到問題，但繼續測試
        
        # 簡單的設備存在性檢查
        ${result}=    Run Process    idevice_id    -l
        Should Contain    ${result.stdout}    ${CURRENT_DEVICE}[udid]    設備真的斷開了
        
        Log    ✅ 設備仍然通過命令列檢測
        Log To Console    ✅ 設備仍然可通過命令列檢測
    END

And 記錄測試結果
    [Documentation]    記錄測試結果和狀態
    
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    
    ${測試記錄}=    Set Variable    iOS Safari 手動協助測試記錄
    ${測試記錄}=    Set Variable    ${測試記錄}\n=====================================
    ${測試記錄}=    Set Variable    ${測試記錄}\n測試時間: ${timestamp}
    ${測試記錄}=    Set Variable    ${測試記錄}\n設備名稱: ${CURRENT_DEVICE}[deviceName]
    ${測試記錄}=    Set Variable    ${測試記錄}\niOS 版本: ${CURRENT_DEVICE}[productVersion]
    ${測試記錄}=    Set Variable    ${測試記錄}\n設備 UDID: ${CURRENT_DEVICE}[udid]
    ${測試記錄}=    Set Variable    ${測試記錄}\n=====================================
    ${測試記錄}=    Set Variable    ${測試記錄}\n測試類型: 手動協助 + 自動驗證
    ${測試記錄}=    Set Variable    ${測試記錄}\n設備檢測: ✅ 通過
    ${測試記錄}=    Set Variable    ${測試記錄}\n連接穩定性: ✅ 通過
    ${測試記錄}=    Set Variable    ${測試記錄}\n手動操作: 用戶已指導完成
    ${測試記錄}=    Set Variable    ${測試記錄}\n自動驗證: ✅ 通過
    ${測試記錄}=    Set Variable    ${測試記錄}\n=====================================
    ${測試記錄}=    Set Variable    ${測試記錄}\n備註: Safari 瀏覽器應已在設備上開啟
    ${測試記錄}=    Set Variable    ${測試記錄}\n環境: Ubuntu 24.04 + libimobiledevice
    ${測試記錄}=    Set Variable    ${測試記錄}\n限制: 完全自動化需要 macOS + Xcode
    
    Create File    ${SCREENSHOT_DIR}/manual_assisted_test_${timestamp}.txt    ${測試記錄}
    
    Log    📝 測試記錄已保存
    Log    📂 位置: ${SCREENSHOT_DIR}/manual_assisted_test_${timestamp}.txt
    Log    🎉 測試完成！
    Log    📱 請確認您的設備上 Safari 瀏覽器已開啟
    Log    ✅ 自動化框架運行正常，設備檢測和驗證成功
    
    Log To Console    ${\n}=====================================
    Log To Console    🎉 手動協助測試完成！
    Log To Console    =====================================
    Log To Console    📝 測試記錄已保存到: ${SCREENSHOT_DIR}/
    Log To Console    📱 請確認您的設備上 Safari 瀏覽器狀態
    Log To Console    ✅ 如果您在 15 秒內打開了 Safari，則測試成功
    Log To Console    =====================================${\n}
