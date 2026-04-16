# 語音控制模組 - Scarlett 4i4 專業音效控制系統

基於 Google Text-to-Speech (TTS) 與 Focusrite Scarlett 4i4 音效介面的專業語音控制系統，提供高品質語音合成、真正獨立的 4 聲道音訊輸出與精準音量控制功能。

## 模組架構

### 核心檔案結構

```
libraries/voice_control/
├── VoiceControlKeywords.py    # Robot Framework 主關鍵字庫（整合 TTS + 音訊）
├── AudioPlayer.py             # 核心音訊播放器類別
├── TTSManager.py             # 文字轉語音管理器
├── AudioKeywords.py          # 額外的 Robot Framework 關鍵字
├── ultimate_play.py          # 獨立音訊播放腳本
├── setup_pipewire_routing_v5.sh  # 全自動 PipeWire 設定腳本（含自動啟動安裝）
├── requirements.txt          # Python 依賴清單
└── docs/                     # 說明文件目錄
```

### 模組職責

1. **VoiceControlKeywords.py** - 主要 Robot Framework 介面
   - 整合 TTS 與音訊播放功能
   - 提供中文關鍵字支援
   - 管理暫存檔案

2. **AudioPlayer.py** - 核心音訊播放引擎
   - 控制 Scarlett 4i4 聲道輸出
   - PipeWire 設備切換
   - FFmpeg 音訊處理

3. **TTSManager.py** - 文字轉語音引擎
   - 支援 Google TTS (gtts) 與離線 TTS (pyttsx3)
   - 多語言支援（中文、英文、日文等）
   - 音訊格式轉換

4. **ultimate_play.py** - 獨立播放工具
   - 命令列音訊播放工具
   - 直接聲道控制
   - 可獨立使用或被其他模組調用

## 功能特色

- 🎵 **Google TTS 整合** - 高品質多語言文字轉語音
- 🎛️ **Scarlett 4i4 第四代支援** - 專業音效介面 4 聲道完全獨立輸出
- 🔊 **真實多聲道輸出** - 4 個完全獨立的物理音訊輸出
- 🚀 **全自動化設定** - 一鍵完成 PipeWire 路由設定與模式切換
- 🎯 **精準聲道控制** - 每個聲道精確獨立控制
- 🤖 **Robot Framework 整合** - 完整的中文關鍵字支援
- 🔧 **智能錯誤處理** - 自動檢測並修復常見音效問題
- 🌐 **多語言 TTS** - 支援中文、英文、日文等多種語言

## 系統需求

### Python 套件安裝

```bash
# 進入語音控制模組目錄
cd /home/thortron/Tools/robot-multiplatform-automation/libraries/voice_control

# 使用 pipenv 安裝依賴（推薦）
pipenv install

# 或使用 pip 直接安裝
pip install -r requirements.txt

# 主要依賴套件：
# - gtts: Google Text-to-Speech
# - pyttsx3: 離線 TTS 引擎  
# - loguru: 日誌記錄
# - robotframework: Robot Framework 核心（選用）
# - pyyaml, python-dotenv: 配置檔案支援
# - requests: HTTP 請求庫
```

### Ubuntu 系統套件安裝

```bash
# 更新套件列表
sudo apt update

# 安裝 PipeWire 及相關工具
sudo apt install -y pipewire pipewire-pulse pipewire-audio-client-libraries pipewire-bin

# 安裝音訊工具
sudo apt install -y pulseaudio-utils alsa-utils ffmpeg sox

# 安裝 Scarlett 控制工具（選用）
sudo apt install -y alsa-scarlett-gui
```

### 音效硬體需求

- Focusrite Scarlett 4i4 (第四代) USB 音效介面
- 4 組監聽音箱或耳機（連接到輸出 1-4）
- USB 連接埠

## 🚀 快速開始（3 分鐘完成設定）

### 1. 硬體連接

1. 使用 USB 線連接 Scarlett 4i4 到電腦
2. 確認電源指示燈亮起
3. 分別連接 4 組音箱到輸出 1-4

### 2. 全自動化設定

```bash
# 進入語音控制模組目錄
cd /home/thortron/Tools/robot-multiplatform-automation/libraries/voice_control

# 執行全自動設定腳本（首次部署）
./setup_pipewire_routing_v5.sh

# 腳本會自動完成：
# ✅ 檢測 Scarlett 4i4 設備
# ✅ 自動切換到 Pro Audio 模式
# ✅ 建立 Scarlett_1-2 / Scarlett_3-4 虛擬音訊節點
# ✅ 透過 pw-link 接線到 4 個實體輸出
# ✅ 修復 surround-21/surround-50 模式問題
# ✅ 自動播放測試音訊驗證各聲道

# 安裝登入自動啟動（首次部署後執行一次）
./setup_pipewire_routing_v5.sh --install
```

### 3. 驗證設定

```bash
# 測試各聲道輸出（確認每個輸出都有聲音）
python3 ultimate_play.py file_example_WAV_2MG.wav 1  # 測試輸出 1
python3 ultimate_play.py file_example_WAV_2MG.wav 2  # 測試輸出 2  
python3 ultimate_play.py file_example_WAV_2MG.wav 3  # 測試輸出 3
python3 ultimate_play.py file_example_WAV_2MG.wav 4  # 測試輸出 4

# 如果聽到聲音從正確的輸出播放，設定就成功了！
```

### 4. Robot Framework 測試

```bash
# 執行基本音效測試
robot audio_test.robot

# 執行進階多聲道測試  
robot advanced_audio_test.robot

# 執行所有測試
robot tests/

# 或使用自動化測試腳本
./run_tests.sh
```

**就這麼簡單！** v5 版本的全自動化腳本會處理所有複雜的設定工作。

## API 參考與使用範例

### Python API 使用

```python
# 方法一：使用 VoiceControlKeywords（整合 TTS + 音訊播放）
from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords

# 初始化語音控制系統
voice = VoiceControlKeywords()

# 文字轉語音並播放到指定聲道
voice.speak_text_to_channel("你好，這是測試", 1, language="zh-TW", duration=5)
voice.speak_text_to_channel("Hello World", 2, language="en", duration=3)

# 設定 TTS 引擎
voice.set_tts_engine("gtts")  # 使用 Google TTS
voice.set_tts_engine("pyttsx3")  # 使用離線 TTS

# 方法二：使用 AudioPlayer（僅音訊播放）
from libraries.voice_control.AudioPlayer import AudioPlayer

# 初始化音訊播放器
player = AudioPlayer()

# 播放現有音訊檔案到指定聲道
player.play_to_channel("test.wav", 1, duration=5)
player.play_to_channel("music.mp3", 3, duration=10)

# 方法三：使用獨立腳本（命令行工具）
import subprocess

# 直接使用 ultimate_play.py 腳本
subprocess.run(["python3", "ultimate_play.py", "test.wav", "1"])
```

### Robot Framework 使用範例

```robotframework
*** Settings ***
Library    libraries.voice_control.VoiceControlKeywords

*** Test Cases ***
Scarlett 4i4 四聲道獨立測試
    [Documentation]    測試 Scarlett 4i4 四個完全獨立的物理輸出
    
    Given 初始化音效系統
    When 播放現有音訊檔案到聲道    file_example_WAV_2MG.wav    1    5
    And 等待    3 秒
    When 播放現有音訊檔案到聲道    file_example_WAV_2MG.wav    2    5
    And 等待    3 秒
    When 播放現有音訊檔案到聲道    file_example_WAV_2MG.wav    3    5
    And 等待    3 秒
    When 播放現有音訊檔案到聲道    file_example_WAV_2MG.wav    4    5
    Then 驗證四聲道獨立播放成功

中文 TTS 多聲道播放測試
    [Documentation]    測試中文語音合成與多聲道播放
    
    When 播放文字到聲道    你好，這是輸出一    1    zh-TW    5
    And 等待    3 秒
    When 播放文字到聲道    你好，這是輸出二    2    zh-TW    5  
    And 等待    3 秒
    When 播放文字到聲道    你好，這是輸出三    3    zh-TW    5
    And 等待    3 秒
    When 播放文字到聲道    你好，這是輸出四    4    zh-TW    5
    Then 驗證所有播放成功

多語言 TTS 測試
    [Documentation]    測試多種語言的 TTS 功能
    
    When 設定 TTS 引擎    gtts
    And 播放文字到聲道    Hello World    1    en    5
    And 等待    3 秒
    When 播放文字到聲道    你好世界    2    zh-TW    5
    And 等待    3 秒
    When 播放文字到聲道    こんにちは世界    3    ja    5
    Then 驗證多語言播放成功
```

### 主要 API 方法

#### VoiceControlKeywords 類別（整合 TTS + 音訊播放）

**核心關鍵字：**
- `播放文字到聲道(text, channel, language="zh-TW", duration=5)` - 文字轉語音並播放到指定聲道
- `播放現有音訊檔案到聲道(audio_file, channel, duration=5)` - 播放現有音訊檔案到指定聲道
- `設定 TTS 引擎(engine_name)` - 切換 TTS 引擎（gtts/pyttsx3）
- `清理暫存音訊檔案()` - 清理 TTS 產生的暫存檔案

**Python 方法：**
- `speak_text_to_channel(text, channel, language="zh-TW", duration=5)` - 核心語音播放方法
- `set_tts_engine(engine_name)` - 設定 TTS 引擎
- `cleanup_temp_files()` - 清理暫存檔案

#### AudioPlayer 類別（純音訊播放）

- `play_to_channel(audio_file, target_channel, duration=5)` - 播放音訊到指定聲道
- `_check_scarlett_device()` - 檢查 Scarlett 4i4 設備狀態

#### TTSManager 類別（文字轉語音）

- `text_to_file(text, language="zh-TW", format="mp3")` - 將文字轉換為音訊檔案
- `set_engine(engine_name)` - 設定 TTS 引擎
- `get_available_engines()` - 取得可用的 TTS 引擎清單

#### ultimate_play.py 腳本（命令行工具）

```bash
# 使用方法
python3 ultimate_play.py <音訊檔案> <聲道編號(1-4)> [播放時長]

# 範例
python3 ultimate_play.py test.wav 1 5    # 播放到聲道 1，持續 5 秒
python3 ultimate_play.py music.mp3 3     # 播放到聲道 3，預設 5 秒
```

## 硬體設定指南

### Scarlett 4i4 實體輸出對應

```
輸出 1 ←→ Scarlett 4i4 後面板 "LINE OUTPUT 1" (左聲道)
輸出 2 ←→ Scarlett 4i4 後面板 "LINE OUTPUT 2" (右聲道)  
輸出 3 ←→ Scarlett 4i4 後面板 "LINE OUTPUT 3" (左聲道)
輸出 4 ←→ Scarlett 4i4 後面板 "LINE OUTPUT 4" (右聲道)
```

**重要：** 每個輸出都是完全獨立的物理輸出，不是立體聲配對。

## ✨ v6 版本重大更新（2025-11-11）

**完整模組化架構與 Robot Framework 深度整合！**

- ✅ **模組化重構** - 拆分為 VoiceControlKeywords、AudioPlayer、TTSManager 獨立模組
- ✅ **Google TTS 整合** - 支援高品質多語言文字轉語音
- ✅ **Robot Framework 深度整合** - 完整的中文關鍵字庫和測試支援
- ✅ **智能音訊管理** - 自動暫存檔案清理與資源管理
- ✅ **多引擎支援** - Google TTS (線上) + pyttsx3 (離線) 雙引擎
- ✅ **模組獨立性** - 每個模組可獨立使用或組合使用
- ✅ **增強錯誤處理** - 詳細的錯誤訊息和故障排除指引

**重要變更：**
- 新增 `播放文字到聲道` 關鍵字 - 一步完成 TTS + 音訊播放
- 新增 `設定 TTS 引擎` 關鍵字 - 動態切換線上/離線引擎
- 優化模組匯入結構，支援相對和絕對匯入
- 完整的 Python 和 Robot Framework API 文件

---

## 🚀 3 分鐘快速開始

```bash
# 1. 進入目錄
cd /path/to/voice_control

# 2. 執行自動設定腳本
./setup_pipewire_routing_v5.sh

# 3. 測試播放（確認每個輸出都有聲音）
python3 ultimate_play.py file_example_WAV_2MG.wav 1  # 測試輸出 1
python3 ultimate_play.py file_example_WAV_2MG.wav 2  # 測試輸出 2
python3 ultimate_play.py file_example_WAV_2MG.wav 3  # 測試輸出 3
python3 ultimate_play.py file_example_WAV_2MG.wav 4  # 測試輸出 4
```

**就這麼簡單！** 腳本會自動完成所有設定，包括：
- 檢測並切換到 Pro Audio 模式
- 創建虛擬音訊設備
- 連接到 4 個獨立輸出

如果需要開機自動執行，請參閱下方的「設定開機自動執行」章節。

---

## 快速部署到新系統

如果你要在新機器上部署此系統，請按照以下步驟進行：

```bash
# 1. 確保系統滿足所有依賴要求（參見「系統需求與安裝」章節）
# 2. 複製整個 voice_control 目錄到新系統
# 3. 進入目錄並安裝 Python 依賴
cd voice_control
pip install -r requirements.txt

# 4. 設定執行權限
chmod +x setup_pipewire_routing_v5.sh
chmod +x fix_scarlett_usb.sh
chmod +x run_tests.sh

# 5. 執行自動設定
./setup_pipewire_routing_v5.sh

# 6. 測試功能
python3 ultimate_play.py file_example_WAV_2MG.wav 1
```

---

## 📋 完整部署清單（新設備/新系統）

**適用情境：**
- ✅ 部署到新的 Scarlett 4i4 設備（相同型號，不同序列號）
- ✅ 在新系統上安裝
- ✅ 替換舊設備

**好消息：腳本使用通配符匹配，自動支援所有 Scarlett 4i4 4th Gen 設備，無需修改程式碼！**

### 檢查清單

#### ☑️ 1. 硬體連接
```bash
# USB 線已連接
# 設備已開機
# 驗證系統可見設備
lsusb | grep -i focusrite
# 應該看到：Bus XXX Device XXX: ID 1235:821a Focusrite-Novation Scarlett 4i4 4th Gen
```

#### ☑️ 2. 系統依賴檢查
```bash
# 檢查 PipeWire
pipewire --version

# 檢查 pactl（PulseAudio 工具）
pactl --version

# 檢查 Python 3
python3 --version

# 如缺少依賴，請參閱下方「系統需求與安裝」章節
```

#### ☑️ 3. 用戶權限設定
```bash
# 檢查是否在 audio 群組
groups | grep audio

# 如未加入，執行以下命令
sudo usermod -a -G audio $USER

# 登出重新登入，或執行
newgrp audio
```

#### ☑️ 4. 執行自動設定腳本
```bash
cd /path/to/voice_control

# 賦予執行權限（首次需要）
chmod +x setup_pipewire_routing_v5.sh

# 執行完整設定（包含 Pro Audio 模式切換 + 路由建立 + 音訊測試）
./setup_pipewire_routing_v5.sh

# 確認看到以下訊息
# ✅ 已成功切換到 Pro Audio 模式
# ✅ Scarlett_1-2 -> playback_AUX0
# ✅ Scarlett_1-2 -> playback_AUX1
# ✅ Scarlett_3-4 -> playback_AUX2
# ✅ Scarlett_3-4 -> playback_AUX3
# ✅ 路由設定完成！
```

#### ☑️ 5. 測試播放
```bash
# 測試 4 個獨立輸出（需先完成步驟 4）
uv run python ultimate_play.py file_example_WAV_2MG.wav 1  # 測試輸出 1
uv run python ultimate_play.py file_example_WAV_2MG.wav 2  # 測試輸出 2
uv run python ultimate_play.py file_example_WAV_2MG.wav 3  # 測試輸出 3
uv run python ultimate_play.py file_example_WAV_2MG.wav 4  # 測試輸出 4

# 確認每個輸出都能聽到聲音
# 注意：請確認硬體音量旋鈕不在最小位置
```

#### ☑️ 6. 安裝登入自動啟動（必做）
```bash
# 一鍵安裝 systemd user service
./setup_pipewire_routing_v5.sh --install

# 立即測試服務
systemctl --user start scarlett-routing.service

# 檢查狀態
systemctl --user status scarlett-routing.service
# 應該看到：Active: active (exited)

# 查看日誌（排查問題）
journalctl --user -u scarlett-routing.service
```

> **為什麼必須安裝自動啟動？** 詳見故障排除「ultimate_play.py 播放沒有聲音」章節。

### 常見問題快速排查

**Q: 新設備序列號不同，需要修改程式碼嗎？**
A: ❌ **不需要！** 腳本使用通配符 `.*` 自動匹配所有 Scarlett 4i4 4th Gen 設備。

**Q: 找不到設備怎麼辦？**
A: 執行診斷腳本：
```bash
./fix_scarlett_usb.sh
```

**Q: 播放沒有聲音？**
A: 最常見的原因是 `pw-link` 接線消失。依序檢查：
1. `pw-link -l | grep -i Scarlett` — 確認 4 條接線存在，沒有接線表示需要重新執行 setup 或 `--routing-only`
2. Scarlett 前面板的音量旋鈕是否調整到中間位置
3. 喇叭/耳機是否正確連接到對應的物理輸出
4. 安裝自動啟動 `./setup_pipewire_routing_v5.sh --install` 避免重複發生

**Q: 為什麼 setup 腳本有聲音，但單獨執行 ultimate_play.py 沒有聲音？**
A: 詳見故障排除「ultimate_play.py 播放沒有聲音」章節。

**Q: 需要同時使用兩台 Scarlett 設備？**
A: 當前腳本設計為單設備使用。如需多設備支援，請聯繫開發者。

---

## 系統需求與安裝

### 必要軟體安裝

在開始設定之前，請確保安裝以下所有必要的程式：

```bash
# 更新套件列表
sudo apt update

# 安裝 PipeWire 及相關工具
sudo apt install -y pipewire pipewire-pulse pipewire-audio-client-libraries

# 安裝 PulseAudio 工具 (提供 pactl 命令)
sudo apt install -y pulseaudio-utils

# 安裝 PipeWire 連接工具 (提供 pw-link 命令)
sudo apt install -y pipewire-bin

# 安裝 Python 3 及 pip (如果尚未安裝)
sudo apt install -y python3 python3-pip python3-venv

# 安裝音訊播放工具
sudo apt install -y ffmpeg sox

# 安裝 Scarlett 控制工具
sudo apt install -y alsa-scarlett-gui

# 安裝 ALSA 工具 (用於儲存音效卡設定)
sudo apt install -y alsa-utils
```

### Python 依賴套件

```bash
# 建立虛擬環境 (建議)
python3 -m venv venv
source venv/bin/activate

# 安裝 Python 依賴
pip install -r requirements.txt
```

## 最終成果

透過本方案設定後，您將可以：
1.  讓物理輸出 1, 2, 3, 4 都能作為獨立的單聲道音訊出口。
2.  使用一個簡單的 `ultimate_play.py` Python 腳本，將聲音精確地播放到任意一個指定的物理輸出。

---

## 快速設定（v5 版本 - 全自動）

### 步驟 1: 執行自動設定腳本

**v5 版本的腳本已完全自動化**，會自動完成以下操作：
- ✅ 自動檢測當前 PipeWire Profile
- ✅ 自動切換到 Pro Audio 模式（Direct 模式）
- ✅ 自動創建虛擬音訊設備（Scarlett_1-2 / Scarlett_3-4）
- ✅ 透過 pw-link 接線到 Scarlett 4i4 的 4 個獨立輸出

```bash
cd libraries/voice_control
./setup_pipewire_routing_v5.sh
```

**執行結果範例：**
```
===========================================
Scarlett 4i4 PipeWire 路由設定 (v5)
===========================================

(i) 檢查 Scarlett 設備的 PipeWire Profile...
    找到音訊卡: alsa_card.usb-Focusrite_Scarlett_4i4_4th_Gen...
    當前 Profile: output:analog-surround-21+input:analog-surround-21
    ⚠️  非 Pro Audio 模式，正在自動切換...
    ✅ 已成功切換到 Pro Audio 模式

(i) 正在創建虛擬輸出設備...
    ✅ 成功創建 'Scarlett_1-2'
    ✅ 成功創建 'Scarlett_3-4'

(i) 正在連接到 AUX 端口...
    ✅ 輸出 1 已連接
    ✅ 輸出 2 已連接
    ✅ 輸出 3 已連接
    ✅ 輸出 4 已連接

===========================================
✅ 設定完成 - Pro Audio 模式
===========================================
```

### 步驟 2: 測試播放

```bash
# 測試 4 個獨立輸出
uv run python ultimate_play.py file_example_WAV_2MG.wav 1  # 輸出 1
uv run python ultimate_play.py file_example_WAV_2MG.wav 2  # 輸出 2
uv run python ultimate_play.py file_example_WAV_2MG.wav 3  # 輸出 3
uv run python ultimate_play.py file_example_WAV_2MG.wav 4  # 輸出 4
```

### 舊版設定方式（僅供參考）

**注意：v5 版本已不需要手動設定，以下步驟僅供參考或故障排除使用。**

<details>
<summary>展開查看舊版手動設定步驟</summary>

#### 舊步驟 1: 手動設定硬體為「直接輸出」模式

使用 `alsa-scarlett-gui` 手動更改音效卡模式：

1.  安裝 `alsa-scarlett-gui`
2.  打開工具，找到 **Routing** (路由) 選項
3.  將其設定為 **`Direct`** 模式並儲存

#### 舊步驟 2: 手動創建虛擬設備

舊版腳本需要手動設定或每次開機執行。

</details>

### 步驟 3: 安裝登入自動啟動（必做）

`pw-link` 的接線**不是永久性的**，PipeWire 重啟或重新登入後會消失，導致 `ultimate_play.py` 播放沒有聲音。
必須安裝 systemd user service，讓每次登入後自動重建路由。

```bash
# 一鍵安裝（自動建立並啟用 systemd user service）
./setup_pipewire_routing_v5.sh --install

# 立即啟動服務（無需重開機）
systemctl --user start scarlett-routing.service

# 驗證服務狀態（應顯示 active (exited)）
systemctl --user status scarlett-routing.service

# 查看詳細日誌
journalctl --user -u scarlett-routing.service
```

**驗證路由是否正常：**
```bash
# 確認虛擬設備存在
pactl list sinks short | grep Scarlett
# 應該看到：Scarlett_1-2 和 Scarlett_3-4

# 確認接線完整
pw-link -l | grep -i "Scarlett\|Focusrite"
# 應該看到 4 條接線：monitor_FL/FR -> playback_AUX0/1/2/3

# 測試播放
uv run python ultimate_play.py file_example_WAV_2MG.wav 1
uv run python ultimate_play.py file_example_WAV_2MG.wav 4
```

**移除自動啟動：**
```bash
./setup_pipewire_routing_v5.sh --uninstall
```

#### 部署到其他機器的檢查清單

在將此設定部署到新機器前，請確認以下條件：

**前置需求檢查：**
1. ✅ 用戶已加入 `audio` 群組
   ```bash
   sudo usermod -a -G audio $USER
   # 需要登出重新登入或執行 newgrp audio
   ```

2. ✅ 系統可以識別 Scarlett 設備
   ```bash
   aplay -l | grep Scarlett
   # 應該看到 "Scarlett 4i4 4th Gen"
   ```

3. ✅ 腳本具有執行權限
   ```bash
   chmod +x setup_pipewire_routing_v5.sh
   ```

4. ✅ 服務檔案路徑正確
   - 確認 `ExecStart` 路徑與實際安裝位置一致
   - 使用 `%h` 變數會自動替換為用戶家目錄

5. ✅ Python 環境就緒
   ```bash
   python3 --version  # 確認 Python 3 已安裝
   which python3 ultimate_play.py  # 確認腳本存在
   ```

**部署步驟摘要：**
```bash
# 1. 確認前置需求
groups | grep audio || sudo usermod -a -G audio $USER

# 2. 登出重新登入或執行
newgrp audio

# 3. 首次完整設定（建立 Pro Audio 模式 + 路由）
chmod +x setup_pipewire_routing_v5.sh
./setup_pipewire_routing_v5.sh

# 4. 安裝登入自動啟動
./setup_pipewire_routing_v5.sh --install

# 5. 重新開機測試
sudo reboot

# 6. 開機後驗證
systemctl --user status scarlett-routing.service
pactl list sinks short | grep Scarlett
uv run python ultimate_play.py file_example_WAV_2MG.wav 1
```

---

## 音量控制

### 調整虛擬 Sink 音量

```bash
# 設定 Scarlett_1-2 音量（輸出 1、2）
pactl set-sink-volume Scarlett_1-2 80%

# 設定 Scarlett_3-4 音量（輸出 3、4）
pactl set-sink-volume Scarlett_3-4 50%

# 查看目前音量
pactl get-sink-volume Scarlett_1-2
pactl get-sink-volume Scarlett_3-4
```

### 調整實體輸出音量

```bash
# 實體輸出音量（同時影響所有接到此設備的輸出）
CARD="alsa_output.usb-Focusrite_Scarlett_4i4_4th_Gen_S4UQEAE5487CB5-00.pro-output-0"
pactl set-sink-volume "$CARD" 70%
```

### 在 ultimate_play.py 使用 ffmpeg volume filter

若需要在播放時動態控制音量，可在 `pan_filter` 前加上 `volume=` filter：

```python
# 原本（100% 音量）
self.pan_filter = "pan=stereo|c0=1*c0|c1=0*c0"

# 加上 50% 音量
self.pan_filter = "volume=0.5,pan=stereo|c0=1*c0|c1=0*c0"
```

---

## 故障排除

### 常見問題 0：ultimate_play.py 播放沒有聲音

#### 症狀
- `setup_pipewire_routing_v5.sh` 執行後有聲音
- 重新登入或 PipeWire 重啟後，單獨執行 `uv run python ultimate_play.py` 沒有聲音
- `ultimate_play.py` 顯示「✅ 播放完毕」但聽不到任何聲音

#### 原因

```
pactl list sinks short | grep Scarlett
→ Scarlett_1-2  IDLE   ← 存在但沒有收到音訊（或無出口）
→ Scarlett_3-4  IDLE
```

`pw-link` 接線**不是永久性的**。每次 PipeWire 重啟後：
- 虛擬 sink（Scarlett_1-2 / Scarlett_3-4）有時保留
- 但 pw-link 接線**消失**，音訊送進虛擬 sink 後沒有出路

`ultimate_play.py` 用 `pacat --device=Scarlett_1-2` 播放，若接線不存在則無聲，且 exit code 仍為 0（pacat 寫入成功但音訊去向已斷）。

#### 診斷

```bash
# 確認接線是否存在
pw-link -l | grep -i "Scarlett\|Focusrite"
# 應有 4 條接線，如果為空則確認是此問題
```

#### 解決方案

```bash
# 方法 1：重新執行 setup（臨時修復）
./setup_pipewire_routing_v5.sh

# 方法 2：只重建路由（已有 Pro Audio 設定時使用）
./setup_pipewire_routing_v5.sh --routing-only

# 方法 3：安裝自動啟動（永久修復，每次登入自動重建）
./setup_pipewire_routing_v5.sh --install
```

---

### 常見問題 1：音訊模式錯誤（已自動修復）

**v5 版本已自動解決此問題！**

#### 症狀
- 播放到輸出 3 沒有聲音或只有低頻聲音
- 輸出 4 完全無法使用
- 執行舊版腳本時顯示「2.1 模式」或「5.0 模式」警告

#### 原因
PipeWire 預設使用環繞音效 Profile（surround-21/surround-50），而非 Pro Audio 模式。

#### 解決方案
✅ **v5 版本腳本會自動修復此問題**

只需執行：
```bash
./setup_pipewire_routing_v5.sh
```

腳本會自動：
1. 檢測當前 Profile（如 surround-21）
2. 自動切換到 Pro Audio 模式
3. 創建正確的虛擬設備連接

**手動檢查模式（選用）：**
```bash
# 檢查當前 Profile
pactl list cards | grep "Active Profile"

# 手動切換到 Pro Audio（通常不需要，腳本會自動處理）
pactl set-card-profile alsa_card.usb-Focusrite_Scarlett_4i4_4th_Gen_* pro-audio
```

---

### 常見問題 2：Scarlett 設備無法識別

#### 症狀
- `lsusb` 可以看到 Focusrite Scarlett 設備
- `aplay -l` 看不到 Scarlett 設備
- PipeWire 無法識別 Scarlett
- 執行 `setup_pipewire_routing_v5.sh` 時出現「找不到 Scarlett 設備」錯誤

#### 原因
USB 音訊驅動（`snd_usb_audio`）未正確載入或需要重新初始化。這通常發生在：
- 系統剛啟動後
- USB 設備重新插拔後
- 驅動模組載入順序問題

#### 快速修復
使用自動修復腳本：

```bash
./fix_scarlett_usb.sh
```

此腳本會自動：
1. 檢查 USB 設備連接狀態
2. 檢查 ALSA 音訊系統識別狀態
3. 重新載入 USB 音訊驅動（如需要）
4. 重啟 PipeWire 服務
5. 執行路由設定腳本

#### 手動修復步驟

如果需要手動修復，請依序執行：

```bash
# 1. 確認 USB 設備已連接
lsusb | grep -i focusrite
# 應該看到：Bus XXX Device XXX: ID 1235:821a Focusrite-Novation Scarlett 4i4 4th Gen

# 2. 重新載入 USB 音訊驅動
sudo modprobe -r snd_usb_audio
sudo modprobe snd_usb_audio
sleep 2

# 3. 驗證 ALSA 識別
aplay -l | grep -i scarlett
# 應該看到：card X: Gen [Scarlett 4i4 4th Gen], device 0: USB Audio [USB Audio]

# 4. 重啟 PipeWire 服務
systemctl --user restart pipewire pipewire-pulse wireplumber
sleep 3

# 5. 驗證 PipeWire 識別
wpctl status | grep -i scarlett
# 應該看到 Scarlett 4i4 4th Gen 設備

### 常見問題 3：端口名稱變異 (AUX vs FL/FR)

#### 症狀
- 使用 USB 延長線或 Hub 連接時，腳本顯示連接到 `AUX` 端口。
- 直接連接電腦時，腳本顯示連接到 `FL/FR` 端口。
- 設備名稱有時會帶有 `.2` 等後綴（例如 `...pro-output-0.2`）。

#### 原因
這是 PipeWire/ALSA 對 USB 音訊設備的正常識別行為：
1. **標準模式 (AUX)**：當驅動程式無法完全讀取設備拓撲（常見於不穩定的 USB 連接或 Hub）時，會使用通用的 `AUX0-3` 命名。
2. **完整模式 (FL/FR)**：當連接穩定且驅動完全載入時，會使用具體的 `FL/FR/RL/RR` 命名。
3. **設備後綴 (.2)**：當設備被快速拔插（Hotplug），舊的設備節點尚未釋放時，新插入的設備會被分配一個帶有數字後綴的新名稱。

#### 解決方案
✅ **v5 版本腳本已內建智慧偵測機制**

您**不需要**做任何調整，腳本會自動：
1. **動態偵測設備節點**：無論是 `pro-output-0` 還是 `pro-output-0.2`，腳本都能精確抓取。
2. **自動適配端口名稱**：腳本會先檢查當前系統是使用 `FL/FR` 還是 `AUX` 命名，然後自動切換連接策略。

這確保了無論您如何連接設備（直接連接或透過延長線），系統都能穩定運作。

# 6. 重新執行路由設定
./setup_pipewire_routing_v5.sh
```

#### 預防措施

為了避免此問題重複發生，可以考慮：

1. **設定 udev 規則**（自動載入驅動）
   ```bash
   # 創建 udev 規則檔案
   sudo nano /etc/udev/rules.d/99-scarlett.rules

   # 添加以下內容：
   # Focusrite Scarlett 4i4 4th Gen
   SUBSYSTEM=="usb", ATTR{idVendor}=="1235", ATTR{idProduct}=="821a", RUN+="/sbin/modprobe snd_usb_audio"

   # 重新載入 udev 規則
   sudo udevadm control --reload-rules
   ```

2. **設定開機後自動檢查**
   將 `fix_scarlett_usb.sh` 加入 systemd 服務的 `ExecStartPre` 指令中

3. **USB 電源管理**
   禁用 Scarlett 的 USB 自動掛起：
   ```bash
   # 查找設備路徑
   lsusb -t | grep -i scarlett

   # 禁用自動掛起（範例）
   echo 'on' | sudo tee /sys/bus/usb/devices/3-6/power/control
   ```

---

### 步驟 3: 使用終極 Python 腳本播放聲音

在執行完設定腳本後，您就可以使用 `ultimate_play.py` 來向任意聲道播放聲音。這個 Python 腳本會自動切換系統預設的輸出設備，並將聲音播放到正確的聲道。

**`ultimate_play.py`**
```python
#!/usr/bin/env python3
"""
音訊播放腳本 - Python版本
支持自動切换PipeWire輸出設備並播放到指定聲道
可與 Robot Framework 集成使用
"""

import sys
import subprocess
import os
from typing import Tuple

# ... (腳本內容詳見 ultimate_play.py)
```

**用法範例:**
```bash
# 播放到物理輸出 3
python3 ultimate_play.py your_audio_file.wav 3

# 播放到物理輸出 1
python3 ultimate_play.py your_audio_file.wav 1
```

---

## 版本歷史

### setup_pipewire_routing_v5.sh 指令參考

| 指令 | 說明 |
|------|------|
| `./setup_pipewire_routing_v5.sh` | 完整設定（Pro Audio + 路由 + 音訊測試） |
| `./setup_pipewire_routing_v5.sh --routing-only` | 僅重建虛擬 sink 與 pw-link 接線 |
| `./setup_pipewire_routing_v5.sh --install` | 安裝 systemd user service，每次登入自動執行 |
| `./setup_pipewire_routing_v5.sh --uninstall` | 移除自動啟動服務 |
| `./setup_pipewire_routing_v5.sh --test` | 僅執行音訊測試 |
| `./setup_pipewire_routing_v5.sh --cleanup` | 清理所有虛擬裝置 |

### 路由架構說明

```
ultimate_play.py (channel 1) → pacat → Scarlett_1-2 → pw-link → playback_AUX0 → 實體 Output 1
ultimate_play.py (channel 2) → pacat → Scarlett_1-2 → pw-link → playback_AUX1 → 實體 Output 2
ultimate_play.py (channel 3) → pacat → Scarlett_3-4 → pw-link → playback_AUX2 → 實體 Output 3
ultimate_play.py (channel 4) → pacat → Scarlett_3-4 → pw-link → playback_AUX3 → 實體 Output 4
```

**注意：** `pw-link` 接線不是永久性的，必須安裝 `--install` 自動啟動。

---

### v6.0 (2025-11-11)
**重大模組重構與 Robot Framework 深度整合**

新增功能：
- ✅ **完整的模組化架構** - 拆分為 VoiceControlKeywords、AudioPlayer、TTSManager 三大核心模組
- ✅ **Google TTS 整合** - 支援多語言文字轉語音（中文、英文、日文等）
- ✅ **離線 TTS 支援** - pyttsx3 引擎作為備用選項
- ✅ **Robot Framework 深度整合** - 完整的中文關鍵字庫
- ✅ **智能音訊管理** - 自動暫存檔案管理與清理
- ✅ **多語言支援** - 支援 zh-TW、en、ja 等多種語言
- ✅ **模組獨立使用** - 每個模組都可獨立調用

架構改進：
- 📁 **VoiceControlKeywords.py** - 主要 Robot Framework 介面
- 📁 **AudioPlayer.py** - 核心音訊播放引擎  
- 📁 **TTSManager.py** - 文字轉語音管理器
- 📁 **AudioKeywords.py** - 額外測試關鍵字
- 📁 **ultimate_play.py** - 獨立播放工具

API 增強：
- 🔧 **播放文字到聲道** - 一步完成 TTS + 播放
- 🔧 **設定 TTS 引擎** - 動態切換線上/離線引擎
- 🔧 **清理暫存音訊檔案** - 自動資源管理

### v5.0 (2025-10-20)
**重大更新：完全自動化設定流程**

新功能：
- ✅ 自動檢測 PipeWire Profile（surround-21/surround-50/pro-audio）
- ✅ 自動切換到 Pro Audio 模式
- ✅ 移除手動使用 `alsa-scarlett-gui` 的需求
- ✅ 智能錯誤處理和詳細錯誤訊息
- ✅ 簡化的設定流程（一鍵完成）

改進：
- 📝 更新文檔，突出自動化功能
- 🔧 優化腳本執行流程
- 📊 改進連接狀態驗證

修復：
- 🐛 修復在 surround-21 模式下輸出 3 只有低頻信號的問題
- 🐛 修復在 surround-21 模式下輸出 4 無法使用的問題

### v4.0
- 支援多種音訊模式自動偵測（pro-output/surround-50/surround-21/stereo）
- 根據不同模式使用對應的端口連接

### v3.0
- 最簡化的 pactl 命令實現
- 移除所有附加屬性，只保留核心功能

### v2.0
- 初始 PipeWire 路由設定實現

### v1.0
- 基礎音訊播放功能

---