*** Settings ***
Documentation    本地語音驗證測試案例
...              實現 "PC 利用 google tts 發出聲音 Hey Power Pro 並同時錄音 檢測 是否收到 登登的聲音" 的功能測試
Library          ${CURDIR}/../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
Library          BuiltIn
Library          Collections
Library          OperatingSystem

*** Variables ***
${TTS_TEXT}              Hey Power Pro
${TARGET_SOUND}          登登
${RECORD_DURATION}       10
${DETECTION_THRESHOLD}   0.75
${TTS_LANGUAGE}          en

*** Test Cases ***
Test TTS Voice execution
    [Documentation]    測試 TTS 語音執行功能
    [Tags]    voice    tts    execution
    
    # 設定 TTS 語言
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    # 設定 TTS 語速
    ${speed_result} =    Set TTS Speed    1.0
    Should Be True    ${speed_result}    msg=TTS 語速設定失敗
    
    # 執行 TTS 語音播放
    Speak Text    ${TTS_TEXT}
    
    Log    TTS 語音播放成功: ${TTS_TEXT}
    
    [Teardown]    Cleanup Audio Resources



Test Basic Voice Detection
    [Documentation]    測試基本語音檢測功能
    [Tags]    voice    detection    basic
    
    # 設定 TTS 參數
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    ${speed_result} =    Set TTS Speed    1.0
    Should Be True    ${speed_result}    msg=TTS 語速設定失敗
    
    # 設定檢測參數
    ${threshold_result} =    Set Detection Threshold    ${DETECTION_THRESHOLD}
    Should Be True    ${threshold_result}    msg=檢測閾值設定失敗
    
    # 執行核心功能：播放文字並檢測聲音
    ${result} =    Speak And Detect    ${TTS_TEXT}    ${TARGET_SOUND}    ${RECORD_DURATION}
    
    # 驗證檢測結果
    Should Be True    ${result}    msg=未檢測到目標聲音 "${TARGET_SOUND}"
    
    # 獲取詳細檢測結果
    ${details} =    Get Detection Result
    Should Be True    ${details['detected']}
    Should Be True    ${details['confidence']} > 0.5    msg=檢測信心度過低
    
    # 記錄檢測資訊
    Log    檢測成功！信心度: ${details['confidence']}
    Log    檢測時間: ${details['detection_time']}
    
    [Teardown]    Cleanup Audio Resources

Test Individual Voice Functions
    [Documentation]    測試個別語音功能
    [Tags]    voice    individual    functions
    
    # 測試錄音功能
    Start Voice Recording    5
    Sleep    2s    reason=等待錄音進行
    ${audio_file} =    Stop Voice Recording
    Should Not Be Empty    ${audio_file}    msg=錄音檔案路徑為空
    File Should Exist    ${audio_file}
    
    # 測試聲音檢測（使用剛才的錄音）
    ${detected} =    Detect Target Sound    ${TARGET_SOUND}    ${audio_file}
    Log    個別檢測結果: ${detected}
    
    # 獲取檢測統計
    ${result_details} =    Get Detection Result
    Log Many    &{result_details}
    
    [Teardown]    Cleanup Audio Resources

Test Voice Detection With Different Thresholds
    [Documentation]    測試不同閾值下的聲音檢測設定（不重複播放語音）
    [Tags]    voice    threshold    parametric
    
    @{thresholds} =    Create List    0.6    0.7    0.8    0.9
    
    # 先執行一次語音檢測
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    ${threshold_result} =    Set Detection Threshold    0.75
    Should Be True    ${threshold_result}    msg=檢測閾值設定失敗
    
    ${result} =    Speak And Detect    ${TTS_TEXT}    ${TARGET_SOUND}    5
    
    # 然後測試不同閾值設定（不重複播放）
    FOR    ${threshold}    IN    @{thresholds}
        Log    測試閾值設定: ${threshold}
        
        # 只測試閾值設定功能
        ${setting_result} =    Set Detection Threshold    ${threshold}
        Should Be True    ${setting_result}    msg=閾值設定失敗: ${threshold}
        
        Log    閾值 ${threshold} 設定成功
        
        Sleep    0.5s
    END
    
    # 恢復預設閾值
    ${restore_result} =    Set Detection Threshold    ${DETECTION_THRESHOLD}
    Should Be True    ${restore_result}    msg=預設閾值恢復失敗
    
    [Teardown]    Cleanup Audio Resources

Test TTS Language Settings
    [Documentation]    測試 TTS 英文語言設定功能（不執行實際語音檢測）
    [Tags]    voice    tts    language
    
    # 測試語言設定功能
    ${language} =    Set Variable    en
    
    Log    測試語言: ${language}
    
    # 設定 TTS 語言為英文
    ${result} =    Set TTS Language    ${language}
    Should Be True    ${result}    msg=語言設定失敗: ${language}
    
    Log    語言設定成功: ${language}
    
    # 測試恢復預設語言設定
    ${default_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${default_result}    msg=預設語言設定失敗: ${TTS_LANGUAGE}
    
    Log    預設語言設定成功: ${TTS_LANGUAGE}
    
    [Teardown]    Cleanup Audio Resources

Test Voice Detection Error Handling
    [Documentation]    測試錯誤處理機制
    [Tags]    voice    error    negative
    
    # 測試無效閾值
    ${result} =    Set Detection Threshold    1.5
    Should Not Be True    ${result}    msg=應該拒絕無效閾值
    
    ${result} =    Set Detection Threshold    -0.1
    Should Not Be True    ${result}    msg=應該拒絕負數閾值
    
    # 測試檢測不存在的聲音
    ${result} =    Detect Target Sound    不存在的聲音
    Should Not Be True    ${result}    msg=檢測不存在的聲音應該回傳 False
    
    # 測試載入不存在的參考聲音
    ${result} =    Load Reference Sound    測試聲音    /不存在的路徑/test.wav
    Should Not Be True    ${result}    msg=載入不存在的檔案應該失敗
    
    [Teardown]    Cleanup Audio Resources

Test Reference Sound Loading
    [Documentation]    測試參考聲音載入功能
    [Tags]    voice    reference    loading
    
    # 注意：此測試需要實際的參考聲音檔案
    # 在實際使用時，請確保 audio_samples/reference_sounds/ 目錄下有對應的檔案
    
    # 嘗試載入預設參考聲音
    ${result} =    Load Reference Sound    ${TARGET_SOUND}    ${EMPTY}
    
    Run Keyword If    ${result}
    ...    Log    成功載入參考聲音: ${TARGET_SOUND}
    ...    ELSE
    ...    Log    參考聲音載入失敗，請確認 audio_samples/reference_sounds/${TARGET_SOUND}.wav 檔案存在    WARN
    
    [Teardown]    Cleanup Audio Resources

Test Long Duration Recording
    [Documentation]    測試長時間錄音設定（不重複播放語音）
    [Tags]    voice    duration    extended
    
    # 測試錄音時長設定
    ${long_duration} =    Set Variable    20
    
    # 測試錄音功能（不播放 TTS）
    Start Voice Recording    ${long_duration}
    
    # 短暫等待
    Sleep    2s
    
    # 停止錄音
    ${audio_file} =    Stop Voice Recording
    
    # 驗證錄音檔案
    Verify Audio File Exists    ${audio_file}
    
    Log    長時間錄音測試完成，檔案: ${audio_file}
    
    [Teardown]    Cleanup Audio Resources

*** Keywords ***
Setup Voice Test Environment
    [Documentation]    設定語音測試環境
    
    # 設定預設 TTS 參數
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    ${speed_result} =    Set TTS Speed    1.0
    Should Be True    ${speed_result}    msg=TTS 語速設定失敗
    
    # 設定預設檢測參數
    ${threshold_result} =    Set Detection Threshold    ${DETECTION_THRESHOLD}
    Should Be True    ${threshold_result}    msg=檢測閾值設定失敗
    
    Log    語音測試環境設定完成

Verify Audio File Exists
    [Arguments]    ${file_path}
    [Documentation]    驗證音訊檔案存在且非空
    
    File Should Exist    ${file_path}
    ${file_size} =    Get File Size    ${file_path}
    Should Be True    ${file_size} > 1000    msg=音訊檔案過小，可能錄音失敗

Log Detection Statistics
    [Documentation]    記錄檢測統計資訊
    
    ${details} =    Get Detection Result
    
    Run Keyword If    ${details}
    ...    Log Many
    ...    檢測結果=${details.get('detected', 'Unknown')}
    ...    信心度=${details.get('confidence', 'Unknown')}
    ...    目標聲音=${details.get('target_sound', 'Unknown')}
    ...    閾值=${details.get('threshold', 'Unknown')}
    ...    音訊長度=${details.get('audio_length', 'Unknown')}
    ...    檢測時間=${details.get('detection_time', 'Unknown')}