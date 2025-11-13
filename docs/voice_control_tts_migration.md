# 語音控制 TTS 整合遷移指南

## 📅 遷移日期
2025-11-06

## 🎯 遷移目標

將 TTS（文字轉語音）功能從 `local_voice_verifying` 模組遷移到 `voice_control` 模組，實現：

1. **職責清晰化** - local_voice_verifying 專注於聲音檢測，voice_control 負責聲音輸出
2. **硬體整合** - TTS 與 Scarlett 4i4 聲道控制深度整合
3. **功能增強** - 支援四聲道獨立 TTS 輸出

---

## 📊 架構變更

### 變更前（舊架構）

```
local_voice_verifying/
├── voice_tts_manager.py        # TTS 管理
├── voice_audio_recorder.py     # 錄音
├── voice_sound_detector.py     # 聲音檢測
└── LocalVoiceVerifyingLibrary.py
    ├── Speak Text              # TTS 關鍵字
    ├── Set TTS Language
    ├── Set TTS Speed
    ├── Start Voice Recording
    └── Detect Target Sound
```

### 變更後（新架構）

```
voice_control/                   # 新增：語音輸出控制
├── TTSManager.py               # 從 local_voice_verifying 遷移
├── AudioPlayer.py              # 重構自 ultimate_play.py
├── VoiceControlKeywords.py     # 新增：整合關鍵字
└── AudioKeywords.py            # 原有：硬體控制

local_voice_verifying/           # 精簡：專注聲音檢測
├── voice_audio_recorder.py     # 保留：錄音
├── voice_sound_detector.py     # 保留：聲音檢測
└── LocalVoiceVerifyingLibrary.py
    ├── Start Voice Recording   # 保留
    ├── Stop Voice Recording    # 保留
    ├── Detect Target Sound     # 保留
    └── Speak And Detect        # ❌ 移除或標記為 deprecated
```

---

## ⚠️ 不相容變更清單

### 1. 模組位置變更

#### TTS 功能遷移

| 舊位置 | 新位置 | 狀態 |
|--------|--------|------|
| `libraries/local_voice_verifying/voice_tts_manager.py` | `libraries/voice_control/TTSManager.py` | ✅ 已遷移 |
| `libraries/voice_control/ultimate_play.py` | `libraries/voice_control/AudioPlayer.py` | ✅ 已重構 |

**影響：**
- 直接 import `voice_tts_manager` 的程式碼需要更新
- `ultimate_play.py` 的直接調用需要改為 `AudioPlayer.py`

#### 修復方式：

```python
# ❌ 舊的 import
from libraries.local_voice_verifying.voice_tts_manager import TTSManager

# ✅ 新的 import
from libraries.voice_control.TTSManager import TTSManager
```

---

### 2. Robot Framework 關鍵字變更

#### 移除的關鍵字（LocalVoiceVerifyingLibrary）

以下關鍵字已從 `LocalVoiceVerifyingLibrary` 移除：

| 關鍵字 | 狀態 | 替代方案 |
|--------|------|----------|
| `Speak Text` | ❌ 移除 | 使用 `VoiceControlKeywords.播放文字到聲道` |
| `Set TTS Language` | ❌ 移除 | 使用 `VoiceControlKeywords.設定 TTS 語言` |
| `Set TTS Speed` | ❌ 移除 | 使用 `VoiceControlKeywords.設定 TTS 語速` |
| `Speak And Detect` | ⚠️ 待定 | 需要重新實作或移除 |

**影響的測試檔案：**
- `tests/physical_interaction/voice_test.robot`

#### 新增的關鍵字（VoiceControlKeywords）

| 關鍵字 | 說明 |
|--------|------|
| `播放文字到聲道` | 核心功能：TTS + 聲道控制 |
| `設定 TTS 引擎` | 切換 gtts/pyttsx3 |
| `設定 TTS 語言` | 設定語言（en, zh-TW, ja 等）|
| `設定 TTS 語速` | 設定語速（120-250）|
| `播放語音到所有聲道` | 測試四聲道 |
| `檢查 Scarlett 設備` | 設備檢查 |
| `清理語音控制資源` | 資源清理 |

---

### 3. 測試案例變更

#### 需要更新的測試檔案

**`tests/physical_interaction/voice_test.robot`**

這個檔案需要重大修改：

**變更項目：**

1. **Library 匯入變更：**

```robotframework
# ❌ 舊的
Library    ${CURDIR}/../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

# ✅ 新的（如果需要 TTS 功能）
Library    ${CURDIR}/../../libraries/voice_control/VoiceControlKeywords.py
Library    ${CURDIR}/../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
Resource   ${CURDIR}/../../resources/voice_control_keywords.robot
```

2. **關鍵字使用變更：**

```robotframework
# ❌ 舊的
Speak Text    Hey Power Pro
Set TTS Language    zh-TW
Set TTS Speed    1.0

# ✅ 新的
播放文字到聲道    Hey Power Pro    1    en
設定 TTS 語言    zh-TW
設定 TTS 語速    180
```

3. **`Speak And Detect` 關鍵字處理：**

**選項 A：分離使用（推薦）**

```robotframework
# 使用 voice_control 播放 + local_voice_verifying 檢測
Start Voice Recording    10
播放文字到聲道    Hey Power Pro    1    en
${detected}=    Detect Target Sound    登登
```

**選項 B：在 LocalVoiceVerifyingLibrary 中重新實作**

需要在 `LocalVoiceVerifyingLibrary.py` 中依賴 `VoiceControlKeywords`：

```python
from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords

class LocalVoiceVerifyingLibrary:
    def __init__(self):
        self.voice_control = VoiceControlKeywords()
        ...

    @keyword('Speak And Detect')
    def speak_and_detect(self, text, target_sound, duration=10):
        # 開始錄音
        self.audio_recorder.start_recording(duration)
        # 使用 voice_control 播放
        self.voice_control.speak_text_to_channel(text, 1)
        # 檢測
        ...
```

---

### 4. 配置檔案變更

**`config/voice_config.py`**

需要確保配置可被兩個模組共用：

```python
# TTS 配置（voice_control 使用）
TTS_CONFIG = {
    'primary_engine': 'gtts',
    'fallback_engine': 'pyttsx3',
    'gtts': {'language': 'en', 'slow': False},
    'pyttsx3': {'rate': 180, 'volume': 0.8, 'voice_id': 0}
}

# 音訊配置（local_voice_verifying 使用）
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'channels': 1,
    ...
}
```

**影響：** 無，配置保持統一，兩個模組都從 `config.voice_config` 匯入

---

## 🔧 遷移步驟

### 步驟 1：更新測試案例

#### 1.1 識別受影響的測試檔案

```bash
# 搜尋使用 TTS 關鍵字的測試檔案
grep -r "Speak Text\|Set TTS Language\|Set TTS Speed" tests/
```

#### 1.2 更新 `voice_test.robot`

**選項 A：完全重寫（推薦）**

移除 TTS 相關測試，專注於聲音檢測：

```robotframework
*** Test Cases ***
測試聲音檢測功能
    [Documentation]    測試錄音與聲音檢測
    Given 準備參考聲音    登登
    When 開始錄音    10
    And 播放測試音訊    test_audio.wav
    And 停止錄音
    Then 應該檢測到目標聲音    登登
```

**選項 B：保留並修改**

更新為使用新的 VoiceControlKeywords：

```robotframework
*** Settings ***
Library    ../../libraries/voice_control/VoiceControlKeywords.py
Library    ../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
測試語音助手喚醒檢測
    # 使用新的整合方式
    Start Voice Recording    10
    播放文字到聲道    Hey Power Pro    1    en
    ${detected}=    Detect Target Sound    登登
    Should Be True    ${detected}
```

---

### 步驟 2：更新自定義程式碼

如果有其他程式碼直接使用 `voice_tts_manager`：

```bash
# 搜尋所有匯入
grep -r "from.*voice_tts_manager\|import.*voice_tts_manager" libraries/ tests/
```

更新匯入路徑：

```python
# ❌ 舊的
from libraries.local_voice_verifying.voice_tts_manager import TTSManager

# ✅ 新的
from libraries.voice_control.TTSManager import TTSManager
```

---

### 步驟 3：處理 LocalVoiceVerifyingLibrary

#### 選項 A：完全移除 TTS 關鍵字（乾淨方案）

修改 `LocalVoiceVerifyingLibrary.py`：

```python
class LocalVoiceVerifyingLibrary:
    def __init__(self):
        # ❌ 移除
        # self.tts_manager = TTSManager()

        # ✅ 保留
        self.audio_recorder = AudioRecorder()
        self.sound_detector = SoundDetector()

    # ❌ 移除所有 TTS 相關方法
    # @keyword('Speak Text')
    # @keyword('Set TTS Language')
    # @keyword('Set TTS Speed')
    # @keyword('Speak And Detect')
```

#### 選項 B：標記為 Deprecated 並轉發

保留方法但標記為已棄用：

```python
from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords

class LocalVoiceVerifyingLibrary:
    def __init__(self):
        self.voice_control = VoiceControlKeywords()
        self.audio_recorder = AudioRecorder()
        self.sound_detector = SoundDetector()

    @keyword('Speak Text')
    def speak_text(self, text: str) -> bool:
        """
        [DEPRECATED] 此關鍵字已棄用，請使用 VoiceControlKeywords.播放文字到聲道
        """
        logger.warning("Speak Text 已棄用，請改用 播放文字到聲道")
        return self.voice_control.speak_text_to_channel(text, 1, 'en')
```

---

### 步驟 4：驗證遷移

#### 4.1 測試新功能

```bash
# 測試 voice_control 整合
cd /home/thortron/Tools/robot-multiplatform-automation
robot tests/voice_control/voice_tts_integration_test.robot
```

#### 4.2 測試受影響的現有測試

```bash
# 測試 voice_test.robot（如果保留）
robot tests/physical_interaction/voice_test.robot
```

#### 4.3 單元測試

```bash
# 測試 TTSManager
cd libraries/voice_control
python3 TTSManager.py

# 測試 AudioPlayer
python3 AudioPlayer.py file_example_WAV_2MG.wav 1

# 測試 VoiceControlKeywords
python3 VoiceControlKeywords.py
```

---

## 📝 遷移檢查清單

### 程式碼遷移

- [x] ✅ TTSManager 已遷移到 voice_control
- [x] ✅ AudioPlayer 已創建並重構
- [x] ✅ VoiceControlKeywords 已實作
- [x] ✅ text_to_file() 方法已新增
- [x] ✅ Robot 關鍵字資源檔已創建

### 測試案例

- [ ] ⏳ 更新 `voice_test.robot`（待決定選項 A 或 B）
- [x] ✅ 新增 `voice_tts_integration_test.robot`
- [ ] ⏳ 驗證所有測試通過

### 文檔更新

- [ ] ⏳ 更新 README.md
- [ ] ⏳ 更新 CLAUDE.md
- [ ] ⏳ 更新 keywords_readme.md
- [ ] ⏳ 更新 spec.md

### LocalVoiceVerifyingLibrary 處理

- [ ] ⏳ 決定採用選項 A（移除）或選項 B（deprecated）
- [ ] ⏳ 實作選擇的方案
- [ ] ⏳ 更新相關測試

---

## 🎯 建議的遷移策略

### 推薦：漸進式遷移

1. **階段一：新功能先行（已完成）**
   - ✅ 建立 voice_control TTS 模組
   - ✅ 新增測試案例驗證功能

2. **階段二：標記舊功能為 Deprecated**
   - 在 LocalVoiceVerifyingLibrary 中標記 TTS 方法為 deprecated
   - 內部轉發到新的 VoiceControlKeywords
   - 確保現有測試仍可運行

3. **階段三：更新測試案例**
   - 逐步更新 voice_test.robot
   - 新測試使用新 API

4. **階段四：移除舊功能**
   - 確認所有測試都已遷移
   - 完全移除 LocalVoiceVerifyingLibrary 中的 TTS 功能

---

## 📞 需要協助？

如遇到遷移問題，請檢查：

1. **Scarlett 設備狀態：**
   ```bash
   wpctl status | grep Scarlett
   ```

2. **PipeWire 路由設定：**
   ```bash
   cd libraries/voice_control
   ./setup_pipewire_routing_v3.sh
   ```

3. **Python 依賴：**
   ```bash
   pip list | grep -E "gtts|pyttsx3"
   ```

4. **測試環境：**
   ```bash
   python3 libraries/voice_control/VoiceControlKeywords.py
   ```

---

## 📚 相關文檔

- [Scarlett 4i4 設定指南](../libraries/voice_control/README.md)
- [VoiceControlKeywords API 文檔](../libraries/voice_control/VoiceControlKeywords.py)
- [測試案例範例](../tests/voice_control/voice_tts_integration_test.robot)
- [Robot 關鍵字資源](../resources/voice_control_keywords.robot)

---

## 🔄 回滾方案

如果遷移出現問題，可以：

1. **保留舊模組：** `local_voice_verifying/voice_tts_manager.py` 未被刪除
2. **測試案例備份：** 建議先備份 `voice_test.robot`
3. **回復 import：** 修改 import 路徑即可回滾

---

## ✅ 遷移完成標準

遷移被視為完成的標準：

1. ✅ 新的 VoiceControlKeywords 測試全部通過
2. ⏳ 舊的 voice_test.robot 已更新或重寫
3. ⏳ LocalVoiceVerifyingLibrary 中 TTS 功能已處理（移除或標記）
4. ⏳ 所有文檔已更新
5. ⏳ 所有相關測試通過

**當前狀態：** 階段一完成，等待用戶決定後續處理方案
