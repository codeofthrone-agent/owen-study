*** Settings ***
Documentation    Voice Control Keywords - Gherkin Style
...              語音控制關鍵字資源檔案 - Gherkin 風格
...
...              This resource file provides Gherkin-style keywords for voice control.
...              It uses the VoiceControlKeywords Python library for implementation.
...
...              此資源檔案提供 Gherkin 風格的語音控制關鍵字。
...              它使用 VoiceControlKeywords Python 函式庫來實現。

Library          ../libraries/voice_control/VoiceControlKeywords.py

*** Keywords ***
Given 語音控制系統已成功初始化
    [Documentation]    Given: Confirms voice control system has been successfully initialized.
    ...                中文說明: 確認語音控制系統已成功初始化。
    Given 語音控制系統已成功初始化

Given Scarlett 4i4 音效介面已正確連接
    [Documentation]    Given: Confirms Scarlett 4i4 audio interface is properly connected.
    ...                中文說明: 確認 Scarlett 4i4 音效介面已正確連接。
    Given Scarlett 4i4 音效介面已正確連接

Given TTS 引擎已設定為 "${engine_name}"
    [Documentation]    Given: Confirms TTS engine is set to specified engine.
    ...                中文說明: 確認 TTS 引擎已設定為指定引擎。
    [Arguments]    ${engine_name}
    Given TTS 引擎已設定為 "${engine_name}"    ${engine_name}

Given TTS 語言已設定為 "${language}"
    [Documentation]    Given: Confirms TTS language is set to specified language.
    ...                中文說明: 確認 TTS 語言已設定為指定語言。
    [Arguments]    ${language}
    Given TTS 語言已設定為 "${language}"    ${language}

When 使用者播放文字 "${text}" 到聲道 "${channel}"
    [Documentation]    When: User plays text to specified channel.
    ...                中文說明: 使用者播放文字到指定聲道。
    [Arguments]    ${text}    ${channel}
    When 使用者播放文字 "${text}" 到聲道 "${channel}"    ${text}    ${channel}

When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"
    [Documentation]    When: User plays text to specified channel using specified language.
    ...                中文說明: 使用者播放文字到指定聲道使用指定語言。
    [Arguments]    ${text}    ${channel}    ${language}
    When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"    ${text}    ${channel}    ${language}

Then 語音應該成功播放到指定聲道
    [Documentation]    Then: Speech should play successfully to specified channel.
    ...                中文說明: 語音應該成功播放到指定聲道。
    Then 語音應該成功播放到指定聲道

And 暫存檔案應該正確清理
    [Documentation]    And: Temporary files should be cleaned properly.
    ...                中文說明: 暫存檔案應該正確清理。
    And 暫存檔案應該正確清理

*** Variables ***
# 預設配置
${DEFAULT_LANGUAGE}     en
${DEFAULT_ENGINE}       gtts
${DEFAULT_SPEED}        180
${DEFAULT_DURATION}     5

# 語言代碼對照
${LANG_ENGLISH}         en
${LANG_CHINESE_TW}      zh-TW
${LANG_CHINESE_CN}      zh-CN
${LANG_JAPANESE}        ja
${LANG_KOREAN}          ko

# TTS 引擎
${ENGINE_GTTS}          gtts
${ENGINE_PYTTSX3}       pyttsx3

# Scarlett 聲道
${CHANNEL_1}            1
${CHANNEL_2}            2
${CHANNEL_3}            3
${CHANNEL_4}            4