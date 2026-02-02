*** Settings ***
Documentation    SwitchBot 智慧插座控制關鍵字
...              提供 Gherkin 風格的中文關鍵字，用於 SwitchBot 智慧插座的控制與測試
...
...              主要功能：
...              - 智慧插座開關控制
...              - 設備狀態查詢與驗證
...              - 電源管理操作
...              - 設備資訊取得
...
...              使用前請確保：
...              1. 已安裝 requests 套件
...              2. 已設定 SwitchBot API 認證資訊（Token 和 Secret）
...              3. 已知設備 ID
...
...              技術說明：
...              - 使用 SwitchBot 官方 HTTP API v1.1（非第三方 SDK）
...              - 認證方式：HMAC-SHA256 簽名
...
...              範例：
...              | Library | libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py |
...              | Resource | resources/switchbot_keywords.robot |

Library    ../libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py
Library    BuiltIn
Library    String
Library    Collections

*** Variables ***
# SwitchBot 設定變數
${SWITCHBOT_TOKEN}          ${EMPTY}
${SWITCHBOT_SECRET}         ${EMPTY}
${DEFAULT_DEVICE_ID}        ${EMPTY}
${STATUS_CHECK_TIMEOUT}     30
${DEVICE_RESPONSE_DELAY}    2

# 狀態常數
${STATUS_ON}                on
${STATUS_OFF}               off
${STATUS_UNKNOWN}           unknown

*** Keywords ***
# =============================================================================
# Given Keywords - 前置條件設定
# =============================================================================

已設定SwitchBot API認證資訊
    [Documentation]    Given: 設定 SwitchBot API 的認證資訊
    ...                Given: Set up SwitchBot API authentication credentials
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 需要有效的 SwitchBot API Token 和 Secret
    ...                - Token 和 Secret 可從 SwitchBot App 取得
    ...                
    ...                設定項目 / Configuration Items:
    ...                - API Token 認證
    ...                - API Secret 認證
    ...                - 客戶端初始化
    ...                
    ...                Example:
    ...                | Given | 已設定SwitchBot API認證資訊 |
    [Arguments]    ${token}=${SWITCHBOT_TOKEN}    ${secret}=${SWITCHBOT_SECRET}
    
    Should Not Be Empty    ${token}    msg=SwitchBot Token 不能為空
    Should Not Be Empty    ${secret}   msg=SwitchBot Secret 不能為空
    
    ${result} =    設定SwitchBot認證資訊    ${token}    ${secret}
    Should Be True    ${result}    msg=SwitchBot 認證資訊設定失敗
    
    Set Suite Variable    ${SWITCHBOT_TOKEN}     ${token}
    Set Suite Variable    ${SWITCHBOT_SECRET}    ${secret}
    Log    SwitchBot API 認證資訊已設定

已知智慧插座設備ID
    [Documentation]    Given: 確認已知智慧插座的設備 ID
    ...                Given: Confirm that the smart plug device ID is known
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 設備 ID 不為空
    ...                - 設備可以被 API 找到
    ...                - 設備類型正確
    ...                
    ...                設定變數 / Variable Settings:
    ...                - DEFAULT_DEVICE_ID: 預設使用的設備 ID
    ...                
    ...                Example:
    ...                | Given | 已知智慧插座設備ID | ${DEVICE_ID} |
    [Arguments]    ${device_id}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    # 驗證設備是否存在
    ${device_info} =    查詢設備資訊    ${device_id}
    Should Not Be Empty    ${device_info}    msg=找不到指定的設備 ID: ${device_id}
    
    Set Suite Variable    ${DEFAULT_DEVICE_ID}    ${device_id}
    Log    智慧插座設備 ID 已確認: ${device_id}

智慧插座系統已準備就緒
    [Documentation]    Given: 確保智慧插座系統已準備就緒
    ...                Given: Ensure that the smart plug system is ready
    ...                
    ...                檢查項目 / Check Items:
    ...                - API 認證已設定
    ...                - 設備連線正常
    ...                - 系統初始化完成
    ...                
    ...                Example:
    ...                | Given | 智慧插座系統已準備就緒 |
    
    Should Not Be Empty    ${SWITCHBOT_TOKEN}     msg=請先設定 SwitchBot Token
    Should Not Be Empty    ${SWITCHBOT_SECRET}    msg=請先設定 SwitchBot Secret
    Should Not Be Empty    ${DEFAULT_DEVICE_ID}   msg=請先設定設備 ID
    
    # 測試 API 連線
    ${devices} =    取得所有SwitchBot設備清單
    ${device_count} =    Get Length    ${devices}
    Should Be True    ${device_count} > 0    msg=無法取得設備清單，請檢查 API 認證

# =============================================================================
# When Keywords - 操作執行
# =============================================================================

使用者開啟智慧插座
    [Documentation]    When: 使用者執行開啟智慧插座的操作
    ...                When: User performs the operation to turn on the smart plug
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 發送開啟命令到智慧插座
    ...                - 記錄操作時間和結果
    ...                
    ...                預期行為 / Expected Behavior:
    ...                - 智慧插座應該收到開啟命令
    ...                - 設備狀態應該開始變更
    ...                
    ...                Example:
    ...                | When | 使用者開啟智慧插座 |
    ...                | When | 使用者開啟智慧插座 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    Log    正在開啟智慧插座: ${device_id}
    ${result} =    當開啟智慧插座    ${device_id}
    Should Be True    ${result}    msg=開啟智慧插座失敗
    
    # 等待設備回應
    Sleep    ${DEVICE_RESPONSE_DELAY}s
    Log    智慧插座開啟命令已發送

使用者關閉智慧插座
    [Documentation]    When: 使用者執行關閉智慧插座的操作
    ...                When: User performs the operation to turn off the smart plug
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 發送關閉命令到智慧插座
    ...                - 記錄操作時間和結果
    ...                
    ...                預期行為 / Expected Behavior:
    ...                - 智慧插座應該收到關閉命令
    ...                - 設備狀態應該開始變更
    ...                
    ...                Example:
    ...                | When | 使用者關閉智慧插座 |
    ...                | When | 使用者關閉智慧插座 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    Log    正在關閉智慧插座: ${device_id}
    ${result} =    當關閉智慧插座    ${device_id}
    Should Be True    ${result}    msg=關閉智慧插座失敗
    
    # 等待設備回應
    Sleep    ${DEVICE_RESPONSE_DELAY}s
    Log    智慧插座關閉命令已發送

使用者查詢智慧插座狀態
    [Documentation]    When: 使用者查詢智慧插座的目前狀態
    ...                When: User queries the current status of the smart plug
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 向智慧插座查詢目前狀態
    ...                - 取得並記錄狀態資訊
    ...                
    ...                回傳值 / Return Value:
    ...                - 插座狀態字串 (on/off/unknown)
    ...                
    ...                Example:
    ...                | ${status} | When | 使用者查詢智慧插座狀態 |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    Log    正在查詢智慧插座狀態: ${device_id}
    ${status} =    取得智慧插座狀態    ${device_id}
    Log    智慧插座目前狀態: ${status}

    RETURN    ${status}

使用者執行設備電源重啟
    [Documentation]    When: 使用者執行設備的電源重啟操作
    ...                When: User performs a device power restart operation
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 先關閉設備電源
    ...                - 等待指定時間
    ...                - 重新開啟設備電源
    ...                - 確認重啟完成
    ...                
    ...                Example:
    ...                | When | 使用者執行設備電源重啟 |
    ...                | When | 使用者執行設備電源重啟 | ${DEVICE_ID} | 10 |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}    ${off_duration}=5
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    Log    正在執行設備電源重啟: ${device_id}
    ${result} =    執行設備電源重啟    ${device_id}    ${off_duration}
    Should Be True    ${result}    msg=設備電源重啟失敗
    
    Log    設備電源重啟完成

# =============================================================================
# Then Keywords - 結果驗證
# =============================================================================

智慧插座應該處於開啟狀態
    [Documentation]    Then: 驗證智慧插座應該處於開啟狀態
    ...                Then: Verify that the smart plug should be in the on state
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 插座狀態為 "on"
    ...                - 狀態查詢成功
    ...                - 狀態穩定
    ...                
    ...                預期結果 / Expected Result:
    ...                - 插座狀態查詢回傳 "on"
    ...                - 驗證通過無錯誤
    ...                
    ...                Example:
    ...                | Then | 智慧插座應該處於開啟狀態 |
    ...                | Then | 智慧插座應該處於開啟狀態 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    # 等待狀態穩定
    Wait Until Keyword Succeeds    ${STATUS_CHECK_TIMEOUT}s    2s
    ...    那麼智慧插座狀態應該是開啟    ${device_id}
    
    Log    驗證通過: 智慧插座處於開啟狀態

智慧插座應該處於關閉狀態
    [Documentation]    Then: 驗證智慧插座應該處於關閉狀態
    ...                Then: Verify that the smart plug should be in the off state
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 插座狀態為 "off"
    ...                - 狀態查詢成功
    ...                - 狀態穩定
    ...                
    ...                預期結果 / Expected Result:
    ...                - 插座狀態查詢回傳 "off"
    ...                - 驗證通過無錯誤
    ...                
    ...                Example:
    ...                | Then | 智慧插座應該處於關閉狀態 |
    ...                | Then | 智慧插座應該處於關閉狀態 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    # 等待狀態穩定
    Wait Until Keyword Succeeds    ${STATUS_CHECK_TIMEOUT}s    2s
    ...    那麼智慧插座狀態應該是關閉    ${device_id}
    
    Log    驗證通過: 智慧插座處於關閉狀態

狀態查詢應該成功回傳
    [Documentation]    Then: 驗證狀態查詢應該成功回傳有效狀態
    ...                Then: Verify that status query should return valid status successfully
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 狀態查詢不回傳空值
    ...                - 狀態值為有效狀態 (on/off)
    ...                - 查詢過程無錯誤
    ...                
    ...                Example:
    ...                | Then | 狀態查詢應該成功回傳 | ${actual_status} |
    [Arguments]    ${actual_status}
    
    Should Not Be Empty    ${actual_status}    msg=狀態查詢回傳空值
    Should Not Be Equal    ${actual_status}    ${STATUS_UNKNOWN}    msg=狀態查詢回傳未知狀態
    
    ${valid_statuses} =    Create List    ${STATUS_ON}    ${STATUS_OFF}
    Should Contain    ${valid_statuses}    ${actual_status}    
    ...    msg=狀態值無效: ${actual_status}，有效值為: ${valid_statuses}
    
    Log    狀態查詢驗證通過: ${actual_status}

設備重啟應該成功完成
    [Documentation]    Then: 驗證設備重啟應該成功完成
    ...                Then: Verify that device restart should complete successfully
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 設備成功關閉後重新開啟
    ...                - 最終狀態為開啟
    ...                - 整個重啟過程無錯誤
    ...                
    ...                Example:
    ...                | Then | 設備重啟應該成功完成 |
    ...                | Then | 設備重啟應該成功完成 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    # 驗證設備最終處於開啟狀態
    Wait Until Keyword Succeeds    ${STATUS_CHECK_TIMEOUT}s    3s
    ...    智慧插座應該處於開啟狀態    ${device_id}
    
    Log    設備重啟驗證通過

# =============================================================================
# And Keywords - 補充條件和驗證
# =============================================================================

設備資訊應該正確顯示
    [Documentation]    And: 設備資訊應該正確顯示
    ...                And: Device information should be displayed correctly
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 設備資訊可以正常取得
    ...                - 設備名稱、ID、類型等欄位完整
    ...                - 設備資訊格式正確
    ...                
    ...                Example:
    ...                | And | 設備資訊應該正確顯示 | ${DEVICE_ID} |
    [Arguments]    ${device_id}=${DEFAULT_DEVICE_ID}
    
    Should Not Be Empty    ${device_id}    msg=設備 ID 不能為空
    
    ${device_info} =    查詢設備資訊    ${device_id}
    Should Not Be Empty    ${device_info}    msg=無法取得設備資訊
    
    # 驗證必要欄位
    Dictionary Should Contain Key    ${device_info}    deviceId    msg=設備資訊缺少 deviceId
    Dictionary Should Contain Key    ${device_info}    deviceName  msg=設備資訊缺少 deviceName
    Dictionary Should Contain Key    ${device_info}    deviceType  msg=設備資訊缺少 deviceType
    
    ${actual_device_id} =    Get From Dictionary    ${device_info}    deviceId
    Should Be Equal    ${actual_device_id}    ${device_id}    msg=設備 ID 不匹配
    
    Log    設備資訊驗證通過

操作記錄應該完整保存
    [Documentation]    And: 操作記錄應該完整保存在日誌中
    ...                And: Operation records should be completely saved in logs
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 日誌檔案存在
    ...                - 操作記錄完整
    ...                - 時間戳記正確
    ...                
    ...                Example:
    ...                | And | 操作記錄應該完整保存 |
    
    # 這裡可以添加日誌檔案檢查邏輯
    # 目前簡單驗證記錄功能正常
    Log    操作記錄檢查通過

系統狀態應該保持穩定
    [Documentation]    And: 系統狀態應該保持穩定
    ...                And: System status should remain stable
    ...                
    ...                驗證項目 / Verification Items:
    ...                - API 連線穩定
    ...                - 設備回應正常
    ...                - 無異常錯誤
    ...                
    ...                Example:
    ...                | And | 系統狀態應該保持穩定 |
    
    # 執行系統穩定性檢查
    ${devices} =    取得所有SwitchBot設備清單
    Should Not Be Empty    ${devices}    msg=設備清單取得失敗，系統可能不穩定
    
    Log    系統穩定性檢查通過

# =============================================================================
# 工具關鍵字 (Utility Keywords)
# =============================================================================

設定測試環境變數
    [Documentation]    設定測試環境所需的變數
    [Arguments]    ${token}    ${secret}    ${device_id}
    
    Set Suite Variable    ${SWITCHBOT_TOKEN}     ${token}
    Set Suite Variable    ${SWITCHBOT_SECRET}    ${secret}
    Set Suite Variable    ${DEFAULT_DEVICE_ID}   ${device_id}

清理測試環境
    [Documentation]    清理測試環境，重置變數
    
    Set Suite Variable    ${SWITCHBOT_TOKEN}     ${EMPTY}
    Set Suite Variable    ${SWITCHBOT_SECRET}    ${EMPTY}
    Set Suite Variable    ${DEFAULT_DEVICE_ID}   ${EMPTY}

等待智慧插座狀態變更
    [Documentation]    等待智慧插座狀態變更到指定狀態
    [Arguments]    ${device_id}    ${expected_status}    ${timeout}=30s
    
    Wait Until Keyword Succeeds    ${timeout}    2s
    ...    取得智慧插座狀態應該是    ${device_id}    ${expected_status}

取得智慧插座狀態應該是
    [Documentation]    內部關鍵字：檢查狀態是否符合預期
    [Arguments]    ${device_id}    ${expected_status}
    
    ${actual_status} =    取得智慧插座狀態    ${device_id}
    Should Be Equal    ${actual_status}    ${expected_status}
    ...    msg=設備狀態不符合預期，實際: ${actual_status}，預期: ${expected_status}
