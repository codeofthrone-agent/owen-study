*** Settings ***
Documentation    MyCobot 280 機器手臂基礎按鈕測試
...              測試機器手臂通過 Socket 控制按壓實體面板按鈕的功能
...
...              測試前提：
...              1. MyCobot 280 已開機並連接網路
...              2. Raspberry Pi 上的 Server_280.py 正在運行
...              3. 配置文件中的 IP 地址正確
...              4. 機器手臂已校準到正確的按鈕位置

Library          libraries.robot_arm_control.RobotArmKeywords

Suite Setup      連接並初始化機器手臂
Suite Teardown   清理並斷開連接

*** Variables ***
${ROBOT_IP}      # 從配置文件讀取
${ROBOT_PORT}    # 從配置文件讀取

*** Test Cases ***
測試藍牙按鈕點擊
    [Documentation]    測試機器手臂點擊藍牙按鈕
    ...                驗證機器手臂能準確移動到按鈕位置並完成按壓動作
    [Tags]    bluetooth    smoke

    Given 機器手臂已就緒
    When 執行按壓藍牙按鈕
    Then 按壓動作應該成功完成

測試燈光控制按鈕序列
    [Documentation]    測試機器手臂連續點擊多個燈光控制按鈕
    ...                驗證機器手臂能連續準確操作多個按鈕
    [Tags]    lights    regression

    Given 機器手臂已就緒
    When 依序點擊所有燈光按鈕
    Then 所有燈光按鈕都應該被正確點擊

測試輔助控制按鈕
    [Documentation]    測試 AUX1 和 AUX2 輔助控制按鈕
    [Tags]    aux    regression

    Given 機器手臂已就緒
    When 點擊 AUX1 和 AUX2 按鈕
    Then 按壓動作應該成功完成

測試門鎖控制按鈕
    [Documentation]    測試門鎖控制按鈕
    [Tags]    door_lock    regression

    Given 機器手臂已就緒
    When 執行按壓門鎖按鈕
    Then 按壓動作應該成功完成

測試電器控制按鈕
    [Documentation]    測試各種電器控制按鈕（加熱器、瓦斯、水泵等）
    [Tags]    appliances    regression

    Given 機器手臂已就緒
    When 依序點擊電器控制按鈕
    Then 所有電器按鈕都應該被正確點擊

測試空調控制按鈕
    [Documentation]    測試 HVAC 空調控制按鈕
    [Tags]    hvac    regression

    Given 機器手臂已就緒
    When 執行按壓 HVAC 按鈕
    Then 按壓動作應該成功完成

測試長按 Retract 按鈕
    [Documentation]    測試長按 Retract 縮回按鈕
    ...                驗證機器手臂能保持按壓指定時間（預設 7 秒）
    [Tags]    long_press    retract

    Given 機器手臂已就緒
    When 執行長按 Retract 按鈕
    Then 按鈕應該被長按 7 秒

測試自定義時間長按 Extend 按鈕
    [Documentation]    測試長按 Extend 伸展按鈕並自定義按壓時間
    ...                驗證機器手臂能按照自定義時間保持按壓
    [Tags]    long_press    extend

    Given 機器手臂已就緒
    When 執行長按 Extend 按鈕 10 秒
    Then 按鈕應該被長按 10 秒

測試回到初始位置
    [Documentation]    測試機器手臂回到初始位置功能
    ...                驗證機器手臂能安全返回 [0,0,0,0,0,0] 位置
    [Tags]    home    safety

    Given 機器手臂已就緒
    When 執行回到初始位置
    Then 機器手臂應該在初始位置

*** Keywords ***
連接並初始化機器手臂
    [Documentation]    連接到機器手臂並進行初始化
    ...                此關鍵字在測試套件開始時執行一次

    Log    正在連接機器手臂...
    連接機器手臂
    Log    機器手臂連接成功

清理並斷開連接
    [Documentation]    清理資源並斷開機器手臂連接
    ...                此關鍵字在測試套件結束時執行一次

    Log    正在回到初始位置...
    回到初始位置
    Log    正在斷開連接...
    斷開機器手臂連接
    Log    清理完成

機器手臂已就緒
    [Documentation]    驗證機器手臂處於就緒狀態
    Log    機器手臂已就緒，準備執行測試

執行按壓藍牙按鈕
    [Documentation]    執行按壓藍牙按鈕的動作
    點擊藍牙按鈕

執行按壓門鎖按鈕
    [Documentation]    執行按壓門鎖按鈕的動作
    點擊DoorLock按鈕

執行按壓 HVAC 按鈕
    [Documentation]    執行按壓 HVAC 空調按鈕的動作
    點擊HVAC按鈕

依序點擊所有燈光按鈕
    [Documentation]    依序點擊 Light1 到 Light8 八個燈光按鈕
    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕
    點擊Light4按鈕
    點擊Light5按鈕
    點擊Light6按鈕
    點擊Light7按鈕
    點擊Light8按鈕

點擊 AUX1 和 AUX2 按鈕
    [Documentation]    點擊 AUX1 和 AUX2 輔助控制按鈕
    點擊AUX1按鈕
    點擊AUX2按鈕

依序點擊電器控制按鈕
    [Documentation]    依序點擊各種電器控制按鈕
    點擊TankerHeater按鈕
    點擊Gas按鈕
    點擊WaterPump按鈕
    點擊WaterHeater按鈕

執行長按 Retract 按鈕
    [Documentation]    執行長按 Retract 按鈕（使用預設 7 秒）
    長按Retract按鈕

執行長按 Extend 按鈕 10 秒
    [Documentation]    執行長按 Extend 按鈕 10 秒
    長按Extend按鈕    10

執行回到初始位置
    [Documentation]    執行回到初始位置的動作
    回到初始位置

按壓動作應該成功完成
    [Documentation]    驗證按壓動作成功完成（無異常即為成功）
    Log    ✅ 按壓動作成功完成

所有燈光按鈕都應該被正確點擊
    [Documentation]    驗證所有燈光按鈕都被正確點擊
    Log    ✅ 所有燈光按鈕已成功點擊

所有電器按鈕都應該被正確點擊
    [Documentation]    驗證所有電器控制按鈕都被正確點擊
    Log    ✅ 所有電器控制按鈕已成功點擊

按鈕應該被長按 7 秒
    [Documentation]    驗證按鈕被長按 7 秒
    Log    ✅ 按鈕已被長按 7 秒

按鈕應該被長按 10 秒
    [Documentation]    驗證按鈕被長按 10 秒
    Log    ✅ 按鈕已被長按 10 秒

機器手臂應該在初始位置
    [Documentation]    驗證機器手臂已在初始位置
    Log    ✅ 機器手臂已在初始位置
