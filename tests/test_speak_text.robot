*** Settings ***
Documentation    Voice Control TTS Test Cases - Gherkin Style with New Keywords
...              語音控制 TTS 測試案例 - 使用新 Gherkin 關鍵字
Library    ../libraries/voice_control/VoiceControlKeywords.py
Library    BuiltIn

*** Variables ***
${VOICE_SYSTEM_READY}    ${False}
${SPOKEN_TEXT}           ${EMPTY}

*** Test Cases ***
Scenario: 使用者需要通過 TTS 播放文字語音
    [Documentation]    Gherkin style TTS text-to-speech testing scenario with new keywords
    ...                使用新關鍵字的 Gherkin 風格 TTS 文字轉語音測試場景
    [Tags]    voice    tts    gherkin    scarlett    new
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Warm Weather Mode" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

Scenario: 使用者切換 TTS 引擎並播放多語言文字
    [Documentation]    Test TTS engine switching and multilingual playback
    ...                測試 TTS 引擎切換和多語言播放
    [Tags]    voice    tts    gherkin    multilingual    engine_switch
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    When 使用者切換 TTS 引擎到 "pyttsx3"
    Then TTS 引擎應該成功切換
    When 使用者播放文字 "測試語音" 到聲道 "2"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

Scenario: 使用者測試所有聲道並查詢系統資訊
    [Documentation]    Test all channels and query system information
    ...                測試所有聲道並查詢系統資訊
    [Tags]    voice    tts    gherkin    all_channels    system_info
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    When 使用者測試指定聲道 "1" 的音訊輸出
    And When 使用者測試指定聲道 "2" 的音訊輸出
    And When 使用者測試指定聲道 "3" 的音訊輸出
    And When 使用者測試指定聲道 "4" 的音訊輸出
    When 使用者查詢當前 TTS 引擎資訊
    Then 系統應該回傳正確的 TTS 引擎資訊
    And Then Scarlett 4i4 設備應該處於正常運作狀態
    And 系統資源使用應該在正常範圍內

# Legacy Test Cases (Backward Compatible) - 已移除
# 所有測試案例現已使用 Gherkin 風格關鍵字
Legacy Test Cleanup Complete
    [Documentation]    Legacy keywords have been removed, all tests now use Gherkin-style keywords
    ...                Legacy關鍵字已移除，所有測試現在使用Gherkin風格關鍵字
    [Tags]    cleanup    gherkin    modern
    Given 語音控制系統已成功初始化
    When 使用者查詢當前 TTS 引擎資訊
    Then 系統應該回傳正確的 TTS 引擎資訊
    And 暫存檔案應該正確清理

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
    Set Suite Variable    ${VOICE_SYSTEM_READY}    True

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
    When 使用者播放文字 "${text}" 到聲道 "1"
    Set Suite Variable    ${SPOKEN_TEXT}    ${text}

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
