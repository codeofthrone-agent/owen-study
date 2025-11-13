"""
遠端系統配置驗證器 - RemoteSystemConfigValidator

透過 UART 串列埠連接到遠端語音助手設備，檢查並修正系統配置。

主要功能:
    - 透過 UART 執行遠端命令
    - 檢查 /etc/init.d/emmc 配置
    - 自動修正錯誤配置
    - 提供重開機指示

使用場景:
    - 確保遠端設備日誌正確輸出到 UART
    - 自動化設備初始化流程
    - 減少手動配置錯誤

Python 使用範例:
    from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

    validator = RemoteSystemConfigValidator('/dev/ttyUSB0', 115200)
    result = validator.validate_uart_setup()

    if result['needs_reboot']:
        print(f"請重開機: {result['reboot_command']}")
"""

import time
import re
from typing import Optional, Dict, Tuple
from pathlib import Path
from loguru import logger

# 串列埠通訊
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial 未安裝，遠端配置驗證功能將不可用")


class RemoteSystemConfigValidator:
    """
    遠端系統配置驗證器

    透過 UART 串列埠連接到遠端設備，檢查並修正系統配置。

    Attributes:
        port (str): 串列埠路徑（如 /dev/ttyUSB0）
        baudrate (int): 鮑率（預設 115200）
        serial_conn (serial.Serial): 串列埠連線物件
        command_timeout (float): 命令執行超時時間（秒）
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.1.0'  # v1.1.0: 新增重複執行錯誤檢測，改進 sed 修正策略

    # 配置檔案路徑
    EMMC_CONFIG_PATH = '/etc/init.d/emmc'

    # 錯誤配置模式（正規表達式）
    WRONG_PATTERNS = [
        # 重複執行（同一行出現兩次 start_uvoice.sh）
        (r'/uvoice/start_uvoice\.sh.*?/uvoice/start_uvoice\.sh', 'duplicate_execution'),
        # 輸出到 /dev/null
        (r'/uvoice/start_uvoice\.sh\s*>\s*/dev/null', 'output_to_null'),
        # 有 & 但沒有重導向
        (r'/uvoice/start_uvoice\.sh\s+&(?!\s*>)', 'no_redirect'),
        # 沒有背景執行也沒有重導向
        (r'/uvoice/start_uvoice\.sh(?!\s*>)(?!\s+&)', 'no_background'),
    ]

    # 正確的配置
    CORRECT_CONFIG = '/uvoice/start_uvoice.sh > /dev/ttyS0 &'

    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200, command_timeout: float = 5.0):
        """
        初始化遠端系統配置驗證器

        Args:
            port: 串列埠路徑（預設 /dev/ttyUSB0）
            baudrate: 鮑率（預設 115200）
            command_timeout: 命令執行超時時間（秒，預設 5.0）
        """
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial 未安裝，無法使用遠端配置驗證功能")

        self.port = port
        self.baudrate = baudrate
        self.command_timeout = command_timeout
        self.serial_conn: Optional[serial.Serial] = None

        logger.info(f"初始化遠端系統配置驗證器 (v{self.ROBOT_LIBRARY_VERSION})")
        logger.info(f"串列埠: {port}, 鮑率: {baudrate}, 命令超時: {command_timeout}s")

    def connect(self) -> bool:
        """
        連接串列埠

        Returns:
            是否成功連接
        """
        if self.serial_conn and self.serial_conn.is_open:
            logger.warning("串列埠已連接")
            return True

        try:
            logger.info(f"嘗試連接串列埠: {self.port}")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )

            # 清空輸入緩衝區
            self.serial_conn.reset_input_buffer()

            logger.info(f"✓ 串列埠連接成功: {self.port}")
            return True

        except Exception as e:
            logger.error(f"串列埠連接失敗: {e}")
            return False

    def disconnect(self):
        """關閉串列埠連接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("串列埠已關閉")

    def execute_remote_command(self, cmd: str, timeout: Optional[float] = None) -> str:
        """
        透過 UART 執行遠端命令並取得輸出

        Args:
            cmd: 要執行的命令
            timeout: 超時時間（秒），若為 None 則使用預設值

        Returns:
            命令輸出結果
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("串列埠未連接")

        if timeout is None:
            timeout = self.command_timeout

        # 生成唯一標記
        marker = f"__CMD_END_{int(time.time() * 1000)}__"

        # 發送命令（附加標記）
        full_cmd = f"{cmd}; echo '{marker}'\n"
        logger.debug(f"執行遠端命令: {cmd}")

        try:
            self.serial_conn.write(full_cmd.encode('utf-8'))
            self.serial_conn.flush()

            # 接收回應
            output_lines = []
            all_lines = []  # 用於調試，記錄所有行
            start_time = time.time()
            marker_found = False
            cmd_echo_skipped = False

            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting > 0:
                    try:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').rstrip()
                        all_lines.append(line)  # 記錄所有行用於調試
                        logger.debug(f"收到原始行: {repr(line)}")

                        # 跳過空行
                        if not line.strip():
                            logger.debug("跳過空行")
                            continue

                        # 跳過 shell prompt（root@xxx:/#）
                        if re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+:[^#]*#', line):
                            logger.debug(f"跳過 shell prompt: {line}")
                            continue

                        # 檢查是否為結束標記（必須是單獨一行，不包含其他內容）
                        if line.strip() == marker:
                            marker_found = True
                            logger.debug(f"找到結束標記（單獨一行）")
                            break

                        # 跳過命令回顯行（包含完整命令的行）
                        if not cmd_echo_skipped and (f"{cmd};" in line or full_cmd.strip() in line):
                            cmd_echo_skipped = True
                            logger.debug(f"跳過命令回顯: {line[:80]}...")
                            continue

                        # 收集有效輸出
                        output_lines.append(line)
                        logger.debug(f"✓ 收集輸出行 #{len(output_lines)}: {line[:80]}...")

                    except Exception as e:
                        logger.warning(f"讀取行時發生錯誤: {e}")
                        continue
                else:
                    time.sleep(0.01)  # 短暫休息避免忙等待

            if not marker_found:
                logger.warning(f"命令執行超時 ({timeout}s)，可能未完成")
                logger.debug(f"收到的所有行 ({len(all_lines)} 行): {all_lines}")

            output = '\n'.join(output_lines)
            logger.debug(f"命令輸出 ({len(output_lines)} 行):")
            if output:
                for i, line in enumerate(output_lines[:5], 1):  # 只顯示前 5 行
                    logger.debug(f"  [{i}] {line}")
                if len(output_lines) > 5:
                    logger.debug(f"  ... ({len(output_lines) - 5} 行省略)")

            return output

        except Exception as e:
            logger.error(f"執行遠端命令失敗: {e}")
            return ""

    def check_emmc_config(self) -> Dict[str, any]:
        """
        檢查 /etc/init.d/emmc 配置

        Returns:
            檢查結果字典：
                - has_error (bool): 是否有錯誤
                - error_type (str): 錯誤類型
                - current_content (str): 當前配置內容
                - needs_fix (bool): 是否需要修正
                - matched_line (str): 匹配到的錯誤行
        """
        logger.info(f"檢查遠端配置檔: {self.EMMC_CONFIG_PATH}")

        # 讀取配置檔
        cmd = f"cat {self.EMMC_CONFIG_PATH}"
        content = self.execute_remote_command(cmd)

        if not content:
            logger.error(f"無法讀取配置檔: {self.EMMC_CONFIG_PATH}")
            return {
                'has_error': None,
                'error_type': 'file_not_readable',
                'current_content': '',
                'needs_fix': False,
                'matched_line': None
            }

        # 檢查是否已經是正確配置
        if self.CORRECT_CONFIG in content:
            logger.info("✓ 配置已經正確")
            return {
                'has_error': False,
                'error_type': None,
                'current_content': content,
                'needs_fix': False,
                'matched_line': None
            }

        # 檢查錯誤模式
        for pattern, error_type in self.WRONG_PATTERNS:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                matched_line = match.group(0)
                logger.warning(f"⚠️ 檢測到配置錯誤: {error_type}")
                logger.warning(f"   錯誤行: {matched_line}")

                return {
                    'has_error': True,
                    'error_type': error_type,
                    'current_content': content,
                    'needs_fix': True,
                    'matched_line': matched_line
                }

        # 沒有匹配到任何模式（可能是其他配置）
        logger.info("未檢測到已知的錯誤配置模式")
        return {
            'has_error': False,
            'error_type': None,
            'current_content': content,
            'needs_fix': False,
            'matched_line': None
        }

    def fix_emmc_config(self) -> bool:
        """
        修正 /etc/init.d/emmc 配置

        Returns:
            是否修正成功
        """
        logger.info("=" * 60)
        logger.info("正在修正遠端配置...")

        # 1. 備份原始檔案
        logger.info("步驟 1: 備份原始配置")
        backup_cmd = f"cp {self.EMMC_CONFIG_PATH} {self.EMMC_CONFIG_PATH}.backup"
        backup_result = self.execute_remote_command(backup_cmd)
        logger.info("✓ 配置已備份")

        # 2. 使用 sed 修正配置
        logger.info("步驟 2: 修正配置")
        # 策略：先刪除包含 start_uvoice.sh 的所有行，然後在 bt_gatt_server 之後插入正確配置

        # 步驟 2.1: 刪除所有包含 start_uvoice.sh 的行
        delete_cmd = f"sed -i '/\\/uvoice\\/start_uvoice\\.sh/d' {self.EMMC_CONFIG_PATH}"
        logger.debug(f"執行 sed 刪除命令: {delete_cmd}")
        self.execute_remote_command(delete_cmd)

        # 步驟 2.2: 在 bt_gatt_server 之後插入正確配置（保持縮排）
        # 使用 shell 變數搭配 $'...' 語法來產生真正的 tab 字元
        # 原始配置使用 8 個空格縮排，為了保持一致，這裡也使用空格
        indent = "        "  # 8 個空格，與原始配置保持一致
        insert_cmd = f"sed -i '/bt_gatt_server/a\\{indent}{self.CORRECT_CONFIG}' {self.EMMC_CONFIG_PATH}"
        logger.debug(f"執行 sed 插入命令 (使用 8 空格縮排): {insert_cmd}")
        fix_result = self.execute_remote_command(insert_cmd)

        # 3. 驗證修正結果
        logger.info("步驟 3: 驗證修正結果")
        check_result = self.check_emmc_config()

        if not check_result['has_error'] and self.CORRECT_CONFIG in check_result['current_content']:
            logger.info("✓ 配置修正成功")
            logger.info(f"   新配置: {self.CORRECT_CONFIG}")
            logger.info("=" * 60)
            return True
        else:
            logger.error("✗ 配置修正失敗")
            logger.error(f"   檢查結果: {check_result}")
            logger.info("=" * 60)
            return False

    def validate_uart_setup(self) -> Dict[str, any]:
        """
        完整的 UART 設定驗證流程

        Returns:
            驗證結果字典：
                - config_ok (bool): 配置是否正確
                - fixed (bool): 是否已修正
                - needs_reboot (bool): 是否需要重開機
                - reboot_command (str): 重開機命令
                - error_message (str): 錯誤訊息
                - details (dict): 詳細資訊
        """
        result = {
            'config_ok': False,
            'fixed': False,
            'needs_reboot': False,
            'reboot_command': None,
            'error_message': None,
            'details': {}
        }

        try:
            # 連接串列埠
            logger.info("驗證遠端系統配置...")

            if not self.connect():
                result['error_message'] = f"無法連接串列埠: {self.port}"
                return result

            # 等待遠端設備就緒
            logger.info("等待遠端設備就緒...")
            time.sleep(1.0)

            # 發送換行以激活 shell
            self.serial_conn.write(b'\n')
            time.sleep(0.5)

            # 檢查配置
            check_result = self.check_emmc_config()
            result['details']['check_result'] = check_result

            if check_result['has_error'] is None:
                result['error_message'] = f"無法讀取配置檔: {self.EMMC_CONFIG_PATH}"
                return result

            if not check_result['has_error']:
                logger.info("✓ 遠端配置正確")
                result['config_ok'] = True
                return result

            # 自動修正
            logger.warning(f"⚠️ 檢測到配置錯誤: {check_result['error_type']}")
            logger.warning(f"   錯誤行: {check_result['matched_line']}")
            logger.info(f"將自動修正為: {self.CORRECT_CONFIG}")

            if self.fix_emmc_config():
                result['fixed'] = True
                result['needs_reboot'] = True
                result['reboot_command'] = "reboot"

                logger.warning("")
                logger.warning("=" * 60)
                logger.warning("⚠️  重要：配置已修正，但需要重開機才能生效")
                logger.warning("=" * 60)
                logger.warning("")
                logger.warning("請執行以下命令重開機遠端設備：")
                logger.warning(f"  {result['reboot_command']}")
                logger.warning("")
                logger.warning("重開機後，請重新執行測試。")
                logger.warning("=" * 60)
            else:
                result['error_message'] = "配置修正失敗，請手動檢查"

            return result

        except Exception as e:
            logger.error(f"驗證過程發生錯誤: {e}")
            result['error_message'] = str(e)
            return result

        finally:
            self.disconnect()

    # ===========================================
    # Robot Framework 關鍵字
    # ===========================================

    def 連接遠端設備(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200) -> bool:
        """
        連接遠端設備

        Args:
            port: 串列埠路徑
            baudrate: 鮑率

        Returns:
            是否成功連接
        """
        self.port = port
        self.baudrate = baudrate
        return self.connect()

    def 檢查遠端配置(self) -> Dict[str, any]:
        """檢查遠端 /etc/init.d/emmc 配置"""
        return self.check_emmc_config()

    def 修正遠端配置(self) -> bool:
        """修正遠端 /etc/init.d/emmc 配置"""
        return self.fix_emmc_config()

    def 驗證並修正遠端配置(self) -> Dict[str, any]:
        """完整的遠端配置驗證與修正流程"""
        return self.validate_uart_setup()

    def 斷開遠端連接(self):
        """斷開遠端設備連接"""
        self.disconnect()


if __name__ == "__main__":
    # 測試腳本
    print("=" * 50)
    print("RemoteSystemConfigValidator 測試腳本")
    print("=" * 50)
    print("注意: 此腳本需要連接到實際的遠端設備才能正常運作。")

    try:
        # 建立驗證器實例
        validator = RemoteSystemConfigValidator(port='/dev/ttyUSB0', baudrate=115200)

        # 執行完整驗證流程
        print("\n執行完整驗證流程...")
        result = validator.validate_uart_setup()

        print("\n驗證結果:")
        print(f"  - 配置正確: {result['config_ok']}")
        print(f"  - 已修正: {result['fixed']}")
        print(f"  - 需要重開機: {result['needs_reboot']}")

        if result['needs_reboot']:
            print(f"\n⚠️  請執行以下命令重開機:")
            print(f"  {result['reboot_command']}")

        if result['error_message']:
            print(f"\n❌ 錯誤: {result['error_message']}")

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("測試腳本結束")
    print("=" * 50)
