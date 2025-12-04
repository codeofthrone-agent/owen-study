*** Settings ***
Documentation     進階音訊播放測試套件
...               包含設備驗證、sink 切換驗證等完整測試
...               使用 Gherkin 風格與中文關鍵字
Resource          ../../resources/audio_keywords.robot
Library           OperatingSystem
Library           Collections
Suite Setup       驗證測試環境
Suite Teardown    測試清理

*** Variables ***
${TEST_AUDIO_FILE}     ${EXECDIR}/libraries/voice_control/file_example_WAV_2MG.wav
${DURATION}            5

*** Test Cases ***
TC01 - 驗證 Scarlett 虛擬設備存在
    [Documentation]    確認 setup_pipewire_routing_v3.sh 已正確執行
    [Tags]    setup    prerequisite
    Given Scarlett 音訊介面可用

TC02 - 驗證聲道 1 和 2 使用 Scarlett_1-2
    [Documentation]    驗證聲道 1 和 2 路由到正確的 sink
    [Tags]    routing
    ${sink_1}=    取得聲道對應的輸出設備    1
    Should Be Equal    ${sink_1}    Scarlett_1-2
    ${sink_2}=    取得聲道對應的輸出設備    2
    Should Be Equal    ${sink_2}    Scarlett_1-2

TC03 - 驗證聲道 3 和 4 使用 Scarlett_3-4
    [Documentation]    驗證聲道 3 和 4 路由到正確的 sink
    [Tags]    routing
    ${sink_3}=    取得聲道對應的輸出設備    3
    Should Be Equal    ${sink_3}    Scarlett_3-4
    ${sink_4}=    取得聲道對應的輸出設備    4
    Should Be Equal    ${sink_4}    Scarlett_3-4

TC04 - 測試聲道 1 播放並驗證 sink 切換
    [Documentation]    播放到聲道 1，確認 sink 已切換
    [Tags]    playback    channel-1
    Given Scarlett 音訊介面可用
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "1" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_1-2"

TC05 - 測試聲道 2 播放並驗證 sink 切換
    [Documentation]    播放到聲道 2，確認 sink 已切換
    [Tags]    playback    channel-2
    Given Scarlett 音訊介面可用
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "2" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_1-2"

TC06 - 測試聲道 3 播放並驗證 sink 切換
    [Documentation]    播放到聲道 3，確認 sink 已切換到 3-4
    [Tags]    playback    channel-3
    Given Scarlett 音訊介面可用
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "3" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_3-4"

TC07 - 測試聲道 4 播放並驗證 sink 切換
    [Documentation]    播放到聲道 4，確認 sink 已切換到 3-4
    [Tags]    playback    channel-4
    Given Scarlett 音訊介面可用
    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "4" 持續 "${DURATION}" 秒
    Then 預設音訊輸出應該是 "Scarlett_3-4"

TC08 - 測試快速切換聲道
    [Documentation]    快速在聲道間切換以測試穩定性
    [Tags]    stress
    Given Scarlett 音訊介面可用
    FOR    ${i}    IN RANGE    3
        Log    第 ${i+1} 輪快速切換測試
        When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "1" 持續 "2" 秒
        When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "4" 持續 "2" 秒
    END

TC09 - 負面測試：無效聲道號
    [Documentation]    測試無效的聲道參數
    [Tags]    negative
    Given Scarlett 音訊介面可用
    Run Keyword And Expect Error    *    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "0" 持續 "${DURATION}" 秒
    Run Keyword And Expect Error    *    When 使用者播放音訊檔案 "${TEST_AUDIO_FILE}" 到聲道 "5" 持續 "${DURATION}" 秒

TC10 - 負面測試：不存在的檔案
    [Documentation]    測試不存在的音訊檔案
    [Tags]    negative
    Given Scarlett 音訊介面可用
    Run Keyword And Expect Error    *    When 使用者播放音訊檔案 "/tmp/nonexistent_audio.wav" 到聲道 "1"

*** Keywords ***
驗證測試環境
    [Documentation]    測試前的環境檢查
    Log    開始音訊測試套件
    OperatingSystem.File Should Exist    ${TEST_AUDIO_FILE}    msg=測試音訊檔案不存在
    ${sinks}=    列出可用輸出設備
    Log    可用的音訊設備: ${sinks}

測試清理
    [Documentation]    測試後清理
    Log    音訊測試套件完成
    ${current_sink}=    取得當前預設輸出設備
    Log    當前預設 sink: ${current_sink}
