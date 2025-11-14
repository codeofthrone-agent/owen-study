#!/bin/bash
# Phase 4.1 環境檢查腳本
# 用途：檢查視覺檢測系統的所有前置條件

echo "=========================================="
echo "Phase 4.1 - 視覺檢測環境檢查"
echo "=========================================="
echo ""

# 1. 檢查 Jetson Nano 連接
echo "1. 檢查 Jetson Nano 連接 (10.42.0.180)..."
if ping -c 2 10.42.0.180 >/dev/null 2>&1; then
    echo "   ✅ Jetson Nano 可連接"
else
    echo "   ❌ Jetson Nano 無法連接"
    echo "   請確認："
    echo "   - Jetson Nano 已開機"
    echo "   - 網路線已連接"
    echo "   - IP 設定正確"
    exit 1
fi
echo ""

# 2. 檢查機器手臂伺服器端口
echo "2. 檢查機器手臂伺服器 (10.42.0.180:9000)..."
if nc -z -w 2 10.42.0.180 9000 2>/dev/null; then
    echo "   ✅ 機器手臂伺服器端口開啟"
else
    echo "   ❌ 機器手臂伺服器端口未開啟"
    echo "   請在 Jetson Nano 上執行："
    echo "   python3 scripts/robot_arm_server.py --enable-vision --host 10.42.0.180 --port 9000"
    exit 1
fi
echo ""

# 3. 檢查配置檔案
echo "3. 檢查配置檔案..."
if [ -f "config/robot_arm/button_positions.yaml" ]; then
    echo "   ✅ 配置檔案存在"

    # 檢查是否有任何按鈕已校準視覺 ROI
    if grep -q "vision:" config/robot_arm/button_positions.yaml; then
        echo "   ✅ 發現已校準的視覺 ROI"
        echo "   已校準的按鈕："
        grep -B 3 "vision:" config/robot_arm/button_positions.yaml | grep "  [a-z_]*:" | sed 's/://g' | sed 's/^/      - /'
    else
        echo "   ⚠️  尚未校準任何視覺 ROI"
        echo "   需要執行: python3 scripts/calibrate_button_roi.py"
    fi
else
    echo "   ❌ 配置檔案不存在: config/robot_arm/button_positions.yaml"
    exit 1
fi
echo ""

# 4. 檢查 Python 環境
echo "4. 檢查 Python 環境..."
if command -v uv >/dev/null 2>&1; then
    echo "   ✅ uv 已安裝"
else
    echo "   ❌ uv 未安裝"
    exit 1
fi
echo ""

# 5. 檢查必要的 Python 套件
echo "5. 檢查 Python 套件..."
uv run python -c "import cv2; import yaml; import numpy; print('   ✅ 必要套件已安裝 (opencv, yaml, numpy)')" 2>/dev/null || echo "   ❌ 缺少必要套件"
echo ""

echo "=========================================="
echo "環境檢查完成"
echo "=========================================="
echo ""
echo "下一步建議："
echo "1. 如果所有檢查都通過，請執行 ROI 校準"
echo "2. 校準完成後，執行快速測試驗證"
echo ""
