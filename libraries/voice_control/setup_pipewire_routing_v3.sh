#!/bin/bash

# v5 版本：自動切換到 Pro Audio 模式並設定路由

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
echo "Scarlett 4i4 PipeWire 路由設定 (v5)"
echo "==========================================="
echo ""

# 1. 檢查並切換到 Pro Audio 模式
echo "(i) 檢查 Scarlett 設備的 PipeWire Profile..."

# 獲取 Scarlett 卡片名稱
CARD_NAME=$(pactl list cards short | grep -i "Scarlett_4i4" | awk '{print $2}')
if [ -z "$CARD_NAME" ]; then
    # 嘗試其他可能的名稱格式
    CARD_NAME=$(pactl list cards short | grep -i "Focusrite.*Scarlett" | awk '{print $2}')
fi

if [ -z "$CARD_NAME" ]; then
    echo "❌ 錯誤：找不到 Scarlett 音訊卡！"
    echo "請確認："
    echo "  1. Scarlett 4i4 已連接並開機"
    echo "  2. 執行 pactl list cards short 檢查"
    exit 1
fi

echo "    找到音訊卡: $CARD_NAME"

# 檢查當前 profile
CURRENT_PROFILE=$(pactl list cards | grep -A 100 "$CARD_NAME" | grep "Active Profile:" | awk -F': ' '{print $2}')
echo "    當前 Profile: $CURRENT_PROFILE"

# 切換到 Pro Audio 模式
if [ "$CURRENT_PROFILE" != "pro-audio" ]; then
    echo "    ⚠️  非 Pro Audio 模式，正在自動切換..."
    pactl set-card-profile "$CARD_NAME" pro-audio

    if [ $? -eq 0 ]; then
        echo "    ✅ 已成功切換到 Pro Audio 模式"
        sleep 2  # 等待 PipeWire 應用新配置
    else
        echo "    ❌ 切換失敗！"
        echo ""
        echo "請手動切換："
        echo "  pactl set-card-profile $CARD_NAME pro-audio"
        exit 1
    fi
else
    echo "    ✅ 已是 Pro Audio 模式"
fi

echo ""

# 2. 清理舊的虛擬設備
echo "(i) 清理舊的虛擬設備 (如果存在)..."
pactl unload-module module-null-sink >/dev/null 2>&1
sleep 1

# 3. 創建新的虛擬設備
create_virtual_sink "Scarlett_1-2"
create_virtual_sink "Scarlett_3-4"

echo " "
echo "等待 2 秒，讓 PipeWire 完成設備創建..."
sleep 2

# 4. 自動偵測 Scarlett Pro Audio 設備名稱
echo "(i) 偵測 Scarlett Pro Audio 設備..."
DEVICE_NAME=$(pactl list sinks short | grep -i "usb-Focusrite_Scarlett_4i4.*pro-output" | awk '{print $2}' | head -1)

if [ -z "$DEVICE_NAME" ]; then
    echo "❌ 錯誤：找不到 Scarlett Pro Audio 設備！"
    echo "請確認："
    echo "  1. Scarlett 4i4 已連接並開機"
    echo "  2. Profile 已切換到 pro-audio"
    echo "  3. 執行 pactl list sinks short 檢查"
    exit 1
fi

echo "    找到設備: $DEVICE_NAME"

# 5. 確認模式
echo "    模式: Pro Audio (Direct Mode)"
echo "    ✅ 可使用全部 4 個獨立輸出"
echo ""

# 6. 連接虛擬設備到實體輸出（Direct 模式）
echo "(i) 正在連接到 AUX 端口..."

# 專業輸出模式 - 使用 AUX 端口進行獨立四通道輸出
pw-link "Scarlett_1-2:monitor_FL" "$DEVICE_NAME:playback_AUX0" && echo "    ✅ 輸出 1 已連接"
pw-link "Scarlett_1-2:monitor_FR" "$DEVICE_NAME:playback_AUX1" && echo "    ✅ 輸出 2 已連接"
pw-link "Scarlett_3-4:monitor_FL" "$DEVICE_NAME:playback_AUX2" && echo "    ✅ 輸出 3 已連接"
pw-link "Scarlett_3-4:monitor_FR" "$DEVICE_NAME:playback_AUX3" && echo "    ✅ 輸出 4 已連接"

echo " "

# 7. 驗證連接
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
echo "✅ 設定完成 - Pro Audio 模式"
echo "==========================================="
echo ""
echo "設備對應："
echo "  Scarlett_1-2 → 物理輸出 1 和 2 (獨立單聲道)"
echo "  Scarlett_3-4 → 物理輸出 3 和 4 (獨立單聲道)"
echo ""
echo "測試播放："
echo "  python3 ultimate_play.py <音訊檔案> 1  # 播放到輸出 1"
echo "  python3 ultimate_play.py <音訊檔案> 2  # 播放到輸出 2"
echo "  python3 ultimate_play.py <音訊檔案> 3  # 播放到輸出 3"
echo "  python3 ultimate_play.py <音訊檔案> 4  # 播放到輸出 4"
echo ""
