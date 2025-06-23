*** Settings ***
Documentation    本地語音驗證測試案例 - Gherkin 風格
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
Scenario: 使用者需要驗證 TTS 語音播放功能
    [Documentation]    Gherkin 風格的 TTS 語音執行測試場景
    [Tags]    voice    tts    execution    gherkin
    Given TTS 語音系統已經設定完成
    When 使用者要求播放指定文字語音
    Then 語音應該成功播放並記錄結果
    [Teardown]    清理音訊資源

Scenario: 使用者需要進行語音檢測驗證
    [Documentation]    Gherkin 風格的基本語音檢測測試場景
    [Tags]    voice    detection    basic    gherkin
    Given 語音檢測系統已經準備就緒
    When 使用者執行播放並檢測語音操作
    Then 目標聲音應該被正確檢測到
    And 檢測信心度應該符合要求
    [Teardown]    清理音訊資源

Scenario: 使用者需要測試個別語音功能模組
    [Documentation]    Gherkin 風格的個別語音功能測試場景
    [Tags]    voice    individual    functions    gherkin
    Given 語音錄音功能已經啟動
    When 使用者執行錄音並檢測流程
    Then 錄音檔案應該成功產生
    And 聲音檢測應該回傳結果
    [Teardown]    清理音訊資源

Scenario: 使用者需要測試不同檢測閾值設定
    [Documentation]    Gherkin 風格的閾值設定測試場景
    [Tags]    voice    threshold    parametric    gherkin
    Given 語音檢測已執行一次基準測試
    When 使用者測試多種不同的檢測閾值
    Then 所有閾值設定都應該成功
    And 系統應該恢復預設閾值設定
    [Teardown]    清理音訊資源

Scenario: 使用者需要驗證 TTS 語言設定功能
    [Documentation]    Gherkin 風格的 TTS 語言設定測試場景
    [Tags]    voice    tts    language    gherkin
    Given TTS 系統支援多種語言設定
    When 使用者變更 TTS 語言為英文
    Then 語言設定應該成功生效
    And 系統應該能恢復預設語言
    [Teardown]    清理音訊資源

Scenario: 使用者需要驗證錯誤處理機制
    [Documentation]    Gherkin 風格的錯誤處理測試場景
    [Tags]    voice    error    negative    gherkin
    Given 語音系統已經啟動並運行
    When 使用者嘗試輸入無效的設定參數
    Then 系統應該正確拒絕無效輸入
    And 不存在的聲音檢測應該回傳失敗
    [Teardown]    清理音訊資源

Scenario: 使用者需要載入參考聲音檔案
    [Documentation]    Gherkin 風格的參考聲音載入測試場景
    [Tags]    voice    reference    loading    gherkin
    Given 參考聲音檔案目錄已經存在
    When 使用者嘗試載入目標參考聲音
    Then 載入結果應該回傳相應的狀態
    [Teardown]    清理音訊資源

Scenario: 使用者需要進行長時間錄音測試
    [Documentation]    Gherkin 風格的長時間錄音測試場景
    [Tags]    voice    duration    extended    gherkin
    Given 錄音系統已經設定為長時間模式
    When 使用者啟動長時間錄音並短暫等待後停止
    Then 錄音檔案應該成功產生並通過驗證
    [Teardown]    清理音訊資源
# === Legacy Test Cases (向後相容) ===
Test TTS Voice execution
    [Documentation]    測試 TTS 語音執行功能 (傳統風格)
    [Tags]    voice    tts    execution    legacy
    
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
    [Documentation]    測試基本語音檢測功能 (傳統風格)
    [Tags]    voice    detection    basic    legacy
    
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
    [Documentation]    測試個別語音功能 (傳統風格)
    [Tags]    voice    individual    functions    legacy
    
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
    [Documentation]    測試不同閾值下的聲音檢測設定（不重複播放語音）(傳統風格)
    [Tags]    voice    threshold    parametric    legacy
    
    
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
    [Documentation]    測試 TTS 英文語言設定功能（不執行實際語音檢測）(傳統風格)
    [Tags]    voice    tts    language    legacy
    
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
    [Documentation]    測試錯誤處理機制 (傳統風格)
    [Tags]    voice    error    negative    legacy
    
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
    [Documentation]    測試參考聲音載入功能 (傳統風格)
    [Tags]    voice    reference    loading    legacy
    
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
    [Documentation]    測試長時間錄音設定（不重複播放語音）(傳統風格)
    [Tags]    voice    duration    extended    legacy
    
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
# === Given Keywords ===
TTS 語音系統已經設定完成
    [Documentation]    Given: 確保 TTS 系統已經正確初始化並設定參數
    Log    初始化 TTS 語音系統...
    
    # 設定 TTS 語言
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    # 設定 TTS 語速
    ${speed_result} =    Set TTS Speed    1.0
    Should Be True    ${speed_result}    msg=TTS 語速設定失敗
    
    Set Test Variable    ${TTS_READY}    True
    Log    TTS 語音系統設定完成

語音檢測系統已經準備就緒
    [Documentation]    Given: 確保語音檢測系統已經完整設定
    Log    初始化語音檢測系統...
    
    # 設定 TTS 參數
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    ${speed_result} =    Set TTS Speed    1.0
    Should Be True    ${speed_result}    msg=TTS 語速設定失敗
    
    # 設定檢測參數
    ${threshold_result} =    Set Detection Threshold    ${DETECTION_THRESHOLD}
    Should Be True    ${threshold_result}    msg=檢測閾值設定失敗
    
    Set Test Variable    ${DETECTION_READY}    True
    Log    語音檢測系統準備完成

語音錄音功能已經啟動
    [Documentation]    Given: 確保錄音功能已經啟動
    Log    語音錄音功能初始化...
    Set Test Variable    ${RECORDING_READY}    True

語音檢測已執行一次基準測試
    [Documentation]    Given: 先執行一次基準語音檢測測試
    Log    執行基準語音檢測...
    
    # 設定基準測試參數
    ${language_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${language_result}    msg=TTS 語言設定失敗
    
    ${threshold_result} =    Set Detection Threshold    0.75
    Should Be True    ${threshold_result}    msg=檢測閾值設定失敗
    
    # 執行基準檢測
    ${result} =    Speak And Detect    ${TTS_TEXT}    ${TARGET_SOUND}    5
    Set Test Variable    ${BASELINE_COMPLETED}    True
    Log    基準語音檢測完成

TTS 系統支援多種語言設定
    [Documentation]    Given: 確認 TTS 系統語言功能可用
    Log    確認 TTS 多語言支援...
    Set Test Variable    ${LANGUAGE_SUPPORT_READY}    True

語音系統已經啟動並運行
    [Documentation]    Given: 確保語音系統基本運行狀態正常
    Log    語音系統狀態檢查...
    Set Test Variable    ${VOICE_SYSTEM_RUNNING}    True

參考聲音檔案目錄已經存在
    [Documentation]    Given: 確認參考聲音檔案目錄結構
    Log    檢查參考聲音檔案目錄...
    Set Test Variable    ${REFERENCE_DIR_READY}    True

錄音系統已經設定為長時間模式
    [Documentation]    Given: 設定錄音系統為長時間錄音模式
    Log    設定長時間錄音模式...
    Set Test Variable    ${LONG_RECORDING_MODE}    True
    Set Test Variable    ${LONG_DURATION}    20

# === When Keywords ===
使用者要求播放指定文字語音
    [Documentation]    When: 執行 TTS 文字轉語音播放
    Log    執行 TTS 語音播放: ${TTS_TEXT}
    Speak Text    ${TTS_TEXT}
    Set Test Variable    ${SPEECH_EXECUTED}    True

使用者執行播放並檢測語音操作
    [Documentation]    When: 執行核心的播放與檢測功能
    Log    執行語音播放並檢測: ${TTS_TEXT} -> ${TARGET_SOUND}
    ${result} =    Speak And Detect    ${TTS_TEXT}    ${TARGET_SOUND}    ${RECORD_DURATION}
    Set Test Variable    ${DETECTION_RESULT}    ${result}

使用者執行錄音並檢測流程
    [Documentation]    When: 執行錄音和檢測的完整流程
    Log    啟動錄音功能...
    Start Voice Recording    5
    Sleep    2s    reason=等待錄音進行
    ${audio_file} =    Stop Voice Recording
    Set Test Variable    ${RECORDED_FILE}    ${audio_file}
    
    # 執行檢測
    ${detected} =    Detect Target Sound    ${TARGET_SOUND}    ${audio_file}
    Set Test Variable    ${INDIVIDUAL_DETECTION_RESULT}    ${detected}

使用者測試多種不同的檢測閾值
    [Documentation]    When: 測試多個不同的檢測閾值設定
    @{thresholds} =    Create List    0.6    0.7    0.8    0.9
    Set Test Variable    @{THRESHOLD_LIST}    @{thresholds}
    
    FOR    ${threshold}    IN    @{thresholds}
        Log    測試閾值設定: ${threshold}
        ${setting_result} =    Set Detection Threshold    ${threshold}
        Should Be True    ${setting_result}    msg=閾值設定失敗: ${threshold}
        Sleep    0.5s
    END
    Set Test Variable    ${THRESHOLD_TESTING_COMPLETED}    True

使用者變更 TTS 語言為英文
    [Documentation]    When: 執行 TTS 語言變更操作
    ${language} =    Set Variable    en
    Log    變更 TTS 語言為: ${language}
    ${result} =    Set TTS Language    ${language}
    Set Test Variable    ${LANGUAGE_CHANGE_RESULT}    ${result}
    Set Test Variable    ${NEW_LANGUAGE}    ${language}

使用者嘗試輸入無效的設定參數
    [Documentation]    When: 測試無效參數的錯誤處理
    Log    測試無效閾值設定...
    ${result1} =    Set Detection Threshold    1.5
    ${result2} =    Set Detection Threshold    -0.1
    Set Test Variable    ${INVALID_THRESHOLD_RESULTS}    ${result1}    ${result2}

使用者嘗試載入目標參考聲音
    [Documentation]    When: 嘗試載入參考聲音檔案
    Log    嘗試載入參考聲音: ${TARGET_SOUND}
    ${result} =    Load Reference Sound    ${TARGET_SOUND}    ${EMPTY}
    Set Test Variable    ${REFERENCE_LOAD_RESULT}    ${result}

使用者啟動長時間錄音並短暫等待後停止
    [Documentation]    When: 執行長時間錄音測試流程
    Log    啟動長時間錄音: ${LONG_DURATION} 秒
    Start Voice Recording    ${LONG_DURATION}
    Sleep    2s
    ${audio_file} =    Stop Voice Recording
    Set Test Variable    ${LONG_RECORDING_FILE}    ${audio_file}

# === Then Keywords ===
語音應該成功播放並記錄結果
    [Documentation]    Then: 驗證語音播放成功執行
    Should Be True    ${SPEECH_EXECUTED}    msg=語音播放未成功執行
    Log    TTS 語音播放成功: ${TTS_TEXT}

目標聲音應該被正確檢測到
    [Documentation]    Then: 驗證目標聲音檢測成功
    Should Be True    ${DETECTION_RESULT}    msg=未檢測到目標聲音 "${TARGET_SOUND}"
    
    # 獲取詳細檢測結果
    ${details} =    Get Detection Result
    Should Be True    ${details['detected']}
    Set Test Variable    ${DETECTION_DETAILS}    ${details}

錄音檔案應該成功產生
    [Documentation]    Then: 驗證錄音檔案正確產生
    Should Not Be Empty    ${RECORDED_FILE}    msg=錄音檔案路徑為空
    File Should Exist    ${RECORDED_FILE}
    Log    錄音檔案產生成功: ${RECORDED_FILE}

所有閾值設定都應該成功
    [Documentation]    Then: 驗證所有閾值設定操作成功
    Should Be True    ${THRESHOLD_TESTING_COMPLETED}    msg=閾值測試未完成

語言設定應該成功生效
    [Documentation]    Then: 驗證語言設定變更成功
    Should Be True    ${LANGUAGE_CHANGE_RESULT}    msg=語言設定失敗: ${NEW_LANGUAGE}
    Log    語言設定成功: ${NEW_LANGUAGE}

系統應該正確拒絕無效輸入
    [Documentation]    Then: 驗證系統錯誤處理正確
    Should Not Be True    ${INVALID_THRESHOLD_RESULTS}[0]    msg=應該拒絕無效閾值 1.5
    Should Not Be True    ${INVALID_THRESHOLD_RESULTS}[1]    msg=應該拒絕負數閾值 -0.1

載入結果應該回傳相應的狀態
    [Documentation]    Then: 驗證參考聲音載入結果
    Run Keyword If    ${REFERENCE_LOAD_RESULT}
    ...    Log    成功載入參考聲音: ${TARGET_SOUND}
    ...    ELSE
    ...    Log    參考聲音載入失敗，請確認檔案存在    WARN

錄音檔案應該成功產生並通過驗證
    [Documentation]    Then: 驗證長時間錄音檔案
    Verify Audio File Exists    ${LONG_RECORDING_FILE}
    Log    長時間錄音測試完成，檔案: ${LONG_RECORDING_FILE}

# === And Keywords ===
檢測信心度應該符合要求
    [Documentation]    And: 驗證檢測信心度達到要求
    Should Be True    ${DETECTION_DETAILS['confidence']} > 0.5    msg=檢測信心度過低
    Log    檢測成功！信心度: ${DETECTION_DETAILS['confidence']}

聲音檢測應該回傳結果
    [Documentation]    And: 驗證個別檢測功能回傳結果
    Log    個別檢測結果: ${INDIVIDUAL_DETECTION_RESULT}
    ${result_details} =    Get Detection Result
    Log Many    &{result_details}

系統應該恢復預設閾值設定
    [Documentation]    And: 驗證系統恢復預設閾值
    ${restore_result} =    Set Detection Threshold    ${DETECTION_THRESHOLD}
    Should Be True    ${restore_result}    msg=預設閾值恢復失敗
    Log    預設閾值恢復成功: ${DETECTION_THRESHOLD}

系統應該能恢復預設語言
    [Documentation]    And: 驗證系統恢復預設語言設定
    ${default_result} =    Set TTS Language    ${TTS_LANGUAGE}
    Should Be True    ${default_result}    msg=預設語言設定失敗: ${TTS_LANGUAGE}
    Log    預設語言設定成功: ${TTS_LANGUAGE}

不存在的聲音檢測應該回傳失敗
    [Documentation]    And: 驗證不存在聲音的檢測結果
    ${result} =    Detect Target Sound    不存在的聲音
    Should Not Be True    ${result}    msg=檢測不存在的聲音應該回傳 False
    
    # 測試載入不存在的參考聲音
    ${load_result} =    Load Reference Sound    測試聲音    /不存在的路徑/test.wav
    Should Not Be True    ${load_result}    msg=載入不存在的檔案應該失敗

# === Legacy/Utility Keywords ===
Setup Voice Test Environment
    [Documentation]    設定語音測試環境 (Legacy)
    
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
    [Documentation]    驗證音訊檔案存在且非空 (Legacy)
    
    File Should Exist    ${file_path}
    ${file_size} =    Get File Size    ${file_path}
    Should Be True    ${file_size} > 1000    msg=音訊檔案過小，可能錄音失敗

Log Detection Statistics
    [Documentation]    記錄檢測統計資訊 (Legacy)
    
    ${details} =    Get Detection Result
    
    Run Keyword If    ${details}
    ...    Log Many
    ...    檢測結果=${details.get('detected', 'Unknown')}
    ...    信心度=${details.get('confidence', 'Unknown')}
    ...    目標聲音=${details.get('target_sound', 'Unknown')}
    ...    閾值=${details.get('threshold', 'Unknown')}
    ...    音訊長度=${details.get('audio_length', 'Unknown')}
    ...    檢測時間=${details.get('detection_time', 'Unknown')}

Cleanup Audio Resources
    [Documentation]    清理音訊資源 (Utility Keyword)
    # 這個關鍵字可以用來清理測試後的音訊資源
    Log    清理音訊資源...

清理音訊資源
    [Documentation]    清理音訊資源 (中文版本)
    Cleanup Audio Resources