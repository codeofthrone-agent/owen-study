# 本地語音驗證模組

整合文字轉語音（TTS）、音訊錄製與聲音檢測功能的專業 Robot Framework 函式庫，專為語音互動測試與聲音檢測場景設計。

## 功能特色

- 🎵 **Google TTS 整合** - 高品質多語言文字轉語音合成
- 🎤 **專業音訊錄製** - 高品質即時錄音與檔案管理
- � **智慧聲音檢測** - 基於音訊分析的聲音模式檢測
- 🎯 **同步語音驗證** - 同時進行語音播放與錄音檢測
- 📊 **音訊分析** - 音量分析、頻譜分析、聲音匹配
- 🤖 **Robot Framework 整合** - 完整的中文關鍵字支援

## 系統需求

### 必要套件

```bash
pip install gtts pygame pyaudio numpy scipy librosa matplotlib loguru pyyaml python-dotenv
```

### 音效硬體需求

- 音效卡（錄音輸入）
- 喇叭或耳機（音訊輸出）
- 支援 PyAudio 的音訊驅動程式

### Ubuntu 額外需求

```bash
sudo apt-get install python3-pyaudio portaudio19-dev
```

## 快速開始

### 1. 配置參考聲音

將您要檢測的聲音樣本（例如 `dengdeng.wav`）放置在 `libraries/local_voice_verifying/test_data/reference_sounds/` 目錄下。

### 2. Python 使用範例

```python
from libraries.local_voice_verifying import LocalVoiceVerifyingLibrary

# 初始化
lib = LocalVoiceVerifyingLibrary()

# 執行核心功能：播放 "Hey Power Pro" 並檢測 "登登" 聲
detected = lib.speak_and_detect(text="Hey Power Pro", target_sound="登登", duration=5)

if detected:
    print("成功檢測到 '登登' 聲！")
else:
    print("未檢測到 '登登' 聲。")

# 清理資源
lib.cleanup_audio_resources()
```

### 3. Robot Framework 使用範例

```robotframework
*** Settings ***
Library    libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
測試語音喚醒與回應
    ${detected}=    Speak And Detect    text=Hey Power Pro    target_sound=登登    duration=5
    Should Be True    ${detected}    未檢測到指定回應聲音
```

## Robot Framework 關鍵字

### 主要關鍵字

- `Speak And Detect`
  - **功能**: 播放指定文字並同時檢測目標聲音。
  - **參數**: `text` (要播放的文字), `target_sound` (要檢測的聲音名稱), `duration` (錄音時長)。
  - **範例**: `Speak And Detect    Hey Power Pro    登登    10`

### 輔助關鍵字

- `Start Voice Recording`: 開始錄音。
- `Stop Voice Recording`: 停止錄音並回傳檔案路徑。
- `Detect Target Sound`: 檢測指定聲音。
- `Speak Text`: 僅播放文字轉語音。
- `Set Detection Threshold`: 設定聲音檢測的相似度閾值。
- `Load Reference Sound`: 從指定路徑載入參考聲音。
- `Set TTS Language`: 設定 TTS 的語言。
- `Set TTS Speed`: 設定 TTS 的語速。
- `Cleanup Audio Resources`: 清理音訊資源。

## 目錄結構

```
libraries/local_voice_verifying/
├── LocalVoiceVerifyingLibrary.py  # 主要 Library
├── voice_tts_manager.py           # TTS 管理模組
├── voice_audio_recorder.py        # 錄音模組
├── voice_sound_detector.py        # 聲音檢測模組
├── README.md                      # 本說明文件
├── requirements.txt               # 相依套件
└── test_data/
    └── reference_sounds/          # 參考聲音樣本目錄
```

## 注意事項

1. **參考聲音**: 檢測的準確度高度依賴參考聲音的品質。請提供清晰、無雜訊的聲音樣本。
2. **硬體設備**: 請確保麥克風與喇叭正常運作。
3. **環境噪音**: 測試環境的背景噪音可能會影響檢測結果。
4. **資源清理**: 測試結束後，建議執行 `Cleanup Audio Resources` 關鍵字以釋放資源。
