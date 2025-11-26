#!/bin/bash

# ==============================================================================
#           專業音訊環境整合診斷腳本 (diagnose_pro_audio.sh)
#
# 這個腳本會全面檢查您的專業音訊設定，從系統底層到專案環境，
# 並為每一個檢查點提供清晰的成功或失敗狀態，最後提供一份總結報告。
# ==============================================================================

# --- Setup ---
set -o pipefail
FAILURES=()

# --- 彩色輸出與日誌函式 ---
C_GREEN='\033[0;32m'
C_RED='\033[0;31m'
C_YELLOW='\033[1;33m'
C_BLUE='\033[0;34m'
C_NC='\033[0m'

print_section() { echo -e "\n${C_BLUE}===== $1 =====${C_NC}"; }
check_ok() { echo -e "[${C_GREEN}✅ OK${C_NC}] $1"; }
check_fail() {
    echo -e "[${C_RED}❌ FAIL${C_NC}] $1"
    FAILURES+=("$2")
}
check_warn() { echo -e "[${C_YELLOW}⚠️ WARN${C_NC}] $1"; }

# ==============================================================================
#                           開始執行檢查
# ==============================================================================

print_section "第一部分：系統健康度檢查"

# 1.1 檢查 Audio 群組
if groups "$(whoami)" | grep -q '\baudio\b'; then
    check_ok "使用者隸屬於 'audio' 群組"
else
    check_fail "使用者不屬於 'audio' 群組" "將使用者加入 audio 群組：sudo usermod -aG audio \$USER (需重新登入)"
fi

# 1.2 檢查即時權限
if grep -r -q '@audio - rtprio' /etc/security/limits.d/ /etc/security/limits.conf 2>/dev/null; then
    check_ok "已為 'audio' 群組設定即時權限 (rtprio)"
else
    check_fail "未設定 'audio' 群組的即時權限" "請參考 setup_v5.sh 註解中的步驟2，創建權限設定檔 (需重啟)"
fi

# 1.3 檢查 PipeWire 服務
if pactl info 2>/dev/null | grep -q 'on PipeWire'; then
    check_ok "PipeWire 正在作為主要音訊伺服器運行"
else
    check_fail "PipeWire 未作為主要音訊伺服器運行" "請確保已安裝 PipeWire 並取代 PulseAudio"
fi

print_section "第二部分：硬體與設定檔檢查"

# 2.1 檢查硬體偵測
if aplay -l 2>/dev/null | grep -q -i 'Scarlett'; then
    check_ok "ALSA 已偵測到 Scarlett 硬體"
    CARD_NAME=$(pactl list cards short | grep -i -E "Focusrite.*Scarlett|Scarlett.*Focusrite" | awk '{print $2}' | head -n 1)

    # 2.2 檢查 Pro Audio 設定檔可用性
    if pactl list cards | grep -A 10 "Name: $CARD_NAME" | grep -q 'pro-audio'; then
        check_ok "'pro-audio' 設定檔可用"

        # 2.3 檢查 Pro Audio 設定檔是否啟用
        if pactl list cards | grep -A 10 "Name: $CARD_NAME" | grep 'Active Profile:' | grep -q 'pro-audio'; then
            check_ok "'pro-audio' 設定檔已啟用"
        else
            check_fail "'pro-audio' 設定檔未啟用" "請執行 ./setup_pipewire_routing_v5.sh 自動切換"
        fi
    else
        check_fail "'pro-audio' 設定檔不可用" "請執行 ./setup_pipewire_routing_v5.sh 嘗試自動創建設定檔"
    fi
else
    check_fail "ALSA 未偵測到 Scarlett 硬體" "請確認 Scarlett 已連接並開機"
fi


print_section "第三部分：虛擬裝置與路由檢查"

# 3.1 檢查虛擬裝置
SINK_1_2_EXISTS=false
if pactl list sinks short | grep -q 'Scarlett_1-2'; then
    check_ok "虛擬裝置 'Scarlett_1-2' 已創建"
    SINK_1_2_EXISTS=true
else
    check_fail "虛擬裝置 'Scarlett_1-2' 未創建" "請執行 ./setup_pipewire_routing_v5.sh"
fi

SINK_3_4_EXISTS=false
if pactl list sinks short | grep -q 'Scarlett_3-4'; then
    check_ok "虛擬裝置 'Scarlett_3-4' 已創建"
    SINK_3_4_EXISTS=true
else
    check_fail "虛擬裝置 'Scarlett_3-4' 未創建" "請執行 ./setup_pipewire_routing_v5.sh"
fi

# 3.2 檢查路由連接
DEVICE_NAME=$(pactl list sinks short | grep -i "Focusrite_Scarlett.*pro-output" | awk '{print $2}' | head -n 1)
if [ -z "$DEVICE_NAME" ]; then
    check_fail "找不到 Scarlett Pro Audio 實體輸出設備" "Pro Audio 模式可能未正確啟用，請執行 ./setup_pipewire_routing_v5.sh"
else
    check_ok "找到實體輸出設備: $DEVICE_NAME"
    declare -a LINKS_TO_CHECK
    LINKS_TO_CHECK=(
        "Scarlett_1-2:monitor_FL $DEVICE_NAME:playback_FL"
        "Scarlett_1-2:monitor_FR $DEVICE_NAME:playback_FR"
        "Scarlett_3-4:monitor_FL $DEVICE_NAME:playback_RL"
        "Scarlett_3-4:monitor_FR $DEVICE_NAME:playback_RR"
    )
    ALL_LINKS_OK=true
    for link_pair in "${LINKS_TO_CHECK[@]}"; do
        src=$(echo "$link_pair" | awk '{print $1}')
        dst=$(echo "$link_pair" | awk '{print $2}')
        if pw-link -l | grep -q "$src" && pw-link -l | grep "$src" | grep -q "$dst"; then
            check_ok "路由正確: $src -> $dst"
        else
            check_fail "路由錯誤或缺失: $src -> $dst" "音訊路由不完整，請重新執行 ./setup_pipewire_routing_v5.sh"
            ALL_LINKS_OK=false
        fi
    done
fi


print_section "第四部分：專案環境檢查"

# 4.1 檢查 uv
if command -v uv &> /dev/null; then
    check_ok "'uv' 指令已安裝"
else
    check_fail "'uv' 指令不存在" "請安裝 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 4.2 檢查虛擬環境
if [ -d ".venv" ]; then
    check_ok "找到 '.venv' 虛擬環境目錄"
    # 簡單檢查一個關鍵套件
    if .venv/bin/pip list 2>/dev/null | grep -q 'gtts'; then
         check_ok "在 .venv 中找到關鍵套件 'gtts'"
    else
         check_warn "在 .venv 中未找到關鍵套件 'gtts'。建議執行 'uv pip install -r requirements.txt'"
    fi
else
    check_warn "找不到 '.venv' 虛擬環境目錄。建議執行 'uv venv' 和 'uv pip install -r requirements.txt'"
fi

# ==============================================================================
#                           最終診斷報告
# ==============================================================================
print_section "最終診斷報告"

if [ ${#FAILURES[@]} -eq 0 ]; then
    echo -e "${C_GREEN}恭喜！所有關鍵檢查點均已通過。您的專業音訊環境設定看起來非常健康。${C_NC}"
else
    echo -e "${C_RED}發現 ${#FAILURES[@]} 個問題。請參考以下建議來修復：${C_NC}"
    for (( i=0; i<${#FAILURES[@]}; i++ )); do
        echo -e "\n  ${C_YELLOW}問題 $((i+1)):${C_NC}"
        echo -e "    ${FAILURES[$i]}"
    done
    echo -e "\n修復問題後，請重新執行此診斷腳本以確認。 "
fi
echo ""
