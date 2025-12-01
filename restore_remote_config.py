#!/usr/bin/env python3
"""
R328 遠端配置回復腳本 (Restore R328 Settings)

此腳本用於將遠端設備 (R328) 的系統配置回復到標準狀態。
主要修正以下兩個檔案：

1. /etc/init.d/emmc
----------------------------------------
#!/bin/sh /etc/rc.common

START=99
STOP=70

USE_PROCD=1
#PROG=/bin/wifi_connect_ap_test
#DEPEND=bluetoothd
start_service() {
    sleep 8
    #/etc/thortron/start_emmc.sh
    bt_gatt_server > /dev/S0 &
	sleep 8
	/uvoice/start_uvoice.sh
}
----------------------------------------

2. /uvoice/start_uvoice.sh
----------------------------------------
export LD_LIBRARY_PATH=/uvoice:/aws/lib
cd /uvoice
./uvcapture > /dev/ttyS0 &
----------------------------------------
"""

import sys
import os
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

def restore_config():
    logger.info("開始回復遠端配置...")
    
    try:
        validator = RemoteSystemConfigValidator()
        result = validator.validate_uart_setup()
        
        if result['config_ok']:
            logger.info("✓ 配置已符合預期")
        elif result['fixed']:
            logger.info("✓ 配置已修正")
            if result['needs_reboot']:
                logger.warning(f"⚠️  需要重開機: {result['reboot_command']}")
        else:
            logger.error(f"✗ 配置修正失敗: {result['error_message']}")
            
    except Exception as e:
        logger.error(f"執行失敗: {e}")

if __name__ == "__main__":
    restore_config()
