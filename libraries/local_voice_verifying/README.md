# 本地語音驗證模組

這是一個為 Robot Framework 設計的本地語音驗證系統，實現了 "PC 利用 google tts 發出聲音 Hey Power Pro 並同時錄音 檢測 是否收到 登登的聲音" 的功能需求。

## 功能特點

- **多引擎 TTS 支援**: Google TTS (在線) + pyttsx3 (離線) 備援機制
- **即時音訊錄製**: 基於 PyAudio 的高品質音訊錄製
- **智能聲音檢測**: MFCC 特徵提取 + DTW 相似度比對
- **Robot Framework 整合**: 提供完整的關鍵字介面
- **跨平台支援**: 主要支援 macOS，次要支援 Windows/Linux

## 安裝方式

### 1. 安裝相依套件

```bash
# 確保 Python 3.8+ 已安裝
pip install -r requirements.txt

# macOS 需要額外安裝 portaudio
brew install portaudio
```

### 2. 音訊權限設定 (macOS)

在 macOS 系統中，需要給予應用程式麥克風權限：
1. 開啟「系統偏好設定」→「安全性與隱私」→「隱私權」
2. 選擇「麥克風」
3. 勾選您的終端機應用程式 (Terminal, iTerm2 等)

### 3. 準備參考聲音檔案

將目標聲音的參考音訊檔案放置在 `audio_samples/reference_sounds/` 目錄下：

```
audio_samples/
└── reference_sounds/
    ├── 登登.wav          # 參考聲音檔案
    ├── beep.wav          # 其他參考聲音
    └── notification.wav  # 更多參考聲音
```

支援的音訊格式：WAV, MP3, M4A

## 使用方式

### Robot Framework 測試

```robot
*** Settings ***
Library    libraries.local_voice_verifying.LocalVoiceVerifyingLibrary

*** Test Cases ***
Test Voice Detection
    [Documentation]    測試語音檢測功能
    # 設定 TTS 語言和速度
    Set TTS Language    zh-TW
    Set TTS Speed       1.0
    
    # 設定檢測閾值
    Set Detection Threshold    0.75
    
    # 執行語音檢測
    ${result} =    Speak And Detect    Hey Power Pro    登登    10
    Should Be True    ${result}
    
    # 獲取詳細結果
    ${details} =    Get Detection Result
    Should Be True    ${details['detected']}
    Should Be True    ${details['confidence']} > 0.7
    
    # 清理資源
    Cleanup Audio Resources

Test Individual Functions
    [Documentation]    測試個別功能
    # 載入參考聲音
    Load Reference Sound    登登    /path/to/dengdeng.wav
    
    # 開始錄音
    Start Voice Recording    5
    Sleep    2s
    
    # 停止錄音並保存
    ${file_path} =    Stop Voice Recording
    Should Not Be Empty    ${file_path}
    
    # 檢測聲音
    ${detected} =    Detect Target Sound    登登    ${file_path}
    Log    Detection result: ${detected}
```

### Python 腳本使用

```python
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary

# 建立 Library 實例
lib = LocalVoiceVerifyingLibrary()

# 設定參數
lib.set_tts_language('zh-TW')
lib.set_detection_threshold(0.75)

# 執行檢測
result = lib.speak_and_detect("Hey Power Pro", "登登", 10)
print(f"檢測結果: {result}")

# 獲取詳細資訊
details = lib.get_detection_result()
print(f"信心度: {details.get('confidence', 0)}")

# 清理資源
lib.cleanup_audio_resources()
```

## 核心關鍵字說明

### 主要關鍵字

- **`Speak And Detect`**: 核心功能，播放文字並同時檢測目標聲音
- **`Start Voice Recording`**: 開始音訊錄製
- **`Stop Voice Recording`**: 停止錄製並保存檔案
- **`Detect Target Sound`**: 檢測指定聲音
- **`Get Detection Result`**: 獲取詳細檢測結果

### 設定關鍵字

- **`Set Detection Threshold`**: 設定檢測閾值 (0.0-1.0)
- **`Load Reference Sound`**: 載入參考聲音檔案
- **`Set TTS Language`**: 設定 TTS 語言
- **`Set TTS Speed`**: 設定 TTS 播放速度
- **`Cleanup Audio Resources`**: 清理音訊資源

## 技術規格

### 音訊處理
- 取樣率: 16 kHz (語音優化)
- 聲道: 單聲道
- 位元深度: 16-bit
- 格式: WAV

### 聲音檢測算法
- 特徵提取: MFCC (13維) + Delta + Delta-Delta
- 相似度計算: DTW (動態時間規整) / 餘弦相似度
- 預設閾值: 0.75
- 分析窗口: 1秒，50% 重疊

### 效能需求
- 檢測延遲: < 200ms
- 記憶體使用: < 50MB
- CPU 使用率: < 30%
- 準確率目標: > 90%

## 疑難排解

### 常見問題

1. **音訊設備無法存取**
   ```
   錯誤: pyaudio 初始化失敗
   解決: 檢查麥克風權限設定
   ```

2. **TTS 播放失敗**
   ```
   錯誤: Google TTS 網路連線失敗
   解決: 系統會自動切換到離線 TTS (pyttsx3)
   ```

3. **參考聲音載入失敗**
   ```
   錯誤: 找不到參考聲音檔案
   解決: 確認檔案路徑和格式正確
   ```

4. **檢測準確率低**
   ```
   解決方案:
   - 調整檢測閾值 (降低到 0.6-0.7)
   - 改善參考聲音品質
   - 減少背景噪音
   ```

### 日誌檔案

系統會在 `logs/` 目錄下產生詳細日誌：
- `voice_library.log`: 主要 Library 日誌
- `tts_manager.log`: TTS 相關日誌
- `audio_recorder.log`: 錄音相關日誌
- `sound_detector.log`: 檢測相關日誌

### 除錯模式

```python
# 啟用詳細日誌
import logging
logging.basicConfig(level=logging.DEBUG)

# 獲取檢測統計
lib = LocalVoiceVerifyingLibrary()
stats = lib.sound_detector.get_detection_statistics()
print(f"檢測統計: {stats}")
```

## 目錄結構

```
libraries/local_voice_verifying/
├── spec.md                         # 規格文件
├── todo.md                         # 任務清單
├── README.md                       # 說明文件
├── requirements.txt                # 相依套件
├── LocalVoiceVerifyingLibrary.py   # 主要 Library
├── voice_config.py                 # 配置模組
├── voice_tts_manager.py            # TTS 管理
├── voice_audio_recorder.py         # 音訊錄製
├── voice_sound_detector.py         # 聲音檢測
├── audio_samples/                  # 音訊樣本
│   ├── reference_sounds/           # 參考聲音
│   ├── recorded/                   # 錄音檔案
│   └── temp/                       # 暫存檔案
├── logs/                           # 日誌檔案
├── test_data/                      # 測試數據
└── models/                         # 模型檔案
```

## 版本歷史

- **v1.0.0**: 初始版本，實現基本語音檢測功能
  - TTS 播放功能
  - 音訊錄製功能
  - MFCC 特徵檢測
  - Robot Framework 整合

## 授權與支援

本專案遵循專案授權條款。如需技術支援或回報問題，請聯繫開發團隊。

## 貢獻指南

歡迎提交功能改善建議或錯誤回報。請遵循以下步驟：

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

## 致謝

感謝以下開源專案的支援：
- Robot Framework
- librosa (音訊分析)
- gTTS (Google Text-to-Speech)
- PyAudio (音訊處理)
- pyttsx3 (離線 TTS)
