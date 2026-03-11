*** Settings ***
Documentation    平台無關裝置控制 BDD 關鍵字資源檔。封裝 Given-When-Then 關鍵字，
...              透過 DeviceControlKeywords 底層 Library 執行實際操作，
...              測試案例无需了解平台細節。
Library          BuiltIn
Library          ../libraries/mobile_testing/DeviceControlKeywords.py    WITH NAME    DeviceControl

*** Keywords ***
# ============================================================================
# Given - 前置條件
# ============================================================================

Given 裝置控制已初始化
    [Documentation]    透過底層裝置控制 Library 初始化跨平台控制能力。
    [Arguments]    ${platform}
    DeviceControl.初始化裝置控制    ${platform}
    Log    Given: ${platform} 裝置控制已初始化

Given 藍牙已開啟
    [Documentation]    確保藍牙處於開啟狀態。
    DeviceControl.開啟藍牙

Given WiFi 已開啟
    [Documentation]    確保 WiFi 處於開啟狀態。
    DeviceControl.開啟 WiFi

Given 行動數據已關閉
    [Documentation]    確保行動數據關閉以避免干擾測試。
    DeviceControl.關閉行動數據

Given 飛航模式已關閉
    [Documentation]    確保飛航模式為關閉狀態。
    DeviceControl.關閉飛航模式

Given 音訊硬體已就緒
    [Documentation]    確認 Scarlett 4i4 音訊硬體與 PipeWire 路由已就緒。
    ...                播放語音指令前必須執行，未就緒時立即拋出 RuntimeError。
    DeviceControl.檢查音訊硬體就緒

# ============================================================================
# When - 動作
# ============================================================================

When 使用者開啟藍牙
    [Documentation]    透過跨平台裝置控制開啟藍牙。
    DeviceControl.開啟藍牙

When 使用者關閉藍牙
    [Documentation]    關閉藍牙。
    DeviceControl.關閉藍牙

When 使用者開啟 WiFi
    [Documentation]    開啟 WiFi。
    DeviceControl.開啟 WiFi

When 使用者關閉 WiFi
    [Documentation]    關閉 WiFi。
    DeviceControl.關閉 WiFi

When 使用者開啟行動數據
    [Documentation]    開啟行動數據。
    DeviceControl.開啟行動數據

When 使用者關閉行動數據
    [Documentation]    關閉行動數據。
    DeviceControl.關閉行動數據

When 使用者開啟飛航模式
    [Documentation]    切換飛航模式為啟用。
    DeviceControl.開啟飛航模式

When 使用者關閉飛航模式
    [Documentation]    切換飛航模式為關閉。
    DeviceControl.關閉飛航模式

When 使用者調高音量
    [Documentation]    透過實體音量鍵調高一級。
    DeviceControl.調高音量

When 使用者調低音量
    [Documentation]    透過實體音量鍵調低一級。
    DeviceControl.調低音量

When 使用者靜音
    [Documentation]    將媒體音量靜音。
    DeviceControl.靜音

When 使用者設定媒體音量為
    [Documentation]    設定媒體音量至指定等級。
    [Arguments]    ${level}
    DeviceControl.設定媒體音量    ${level}

When 使用者將應用程式置於背景
    [Documentation]    將當前 App 送至背景並等待指定秒數（預設立即）。
    [Arguments]    ${seconds}=-1
    DeviceControl.將應用程式置於背景    ${seconds}

When 使用者恢復應用程式
    [Documentation]    從背景恢復指定 Package。
    [Arguments]    ${package}
    DeviceControl.啟動應用程式    ${package}

When 使用者從最近應用清除
    [Documentation]    在最近應用畫面滑掉當前 App。
    DeviceControl.從最近應用清除

When 使用者強制停止應用程式
    [Documentation]    強制停止指定 package。
    [Arguments]    ${package}
    DeviceControl.強制停止應用程式    ${package}

When 使用者點擊語音輸入按鈕
    [Documentation]    透過 UI 觸發 App 內語音輸入。
    ...                支援 accessibility_id / id / xpath 三種定位方式。
    [Arguments]    ${locator}    ${locator_type}=accessibility_id    ${timeout}=10
    DeviceControl.點擊語音輸入按鈕    ${locator}    ${locator_type}    ${timeout}

When 使用者觸發系統語音搜尋
    [Documentation]    使用 Android Intent 觸發系統級語音搜尋。
    DeviceControl.觸發系統語音搜尋

When 使用者觸發語音輸入並播放指令
    [Documentation]    完整語音觸發流程：硬體檢查→點擊按鈕→等待麥克風就緒→播放語音指令。
    [Arguments]
    ...    ${voice_text}
    ...    ${button_locator}
    ...    ${channel}=1
    ...    ${button_locator_type}=accessibility_id
    ...    ${mic_ready_delay}=1.5
    ...    ${max_retries}=2
    ...    ${voice_ui_locator}=${EMPTY}
    ...    ${voice_ui_locator_type}=accessibility_id
    ...    ${language}=zh-TW
    DeviceControl.觸發語音輸入並播放指令
    ...    ${voice_text}
    ...    ${button_locator}
    ...    ${channel}
    ...    ${button_locator_type}
    ...    ${mic_ready_delay}
    ...    ${max_retries}
    ...    ${voice_ui_locator}
    ...    ${voice_ui_locator_type}
    ...    ${language}

When 使用者等待語音輸入結果
    [Documentation]    等待指定元素顯示語音辨識結果，回傳辨識文字。
    [Arguments]    ${locator}    ${locator_type}=id    ${timeout}=10
    ${result}=    DeviceControl.等待語音輸入結果    ${locator}    ${locator_type}    ${timeout}
    RETURN    ${result}

# ============================================================================
# Then - 驗證
# ============================================================================

Then 藍牙應該為開啟狀態
    DeviceControl.藍牙應該為開啟狀態

Then 藍牙應該為關閉狀態
    DeviceControl.藍牙應該為關閉狀態

Then WiFi 應該為開啟狀態
    DeviceControl.WiFi 應該為開啟狀態

Then WiFi 應該為關閉狀態
    DeviceControl.WiFi 應該為關閉狀態

Then 行動數據應該為開啟狀態
    DeviceControl.行動數據應該為開啟狀態

Then 行動數據應該為關閉狀態
    DeviceControl.行動數據應該為關閉狀態

Then 飛航模式應該為啟用
    DeviceControl.飛航模式應該為開啟狀態

Then 飛航模式應該為關閉
    DeviceControl.飛航模式應該為關閉狀態

Then 應用程式應該回到前景
    [Arguments]    ${package}
    DeviceControl.應用程式應該在前景    ${package}

Then 語音指令結果應包含
    [Documentation]    驗證語音指令執行結果包含預期文字；不符時拋出 AssertionError 附帶建議。
    [Arguments]    ${expected_text}    ${result_locator}    ${result_locator_type}=id    ${timeout}=10
    DeviceControl.語音指令結果應包含    ${expected_text}    ${result_locator}    ${result_locator_type}    ${timeout}

Then 語音輸入結果應更新為
    [Arguments]    ${expected_text}
    驗證或等待尚未實作的關鍵字    驗證語音輸入結果    ${expected_text}

# ============================================================================
# Helpers - 尚未實作的底層關鍵字代理
# ============================================================================

呼叫或等待尚未實作的關鍵字
    [Arguments]    ${keyword_name}    @{args}
    ${status}    ${message}=    Run Keyword And Ignore Error    ${keyword_name}    @{args}
    Run Keyword If    '${status}' == 'PASS'    RETURN
    Fail    關鍵字 "${keyword_name}" 尚未實作：${message}

驗證或等待尚未實作的關鍵字
    [Arguments]    ${keyword_name}    @{args}
    呼叫或等待尚未實作的關鍵字    ${keyword_name}    @{args}
