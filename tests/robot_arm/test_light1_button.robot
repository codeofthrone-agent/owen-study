*** Settings ***
Documentation    MyCobot 280 機器手臂 Light1 按鈕測試 - BDD 風格
...              測試機器手臂點擊 Light1 燈光按鈕的功能
...              採用 BDD (Gherkin) 風格進行測試設計

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

*** Variables ***
${BUTTON_NAME}    Light1

*** Test Cases ***
測試點擊 Light1 按鈕 - BDD 風格
    [Documentation]    
    ...    此測試案例展示如何使用 BDD 語法測試機器手臂點擊 Light1 按鈕。
    ...    
    ...    測試流程：
    ...    1. Given: 確認機器手臂已正確連接到控制面板
    ...    2. When: 用戶透過機器手臂開啟第 1 號燈光
    ...    3. Then: 機器手臂操作應該成功完成
    ...    4. And: 確認系統記錄了操作結果
    [Tags]    robot_arm    light1    smoke    bdd

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂開啟第 "1" 號燈光
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Light1 燈光已開啟" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程

*** Keywords ***
# 這個文件不再需要自定義關鍵字，因為所有功能都由 BDD 關鍵字提供