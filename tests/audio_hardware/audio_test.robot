*** Settings ***
Documentation     音訊播放測試套件
...               驗證通過 Scarlett 4i4 各個聲道播放音訊的功能
...               使用 Gherkin 風格與中文關鍵字
Resource          ../../resources/audio_keywords.robot
Library           OperatingSystem

*** Variables ***
# 測試音訊檔案路徑，應與 config/audio_config.py 中的設定一致
${TEST_AUDIO_FILE}     ${EXECDIR}/libraries/voice_control/file_example_WAV_2MG.wav
${DURATION}            5

*** Test Cases ***
測試聲道1播放
    [Documentation]    驗證音訊能從 Scarlett 4i4 的物理輸出 1 正確播放
    [Tags]    channel-1
    Given Scarlett 音訊介面可用
    And 測試音訊檔案存在於 "${TEST_AUDIO_FILE}"
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "1" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_1-2"

測試聲道2播放
    [Documentation]    驗證音訊能從 Scarlett 4i4 的物理輸出 2 正確播放
    [Tags]    channel-2
    Given Scarlett 音訊介面可用
    And 測試音訊檔案存在於 "${TEST_AUDIO_FILE}"
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "2" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_1-2"

測試聲道3播放
    [Documentation]    驗證音訊能從 Scarlett 4i4 的物理輸出 3 正確播放
    [Tags]    channel-3
    Given Scarlett 音訊介面可用
    And 測試音訊檔案存在於 "${TEST_AUDIO_FILE}"
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "3" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_3-4"

測試聲道4播放
    [Documentation]    驗證音訊能從 Scarlett 4i4 的物理輸出 4 正確播放
    [Tags]    channel-4
    Given Scarlett 音訊介面可用
    And 測試音訊檔案存在於 "${TEST_AUDIO_FILE}"
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "4" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_3-4"

測試所有聲道循環播放
    [Documentation]    依序測試所有 4 個聲道
    [Tags]    all-channels
    Given Scarlett 音訊介面可用
    FOR    ${channel}    IN RANGE    1    5
        Log    正在測試聲道 ${channel}
        When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "${channel}" 持續 "${DURATION}" 秒
    END

測試無效聲道參數
    [Documentation]    測試錯誤的聲道參數應該失敗 (負面測試)
    [Tags]    negative
    Given Scarlett 音訊介面可用
    Run Keyword And Expect Error    *    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "5" 持續 "${DURATION}" 秒

測試不存在的音訊檔案
    [Documentation]    測試不存在的檔案應該失敗 (負面測試)
    [Tags]    negative
    Given Scarlett 音訊介面可用
    Run Keyword And Expect Error    *    When 使用者播放音訊檔案 "/nonexistent/file.wav" 到聲道 "1"
