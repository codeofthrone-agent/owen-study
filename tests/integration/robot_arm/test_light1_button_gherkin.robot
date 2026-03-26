*** Settings ***
Documentation    MyCobot 280 機器手臂 Light1 按鈕測試 - BDD 風格（Gherkin 版本）
...              測試機器手臂點擊 Light1 燈光按鈕的功能
...              採用 BDD (Gherkin) 風格進行測試設計

Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

*** Variables ***
${BUTTON_NAME}    Light1
${LIGHT_NUMBER}   1

*** Test Cases ***
測試點擊 Light1 按鈕 - 完整 BDD 流程
    [Documentation]    
    ...    此測試案例展示如何使用完整的 BDD 語法測試機器手臂點擊 Light1 按鈕。
    ...    
    ...    BDD 測試流程：
    ...    1. Given: 機器手臂已正確連接到控制面板並處於待命狀態
    ...    2. When: 用戶透過機器手臂開啟第 1 號燈光
    ...    3. Then: 機器手臂操作應該成功完成
    ...    4. And: 控制面板顯示燈光狀態變化
    ...    5. And: 機器手臂返回待命位置並記錄操作歷程
    [Tags]    robot_arm    light1    smoke    bdd    gherkin

    Given 機器手臂已正確連接到控制面板
    Given 機器手臂系統處於待命狀態
    Given 控制面板電源狀態為 "ON"
    When 用戶透過機器手臂開啟第 "${LIGHT_NUMBER}" 號燈光
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Light1 燈光已開啟" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

測試多重燈光控制序列
    [Documentation]    
    ...    測試案例：連續控制多個燈光按鈕
    ...    驗證機器手臂能夠連續準確操作多個燈光控制
    [Tags]    robot_arm    lights    regression    sequence

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂開啟第 "1" 號燈光
    When 用戶透過機器手臂開啟第 "2" 號燈光  
    When 用戶透過機器手臂開啟第 "1" 號燈光
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "燈光控制序列完成" 狀態
    And 機器手臂應該返回待命位置

*** Keywords ***
# 此文件使用標準 BDD 關鍵字，不需要自定義關鍵字
# 所有功能都由 RobotArmKeywords.py 中的 BDD 關鍵字提供