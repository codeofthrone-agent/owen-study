*** Settings ***
Documentation    平台無關手勢控制 BDD 關鍵字資源檔，封裝常見長按/滑動/
...              點擊/拖曳等操作，避免測試案例暴露 Appium 實作細節。
Library          BuiltIn
Library          ../libraries/mobile_testing/GestureControlKeywords.py    WITH NAME    GestureControl

*** Keywords ***
# ============================================================================
# Given - 前置條件
# ============================================================================

Given 手勢控制已初始化
    [Documentation]    初始化手勢控制模組，根據平台載入對應實作。
    [Arguments]    ${platform}
    GestureControl.初始化手勢控制    ${platform}
    Log    Given: ${platform} 手勢控制已準備

# ============================================================================
# When - 動作
# ============================================================================

When 使用者長按元素
    [Documentation]    針對指定元素執行長按。
    [Arguments]    ${locator}    ${duration}=1000
    GestureControl.長按元素    ${locator}    ${duration}

When 使用者長按座標
    [Documentation]    針對指定座標執行長按。
    [Arguments]    ${x}    ${y}    ${duration}=1000
    GestureControl.長按座標    ${x}    ${y}    ${duration}

When 使用者滑動螢幕
    [Documentation]    依方向滑動整個螢幕。
    [Arguments]    ${direction}    ${percent}=0.75
    GestureControl.滑動螢幕    ${direction}    ${percent}

When 使用者在區域內滑動
    [Documentation]    在指定矩形區域內滑動。
    [Arguments]    ${left}    ${top}    ${width}    ${height}    ${direction}    ${percent}=0.75
    GestureControl.在區域內滑動    ${left}    ${top}    ${width}    ${height}    ${direction}    ${percent}

When 使用者點擊座標
    [Documentation]    在指定座標單擊。
    [Arguments]    ${x}    ${y}
    GestureControl.點擊座標    ${x}    ${y}

When 使用者雙擊元素
    [Documentation]    對元素執行雙擊。
    [Arguments]    ${locator}
    GestureControl.雙擊元素    ${locator}

When 使用者拖曳元素到座標
    [Documentation]    將元素拖曳至指定終點。
    [Arguments]    ${locator}    ${end_x}    ${end_y}    ${speed}=1000
    GestureControl.拖曳元素    ${locator}    ${end_x}    ${end_y}    ${speed}

# ============================================================================
# Then - 驗證
# ============================================================================

Then 元素應該被長按
    [Documentation]    驗證元素長按後的預期效果（由底層實作負責判斷）。
    [Arguments]    ${locator}
    呼叫或等待尚未實作的手勢關鍵字    驗證元素長按結果    ${locator}

Then 元素應該被拖曳到座標
    [Documentation]    驗證元素已拖曳至目標位置。
    [Arguments]    ${locator}    ${end_x}    ${end_y}
    呼叫或等待尚未實作的手勢關鍵字    驗證拖曳結果    ${locator}    ${end_x}    ${end_y}

# ============================================================================
# Helpers - 尚未實作的手勢驗證代理
# ============================================================================

呼叫或等待尚未實作的手勢關鍵字
    [Arguments]    ${keyword_name}    @{args}
    ${status}    ${message}=    Run Keyword And Ignore Error    ${keyword_name}    @{args}
    Run Keyword If    '${status}' == 'PASS'    RETURN
    Fail    手勢驗證關鍵字 "${keyword_name}" 尚未實作：${message}
