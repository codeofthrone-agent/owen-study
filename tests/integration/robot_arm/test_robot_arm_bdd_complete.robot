*** Settings ***
Documentation    MyCobot 280 機器手臂控制 - 完整 BDD 風格測試案例
...
...              採用 BDD (Gherkin) 風格進行機器手臂控制測試。
...              此檔案展示如何使用新的 BDD 關鍵字進行機器手臂控制測試。
...
...              測試範圍：
...              - 單一燈光控制（8 個燈光按鈕）
...              - 藍牙連接切換
...              - 設備啟動控制（熱水器、空調、瓦斯等）
...              - 長按按鈕操作（Retract/Extend）
...              - 錯誤處理與邊界條件
...
...              架構說明：
...              - 直接使用 Python Library 中的 @keyword 定義的 BDD 關鍵字
...              - 每個測試案例完全獨立，自包含連接和清理
...              - 所有關鍵字遵循 Gherkin 語法（Given-When-Then-And）

Library          ../../../libraries/robot_arm_control/RobotArmKeywords.py
Library          DateTime

*** Variables ***
${ROBOT_ARM_HOST}    192.168.1.100
${ROBOT_ARM_PORT}    9000

*** Test Cases ***
Scenario: 測試機器手臂開啟第 1 號燈光
    [Documentation]
    ...    驗證機器手臂能夠成功按壓 Light1 按鈕並開啟燈光。
    ...
    ...    前置條件：
    ...    - 機器手臂已連接到控制面板
    ...    - 控制面板電源已開啟
    ...
    ...    測試步驟：
    ...    1. 確認機器手臂連接狀態和面板電源
    ...    2. 透過機器手臂按壓 Light1 按鈕
    ...    3. 驗證操作成功完成
    ...    4. 確認控制面板顯示燈光開啟狀態
    ...    5. 機器手臂返回待命位置
    [Tags]    robot_arm    light_control    smoke    bdd

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂開啟第 "1" 號燈光
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Light1 開啟" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂批次開啟多個燈光
    [Documentation]
    ...    驗證機器手臂能夠連續按壓多個燈光按鈕。
    ...    測試範圍：Light1 ~ Light4 共 4 個燈光。
    [Tags]    robot_arm    light_control    batch

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    
    # 開啟前4個燈光
    When 用戶透過機器手臂開啟第 "1" 號燈光
    When 用戶透過機器手臂開啟第 "2" 號燈光
    When 用戶透過機器手臂開啟第 "3" 號燈光
    When 用戶透過機器手臂開啟第 "4" 號燈光
    
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "多個燈光已開啟" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂切換藍牙連接
    [Documentation]
    ...    驗證機器手臂能夠成功按壓藍牙按鈕並切換連接狀態。
    [Tags]    robot_arm    bluetooth    connectivity

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂切換藍牙連接
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "藍牙已啟動" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂啟動熱水器設備
    [Documentation]
    ...    驗證機器手臂能夠成功按壓熱水器按鈕並啟動設備。
    [Tags]    robot_arm    device_control    water_heater

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂啟動 "熱水器" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "熱水器已啟動" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂批次啟動多個設備
    [Documentation]
    ...    驗證機器手臂能夠連續啟動多個設備。
    [Tags]    robot_arm    device_control    batch

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    When 用戶透過機器手臂啟動 "熱水器" 設備
    When 用戶透過機器手臂啟動 "空調" 設備
    When 用戶透過機器手臂啟動 "瓦斯" 設備
    When 用戶透過機器手臂啟動 "水泵" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "多個設備已啟動" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂長按 Retract 按鈕
    [Documentation]
    ...    驗證機器手臂能夠執行長按操作（按住 3 秒）。
    [Tags]    robot_arm    long_press    retract

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂長按 "縮回" 按鈕 "3" 秒
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "縮回執行完成" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂長按 Extend 按鈕
    [Documentation]
    ...    驗證機器手臂能夠執行長按 Extend 操作（按住 5 秒）。
    [Tags]    robot_arm    long_press    extend

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"  
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂長按 "伸展" 按鈕 "5" 秒
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "伸展執行完成" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試複雜操作序列 - 完整系統啟動流程
    [Documentation]
    ...    驗證機器手臂能夠執行完整的系統啟動流程。
    [Tags]    robot_arm    complex_sequence    integration

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "ON"
    Given 機器手臂系統處於待命狀態
    
    # 完整啟動序列
    When 用戶透過機器手臂切換藍牙連接
    When 用戶透過機器手臂啟動 "熱水器" 設備
    When 用戶透過機器手臂啟動 "空調" 設備
    When 用戶透過機器手臂開啟第 "1" 號燈光
    When 用戶透過機器手臂開啟第 "2" 號燈光
    
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "系統啟動完成" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理

Scenario: 測試機器手臂狀態驗證
    [Documentation]
    ...    驗證機器手臂能夠正確檢測和報告待命狀態。
    [Tags]    robot_arm    status_check

    Given 機器手臂已正確連接到控制面板
    Given 機器手臂系統處於待命狀態
    Then 機器手臂操作應該成功完成
    And 暫存檔案應該正確清理

*** Keywords ***
# 此文件使用標準 BDD 關鍵字，不需要額外的自定義關鍵字
# 所有功能都由 RobotArmKeywords.py 中的 BDD 關鍵字提供
