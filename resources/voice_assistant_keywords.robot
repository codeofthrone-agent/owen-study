*** Settings ***
Documentation    語音助手多感官檢測關鍵字資源
...
...    提供語音助手完整回應測試的輔助關鍵字。
...
Library          ../libraries/multimodal_detection/VoiceAssistantDetection.py

*** Keywords ***
測試語音助手完整回應
    [Documentation]    測試語音助手是否同時具備視覺和聽覺回應
    ...
    ...    驗證邏輯：視覺 AND 聽覺都必須通過
    ...
    ...    參數：
    ...    - 喚醒詞: 要播放的喚醒詞（如 "Hey Power Pro"）
    ...    - 環境: IP Camera 環境名稱
    ...    - 攝影機: IP Camera 名稱
    ...    - 參考聲音: 要檢測的提示音（預設: 登登）
    ...    - 超時: 檢測超時時間（秒）
    ...
    ...    回傳：檢測結果字典
    [Arguments]    ${喚醒詞}    ${環境}    ${攝影機}    ${參考聲音}=登登    ${超時}=10

    Log    開始測試語音助手完整回應
    Log    喚醒詞: ${喚醒詞}
    Log    IP Camera: ${環境}/${攝影機}
    Log    參考聲音: ${參考聲音}
    Log    超時時間: ${超時}秒

    ${結果}=    測試語音助理回應
    ...    ${喚醒詞}
    ...    ${環境}
    ...    ${攝影機}
    ...    ${參考聲音}
    ...    1
    ...    ${超時}
    ...    True

    RETURN    ${結果}

驗證語音助手完整回應成功
    [Documentation]    驗證語音助手同時具備視覺和聽覺回應
    ...
    ...    驗證標準：
    ...    1. 視覺檢測通過（螢幕變亮）
    ...    2. 聽覺檢測通過（偵測到提示音）
    ...    3. 綜合判定為成功
    [Arguments]    ${結果}

    # 1. 驗證視覺回應
    Should Be True    ${結果}[vision_detected]
    ...    msg=視覺檢測失敗: ${結果}[vision_details]

    # 2. 驗證聽覺回應
    Should Be True    ${結果}[audio_detected]
    ...    msg=聽覺檢測失敗: ${結果}[audio_details]

    # 3. 驗證綜合判定
    Should Be True    ${結果}[overall_success]
    ...    msg=語音助手回應失敗: ${結果.get('failure_reason', '未知原因')}

    Log    ✓ 語音助手完整回應驗證通過

記錄檢測詳細資料
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

驗證視覺和聽覺都有回應
    [Documentation]    明確驗證視覺和聽覺都有檢測到（別名關鍵字）
    [Arguments]    ${結果}

    驗證語音助手完整回應成功    ${結果}

設定檢測參數
    [Documentation]    設定檢測參數
    [Arguments]    ${環境}    ${攝影機}    ${參考聲音}=登登    ${超時}=10

    Set Suite Variable    ${環境}
    Set Suite Variable    ${攝影機}
    Set Suite Variable    ${參考聲音}
    Set Suite Variable    ${超時}

    Log    檢測參數已設定:
    Log    - 環境: ${環境}
    Log    - 攝影機: ${攝影機}
    Log    - 參考聲音: ${參考聲音}
    Log    - 超時: ${超時}秒

驗證檢測結果符合預期
    [Documentation]    驗證檢測結果是否符合預期
    [Arguments]    ${結果}    ${預期視覺}    ${預期聽覺}

    Should Be Equal    ${結果}[vision_detected]    ${預期視覺}
    ...    msg=視覺檢測結果不符合預期

    Should Be Equal    ${結果}[audio_detected]    ${預期聽覺}
    ...    msg=聽覺檢測結果不符合預期

    Log    ✓ 檢測結果符合預期

等待語音助手恢復
    [Documentation]    等待語音助手恢復到待命狀態
    [Arguments]    ${等待時間}=5

    Log    等待語音助手恢復 (${等待時間}秒)...
    Sleep    ${等待時間}s
    Log    ✓ 語音助手已恢復

清理檢測資源
    [Documentation]    清理檢測使用的資源
    Log    清理檢測資源...
    # 這裡可以加入清理邏輯
    Log    ✓ 資源清理完成
