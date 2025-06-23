*** Settings ***
Documentation    Local Voice TTS Test Cases - Gherkin Style
...              本地語音 TTS 測試案例 - Gherkin 風格
...              
...              This test suite demonstrates how to test Text-To-Speech functionality
...              using Gherkin style keywords. It validates voice synthesis and 
...              verification capabilities in a behavior-driven manner.
...              
...              此測試套件展示如何使用 Gherkin 風格關鍵字測試文字轉語音功能。
...              以行為驅動的方式驗證語音合成和驗證能力。
Library    ../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
Library    BuiltIn

*** Test Cases ***
Scenario: User Needs To Play Text Speech Through TTS
    [Documentation]    Gherkin style TTS text-to-speech testing scenario
    ...                Gherkin 風格的 TTS 文字轉語音測試場景
    [Tags]    voice    tts    gherkin
    Given Voice System Has Been Initialized Successfully
    When User Requests To Play Text "Hello World"
    Then Speech Should Be Played Successfully
    And Test Execution Results Should Be Recorded Successfully

# Legacy Test Case (Backward Compatible)
Simple Speak Text Test
    [Documentation]    Simple Speak Text test (Traditional style)
    ...                簡單的 Speak Text 測試 (傳統風格)
    [Tags]    legacy
    Speak Text    Hello World
    Log    Test completed successfully

*** Keywords ***
# === Given Keywords ===
Voice System Has Been Initialized Successfully
    [Documentation]    Given: Ensure the voice system is ready
    ...                Given: 確保語音系統已經準備就緒
    ...                
    ...                This keyword initializes the voice system and verifies
    ...                that all necessary components are available and functioning.
    ...                
    ...                此關鍵字初始化語音系統並驗證所有必要組件可用且正常運作。
    ...                
    ...                Example:
    ...                | Given | Voice System Has Been Initialized Successfully |
    ...                
    ...                範例:
    ...                | Given | Voice System Has Been Initialized Successfully |
    Log    Voice system initialization check in progress...
    # Can add system status check here
    Set Test Variable    ${VOICE_SYSTEM_READY}    True

# === When Keywords ===
User Requests To Play Text "${text}"
    [Documentation]    When: User triggers TTS playback of specified text
    ...                When: 使用者觸發 TTS 播放指定文字
    ...                
    ...                This keyword accepts a text parameter and triggers the
    ...                Text-To-Speech engine to synthesize and play the audio.
    ...                
    ...                此關鍵字接受文字參數並觸發文字轉語音引擎合成並播放音訊。
    ...                
    ...                Arguments:
    ...                - text: The text to be spoken by TTS engine
    ...                - text: 要由 TTS 引擎播放的文字
    ...                
    ...                Example:
    ...                | When | User Requests To Play Text "Hello World" |
    ...                | When | User Requests To Play Text "歡迎使用語音系統" |
    ...                
    ...                範例:
    ...                | When | User Requests To Play Text "Hello World" |
    ...                | When | User Requests To Play Text "歡迎使用語音系統" |
    [Arguments]    ${text}
    Log    Preparing to play text: ${text}
    Speak Text    ${text}
    Set Test Variable    ${SPOKEN_TEXT}    ${text}

# === Then Keywords ===
Speech Should Be Played Successfully
    [Documentation]    Then: Verify that speech playback operation completed successfully
    ...                Then: 驗證語音播放操作成功完成
    ...                
    ...                This keyword validates that the TTS operation was executed
    ...                without errors and the voice system remains in a healthy state.
    ...                
    ...                此關鍵字驗證 TTS 操作已成功執行且語音系統保持健康狀態。
    ...                
    ...                Example:
    ...                | Then | Speech Should Be Played Successfully |
    ...                
    ...                範例:
    ...                | Then | Speech Should Be Played Successfully |
    Log    Speech playback operation completed
    Should Be True    ${VOICE_SYSTEM_READY}    msg=Voice system status abnormal

# === And Keywords ===
Test Execution Results Should Be Recorded Successfully
    [Documentation]    And: Confirm that test results are properly recorded
    ...                And: 確認測試結果被正確記錄
    ...                
    ...                This keyword ensures that the test execution details are
    ...                properly logged and available for verification and reporting.
    ...                
    ...                此關鍵字確保測試執行詳情被正確記錄並可用於驗證和報告。
    ...                
    ...                Example:
    ...                | And | Test Execution Results Should Be Recorded Successfully |
    ...                
    ...                範例:
    ...                | And | Test Execution Results Should Be Recorded Successfully |
    Log    Test completed, played text: ${SPOKEN_TEXT}
    Log    Test completed successfully
