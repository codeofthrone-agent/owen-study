*** Settings ***
Documentation    機器手臂控制 - 完整 BDD 風格測試案例
...
...    採用雙層架構設計（Voice Control 模式），所有測試案例遵循 Gherkin 語法。
...    此檔案展示如何使用新的 BDD 關鍵字進行機器手臂控制測試。
...
...    測試範圍：
...    - 單一燈光控制（8 個燈光按鈕）
...    - 藍牙連接切換
...    - 設備啟動控制（熱水器、空調、瓦斯等）
...    - 長按按鈕操作（Retract/Extend）
...    - 錯誤處理與邊界條件
...
...    架構說明：
...    - 直接使用 Python Library 中的 @keyword 定義的 BDD 關鍵字
...    - 不需要額外的 Resource 檔案（雙層架構）
...    - 與 test_asrpro_commands.robot 模式一致

Library          libraries.robot_arm_control.RobotArmKeywords
Library          DateTime

Suite Setup      連接機器手臂    # 傳統關鍵字（連接管理）
Suite Teardown   斷開機器手臂連接    # 傳統關鍵字（連接管理）

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
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    # TODO light1 點及是否成功 需要檢查 log
    When 用戶透過機器手臂開啟第 "1" 號燈光
    When 用戶透過機器手臂開啟第 "2" 號燈光
    When 用戶透過機器手臂開啟第 "3" 號燈光
    When 用戶透過機器手臂開啟第 "4" 號燈光

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Light1 開啟" 狀態
    And 機器手臂應該返回待命位置    50
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂批次開啟多個燈光
    [Documentation]
    ...    驗證機器手臂能夠連續按壓多個燈光按鈕。
    ...    測試範圍：Light1 ~ Light8 共 8 個燈光。
    [Tags]    robot_arm    light_control    batch

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"

    # 開啟所有燈光
    FOR    ${light_number}    IN RANGE    1    9
        When 用戶透過機器手臂開啟第 "${light_number}" 號燈光
        Then 機器手臂操作應該成功完成
        And 機器手臂應該返回待命位置
        Log    ✓ Light${light_number} 開啟成功
    END

    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂切換藍牙連接
    [Documentation]
    ...    驗證機器手臂能夠成功按壓藍牙按鈕並切換連接狀態。
    ...
    ...    藍牙狀態切換：
    ...    - 第一次按壓：開啟藍牙 / 開始配對
    ...    - 第二次按壓：關閉藍牙 / 中斷連接
    [Tags]    robot_arm    bluetooth    connectivity

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂切換藍牙連接

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "藍牙已啟動" 狀態
    And 機器手臂應該返回待命位置 50
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂啟動熱水器設備
    [Documentation]
    ...    驗證機器手臂能夠成功按壓熱水器按鈕並啟動設備。
    ...
    ...    支援的設備類型：
    ...    - 熱水器 (Water Heater)
    ...    - 空調 (HVAC)
    ...    - 瓦斯 (Gas)
    ...    - 水泵 (Water Pump)
    ...    - 水箱加熱器 (Tanker Heater)
    ...    - 門鎖 (Door Lock)
    ...    - AUX1, AUX2
    [Tags]    robot_arm    device_control    water_heater

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂啟動 "熱水器" 設備

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "熱水器已啟動" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂批次啟動多個設備
    [Documentation]
    ...    驗證機器手臂能夠連續啟動多個設備。
    ...    測試設備：熱水器、空調、瓦斯、水泵
    [Tags]    robot_arm    device_control    batch

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"

    # 批次啟動設備
    FOR    ${device}    IN    熱水器    空調    瓦斯    水泵
        When 用戶透過機器手臂啟動 "${device}" 設備
        Then 機器手臂操作應該成功完成
        And 機器手臂應該返回待命位置
        Log    ✓ ${device} 設備啟動成功
    END

    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂長按 Retract 按鈕
    [Documentation]
    ...    驗證機器手臂能夠執行長按操作（按住 3 秒）。
    ...
    ...    長按功能用途：
    ...    - Retract（縮回）：收回特定機構或執行特殊功能
    ...    - Extend（伸展）：延伸特定機構或執行特殊功能
    ...
    ...    長按時間：通常為 2-5 秒
    [Tags]    robot_arm    long_press    retract

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂長按 "縮回" 按鈕 "3.0" 秒

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Retract 執行完成" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂長按 Extend 按鈕
    [Documentation]
    ...    驗證機器手臂能夠執行長按 Extend 操作（按住 5 秒）。
    [Tags]    robot_arm    long_press    extend

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    When 用戶透過機器手臂長按 "伸展" 按鈕 "5.0" 秒

    Then 機器手臂操作應該成功完成
    Then 控制面板應該顯示 "Extend 執行完成" 狀態
    And 機器手臂應該返回待命位置
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試複雜操作序列 - 完整系統啟動流程
    [Documentation]
    ...    驗證機器手臂能夠執行完整的系統啟動流程。
    ...
    ...    操作序列：
    ...    1. 開啟藍牙連接
    ...    2. 啟動熱水器
    ...    3. 啟動空調
    ...    4. 開啟 Light1 照明
    ...    5. 開啟 Light2 照明
    ...
    ...    這個測試模擬真實的系統啟動場景。
    [Tags]    robot_arm    complex_sequence    integration

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"
    Given 機器手臂系統處於待命狀態

    # 步驟 1: 開啟藍牙
    When 用戶透過機器手臂切換藍牙連接
    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置
    Log    ✓ 步驟 1: 藍牙連接已啟動

    # 步驟 2: 啟動熱水器
    When 用戶透過機器手臂啟動 "熱水器" 設備
    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置
    Log    ✓ 步驟 2: 熱水器已啟動

    # 步驟 3: 啟動空調
    When 用戶透過機器手臂啟動 "空調" 設備
    Then 機器手臂操作應該成功完成
    And 機器手臂應該返回待命位置
    Log    ✓ 步驟 3: 空調已啟動

    # 步驟 4-5: 開啟照明
    FOR    ${light_number}    IN    1    2
        When 用戶透過機器手臂開啟第 "${light_number}" 號燈光
        Then 機器手臂操作應該成功完成
        And 機器手臂應該返回待命位置
        Log    ✓ 步驟 ${light_number + 3}: Light${light_number} 已開啟
    END

    # 最終驗證
    Then 控制面板應該顯示 "系統啟動完成" 狀態
    And 系統應該記錄完整操作歷程

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試錯誤處理 - 無效的燈光編號
    [Documentation]
    ...    驗證系統能夠正確處理無效的燈光編號輸入。
    ...
    ...    有效範圍：1-8
    ...    測試邊界：0, 9, -1
    [Tags]    robot_arm    error_handling    boundary

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"

    # 測試無效編號應該拋出異常
    Run Keyword And Expect Error    ValueError: 燈光編號必須在 1-8 之間*
    ...    When 用戶透過機器手臂開啟第 "9" 號燈光

    Log    ✓ 系統正確拒絕無效的燈光編號

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試錯誤處理 - 無效的設備名稱
    [Documentation]
    ...    驗證系統能夠正確處理不支援的設備名稱。
    [Tags]    robot_arm    error_handling

    Given 機器手臂已正確連接到控制面板
    Given 控制面板電源狀態為 "開啟"

    # 測試無效設備名稱應該拋出異常
    Run Keyword And Expect Error    ValueError: 未知的設備名稱*
    ...    When 用戶透過機器手臂啟動 "不存在的設備" 設備

    Log    ✓ 系統正確拒絕無效的設備名稱

    [Teardown]    And 暫存檔案應該正確清理

Scenario: 測試機器手臂狀態驗證
    [Documentation]
    ...    驗證機器手臂能夠正確檢測和報告待命狀態。
    ...
    ...    待命狀態定義：
    ...    - 所有關節角度接近初始位置 [0, 0, 0, 0, 0, 0]
    ...    - 容許誤差：±5 度
    [Tags]    robot_arm    status_check

    Given 機器手臂已正確連接到控制面板

    # 確保機器手臂在初始位置
    回到初始位置

    # 驗證待命狀態
    Given 機器手臂系統處於待命狀態

    Log    ✓ 機器手臂狀態驗證成功

    [Teardown]    And 暫存檔案應該正確清理

*** Keywords ***
# 以下為簡化的輔助關鍵字（非 BDD 風格）
# 主要測試案例應使用上述的 BDD 關鍵字

驗證測試環境
    [Documentation]    驗證測試環境是否正確設置
    Log    檢查機器手臂連接...
    ${is_connected}=    Run Keyword And Return Status    Given 機器手臂系統處於待命狀態
    Should Be True    ${is_connected}    msg=機器手臂未正確連接

記錄測試結果
    [Documentation]    記錄測試執行結果到日誌
    [Arguments]    ${test_name}    ${result}
    ${timestamp}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Log    測試案例: ${test_name}
    Log    執行時間: ${timestamp}
    Log    測試結果: ${result}

*** Comments ***
使用範例說明：

1. 單一按鈕測試：
   - 使用 "Scenario: 測試機器手臂開啟第 1 號燈光" 作為模板
   - 修改燈光編號或設備名稱即可

2. 批次操作測試：
   - 使用 FOR 迴圈遍歷多個目標
   - 參考 "測試機器手臂批次開啟多個燈光" 範例

3. 複雜序列測試：
   - 使用多個 When-Then-And 組合
   - 參考 "測試複雜操作序列" 範例

4. 錯誤處理測試：
   - 使用 "Run Keyword And Expect Error" 捕獲預期異常
   - 驗證系統邊界條件

5. 執行特定測試：
   robot --test "Scenario: 測試機器手臂開啟第 1 號燈光" tests/robot_arm/test_robot_arm_bdd_complete.robot

6. 執行特定標籤：
   robot --include smoke tests/robot_arm/test_robot_arm_bdd_complete.robot

7. 產生詳細報告：
   robot --outputdir results/robot_arm --loglevel DEBUG tests/robot_arm/test_robot_arm_bdd_complete.robot

架構說明：
- 此檔案採用 Voice Control 模式（雙層架構）
- 直接使用 Python Library 中定義的 @keyword BDD 關鍵字
- 不需要額外的 Resource 檔案（與 test_asrpro_commands.robot 一致）
- 所有關鍵字遵循 Gherkin 語法（Given-When-Then-And）
- 所有關鍵字名稱使用中文
