#!/usr/bin/env python3
"""
快速修正 /etc/init.d/emmc 配置錯誤

錯誤配置範例：
  /uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh

正確配置：
  /uvoice/start_uvoice.sh > /dev/ttyS0 &

使用方法：
  python3 scripts/fix_emmc_config.py
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
    print("  /etc/init.d/emmc 配置修正工具")
    print("=" * 70)
    print()

    # 建立驗證器
    port = '/dev/ttyUSB0'
    baudrate = 115200

    print(f"📝 連接資訊:")
    print(f"   - UART 端口: {port}")
    print(f"   - 鮑率: {baudrate}")
    print()

    validator = RemoteSystemConfigValidator(port, baudrate)

    # 連接
    logger.info(f"嘗試連接串列埠: {port}")
    if not validator.connect():
        logger.error(f"無法連接串列埠: {port}")
        return 1

    logger.info(f"✓ 串列埠連接成功: {port}")

    # 檢查當前配置
    logger.info("檢查當前配置...")
    try:
        current_config = validator.execute_remote_command("cat /etc/init.d/emmc | grep start_uvoice")
        print()
        print("🔍 當前配置:")
        print(f"   {current_config.strip()}")
        print()
    except Exception as e:
        logger.error(f"無法讀取配置: {e}")
        return 1

    # 使用手動 sed 命令修正
    logger.info("開始修正配置...")

    # 備份
    logger.info("步驟 1: 備份原始配置")
    try:
        validator.execute_remote_command("cp /etc/init.d/emmc /etc/init.d/emmc.backup")
        logger.info("✓ 配置已備份到 /etc/init.d/emmc.backup")
    except Exception as e:
        logger.error(f"備份失敗: {e}")
        return 1

    # 修正配置（處理重複的 /uvoice/start_uvoice.sh）
    logger.info("步驟 2: 修正配置")

    # 方案 1: 移除重複的部分
    sed_cmd = r"sed -i 's|/uvoice/start_uvoice\.sh > /dev/ttyS0[[:space:]]*/.*/start_uvoice\.sh|/uvoice/start_uvoice.sh > /dev/ttyS0 \&|g' /etc/init.d/emmc"

    try:
        result = validator.execute_remote_command(sed_cmd)
        logger.info("✓ sed 命令執行完成")
    except Exception as e:
        logger.error(f"sed 執行失敗: {e}")
        logger.info("嘗試使用備用方案...")

        # 備用方案：直接替換整行
        try:
            # 先刪除錯誤行
            validator.execute_remote_command(r"sed -i '/start_uvoice\.sh.*start_uvoice\.sh/d' /etc/init.d/emmc")
            # 在 bt_gatt_server 之後插入正確配置
            validator.execute_remote_command(r"sed -i '/bt_gatt_server/a\        /uvoice/start_uvoice.sh > /dev/ttyS0 \&' /etc/init.d/emmc")
            logger.info("✓ 使用備用方案修正成功")
        except Exception as e2:
            logger.error(f"備用方案也失敗: {e2}")
            return 1

    # 驗證修正結果
    logger.info("步驟 3: 驗證修正結果")
    try:
        new_config = validator.execute_remote_command("cat /etc/init.d/emmc | grep start_uvoice")
        print()
        print("✅ 修正後配置:")
        print(f"   {new_config.strip()}")
        print()

        # 檢查是否包含正確格式
        if "/uvoice/start_uvoice.sh > /dev/ttyS0 &" in new_config:
            logger.info("✓ 配置修正成功！")
            print()
            print("=" * 70)
            print("⚠️  重要：配置已修正，需要重開機才能生效")
            print("=" * 70)
            print()
            print("請在遠端設備上執行：")
            print("  reboot")
            print()
            validator.disconnect()
            return 0
        else:
            logger.warning("⚠️ 配置可能不正確，請手動檢查")
            return 2

    except Exception as e:
        logger.error(f"驗證失敗: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ 使用者中斷執行")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"未預期的錯誤: {e}")
        sys.exit(1)
