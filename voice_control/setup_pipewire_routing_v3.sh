#!/bin/bash

# v4 版本：自動偵測設備模式，支援 pro-output 和 surround 模式

# 函數：用於創建虛擬 sink，並檢查是否成功
create_virtual_sink() {
    local SINK_NAME=$1
    echo "(i) 正在創建虛擬輸出設備 '$SINK_NAME'..."

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

echo "==========================================="
echo "Scarlett 4i4 PipeWire 路由設定"
echo "==========================================="
echo ""

# 1. 清理舊的虛擬設備
echo "(i) 清理舊的虛擬設備 (如果存在)..."
pactl unload-module module-null-sink >/dev/null 2>&1
sleep 1

# 2. 創建新的虛擬設備
create_virtual_sink "Scarlett_1-2"
create_virtual_sink "Scarlett_3-4"

echo " "
echo "等待 2 秒，讓 PipeWire 完成設備創建..."
sleep 2

# 3. 自動偵測 Scarlett 設備名稱
echo "(i) 偵測 Scarlett 設備..."
DEVICE_NAME=$(pactl list sinks short | grep -i "usb-Focusrite_Scarlett_4i4" | awk '{print $2}' | head -1)

if [ -z "$DEVICE_NAME" ]; then
    echo "❌ 錯誤：找不到 Scarlett 設備！"
    echo "請確認："
    echo "  1. Scarlett 4i4 已連接並開機"
    echo "  2. 設備已被系統識別 (執行 aplay -l 檢查)"
    exit 1
fi

echo "    找到設備: $DEVICE_NAME"

# 4. 判斷設備模式
MODE=""
if [[ "$DEVICE_NAME" == *"pro-output-0"* ]]; then
    MODE="pro-output"
    echo "    模式: 專業輸出模式 (Direct Mode)"
elif [[ "$DEVICE_NAME" == *"surround-50"* ]]; then
    MODE="surround-50"
    echo "    模式: 5.0 環繞音效"
elif [[ "$DEVICE_NAME" == *"surround-21"* ]]; then
    MODE="surround-21"
    echo "    模式: 2.1 環繞音效"
elif [[ "$DEVICE_NAME" == *"analog-stereo"* ]]; then
    MODE="stereo"
    echo "    模式: 立體聲"
else
    echo "    ⚠️  警告: 未知模式"
    MODE="unknown"
fi
echo ""

# 5. 根據模式進行連接
echo "(i) 正在進行連接..."

if [ "$MODE" = "pro-output" ]; then
    # 專業輸出模式 - 使用 AUX 端口
    echo "    連接到 AUX 端口..."
    pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_AUX0" && echo "    ✅ 輸出 1 已連接"
    pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_AUX1" && echo "    ✅ 輸出 2 已連接"
    pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_AUX2" && echo "    ✅ 輸出 3 已連接"
    pw-link "Scarlett_3-4:monitor_FR" "$DEVICE_NAME:playback_AUX3" && echo "    ✅ 輸出 4 已連接"

elif [ "$MODE" = "surround-50" ]; then
    # 5.0 環繞音效模式 - 使用 FL, FR, RL, RR
    echo "    連接到環繞音效端口..."
    pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_FL" && echo "    ✅ 輸出 1 (前左) 已連接"
    pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_FR" && echo "    ✅ 輸出 2 (前右) 已連接"
    pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_RL" && echo "    ✅ 輸出 3 (後左) 已連接"
    pw-link "Scarlett_3-4:monitor_FR" "$DEVICE_NAME:playback_RR" && echo "    ✅ 輸出 4 (後右) 已連接"

elif [ "$MODE" = "surround-21" ]; then
    # 2.1 環繞音效模式 - 使用 FL, FR, LFE (只有 3 個聲道)
    echo "    連接到 2.1 環繞音效端口..."
    echo "    ⚠️  注意: 2.1 模式只有 3 個聲道，僅能使用輸出 1, 2, 3"
    pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_FL" && echo "    ✅ 輸出 1 (前左) 已連接"
    pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_FR" && echo "    ✅ 輸出 2 (前右) 已連接"
    pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_LFE" && echo "    ✅ 輸出 3 (重低音) 已連接"

else
    echo "❌ 錯誤: 無法自動判斷連接方式"
    echo ""
    echo "請檢查 Scarlett 4i4 的設定："
    echo "  1. 打開 alsa-scarlett-gui"
    echo "  2. 將 Routing 設定為 'Direct' 模式"
    echo "  3. 點擊 'Save to Hardware'"
    echo "  4. 重新插拔 USB"
    echo "  5. 再次執行此腳本"
    exit 1
fi

echo " "

# 6. 驗證連接
echo "(i) 驗證連接狀態..."
echo "-------------------------------------------"
CONNECTIONS=$(pw-link -l | grep -A 1 "Scarlett_1-2:monitor\|Scarlett_3-4:monitor" | grep "|")

if [ -z "$CONNECTIONS" ]; then
    echo "⚠️  警告: 無法驗證連接 (可能是 pw-link 版本問題)"
    echo "請手動執行以下命令驗證："
    echo "  pw-link -l | grep Scarlett"
else
    echo "$CONNECTIONS"
fi

echo ""
echo "==========================================="
echo "✅ 腳本執行完畢"
echo "==========================================="
echo ""
echo "設備對應："
if [ "$MODE" = "pro-output" ]; then
    echo "  Scarlett_1-2 → 物理輸出 1 和 2"
    echo "  Scarlett_3-4 → 物理輸出 3 和 4"
elif [ "$MODE" = "surround-50" ]; then
    echo "  Scarlett_1-2 → 物理輸出 1 (前左) 和 2 (前右)"
    echo "  Scarlett_3-4 → 物理輸出 3 (後左) 和 4 (後右)"
elif [ "$MODE" = "surround-21" ]; then
    echo "  Scarlett_1-2 → 物理輸出 1 (前左) 和 2 (前右)"
    echo "  Scarlett_3-4 → 物理輸出 3 (重低音) [注意: 輸出 4 無法使用]"
fi
echo ""
echo "測試播放："
echo "  python3 ultimate_play.py <音訊檔案> 1  # 播放到輸出 1"
echo "  python3 ultimate_play.py <音訊檔案> 3  # 播放到輸出 3"
echo ""
