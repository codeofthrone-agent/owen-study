*** Settings ***
Documentation    SwitchBot 智慧插座測試案例
...
...              本測試案例驗證 SwitchBot 智慧插座控制功能，包括：
...              - 基本開關控制
...              - 狀態查詢
...              - 電源管理
...              - 設備重啟
...
...              測試前置條件：
...              1. 已安裝 requests 套件
...              2. 已設定 SwitchBot API 認證資訊（Token 和 Secret）
...              3. 已知測試用智慧插座設備 ID
...              4. 智慧插座處於在線狀態
...
...              技術說明：
...              - 使用 SwitchBot 官方 HTTP API v1.1（非第三方 SDK）
...              - 認證方式：HMAC-SHA256 簽名

Library    ../../libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py
Resource   ../../resources/switchbot_keywords.robot
Resource   ../../resources/common_keywords.robot

Test Setup       測試前置設定
Test Teardown    測試後置清理

*** Variables ***
# 測試配置變數 - 從環境變數讀取，請在 .env 檔案中設定
# SWITCHBOT_TOKEN, SWITCHBOT_SECRET, SWITCHBOT_DEVICE_ID
${TEST_TOKEN}           %{TOKEN=}
${TEST_SECRET}          %{SECRET=}
${TEST_DEVICE_ID}       %{DEVICE_ID=}
${TEST_TIMEOUT}         30s

# 測試狀態常數
${EXPECTED_ON}          on
${EXPECTED_OFF}         off

*** Test Cases ***
Scenario: User Needs To Turn On Smart Plug
    [Documentation]    Gherkin style test case for turning on smart plug
    ...                Gherkin 風格的智慧插座開啟測試案例
    [Tags]    smartplug    power    gherkin    basic
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    And 設備資訊應該正確顯示    ${TEST_DEVICE_ID}
    And 操作記錄應該完整保存

Scenario: User Needs To Turn Off Smart Plug  
    [Documentation]    Gherkin style test case for turning off smart plug
    ...                Gherkin 風格的智慧插座關閉測試案例
    [Tags]    smartplug    power    gherkin    basic
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    When 使用者關閉智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於關閉狀態    ${TEST_DEVICE_ID}
    And 設備資訊應該正確顯示    ${TEST_DEVICE_ID}
    And 操作記錄應該完整保存

Scenario: User Needs To Query Smart Plug Status
    [Documentation]    Gherkin style test case for querying smart plug status
    ...                Gherkin 風格的智慧插座狀態查詢測試案例
    [Tags]    smartplug    status    gherkin    query
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    ${status} =    When 使用者查詢智慧插座狀態    ${TEST_DEVICE_ID}
    Then 狀態查詢應該成功回傳    ${status}
    And 設備資訊應該正確顯示    ${TEST_DEVICE_ID}
    And 系統狀態應該保持穩定

Scenario: User Needs To Restart Smart Plug Power
    [Documentation]    Gherkin style test case for restarting smart plug power
    ...                Gherkin 風格的智慧插座電源重啟測試案例
    [Tags]    smartplug    restart    gherkin    power
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    When 使用者執行設備電源重啟    ${TEST_DEVICE_ID}    5
    Then 設備重啟應該成功完成    ${TEST_DEVICE_ID}
    And 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    And 系統狀態應該保持穩定

Scenario: User Needs To Control Multiple Operations In Sequence
    [Documentation]    Gherkin style test case for sequential operations
    ...                Gherkin 風格的智慧插座序列操作測試案例
    [Tags]    smartplug    sequence    gherkin    comprehensive
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    
    # 第一步：開啟插座
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    
    # 第二步：查詢狀態
    ${status} =    When 使用者查詢智慧插座狀態    ${TEST_DEVICE_ID}
    Then 狀態查詢應該成功回傳    ${status}
    
    # 第三步：關閉插座
    When 使用者關閉智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於關閉狀態    ${TEST_DEVICE_ID}
    
    # 第四步：重新開啟
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    And 系統狀態應該保持穩定

# Legacy Test Cases (Traditional Style) - 向後相容
Basic Smart Plug On Test
    [Documentation]    Basic test for turning on smart plug (Traditional style)
    ...                智慧插座開啟基本測試 (傳統風格)
    [Tags]    legacy    basic
    
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    當開啟智慧插座    ${TEST_DEVICE_ID}
    那麼智慧插座狀態應該是開啟    ${TEST_DEVICE_ID}
    Log    Legacy test completed successfully

Basic Smart Plug Off Test
    [Documentation]    Basic test for turning off smart plug (Traditional style)
    ...                智慧插座關閉基本測試 (傳統風格)
    [Tags]    legacy    basic
    
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    當關閉智慧插座    ${TEST_DEVICE_ID}
    那麼智慧插座狀態應該是關閉    ${TEST_DEVICE_ID}
    Log    Legacy test completed successfully

Basic Status Query Test
    [Documentation]    Basic test for querying smart plug status (Traditional style)
    ...                智慧插座狀態查詢基本測試 (傳統風格)
    [Tags]    legacy    query
    
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    ${status} =    取得智慧插座狀態    ${TEST_DEVICE_ID}
    Should Not Be Empty    ${status}
    Log    Current status: ${status}
    Log    Legacy test completed successfully

*** Keywords ***
測試前置設定
    [Documentation]    測試案例執行前的設定工作
    ...
    ...                環境變數設定方式：
    ...                1. 在專案根目錄的 .env 檔案中設定：
    ...                   SWITCHBOT_TOKEN=your_token
    ...                   SWITCHBOT_SECRET=your_secret
    ...                   SWITCHBOT_DEVICE_ID=your_device_id
    ...                2. 或直接設定系統環境變數

    Log    開始執行智慧插座測試案例

    # 檢查測試配置（從環境變數讀取）
    Should Not Be Empty    ${TEST_TOKEN}
    ...    msg=請設定環境變數 SWITCHBOT_TOKEN（可在 .env 檔案中設定）
    Should Not Be Empty    ${TEST_SECRET}
    ...    msg=請設定環境變數 SWITCHBOT_SECRET（可在 .env 檔案中設定）
    Should Not Be Empty    ${TEST_DEVICE_ID}
    ...    msg=請設定環境變數 SWITCHBOT_DEVICE_ID（可在 .env 檔案中設定）

    # 設定測試環境
    設定測試環境變數    ${TEST_TOKEN}    ${TEST_SECRET}    ${TEST_DEVICE_ID}

    Log    測試前置設定完成（使用環境變數: SWITCHBOT_TOKEN, SWITCHBOT_SECRET, SWITCHBOT_DEVICE_ID）

測試後置清理
    [Documentation]    測試案例執行後的清理工作

    Log    執行測試後置清理

    # 清理測試環境變數
    清理測試環境

    Log    測試後置清理完成

驗證設備連線狀態
    [Documentation]    驗證設備是否處於可用狀態
    [Arguments]    ${device_id}

    ${devices} =    取得所有SwitchBot設備清單
    ${device_found} =    Set Variable    False

    FOR    ${device}    IN    @{devices}
        ${current_id} =    Get From Dictionary    ${device}    deviceId
        IF    '${current_id}' == '${device_id}'
            ${device_found} =    Set Variable    True
            ${device_name} =    Get From Dictionary    ${device}    deviceName
            Log    找到測試設備: ${device_name} (${device_id})
            BREAK
        END
    END

    Should Be True    ${device_found}    msg=測試設備 ${device_id} 未找到
