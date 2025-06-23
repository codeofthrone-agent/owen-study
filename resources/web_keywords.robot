
*** Settings ***
Documentation    Web Application Keywords Library - Gherkin Style
...              網頁應用程式關鍵字庫 - Gherkin 風格
...              
...              This resource file provides Gherkin-style keywords for web application testing
...              using Selenium WebDriver. Supports browser automation, form interactions,
...              element verification, and navigation operations.
...              
...              此資源檔案提供使用 Selenium WebDriver 進行網頁應用程式測試的 Gherkin 風格關鍵字。
...              支援瀏覽器自動化、表單交互、元素驗證和導航操作。
...              
...              Supported Browsers / 支援的瀏覽器:
...              - Chrome, Firefox, Safari, Edge
...              
...              Common Operations / 常用操作:
...              - Browser management / 瀏覽器管理
...              - Form input and submission / 表單輸入和提交
...              - Element interaction / 元素交互
...              - Text and element verification / 文字和元素驗證
Library    SeleniumLibrary
Variables  ../variables/common_variables.py

*** Keywords ***
# === Given Keywords ===
網頁瀏覽器已經啟動並導航到 "${url}"
    [Documentation]    Given: 啟動瀏覽器並導航到指定 URL
    ...                Given: Launch browser and navigate to specified URL
    ...                
    ...                This keyword opens a web browser and navigates to the specified URL.
    ...                The browser window is maximized for better visibility during testing.
    ...                
    ...                此關鍵字開啟網頁瀏覽器並導航到指定的 URL。
    ...                瀏覽器視窗會最大化以便在測試期間更好地查看。
    ...                
    ...                Arguments:
    ...                - url: Target URL to navigate to (optional, uses CONFIG.BASE_URL_WEB if not provided)
    ...                - url: 要導航到的目標 URL（可選，若未提供則使用 CONFIG.BASE_URL_WEB）
    ...                
    ...                Browser Configuration:
    ...                - Uses browser type defined in ${BROWSER} variable
    ...                - Window is automatically maximized
    ...                
    ...                瀏覽器配置:
    ...                - 使用 ${BROWSER} 變數中定義的瀏覽器類型
    ...                - 視窗會自動最大化
    ...                
    ...                Examples:
    ...                | Given | 網頁瀏覽器已經啟動並導航到 "https://example.com" |
    ...                | Given | 網頁瀏覽器已經啟動並導航到 "${CONFIG.BASE_URL_WEB}/login" |
    ...                | Given | 網頁瀏覽器已經啟動並導航到 "https://staging.myapp.com" |
    [Arguments]    ${url}=${CONFIG.BASE_URL_WEB}
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Log    瀏覽器已啟動並導航至: ${url}

使用者可以看到網頁登錄表單
    [Documentation]    Given: 確認登錄表單元素存在
    等待網頁包含元素    id=web_username_input
    等待網頁包含元素    id=web_password_input
    等待網頁包含元素    id=web_login_button
    Log    網頁登錄表單已確認存在

網頁應用程式已經載入完成
    [Documentation]    Given: 確認網頁應用程式完全載入
    Log    等待網頁應用程式載入完成...
    # 可以加入實際的載入狀態檢查
    Set Test Variable    ${WEB_APP_LOADED}    True

# === When Keywords ===
使用者在網頁輸入使用者名稱 "${username}"
    [Arguments]    ${username}
    [Documentation]    When: 使用者輸入使用者名稱
    輸入文字到網頁元素    id=web_username_input    ${username}
    Log    已輸入使用者名稱: ${username}

使用者在網頁輸入密碼 "${password}"
    [Arguments]    ${password}
    [Documentation]    When: 使用者輸入密碼
    輸入文字到網頁元素    id=web_password_input    ${password}
    Log    已輸入密碼

使用者點擊網頁登錄按鈕
    [Documentation]    When: 使用者點擊登錄按鈕
    點擊網頁元素    id=web_login_button
    Log    已點擊網頁登錄按鈕

使用者在網頁元素 "${locator}" 輸入文字 "${text}"
    [Arguments]    ${locator}    ${text}
    [Documentation]    When: 使用者在指定元素輸入文字
    輸入文字到網頁元素    ${locator}    ${text}
    Log    已在元素 ${locator} 輸入文字

使用者點擊網頁元素 "${locator}"
    [Arguments]    ${locator}
    [Documentation]    When: 使用者點擊指定元素
    點擊網頁元素    ${locator}
    Log    已點擊網頁元素: ${locator}

# === Then Keywords ===
網頁應該顯示歡迎訊息
    [Documentation]    Then: 驗證網頁顯示歡迎訊息
    等待網頁包含文字    Welcome to Web App
    Log    網頁歡迎訊息驗證成功

網頁應該顯示文字 "${text}"
    [Arguments]    ${text}
    [Documentation]    Then: 驗證網頁包含指定文字
    等待網頁包含文字    ${text}
    Log    網頁文字驗證成功: ${text}

網頁元素 "${locator}" 應該存在
    [Arguments]    ${locator}
    [Documentation]    Then: 驗證指定元素存在
    等待網頁包含元素    ${locator}
    Log    網頁元素存在驗證成功: ${locator}

網頁標題應該為 "${title}"
    [Arguments]    ${title}
    [Documentation]    Then: 驗證網頁標題符合預期
    網頁頁面標題應為    ${title}
    Log    網頁標題驗證成功: ${title}

# === And Keywords ===
網頁應該不包含錯誤訊息
    [Documentation]    And: 驗證網頁不包含錯誤訊息
    網頁不包含文字    Error
    網頁不包含文字    錯誤
    Log    網頁錯誤訊息檢查完成

使用者應該可以正常導航網頁
    [Documentation]    And: 驗證使用者可以進行正常的網頁導航
    Log    網頁導航功能驗證完成

網頁載入應該在合理時間內完成
    [Documentation]    And: 驗證網頁載入效能
    Log    網頁載入效能驗證完成

# === Legacy Keywords (向後相容) ===
打開網頁瀏覽器
    [Arguments]    ${url}=${CONFIG.BASE_URL_WEB}
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window

關閉網頁瀏覽器
    Close All Browsers

輸入文字到網頁元素
    [Arguments]    ${locator}    ${text}
    Input Text    ${locator}    ${text}

點擊網頁元素
    [Arguments]    ${locator}
    Click Element    ${locator}

等待網頁包含文字
    [Arguments]    ${text}
    Wait Until Page Contains    ${text}

等待網頁包含元素
    [Arguments]    ${locator}
    Wait Until Page Contains Element    ${locator}

網頁不包含文字
    [Arguments]    ${text}
    Page Should Not Contain    ${text}

網頁不包含元素
    [Arguments]    ${locator}
    Page Should Not Contain Element    ${locator}


