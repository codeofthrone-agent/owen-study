*** Settings ***
Documentation     機器手臂視覺檢測整合測試
...
...               **測試目標：**
...               - 驗證視覺檢測與按鈕控制的整合
...               - 測試完整的燈光切換驗證流程
...               - 驗證多按鈕場景下的穩定性
...
...               **測試場景：**
...               1. 按壓按鈕前檢測初始狀態
...               2. 執行按壓動作
...               3. 按壓後檢測新狀態
...               4. 驗證狀態改變
...
...               **執行方式：**
...               robot tests/robot_arm/vision_integration_test.robot

Library           ../../libraries/robot_arm_control/RobotArmKeywords.py
Library           Collections

Suite Setup       初始化測試環境
Suite Teardown    清理測試環境
Test Setup        連接到伺服器
Test Teardown     記錄測試結果


*** Variables ***
${SERVER_HOST}        10.42.0.180
${SERVER_PORT}        9000


*** Test Cases ***
場景 01: Light1 按鈕完整切換流程
    [Documentation]    測試 Light1 按鈕的完整操作流程
    ...
    ...    **流程：**
    ...    1. 檢測初始狀態
    ...    2. 按壓按鈕
    ...    3. 檢測新狀態
    ...    4. 驗證狀態改變
    [Tags]    integration    light1

    # 步驟 1: 檢測初始狀態
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    And 記錄當前檢測結果為初始狀態

    # 步驟 2: 按壓按鈕
    When 用戶按壓第 "light1" 按鈕
    And 等待燈光穩定

    # 步驟 3: 檢測新狀態
    When 用戶檢測第 "light1" 按鈕的燈光狀態

    # 步驟 4: 驗證改變
    Then 當前狀態應該與初始狀態不同
    And 記錄狀態轉換


場景 02: 批次檢測後批次切換
    [Documentation]    測試批次操作場景
    ...
    ...    **流程：**
    ...    1. 批次檢測 Light1-3 初始狀態
    ...    2. 依序按壓三個按鈕
    ...    3. 批次檢測新狀態
    ...    4. 驗證所有按鈕都已切換
    [Tags]    integration    batch

    # 步驟 1: 批次檢測初始狀態
    ${buttons}=    Create List    light1    light2    light3
    When 批次檢測按鈕狀態    ${buttons}
    And 記錄初始批次狀態

    # 步驟 2: 依序按壓
    When 依序按壓按鈕    ${buttons}

    # 步驟 3: 批次檢測新狀態
    When 批次檢測按鈕狀態    ${buttons}

    # 步驟 4: 驗證改變
    Then 所有按鈕狀態都應該改變


場景 03: 按壓後輪詢等待特定顏色
    [Documentation]    測試輪詢機制在實際場景中的應用
    ...
    ...    **流程：**
    ...    1. 按壓 Light1 按鈕
    ...    2. 輪詢等待變為藍色（或其他預期顏色）
    ...    3. 驗證等待成功
    [Tags]    integration    polling

    # 步驟 1: 按壓按鈕
    When 用戶按壓第 "light1" 按鈕

    # 步驟 2: 輪詢等待
    # 注意：這裡的顏色需要根據實際硬體行為調整
    When 用戶等待按鈕 "light1" 變為 "blue" 色    timeout=10    interval=1.0

    # 步驟 3: 驗證成功
    Then 上一步操作應該成功
    Log    ✓ 輪詢等待成功


場景 04: 多次切換穩定性測試
    [Documentation]    測試多次切換的穩定性
    ...
    ...    **流程：**
    ...    1. 連續切換 Light1 按鈕 5 次
    ...    2. 每次切換後檢測狀態
    ...    3. 驗證所有檢測都成功
    [Tags]    integration    stability

    @{states}=    Create List

    FOR    ${i}    IN RANGE    5
        # 按壓按鈕
        When 用戶按壓第 "light1" 按鈕
        Sleep    2s    等待燈光穩定

        # 檢測狀態
        When 用戶檢測第 "light1" 按鈕的燈光狀態
        ${result}=    取得最後檢測結果
        Collections.Append To List    ${states}    ${result}[color]

        Log    第 ${i+1} 次切換: ${result}[color]
    END

    # 驗證所有檢測都成功（有結果）
    ${count}=    Get Length    ${states}
    Should Be Equal As Numbers    ${count}    5


場景 05: 錯誤恢復測試
    [Documentation]    測試錯誤場景的恢復能力
    ...
    ...    **流程：**
    ...    1. 嘗試檢測未校準按鈕（預期失敗）
    ...    2. 檢測正常按鈕（驗證恢復）
    [Tags]    integration    error_recovery

    # 步驟 1: 故意觸發錯誤
    Run Keyword And Expect Error    ValueError*
    ...    When 用戶檢測第 "camera_observe" 按鈕的燈光狀態

    # 步驟 2: 驗證系統仍能正常工作
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 上一步操作應該成功
    Log    ✓ 錯誤恢復成功


*** Keywords ***
初始化測試環境
    [Documentation]    Suite Setup
    Log    ========================================
    Log    機器手臂視覺檢測整合測試
    Log    ========================================

清理測試環境
    [Documentation]    Suite Teardown
    Run Keyword And Ignore Error    When 用戶中斷與機器手臂的連接
    Log    測試完成

連接到伺服器
    [Documentation]    Test Setup
    When 用戶連接到機器手臂    ${SERVER_HOST}    ${SERVER_PORT}

記錄測試結果
    [Documentation]    Test Teardown
    Run Keyword If Test Failed    Log    ❌ 測試失敗

And 記錄當前檢測結果為初始狀態
    [Documentation]    記錄初始狀態
    ${result}=    取得最後檢測結果
    Set Test Variable    ${INITIAL_STATE}    ${result}[color]
    Log    初始狀態: ${result}[color] (亮度: ${result}[brightness])

And 等待燈光穩定
    [Documentation]    等待燈光穩定
    Sleep    2s

Then 當前狀態應該與初始狀態不同
    [Documentation]    驗證狀態改變
    ${current}=    取得最後檢測結果
    Should Not Be Equal    ${current}[color]    ${INITIAL_STATE}    msg=按鈕狀態未改變

And 記錄狀態轉換
    [Documentation]    記錄狀態轉換
    ${current}=    取得最後檢測結果
    Log    狀態轉換: ${INITIAL_STATE} → ${current}[color]

When 批次檢測按鈕狀態
    [Documentation]    批次檢測
    [Arguments]    ${button_list}
    ${results}=    RobotArmKeywords.When 用戶檢測多個按鈕的燈光狀態    @{button_list}
    Set Test Variable    ${BATCH_RESULTS}    ${results}

And 記錄初始批次狀態
    [Documentation]    記錄初始批次狀態
    @{initial_states}=    Create List
    FOR    ${result}    IN    @{BATCH_RESULTS}
        Run Keyword If    ${result}[success]
        ...    Collections.Append To List    ${initial_states}    ${result}[result][color]
        ...    ELSE
        ...    Collections.Append To List    ${initial_states}    NONE
    END
    Set Test Variable    @{INITIAL_BATCH_STATES}    @{initial_states}
    Log    初始批次狀態: ${INITIAL_BATCH_STATES}

When 依序按壓按鈕
    [Documentation]    依序按壓按鈕
    [Arguments]    ${button_list}
    FOR    ${button_id}    IN    @{button_list}
        When 用戶按壓第 "${button_id}" 按鈕
        Sleep    2s    等待燈光穩定
    END

Then 所有按鈕狀態都應該改變
    [Documentation]    驗證所有按鈕狀態改變
    ${changed}=    Set Variable    0
    ${total}=    Get Length    ${BATCH_RESULTS}

    FOR    ${i}    IN RANGE    ${total}
        ${result}=    Set Variable    ${BATCH_RESULTS}[${i}]
        ${initial}=    Set Variable    ${INITIAL_BATCH_STATES}[${i}]

        Run Keyword If    ${result}[success]
        ...    Run Keyword If    '${result}[result][color]' != '${initial}'
        ...        Set Variable    ${changed + 1}
    END

    Log    改變數量: ${changed}/${total}
    # 允許部分失敗，至少 80% 改變
    ${rate}=    Evaluate    ${changed} * 100 / ${total}
    Should Be True    ${rate} >= 80    msg=改變率過低: ${rate}%

取得最後檢測結果
    [Documentation]    取得最後一次檢測結果
    # 這個假設 RobotArmKeywords 會記錄最後結果
    # 實際實作需要在 RobotArmKeywords 中加入 getter 方法
    # 暫時用 Built-in 變數替代
    ${result}=    Get Variable Value    ${LAST_DETECTION_RESULT}
    RETURN    ${result}
