#!/bin/bash
"""
Android 測試環境設置腳本
此腳本用於一鍵式設置 Android 測試環境，包含環境檢查、工具安裝和配置驗證。
支援 Ubuntu 24.04 系統的完整 Android 自動化測試環境設置。

Usage:
    ./setup_android_testing.sh [options]

Options:
    --install-deps, -i     自動安裝所需依賴
    --verify-only, -v      僅驗證環境，不安裝
    --help, -h             顯示此說明

Author: Robot Framework Team
Date: 2025-07-10
"""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設設定
INSTALL_DEPS=false
VERIFY_ONLY=false
VERBOSE=false

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# 顯示使用說明
show_help() {
    echo "Android 測試環境設置腳本"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --install-deps, -i     自動安裝所需依賴"
    echo "  --verify-only, -v      僅驗證環境，不安裝"
    echo "  --verbose              顯示詳細輸出"
    echo "  --help, -h             顯示此說明"
    echo ""
    echo "Examples:"
    echo "  $0 --install-deps      # 自動安裝並設置環境"
    echo "  $0 --verify-only       # 僅驗證現有環境"
    echo "  $0 --verbose          # 顯示詳細安裝過程"
    echo ""
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps|-i)
                INSTALL_DEPS=true
                shift
                ;;
            --verify-only|-v)
                VERIFY_ONLY=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知參數: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 檢查作業系統
check_os() {
    log_step "檢查作業系統..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        local distro=$(lsb_release -si 2>/dev/null || echo "Unknown")
        local version=$(lsb_release -sr 2>/dev/null || echo "Unknown")
        log_success "檢測到作業系統: $distro $version"
        
        if [[ "$distro" != "Ubuntu" ]]; then
            log_warn "此腳本主要針對 Ubuntu 系統設計"
        fi
    else
        log_error "不支援的作業系統: $OSTYPE"
        log_error "此腳本僅支援 Linux 系統"
        return 1
    fi
}

# 檢查 Java 環境
check_java() {
    log_step "檢查 Java 環境..."
    if command -v java >/dev/null 2>&1; then
        local java_version=$(java -version 2>&1 | head -n1 | cut -d '"' -f2)
        log_success "Java 版本: $java_version"
        
        if [[ -n "$JAVA_HOME" ]]; then
            log_success "JAVA_HOME: $JAVA_HOME"
        else
            log_warn "JAVA_HOME 環境變數未設定"
        fi
    else
        if [ "$INSTALL_DEPS" = true ]; then
            log_verbose "安裝 OpenJDK..."
            sudo apt update
            sudo apt install -y openjdk-11-jdk
            
            # 設定 JAVA_HOME
            local java_home="/usr/lib/jvm/java-11-openjdk-amd64"
            if [[ -d "$java_home" ]]; then
                export JAVA_HOME="$java_home"
                echo "export JAVA_HOME=\"$java_home\"" >> ~/.bashrc
                log_success "Java 安裝完成，JAVA_HOME 設定為: $java_home"
            fi
        else
            log_error "Java 未安裝"
            return 1
        fi
    fi
}

# 檢查 Android SDK
check_android_sdk() {
    log_step "檢查 Android SDK..."
    
    # 檢查 ADB
    if command -v adb >/dev/null 2>&1; then
        local adb_version=$(adb version 2>&1 | head -n1)
        log_success "ADB 已安裝: $adb_version"
    else
        if [ "$INSTALL_DEPS" = true ]; then
            log_verbose "安裝 Android SDK 工具..."
            sudo apt update
            sudo apt install -y android-sdk-platform-tools
            log_success "Android SDK 工具安裝完成"
        else
            log_error "ADB 未安裝"
            return 1
        fi
    fi
    
    # 檢查環境變數
    if [[ -n "$ANDROID_HOME" ]]; then
        log_success "ANDROID_HOME: $ANDROID_HOME"
    else
        log_warn "ANDROID_HOME 環境變數未設定"
        if [ "$INSTALL_DEPS" = true ]; then
            local android_home="/usr/lib/android-sdk"
            if [[ -d "$android_home" ]]; then
                export ANDROID_HOME="$android_home"
                echo "export ANDROID_HOME=\"$android_home\"" >> ~/.bashrc
                echo "export PATH=\"\$PATH:\$ANDROID_HOME/platform-tools\"" >> ~/.bashrc
                log_success "ANDROID_HOME 設定為: $android_home"
            fi
        fi
    fi
}

# 檢查 Appium 環境
check_appium() {
    log_step "檢查 Appium 環境..."
    if command -v appium >/dev/null 2>&1; then
        local appium_version=$(appium --version 2>/dev/null | head -n1)
        log_success "Appium 已安裝: $appium_version"
        
        # 檢查 uiautomator2 驅動
        log_verbose "檢查 uiautomator2 驅動..."
        if appium driver list 2>/dev/null | grep -q "uiautomator2.*installed"; then
            log_success "uiautomator2 驅動已安裝"
        else
            if [ "$INSTALL_DEPS" = true ]; then
                log_verbose "安裝 uiautomator2 驅動..."
                appium driver install uiautomator2
                log_success "uiautomator2 驅動安裝完成"
            else
                log_error "uiautomator2 驅動未安裝"
                return 1
            fi
        fi
    else
        log_error "Appium 未安裝"
        return 1
    fi
}

# 檢查 Python 環境
check_python_env() {
    log_step "檢查 Python 環境..."
    
    # 檢查專案目錄
    local project_root="/home/thortron/Tools/robot-multiplatform-automation"
    if [[ ! -d "$project_root" ]]; then
        log_error "專案目錄不存在: $project_root"
        return 1
    fi
    
    cd "$project_root"
    
    # 檢查虛擬環境
    if [[ -d ".venv" ]]; then
        log_success "虛擬環境已存在"
        
        # 檢查 Appium Python 客戶端
        if .venv/bin/python3 -c "import appium" 2>/dev/null; then
            log_success "Appium Python 客戶端已安裝"
        else
            if [ "$INSTALL_DEPS" = true ]; then
                log_verbose "安裝 Appium Python 客戶端..."
                .venv/bin/pip install Appium-Python-Client
                log_success "Appium Python 客戶端安裝完成"
            else
                log_error "Appium Python 客戶端未安裝"
                return 1
            fi
        fi
    else
        log_error "虛擬環境不存在"
        return 1
    fi
}

# 測試 Android 設備連接
test_android_connection() {
    log_step "測試 Android 設備連接..."
    
    # 檢查 ADB 服務
    if timeout 5 adb devices >/dev/null 2>&1; then
        local devices=$(timeout 5 adb devices 2>/dev/null | grep -v "List of devices" | grep -v "^$" | wc -l)
        if [[ "$devices" -gt 0 ]]; then
            log_success "檢測到 $devices 個 Android 設備"
            timeout 5 adb devices 2>/dev/null | grep -v "List of devices" | grep -v "^$"
        else
            log_warn "未檢測到 Android 設備"
            log_info "請確認："
            log_info "  1. Android 設備已連接並開啟 USB 除錯"
            log_info "  2. 設備已信任此電腦"
            log_info "  3. 設備驅動程式已正確安裝"
        fi
    else
        log_error "ADB 服務無法啟動"
        return 1
    fi
}

# 測試 Appium 伺服器
test_appium_server() {
    log_step "測試 Appium 伺服器..."
    
    # 檢查 Appium 伺服器是否正在運行
    if curl -s http://localhost:4723/wd/hub/status >/dev/null 2>&1; then
        log_success "Appium 伺服器正在運行"
        local server_info=$(curl -s http://localhost:4723/wd/hub/status | jq -r '.value.build.version' 2>/dev/null || echo "Unknown")
        log_info "伺服器版本: $server_info"
    else
        log_warn "Appium 伺服器未運行"
        log_info "可使用以下命令啟動："
        log_info "  ./scripts/start_appium.sh --background"
    fi
}

# 驗證配置文件
verify_configuration() {
    log_step "驗證配置文件..."
    
    local project_root="/home/thortron/Tools/robot-multiplatform-automation"
    cd "$project_root"
    
    # 檢查 Android 配置
    if [[ -f "config/mobile/appium_config.py" ]]; then
        log_success "Android 配置文件存在"
        
        # 測試配置載入
        if timeout 10 .venv/bin/python3 -c "
import sys
sys.path.insert(0, '.')
from config.mobile.appium_config import appium_config
android_caps = appium_config.get_capability('android')
print('Android 配置載入成功')
" 2>/dev/null; then
            log_success "Android 配置載入測試通過"
        else
            log_error "Android 配置載入測試失敗"
            return 1
        fi
    else
        log_error "Android 配置文件不存在"
        return 1
    fi
}

# 生成環境報告
generate_report() {
    log_step "生成環境報告..."
    
    local report_file="results/android_environment_report.md"
    local project_root="/home/thortron/Tools/robot-multiplatform-automation"
    cd "$project_root"
    
    mkdir -p results
    
    cat > "$report_file" << EOF
# Android 測試環境設置報告

## 環境資訊
- **作業系統**: $(lsb_release -d | cut -f2 2>/dev/null || echo "Unknown")
- **檢查時間**: $(date '+%Y-%m-%d %H:%M:%S')
- **Java 版本**: $(java -version 2>&1 | head -n1 | cut -d '"' -f2 2>/dev/null || echo "未安裝")
- **Android SDK**: $(adb version 2>&1 | head -n1 2>/dev/null || echo "未安裝")
- **Appium 版本**: $(appium --version 2>/dev/null || echo "未安裝")

## 環境變數
- **JAVA_HOME**: ${JAVA_HOME:-"未設定"}
- **ANDROID_HOME**: ${ANDROID_HOME:-"未設定"}

## 連接設備
EOF
    
    if timeout 5 adb devices >/dev/null 2>&1; then
        echo "### Android 設備列表" >> "$report_file"
        echo '```' >> "$report_file"
        timeout 5 adb devices 2>/dev/null >> "$report_file"
        echo '```' >> "$report_file"
    else
        echo "### Android 設備列表" >> "$report_file"
        echo "無法獲取設備列表" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## Appium 驅動程式" >> "$report_file"
    echo '```' >> "$report_file"
    timeout 10 appium driver list 2>/dev/null >> "$report_file" || echo "無法獲取驅動列表" >> "$report_file"
    echo '```' >> "$report_file"
    
    log_success "環境報告已生成: $report_file"
}

# 主函數
main() {
    echo "========================================"
    echo "Android 測試環境設置腳本"
    echo "========================================"
    echo ""
    
    parse_args "$@"
    
    # 執行檢查
    check_os || exit 1
    check_java || exit 1
    check_android_sdk || exit 1
    check_appium || exit 1
    check_python_env || exit 1
    
    # 測試連接
    test_android_connection
    test_appium_server
    
    # 驗證配置
    verify_configuration || exit 1
    
    # 生成報告
    generate_report
    
    echo ""
    echo "========================================"
    log_success "Android 測試環境設置完成！"
    echo "========================================"
    echo ""
    
    if [ "$VERIFY_ONLY" = false ]; then
        log_info "後續步驟："
        log_info "1. 連接 Android 設備並開啟 USB 除錯"
        log_info "2. 啟動 Appium 伺服器: ./scripts/start_appium.sh --background"
        log_info "3. 執行 Android 測試: uv run robot tests/mobile/android/"
    fi
}

# 執行主函數
main "$@"
