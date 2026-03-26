*** Settings ***
Documentation     機器手臂視覺檢測快速測試
...
...               **用途：** 快速驗證視覺檢測功能是否正常
...               **適用場景：** 開發階段快速測試、CI/CD 整合
...
...               **前置條件：**
...               - robot_arm_server.py 已啟動
...               - 至少 Light1 按鈕已校準 ROI
...
...               **執行方式：**
...               robot tests/robot_arm/vision_quick_test.robot

Library           ../../../libraries/robot_arm_control/RobotArmKeywords.py

Suite Setup       連接機器手臂伺服器
Suite Teardown    斷開機器手臂連接


*** Variables ***
${SERVER_HOST}        10.42.0.180
${SERVER_PORT}        9000


*** Test Cases ***
快速測試: 檢測單一按鈕
    [Documentation]    最基本的視覺檢測測試
    [Tags]    quick    smoke

    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 上一步操作應該成功
    Log    ✓ 視覺檢測功能正常


快速測試: 批次檢測三個按鈕
    [Documentation]    測試批次檢測功能
    [Tags]    quick    batch

    ${button_list}=    Create List    light1    light2    light3
    ${results}=    When 用戶檢測多個按鈕的燈光狀態    ${button_list}

    ${total}=    Get Length    ${results}
    Log    批次檢測完成: ${total} 個按鈕

    Should Be Equal As Numbers    ${total}    3


*** Keywords ***
連接機器手臂伺服器
    [Documentation]    連接到伺服器
    When 用戶連接到機器手臂    ${SERVER_HOST}    ${SERVER_PORT}
    Log    ✓ 已連接到 ${SERVER_HOST}:${SERVER_PORT}

斷開機器手臂連接
    [Documentation]    斷開連接
    When 用戶中斷與機器手臂的連接
    Log    ✓ 已斷開連接
