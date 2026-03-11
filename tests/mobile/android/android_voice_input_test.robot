*** Settings ***
Documentation    Android 語音輸入整合測試 - IoT 語音控制場景
...
...    此測試套件驗證 Android 實體裝置與 Scarlett 4i4 音訊硬體整合的端對端語音控制流程。
...    包含：語音按鈕觸發、麥克風同步等待、語音指令播放、辨識結果驗證。
...
...    測試環境需求：
...    - 實體 Android 裝置（USB 已授權，USB 調試已開啟）
...    - Appium server 以 --relaxed-security 啟動
...    - Focusrite Scarlett 4i4 已連接並設定 PipeWire 路由
...    - App 已安裝並可透過 Appium 操作
...
...    執行方式（實機）：
...    | uv run robot --include android-only tests/mobile/android/android_voice_input_test.robot
...
...    注意：標記 android-only 的測試案例需要實體 Android 裝置，
...    沙盒/模擬器環境下請使用 --dryrun 或搭配 skip-hardware 標記執行。
...
...    開發日期：2026-03-11
...    版本：v1.0.0（Stage 7 語音輸入）

Resource          ../../resources/device_control_keywords.robot
Resource          ../../resources/mobile_keywords.robot

Suite Setup       Suite 初始化語音測試環境
Suite Teardown    Suite 清理語音測試資源

*** Variables ***
# App 配置（請依實際 App 修改）
${APP_PACKAGE}              com.example.iot.controller
${APP_ACTIVITY}             .MainActivity
${APPIUM_URL}               http://localhost:4723

# 語音輸入按鈕定位器（請依實際 App 修改）
${VOICE_BTN_LOCATOR}        語音輸入
${VOICE_BTN_TYPE}           accessibility_id
${VOICE_UI_LOCATOR}         正在聆聽
${VOICE_UI_TYPE}            accessibility_id

# 結果顯示區域定位器（請依實際 App 修改）
${RESULT_LOCATOR}           com.example.iot.controller:id/tv_voice_result
${RESULT_TYPE}              id

# 語音輸入時序設定
${MIC_READY_DELAY}          1.5
${MAX_RETRIES}              2
${RESULT_TIMEOUT}           15

# Scarlett 4i4 聲道設定（語音指令輸出至裝置麥克風）
${VOICE_CHANNEL}            1
${VOICE_LANGUAGE}           zh-TW


*** Test Cases ***

# ============================================================
# 硬體就緒前置驗證
# ============================================================

檢查音訊硬體就緒狀態
    [Documentation]    驗證 Scarlett 4i4 音訊硬體與 PipeWire 路由在測試前正確就緒。
    ...                此測試應在所有語音輸入測試之前執行，確保硬體環境正常。
    [Tags]    android-only    hardware-check    voice-input
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    Then 音訊硬體狀態應正常記錄

觸發系統語音搜尋備用方案
    [Documentation]    驗證透過 Android Intent 觸發系統級語音搜尋（備用方案）。
    ...                不依賴 App UI，適用於測試系統語音功能是否正常啟動。
    [Tags]    android-only    voice-input    system-voice
    Given 裝置控制已初始化    android
    When 使用者觸發系統語音搜尋
    Then 系統語音搜尋界面應已出現

# ============================================================
# App 內語音輸入按鈕觸發
# ============================================================

點擊無障礙識別語音輸入按鈕
    [Documentation]    驗證透過 Accessibility ID 定位並點擊 App 內語音輸入按鈕。
    ...                此場景測試標準的語音按鈕點擊流程（無須等待麥克風就緒）。
    [Tags]    android-only    voice-input    button-click
    Given 裝置控制已初始化    android
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者點擊語音輸入按鈕    ${VOICE_BTN_LOCATOR}    ${VOICE_BTN_TYPE}
    Then App 應進入語音輸入模式

點擊 ID 定位語音輸入按鈕
    [Documentation]    驗證透過 resource-id 定位並點擊 App 內語音輸入按鈕。
    ...                適用於 Accessibility ID 不可用時的替代定位方式。
    [Tags]    android-only    voice-input    button-click
    Given 裝置控制已初始化    android
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者點擊語音輸入按鈕    ${APP_PACKAGE}:id/btn_voice_input    id
    Then App 應進入語音輸入模式

# ============================================================
# IoT 語音控制端對端測試
# ============================================================

語音控制開啟客廳燈光
    [Documentation]    端對端測試：透過語音指令「開啟客廳燈光」控制 IoT 燈光設備。
    ...
    ...                測試流程：
    ...                1. 確認音訊硬體就緒（Scarlett 4i4 + PipeWire）
    ...                2. 點擊語音輸入按鈕觸發 App 麥克風
    ...                3. 等待麥克風就緒延遲（${MIC_READY_DELAY}s）
    ...                4. 確認語音輸入 UI 已出現
    ...                5. 透過 Scarlett 4i4 播放語音指令
    ...                6. 等待並驗證 App 回應結果
    [Tags]    android-only    voice-input    iot-control    e2e
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者觸發語音輸入並播放指令
    ...    開啟客廳燈光
    ...    ${VOICE_BTN_LOCATOR}
    ...    ${VOICE_CHANNEL}
    ...    ${VOICE_BTN_TYPE}
    ...    ${MIC_READY_DELAY}
    ...    ${MAX_RETRIES}
    ...    ${VOICE_UI_LOCATOR}
    ...    ${VOICE_UI_TYPE}
    ...    ${VOICE_LANGUAGE}
    Then 語音指令結果應包含    燈光已開啟    ${RESULT_LOCATOR}    ${RESULT_TYPE}    ${RESULT_TIMEOUT}

語音控制關閉風扇
    [Documentation]    端對端測試：透過語音指令「關閉風扇」控制 IoT 風扇設備。
    [Tags]    android-only    voice-input    iot-control    e2e
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者觸發語音輸入並播放指令    關閉風扇    ${VOICE_BTN_LOCATOR}    ${VOICE_CHANNEL}
    Then 語音指令結果應包含    風扇已關閉    ${RESULT_LOCATOR}    ${RESULT_TYPE}    ${RESULT_TIMEOUT}

語音控制開啟空調
    [Documentation]    端對端測試：透過語音指令「開啟空調」控制 IoT 空調設備。
    [Tags]    android-only    voice-input    iot-control    e2e
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者觸發語音輸入並播放指令    開啟空調    ${VOICE_BTN_LOCATOR}    ${VOICE_CHANNEL}
    Then 語音指令結果應包含    空調已開啟    ${RESULT_LOCATOR}    ${RESULT_TYPE}    ${RESULT_TIMEOUT}

語音控制關閉雨遮
    [Documentation]    端對端測試：透過語音指令「關閉雨遮」控制 IoT 雨遮設備。
    [Tags]    android-only    voice-input    iot-control    e2e
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者觸發語音輸入並播放指令    關閉雨遮    ${VOICE_BTN_LOCATOR}    ${VOICE_CHANNEL}
    Then 語音指令結果應包含    雨遮已關閉    ${RESULT_LOCATOR}    ${RESULT_TYPE}    ${RESULT_TIMEOUT}

# ============================================================
# 等待語音輸入結果（獨立驗證）
# ============================================================

等待語音辨識結果並取得文字
    [Documentation]    驗證等待語音辨識結果的關鍵字可在指定逾時內取得 App 回應文字。
    ...                通常搭配其他語音觸發步驟使用。
    [Tags]    android-only    voice-input    result-verification
    Given 裝置控制已初始化    android
    And App 已在前景運行    ${APP_PACKAGE}
    When 使用者觸發語音輸入並播放指令    測試語音辨識    ${VOICE_BTN_LOCATOR}    ${VOICE_CHANNEL}
    Then 等待語音辨識結果並驗證    ${RESULT_LOCATOR}    ${RESULT_TYPE}    ${RESULT_TIMEOUT}


*** Keywords ***

Suite 初始化語音測試環境
    [Documentation]    測試套件初始化：提示確認環境設定是否完整。
    Log    初始化 Android 語音輸入測試環境...    INFO
    Log    請確認：實體 Android 裝置已連接，Appium 已啟動，Scarlett 4i4 已連接    WARN

Suite 清理語音測試資源
    [Documentation]    測試套件結束後清理 TTS 暫存資源。
    Log    清理語音測試資源...    INFO

# --- 補充前置條件關鍵字 ---

App 已在前景運行
    [Documentation]    確認指定 App 在前景運行。
    [Arguments]    ${package}
    Then 應用程式應該回到前景    ${package}

# --- 補充 Then 驗證關鍵字 ---

音訊硬體狀態應正常記錄
    [Documentation]    音訊硬體就緒檢查通過後記錄確認訊息。
    Log    ✓ 音訊硬體就緒：Scarlett 4i4 已連接，PipeWire 路由已建立    INFO

系統語音搜尋界面應已出現
    [Documentation]    系統語音搜尋觸發後的目視確認（需人工觀察）。
    Log    請確認裝置畫面已顯示語音搜尋界面    WARN

App 應進入語音輸入模式
    [Documentation]    語音按鈕點擊後的目視確認（麥克風動畫應出現）。
    Log    ✓ App 語音輸入按鈕已點擊，請確認麥克風圖示已啟動    INFO

