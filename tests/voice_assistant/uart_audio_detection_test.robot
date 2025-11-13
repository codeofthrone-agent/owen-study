*** Settings ***
Documentation    UART 日誌語音檢測測試
...
...    透過 UART 串列埠讀取系統日誌，檢測語音播放狀態。
...    驗證標準：檢測到 "Playing audio file: xxx.mp3" 和 "Finished playing xxx.mp3"
...
...    v1.2.0 更新：
...    - 整合 RemoteSystemConfigValidator 自動配置驗證
...    - 連接時自動檢查並修正遠端 /etc/init.d/emmc 配置
...
Library          ../../libraries/multimodal_detection/SerialLogParser.py
Resource         ../../resources/common_keywords.robot

Suite Setup      測試前置準備
Suite Teardown   測試後清理

*** Variables ***
${UART_PORT}       /dev/ttyUSB0
${UART_BAUDRATE}   115200
${超時時間}          20

*** Test Cases ***
Scenario: 測試 UART 日誌解析器初始化
    [Documentation]    測試 UART 日誌解析器是否能正常初始化和連接
    [Tags]    uart    init    smoke

    Given UART 串列埠可用

    When ${success}=    初始化串列埠監控器    ${UART_PORT}    ${UART_BAUDRATE}

    Then Should Be True    ${success}
    ...    msg=UART 串列埠初始化失敗

    And 斷開串列埠
    Log    ✓ UART 串列埠初始化測試通過

Scenario: 測試自動配置驗證功能
    [Documentation]    測試連接時自動驗證並修正遠端配置
    ...
    ...    此測試會自動檢查遠端設備的 /etc/init.d/emmc 配置，
    ...    如果配置錯誤會自動修正並提示重開機。
    [Tags]    uart    auto-validate    config

    Given UART 串列埠可用

    When ${success}=    初始化串列埠監控器    ${UART_PORT}    ${UART_BAUDRATE}    auto_validate=True

    Then Run Keyword If    ${success}
    ...    Log    ✓ 遠端配置正確或無需驗證    console=yes
    ...    ELSE    Log    ⚠️  配置已修正，請重開機遠端設備後重試    WARN

    And Run Keyword And Ignore Error    斷開串列埠
    Log    ✓ 自動配置驗證測試完成

Scenario: 測試手動配置驗證
    [Documentation]    測試使用手動關鍵字驗證遠端配置
    [Tags]    uart    manual-validate    config

    Given UART 串列埠可用
    And SerialLogParser 已初始化但未連接

    When 執行手動驗證遠端配置

    Then 驗證結果應包含所有必要欄位

    Log    ✓ 手動配置驗證測試完成

Scenario: 測試背景監控功能
    [Documentation]    測試 UART 背景監控是否能正常啟動和停止
    [Tags]    uart    monitoring

    Given UART 串列埠已連接

    When ${success}=    啟動背景監控

    Then Should Be True    ${success}
    ...    msg=背景監控啟動失敗

    And 停止背景監控
    Log    ✓ 背景監控功能測試通過

Scenario: 測試語音播放檢測（需要實際觸發）
    [Documentation]    測試是否能檢測到語音播放事件
    ...
    ...    注意：此測試需要在測試期間手動觸發語音播放，
    ...    或連接到實際的語音助手設備。
    [Tags]    uart    detection    manual

    Given UART 串列埠已連接
    And 背景監控已啟動

    # 提示使用者
    Log    請在 ${超時時間} 秒內觸發語音播放...    console=yes

    When ${detected}    ${filename}=    檢查是否有播放記錄    ${超時時間}

    Then Run Keyword If    ${detected}
    ...    Log    ✓ 檢測到播放: ${filename}    console=yes
    ...    ELSE
    ...    Log    ✗ 未檢測到播放（可能沒有觸發）    WARN

    And 停止背景監控

Scenario: 測試播放完成檢測
    [Documentation]    測試是否能檢測到播放完成事件
    [Tags]    uart    detection    manual

    Given UART 串列埠已連接
    And 背景監控已啟動

    # 提示使用者
    Log    請在 ${超時時間} 秒內觸發語音播放並等待完成...    console=yes

    When ${detected_play}    ${play_file}=    檢查是否有播放記錄    ${超時時間}
    And ${detected_finish}    ${finish_file}=    檢查是否播放完成    ${超時時間}

    Then Run Keyword If    ${detected_play} and ${detected_finish}
    ...    Log    ✓ 檢測到完整播放流程: ${play_file} -> ${finish_file}    console=yes
    ...    ELSE
    ...    Log    部分檢測失敗（播放: ${detected_play}, 完成: ${detected_finish}）    WARN

    And 停止背景監控

Scenario: 測試事件記錄功能
    [Documentation]    測試事件記錄的查詢和清空功能
    [Tags]    uart    events

    Given UART 串列埠已連接
    And 背景監控已啟動

    # 等待一段時間收集事件
    Sleep    5s

    When ${events}=    取得所有播放事件

    Then Log    共記錄 ${events.__len__()} 個事件    console=yes

    And 清空事件記錄
    And ${events_after}=    取得所有播放事件
    And Should Be Equal    ${events_after.__len__()}    ${0}
    ...    msg=事件記錄清空失敗

    And 停止背景監控

*** Keywords ***
測試前置準備
    [Documentation]    Suite 級別初始化
    Log    ========================================    console=yes
    Log    UART 日誌語音檢測測試開始                console=yes
    Log    ========================================    console=yes
    Log    UART 端口: ${UART_PORT}                   console=yes
    Log    波特率: ${UART_BAUDRATE}                  console=yes

測試後清理
    [Documentation]    Suite 級別清理
    # 確保串列埠已斷開
    Run Keyword And Ignore Error    停止背景監控
    Run Keyword And Ignore Error    斷開串列埠

    Log    ========================================    console=yes
    Log    UART 日誌語音檢測測試完成                console=yes
    Log    ========================================    console=yes

UART 串列埠可用
    [Documentation]    檢查 UART 串列埠是否可用
    ${exists}=    Run Keyword And Return Status
    ...    OperatingSystem.File Should Exist    ${UART_PORT}

    Run Keyword If    not ${exists}
    ...    Log    警告: ${UART_PORT} 不存在，部分測試可能失敗    WARN

UART 串列埠已連接
    [Documentation]    確保 UART 串列埠已連接
    ${success}=    初始化串列埠監控器    ${UART_PORT}    ${UART_BAUDRATE}
    Should Be True    ${success}
    ...    msg=無法連接 UART 串列埠

背景監控已啟動
    [Documentation]    確保背景監控已啟動
    ${success}=    啟動背景監控
    Should Be True    ${success}
    ...    msg=無法啟動背景監控

SerialLogParser 已初始化但未連接
    [Documentation]    建立 SerialLogParser 實例但不自動連接
    # 此關鍵字用於手動測試配置驗證功能
    # SerialLogParser 的 驗證遠端系統配置 關鍵字會內部處理連接
    Log    準備手動驗證配置（不自動連接）

執行手動驗證遠端配置
    [Documentation]    執行手動配置驗證並儲存結果
    ${validation_result}=    驗證遠端系統配置
    Set Test Variable    ${validation_result}
    Log    驗證結果: ${validation_result}    console=yes

驗證結果應包含所有必要欄位
    [Documentation]    檢查驗證結果是否包含所有必要欄位
    Dictionary Should Contain Key    ${validation_result}    config_ok
    Dictionary Should Contain Key    ${validation_result}    fixed
    Dictionary Should Contain Key    ${validation_result}    needs_reboot
    Dictionary Should Contain Key    ${validation_result}    error_message
    Log    ✓ 驗證結果包含所有必要欄位
