#!/bin/bash
# Scarlett 4i4 音訊路由診斷腳本
# 用於診斷為什麼聲道 3/4 沒有聲音，而聲道 1 會從輸出 1 和 2 發聲

echo "=========================================="
echo "Scarlett 4i4 音訊路由診斷工具"
echo "=========================================="
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 檢查基本系統資訊
echo "【1. 系統基本檢查】"
echo "===================="

echo -n "✓ 檢查用戶群組: "
if groups | grep -q audio; then
    echo -e "${GREEN}已加入 audio 群組${NC}"
else
    echo -e "${RED}未加入 audio 群組 (需執行: sudo usermod -a -G audio \$USER)${NC}"
fi

echo -n "✓ 檢查 ALSA 設備: "
if aplay -l | grep -q "Scarlett"; then
    echo -e "${GREEN}Scarlett 設備已識別${NC}"
    aplay -l | grep -A 2 "Scarlett"
else
    echo -e "${RED}找不到 Scarlett 設備${NC}"
fi

echo ""

# 2. 檢查 systemd 服務狀態
echo "【2. Systemd 服務狀態】"
echo "======================="

if systemctl --user is-active --quiet pipewire_scarlett_setup.service; then
    echo -e "✓ 服務狀態: ${GREEN}執行中${NC}"
else
    echo -e "✓ 服務狀態: ${RED}未執行${NC}"
fi

if systemctl --user is-enabled --quiet pipewire_scarlett_setup.service; then
    echo -e "✓ 開機啟動: ${GREEN}已啟用${NC}"
else
    echo -e "✓ 開機啟動: ${YELLOW}未啟用${NC}"
fi

echo ""
echo "服務日誌（最後 10 行）:"
systemctl --user status pipewire_scarlett_setup.service --no-pager -n 10 | tail -n 10

echo ""

# 3. 檢查 PipeWire 設備
echo "【3. PipeWire 設備檢查】"
echo "========================"

echo "✓ 所有音訊設備:"
wpctl status | grep -A 20 "Audio"

echo ""

# 4. 檢查虛擬設備是否創建
echo "【4. 虛擬設備檢查】"
echo "==================="

SCARLETT_1_2=$(pactl list sinks short | grep "Scarlett_1-2")
SCARLETT_3_4=$(pactl list sinks short | grep "Scarlett_3-4")

if [ -n "$SCARLETT_1_2" ]; then
    echo -e "✓ Scarlett_1-2: ${GREEN}已創建${NC}"
    echo "  $SCARLETT_1_2"
else
    echo -e "✓ Scarlett_1-2: ${RED}未創建${NC}"
fi

if [ -n "$SCARLETT_3_4" ]; then
    echo -e "✓ Scarlett_3-4: ${GREEN}已創建${NC}"
    echo "  $SCARLETT_3_4"
else
    echo -e "✓ Scarlett_3-4: ${RED}未創建${NC}"
fi

echo ""

# 5. 檢查實體 Scarlett 設備
echo "【5. 實體 Scarlett 設備檢查】"
echo "============================="

echo "✓ 實體設備節點:"
pw-cli ls Node | grep -i "scarlett\|4i4" | grep -v "Scarlett_1-2\|Scarlett_3-4" | head -20

echo ""

# 6. 檢查 PipeWire 連接
echo "【6. PipeWire 音訊路由連接】"
echo "============================"

echo "✓ 輸出端口 (Sources):"
pw-link -o | head -30

echo ""
echo "✓ 輸入端口 (Targets):"
pw-link -i | head -30

echo ""

# 7. 檢查實體 Scarlett 的具體連接
echo "【7. Scarlett 實體設備連接詳情】"
echo "=================================="

echo "✓ 查找實體 Scarlett 輸出端口:"
SCARLETT_HW=$(pw-link -o | grep -i "4i4\|Gen.*output\|alsa.*scarlett.*playback" | head -10)
if [ -n "$SCARLETT_HW" ]; then
    echo -e "${GREEN}找到實體端口:${NC}"
    echo "$SCARLETT_HW"
else
    echo -e "${RED}找不到實體 Scarlett 輸出端口${NC}"
    echo "可能原因: PipeWire 未正確載入硬體設備"
fi

echo ""

# 8. 檢查虛擬設備的連接狀態
echo "【8. 虛擬設備連接檢查】"
echo "======================="

echo "✓ Scarlett_1-2 的連接:"
pw-link -l | grep -A 5 "Scarlett_1-2" | head -20

echo ""
echo "✓ Scarlett_3-4 的連接:"
pw-link -l | grep -A 5 "Scarlett_3-4" | head -20

echo ""

# 9. 檢查 ALSA 配置
echo "【9. ALSA 硬體資訊】"
echo "==================="

echo "✓ Scarlett 支援的音訊格式:"
if [ -f /proc/asound/card1/stream0 ]; then
    cat /proc/asound/card1/stream0
else
    echo -e "${YELLOW}找不到 /proc/asound/card1/stream0${NC}"
fi

echo ""

# 10. 檢查 alsa-scarlett-gui 設定
echo "【10. Scarlett 硬體路由模式】"
echo "============================="

echo "✓ 檢查是否設定為 Direct 模式:"
if command -v alsa-scarlett-gui &> /dev/null; then
    echo "alsa-scarlett-gui 已安裝"
    echo -e "${YELLOW}請手動開啟 alsa-scarlett-gui 確認 Routing 是否設為 Direct 模式${NC}"
else
    echo -e "${RED}alsa-scarlett-gui 未安裝${NC}"
    echo "安裝: sudo apt install alsa-scarlett-gui"
fi

echo ""

# 11. 診斷問題總結
echo "【11. 問題診斷總結】"
echo "===================="

echo ""
echo "🔍 可能的問題原因:"
echo ""

# 檢查虛擬設備是否連接到實體設備
if [ -z "$SCARLETT_HW" ]; then
    echo -e "${RED}❌ 問題 1: 找不到實體 Scarlett 輸出端口${NC}"
    echo "   解決方法: 檢查 WirePlumber 是否正確載入 ALSA 設備"
    echo "   執行: systemctl --user restart wireplumber pipewire"
fi

# 檢查虛擬設備連接
LINK_1_2=$(pw-link -l | grep "Scarlett_1-2:playback" | grep -v "monitor")
LINK_3_4=$(pw-link -l | grep "Scarlett_3-4:playback" | grep -v "monitor")

if [ -z "$LINK_1_2" ] || [ -z "$LINK_3_4" ]; then
    echo -e "${RED}❌ 問題 2: 虛擬設備未連接到實體設備${NC}"
    echo "   解決方法: 執行 setup_pipewire_routing_v3.sh 重新建立連接"
    echo "   或檢查腳本中的 pw-link 命令是否正確執行"
fi

# 檢查聲道映射
echo ""
echo -e "${YELLOW}⚠️  問題 3: 聲道映射可能不正確${NC}"
echo "   現象: 播放到聲道 1 時，輸出 1 和 2 都有聲音"
echo "   原因: Scarlett_1-2 是立體聲設備，包含 L/R 兩個聲道"
echo "   期望行為:"
echo "     - python3 ultimate_play.py file.wav 1 → 只從輸出 1 發聲 (L)"
echo "     - python3 ultimate_play.py file.wav 2 → 只從輸出 2 發聲 (R)"
echo "     - python3 ultimate_play.py file.wav 3 → 只從輸出 3 發聲 (L)"
echo "     - python3 ultimate_play.py file.wav 4 → 只從輸出 4 發聲 (R)"
echo ""
echo "   實際行為 (如果映射錯誤):"
echo "     - 聲道 1 → 輸出 1+2 都發聲 (立體聲)"
echo "     - 聲道 3 → 沒有聲音 (連接錯誤)"

echo ""
echo -e "${GREEN}✅ 建議的修復步驟:${NC}"
echo "1. 檢查 ultimate_play.py 是否正確設定單聲道播放"
echo "2. 檢查 setup_pipewire_routing_v3.sh 中的 pw-link 連接"
echo "3. 確認實體 Scarlett 設備的端口名稱"
echo "4. 使用 pw-link 手動測試連接"

echo ""
echo "=========================================="
echo "診斷完成"
echo "=========================================="
