*** Settings ***
Documentation    Voice Control TTS Test Cases - Cross-Channel Light Control
...              語音控制 TTS 測試案例 - 跨聲道燈光控制演示
...
...              測試場景:
...              模擬在一個位置開啟燈光，然後移動到另一個位置關閉燈光
...              流程: Location A (Turn On) -> Sleep 2s -> Location B (Turn Off)
...
...              位置對應:
...              - 聲道 1: 客廳 (Living Room)

...              - 聲道 3: 廚房 (Kitchen)

Library    ../libraries/voice_control/VoiceControlKeywords.py
Library    ../libraries/ipcam_light_detection/IPCamKeywords.py
Library    ../libraries/robot_arm_control/RobotArmKeywords.py
Library    DateTime
Library    String
Library    BuiltIn

Suite Setup    測試套件初始化
Suite Teardown    測試套件清理

*** Keywords ***
測試套件初始化
    [Documentation]    初始化測試套件所需的資源
    Log    ========================================
    Log    開始跨聲道燈光控制測試
    Log    ========================================
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given IP 攝影機已連接到攝影機    taipei_lab    level1
    And Given 測試環境設定為 "taipei_lab"
    And Given UART 日誌監控器已初始化
    When 使用者啟動 UART 背景監控
    Log    ✓ 測試套件初始化完成
    

測試套件清理
    [Documentation]    清理測試套件使用的資源
    When 使用者停止 UART 背景監控
    Log    ✓ 測試套件清理完成

   

*** Test Cases ***

# ==========================================
# 燈光 1 (Light One) 測試組合
# ==========================================

S01 : Light 1 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光1：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_1    cross_channel    ch1_ch3
    # Step 1: Turn On (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "3" 秒內收到包含以下檔案的語音回應 "kws_answer.mp3"
    

    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    喚醒命令完成時間: ${command_end}    console=True
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_on_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_on_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_one
    When 使用者播放文字 "Turn on light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Then 應該在 "3" 秒內收到包含以下檔案的語音回應 "cmd_002.mp3"
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_on_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_on_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_one
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    增加    10
    
    # Interval
    Sleep    3
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Then 應該在 "3" 秒內收到包含以下檔案的語音回應 "kws_answer.mp3"
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_off_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_off_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_one
    When 使用者播放文字 "Turn off light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Then 應該在 "3" 秒內收到包含以下檔案的語音回應 "cmd_003.mp3"
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_off_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_off_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_one
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_one    off


s02 : Light 1 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光1：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_1    cross_channel    ch3_ch1
    # Step 1: Turn On (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_on_ch3_roi.jpg
    # ${brightness_before}=    When 取得環境燈光亮度    light_one
    When 使用者播放文字 "Turn on light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_on_ch3_roi.jpg
    # ${brightness_after}=    When 取得環境燈光亮度    light_one
    # And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    increase    10
    And Then 驗證環境燈光狀態    light_one    on
    # And Then 驗證面板燈光狀態    light_one    on
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_before_off_ch1_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_one
    When 使用者播放文字 "Turn off light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_one    ${OUTPUT DIR}/${prefix}_${timestamp}_light_one_after_off_ch1_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_one
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_one    off
    # And Then 驗證面板燈光狀態    light_one    off

# ==========================================
# 燈光 2 (Light Two) 測試組合
# ==========================================

s03 : Light 2 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光2：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_2    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_on_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_on_roi.jpg
    When 使用者播放文字 "Turn on light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_on_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_on_roi.jpg
    And Then 驗證環境燈光狀態    light_two    on
    # And Then 驗證面板燈光狀態    light_two    on
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_off_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_off_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_two
    When 使用者播放文字 "Turn off light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_off_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_off_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_two
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_two    off
    # And Then 驗證面板燈光狀態    light_two    off

s04 : Light 2 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光2：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_2    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_on_ch3_roi.jpg
    When 使用者播放文字 "Turn on light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_on_ch3_roi.jpg
    And Then 驗證環境燈光狀態    light_two    on
    # And Then 驗證面板燈光狀態    light_two    on
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_before_off_ch1_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_two
    When 使用者播放文字 "Turn off light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_two    ${OUTPUT DIR}/${prefix}_${timestamp}_light_two_after_off_ch1_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_two
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_two    off
    # And Then 驗證面板燈光狀態    light_two    off

# ==========================================
# 燈光 3 (Light Three) 測試組合
# ==========================================

s05 : Light 3 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光3：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_3    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_on_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_on_roi.jpg
    When 使用者播放文字 "Turn on light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_on_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_on_roi.jpg
    And Then 驗證環境燈光狀態    light_three    on
    # And Then 驗證面板燈光狀態    light_three    on
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_off_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_off_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_three
    When 使用者播放文字 "Turn off light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_off_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_off_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_three
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_three    off
    # And Then 驗證面板燈光狀態    light_three    off

s06 : Light 3 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光3：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_3    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_on_ch3_roi.jpg
    When 使用者播放文字 "Turn on light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_on_ch3_roi.jpg
    And Then 驗證環境燈光狀態    light_three    on
    # And Then 驗證面板燈光狀態    light_three    on
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_before_off_ch1_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_three
    When 使用者播放文字 "Turn off light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_three    ${OUTPUT DIR}/${prefix}_${timestamp}_light_three_after_off_ch1_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_three
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_three    off
    # And Then 驗證面板燈光狀態    light_three    off

# ==========================================
# 燈光 4 (Light Four) 測試組合
# ==========================================

s07 : Light 4 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光4：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_4    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_on_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_on_roi.jpg
    When 使用者播放文字 "Turn on light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_on_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_on_roi.jpg
    And Then 驗證環境燈光狀態    light_four    on
    # And Then 驗證面板燈光狀態    light_four    on
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_off_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_off_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_four
    When 使用者播放文字 "Turn off light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_off_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_off_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_four
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_four    off
    # And Then 驗證面板燈光狀態    light_four    off

s08 : Light 4 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光4：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_4    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${prefix}=    Fetch From Left    ${TEST NAME}    ${SPACE}:${SPACE}
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_on_ch3_roi.jpg
    When 使用者播放文字 "Turn on light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_on_ch3_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_on_ch3_roi.jpg
    And Then 驗證環境燈光狀態    light_four    on
    # And Then 驗證面板燈光狀態    light_four    on
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_before_off_ch1_roi.jpg
    ${brightness_before}=    When 取得環境燈光亮度    light_four
    When 使用者播放文字 "Turn off light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    ${command_end}=    Get Current Date    result_format=%Y%m%d_%H%M%S.%f
    Log    語音命令完成時間: ${command_end}    console=True
    Sleep    3
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    And When 儲存完整影像包含標註    light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_off_ch1_full.jpg
    And When 儲存 ROI 影像        light_four    ${OUTPUT DIR}/${prefix}_${timestamp}_light_four_after_off_ch1_roi.jpg
    ${brightness_after}=    When 取得環境燈光亮度    light_four
    And Then 驗證亮度變化    ${brightness_before}    ${brightness_after}    減少    10
    # And Then 驗證環境燈光狀態    light_four    off
    # And Then 驗證面板燈光狀態    light_four    off
