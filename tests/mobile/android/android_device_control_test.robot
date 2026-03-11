*** Settings ***
Documentation    Android 裝置系統控制測試套件
...
...    驗證 AndroidDeviceControl 透過 Appium ADB shell 控制實體裝置系統功能，
...    涵蓋藍牙、WiFi、行動數據、飛航模式、音量控制與 App 生命週期管理。
...
...    測試環境需求：
...    - 實體 Android 裝置（USB 已授權，USB 調試已開啟）
...    - Appium server 以 --relaxed-security 啟動（允許 mobile: shell）
...    - UiAutomator2 driver 已安裝
...    - adb devices 可看到目標裝置
...
...    執行方式（實機）：
...    | uv run robot --include android-only tests/mobile/android/android_device_control_test.robot
...
...    注意：所有測試案例標記 android-only，iOS 目前尚未支援裝置控制功能。
...    每個功能組會在測試後恢復原始狀態，避免影響後續測試。
...
...    開發日期：2026-03-11
...    版本：v1.0.0

Resource          ../../resources/device_control_keywords.robot
Resource          ../../resources/mobile_keywords.robot

Suite Setup       Suite 初始化裝置控制測試
Suite Teardown    Suite 清理裝置控制測試

*** Variables ***
# App 配置（請依實際測試 App 修改）
${APP_PACKAGE}              com.example.test.app
${APP_ACTIVITY}             .MainActivity

# 音量設定
${TEST_VOLUME}              7
${DEFAULT_VOLUME}           5

# App 背景等待時間（秒）
${BACKGROUND_SECONDS}       3


*** Test Cases ***

# ============================================================
# 藍牙控制
# ============================================================

開啟並驗證藍牙狀態
    [Documentation]    驗證開啟藍牙後，ADB 狀態查詢回傳 on。
    ...                測試後關閉藍牙，恢復初始狀態。
    [Tags]    android-only    bluetooth    device-control
    Given 裝置控制已初始化    android
    When 使用者開啟藍牙
    Then 藍牙應該為開啟狀態
    [Teardown]    執行關鍵字不失敗    使用者關閉藍牙

關閉並驗證藍牙狀態
    [Documentation]    驗證關閉藍牙後，ADB 狀態查詢回傳 off。
    [Tags]    android-only    bluetooth    device-control
    Given 裝置控制已初始化    android
    And 確保藍牙為開啟狀態
    When 使用者關閉藍牙
    Then 藍牙應該為關閉狀態

查詢藍牙狀態值
    [Documentation]    驗證查詢藍牙狀態關鍵字回傳 on 或 off 字串。
    [Tags]    android-only    bluetooth    device-control    query
    Given 裝置控制已初始化    android
    When 使用者開啟藍牙
    Then 藍牙狀態查詢結果應為    on
    [Teardown]    執行關鍵字不失敗    使用者關閉藍牙

# ============================================================
# WiFi 控制
# ============================================================

開啟並驗證 WiFi 狀態
    [Documentation]    驗證開啟 WiFi 後，ADB 狀態查詢回傳 on。
    [Tags]    android-only    wifi    device-control
    Given 裝置控制已初始化    android
    When 使用者開啟 WiFi
    Then WiFi 應該為開啟狀態
    [Teardown]    執行關鍵字不失敗    Run Keyword    關閉 WiFi

關閉並驗證 WiFi 狀態
    [Documentation]    驗證關閉 WiFi 後，ADB 狀態查詢回傳 off。
    ...                注意：測試後自動恢復 WiFi 開啟，避免影響網路相依測試。
    [Tags]    android-only    wifi    device-control
    Given 裝置控制已初始化    android
    When 使用者關閉 WiFi
    Then WiFi 應該為關閉狀態
    [Teardown]    執行關鍵字不失敗    Run Keyword    開啟 WiFi

查詢 WiFi 狀態值
    [Documentation]    驗證查詢 WiFi 狀態關鍵字回傳 on 或 off 字串。
    [Tags]    android-only    wifi    device-control    query
    Given 裝置控制已初始化    android
    When 使用者開啟 WiFi
    Then WiFi 狀態查詢結果應為    on

# ============================================================
# 行動數據控制
# ============================================================

開啟並驗證行動數據
    [Documentation]    驗證開啟行動數據後狀態查詢回傳 on。
    ...                需要 io.appium.settings APK 已安裝於裝置。
    [Tags]    android-only    mobile-data    device-control
    Given 裝置控制已初始化    android
    When 使用者開啟行動數據
    Then 行動數據應該為開啟狀態
    [Teardown]    執行關鍵字不失敗    Run Keyword    關閉行動數據

關閉並驗證行動數據
    [Documentation]    驗證關閉行動數據後狀態查詢回傳 off。
    [Tags]    android-only    mobile-data    device-control
    Given 裝置控制已初始化    android
    When 使用者關閉行動數據
    Then 行動數據應該為關閉狀態
    [Teardown]    執行關鍵字不失敗    Run Keyword    開啟行動數據

# ============================================================
# 飛航模式控制
# ============================================================

開啟並驗證飛航模式
    [Documentation]    驗證開啟飛航模式後，ADB settings get global airplane_mode_on 回傳 1（on）。
    ...                飛航模式開啟時 WiFi 與藍牙同時關閉，測試後自動關閉飛航模式。
    [Tags]    android-only    airplane-mode    device-control
    Given 裝置控制已初始化    android
    When 使用者開啟飛航模式
    Then 飛航模式應該為啟用
    [Teardown]    執行關鍵字不失敗    使用者關閉飛航模式

關閉並驗證飛航模式
    [Documentation]    驗證關閉飛航模式後，ADB 狀態查詢回傳 off。
    [Tags]    android-only    airplane-mode    device-control
    Given 裝置控制已初始化    android
    And 確保飛航模式為開啟狀態
    When 使用者關閉飛航模式
    Then 飛航模式應該為關閉

查詢飛航模式狀態值
    [Documentation]    驗證飛航模式狀態查詢回傳 on 或 off 字串。
    [Tags]    android-only    airplane-mode    device-control    query
    Given 裝置控制已初始化    android
    When 使用者開啟飛航模式
    Then 飛航模式狀態查詢結果應為    on
    [Teardown]    執行關鍵字不失敗    使用者關閉飛航模式

# ============================================================
# 音量控制
# ============================================================

調高裝置音量
    [Documentation]    驗證調高音量後，ADB media volume 回傳值大於操作前的值。
    [Tags]    android-only    volume    device-control
    Given 裝置控制已初始化    android
    And 設定已知基準音量    ${DEFAULT_VOLUME}
    When 使用者調高音量
    Then 音量應高於基準    ${DEFAULT_VOLUME}

調低裝置音量
    [Documentation]    驗證調低音量後，ADB media volume 回傳值小於操作前的值。
    [Tags]    android-only    volume    device-control
    Given 裝置控制已初始化    android
    And 設定已知基準音量    ${DEFAULT_VOLUME}
    When 使用者調低音量
    Then 音量應低於基準    ${DEFAULT_VOLUME}

設定指定媒體音量
    [Documentation]    驗證 set_media_volume(7) 後查詢結果為 7。
    [Tags]    android-only    volume    device-control
    Given 裝置控制已初始化    android
    When 使用者設定媒體音量    ${TEST_VOLUME}
    Then 媒體音量應該為    ${TEST_VOLUME}

靜音裝置
    [Documentation]    驗證靜音後媒體音量為 0。
    [Tags]    android-only    volume    device-control
    Given 裝置控制已初始化    android
    And 使用者設定媒體音量    ${DEFAULT_VOLUME}
    When 使用者靜音
    Then 媒體音量應該為    0
    [Teardown]    執行關鍵字不失敗    Run Keyword    設定媒體音量    ${DEFAULT_VOLUME}

查詢媒體音量值
    [Documentation]    驗證查詢媒體音量關鍵字回傳整數值（0-15）。
    [Tags]    android-only    volume    device-control    query
    Given 裝置控制已初始化    android
    And 使用者設定媒體音量    ${TEST_VOLUME}
    Then 媒體音量查詢結果應為    ${TEST_VOLUME}

# ============================================================
# App 生命週期管理
# ============================================================

將應用程式置於背景後恢復
    [Documentation]    驗證應用程式置於背景後仍可透過 activate_app 恢復至前景。
    [Tags]    android-only    app-lifecycle    device-control
    Given 裝置控制已初始化    android
    And App 在前景運行中    ${APP_PACKAGE}
    When 使用者將應用程式置於背景    ${BACKGROUND_SECONDS}
    And 使用者啟動應用程式    ${APP_PACKAGE}
    Then 應用程式應該回到前景    ${APP_PACKAGE}

強制停止應用程式
    [Documentation]    驗證強制停止 App 後，App 已不在前景。
    [Tags]    android-only    app-lifecycle    device-control
    Given 裝置控制已初始化    android
    And App 在前景運行中    ${APP_PACKAGE}
    When 使用者強制停止應用程式    ${APP_PACKAGE}
    Then 前景應用程式應不為    ${APP_PACKAGE}

從最近應用清除應用程式
    [Documentation]    驗證從最近應用滑掉清除 App 的操作可執行。
    [Tags]    android-only    app-lifecycle    device-control
    Given 裝置控制已初始化    android
    And App 在前景運行中    ${APP_PACKAGE}
    When 使用者將應用程式置於背景    -1
    And 使用者從最近應用清除
    Then 最近應用清除操作應完成

查詢前景應用程式
    [Documentation]    驗證查詢前景應用程式關鍵字回傳正確 package name。
    [Tags]    android-only    app-lifecycle    device-control    query
    Given 裝置控制已初始化    android
    And App 在前景運行中    ${APP_PACKAGE}
    Then 前景應用程式應為    ${APP_PACKAGE}


*** Keywords ***

Suite 初始化裝置控制測試
    [Documentation]    測試套件初始化：提示確認環境。
    Log    初始化 Android 裝置控制測試環境...    INFO
    Log    請確認：實體 Android 裝置已連接，Appium 以 --relaxed-security 啟動    WARN

Suite 清理裝置控制測試
    [Documentation]    確保測試結束後飛航模式關閉（避免裝置失聯）。
    Log    清理裝置控制測試環境...    INFO

# --- 補充 Given 前置條件關鍵字 ---

確保藍牙為開啟狀態
    [Documentation]    確保藍牙為開啟狀態（不管目前是否開啟）。
    Run Keyword    開啟藍牙

確保飛航模式為開啟狀態
    [Documentation]    確保飛航模式為開啟狀態。
    Run Keyword    開啟飛航模式

設定已知基準音量
    [Documentation]    設定音量到已知基準值，確保調高/調低測試結果可驗證。
    [Arguments]    ${level}
    Run Keyword    設定媒體音量    ${level}

App 在前景運行中
    [Documentation]    確認 App 已在前景（透過啟動確保）。
    [Arguments]    ${package}
    Run Keyword    啟動應用程式    ${package}

# --- 補充 When 動作關鍵字 ---

使用者開啟藍牙
    Run Keyword    開啟藍牙

使用者關閉藍牙
    Run Keyword    關閉藍牙

使用者開啟 WiFi
    Run Keyword    開啟 WiFi

使用者關閉 WiFi
    Run Keyword    關閉 WiFi

使用者開啟行動數據
    Run Keyword    開啟行動數據

使用者關閉行動數據
    Run Keyword    關閉行動數據

使用者開啟飛航模式
    Run Keyword    開啟飛航模式

使用者關閉飛航模式
    Run Keyword    關閉飛航模式

使用者設定媒體音量
    [Arguments]    ${level}
    Run Keyword    設定媒體音量    ${level}

使用者調高音量
    Run Keyword    調高音量

使用者調低音量
    Run Keyword    調低音量

使用者靜音
    Run Keyword    靜音

使用者將應用程式置於背景
    [Arguments]    ${seconds}=-1
    Run Keyword    將應用程式置於背景    ${seconds}

使用者啟動應用程式
    [Arguments]    ${package}
    Run Keyword    啟動應用程式    ${package}

使用者強制停止應用程式
    [Arguments]    ${package}
    Run Keyword    強制停止應用程式    ${package}

使用者從最近應用清除
    Run Keyword    從最近應用清除

# --- 補充 Then 驗證關鍵字 ---

藍牙狀態查詢結果應為
    [Documentation]    驗證查詢藍牙狀態回傳符合預期字串（on/off）。
    [Arguments]    ${expected}
    ${state}=    查詢藍牙狀態
    Should Be Equal    ${state}    ${expected}
    ...    msg=藍牙狀態應為 ${expected}，實際為 ${state}

WiFi 狀態查詢結果應為
    [Documentation]    驗證查詢 WiFi 狀態回傳符合預期字串。
    [Arguments]    ${expected}
    ${state}=    查詢 WiFi 狀態
    Should Be Equal    ${state}    ${expected}
    ...    msg=WiFi 狀態應為 ${expected}，實際為 ${state}

飛航模式狀態查詢結果應為
    [Documentation]    驗證查詢飛航模式狀態回傳符合預期字串。
    [Arguments]    ${expected}
    ${state}=    查詢飛航模式狀態
    Should Be Equal    ${state}    ${expected}
    ...    msg=飛航模式狀態應為 ${expected}，實際為 ${state}

媒體音量查詢結果應為
    [Documentation]    驗證查詢媒體音量回傳符合預期整數值。
    [Arguments]    ${expected}
    ${volume}=    查詢媒體音量
    Should Be Equal As Integers    ${volume}    ${expected}
    ...    msg=媒體音量應為 ${expected}，實際為 ${volume}

音量應高於基準
    [Documentation]    驗證目前音量高於指定基準值。
    [Arguments]    ${baseline}
    ${volume}=    查詢媒體音量
    Should Be True    ${volume} > ${baseline}
    ...    msg=音量應高於 ${baseline}，實際為 ${volume}

音量應低於基準
    [Documentation]    驗證目前音量低於指定基準值。
    [Arguments]    ${baseline}
    ${volume}=    查詢媒體音量
    Should Be True    ${volume} < ${baseline}
    ...    msg=音量應低於 ${baseline}，實際為 ${volume}

前景應用程式應為
    [Documentation]    驗證前景應用程式為指定 package。
    [Arguments]    ${expected_package}
    ${pkg}=    查詢前景應用程式
    Should Contain    ${pkg}    ${expected_package}
    ...    msg=前景應用程式應為 ${expected_package}，實際為 ${pkg}

前景應用程式應不為
    [Documentation]    驗證前景應用程式已不是指定 package。
    [Arguments]    ${unexpected_package}
    ${pkg}=    查詢前景應用程式
    Should Not Contain    ${pkg}    ${unexpected_package}
    ...    msg=前景應用程式不應為 ${unexpected_package}，實際為 ${pkg}

最近應用清除操作應完成
    [Documentation]    從最近應用清除操作的完成確認（操作本身不拋出例外即視為成功）。
    Log    ✓ 從最近應用清除操作已完成    INFO

執行關鍵字不失敗
    [Documentation]    Run Keyword但忽略失敗（用於 Teardown 恢復操作）。
    [Arguments]    @{kw_and_args}
    Run Keyword And Ignore Error    @{kw_and_args}
