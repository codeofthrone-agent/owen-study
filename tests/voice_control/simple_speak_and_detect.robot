*** Settings ***
Documentation     一個使用背景錄音和音訊裁切技術來偵測喚醒詞後系統回應的測試案例。
...               流程:
...               1. 啟動背景錄音
...               2. 播放喚醒詞
...               3. 等待系統回應
...               4. 停止錄音
...               5. 從錄音中裁切掉喚醒詞的部分
...               6. 比對剩下的音訊是否為預期的系統回應音

Resource          ../../resources/voice_control_keywords.robot
Library           ../../libraries/ipcam_light_detection/IPCamAudioDetection.py    WITH NAME    AudioDetector
Library           BuiltIn
Library           OperatingSystem
Library           Collections

*** Variables ***
${CAMERA_ENV}            laboratory
${CAMERA_NAME}           level1
${REFERENCE_SOUND}       登登
${WAKE_WORD}             Hey Power Pro
${SCARLETT_CHANNEL}      1
${LANGUAGE}              en
${RESPONSE_WAIT_TIME}    3s
${WAKE_WORD_DURATION}    1.5

*** Test Cases ***
Speak And Detect Response Test
    [Documentation]    播放喚醒詞，並使用背景錄音和音訊裁切技術來驗證系統是否發出預期的回應音。
    [Tags]    speak-and-detect    audio-processing

    # 步驟 1: 初始化設定
    Log To Console    步驟 1: 初始化設定...
    ${project_root}=    Normalize Path    ${CURDIR}/../..
    Append To Environment Variable    PYTHONPATH    ${project_root}
    ${rtsp_url}=    Evaluate    importlib.import_module('config.ipcam_config').get_camera_url('${CAMERA_ENV}', '${CAMERA_NAME}')    modules=importlib
    Log    RTSP URL: ${rtsp_url}
    Should Not Be Empty    ${rtsp_url}    RTSP URL 不應為空
    AudioDetector.初始化音訊檢測器    ${rtsp_url}

    # 步驟 2: 啟動背景錄音
    Log To Console    步驟 2: 啟動背景錄音...
    ${recording_file}=    AudioDetector.啟動背景錄音
    Should Not Be Empty    ${recording_file}    啟動背景錄音失敗，未回傳檔案路徑。

    # 步驟 3: 播放喚醒詞
    Log To Console    步驟 3: 播放喚醒詞 "${WAKE_WORD}"...
    When 使用者播放文字 "${WAKE_WORD}" 到聲道 "${SCARLETT_CHANNEL}" 使用語言 "${LANGUAGE}"

    # 步驟 4: 等待系統回應並停止錄音
    Log To Console    步驟 4: 等待 ${RESPONSE_WAIT_TIME} 並停止錄音...
    Sleep    ${RESPONSE_WAIT_TIME}
    ${full_audio}=    AudioDetector.停止背景錄音
    Should Not Be Empty    ${full_audio}    停止背景錄音失敗，未回傳檔案路徑。
    Log    完整錄音檔: ${full_audio}

    # 步驟 5: 裁切音訊，移除喚醒詞
    Log To Console    步驟 5: 從錄音開頭裁切 ${WAKE_WORD_DURATION} 秒...
    ${trimmed_audio}=    AudioDetector.裁切音訊開頭    ${full_audio}    ${WAKE_WORD_DURATION}
    Should Not Be Empty    ${trimmed_audio}    裁切音訊失敗，未回傳檔案路徑。
    Log    裁切後的音訊檔: ${trimmed_audio}

    # 步驟 6: 比對裁切後的音訊與參考音檔
    Log To Console    步驟 6: 比對裁切後的音訊與參考音檔 "${REFERENCE_SOUND}"...
    ${detected}    ${confidence}=    AudioDetector.比對音訊與參考音檔    ${trimmed_audio}    ${REFERENCE_SOUND}

    # 步驟 7: 驗證結果
    Log To Console    步驟 7: 驗證結果...
    Log    檢測結果: ${detected}, 信心度: ${confidence}
    Should Be True    ${detected}    msg=未偵測到預期的回應音 '${REFERENCE_SOUND}'。 信心度: ${confidence}
    Log To Console    ✓ 成功偵測到回應音 '${REFERENCE_SOUND}'，信心度為 ${confidence}。
