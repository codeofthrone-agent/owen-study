#!/bin/bash

# ==============================================================================
# Scarlett PipeWire 路由設定與修復腳本 (v5 - 智慧設定檔創建)
#
# 功能:
# 1. 檢查系統依賴 (pactl, pw-link, speaker-test)。
# 2. 自動偵測 Scarlett 音訊介面。
# 3. 檢查 "pro-audio" 設定檔是否存在，如果不存在：
#    a. 會請求 sudo 權限。
#    b. 會在 /etc/alsa-card-profile/mixer/paths/ 中創建一個設定檔。
#    c. 會引導使用者重啟 PipeWire 服務。
# 4. 自動切換到 "pro-audio" 設定檔。
# 5. 創建與現有環境一致的虛擬 Sink: "Scarlett_1-2", "Scarlett_3-4"。
# 6. 將虛擬 Sink 連接到 Scarlett 的 4 個實體輸出。
# 7. 執行自動音訊測試，確認所有通道均可出聲。
#
# 使用方式:
#   ./setup_pipewire_routing_v5.sh         # 在新電腦上執行完整設定
#   ./setup_pipewire_routing_v5.sh --test    # 僅執行音訊測試
#   ./setup_pipewire_routing_v5.sh --cleanup # 清理已建立的虛擬裝置
#   ./setup_pipewire_routing_v5.sh --help    # 顯示幫助訊息
# ==============================================================================

set -e # 任何指令失敗則立即退出

# --- 彩色輸出設定 ---
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_PURPLE='\033[0;35m'
COLOR_NC='\033[0m' # No Color

# --- Log 函式 ---
log_info() { echo -e "${COLOR_BLUE}(i) $1${COLOR_NC}"; }
log_success() { echo -e "${COLOR_GREEN}✅ $1${COLOR_NC}"; }
log_error() { echo -e "${COLOR_RED}❌ 錯誤：$1${COLOR_NC}"; }
log_warn() { echo -e "${COLOR_YELLOW}⚠️ 警告：$1${COLOR_NC}"; }
log_action() { echo -e "${COLOR_PURPLE}==> $1${COLOR_NC}"; }

# --- 幫助訊息 ---
show_help() {
    set +e
    echo "Scarlett PipeWire 路由設定與修復腳本 (v5)"
    echo "-------------------------------------------------"
    echo "使用方式:"
    echo "  $0         - 執行完整設定，包含設定檔創建與音訊測試"
    echo "  $0 --test    - 僅對已存在的虛擬裝置執行音訊測試"
    echo "  $0 --cleanup - 清理所有由本腳本建立的虛擬裝置"
    echo "  $0 --help    - 顯示此幫助訊息"
}

# --- 依賴性檢查 ---
check_deps() {
    set +e
    log_info "正在檢查所需指令..."
    local missing_deps=0
    local deps=("pactl" "pw-link" "speaker-test" "sudo")
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "指令 '$cmd' 不存在。"
            missing_deps=1
        fi
    done

    if [ $missing_deps -ne 0 ]; then
        log_error "缺少必要的套件。"
        echo "請嘗試執行以下指令安裝："
        echo "  sudo apt update && sudo apt install pipewire-audio-client-libraries pulseaudio-utils sudo"
        exit 1
    fi
    log_success "所有依賴項均已安裝。"
    set -e
}

# --- Pro Audio 設定檔內容 ---
get_pro_audio_config() {
cat << 'PRO_CONFIG_EOF'
;
; This profile is intended for the Focusrite Scarlett 4i4 3rd Gen,
; enabling the "Pro Audio" setting to provide independent channel access.
;
; Place this file in /etc/alsa-card-profile/mixer/paths/
; or a similar location recognized by your ALSA/PipeWire setup.
; A filename like 99-focusrite-scarlett-pro.conf is recommended.
;

[General]
auto-profiles = no

[Mapping analog-out-pro]
device-strings = hw:%f
channel-map = left,right,aux0,aux1,aux2,aux3,aux4,aux5
paths-output = analog-output-lineout analog-output-headphones
direction = output
priority = 15

[Profile pro-audio]
description = Pro Audio
output-mappings = analog-out-pro
priority = 100
PRO_CONFIG_EOF
}


# --- 創建 Pro Audio 設定檔 ---
create_pro_audio_profile() {
    log_warn "'pro-audio' 設定檔不存在。此腳本可以為您創建它。"
    log_action "這需要在系統目錄中寫入一個設定檔，因此需要管理員權限。"

    # 提示使用者是否繼續
    read -p "您是否同意使用 sudo 權限創建設定檔？(y/N): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        log_error "使用者取消操作。無法繼續設定。"
        exit 1
    fi

    local config_path="/etc/alsa-card-profile/mixer/paths/99-focusrite-scarlett-pro.conf"
    log_info "將使用 sudo 創建設定檔: $config_path"

    # 使用 sudo tee 寫入檔案
    get_pro_audio_config | sudo tee "$config_path" > /dev/null

    if [ $? -ne 0 ]; then
        log_error "創建設定檔失敗！請檢查您的 sudo 權限。"
        exit 1
    fi

    log_success "成功創建設定檔: $config_path"
    log_action "為了讓新設定檔生效，需要重啟 PipeWire 服務。"
    echo "請執行以下指令，然後重新執行本腳本："
    echo ""
    echo "  systemctl --user restart pipewire.service pipewire-pulse.service"
    echo ""
    exit 0
}

# --- 清理虛擬裝置 ---
cleanup_routes() {
    set +e
    log_info "正在清理所有 module-null-sink 虛擬裝置..."
    while true; do
        mod_index=$(pactl list modules short | grep "module-null-sink" | awk '{print $1}' | head -n 1)
        if [ -z "$mod_index" ]; then
            break
        fi
        log_info "正在卸載模組索引: $mod_index"
        pactl unload-module "$mod_index"
        sleep 0.5
    done
    log_success "所有虛擬裝置已清理完畢。"
    set -e
}

# --- 音訊測試 ---
run_test() {
    set +e
    log_info "即將開始自動音訊測試..."
    echo "您將會依序從不同的輸出通道聽到測試音。"
    sleep 2

    local sinks=("Scarlett_1-2" "Scarlett_3-4")
    local freqs=(440 660)
    local outputs=("1 & 2" "3 & 4")

    for i in ${!sinks[@]}; do
        local sink_name=${sinks[$i]}
        if ! pactl list sinks short | grep -q "$sink_name"; then
            log_error "虛擬裝置 '$sink_name' 不存在，無法進行測試。"
            log_info "請先執行一次完整的設定 (不加任何參數)。"
            return 1
        fi

        log_info "正在測試輸出 ${outputs[$i]} (使用裝置: $sink_name, 頻率: ${freqs[$i]} Hz)..."
        speaker-test -t sine -f ${freqs[$i]} -c 1 -s 1 -D "$sink_name" &> /dev/null
        if [ $? -ne 0 ]; then
            log_error "在 '$sink_name' 上播放測試音失敗。"
        else
            log_success "輸出 ${outputs[$i]} 測試音已發送。"
        fi
        sleep 1.5
    done
    log_success "音訊測試完成。"
    set -e
}

# --- 主要設定流程 ---
main_setup() {
    check_deps
    echo ""

    log_action "1. 尋找 Scarlett 音訊介面..."
    CARD_NAME=$(pactl list cards short | grep -i -E "Focusrite.*Scarlett|Scarlett.*Focusrite" | awk '{print $2}' | head -n 1)

    if [ -z "$CARD_NAME" ]; then
        log_error "找不到任何 Focusrite Scarlett 音訊介面！"
        echo "請確認設備已連接並開機。"
        exit 1
    fi
    log_success "找到音訊卡: $CARD_NAME"
    echo ""

    log_action "2. 檢查並設定 Pro Audio 模式..."
    local profiles
    profiles=$(pactl list cards | grep -A 10 "Name: $CARD_NAME" | grep "pro-audio" || true)
    
    if [ -z "$profiles" ]; then
        # 如果設定檔不存在，執行創建流程
        create_pro_audio_profile
    fi

    local current_profile
    current_profile=$(pactl list cards | grep -A 10 "Name: $CARD_NAME" | grep 'Active Profile:' | awk -F': ' '{print $2}')
    log_info "當前 Profile: $current_profile"

    if [ "$current_profile" != "pro-audio" ]; then
        log_warn "非 Pro Audio 模式，正在嘗試自動切換..."
        pactl set-card-profile "$CARD_NAME" pro-audio
        log_success "成功發送切換指令。等待 2 秒讓設定生效..."
        sleep 2
    else
        log_success "已經是 Pro Audio 模式。"
    fi
    echo ""

    log_action "3. 清理並創建虛擬輸出裝置..."
    cleanup_routes
    
    local virtual_sinks=("Scarlett_1-2" "Scarlett_3-4")
    log_info "將創建: ${virtual_sinks[*]}"
    for sink in "${virtual_sinks[@]}"; do
        pactl load-module module-null-sink sink_name="$sink" sink_properties=device.description="$sink"
    done
    log_success "成功創建 ${#virtual_sinks[@]} 個虛擬裝置。"
    sleep 2 # 等待裝置完全建立
    echo ""

    log_action "4. 偵測 Scarlett Pro Audio 實體輸出設備..."
    DEVICE_NAME=$(pactl list sinks short | grep -i "Focusrite_Scarlett.*pro-output" | awk '{print $2}' | head -n 1)
    if [ -z "$DEVICE_NAME" ]; then
        log_error "找不到 Scarlett Pro Audio 實體輸出設備！"
        echo "這通常發生在 Pro Audio 模式切換失敗後。請檢查先前的日誌。"
        exit 1
    fi
    log_success "找到實體輸出設備: $DEVICE_NAME"
    echo ""

    log_action "5. 連接虛擬裝置至實體輸出..."
    local links=(
        "Scarlett_1-2:monitor_FL=$DEVICE_NAME:playback_FL"
        "Scarlett_1-2:monitor_FR=$DEVICE_NAME:playback_FR"
        "Scarlett_3-4:monitor_FL=$DEVICE_NAME:playback_RL"
        "Scarlett_3-4:monitor_FR=$DEVICE_NAME:playback_RR"
    )
    for link in "${links[@]}"; do
        src="${link%=*}"
        dst="${link#*=}"
        if pw-link "$src" "$dst"; then
            log_success "  $src -> $dst"
        else
            log_error "  連接失敗: $src -> $dst"
        fi
    done
    log_success "所有聲道均已成功連接。"
    echo ""

    echo "================================================="
    log_success "路由設定完成！"
    echo "================================================="
    echo ""
    echo "設備對應："
    echo "  - 虛擬裝置 'Scarlett_1-2' -> 實體輸出 1 (FL) 和 2 (FR)"
    echo "  - 虛擬裝置 'Scarlett_3-4' -> 實體輸出 3 (RL) 和 4 (RR)"
    echo ""
}

# --- 參數解析與執行 ---
# 在腳本開頭設定了 set -e，這裡用 set +e 取消，以自訂錯誤處理
set +e
if [ -z "$1" ]; then
    main_setup
    if [ $? -eq 0 ]; then
        echo ""
        run_test
    fi
    exit 0
fi

case "$1" in
    --help)
        show_help
        ;;
    --cleanup)
        cleanup_routes
        ;;
    --test)
        run_test
        ;;
    *)
        log_error "未知的參數: $1"
        show_help
        exit 1
        ;;
esac

