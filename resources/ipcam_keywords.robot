*** Settings ***
Documentation    IP 攝影機燈光偵測關鍵字庫
...              此檔案包含 IP 攝影機燈光偵測的 BDD 風格關鍵字。
...              支援攝影機連接、影像處理和燈光狀態檢測功能。
...              
...              主要功能:
...              - 連接到 IP 攝影機並設定環境
...              - 擷取和儲存攝影機影像
...              - 檢測和驗證燈光狀態
...              - 分析燈光亮度變化
...              
...              使用智慧匯入機制，支援模組匯入和檔案匯入兩種方式。

Library          ../libraries/ipcam_light_detection/IPCamKeywords.py

*** Keywords ***
Given IP 攝影機 "${camera_name}" 已在 "${environment}" 環境中連接
    [Documentation]    Given: Connects to the specified IP camera in a given environment.
    ...                中文說明: 在指定環境中連接到指定的 IP 攝影機。
    [Arguments]    ${camera_name}    ${environment}
    Given IP 攝影機已連接到攝影機    ${environment}    ${camera_name}

When 用戶請求儲存當前攝影機影像到 "${file_path}"
    [Documentation]    When: Saves the current camera image to the specified file path.
    ...                中文說明: 當用戶請求時，儲存當前攝影機影像到指定檔案路徑。
    [Arguments]    ${file_path}
    When 儲存當前攝影機影像到指定路徑    ${file_path}

When 用戶等待燈光變為開啟狀態
    [Documentation]    When: Waits for the light to turn on within a default timeout.
    ...                中文說明: 當用戶等待時，直到燈光變為開啟狀態。
    [Arguments]    ${timeout}=30
    When 等待燈光開啟指定秒數    ${timeout}

When 用戶等待燈光變為關閉狀態
    [Documentation]    When: Waits for the light to turn off within a default timeout.
    ...                中文說明: 當用戶等待時，直到燈光變為關閉狀態。
    [Arguments]    ${timeout}=30
    When 等待燈光關閉指定秒數    ${timeout}

Then 燈光狀態應該為 "開啟"
    [Documentation]    Then: Verifies that the light is currently on.
    ...                中文說明: 驗證目前燈光為開啟狀態。
    Then 燈光應該為開啟狀態

Then 燈光狀態應該為 "關閉"
    [Documentation]    Then: Verifies that the light is currently off.
    ...                中文說明: 驗證目前燈光為關閉狀態。
    Then 燈光應該為關閉狀態

Then 燈光亮度應該高於 "${expected_brightness}"
    [Documentation]    Then: Checks the current brightness and verifies it is greater than the expected value.
    ...                中文說明: 驗證目前燈光亮度高於指定值。
    [Arguments]    ${expected_brightness}
    ${brightness}=    When 檢查當前燈光亮度
    Then 亮度應該大於指定值    ${expected_brightness}

Then 燈光亮度應該低於 "${expected_brightness}"
    [Documentation]    Then: Checks the current brightness and verifies it is less than the expected value.
    ...                中文說明: 驗證目前燈光亮度低於指定值。
    [Arguments]    ${expected_brightness}
    ${brightness}=    When 檢查當前燈光亮度
    Then 亮度應該小於指定值    ${expected_brightness}

Then 燈光亮度應該介於 "${min_brightness}" 和 "${max_brightness}" 之間
    [Documentation]    Then: Checks the current brightness and verifies it is within the specified range.
    ...                中文說明: 驗證目前燈光亮度在指定範圍內。
    [Arguments]    ${min_brightness}    ${max_brightness}
    ${brightness}=    When 檢查當前燈光亮度
    Then 亮度應該在指定範圍內    ${min_brightness}    ${max_brightness}
