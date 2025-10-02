# Scarlett 4i4 Linux 音訊輸出問題偵錯報告 (最終方案版)

本文檔記錄了從發現問題到最終解決 Focusrite Scarlett 4i4 4th Gen 在 Ubuntu 24 環境下實現真正獨立四通道音訊輸出的完整過程。

## 1. 最終結論與現況

經過詳盡的、反覆的測試與配置，我們成功地找到了讓 Scarlett 4i4 的**全部 4 個物理輸出都能獨立工作**的方法。

**最終結論：**

透過 `alsa-scarlett-gui` 設定硬體模式，並結合 PipeWire 的進階路由功能，可以繞過系統預設的錯誤混音行為，實現真正的獨立四通道輸出。

**目前狀態 (正確設定後):**

1.  音效卡硬體處於 **`Direct` (直接)** 模式。
2.  系統中創建了兩個虛擬立體聲輸出設備：`Scarlett_1-2` 和 `Scarlett_3-4`。
3.  透過 `pw-link` 建立了手動路由連結：
    *   `Scarlett_1-2` 的左右聲道 → **物理輸出 1 和 2**
    *   `Scarlett_3-4` 的左右聲道 → **物理輸出 3 和 4**

## 2. 最終解決方案

完整的解決方案包含三個核心部分：硬體模式設定、PipeWire 路由設定、以及最終的播放腳本。

### A. 硬體模式設定 (只需做一次)

1.  安裝並打開 `alsa-scarlett-gui` 工具。
2.  找到 `Routing` (路由) 選項，將其設定為 **`Direct` (直接)** 模式。
3.  儲存設定。此設定會被記憶在音效卡的硬體中。

### B. PipeWire 路由設定 (每次開機執行)

以下腳本 (`setup_pipewire_routing_v3.sh`) 負責創建並連結虛擬輸出設備。此腳本需要在每次開機後、播放聲音前被執行一次。

```bash
#!/bin/bash

# v3 版本：使用最簡化的 pactl 命令，移除所有附加屬性，只保留核心功能。

# 函數：用於創建虛擬 sink，並檢查是否成功
create_virtual_sink() {
    local SINK_NAME=$1
    echo "(i) 正在嘗試使用簡化命令創建虛擬輸出設備 '$SINK_NAME'..."
    
    OUTPUT=$(pactl load-module module-null-sink sink_name=$SINK_NAME 2>&1)
    
    if [ $? -ne 0 ]; then
        echo "❌ 錯誤：創建 '$SINK_NAME' 失敗！"
        echo "    原因: $OUTPUT"
        exit 1
    else
        echo "    ✅ 成功創建 '$SINK_NAME'。 模組索引: $OUTPUT"
    fi
}

# 1. 清理舊的虛擬設備 (如果存在)
echo "(i) 清理舊的虛擬設備 (如果存在)..."
pactl unload-module module-null-sink >/dev/null 2>&1
sleep 1

# 2. 創建新的虛擬設備
create_virtual_sink "Scarlett_1-2"
create_virtual_sink "Scarlett_3-4"

echo " "
echo "等待 2 秒..."
sleep 2

# 3. 進行連接
DEVICE_NAME="alsa_output.usb-Focusrite_Scarlett_4i4_4th_Gen_S46AMBA3A82925-00.pro-output-0"

echo "(i) 正在連接 'Scarlett_1-2' 到物理輸出 1 和 2..."
pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_AUX0"
pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_AUX1"

echo "(i) 正在連接 'Scarlett_3-4' 到物理輸出 3 和 4..."
pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_AUX2"
pw-link "Scarlett_3-4:monitor_FR" "$DEVICE_NAME:playback_AUX3"

echo " "
echo "✅ PipeWire 路由設定完成！"
```
**註記**: 要讓此設定永久生效，可將此腳本設定為開機自動執行。

### C. 全自動播放腳本

`ultimate_play.sh` 腳本是最終的播放工具，它會自動切換系統預設輸出，並將聲音播放到指定的單一聲道。

```bash
#!/bin/bash

# 終極版 v2：全自動播放腳本。自動切換預設輸出設備，並播放到指定聲道。

AUDIO_FILE="$1"
TARGET_CHANNEL="$2"

# ... (腳本內容詳見 ultimate_play.sh)
```

## 3. 偵錯與探索歷程

我們的最終成功，是建立在一系列排除錯誤的基礎上：

1.  **確認硬體混音**：最初，我們發現音效卡在預設模式下，會將多個邏輯聲道混合到物理輸出 1/2。
2.  **繞過 `ffplay` 的 Bug**：我們發現 `ffplay` 會錯誤地將多聲道音訊壓縮回單聲道，因此改用 `ffmpeg | aplay` 的穩定組合。
3.  **解決 `aplay` 硬體衝突**：我們發現 `aplay -D hw:1,0` 會因設備忙碌而失敗，因此改用 `PULSE_SINK` 讓 `aplay` 與系統音訊服務員合作。
4.  **找到硬體模式切換的關鍵**：透過網路搜尋，我們找到了 `alsa-scarlett-gui`，並用它將硬體切換到 `Direct` 模式，這是實現獨立輸出的前提。
5.  **實現 PipeWire 進階路由**：在您的研究基礎上，我們採用了創建虛擬設備 (`null-sink`) 並手動連結 (`pw-link`) 的進階方案，這繞過了 PipeWire 的預設錯誤行為。
6.  **解決 `pactl` 參數問題**：我們發現 `pactl load-module` 命令對附加參數敏感，因此將其簡化為最核心的形式，最終成功創建了虛擬設備。
7.  **解決 `PULSE_SINK` 的無效問題**：我們發現 `PULSE_SINK` 對於我們的腳本沒有如預期般動態切換輸出，最終採用了 `pactl set-default-sink` 在腳本中強制切換，從而實現了全自動播放。

這個過程證明了，解決複雜的 Linux 音訊問題，需要結合底層 ALSA 設定、音訊服務員 (PipeWire) 的進階路由，以及正確的播放工具鏈，三者缺一不可。