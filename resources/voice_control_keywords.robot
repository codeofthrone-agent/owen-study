*** Settings ***
Documentation    Voice Control Keywords - Gherkin Style
...              語音控制關鍵字資源檔案 - Gherkin 風格
...
...              This resource file imports the VoiceControlKeywords Python library.
...              All keywords are defined in the Python library with @keyword decorator.
...              Do not redefine keywords here - they are already available from the library.
...
...              此資源檔案匯入 VoiceControlKeywords Python 函式庫。
...              所有關鍵字都在 Python 函式庫中透過 @keyword 裝飾器定義。
...              不要在此重複定義關鍵字 - 它們已經可以從函式庫中使用。

Library          ../libraries/voice_control/VoiceControlKeywords.py

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
