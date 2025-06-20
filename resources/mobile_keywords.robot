*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    BuiltIn
Variables    ../variables/common_variables.py

*** Keywords ***
打開行動應用程式
    [Arguments]    ${platform}    ${app_path}    ${device_name}    ${platform_version}
    ${desired_caps}=    Create Dictionary
    ...    platformName=${platform}
    ...    deviceName=${device_name}
    ...    platformVersion=${platform_version}
    ...    app=${app_path}
    
    # 根據平台設定 automationName
    Run Keyword If    '${platform}' == 'Android'
    ...    Set To Dictionary    ${desired_caps}    automationName=UiAutomator2
    ...    ELSE IF    '${platform}' == 'iOS'
    ...    Set To Dictionary    ${desired_caps}    automationName=XCUITest
    
    Open Application    http://localhost:4723/wd/hub    ${desired_caps}

關閉行動應用程式
    Close Application

輸入文字到行動應用程式元素
    [Arguments]    ${locator}    ${text}
    Input Text    ${locator}    ${text}

點擊行動應用程式元素
    [Arguments]    ${locator}
    Click Element    ${locator}

等待行動應用程式頁面包含文字
    [Arguments]    ${text}
    Wait Until Page Contains    ${text}

等待行動應用程式頁面包含元素
    [Arguments]    ${locator}
    Wait Until Page Contains Element    ${locator}

行動應用程式頁面不包含文字
    [Arguments]    ${text}
    Page Should Not Contain Text    ${text}

行動應用程式頁面不包含元素
    [Arguments]    ${locator}
    Page Should Not Contain Element    ${locator}


