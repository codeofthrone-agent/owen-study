*** Settings ***
Documentation    機械手臂關節移動追蹤驗證測試
...              驗證 Maintenance Analysis 功能是否正確追蹤關節移動量
...              環境: taipei_lab
...              面板: 3611a

Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          Collections

Suite Setup      Setup Suite Environment
Suite Teardown   Teardown Suite Environment

*** Keywords ***
Setup Suite Environment
    [Documentation]    Suite 初始化
    Given 測試環境設定為 "taipei_lab"
    Given 機器手臂已正確連接到控制面板

Teardown Suite Environment
    [Documentation]    Suite 結束
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

*** Test Cases ***
驗證關節移動統計功能
    [Documentation]    測試關節移動統計的重置與累計功能
    [Tags]    maintenance    tracking

    # 1. 重置統計
    重置關節移動統計
    ${initial_stats}=    取得關節移動統計
    
    # 驗證初始值全為 0
    FOR    ${val}    IN    @{initial_stats}
        Should Be Equal As Numbers    ${val}    0.0
    END

    # 2. 執行移動動作 (按壓 Light 1)
    # 這會觸發: Current -> Up -> Down -> Up -> (Next Move)
    # 根據推算模式，應該會累積移動量
    When 用戶透過機器手臂開啟第 "1" 號燈光
    Then 機器手臂操作應該成功完成

    # 3. 取得統計數據
    ${final_stats}=    取得關節移動統計
    記錄關節移動統計

    # 4. 驗證數據 (確認有移動)
    # 至少某些關節應該有移動量 (> 0)
    ${total_movement}=    Evaluate    sum(${final_stats})
    Should Be True    ${total_movement} > 0    msg=總移動量應該大於 0

    Log    Total Movement: ${total_movement} degrees
