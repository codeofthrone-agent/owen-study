*** Settings ***
Documentation     語音控制各模組關鍵字封裝 (Resource 層)
Library           ../libraries/voice_control/VoiceControlKeywords.py
Library           String
Library           Collections

*** Variables ***
# 預設參數 (對齊 TTSManager.py)
${DEFAULT_ENGINE}       gtts
${DEFAULT_LANGUAGE}     en
${DEFAULT_SPEED}        180
${DEFAULT_DURATION}     5

# 常用聲道常數
${CHANNEL_1}            1
${CHANNEL_2}            2
${CHANNEL_3}            3
${CHANNEL_4}            4

*** Keywords ***
Given Scarlett 設備已就緒
    [Documentation]    [Alias] 確認音效介面已準備就緒
    Given Scarlett 4i4 音效介面已正確連接

Given 設定語音環境
    [Arguments]    ${engine}=${DEFAULT_ENGINE}    ${language}=${DEFAULT_LANGUAGE}    ${speed}=${DEFAULT_SPEED}
    [Documentation]    [Alias] 設定 TTS 環境 (支援預設值)
    Given 語音控制系統已成功初始化
    Given TTS 引擎已設定為 "${engine}"
    Given TTS 語言已設定為 "${language}"
    Given TTS 語速已設定為 "${speed}"
