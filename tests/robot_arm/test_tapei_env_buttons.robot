*** Settings ***
Documentation    Taipei Lab 按鈕完整循環測試套件
...              測試所有按鈕的 ON -> OFF 循環
...              環境: taipei_lab
...              面板: 3611a

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime
Library          Collections

Suite Setup      Setup Suite Environment
Suite Teardown   Teardown Suite Environment

*** Variables ***
${SUITE_START_TIME}    ${EMPTY}
${SUITE_END_TIME}      ${EMPTY}

*** Keywords ***
Setup Suite Environment
    [Documentation]    Suite 初始化：連接機器手臂並記錄開始時間
    # 記錄開始時間
    ${start}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Set Suite Variable    ${SUITE_START_TIME}    ${start}
    Log    ========== 測試開始時間: ${start} ==========    console=yes
    # 設定環境（只執行一次）
    Given 測試環境設定為 "taipei_lab"
    Given 面板類型設定為 "3611a"
    Given 機器手臂已正確連接到控制面板

Teardown Suite Environment
    [Documentation]    Suite 結束：返回待命位置並顯示總耗時
    # 返回待命位置
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置
    # 計算耗時
    ${end}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Set Suite Variable    ${SUITE_END_TIME}    ${end}
    ${start_dt}=    Convert Date    ${SUITE_START_TIME}    date_format=%Y-%m-%d %H:%M:%S
    ${end_dt}=      Convert Date    ${SUITE_END_TIME}      date_format=%Y-%m-%d %H:%M:%S
    ${elapsed}=     Subtract Date From Date    ${end_dt}    ${start_dt}
    ${minutes}=     Evaluate    int(${elapsed} // 60)
    ${seconds}=     Evaluate    int(${elapsed} % 60)
    Log    ========== 測試結束時間: ${end} ==========    console=yes
    Log    ========== 總耗時: ${minutes} 分 ${seconds} 秒 (${elapsed} 秒) ==========    console=yes

按壓按鈕並驗證狀態變化
    [Documentation]    通用關鍵字：按壓按鈕並驗證 off -> on -> off -> on -> off 循環
    [Arguments]    ${button_id}
    # 步驟 0: 若檢測到 x status 則多點一下喚醒
    Given 若 YOLO 檢測到按鈕 "${button_id}" 為 "x" 則點擊喚醒
    # 步驟 1: 驗證初始狀態為 off
    Given YOLO 應該檢測到按鈕 "${button_id}" 為 "off"
    # 步驟 2: 按壓按鈕開啟
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成
    # 步驟 3: 驗證狀態變為 on
    And YOLO 應該檢測到按鈕 "${button_id}" 為 "on"
    # 步驟 4: 再次按壓按鈕關閉
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成
    # 步驟 5: 驗證狀態變回 off
    And YOLO 應該檢測到按鈕 "${button_id}" 為 "off"


連續按壓按鈕並拍照
    [Documentation]    連續按壓按鈕 N 次，每次按壓後拍照記錄
    [Arguments]    ${button_id}    ${times}=7
    FOR    ${i}    IN RANGE    1    ${times}+1
        Log    ===== 第 ${i}/${times} 次按壓 ${button_id} =====    console=yes
        When 用戶按壓第 "${button_id}" 按鈕
        Then 機器手臂操作應該成功完成
        # 每次按壓後拍照記錄狀態
        YOLO 僅檢測並儲存按鈕影像 "${button_id}" 預期狀態 "click_${i}"
    END

長按按鈕
    [Documentation]    長按按鈕指定秒數
    [Arguments]    ${button_id}    ${duration}=4
    Log    ===== 長按 ${button_id} ${duration} 秒 =====    console=yes
    When 用戶按壓第 "${button_id}" 按鈕持續 "${duration}" 秒
    Then 機器手臂操作應該成功完成
    # 長按後拍照記錄
    YOLO 僅檢測並儲存按鈕影像 "${button_id}" 預期狀態 "long_press"

*** Test Cases ***
測試 Light1 按鈕 ON-OFF 循環
    [Documentation]    測試 Light1 按鈕: off -> on -> off
    [Tags]    taipei_lab    light1    button    cycle
    按壓按鈕並驗證狀態變化    light1

測試 Light2 按鈕 ON-OFF 循環
    [Documentation]    測試 Light2 按鈕: off -> on -> off
    [Tags]    taipei_lab    light2    button    cycle
    按壓按鈕並驗證狀態變化    light2

測試 Light3 按鈕 ON-OFF 循環
    [Documentation]    測試 Light3 按鈕: off -> on -> off
    [Tags]    taipei_lab    light3    button    cycle
    按壓按鈕並驗證狀態變化    light3

測試 Light4 按鈕 ON-OFF 循環
    [Documentation]    測試 Light4 按鈕: off -> on -> off
    [Tags]    taipei_lab    light4    button    cycle
    按壓按鈕並驗證狀態變化    light4

測試 Light5 按鈕 ON-OFF 循環
    [Documentation]    測試 Light5 按鈕: off -> on -> off
    [Tags]    taipei_lab    light5    button    cycle
    按壓按鈕並驗證狀態變化    light5

測試 Light6 按鈕 ON-OFF 循環
    [Documentation]    測試 Light6 按鈕: off -> on -> off
    [Tags]    taipei_lab    light6    button    cycle
    按壓按鈕並驗證狀態變化    light6

測試 Light7 按鈕 ON-OFF 循環
    [Documentation]    測試 Light7 按鈕: off -> on -> off
    [Tags]    taipei_lab    light7    button    cycle
    按壓按鈕並驗證狀態變化    light7

測試 Light8 按鈕 ON-OFF 循環
    [Documentation]    測試 Light8 按鈕: off -> on -> off
    [Tags]    taipei_lab    light8    button    cycle
    按壓按鈕並驗證狀態變化    light8

測試 Bluetooth 按鈕 ON-OFF 循環
    [Documentation]    測試 Bluetooth 按鈕: off -> on -> off
    [Tags]    taipei_lab    bluetooth    button    cycle
    按壓按鈕並驗證狀態變化    bluetooth

測試 AUX1 按鈕 ON-OFF 循環
    [Documentation]    測試 AUX1 按鈕: off -> on -> off
    [Tags]    taipei_lab    aux1    button    cycle
    按壓按鈕並驗證狀態變化    aux1

測試 AUX2 按鈕 ON-OFF 循環
    [Documentation]    測試 AUX2 按鈕: off -> on -> off
    [Tags]    taipei_lab    aux2    button    cycle
    按壓按鈕並驗證狀態變化    aux2

測試 Door Lock 按鈕 ON-OFF 循環
    [Documentation]    測試 Door Lock 按鈕: off -> on -> off
    [Tags]    taipei_lab    door_lock    button    cycle
    按壓按鈕並驗證狀態變化    door_lock

測試 Tank Heater 按鈕 ON-OFF 循環
    [Documentation]    測試 Tank Heater 按鈕: off -> on -> off
    [Tags]    taipei_lab    tank_heater    button    cycle
    按壓按鈕並驗證狀態變化    tank_heater

測試 Water Pump 按鈕 ON-OFF 循環
    [Documentation]    測試 Water Pump 按鈕: off -> on -> off
    [Tags]    taipei_lab    water_pump    button    cycle
    按壓按鈕並驗證狀態變化    water_pump

測試 Water Heater Electric 按鈕 ON-OFF 循環
    [Documentation]    測試 Water Heater Electric 按鈕: off -> on -> off
    [Tags]    taipei_lab    water_heater_electric    button    cycle
    按壓按鈕並驗證狀態變化    water_heater_electric

測試 Water Heater Gas 按鈕 ON-OFF 循環
    [Documentation]    測試 Water Heater Gas 按鈕: off -> on -> off
    [Tags]    taipei_lab    water_heater_gas    button    cycle
    按壓按鈕並驗證狀態變化    water_heater_gas

測試 Climate Control 按鈕 ON-OFF 循環
    [Documentation]    測試 Climate Control 按鈕: off -> on -> off
    [Tags]    taipei_lab    climate_control    button    cycle
    按壓按鈕並驗證狀態變化    climate_control

測試 Fridge 按鈕 ON-OFF 循環
    [Documentation]    測試 Fridge 按鈕: off -> on -> off
    [Tags]    taipei_lab    fridge    button    cycle
    按壓按鈕並驗證狀態變化    fridge

測試 Select 按鈕連點7次
    [Documentation]    測試 Select 按鈕連續按壓 7 次，每次拍照記錄
    [Tags]    taipei_lab    select    button    loop
    連續按壓按鈕並拍照    select    7

測試 Extend 長按按鈕
    [Documentation]    測試 Extend 按鈕長按 4 秒
    [Tags]    taipei_lab    extend    button    long_press
    長按按鈕    extend    4

測試 Retract 長按按鈕
    [Documentation]    測試 Retract 按鈕長按 4 秒
    [Tags]    taipei_lab    retract    button    long_press
    長按按鈕    retract    4