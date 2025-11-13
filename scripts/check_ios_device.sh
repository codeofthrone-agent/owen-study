#!/bin/bash

"""
iOS 設備檢查腳本

此腳本用於檢查 iOS 設備連接狀態，獲取設備資訊，並驗證測試環境。

Usage:
    ./check_ios_device.sh [--verbose] [--json]

Options:
    --verbose, -v    顯示詳細資訊
    --json, -j       以 JSON 格式輸出設備資訊
    --help, -h       顯示此說明

Author: Robot Framework Team
Date: 2025-06-27
"""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設設定
VERBOSE=false
JSON_OUTPUT=false

# 函式：顯示說明
show_help() {
    echo -e "${BLUE}iOS 設備檢查腳本${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose    顯示詳細資訊"
    echo "  -j, --json       以 JSON 格式輸出設備資訊"
    echo "  -h, --help       顯示此說明"
    echo ""
    echo "此腳本會檢查:"
    echo "  • iOS 設備連接狀態"
    echo "  • 設備基本資訊 (名稱、iOS 版本、UDID)"
    echo "  • libimobiledevice 工具可用性"
    echo "  • usbmuxd 服務狀態"
    echo ""
}

# 函式：詳細日誌
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[詳細]${NC} $1"
    fi
}

# 函式：錯誤訊息
log_error() {
    echo -e "${RED}[錯誤]${NC} $1" >&2
}

# 函式：成功訊息
log_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

# 函式：警告訊息
log_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

# 函式：資訊訊息
log_info() {
    echo -e "${BLUE}[資訊]${NC} $1"
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -j|--json)
                JSON_OUTPUT=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知選項: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 函式：檢查必要工具
check_required_tools() {
    log_verbose "檢查必要工具..."
    
    local tools=("idevice_id" "ideviceinfo" "idevicename")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        log_info "請安裝 libimobiledevice-utils:"
        echo "  sudo apt install -y libimobiledevice-utils"
        return 1
    fi
    
    log_verbose "所有必要工具都已安裝 ✅"
    return 0
}

# 函式：檢查 usbmuxd 服務
check_usbmuxd_service() {
    log_verbose "檢查 usbmuxd 服務狀態..."
    
    if systemctl is-active --quiet usbmuxd; then
        log_verbose "usbmuxd 服務正在執行 ✅"
        return 0
    else
        log_warning "usbmuxd 服務未執行"
        log_info "嘗試啟動 usbmuxd 服務..."
        
        if sudo systemctl start usbmuxd; then
            log_success "usbmuxd 服務已啟動"
            return 0
        else
            log_error "無法啟動 usbmuxd 服務"
            return 1
        fi
    fi
}

# 函式：獲取設備列表
get_device_list() {
    log_verbose "獲取 iOS 設備列表..."
    
    local devices
    devices=$(idevice_id -l 2>/dev/null)
    
    if [ $? -ne 0 ] || [ -z "$devices" ]; then
        return 1
    fi
    
    echo "$devices"
    return 0
}

# 函式：獲取設備詳細資訊
get_device_info() {
    local udid=$1
    local device_info=()
    
    log_verbose "獲取設備 $udid 的詳細資訊..."
    
    # 獲取基本資訊
    local device_name
    local product_version
    local product_type
    local serial_number
    
    device_name=$(ideviceinfo -u "$udid" -k DeviceName 2>/dev/null || echo "未知")
    product_version=$(ideviceinfo -u "$udid" -k ProductVersion 2>/dev/null || echo "未知")
    product_type=$(ideviceinfo -u "$udid" -k ProductType 2>/dev/null || echo "未知")
    serial_number=$(ideviceinfo -u "$udid" -k SerialNumber 2>/dev/null || echo "未知")
    
    if [ "$JSON_OUTPUT" = true ]; then
        cat << EOF
{
  "udid": "$udid",
  "deviceName": "$device_name",
  "productVersion": "$product_version",
  "productType": "$product_type",
  "serialNumber": "$serial_number"
}
EOF
    else
        echo "  UDID: $udid"
        echo "  設備名稱: $device_name"
        echo "  iOS 版本: $product_version"
        echo "  產品型號: $product_type"
        echo "  序列號: $serial_number"
    fi
}

# 函式：檢查設備開發者模式
check_developer_mode() {
    local udid=$1
    
    log_verbose "檢查設備 $udid 的開發者模式..."
    
    # 嘗試獲取開發者模式狀態（此功能可能需要設備解鎖）
    local dev_mode
    dev_mode=$(ideviceinfo -u "$udid" -k DeveloperModeStatus 2>/dev/null)
    
    if [ -n "$dev_mode" ]; then
        if [ "$dev_mode" = "true" ]; then
            log_success "開發者模式已啟用"
        else
            log_warning "開發者模式未啟用"
            log_info "請在設備上啟用開發者模式: 設定 > 隱私權與安全性 > 開發者模式"
        fi
    else
        log_info "無法檢查開發者模式狀態（設備可能已鎖定）"
    fi
}

# 函式：提供疑難排解建議
provide_troubleshooting() {
    log_info "疑難排解建議:"
    echo ""
    echo "1. 確認設備已連接並解鎖"
    echo "2. 在設備上點選「信任這部電腦」"
    echo "3. 確認 USB 傳輸線功能正常"
    echo "4. 嘗試重新啟動 usbmuxd 服務:"
    echo "   sudo systemctl restart usbmuxd"
    echo "5. 檢查 USB 連接："
    echo "   lsusb | grep Apple"
    echo "6. 確認設備已啟用開發者模式"
    echo ""
}

# 主函式
main() {
    parse_args "$@"
    
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}=== iOS 設備檢查 ===${NC}"
        echo ""
    fi
    
    # 檢查必要工具
    if ! check_required_tools; then
        exit 1
    fi
    
    # 檢查 usbmuxd 服務
    if ! check_usbmuxd_service; then
        log_error "usbmuxd 服務檢查失敗"
    fi
    
    # 獲取設備列表
    local devices
    if ! devices=$(get_device_list); then
        log_warning "未檢測到 iOS 設備"
        
        if [ "$JSON_OUTPUT" = true ]; then
            echo '{"devices": [], "status": "no_devices"}'
        else
            provide_troubleshooting
        fi
        exit 1
    fi
    
    # 處理檢測到的設備
    local device_count=0
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo '{"devices": ['
    else
        log_success "檢測到 iOS 設備:"
        echo ""
    fi
    
    local first_device=true
    
    while IFS= read -r udid; do
        if [ -n "$udid" ]; then
            device_count=$((device_count + 1))
            
            if [ "$JSON_OUTPUT" = true ]; then
                if [ "$first_device" = false ]; then
                    echo ","
                fi
                get_device_info "$udid"
                first_device=false
            else
                echo "設備 #$device_count:"
                get_device_info "$udid"
                
                # 檢查開發者模式
                check_developer_mode "$udid"
                echo ""
            fi
        fi
    done <<< "$devices"
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo '], "status": "success", "deviceCount": '$device_count'}'
    else
        echo ""
        log_success "iOS 設備檢查完成 ✅"
        log_info "總共檢測到 $device_count 個設備"
        
        if [ $device_count -gt 0 ]; then
            echo ""
            log_info "您現在可以執行 iOS 測試:"
            echo "  robot --variable PLATFORM:ios tests/mobile/ios/ios_app_test.robot"
        fi
    fi
}

# 執行主函式
main "$@"
