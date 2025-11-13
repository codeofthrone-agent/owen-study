#!/bin/bash

# ============================================
# Scarlett 4i4 USB 音訊驅動修復腳本
# ============================================
# 用途：修復 PipeWire 無法識別 Scarlett 4i4 的問題
# 症狀：設備在 lsusb 可見，但 aplay -l 或 PipeWire 看不到
# 原因：USB 音訊驅動未正確載入或需要重新初始化
# ============================================

set -e  # 遇到錯誤立即停止

echo "============================================"
echo "Scarlett 4i4 USB 音訊驅動修復工具"
echo "============================================"
echo ""

# 1. 檢查設備是否連接
echo "[1/5] 檢查 USB 設備連接狀態..."
if lsusb | grep -iq "Focusrite.*Scarlett"; then
    echo "  ✅ Scarlett 設備已連接到 USB"
    lsusb | grep -i "Focusrite.*Scarlett"
else
    echo "  ❌ 錯誤：找不到 Scarlett USB 設備"
    echo "  請檢查："
    echo "    - USB 連接是否穩固"
    echo "    - 設備是否開機"
    echo "    - 更換 USB 連接埠"
    exit 1
fi
echo ""

# 2. 檢查 ALSA 是否識別
echo "[2/5] 檢查 ALSA 音訊系統識別狀態..."
if aplay -l | grep -iq "Scarlett"; then
    echo "  ✅ ALSA 已正確識別 Scarlett 設備"
    aplay -l | grep -i "Scarlett"
    echo ""
    echo "  ℹ️  驅動正常，跳過修復步驟..."
    NEED_FIX=false
else
    echo "  ⚠️  ALSA 未識別 Scarlett 設備，需要修復"
    NEED_FIX=true
fi
echo ""

# 3. 修復：重新載入 USB 音訊驅動
if [ "$NEED_FIX" = true ]; then
    echo "[3/5] 重新載入 USB 音訊驅動模組..."
    echo "  執行：sudo modprobe -r snd_usb_audio"
    sudo modprobe -r snd_usb_audio
    sleep 1

    echo "  執行：sudo modprobe snd_usb_audio"
    sudo modprobe snd_usb_audio
    sleep 2

    # 驗證修復結果
    if aplay -l | grep -iq "Scarlett"; then
        echo "  ✅ 驅動修復成功！"
        aplay -l | grep -i "Scarlett"
    else
        echo "  ❌ 驅動修復失敗"
        echo "  建議："
        echo "    1. 重新插拔 USB"
        echo "    2. 重新啟動系統"
        echo "    3. 檢查 dmesg 日誌: dmesg | tail -50"
        exit 1
    fi
else
    echo "[3/5] 跳過驅動修復（已正常運作）"
fi
echo ""

# 4. 重啟 PipeWire 服務
echo "[4/5] 重啟 PipeWire 音訊服務..."
echo "  執行：systemctl --user restart pipewire pipewire-pulse wireplumber"
systemctl --user restart pipewire pipewire-pulse wireplumber
sleep 3

# 檢查 PipeWire 是否識別
if wpctl status | grep -iq "Scarlett 4i4"; then
    echo "  ✅ PipeWire 已識別 Scarlett 設備"
else
    echo "  ⚠️  警告：PipeWire 可能未正確識別設備"
    echo "  請執行：wpctl status | grep -i scarlett"
fi
echo ""

# 5. 執行路由設定
echo "[5/5] 執行 PipeWire 路由設定..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/setup_pipewire_routing_v3.sh" ]; then
    echo "  執行：$SCRIPT_DIR/setup_pipewire_routing_v3.sh"
    bash "$SCRIPT_DIR/setup_pipewire_routing_v3.sh"
else
    echo "  ⚠️  警告：找不到 setup_pipewire_routing_v3.sh"
    echo "  請手動執行路由設定腳本"
fi
echo ""

# 完成
echo "============================================"
echo "✅ 修復流程完成"
echo "============================================"
echo ""
echo "驗證步驟："
echo "  1. 檢查設備：wpctl status | grep -i scarlett"
echo "  2. 測試播放：python3 ultimate_play.py file_example_WAV_2MG.wav 1"
echo ""
echo "如果仍無聲音，請檢查："
echo "  - alsa-scarlett-gui 是否設定為 Direct 模式"
echo "  - 實體音訊線是否正確連接"
echo "  - 音量設定：wpctl set-volume @DEFAULT_SINK@ 0.8"
echo ""
