*** Settings ***
Documentation    IP Camera 燈光檢測測試案例集
...
...              測試 IP Camera 基於 RTSP 串流的燈光檢測功能，包括：
...              - 攝影機連線測試
...              - 影像擷取測試
...              - 亮度計算測試
...              - 燈光狀態判定測試
...              - 燈光變化等待測試
...
...              環境需求:
...              - IP Camera 需支援 RTSP 協議
...              - 需在 config/ipcam_config.yaml 中正確設定攝影機資訊
...              - 需安裝 opencv-python 套件

Resource         ../../resources/ipcam_keywords.robot
Resource         ../../resources/common_keywords.robot

Suite Setup      測試套件初始化
Suite Teardown   測試套件清理

Test Tags        ipcam    light_detection    rtsp


*** Variables ***
${SCREENSHOT_DIR}    ${CURDIR}/../../results/screenshots/ipcam


*** Test Cases ***
測試案例 01: 連接實驗室 Level1 攝影機
    [Documentation]    驗證能夠成功連接到實驗室 Level1 攝影機
    ...
    ...    **前置條件:**
    ...    - IP Camera 已開啟並可連線
    ...    - RTSP 服務正常運作
    ...
    ...    **測試步驟:**
    ...    1. 連接實驗室 Level1 攝影機
    ...    2. 擷取一幀影像驗證連線
    ...
    ...    **預期結果:**
    ...    - 成功連接攝影機
    ...    - 成功擷取影像
    [Tags]    smoke    connection

    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then Log    攝影機連接成功並可正常擷取影像

測試案例 02: 擷取影像並儲存
    [Documentation]    測試從 IP Camera 擷取影像並儲存到檔案
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 擷取影像
    ...    3. 儲存影像到測試結果目錄
    ...
    ...    **預期結果:**
    ...    - 影像成功儲存
    ...    - 檔案存在且大小合理
    [Tags]    image_capture

    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 儲存當前攝影機影像    ${SCREENSHOT_DIR}/test_capture_level1.jpg

測試案例 03: 計算影像亮度值
    [Documentation]    測試影像亮度計算功能
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 擷取影像並計算亮度
    ...    3. 驗證亮度值在合理範圍內 (0-255)
    ...
    ...    **預期結果:**
    ...    - 亮度值在 0-255 範圍內
    ...    - 亮度值為數字類型
    [Tags]    brightness    analysis

    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 亮度應該在範圍內    0    255

測試案例 04: 檢測燈光開啟狀態
    [Documentation]    測試燈光開啟狀態檢測
    ...
    ...    **前置條件:**
    ...    - 測試環境燈光已開啟
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 取得當前亮度
    ...    3. 驗證燈光為開啟狀態（亮度 > 150）
    ...
    ...    **預期結果:**
    ...    - 偵測到燈光為開啟狀態
    ...    - 亮度高於閾值
    [Tags]    light_on    detection

    Given 連接實驗室 Level1 攝影機
    When 檢查燈光狀態並記錄
    Then 驗證燈光為開啟狀態

測試案例 05: 檢測燈光關閉狀態
    [Documentation]    測試燈光關閉狀態檢測
    ...
    ...    **前置條件:**
    ...    - 測試環境燈光已關閉
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 取得當前亮度
    ...    3. 驗證燈光為關閉狀態（亮度 < 50）
    ...
    ...    **預期結果:**
    ...    - 偵測到燈光為關閉狀態
    ...    - 亮度低於閾值
    ...
    ...    **注意:**
    ...    此測試案例需要手動關閉測試環境燈光
    [Tags]    light_off    detection    manual

    Given 連接實驗室 Level1 攝影機
    When 檢查燈光狀態並記錄
    Then 驗證燈光為關閉狀態

測試案例 06: 多攝影機連接切換測試
    [Documentation]    測試在多個攝影機之間切換連接
    ...
    ...    **測試步驟:**
    ...    1. 連接 Level1 攝影機並擷取影像
    ...    2. 切換連接 Level2 攝影機並擷取影像
    ...    3. 切換連接馬達區攝影機並擷取影像
    ...
    ...    **預期結果:**
    ...    - 所有攝影機都能成功連接
    ...    - 能正確切換並擷取各攝影機影像
    [Tags]    multi_camera    switching

    Given 連接實驗室 Level1 攝影機
    ${亮度_level1} =    取得當前燈光亮度
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/multi_test_level1.jpg

    When 連接實驗室 Level2 攝影機
    ${亮度_level2} =    取得當前燈光亮度
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/multi_test_level2.jpg

    And 連接實驗室馬達區攝影機
    ${亮度_motor} =    取得當前燈光亮度
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/multi_test_motor.jpg

    Then Log    Level1 亮度: ${亮度_level1}
    And Log    Level2 亮度: ${亮度_level2}
    And Log    馬達區亮度: ${亮度_motor}

測試案例 07: 等待燈光狀態變化
    [Documentation]    測試等待燈光狀態變化功能
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 記錄初始燈光狀態
    ...    3. 提示使用者改變燈光狀態
    ...    4. 等待燈光狀態變化
    ...
    ...    **預期結果:**
    ...    - 能正確偵測到燈光狀態變化
    ...    - 等待函數在逾時前完成
    ...
    ...    **注意:**
    ...    此測試案例需要手動操作燈光開關
    [Tags]    wait    state_change    manual

    Given 連接實驗室 Level1 攝影機
    ${初始狀態} =    檢查燈光狀態並記錄

    When Log    請在 30 秒內改變燈光狀態（開啟或關閉）
    ${是否開啟} =    Get From Dictionary    ${初始狀態}    is_on

    Run Keyword If    ${是否開啟}    等待燈光關閉    timeout=30
    ...    ELSE    等待燈光開啟    timeout=30

    Then 檢查燈光狀態並記錄

測試案例 08: 亮度變化偵測測試
    [Documentation]    測試亮度變化偵測功能
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 進行兩次亮度測量（間隔 2 秒）
    ...    3. 比較亮度變化
    ...
    ...    **預期結果:**
    ...    - 兩次測量都成功
    ...    - 能計算出亮度差異
    [Tags]    brightness    change_detection

    Given 連接實驗室 Level1 攝影機
    When 比較兩次亮度變化    delay=2.0
    Then Log    亮度變化測試完成

測試案例 09: 使用次串流 (live1) 擷取影像
    [Documentation]    測試使用次串流 (/live1) 擷取影像
    ...
    ...    **測試步驟:**
    ...    1. 連接攝影機
    ...    2. 使用主串流 (/live0) 擷取影像
    ...    3. 使用次串流 (/live1) 擷取影像
    ...    4. 比較兩個串流的影像
    ...
    ...    **預期結果:**
    ...    - 兩個串流都能成功擷取影像
    ...    - 次串流通常解析度較低或品質較差
    [Tags]    stream    live1    alternative

    Given 連接實驗室 Level1 攝影機

    # 主串流 (預設 /live0)
    ${亮度_live0} =    取得當前燈光亮度
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/stream_live0.jpg

    # 次串流 (/live1)
    When 擷取影像    /live1
    And 儲存最後影像    ${SCREENSHOT_DIR}/stream_live1.jpg
    ${亮度_live1} =    計算亮度

    Then Log    主串流 (live0) 亮度: ${亮度_live0}
    And Log    次串流 (live1) 亮度: ${亮度_live1}

測試案例 10: 完整燈光狀態報告
    [Documentation]    取得並顯示完整的燈光狀態資訊
    ...
    ...    **測試步驟:**
    ...    1. 連接所有實驗室攝影機
    ...    2. 取得各攝影機的燈光狀態
    ...    3. 產生完整報告
    ...
    ...    **預期結果:**
    ...    - 所有攝影機都能正常取得狀態
    ...    - 報告包含完整資訊
    [Tags]    report    status    comprehensive

    Log    === 實驗室燈光狀態報告 ===    console=True

    Given 連接實驗室 Level1 攝影機
    ${狀態_level1} =    檢查燈光狀態並記錄
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/report_level1.jpg

    When 連接實驗室 Level2 攝影機
    ${狀態_level2} =    檢查燈光狀態並記錄
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/report_level2.jpg

    And 連接實驗室馬達區攝影機
    ${狀態_motor} =    檢查燈光狀態並記錄
    And 儲存當前攝影機影像    ${SCREENSHOT_DIR}/report_motor.jpg

    Then Log    Level1 狀態: ${狀態_level1}    console=True
    And Log    Level2 狀態: ${狀態_level2}    console=True
    And Log    馬達區狀態: ${狀態_motor}    console=True


*** Keywords ***
測試套件初始化
    [Documentation]    測試套件開始前的初始化設定
    Log    開始執行 IP Camera 燈光檢測測試
    Create Directory    ${SCREENSHOT_DIR}
    Set Log Level    DEBUG

測試套件清理
    [Documentation]    測試套件結束後的清理工作
    Log    IP Camera 燈光檢測測試執行完成
    斷開攝影機連線
