# 語音控制 TTS 整合完成摘要

## ✅ 已完成的工作

### 1. 核心模組建立

#### TTSManager (新建)
**位置：** [libraries/voice_control/TTSManager.py](libraries/voice_control/TTSManager.py)

**主要功能：**
- 支援 Google TTS (gtts) 和離線 TTS (pyttsx3)
- 新增 `text_to_file()` 方法：生成音訊檔案供 AudioPlayer 使用
- 引擎切換、語言設定、語速控制
- 自動暫存檔案管理

**關鍵方法：**
```python
text_to_file(text, output_file=None, language='en', format='mp3') -> str
set_engine(engine_name: str) -> bool
set_language(language: str) -> bool
set_voice_speed(speed: float) -> bool
```

---

#### AudioPlayer (重構)
**位置：** [libraries/voice_control/AudioPlayer.py](libraries/voice_control/AudioPlayer.py)

**變更：**
- 從 `ultimate_play.py` 重構為類別化設計
- 新增設備檢查功能
- 優化錯誤處理

**關鍵方法：**
```python
play_to_channel(audio_file, target_channel, duration=5) -> bool
get_current_sink() -> str
list_available_sinks() -> list
```

---

#### VoiceControlKeywords (新建)
**位置：** [libraries/voice_control/VoiceControlKeywords.py](libraries/voice_control/VoiceControlKeywords.py)

**主要功能：**
- 整合 TTSManager 和 AudioPlayer
- 提供 Robot Framework 關鍵字
- 實現「文字轉語音並輸出到指定聲道」

**核心關鍵字：**
```robotframework
播放文字到聲道    ${text}    ${channel}    ${language}=en    ${duration}=5
設定 TTS 引擎      ${engine_name}
設定 TTS 語言      ${language}
設定 TTS 語速      ${speed}
播放語音到所有聲道 ${text}    ${language}=en    ${duration}=3
檢查 Scarlett 設備
```

---

### 2. Robot Framework 資源

#### 關鍵字資源檔
**位置：** [resources/voice_control_keywords.robot](resources/voice_control_keywords.robot)

**提供的輔助關鍵字：**
- `Scarlett 設備已就緒` - Given 關鍵字
- `設定語音環境` - 一次設定引擎、語言、語速
- `從聲道播放文字` - When 關鍵字
- `應該成功播放語音` - Then 關鍵字
- `清理語音資源` - Teardown 關鍵字

---

### 3. 測試案例

#### 整合測試
**位置：** [tests/voice_control/voice_tts_integration_test.robot](tests/voice_control/voice_tts_integration_test.robot)

**測試場景：**
1. ✅ 英文 TTS 輸出到聲道 1
2. ✅ 中文 TTS 輸出到聲道 3
3. ✅ 四聲道依序播放
4. ✅ TTS 引擎切換（gtts ↔ pyttsx3）
5. ✅ 多語言支援（英文、中文、日文）
6. ✅ 語速控制（慢速、正常、快速）
7. ✅ 設備檢查功能
8. ✅ TTS 引擎資訊查詢
9. ✅ 長文本播放
10. ✅ 聲道獨立性測試

---

### 4. 遷移文檔

**位置：** [docs/voice_control_tts_migration.md](docs/voice_control_tts_migration.md)

**包含內容：**
- 架構變更說明
- 不相容變更清單
- 遷移步驟指南
- 回滾方案

---

## 🎯 使用範例

### 基本使用

```robotframework
*** Settings ***
Library    libraries/voice_control/VoiceControlKeywords.py
Resource   resources/voice_control_keywords.robot

*** Test Cases ***
測試語音輸出
    Given 設定語音環境    language=en    engine=gtts
    When ${result}=    從聲道播放文字    Hello World    1
    Then 應該成功播放語音    ${result}
    [Teardown]    清理語音資源
```

### 多語言測試

```robotframework
測試多語言
    Given Scarlett 設備已就緒

    # 英文
    When 切換語音語言    en
    And 播放文字到聲道    Hello    1    en

    # 中文
    When 切換語音語言    zh-TW
    And 播放文字到聲道    你好    2    zh-TW

    # 日文
    When 切換語音語言    ja
    And 播放文字到聲道    こんにちは    3    ja

    [Teardown]    清理語音資源
```

### 引擎切換

```robotframework
測試 TTS 引擎
    Given Scarlett 設備已就緒

    # Google TTS（線上）
    When 切換語音引擎    gtts
    And 播放文字到聲道    Online TTS    1

    # pyttsx3（離線）
    When 切換語音引擎    pyttsx3
    And 播放文字到聲道    Offline TTS    2

    [Teardown]    清理語音資源
```

---

## ⚠️ 不相容變更

### LocalVoiceVerifyingLibrary 影響

以下關鍵字已從 `LocalVoiceVerifyingLibrary` 移除或需要重新設計：

| 舊關鍵字 | 狀態 | 新替代方案 |
|---------|------|-----------|
| `Speak Text` | ❌ 移除 | `VoiceControlKeywords.播放文字到聲道` |
| `Set TTS Language` | ❌ 移除 | `VoiceControlKeywords.設定 TTS 語言` |
| `Set TTS Speed` | ❌ 移除 | `VoiceControlKeywords.設定 TTS 語速` |
| `Speak And Detect` | ⚠️ 需重新設計 | 分離為 TTS 播放 + 聲音檢測 |

### 受影響的測試檔案

- `tests/physical_interaction/voice_test.robot` - **需要更新**

---

## 📋 待處理事項

### 必須處理

1. **決定 LocalVoiceVerifyingLibrary TTS 功能處理方式**
   - [ ] 選項 A：完全移除 TTS 功能
   - [ ] 選項 B：標記為 deprecated 並轉發到 VoiceControlKeywords

2. **更新 voice_test.robot**
   - [ ] 選項 A：重寫測試，專注聲音檢測
   - [ ] 選項 B：修改為使用新的 VoiceControlKeywords

3. **更新專案文檔**
   - [ ] README.md
   - [ ] CLAUDE.md
   - [ ] keywords_readme.md

### 驗證測試

```bash
# 測試新功能
robot tests/voice_control/voice_tts_integration_test.robot

# 測試受影響的現有功能
robot tests/physical_interaction/voice_test.robot

# 單元測試
python3 libraries/voice_control/TTSManager.py
python3 libraries/voice_control/AudioPlayer.py
python3 libraries/voice_control/VoiceControlKeywords.py
```

---

## 🎉 成果

### 新增功能

✅ **四聲道獨立 TTS 輸出**
- 可以將文字轉語音後播放到 Scarlett 4i4 的任意聲道

✅ **多引擎支援**
- Google TTS（線上，高品質）
- pyttsx3（離線，快速）

✅ **多語言支援**
- 英文、繁體中文、簡體中文、日文、韓文等

✅ **完整的 Robot Framework 整合**
- 中文關鍵字
- Gherkin 風格測試
- 完整的測試案例

✅ **架構優化**
- 職責清晰（輸出 vs 輸入）
- 模組獨立（可單獨使用）
- 易於擴展（新增 TTS 引擎）

---

## 📞 快速開始

### 1. 檢查環境

```bash
# 檢查 Scarlett 設備
wpctl status | grep Scarlett

# 設定 PipeWire 路由
cd libraries/voice_control
./setup_pipewire_routing_v3.sh

# 檢查 Python 依賴
pip list | grep -E "gtts|pyttsx3"
```

### 2. 執行測試

```bash
# 執行完整測試套件
robot tests/voice_control/voice_tts_integration_test.robot

# 執行特定測試
robot --include basic tests/voice_control/voice_tts_integration_test.robot
robot --include multilingual tests/voice_control/voice_tts_integration_test.robot
```

### 3. 在自己的測試中使用

```robotframework
*** Settings ***
Library    libraries/voice_control/VoiceControlKeywords.py
Resource   resources/voice_control_keywords.robot

*** Test Cases ***
你的測試案例
    Given Scarlett 設備已就緒
    When 播放文字到聲道    Your Text    1    en
    [Teardown]    清理語音資源
```

---

## 📚 延伸閱讀

- [詳細遷移指南](voice_control_tts_migration.md)
- [Scarlett 4i4 設定指南](../libraries/voice_control/README.md)
- [VoiceControlKeywords API 文檔](../libraries/voice_control/VoiceControlKeywords.py)
- [測試案例範例](../tests/voice_control/voice_tts_integration_test.robot)

---

**整合完成日期：** 2025-11-06
**版本：** 1.0.0
**狀態：** ✅ 核心功能完成，等待處理舊測試遷移
