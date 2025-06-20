
***Settings***
Library    SeleniumLibrary
Variables  ../variables/common_variables.py

***Keywords***
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


