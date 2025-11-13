# LocalVoiceVerifyingLibrary 重構指南

## 📅 重構日期
2025-11-07

## 🎯 重構目標

移除 TTS（文字轉語音）相關功能，專注於核心職責：**聲音檢測與驗證**。

TTS 功能已於 2025-11-06 遷移至 `voice_control` 模組。

## ⚠️ 重大變更

### 移除的關鍵字

以下 Robot Framework 關鍵字將被移除：

| 關鍵字 | 狀態 | 替代方案 |
|--------|------|---------|
| `Speak Text` | ❌ 移除 | 使用 `VoiceControlKeywords.播放文字到聲道` |
| `Set TTS Language` | ❌ 移除 | 使用 `VoiceControlKeywords.設定 TTS 語言` |
| `Set TTS Speed` | ❌ 移除 | 使用 `VoiceControlKeywords.設定 TTS 語速` |
| `Speak And Detect` | ⚠️ 需重新設計 | 見下方說明 |

### 移除的內部組件

1. **TTSManager 匯入**
   ```python
   # ❌ 移除
   from .voice_tts_manager import TTSManager
   self.tts_manager = TTSManager()
   ```

2. **TTS 相關方法**
   - `speak_text()`
   - `set_tts_language()`
   - `set_tts_speed()`

3. **TTS 相關配置**
   - 從 `voice_config.py` 匯入的 `TTS_CONFIG`

### 保留的核心功能

✅ **保留以下功能（核心職責）：**

1. **音訊錄製**
   - `Start Voice Recording`
   - `Stop Voice Recording`
   - `Get Recording Status`

2. **聲音檢測**
   - `Detect Target Sound`
   - `Load Reference Sound`
   - `Compare Audio Samples`

3. **錄音管理**
   - `Save Recording`
   - `Clear Recordings`

## 🔧 重構步驟

### 步驟 1：移除 TTS 匯入

**檔案：** `libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py`

```python
# ❌ 移除這行
from .voice_tts_manager import TTSManager

# ❌ 移除 TTS_CONFIG 匯入
from config.voice_config import (
    ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG,  # ← 移除 TTS_CONFIG
    DETECTION_CONFIG, PATHS, get_config_value, create_directories
)

# ✅ 修改為
from config.voice_config import (
    ROBOT_CONFIG, AUDIO_CONFIG, DETECTION_CONFIG,
    PATHS, get_config_value, create_directories
)
```

### 步驟 2：移除 TTS Manager 初始化

```python
# 在 __init__() 方法中

# ❌ 移除
self.tts_manager = TTSManager(
    tts_config=TTS_CONFIG,
    audio_config=AUDIO_CONFIG
)

# ✅ 保留
self.audio_recorder = AudioRecorder(
    audio_config=AUDIO_CONFIG,
    paths=PATHS
)
self.sound_detector = SoundDetector(
    detection_config=DETECTION_CONFIG
)
```

### 步驟 3：移除 TTS 相關方法

移除以下方法（約行號 607-710）：

```python
# ❌ 完全移除以下方法
@keyword('Set TTS Language')
def set_tts_language(self, language: str = 'en') -> bool:
    # ...

@keyword('Set TTS Speed')
def set_tts_speed(self, speed: float = 1.0) -> bool:
    # ...

@keyword('Speak Text')
def speak_text(self, text: str) -> bool:
    # ...
```

### 步驟 4：處理 `Speak And Detect`

**選項 A：完全移除（推薦）**

```python
# ❌ 完全移除
@keyword('Speak And Detect')
def speak_and_detect(self, text: str, target_sound: str, ...) -> Dict:
    # ...
```

**選項 B：重新實作（使用新的 VoiceControlKeywords）**

```python
# 如果要保留，需要整合新的 voice_control
from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords

def __init__(self):
    # ...
    self.voice_control = VoiceControlKeywords()

@keyword('Speak And Detect')
def speak_and_detect(self, text: str, target_sound: str, duration: int = 10) -> Dict:
    """
    [DEPRECATED] 此關鍵字將在未來版本移除
    請改用分離的方式：
    1. 使用 VoiceControlKeywords.播放文字到聲道
    2. 使用 LocalVoiceVerifyingLibrary.Start Voice Recording
    3. 使用 LocalVoiceVerifyingLibrary.Detect Target Sound
    """
    logger.warning("Speak And Detect 已棄用，建議使用分離的錄音與播放")

    # 開始錄音
    self.start_voice_recording(duration)

    # 播放文字（使用 voice_control）
    self.voice_control.speak_text_to_channel(text, channel=1, language='en')

    # 等待錄音完成
    time.sleep(duration)

    # 停止錄音
    recording_path = self.stop_voice_recording()

    # 檢測聲音
    detected, confidence, details = self.detect_target_sound(
        target_sound=target_sound,
        audio_file=recording_path
    )

    return {
        'detected': detected,
        'confidence': confidence,
        'details': details
    }
```

**建議：選擇選項 A**，因為：
- 職責更清晰
- 避免模組間的循環依賴
- 鼓勵使用者使用新的模組化方式

### 步驟 5：更新文檔字串

```python
class LocalVoiceVerifyingLibrary:
    """
    本地語音驗證 Robot Framework Library

    提供以下主要功能：
    1. 即時音訊錄製
    2. 聲音檢測與識別
    3. 錄音管理與分析

    注意：TTS (文字轉語音) 功能已遷移至 voice_control 模組。
    如需 TTS 功能，請使用 VoiceControlKeywords。
    """
```

## 📋 受影響的測試檔案

### tests/physical_interaction/voice_test.robot

**需要更新的測試案例：**

```robotframework
# ❌ 舊的方式（已不可用）
*** Settings ***
Library    ../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
測試語音喚醒
    Speak Text    Hey Power Pro
    Set TTS Language    zh-TW
```

```robotframework
# ✅ 新的方式（推薦）
*** Settings ***
Library    ../../libraries/voice_control/VoiceControlKeywords.py
Library    ../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
測試語音喚醒
    # 使用 voice_control 播放
    播放文字到聲道    Hey Power Pro    1    en

    # 使用 local_voice_verifying 錄音與檢測
    Start Voice Recording    10
    Sleep    5s
    ${recording}=    Stop Voice Recording
    ${detected}=    Detect Target Sound    登登    ${recording}
```

## ✅ 驗證檢查清單

### 程式碼驗證

- [ ] 移除 TTSManager 匯入
- [ ] 移除 TTS_CONFIG 匯入
- [ ] 移除 tts_manager 初始化
- [ ] 移除 `speak_text()` 方法
- [ ] 移除 `set_tts_language()` 方法
- [ ] 移除 `set_tts_speed()` 方法
- [ ] 處理 `speak_and_detect()` 方法（移除或重新實作）
- [ ] 更新類別文檔字串

### 測試驗證

- [ ] 更新 `voice_test.robot`
- [ ] 執行測試確認錄音功能正常
- [ ] 執行測試確認聲音檢測功能正常
- [ ] 確認沒有使用已移除的 TTS 關鍵字

### 文檔更新

- [ ] 更新 `libraries/local_voice_verifying/README.md`
- [ ] 更新 `keywords_readme.md`
- [ ] 更新 `CLAUDE.md`（已完成）

## 🚀 執行重構

### 測試重構後的功能

```bash
# 1. 測試錄音功能
python3 -c "
from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
lib = LocalVoiceVerifyingLibrary()
lib.start_voice_recording(5)
print('✅ 錄音功能正常')
"

# 2. 執行更新後的測試
robot tests/physical_interaction/voice_test.robot
```

## 📝 遷移範例

### 範例 1：簡單的 TTS 播放

**舊方式：**
```robotframework
*** Test Cases ***
播放文字
    Speak Text    Hello World
```

**新方式：**
```robotframework
*** Settings ***
Library    ../../libraries/voice_control/VoiceControlKeywords.py

*** Test Cases ***
播放文字
    播放文字到聲道    Hello World    1    en
```

### 範例 2：語音喚醒檢測

**舊方式：**
```robotframework
*** Test Cases ***
測試語音喚醒
    ${result}=    Speak And Detect    Hey Power Pro    登登    10
    Should Be True    ${result}[detected]
```

**新方式：**
```robotframework
*** Settings ***
Library    ../../libraries/voice_control/VoiceControlKeywords.py
Library    ../../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py

*** Test Cases ***
測試語音喚醒
    # 開始錄音
    Start Voice Recording    10

    # 播放喚醒詞
    播放文字到聲道    Hey Power Pro    1    en

    # 等待並停止錄音
    Sleep    5s
    ${recording}=    Stop Voice Recording

    # 檢測聲音
    ${detected}  ${confidence}  ${details}=    Detect Target Sound    登登    ${recording}
    Should Be True    ${detected}
```

## 🎯 重構後的優勢

1. **職責清晰**
   - LocalVoiceVerifyingLibrary：專注於聲音檢測（輸入）
   - VoiceControlKeywords：專注於語音輸出（輸出）

2. **模組獨立**
   - 各模組可獨立使用
   - 降低耦合度

3. **易於維護**
   - TTS 功能集中在 voice_control
   - 聲音檢測集中在 local_voice_verifying

4. **擴展性更好**
   - 可輕鬆新增新的 TTS 引擎到 voice_control
   - 可輕鬆新增新的檢測算法到 local_voice_verifying

## 📞 需要協助？

如遇到問題，請檢查：

1. **相關文檔**
   - [TTS 遷移指南](voice_control_tts_migration.md)
   - [TTS 整合摘要](voice_control_tts_integration_summary.md)
   - [多感官檢測實作摘要](voice_assistant_multimodal_detection_implementation_summary.md)

2. **測試新功能**
   ```bash
   # 測試 voice_control TTS
   robot tests/voice_control/voice_tts_integration_test.robot

   # 測試 local_voice_verifying 錄音檢測
   robot tests/physical_interaction/voice_test.robot
   ```

---

**重構完成標準：**
1. ✅ 所有 TTS 相關程式碼已移除
2. ✅ 測試案例已更新
3. ✅ 文檔已更新
4. ✅ 所有測試通過

**重構狀態：** ⏳ 待執行（文檔已完成，等待實際重構）
