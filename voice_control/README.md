# Scarlett 4i4 (4th Gen) Linux 獨立四通道輸出解決方案

本文件提供了在 Linux (Ubuntu 24) 環境下，為 Focusrite Scarlett 4i4 (第四代) 設定並使用真正獨立的 4 個物理輸出的最終解決方案。

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