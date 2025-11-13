*** Settings ***
Documentation    Multi-Light Array Detection Keywords - Gherkin Style
...              多燈號陣列檢測關鍵字集 - Gherkin 風格
...
...              This resource file provides Gherkin-style keywords for multi-light array detection.
...              It uses the MultiLightKeywords Python library for implementation.
...
...              此資源檔案提供 Gherkin 風格的多燈號陣列檢測關鍵字。
...              它使用 MultiLightKeywords Python 函式庫來實現。

# 主要匯入
Library          ../libraries/ipcam_light_detection/MultiLightKeywords.py    WITH NAME    MultiLightLib


*** Keywords ***
Given 多燈號陣列攝影機已連接到陣列
    [Documentation]    Given: Connects to the specified multi-light array camera.
    ...                中文說明: 連接到指定的多燈號陣列攝影機。
    [Arguments]    ${array_name}
    MultiLightLib.Given 多燈號陣列攝影機已連接    ${array_name}

When 偵測並記錄所有燈號狀態
    [Documentation]    When: Detects and logs the status of all lights in the array.
    ...                中文說明: 偵測並記錄所有燈號狀態。
    ${result}=    MultiLightLib.When 偵測並記錄所有燈號狀態
    Set Test Variable    \${MULTI_LIGHT_RESULT}    ${result}

When 偵測並記錄指定燈號狀態
    [Documentation]    When: Detects and logs the status of a single light.
    ...                中文說明: 偵測並記錄單一燈號的狀態。
    [Arguments]    ${light_key}
    ${status}=    MultiLightLib.When 偵測並記錄指定燈號狀態    ${light_key}
    Set Test Variable    \${LIGHT_STATUS}    ${status}

Then 燈號應該為開啟狀態
    [Documentation]    Then: Verifies that the specified light is on.
    ...                中文說明: 驗證指定燈號為開啟狀態。
    [Arguments]    ${light_key}
    MultiLightLib.Then 燈號應該為開啟狀態    ${light_key}

Then 燈號應該為關閉狀態
    [Documentation]    Then: Verifies that the specified light is off.
    ...                中文說明: 驗證指定燈號為關閉狀態。
    [Arguments]    ${light_key}
    MultiLightLib.Then 燈號應該為關閉狀態    ${light_key}

Then 燈號的亮度等級應該為指定值
    [Documentation]    Then: Verifies the brightness level of the specified light.
    ...                中文說明: 驗證指定燈號的亮度等級。
    [Arguments]    ${light_key}    ${expected_level}
    MultiLightLib.Then 燈號亮度等級應該為指定值    ${light_key}    ${expected_level}

Then 開啟的燈號數量應該為指定值
    [Documentation]    Then: Verifies the number of lights that are on.
    ...                中文說明: 驗證開啟的燈號數量。
    [Arguments]    ${expected_count}
    MultiLightLib.Then 開啟燈號數量應該為指定值    ${expected_count}

Then 關閉的燈號數量應該為指定值
    [Documentation]    Then: Verifies the number of lights that are off.
    ...                中文說明: 驗證關閉的燈號數量。
    [Arguments]    ${expected_count}
    MultiLightLib.Then 關閉燈號數量應該為指定值    ${expected_count}

When 將標註的陣列影像儲存到指定路徑
    [Documentation]    When: Saves the annotated array image.
    ...                中文說明: 儲存標註的陣列影像。
    [Arguments]    ${file_path}
    MultiLightLib.When 儲存標註陣列影像到指定路徑    ${file_path}

When 等待指定燈號開啟
    [Documentation]    When: Waits for a specific light to turn on.
    ...                中文說明: 等待指定燈號開啟。
    [Arguments]    ${light_key}    ${timeout}=30
    MultiLightLib.When 等待指定燈號開啟    ${light_key}    ${timeout}

When 等待指定燈號關閉
    [Documentation]    When: Waits for a specific light to turn off.
    ...                中文說明: 等待指定燈號關閉。
    [Arguments]    ${light_key}    ${timeout}=30
    MultiLightLib.When 等待指定燈號關閉    ${light_key}    ${timeout}

And 陣列攝影機已斷開連接
    [Documentation]    And: Disconnects the array camera.
    ...                中文說明: 斷開陣列攝影機連接。
    MultiLightLib.And 陣列攝影機已斷開連接
