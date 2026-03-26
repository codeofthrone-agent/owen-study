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

Library           ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library           Collections

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
    ${initial_result}=    取得最後檢測結果
    ${initial_color}=    Set Variable    ${initial_result}[color]
    Log    初始狀態: ${initial_color}

    # 步驟 2: 按壓按鈕
    When 用戶按壓第 "light1" 按鈕
    Sleep    2s    # 等待燈光穩定

    # 步驟 3: 檢測新狀態
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    ${current_result}=    取得最後檢測結果
    ${current_color}=    Set Variable    ${current_result}[color]

    # 步驟 4: 驗證改變
    Should Not Be Equal    ${current_color}    ${initial_color}    msg=按鈕狀態未改變
    Log    狀態轉換: ${initial_color} → ${current_color}


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
    When 用戶檢測多個按鈕的燈光狀態    ${buttons}
    ${initial_results}=    取得批次檢測結果

    # 步驟 2: 依序按壓
    FOR    ${button_id}    IN    @{buttons}
        When 用戶按壓第 "${button_id}" 按鈕
        Sleep    2s    等待燈光穩定
    END

    # 步驟 3: 批次檢測新狀態
    When 用戶檢測多個按鈕的燈光狀態    ${buttons}
    ${final_results}=    取得批次檢測結果

    # 步驟 4: 驗證改變
    ${changed_count}=    Set Variable    0
    ${total}=    Get Length    ${buttons}
    FOR    ${i}    IN RANGE    ${total}
        ${initial_color}=    Set Variable    ${initial_results}[${i}][result][color]
        ${final_color}=    Set Variable    ${final_results}[${i}][result][color]
        ${changed_count}=    Set Variable If    '${initial_color}' != '${final_color}'    ${changed_count + 1}    ${changed_count}
    END
    ${success_rate}=    Evaluate    ${changed_count} * 100 / ${total}
    Should Be True    ${success_rate} >= 80    msg=切換成功率過低: ${success_rate}%
    Log    批次切換成功率: ${success_rate}% (${changed_count}/${total})


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
    Log    ✓ 輪詢等待成功


場景 04: 多次切換穩定性測試
    [Documentation]    測試多次切換的穩定性
    ...
    ...    **流程：**
    ...    1. 連續切換 Light1 按鈕 5 次
    ...    2. 每次切換後檢測狀態
    ...    3. 驗證所有檢測都成功
    [Tags]    integration    stability

    ${success_count}=    Set Variable    0

    FOR    ${i}    IN RANGE    5
        # 按壓按鈕
        When 用戶按壓第 "light1" 按鈕
        Sleep    2s    等待燈光穩定

        # 檢測狀態
        ${status}=    Run Keyword And Return Status    When 用戶檢測第 "light1" 按鈕的燈光狀態
        ${success_count}=    Set Variable If    ${status}    ${success_count + 1}    ${success_count}

        Run Keyword If    ${status}
        ...    Log    第 ${i+1} 次切換成功
        ...    ELSE
        ...    Log    第 ${i+1} 次切換失敗
    END

    # 驗證至少 80% 檢測成功
    ${success_rate}=    Evaluate    ${success_count} * 100 / 5
    Should Be True    ${success_rate} >= 80    msg=成功率過低: ${success_rate}%
    Log    穩定性測試結果: ${success_count}/5 成功 (${success_rate}%)


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
連接到伺服器
    [Documentation]    Test Setup
    When 用戶連接到機器手臂    ${SERVER_HOST}    ${SERVER_PORT}

記錄測試結果
    [Documentation]    Test Teardown
    Run Keyword If Test Failed    Log    ❌ 測試失敗

取得最後檢測結果
    [Documentation]    使用庫文件的檢測結果獲取方法
    ${result}=    取得最後檢測結果
    RETURN    ${result}
