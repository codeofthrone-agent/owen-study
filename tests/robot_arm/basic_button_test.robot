*** Settings ***
Documentation    MyCobot 280 機器手臂基礎按鈕測試
...              採用 BDD (Gherkin) 風格測試機器手臂通過 Socket 控制按壓實體面板按鈕的功能
...
...              測試前提：
...              1. MyCobot 280 已開機並連接網路
...              2. MyCobot 280 Jetson Nano 上的 Server_280.py 正在運行
...              3. 配置文件中的 IP 地址正確
...              4. 機器手臂已校準到正確的按鈕位置

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py

*** Variables ***
${ROBOT_IP}      # 從配置文件讀取
${ROBOT_PORT}    # 從配置文件讀取

*** Test Cases ***
測試藍牙按鈕點擊
    [Documentation]    測試機器手臂點擊藍牙按鈕
    ...                驗證機器手臂能準確移動到按鈕位置並完成按壓動作
    [Tags]    bluetooth    smoke

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂切換藍牙連接
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "藍牙已切換" 狀態
    And 機器手臂應該返回待命位置

測試燈光控制按鈕序列
    [Documentation]    測試機器手臂連續點擊多個燈光控制按鈕
    ...                驗證機器手臂能連續準確操作多個按鈕
    [Tags]    lights    regression

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂開啟第 "1" 號燈光
    When 用戶透過機器手臂開啟第 "2" 號燈光
    When 用戶透過機器手臂開啟第 "3" 號燈光
    When 用戶透過機器手臂開啟第 "4" 號燈光
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "所有燈光已開啟" 狀態
    And 機器手臂應該返回待命位置

測試輔助控制按鈕
    [Documentation]    測試 AUX1 和 AUX2 輔助控制按鈕
    [Tags]    aux    regression

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂啟動 "AUX1" 設備
    When 用戶透過機器手臂啟動 "AUX2" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "輔助設備已啟動" 狀態
    And 機器手臂應該返回待命位置

測試門鎖控制按鈕
    [Documentation]    測試門鎖控制按鈕
    [Tags]    door_lock    regression

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂啟動 "門鎖" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "門鎖已切換" 狀態
    And 機器手臂應該返回待命位置

測試電器控制按鈕
    [Documentation]    測試各種電器控制按鈕（加熱器、瓦斯、水泵等）
    [Tags]    appliances    regression

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂啟動 "水箱加熱器" 設備
    When 用戶透過機器手臂啟動 "瓦斯" 設備
    When 用戶透過機器手臂啟動 "水泵" 設備
    When 用戶透過機器手臂啟動 "熱水器" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "所有電器已啟動" 狀態
    And 機器手臂應該返回待命位置

測試空調控制按鈕
    [Documentation]    測試 HVAC 空調控制按鈕
    [Tags]    hvac    regression

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂啟動 "空調" 設備
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "空調已啟動" 狀態
    And 機器手臂應該返回待命位置

測試長按 Retract 按鈕
    [Documentation]    測試長按 Retract 縮回按鈕
    ...                驗證機器手臂能保持按壓指定時間（預設 7 秒）
    [Tags]    long_press    retract

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂長按 "縮回" 按鈕 "7" 秒
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "縮回動作完成" 狀態
    And 機器手臂應該返回待命位置

測試自定義時間長按 Extend 按鈕
    [Documentation]    測試長按 Extend 伸展按鈕並自定義按壓時間
    ...                驗證機器手臂能按照自定義時間保持按壓
    [Tags]    long_press    extend

    Given 機器手臂已正確連接到控制面板
    When 用戶透過機器手臂長按 "伸展" 按鈕 "10" 秒
    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "伸展動作完成" 狀態
    And 機器手臂應該返回待命位置

測試機器手臂待命狀態檢查
    [Documentation]    測試機器手臂待命狀態檢查功能
    ...                驗證機器手臂能正確檢查並返回初始位置
    [Tags]    home    safety

    Given 機器手臂已正確連接到控制面板
    Given 機器手臂系統處於待命狀態
    When 用戶透過機器手臂切換藍牙連接
    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程
    And 暫存檔案應該正確清理
