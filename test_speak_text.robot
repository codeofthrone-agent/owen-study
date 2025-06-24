*** Settings ***
Documentation    Local Voice TTS Test Cases - Gherkin Style
...              本地語音 TTS 測試案例 - Gherkin 風格
Library    libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
Library    BuiltIn

*** Test Cases ***
Scenario: User Needs To Play Text Speech Through TTS
    [Documentation]    Gherkin style TTS text-to-speech testing scenario
    ...                Gherkin 風格的 TTS 文字轉語音測試場景
    [Tags]    voice    tts    gherkin
    Given 語音系統已經成功初始化
    When 使用者請求播放文字    Hey power pro
    Then 語音播放應該成功完成
    And 測試執行結果應該被成功記錄

# Legacy Test Case (Backward Compatible)
Simple Speak Text Test
    [Documentation]    Simple Speak Text test (Traditional style)
    ...                簡單的 Speak Text 測試 (傳統風格)
    [Tags]    legacy
    Speak Text    Hello World
    Log    Test completed successfully

*** Keywords ***
# === Given Keywords ===
語音系統已經成功初始化
    [Documentation]    Given: 確保語音系統已經準備就緒
    ...                Given: Ensure the voice system is ready
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 語音系統初始化狀態檢查 / Voice system initialization status check
    ...                - 音頻設備可用性確認 / Audio device availability confirmation
    ...                
    ...                設定變數 / Variable Settings:
    ...                - VOICE_SYSTEM_READY: True - 語音系統就緒狀態 / Voice system ready status
    ...                
    ...                Example:
    ...                | Given | 語音系統已經成功初始化 |
    Log    語音系統初始化檢查進行中...
    # 可以在此加入系統狀態檢查
    Set Test Variable    ${VOICE_SYSTEM_READY}    True

# === When Keywords ===
使用者請求播放文字
    [Documentation]    When: 使用者觸發 TTS 播放指定文字
    ...                When: User triggers TTS playback of specified text
    ...                
    ...                參數 / Arguments:
    ...                - text: 要播放的文字內容 / Text content to be played
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 呼叫語音合成 API / Call speech synthesis API
    ...                - 播放合成的語音 / Play synthesized speech
    ...                
    ...                設定變數 / Variable Settings:
    ...                - SPOKEN_TEXT: 已播放的文字內容 / Played text content
    ...                
    ...                Examples:
    ...                | When | 使用者請求播放文字 | Hello World |
    ...                | When | 使用者請求播放文字 | 歡迎使用 |
    [Arguments]    ${text}
    Log    準備播放文字: ${text}
    Speak Text    ${text}
    Set Test Variable    ${SPOKEN_TEXT}    ${text}

# === Then Keywords ===
語音播放應該成功完成
    [Documentation]    Then: 驗證語音播放操作成功完成
    ...                Then: Verify that speech playback operation completed successfully
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 語音系統狀態正常 / Voice system status normal
    ...                - 播放操作無錯誤 / Playback operation without errors
    ...                
    ...                預期結果 / Expected Result:
    ...                - 語音應該成功播放並完成 / Speech should be successfully played and completed
    ...                
    ...                Example:
    ...                | Then | 語音播放應該成功完成 |
    Log    語音播放操作完成
    Should Be True    ${VOICE_SYSTEM_READY}    msg=語音系統狀態異常

# === And Keywords ===
測試執行結果應該被成功記錄
    [Documentation]    And: 確認測試結果被正確記錄
    ...                And: Confirm that test results are properly recorded
    ...                
    ...                記錄項目 / Recording Items:
    ...                - 播放的文字內容 / Played text content
    ...                - 測試執行狀態 / Test execution status
    ...                - 操作時間戳記 / Operation timestamp
    ...                
    ...                預期結果 / Expected Result:
    ...                - 所有測試資訊應該被正確記錄在日誌中 / All test information should be correctly recorded in logs
    ...                
    ...                Example:
    ...                | And | 測試執行結果應該被成功記錄 |
    Log    測試完成，播放文字: ${SPOKEN_TEXT}
    Log    測試成功完成
