*** Settings ***
Documentation     Voice Control Default Speaker Test
...               Test TTS playback using default system speaker (bypassing Scarlett 4i4)
Library           ../../libraries/voice_control/VoiceControlKeywords.py
Test Setup        Given 語音控制系統已成功初始化

*** Test Cases ***
Scenario: 使用者使用預設喇叭播放文字
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "companion"


*** Test Cases ***
Scenario: lcd名稱改
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Living Room"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on kitchen"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on bedroom"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on exterior"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on bathroom"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Galley"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Dinette"


*** Test Cases ***
Scenario: lcd名稱
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light1"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light2"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light3"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light4"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light7"
    Sleep    3s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    0.5s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn on Light8"


*** Test Cases ***
Scenario: lcd1
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Living Room light on"
    Sleep    3s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "kitchen light on"
    Sleep    3s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "bedroom light on"
    Sleep    3s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "exterior light on"
    Sleep    3s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Galley light on"
    Sleep    3s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Dinette light on"



*** Test Cases ***
Scenario: LLM20
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What can you do for me"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Can you give me a checklist of things to check before traveling in an RV"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What devices can I control with the Power Pro panel"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What does the green microphone LED on the panel mean"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Why isn’t my phone automatically connecting to the panel"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "How do I pair the Power Pro panel with the mobile app using Bluetooth"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What should I do if the OTA update fails"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Can an OTA update brick my device"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "what voice command about make light brighter"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "How do I turn on voice control on the Power Pro panel"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Can you show me a list of all the voice commands"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Why is the Wi-Fi light on"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What should I do if there’s no power in my RV"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What does it mean when the red light on the fuse board comes on"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "If the lights are already on, can I say “Turn on the lights” again to make them brighte"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Can I turn off voice commands? If so, how do I turn them back on later"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Can I control the air conditioner using the Power Pro panel"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "Why are my voice commands not matching the correct light zones"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What should I say to turn off all the lights"
    Sleep    60s
    When 使用者使用預設喇叭播放文字 "Hey Power Pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s
    When 使用者使用預設喇叭播放文字 "What are the steps to pair the Power Pro panel with my mobile phone"
    Sleep    60s




*** Test Cases ***
Scenario: LLMAPP
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "turn off all lights"
    Sleep    1s
    Then 語音應該成功播放到指定聲道




*** Test Cases ***
Scenario: LLM測試
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey power pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Companion"
    Sleep    5s    
    When 使用者使用預設喇叭播放文字 "what can you do"
    
*** Test Cases ***
Scenario: 測試變形
    [Documentation]    測試使用預設喇叭播放 TTS 文字
    When 使用者使用預設喇叭播放文字 "Hey power pro"
    Sleep    1s
    Then 語音應該成功播放到指定聲道
    When 使用者使用預設喇叭播放文字 "Turn off light zone four"