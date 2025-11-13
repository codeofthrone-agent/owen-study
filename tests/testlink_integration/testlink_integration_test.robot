*** Settings ***
Documentation     TestLink 整合模組測試
...
...               這個測試套件驗證 TestLink 整合模組的核心功能。
...
...               測試範圍：
...               - TestLink 連接與初始化
...               - 測試結果回報（單一/批次）
...               - 測試案例查詢
...               - 錯誤處理
...
...               前置需求：
...               1. TestLink 服務正在運行
...               2. .env 檔案中已配置 TestLink 連接資訊
...               3. TestLink 中存在測試專案和測試計畫
...
...               執行方式：
...               | robot tests/testlink_integration/testlink_integration_test.robot
...
...               執行特定測試：
...               | robot --test "測試 TestLink 基本連接" tests/testlink_integration/
...
...               作者: Robot Framework Automation Team
...               日期: 2025-11-10

Library           libraries.testlink_integration.TestLinkConnector
Resource          resources/testlink_keywords.robot

Suite Setup       Setup TestLink Integration Test Suite
Suite Teardown    Teardown TestLink Integration Test Suite


*** Variables ***
# 測試用測試案例 ID（請根據你的 TestLink 環境調整）
${VALID_TEST_CASE}       CCU-123
${INVALID_TEST_CASE}     INVALID-999


*** Test Cases ***
測試 TestLink 基本連接
    [Documentation]    測試基本的 TestLink 連接功能
    ...
    ...    驗證項目：
    ...    - 能成功連接到 TestLink
    ...    - 能取得專案資訊
    ...    - 連接狀態檢查正常
    [Tags]    testlink    connection    smoke

    Given TestLink 服務已連接
    And 驗證 TestLink 連接正常
    And 記錄當前 TestLink 專案資訊

    ${info}=    取得當前專案資訊
    Should Not Be Empty    ${info['project_name']}    訊息=專案名稱不應為空
    Should Not Be Empty    ${info['test_plan_name']}    訊息=測試計畫名稱不應為空

測試回報 PASS 結果
    [Documentation]    測試回報 PASS 測試結果
    [Tags]    testlink    report    pass

    Given TestLink 服務已連接

    When 回報測試案例 "${VALID_TEST_CASE}" 的執行結果為 "PASS"

    Then TestLink 應該記錄測試結果
    And 測試案例 "${VALID_TEST_CASE}" 的最後執行狀態應為 "p"

測試回報 FAIL 結果
    [Documentation]    測試回報 FAIL 測試結果
    [Tags]    testlink    report    fail

    Given TestLink 服務已連接

    When 回報測試案例 "${VALID_TEST_CASE}" 的執行結果為 "FAIL" 並附註 "測試失敗：整合測試驗證"

    Then TestLink 應該記錄測試結果
    And 測試案例 "${VALID_TEST_CASE}" 的最後執行狀態應為 "f"

測試回報 BLOCKED 結果
    [Documentation]    測試回報 BLOCKED 測試結果
    [Tags]    testlink    report    blocked

    Given TestLink 服務已連接

    When 回報測試案例 "${VALID_TEST_CASE}" 的執行結果為 "BLOCKED" 並附註 "測試阻塞：環境問題"

    Then TestLink 應該記錄測試結果
    And 測試案例 "${VALID_TEST_CASE}" 的最後執行狀態應為 "b"

測試查詢測試案例資訊
    [Documentation]    測試查詢測試案例資訊功能
    [Tags]    testlink    query

    Given TestLink 服務已連接

    ${info}=    When 查詢測試案例 "${VALID_TEST_CASE}" 的資訊

    # 驗證回傳資訊
    Should Not Be Empty    ${info}    訊息=測試案例資訊不應為空
    Should Not Be Empty    ${info['testcase_id']}    訊息=測試案例 ID 不應為空
    Should Not Be Empty    ${info['name']}    訊息=測試案例名稱不應為空

    Log    測試案例資訊: ${info}

測試批次回報功能
    [Documentation]    測試批次回報多個測試結果
    [Tags]    testlink    batch

    Given TestLink 服務已連接

    # 建立測試結果列表
    ${results}=    建立測試結果列表
    ${results}=    添加測試結果    ${results}    ${VALID_TEST_CASE}    PASS    notes=批次測試 1
    ${results}=    添加測試結果    ${results}    ${VALID_TEST_CASE}    FAIL    notes=批次測試 2
    ${results}=    添加測試結果    ${results}    ${VALID_TEST_CASE}    PASS    notes=批次測試 3    duration=1.5

    # 批次回報
    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}

    # 驗證統計
    Should Be Equal As Integers    ${stats['success']}    3    訊息=應該成功回報 3 個結果
    Should Be Equal As Integers    ${stats['failed']}    0    訊息=不應該有失敗的回報

測試錯誤處理_無效測試案例
    [Documentation]    測試無效測試案例的錯誤處理
    [Tags]    testlink    error_handling    negative

    Given TestLink 服務已連接

    # 嘗試回報不存在的測試案例
    Run Keyword And Expect Error
    ...    *找不到測試案例*
    ...    回報測試結果到 TestLink    ${INVALID_TEST_CASE}    PASS

    Log    ✅ 錯誤處理正常：無效測試案例被正確攔截

測試錯誤處理_無效狀態
    [Documentation]    測試無效測試狀態的錯誤處理
    [Tags]    testlink    error_handling    negative

    Given TestLink 服務已連接

    # 嘗試使用無效的測試狀態
    Run Keyword And Expect Error
    ...    *無效的測試狀態*
    ...    回報測試結果到 TestLink    ${VALID_TEST_CASE}    INVALID_STATUS

    Log    ✅ 錯誤處理正常：無效狀態被正確攔截

測試連接狀態檢查
    [Documentation]    測試 TestLink 連接狀態檢查功能
    [Tags]    testlink    connection    health

    Given TestLink 服務已連接

    ${status}=    檢查 TestLink 連接狀態
    Should Be True    ${status}    訊息=TestLink 連接應該正常

    And 驗證 TestLink 連接正常

測試 Gherkin 完整流程
    [Documentation]    測試完整的 Gherkin 語法流程
    ...
    ...    這個測試案例示範標準的 Gherkin 語法：
    ...    Given（前置條件）-> When（執行動作）-> Then（結果驗證）-> And（附加條件）
    [Tags]    testlink    gherkin    integration

    # Given - 前置條件
    Given TestLink 服務已連接
    And 驗證 TestLink 連接正常

    # When - 執行動作
    When 回報測試案例 "${VALID_TEST_CASE}" 的執行結果為 "PASS" 並附註 "Gherkin 完整流程測試"

    # Then - 結果驗證
    Then TestLink 應該記錄測試結果
    And 測試案例 "${VALID_TEST_CASE}" 應該存在於 TestLink
    And 測試案例 "${VALID_TEST_CASE}" 的最後執行狀態應為 "p"


*** Keywords ***
Setup TestLink Integration Test Suite
    [Documentation]    測試套件前置設定
    Log    開始執行 TestLink 整合測試套件
    Log    請確保 TestLink 服務正在運行且已正確配置

Teardown TestLink Integration Test Suite
    [Documentation]    測試套件清理
    Log    TestLink 整合測試套件執行完成
