"""
UART 日誌解析器模組 - SerialLogParser

透過 UART (/dev/ttyUSB0) 讀取系統日誌，解析語音播放狀態。

主要功能:
    - 監控 UART 輸出的日誌訊息
    - 檢測 "Playing audio file: xxx.mp3" 和 "Finished playing xxx.mp3"
    - 提供非阻塞的背景監控機制
    - 記錄播放歷史和狀態

使用場景:
    - 檢測語音助手是否開始播放回應
    - 檢測語音助手是否完成播放
    - 追蹤播放的音檔名稱

Robot Framework 使用範例:
    *** Settings ***
    Library    libraries/multimodal_detection/SerialLogParser.py

    *** Test Cases ***
    檢測語音播放
        初始化串列埠監控器    /dev/ttyUSB0    115200
        啟動背景監控
        Sleep    5s  # 執行會觸發語音播放的操作
        ${detected}    ${filename}=    檢查是否有播放記錄
        Should Be True    ${detected}
        Log    檢測到播放: ${filename}
        停止背景監控
"""

import threading
import time
import re
import os
from typing import Optional, Tuple, List, Dict
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# 從 .env 檔案載入環境變數
load_dotenv()

# 串列埠通訊
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial 未安裝，UART 功能將不可用。請執行: pip install pyserial")


class SerialLogParser:
    """
    UART 日誌解析器類別

    透過串列埠讀取系統日誌，解析語音播放狀態。

    Attributes:
        port (str): 串列埠路徑（如 /dev/ttyUSB0）
        baudrate (int): 鮑率（預設 115200）
        serial_conn (serial.Serial): 串列埠連線物件
        monitoring (bool): 是否正在監控
        monitor_thread (threading.Thread): 背景監控執行緒
        play_events (List[Dict]): 播放事件記錄
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.3.0'  # v1.3.0: 新增完整日誌記錄功能

    # 正規表達式模式
    # 支援兩種格式:
    # 1. "Playing audio file: xxx.mp3"
    # 2. "Playing voice command reply: /path/to/xxx.mp3"
    PATTERN_PLAYING = re.compile(r'Playing (?:audio file|voice command reply):\s+(.+\.mp3)')
    PATTERN_FINISHED = re.compile(r'Finished playing\s+(.+\.mp3)')

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        """
        初始化 UART 日誌解析器

        Args:
            port: 串列埠路徑。若為 None，則從環境變數 `UART_PORT` 讀取，預設為 '/dev/ttyUSB0'。
            baudrate: 鮑率（預設 115200）
        """
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial 未安裝，無法使用 UART 功能")

        self.port = port if port is not None else os.getenv('UART_PORT', '/dev/ttyUSB0')
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.play_events: List[Dict[str, any]] = []
        self.raw_logs: List[Dict[str, any]] = []  # v1.3.0: 保存所有原始日誌
        self._lock = threading.Lock()

        logger.info(f"初始化 UART 日誌解析器 (v{self.ROBOT_LIBRARY_VERSION})")
        logger.info(f"串列埠: {self.port} (來源: {'參數' if port else '環境變數或預設值'}), 鮑率: {self.baudrate}")

    def connect(self, auto_validate: bool = True) -> bool:
        """
        連接串列埠

        Args:
            auto_validate: 是否自動驗證並修正遠端配置（預設 True）

        Returns:
            是否成功連接
        """
        if self.serial_conn and self.serial_conn.is_open:
            logger.warning("串列埠已連接")
            return True

        try:
            # 如果需要自動驗證，先不要開啟連接，或者先關閉連接
            # 因為 RemoteSystemConfigValidator 會自己開啟連接
            if auto_validate:
                if self.serial_conn and self.serial_conn.is_open:
                    self.serial_conn.close()
                
                logger.info("開始驗證遠端系統配置...")
                from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

                validator = RemoteSystemConfigValidator(self.port, self.baudrate)
                result = validator.validate_uart_setup()

                if result['error_message']:
                    logger.error(f"配置驗證失敗: {result['error_message']}")
                    return False

                if result['needs_reboot']:
                    logger.warning("")
                    logger.warning("=" * 60)
                    logger.warning("⚠️  配置已修正，但需要重開機遠端設備才能生效")
                    logger.warning("=" * 60)
                    logger.warning(f"請執行: {result['reboot_command']}")
                    logger.warning("重開機後，請重新執行測試")
                    logger.warning("=" * 60)
                    return False

                if result['config_ok']:
                    logger.info("✓ 遠端配置正確，可以開始監控")

            # 驗證完成後，(重新)開啟連接供 Parser 使用
            if not self.serial_conn or not self.serial_conn.is_open:
                logger.info(f"嘗試連接串列埠: {self.port}")
                self.serial_conn = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=1,  # 讀取超時 1 秒
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False
                )
                # 嘗試清除 DTR/RTS
                self.serial_conn.dtr = False
                self.serial_conn.rts = False
                logger.info(f"✓ 串列埠連接成功: {self.port}")
            
            return True
        except Exception as e:
            logger.error(f"串列埠連接失敗: {e}")
            return False

    def disconnect(self):
        """關閉串列埠連接"""
        if self.monitoring:
            self.stop_monitoring()

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("串列埠已關閉")

    def start_monitoring(self) -> bool:
        """
        啟動背景監控

        Returns:
            是否成功啟動
        """
        if self.monitoring:
            logger.warning("背景監控已在運行中")
            return True

        if not self.serial_conn or not self.serial_conn.is_open:
            logger.error("串列埠未連接，無法啟動監控")
            return False

        logger.info("=" * 60)
        logger.info("🚀 啟動 UART 背景監控...")

        # 清空之前的事件記錄和原始日誌
        with self._lock:
            self.play_events.clear()
            self.raw_logs.clear()  # v1.3.0: 清空原始日誌
            
        # 清空硬體輸入緩衝區，避免讀取到之前的殘留資料 (如驗證過程的輸出)
        if self.serial_conn:
            self.serial_conn.reset_input_buffer()

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✓ UART 背景監控已啟動")
        return True

    def stop_monitoring(self):
        """停止背景監控"""
        if not self.monitoring:
            logger.warning("背景監控未運行")
            return

        logger.info("🛑 停止 UART 背景監控...")
        self.monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
            logger.info("✓ UART 背景監控已停止")

    def _monitor_loop(self):
        """背景監控執行緒主迴圈"""
        logger.info("[監控執行緒] 開始監控 UART 輸出...")

        while self.monitoring:
            try:
                if self.serial_conn.in_waiting > 0:
                    # 讀取一行
                    line = self.serial_conn.readline()

                    try:
                        line_str = line.decode('utf-8', errors='ignore').strip()
                    except:
                        line_str = line.decode('latin-1', errors='ignore').strip()

                    if line_str:
                        # 解析日誌
                        self._parse_log_line(line_str)
                else:
                    # 沒有資料時短暫休息
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"[監控執行緒] 讀取錯誤: {e}")
                time.sleep(0.5)

        logger.info("[監控執行緒] 監控結束")

    def _parse_log_line(self, line: str):
        """
        解析日誌行

        Args:
            line: 日誌字串
        """
        # v1.3.0: 保存所有原始日誌（包含時間戳記）
        raw_log_entry = {
            'timestamp': time.time(),
            'line': line
        }
        with self._lock:
            self.raw_logs.append(raw_log_entry)

        # 檢測 "Playing audio file: xxx.mp3"
        match_playing = self.PATTERN_PLAYING.search(line)
        if match_playing:
            filename = match_playing.group(1)
            event = {
                'type': 'playing',
                'filename': filename,
                'timestamp': time.time(),
                'raw_line': line
            }
            with self._lock:
                self.play_events.append(event)
            logger.info(f"[UART] 📢 檢測到播放: {filename}")
            return

        # 檢測 "Finished playing xxx.mp3"
        match_finished = self.PATTERN_FINISHED.search(line)
        if match_finished:
            filename = match_finished.group(1)
            event = {
                'type': 'finished',
                'filename': filename,
                'timestamp': time.time(),
                'raw_line': line
            }
            with self._lock:
                self.play_events.append(event)
            logger.info(f"[UART] ✓ 檢測到完成: {filename}")
            return

    def check_playing_detected(self, timeout: float = 10.0) -> Tuple[bool, Optional[str]]:
        """
        檢查是否檢測到播放事件

        Args:
            timeout: 超時時間（秒）

        Returns:
            (是否檢測到, 檔案名稱)
        """
        start_time = time.time()
        logger.info(f"等待播放事件... (超時: {timeout}s)")

        while time.time() - start_time < timeout:
            with self._lock:
                for event in self.play_events:
                    if event['type'] == 'playing':
                        filename = event['filename']
                        logger.info(f"✓ 檢測到播放事件: {filename}")
                        return True, filename

            time.sleep(0.1)

        logger.warning(f"✗ 超時 {timeout}s，未檢測到播放事件")
        return False, None

    def check_finished_detected(self, timeout: float = 10.0) -> Tuple[bool, Optional[str]]:
        """
        檢查是否檢測到完成事件

        Args:
            timeout: 超時時間（秒）

        Returns:
            (是否檢測到, 檔案名稱)
        """
        start_time = time.time()
        logger.info(f"等待完成事件... (超時: {timeout}s)")

        while time.time() - start_time < timeout:
            with self._lock:
                for event in self.play_events:
                    if event['type'] == 'finished':
                        filename = event['filename']
                        logger.info(f"✓ 檢測到完成事件: {filename}")
                        return True, filename

            time.sleep(0.1)

        logger.warning(f"✗ 超時 {timeout}s，未檢測到完成事件")
        return False, None

    def get_all_events(self) -> List[Dict]:
        """
        取得所有事件記錄

        Returns:
            事件記錄列表
        """
        with self._lock:
            return self.play_events.copy()

    def get_raw_logs(self) -> List[Dict]:
        """
        取得所有原始日誌記錄 (v1.3.0 新增)

        Returns:
            原始日誌記錄列表，每個項目包含 timestamp 和 line
        """
        with self._lock:
            return self.raw_logs.copy()

    def clear_events(self):
        """清空事件記錄和原始日誌"""
        with self._lock:
            self.play_events.clear()
            self.raw_logs.clear()  # v1.3.0: 同時清空原始日誌
        logger.info("事件記錄和原始日誌已清空")

    # ===========================================
    # Robot Framework 關鍵字
    # ===========================================

    def 初始化串列埠監控器(self, port: Optional[str] = None, baudrate: int = 115200, auto_validate: bool = True):
        """
        初始化串列埠監控器並連接

        Args:
            port: 串列埠路徑。若為 None，則從環境變數 `UART_PORT` 讀取，預設為 '/dev/ttyUSB0'。
            baudrate: 鮑率
            auto_validate: 是否自動驗證並修正遠端配置（預設 True）

        Returns:
            是否成功
        """
        self.port = port if port is not None else os.getenv('UART_PORT', '/dev/ttyUSB0')
        self.baudrate = baudrate
        logger.info(f"重新初始化串列埠: {self.port} (來源: {'參數' if port else '環境變數或預設值'}), 鮑率: {self.baudrate}")
        return self.connect(auto_validate=auto_validate)

    def 啟動背景監控(self) -> bool:
        """啟動背景監控"""
        return self.start_monitoring()

    def 停止背景監控(self):
        """停止背景監控"""
        self.stop_monitoring()

    def 檢查是否有播放記錄(self, timeout: float = 10.0) -> Tuple[bool, str]:
        """
        檢查是否有播放記錄

        Args:
            timeout: 超時時間（秒）

        Returns:
            (是否檢測到, 檔案名稱)
        """
        detected, filename = self.check_playing_detected(timeout)
        return detected, filename or ""

    def 檢查是否播放完成(self, timeout: float = 10.0) -> Tuple[bool, str]:
        """
        檢查是否播放完成

        Args:
            timeout: 超時時間（秒）

        Returns:
            (是否檢測到, 檔案名稱)
        """
        detected, filename = self.check_finished_detected(timeout)
        return detected, filename or ""

    def 取得所有播放事件(self) -> List[Dict]:
        """取得所有播放事件記錄"""
        return self.get_all_events()

    def 清空事件記錄(self):
        """清空事件記錄"""
        self.clear_events()

    def 斷開串列埠(self):
        """斷開串列埠連接"""
        self.disconnect()

    def 驗證遠端系統配置(self) -> Dict[str, any]:
        """
        驗證遠端系統 UART 配置是否正確

        檢查遠端設備的 /etc/init.d/emmc 配置，確保日誌正確輸出到 UART。
        如果配置錯誤，會自動修正並提示需要重開機。

        Returns:
            驗證結果字典：
                - config_ok (bool): 配置是否正確
                - fixed (bool): 是否已修正
                - needs_reboot (bool): 是否需要重開機
                - reboot_command (str): 重開機命令
                - error_message (str): 錯誤訊息
                - details (dict): 詳細資訊

        Example:
            | ${result}= | 驗證遠端系統配置 |
            | Should Be True | ${result['config_ok']} or ${result['fixed']} |
            | Run Keyword If | ${result['needs_reboot']} | Log | 請執行: ${result['reboot_command']} |
        """
        from libraries.multimodal_detection.RemoteSystemConfigValidator import RemoteSystemConfigValidator

        logger.info(f"手動驗證遠端系統配置 (Port: {self.port}, Baudrate: {self.baudrate})")
        validator = RemoteSystemConfigValidator(self.port, self.baudrate)
        result = validator.validate_uart_setup()

        # 記錄結果
        if result['config_ok']:
            logger.info("✓ 遠端配置正確")
        elif result['fixed']:
            logger.warning(f"⚠️  配置已修正，需要重開機: {result['reboot_command']}")
        elif result['error_message']:
            logger.error(f"✗ 配置驗證失敗: {result['error_message']}")

        return result


if __name__ == "__main__":
    # 測試腳本
    print("=" * 50)
    print("SerialLogParser 測試腳本")
    print("=" * 50)
    print("注意: 此腳本需要連接到實際的 UART 設備才能正常運作。")
    print("UART Port 可透過 .env 檔案中的 `UART_PORT` 變數設定。")

    parser = None
    try:
        # 建立解析器實例 (不帶參數，將使用 .env 或預設值)
        parser = SerialLogParser(baudrate=115200)

        # 連接串列埠
        if not parser.connect():
            print(f"❌ 無法連接串列埠 {parser.port}")
            exit(1)

        print(f"✓ 串列埠連接成功: {parser.port}")

        # 啟動監控
        if not parser.start_monitoring():
            print("❌ 無法啟動監控")
            exit(1)

        print("✓ 監控已啟動，等待 20 秒...")
        print("   請在此期間觸發語音播放")

        # 等待並檢測
        detected, filename = parser.check_playing_detected(timeout=20.0)

        if detected:
            print(f"✓ 檢測到播放: {filename}")

            # 繼續等待完成事件
            print("等待播放完成...")
            finished, fin_filename = parser.check_finished_detected(timeout=10.0)

            if finished:
                print(f"✓ 播放完成: {fin_filename}")
        else:
            print("✗ 未檢測到播放事件")

        # 顯示所有事件
        events = parser.get_all_events()
        print(f"\n共記錄 {len(events)} 個事件:")
        for event in events:
            print(f"  - {event['type']}: {event['filename']} (時間: {event['timestamp']:.2f})")

    except ImportError as e:
        print(f"❌ 缺少必要的套件: {e}")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if parser:
            try:
                parser.stop_monitoring()
                parser.disconnect()
            except Exception as e:
                logger.warning(f"清理時發生錯誤: {e}")

    print("\n" + "=" * 50)
    print("測試腳本結束")
    print("=" * 50)
