*** Settings ***
Documentation    TTS 語速設定測試案例 - Gherkin 風格
...              TTS Speed Setting Test Cases - Gherkin Style
Library    ../../libraries/voice_control/VoiceControlKeywords.py
Library    BuiltIn

*** Test Cases ***
Scenario: 使用者設定不同 TTS 語速並測試播放效果
    [Documentation]    Test TTS speed setting with different rates
    ...                測試不同語速設定並驗證播放效果
    ...
    ...                測試目標:
    ...                - 驗證語速設定功能是否正常運作
    ...                - 測試慢速 (150 wpm)、標準速度 (180 wpm)、快速 (220 wpm)
    ...                - 確保語音播放品質符合標準
    [Tags]    voice    tts    gherkin    speed    new_feature
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "pyttsx3"
    And Given 音訊輸出聲道 "1" 已準備就緒

    # 測試較慢速度 (150 wpm)
    When 使用者設定 TTS 語速為 "150"
    Then TTS 語速應該成功設定
    When 使用者播放文字 "This is a slow speed test" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

    # 測試標準速度 (180 wpm)
    When 使用者設定 TTS 語速為 "180"
    Then TTS 語速應該成功設定
    When 使用者播放文字 "This is a normal speed test" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

    # 測試較快速度 (220 wpm)
    When 使用者設定 TTS 語速為 "220"
    Then TTS 語速應該成功設定
    When 使用者播放文字 "This is a fast speed test" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

Scenario: 使用者通過 Given 關鍵字預設 TTS 語速
    [Documentation]    Test TTS speed presetting using Given keyword
    ...                使用 Given 關鍵字預設 TTS 語速
    ...
    ...                測試目標:
    ...                - 驗證 Given 關鍵字可正確預設語速
    ...                - 確保預設語速後播放功能正常
    [Tags]    voice    tts    gherkin    speed    preset
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "pyttsx3"
    And Given TTS 語速已設定為 "200"
    And Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "Testing with preset speed of 200 words per minute" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

Scenario: 使用者測試極端語速值的處理
    [Documentation]    Test handling of extreme speed values
    ...                測試極端語速值的處理
    ...
    ...                測試目標:
    ...                - 驗證系統對極慢速度 (100 wpm) 的處理
    ...                - 驗證系統對極快速度 (300 wpm) 的處理
    [Tags]    voice    tts    gherkin    speed    edge_case
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "pyttsx3"
    And Given 音訊輸出聲道 "1" 已準備就緒

    # 測試極慢速度
    When 使用者設定 TTS 語速為 "100"
    Then TTS 語速應該成功設定
    When 使用者播放文字 "Very slow speed" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

    # 測試極快速度
    When 使用者設定 TTS 語速為 "300"
    Then TTS 語速應該成功設定
    When 使用者播放文字 "Very fast speed" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

Scenario: 使用者在不同聲道測試相同語速
    [Documentation]    Test same speed on different channels
    ...                在不同聲道測試相同語速
    ...
    ...                測試目標:
    ...                - 驗證語速設定對所有聲道均生效
    ...                - 測試四個聲道的語音輸出一致性
    [Tags]    voice    tts    gherkin    speed    multi_channel
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "pyttsx3"
    And Given TTS 語速已設定為 "180"

    # 測試聲道 1
    Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "Testing channel 1 with speed 180" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

    # 測試聲道 2
    Given 音訊輸出聲道 "2" 已準備就緒
    When 使用者播放文字 "Testing channel 2 with speed 180" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

    # 測試聲道 3
    Given 音訊輸出聲道 "3" 已準備就緒
    When 使用者播放文字 "Testing channel 3 with speed 180" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

    # 測試聲道 4
    Given 音訊輸出聲道 "4" 已準備就緒
    When 使用者播放文字 "Testing channel 4 with speed 180" 到聲道 "4"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

Scenario: 使用者切換語速後驗證設定值
    [Documentation]    Verify speed value after multiple changes
    ...                多次切換語速後驗證設定值
    ...
    ...                測試目標:
    ...                - 驗證語速設定的持續性
    ...                - 確保每次變更都正確生效
    [Tags]    voice    tts    gherkin    speed    validation
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "pyttsx3"

    # 第一次設定
    When 使用者設定 TTS 語速為 "150"
    Then TTS 語速應該成功設定

    # 第二次設定
    When 使用者設定 TTS 語速為 "200"
    Then TTS 語速應該成功設定

    # 第三次設定
    When 使用者設定 TTS 語速為 "180"
    Then TTS 語速應該成功設定

    # 驗證最終播放效果
    When 使用者播放文字 "Final speed test at 180 words per minute" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 系統資源使用應該在正常範圍內

*** Keywords ***
# 自定義關鍵字可在此處定義
