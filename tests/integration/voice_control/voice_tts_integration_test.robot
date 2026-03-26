*** Settings ***
Documentation    語音控制與 TTS 整合測試
...              測試 VoiceControlKeywords 的完整功能
...              包含 TTS 生成、聲道控制、多語言支援
Library          ../../../libraries/voice_control/VoiceControlKeywords.py
Resource         ../../../resources/voice_control_keywords.robot

Suite Setup      Suite 初始化
Suite Teardown   Suite 清理

*** Variables ***
${TEST_TEXT_EN}         Hello World
${TEST_TEXT_ZH}         測試語音
${TEST_TEXT_JA}         テスト
${TEST_DURATION}        3

*** Test Cases ***
Scenario: 測試英文 TTS 輸出到聲道1
    [Documentation]    測試基本的英文文字轉語音並輸出到聲道 1
    [Tags]    voice_control    tts    basic    channel1

    Given 設定語音環境    language=en    engine=gtts
    When ${result}=    從聲道播放文字    ${TEST_TEXT_EN}    1    en    ${TEST_DURATION}
    Then 應該成功播放語音    ${result}

Scenario: 測試中文 TTS 輸出到聲道3
    [Documentation]    測試中文文字轉語音並輸出到聲道 3
    [Tags]    voice_control    tts    multilingual    channel3

    Given 設定語音環境    language=zh-TW    engine=gtts
    When ${result}=    從聲道播放文字    ${TEST_TEXT_ZH}    3    zh-TW    ${TEST_DURATION}
    Then 應該成功播放語音    ${result}

Scenario: 測試四聲道依序播放
    [Documentation]    測試四個聲道依序播放相同內容
    [Tags]    voice_control    tts    all_channels

    Given Scarlett 設備已就緒
    And 切換語音語言    en

    When ${results}=    播放語音到所有聲道    Channel Test    en    2
    Then 驗證所有聲道可用    ${results}

Scenario: 測試 TTS 引擎切換
    [Documentation]    測試在線與離線 TTS 引擎切換
    [Tags]    voice_control    tts    engine_switch

    Given Scarlett 設備已就緒

    # 測試 Google TTS（在線）
    When 切換語音引擎    gtts
    And ${result1}=    從聲道播放文字    Online TTS    1    en    2
    Then 應該成功播放語音    ${result1}

    # 測試 pyttsx3（離線）
    When 切換語音引擎    pyttsx3
    And ${result2}=    從聲道播放文字    Offline TTS    2    en    2
    Then 應該成功播放語音    ${result2}

Scenario: 測試多語言支援
    [Documentation]    測試不同語言的 TTS 輸出
    [Tags]    voice_control    tts    multilingual

    Given Scarlett 設備已就緒

    # 英文
    When 切換語音語言    en
    And ${result_en}=    從聲道播放文字    ${TEST_TEXT_EN}    1    en    2
    Then 應該成功播放語音    ${result_en}

    # 中文
    When 切換語音語言    zh-TW
    And ${result_zh}=    從聲道播放文字    ${TEST_TEXT_ZH}    2    zh-TW    2
    Then 應該成功播放語音    ${result_zh}

    # 日文
    When 切換語音語言    ja
    And ${result_ja}=    從聲道播放文字    ${TEST_TEXT_JA}    3    ja    2
    Then 應該成功播放語音    ${result_ja}

Scenario: 測試語速控制
    [Documentation]    測試不同語速的 TTS 輸出
    [Tags]    voice_control    tts    speed

    Given Scarlett 設備已就緒
    And 切換語音語言    en

    # 慢速
    When 設定 TTS 語速    120
    And ${result1}=    從聲道播放文字    Slow speed    1    en    3
    Then 應該成功播放語音    ${result1}

    # 正常速度
    When 設定 TTS 語速    180
    And ${result2}=    從聲道播放文字    Normal speed    2    en    2
    Then 應該成功播放語音    ${result2}

    # 快速
    When 設定 TTS 語速    250
    And ${result3}=    從聲道播放文字    Fast speed    3    en    2
    Then 應該成功播放語音    ${result3}

Scenario: 測試設備檢查功能
    [Documentation]    測試 Scarlett 設備檢查功能
    [Tags]    voice_control    device    check

    Given Scarlett 4i4 音效介面已正確連接
    Then Scarlett 4i4 設備應該處於正常運作狀態

Scenario: 測試 TTS 引擎資訊
    [Documentation]    測試取得 TTS 引擎資訊
    [Tags]    voice_control    tts    info

    Given 語音控制系統已成功初始化
    When 使用者查詢當前 TTS 引擎資訊
    Then 系統應該回傳正確的 TTS 引擎資訊

Scenario: 測試長文本播放
    [Documentation]    測試較長文本的 TTS 播放
    [Tags]    voice_control    tts    long_text

    Given 設定語音環境    language=en    engine=gtts

    ${long_text}=    Set Variable    This is a longer text to test the text-to-speech functionality with multiple words and sentences.

    When 使用者播放文字 "${long_text}" 到聲道 "1" 使用語言 "en"
    Then 語音應該成功播放到指定聲道

Scenario: 測試不同聲道的獨立性
    [Documentation]    測試不同聲道的獨立輸出能力
    [Tags]    voice_control    tts    independence

    Given 設定語音環境    language=en

    # 聲道 1
    When 使用者播放文字 "Output One" 到聲道 "1"
    Then 語音應該成功播放到指定聲道

    Sleep    0.5s

    # 聲道 2
    When 使用者播放文字 "Output Two" 到聲道 "2"
    Then 語音應該成功播放到指定聲道

    Sleep    0.5s

    # 聲道 3
    When 使用者播放文字 "Output Three" 到聲道 "3"
    Then 語音應該成功播放到指定聲道

    Sleep    0.5s

    # 聲道 4
    When 使用者播放文字 "Output Four" 到聲道 "4"
    Then 語音應該成功播放到指定聲道

*** Keywords ***
Suite 初始化
    [Documentation]    Suite 級別初始化
    Log    ========================================
    Log    語音控制與 TTS 整合測試開始
    Log    ========================================

    # 檢查設備
    Given Scarlett 4i4 音效介面已正確連接

    # 顯示系統資訊
    When 使用者查詢當前 TTS 引擎資訊
    Then 系統應該回傳正確的 TTS 引擎資訊

Suite 清理
    [Documentation]    Suite 級別清理
    Log    清理測試資源...
    And 暫存檔案應該正確清理

    Log    ========================================
    Log    語音控制與 TTS 整合測試完成
    Log    ========================================

*** Comments ***
執行方式：

    # 執行所有測試
    robot tests/voice_control/voice_tts_integration_test.robot

    # 執行特定標籤
    robot --include basic tests/voice_control/voice_tts_integration_test.robot
    robot --include multilingual tests/voice_control/voice_tts_integration_test.robot

    # 產生詳細報告
    robot --outputdir results/voice_control --loglevel DEBUG tests/voice_control/voice_tts_integration_test.robot
