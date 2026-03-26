*** Settings ***
Documentation    Voice Control TTS Test Cases - Cross-Channel Light Control (Light 1-4)
...              語音控制 TTS 測試案例 - 跨聲道燈光控制演示 (Light 1-4)
...
...              測試場景:
...              針對每個燈光 (Light 1-4)，測試從不同聲道發出開啟與關閉指令的交叉組合。
...              確保語音命令可以從任意位置 (聲道 1-3) 成功控制。
...
...              位置對應:
...              - 聲道 1: 客廳 (Bed)
...              - 聲道 2: 廚房 (Sofa)
...              - 聲道 3: 廚房 (Dining)

Library    ../../../../libraries/voice_control/VoiceControlKeywords.py
Library    ../../../../libraries/ipcam_light_detection/IPCamKeywords.py
Library    ../../../../libraries/robot_arm_control/RobotArmKeywords.py
Library    DateTime
Library    String
Library    BuiltIn

Suite Setup    測試套件初始化
Suite Teardown    測試套件清理

*** Keywords ***
測試套件初始化
    [Documentation]    初始化測試套件所需的資源
    Log    ========================================
    Log    開始跨聲道燈光控制測試 (Light 1-4)
    Log    ========================================
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given IP 攝影機已連接到攝影機    rv_car    cam1
    And Given IP 攝影機已連接到攝影機    rv_car    cam2
    And Given IP 攝影機已連接到攝影機    rv_car    cam3
    And Given 測試環境設定為 "rv_car"
    And Given UART 日誌監控器已初始化
    When 使用者啟動 UART 背景監控
    Log    ✓ 測試套件初始化完成

測試套件清理
    [Documentation]    清理測試套件使用的資源
    When 使用者停止 UART 背景監控
    Log    ✓ 測試套件清理完成

*** Test Cases ***
S00 : All Light off 
    [Documentation]    測試燈光1：客廳開啟(Ch1)，廚房關閉(Ch2)
    [Tags]    voice    tts    light_1 light_2 light_3 light_4    ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    
    # Step 1: Turn On (Channel 1)
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    3
    # Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    
    When 使用者播放文字 "Turn on all lights" 到聲道 "2"

    # Then 應該在 "3" 秒內收到語音指令 "CMD_ALL_LIGHTS_ON" 的回應


    Sleep    3
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    3
    # Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    
    When 使用者播放文字 "Turn off all lights" 到聲道 "2"

    # Then 應該在 "3" 秒內收到語音指令 "CMD_ALL_LIGHTS_OFF" 的回應


    Sleep    3



# ==========================================
# Light 1 (Light One)
# ==========================================
S01 : Light 1 - 客廳開(Ch1) -> 廚房關(Ch2)
    [Documentation]    測試燈光1：客廳開啟(Ch1)，廚房關閉(Ch2)
    [Tags]    voice    tts    light_1    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 1)
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light one" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_ON" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light one" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_OFF" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_off_roi.jpg

S02 : Light 1 - 廚房開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光1：廚房開啟(Ch2)，廚房關閉(Ch3)
    [Tags]    voice    tts    light_1    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 2)
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light one" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_ON" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light one" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_OFF" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_off_roi.jpg

S03 : Light 1 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光1：廚房開啟(Ch3)，客廳關閉(Ch1)
    [Tags]    voice    tts    light_1    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 3)
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light one" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_ON" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_on_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_before_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light one" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT1_OFF" 的回應
    And When 儲存完整影像包含標註    light_one    output/${prefix}_{timestamp}_light_one_after_off_full.jpg
    And When 儲存 ROI 影像        light_one    output/${prefix}_{timestamp}_light_one_after_off_roi.jpg

# ==========================================
# Light 2 (Light Two)
# ==========================================
S04 : Light 2 - 客廳開(Ch1) -> 廚房關(Ch2)
    [Documentation]    測試燈光2：客廳開啟(Ch1)，廚房關閉(Ch2)
    [Tags]    voice    tts    light_2    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 1)
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light two" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_ON" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light two" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_OFF" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_off_roi.jpg

S05 : Light 2 - 廚房開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光2：廚房開啟(Ch2)，廚房關閉(Ch3)
    [Tags]    voice    tts    light_2    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 2)
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light two" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_ON" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light two" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_OFF" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_off_roi.jpg

S06 : Light 2 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光2：廚房開啟(Ch3)，客廳關閉(Ch1)
    [Tags]    voice    tts    light_2    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 3)
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light two" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_ON" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_on_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_before_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light two" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT2_OFF" 的回應
    And When 儲存完整影像包含標註    light_two    output/${prefix}_{timestamp}_light_two_after_off_full.jpg
    And When 儲存 ROI 影像        light_two    output/${prefix}_{timestamp}_light_two_after_off_roi.jpg

# ==========================================
# Light 3 (Light Three)
# ==========================================
S07 : Light 3 - 客廳開(Ch1) -> 廚房關(Ch2)
    [Documentation]    測試燈光3：客廳開啟(Ch1)，廚房關閉(Ch2)
    [Tags]    voice    tts    light_3    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 1)
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light three" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_ON" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light three" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_OFF" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_off_roi.jpg

S08 : Light 3 - 廚房開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光3：廚房開啟(Ch2)，廚房關閉(Ch3)
    [Tags]    voice    tts    light_3    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 2)
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light three" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_ON" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light three" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_OFF" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_off_roi.jpg

S09 : Light 3 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光3：廚房開啟(Ch3)，客廳關閉(Ch1)
    [Tags]    voice    tts    light_3    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 3)
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light three" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_ON" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_on_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_before_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light three" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT3_OFF" 的回應
    And When 儲存完整影像包含標註    light_three    output/${prefix}_{timestamp}_light_three_after_off_full.jpg
    And When 儲存 ROI 影像        light_three    output/${prefix}_{timestamp}_light_three_after_off_roi.jpg

# ==========================================
# Light 4 (Light Four)
# ==========================================
S10 : Light 4 - 客廳開(Ch1) -> 廚房關(Ch2)
    [Documentation]    測試燈光4：客廳開啟(Ch1)，廚房關閉(Ch2)
    [Tags]    voice    tts    light_4    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 1)
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light four" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_ON" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light four" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_OFF" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_off_roi.jpg

S11 : Light 4 - 廚房開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光4：廚房開啟(Ch2)，廚房關閉(Ch3)
    [Tags]    voice    tts    light_4    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 2)
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light four" 到聲道 "2"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_ON" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light four" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_OFF" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_off_roi.jpg

S12 : Light 4 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光4：廚房開啟(Ch3)，客廳關閉(Ch1)
    [Tags]    voice    tts    light_4    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    
    # Step 1: Turn On (Channel 3)
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_on_roi.jpg
    
    When 使用者播放文字 "Turn on light four" 到聲道 "3"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_ON" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_on_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_on_roi.jpg

    Sleep    3
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到語音指令 "CMD_WAKE_UP" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_before_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_before_off_roi.jpg
    
    When 使用者播放文字 "Turn off light four" 到聲道 "1"

    Then 應該在 "3" 秒內收到語音指令 "CMD_LIGHT4_OFF" 的回應
    And When 儲存完整影像包含標註    light_four    output/${prefix}_{timestamp}_light_four_after_off_full.jpg
    And When 儲存 ROI 影像        light_four    output/${prefix}_{timestamp}_light_four_after_off_roi.jpg
