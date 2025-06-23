#!/bin/bash

"""
Appium 伺服器停止腳本

此腳本用於停止正在執行的 Appium 伺服器。

Usage:
    ./stop_appium.sh [--force]

Options:
    --force, -f    強制停止所有 Appium 程序
    --help         顯示此說明

Author: Robot Framework Team
Date: 2025-06-23
"""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FORCE_MODE=false
PID_FILE="logs/appium.pid"

# 函式：顯示說明
show_help() {
    echo -e "${BLUE}Appium 伺服器停止腳本${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -f, --force    強制停止所有 Appium 程序"
    echo "  --help         顯示此說明"
    echo ""
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

# 函式：停止透過 PID 檔案記錄的 Appium
stop_appium_by_pid() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 "$pid" 2>/dev/null; then
            log_info "停止 Appium 程序 (PID: $pid)..."
            kill "$pid"
            
            # 等待程序停止
            for i in {1..10}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            # 檢查程序是否仍在執行
            if kill -0 "$pid" 2>/dev/null; then
                log_warn "程序仍在執行，強制停止..."
                kill -9 "$pid"
            fi
            
            log_info "Appium 程序已停止"
        else
            log_warn "PID 檔案中的程序 ($pid) 不存在"
        fi
        
        # 清理 PID 檔案
        rm -f "$PID_FILE"
    else
        log_warn "找不到 PID 檔案: $PID_FILE"
    fi
}

# 函式：強制停止所有 Appium 程序
force_stop_appium() {
    log_info "搜尋所有 Appium 程序..."
    
    local pids=$(pgrep -f "appium")
    
    if [[ -n "$pids" ]]; then
        log_info "找到 Appium 程序: $pids"
        
        for pid in $pids; do
            log_info "停止程序 $pid..."
            kill "$pid"
        done
        
        # 等待程序停止
        sleep 3
        
        # 檢查是否仍有程序執行
        local remaining_pids=$(pgrep -f "appium")
        if [[ -n "$remaining_pids" ]]; then
            log_warn "仍有程序執行，強制停止..."
            for pid in $remaining_pids; do
                kill -9 "$pid"
            done
        fi
        
        log_info "所有 Appium 程序已停止"
    else
        log_info "沒有找到執行中的 Appium 程序"
    fi
    
    # 清理 PID 檔案
    rm -f "$PID_FILE"
}

# 函式：檢查埠號使用情況
check_port_usage() {
    local default_port="4723"
    local pid=$(lsof -ti :$default_port)
    
    if [[ -n "$pid" ]]; then
        log_warn "埠號 $default_port 仍被程序 $pid 佔用"
        local process_name=$(ps -p $pid -o comm= 2>/dev/null)
        if [[ -n "$process_name" ]]; then
            log_info "佔用程序: $process_name"
        fi
        
        read -p "是否要停止佔用埠號的程序？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill "$pid"
            log_info "已停止佔用埠號的程序"
        fi
    else
        log_info "埠號 $default_port 已釋放"
    fi
}

# 解析命令列參數
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_MODE=true
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
    echo -e "${BLUE}    Appium 伺服器停止腳本${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    
    if [[ "$FORCE_MODE" == true ]]; then
        force_stop_appium
    else
        stop_appium_by_pid
    fi
    
    # 檢查埠號使用情況
    check_port_usage
    
    log_info "Appium 停止腳本執行完成"
}

# 執行主函式
main
