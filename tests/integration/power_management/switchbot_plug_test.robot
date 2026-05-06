*** Settings ***
Documentation     SwitchBot 智慧插座測試案例
...
...              本測試案例驗證 SwitchBot 智慧插座控制功能，包括：
...              - 基本開關控制
...              - 狀態查詢
...              - 電源管理
...              - 設備重啟
...               
...               執行流程：
...               1. 先執行所有單次功能驗證 (確保環境 Pass)
...               2. 結束後自動進入每 10 分鐘一次的長效循環測試
...               
...               測試前置條件：
...               1. 已安裝 requests 套件
...               2. 已設定 SwitchBot API 認證資訊 (TOKEN & SECRET)
...               3. 已知測試用智慧插座設備 ID
...               4. 智慧插座處於在線狀態

Library           OperatingSystem    # 支援 Get Environment Variable
Library           Collections        # 支援 Get From Dictionary
Library           DateTime           # 用於計算與顯示下一次重啟時間
# 匯入自定義函式庫與資源
Library           ../../../libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py
Resource          ../../../resources/switchbot_keywords.robot
Resource          ../../../resources/common_keywords.robot

Test Setup        測試前置設定
Test Teardown     測試後置清理

*** Variables ***
# 測試配置變數 - 從環境變數讀取
${TEST_TOKEN}           %{TOKEN}
${TEST_SECRET}          %{SECRET}
${TEST_DEVICE_ID}       %{DEVICE_ID}
${TEST_TIMEOUT}         30s

# 測試狀態常數
${EXPECTED_ON}          on
${EXPECTED_OFF}         off

*** Test Cases ***
# =================================================================
# 第一部分：基礎功能驗證 (跑完這 8 個才會進循環)
# =================================================================

Scenario: User Needs To Turn On Smart Plug
    [Documentation]    Gherkin style test case for turning on smart plug
    ...                Gherkin 風格的智慧插座開啟測試案例
    [Tags]    smartplug    power    gherkin    basic

    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    Log To Console    [PASS] 設備已開啟。
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
    Log To Console    [PASS] 設備已關閉。
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
    Log To Console    [PASS] 設備狀態查詢成功。
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
    Log To Console    [PASS] 設備已重啟。
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
    Log To Console    [PASS] 設備已開啟。

    # 第二步：查詢狀態
    ${status} =    When 使用者查詢智慧插座狀態    ${TEST_DEVICE_ID}
    Then 狀態查詢應該成功回傳    ${status}
    Log To Console    [PASS] 設備狀態查詢成功：${status}。

    # 第三步：關閉插座
    When 使用者關閉智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於關閉狀態    ${TEST_DEVICE_ID}
    Log To Console    [PASS] 設備已關閉。

    # 第四步：再次開啟插座
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    Log To Console    [PASS] 設備已開啟。
    And 系統狀態應該保持穩定

# Legacy Test Cases (Traditional Style) - 向後相容
Basic Smart Plug On Test
    [Documentation]    Basic test for turning on smart plug (Traditional style)
    ...                智慧插座開啟基本測試 (傳統風格)
    [Tags]    legacy    basic
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    當開啟智慧插座    ${TEST_DEVICE_ID}
    那麼智慧插座狀態應該是開啟    ${TEST_DEVICE_ID}
    Log To Console    [PASS] 設備已開啟。

Basic Smart Plug Off Test
    [Documentation]    Basic test for turning off smart plug (Traditional style)
    ...                智慧插座關閉基本測試 (傳統風格)
    [Tags]    legacy    basic
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    當關閉智慧插座    ${TEST_DEVICE_ID}
    Sleep    5s
    那麼智慧插座狀態應該是關閉    ${TEST_DEVICE_ID}
    Log To Console    [PASS] 設備已關閉。

Basic Status Query Test
    [Documentation]    Basic test for querying smart plug status (Traditional style)
    ...                智慧插座狀態查詢基本測試 (傳統風格)
    [Tags]    legacy    query
    設定SwitchBot認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    ${status} =    取得智慧插座狀態    ${TEST_DEVICE_ID}
    Should Not Be Empty    ${status}
    Log To Console    [PASS] 設備狀態查詢成功: ${status}。

# =================================================================
# 第二部分：自動化無窮循環測試 (放在最後執行)
# =================================================================

Scenario: AUTOMATED LOOP - Continuous 10-Minute Power Cycle
    [Documentation]    前述測試全部 Pass 後，進入此循環。
    ...                每 10 分鐘關閉電源一次後重新開啟，確保最終狀態為 ON。
    [Tags]    automated_loop    stress_test
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    And 智慧插座系統已準備就緒

    WHILE    ${TRUE}
        ${now} =    Get Current Date
        ${current_time} =    Convert Date    ${now}    result_format=%H:%M:%S
        Log To Console    \n[${current_time}] >>> 啟動循環測試 (關閉 -> 等待5s -> 開啟)
        
        # 執行關閉
        When 使用者關閉智慧插座    ${TEST_DEVICE_ID}
        Then 智慧插座應該處於關閉狀態    ${TEST_DEVICE_ID}
        Log To Console    [PASS] 設備已關閉。
        
        Sleep    5s
        
        # 執行開啟 (最終狀態)
        When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
        Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
        Log To Console    [PASS] 設備已重新開啟。
        
        # 計算下次重啟時間
        ${next_time_raw} =    Add Time To Date    ${now}    600 seconds
        ${next_time} =    Convert Date    ${next_time_raw}    result_format=%H:%M:%S
        Log To Console    [INFO] 循環完成。下一次預計重啟時間: ${next_time}
        
        Sleep    600s
    END

*** Keywords ***
測試前置設定
    [Documentation]    測試案例執行前的設定工作
    Log    [SETUP] 開始執行智慧插座測試案例
    Should Not Be Empty    ${TEST_TOKEN}     msg=請設定環境變數 TOKEN
    Should Not Be Empty    ${TEST_SECRET}    msg=請設定環境變數 SECRET  
    Should Not Be Empty    ${TEST_DEVICE_ID} msg=請設定環境變數 DEVICE_ID
    # 此關鍵字來自 switchbot_keywords.robot
    設定測試環境變數    ${TEST_TOKEN}    ${TEST_SECRET}    ${TEST_DEVICE_ID}
    # 驗證設備是否連線
    驗證設備連線狀態    ${TEST_DEVICE_ID}
    Log    [SETUP] 測試前置設定完成，設備已就緒

測試後置清理
    [Documentation]    測試案例執行後的清理工作
    Log    [CLEANUP] 執行測試後置清理
    # 此關鍵字來自 switchbot_keywords.robot
    清理測試環境
    Log    [CLEANUP] 測試後置清理完成

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
            Log To Console    \n[INFO] 找到測試設備: ${device_name} (${device_id})
            BREAK
        END
    END

    Should Be True    ${device_found}    msg=測試設備 ${device_id} 未找到
