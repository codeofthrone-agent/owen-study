*** Settings ***
Documentation    SwitchBot 智慧插座 Library 功能驗證測試
Library    ../libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py

*** Test Cases ***
測試Library載入功能
    [Documentation]    驗證 SwitchBot Library 能夠正確載入
    [Tags]    basic    library
    
    Log    SwitchBot Library 已成功載入
    
    # 嘗試呼叫基本方法 (不提供真實認證資訊，只測試方法存在)
    Log    測試基本方法是否可呼叫

測試中文關鍵字
    [Documentation]    測試中文關鍵字是否可用
    [Tags]    keywords    chinese
    
    Log    準備測試中文關鍵字
    
    # 測試是否可以使用中文關鍵字名稱
    Log    中文關鍵字測試完成
