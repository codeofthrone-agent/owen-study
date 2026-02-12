*** Settings ***
Documentation    Taipei Lab 按鈕完整循環測試套件
...              測試所有按鈕的 ON -> OFF 循環
...              環境: taipei_lab
...              面板: 3611a

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime
Library          Collections
Library          Process
Library          String

Suite Setup      Setup Suite Environment
Suite Teardown   Teardown Suite Environment
Test Teardown    Teardown Test Environment

*** Variables ***
${SUITE_START_TIME}    ${EMPTY}
${SUITE_END_TIME}      ${EMPTY}
# 環境燈光穩定等待時間（秒）- 讓光暈/餘暉消散
${ENV_LIGHT_SETTLE_TIME}    1

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
    # 預熱 IP Camera 連接（避免 HEVC codec 錯誤）
    Given 環境 IP Camera 已完成預熱連接    60

Teardown Test Environment
    [Documentation]    Test 結束：返回待命位置
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

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


列出最新 Debug 圖片
    [Documentation]    列出指定前綴的最新 debug 圖片路徑
    [Arguments]    ${step_prefix}
    ${debug_dir}=    Set Variable    ${CURDIR}/../../output/debug_images
    ${result}=    Run Process    ls -t ${debug_dir}/${step_prefix}*.jpg 2>/dev/null | head -2    shell=True
    Log    📷 [${step_prefix}] Debug 圖片:    console=True
    ${lines}=    Split String    ${result.stdout}    \n
    FOR    ${line}    IN    @{lines}
        Continue For Loop If    '${line}' == ''
        Log    　　${line}    console=True
    END

按壓按鈕並驗證狀態變化
    [Documentation]    智慧驗證關鍵字：根據設定檔自動判斷驗證模式
    ...                - 若有環境燈光設定：驗證環境亮度 (0% <-> 100%)
    ...                - 若無環境燈光設定：驗證面板按鈕狀態 (OFF <-> ON)
    [Arguments]    ${button_id}
    
    # 1. 動態查詢驗證模式
    ${env_id}=    取得按鈕對應的環境燈光 ID    ${button_id}
    Log    按鈕 ${button_id} 對應的環境燈光 ID: ${env_id}    console=True
    
    # 2. 執行驗證 (分支邏輯)
    Run Keyword If    '${env_id}' != '${None}'    執行環境燈光循環測試    ${button_id}    ${env_id}
    ...    ELSE    執行面板燈光循環測試    ${button_id}

執行環境燈光循環測試
    [Arguments]    ${button_id}    ${env_id}
    [Documentation]    環境燈光驗證模式 (OFF -> ON -> OFF)
    ...                同時驗證環境燈光 (RTSP) 和面板燈光 (YOLO)

    Log    [模式 A] 執行雙重燈光驗證: ${env_id} (環境) + ${button_id} (面板)    console=True

    # 步驟 0: 若檢測到 x status 則多點一下喚醒
    若 YOLO 檢測到按鈕 "${button_id}" 為 "x" 則點擊喚醒

    # 步驟 1: 驗證初始狀態為 off (環境燈光 + 面板燈光)
    ${t0}=    Get Current Date    result_format=epoch
    ${result1}=    When 用戶檢測環境燈光亮度 "${env_id}"    save_debug_image=${True}    step_prefix=step1_off
    ${t1}=    Get Current Date    result_format=epoch
    ${d1}=    Evaluate    round(${t1} - ${t0}, 1)
    Log    ⏱️ [Step1] 檢測環境燈光初始狀態: ${d1}s    console=True
    列出最新 Debug 圖片    step1_off
    Then 環境燈光狀態應該為 "off"
    # 雙重驗證: YOLO 檢測面板燈光
    YOLO 應該檢測到按鈕 "${button_id}" 為 "off"    save_debug_image=${True}
    列出最新 Debug 圖片    yolo_valid

    # 步驟 2: 按壓按鈕開啟
    ${t2}=    Get Current Date    result_format=epoch
    When 用戶按壓第 "${button_id}" 按鈕
    ${t3}=    Get Current Date    result_format=epoch
    ${d2}=    Evaluate    round(${t3} - ${t2}, 1)
    Log    ⏱️ [Step2] 按壓按鈕開啟: ${d2}s    console=True
    Then 機器手臂操作應該成功完成
    # 等待環境燈光穩定（讓光暈消散）
    Log    ⏳ 等待環境燈光穩定 ${ENV_LIGHT_SETTLE_TIME}s...    console=True
    Sleep    ${ENV_LIGHT_SETTLE_TIME}

    # 步驟 3: 驗證狀態變為 on (環境燈光 + 面板燈光)
    ${t4}=    Get Current Date    result_format=epoch
    ${result2}=    When 用戶檢測環境燈光亮度 "${env_id}"    save_debug_image=${True}    step_prefix=step2_on
    ${t5}=    Get Current Date    result_format=epoch
    ${d3}=    Evaluate    round(${t5} - ${t4}, 1)
    Log    ⏱️ [Step3] 檢測環境燈光開啟狀態: ${d3}s    console=True
    列出最新 Debug 圖片    step2_on
    Then 環境燈光狀態應該為 "on"
    # 雙重驗證: YOLO 檢測面板燈光
    YOLO 應該檢測到按鈕 "${button_id}" 為 "on"    save_debug_image=${True}
    列出最新 Debug 圖片    yolo_valid

    # 步驟 4: 再次按壓按鈕關閉
    ${t6}=    Get Current Date    result_format=epoch
    When 用戶按壓第 "${button_id}" 按鈕
    ${t7}=    Get Current Date    result_format=epoch
    ${d4}=    Evaluate    round(${t7} - ${t6}, 1)
    Log    ⏱️ [Step4] 按壓按鈕關閉: ${d4}s    console=True
    Then 機器手臂操作應該成功完成
    # 等待環境燈光穩定（讓光暈/餘暉消散）
    Log    ⏳ 等待環境燈光穩定 ${ENV_LIGHT_SETTLE_TIME}s...    console=True
    Sleep    ${ENV_LIGHT_SETTLE_TIME}

    # 步驟 5: 驗證狀態變回 off (環境燈光 + 面板燈光)
    ${t8}=    Get Current Date    result_format=epoch
    ${result3}=    When 用戶檢測環境燈光亮度 "${env_id}"    save_debug_image=${True}    step_prefix=step3_off
    ${t9}=    Get Current Date    result_format=epoch
    ${d5}=    Evaluate    round(${t9} - ${t8}, 1)
    Log    ⏱️ [Step5] 檢測環境燈光關閉狀態: ${d5}s    console=True
    列出最新 Debug 圖片    step3_off
    Then 環境燈光狀態應該為 "off"
    # 雙重驗證: YOLO 檢測面板燈光
    YOLO 應該檢測到按鈕 "${button_id}" 為 "off"    save_debug_image=${True}
    列出最新 Debug 圖片    yolo_valid

    # 總結
    ${total}=    Evaluate    round(${t9} - ${t0}, 1)
    Log    ⏱️ [總計] 循環測試: ${total}s (檢測=${d1}+${d3}+${d5}, 按壓=${d2}+${d4})    console=True
    Log    ✅ 雙重驗證完成: 環境燈光 (RTSP) ✓ 面板燈光 (YOLO) ✓    console=True

執行面板燈光循環測試
    [Arguments]    ${button_id}
    [Documentation]    面板燈光驗證模式 (OFF -> ON -> OFF)
    
    Log    [模式 B] 執行面板LED驗證: ${button_id}    console=True
    
    # 步驟 0: 若檢測到 x status 則多點一下喚醒
    Given 若 YOLO 檢測到按鈕 "${button_id}" 為 "x" 則點擊喚醒

    # 步驟 1: 驗證初始狀態為 off
    Given YOLO 應該檢測到按鈕 "${button_id}" 為 "off"    save_debug_image=${True}

    # 步驟 2: 按壓按鈕開啟
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成

    # 步驟 3: 驗證狀態變為 on
    And YOLO 應該檢測到按鈕 "${button_id}" 為 "on"    save_debug_image=${True}

    # 步驟 4: 再次按壓按鈕關閉
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成

    # 步驟 5: 驗證狀態變回 off
    And YOLO 應該檢測到按鈕 "${button_id}" 為 "off"    save_debug_image=${True}
    

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

執行 Select-Extend-Retract 測試循環
    [Documentation]    執行 Select(1次) -> Extend(4秒) -> Retract(4秒) 的測試循環
    [Arguments]    ${times}=7    ${duration}=4
    FOR    ${i}    IN RANGE    1    ${times}+1
        Log    ===== 第 ${i}/${times} 次循環：Select -> Extend -> Retract =====    console=yes
        
        # 1. Select Click
        When 用戶按壓第 "select" 按鈕
        Then 機器手臂操作應該成功完成
        # 每次按壓後拍照記錄狀態
        YOLO 僅檢測並儲存按鈕影像 "select" 預期狀態 "click_${i}"
        
        # 2. Extend Long Press
        When 用戶按壓第 "extend" 按鈕持續 "${duration}" 秒
        Then 機器手臂操作應該成功完成
        And 機器手臂應該返回待命位置

        # 3. Retract Long Press
        When 用戶按壓第 "retract" 按鈕持續 "${duration}" 秒
        Then 機器手臂操作應該成功完成

    END

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

測試 Select-Extend-Retract 循環
    [Documentation]    測試 Select -> Extend -> Retract 循環 7 次
    [Tags]    taipei_lab    select    extend    retract    loop    complex
    執行 Select-Extend-Retract 測試循環    7