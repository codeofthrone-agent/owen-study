#!/bin/bash

# 終極版 v2：全自動播放腳本。自動切換預設輸出設備，並播放到指定聲道。

AUDIO_FILE="$1"
TARGET_CHANNEL="$2"

# --- 1. 檢查輸入 ---
if [ "$#" -ne 2 ]; then
    echo "使用方法: $0 <音訊檔案路徑> <目標邏輯聲道 (1-4)>"
    exit 1
fi

if ! [[ "$TARGET_CHANNEL" =~ ^[1-4]$ ]]; then
    echo "錯誤: 目標邏輯聲道必須是 1 到 4 之間的數字。"
    exit 1
fi

# --- 2. 根據目標決定虛擬設備和聲道映射 ---
SINK_NAME=""
PAN_FILTER=""
PHYSICAL_OUTPUT=""

if [[ "$TARGET_CHANNEL" -eq 1 || "$TARGET_CHANNEL" -eq 2 ]]; then
    SINK_NAME="Scarlett_1-2"
else
    SINK_NAME="Scarlett_3-4"
fi

if [[ "$TARGET_CHANNEL" -eq 1 || "$TARGET_CHANNEL" -eq 3 ]]; then
    PAN_FILTER="pan=stereo|c0=1*c0|c1=0*c0"
    PHYSICAL_OUTPUT=$([ "$TARGET_CHANNEL" -eq 1 ] && echo 1 || echo 3)
else
    PAN_FILTER="pan=stereo|c0=0*c0|c1=1*c0"
    PHYSICAL_OUTPUT=$([ "$TARGET_CHANNEL" -eq 2 ] && echo 2 || echo 4)
fi

# --- 3. 自動切換預設輸出設備 --- 
echo "(步驟 1/3) 正在將系統預設輸出切換到: $SINK_NAME ..."

# 執行切換命令，並檢查是否成功
OUTPUT=$(pactl set-default-sink "$SINK_NAME" 2>&1)
if [ $? -ne 0 ]; then
    echo "❌ 錯誤：切換輸出設備失敗！"
    echo "    原因: $OUTPUT"
    echo "    請確認 setup_pipewire_routing_v3.sh 是否已成功執行。"
    exit 1
fi
echo "    ✅ 切換成功。"

# --- 4. 執行播放 --- 
echo "(步驟 2/3) 準備播放到邏輯聲道 $TARGET_CHANNEL..."
echo "    - 聲音應從【物理輸出 $PHYSICAL_OUTPUT】播放出來。"
echo "(步驟 3/3) 播放 5 秒鐘..."

# 直接播放，因為預設輸出已經被我們設定好了
ffmpeg -i "$AUDIO_FILE" -t 5 -af "$PAN_FILTER" -ar 48000 -ac 2 -f s16le - | aplay -f S16_LE -r 48000 -c 2

if [ $? -eq 0 ]; then
    echo "✅ 播放完畢。"
else
    echo "❌ 播放失敗。"
fi
