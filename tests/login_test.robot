***Settings***
Resource    ../resources/common_keywords.robot
Variables   ../variables/common_variables.py

***Test Cases***
成功登錄行動應用程式
    Set Test Variable    ${PLATFORM}    mobile
    登錄應用程式    ${USERS}[0][username]    ${USERS}[0][password]
    驗證頁面標題    歡迎頁面標題

成功登錄網頁應用程式
    Set Test Variable    ${PLATFORM}    web
    登錄應用程式    ${USERS}[0][username]    ${USERS}[0][password]
    驗證頁面標題    Welcome to Web App

API 登錄測試
    執行 API 登錄    ${USERS}[0][username]    ${USERS}[0][password]

機器手臂點擊測試
    點擊實體按鈕    主電源按鈕    100    200    50
    驗證實體物件存在    主電源按鈕    True


