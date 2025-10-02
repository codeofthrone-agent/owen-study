# Scarlett 4i4 (4th Gen) Linux 獨立四通道輸出解決方案

本文件提供了在 Linux (Ubuntu 24) 環境下，為 Focusrite Scarlett 4i4 (第四代) 設定並使用真正獨立的 4 個物理輸出的最終解決方案。

## 快速開始（新系統部署）

如果你要在新機器上部署此系統，只需要：

```bash
# 1. 複製整個目錄到新系統
# 2. 進入目錄並執行快速部署腳本
cd Audio_test
./deploy_to_new_system.sh
```

部署腳本會自動：
- 檢查必要檔案
- 設定執行權限
- 檢查並提示安裝系統依賴
- 建立 Python 虛擬環境
- 安裝 Python 套件
- 檢測 Scarlett 設備狀態

**詳細的安裝步驟請參閱 [INSTALL.md](INSTALL.md)**

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

## 設定三部曲

### 步驟 1: 設定硬體為「直接輸出」模式 (只需做一次)

這是最關鍵的前提。您需要使用 `alsa-scarlett-gui` 這個圖形化工具來更改音效卡的內部模式。

1.  安裝 `alsa-scarlett-gui`。
2.  打開工具，找到 **Routing** (路由) 選項。
3.  將其設定為 **`Direct`** 模式並儲存。

### 步驟 2: 創建並連結虛擬音訊設備 (每次開機執行)

`Direct` 模式只是前提，我們還需要透過 PipeWire 的進階功能來手動「接線」。`setup_pipewire_routing_v3.sh` 腳本會為您完成此操作。此腳本需要在每次開機後執行一次 (建議設定為開機自動啟動)。

**`setup_pipewire_routing_v3.sh`**
```bash
#!/bin/bash
# v3 版本：使用最簡化的 pactl 命令，移除所有附加屬性，只保留核心功能。

# ... (腳本內容詳見 setup_pipewire_routing_v3.sh)
```

#### 設定開機自動執行

使用 systemd 服務讓路由設定在每次開機後自動執行：

```bash
# 1. 複製服務檔案到用戶 systemd 目錄
mkdir -p ~/.config/systemd/user
cp pipewire_scarlett_setup.service ~/.config/systemd/user/

# 2. 重新載入 systemd 配置
systemctl --user daemon-reload

# 3. 啟用服務（開機自動執行）
systemctl --user enable pipewire_scarlett_setup.service

# 4. 立即啟動服務（無需重開機）
systemctl --user start pipewire_scarlett_setup.service

# 檢查服務狀態
systemctl --user status pipewire_scarlett_setup.service
```

**注意事項：**
- 服務檔案中的腳本路徑使用 `%h` 代表用戶家目錄
- 如果腳本位置不同，請修改 `pipewire_scarlett_setup.service` 中的 `ExecStart` 路徑
- 服務會在 PipeWire 啟動後自動執行
- 如果執行失敗，會在 5 秒後自動重試

**驗證服務是否正常運作：**
```bash
# 檢查服務狀態（應顯示 active (exited) 且 status=0/SUCCESS）
systemctl --user status pipewire_scarlett_setup.service

# 檢查虛擬設備是否創建成功
wpctl status | grep Scarlett
# 應該看到：
#   - Scarlett_1-2 Audio/Sink sink
#   - Scarlett_3-4 Audio/Sink sink
#   - Scarlett 4i4 4th Gen (實體設備)

# 測試播放到各個聲道
python3 ultimate_play.py file_example_WAV_2MG.wav 1  # 測試輸出 1
python3 ultimate_play.py file_example_WAV_2MG.wav 4  # 測試輸出 4
```

**停用開機自動啟動（如需要）：**
```bash
# 停用服務
systemctl --user disable pipewire_scarlett_setup.service

# 停止當前運行的服務
systemctl --user stop pipewire_scarlett_setup.service
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
   chmod +x setup_pipewire_routing_v3.sh
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

# 3. 安裝服務
mkdir -p ~/.config/systemd/user
cp pipewire_scarlett_setup.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable pipewire_scarlett_setup.service

# 4. 重新開機測試
sudo reboot

# 5. 開機後驗證
systemctl --user status pipewire_scarlett_setup.service
wpctl status | grep Scarlett
python3 ultimate_play.py file_example_WAV_2MG.wav 1
```

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