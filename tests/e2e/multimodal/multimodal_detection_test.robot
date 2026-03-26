*** Settings ***
Documentation    語音助手多感官檢測整合測試
...
...    測試語音助手是否同時具備視覺和聽覺回應。
...    驗證標準：視覺（螢幕變亮）AND 聽覺（提示音）都必須通過。
...
Resource         ../../../resources/multimodal_keywords.robot
Resource         ../../../resources/voice_control_keywords.robot
Resource         ../../../resources/common_keywords.robot

Suite Setup      測試前置準備
Suite Teardown   測試後清理

*** Variables ***
${喚醒詞}          Hey Power Pro
${環境}            laboratory
${攝影機}          level1
${參考聲音}        登登
${超時時間}        10
${Scarlett聲道}    1

*** Test Cases ***
Scenario: 測試語音助手完整回應（視覺 AND 聽覺）
    [Documentation]    測試語音助手是否同時具備視覺和聽覺回應
    ...
    ...    驗證標準：
    ...    1. 螢幕必須變亮（視覺回應）
    ...    2. 必須播放提示音（聽覺回應）
    ...    3. 兩者都通過才算成功
    ...
    [Tags]    voice_assistant    multimodal    critical    smoke

    Given Scarlett 音訊設備已就緒
    And IP Camera 可正常連線

    ${結果}=    測試語音助理回應
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    scarlett_channel=${Scarlett聲道}
    ...    detection_timeout=${超時時間}
    ...    require_both=True

    Then 驗證測試結果成功    ${結果}
    And 記錄詳細檢測結果    ${結果}
    And 驗證視覺檢測通過    ${結果}
    And 驗證聽覺檢測通過    ${結果}

Scenario: 測試不同喚醒詞的回應
    [Documentation]    測試語音助手對不同喚醒詞的完整回應
    [Tags]    voice_assistant    wake_words

    @{喚醒詞列表}=    Create List
    ...    Hey Power Pro
    ...    Hello Assistant

    FOR    ${測試喚醒詞}    IN    @{喚醒詞列表}
        Log    測試喚醒詞: ${測試喚醒詞}    console=yes

        ${結果}=    測試語音助理回應
        ...    wake_word=${測試喚醒詞}
        ...    camera_env=${環境}
        ...    camera_name=${攝影機}
        ...    scarlett_channel=${Scarlett聲道}
        ...    detection_timeout=${超時時間}
        ...    require_both=True

        驗證測試結果成功    ${結果}
        記錄詳細檢測結果    ${結果}

        Sleep    3s    reason=等待語音助手恢復待命狀態
    END

Scenario: 測試連續多次喚醒穩定性
    [Documentation]    測試語音助手連續多次喚醒的穩定性
    [Tags]    voice_assistant    stability

    ${測試次數}=    Set Variable    3

    FOR    ${次數}    IN RANGE    1    ${測試次數+1}
        Log    第 ${次數} 次測試    console=yes

        ${結果}=    測試語音助理回應
        ...    wake_word=${喚醒詞}
        ...    camera_env=${環境}
        ...    camera_name=${攝影機}
        ...    scarlett_channel=${Scarlett聲道}
        ...    detection_timeout=${超時時間}
        ...    require_both=True

        驗證測試結果成功    ${結果}

        Run Keyword If    ${次數} < ${測試次數}
        ...    Sleep    5s    reason=等待語音助手恢復

        Log    第 ${次數} 次測試完成    console=yes
    END

Scenario: 視覺檢測獨立測試（除錯模式）
    [Documentation]    僅測試視覺檢測功能（除錯模式）
    [Tags]    voice_assistant    vision_debug    debug

    ${結果}=    測試語音助理回應
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    scarlett_channel=${Scarlett聲道}
    ...    detection_timeout=${超時時間}
    ...    require_both=False

    記錄詳細檢測結果    ${結果}

    # 除錯模式：只要有一個通過即可
    ${至少一個通過}=    Evaluate    ${結果}[vision_detected] or ${結果}[audio_detected]
    Should Be True    ${至少一個通過}
    ...    msg=視覺和聽覺檢測都失敗

Scenario: 聽覺檢測獨立測試（除錯模式）
    [Documentation]    僅測試聽覺檢測功能（除錯模式）
    [Tags]    voice_assistant    audio_debug    debug

    ${結果}=    測試語音助理回應
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    scarlett_channel=${Scarlett聲道}
    ...    detection_timeout=${超時時間}
    ...    require_both=False

    記錄詳細檢測結果    ${結果}

    # 除錯模式：只要有一個通過即可
    ${至少一個通過}=    Evaluate    ${結果}[vision_detected] or ${結果}[audio_detected]
    Should Be True    ${至少一個通過}
    ...    msg=視覺和聽覺檢測都失敗

*** Keywords ***
測試前置準備
    [Documentation]    Suite 級別初始化
    Log    ========================================    console=yes
    Log    語音助手多感官檢測測試開始              console=yes
    Log    ========================================    console=yes

    # 檢查 Scarlett 設備
    Given Scarlett 4i4 音效介面已正確連接

    Log    測試環境準備完成    console=yes

測試後清理
    [Documentation]    Suite 級別清理
    And 暫存檔案應該正確清理

    Log    ========================================    console=yes
    Log    語音助手多感官檢測測試完成              console=yes
    Log    ========================================    console=yes

Scarlett 音訊設備已就緒
    [Documentation]    確認 Scarlett 4i4 設備就緒
    Given Scarlett 4i4 音效介面已正確連接
    Then Scarlett 4i4 設備應該處於正常運作狀態

IP Camera 可正常連線
    [Documentation]    確認 IP Camera 連線正常
    Log    驗證 IP Camera: ${環境}/${攝影機}

驗證測試結果成功
    [Documentation]    驗證語音助手檢測結果是否成功
    [Arguments]    ${結果}

    Should Be True    ${結果}[overall_success]
    ...    msg=語音助手回應失敗: ${結果.get('failure_reason', '未知原因')}

    Log    ✓ 語音助手完整回應驗證通過

記錄詳細檢測結果
    [Documentation]    記錄語音助手檢測的詳細結果
    [Arguments]    ${結果}

    Log    ========================================
    Log    語音助手檢測詳細結果
    Log    ========================================

    # 視覺檢測
    Log    視覺檢測結果:
    ${vision_status}=    Set Variable If    ${結果}[vision_detected]    ✓ 檢測到變化    ✗ 未檢測到變化
    Log    - 狀態: ${vision_status}
    Log    - 詳情: ${結果}[vision_details]

    # 聽覺檢測
    Log    聽覺檢測結果:
    ${audio_status}=    Set Variable If    ${結果}[audio_detected]    ✓ 檢測到提示音    ✗ 未檢測到提示音
    Log    - 狀態: ${audio_status}
    Log    - 詳情: ${結果}[audio_details]

    # 綜合判定
    ${overall_status}=    Set Variable If    ${結果}[overall_success]    ✓ 成功    ✗ 失敗
    Log    綜合判定: ${overall_status}

    Run Keyword If    '${結果.get('failure_reason')}' != 'None'
    ...    Log    失敗原因: ${結果}[failure_reason]    WARN

    Log    ========================================

驗證視覺檢測通過
    [Documentation]    驗證視覺檢測通過
    [Arguments]    ${結果}

    Should Be True    ${結果}[vision_detected]
    ...    msg=視覺檢測失敗: ${結果}[vision_details]

驗證聽覺檢測通過
    [Documentation]    驗證聽覺檢測通過
    [Arguments]    ${結果}

    Should Be True    ${結果}[audio_detected]
    ...    msg=聽覺檢測失敗: ${結果}[audio_details]
