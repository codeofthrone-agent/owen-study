#!/bin/bash
# 快速修正 /etc/init.d/emmc 配置腳本
# 使用 Python 的 RemoteSystemConfigValidator 透過 UART 修正遠端配置

echo "=========================================="
echo "  /etc/init.d/emmc 配置修正工具"
echo "=========================================="
echo ""

# 檢查是否在專案根目錄
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ 錯誤: 請在專案根目錄執行此腳本"
    echo "   cd /home/thortron/Tools/robot-multiplatform-automation"
    exit 1
fi

# 啟用虛擬環境
if [ -d ".venv" ]; then
    echo "🔧 啟用虛擬環境..."
    source .venv/bin/activate
else
    echo "⚠️  未找到虛擬環境，使用系統 Python"
fi

# 執行驗證與修正
echo "📡 連接到遠端設備並驗證配置..."
echo ""

python3 << 'EOF'
import sys
from pathlib import Path

# 加入專案路徑
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator
from loguru import logger

def main():
    # 建立驗證器
    port = '/dev/ttyUSB0'
    baudrate = 115200

    print(f"📝 連接資訊:")
    print(f"   UART 端口: {port}")
    print(f"   鮑率: {baudrate}")
    print()

    validator = RemoteSystemConfigValidator(port, baudrate)

    # 執行驗證
    logger.info("開始驗證遠端配置...")
    result = validator.validate_uart_setup()

    print()
    print("=" * 60)
    print("  驗證結果")
    print("=" * 60)

    if result['config_ok']:
        print("✅ 配置正確，無需修正")
        return 0
    elif result['fixed'] and result['needs_reboot']:
        print("⚠️  配置已修正，但需要重開機")
        print()
        print("請在遠端設備上執行:")
        print(f"  {result['reboot_command']}")
        print()
        print("重開機後，配置將生效")
        return 2
    elif result['error_message']:
        print(f"❌ 驗證失敗: {result['error_message']}")
        return 1
    else:
        print("⚠️  未知狀態")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"執行失敗: {e}")
        sys.exit(1)
EOF

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 配置正確"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️  配置已修正，需要重開機"
else
    echo "❌ 修正失敗"
fi
echo "=========================================="

exit $EXIT_CODE
