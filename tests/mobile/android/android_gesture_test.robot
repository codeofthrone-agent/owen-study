*** Settings ***
Documentation    Android 進階手勢控制測試套件
...
...    驗證 AndroidGestureControl 透過 Appium mobile: 命令執行實體裝置的手勢操作，
...    涵蓋長按、精確滑動、座標點擊、雙擊與拖曳。
...
...    測試環境需求：
...    - 實體 Android 裝置（USB 已授權，USB 調試已開啟）
...    - Appium server 以 --relaxed-security 啟動
...    - UiAutomator2 driver 已安裝（版本 >= 2.0）
...    - 目標 App 已安裝，包含用於手勢測試的可互動元素
...
...    執行方式（實機）：
...    | uv run robot --include android-only tests/mobile/android/android_gesture_test.robot
...
...    注意：所有測試案例標記 android-only，iOS 目前尚未支援進階手勢功能。
...    座標值以 1080x2340 解析度裝置為基準，實際使用時請依裝置解析度調整。
...
...    開發日期：2026-03-11
...    版本：v1.0.0

Resource          ../../resources/gesture_control_keywords.robot

Suite Setup       Suite 初始化手勢控制測試
Suite Teardown    Suite 清理手勢控制測試

*** Variables ***
# App 配置（請依實際測試 App 修改）
${APP_PACKAGE}              com.example.test.app
${APP_ACTIVITY}             .MainActivity

# 手勢測試用元素定位器（請依實際 App 修改）
${LONG_PRESS_ELEMENT}       com.example.test.app:id/btn_long_press_target
${DRAG_SOURCE_ELEMENT}      com.example.test.app:id/drag_source
${DOUBLE_TAP_ELEMENT}       com.example.test.app:id/btn_double_tap

# 座標設定（以 1080x2340 解析度為基準）
${CENTER_X}                 540
${CENTER_Y}                 1170
${DRAG_END_X}               800
${DRAG_END_Y}               1000

# 手勢參數
${LONG_PRESS_DURATION}      1500
${SWIPE_PERCENT}            75
${DRAG_SPEED}               1000


*** Test Cases ***

# ============================================================
# 長按手勢
# ============================================================

長按元素（元素定位）
    [Documentation]    驗證透過元素定位器執行長按手勢。
    ...                使用 mobile: longClickGesture 命令，預設長按 1000ms。
    [Tags]    android-only    long-press    gesture
    Given 手勢控制已初始化    android
    When 使用者長按元素    ${LONG_PRESS_ELEMENT}
    Then 長按操作應成功完成

長按元素（自定義持續時間）
    [Documentation]    驗證長按手勢可透過 duration 參數調整持續時間（毫秒）。
    [Tags]    android-only    long-press    gesture
    Given 手勢控制已初始化    android
    When 使用者長按元素    ${LONG_PRESS_ELEMENT}    ${LONG_PRESS_DURATION}
    Then 長按操作應成功完成

長按座標
    [Documentation]    驗證透過螢幕座標執行長按手勢。
    ...                適用於無 ID 的元素或需要精確座標操作的場景。
    [Tags]    android-only    long-press    gesture
    Given 手勢控制已初始化    android
    When 使用者長按座標    ${CENTER_X}    ${CENTER_Y}    ${LONG_PRESS_DURATION}
    Then 長按操作應成功完成

# ============================================================
# 滑動手勢
# ============================================================

向上滑動螢幕
    [Documentation]    驗證向上滑動整個螢幕（預設 75% 距離）。
    ...                常用於捲動頁面、下拉刷新等操作。
    [Tags]    android-only    swipe    gesture
    Given 手勢控制已初始化    android
    When 使用者滑動螢幕    up
    Then 滑動操作應成功完成

向下滑動螢幕
    [Documentation]    驗證向下滑動整個螢幕（預設 75% 距離）。
    [Tags]    android-only    swipe    gesture
    Given 手勢控制已初始化    android
    When 使用者滑動螢幕    down
    Then 滑動操作應成功完成

向左滑動螢幕
    [Documentation]    驗證向左滑動整個螢幕。
    ...                常用於切換頁面、返回操作等場景。
    [Tags]    android-only    swipe    gesture
    Given 手勢控制已初始化    android
    When 使用者滑動螢幕    left
    Then 滑動操作應成功完成

向右滑動螢幕
    [Documentation]    驗證向右滑動整個螢幕。
    [Tags]    android-only    swipe    gesture
    Given 手勢控制已初始化    android
    When 使用者滑動螢幕    right
    Then 滑動操作應成功完成

在指定區域內滑動
    [Documentation]    驗證在指定矩形區域內執行精確滑動（不影響區域外元素）。
    ...                left=100, top=500, width=880, height=1000, 向上 75%。
    [Tags]    android-only    swipe    gesture
    Given 手勢控制已初始化    android
    When 使用者在區域內滑動    100    500    880    1000    up    ${SWIPE_PERCENT}
    Then 滑動操作應成功完成

# ============================================================
# 座標點擊
# ============================================================

點擊螢幕座標
    [Documentation]    驗證透過 mobile: clickGesture 精確點擊指定座標。
    ...                適用於無 ID 元素或需要精確座標點擊的場景。
    [Tags]    android-only    tap    gesture
    Given 手勢控制已初始化    android
    When 使用者點擊座標    ${CENTER_X}    ${CENTER_Y}
    Then 點擊操作應成功完成

點擊螢幕左上角
    [Documentation]    驗證點擊左上角座標（100, 200）。
    [Tags]    android-only    tap    gesture
    Given 手勢控制已初始化    android
    When 使用者點擊座標    100    200
    Then 點擊操作應成功完成

點擊螢幕右下角
    [Documentation]    驗證點擊右下角座標（980, 2100）。
    [Tags]    android-only    tap    gesture
    Given 手勢控制已初始化    android
    When 使用者點擊座標    980    2100
    Then 點擊操作應成功完成

# ============================================================
# 雙擊手勢
# ============================================================

雙擊元素
    [Documentation]    驗證對元素執行雙擊（mobile: doubleClickGesture）。
    ...                常用於縮放、選擇文字、觸發雙擊事件。
    [Tags]    android-only    double-tap    gesture
    Given 手勢控制已初始化    android
    When 使用者雙擊元素    ${DOUBLE_TAP_ELEMENT}
    Then 雙擊操作應成功完成

# ============================================================
# 拖曳手勢
# ============================================================

拖曳元素到指定座標
    [Documentation]    驗證將元素拖曳至目標座標（mobile: dragGesture）。
    ...                起點為 ${DRAG_SOURCE_ELEMENT}，終點為 (${DRAG_END_X}, ${DRAG_END_Y})。
    [Tags]    android-only    drag    gesture
    Given 手勢控制已初始化    android
    When 使用者拖曳元素到座標    ${DRAG_SOURCE_ELEMENT}    ${DRAG_END_X}    ${DRAG_END_Y}
    Then 拖曳操作應成功完成

拖曳元素（自定義速度）
    [Documentation]    驗證拖曳手勢可透過 speed 參數調整速度（預設 1000ms）。
    [Tags]    android-only    drag    gesture
    Given 手勢控制已初始化    android
    When 使用者拖曳元素到座標    ${DRAG_SOURCE_ELEMENT}    ${DRAG_END_X}    ${DRAG_END_Y}    ${DRAG_SPEED}
    Then 拖曳操作應成功完成

# ============================================================
# 複合手勢場景
# ============================================================

滑動後長按元素
    [Documentation]    驗證複合手勢：先滑動頁面找到目標，再長按。
    ...                模擬實際使用場景中需要先捲動才能找到目標元素的情況。
    [Tags]    android-only    composite-gesture    gesture
    Given 手勢控制已初始化    android
    When 使用者滑動螢幕    up
    When 使用者長按元素    ${LONG_PRESS_ELEMENT}
    Then 複合手勢操作應成功完成

點擊後雙擊驗證
    [Documentation]    驗證先單擊聚焦，再雙擊觸發動作的複合手勢。
    [Tags]    android-only    composite-gesture    gesture
    Given 手勢控制已初始化    android
    When 使用者點擊座標    ${CENTER_X}    ${CENTER_Y}
    When 使用者雙擊元素    ${DOUBLE_TAP_ELEMENT}
    Then 複合手勢操作應成功完成


*** Keywords ***

Suite 初始化手勢控制測試
    [Documentation]    測試套件初始化：提示確認環境。
    Log    初始化 Android 手勢控制測試環境...    INFO
    Log    請確認：實體 Android 裝置已連接，Appium UiAutomator2 driver 已安裝    WARN
    Log    座標值以 1080x2340 解析度為基準，如裝置解析度不同請調整變數    WARN

Suite 清理手勢控制測試
    [Documentation]    測試套件結束清理。
    Log    清理手勢控制測試環境...    INFO

# --- Then 驗證關鍵字（手勢執行成功確認）---
# 手勢操作本身不拋出例外即視為成功；實際驗證需在 App UI 層面進行

長按操作應成功完成
    [Documentation]    長按手勢執行成功確認（執行不拋出例外）。
    Log    ✓ 長按手勢已成功執行    INFO

滑動操作應成功完成
    [Documentation]    滑動手勢執行成功確認。
    Log    ✓ 滑動手勢已成功執行    INFO

點擊操作應成功完成
    [Documentation]    點擊手勢執行成功確認。
    Log    ✓ 座標點擊已成功執行    INFO

雙擊操作應成功完成
    [Documentation]    雙擊手勢執行成功確認。
    Log    ✓ 雙擊手勢已成功執行    INFO

拖曳操作應成功完成
    [Documentation]    拖曳手勢執行成功確認。
    Log    ✓ 拖曳手勢已成功執行    INFO

複合手勢操作應成功完成
    [Documentation]    複合手勢序列執行成功確認。
    Log    ✓ 複合手勢序列已成功執行    INFO
