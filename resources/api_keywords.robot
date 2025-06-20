
***Settings***
Library    RequestsLibrary
Variables  ../variables/common_variables.py

***Keywords***
建立 API 會話
    [Arguments]    ${alias}    ${url}=${CONFIG.BASE_URL_API}
    Create Session    ${alias}    ${url}

發送 GET 請求
    [Arguments]    ${alias}    ${path}    ${expected_status}=200
    ${resp}=    Get Request    ${alias}    ${path}
    Status Should Be    ${expected_status}    ${resp}
    [Return]    ${resp}

發送 POST 請求
    [Arguments]    ${alias}    ${path}    ${data}    ${expected_status}=200
    ${resp}=    Post Request    ${alias}    ${path}    json=${data}
    Status Should Be    ${expected_status}    ${resp}
    [Return]    ${resp}

驗證 JSON 響應包含鍵值對
    [Arguments]    ${response}    ${key}    ${value}
    ${json_data}=    To Json    ${response.content}
    Should Be Equal    ${json_data}[${key}]    ${value}

驗證 JSON 響應包含多個鍵值對
    [Arguments]    ${response}    &{expected_data}
    ${json_data}=    To Json    ${response.content}
    FOR    ${key}    ${value}    IN HASH    ${expected_data}
        Should Be Equal    ${json_data}[${key}]    ${value}
    END

驗證 JSON 響應路徑值
    [Arguments]    ${response}    ${json_path}    ${expected_value}
    ${json_data}=    To Json    ${response.content}
    ${actual_value}=    Get Value From Json    ${json_data}    ${json_path}
    Should Be Equal    ${actual_value}    ${expected_value}


