*** Settings ***
Documentation    桃園 4F 按鈕測試套件
...              測試 config/robot_arm/taoyuan_4f_buttons.yaml 中定義的所有按鈕
...              環境: Taoyuan 4F

Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

Test Setup       Setup Test Environment
Test Teardown    Teardown Test Environment

*** Keywords ***
Setup Test Environment
    # 1. 設定環境為 桃園 4F
    Given 測試環境設定為 "taoyuan_4f"
    # 2. 連接機器手臂
    Given 機器手臂已正確連接到控制面板

Teardown Test Environment
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

*** Test Cases ***
測試 Light1 按鈕
    [Documentation]    測試按壓 Light1 按鈕
    [Tags]    taoyuan_4f    light1    button
    When 用戶按壓第 "light1" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light2 按鈕
    [Documentation]    測試按壓 Light2 按鈕
    [Tags]    taoyuan_4f    light2    button
    When 用戶按壓第 "light2" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light3 按鈕
    [Documentation]    測試按壓 Light3 按鈕
    [Tags]    taoyuan_4f    light3    button
    When 用戶按壓第 "light3" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light4 按鈕
    [Documentation]    測試按壓 Light4 按鈕
    [Tags]    taoyuan_4f    light4    button
    When 用戶按壓第 "light4" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light5 按鈕
    [Documentation]    測試按壓 Light5 按鈕
    [Tags]    taoyuan_4f    light5    button
    When 用戶按壓第 "light5" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light6 按鈕
    [Documentation]    測試按壓 Light6 按鈕
    [Tags]    taoyuan_4f    light6    button
    When 用戶按壓第 "light6" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light7 按鈕
    [Documentation]    測試按壓 Light7 按鈕
    [Tags]    taoyuan_4f    light7    button
    When 用戶按壓第 "light7" 按鈕
    Then 機器手臂操作應該成功完成

測試 Light8 按鈕
    [Documentation]    測試按壓 Light8 按鈕
    [Tags]    taoyuan_4f    light8    button
    When 用戶按壓第 "light8" 按鈕
    Then 機器手臂操作應該成功完成

測試 Bluetooth 按鈕
    [Documentation]    測試按壓 Bluetooth 按鈕
    [Tags]    taoyuan_4f    bluetooth    button
    When 用戶按壓第 "bluetooth" 按鈕
    Then 機器手臂操作應該成功完成

測試 Select 按鈕
    [Documentation]    測試按壓 Select 按鈕
    [Tags]    taoyuan_4f    select    button
    When 用戶按壓第 "select" 按鈕
    Then 機器手臂操作應該成功完成

測試 AUX1 按鈕
    [Documentation]    測試按壓 AUX1 按鈕
    [Tags]    taoyuan_4f    aux1    button
    When 用戶按壓第 "aux1" 按鈕
    Then 機器手臂操作應該成功完成

測試 AUX2 按鈕
    [Documentation]    測試按壓 AUX2 按鈕
    [Tags]    taoyuan_4f    aux2    button
    When 用戶按壓第 "aux2" 按鈕
    Then 機器手臂操作應該成功完成

測試 Door Lock 按鈕
    [Documentation]    測試按壓 Door Lock 按鈕
    [Tags]    taoyuan_4f    door_lock    button
    When 用戶按壓第 "door_lock" 按鈕
    Then 機器手臂操作應該成功完成

測試 Tank Heater 按鈕
    [Documentation]    測試按壓 Tank Heater 按鈕
    [Tags]    taoyuan_4f    tank_heater    button
    When 用戶按壓第 "tank_heater" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Pump 按鈕
    [Documentation]    測試按壓 Water Pump 按鈕
    [Tags]    taoyuan_4f    water_pump    button
    When 用戶按壓第 "water_pump" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Heater Electric 按鈕
    [Documentation]    測試按壓 Water Heater Electric 按鈕
    [Tags]    taoyuan_4f    water_heater_electric    button
    When 用戶按壓第 "water_heater_electric" 按鈕
    Then 機器手臂操作應該成功完成

測試 Water Heater Gas 按鈕
    [Documentation]    測試按壓 Water Heater Gas 按鈕
    [Tags]    taoyuan_4f    water_heater_gas    button
    When 用戶按壓第 "water_heater_gas" 按鈕
    Then 機器手臂操作應該成功完成

測試 Fridge 按鈕
    [Documentation]    測試按壓 Fridge 按鈕
    [Tags]    taoyuan_4f    fridge    button
    When 用戶按壓第 "fridge" 按鈕
    Then 機器手臂操作應該成功完成

測試 Climate Control 按鈕
    [Documentation]    測試按壓 Climate Control 按鈕
    [Tags]    taoyuan_4f    climate_control    button
    When 用戶按壓第 "climate_control" 按鈕
    Then 機器手臂操作應該成功完成

測試 Extend 按鈕
    [Documentation]    測試按壓 Extend 按鈕
    [Tags]    taoyuan_4f    extend    button
    When 用戶按壓第 "extend" 按鈕持續 "4" 秒
    Then 機器手臂操作應該成功完成

測試 Retract 按鈕
    [Documentation]    測試按壓 Retract 按鈕
    [Tags]    taoyuan_4f    retract    button
    When 用戶按壓第 "retract" 按鈕持續 "4" 秒
    Then 機器手臂操作應該成功完成

測試 A 按鈕
    [Documentation]    測試按壓 A 按鈕
    [Tags]    taoyuan_4f    lcd_a    button
    When 用戶按壓第 "lcd_a" 按鈕
    Then 機器手臂操作應該成功完成

測試 B 按鈕
    [Documentation]    測試按壓 B 按鈕
    [Tags]    taoyuan_4f    lcd_b    button
    When 用戶按壓第 "lcd_b" 按鈕
    Then 機器手臂操作應該成功完成

測試 左按鈕 按鈕
    [Documentation]    測試按壓 左按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_left    button
    When 用戶按壓第 "lcd_left" 按鈕
    Then 機器手臂操作應該成功完成

測試 右按鈕 按鈕
    [Documentation]    測試按壓 右按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_right    button
    When 用戶按壓第 "lcd_right" 按鈕
    Then 機器手臂操作應該成功完成

測試 上按鈕 按鈕
    [Documentation]    測試按壓 上按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_up    button
    When 用戶按壓第 "lcd_up" 按鈕
    Then 機器手臂操作應該成功完成

測試 下按鈕 按鈕
    [Documentation]    測試按壓 下按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_down    button
    When 用戶按壓第 "lcd_down" 按鈕
    Then 機器手臂操作應該成功完成

測試 選擇按鈕 按鈕
    [Documentation]    測試按壓 選擇按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_select    button
    When 用戶按壓第 "lcd_select" 按鈕
    Then 機器手臂操作應該成功完成

測試 返回按鈕 按鈕
    [Documentation]    測試按壓 返回按鈕 按鈕
    [Tags]    taoyuan_4f    lcd_back    button
    When 用戶按壓第 "lcd_back" 按鈕
    Then 機器手臂操作應該成功完成

