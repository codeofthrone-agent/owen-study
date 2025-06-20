
*** Settings ***
Resource    ../resources/mobile_keywords.robot
Resource    ../resources/web_keywords.robot
Resource    ../resources/api_keywords.robot
# Library     ../libraries/robot_arm_control/robot_arm_library.py    WITH NAME    RobotArm
Library     BuiltIn
Variables   ../variables/common_variables.py

*** Variables ***
${PLATFORM}    web    # 預設平台設定

*** Keywords ***
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


