# 語音控制相關關鍵字文件

> 索引文件：[keywords_readme.md](../../keywords_readme.md)
> 
> 涵蓋模組：VoiceControlKeywords、AudioKeywords、LocalVoiceVerifyingLibrary、VoiceAssistantDetection
> 
> 最後更新：2026-03-27

## 🚀 重大更新 (2025-12-02) - v1.3.0 音訊路由驗證增強

### ✅ 音訊關鍵字增強
- **Given 音訊輸出聲道 "${channel}" 已準備就緒**
  - 新增自動路由驗證功能
  - 現在會檢查 PipeWire 虛擬 Sink (Scarlett_1-2 / Scarlett_3-4) 是否存在
  - 若路由未設定，將自動報錯並提示執行 `setup_pipewire_routing_v5.sh`

## 🚀 重大更新 (2025-12-02) - v1.4.0 語音命令日誌與交叉測試增強

### ✅ 語音控制關鍵字優化
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"**
  - 新增自動記錄語音命令完成時間 (`${command_end}`)
  - 格式: `YYYYMMDD_HHMMSS.f`
  - 方便後續計算響應時間，無需在測試案例中手動調用 `Get Current Date`

### ✅ 測試案例完善
- **tests/test_voice_commands_rv.robot**
  - 新增 Light 1 - Light 4 的完整交叉聲道測試
  - 涵蓋 Ch1->Ch2, Ch2->Ch3, Ch3->Ch1 的所有組合
  - 移除 `Then 語音應該成功播放到指定聲道` (改由 UART 回應驗證)

## AudioKeywords - 音訊硬體控制關鍵字 (libraries/voice_control/AudioKeywords.py)

用於控制 Focusrite Scarlett 4i4 音訊介面，支援 4 聲道獨立輸出測試。

### 引用方式
```robotframework
Resource    resources/audio_keywords.robot
```

### 常用關鍵字

#### Given Scarlett 音訊介面可用
檢查系統中是否已正確設定 Scarlett 4i4 的虛擬音訊設備 (Scarlett_1-2, Scarlett_3-4)。

#### When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}"
播放指定的音訊檔案到目標聲道 (1-4)。
- `audio_file`: 音訊檔案路徑
- `channel`: 目標聲道 (1, 2, 3, 4)
- `duration`: 播放時間 (秒)，預設 5 秒

#### When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}" 持續 "${duration}" 秒
播放指定的音訊檔案到目標聲道，並指定播放持續時間。
- `audio_file`: 音訊檔案路徑
- `channel`: 目標聲道 (1, 2, 3, 4)
- `duration`: 播放時間 (秒)

#### Then 預設音訊輸出應該是 "${expected_sink}"
驗證當前的系統預設音訊輸出設備。
- `expected_sink`: 預期的設備名稱 (如 "Scarlett_1-2")

#### 列出可用輸出設備
列出系統中所有可用的 PipeWire/PulseAudio 輸出設備並記錄到日誌。無參數。

**使用範例**:
```robotframework
列出可用輸出設備
```

#### 取得當前預設輸出設備
取得系統當前預設的音訊輸出設備名稱，回傳 sink 名稱字串。

**使用範例**:
```robotframework
${sink}=    取得當前預設輸出設備
Log    當前輸出設備: ${sink}
```

#### 取得聲道對應的輸出設備
依聲道編號 (1–4) 回傳對應的 Scarlett 虛擬設備名稱。
- `channel`: 聲道編號 (1, 2, 3, 4)

**使用範例**:
```robotframework
${device}=    取得聲道對應的輸出設備    1
Log    聲道 1 對應設備: ${device}
```

---

## 🎤 語音控制關鍵字 (libraries/voice_control/VoiceControlKeywords.py) ✅ **符合規範**

### 📋 模組資訊

- **庫名稱**: `VoiceControlKeywords`
- **控制設備**: Focusrite Scarlett 4i4 (第四代) USB 音效介面
- **功能**: Google TTS + 多聲道音訊播放控制 + UART 語音回應監控
- **總關鍵字數**: 26個 (6個 Given + 7個 When + 7個 Then + 6個 And)
- **符合規範狀態**: ✅ **完全符合** - 2025-11-12 UART 整合完成
- **建立日期**: 2025-11-11
- **重構日期**: 2025-11-11
- **UART 整合日期**: 2025-11-12 (v1.2.0)

### ✅ 規範符合性分析

| 評估項目 | 狀態 | 說明 |
|---------|------|------|
| **中文關鍵字名稱** | ✅ 符合 | 所有關鍵字使用中文命名 |
| **Gherkin 語法結構** | ✅ 符合 | 完整的 Given-When-Then-And 前綴 |
| **詳細文檔說明** | ✅ 符合 | 每個關鍵字有完整 Documentation |
| **測試案例覆蓋** | ✅ 符合 | 測試案例使用 Gherkin 結構 |
| **向後相容性** | ✅ 符合 | 保留 Legacy 關鍵字確保相容性 |

### 🎯 Gherkin 關鍵字清單 (新版本)

#### Given Keywords (前置條件)
- **Given 語音控制系統已成功初始化** - 確認語音控制系統已成功初始化，包括 TTS 管理器和音訊播放器
- **Given Scarlett 4i4 音效介面已正確連接** - 確認 Focusrite Scarlett 4i4 音效介面正確連接並可用
- **Given TTS 引擎已設定為 "${engine_name}"** - 設定並確認指定的 TTS 引擎已正確配置 (gtts/pyttsx3)
- **Given TTS 語言已設定為 "${language}"** - 設定並確認指定的 TTS 語言已正確配置 (en/zh-TW/ja)
- **Given TTS 語速已設定為 "${speed}"** - 設定並確認指定的 TTS 語速已正確配置 (wpm, 僅 pyttsx3)
- **Given 音訊輸出聲道 "${channel}" 已準備就緒** - 確認指定音訊輸出聲道已準備就緒 (含路由驗證) (1-4)
- **Given UART 日誌監控器已初始化** - 初始化 UART 監控器用於檢測語音回應 (v1.2.0 新增)

#### When Keywords (執行動作)
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"** - 使用者播放文字到指定聲道
- **When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"** - 使用者播放文字到指定聲道使用指定語言
- **When 使用者切換 TTS 引擎到 "${engine_name}"** - 使用者切換 TTS 引擎到指定引擎
- **When 使用者設定 TTS 語速為 "${speed}"** - 使用者設定 TTS 語速為指定值
- **When 使用者查詢當前 TTS 引擎資訊** - 使用者查詢當前 TTS 引擎資訊
- **When 使用者測試指定聲道 "${channel}" 的音訊輸出** - 使用者測試指定聲道的音訊輸出
- **When 使用者啟動 UART 背景監控** - 啟動 UART 背景監控以檢測語音回應 (v1.2.0 新增)
- **When 使用者停止 UART 背景監控** - 停止 UART 背景監控 (v1.2.0 新增)

#### Then Keywords (驗證結果)
- **Then 語音應該成功播放到指定聲道** - 驗證語音播放操作是否成功完成
- **Then TTS 引擎應該成功切換** - 驗證 TTS 引擎切換是否成功
- **Then 音訊輸出應該清晰無雜音** - 驗證音訊輸出品質是否符合標準
- **Then 系統應該回傳正確的 TTS 引擎資訊** - 驗證系統是否回傳正確的 TTS 引擎資訊
- **Then Scarlett 4i4 設備應該處於正常運作狀態** - 驗證 Scarlett 4i4 設備是否處於正常運作狀態
- **Then 應該在 "${timeout}" 秒內收到恰好 "${count}" 個語音回應** - 驗證 UART 日誌中語音回應的數量 (v1.2.0 新增)
- **Then 應該在 "${timeout}" 秒內收到包含以下檔案的語音回應 "${patterns}"** - 驗證 UART 日誌中語音回應的檔案名稱（支援多個檔案，逗號分隔） (v1.2.0 新增)
- **Then 應該在 "${timeout}" 秒內收到語音指令 "${command_keys}" 的回應** - 驗證 UART 日誌中語音回應是否符合指定的語音指令 Key（支援多個 Key，逗號分隔） (v1.4.1 新增)

#### And Keywords (附加驗證)
- **And 語音品質應該符合標準** - 驗證語音品質是否符合預定標準
- **And 沒有音訊延遲或中斷** - 驗證音訊播放過程中沒有延遲或中斷
- **And 暫存檔案應該正確清理** - 驗證暫存檔案是否正確清理
- **And 錯誤日誌應該為空** - 驗證系統錯誤日誌是否為空
- **And 系統資源使用應該在正常範圍內** - 驗證系統資源使用是否在正常範圍內
- **And 清空 UART 事件記錄** - 清空 UART 監控器的事件記錄 (v1.2.0 新增)

### 🔌 UART 語音回應監控功能 (v1.2.0 新增 - 2025-11-12)

**功能概述:**
整合 SerialLogParser 模組，透過 UART 串列埠監控 ASR Pro 語音助手的回應，用於驗證語音命令是否正確觸發語音回應。

**核心功能:**
- 背景監控 UART 串列埠日誌
- 檢測語音播放事件（Playing audio file / Playing voice command reply）
- 驗證語音回應數量（恰好 N 個回應）
- 驗證語音回應檔案名稱（檔案模式匹配）
- 完整日誌記錄與診斷輸出

**UART 監控關鍵字:**

1. **Given UART 日誌監控器已初始化** - 初始化 UART 監控器
   ```robotframework
   Given UART 日誌監控器已初始化
   Given UART 日誌監控器已初始化    /dev/ttyUSB0    115200
   ```

2. **When 使用者啟動 UART 背景監控** - 啟動背景監控
   ```robotframework
   When 使用者啟動 UART 背景監控
   ```

3. **Then 應該在 "${timeout}" 秒內收到恰好 "${count}" 個語音回應** - 驗證回應數量
   ```robotframework
   Then 應該在 "5" 秒內收到恰好 "1" 個語音回應
   Then 應該在 "10" 秒內收到恰好 "3" 個語音回應
   ```

4. **Then 應該在 "${timeout}" 秒內收到包含以下檔案的語音回應 "${patterns}"** - 驗證檔案名稱
   ```robotframework
   # 單一檔案
   Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3"

   # 多個檔案（逗號分隔）
   Then 應該在 "10" 秒內收到包含以下檔案的語音回應 "Light_timer_set.mp3,1.mp3,hours.mp3"
   ```

5. **And 清空 UART 事件記錄** - 清空事件記錄（用於測試間隔離）
   ```robotframework
   And 清空 UART 事件記錄
   ```

6. **When 使用者停止 UART 背景監控** - 停止監控
   ```robotframework
   When 使用者停止 UART 背景監控
   ```

**完整測試範例:**
```robotframework
*** Test Cases ***
Scenario: 測試 Off Grid Mode 語音指令
    [Documentation]    測試離網模式的語音指令與 UART 回應驗證
    [Tags]    voice    uart    asrpro

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Off Grid Mode" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3"
```

**支援的日誌格式:**
- `Playing audio file: xxx.mp3` - 基本音訊播放
- `Playing voice command reply: /path/to/xxx.mp3` - 語音命令回應

**失敗情境:**
- 數量不符：預期 1 個，實際 0 個或 2+ 個 → FAIL
- 檔案不符：預期 "Off_grid_mode.mp3"，實際 "Welcome_back.mp3" → FAIL
- 超時：在指定時間內未收到任何回應 → FAIL

**診斷功能:**
測試失敗時會自動輸出：
- 完整的 UART 日誌（所有行）
- 包含 mp3/audio/playing 關鍵字的行（診斷用）
- 預期與實際的檔案名稱比對

---

### 🎯 現代化完成 - 純 Gherkin 關鍵字架構

> **⚠️ 重要變更 (2025-11-11)**: Legacy 關鍵字已完全移除，voice_control 模組現在採用 100% Gherkin 中文關鍵字架構
> **🆕 最新功能 (2025-11-12 v1.2.0)**: 新增 UART 語音回應監控功能，支援 ASR Pro 語音命令測試

#### ✅ 核心語音播放功能 (現代化版本)
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"** - 文字轉語音並播放到指定聲道 (1-4)
- **When 使用者使用預設喇叭播放文字 "${text}"**
將文字轉換為語音並使用系統預設音訊輸出設備播放（不經過 Scarlett 4i4）。
- **跨平台支援**: 自動偵測作業系統
  - **macOS**: 使用 `afplay` 指令
  - **Linux**: 使用 `ffplay` 或 `aplay` 指令
- `text`: 要播放的文字
- **When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"** - 多語言文字轉語音播放

#### ✅ TTS 系統初始化與設定 (現代化版本)
- **Given 語音控制系統已成功初始化** - 初始化語音控制系統
- **Given TTS 引擎已設定為 "${engine_name}"** - 切換 TTS 引擎 (gtts/pyttsx3)
- **Given TTS 語言已設定為 "${language}"** - 設定語音語言 (zh-TW/en/ja)
- **Given 音訊輸出聲道 "${channel}" 已準備就緒** - 準備指定聲道輸出 (含路由驗證)

#### ✅ 設備連接與狀態驗證 (現代化版本)
- **Given Scarlett 4i4 音效介面已正確連接** - 檢查並確認 Scarlett 4i4 設備狀態
- **When 使用者查詢當前 TTS 引擎資訊** - 查詢當前 TTS 引擎狀態與配置
- **When 使用者測試指定聲道 "${channel}" 的音訊輸出** - 測試特定聲道的音訊輸出功能

#### ✅ 結果驗證與品質檢查 (現代化版本)
- **Then 語音應該成功播放到指定聲道** - 驗證語音播放成功
- **Then TTS 引擎應該成功切換** - 驗證 TTS 引擎切換成功
- **Then 音訊輸出應該清晰無雜音** - 驗證音訊品質
- **Then 系統應該回傳正確的 TTS 引擎資訊** - 驗證系統資訊查詢結果
- **Then Scarlett 4i4 設備應該處於正常運作狀態** - 驗證硬體設備狀態

#### ✅ 系統資源與品質管理 (現代化版本)
- **And 暫存檔案應該正確清理** - 自動清理暫存檔案和系統資源
- **And 語音品質應該符合標準** - 驗證語音品質標準
- **And 沒有音訊延遲或中斷** - 確保音訊播放流暢
- **And 錯誤日誌應該為空** - 確保系統無錯誤
- **And 系統資源使用應該在正常範圍內** - 監控系統資源使用情況

### 🚫 已移除的 Legacy 關鍵字 (不再支援)
> 以下 Legacy 關鍵字已於 2025-11-11 完全移除，請使用上述 Gherkin 關鍵字替代：

- ~~`播放文字到聲道`~~ → 使用 `When 使用者播放文字 "${text}" 到聲道 "${channel}"`
- ~~`設定 TTS 引擎`~~ → 使用 `Given TTS 引擎已設定為 "${engine_name}"`
- ~~`設定 TTS 語言`~~ → 使用 `Given TTS 語言已設定為 "${language}"`
- ~~`取得 TTS 引擎資訊`~~ → 使用 `When 使用者查詢當前 TTS 引擎資訊`
- ~~`檢查 Scarlett 設備`~~ → 使用 `Given Scarlett 4i4 音效介面已正確連接`
- ~~`清理語音控制資源`~~ → 使用 `And 暫存檔案應該正確清理`

### 🎯 使用範例

#### 現代化 Gherkin 測試案例範例
```robotframework
*** Test Cases ***
Scenario: 使用者需要通過 TTS 播放文字語音
    [Documentation]    使用現代化 Gherkin 關鍵字的完整測試場景
    [Tags]    voice    tts    gherkin    scarlett    modern
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "Hello World" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷
    And 暫存檔案應該正確清理
```

#### 多語言與引擎切換範例
```robotframework
*** Test Cases ***
Scenario: 使用者切換 TTS 引擎並播放多語言文字
    [Documentation]    測試 TTS 引擎切換和多語言播放功能
    [Tags]    voice    tts    multilingual    engine_switch
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    When 使用者切換 TTS 引擎到 "pyttsx3"
    Then TTS 引擎應該成功切換
    When 使用者播放文字 "測試語音" 到聲道 "2" 使用語言 "zh-TW"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
```

### � 重構成果總結

**重構前 (2025-11-11 之前):**
- ❌ 不符合 Gherkin 語法結構
- ✅ 關鍵字名稱使用中文
- ✅ 有詳細文檔
- ⚠️ 測試案例結構不一致

**重構後 (2025-11-11 完成):**
- ✅ **100% 符合專案規範** - 完整的 Gherkin 語法支援
- ✅ **完全現代化** - Legacy 關鍵字已完全移除，純 Gherkin 架構
- ✅ **提升可讀性** - Given-When-Then-And 結構更易理解
- ✅ **標準化測試** - 與其他模組保持一致的測試風格
- ✅ **功能完全保持** - 測試 100% 通過，無破壞性變更
- ✅ **現代化完成** - 成為專案中第二個 100% Gherkin 合規的模組

### 🔧 技術實作細節

- **主要類別**: `VoiceControlKeywords`
- **版本**: v1.2.0 (UART 整合版本)
- **關鍵字數量**: 26個 Gherkin 關鍵字 (純中文 + Gherkin 結構)
  - 6個 Given (前置條件)
  - 7個 When (執行動作)
  - 7個 Then (驗證結果)
  - 6個 And (附加驗證)
- **支援設備**:
  - Focusrite Scarlett 4i4 (第四代) - 音訊輸出
  - UART 串列埠 (預設 /dev/ttyUSB0, 115200 baud) - 語音回應監控
- **支援語言**: 英文 (en)、繁體中文 (zh-TW)、日文 (ja)
- **TTS 引擎**: Google TTS (gtts)、離線 TTS (pyttsx3)
- **整合模組**: SerialLogParser (UART 日誌解析)

### 🎯 Legacy 關鍵字移除完成 (2025年)

**✅ 完全移除的 Legacy 關鍵字:**
- `播放文字到聲道` → 改用 `When 使用者播放文字 "${text}" 到聲道 "${channel}"`
- `設定 TTS 引擎` → 改用 `Given TTS 引擎已設定為 "${engine_name}"`
- `取得 TTS 引擎資訊` → 改用 `When 使用者查詢當前 TTS 引擎資訊`
- `取得可用音訊設備` → 功能整合至 Gherkin 關鍵字
- `檢查 Scarlett 設備` → 改用 `Given Scarlett 4i4 音效介面已正確連接`
- `清理語音控制資源` → 改用 `And 暫存檔案應該正確清理`
- 其他 Legacy 關鍵字已轉為內部方法

**✅ 現代化完成狀態:**
- 所有 Robot Framework 測試檔案已更新使用新的 Gherkin 關鍵字
- Legacy @keyword 裝飾器已完全移除
- 舊功能保留為內部方法，供 Gherkin 關鍵字使用
- 測試套件 100% 通過，功能完全保持

### 📚 相關文檔

- **完整重構計劃**: `libraries/voice_control/GHERKIN_REFACTOR_PLAN.md` ✅ 已完成
- **模組 README**: `libraries/voice_control/README.md` ✅ 已更新
- **Python 關鍵字庫**: `libraries/voice_control/VoiceControlKeywords.py` ✅ v1.2.0 (UART 整合)
- **測試案例**:
  - `test_speak_text.robot` ✅ 100% Gherkin 格式 (基礎 TTS 測試)
  - `tests/test_asrpro_commands.robot` ✅ ASR Pro 語音命令測試 (UART 驗證)
- **備份檔案**: `libraries/voice_control/VoiceControlKeywords.py.backup` ✅ 已建立
- **UART 模組**: `libraries/multimodal_detection/SerialLogParser.py` ✅ v1.3.0 (支援雙格式)

**重構時間**: 約 2 小時 (實際完成時間: 2025-11-11)
**Legacy 移除時間**: 約 1.5 小時 (完成時間: 2025-11-11)
**UART 整合時間**: 約 3 小時 (完成時間: 2025-11-12)
**風險評估**: 無風險 (完整的診斷輸出與錯誤處理)
**測試狀態**: ✅ 所有功能測試通過，100% Gherkin 標準
**UART 測試**: ✅ Regex 修復完成，支援雙格式日誌  

---

## 📊 語音系統關鍵字 (test_speak_text.robot) ⚠️ **需要移動**

### Given Keywords (前置條件)
- `語音系統已經成功初始化` - 確保語音系統準備就緒

### When Keywords (執行動作)
- `使用者請求播放文字 "${text}"` - 使用者觸發 TTS 播放

### Then Keywords (驗證結果)
- `語音播放應該成功完成` - 驗證語音播放成功

### And Keywords (附加驗證)
- `測試執行結果應該被成功記錄` - 確認測試結果記錄

### Legacy Keywords (向後相容)
- `Voice System Has Been Initialized Successfully`
- `User Requests To Play Text "${text}"`
- `Speech Should Be Played Successfully`
- `Test Execution Results Should Be Recorded Successfully`

---

## 🔊 本機語音驗證關鍵字（libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py）

> **更新日期**：2026-03-27

此模組提供「PC 播放語音 → 麥克風錄音 → 聲音特徵比對」的完整流程，用於驗證設備對喚醒詞的回應聲音。

### 引用方式
```robotframework
Library    ../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
```

### Python Library 關鍵字

| 關鍵字名稱 | 參數 | 說明 |
|---|---|---|
| `Speak And Detect` | `text`, `target_sound`, `duration=10` | 播放文字語音並同時錄音，比對是否檢測到目標聲音；回傳 True/False |
| `Start Voice Recording` | `duration=10` | 開始後台錄音，持續指定秒數 |
| `Stop Voice Recording` | — | 停止後台錄音並儲存音訊緩衝 |
| `Detect Target Sound` | `target_sound`, `threshold=0.7` | 比對已錄製的音訊是否包含目標聲音；回傳 True/False |
| `Get Detection Result` | — | 取得最後一次偵測結果（字典：sound、detected、confidence、timestamp） |
| `Set Detection Threshold` | `threshold` | 設定聲音比對的信心度閾值（0.0–1.0，預設 0.7） |
| `Load Reference Sound` | `sound_name` | 從 `libraries/local_voice_verifying/reference_sounds/` 載入參考聲音樣本 |
| `Set TTS Language` | `language` | 設定 TTS 語言（如 "zh-TW"、"en"） |
| `Set TTS Speed` | `speed` | 設定 TTS 語速（0.5–2.0，1.0 為正常） |
| `Speak Text` | `text`, `language=None` | 使用 gTTS 播放文字（不錄音） |
| `Cleanup Audio Resources` | — | 釋放所有音訊資源（錄音流、TTS 引擎） |

### 使用範例
```robotframework
*** Test Cases ***
驗證設備回應喚醒詞
    Load Reference Sound    登登
    Set Detection Threshold    0.75
    ${result}=    Speak And Detect    Hey Power Pro    登登    10
    Should Be True    ${result}    msg=未偵測到目標聲音「登登」
    ${detail}=    Get Detection Result
    Log    信心度：${detail}[confidence]
    [Teardown]    Cleanup Audio Resources
```

---

## 🤖 多感官檢測關鍵字（libraries/multimodal_detection/VoiceAssistantDetection.py）

> **更新日期**：2026-03-27

整合語音播放（VoiceControlKeywords）、IP Camera 視覺檢測（IPCamLightDetection）與 UART 日誌監控（SerialLogParser），提供語音助手多感官回應的一站式驗證。

### Python Library 關鍵字

| 關鍵字名稱 | 參數 | 說明 |
|---|---|---|
| `測試語音助理回應` | `wake_word`, `camera_env`, `camera_name`, `uart_port=None`, `uart_baudrate=115200`, `scarlett_channel=1`, `detection_timeout=10`, `require_both=True` | 執行完整的多感官回應測試：播放喚醒詞 → 同時偵測視覺亮度變化與 UART 日誌；回傳結果字典 |

**回傳字典欄位**：
- `overall_success` (bool)：整體測試是否通過
- `vision_detected` (bool)：視覺偵測是否成功
- `audio_detected` (bool)：聽覺（UART）偵測是否成功
- `vision_details` (str)：視覺檢測詳情
- `audio_details` (str)：聽覺檢測詳情
- `failure_reason` (str)：失敗原因摘要

### BDD 資源檔關鍵字（resources/voice_assistant_keywords.robot）

| 關鍵字名稱 | 類型 | 說明 |
|---|---|---|
| `測試語音助手完整回應` | When | 呼叫 `測試語音助理回應`，包裝成 BDD 風格；參數：喚醒詞、環境、攝影機、參考聲音（預設「登登」）、超時（預設 10 秒） |
| `驗證語音助手完整回應成功` | Then | 驗證結果字典中 vision_detected、audio_detected、overall_success 均為 True |
| `驗證視覺和聽覺都有回應` | Then | `驗證語音助手完整回應成功` 的別名關鍵字 |
| `記錄檢測詳細資料` | And | 將結果字典格式化輸出至測試日誌（視覺/聽覺/綜合判定） |
| `驗證檢測結果符合預期` | Then | 驗證結果字典中 vision_detected 和 audio_detected 是否符合預期布林值 |
| `設定檢測參數` | Given | 以 Suite Variable 設定環境、攝影機、參考聲音、超時等參數 |
| `等待語音助手恢復` | And | Sleep 指定秒數（預設 5 秒），等待語音助手回到待命狀態 |
| `清理檢測資源` | （Teardown） | 清理測試使用的資源（日誌記錄） |

**使用範例**:
```robotframework
*** Settings ***
Resource    resources/voice_assistant_keywords.robot

*** Test Cases ***
驗證語音助手對喚醒詞的完整回應
    Given 設定檢測參數    laboratory    level1    登登    10
    When 測試語音助手完整回應    Hey Power Pro    laboratory    level1
    Then 驗證語音助手完整回應成功    ${結果}
    And 記錄檢測詳細資料    ${結果}
    [Teardown]    清理檢測資源
```

---

