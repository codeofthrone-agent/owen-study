*** Settings ***
Documentation     Voice Control Default Speaker Test
...               Test TTS playback using default system speaker (bypassing Scarlett 4i4)
Library           ../libraries/voice_control/VoiceControlKeywords.py
Test Setup        Given 語音控制系統已成功初始化

*** Test Cases ***
Scenario: 使用者使用預設喇叭播放文字
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Then 語音應該成功播放到指定聲道
