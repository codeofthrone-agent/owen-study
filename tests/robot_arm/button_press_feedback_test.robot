*** Settings ***
Documentation     按壓反饋測試 - 驗證按鈕按壓後 LED 狀態變化
...
...               **測試目標：**
...               - 檢測按壓前的 LED 狀態
...               - 執行按鈕按壓
...               - 檢測按壓後的 LED 狀態
...               - 比較前後差異並顯示結果
...
...               **前置條件：**
...               - robot_arm_server.py 已啟動（--enable-vision）
...               - 按鈕已校準 ROI
...               - 被測設備已通電
...
...               **執行方式：**
...               robot tests/robot_arm/button_press_feedback_test.robot
...               robot --variable BUTTON:light2 tests/robot_arm/button_press_feedback_test.robot

Library           ../../libraries/robot_arm_control/RobotArmKeywords.py

Suite Setup       連接機器手臂伺服器
Suite Teardown    斷開機器手臂連接


*** Variables ***
${SERVER_HOST}        10.42.0.180
${SERVER_PORT}        9000
${DEFAULT_BUTTON}     light1


*** Test Cases ***
按壓反饋測試: Light1 按鈕
    [Documentation]    測試 Light1 按鈕的按壓反饋
    [Tags]    feedback    light1

    Given 機器手臂已正確連接到控制面板    speed=30

    # 步驟 1: 檢測按壓前狀態
    Log To Console    ${\n}🔍 步驟 1/4: 檢測按壓前狀態 (儲存完整圖像)...
    ${before_result}=    When 用戶檢測第 "light1" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓前狀態: 顏色=${before_result['color']}, 亮度=${before_result['brightness']}, 信心度=${before_result['confidence']}

    # 步驟 2: 執行按壓
    Log To Console    ${\n}🖱️  步驟 2/4: 執行按鈕按壓...
    When 用戶按壓第 "light1" 按鈕
    Then 上一步操作應該成功
    Log To Console    ✓ 按壓完成

    # 等待 LED 狀態穩定
    Sleep    1s    等待 LED 狀態穩定

    # 步驟 3: 檢測按壓後狀態
    Log To Console    ${\n}🔍 步驟 3/4: 檢測按壓後狀態 (儲存完整圖像)...
    ${after_result}=    When 用戶檢測第 "light1" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓後狀態: 顏色=${after_result['color']}, 亮度=${after_result['brightness']}, 信心度=${after_result['confidence']}

    # 步驟 4: 比較結果
    Log To Console    ${\n}📊 步驟 4/4: 比較結果...
    比較並顯示 LED 狀態變化    ${before_result}    ${after_result}


按壓反饋測試: Light2 按鈕
    [Documentation]    測試 Light2 按鈕的按壓反饋
    [Tags]    feedback    light2

    Given 機器手臂已正確連接到控制面板    speed=30

    Log To Console    ${\n}🔍 步驟 1/4: 檢測按壓前狀態 (儲存完整圖像)...
    ${before_result}=    When 用戶檢測第 "light2" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓前狀態: 顏色=${before_result['color']}, 亮度=${before_result['brightness']}, 信心度=${before_result['confidence']}

    Log To Console    ${\n}🖱️  步驟 2/4: 執行按鈕按壓...
    When 用戶按壓第 "light2" 按鈕
    Then 上一步操作應該成功
    Log To Console    ✓ 按壓完成

    Sleep    1s    等待 LED 狀態穩定

    Log To Console    ${\n}🔍 步驟 3/4: 檢測按壓後狀態 (儲存完整圖像)...
    ${after_result}=    When 用戶檢測第 "light2" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓後狀態: 顏色=${after_result['color']}, 亮度=${after_result['brightness']}, 信心度=${after_result['confidence']}

    Log To Console    ${\n}📊 步驟 4/4: 比較結果...
    比較並顯示 LED 狀態變化    ${before_result}    ${after_result}


按壓反饋測試: Light3 按鈕
    [Documentation]    測試 Light3 按鈕的按壓反饋
    [Tags]    feedback    light3

    Given 機器手臂已正確連接到控制面板    speed=30

    Log To Console    ${\n}🔍 步驟 1/4: 檢測按壓前狀態 (儲存完整圖像)...
    ${before_result}=    When 用戶檢測第 "light3" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓前狀態: 顏色=${before_result['color']}, 亮度=${before_result['brightness']}, 信心度=${before_result['confidence']}

    Log To Console    ${\n}🖱️  步驟 2/4: 執行按鈕按壓...
    When 用戶按壓第 "light3" 按鈕
    Then 上一步操作應該成功
    Log To Console    ✓ 按壓完成

    Sleep    1s    等待 LED 狀態穩定

    Log To Console    ${\n}🔍 步驟 3/4: 檢測按壓後狀態 (儲存完整圖像)...
    ${after_result}=    When 用戶檢測第 "light3" 按鈕的燈光狀態並儲存完整圖像
    Log To Console    ✓ 按壓後狀態: 顏色=${after_result['color']}, 亮度=${after_result['brightness']}, 信心度=${before_result['confidence']}

    Log To Console    ${\n}📊 步驟 4/4: 比較結果...
    比較並顯示 LED 狀態變化    ${before_result}    ${after_result}


按壓反饋測試: Bluetooth 按鈕
    [Documentation]    測試 Bluetooth 按鈕的按壓反饋（藍色 LED）
    [Tags]    feedback    bluetooth

    Given 機器手臂已正確連接到控制面板    speed=30

    Log To Console    ${\n}🔍 步驟 1/4: 檢測按壓前狀態...
    ${before_result}=    When 用戶檢測第 "bluetooth" 按鈕的燈光狀態
    Log To Console    ✓ 按壓前: 顏色=${before_result['color']}, 亮度=${before_result['brightness']}

    Log To Console    ${\n}🖱️  步驟 2/4: 執行按鈕按壓（2次）...
    When 用戶按壓第 "bluetooth" 按鈕
    Then 上一步操作應該成功
    Log To Console    ✓ 按壓完成

    Sleep    1s    等待 LED 狀態穩定

    Log To Console    ${\n}🔍 步驟 3/4: 檢測按壓後狀態...
    ${after_result}=    When 用戶檢測第 "bluetooth" 按鈕的燈光狀態
    Log To Console    ✓ 按壓後: 顏色=${after_result['color']}, 亮度=${after_result['brightness']}

    Log To Console    ${\n}📊 步驟 4/4: 比較結果...
    比較並顯示 LED 狀態變化    ${before_result}    ${after_result}


*** Keywords ***
連接機器手臂伺服器
    [Documentation]    連接到伺服器
    When 用戶連接到機器手臂    ${SERVER_HOST}    ${SERVER_PORT}
    Log To Console    ✓ 已連接到 ${SERVER_HOST}:${SERVER_PORT}

斷開機器手臂連接
    [Documentation]    斷開連接
    When 用戶中斷與機器手臂的連接
    Log To Console    ✓ 已斷開連接

比較並顯示 LED 狀態變化
    [Documentation]    比較並顯示按壓前後的 LED 狀態變化
    [Arguments]    ${before}    ${after}

    # 計算亮度變化
    ${brightness_diff}=    Evaluate    ${after['brightness']} - ${before['brightness']}
    ${brightness_change_percent}=    Evaluate    abs(${brightness_diff}) / ${before['brightness']} * 100 if ${before['brightness']} > 0 else 0
    ${brightness_change_percent_str}=    Evaluate    f"{${brightness_change_percent}:.2f}"

    # 顯示比較結果
    Log To Console    ${\n}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Log To Console    📊 LED 狀態變化分析
    Log To Console    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Log To Console    ${\n}📍 按壓前狀態:
    Log To Console       • 顏色: ${before['color']}
    Log To Console       • 亮度: ${before['brightness']}
    Log To Console       • 信心度: ${before['confidence']}
    Log To Console    ${\n}📍 按壓後狀態:
    Log To Console       • 顏色: ${after['color']}
    Log To Console       • 亮度: ${after['brightness']}
    Log To Console       • 信心度: ${after['confidence']}
    Log To Console    ${\n}📈 變化分析:
    Log To Console       • 顏色變化: ${before['color']} → ${after['color']}
    Log To Console       • 亮度變化: ${brightness_diff} (${brightness_change_percent_str}%)

    # 判斷變化類型
    ${status_changed}=    Run Keyword And Return Status
    ...    Should Not Be Equal    ${before['color']}    ${after['color']}

    Run Keyword If    ${status_changed}
    ...    Log To Console    ${\n}✅ 結論: LED 狀態已改變（顏色切換）
    ...    ELSE IF    ${brightness_change_percent} > 20
    ...    Log To Console    ${\n}✅ 結論: LED 亮度有顯著變化（${brightness_change_percent_str}%）
    ...    ELSE
    ...    Log To Console    ${\n}⚠️  結論: LED 狀態變化不明顯（可能已是目標狀態或需要多次按壓）

    Log To Console    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${\n}

    # 儲存結果到測試報告
    Set Test Message    按壓前: ${before['color']} (亮度 ${before['brightness']}) → 按壓後: ${after['color']} (亮度 ${after['brightness']})
