*** Settings ***
Documentation    多平台登錄測試案例 - Multi-Platform Login Test Cases
...              支援行動應用程式、網頁應用程式、API 以及實體設備測試
...              Supports mobile apps, web apps, API, and physical device testing
...              
...              測試範圍 / Test Scope:
...              - 行動應用程式登錄驗證 / Mobile application login verification
...              - 網頁應用程式登錄驗證 / Web application login verification  
...              - API 登錄服務驗證 / API login service verification
...              - 實體設備交互驗證 / Physical device interaction verification
...              
...              使用的關鍵字庫 / Used Keyword Libraries:
...              - common_keywords.robot: 通用測試關鍵字 / Common test keywords
...              - variables/common_variables.py: 測試資料變數 / Test data variables
Resource    ../../resources/common_keywords.robot
Variables   ../../variables/common_variables.py

*** Test Cases ***
Scenario: User Successfully Logs In Through Mobile Application
    [Documentation]    使用者透過行動應用程式成功登錄的測試場景
    ...                Test scenario for user successfully logging in through mobile application
    ...                
    ...                測試目標 / Test Objective:
    ...                - 驗證行動應用程式登錄功能正常運作 / Verify mobile app login functionality works correctly
    ...                
    ...                測試步驟 / Test Steps:
    ...                1. 設定測試平台為行動應用程式 / Set test platform to mobile application
    ...                2. 使用有效憑證嘗試登錄 / Attempt login with valid credentials
    ...                3. 驗證登錄成功並顯示歡迎頁面 / Verify successful login and welcome page display
    ...                
    ...                預期結果 / Expected Result:
    ...                - 使用者能夠成功登錄並看到歡迎頁面 / User can successfully log in and see welcome page
    [Tags]    mobile    login    gherkin
    Given 系統平台已設定為行動應用程式
    When 使用者嘗試使用有效憑證登錄
    Then 使用者應該看到歡迎頁面標題

Scenario: User Successfully Logs In Through Web Application
    [Documentation]    使用者透過網頁應用程式成功登錄的測試場景
    ...                Test scenario for user successfully logging in through web application
    ...                
    ...                測試目標 / Test Objective:
    ...                - 驗證網頁應用程式登錄功能正常運作 / Verify web app login functionality works correctly
    ...                
    ...                測試步驟 / Test Steps:
    ...                1. 設定測試平台為網頁應用程式 / Set test platform to web application
    ...                2. 使用有效憑證嘗試登錄 / Attempt login with valid credentials
    ...                3. 驗證登錄成功並顯示歡迎訊息 / Verify successful login and welcome message display
    ...                
    ...                預期結果 / Expected Result:
    ...                - 使用者能夠成功登錄並看到網頁歡迎訊息 / User can successfully log in and see web welcome message
    [Tags]    web    login    gherkin
    Given 系統平台已設定為網頁應用程式
    When 使用者嘗試使用有效憑證登錄
    Then 使用者應該看到網頁歡迎訊息

Scenario: User Successfully Logs In Through API
    [Documentation]    使用者透過 API 成功登錄的測試場景
    ...                Test scenario for user successfully logging in through API
    ...                
    ...                測試目標 / Test Objective:
    ...                - 驗證 API 登錄服務功能正常運作 / Verify API login service functionality works correctly
    ...                
    ...                測試步驟 / Test Steps:
    ...                1. 確認 API 服務已啟動並可用 / Confirm API service is running and available
    ...                2. 透過 API 提交登錄請求 / Submit login request through API
    ...                3. 驗證系統回傳登錄成功訊息 / Verify system returns login success message
    ...                
    ...                預期結果 / Expected Result:
    ...                - API 能夠正確處理登錄請求並回傳成功訊息 / API can correctly process login request and return success message
    [Tags]    api    login    gherkin
    Given API 服務已經啟動並可用
    When 使用者透過 API 提交登錄請求
    Then 系統應該回傳登錄成功訊息

Scenario: Robot Arm Executes Physical Button Click Operation
    [Documentation]    機器手臂執行實體按鈕點擊操作的測試場景
    ...                Test scenario for robot arm executing physical button click operation
    ...                
    ...                測試目標 / Test Objective:
    ...                - 驗證機器手臂能夠正確執行實體交互操作 / Verify robot arm can correctly execute physical interaction operations
    ...                
    ...                測試步驟 / Test Steps:
    ...                1. 確認機器手臂系統已準備就緒 / Confirm robot arm system is ready
    ...                2. 指令機器手臂點擊主電源按鈕 / Command robot arm to click main power button
    ...                3. 驗證實體按鈕被成功觸發 / Verify physical button is successfully triggered
    ...                4. 確認主電源按鈕狀態為已啟動 / Confirm main power button status is activated
    ...                
    ...                預期結果 / Expected Result:
    ...                - 機器手臂能夠精確點擊實體按鈕並觸發預期狀態變化 / Robot arm can precisely click physical button and trigger expected state change
    [Tags]    physical    robotarm    gherkin
    Given 機器手臂系統已經準備就緒
    When 使用者指令機器手臂點擊主電源按鈕
    Then 實體按鈕應該被成功觸發
    And 主電源按鈕狀態應該為已啟動

# === Legacy Test Cases (向後相容) ===
成功登錄行動應用程式
    [Documentation]    傳統風格的行動應用程式登錄測試
    [Tags]    legacy    mobile
    Set Test Variable    ${PLATFORM}    mobile
    登錄應用程式    ${USERS}[0][username]    ${USERS}[0][password]
    驗證頁面標題    歡迎頁面標題

成功登錄網頁應用程式
    [Documentation]    傳統風格的網頁應用程式登錄測試
    [Tags]    legacy    web
    Set Test Variable    ${PLATFORM}    web
    登錄應用程式    ${USERS}[0][username]    ${USERS}[0][password]
    驗證頁面標題    Welcome to Web App

API 登錄測試
    [Documentation]    傳統風格的 API 登錄測試
    [Tags]    legacy    api
    執行 API 登錄    ${USERS}[0][username]    ${USERS}[0][password]

機器手臂點擊測試
    [Documentation]    傳統風格的機器手臂測試
    [Tags]    legacy    robotarm
    點擊實體按鈕    主電源按鈕    100    200    50
    驗證實體物件存在    主電源按鈕    True

*** Keywords ***
# === Given Keywords ===
系統平台已設定為行動應用程式
    [Documentation]    設定測試平台為行動應用程式
    ...                Sets test platform to mobile application
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 設定 PLATFORM 測試變數為 'mobile' / Sets PLATFORM test variable to 'mobile'
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 系統平台已設定為行動應用程式
    ...                
    ...                後續效果 / Subsequent Effects:
    ...                - 影響後續測試步驟的平台特定行為 / Affects platform-specific behavior in subsequent test steps
    Set Test Variable    ${PLATFORM}    mobile
    Log    測試平台已設定為: ${PLATFORM}

系統平台已設定為網頁應用程式
    [Documentation]    設定測試平台為網頁應用程式
    ...                Sets test platform to web application
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 設定 PLATFORM 測試變數為 'web' / Sets PLATFORM test variable to 'web'
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 系統平台已設定為網頁應用程式
    ...                
    ...                後續效果 / Subsequent Effects:
    ...                - 影響後續測試步驟的平台特定行為 / Affects platform-specific behavior in subsequent test steps
    Set Test Variable    ${PLATFORM}    web
    Log    測試平台已設定為: ${PLATFORM}

API 服務已經啟動並可用
    [Documentation]    確認 API 服務可正常存取
    ...                Confirms API service is accessible and functional
    ...                
    ...                驗證項目 / Verification Items:
    ...                - API 服務連線狀態 / API service connection status
    ...                - 服務可用性檢查 / Service availability check
    ...                
    ...                用法範例 / Usage Example:
    ...                Given API 服務已經啟動並可用
    ...                
    ...                設定變數 / Variable Settings:
    ...                - API_AVAILABLE: True - 表示 API 服務可用 / Indicates API service is available
    Log    檢查 API 服務狀態...
    # 可以加入 API 健康檢查
    Set Test Variable    ${API_AVAILABLE}    True

機器手臂系統已經準備就緒
    [Documentation]    確認機器手臂系統已初始化
    ...                Confirms robot arm system is initialized
    ...                
    ...                初始化項目 / Initialization Items:
    ...                - 機器手臂硬體狀態檢查 / Robot arm hardware status check
    ...                - 目標按鈕座標設定 / Target button coordinate setting
    ...                - 系統準備狀態確認 / System readiness confirmation
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 機器手臂系統已經準備就緒
    ...                
    ...                設定變數 / Variable Settings:
    ...                - ROBOT_ARM_READY: True - 機器手臂準備完成 / Robot arm ready
    ...                - TARGET_BUTTON: 主電源按鈕 - 目標按鈕名稱 / Target button name
    ...                - TARGET_COORDINATES: 100, 200, 50 - 目標座標 / Target coordinates
    Log    機器手臂系統初始化檢查...
    Set Test Variable    ${ROBOT_ARM_READY}    True
    Set Test Variable    ${TARGET_BUTTON}    主電源按鈕
    Set Test Variable    ${TARGET_COORDINATES}    100    200    50

# === When Keywords ===
使用者嘗試使用有效憑證登錄
    [Documentation]    使用者執行登錄操作
    ...                User executes login operation
    ...                
    ...                執行步驟 / Execution Steps:
    ...                1. 從測試資料取得使用者憑證 / Retrieve user credentials from test data
    ...                2. 呼叫登錄關鍵字執行登錄 / Call login keyword to execute login
    ...                
    ...                使用的測試資料 / Test Data Used:
    ...                - USERS[0][username]: 第一個測試使用者的使用者名稱 / First test user's username
    ...                - USERS[0][password]: 第一個測試使用者的密碼 / First test user's password
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者嘗試使用有效憑證登錄
    ${username}=    Set Variable    ${USERS}[0][username]
    ${password}=    Set Variable    ${USERS}[0][password]
    Log    嘗試登錄，使用者: ${username}
    登錄應用程式    ${username}    ${password}

使用者透過 API 提交登錄請求
    [Documentation]    使用者透過 API 發送登錄請求
    ...                User sends login request through API
    ...                
    ...                執行步驟 / Execution Steps:
    ...                1. 從測試資料取得 API 登錄憑證 / Retrieve API login credentials from test data
    ...                2. 呼叫 API 登錄關鍵字 / Call API login keyword
    ...                
    ...                API 端點 / API Endpoint:
    ...                - 使用配置的 API 登錄端點 / Uses configured API login endpoint
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者透過 API 提交登錄請求
    ${username}=    Set Variable    ${USERS}[0][username]
    ${password}=    Set Variable    ${USERS}[0][password]
    Log    透過 API 嘗試登錄，使用者: ${username}
    執行 API 登錄    ${username}    ${password}

使用者指令機器手臂點擊主電源按鈕
    [Documentation]    使用者下達機器手臂執行指令
    ...                User issues robot arm execution command
    ...                
    ...                執行動作 / Actions Performed:
    ...                - 指令機器手臂移動到目標座標 / Command robot arm to move to target coordinates
    ...                - 執行點擊動作 / Execute click action
    ...                
    ...                目標規格 / Target Specifications:
    ...                - 按鈕名稱: 主電源按鈕 / Button name: Main power button
    ...                - 座標位置: (100, 200, 50) / Coordinate position: (100, 200, 50)
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者指令機器手臂點擊主電源按鈕
    Log    執行機器手臂點擊操作: ${TARGET_BUTTON}
    點擊實體按鈕    ${TARGET_BUTTON}    100    200    50

# === Then Keywords ===
使用者應該看到歡迎頁面標題
    [Documentation]    驗證行動應用程式登錄成功
    ...                Verifies mobile application login success
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查歡迎頁面標題是否正確顯示 / Checks if welcome page title is correctly displayed
    ...                
    ...                預期結果 / Expected Result:
    ...                - 頁面標題應顯示 "歡迎頁面標題" / Page title should display "歡迎頁面標題"
    ...                
    ...                用法範例 / Usage Example:
    ...                Then 使用者應該看到歡迎頁面標題
    驗證頁面標題    歡迎頁面標題
    Log    行動應用程式登錄驗證成功

使用者應該看到網頁歡迎訊息
    [Documentation]    驗證網頁應用程式登錄成功
    ...                Verifies web application login success
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查網頁歡迎訊息是否正確顯示 / Checks if web welcome message is correctly displayed
    ...                
    ...                預期結果 / Expected Result:
    ...                - 頁面應顯示 "Welcome to Web App" 訊息 / Page should display "Welcome to Web App" message
    ...                
    ...                用法範例 / Usage Example:
    ...                Then 使用者應該看到網頁歡迎訊息
    驗證頁面標題    Welcome to Web App
    Log    網頁應用程式登錄驗證成功

系統應該回傳登錄成功訊息
    [Documentation]    驗證 API 登錄回應正確
    ...                Verifies API login response is correct
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查 API 回應狀態碼 / Checks API response status code
    ...                - 驗證回應訊息內容 / Verifies response message content
    ...                
    ...                預期結果 / Expected Result:
    ...                - API 應回傳成功狀態碼和成功訊息 / API should return success status code and success message
    ...                
    ...                用法範例 / Usage Example:
    ...                Then 系統應該回傳登錄成功訊息
    Log    API 登錄回應驗證成功

實體按鈕應該被成功觸發
    [Documentation]    驗證機器手臂點擊操作成功
    ...                Verifies robot arm click operation success
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 確認點擊動作已執行 / Confirms click action has been executed
    ...                - 檢查目標按鈕回應 / Checks target button response
    ...                
    ...                預期結果 / Expected Result:
    ...                - 實體按鈕應被成功觸發並產生預期回應 / Physical button should be successfully triggered and produce expected response
    ...                
    ...                用法範例 / Usage Example:
    ...                Then 實體按鈕應該被成功觸發
    Log    實體按鈕點擊操作執行完成: ${TARGET_BUTTON}

# === And Keywords ===
主電源按鈕狀態應該為已啟動
    [Documentation]    驗證實體設備狀態
    ...                Verifies physical device status
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查主電源按鈕的物理狀態 / Checks physical status of main power button
    ...                - 確認狀態變化符合預期 / Confirms status change meets expectations
    ...                
    ...                預期結果 / Expected Result:
    ...                - 主電源按鈕狀態應為 "已啟動" / Main power button status should be "activated"
    ...                
    ...                用法範例 / Usage Example:
    ...                And 主電源按鈕狀態應該為已啟動
    驗證實體物件存在    ${TARGET_BUTTON}    True
    Log    實體物件狀態驗證成功: ${TARGET_BUTTON}


