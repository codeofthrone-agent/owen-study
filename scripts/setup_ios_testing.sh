#!/bin/bash

"""
iOS 測試環境完整設置腳本

此腳本提供一鍵式 iOS 測試環境設置，包括：
- 系統依賴檢查和安裝
- Appium 和驅動程式安裝
- Python 套件安裝
- iOS 設備檢測和驗證
- 測試環境驗證

Usage:
    ./setup_ios_testing.sh [--install-deps] [--verify-only] [--verbose]

Options:
    --install-deps    自動安裝缺少的系統依賴
    --verify-only     僅驗證現有環境，不進行安裝
    --verbose         顯示詳細輸出
    --help           顯示此說明

Author: Robot Framework Team
Date: 2025-06-27
"""

# 設定和顏色定義
set -e  # 遇到錯誤立即退出

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 預設設定
INSTALL_DEPS=false
VERIFY_ONLY=false
VERBOSE=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 日誌函式
log_info() {
    echo -e "${BLUE}[資訊]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[錯誤]${NC} $1" >&2
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[詳細]${NC} $1"
    fi
}

log_step() {
    echo -e "${PURPLE}[步驟]${NC} $1"
}

# 顯示說明
show_help() {
    echo -e "${BLUE}iOS 測試環境設置腳本${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --install-deps    自動安裝缺少的系統依賴"
    echo "  --verify-only     僅驗證現有環境，不進行安裝"
    echo "  --verbose         顯示詳細輸出"
    echo "  --help           顯示此說明"
    echo ""
    echo "此腳本將："
    echo "  1. 檢查系統需求和依賴"
    echo "  2. 安裝 Node.js、Appium 和相關工具"
    echo "  3. 配置 Python 環境和套件"
    echo "  4. 檢測和驗證 iOS 設備"
    echo "  5. 執行完整環境測試"
    echo ""
    echo "系統需求："
    echo "  - Ubuntu 24.04 LTS"
    echo "  - Python 3.8+"
    echo "  - 至少 8GB RAM"
    echo "  - 10GB 可用儲存空間"
    echo ""
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                INSTALL_DEPS=true
                shift
                ;;
            --verify-only)
                VERIFY_ONLY=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
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

# 檢查是否為 Ubuntu 24.04
check_system_requirements() {
    log_step "檢查系統需求..."
    
    # 檢查作業系統
    if [ ! -f /etc/os-release ]; then
        log_error "無法確定作業系統版本"
        return 1
    fi
    
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        log_warning "此腳本主要針對 Ubuntu 系統設計，當前系統: $ID"
    elif [ "$VERSION_ID" != "24.04" ]; then
        log_warning "此腳本針對 Ubuntu 24.04 設計，當前版本: $VERSION_ID"
    else
        log_success "系統版本檢查通過: Ubuntu $VERSION_ID"
    fi
    
    # 檢查記憶體
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$mem_gb" -lt 8 ]; then
        log_warning "建議至少 8GB RAM，當前: ${mem_gb}GB"
    else
        log_success "記憶體檢查通過: ${mem_gb}GB"
    fi
    
    # 檢查磁碟空間
    local disk_gb=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_gb" -lt 10 ]; then
        log_warning "建議至少 10GB 可用空間，當前: ${disk_gb}GB"
    else
        log_success "磁碟空間檢查通過: ${disk_gb}GB 可用"
    fi
}

# 檢查和安裝系統依賴
install_system_dependencies() {
    if [ "$VERIFY_ONLY" = true ]; then
        log_verbose "略過系統依賴安裝（僅驗證模式）"
        return 0
    fi
    
    log_step "檢查和安裝系統依賴..."
    
    # 更新套件列表
    log_verbose "更新套件列表..."
    sudo apt update -qq
    
    # 必要的基礎套件
    local base_packages=(
        "curl" "wget" "git" "build-essential"
        "python3" "python3-pip" "python3-venv"
    )
    
    # iOS 相關套件
    local ios_packages=(
        "libimobiledevice-utils" "usbmuxd" 
        "libgtk-3-dev" "libnotify-dev" 
        "libnss3" "libxss1" "libasound2t64"
    )
    
    local all_packages=("${base_packages[@]}" "${ios_packages[@]}")
    
    if [ "$INSTALL_DEPS" = true ]; then
        log_verbose "安裝系統套件: ${all_packages[*]}"
        sudo apt install -y "${all_packages[@]}"
        log_success "系統依賴安裝完成"
    else
        # 僅檢查套件是否已安裝
        local missing_packages=()
        for package in "${all_packages[@]}"; do
            if ! dpkg -l | grep -q "^ii  $package "; then
                missing_packages+=("$package")
            fi
        done
        
        if [ ${#missing_packages[@]} -ne 0 ]; then
            log_warning "缺少系統套件: ${missing_packages[*]}"
            log_info "執行 '$0 --install-deps' 來安裝缺少的套件"
            return 1
        else
            log_success "所有系統依賴已安裝"
        fi
    fi
}

# 檢查和安裝 Node.js
install_nodejs() {
    if [ "$VERIFY_ONLY" = true ]; then
        log_verbose "略過 Node.js 安裝（僅驗證模式）"
        return 0
    fi
    
    log_step "檢查 Node.js 安裝..."
    
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        log_success "Node.js 已安裝: $node_version"
        
        # 檢查版本是否符合需求 (v18+)
        local major_version=$(echo "$node_version" | sed 's/v\([0-9]*\).*/\1/')
        if [ "$major_version" -lt 18 ]; then
            log_warning "建議使用 Node.js 18.x 或更高版本，當前: $node_version"
        fi
    else
        if [ "$INSTALL_DEPS" = true ]; then
            log_verbose "安裝 Node.js..."
            sudo apt install -y nodejs npm
            log_success "Node.js 安裝完成"
        else
            log_error "Node.js 未安裝"
            return 1
        fi
    fi
    
    # 檢查 npm
    if ! command -v npm >/dev/null 2>&1; then
        log_error "npm 未安裝"
        return 1
    fi
    
    local npm_version=$(npm --version)
    log_success "npm 版本: $npm_version"
}

# 檢查和安裝 Appium
install_appium() {
    if [ "$VERIFY_ONLY" = true ]; then
        log_verbose "略過 Appium 安裝（僅驗證模式）"
        return 0
    fi
    
    log_step "檢查 Appium 安裝..."
    
    if command -v appium >/dev/null 2>&1; then
        local appium_version=$(appium --version 2>/dev/null | head -n1)
        log_success "Appium 已安裝: $appium_version"
    else
        if [ "$INSTALL_DEPS" = true ]; then
            log_verbose "全域安裝 Appium..."
            sudo npm install -g appium@next
            log_success "Appium 安裝完成"
        else
            log_error "Appium 未安裝"
            return 1
        fi
    fi
    
    # 檢查 XCUITest 驅動
    log_verbose "檢查 XCUITest 驅動..."
    if appium driver list 2>/dev/null | grep -q "xcuitest.*installed"; then
        log_success "XCUITest 驅動已安裝"
    else
        if [ "$INSTALL_DEPS" = true ]; then
            log_verbose "安裝 XCUITest 驅動..."
            appium driver install xcuitest
            log_success "XCUITest 驅動安裝完成"
        else
            log_error "XCUITest 驅動未安裝"
            return 1
        fi
    fi
}

# 設置 Python 環境
setup_python_environment() {
    if [ "$VERIFY_ONLY" = true ]; then
        log_verbose "略過 Python 環境設置（僅驗證模式）"
        return 0
    fi
    
    log_step "設置 Python 環境..."
    
    cd "$PROJECT_ROOT"
    
    # 檢查虛擬環境
    if [ -d ".venv" ]; then
        log_success "Python 虛擬環境已存在"
    else
        log_verbose "建立 Python 虛擬環境..."
        python3 -m venv .venv
        log_success "Python 虛擬環境建立完成"
    fi
    
    # 啟動虛擬環境
    source .venv/bin/activate
    
    # 升級 pip
    log_verbose "升級 pip..."
    pip install --upgrade pip
    
    # 安裝必要的 Python 套件
    local python_packages=(
        "robotframework>=6.0"
        "Appium-Python-Client>=3.0.0"
        "robotframework-appiumlibrary"
        "selenium>=4.0.0"
    )
    
    log_verbose "安裝 Python 套件: ${python_packages[*]}"
    pip install "${python_packages[@]}"
    
    log_success "Python 環境設置完成"
}

# 驗證 iOS 工具
verify_ios_tools() {
    log_step "驗證 iOS 工具..."
    
    # 檢查 libimobiledevice 工具
    local ios_tools=("idevice_id" "ideviceinfo" "idevicename")
    local missing_tools=()
    
    for tool in "${ios_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少 iOS 工具: ${missing_tools[*]}"
        log_info "執行 'sudo apt install libimobiledevice-utils' 來安裝"
        return 1
    fi
    
    log_success "所有 iOS 工具已安裝"
    
    # 檢查 usbmuxd 服務
    if systemctl is-active --quiet usbmuxd; then
        log_success "usbmuxd 服務正在執行"
    else
        log_warning "usbmuxd 服務未執行，嘗試啟動..."
        if sudo systemctl start usbmuxd; then
            log_success "usbmuxd 服務已啟動"
        else
            log_error "無法啟動 usbmuxd 服務"
            return 1
        fi
    fi
}

# 檢測 iOS 設備
detect_ios_devices() {
    log_step "檢測 iOS 設備..."
    
    # 使用專用的設備檢查腳本
    local device_check_script="$SCRIPT_DIR/check_ios_device.sh"
    
    if [ -f "$device_check_script" ]; then
        log_verbose "使用設備檢查腳本: $device_check_script"
        
        if "$device_check_script" --verbose; then
            log_success "iOS 設備檢測完成"
        else
            log_warning "未檢測到 iOS 設備或設備檢查失敗"
            log_info "請確認："
            echo "  1. iOS 設備已連接並解鎖"
            echo "  2. 在設備上點選「信任這部電腦」"
            echo "  3. 設備已啟用開發者模式"
            return 1
        fi
    else
        log_verbose "使用基本設備檢測..."
        
        local devices=$(idevice_id -l 2>/dev/null)
        if [ -z "$devices" ]; then
            log_warning "未檢測到 iOS 設備"
            return 1
        else
            log_success "檢測到 iOS 設備:"
            echo "$devices" | while read -r device; do
                if [ -n "$device" ]; then
                    echo "  - $device"
                fi
            done
        fi
    fi
}

# 執行完整測試
run_environment_test() {
    log_step "執行環境測試..."
    
    cd "$PROJECT_ROOT"
    
    # 啟動虛擬環境
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # 測試 Python 套件匯入
    log_verbose "測試 Python 套件匯入..."
    
    local test_imports=(
        "import robot"
        "import appium"
        "from AppiumLibrary import AppiumLibrary"
        "from config.mobile.appium_config import appium_config"
    )
    
    for import_test in "${test_imports[@]}"; do
        if python3 -c "$import_test" 2>/dev/null; then
            log_verbose "✅ $import_test"
        else
            log_error "❌ $import_test"
            return 1
        fi
    done
    
    log_success "Python 套件測試通過"
    
    # 測試 iOS 配置載入
    log_verbose "測試 iOS 配置載入..."
    
    if python3 -c "
from config.mobile.ios_config import ios_config, validate_ios_environment
result = validate_ios_environment()
print('iOS 環境驗證結果:', result)
" 2>/dev/null; then
        log_success "iOS 配置測試通過"
    else
        log_warning "iOS 配置測試失敗（可能是因為無設備連接）"
    fi
    
    # 測試 Robot Framework 語法
    log_verbose "測試 Robot Framework 語法..."
    
    local test_file="tests/mobile/ios/ios_real_device_test.robot"
    if [ -f "$test_file" ]; then
        if robot --dryrun --output NONE --report NONE --log NONE "$test_file" 2>/dev/null; then
            log_success "Robot Framework 語法測試通過"
        else
            log_error "Robot Framework 語法測試失敗"
            return 1
        fi
    else
        log_warning "測試檔案不存在: $test_file"
    fi
}

# 生成環境報告
generate_environment_report() {
    log_step "生成環境報告..."
    
    local report_file="$PROJECT_ROOT/results/ios_environment_report.txt"
    mkdir -p "$(dirname "$report_file")"
    
    {
        echo "iOS 測試環境報告"
        echo "================="
        echo "生成時間: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        
        echo "系統資訊:"
        echo "--------"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            echo "作業系統: $NAME $VERSION"
        fi
        echo "核心版本: $(uname -r)"
        echo "架構: $(uname -m)"
        echo "記憶體: $(free -h | awk '/^Mem:/{print $2}')"
        echo ""
        
        echo "軟體版本:"
        echo "--------"
        echo "Python: $(python3 --version 2>/dev/null || echo '未安裝')"
        echo "Node.js: $(node --version 2>/dev/null || echo '未安裝')"
        echo "npm: $(npm --version 2>/dev/null || echo '未安裝')"
        echo "Appium: $(appium --version 2>/dev/null | head -n1 || echo '未安裝')"
        echo ""
        
        echo "iOS 工具:"
        echo "--------"
        echo "idevice_id: $(command -v idevice_id >/dev/null && echo '已安裝' || echo '未安裝')"
        echo "ideviceinfo: $(command -v ideviceinfo >/dev/null && echo '已安裝' || echo '未安裝')"
        echo "usbmuxd: $(systemctl is-active usbmuxd 2>/dev/null || echo '未執行')"
        echo ""
        
        echo "Appium 驅動:"
        echo "----------"
        if command -v appium >/dev/null 2>&1; then
            appium driver list 2>/dev/null || echo "無法獲取驅動列表"
        else
            echo "Appium 未安裝"
        fi
        echo ""
        
        echo "iOS 設備:"
        echo "--------"
        local devices=$(idevice_id -l 2>/dev/null)
        if [ -n "$devices" ]; then
            echo "$devices"
        else
            echo "未檢測到設備"
        fi
        
    } > "$report_file"
    
    log_success "環境報告已生成: $report_file"
}

# 顯示完成摘要
show_completion_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  iOS 測試環境設置完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    echo -e "${BLUE}下一步操作:${NC}"
    echo ""
    
    echo "1. 連接 iOS 設備並確保："
    echo "   • 設備已解鎖"
    echo "   • 已信任此電腦"
    echo "   • 已啟用開發者模式"
    echo ""
    
    echo "2. 啟動 Appium 伺服器："
    echo "   ./scripts/start_appium.sh --background"
    echo ""
    
    echo "3. 檢查設備連接："
    echo "   ./scripts/check_ios_device.sh --verbose"
    echo ""
    
    echo "4. 執行測試："
    echo "   robot tests/mobile/ios/ios_real_device_test.robot"
    echo ""
    
    echo -e "${YELLOW}文檔和資源:${NC}"
    echo "• 設置指南: docs/ios_device_setup.md"
    echo "• 環境報告: results/ios_environment_report.txt"
    echo "• 疑難排解: 參考設置指南中的疑難排解章節"
    echo ""
}

# 主函式
main() {
    parse_args "$@"
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  iOS 測試環境設置腳本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # 檢查系統需求
    if ! check_system_requirements; then
        log_error "系統需求檢查失敗"
        exit 1
    fi
    
    # 安裝系統依賴
    if ! install_system_dependencies; then
        log_error "系統依賴檢查/安裝失敗"
        exit 1
    fi
    
    # 安裝 Node.js
    if ! install_nodejs; then
        log_error "Node.js 檢查/安裝失敗"
        exit 1
    fi
    
    # 安裝 Appium
    if ! install_appium; then
        log_error "Appium 檢查/安裝失敗"
        exit 1
    fi
    
    # 設置 Python 環境
    if ! setup_python_environment; then
        log_error "Python 環境設置失敗"
        exit 1
    fi
    
    # 驗證 iOS 工具
    if ! verify_ios_tools; then
        log_error "iOS 工具驗證失敗"
        exit 1
    fi
    
    # 檢測 iOS 設備（非必需，可能無設備連接）
    detect_ios_devices || log_warning "iOS 設備檢測失敗（可能無設備連接）"
    
    # 執行環境測試
    if ! run_environment_test; then
        log_error "環境測試失敗"
        exit 1
    fi
    
    # 生成環境報告
    generate_environment_report
    
    # 顯示完成摘要
    show_completion_summary
    
    log_success "iOS 測試環境設置腳本執行完成！"
}

# 執行主函式
main "$@"
