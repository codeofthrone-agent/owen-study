*** Settings ***
Documentation    RV Car 按鈕測試套件
...              測試 config/robot_arm/rv_car_buttons.yaml 中定義的所有按鈕
...              環境: RV Car
...              面板: 3611a

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

Test Setup       Setup Test Environment
Test Teardown    Teardown Test Environment

*** Keywords ***
Setup Test Environment
    # 1. 設定環境為 RV Car
    Given 測試環境設定為 "taipei_lab"
    # 2. 設定面板類型
    Given 面板類型設定為 "3611a"
    # 3. 連接機器手臂 (如果尚未連接)
    Given 機器手臂已正確連接到控制面板

Teardown Test Environment
    # 測試結束後返回待命位置
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

*** Test Cases ***
測試 Light1 按鈕
    [Documentation]    測試按壓 Light1 按鈕
    [Tags]    rv_car    light1    button
    When 用戶按壓第 "light1" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light2 按鈕
    [Documentation]    測試按壓 Light2 按鈕
    [Tags]    rv_car    light2    button
    When 用戶按壓第 "light2" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light3 按鈕
    [Documentation]    測試按壓 Light3 按鈕
    [Tags]    rv_car    light3    button
    When 用戶按壓第 "light3" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light4 按鈕
    [Documentation]    測試按壓 Light4 按鈕
    [Tags]    rv_car    light4    button
    When 用戶按壓第 "light4" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light5 按鈕
    [Documentation]    測試按壓 Light5 按鈕
    [Tags]    rv_car    light5    button
    When 用戶按壓第 "light5" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light6 按鈕
    [Documentation]    測試按壓 Light6 按鈕 FIX
    [Tags]    rv_car    light6    button
    When 用戶按壓第 "light6" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light7 按鈕
    [Documentation]    測試按壓 Light7 按鈕
    [Tags]    rv_car    light7    button
    When 用戶按壓第 "light7" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light8 按鈕
    [Documentation]    測試按壓 Light8 按鈕
    [Tags]    rv_car    light8    button
    When 用戶按壓第 "light8" 按鈕
    Then 機器手臂操作應該成功完成

測試 Bluetooth 按鈕
    [Documentation]    測試按壓 Bluetooth 按鈕
    [Tags]    rv_car    bluetooth    button
    When 用戶按壓第 "bluetooth" 按鈕
    Then 機器手臂操作應該成功完成

測試 Select 按鈕
    [Documentation]    測試按壓 Select 按鈕
    [Tags]    rv_car    select    button
    When 用戶按壓第 "select" 按鈕
    Then 機器手臂操作應該成功完成

測試 AUX1 按鈕
    [Documentation]    測試按壓 AUX1 按鈕
    [Tags]    rv_car    aux1    button
    When 用戶按壓第 "aux1" 按鈕
    Then 機器手臂操作應該成功完成

測試 AUX2 按鈕
    [Documentation]    測試按壓 AUX2 按鈕
    [Tags]    rv_car    aux2    button
    When 用戶按壓第 "aux2" 按鈕
    Then 機器手臂操作應該成功完成

測試 Door Lock 按鈕
    [Documentation]    測試按壓 Door Lock 按鈕
    [Tags]    rv_car    door_lock    button
    When 用戶按壓第 "door_lock" 按鈕
    Then 機器手臂操作應該成功完成

測試 Tank Heater 按鈕
    [Documentation]    測試按壓 Tank Heater 按鈕
    [Tags]    rv_car    tank_heater    button
    When 用戶按壓第 "tank_heater" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Pump 按鈕
    [Documentation]    測試按壓 Water Pump 按鈕
    [Tags]    rv_car    water_pump    button
    When 用戶按壓第 "water_pump" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Heater Electric 按鈕
    [Documentation]    測試按壓 Water Heater Electric 按鈕
    [Tags]    rv_car    water_heater_electric    button
    When 用戶按壓第 "water_heater_electric" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Heater Gas 按鈕
    [Documentation]    測試按壓 Water Heater Gas 按鈕
    [Tags]    rv_car    water_heater_gas    button
    When 用戶按壓第 "water_heater_gas" 按鈕
    Then 機器手臂操作應該成功完成

測試 Climate control 按鈕
    [Documentation]    測試按壓 Climate control 按鈕
    [Tags]    rv_car    climate_control    button
    When 用戶按壓第 "climate_control" 按鈕
    Then 機器手臂操作應該成功完成

測試 Extend 按鈕
    [Documentation]    測試按壓 Extend 按鈕
    [Tags]    rv_car    extend    button
    When 用戶按壓第 "extend" 按鈕持續 "4" 秒
    Then 機器手臂操作應該成功完成

測試 Retract 按鈕
    [Documentation]    測試按壓 Retract 按鈕
    [Tags]    rv_car    retract    button
    When 用戶按壓第 "retract" 按鈕持續 "4" 秒
    Then 機器手臂操作應該成功完成

測試 Fridge 按鈕
    [Documentation]    測試按壓 Fridge 按鈕
    [Tags]    rv_car    fridge    button
    When 用戶按壓第 "fridge" 按鈕
    Then 機器手臂操作應該成功完成