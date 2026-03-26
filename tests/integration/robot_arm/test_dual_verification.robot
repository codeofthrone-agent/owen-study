*** Settings ***
Documentation    面板燈號雙重驗證測試 (Dual Verification)
...              測試 YOLO + ROI 聯合驗證機制
Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

Suite Setup      Setup Suite Environment
Suite Teardown   Teardown Suite Environment

*** Keywords ***
Setup Suite Environment
    [Documentation]    初始化環境
    Given 測試環境設定為 "taipei_lab"
    Given 機器手臂已正確連接到控制面板

Teardown Suite Environment
    [Documentation]    清理環境
    Run Keyword And Ignore Error    And 機器手臂應該返回待命位置

*** Test Cases ***
Verify Dual Check Mechanism - Loose Mode (Default)
    [Documentation]    測試寬鬆模式 (YOLO OR ROI)
    [Tags]    dual_verification    loose
    
    # 測試 light1 (假設初始狀態為 OFF - 藍燈)
    Then 雙重驗證面板按鈕 "light1" 狀態應為 "off"
    
    # 測試 light2
    Then 雙重驗證面板按鈕 "light2" 狀態應為 "off"

Verify Dual Check Mechanism - Strict Mode
    [Documentation]    測試嚴格模式 (YOLO AND ROI)
    [Tags]    dual_verification    strict
    
    # 測試 light1 (嚴格模式)
    Then 雙重驗證面板按鈕 "light1" 狀態應為 "off" (模式: "strict")

Verify Dual Check Mechanism - Expect ON (Will Fail if OFF)
    [Documentation]    測試預期 ON 但實際 OFF 的情況 (應失敗)
    [Tags]    dual_verification    negative
    
    Run Keyword And Expect Error    *    Then 雙重驗證面板按鈕 "light1" 狀態應為 "on" (模式: "strict")
