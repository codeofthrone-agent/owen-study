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
...              - 聲道 2: 臥室 (Bedroom)
...              - 聲道 3: 廚房 (Kitchen)

Library    ../../../../libraries/voice_control/VoiceControlKeywords.py
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
    Log    ✓ 測試套件初始化完成

測試套件清理
    [Documentation]    清理測試套件使用的資源
    Log    ✓ 測試套件清理完成

*** Test Cases ***

# ==========================================
# 燈光 1 (Light One) 測試組合
# ==========================================

Scenario: Light 1 - 客廳開(Ch1) -> 臥室關(Ch2)
    [Documentation]    測試燈光1：客廳開啟，臥室關閉
    [Tags]    voice    tts    light_1    cross_channel    ch1_ch2
    # Step 1: Turn On (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

Scenario: Light 1 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光1：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_1    cross_channel    ch1_ch3
    # Step 1: Turn On (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 1 - 臥室開(Ch2) -> 客廳關(Ch1)
    [Documentation]    測試燈光1：臥室開啟，客廳關閉
    [Tags]    voice    tts    light_1    cross_channel    ch2_ch1
    # Step 1: Turn On (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 1 - 臥室開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光1：臥室開啟，廚房關閉
    [Tags]    voice    tts    light_1    cross_channel    ch2_ch3
    # Step 1: Turn On (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 1 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光1：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_1    cross_channel    ch3_ch1
    # Step 1: Turn On (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 1)
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 1 - 廚房開(Ch3) -> 臥室關(Ch2)
    [Documentation]    測試燈光1：廚房開啟，臥室關閉
    [Tags]    voice    tts    light_1    cross_channel    ch3_ch2
    # Step 1: Turn On (Channel 3)
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light one" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    
    # Interval
    Sleep    2
    
    # Step 2: Turn Off (Channel 2)
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light one" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

# ==========================================
# 燈光 2 (Light Two) 測試組合
# ==========================================

Scenario: Light 2 - 客廳開(Ch1) -> 臥室關(Ch2)
    [Documentation]    測試燈光2：客廳開啟，臥室關閉
    [Tags]    voice    tts    light_2    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

Scenario: Light 2 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光2：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_2    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 2 - 臥室開(Ch2) -> 客廳關(Ch1)
    [Documentation]    測試燈光2：臥室開啟，客廳關閉
    [Tags]    voice    tts    light_2    cross_channel    ch2_ch1
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 2 - 臥室開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光2：臥室開啟，廚房關閉
    [Tags]    voice    tts    light_2    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 2 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光2：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_2    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 2 - 廚房開(Ch3) -> 臥室關(Ch2)
    [Documentation]    測試燈光2：廚房開啟，臥室關閉
    [Tags]    voice    tts    light_2    cross_channel    ch3_ch2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light two" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light two" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

# ==========================================
# 燈光 3 (Light Three) 測試組合
# ==========================================

Scenario: Light 3 - 客廳開(Ch1) -> 臥室關(Ch2)
    [Documentation]    測試燈光3：客廳開啟，臥室關閉
    [Tags]    voice    tts    light_3    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

Scenario: Light 3 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光3：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_3    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 3 - 臥室開(Ch2) -> 客廳關(Ch1)
    [Documentation]    測試燈光3：臥室開啟，客廳關閉
    [Tags]    voice    tts    light_3    cross_channel    ch2_ch1
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 3 - 臥室開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光3：臥室開啟，廚房關閉
    [Tags]    voice    tts    light_3    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 3 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光3：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_3    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 3 - 廚房開(Ch3) -> 臥室關(Ch2)
    [Documentation]    測試燈光3：廚房開啟，臥室關閉
    [Tags]    voice    tts    light_3    cross_channel    ch3_ch2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light three" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

# ==========================================
# 燈光 4 (Light Four) 測試組合
# ==========================================

Scenario: Light 4 - 客廳開(Ch1) -> 臥室關(Ch2)
    [Documentation]    測試燈光4：客廳開啟，臥室關閉
    [Tags]    voice    tts    light_4    cross_channel    ch1_ch2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

Scenario: Light 4 - 客廳開(Ch1) -> 廚房關(Ch3)
    [Documentation]    測試燈光4：客廳開啟，廚房關閉
    [Tags]    voice    tts    light_4    cross_channel    ch1_ch3
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 4 - 臥室開(Ch2) -> 客廳關(Ch1)
    [Documentation]    測試燈光4：臥室開啟，客廳關閉
    [Tags]    voice    tts    light_4    cross_channel    ch2_ch1
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 4 - 臥室開(Ch2) -> 廚房關(Ch3)
    [Documentation]    測試燈光4：臥室開啟，廚房關閉
    [Tags]    voice    tts    light_4    cross_channel    ch2_ch3
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

Scenario: Light 4 - 廚房開(Ch3) -> 客廳關(Ch1)
    [Documentation]    測試燈光4：廚房開啟，客廳關閉
    [Tags]    voice    tts    light_4    cross_channel    ch3_ch1
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

Scenario: Light 4 - 廚房開(Ch3) -> 臥室關(Ch2)
    [Documentation]    測試燈光4：廚房開啟，臥室關閉
    [Tags]    voice    tts    light_4    cross_channel    ch3_ch2
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Turn on light four" 到聲道 "3"
    Then 語音應該成功播放到指定聲道
    Sleep    2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "2"
    Sleep    2
    When 使用者播放文字 "Turn off light four" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
