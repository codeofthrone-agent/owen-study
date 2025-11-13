*** Settings ***
Documentation    多燈號陣列檢測測試案例集
...
...              測試基於 IP Camera 的多燈號陣列檢測功能，專門用於紙箱分隔的燈泡陣列。
...
...              **測試範圍:**
...              - 陣列攝影機連接測試
...              - 單一燈號偵測測試
...              - 全陣列偵測測試
...              - 燈號狀態驗證測試
...              - 亮度等級判定測試
...              - 陣列狀態變化偵測測試
...              - 視覺化與調試測試
...
...              **環境需求:**
...              - IP Camera 需支援 RTSP 協議
...              - 需在 config/ipcam_config.yaml 中正確設定多燈號陣列配置
...              - 需安裝 opencv-python 套件
...              - 燈泡陣列需使用紙箱分隔以避免光線干擾
...
...              **測試環境:**
...              - 3x4 燈泡陣列（共 12 個燈泡）
...              - 紙箱格子分隔
...              - IP Camera 固定拍攝角度

Resource         ../../resources/multi_light_keywords.robot
Resource         ../../resources/common_keywords.robot

Suite Setup      多燈號測試套件初始化
Suite Teardown   多燈號測試套件清理

Test Tags        ipcam    multi_light    array_detection


*** Variables ***
${ARRAY_NAME}           default_array
${TEST_SCREENSHOT_DIR}  ${CURDIR}/../../results/screenshots/multi_light


*** Test Cases ***
測試案例 01: 連接多燈號陣列攝影機
    [Documentation]    驗證能夠成功連接到多燈號陣列攝影機
    ...
    ...    **前置條件:**
    ...    - IP Camera 已開啟並可連線
    ...    - RTSP 服務正常運作
    ...    - 陣列配置已在 config/ipcam_config.yaml 中定義
    ...
    ...    **測試步驟:**
    ...    1. 連接預設陣列攝影機
    ...    2. 擷取一幀影像驗證連線
    ...
    ...    **預期結果:**
    ...    - 成功連接攝影機
    ...    - 成功擷取影像
    [Tags]    smoke    connection

    Given 連接預設陣列攝影機
    When 擷取陣列影像
    Then Log    ✅ 陣列攝影機連接成功並可正常擷取影像


測試案例 02: 偵測所有燈號狀態
    [Documentation]    測試同時偵測所有燈號的狀態
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號（共 12 個）
    ...    3. 記錄每個燈號的亮度和狀態
    ...
    ...    **預期結果:**
    ...    - 成功偵測 12 個燈號
    ...    - 每個燈號都有亮度和狀態資訊
    [Tags]    detection    core

    Given 連接預設陣列攝影機
    When 偵測所有燈號並記錄
    Then 儲存陣列標註影像    test_all_lights.jpg


測試案例 03: 偵測單一燈號狀態
    [Documentation]    測試偵測單一指定燈號的狀態
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測燈泡 A1 (0_0) 的狀態
    ...    3. 驗證回傳資料包含必要欄位
    ...
    ...    **預期結果:**
    ...    - 成功偵測單一燈號
    ...    - 回傳資料包含亮度、狀態、等級等資訊
    [Tags]    detection    single_light

    Given 連接預設陣列攝影機
    When 擷取陣列影像
    ${狀態} =    And 偵測單一燈號並記錄    0_0

    Then Dictionary Should Contain Key    ${狀態}    brightness
    And Dictionary Should Contain Key    ${狀態}    is_on
    And Dictionary Should Contain Key    ${狀態}    brightness_level
    And Dictionary Should Contain Key    ${狀態}    name


測試案例 04: 驗證燈號開啟狀態
    [Documentation]    測試驗證指定燈號為開啟狀態
    ...
    ...    **前置條件:**
    ...    - 測試環境中燈泡 A1 (0_0) 已開啟
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測燈泡 A1
    ...    3. 驗證燈泡為開啟狀態
    ...
    ...    **預期結果:**
    ...    - 偵測到燈泡為開啟狀態
    ...    - 亮度高於開啟閾值
    ...
    ...    **注意:**
    ...    此測試案例需要確保燈泡 A1 實際為開啟狀態
    [Tags]    verification    light_on    manual

    Given 連接預設陣列攝影機
    When 擷取陣列影像
    Then 驗證燈號為開啟狀態    0_0


測試案例 05: 驗證燈號關閉狀態
    [Documentation]    測試驗證指定燈號為關閉狀態
    ...
    ...    **前置條件:**
    ...    - 測試環境中燈泡 C4 (2_3) 已關閉
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測燈泡 C4
    ...    3. 驗證燈泡為關閉狀態
    ...
    ...    **預期結果:**
    ...    - 偵測到燈泡為關閉狀態
    ...    - 亮度低於關閉閾值
    ...
    ...    **注意:**
    ...    此測試案例需要確保燈泡 C4 實際為關閉狀態
    [Tags]    verification    light_off    manual

    Given 連接預設陣列攝影機
    When 擷取陣列影像
    Then 驗證燈號為關閉狀態    2_3


測試案例 06: 驗證燈號亮度等級
    [Documentation]    測試驗證燈號的亮度等級判定
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號
    ...    3. 驗證每個燈號的亮度等級在合理範圍內
    ...
    ...    **預期結果:**
    ...    - 每個燈號都有明確的亮度等級（off, dim, medium, bright）
    [Tags]    verification    brightness_level

    Given 連接預設陣列攝影機
    ${結果} =    When 偵測所有燈號並記錄

    Then Log    驗證亮度等級判定正確性
    FOR    ${light_key}    IN    @{結果.keys()}
        ${燈號} =    Get From Dictionary    ${結果}    ${light_key}
        ${等級} =    Get From Dictionary    ${燈號}    brightness_level

        Should Be True
        ...    '${等級}' in ['off', 'dim', 'medium', 'bright']
        ...    msg=燈號 ${燈號}[name] 的亮度等級 '${等級}' 不在預期範圍內
    END


測試案例 07: 驗證陣列開啟數量
    [Documentation]    測試驗證陣列中開啟的燈號數量
    ...
    ...    **前置條件:**
    ...    - 已知陣列中有特定數量的燈號開啟
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號
    ...    3. 驗證開啟數量符合預期
    ...
    ...    **預期結果:**
    ...    - 開啟數量統計正確
    ...
    ...    **注意:**
    ...    此測試案例需要手動確認實際開啟的燈號數量
    [Tags]    verification    count    manual

    Given 連接預設陣列攝影機
    When 偵測所有燈號並記錄

    # 取得摘要資訊
    ${摘要} =    And 取得燈號狀態摘要
    Log    目前開啟數量: ${摘要}[on_count]    console=True

    # 此處需要根據實際情況調整預期數量
    # 範例：驗證陣列開啟數量 5
    Then Log    ⚠️  請手動驗證開啟數量是否正確


測試案例 08: 偵測所有行列燈號
    [Documentation]    測試偵測每一行每一列的燈號
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 依序偵測每個行列位置的燈號
    ...    3. 記錄完整的行列資訊
    ...
    ...    **預期結果:**
    ...    - 成功偵測 3 行 x 4 列 = 12 個燈號
    ...    - 每個行列位置都有對應的燈號
    [Tags]    detection    comprehensive

    Given 連接預設陣列攝影機
    When 擷取陣列影像

    Log    === 依行列順序偵測燈號 ===    console=True

    FOR    ${row}    IN RANGE    3
        FOR    ${col}    IN RANGE    4
            ${light_key} =    Set Variable    ${row}_${col}
            ${狀態} =    偵測單一燈號並記錄    ${light_key}

            ${狀態文字} =    Set Variable If    ${狀態}[is_on]    開啟    關閉
            Log    行${row} 列${col}: ${狀態}[name] - ${狀態文字} (${狀態}[brightness])    console=True
        END
    END

    Then 儲存陣列標註影像    test_all_rows_cols.jpg


測試案例 09: 比較兩次偵測的亮度變化
    [Documentation]    測試比較兩次偵測之間的亮度變化
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 第一次偵測所有燈號
    ...    3. 等待 2 秒
    ...    4. 第二次偵測所有燈號
    ...    5. 比較亮度變化
    ...
    ...    **預期結果:**
    ...    - 能計算出每個燈號的亮度變化
    [Tags]    analysis    comparison

    Given 連接預設陣列攝影機
    ${變化} =    When 比較兩次陣列亮度變化    delay=2.0

    Then Log Dictionary    ${變化}
    And Log    亮度變化分析完成


測試案例 10: 儲存標註影像
    [Documentation]    測試儲存帶有 ROI 標註和亮度數值的影像
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號
    ...    3. 儲存標註影像（包含 ROI 框、名稱、亮度、狀態）
    ...
    ...    **預期結果:**
    ...    - 影像成功儲存
    ...    - 影像包含完整的標註資訊
    [Tags]    visualization    output

    Given 連接預設陣列攝影機
    When 偵測所有燈號並記錄
    Then 儲存陣列標註影像    full_annotated_array.jpg    show_brightness=True


測試案例 11: 等待燈號變化（互動測試）
    [Documentation]    測試等待燈號狀態變化功能
    ...
    ...    **前置條件:**
    ...    - 測試人員準備手動改變燈號狀態
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 記錄初始狀態
    ...    3. 提示測試人員改變燈號 A1 (0_0) 狀態
    ...    4. 等待燈號狀態變化
    ...
    ...    **預期結果:**
    ...    - 能正確偵測到燈號狀態變化
    ...
    ...    **注意:**
    ...    此測試案例需要測試人員手動操作燈光開關
    [Tags]    wait    state_change    manual    interactive

    Given 連接預設陣列攝影機
    ${初始狀態} =    When 偵測單一燈號並記錄    0_0

    ${是否開啟} =    Get From Dictionary    ${初始狀態}    is_on

    Log    ⚠️  請在 30 秒內改變燈號 A1 (0_0) 的狀態    console=True
    Log    目前狀態: ${{ '開啟' if ${是否開啟} else '關閉' }}    console=True

    Run Keyword If    ${是否開啟}
    ...    等待燈號關閉    0_0    timeout=30
    ...    ELSE
    ...    等待燈號開啟    0_0    timeout=30

    ${最終狀態} =    Then 偵測單一燈號並記錄    0_0
    ${最終是否開啟} =    Get From Dictionary    ${最終狀態}    is_on

    Log    最終狀態: ${{ '開啟' if ${最終是否開啟} else '關閉' }}    console=True


測試案例 12: 完整陣列狀態報告
    [Documentation]    產生完整的陣列狀態報告
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號
    ...    3. 產生包含統計資訊的完整報告
    ...    4. 儲存標註影像
    ...
    ...    **預期結果:**
    ...    - 報告包含所有必要資訊
    ...    - 影像正確標註
    [Tags]    report    comprehensive

    Log    === 多燈號陣列完整報告 ===    console=True

    Given 連接預設陣列攝影機
    ${結果} =    When 偵測所有燈號並記錄
    ${摘要} =    And 取得燈號狀態摘要

    Then Log    總燈泡數: ${摘要}[total_lights]    console=True
    And Log    開啟數量: ${摘要}[on_count]    console=True
    And Log    關閉數量: ${摘要}[off_count]    console=True
    And Log    不確定數量: ${摘要}[uncertain_count]    console=True
    And Log    平均亮度: ${摘要}[average_brightness]    console=True
    And Log    等級分布: ${摘要}[level_counts]    console=True

    And 儲存陣列標註影像    full_report.jpg


測試案例 13: ROI 區域視覺化驗證
    [Documentation]    視覺化驗證 ROI 區域劃分是否正確
    ...
    ...    **測試步驟:**
    ...    1. 連接陣列攝影機
    ...    2. 偵測所有燈號
    ...    3. 儲存標註影像
    ...    4. 人工檢查 ROI 區域是否正確對準燈泡
    ...
    ...    **預期結果:**
    ...    - 每個 ROI 區域都正確對準對應的燈泡
    ...    - 沒有 ROI 區域跨越多個燈泡
    ...    - 紙箱邊緣沒有被納入 ROI 區域
    ...
    ...    **注意:**
    ...    需要人工檢查儲存的影像以驗證 ROI 劃分正確性
    [Tags]    verification    roi    manual

    Given 連接預設陣列攝影機
    When 偵測所有燈號並記錄
    Then 儲存陣列標註影像    roi_verification.jpg    show_brightness=True

    Log    ⚠️  請檢查影像 ${TEST_SCREENSHOT_DIR}/roi_verification.jpg    console=True
    Log    驗證每個 ROI 區域是否正確對準燈泡    console=True


*** Keywords ***
多燈號測試套件初始化
    [Documentation]    測試套件開始前的初始化設定

    Log    === 開始執行多燈號陣列檢測測試 ===    console=True
    Log    陣列名稱: ${ARRAY_NAME}    console=True

    # 建立截圖目錄
    Create Directory    ${TEST_SCREENSHOT_DIR}

    # 設定日誌級別
    Set Log Level    DEBUG


多燈號測試套件清理
    [Documentation]    測試套件結束後的清理工作

    Log    === 清理測試資源 ===    console=True

    # 斷開陣列攝影機連線
    Run Keyword And Ignore Error    斷開陣列攝影機

    Log    === 多燈號陣列檢測測試執行完成 ===    console=True
