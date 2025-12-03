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

    # 預期的配置內容定義
    TARGET_CONFIGS = {
        '/etc/init.d/emmc': """#!/bin/sh /etc/rc.common

START=99
STOP=70

USE_PROCD=1
#PROG=/bin/wifi_connect_ap_test
#DEPEND=bluetoothd
start_service() {
    sleep 8
    #/etc/thortron/start_emmc.sh
    bt_gatt_server > /dev/ttyS0 &
	sleep 8
	/uvoice/start_uvoice.sh
}
""",
        '/uvoice/start_uvoice.sh': """export LD_LIBRARY_PATH=/uvoice:/aws/lib
cd /uvoice
./uvcapture > /dev/ttyS0 &
"""
    }

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
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # 嘗試清除 DTR/RTS (有些板子會在 DTR 拉低時重置)
            self.serial_conn.dtr = False
            self.serial_conn.rts = False

            # 1. 先嘗試簡單的 Enter 檢查狀態 (使用 \r)
            logger.info("檢查目前 Shell 狀態...")
            self.serial_conn.write(b'\r')
            
            # 使用 read() 而非 in_waiting，確保能讀到資料
            time.sleep(0.1)
            initial_response = self.serial_conn.read(1000).decode('utf-8', errors='ignore')
            logger.debug(f"初始回應: {repr(initial_response)}")
            
            # 如果已經是正常 Prompt，直接回傳成功
            if ('#' in initial_response or '$' in initial_response) and '>' not in initial_response:
                logger.info(f"✓ Shell 已就緒 (Prompt: {initial_response.strip()})")
                self.serial_conn.reset_input_buffer()
                return True

            # 2. 如果不是正常狀態，才執行萬能解鎖
            logger.warning("Shell 未就緒或處於 Stuck 狀態，執行萬能解鎖...")
            
            unstuck_sequences = [
                b'\x03',       # Ctrl-C (基本中斷)
                b"'\x03",      # 嘗試關閉單引號
                b'"\x03',      # 嘗試關閉雙引號
                b'}\x03',      # 嘗試關閉大括號
                b')\x03',      # 嘗試關閉小括號
                b']\x03',      # 嘗試關閉中括號
                b'\\\x03',     # 嘗試關閉轉義
                b'\nEOF\n',    # 嘗試結束 heredoc
                b'EOF\n',      # 嘗試結束 heredoc (無前導換行)
                b'\n\x04',     # Ctrl-D (EOF)
            ]
            
            for seq in unstuck_sequences:
                self.serial_conn.write(seq)
                time.sleep(0.1)
                self.serial_conn.write(b'\n')
                time.sleep(0.1)
            
            # 最後再送幾次 Ctrl-C 確保乾淨
            for _ in range(3):
                self.serial_conn.write(b'\x03')
                time.sleep(0.1)
            
            self.serial_conn.write(b'\n')
            time.sleep(1.0)
            
            # 清空殘留輸出並檢查
            if self.serial_conn.in_waiting > 0:
                junk = self.serial_conn.read(self.serial_conn.in_waiting)
                try:
                    junk_str = junk.decode('utf-8', errors='ignore')
                    logger.debug(f"清除殘留資料: {repr(junk_str)}")
                except:
                    logger.debug(f"清除殘留資料: {len(junk)} bytes")
            
            self.serial_conn.reset_input_buffer()

            # 檢查是否仍處於 stuck 狀態，並確認是否回到 Shell
            self.serial_conn.write(b'\n')
            time.sleep(0.5)
            if self.serial_conn.in_waiting > 0:
                response = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                logger.debug(f"重置後回應: {repr(response)}")
                
                if '>' in response and '#' not in response and '$' not in response:
                    logger.error("Shell 仍處於 stuck 狀態 (>)，無法自動修復")
                    return False
                
                if 'login:' in response:
                    logger.error("Shell 已登出，處於登入提示符")
                    # 這裡可以考慮自動登入，但目前先報錯
                    return False
            
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

        # 清空輸入緩衝區，避免讀取到上一次命令的殘留輸出 (如 Prompt)
        self.serial_conn.reset_input_buffer()
        
        # 生成唯一標記
        timestamp = int(time.time() * 1000)
        start_marker = f"__CMD_START_{timestamp}__"
        end_marker = f"__CMD_END_{timestamp}__"

        # 發送命令（附加標記，使用 \r 確保執行）
        # 使用開始和結束標記來精確擷取輸出
        full_cmd = f"\necho '{start_marker}'\n{cmd}\necho '{end_marker}'\r"
        logger.debug(f"執行遠端命令: {cmd}")

        try:
            self.serial_conn.write(full_cmd.encode('utf-8'))
            self.serial_conn.flush()

            # 接收回應
            output_lines = []
            start_time = time.time()
            marker_found = False
            start_marker_found = False

            # 使用 read_until 讀取直到結束標記出現
            marker_bytes = end_marker.encode('utf-8')
            raw_output = b''
            
            while True:
                chunk = self.serial_conn.read_until(marker_bytes)
                raw_output += chunk
                
                if marker_bytes not in chunk:
                    break
                
                # 檢查是否為命令回顯
                chunk_str = chunk.decode('utf-8', errors='ignore')
                if f"echo '{end_marker}'" in chunk_str:
                    logger.debug("跳過包含結束標記的命令回顯")
                    continue
                
                logger.debug("✓ 找到結束標記")
                marker_found = True
                break

            output_str = raw_output.decode('utf-8', errors='ignore')
            logger.debug(f"Raw output len: {len(output_str)}")
            logger.debug(f"Raw output content:\n{output_str}")
            
            # 處理輸出
            lines = output_str.splitlines()
            output_lines = []
            start_marker_found = False
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # 尋找開始標記
                if start_marker in line:
                    if not start_marker_found:
                        start_marker_found = True
                        logger.debug("✓ 找到開始標記")
                    continue
                
                if not start_marker_found:
                    continue
                
                # 尋找結束標記
                if end_marker in line:
                    break
                    
                # 跳過 echo 回顯
                # 寬鬆匹配：如果行包含命令，或者是命令的一部分
                if line == cmd or cmd in line or line in cmd:
                    logger.debug(f"  [Skip] Command echo: {line}")
                    continue
                
                # 跳過 prompt
                if line.endswith('#') or line.endswith('$') or line.startswith('root@'):
                    logger.debug(f"  [Skip] Prompt: {line}")
                    continue
                    
                output_lines.append(line)

            if not marker_found:
                logger.warning(f"命令執行超時 ({timeout}s)，可能未完成")
                logger.debug(f"收到的所有行 ({len(output_lines)} 行): {output_lines}")

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

    def check_file_config(self, file_path: str, expected_content: str) -> Dict[str, any]:
        """
        檢查單一檔案配置

        Args:
            file_path: 檔案路徑
            expected_content: 預期內容

        Returns:
            檢查結果字典
        """
        logger.info(f"檢查遠端配置檔: {file_path}")

        # 讀取配置檔，增加重試機制
        content = ""
        max_retries = 3
        for attempt in range(max_retries):
            cmd = f"cat {file_path}"
            content = self.execute_remote_command(cmd)
            if content:
                break
            logger.warning(f"讀取失敗，重試 {attempt + 1}/{max_retries}...")
            time.sleep(1.0)

        if not content:
            logger.error(f"無法讀取配置檔: {file_path}")
            ret = {
                'file_path': file_path,
                'has_error': None,
                'error_type': 'file_not_readable',
                'current_content': '',
                'needs_fix': False,
                'matched_line': None
            }
            logger.debug(f"Returning from check_file_config (error): {ret}")
            return ret

        # 移除內容前後的空白以便比較
        clean_content = content.strip()
        
        # 正規化預期內容（移除空白行和縮排，以匹配 execute_remote_command 的行為）
        expected_lines = [line.strip() for line in expected_content.splitlines() if line.strip()]
        expected_clean = '\n'.join(expected_lines)
        
        # 簡單比較
        if clean_content == expected_clean:
            logger.info(f"✓ {file_path} 配置完全匹配")
            return {
                'file_path': file_path,
                'has_error': False,
                'error_type': None,
                'current_content': content,
                'needs_fix': False,
                'matched_line': None
            }
        
        logger.warning(f"⚠️ {file_path} 配置內容不匹配")
        logger.debug(f"預期長度: {len(expected_clean)}, 實際長度: {len(clean_content)}")
        logger.debug(f"預期內容:\n{expected_clean}")
        logger.debug(f"實際內容:\n{clean_content}")
        
        return {
            'file_path': file_path,
            'has_error': True,
            'error_type': 'content_mismatch',
            'current_content': content,
            'needs_fix': True,
            'matched_line': 'Entire file content mismatch'
        }

    def fix_file_config(self, file_path: str, expected_content: str) -> bool:
        """
        修正單一檔案配置
        
        Args:
            file_path: 檔案路徑
            expected_content: 預期內容

        Returns:
            是否修正成功
        """
        logger.info("-" * 40)
        logger.info(f"正在修正檔案: {file_path}")

        # 1. 備份
        backup_cmd = f"cp {file_path} {file_path}.backup"
        self.execute_remote_command(backup_cmd)
        
        # 2. 寫入新內容
        temp_file = f"/tmp/config_new_{int(time.time())}"
        write_cmd = f"cat > {temp_file} << 'EOF'\n{expected_content}\nEOF"
        
        logger.debug("執行寫入命令...")
        self.execute_remote_command(write_cmd, timeout=10.0)
        
        # 移動並設定權限
        mv_cmd = f"mv {temp_file} {file_path} && chmod 755 {file_path}"
        self.execute_remote_command(mv_cmd)
        
        # 3. 驗證
        check_result = self.check_file_config(file_path, expected_content)

        if not check_result['has_error']:
            logger.info(f"✓ {file_path} 修正成功")
            return True
        else:
            logger.error(f"✗ {file_path} 修正失敗")
            return False

    def validate_uart_setup(self) -> Dict[str, any]:
        """
        完整的 UART 設定驗證流程 (檢查所有配置檔)

        Returns:
            驗證結果字典
        """
        result = {
            'config_ok': True,
            'fixed': False,
            'needs_reboot': False,
            'reboot_command': None,
            'error_message': None,
            'details': {}
        }

        try:
            logger.info("驗證遠端系統配置...")

            if not self.connect():
                result['error_message'] = f"無法連接串列埠: {self.port}"
                result['config_ok'] = False
                return result

            logger.info("等待遠端設備就緒...")
            time.sleep(1.0)
            self.serial_conn.write(b'\n')
            time.sleep(0.5)

            # 檢查所有配置
            all_fixed = True
            any_error = False
            
            for file_path, expected_content in self.TARGET_CONFIGS.items():
                check_result = self.check_file_config(file_path, expected_content)
                logger.debug(f"Check result for {file_path}: {check_result}")
                result['details'][file_path] = check_result

                if check_result['has_error']:
                    any_error = True
                    result['config_ok'] = False
                    logger.warning(f"⚠️ 發現錯誤: {file_path}")
                    
                    # 嘗試修正
                    if self.fix_file_config(file_path, expected_content):
                        result['fixed'] = True
                        result['needs_reboot'] = True
                    else:
                        all_fixed = False
                        result['error_message'] = f"修正失敗: {file_path}"

            if result['fixed'] and all_fixed:
                result['reboot_command'] = "reboot"
                logger.warning("=" * 60)
                logger.warning("⚠️  配置已修正，需要重開機")
                logger.warning(f"  {result['reboot_command']}")
                logger.warning("=" * 60)
            elif any_error and not all_fixed:
                result['error_message'] = "部分配置修正失敗，請檢查日誌"

            return result

        except Exception as e:
            logger.error(f"驗證過程發生錯誤: {e}")
            result['error_message'] = str(e)
            # 檢查 uvcapture 是否正在運行
            logger.info("檢查 uvcapture 狀態...")
            ps_output = self.execute_remote_command("ps | grep uvcapture")
            uvcapture_running = False
            for line in ps_output:
                if "uvcapture" in line and "grep" not in line:
                    uvcapture_running = True
                    logger.info(f"✓ uvcapture 正在運行: {line}")
                    break
            
            if not uvcapture_running:
                logger.warning("⚠️  uvcapture 未運行，嘗試手動啟動...")
                self.execute_remote_command("/uvoice/start_uvoice.sh &")
                time.sleep(2)
                
                # 再次檢查
                ps_output = self.execute_remote_command("ps | grep uvcapture")
                for line in ps_output:
                    if "uvcapture" in line and "grep" not in line:
                        uvcapture_running = True
                        logger.info(f"✓ uvcapture 已啟動: {line}")
                        break
                
                if not uvcapture_running:
                    logger.error("✗ 無法啟動 uvcapture")
                    result['error_message'] = "uvcapture 服務無法啟動"
                    return result

            result['config_ok'] = True
            return result

        finally:
            self.disconnect()

    # ===========================================
    # Robot Framework 關鍵字
    # ===========================================

    def 連接遠端設備(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200) -> bool:
        """連接遠端設備"""
        self.port = port
        self.baudrate = baudrate
        return self.connect()

    def 檢查遠端配置(self) -> Dict[str, any]:
        """檢查所有遠端配置"""
        results = {}
        for file_path, expected_content in self.TARGET_CONFIGS.items():
            results[file_path] = self.check_file_config(file_path, expected_content)
        return results

    def 修正遠端配置(self) -> bool:
        """修正所有遠端配置"""
        all_success = True
        for file_path, expected_content in self.TARGET_CONFIGS.items():
            if not self.fix_file_config(file_path, expected_content):
                all_success = False
        return all_success

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
