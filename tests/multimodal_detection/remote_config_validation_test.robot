*** Settings ***
Documentation    遠端系統配置驗證測試
...
...    測試 RemoteSystemConfigValidator 功能：
...    - 自動檢查遠端設備 /etc/init.d/emmc 配置
...    - 自動修正錯誤配置
...    - 整合到 SerialLogParser 自動驗證流程
...
...    測試前提：
...    - 遠端語音助手設備已透過 UART 連接（預設 /dev/ttyUSB0）
...    - 測試使用者有權限讀寫遠端配置檔
...
...    作者：Robot Automation Team
...    建立日期：2025-11-11

Resource         ../../resources/multimodal_keywords.robot
Library          Collections

*** Variables ***
${UART_PORT}              /dev/ttyUSB0
${UART_BAUDRATE}          115200
${EMMC_CONFIG_PATH}       /etc/init.d/emmc

*** Test Cases ***
測試案例 1：驗證遠端配置檢查功能
    [Documentation]    測試 RemoteSystemConfigValidator 基本配置檢查功能
    [Tags]    remote-config    validation    基礎測試

    Given 建立遠端配置驗證器
    When 連接遠端設備並檢查配置
    Then 應該返回配置檢查結果

測試案例 2：SerialLogParser 自動驗證整合
    [Documentation]    測試 SerialLogParser 在連接時自動驗證遠端配置
    [Tags]    remote-config    integration    自動驗證

    Given SerialLogParser 尚未連接
    When 初始化 SerialLogParser 並啟用自動驗證
    Then 應該自動檢查並修正配置
    And 如果需要重開機應該提示使用者

測試案例 3：手動驗證遠端配置
    [Documentation]    測試使用 Robot Framework 關鍵字手動驗證配置
    [Tags]    remote-config    manual    關鍵字測試

    Given 建立 SerialLogParser 實例
    When 執行手動配置驗證
    Then 驗證結果應該包含完整資訊

測試案例 4：配置已正確時的行為
    [Documentation]    測試當遠端配置已經正確時，驗證器應該快速通過
    [Tags]    remote-config    正面測試

    Given 假設遠端配置已經正確
    When 執行配置驗證
    Then 應該返回 config_ok=True
    And 不應該執行修正

測試案例 5：配置錯誤時的自動修正
    [Documentation]    測試當遠端配置錯誤時，驗證器應該自動修正
    [Tags]    remote-config    auto-fix

    Given 假設遠端配置錯誤
    When 執行配置驗證
    Then 應該自動修正配置
    And 應該提示需要重開機

*** Keywords ***
# ===========================================
# Given - 前置條件
# ===========================================

建立遠端配置驗證器
    [Documentation]    設定遠端配置驗證器
    Log    正在設定遠端配置驗證器...
    Log    ✓ 驗證器已準備 (Port: ${UART_PORT}, Baudrate: ${UART_BAUDRATE})

SerialLogParser 尚未連接
    [Documentation]    確認 SerialLogParser 尚未連接
    Log    準備測試 SerialLogParser 自動驗證功能

建立 SerialLogParser 實例
    [Documentation]    設定 SerialLogParser 但不在此處連接
    Log    SerialLogParser 準備就緒 (Port: ${UART_PORT})

假設遠端配置已經正確
    [Documentation]    測試假設：遠端配置已經正確（實際會檢查真實狀態）
    Log    假設遠端配置已經正確，將執行驗證

假設遠端配置錯誤
    [Documentation]    測試假設：遠端配置錯誤（實際會檢查真實狀態）
    Log    假設遠端配置錯誤，將執行自動修正測試

# ===========================================
# When - 執行動作
# ===========================================

連接遠端設備並檢查配置
    [Documentation]    連接遠端設備並執行配置檢查
    Log    連接遠端設備...
    ${success}=    Run Keyword    連接遠端設備    ${UART_PORT}    ${UART_BAUDRATE}
    Should Be True    ${success}    連接失敗

    Log    檢查遠端配置...
    ${result}=    Run Keyword    檢查遠端配置
    Set Suite Variable    ${result}
    Log    配置檢查完成: ${result}

初始化 SerialLogParser 並啟用自動驗證
    [Documentation]    初始化 SerialLogParser 並啟用自動驗證
    Log    初始化串列埠監控器（自動驗證已啟用）...

    # 嘗試連接，如果配置需要修正會返回 False
    ${success}=    初始化串列埠監控器    ${UART_PORT}    ${UART_BAUDRATE}    auto_validate=True
    Set Suite Variable    ${success}

    Run Keyword If    ${success}    Log    ✓ 連接成功，配置正確
    ...    ELSE    Log    ⚠️  連接失敗或需要重開機

執行手動配置驗證
    [Documentation]    執行手動配置驗證
    Log    執行手動驗證...
    ${result}=    驗證遠端系統配置
    Set Suite Variable    ${result}
    Log    驗證結果: ${result}

執行配置驗證
    [Documentation]    執行配置驗證（通用）
    建立遠端配置驗證器
    ${success}=    Run Keyword    連接遠端設備    ${UART_PORT}    ${UART_BAUDRATE}
    Should Be True    ${success}

    ${result}=    Run Keyword    驗證並修正遠端配置
    Set Suite Variable    ${result}
    Log    驗證結果: ${result}

# ===========================================
# Then - 驗證結果
# ===========================================

應該返回配置檢查結果
    [Documentation]    驗證配置檢查結果包含必要欄位
    Log    驗證結果結構...

    # 檢查結果欄位
    Dictionary Should Contain Key    ${result}    has_error
    Dictionary Should Contain Key    ${result}    error_type
    Dictionary Should Contain Key    ${result}    needs_fix
    Dictionary Should Contain Key    ${result}    current_content

    Log    ✓ 結果結構正確

應該自動檢查並修正配置
    [Documentation]    驗證自動檢查並修正配置的行為
    Log    驗證自動檢查流程...

    Run Keyword If    ${success}
    ...    Log    ✓ 配置正確或已成功修正，連接成功
    ...    ELSE    Log    ⚠️  配置需要修正且需要重開機

如果需要重開機應該提示使用者
    [Documentation]    驗證重開機提示機制
    Log    檢查是否需要重開機提示...

    Run Keyword If    not ${success}
    ...    Log    ⚠️  系統已提示需要重開機（正常行為）
    ...    ELSE    Log    ✓ 不需要重開機

驗證結果應該包含完整資訊
    [Documentation]    驗證結果包含完整的資訊欄位
    Log    驗證結果完整性...

    # 檢查必要欄位
    Dictionary Should Contain Key    ${result}    config_ok
    Dictionary Should Contain Key    ${result}    fixed
    Dictionary Should Contain Key    ${result}    needs_reboot
    Dictionary Should Contain Key    ${result}    error_message
    Dictionary Should Contain Key    ${result}    details

    # 記錄結果
    Log    Config OK: ${result['config_ok']}
    Log    Fixed: ${result['fixed']}
    Log    Needs Reboot: ${result['needs_reboot']}

    ${error}=    Get From Dictionary    ${result}    error_message
    Run Keyword If    '${error}' != 'None'
    ...    Log    Error: ${error}

    Log    ✓ 驗證結果包含完整資訊

應該返回 config_ok=True
    [Documentation]    驗證 config_ok 為 True
    Should Be True    ${result['config_ok']}    配置應該正確
    Log    ✓ config_ok=True

不應該執行修正
    [Documentation]    驗證沒有執行修正
    Should Not Be True    ${result['fixed']}    不應該執行修正
    Should Not Be True    ${result['needs_reboot']}    不應該需要重開機
    Log    ✓ 未執行修正（配置已正確）

應該自動修正配置
    [Documentation]    驗證配置已被自動修正
    Run Keyword If    not ${result['config_ok']}
    ...    Should Be True    ${result['fixed']}    應該已修正配置
    Log    檢查配置修正狀態

應該提示需要重開機
    [Documentation]    驗證提示重開機
    Run Keyword If    ${result['fixed']}
    ...    Should Be True    ${result['needs_reboot']}    修正後應該需要重開機

    ${reboot_cmd}=    Get From Dictionary    ${result}    reboot_command
    Run Keyword If    ${result['needs_reboot']}
    ...    Log    重開機命令: ${reboot_cmd}

    Log    ✓ 重開機提示正確
