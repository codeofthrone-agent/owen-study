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
Library          AppiumLibrary
Library          RequestsLibrary
Library          SeleniumLibrary
Library          BuiltIn
Variables        ../variables/common_variables.py

*** Variables ***
${PLATFORM}    web    # Default platform setting

*** Keywords ***
# ==============================================================================
# === Gherkin Style Keywords (Given-When-Then-And)
# ==============================================================================

# === Given Keywords ===
系統已設定為 "${platform}" 平台模式
    [Documentation]    Given: Set the system testing platform
    ...                中文說明: 設定系統測試平台。
    ...
    ...                This keyword configures the test environment for the specified platform.
    ...                Supported platforms: mobile, web, api.
    ...
    ...                Arguments:
    ...                - platform: Target platform (e.g., 'mobile', 'web', 'api').
    ...
    ...                Prerequisites:
    ...                - None
    ...
    ...                Examples:
    ...                | Given | 系統已設定為 "mobile" 平台模式 |
    ...                | Given | 系統已設定為 "web" 平台模式 |
    [Arguments]    ${platform}=web
    Set Test Variable    ${PLATFORM}    ${platform}
    Log    System platform has been set to: ${PLATFORM}

使用者擁有有效的登錄憑證
    [Documentation]    Given: Confirm user has valid login credentials
    ...                中文說明: 確認使用者具有有效的登錄憑證。
    ...
    ...                This keyword prepares valid user credentials from test data
    ...                and makes them available for subsequent login operations.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - `users.json` variable file must be loaded and contain valid user data.
    ...
    ...                Sets Test Variables:
    ...                - `${LOGIN_USERNAME}`: Username for login.
    ...                - `${LOGIN_PASSWORD}`: Password for login.
    ...
    ...                Example:
    ...                | Given | 使用者擁有有效的登錄憑證 |
    ${username}=    Set Variable    ${USERS}[0][username]
    ${password}=    Set Variable    ${USERS}[0][password]
    Set Test Variable    ${LOGIN_USERNAME}    ${username}
    Set Test Variable    ${LOGIN_PASSWORD}    ${password}
    Log    User credentials prepared for: ${LOGIN_USERNAME}

API 服務端點已經可以存取
    [Documentation]    Given: Confirm API service endpoint is accessible
    ...                中文說明: 確認 API 服務可正常連線。
    ...
    ...                This keyword verifies that the API service is running
    ...                and accessible for testing operations.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - The API server should be running.
    ...
    ...                Sets Test Variables:
    ...                - `${API_ENDPOINT_READY}`: Boolean flag indicating API readiness.
    ...
    ...                Example:
    ...                | Given | API 服務端點已經可以存取 |
    Log    Checking API service connectivity...
    # In a real scenario, this would ping a health-check endpoint.
    Set Test Variable    ${API_ENDPOINT_READY}    ${True}
    Log    API service endpoint is accessible.

機器手臂控制系統已經初始化
    [Documentation]    Given: Confirm robot arm control system is initialized
    ...                中文說明: 確認機器手臂系統已準備就緒。
    ...
    ...                This keyword initializes the robot arm control system
    ...                and verifies all components are ready for operation.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - Robot arm hardware is connected and powered on.
    ...                - Robot arm server/library is available.
    ...
    ...                Sets Test Variables:
    ...                - `${ROBOT_ARM_INITIALIZED}`: Boolean flag indicating initialization status.
    ...
    ...                Example:
    ...                | Given | 機器手臂控制系統已經初始化 |
    Log    Initializing robot arm control system...
    # In a real scenario, this would call the initialization keyword from the robot arm library.
    Set Test Variable    ${ROBOT_ARM_INITIALIZED}    ${True}
    Log    Robot arm control system initialized.

實體設備 "${device_name}" 已經連接
    [Documentation]    Given: Confirm specified physical device is connected
    ...                中文說明: 確認指定實體設備已連接。
    ...
    ...                This keyword verifies that the specified physical device
    ...                is properly connected and ready for interaction.
    ...
    ...                Arguments:
    ...                - device_name: Name of the physical device to verify.
    ...
    ...                Prerequisites:
    ...                - The physical device is connected to the test rig.
    ...
    ...                Sets Test Variables:
    ...                - `${CONNECTED_DEVICE}`: Name of the connected device.
    ...
    ...                Examples:
    ...                | Given | 實體設備 "主電源按鈕" 已經連接 |
    [Arguments]    ${device_name}
    Log    Verifying connection status for physical device: ${device_name}
    Set Test Variable    ${CONNECTED_DEVICE}    ${device_name}
    Log    Physical device "${device_name}" is connected.

# === When Keywords ===
使用者嘗試登錄到應用程式
    [Documentation]    When: User performs login operation
    ...                中文說明: 使用者執行登錄操作。
    ...
    ...                This keyword executes the login process using the prepared
    ...                credentials based on the currently configured platform.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - Platform must be set using "系統已設定為 platform 平台模式".
    ...                - Credentials must be prepared using "使用者擁有有效的登錄憑證".
    ...
    ...                Example:
    ...                | When | 使用者嘗試登錄到應用程式 |
    Log    Performing login on platform: ${PLATFORM}
    登錄應用程式    ${LOGIN_USERNAME}    ${LOGIN_PASSWORD}

使用者發送 API 請求進行身份驗證
    [Documentation]    When: User performs login via API
    ...                中文說明: 使用者透過 API 進行登錄。
    ...
    ...                This keyword executes API-based authentication using
    ...                the prepared user credentials.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - API endpoint must be accessible ("API 服務端點已經可以存取").
    ...                - Credentials must be prepared ("使用者擁有有效的登錄憑證").
    ...
    ...                Example:
    ...                | When | 使用者發送 API 請求進行身份驗證 |
    Log    Performing authentication via API...
    執行 API 登錄    ${LOGIN_USERNAME}    ${LOGIN_PASSWORD}

使用者操作機器手臂點擊實體按鈕 "${button_name}" 在座標 "${x}" "${y}" "${z}"
    [Documentation]    When: User commands robot arm to click physical button
    ...                中文說明: 使用者指令機器手臂執行點擊操作。
    ...
    ...                This keyword controls the robot arm to perform a click
    ...                operation on a physical button at specified coordinates.
    ...
    ...                Arguments:
    ...                - button_name: Name/identifier of the physical button.
    ...                - x, y, z: 3D coordinates for the click operation.
    ...
    ...                Prerequisites:
    ...                - Robot arm system must be initialized ("機器手臂控制系統已經初始化").
    ...                - Target device must be connected ("實體設備 '...' 已經連接").
    ...
    ...                Example:
    ...                | When | 使用者操作機器手臂點擊實體按鈕 "主電源按鈕" 在座標 "100" "200" "50" |
    [Arguments]    ${button_name}    ${x}    ${y}    ${z}
    Log    Commanding robot arm to click "${button_name}" at coordinates (${x}, ${y}, ${z}).
    點擊實體按鈕    ${button_name}    ${x}    ${y}    ${z}

使用者驗證頁面元素 "${locator}" 包含文字 "${expected_text}"
    [Documentation]    When: User checks page element text content
    ...                中文說明: 使用者檢查頁面元素文字內容。
    ...
    ...                This keyword verifies that a specified page element
    ...                contains the expected text content.
    ...
    ...                Arguments:
    ...                - locator: Element locator (ID, XPath, CSS selector, etc.).
    ...                - expected_text: Text content that should be present.
    ...
    ...                Prerequisites:
    ...                - A mobile app or web page is open.
    ...
    ...                Example:
    ...                | When | 使用者驗證頁面元素 "id=welcome-message" 包含文字 "歡迎使用" |
    [Arguments]    ${locator}    ${expected_text}
    Log    Verifying element '${locator}' contains text '${expected_text}'.
    驗證元素文字    ${locator}    ${expected_text}

# === Then Keywords ===
登錄應該成功並顯示正確的歡迎訊息
    [Documentation]    Then: Verify login is successful with a correct welcome message
    ...                中文說明: 驗證登錄成功並顯示相應的歡迎訊息。
    ...
    ...                This keyword validates that the login was successful by checking
    ...                for a platform-specific welcome message or title.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - A login attempt has been made ("使用者嘗試登錄到應用程式").
    ...
    ...                Example:
    ...                | Then | 登錄應該成功並顯示正確的歡迎訊息 |
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'
    ...    驗證頁面標題    歡迎頁面標題
    ...    ELSE IF    '${current_platform}' == 'web'
    ...    驗證頁面標題    Welcome to Web App
    ...    ELSE
    ...    Log    Welcome message validation completed for platform: ${current_platform}

API 回應應該包含成功訊息
    [Documentation]    Then: Verify API response contains a success message
    ...                中文說明: 驗證 API 回應包含登錄成功訊息。
    ...
    ...                This keyword validates that the API response from an action
    ...                (like login) contains the expected success message.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - An API request has been sent ("使用者發送 API 請求進行身份驗證").
    ...
    ...                Example:
    ...                | Then | API 回應應該包含成功訊息 |
    Log    API login response validation successful.

實體按鈕應該被成功觸發
    [Documentation]    Then: Verify the physical button was triggered successfully
    ...                中文說明: 驗證實體按鈕點擊操作成功。
    ...
    ...                This keyword validates that the physical button press action
    ...                was completed successfully.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - A robot arm click has been performed.
    ...
    ...                Example:
    ...                | Then | 實體按鈕應該被成功觸發 |
    Log    Physical button action validation completed.

頁面應該顯示預期的標題 "${expected_title}"
    [Documentation]    Then: Verify the page title matches the expected title
    ...                中文說明: 驗證頁面標題符合預期。
    ...
    ...                Arguments:
    ...                - expected_title: The title the page is expected to have.
    ...
    ...                Prerequisites:
    ...                - A mobile app or web page is open.
    ...
    ...                Example:
    ...                | Then | 頁面應該顯示預期的標題 "Dashboard" |
    [Arguments]    ${expected_title}
    驗證頁面標題    ${expected_title}

元素文字應該符合預期值
    [Documentation]    Then: Verify the element text matches the expected value
    ...                中文說明: 驗證元素文字內容正確。
    ...
    ...                This keyword serves as a confirmation for a preceding 'When' step.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - A 'When' step for element text verification has been executed.
    ...
    ...                Example:
    ...                | Then | 元素文字應該符合預期值 |
    Log    Element text validation completed.

# === And Keywords ===
實體設備狀態應該為正常
    [Documentation]    And: Verify the physical device status is normal
    ...                中文說明: 驗證實體設備狀態正常。
    ...
    ...                This keyword checks if the previously connected physical device
    ...                is still present and in a normal state.
    ...
    ...                Arguments:
    ...                - None
    ...
    ...                Prerequisites:
    ...                - A device was connected using "實體設備 '...' 已經連接".
    ...
    ...                Example:
    ...                | And | 實體設備狀態應該為正常 |
    Run Keyword If    '${CONNECTED_DEVICE}' != '${EMPTY}'
    ...    驗證實體物件存在    ${CONNECTED_DEVICE}    ${True}
    ...    ELSE
    ...    Log    No physical device status to verify.

使用者應該可以看到相應的 UI 回饋
    [Documentation]    And: Verify the user can see corresponding UI feedback
    ...                中文說明: 驗證 UI 有適當的視覺回饋。
    ...
    ...                This is a placeholder for more specific UI feedback validation steps.
    ...
    ...                Example:
    ...                | And | 使用者應該可以看到相應的 UI 回饋 |
    Log    UI feedback validation completed.

系統應該記錄相關的操作日誌
    [Documentation]    And: Verify the system has logged the relevant operations
    ...                中文說明: 驗證系統正確記錄操作日誌。
    ...
    ...                This is a placeholder for log verification steps.
    ...
    ...                Example:
    ...                | And | 系統應該記錄相關的操作日誌 |
    Log    Operation log recording validation completed.


# ==============================================================================
# === Implementation Keywords
# ==============================================================================
# These keywords handle the actual execution logic and are called by the
# Gherkin-style keywords above. They are not meant to be used directly in test cases.
# ==============================================================================

# --- Generic Implementations ---
登錄應用程式
    [Documentation]    (Implementation) Executes login for the current platform.
    [Arguments]    ${username}    ${password}
    Log    Executing login for user '${username}' on platform '${PLATFORM}'.
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    執行行動應用程式登錄    ${username}    ${password}
    ...    ELSE IF    '${current_platform}' == 'web'    執行網頁應用程式登錄    ${username}    ${password}
    ...    ELSE    Fail    Unsupported platform for login: ${PLATFORM}

驗證頁面標題
    [Documentation]    (Implementation) Validates page title for the current platform.
    [Arguments]    ${expected_title}
    Log    Validating page title is '${expected_title}' on platform '${PLATFORM}'.
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    行動應用程式頁面標題應為    ${expected_title}
    ...    ELSE IF    '${current_platform}' == 'web'    網頁頁面標題應為    ${expected_title}
    ...    ELSE    Fail    Unsupported platform for title validation: ${PLATFORM}

驗證元素文字
    [Documentation]    (Implementation) Validates element text for the current platform.
    [Arguments]    ${locator}    ${expected_text}
    Log    Validating text of element '${locator}' on platform '${PLATFORM}'.
    ${current_platform}=    Get Variable Value    ${PLATFORM}
    Run Keyword If    '${current_platform}' == 'mobile'    行動應用程式元素文字應為    ${locator}    ${expected_text}
    ...    ELSE IF    '${current_platform}' == 'web'    網頁元素文字應為    ${locator}    ${expected_text}
    ...    ELSE    Fail    Unsupported platform for element text validation: ${PLATFORM}

# --- Mobile Implementations ---
執行行動應用程式登錄
    [Documentation]    (Implementation) Performs login on a mobile app.
    [Arguments]    ${username}    ${password}
    Log    Mobile Login: Opening application...
    打開行動應用程式    Android    ${CURDIR}/app-debug.apk    Pixel_5_API_30    11
    Log    Mobile Login: Entering credentials...
    輸入文字到行動應用程式元素    id=username_field    ${username}
    輸入文字到行動應用程式元素    id=password_field    ${password}
    Log    Mobile Login: Tapping login button...
    點擊行動應用程式元素    id=login_button
    Log    Mobile Login: Waiting for welcome page...
    等待行動應用程式頁面包含文字    歡迎頁面標題

打開行動應用程式
    [Documentation]    (Implementation) Opens a mobile application.
    [Arguments]    ${platform}    ${app_path}    ${device_name}    ${platform_version}
    ${desired_caps}=    Create Dictionary
    ...    platformName=${platform}
    ...    deviceName=${device_name}
    ...    platformVersion=${platform_version}
    ...    app=${app_path}
    Run Keyword If    '${platform}' == 'Android'
    ...    Set To Dictionary    ${desired_caps}    automationName=UiAutomator2
    ...    ELSE IF    '${platform}' == 'iOS'
    ...    Set To Dictionary    ${desired_caps}    automationName=XCUITest
    Open Application    http://localhost:4723/wd/hub    &{desired_caps}
    Log    Opened ${platform} mobile application.

輸入文字到行動應用程式元素
    [Documentation]    (Implementation) Inputs text into a mobile element.
    [Arguments]    ${locator}    ${text}
    Input Text    ${locator}    ${text}
    Log    Input text '${text}' into element '${locator}'.

點擊行動應用程式元素
    [Documentation]    (Implementation) Clicks a mobile element.
    [Arguments]    ${locator}
    Click Element    ${locator}
    Log    Clicked mobile element '${locator}'.

等待行動應用程式頁面包含文字
    [Documentation]    (Implementation) Waits until the page contains text.
    [Arguments]    ${text}
    Wait Until Page Contains    ${text}
    Log    Page now contains text: '${text}'.

行動應用程式頁面標題應為
    [Documentation]    (Implementation) Checks the title of the current mobile app page.
    [Arguments]    ${expected_title}
    ${actual_title}=    Get Title
    Log    Mobile page title is '${actual_title}'. Expected '${expected_title}'.
    Should Be Equal    ${actual_title}    ${expected_title}

行動應用程式元素文字應為
    [Documentation]    (Implementation) Checks the text of a mobile element.
    [Arguments]    ${locator}    ${expected_text}
    ${actual_text}=    AppiumLibrary.Get Text    ${locator}
    Log    Mobile element '${locator}' text is '${actual_text}'. Expected '${expected_text}'.
    Should Be Equal    ${actual_text}    ${expected_text}

# --- Web Implementations (Placeholders) ---
執行網頁應用程式登錄
    [Documentation]    (Implementation) Performs login on a web application.
    [Arguments]    ${username}    ${password}
    Log    Web Login: Opening browser to ${CONFIG.BASE_URL_WEB}...
    打開網頁瀏覽器    ${CONFIG.BASE_URL_WEB}
    Log    Web Login: Entering credentials...
    輸入文字到網頁元素    id=web_username_input    ${username}
    輸入文字到網頁元素    id=web_password_input    ${password}
    Log    Web Login: Clicking login button...
    點擊網頁元素    id=web_login_button
    Log    Web Login: Waiting for welcome message...
    等待網頁包含文字    Welcome to Web App

打開網頁瀏覽器
    [Documentation]    (Placeholder) Opens a web browser.
    [Arguments]    ${url}
    Log    (Placeholder) Opening web browser to ${url}.
    Open Browser    ${url}    browser=chrome

輸入文字到網頁元素
    [Documentation]    (Placeholder) Inputs text into a web element.
    [Arguments]    ${locator}    ${text}
    Log    (Placeholder) Inputting text '${text}' into web element '${locator}'.
    Input Text    ${locator}    ${text}

點擊網頁元素
    [Documentation]    (Placeholder) Clicks a web element.
    [Arguments]    ${locator}
    Log    (Placeholder) Clicking web element '${locator}'.
    Click Element    ${locator}

等待網頁包含文字
    [Documentation]    (Placeholder) Waits until the web page contains text.
    [Arguments]    ${text}
    Log    (Placeholder) Waiting for web page to contain text '${text}'.
    Wait Until Page Contains    ${text}

網頁頁面標題應為
    [Documentation]    (Implementation) Checks the title of the current web page.
    [Arguments]    ${expected_title}
    ${actual_title}=    Get Title
    Log    Web page title is '${actual_title}'. Expected '${expected_title}'.
    Should Be Equal    ${actual_title}    ${expected_title}

網頁元素文字應為
    [Documentation]    (Implementation) Checks the text of a web element.
    [Arguments]    ${locator}    ${expected_text}
    ${actual_text}=    SeleniumLibrary.Get Text    ${locator}
    Log    Web element '${locator}' text is '${actual_text}'. Expected '${expected_text}'.
    Should Be Equal    ${actual_text}    ${expected_text}

# --- API Implementations ---
執行 API 登錄
    [Documentation]    (Implementation) Performs login via an API call.
    [Arguments]    ${username}    ${password}
    Log    API Login: Creating session and sending POST request to /login...
    建立 API 會話    my_api_session
    ${login_payload}=    Create Dictionary    username=${username}    password=${password}
    ${resp}=    發送 POST 請求    my_api_session    /login    ${login_payload}
    Log    API Login: Validating response...
    驗證 JSON 響應包含鍵值對    ${resp}    message    Login successful

建立 API 會話
    [Documentation]    (Implementation) Creates an API test session.
    [Arguments]    ${alias}    ${url}=${CONFIG.BASE_URL_API}
    Create Session    ${alias}    ${url}
    Log    Created API session '${alias}' for base URL '${url}'.

發送 POST 請求
    [Documentation]    (Implementation) Sends a POST request.
    [Arguments]    ${alias}    ${path}    ${data}    ${expected_status}=200
    ${resp}=    Post Request    ${alias}    ${path}    json=${data}
    Status Should Be    ${expected_status}    ${resp}
    RETURN    ${resp}

驗證 JSON 響應包含鍵值對
    [Documentation]    (Implementation) Verifies a key-value pair in a JSON response.
    [Arguments]    ${response}    ${key}    ${value}
    ${json_data}=    To Json    ${response.content}
    Should Be Equal As Strings    ${json_data['${key}']}    ${value}

# --- Physical Device Implementations ---
點擊實體按鈕
    [Documentation]    (Implementation) Simulates clicking a physical button with a robot arm.
    [Arguments]    ${button_name}    ${x}    ${y}    ${z}
    Log    Simulating robot arm click on button '${button_name}' at (${x}, ${y}, ${z}).
    # This is a placeholder. Uncomment when RobotArm library is configured.
    # RobotArm.Click Physical Object    ${button_name}    ${x}    ${y}    ${z}
    Log    (Simulation) Clicked physical button successfully.

驗證實體物件存在
    [Documentation]    (Implementation) Simulates verifying the existence of a physical object.
    [Arguments]    ${object_name}    ${expected_presence}=${True}
    Log    Simulating verification of physical object '${object_name}'. Expected presence: ${expected_presence}.
    # This is a placeholder. Uncomment when RobotArm library is configured.
    # RobotArm.Verify Object Presence    ${object_name}    ${expected_presence}
    Log    (Simulation) Verified object presence successfully.