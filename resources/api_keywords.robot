
*** Settings ***
Documentation    API 測試關鍵字庫 - API Testing Keyword Library
...              提供 Gherkin 風格的 API 測試關鍵字，支援 REST API 服務測試
...              Provides Gherkin-style API testing keywords for REST API service testing
...              
...              主要用途 / Main Uses:
...              - REST API 請求測試 / REST API request testing
...              - JSON 回應驗證 / JSON response validation
...              - API 效能測試 / API performance testing
...              - HTTP 狀態碼檢查 / HTTP status code verification
...              
...              支援的請求類型 / Supported Request Types:
...              - GET, POST, PUT, DELETE
...              - JSON 格式的請求和回應 / JSON format requests and responses
...              
...              使用方式 / Usage:
...              在測試案例中引用此資源檔案，並使用 Given-When-Then-And 格式的關鍵字
...              Import this resource file in test cases and use Given-When-Then-And style keywords
Library    RequestsLibrary
Variables  ../variables/common_variables.py

*** Keywords ***
# === Given Keywords ===
Given API 服務已在端點 "${url}" 運行
    [Arguments]    ${url}=${CONFIG.BASE_URL_API}
    [Documentation]    確認 API 服務在指定端點可用
    ...                Confirms API service is available at specified endpoint
    ...                
    ...                參數說明 / Parameters:
    ...                - url: API 服務端點 URL / API service endpoint URL (default: ${CONFIG.BASE_URL_API})
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API 服務必須已經啟動 / API service must be running
    ...                
    ...                用法範例 / Usage Example:
    ...                Given API 服務已在端點 "http://localhost:8080" 運行
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 如果服務無法連接將記錄錯誤 / Logs error if service is unreachable
    建立 API 會話    test_session    ${url}
    Set Test Variable    ${API_SESSION}    test_session
    Set Test Variable    ${API_BASE_URL}    ${url}
    Log    API 服務端點已設定: ${url}

Given 使用者擁有有效的 API 憑證
    [Documentation]    確認使用者具有有效的 API 憑證
    ...                Confirms user has valid API credentials
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 使用者已獲得有效的認證資訊 / User has obtained valid authentication information
    ...                
    ...                用法範例 / Usage Example:
    ...                Given 使用者擁有有效的 API 憑證
    ...                
    ...                說明 / Notes:
    ...                - 設定測試變數 API_CREDENTIALS_READY 為 True / Sets test variable API_CREDENTIALS_READY to True
    Set Test Variable    ${API_CREDENTIALS_READY}    True
    Log    API 憑證已準備就緒

Given API 請求資料已準備包含 "${key}" 和 "${value}"
    [Arguments]    ${key}    ${value}
    [Documentation]    準備 API 請求的資料
    ...                Prepares API request data
    ...                
    ...                參數說明 / Parameters:
    ...                - key: 資料鍵名 / Data key name
    ...                - value: 資料值 / Data value
    ...                
    ...                前置條件 / Prerequisites:
    ...                - 需要有效的鍵值對 / Requires valid key-value pair
    ...                
    ...                用法範例 / Usage Example:
    ...                Given API 請求資料已準備包含 "username" 和 "testuser"
    ...                
    ...                說明 / Notes:
    ...                - 建立包含鍵值對的字典並設為測試變數 / Creates dictionary with key-value pair and sets as test variable
    ${request_data} =    Create Dictionary    ${key}=${value}
    Set Test Variable    ${API_REQUEST_DATA}    ${request_data}
    Log    API 請求資料已準備: ${key}=${value}

# === When Keywords ===
When 使用者發送 GET 請求到路徑 "${path}"
    [Arguments]    ${path}    ${expected_status}=200
    [Documentation]    使用者發送 GET 請求
    ...                User sends GET request
    ...                
    ...                參數說明 / Parameters:
    ...                - path: API 路徑 / API path
    ...                - expected_status: 預期的 HTTP 狀態碼 / Expected HTTP status code (default: 200)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API 會話必須已經建立 / API session must be established
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者發送 GET 請求到路徑 "/api/users"
    ...                When 使用者發送 GET 請求到路徑 "/api/status"
    ...                
    ...                回傳 / Returns:
    ...                - 設定 API_RESPONSE 測試變數 / Sets API_RESPONSE test variable
    ${response} =    發送 GET 請求    ${API_SESSION}    ${path}    ${expected_status}
    Set Test Variable    ${API_RESPONSE}    ${response}
    Log    已發送 GET 請求到: ${path}

When 使用者發送 POST 請求到路徑 "${path}" 包含登錄資料
    [Arguments]    ${path}    ${expected_status}=200
    [Documentation]    使用者發送包含登錄資料的 POST 請求
    ...                User sends POST request with login data
    ...                
    ...                參數說明 / Parameters:
    ...                - path: API 路徑 / API path
    ...                - expected_status: 預期的 HTTP 狀態碼 / Expected HTTP status code (default: 200)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API 會話必須已經建立 / API session must be established
    ...                - API_REQUEST_DATA 必須包含登錄資料 / API_REQUEST_DATA must contain login data
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者發送 POST 請求到路徑 "/api/login" 包含登錄資料
    ...                
    ...                回傳 / Returns:
    ...                - 設定 API_RESPONSE 測試變數 / Sets API_RESPONSE test variable
    ${response} =    發送 POST 請求    ${API_SESSION}    ${path}    ${API_REQUEST_DATA}    ${expected_status}
    Set Test Variable    ${API_RESPONSE}    ${response}
    Log    已發送 POST 請求到: ${path}

When 使用者發送 POST 請求到路徑 "${path}" 包含資料 "${data}"
    [Arguments]    ${path}    ${data}    ${expected_status}=200
    [Documentation]    使用者發送包含指定資料的 POST 請求
    ...                User sends POST request with specified data
    ...                
    ...                參數說明 / Parameters:
    ...                - path: API 路徑 / API path
    ...                - data: 要發送的資料 / Data to send
    ...                - expected_status: 預期的 HTTP 狀態碼 / Expected HTTP status code (default: 200)
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API 會話必須已經建立 / API session must be established
    ...                - 資料格式須為有效的 JSON / Data must be in valid JSON format
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者發送 POST 請求到路徑 "/api/create" 包含資料 "{"name": "test"}"
    ...                
    ...                回傳 / Returns:
    ...                - 設定 API_RESPONSE 測試變數 / Sets API_RESPONSE test variable
    ${response} =    發送 POST 請求    ${API_SESSION}    ${path}    ${data}    ${expected_status}
    Set Test Variable    ${API_RESPONSE}    ${response}
    Log    已發送 POST 請求到: ${path}

When 使用者驗證 API 回應包含鍵值對 "${key}" 和 "${value}"
    [Arguments]    ${key}    ${value}
    [Documentation]    使用者檢查 API 回應的鍵值對
    ...                User checks API response key-value pair
    ...                
    ...                參數說明 / Parameters:
    ...                - key: 要檢查的鍵名 / Key name to check
    ...                - value: 預期的值 / Expected value
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定且為有效的 JSON / API_RESPONSE must be set and contain valid JSON
    ...                
    ...                用法範例 / Usage Example:
    ...                When 使用者驗證 API 回應包含鍵值對 "status" 和 "success"
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 如果鍵不存在或值不匹配將會失敗 / Fails if key doesn't exist or value doesn't match
    驗證 JSON 響應包含鍵值對    ${API_RESPONSE}    ${key}    ${value}
    Log    已驗證 API 回應鍵值對: ${key}=${value}

# === Then Keywords ===
Then API 回應應該包含成功訊息 "${message}"
    [Arguments]    ${message}
    [Documentation]    驗證 API 回應包含成功訊息
    ...                Verifies API response contains success message
    ...                
    ...                參數說明 / Parameters:
    ...                - message: 預期的成功訊息 / Expected success message
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定且為有效的 JSON / API_RESPONSE must be set and contain valid JSON
    ...                
    ...                用法範例 / Usage Example:
    ...                Then API 回應應該包含成功訊息 "Login successful"
    ...                Then API 回應應該包含成功訊息 "登錄成功"
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查回應中的 message 鍵是否包含指定訊息 / Checks if response contains specified message in message key
    驗證 JSON 響應包含鍵值對    ${API_RESPONSE}    message    ${message}
    Log    API 成功訊息驗證完成: ${message}

Then API 回應狀態碼應該為成功
    [Documentation]    驗證 API 回應狀態碼為成功範圍
    ...                Verifies API response status code is in success range
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定 / API_RESPONSE must be set
    ...                
    ...                用法範例 / Usage Example:
    ...                Then API 回應狀態碼應該為成功
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查狀態碼是否在 200-299 範圍內 / Checks if status code is in 200-299 range
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 狀態碼非成功範圍時測試失敗 / Test fails if status code is not in success range
    ${status_code} =    Set Variable    ${API_RESPONSE.status_code}
    Should Be True    200 <= ${status_code} < 300    msg=API 回應狀態碼非成功範圍: ${status_code}
    Log    API 狀態碼驗證成功: ${status_code}

Then API 回應應該包含鍵 "${key}" 且值為 "${value}"
    [Arguments]    ${key}    ${value}
    [Documentation]    驗證 API 回應包含指定的鍵值對
    ...                Verifies API response contains specified key-value pair
    ...                
    ...                參數說明 / Parameters:
    ...                - key: 要檢查的鍵名 / Key name to check
    ...                - value: 預期的值 / Expected value
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定且為有效的 JSON / API_RESPONSE must be set and contain valid JSON
    ...                
    ...                用法範例 / Usage Example:
    ...                Then API 回應應該包含鍵 "status" 且值為 "active"
    ...                Then API 回應應該包含鍵 "user_id" 且值為 "12345"
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查指定鍵是否存在且值完全匹配 / Checks if specified key exists and value matches exactly
    驗證 JSON 響應包含鍵值對    ${API_RESPONSE}    ${key}    ${value}
    Log    API 鍵值對驗證成功: ${key}=${value}

Then API 回應應該是有效的 JSON 格式
    [Documentation]    驗證 API 回應為有效的 JSON 格式
    ...                Verifies API response is in valid JSON format
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定 / API_RESPONSE must be set
    ...                
    ...                用法範例 / Usage Example:
    ...                Then API 回應應該是有效的 JSON 格式
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查回應內容是否可解析為 JSON / Checks if response content can be parsed as JSON
    ...                - 檢查 JSON 資料不為空 / Checks if JSON data is not empty
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 如果回應不是有效 JSON 格式則測試失敗 / Test fails if response is not valid JSON
    ${json_data} =    To Json    ${API_RESPONSE.content}
    Should Not Be Empty    ${json_data}    msg=API 回應不是有效的 JSON 格式
    Log    API JSON 格式驗證成功

# === And Keywords ===
And API 回應時間應該在合理範圍內
    [Documentation]    驗證 API 回應時間效能
    ...                Verifies API response time performance
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定 / API_RESPONSE must be set
    ...                
    ...                用法範例 / Usage Example:
    ...                And API 回應時間應該在合理範圍內
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查回應時間是否小於 5 秒 / Checks if response time is less than 5 seconds
    ...                
    ...                效能指標 / Performance Metrics:
    ...                - 合理回應時間: < 5.0 秒 / Reasonable response time: < 5.0 seconds
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 回應時間超過限制時測試失敗 / Test fails if response time exceeds limit
    ${response_time} =    Set Variable    ${API_RESPONSE.elapsed.total_seconds()}
    Should Be True    ${response_time} < 5.0    msg=API 回應時間過長: ${response_time}s
    Log    API 回應時間驗證成功: ${response_time}s

And API 回應應該包含必要的標頭
    [Documentation]    驗證 API 回應包含必要的 HTTP 標頭
    ...                Verifies API response contains required HTTP headers
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_RESPONSE 必須已設定 / API_RESPONSE must be set
    ...                
    ...                用法範例 / Usage Example:
    ...                And API 回應應該包含必要的標頭
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查 Content-Type 標頭是否存在 / Checks if Content-Type header exists
    ...                
    ...                必要標頭 / Required Headers:
    ...                - Content-Type: 指定回應內容類型 / Specifies response content type
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 缺少必要標頭時測試失敗 / Test fails if required headers are missing
    ${headers} =    Set Variable    ${API_RESPONSE.headers}
    Should Contain    ${headers}    Content-Type    msg=API 回應缺少 Content-Type 標頭
    Log    API 回應標頭驗證完成

And API 會話應該正確建立並維持
    [Documentation]    驗證 API 會話狀態正常
    ...                Verifies API session status is normal
    ...                
    ...                前置條件 / Prerequisites:
    ...                - API_SESSION 變數必須已設定 / API_SESSION variable must be set
    ...                
    ...                用法範例 / Usage Example:
    ...                And API 會話應該正確建立並維持
    ...                
    ...                驗證項目 / Verification Items:
    ...                - 檢查 API 會話是否已正確建立 / Checks if API session is properly established
    ...                - 確認會話變數不為空 / Confirms session variable is not empty
    ...                
    ...                異常情況 / Exception Cases:
    ...                - 會話未建立或狀態異常時測試失敗 / Test fails if session is not established or in abnormal state
    Should Not Be Empty    ${API_SESSION}    msg=API 會話未正確建立
    Log    API 會話狀態驗證完成

# === Legacy Keywords (向後相容) ===
建立 API 會話
    [Arguments]    ${alias}    ${url}=${CONFIG.BASE_URL_API}
    [Documentation]    建立 API 測試會話 (向後相容關鍵字)
    ...                Creates API test session (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - alias: 會話別名 / Session alias
    ...                - url: API 基礎 URL / API base URL
    ...                
    ...                用法範例 / Usage Example:
    ...                建立 API 會話    test_session    http://localhost:8080
    Create Session    ${alias}    ${url}

發送 GET 請求
    [Arguments]    ${alias}    ${path}    ${expected_status}=200
    [Documentation]    發送 GET 請求 (向後相容關鍵字)
    ...                Sends GET request (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - alias: 會話別名 / Session alias
    ...                - path: 請求路徑 / Request path
    ...                - expected_status: 預期狀態碼 / Expected status code
    ...                
    ...                回傳 / Returns:
    ...                - HTTP 回應物件 / HTTP response object
    ${resp}=    Get Request    ${alias}    ${path}
    Status Should Be    ${expected_status}    ${resp}
    RETURN    ${resp}

發送 POST 請求
    [Arguments]    ${alias}    ${path}    ${data}    ${expected_status}=200
    [Documentation]    發送 POST 請求 (向後相容關鍵字)
    ...                Sends POST request (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - alias: 會話別名 / Session alias
    ...                - path: 請求路徑 / Request path
    ...                - data: 請求資料 / Request data
    ...                - expected_status: 預期狀態碼 / Expected status code
    ...                
    ...                回傳 / Returns:
    ...                - HTTP 回應物件 / HTTP response object
    ${resp}=    Post Request    ${alias}    ${path}    json=${data}
    Status Should Be    ${expected_status}    ${resp}
    RETURN    ${resp}

驗證 JSON 響應包含鍵值對
    [Arguments]    ${response}    ${key}    ${value}
    [Documentation]    驗證 JSON 回應包含指定鍵值對 (向後相容關鍵字)
    ...                Verifies JSON response contains specified key-value pair (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - response: HTTP 回應物件 / HTTP response object
    ...                - key: 鍵名 / Key name
    ...                - value: 預期值 / Expected value
    ${json_data}=    To Json    ${response.content}
    Should Be Equal    ${json_data}[${key}]    ${value}

驗證 JSON 響應包含多個鍵值對
    [Arguments]    ${response}    &{expected_data}
    [Documentation]    驗證 JSON 回應包含多個鍵值對 (向後相容關鍵字)
    ...                Verifies JSON response contains multiple key-value pairs (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - response: HTTP 回應物件 / HTTP response object
    ...                - expected_data: 預期的鍵值對字典 / Expected key-value pairs dictionary
    ${json_data}=    To Json    ${response.content}
    FOR    ${key}    ${value}    IN HASH    ${expected_data}
        Should Be Equal    ${json_data}[${key}]    ${value}
    END

驗證 JSON 響應路徑值
    [Arguments]    ${response}    ${json_path}    ${expected_value}
    [Documentation]    驗證 JSON 回應中指定路徑的值 (向後相容關鍵字)
    ...                Verifies value at specified path in JSON response (backward compatibility keyword)
    ...                
    ...                參數說明 / Parameters:
    ...                - response: HTTP 回應物件 / HTTP response object
    ...                - json_path: JSON 路徑表達式 / JSON path expression
    ...                - expected_value: 預期值 / Expected value
    ${json_data}=    To Json    ${response.content}
    ${actual_value}=    Get Value From Json    ${json_data}    ${json_path}
    Should Be Equal    ${actual_value}    ${expected_value}


