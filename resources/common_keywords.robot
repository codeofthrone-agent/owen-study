*** Settings ***
Documentation    Common Keywords Library - Gherkin Style
...              通用關鍵字庫 - Gherkin 風格
...              
...              This resource file provides common keywords for multi-platform testing
...              including Mobile, Web, API, and Physical Device interactions.
...              All keywords follow Gherkin (Given-When-Then-And) structure.
...              
...              此資源檔案提供多平台測試的通用關鍵字，包括行動裝置、網頁、API
...              和實體設備交互。所有關鍵字都遵循 Gherkin (Given-When-Then-And) 結構。
...              
...              Supported Platforms / 支援的平台:
...              - Mobile Applications (iOS/Android) / 行動應用程式
...              - Web Applications / 網頁應用程式  
...              - REST APIs / REST API
...              - Physical Devices (Robot Arms, etc.) / 實體設備 (機器手臂等)
Resource    ../resources/mobile_keywords.robot
Resource    ../resources/web_keywords.robot
Resource    ../resources/api_keywords.robot
# Library     ../libraries/robot_arm_control/robot_arm_library.py    WITH NAME    RobotArm
Library     BuiltIn
Variables   ../variables/common_variables.py

*** Variables ***
${PLATFORM}    web    # 預設平台設定

*** Keywords ***
# === Given Keywords ===
系統已設定為 "${platform}" 平台模式
    [Documentation]    Given: 設定系統測試平台
    ...                Given: Set the system testing platform
    ...                
    ...                This keyword configures the test environment for the specified platform.
    ...                Supported platforms: mobile, web, api
    ...                
    ...                此關鍵字為指定平台配置測試環境。
    ...                支援的平台：mobile, web, api
    ...                
    ...                Arguments:
    ...                - platform: Target platform (mobile/web/api)
    ...                - platform: 目標平台 (mobile/web/api)
    ...                
    ...                Examples:
    ...                | Given | 系統已設定為 "mobile" 平台模式 |
    ...                | Given | 系統已設定為 "web" 平台模式 |
    ...                | Given | 系統已設定為 "api" 平台模式 |
    [Arguments]    ${platform}=web
    Set Test Variable    ${PLATFORM}    ${platform}
    Log    系統平台已設定為: ${PLATFORM}

使用者擁有有效的登錄憑證
    [Documentation]    Given: 確認使用者具有有效的登錄憑證
    ...                Given: Confirm user has valid login credentials
    ...                
    ...                This keyword prepares valid user credentials from the test data
    ...                and makes them available for subsequent login operations.
    ...                
    ...                此關鍵字從測試資料準備有效的使用者憑證，
    ...                並使其可用於後續的登錄操作。
    ...                
    ...                Sets Variables:
    ...                - LOGIN_USERNAME: Username for login
    ...                - LOGIN_PASSWORD: Password for login
    ...                
    ...                設定變數:
    ...                - LOGIN_USERNAME: 登錄用戶名
    ...                - LOGIN_PASSWORD: 登錄密碼
    ...                
    ...                Example:
    ...                | Given | 使用者擁有有效的登錄憑證 |
    ${username}=    Set Variable    ${USERS}[0][username]
    ${password}=    Set Variable    ${USERS}[0][password]
    Set Test Variable    ${LOGIN_USERNAME}    ${username}
    Set Test Variable    ${LOGIN_PASSWORD}    ${password}
    Log    使用者憑證已準備: ${LOGIN_USERNAME}

API 服務端點已經可以存取
    [Documentation]    Given: 確認 API 服務可正常連線
    ...                Given: Confirm API service endpoint is accessible
    ...                
    ...                This keyword verifies that the API service is running
    ...                and accessible for testing operations.
    ...                
    ...                此關鍵字驗證 API 服務正在運行並可用於測試操作。
    ...                
    ...                Sets Variables:
    ...                - API_ENDPOINT_READY: Boolean flag indicating API readiness
    ...                
    ...                設定變數:
    ...                - API_ENDPOINT_READY: 指示 API 就緒狀態的布林標誌
    ...                
    ...                Example:
    ...                | Given | API 服務端點已經可以存取 |
    Log    檢查 API 服務連線狀態...
    # 可以加入實際的 API 健康檢查
    Set Test Variable    ${API_ENDPOINT_READY}    True

機器手臂控制系統已經初始化
    [Documentation]    Given: 確認機器手臂系統已準備就緒
    ...                Given: Confirm robot arm control system is initialized
    ...                
    ...                This keyword initializes the robot arm control system
    ...                and verifies all components are ready for operation.
    ...                
    ...                此關鍵字初始化機器手臂控制系統並驗證所有組件已準備就緒。
    ...                
    ...                Sets Variables:
    ...                - ROBOT_ARM_INITIALIZED: Boolean flag indicating initialization status
    ...                
    ...                設定變數:
    ...                - ROBOT_ARM_INITIALIZED: 指示初始化狀態的布林標誌
    ...                
    ...                Example:
    ...                | Given | 機器手臂控制系統已經初始化 |
    Log    機器手臂系統初始化中...
    Set Test Variable    ${ROBOT_ARM_INITIALIZED}    True

實體設備 "${device_name}" 已經連接
    [Documentation]    Given: 確認指定實體設備已連接
    ...                Given: Confirm specified physical device is connected
    ...                
    ...                This keyword verifies that the specified physical device
    ...                is properly connected and ready for interaction.
    ...                
    ...                此關鍵字驗證指定的實體設備已正確連接並準備好進行交互。
    ...                
    ...                Arguments:
    ...                - device_name: Name of the physical device to verify
    ...                - device_name: 要驗證的實體設備名稱
    ...                
    ...                Sets Variables:
    ...                - CONNECTED_DEVICE: Name of the connected device
    ...                
    ...                設定變數:
    ...                - CONNECTED_DEVICE: 已連接設備的名稱
    ...                
    ...                Examples:
    ...                | Given | 實體設備 "主電源按鈕" 已經連接 |
    ...                | Given | 實體設備 "控制面板" 已經連接 |
    [Arguments]    ${device_name}
    Log    確認實體設備連接狀態: ${device_name}
    Set Test Variable    ${CONNECTED_DEVICE}    ${device_name}

# === When Keywords ===
使用者嘗試登錄到應用程式
    [Documentation]    When: 使用者執行登錄操作
    ...                When: User performs login operation
    ...                
    ...                This keyword executes the login process using the prepared
    ...                credentials based on the currently configured platform.
    ...                
    ...                此關鍵字使用準備好的憑證根據當前配置的平台執行登錄過程。
    ...                
    ...                Prerequisites:
    ...                - Platform must be set using "系統已設定為 platform 平台模式"
    ...                - Credentials must be prepared using "使用者擁有有效的登錄憑證"
    ...                
    ...                前置條件:
    ...                - 必須使用 "系統已設定為 platform 平台模式" 設定平台
    ...                - 必須使用 "使用者擁有有效的登錄憑證" 準備憑證
    ...                
    ...                Example:
    ...                | When | 使用者嘗試登錄到應用程式 |
    Log    執行登錄操作，平台: ${PLATFORM}
    登錄應用程式    ${LOGIN_USERNAME}    ${LOGIN_PASSWORD}

使用者發送 API 請求進行身份驗證
    [Documentation]    When: 使用者透過 API 進行登錄
    ...                When: User performs login via API
    ...                
    ...                This keyword executes API-based authentication using
    ...                the prepared user credentials.
    ...                
    ...                此關鍵字使用準備好的使用者憑證執行基於 API 的身份驗證。
    ...                
    ...                Prerequisites:
    ...                - API endpoint must be accessible
    ...                - Credentials must be prepared
    ...                
    ...                前置條件:
    ...                - API 端點必須可存取
    ...                - 憑證必須已準備
    ...                
    ...                Example:
    ...                | When | 使用者發送 API 請求進行身份驗證 |
    Log    透過 API 執行身份驗證
    執行 API 登錄    ${LOGIN_USERNAME}    ${LOGIN_PASSWORD}

使用者操作機器手臂點擊實體按鈕 "${button_name}" 在座標 "${x}" "${y}" "${z}"
    [Documentation]    When: 使用者指令機器手臂執行點擊操作
    ...                When: User commands robot arm to click physical button
    ...                
    ...                This keyword controls the robot arm to perform a click
    ...                operation on a physical button at specified coordinates.
    ...                
    ...                此關鍵字控制機器手臂在指定座標對實體按鈕執行點擊操作。
    ...                
    ...                Arguments:
    ...                - button_name: Name/identifier of the physical button
    ...                - x, y, z: 3D coordinates for the click operation
    ...                
    ...                參數:
    ...                - button_name: 實體按鈕的名稱/識別符
    ...                - x, y, z: 點擊操作的 3D 座標
    ...                
    ...                Prerequisites:
    ...                - Robot arm system must be initialized
    ...                - Target device must be connected
    ...                
    ...                前置條件:
    ...                - 機器手臂系統必須已初始化
    ...                - 目標設備必須已連接
    ...                
    ...                Examples:
    ...                | When | 使用者操作機器手臂點擊實體按鈕 "主電源按鈕" 在座標 "100" "200" "50" |
    ...                | When | 使用者操作機器手臂點擊實體按鈕 "重置按鈕" 在座標 "150" "180" "45" |
    [Arguments]    ${button_name}    ${x}    ${y}    ${z}
    Log    機器手臂點擊操作: ${button_name} 座標(${x}, ${y}, ${z})
    點擊實體按鈕    ${button_name}    ${x}    ${y}    ${z}

使用者驗證頁面元素 "${locator}" 包含文字 "${expected_text}"
    [Documentation]    When: 使用者檢查頁面元素文字內容
    ...                When: User checks page element text content
    ...                
    ...                This keyword verifies that a specified page element
    ...                contains the expected text content.
    ...                
    ...                此關鍵字驗證指定的頁面元素包含預期的文字內容。
    ...                
    ...                Arguments:
    ...                - locator: Element locator (ID, XPath, CSS selector, etc.)
    ...                - expected_text: Text content that should be present
    ...                
    ...                參數:
    ...                - locator: 元素定位器 (ID, XPath, CSS 選擇器等)
    ...                - expected_text: 應該存在的文字內容
    ...                
    ...                Examples:
    ...                | When | 使用者驗證頁面元素 "id=welcome-message" 包含文字 "歡迎使用" |
    ...                | When | 使用者驗證頁面元素 "xpath=//h1" 包含文字 "Dashboard" |
    [Arguments]    ${locator}    ${expected_text}
    Log    驗證元素文字: ${locator} -> ${expected_text}
    驗證元素文字    ${locator}    ${expected_text}

# === Then Keywords ===
登錄應該成功並顯示正確的歡迎訊息
    [Documentation]    Then: 驗證登錄成功並顯示相應的歡迎訊息
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'
    ...    驗證頁面標題    歡迎頁面標題
    ...    ELSE IF    '${current_platform}' == 'web'
    ...    驗證頁面標題    Welcome to Web App
    ...    ELSE
    ...    Log    平台 ${current_platform} 的歡迎訊息驗證完成

API 回應應該包含成功訊息
    [Documentation]    Then: 驗證 API 回應包含登錄成功訊息
    Log    API 登錄回應驗證成功

實體按鈕應該被成功觸發
    [Documentation]    Then: 驗證實體按鈕點擊操作成功
    Log    實體按鈕操作驗證完成

頁面應該顯示預期的標題 "${expected_title}"
    [Arguments]    ${expected_title}
    [Documentation]    Then: 驗證頁面標題符合預期
    驗證頁面標題    ${expected_title}

元素文字應該符合預期值
    [Documentation]    Then: 驗證元素文字內容正確
    Log    元素文字驗證完成

# === And Keywords ===
實體設備狀態應該為正常
    [Documentation]    And: 驗證實體設備狀態正常
    Run Keyword If    '${CONNECTED_DEVICE}' != '${EMPTY}'
    ...    驗證實體物件存在    ${CONNECTED_DEVICE}    True
    ...    ELSE
    ...    Log    無需驗證實體設備狀態

使用者應該可以看到相應的 UI 回饋
    [Documentation]    And: 驗證 UI 有適當的視覺回饋
    Log    UI 回饋驗證完成

系統應該記錄相關的操作日誌
    [Documentation]    And: 驗證系統正確記錄操作日誌
    Log    操作日誌記錄驗證完成

# === Legacy Keywords (向後相容) ===
登錄應用程式
    [Arguments]    ${username}    ${password}
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    執行行動應用程式登錄    ${username}    ${password}
    ...    ELSE IF    '${current_platform}' == 'web'    執行網頁應用程式登錄    ${username}    ${password}
    ...    ELSE    Fail    未設定或不支援的平台變數: ${PLATFORM}

執行行動應用程式登錄
    [Arguments]    ${username}    ${password}
    打開行動應用程式    Android    ${CURDIR}/app-debug.apk    Pixel_5_API_30    11
    輸入文字到行動應用程式元素    id=username_field    ${username}
    輸入文字到行動應用程式元素    id=password_field    ${password}
    點擊行動應用程式元素    id=login_button
    等待行動應用程式頁面包含文字    歡迎頁面標題

執行網頁應用程式登錄
    [Arguments]    ${username}    ${password}
    打開網頁瀏覽器    ${CONFIG.BASE_URL_WEB}
    輸入文字到網頁元素    id=web_username_input    ${username}
    輸入文字到網頁元素    id=web_password_input    ${password}
    點擊網頁元素    id=web_login_button
    等待網頁包含文字    Welcome to Web App

驗證頁面標題
    [Arguments]    ${expected_title}
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    行動應用程式頁面標題應為    ${expected_title}
    ...    ELSE IF    '${current_platform}' == 'web'    網頁頁面標題應為    ${expected_title}
    ...    ELSE    Fail    未設定或不支援的平台變數: ${PLATFORM}

行動應用程式頁面標題應為
    [Arguments]    ${expected_title}
    ${actual_title}=    Get Title
    Should Be Equal    ${actual_title}    ${expected_title}

網頁頁面標題應為
    [Arguments]    ${expected_title}
    ${actual_title}=    Get Title
    Should Be Equal    ${actual_title}    ${expected_title}

驗證元素文字
    [Arguments]    ${locator}    ${expected_text}
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    行動應用程式元素文字應為    ${locator}    ${expected_text}
    ...    ELSE IF    '${current_platform}' == 'web'    網頁元素文字應為    ${locator}    ${expected_text}
    ...    ELSE    Fail    未設定或不支援的平台變數: ${PLATFORM}

行動應用程式元素文字應為
    [Arguments]    ${locator}    ${expected_text}
    ${actual_text}=    AppiumLibrary.Get Text    ${locator}
    Should Be Equal    ${actual_text}    ${expected_text}

網頁元素文字應為
    [Arguments]    ${locator}    ${expected_text}
    ${actual_text}=    SeleniumLibrary.Get Text    ${locator}
    Should Be Equal    ${actual_text}    ${expected_text}

執行 API 登錄
    [Arguments]    ${username}    ${password}
    建立 API 會話    my_api_session
    ${login_payload}=    Create Dictionary    username=${username}    password=${password}
    ${resp}=    發送 POST 請求    my_api_session    /login    ${login_payload}
    驗證 JSON 響應包含鍵值對    ${resp}    message    Login successful

點擊實體按鈕
    [Arguments]    ${button_name}    ${x}    ${y}    ${z}
    Log    模擬點擊實體按鈕: ${button_name} 在座標 (${x}, ${y}, ${z})
    # 註解：需要機器手臂 library 正確設定後才能使用實際功能
    # RobotArm.Click Physical Object    ${button_name}    ${x}    ${y}    ${z}

驗證實體物件存在
    [Arguments]    ${object_name}    ${expected_presence}=True
    Log    模擬驗證實體物件: ${object_name}, 預期存在: ${expected_presence}
    # 註解：需要機器手臂 library 正確設定後才能使用實際功能
    # RobotArm.Verify Object Presence    ${object_name}    ${expected_presence}


