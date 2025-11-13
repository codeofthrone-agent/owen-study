#!/usr/bin/env python3
"""
檢查目前遠端設備的 /etc/init.d/emmc 配置

使用方法：
  python3 scripts/check_current_config.py
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
    print("  檢查 /etc/init.d/emmc 目前配置")
    print("=" * 70)
    print()

    port = '/dev/ttyUSB0'
    baudrate = 115200

    validator = RemoteSystemConfigValidator(port, baudrate)

    if not validator.connect():
        logger.error(f"無法連接串列埠: {port}")
        return 1

    # 讀取完整配置
    logger.info("讀取完整配置檔...")
    content = validator.execute_remote_command("cat /etc/init.d/emmc")

    print()
    print("=" * 70)
    print("  完整配置內容:")
    print("=" * 70)
    print(content)
    print("=" * 70)
    print()

    # 僅顯示 start_uvoice 相關行
    logger.info("檢查 start_uvoice 配置...")
    grep_result = validator.execute_remote_command("cat /etc/init.d/emmc | grep -A 1 -B 1 start_uvoice")

    print()
    print("=" * 70)
    print("  start_uvoice 相關配置:")
    print("=" * 70)
    print(grep_result)
    print("=" * 70)
    print()

    validator.disconnect()
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
