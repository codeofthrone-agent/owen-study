#!/usr/bin/env python3
"""
遠端 UART 配置驗證腳本

此腳本用於驗證遠端語音助手設備的 UART 配置是否正確。
如果配置錯誤，會自動修正並提示需要重開機。

使用方式:
    python3 scripts/validate_remote_uart_config.py
    python3 scripts/validate_remote_uart_config.py --port /dev/ttyUSB0 --baudrate 115200
    python3 scripts/validate_remote_uart_config.py --check-only  # 僅檢查，不修正

作者: Robot Automation Team
日期: 2025-11-11
版本: 1.0.0
"""

import sys
import os
import argparse
import importlib.util
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 檢查必要套件
try:
    import serial
    from loguru import logger
except ImportError as e:
    print(f"❌ 錯誤：缺少必要的套件")
    print(f"   {e}")
    print()
    print("💡 請執行以下命令安裝：")
    print("   pip install pyserial loguru python-dotenv")
    print("   或")
    print("   uv pip install -r requirements.txt")
    sys.exit(1)

# 直接匯入 RemoteSystemConfigValidator（避免觸發 __init__.py 的其他依賴）
try:
    spec = importlib.util.spec_from_file_location(
        "RemoteSystemConfigValidator",
        project_root / "libraries" / "multimodal_detection" / "RemoteSystemConfigValidator.py"
    )
    validator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator_module)
    RemoteSystemConfigValidator = validator_module.RemoteSystemConfigValidator
except Exception as e:
    # 如果直接匯入失敗，回退到標準匯入
    from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator


def setup_logger(verbose: bool = False):
    """設定日誌輸出"""
    logger.remove()  # 移除預設處理器

    if verbose:
        # 詳細模式：顯示 DEBUG 級別
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )
    else:
        # 一般模式：只顯示 INFO 及以上
        logger.add(
            sys.stderr,
            level="INFO",
            format="<level>{level: <8}</level> | <level>{message}</level>"
        )


def print_banner():
    """顯示橫幅"""
    print("=" * 70)
    print("  遠端 UART 配置驗證工具 v1.0.0")
    print("  Remote UART Configuration Validator")
    print("=" * 70)
    print()


def print_result(result: dict):
    """美化輸出驗證結果"""
    print()
    print("=" * 70)
    print("  驗證結果摘要")
    print("=" * 70)
    print()

    # 配置狀態
    if result['config_ok']:
        print("✅ 配置狀態: 正確")
        print("   遠端設備配置正確，可以開始測試")
    elif result['fixed']:
        print("⚠️  配置狀態: 已修正")
        print("   配置已自動修正，但需要重開機才能生效")
    else:
        print("❌ 配置狀態: 錯誤")
        if result['error_message']:
            print(f"   錯誤訊息: {result['error_message']}")

    print()

    # 詳細資訊
    print("📊 詳細資訊:")
    print(f"   - 配置正確: {result['config_ok']}")
    print(f"   - 已修正:   {result['fixed']}")
    print(f"   - 需要重開機: {result['needs_reboot']}")

    if result['error_message']:
        print(f"   - 錯誤訊息: {result['error_message']}")

    print()

    # 檢查結果詳情
    if 'details' in result:
        for file_path, check_result in result['details'].items():
            if check_result.get('has_error'):
                print(f"🔍 檢測到的配置問題 ({file_path}):")
                print(f"   - 錯誤類型: {check_result.get('error_type')}")
                if check_result.get('matched_line'):
                    print(f"   - 錯誤行: {check_result['matched_line']}")
                print()

    # 重開機指示
    if result['needs_reboot'] and result['reboot_command']:
        print("=" * 70)
        print("⚠️  重要：配置已修正，但需要重開機才能生效")
        print("=" * 70)
        print()
        print("請執行以下步驟：")
        print()
        print("1. 在遠端設備上執行重開機命令：")
        print(f"   {result['reboot_command']}")
        print()
        print("2. 等待設備重新啟動（約 30-60 秒）")
        print()
        print("3. 重新執行此驗證腳本確認配置生效")
        print()
        print("=" * 70)

    print()


def check_only_mode(validator: RemoteSystemConfigValidator) -> dict:
    """僅檢查模式（不自動修正）"""
    logger.info("執行僅檢查模式（不會自動修正配置）")

    # 連接串列埠
    if not validator.connect():
        return {
            'config_ok': False,
            'fixed': False,
            'needs_reboot': False,
            'reboot_command': None,
            'error_message': f"無法連接串列埠: {validator.port}",
            'details': {}
        }

    try:
        # 等待遠端設備就緒
        import time
        logger.info("等待遠端設備就緒...")
        time.sleep(1.0)

        # 發送換行以激活 shell
        validator.serial_conn.write(b'\n')
        time.sleep(0.5)

        # 檢查配置
        all_ok = True
        details = {}
        
        for file_path, expected_content in validator.TARGET_CONFIGS.items():
            check_result = validator.check_file_config(file_path, expected_content)
            details[file_path] = check_result
            if check_result['has_error']:
                all_ok = False

        result = {
            'config_ok': all_ok,
            'fixed': False,
            'needs_reboot': False,
            'reboot_command': None,
            'error_message': None if all_ok else "配置檢查失敗",
            'details': details
        }

        return result

    finally:
        validator.disconnect()


def main():
    """主程式"""
    # 解析命令列參數
    parser = argparse.ArgumentParser(
        description="遠端 UART 配置驗證工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 基本使用（使用預設值）
  %(prog)s

  # 指定串列埠和鮑率
  %(prog)s --port /dev/ttyUSB1 --baudrate 9600

  # 僅檢查配置，不自動修正
  %(prog)s --check-only

  # 詳細模式（顯示 DEBUG 日誌）
  %(prog)s --verbose

  # 從環境變數讀取配置
  UART_PORT=/dev/ttyUSB0 %(prog)s
        """
    )

    parser.add_argument(
        '--port', '-p',
        default=os.getenv('UART_PORT', '/dev/ttyUSB0'),
        help='UART 串列埠路徑（預設: /dev/ttyUSB0 或環境變數 UART_PORT）'
    )

    parser.add_argument(
        '--baudrate', '-b',
        type=int,
        default=115200,
        help='鮑率（預設: 115200）'
    )

    parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=5.0,
        help='命令執行超時時間（秒，預設: 5.0）'
    )

    parser.add_argument(
        '--check-only', '-c',
        action='store_true',
        help='僅檢查配置，不自動修正'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細模式（顯示 DEBUG 日誌）'
    )

    args = parser.parse_args()

    # 設定日誌
    setup_logger(verbose=args.verbose)

    # 顯示橫幅
    print_banner()

    # 顯示配置資訊
    print("📝 配置資訊:")
    print(f"   - UART 端口: {args.port}")
    print(f"   - 鮑率: {args.baudrate}")
    print(f"   - 命令超時: {args.timeout} 秒")
    print(f"   - 模式: {'僅檢查' if args.check_only else '自動修正'}")
    print()

    # 檢查串列埠是否存在
    if not os.path.exists(args.port):
        logger.error(f"串列埠不存在: {args.port}")
        print()
        print("💡 提示:")
        print("   1. 檢查 UART 轉 USB 模組是否已連接")
        print("   2. 執行 'ls /dev/ttyUSB*' 查看可用的串列埠")
        print("   3. 確認使用者有權限訪問串列埠（加入 dialout 群組）")
        print()
        return 1

    try:
        # 建立驗證器實例
        logger.info("初始化遠端配置驗證器...")
        validator = RemoteSystemConfigValidator(
            port=args.port,
            baudrate=args.baudrate,
            command_timeout=args.timeout
        )

        # 執行驗證
        if args.check_only:
            result = check_only_mode(validator)
        else:
            logger.info("開始完整驗證流程（含自動修正）...")
            result = validator.validate_uart_setup()

        # 輸出結果
        print_result(result)

        # 返回狀態碼
        if result['config_ok']:
            return 0  # 配置正確
        elif result['fixed'] and result['needs_reboot']:
            return 2  # 配置已修正，需要重開機
        else:
            return 1  # 驗證失敗

    except ImportError as e:
        logger.error(f"缺少必要的套件: {e}")
        print()
        print("💡 解決方法:")
        print("   pip install pyserial loguru python-dotenv")
        print("   或")
        print("   uv pip install -r requirements.txt")
        print()
        return 1

    except PermissionError:
        logger.error(f"權限不足，無法訪問串列埠: {args.port}")
        print()
        print("💡 解決方法:")
        print(f"   1. 將使用者加入 dialout 群組:")
        print(f"      sudo usermod -a -G dialout $USER")
        print(f"   2. 登出重新登入")
        print(f"   3. 或臨時修改權限:")
        print(f"      sudo chmod 666 {args.port}")
        print()
        return 1

    except KeyboardInterrupt:
        print()
        logger.warning("使用者中斷操作")
        return 130

    except Exception as e:
        logger.error(f"執行過程發生錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
