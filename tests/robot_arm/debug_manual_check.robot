*** Settings ***
Library          ../../libraries/robot_arm_control/RobotArmKeywords.py

*** Test Cases ***
Check Light Status
    [Documentation]    Capture current light status (User says it is ON)
    Given 測試環境設定為 "taipei_lab"
    Given 面板類型設定為 "3611a"
    Given 環境 IP Camera 已完成預熱連接    60
    When 用戶檢測環境燈光亮度 "level1_light_1"    save_debug_image=${True}    step_prefix=manual_on
