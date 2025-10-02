#!/bin/bash

# v3 版本：使用最簡化的 pactl 命令，移除所有附加屬性，只保留核心功能。

# 函數：用於創建虛擬 sink，並檢查是否成功
create_virtual_sink() {
    local SINK_NAME=$1
    echo "(i) 正在嘗試使用簡化命令創建虛擬輸出設備 '$SINK_NAME'..."
    
    # 執行最簡化的命令，只提供模組名和 sink 名稱
    OUTPUT=$(pactl load-module module-null-sink sink_name=$SINK_NAME 2>&1)
    
    if [ $? -ne 0 ]; then
        echo "❌ 錯誤：創建 '$SINK_NAME' 失敗！"
        echo "    原因: $OUTPUT"
        exit 1
    else
        echo "    ✅ 成功創建 '$SINK_NAME'。 模組索引: $OUTPUT"
    fi
}

# --- 執行步驟 ---

# 1. 卸載之前可能失敗的模組，確保一個乾淨的狀態 (如果不存在也沒關係)
echo "(i) 清理舊的虛擬設備 (如果存在)..."
pactl unload-module module-null-sink >/dev/null 2>&1
sleep 1

# 2. 創建新的虛擬設備
create_virtual_sink "Scarlett_1-2"
create_virtual_sink "Scarlett_3-4"

echo " "
echo "等待 2 秒，讓 PipeWire 完成設備創建..."
sleep 2

# 3. 進行連接
DEVICE_NAME="alsa_output.usb-Focusrite_Scarlett_4i4_4th_Gen_S46AMBA3A82925-00.pro-output-0"

echo "(i) 正在嘗試連接 'Scarlett_1-2' 到物理輸出 1 和 2..."
pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_AUX0"
pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_AUX1"

echo "(i) 正在嘗試連接 'Scarlett_3-4' 到物理輸出 3 和 4..."
pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_AUX2"
pw-link "Scarlett_3-4:monitor_FR" "$DEVICE_NAME:playback_AUX3"

echo " "
echo "✅ 腳本執行完畢。"
echo "請再次執行 'pactl list sinks' 來檢查虛擬設備是否已出現。"
