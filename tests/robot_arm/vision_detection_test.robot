*** Settings ***
Documentation     機器手臂視覺檢測測試 - Phase 3
...
...               **測試目標：**
...               - 驗證視覺檢測關鍵字功能
...               - 測試單一按鈕 LED 狀態檢測
...               - 測試批次按鈕檢測
...               - 測試燈光切換驗證
...               - 測試輪詢等待機制
...
...               **前置條件：**
...               - Jetson Nano 上的 robot_arm_server.py 已啟動
...               - 所有按鈕已完成 ROI 校準（calibrate_button_roi.py）
...               - 機器手臂已上電並就緒
...               - 攝影機連接正常（/dev/video0）
...
...               **測試環境：**
...               - Server IP: 10.42.0.180
...               - Server Port: 9000
...               - Config: config/robot_arm/button_positions.yaml
...
...               **版本資訊：**
...               - RobotArmKeywords: v3.0.0
...               - 建立日期: 2025-11-13

Library           ../../libraries/robot_arm_control/RobotArmKeywords.py
Library           BuiltIn
Library           Collections
Resource          ../../resources/common_keywords.robot

Suite Setup       Given 機器手臂系統已準備就緒
Suite Teardown    And 機器手臂已安全斷開連接
Test Setup        Given 機器手臂已連接到遠端伺服器
Test Teardown     Run Keyword If Test Failed    記錄失敗原因


*** Variables ***
${SERVER_HOST}        10.42.0.180
${SERVER_PORT}        9000
${CONFIG_FILE}        config/robot_arm/button_positions.yaml


*** Test Cases ***
測試案例 01: 檢測單一按鈕的燈光狀態（Light1）
    [Documentation]    測試基本的視覺檢測功能
    ...
    ...    **測試步驟：**
    ...    1. 連接到機器手臂伺服器
    ...    2. 檢測 Light1 按鈕的燈光狀態
    ...    3. 記錄檢測結果（顏色、亮度、信心度）
    ...
    ...    **預期結果：**
    ...    - 檢測成功，返回燈光狀態
    ...    - 結果包含顏色資訊（blue/white/off）
    [Tags]    vision    single    light1

    Given 機器手臂已連接到遠端伺服器
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 檢測應該成功完成
    And 記錄檢測結果


測試案例 02: 驗證按鈕燈光顏色為藍色
    [Documentation]    測試顏色驗證功能（假設 Light1 為藍色）
    ...
    ...    **測試步驟：**
    ...    1. 檢測 Light1 按鈕狀態
    ...    2. 驗證燈光顏色為藍色
    ...
    ...    **預期結果：**
    ...    - 如果實際為藍色，驗證通過
    ...    - 如果不是藍色，測試失敗並顯示實際顏色
    ...
    ...    **注意：** 此測試案例依賴實際硬體狀態
    [Tags]    vision    verification    blue

    Given 機器手臂已連接到遠端伺服器
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 按鈕燈光應該為 "blue" 色


測試案例 03: 驗證按鈕燈光狀態為關閉
    [Documentation]    測試狀態驗證功能（假設 Light2 為關閉）
    ...
    ...    **測試步驟：**
    ...    1. 檢測 Light2 按鈕狀態
    ...    2. 驗證燈光狀態為關閉（off）
    ...
    ...    **預期結果：**
    ...    - 如果實際為關閉，驗證通過
    ...    - 如果是開啟，測試失敗
    ...
    ...    **注意：** 此測試案例依賴實際硬體狀態
    [Tags]    vision    verification    off

    Given 機器手臂已連接到遠端伺服器
    When 用戶檢測第 "light2" 按鈕的燈光狀態
    Then 按鈕燈光應該為 "off" 狀態


測試案例 04: 批次檢測多個按鈕的燈光狀態
    [Documentation]    測試批次檢測功能
    ...
    ...    **測試步驟：**
    ...    1. 準備檢測按鈕清單（Light1, Light2, Light3）
    ...    2. 執行批次檢測
    ...    3. 驗證所有按鈕都成功檢測
    ...
    ...    **預期結果：**
    ...    - 所有按鈕都成功檢測
    ...    - 返回每個按鈕的檢測結果
    [Tags]    vision    batch    multiple

    Given 機器手臂已連接到遠端伺服器
    And 準備檢測按鈕清單    light1    light2    light3
    When 用戶檢測多個按鈕的燈光狀態
    Then 所有按鈕檢測應該成功
    And 記錄批次檢測結果


測試案例 05: 檢測所有燈光按鈕（Light1-8）
    [Documentation]    測試大規模批次檢測（8 個燈光按鈕）
    ...
    ...    **測試步驟：**
    ...    1. 準備 8 個燈光按鈕清單
    ...    2. 執行批次檢測
    ...    3. 統計成功率
    ...
    ...    **預期結果：**
    ...    - 成功率 >= 80%（允許部分失敗）
    [Tags]    vision    batch    comprehensive

    Given 機器手臂已連接到遠端伺服器
    And 準備檢測按鈕清單    light1    light2    light3    light4    light5    light6    light7    light8
    When 用戶檢測多個按鈕的燈光狀態
    Then 批次檢測成功率應該大於    80


測試案例 06: 按壓按鈕後驗證燈光切換（Light1）
    [Documentation]    測試燈光切換驗證流程
    ...
    ...    **測試步驟：**
    ...    1. 檢測 Light1 初始狀態
    ...    2. 按壓 Light1 按鈕
    ...    3. 再次檢測狀態
    ...    4. 驗證狀態已改變
    ...
    ...    **預期結果：**
    ...    - 按壓後燈光狀態改變
    ...    - 兩次檢測結果不同
    [Tags]    vision    integration    toggle

    Given 機器手臂已連接到遠端伺服器
    And 記錄按鈕 "light1" 的初始狀態
    When 用戶按壓第 "light1" 按鈕
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 按鈕狀態應該與初始狀態不同


測試案例 07: 等待按鈕變為藍色（輪詢檢測）
    [Documentation]    測試輪詢等待機制
    ...
    ...    **測試步驟：**
    ...    1. 按壓 Light1 按鈕（假設會變為藍色）
    ...    2. 使用輪詢機制等待按鈕變為藍色
    ...    3. 驗證等待成功
    ...
    ...    **預期結果：**
    ...    - 在超時時間內檢測到藍色
    ...    - 返回成功
    ...
    ...    **注意：** 此測試依賴按鈕硬體行為
    [Tags]    vision    polling    timeout

    Given 機器手臂已連接到遠端伺服器
    When 用戶按壓第 "light1" 按鈕
    When 用戶等待按鈕 "light1" 變為 "blue" 色
    Then 等待應該成功完成


測試案例 08: 輪詢等待超時測試（負面測試）
    [Documentation]    測試輪詢超時機制
    ...
    ...    **測試步驟：**
    ...    1. 等待一個不存在的顏色（例如 "red"）
    ...    2. 設定短超時時間（5 秒）
    ...    3. 驗證超時錯誤
    ...
    ...    **預期結果：**
    ...    - 超時後拋出 TimeoutError
    ...    - 錯誤訊息包含超時資訊
    [Tags]    vision    polling    timeout    negative

    Given 機器手臂已連接到遠端伺服器
    When 用戶嘗試等待按鈕 "light1" 變為 "red" 色並設定超時 5 秒
    Then 應該拋出超時錯誤


測試案例 09: 檢測未校準按鈕（負面測試）
    [Documentation]    測試未校準按鈕的錯誤處理
    ...
    ...    **測試步驟：**
    ...    1. 嘗試檢測一個未校準 ROI 的按鈕
    ...    2. 驗證錯誤訊息
    ...
    ...    **預期結果：**
    ...    - 拋出 ValueError
    ...    - 錯誤訊息提示需要校準
    [Tags]    vision    error    negative

    Given 機器手臂已連接到遠端伺服器
    When 用戶嘗試檢測未校準按鈕
    Then 應該提示需要校準 ROI


測試案例 10: 連續檢測穩定性測試
    [Documentation]    測試連續檢測的穩定性
    ...
    ...    **測試步驟：**
    ...    1. 連續檢測 Light1 按鈕 10 次
    ...    2. 驗證結果一致性
    ...
    ...    **預期結果：**
    ...    - 所有檢測都成功
    ...    - 顏色結果一致（允許 1 次誤差）
    [Tags]    vision    stability    stress

    Given 機器手臂已連接到遠端伺服器
    When 用戶連續檢測按鈕 "light1" 共 10 次
    Then 檢測結果應該一致


*** Keywords ***
Given 機器手臂系統已準備就緒
    [Documentation]    Suite Setup - 確認系統環境
    Log    ========================================
    Log    機器手臂視覺檢測測試 - Phase 3
    Log    ========================================
    Log    Server: ${SERVER_HOST}:${SERVER_PORT}
    Log    Config: ${CONFIG_FILE}
    Log    ========================================

Given 機器手臂已連接到遠端伺服器
    [Documentation]    連接到機器手臂伺服器
    When 用戶連接到機器手臂    ${SERVER_HOST}    ${SERVER_PORT}
    Sleep    0.5s    等待連接穩定

And 機器手臂已安全斷開連接
    [Documentation]    Suite Teardown - 斷開連接
    Run Keyword And Ignore Error    When 用戶中斷與機器手臂的連接
    Log    測試套件執行完畢

記錄失敗原因
    [Documentation]    Test Teardown - 記錄失敗資訊
    Log    ❌ 測試失敗，請檢查：
    Log    1. 伺服器是否正常運行
    Log    2. 按鈕是否已校準 ROI
    Log    3. 攝影機是否正常工作
    Log    4. 實際硬體狀態是否符合預期

Then 檢測應該成功完成
    [Documentation]    驗證檢測成功
    Then 上一步操作應該成功

And 記錄檢測結果
    [Documentation]    記錄視覺檢測結果
    ${result}=    取得最後檢測結果
    Log    檢測結果：
    Log    - 顏色: ${result}[color]
    Log    - 亮度: ${result}[brightness]
    Log    - 信心度: ${result}[confidence]

And 準備檢測按鈕清單
    [Documentation]    準備按鈕 ID 清單
    [Arguments]    @{button_ids}
    Set Test Variable    @{BUTTON_LIST}    @{button_ids}
    ${count}=    Get Length    ${button_ids}
    Log    準備檢測 ${count} 個按鈕

When 用戶檢測多個按鈕的燈光狀態
    [Documentation]    執行批次檢測
    ${results}=    RobotArmKeywords.When 用戶檢測多個按鈕的燈光狀態    @{BUTTON_LIST}
    Set Test Variable    ${BATCH_RESULTS}    ${results}

Then 所有按鈕檢測應該成功
    [Documentation]    驗證所有按鈕檢測成功
    ${total}=    Get Length    ${BATCH_RESULTS}
    ${success}=    Set Variable    0
    FOR    ${result}    IN    @{BATCH_RESULTS}
        ${success}=    Set Variable If    ${result}[success]    ${success + 1}    ${success}
    END
    Should Be Equal As Numbers    ${success}    ${total}    msg=部分按鈕檢測失敗

And 記錄批次檢測結果
    [Documentation]    記錄批次檢測結果
    Log    批次檢測結果：
    FOR    ${result}    IN    @{BATCH_RESULTS}
        Log    - ${result}[button_id]: ${result}[result][color] (成功: ${result}[success])
    END

Then 批次檢測成功率應該大於
    [Documentation]    驗證成功率
    [Arguments]    ${min_rate}
    ${total}=    Get Length    ${BATCH_RESULTS}
    ${success}=    Set Variable    0
    FOR    ${result}    IN    @{BATCH_RESULTS}
        ${success}=    Set Variable If    ${result}[success]    ${success + 1}    ${success}
    END
    ${rate}=    Evaluate    ${success} * 100 / ${total}
    Log    成功率: ${rate}%
    Should Be True    ${rate} >= ${min_rate}    msg=成功率過低: ${rate}%

And 記錄按鈕 "${button_id}" 的初始狀態
    [Documentation]    記錄按鈕初始狀態
    ${initial_result}=    When 用戶檢測第 "${button_id}" 按鈕的燈光狀態
    Set Test Variable    ${INITIAL_STATE}    ${initial_result}[color]
    Log    初始狀態: ${INITIAL_STATE}

When 用戶按壓 "${button_id}" 按鈕
    [Documentation]    按壓按鈕
    When 用戶按壓第 "${button_id}" 按鈕
    Sleep    2s    等待燈光穩定

Then 按鈕狀態應該與初始狀態不同
    [Documentation]    驗證狀態改變
    ${current_result}=    取得最後檢測結果
    ${current_state}=    Set Variable    ${current_result}[color]
    Should Not Be Equal    ${current_state}    ${INITIAL_STATE}    msg=按鈕狀態未改變

Then 等待應該成功完成
    [Documentation]    驗證等待成功
    Log    ✓ 輪詢等待成功

When 用戶嘗試等待按鈕 "${button_id}" 變為 "${color}" 色並設定超時 ${timeout} 秒
    [Documentation]    嘗試等待（預期失敗）
    Run Keyword And Expect Error    TimeoutError*
    ...    When 用戶等待按鈕 "${button_id}" 變為 "${color}" 色    timeout=${timeout}    interval=1.0

Then 應該拋出超時錯誤
    [Documentation]    驗證超時錯誤
    Log    ✓ 正確拋出超時錯誤

When 用戶嘗試檢測未校準按鈕
    [Documentation]    嘗試檢測未校準按鈕
    # 假設 camera_observe 沒有實際按鈕，只有觀測角度
    Run Keyword And Expect Error    ValueError*未校準*
    ...    When 用戶檢測第 "camera_observe" 按鈕的燈光狀態

Then 應該提示需要校準 ROI
    [Documentation]    驗證錯誤訊息
    Log    ✓ 正確提示需要校準

When 用戶連續檢測按鈕 "${button_id}" 共 ${count} 次
    [Documentation]    連續檢測
    @{results}=    Create List
    FOR    ${i}    IN RANGE    ${count}
        ${result}=    When 用戶檢測第 "${button_id}" 按鈕的燈光狀態
        Append To List    ${results}    ${result}[color]
    END
    Set Test Variable    @{CONTINUOUS_RESULTS}    @{results}

Then 檢測結果應該一致
    [Documentation]    驗證結果一致性
    ${total}=    Get Length    ${CONTINUOUS_RESULTS}
    ${first}=    Set Variable    ${CONTINUOUS_RESULTS}[0]
    ${same_count}=    Set Variable    0
    FOR    ${color}    IN    @{CONTINUOUS_RESULTS}
        ${same_count}=    Set Variable If    '${color}' == '${first}'    ${same_count + 1}    ${same_count}
    END
    ${consistency}=    Evaluate    ${same_count} * 100 / ${total}
    Log    一致性: ${consistency}%
    Should Be True    ${consistency} >= 90    msg=檢測結果不穩定
