*** Settings ***
Library    libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
Simple Speak Text Test
    [Documentation]    簡單的 Speak Text 測試
    Speak Text    Hello World
    Log    Test completed successfully
