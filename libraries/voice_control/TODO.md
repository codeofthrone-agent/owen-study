# Voice Control 模組整合待辦清單

## 📊 整合程度評估：60%

**最後更新：** 2025-11-06

---

## 整合狀態總覽

| 類別 | 完成度 | 說明 |
|------|--------|------|
| **核心功能** | 100% | Python 模組完全可用 |
| **獨立測試** | 100% | 測試套件完整且可執行 |
| **自動化工具** | 100% | 設定與診斷工具齊全 |
| **目錄結構** | 0% | 未整合到專案架構 |
| **編碼規範** | 30% | 未遵循中文關鍵字規範 |
| **配置管理** | 0% | 未使用統一配置系統 |
| **文檔整合** | 40% | 有完整文檔但未整合到專案 |
| **總體評分** | **60%** | 功能完整但整合不足 |

---

## ✅ 已完成項目

### 核心模組
- [x] `ultimate_play.py` - 核心音訊播放器（支援 4 聲道獨立控制）
- [x] `AudioKeywords.py` - Robot Framework 關鍵字庫（8 個自定義關鍵字）
- [x] 自動 PipeWire 設備切換功能
- [x] 命令列工具與 Python 模組雙模式支援

### 測試套件（獨立）
- [x] `audio_test.robot` - 基礎測試套件（7 個測試案例）
- [x] `advanced_audio_test.robot` - 進階測試套件（11 個測試案例 TC01-TC11）
- [x] 測試標籤系統（channel-1~4, all-channels, negative, setup, routing, playback, stress）
- [x] Suite Setup/Teardown 實作

### 自動化工具
- [x] `setup_pipewire_routing_v3.sh` - 自動化設定腳本（v5 版本，完全自動化）
- [x] `fix_scarlett_usb.sh` - USB 問題修復工具
- [x] `diagnose_audio.sh` / `diagnose_audio_routing.sh` - 音訊系統診斷
- [x] `run_tests.sh` - 測試執行腳本
- [x] `pipewire_scarlett_setup.service` - systemd 服務設定

### 文檔
- [x] `README.md` - 完整的模組說明文件
- [x] `ROBOT_FRAMEWORK_README.md` - Robot Framework 整合文件
- [x] 故障排除指南

---

## ❌ 待完成項目

### 優先級 1（高）- 目錄結構調整

#### 1.1 移動測試案例到專案 tests/ 目錄
**目標：** 符合專案架構規範

```bash
# 需要執行的操作
mkdir -p ../../tests/voice_control/
mv audio_test.robot ../../tests/voice_control/
mv advanced_audio_test.robot ../../tests/voice_control/
```

**影響檔案：**
- [ ] `audio_test.robot` → `tests/voice_control/audio_test.robot`
- [ ] `advanced_audio_test.robot` → `tests/voice_control/advanced_audio_test.robot`

**注意事項：**
- 移動後需更新檔案中的相對路徑
- 更新 Library 引用路徑

#### 1.2 建立統一資源檔案
**目標：** 讓其他測試能輕易引用音訊關鍵字

**需建立檔案：**
- [ ] `resources/audio_keywords.robot`

**內容應包含：**
```robotframework
*** Settings ***
Documentation     音訊硬體控制統一關鍵字
Library           ${EXECDIR}/libraries/voice_control/AudioKeywords.py

*** Keywords ***
# 此處定義高階中文關鍵字，封裝 AudioKeywords.py 的功能
```

#### 1.3 建立配置檔案
**目標：** 使用專案統一配置系統

**需建立檔案：**
- [ ] `config/audio_config.py`

**內容應包含：**
```python
"""
音訊系統配置管理
用於 Scarlett 4i4 四聲道獨立控制
"""
from pathlib import Path
from typing import Dict

# Scarlett 設備配置
SCARLETT_DEVICE_NAME = "Scarlett 4i4 4th Gen"
SCARLETT_CARD_PATTERN = "alsa_card.usb-Focusrite_Scarlett_4i4_4th_Gen*"

# 虛擬音訊設備名稱
VIRTUAL_SINKS = {
    "channels_1_2": "Scarlett_1-2",
    "channels_3_4": "Scarlett_3-4"
}

# 聲道映射
CHANNEL_MAPPING = {
    1: {"sink": "Scarlett_1-2", "physical_output": 1},
    2: {"sink": "Scarlett_1-2", "physical_output": 2},
    3: {"sink": "Scarlett_3-4", "physical_output": 3},
    4: {"sink": "Scarlett_3-4", "physical_output": 4}
}

# 測試配置
TEST_CONFIG = {
    "audio_file": Path(__file__).parent.parent / "libraries/voice_control/file_example_WAV_2MG.wav",
    "default_duration": 5,  # 秒
    "stress_test_rounds": 3
}

# PipeWire 配置
PIPEWIRE_CONFIG = {
    "pro_audio_profile": "pro-audio",
    "sample_rate": 48000,
    "channels": 2,
    "format": "S16_LE"
}
```

**後續調整：**
- [ ] 修改 `AudioKeywords.py` 使用此配置
- [ ] 修改 `ultimate_play.py` 使用此配置
- [ ] 修改測試案例使用此配置

---

### 優先級 2（中）- 編碼規範調整

#### 2.1 關鍵字中文化
**目標：** 遵循專案規範（CLAUDE.md 第 2 點）

**需修改 `AudioKeywords.py` 的方法名稱：**

| 現有英文名稱 | 應改為中文名稱 | 說明 |
|-------------|---------------|------|
| `play_audio_to_channel` | `播放音訊到聲道` | 核心播放功能 |
| `get_current_default_sink` | `取得當前預設輸出設備` | 取得 sink |
| `verify_sink_is` | `驗證輸出設備為` | 驗證 sink |
| `list_available_sinks` | `列出可用輸出設備` | 列出 sinks |
| `check_scarlett_sinks_exist` | `檢查Scarlett虛擬設備是否存在` | 檢查設備 |
| `get_sink_for_channel` | `取得聲道對應的輸出設備` | 取得映射 |
| `test_all_channels_sequentially` | `循序測試所有聲道` | 批次測試 |
| `verify_all_channels_passed` | `驗證所有聲道測試通過` | 驗證結果 |

**實作步驟：**
- [ ] 修改 `AudioKeywords.py` 所有方法名稱
- [ ] 保留英文方法作為 alias（向下相容）
- [ ] 更新測試案例使用新的中文關鍵字
- [ ] 更新文檔

#### 2.2 Gherkin 語法重構
**目標：** 遵循專案規範（CLAUDE.md 第 1 點）

**範例：** 將現有測試案例改為 Given-When-Then 結構

**現有寫法（audio_test.robot）：**
```robotframework
測試聲道1播放
    [Documentation]    測試音訊從物理輸出1播放
    [Tags]    channel-1
    ${result}=    Play Audio To Channel    ${AUDIO_FILE}    ${1}    ${DURATION}
    Should Be True    ${result}    msg=聲道1播放失敗
```

**應改為（Gherkin + 中文關鍵字）：**
```robotframework
測試聲道1播放
    [Documentation]    驗證音訊能從 Scarlett 4i4 的物理輸出 1 正確播放
    [Tags]    channel-1
    Given 音訊系統已準備就緒
    And 測試音訊檔案存在於 "${AUDIO_FILE}"
    When 播放音訊到聲道 "1" 持續 "${DURATION}" 秒
    Then 播放應該成功
    And 當前預設輸出設備應該為 "Scarlett_1-2"
```

**需重構的測試檔案：**
- [ ] `audio_test.robot` - 7 個測試案例
- [ ] `advanced_audio_test.robot` - 11 個測試案例

**需在 `resources/audio_keywords.robot` 中新增的高階關鍵字：**
- [ ] `音訊系統已準備就緒` (Given)
- [ ] `測試音訊檔案存在於 "${file_path}"` (And)
- [ ] `播放音訊到聲道 "${channel}" 持續 "${duration}" 秒` (When)
- [ ] `播放應該成功` (Then)
- [ ] `播放應該失敗` (Then - 負面測試)
- [ ] `當前預設輸出設備應該為 "${sink_name}"` (And)

#### 2.3 繁體中文化
**目標：** 統一使用繁體中文

**需修改的檔案：**
- [ ] `AudioKeywords.py` - 所有簡體中文註解改為繁體
- [ ] `ultimate_play.py` - 所有簡體中文註解改為繁體
- [ ] `audio_test.robot` - 所有簡體中文改為繁體
- [ ] `advanced_audio_test.robot` - 所有簡體中文改為繁體
- [ ] `ROBOT_FRAMEWORK_README.md` - 簡體改繁體

**參考對照：**
- 声道 → 聲道
- 音频 → 音訊
- 设备 → 設備
- 测试 → 測試
- 验证 → 驗證

---

### 優先級 3（低）- 文檔整合

#### 3.1 更新 keywords_readme.md
**目標：** 將 AudioKeywords 加入專案關鍵字文檔

**需新增章節：** "AudioKeywords - 音訊硬體控制關鍵字"

**內容應包含：**
- [ ] 模組說明（Scarlett 4i4 四聲道控制）
- [ ] 8 個關鍵字的詳細說明
- [ ] 使用範例
- [ ] 前置需求（PipeWire 設定）
- [ ] 相關設定腳本說明

#### 3.2 更新主 README.md
**目標：** 在專案主文檔中加入音訊模組說明

**需更新的章節：**
- [ ] "主要特色" - 加入專業音訊硬體控制說明
- [ ] "核心命令" - 加入音訊系統相關命令
- [ ] "架構與關鍵目錄" - 說明 voice_control 模組
- [ ] "語音系統架構說明" - 更新此章節內容

**建議新增快速開始章節：**
```markdown
### 專業音訊硬體控制（Scarlett 4i4）

**一鍵設定：**
```bash
cd libraries/voice_control
./setup_pipewire_routing_v3.sh
```

**快速測試：**
```bash
# 測試四個獨立輸出
python3 ultimate_play.py file_example_WAV_2MG.wav 1
python3 ultimate_play.py file_example_WAV_2MG.wav 2
python3 ultimate_play.py file_example_WAV_2MG.wav 3
python3 ultimate_play.py file_example_WAV_2MG.wav 4
```

**執行 Robot Framework 測試：**
```bash
robot tests/voice_control/advanced_audio_test.robot
```
```

#### 3.3 建立專案層級快速開始指南
**目標：** 簡化新開發者上手流程

**需建立檔案：**
- [ ] `docs/audio_hardware_quick_start.md`

**內容應包含：**
- 系統需求（Ubuntu 24.04, PipeWire）
- 硬體需求（Scarlett 4i4 4th Gen）
- 5 分鐘快速設定步驟
- 常見問題快速排除
- 與其他模組整合範例（如 iOS 測試時控制音訊）

---

## 📝 其他改進項目

### 代碼品質改進
- [ ] 為 `AudioKeywords.py` 新增單元測試
- [ ] 為 `ultimate_play.py` 新增單元測試
- [ ] 新增 pytest 配置檔案
- [ ] 新增 CI/CD 測試流程

### 功能擴展
- [ ] 支援錄音功能（目前只支援播放）
- [ ] 支援音量控制
- [ ] 支援多設備（目前只支援單一 Scarlett 設備）
- [ ] 整合到 TestLink（未來 Phase 4）

### 文檔改進
- [ ] 新增 API 文檔（Sphinx）
- [ ] 新增架構圖（UML）
- [ ] 新增影片教學
- [ ] 新增故障排除流程圖

---

## 🔄 整合流程建議

**建議執行順序：**

### 第一階段：配置與結構（1-2 天）
1. 建立 `config/audio_config.py`
2. 修改 Python 模組使用新配置
3. 移動測試案例到 `tests/voice_control/`
4. 建立 `resources/audio_keywords.robot`

### 第二階段：編碼規範（2-3 天）
1. 關鍵字中文化（`AudioKeywords.py`）
2. Gherkin 語法重構測試案例
3. 繁體中文化所有註解與文檔

### 第三階段：文檔整合（1 天）
1. 更新 `keywords_readme.md`
2. 更新主 `README.md`
3. 建立快速開始指南

**預估總工時：** 4-6 天

---

## 🎯 整合完成標準

當以下條件全部達成時，整合度將達到 **100%**：

- [ ] 所有檔案符合專案目錄結構
- [ ] 所有關鍵字使用中文命名
- [ ] 所有測試案例使用 Gherkin 語法
- [ ] 配置統一使用 `config/audio_config.py`
- [ ] 文檔已整合到專案主文檔
- [ ] 可透過 `resources/audio_keywords.robot` 引用
- [ ] 可與其他模組（iOS、SwitchBot）協同測試
- [ ] 所有註解與文檔使用繁體中文

---

## 📚 參考文件

- [CLAUDE.md](../../CLAUDE.md) - 專案編碼規範
- [README.md](README.md) - 模組說明
- [ROBOT_FRAMEWORK_README.md](ROBOT_FRAMEWORK_README.md) - Robot Framework 整合文件
- [spec.md](../../spec.md) - 系統規格書
- [keywords_readme.md](../../keywords_readme.md) - 關鍵字文檔

---

**整合負責人：** 待指派
**預計完成時間：** 待規劃
**當前狀態：** 規劃中
