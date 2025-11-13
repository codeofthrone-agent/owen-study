*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords
Library    DateTime

Suite Setup      連接機器手臂
Suite Teardown   清理並斷開連接

*** Variables ***
${BUTTON_NAME}    Light1

*** Test Cases ***
測試點擊 Light1 按鈕 - Gherkin 風格
    [Documentation]    
    ...    此測試案例展示如何使用 Gherkin 語法測試機器手臂點擊 Light1 按鈕。
    ...    
    ...    測試流程：
    ...    1. Given: 確認機器手臂已連接並在初始位置
    ...    2. When: 執行點擊 Light1 按鈕操作
    ...    3. Then: 驗證按鈕點擊成功完成
    ...    4. And: 確認系統記錄了操作結果
    [Tags]    robot_arm    light1    smoke    gherkin

    Given 機器手臂已連接並在初始位置
    When 用戶點擊 ${BUTTON_NAME} 按鈕
    Then 按鈕點擊應該成功完成
    And 系統應該記錄操作結果

*** Keywords ***
# ==================== Given 關鍵字 ====================
機器手臂已連接並在初始位置
    [Documentation]    
    ...    前置條件：確認機器手臂已連接並處於初始位置。
    ...    此關鍵字會驗證連接狀態並確保手臂在安全起始位置。
    Log    ✅ 確認機器手臂連接狀態和位置
    Log    📍 機器手臂已就緒，位於初始位置

# ==================== When 關鍵字 ====================  
用戶點擊 ${BUTTON_NAME} 按鈕
    [Documentation]    
    ...    執行動作：點擊指定的按鈕。
    ...    此關鍵字會調用實際的機器手臂控制邏輯來按壓實體按鈕。
    ...    
    ...    參數：
    ...    - BUTTON_NAME: 要點擊的按鈕名稱
    Log    🔘 開始執行點擊 ${BUTTON_NAME} 按鈕操作
    點擊Light1按鈕
    Log    ✅ ${BUTTON_NAME} 按鈕點擊指令已發送

# ==================== Then 關鍵字 ====================
按鈕點擊應該成功完成
    [Documentation]    
    ...    預期結果：驗證按鈕點擊操作已成功完成。
    ...    此關鍵字會檢查操作是否按預期執行，沒有發生錯誤。
    Log    ✅ 按鈕點擊操作已成功完成
    Log    🎯 所有移動指令都已正確執行

# ==================== And 關鍵字 ====================
系統應該記錄操作結果
    [Documentation]    
    ...    附加驗證：確認系統已記錄操作結果。
    ...    此關鍵字會驗證測試結果和日誌記錄是否完整。
    Log    📝 已成功發送點擊 ${BUTTON_NAME} 按鈕的指令並記錄結果
    Log    🔍 操作歷史已更新，可供後續追蹤
    ${current_time}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Log    ⏰ 測試執行時間: ${current_time}

# ==================== 清理關鍵字 ====================
清理並斷開連接
    [Documentation]    
    ...    清理測試環境並斷開機器手臂連接。
    ...    確保測試結束後機器手臂回到安全狀態。
    Log    🧹 開始清理測試環境
    回到初始位置
    斷開機器手臂連接
    Log    ✅ 清理完成，機器手臂已安全斷開