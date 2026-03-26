*** Settings ***
Documentation    LCD 按鈕影像採集專用套件
...              效能: 點擊前拍照 -> 點擊 ON -> 點擊後拍照 -> 點擊 OFF -> 點擊後拍照
...              此套件不驗證偵測狀態，僅產出影像供標記使用

Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime
Library          Collections
Library          Process
Library          String

Suite Setup      Setup Suite Environment
Suite Teardown   Teardown Suite Environment
Test Teardown    And 機器手臂應該返回待命位置

*** Variables ***
${ENV_LIGHT_SETTLE_TIME}    1

*** Keywords ***
Setup Suite Environment
    [Documentation]    初始化：連接手臂並完成預熱
    Given 測試環境設定為 "taipei_lab"
    Given 機器手臂已正確連接到控制面板

Teardown Suite Environment
    [Documentation]    結束：返回待命位置
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

執行 LCD 按鈕影像採集流程
    [Arguments]    ${button_id}
    [Documentation]    依照使用者要求的工作流進行影像採集:
    ...                1. 點擊前拍照 (before_on)
    ...                2. 點擊 ON
    ...                3. 點擊後拍照 (after_on)
    ...                4. 點擊 OFF
    ...                5. 點擊後拍照 (final_off)
    
    Log    📸 開始 LCD 採集流程: ${button_id}    console=True

    # 1. 點擊前拍照 (預期目前是 OFF)
    Log    [Step 1] 點擊 ON 前景觀拍照...    console=True
    YOLO 應該檢測到按鈕 "${button_id}" 為 "before_on"    save_debug_image=${True}    mandatory=${False}

    # 2. 點擊 ON
    Log    [Step 2] 點擊按鈕 (ON)...    console=True
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成
    Sleep    ${ENV_LIGHT_SETTLE_TIME}

    # 3. 點擊後拍照 (預期目前是 ON)
    Log    [Step 3] 點擊 ON 後景觀拍照...    console=True
    YOLO 應該檢測到按鈕 "${button_id}" 為 "after_on"    save_debug_image=${True}    mandatory=${False}

    # 4. 點擊 OFF
    Log    [Step 4] 再次點擊按鈕 (OFF)...    console=True
    When 用戶按壓第 "${button_id}" 按鈕
    Then 機器手臂操作應該成功完成
    Sleep    ${ENV_LIGHT_SETTLE_TIME}

    # 5. 點擊後拍照 (預期目前是 OFF)
    Log    [Step 5] 點擊 OFF 後景觀拍照...    console=True
    YOLO 應該檢測到按鈕 "${button_id}" 為 "final_off"    save_debug_image=${True}    mandatory=${False}

    Log    ✅ ${button_id} 採集流程完成。影像已存檔。    console=True

*** Test Cases ***
採集 lcd_a 按鈕影像
    [Documentation]    執行 lcd_a 的五步驟採集流程
    [Tags]    taipei_lab    lcd    collect    lcd_a
    執行 LCD 按鈕影像採集流程    lcd_a

採集 lcd_b 按鈕影像
    [Documentation]    執行 lcd_b 的五步驟採集流程
    [Tags]    taipei_lab    lcd    collect    lcd_b
    執行 LCD 按鈕影像採集流程    lcd_b

採集 lcd_left 按鈕影像
    [Tags]    taipei_lab    lcd    collect    lcd_left
    執行 LCD 按鈕影像採集流程    lcd_left

採集 lcd_right 按鈕影像
    [Tags]    taipei_lab    lcd    collect    lcd_right
    執行 LCD 按鈕影像採集流程    lcd_right
