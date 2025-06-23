#!/bin/bash

"""
Appium 伺服器啟動腳本

此腳本用於啟動 Appium 伺服器，並進行基本的環境檢查。
支援後台執行模式和前景除錯模式。

Usage:
    ./start_appium.sh [--background] [--port=4723] [--host=localhost]

Options:
    --background, -b    在背景執行 Appium 伺服器
    --port, -p         指定 Appium 伺服器埠號（預設: 4723）
    --host, -h         指定 Appium 伺服器主機（預設: localhost）
    --debug, -d        啟用除錯模式
    --help             顯示此說明

Author: Robot Framework Team
Date: 2025-06-23
"""

# 預設設定
APPIUM_HOST="localhost"
APPIUM_PORT="4723"
BACKGROUND_MODE=false
DEBUG_MODE=false
APPIUM_LOG_FILE="logs/appium.log"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函式：顯示說明
show_help() {
    echo -e "${BLUE}Appium 伺服器啟動腳本${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -b, --background    在背景執行 Appium 伺服器"
    echo "  -p, --port PORT     指定埠號（預設: 4723）"
    echo "  -h, --host HOST     指定主機（預設: localhost）"
    echo "  -d, --debug         啟用除錯模式"
    echo "  --help              顯示此說明"
    echo ""
    echo "Examples:"
    echo "  $0                              # 在前景啟動 Appium"
    echo "  $0 --background                 # 在背景啟動 Appium"
    echo "  $0 --port=4724 --debug          # 在埠號 4724 啟動並啟用除錯"
}

# 函式：記錄訊息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函式：檢查必要工具
check_prerequisites() {
    log_info "檢查必要工具..."
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安裝。請先安裝 Node.js"
        return 1
    fi
    
    # 檢查 Appium
    if ! command -v appium &> /dev/null; then
        log_error "Appium 未安裝。請執行: npm install -g appium"
        return 1
    fi
    
    # 檢查 Android SDK（可選）
    if [[ -z "$ANDROID_HOME" ]]; then
        log_warn "ANDROID_HOME 環境變數未設定，Android 測試可能無法執行"
    fi
    
    # 檢查 iOS 環境（僅在 macOS）
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v xcodebuild &> /dev/null; then
            log_warn "Xcode 未安裝，iOS 測試可能無法執行"
        fi
    fi
    
    log_info "必要工具檢查完成"
    return 0
}

# 函式：檢查埠號是否被佔用
check_port() {
    if lsof -Pi :$APPIUM_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "埠號 $APPIUM_PORT 已被佔用"
        log_info "您可以："
        log_info "1. 使用不同埠號: $0 --port=4724"
        log_info "2. 停止佔用埠號的程序: kill \$(lsof -t -i:$APPIUM_PORT)"
        return 1
    fi
    return 0
}

# 函式：建立必要目錄
create_directories() {
    mkdir -p logs
    mkdir -p output/screenshots
    log_info "已建立必要目錄"
}

# 函式：啟動 Appium 伺服器
start_appium() {
    local appium_cmd="appium --address $APPIUM_HOST --port $APPIUM_PORT"
    
    if [[ "$DEBUG_MODE" == true ]]; then
        appium_cmd="$appium_cmd --log-level debug"
    fi
    
    if [[ "$BACKGROUND_MODE" == true ]]; then
        log_info "在背景啟動 Appium 伺服器..."
        log_info "主機: $APPIUM_HOST, 埠號: $APPIUM_PORT"
        log_info "日誌檔案: $APPIUM_LOG_FILE"
        
        nohup $appium_cmd > "$APPIUM_LOG_FILE" 2>&1 &
        local pid=$!
        echo $pid > logs/appium.pid
        
        # 等待伺服器啟動
        sleep 3
        
        # 檢查程序是否仍在執行
        if kill -0 $pid 2>/dev/null; then
            log_info "Appium 伺服器已啟動 (PID: $pid)"
            log_info "要停止伺服器，請執行: ./stop_appium.sh"
        else
            log_error "Appium 伺服器啟動失敗，請檢查日誌: $APPIUM_LOG_FILE"
            return 1
        fi
    else
        log_info "在前景啟動 Appium 伺服器..."
        log_info "主機: $APPIUM_HOST, 埠號: $APPIUM_PORT"
        log_info "按 Ctrl+C 停止伺服器"
        
        exec $appium_cmd
    fi
}

# 解析命令列參數
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--background)
            BACKGROUND_MODE=true
            shift
            ;;
        -p|--port)
            APPIUM_PORT="$2"
            shift 2
            ;;
        --port=*)
            APPIUM_PORT="${1#*=}"
            shift
            ;;
        -h|--host)
            APPIUM_HOST="$2"
            shift 2
            ;;
        --host=*)
            APPIUM_HOST="${1#*=}"
            shift
            ;;
        -d|--debug)
            DEBUG_MODE=true
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

# 主要執行流程
main() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}    Appium 伺服器啟動腳本${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    
    # 檢查必要工具
    if ! check_prerequisites; then
        exit 1
    fi
    
    # 檢查埠號
    if ! check_port; then
        exit 1
    fi
    
    # 建立必要目錄
    create_directories
    
    # 啟動 Appium
    start_appium
}

# 捕捉中斷信號
trap 'log_info "收到中斷信號，正在停止 Appium 伺服器..."; exit 0' INT TERM

# 執行主函式
main
