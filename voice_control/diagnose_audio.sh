#!/bin/bash

echo "==========================================="
echo "Scarlett 4i4 音訊診斷工具"
echo "==========================================="
echo ""

# 1. 檢查 Scarlett 設備是否被偵測到
echo "1. 檢查 Scarlett 設備是否被偵測到..."
echo "-------------------------------------------"
aplay -l | grep -i scarlett
if [ $? -ne 0 ]; then
    echo "❌ 錯誤：找不到 Scarlett 設備！"
    echo "   請確認設備已連接並開機。"
    exit 1
else
    echo "✅ Scarlett 設備已偵測到"
fi
echo ""

# 2. 檢查 PipeWire 是否正在運行
echo "2. 檢查 PipeWire 服務狀態..."
echo "-------------------------------------------"
systemctl --user status pipewire | grep "Active:"
systemctl --user status pipewire-pulse | grep "Active:"
echo ""

# 3. 列出所有 PipeWire 音訊設備
echo "3. 列出所有 PipeWire 音訊輸出設備..."
echo "-------------------------------------------"
pactl list sinks short
echo ""

# 4. 檢查虛擬設備是否存在
echo "4. 檢查虛擬設備 Scarlett_1-2 和 Scarlett_3-4..."
echo "-------------------------------------------"
pactl list sinks short | grep -i scarlett_1-2
if [ $? -eq 0 ]; then
    echo "✅ 找到虛擬設備 Scarlett_1-2"
else
    echo "❌ 找不到虛擬設備 Scarlett_1-2"
    echo "   請執行 setup_pipewire_routing_v3.sh"
fi

pactl list sinks short | grep -i scarlett_3-4
if [ $? -eq 0 ]; then
    echo "✅ 找到虛擬設備 Scarlett_3-4"
else
    echo "❌ 找不到虛擬設備 Scarlett_3-4"
    echo "   請執行 setup_pipewire_routing_v3.sh"
fi
echo ""

# 5. 檢查當前預設輸出設備
echo "5. 檢查當前預設輸出設備..."
echo "-------------------------------------------"
pactl get-default-sink
echo ""

# 6. 列出所有 PipeWire 連接
echo "6. 列出所有 PipeWire 音訊連接 (pw-link)..."
echo "-------------------------------------------"
pw-link -o | grep -i scarlett
echo ""

# 7. 檢查實際的物理輸出端口
echo "7. 檢查 Scarlett 4i4 的物理輸出端口..."
echo "-------------------------------------------"
pw-link -o | grep "alsa_output.usb-Focusrite" -A 10
echo ""

# 8. 檢查音量設定
echo "8. 檢查 Scarlett 設備的音量設定..."
echo "-------------------------------------------"
pactl list sinks | grep -A 20 "usb-Focusrite" | grep -E "Name:|Volume:|Mute:"
echo ""

# 9. 檢查 ALSA 混音器設定
echo "9. 檢查 ALSA 混音器設定..."
echo "-------------------------------------------"
amixer -c Scarlett | grep -E "PCM|Master|Direct" | head -20
echo ""

# 10. 測試基本音訊播放
echo "10. 測試基本音訊播放 (到預設設備)..."
echo "-------------------------------------------"
if [ -f "file_example_WAV_2MG.wav" ]; then
    echo "正在播放測試音訊到預設設備 (3秒)..."
    timeout 3 ffplay -nodisp -autoexit file_example_WAV_2MG.wav 2>&1 | head -5
    echo ""
    echo "⚠️  如果聽不到聲音，檢查："
    echo "   1. 喇叭或耳機是否正確連接到 Scarlett 的輸出"
    echo "   2. Scarlett 的輸出音量旋鈕是否開啟"
    echo "   3. 系統音量是否太低或靜音"
else
    echo "找不到測試音訊檔案"
fi
echo ""

# 11. 檢查 Python 環境
echo "11. 檢查 Python 環境..."
echo "-------------------------------------------"
python3 --version
echo ""
python3 -c "import sounddevice; print('sounddevice 版本:', sounddevice.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ sounddevice 模組未安裝"
else
    echo "✅ sounddevice 模組已安裝"
fi
echo ""

# 12. 列出所有音訊設備供 Python sounddevice 使用
echo "12. 列出 Python sounddevice 可用的設備..."
echo "-------------------------------------------"
python3 -c "import sounddevice as sd; print(sd.query_devices())" 2>/dev/null
echo ""

echo "==========================================="
echo "診斷完成"
echo "==========================================="
echo ""
echo "常見問題排查："
echo "1. 如果找不到虛擬設備 → 執行 ./setup_pipewire_routing_v3.sh"
echo "2. 如果 PipeWire 未運行 → systemctl --user restart pipewire pipewire-pulse"
echo "3. 如果沒有聲音但設備都正常 → 檢查 Scarlett 硬體音量旋鈕"
echo "4. 如果連接不正確 → 重新執行 setup_pipewire_routing_v3.sh"
echo "5. 檢查 alsa-scarlett-gui 是否設定為 Direct 模式"
echo ""
