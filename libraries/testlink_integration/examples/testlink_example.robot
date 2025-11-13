*** Settings ***
Documentation     TestLink 整合使用範例
...
...               這個檔案展示了如何使用 TestLink 整合模組的各種功能。
...
...               執行前準備：
...               1. 確保 TestLink 服務正在運行
...               2. 在 .env 檔案中配置 TESTLINK_API_URL 和 TESTLINK_API_KEY
...               3. 確保 TestLink 中存在對應的專案、測試計畫、測試案例
...
...               執行方式：
...               | robot libraries/testlink_integration/examples/testlink_example.robot
...
...               作者: Robot Framework Automation Team
...               日期: 2025-11-10

Library           libraries.testlink_integration.TestLinkConnector
Resource          resources/testlink_keywords.robot


*** Variables ***
${TEST_CASE_1}       TEST-001    # 替換為你的測試案例 ID
${TEST_CASE_2}       TEST-002
${TEST_CASE_3}       TEST-003


*** Test Cases ***
範例 1: 基本連接與回報
    [Documentation]    示範最基本的 TestLink 連接與測試結果回報
    [Tags]    example    basic    testlink

    # 前置條件：連接到 TestLink
    Given TestLink 服務已連接

    # 執行動作：回報測試結果
    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "PASS"

    # 結果驗證
    Then TestLink 應該記錄測試結果

範例 2: 回報失敗結果並附註
    [Documentation]    示範如何回報失敗的測試並附加詳細說明
    [Tags]    example    failure    testlink

    Given TestLink 服務已連接

    When 回報測試案例 "${TEST_CASE_2}" 的執行結果為 "FAIL" 並附註 "斷言失敗：預期值為 200，實際值為 404"

    Then TestLink 應該記錄測試結果

範例 3: 完整的 Gherkin 風格測試
    [Documentation]    展示完整的 Gherkin 語法（Given-When-Then-And）
    [Tags]    example    gherkin    testlink

    # Given - 前置條件
    Given TestLink 服務已連接
    And TestLink 連接狀態為正常
    And 記錄當前 TestLink 專案資訊

    # When - 執行動作
    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "PASS"

    # Then - 結果驗證
    Then TestLink 應該記錄測試結果
    And 測試案例 "${TEST_CASE_1}" 應該存在於 TestLink

範例 4: 查詢測試案例資訊
    [Documentation]    示範如何查詢測試案例資訊
    [Tags]    example    query    testlink

    Given TestLink 服務已連接

    # 查詢測試案例資訊
    ${info}=    When 查詢測試案例 "${TEST_CASE_1}" 的資訊

    # 記錄測試案例資訊
    Log    測試案例名稱: ${info['name']}
    Log    測試案例 ID: ${info['testcase_id']}
    Log    測試案例版本: ${info.get('version', '未知')}

    # 驗證測試案例存在
    Then 測試案例 "${TEST_CASE_1}" 應該存在於 TestLink

範例 5: 批次回報測試結果
    [Documentation]    示範如何批次回報多個測試結果
    [Tags]    example    batch    testlink

    Given TestLink 服務已連接

    # 建立測試結果列表
    ${results}=    建立測試結果列表

    # 添加多個測試結果
    ${results}=    添加測試結果    ${results}    ${TEST_CASE_1}    PASS
    ${results}=    添加測試結果    ${results}    ${TEST_CASE_2}    FAIL    notes=測試失敗：連接超時
    ${results}=    添加測試結果    ${results}    ${TEST_CASE_3}    PASS    duration=2.5

    # 批次回報
    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}

    # 驗證結果
    Log    成功回報: ${stats['success']} 個
    Log    失敗回報: ${stats['failed']} 個
    Then 批次回報應該全部成功    ${stats}

範例 6: 使用 Python 語法建立結果列表
    [Documentation]    示範使用 Python 語法建立測試結果列表
    [Tags]    example    batch    python    testlink

    Given TestLink 服務已連接

    # 使用 Python Evaluate 建立結果列表
    ${results}=    Evaluate    [
    ...    {'test_case_id': '${TEST_CASE_1}', 'status': 'PASS'},
    ...    {'test_case_id': '${TEST_CASE_2}', 'status': 'FAIL', 'notes': '預期值不符'},
    ...    {'test_case_id': '${TEST_CASE_3}', 'status': 'PASS', 'duration': 1.5}
    ...    ]

    # 批次回報
    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}

    Log    批次回報統計: ${stats}

範例 7: 連接到不同專案
    [Documentation]    示範如何連接到不同的 TestLink 專案
    [Tags]    example    project    testlink

    # 連接到特定專案
    Given TestLink 服務已連接到專案 "Robot Automation Project"

    # 記錄專案資訊
    And 記錄當前 TestLink 專案資訊

    # 回報測試結果
    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "PASS"

    Then TestLink 應該記錄測試結果

範例 8: 錯誤處理示範
    [Documentation]    示範錯誤處理機制
    [Tags]    example    error_handling    testlink

    Given TestLink 服務已連接

    # 嘗試回報不存在的測試案例（預期會失敗）
    Run Keyword And Expect Error
    ...    *找不到測試案例*
    ...    回報測試結果到 TestLink    INVALID-999    PASS

    Log    ✅ 錯誤處理正常：無效的測試案例 ID 被正確攔截

範例 9: 驗證執行結果
    [Documentation]    示範如何驗證測試案例的執行結果
    [Tags]    example    verification    testlink

    Given TestLink 服務已連接

    # 先回報一個測試結果
    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "PASS"

    # 取得最後執行結果
    ${result}=    取得最後執行結果    ${TEST_CASE_1}

    # 驗證執行狀態（p = passed）
    Then 測試案例 "${TEST_CASE_1}" 的最後執行狀態應為 "p"

    # 記錄執行結果詳細資訊
    Log    執行狀態: ${result['status']}
    Log    執行時間: ${result.get('execution_ts', '未知')}

範例 10: 整合到實際測試流程
    [Documentation]    示範如何將 TestLink 整合到實際的測試流程中
    [Tags]    example    integration    testlink

    # 前置條件
    Given TestLink 服務已連接

    # 執行實際的測試邏輯（這裡用簡單的範例代替）
    ${test_status}=    執行實際測試邏輯

    # 根據測試結果回報到 TestLink
    Run Keyword If    '${test_status}' == 'PASS'
    ...    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "PASS" 並附註 "所有斷言通過"
    ...    ELSE
    ...    When 回報測試案例 "${TEST_CASE_1}" 的執行結果為 "FAIL" 並附註 "測試失敗：${test_status}"

    Then TestLink 應該記錄測試結果


*** Keywords ***
執行實際測試邏輯
    [Documentation]    模擬實際的測試邏輯
    ...
    ...    在真實場景中，這裡會是你的測試步驟，例如：
    ...    - 開啟應用程式
    ...    - 執行操作
    ...    - 驗證結果
    ...
    ...    這裡為了示範，直接回傳 PASS

    # 模擬測試邏輯
    Log    執行測試步驟 1: 初始化測試環境
    Sleep    0.5s
    Log    執行測試步驟 2: 執行測試操作
    Sleep    0.5s
    Log    執行測試步驟 3: 驗證測試結果
    Sleep    0.5s

    # 回傳測試結果
    RETURN    PASS
