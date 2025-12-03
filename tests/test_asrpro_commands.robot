*** Settings ***
Documentation    Voice Control TTS Test Cases - ASR Pro Voice Commands
...              語音控制 TTS 測試案例 - ASR Pro 語音指令測試
...
...              測試重點:
...              1. 語音命令觸發後，檢測 UART 日誌中的語音回應
...              2. 驗證回應數量恰好符合預期（不多不少）
...              3. 驗證回應在指定時間內完成（預設 5 秒）
...              4. 支援單一回應和多個回應組合的測試
...
...              失敗情境:
...              - 在超時時間內沒有收到任何語音回應 → FAIL
...              - 收到的語音回應數量少於預期 → FAIL
...              - 收到的語音回應數量多於預期 → FAIL
...              - 語音回應的檔案名稱不符合預期 → FAIL

Library    ../libraries/voice_control/VoiceControlKeywords.py
Library    BuiltIn

Suite Setup    測試套件初始化
Suite Teardown    測試套件清理

*** Keywords ***
測試套件初始化
    [Documentation]    初始化測試套件所需的資源
    Log    ========================================
    Log    開始 ASR Pro 語音指令測試套件
    Log    ========================================
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given UART 日誌監控器已初始化
    Log    ✓ 測試套件初始化完成

測試套件清理
    [Documentation]    清理測試套件使用的資源
    When 使用者停止 UART 背景監控
    Log    ✓ 測試套件清理完成

*** Test Cases ***
Scenario: 測試 kws_answer
    [Documentation]    測試喚醒詞是否正確觸發
    ...                預期回應: 1 個語音檔案 (kws_answer.mp3)
    [Tags]    voice    tts    asrpro    propane

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "kws_answer.mp3"

# Scenario: 測試 Propane Tank Levels 語音指令
#     #TODO 測試回應不應該是44-1
#     [Documentation]    測試查詢丙烷罐液位的語音指令
#     ...                預期回應: 1 個語音檔案 (cmd_044-1.mp3)
#     [Tags]    voice    tts    asrpro    propane

#     # 前置條件
#     Given 音訊輸出聲道 "1" 已準備就緒
#     And 清空 UART 事件記錄

#     # 啟動 UART 監控
#     When 使用者啟動 UART 背景監控

#     # 執行語音命令
#     When 使用者播放文字 "hey power pro" 到聲道 "1"
#     Sleep    2
#     When 使用者播放文字 "Propane Tank Levels" 到聲道 "1"

#     # 驗證語音播放
#     Then 語音應該成功播放到指定聲道
#     And 語音品質應該符合標準
#     And 沒有音訊延遲或中斷

#     # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
#     Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "cmd_044-1.mp3"


Scenario: 測試 I'm Going Outside 語音指令
    [Documentation]    測試外出模式的語音指令
    ...                預期回應: 1 個語音檔案 (Enjoy_the_outdoors.mp3)
    [Tags]    voice    tts    asrpro    outside

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "I'm Going Outside" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Enjoy_the_outdoors.mp3"


Scenario: 測試 I'm Going Inside 語音指令
    [Documentation]    測試回到室內的語音指令
    ...                預期回應: 1 個語音檔案 (Welcome_back.mp3)
    [Tags]    voice    tts    asrpro    inside

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "I'm Going Inside" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Welcome_back.mp3"


Scenario: 測試 Turn on Bluetooth 語音指令
    [Documentation]    測試開啟藍牙的語音指令
    ...                預期回應: 1 個語音檔案 (Bluetooth_enable.mp3)
    [Tags]    voice    tts    asrpro    bluetooth

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控


    

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on Bluetooth" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Bluetooth_enable.mp3"




Scenario: 測試 Off Grid Mode 語音指令
    [Documentation]    測試離網模式的語音指令
    ...                預期回應: 1 個語音檔案 (Off_grid_mode.mp3)
    ...                ⚠️ 重要：恰好 1 個回應，超過或少於都會 FAIL
    [Tags]    voice    tts    asrpro    offgrid

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "3"
    Sleep    2
    When 使用者播放文字 "Off Grid Mode" 到聲道 "3"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應，多於或少於都會 FAIL）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3"


Scenario: 測試 Away Mode 語音指令
    [Documentation]    測試離開模式的語音指令
    ...                預期回應: 1 個語音檔案 (Away_mode.mp3)
    ...                ⚠️ 重要：恰好 1 個回應，超過或少於都會 FAIL
    [Tags]    voice    tts    asrpro    away

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Away Mode" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應，多於或少於都會 FAIL）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Away_mode.mp3"


Scenario: 測試 Returned to RV 語音指令
    [Documentation]    測試返回 RV 的語音指令
    ...                預期回應: 1 個語音檔案 (Welcome_back.mp3)
    ...                ⚠️ 重要：恰好 1 個回應，超過或少於都會 FAIL
    [Tags]    voice    tts    asrpro    return

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Returned to RV" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應，多於或少於都會 FAIL）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Welcome_back.mp3"


Scenario: 測試 Cold Weather Mode 語音指令
    [Documentation]    測試寒冷天氣模式的語音指令
    ...                預期回應: 1 個語音檔案 (Cold_weather_mode.mp3)
    ...                ⚠️ 重要：恰好 1 個回應，超過或少於都會 FAIL
    [Tags]    voice    tts    asrpro    weather

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Cold Weather Mode" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應，多於或少於都會 FAIL）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Cold_weather_mode.mp3"


Scenario: 測試 Warm Weather Mode 語音指令
    [Documentation]    測試溫暖天氣模式的語音指令
    ...                預期回應: 1 個語音檔案 (Warm_weather_mode.mp3)
    ...                ⚠️ 重要：恰好 1 個回應，超過或少於都會 FAIL
    [Tags]    voice    tts    asrpro    weather

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Warm Weather Mode" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應，多於或少於都會 FAIL）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Warm_weather_mode.mp3"


Scenario: 測試 Set Light Timer for 1 hour 語音指令
    [Documentation]    測試設定燈光計時器 1 小時的語音指令
    ...                預期回應: 3 個語音檔案 (Light_timer_set.mp3, 1.mp3, hours.mp3)
    ...                ⚠️ 重要：恰好 3 個回應，這是多個語音組合的測試案例
    ...                如果收到 1、2、4 或更多個回應都會 FAIL
    [Tags]    voice    tts    asrpro    timer    light    multi-response

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Set Light Timer for 1 hour" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 3 個回應，多於或少於都會 FAIL）
    # 注意：超時時間設為 10 秒，因為有多個語音檔案
    Then 應該在 "10" 秒內收到包含以下檔案的語音回應 "Light_timer_set.mp3,1.mp3,hours.mp3"


Scenario: 測試 Set Timer for 1 minutes 語音指令
    [Documentation]    測試設定計時器 1 分鐘的語音指令
    ...                預期回應: 3 個語音檔案 (timer_set.mp3, 1.mp3, minutes.mp3)
    ...                ⚠️ 重要：恰好 3 個回應，這是多個語音組合的測試案例
    ...                如果收到 1、2、4 或更多個回應都會 FAIL
    ...
    ...                注意：此測試不包含計時器到期後的 alarm 音效
    [Tags]    voice    tts    asrpro    timer    multi-response

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Set Timer for 1 minutes" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 3 個回應，多於或少於都會 FAIL）
    # 注意：超時時間設為 10 秒，因為有多個語音檔案
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "timer_set.mp3,1.mp3,minutes.mp3"
    Then 應該在 "65" 秒內收到包含以下檔案的語音回應 "clock_alarm.mp3"


Scenario: 測試 Stop Timer 語音指令
    [Documentation]    測試停止計時器的語音指令
    ...                預期回應: 1 個語音檔案 (stop_timer.mp3)
    [Tags]    voice    tts    asrpro    timer

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Stop Timer" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "stop_timer.mp3"

Scenario: 測試 Companion 語音指令
    [Documentation]    測試回到Companion的語音指令
    ...                預期回應: 1 個語音檔案 (Welcome_back.mp3)
    [Tags]    voice    tts    asrpro    i

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    # And 清空 UART 事件記錄

    # 啟動 UART 監控
    #When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    3
    When 使用者播放文字 "Companion" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "how to install power pro app" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

Scenario: 測試 Turn on Climate Control 語音指令
    [Documentation]    測試 Turn on Climate Control 的語音指令
    ...                預期回應: 1 個語音檔案 (Welcome_back.mp3)
    [Tags]    voice    tts    asrpro    i

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    # And 清空 UART 事件記錄

    # 啟動 UART 監控
    #When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn on Climate Control" 到聲道 "1"


    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

Scenario: 測試 Turn offClimate Control 語音指令
    [Documentation]    測試 Turn on Climate Control 的語音指令
    ...                預期回應: 1 個語音檔案 (Welcome_back.mp3)
    [Tags]    voice    tts    asrpro    i

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    # And 清空 UART 事件記錄

    # 啟動 UART 監控
    #When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Turn off Climate Control" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷

      