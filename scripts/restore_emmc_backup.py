#!/usr/bin/env python3
"""
恢復 /etc/init.d/emmc 的備份檔案

使用方法：
  python3 scripts/restore_emmc_backup.py
"""

import sys
from pathlib import Path

# 加入專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator
from loguru import logger


def main():
    print("=" * 70)
    print("  恢復 /etc/init.d/emmc 備份檔案")
    print("=" * 70)
    print()

    port = '/dev/ttyUSB0'
    baudrate = 115200

    print(f"📝 連接資訊:")
    print(f"   UART 端口: {port}")
    print(f"   鮑率: {baudrate}")
    print()

    validator = RemoteSystemConfigValidator(port, baudrate)

    # 連接
    if not validator.connect():
        logger.error(f"無法連接串列埠: {port}")
        return 1

    # 檢查備份檔案是否存在
    logger.info("檢查備份檔案...")
    check_cmd = "ls -l /etc/init.d/emmc.backup"
    result = validator.execute_remote_command(check_cmd)

    if "No such file" in result or not result:
        logger.error("❌ 備份檔案不存在: /etc/init.d/emmc.backup")
        validator.disconnect()
        return 1

    logger.info("✓ 找到備份檔案")

    # 恢復備份
    logger.info("恢復備份檔案...")
    restore_cmd = "cp /etc/init.d/emmc.backup /etc/init.d/emmc"
    validator.execute_remote_command(restore_cmd)

    # 驗證
    logger.info("驗證恢復結果...")
    content = validator.execute_remote_command("cat /etc/init.d/emmc | grep start_uvoice")

    print()
    print("=" * 70)
    print("  恢復後的配置:")
    print("=" * 70)
    print(content)
    print("=" * 70)
    print()

    validator.disconnect()

    print("✅ 備份已恢復")
    print()
    print("現在可以重新執行修正腳本:")
    print("  uv run python3 scripts/validate_remote_uart_config.py")
    print()

    return 0


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
