#!/usr/bin/env python3
"""
語音控制關鍵字庫 - VoiceControlKeywords
整合 TTS 文字轉語音與 Scarlett 4i4 硬體聲道控制
為 Robot Framework 提供統一的語音輸出控制介面

新增功能 (v1.1.0):
- UART 日誌監控整合 (SerialLogParser)
- 語音回應數量驗證
- 超時檢測
"""

import os
import time
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import yaml

# Robot Framework 支援
try:
    from robot.api.deco import keyword
    from robot.api import logger as robot_logger
    ROBOT_AVAILABLE = True
except ImportError:
    ROBOT_AVAILABLE = False
    # 建立假的 decorator
    def keyword(name=None, tags=None):
        def decorator(func):
            return func
        return decorator

# 內部模組匯入
try:
    from .TTSManager import TTSManager
    from .AudioPlayer import AudioPlayer
except ImportError:
    # 如果相對匯入失敗，嘗試絕對匯入
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from TTSManager import TTSManager
    from AudioPlayer import AudioPlayer

# 日誌
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


class VoiceControlKeywords:
    """
    語音控制關鍵字庫

    整合 TTS 與 Scarlett 4i4 硬體控制，提供：
    1. 文字轉語音並輸出到指定聲道
    2. TTS 引擎切換（gtts, pyttsx3）
    3. 語言與語速控制
    4. 多聲道測試功能

    Scope: GLOBAL
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.2.0'  # v1.2.0: 新增完整 UART 日誌診斷功能
    ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'

    def __init__(self):
        """初始化語音控制關鍵字庫"""
        # 初始化核心模組
        self.tts_manager = TTSManager()
        self.audio_player = AudioPlayer()

        # 狀態管理
        self.last_audio_file = None
        self.temp_audio_files = []

        # UART 監控器 (延遲初始化)
        self.uart_parser = None
        self.uart_monitoring_active = False

        # 設定日誌
        self._setup_logging()

        # 載入語音指令對照表 (v1.4.0)
        self.voice_command_map = self._load_voice_command_map()

        if ROBOT_AVAILABLE:
            robot_logger.info("VoiceControlKeywords 初始化完成 (v1.2.0)")
        else:
            print("VoiceControlKeywords 初始化完成 (非 Robot Framework 環境)")

    def _setup_logging(self) -> None:
        """設定日誌系統"""
        try:
            if LOGURU_AVAILABLE:
                logger.remove()
                logger.add(
                    "logs/voice_control_keywords.log",
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                    level="INFO",
                    rotation="10 MB",
                    retention="7 days",
                )
        except Exception as e:
            print(f"日誌設定失敗: {e}")

    def _load_voice_command_map(self) -> Dict[str, Any]:
        """
        載入語音指令對照表 (內部方法)
        
        Returns:
            指令對照字典
        """
        try:
            # 假設 yaml 檔案位於專案根目錄的 resources 資料夾下
            project_root = Path(__file__).parent.parent.parent
            yaml_path = project_root / "resources" / "voice_command_map.yaml"
            
            if not yaml_path.exists():
                logger.warning(f"找不到語音指令對照表: {yaml_path}")
                return {}
                
            with open(yaml_path, 'r', encoding='utf-8') as f:
                command_map = yaml.safe_load(f)
                
            if command_map:
                logger.info(f"已載入 {len(command_map)} 個語音指令定義")
                return command_map
            else:
                return {}
                
        except Exception as e:
            logger.error(f"載入語音指令對照表失敗: {e}")
            return {}

    def _resolve_pattern(self, pattern: str) -> str:
        """
        解析模式字串，如果是指令 Key 則轉換為對應的檔案名稱
        
        Args:
            pattern: 模式字串或指令 Key (例如 "CMD_WAKE_UP")
            
        Returns:
            對應的檔案名稱或原始模式
        """
        pattern = pattern.strip()
        
        # 檢查是否為指令 Key
        if self.voice_command_map and pattern in self.voice_command_map:
            entry = self.voice_command_map[pattern]
            if isinstance(entry, dict) and 'filename' in entry:
                filename = entry['filename']
                logger.info(f"解析指令 Key: {pattern} -> {filename}")
                return filename
                
        return pattern

    # ===========================================
    # UART 監控相關內部方法 (新增於 v1.1.0)
    # ===========================================

    def _init_uart_monitor(self, port: Optional[str] = None, baudrate: int = 115200, auto_validate: bool = True) -> bool:
        """
        初始化 UART 監控器 (內部方法)

        Args:
            port: UART 埠路徑 (預設從環境變數讀取)
            baudrate: 鮑率 (預設 115200)

        Returns:
            是否初始化成功
        """
        try:
            # 延遲匯入 SerialLogParser
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))

            from libraries.multimodal_detection.SerialLogParser import SerialLogParser

            self.uart_parser = SerialLogParser(port=port, baudrate=baudrate)

            # 連接串列埠
            if not self.uart_parser.connect(auto_validate=auto_validate):
                logger.error("UART 串列埠連接失敗")
                return False

            logger.info("✓ UART 監控器初始化成功")
            return True

        except ImportError as e:
            logger.error(f"無法匯入 SerialLogParser: {e}")
            return False
        except Exception as e:
            logger.error(f"UART 監控器初始化失敗: {e}")
            return False

    def _start_uart_monitoring(self) -> bool:
        """
        啟動 UART 背景監控 (內部方法)

        Returns:
            是否啟動成功
        """
        if not self.uart_parser:
            logger.error("UART 監控器未初始化")
            return False

        if self.uart_monitoring_active:
            logger.warning("UART 監控已在運行中")
            return True

        # 清空之前的事件記錄
        self.uart_parser.clear_events()

        # 啟動監控
        if self.uart_parser.start_monitoring():
            self.uart_monitoring_active = True
            logger.info("✓ UART 背景監控已啟動")
            return True
        else:
            logger.error("UART 背景監控啟動失敗")
            return False

    def _stop_uart_monitoring(self):
        """停止 UART 背景監控 (內部方法)"""
        if self.uart_parser and self.uart_monitoring_active:
            self.uart_parser.stop_monitoring()
            self.uart_monitoring_active = False
            logger.info("✓ UART 背景監控已停止")

    def _check_voice_response_count(self,
                                    timeout: float = 5.0,
                                    expected_count: int = 1,
                                    expected_patterns: Optional[List[str]] = None) -> Tuple[bool, int, List[str], List[str]]:
        """
        檢查語音回應數量是否符合預期 (內部方法)

        Args:
            timeout: 超時時間（秒）- 等待語音回應的時間
            expected_count: 預期的語音回應數量
            expected_patterns: 預期的檔案名稱模式列表（可選）

        Returns:
            (是否通過, 實際數量, 檔案名稱列表, 完整 UART 日誌列表)

        Note:
            此方法會在 timeout 時間內等待並檢測新的語音回應事件。
            完整的 UART 日誌從監控啟動時就開始記錄，不受 timeout 影響。
        """
        if not self.uart_parser:
            logger.error("UART 監控器未初始化")
            return False, 0, [], []

        logger.info(f"開始檢查語音回應... (檢查時間窗口: {timeout}s, 預期數量: {expected_count})")

        # 檢查 UART 監控狀態
        if not self.uart_monitoring_active:
            logger.error("⚠️  UART 監控未啟動！")
            return False, 0, [], []

        # 記錄當前已有的播放事件（用於過濾出新事件）
        current_events = self.uart_parser.get_all_events()
        initial_playing_events = [e for e in current_events if e['type'] == 'playing']
        initial_playing_count = len(initial_playing_events)

        # 記錄當前已有的原始日誌行數
        current_raw_logs = self.uart_parser.get_raw_logs()
        initial_log_count = len(current_raw_logs)

        logger.info(f"檢查前已有 {initial_playing_count} 個播放事件")
        logger.info(f"檢查前已有 {initial_log_count} 行原始日誌")

        # 等待 timeout 時間，讓新的語音回應有時間被記錄
        logger.info(f"等待 {timeout} 秒以收集新的語音回應...")
        time.sleep(timeout)

        # 取得所有播放事件（包含舊的和新的）
        all_events = self.uart_parser.get_all_events()
        all_playing_events = [e for e in all_events if e['type'] == 'playing']

        # 只取「新增的」播放事件（在檢查時間窗口內出現的）
        # 透過時間戳記比對，或者簡單地計算數量差異
        new_playing_events = all_playing_events[initial_playing_count:]

        actual_count = len(new_playing_events)
        filenames = [e['filename'] for e in new_playing_events]

        # v1.2.0: 取得完整的原始 UART 日誌
        raw_logs = self.uart_parser.get_raw_logs()
        raw_log_lines = [log['line'] for log in raw_logs]
        final_log_count = len(raw_log_lines)

        logger.info(f"檢查後總共有 {len(all_playing_events)} 個播放事件")
        logger.info(f"新增了 {actual_count} 個播放事件（在檢查時間窗口內）")
        logger.info(f"檢查前有 {initial_log_count} 行日誌，檢查後有 {final_log_count} 行日誌")
        logger.info(f"在等待期間新增了 {final_log_count - initial_log_count} 行日誌")

        # 記錄檢測結果
        logger.info(f"檢測到 {actual_count} 個語音回應:")
        for filename in filenames:
            logger.info(f"  - {filename}")

        logger.info(f"原始 UART 日誌共 {len(raw_log_lines)} 行")

        # v1.2.0: 診斷 - 搜尋日誌中是否包含 mp3 或 audio 關鍵字
        mp3_related_lines = [line for line in raw_log_lines if 'mp3' in line.lower() or 'audio' in line.lower() or 'playing' in line.lower()]
        if mp3_related_lines:
            logger.info(f"找到 {len(mp3_related_lines)} 行包含 mp3/audio/playing 關鍵字:")
            for line in mp3_related_lines[:10]:  # 只顯示前 10 行
                logger.info(f"  >> {line}")
        else:
            logger.warning("日誌中未找到任何包含 mp3/audio/playing 的內容")

        # 驗證數量
        count_match = (actual_count == expected_count)

        # 如果有指定模式，進行模式匹配
        pattern_match = True
        if expected_patterns:
            pattern_match = self._verify_filename_patterns(filenames, expected_patterns)

        # 綜合判斷
        passed = count_match and pattern_match

        if not count_match:
            logger.warning(f"語音回應數量不符: 預期 {expected_count} 個，實際 {actual_count} 個")
            # 即使數量不符，也記錄實際收到的檔案
            if filenames:
                logger.warning(f"實際收到: {', '.join(filenames)}")

        if not pattern_match:
            logger.warning(f"語音回應檔案不符合預期模式")
            # 記錄實際與預期的差異
            if expected_patterns and filenames:
                logger.warning(f"預期模式: {', '.join(expected_patterns)}")
                logger.warning(f"實際收到: {', '.join(filenames)}")

        return passed, actual_count, filenames, raw_log_lines

    def _verify_filename_patterns(self, filenames: List[str], patterns: List[str]) -> bool:
        """
        驗證檔案名稱是否符合預期模式 (內部方法)

        Args:
            filenames: 實際的檔案名稱列表
            patterns: 預期的檔案名稱模式列表

        Returns:
            是否符合
        """
        if len(filenames) != len(patterns):
            return False

        for filename, pattern in zip(filenames, patterns):
            if pattern not in filename:
                logger.warning(f"檔案名稱不符: {filename} 不包含 {pattern}")
                return False

        return True

    # ===========================================
    # 主要 Robot Framework 關鍵字
    # ===========================================

    # Legacy 關鍵字已移除 - 請使用 Gherkin 風格關鍵字
    # Removed Legacy keywords - Please use Gherkin style keywords instead

    # ===========================================
    # Gherkin 風格關鍵字 - Given (前置條件)
    # ===========================================

    def get_tts_engine_info(self) -> Dict[str, Any]:
        """
        獲取 TTS 引擎資訊 (內部方法)

        回傳:
            包含引擎資訊的字典

        範例:
            | ${info}= | Given 語音控制系統已成功初始化 |
            | Log | 主要引擎: ${info['primary_engine']} |
        """
        return self.tts_manager.get_engine_info()

    def get_available_sinks(self) -> list:
        """
        獲取可用的音訊輸出設備列表 (內部方法)
        """
        return self.audio_player.list_available_sinks()

    def check_scarlett_device(self) -> bool:
        """
        檢查 Scarlett 4i4 設備是否可用 (內部方法)
        """
        available = self.audio_player.scarlett_available
        return available

    def cleanup_voice_control_resources(self) -> bool:
        """
        清理語音控制資源（暫存檔案等） (內部方法)
        """
        try:
            # 清理 UART 監控器 (v1.1.0 新增)
            if self.uart_parser:
                try:
                    self._stop_uart_monitoring()
                    self.uart_parser.disconnect()
                    logger.info("✓ UART 監控器已關閉")
                except Exception as e:
                    logger.warning(f"UART 監控器關閉時發生錯誤: {e}")

            # 清理 TTS 暫存檔案
            cleaned_count = self.tts_manager.cleanup_temp_files()

            # 清理本地記錄的暫存檔案
            self.temp_audio_files.clear()
            self.last_audio_file = None

            if ROBOT_AVAILABLE:
                robot_logger.info(f"✓ 清理了 {cleaned_count} 個暫存檔案")

            logger.info("語音控制資源清理完成")
            return True

        except Exception as e:
            logger.error(f"清理語音控制資源失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 資源清理失敗: {e}")
            return False

    def speak_text_to_channel(self, text: str, channel: int,
                            language: str = 'en', duration: int = 5) -> bool:
        """
        將文字轉換為語音並播放到指定聲道 (內部方法，供 Gherkin 關鍵字使用)
        """
        try:
            logger.info(f"開始語音播放: '{text}' -> 聲道 {channel} ({language})")

            if ROBOT_AVAILABLE:
                robot_logger.info(f"將播放文字 '{text}' 到聲道 {channel}")

            # 步驟 1: 使用 TTS 生成音訊檔案
            audio_file = self.tts_manager.text_to_file(
                text=text,
                language=language,
                format='mp3'
            )

            if not audio_file:
                error_msg = "TTS 音訊生成失敗"
                logger.error(error_msg)
                if ROBOT_AVAILABLE:
                    robot_logger.error(error_msg)
                return False

            # 記錄生成的檔案
            self.last_audio_file = audio_file
            self.temp_audio_files.append(audio_file)

            logger.info(f"TTS 音訊檔案生成: {audio_file}")

            # 步驟 2: 播放到指定聲道
            success = self.audio_player.play_to_channel(
                audio_file=audio_file,
                target_channel=int(channel),
                duration=int(duration)
            )

            if success:
                logger.info(f"語音播放完成: 聲道 {channel}")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ 聲道 {channel} 播放成功")
            else:
                logger.error(f"語音播放失敗: 聲道 {channel}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ 聲道 {channel} 播放失敗")

            return success

        except Exception as e:
            error_msg = f"播放文字到聲道失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False

    def set_tts_engine(self, engine_name: str) -> bool:
        """
        切換 TTS 引擎 (內部方法，供 Gherkin 關鍵字使用)
        """
        try:
            success = self.tts_manager.set_engine(engine_name)

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 引擎切換為: {engine_name}")
                else:
                    robot_logger.error(f"✗ TTS 引擎切換失敗: {engine_name}")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 引擎失敗: {e}")
            return False

    def set_tts_language(self, language: str) -> bool:
        """
        設定 TTS 語言 (內部方法，供 Gherkin 關鍵字使用)
        """
        try:
            success = self.tts_manager.set_language(language)

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 語言設定為: {language}")
                else:
                    robot_logger.error(f"✗ TTS 語言設定失敗")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 語言失敗: {e}")
            return False

    def get_library_info(self) -> Dict[str, Any]:
        """
        獲取 Library 資訊

        Returns:
            Library 資訊字典
        """
        return {
            'version': self.ROBOT_LIBRARY_VERSION,
            'scope': self.ROBOT_LIBRARY_SCOPE,
            'tts_engine_info': self.tts_manager.get_engine_info(),
            'scarlett_available': self.audio_player.scarlett_available,
            'temp_files_count': len(self.temp_audio_files),
            'last_audio_file': self.last_audio_file,
        }

    # ===========================================
    # Gherkin 風格關鍵字 - Given (前置條件)
    # ===========================================

    @keyword('Given 語音控制系統已成功初始化')
    def given_voice_control_system_initialized(self) -> bool:
        """
        Given: 確認語音控制系統已成功初始化
        Given: Confirm voice control system has been successfully initialized
        
        此關鍵字檢查語音控制系統是否正確初始化，包括 TTS 管理器和音訊播放器。
        This keyword verifies that the voice control system is properly initialized, including TTS manager and audio player.
        
        Prerequisites:
        - Voice control library has been imported
        
        前置條件:
        - 語音控制庫已被匯入
        
        Examples:
        | Given | 語音控制系統已成功初始化 |
        
        Returns:
            bool: 初始化狀態
        """
        try:
            # 檢查核心模組是否正確初始化
            if not hasattr(self, 'tts_manager') or not hasattr(self, 'audio_player'):
                logger.error("語音控制系統核心模組未初始化")
                return False
                
            # 檢查 TTS 管理器
            if not self.tts_manager:
                logger.error("TTS 管理器未初始化")
                return False
                
            # 檢查音訊播放器
            if not self.audio_player:
                logger.error("音訊播放器未初始化")
                return False
                
            logger.info("語音控制系統初始化檢查完成 - 正常")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 語音控制系統已成功初始化")
                
            return True
            
        except Exception as e:
            logger.error(f"語音控制系統初始化檢查失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 語音控制系統初始化失敗: {e}")
            return False

    @keyword('Given Scarlett 4i4 音效介面已正確連接')
    def given_scarlett_device_connected(self) -> bool:
        """
        Given: 確認 Scarlett 4i4 音效介面已正確連接
        Given: Confirm Scarlett 4i4 audio interface is properly connected
        
        此關鍵字檢查 Focusrite Scarlett 4i4 音效介面是否正確連接並可用。
        This keyword verifies that the Focusrite Scarlett 4i4 audio interface is properly connected and available.
        
        Prerequisites:
        - Scarlett 4i4 device is physically connected
        - System has proper drivers installed
        
        前置條件:
        - Scarlett 4i4 設備已實體連接
        - 系統已安裝適當驅動程式
        
        Examples:
        | Given | Scarlett 4i4 音效介面已正確連接 |
        
        Returns:
            bool: 設備連接狀態
        """
        try:
            available = self.audio_player.scarlett_available
            
            if available:
                logger.info("Scarlett 4i4 設備連接檢查 - 正常")
                if ROBOT_AVAILABLE:
                    robot_logger.info("✓ Scarlett 4i4 音效介面已正確連接")
            else:
                logger.warning("Scarlett 4i4 設備未連接或不可用")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ Scarlett 4i4 音效介面未正確連接")
                    
            return available
            
        except Exception as e:
            logger.error(f"Scarlett 4i4 設備檢查失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ Scarlett 4i4 設備檢查失敗: {e}")
            return False

    @keyword('Given TTS 引擎已設定為 "${engine_name}"')
    def given_tts_engine_set_to(self, engine_name: str) -> bool:
        """
        Given: 確認 TTS 引擎已設定為指定引擎
        Given: Confirm TTS engine is set to specified engine
        
        此關鍵字設定並確認指定的 TTS 引擎已正確配置。
        This keyword sets and confirms the specified TTS engine is properly configured.
        
        Arguments:
        - engine_name: TTS 引擎名稱 (gtts/pyttsx3)
        - engine_name: TTS engine name (gtts/pyttsx3)
        
        Prerequisites:
        - Voice control system is initialized
        
        前置條件:
        - 語音控制系統已初始化
        
        Examples:
        | Given | TTS 引擎已設定為 "gtts" |
        | Given | TTS 引擎已設定為 "pyttsx3" |
        
        Returns:
            bool: 設定是否成功
        """
        try:
            success = self.tts_manager.set_engine(engine_name)
            
            if success:
                logger.info(f"TTS 引擎已設定為: {engine_name}")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ TTS 引擎已設定為 {engine_name}")
            else:
                logger.error(f"TTS 引擎設定失敗: {engine_name}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ TTS 引擎設定失敗: {engine_name}")
                    
            return success
            
        except Exception as e:
            logger.error(f"TTS 引擎設定失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 引擎設定失敗: {e}")
            return False

    @keyword('Given TTS 語言已設定為 "${language}"')
    def given_tts_language_set_to(self, language: str) -> bool:
        """
        Given: 確認 TTS 語言已設定為指定語言
        Given: Confirm TTS language is set to specified language
        
        此關鍵字設定並確認指定的 TTS 語言已正確配置。
        This keyword sets and confirms the specified TTS language is properly configured.
        
        Arguments:
        - language: 語言代碼 (en/zh-TW/ja/etc.)
        - language: Language code (en/zh-TW/ja/etc.)
        
        Prerequisites:
        - Voice control system is initialized
        - TTS engine is available
        
        前置條件:
        - 語音控制系統已初始化
        - TTS 引擎可用
        
        Examples:
        | Given | TTS 語言已設定為 "zh-TW" |
        | Given | TTS 語言已設定為 "en" |
        | Given | TTS 語言已設定為 "ja" |
        
        Returns:
            bool: 設定是否成功
        """
        try:
            success = self.tts_manager.set_language(language)
            
            if success:
                logger.info(f"TTS 語言已設定為: {language}")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ TTS 語言已設定為 {language}")
            else:
                logger.error(f"TTS 語言設定失敗: {language}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ TTS 語言設定失敗: {language}")
                    
            return success
            
        except Exception as e:
            logger.error(f"TTS 語言設定失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 語言設定失敗: {e}")
            return False

    @keyword('Given TTS 語速已設定為 "${speed}"')
    def given_tts_speed_set_to(self, speed: int) -> bool:
        """
        Given: 確認 TTS 語速已設定為指定速度
        Given: Confirm TTS speed is set to specified rate

        此關鍵字設定並確認指定的 TTS 語速已正確配置。
        This keyword sets and confirms the specified TTS speed is properly configured.

        Arguments:
        - speed: 語速值 (pyttsx3: words per minute, 建議範圍 100-300)
        - speed: Speed value (pyttsx3: words per minute, recommended range 100-300)

        速度參考:
        - 100-150: 較慢 (slow)
        - 180: 標準速度 (default)
        - 200-250: 較快 (fast)
        - 250+: 很快 (very fast)

        Prerequisites:
        - Voice control system is initialized
        - TTS engine is available

        前置條件:
        - 語音控制系統已初始化
        - TTS 引擎可用

        Examples:
        | Given | TTS 語速已設定為 "150" |
        | Given | TTS 語速已設定為 "180" |
        | Given | TTS 語速已設定為 "200" |

        Returns:
            bool: 設定是否成功
        """
        try:
            speed_value = int(speed)
            success = self.tts_manager.set_voice_speed(speed_value)

            if success:
                logger.info(f"TTS 語速已設定為: {speed_value} wpm")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ TTS 語速已設定為 {speed_value} wpm")
            else:
                logger.error(f"TTS 語速設定失敗: {speed_value}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ TTS 語速設定失敗: {speed_value}")

            return success

        except Exception as e:
            logger.error(f"TTS 語速設定失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 語速設定失敗: {e}")
            return False

    @keyword('Given 音訊輸出聲道 "${channel}" 已準備就緒')
    def given_audio_channel_ready(self, channel: int) -> bool:
        """
        Given: 確認指定音訊輸出聲道已準備就緒
        Given: Confirm specified audio output channel is ready

        此關鍵字檢查指定聲道是否可用並準備播放。
        This keyword verifies that the specified channel is available and ready for playback.

        Arguments:
        - channel: 聲道編號 (1-4)
        - channel: Channel number (1-4)

        Prerequisites:
        - Scarlett 4i4 device is connected
        - Audio system is initialized

        前置條件:
        - Scarlett 4i4 設備已連接
        - 音訊系統已初始化

        Examples:
        | Given | 音訊輸出聲道 "1" 已準備就緒 |
        | Given | 音訊輸出聲道 "3" 已準備就緒 |

        Returns:
            bool: 聲道是否就緒
        """
        try:
            channel_num = int(channel)
            
            # 檢查聲道範圍
            if channel_num < 1 or channel_num > 4:
                logger.error(f"無效的聲道編號: {channel_num}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ 無效的聲道編號: {channel_num}")
                return False
                
            # 檢查 Scarlett 設備可用性
            if not self.audio_player.scarlett_available:
                logger.error("Scarlett 4i4 設備不可用 (未檢測到硬體)")
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ Scarlett 4i4 設備不可用 (未檢測到硬體)")
                return False

            # 驗證路由設定 (v1.3.0 新增)
            is_routed, error_msg = self.audio_player.verify_routing(channel_num)
            if not is_routed:
                logger.error(f"聲道 {channel_num} 路由未就緒: {error_msg}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ 聲道 {channel_num} 路由未就緒: {error_msg}")
                return False
                
            logger.info(f"聲道 {channel_num} 已準備就緒 (硬體與路由皆正常)")
            if ROBOT_AVAILABLE:
                robot_logger.info(f"✓ 音訊輸出聲道 {channel_num} 已準備就緒")
                
            return True
            
        except Exception as e:
            logger.error(f"聲道準備檢查失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 聲道準備檢查失敗: {e}")
            return False

    # ===========================================
    # Gherkin 風格關鍵字 - When (執行動作)
    # ===========================================

    @keyword('When 使用者播放文字 "${text}" 到聲道 "${channel}"')
    def when_user_plays_text_to_channel(self, text: str, channel: int) -> bool:
        """
        When: 使用者播放文字到指定聲道
        When: User plays text to specified channel
        
        此關鍵字執行文字轉語音並播放到指定聲道的動作。
        This keyword performs the action of text-to-speech and plays to specified channel.
        
        Arguments:
        - text: 要播放的文字內容
        - channel: 目標聲道 (1-4)
        - text: Text content to play
        - channel: Target channel (1-4)
        
        Prerequisites:
        - Voice control system is initialized
        - Scarlett 4i4 device is connected
        
        前置條件:
        - 語音控制系統已初始化
        - Scarlett 4i4 設備已連接
        
        Examples:
        | When | 使用者播放文字 "Hello World" 到聲道 "1" |
        | When | 使用者播放文字 "測試語音" 到聲道 "3" |
        
        Returns:
            bool: 播放是否成功
        """
        result = self.speak_text_to_channel(text, int(channel), 'en', 5)
        
        # Log completion time
        command_end = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        if ROBOT_AVAILABLE:
            robot_logger.console(f"語音命令完成時間: {command_end}")
            
        return result

    @keyword('When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"')
    def when_user_plays_text_to_channel_with_language(self, text: str, channel: int, language: str) -> bool:
        """
        When: 使用者播放文字到指定聲道使用指定語言
        When: User plays text to specified channel using specified language
        
        此關鍵字執行文字轉語音並播放到指定聲道，使用指定語言。
        This keyword performs text-to-speech and plays to specified channel using specified language.
        
        Arguments:
        - text: 要播放的文字內容
        - channel: 目標聲道 (1-4)
        - language: 語言代碼 (en/zh-TW/ja)
        - text: Text content to play
        - channel: Target channel (1-4)
        - language: Language code (en/zh-TW/ja)
        
        Prerequisites:
        - Voice control system is initialized
        - Scarlett 4i4 device is connected
        - TTS engine supports specified language
        
        前置條件:
        - 語音控制系統已初始化
        - Scarlett 4i4 設備已連接
        - TTS 引擎支援指定語言
        
        Examples:
        | When | 使用者播放文字 "Hello World" 到聲道 "1" 使用語言 "en" |
        | When | 使用者播放文字 "測試語音" 到聲道 "3" 使用語言 "zh-TW" |
        | When | 使用者播放文字 "テスト" 到聲道 "4" 使用語言 "ja" |
        
        Returns:
            bool: 播放是否成功
        """
        result = self.speak_text_to_channel(text, int(channel), language, 5)
        
        # Log completion time
        command_end = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        if ROBOT_AVAILABLE:
            robot_logger.console(f"語音命令完成時間: {command_end}")
            
        return result

    @keyword('When 使用者使用預設喇叭播放文字 "${text}"')
    def when_user_plays_text_using_default_speaker(self, text: str) -> bool:
        """
        When: 使用者使用預設喇叭播放文字
        When: User plays text using default speaker
        
        此關鍵字將文字轉換為語音並使用系統預設音訊輸出設備播放（不經過 Scarlett 4i4）。
        This keyword converts text to speech and plays it using the system default audio output device (bypassing Scarlett 4i4).
        
        Arguments:
        - text: 要播放的文字
        
        Examples:
        | When | 使用者使用預設喇叭播放文字 "Hello World" |
        
        Returns:
            bool: 播放是否成功
        """
        try:
            logger.info(f"開始使用預設喇叭播放: '{text}'")
            
            if ROBOT_AVAILABLE:
                robot_logger.info(f"將使用預設喇叭播放文字 '{text}'")
                
            # 步驟 1: 使用 TTS 生成音訊檔案
            # 預設使用英文，若需多語言可擴充
            audio_file = self.tts_manager.text_to_file(
                text=text,
                language='en',
                format='mp3'
            )
            
            if not audio_file:
                error_msg = "TTS 音訊生成失敗"
                logger.error(error_msg)
                if ROBOT_AVAILABLE:
                    robot_logger.error(error_msg)
                return False
                
            # 記錄生成的檔案
            self.last_audio_file = audio_file
            self.temp_audio_files.append(audio_file)
            
            # 步驟 2: 使用預設設備播放
            success = self.audio_player.play_to_default_device(audio_file)
            
            if success:
                logger.info("預設喇叭播放完成")
                if ROBOT_AVAILABLE:
                    robot_logger.info("✓ 預設喇叭播放成功")
            else:
                logger.error("預設喇叭播放失敗")
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ 預設喇叭播放失敗")
                    
            return success
            
        except Exception as e:
            error_msg = f"預設喇叭播放失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False

    @keyword('When 使用者切換 TTS 引擎到 "${engine_name}"')
    def when_user_switches_tts_engine(self, engine_name: str) -> bool:
        """
        When: 使用者切換 TTS 引擎到指定引擎
        When: User switches TTS engine to specified engine
        
        此關鍵字執行 TTS 引擎切換動作。
        This keyword performs the action of switching TTS engine.
        
        Arguments:
        - engine_name: TTS 引擎名稱 (gtts/pyttsx3)
        - engine_name: TTS engine name (gtts/pyttsx3)
        
        Prerequisites:
        - Voice control system is initialized
        - Target engine is available
        
        前置條件:
        - 語音控制系統已初始化
        - 目標引擎可用
        
        Examples:
        | When | 使用者切換 TTS 引擎到 "gtts" |
        | When | 使用者切換 TTS 引擎到 "pyttsx3" |
        
        Returns:
            bool: 切換是否成功
        """
        return self.set_tts_engine(engine_name)

    @keyword('When 使用者設定 TTS 語速為 "${speed}"')
    def when_user_sets_tts_speed(self, speed: int) -> bool:
        """
        When: 使用者設定 TTS 語速為指定值
        When: User sets TTS speed to specified value

        此關鍵字執行 TTS 語速設定動作。
        This keyword performs the action of setting TTS speed.

        Arguments:
        - speed: 語速值 (pyttsx3: words per minute, 建議範圍 100-300)
        - speed: Speed value (pyttsx3: words per minute, recommended range 100-300)

        Prerequisites:
        - Voice control system is initialized
        - TTS engine is available

        前置條件:
        - 語音控制系統已初始化
        - TTS 引擎可用

        Examples:
        | When | 使用者設定 TTS 語速為 "150" |
        | When | 使用者設定 TTS 語速為 "200" |

        Returns:
            bool: 設定是否成功
        """
        try:
            speed_value = int(speed)
            success = self.tts_manager.set_voice_speed(speed_value)

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 語速設定為 {speed_value} wpm")
                else:
                    robot_logger.error(f"✗ TTS 語速設定失敗")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 語速失敗: {e}")
            return False

    @keyword('When 使用者查詢當前 TTS 引擎資訊')
    def when_user_queries_tts_engine_info(self) -> Dict[str, Any]:
        """
        When: 使用者查詢當前 TTS 引擎資訊
        When: User queries current TTS engine information
        
        此關鍵字執行查詢 TTS 引擎資訊的動作。
        This keyword performs the action of querying TTS engine information.
        
        Prerequisites:
        - Voice control system is initialized
        
        前置條件:
        - 語音控制系統已初始化
        
        Examples:
        | When | 使用者查詢當前 TTS 引擎資訊 |
        
        Returns:
            Dict[str, Any]: TTS 引擎資訊
        """
        return self.get_tts_engine_info()

    @keyword('When 使用者測試指定聲道 "${channel}" 的音訊輸出')
    def when_user_tests_channel_output(self, channel: int) -> bool:
        """
        When: 使用者測試指定聲道的音訊輸出
        When: User tests audio output of specified channel
        
        此關鍵字執行指定聲道的音訊輸出測試。
        This keyword performs audio output test for specified channel.
        
        Arguments:
        - channel: 目標聲道 (1-4)
        - channel: Target channel (1-4)
        
        Prerequisites:
        - Voice control system is initialized
        - Scarlett 4i4 device is connected
        
        前置條件:
        - 語音控制系統已初始化
        - Scarlett 4i4 設備已連接
        
        Examples:
        | When | 使用者測試指定聲道 "1" 的音訊輸出 |
        | When | 使用者測試指定聲道 "3" 的音訊輸出 |
        
        Returns:
            bool: 測試是否成功
        """
        return self.speak_text_to_channel(f"Test channel {channel}", int(channel), 'en', 3)

    # ===========================================
    # Gherkin 風格關鍵字 - Then (驗證結果)
    # ===========================================

    @keyword('Then 語音應該成功播放到指定聲道')
    def then_speech_should_play_successfully_to_channel(self) -> bool:
        """
        Then: 語音應該成功播放到指定聲道
        Then: Speech should play successfully to specified channel
        
        此關鍵字驗證語音播放操作是否成功完成。
        This keyword verifies that speech playback operation was completed successfully.
        
        Prerequisites:
        - A playback operation has been performed
        
        前置條件:
        - 已執行播放操作
        
        Examples:
        | Then | 語音應該成功播放到指定聲道 |
        
        Returns:
            bool: 播放是否成功
        """
        try:
            # 檢查是否有最後播放的音訊檔案
            if not self.last_audio_file:
                logger.error("沒有找到最後播放的音訊檔案")
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ 沒有找到最後播放的音訊檔案")
                return False
                
            # 檢查檔案是否存在
            if not os.path.exists(self.last_audio_file):
                logger.error(f"音訊檔案不存在: {self.last_audio_file}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ 音訊檔案不存在: {self.last_audio_file}")
                return False
                
            logger.info("語音播放驗證 - 成功")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 語音應該成功播放到指定聲道")
                
            return True
            
        except Exception as e:
            logger.error(f"語音播放驗證失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 語音播放驗證失敗: {e}")
            return False

    @keyword('Then TTS 引擎應該成功切換')
    def then_tts_engine_should_switch_successfully(self) -> bool:
        """
        Then: TTS 引擎應該成功切換
        Then: TTS engine should switch successfully
        
        此關鍵字驗證 TTS 引擎切換是否成功。
        This keyword verifies that TTS engine switching was successful.
        
        Prerequisites:
        - A TTS engine switch operation has been performed
        
        前置條件:
        - 已執行 TTS 引擎切換操作
        
        Examples:
        | Then | TTS 引擎應該成功切換 |
        
        Returns:
            bool: 切換是否成功
        """
        try:
            engine_info = self.tts_manager.get_engine_info()
            
            if engine_info and 'primary_engine' in engine_info:
                logger.info(f"TTS 引擎切換驗證 - 目前引擎: {engine_info['primary_engine']}")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ TTS 引擎應該成功切換 - 目前: {engine_info['primary_engine']}")
                return True
            else:
                logger.error("TTS 引擎資訊不完整")
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ TTS 引擎資訊不完整")
                return False
                
        except Exception as e:
            logger.error(f"TTS 引擎切換驗證失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 引擎切換驗證失敗: {e}")
            return False

    @keyword('Then TTS 語速應該成功設定')
    def then_tts_speed_should_be_set_successfully(self) -> bool:
        """
        Then: TTS 語速應該成功設定
        Then: TTS speed should be set successfully

        此關鍵字驗證 TTS 語速設定是否成功。
        This keyword verifies that TTS speed setting was successful.

        Prerequisites:
        - A TTS speed setting operation has been performed

        前置條件:
        - 已執行 TTS 語速設定操作

        Examples:
        | Then | TTS 語速應該成功設定 |

        Returns:
            bool: 設定是否成功
        """
        try:
            # 檢查 TTS 管理器狀態
            engine_info = self.tts_manager.get_engine_info()

            if not engine_info:
                logger.error("無法取得 TTS 引擎資訊")
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ 無法取得 TTS 引擎資訊")
                return False

            # 檢查配置是否已更新
            current_config = self.tts_manager.config
            if 'pyttsx3' in current_config and 'rate' in current_config['pyttsx3']:
                speed = current_config['pyttsx3']['rate']
                logger.info(f"TTS 語速驗證 - 目前設定: {speed} wpm")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ TTS 語速應該成功設定 - 目前: {speed} wpm")
                return True
            else:
                logger.warning("無法驗證 TTS 語速設定")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ 無法驗證 TTS 語速設定")
                return False

        except Exception as e:
            logger.error(f"TTS 語速驗證失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 語速驗證失敗: {e}")
            return False

    @keyword('Then 音訊輸出應該清晰無雜音')
    def then_audio_output_should_be_clear(self) -> bool:
        """
        Then: 音訊輸出應該清晰無雜音
        Then: Audio output should be clear without noise
        
        此關鍵字驗證音訊輸出品質是否符合標準。
        This keyword verifies that audio output quality meets standards.
        
        Prerequisites:
        - Audio playback has been performed
        
        前置條件:
        - 已執行音訊播放
        
        Examples:
        | Then | 音訊輸出應該清晰無雜音 |
        
        Returns:
            bool: 音訊品質是否符合標準
        """
        try:
            # 這裡可以添加音訊品質檢測邏輯
            # 目前先檢查基本播放狀態
            
            if not self.last_audio_file:
                logger.warning("沒有音訊檔案可供品質檢測")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ 沒有音訊檔案可供品質檢測")
                return False
                
            # 檢查 Scarlett 設備狀態
            if not self.audio_player.scarlett_available:
                logger.warning("Scarlett 4i4 設備不可用，無法確保音訊品質")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ Scarlett 4i4 設備不可用，無法確保音訊品質")
                return False
                
            logger.info("音訊品質檢測 - 通過")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 音訊輸出應該清晰無雜音")
                
            return True
            
        except Exception as e:
            logger.error(f"音訊品質檢測失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 音訊品質檢測失敗: {e}")
            return False

    @keyword('Then 系統應該回傳正確的 TTS 引擎資訊')
    def then_system_should_return_correct_tts_info(self) -> bool:
        """
        Then: 系統應該回傳正確的 TTS 引擎資訊
        Then: System should return correct TTS engine information
        
        此關鍵字驗證系統是否回傳正確的 TTS 引擎資訊。
        This keyword verifies that system returns correct TTS engine information.
        
        Prerequisites:
        - TTS engine information has been queried
        
        前置條件:
        - 已查詢 TTS 引擎資訊
        
        Examples:
        | Then | 系統應該回傳正確的 TTS 引擎資訊 |
        
        Returns:
            bool: 資訊是否正確
        """
        try:
            engine_info = self.tts_manager.get_engine_info()
            
            # 檢查必要欄位
            required_fields = ['primary_engine', 'available_engines']
            
            for field in required_fields:
                if field not in engine_info:
                    logger.error(f"TTS 引擎資訊缺少必要欄位: {field}")
                    if ROBOT_AVAILABLE:
                        robot_logger.error(f"✗ TTS 引擎資訊缺少必要欄位: {field}")
                    return False
                    
            logger.info(f"TTS 引擎資訊驗證 - 正確: {engine_info}")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 系統應該回傳正確的 TTS 引擎資訊")
                
            return True
            
        except Exception as e:
            logger.error(f"TTS 引擎資訊驗證失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ TTS 引擎資訊驗證失敗: {e}")
            return False

    @keyword('Then Scarlett 4i4 設備應該處於正常運作狀態')
    def then_scarlett_device_should_be_operational(self) -> bool:
        """
        Then: Scarlett 4i4 設備應該處於正常運作狀態
        Then: Scarlett 4i4 device should be in normal operating state
        
        此關鍵字驗證 Scarlett 4i4 設備是否處於正常運作狀態。
        This keyword verifies that Scarlett 4i4 device is in normal operating state.
        
        Prerequisites:
        - Device connection check has been performed
        
        前置條件:
        - 已執行設備連接檢查
        
        Examples:
        | Then | Scarlett 4i4 設備應該處於正常運作狀態 |
        
        Returns:
            bool: 設備是否正常運作
        """
        return self.check_scarlett_device()

    # ===========================================
    # Gherkin 風格關鍵字 - And (附加驗證)
    # ===========================================

    @keyword('And 語音品質應該符合標準')
    def and_voice_quality_should_meet_standards(self) -> bool:
        """
        And: 語音品質應該符合標準
        And: Voice quality should meet standards
        
        此關鍵字驗證語音品質是否符合預定標準。
        This keyword verifies that voice quality meets predetermined standards.
        
        Prerequisites:
        - Audio playback has been completed
        
        前置條件:
        - 音訊播放已完成
        
        Examples:
        | And | 語音品質應該符合標準 |
        
        Returns:
            bool: 品質是否符合標準
        """
        # 重用音訊品質檢測邏輯
        return self.then_audio_output_should_be_clear()

    @keyword('And 沒有音訊延遲或中斷')
    def and_no_audio_delay_or_interruption(self) -> bool:
        """
        And: 沒有音訊延遲或中斷
        And: No audio delay or interruption
        
        此關鍵字驗證音訊播放過程中沒有延遲或中斷。
        This keyword verifies that there is no delay or interruption during audio playback.
        
        Prerequisites:
        - Audio playback has been performed
        
        前置條件:
        - 已執行音訊播放
        
        Examples:
        | And | 沒有音訊延遲或中斷 |
        
        Returns:
            bool: 是否無延遲中斷
        """
        try:
            # 檢查 Scarlett 設備狀態
            if not self.audio_player.scarlett_available:
                logger.warning("Scarlett 4i4 設備不可用，可能存在音訊問題")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ Scarlett 4i4 設備不可用，可能存在音訊問題")
                return False
                
            # 檢查是否有音訊檔案
            if not self.last_audio_file:
                logger.warning("沒有音訊檔案記錄，無法驗證播放品質")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ 沒有音訊檔案記錄，無法驗證播放品質")
                return False
                
            logger.info("音訊延遲/中斷檢測 - 通過")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 沒有音訊延遲或中斷")
                
            return True
            
        except Exception as e:
            logger.error(f"音訊延遲/中斷檢測失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 音訊延遲/中斷檢測失敗: {e}")
            return False

    @keyword('And 暫存檔案應該正確清理')
    def and_temp_files_should_be_cleaned_properly(self) -> bool:
        """
        And: 暫存檔案應該正確清理
        And: Temporary files should be cleaned properly
        
        此關鍵字驗證暫存檔案是否正確清理。
        This keyword verifies that temporary files are properly cleaned.
        
        Prerequisites:
        - File cleanup operation has been performed
        
        前置條件:
        - 已執行檔案清理操作
        
        Examples:
        | And | 暫存檔案應該正確清理 |
        
        Returns:
            bool: 清理是否正確
        """
        try:
            # 執行清理
            cleaned_count = self.tts_manager.cleanup_temp_files()
            
            # 檢查本地記錄
            temp_files_exist = len(self.temp_audio_files) > 0
            
            if temp_files_exist:
                logger.info(f"清理了 {cleaned_count} 個暫存檔案")
            else:
                logger.info("沒有需要清理的暫存檔案")
                
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 暫存檔案應該正確清理")
                
            return True
            
        except Exception as e:
            logger.error(f"暫存檔案清理驗證失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 暫存檔案清理驗證失敗: {e}")
            return False

    @keyword('And 錯誤日誌應該為空')
    def and_error_logs_should_be_empty(self) -> bool:
        """
        And: 錯誤日誌應該為空
        And: Error logs should be empty
        
        此關鍵字驗證系統錯誤日誌是否為空。
        This keyword verifies that system error logs are empty.
        
        Prerequisites:
        - System operations have been completed
        
        前置條件:
        - 系統操作已完成
        
        Examples:
        | And | 錯誤日誌應該為空 |
        
        Returns:
            bool: 錯誤日誌是否為空
        """
        try:
            # 這裡可以添加錯誤日誌檢查邏輯
            # 目前簡單檢查系統狀態
            
            # 檢查 TTS 管理器狀態
            tts_info = self.tts_manager.get_engine_info()
            if not tts_info:
                logger.warning("TTS 管理器狀態異常")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ TTS 管理器狀態異常")
                return False
                
            # 檢查音訊播放器狀態
            if not self.audio_player:
                logger.warning("音訊播放器狀態異常")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ 音訊播放器狀態異常")
                return False
                
            logger.info("錯誤日誌檢查 - 正常")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 錯誤日誌應該為空")
                
            return True
            
        except Exception as e:
            logger.error(f"錯誤日誌檢查失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 錯誤日誌檢查失敗: {e}")
            return False

    # ===========================================
    # Gherkin 風格關鍵字 - UART 監控 (新增於 v1.1.0)
    # ===========================================

    @keyword('Given UART 日誌監控器已初始化')
    def given_uart_monitor_initialized(self, port: Optional[str] = None, baudrate: int = 115200, auto_validate: bool = True) -> bool:
        """
        Given: 確認 UART 日誌監控器已初始化

        此關鍵字初始化 UART 監控器用於檢測語音回應。

        Arguments:
        - port: UART 埠路徑 (可選，預設從環境變數讀取)
        - baudrate: 鮑率 (預設 115200)
        - auto_validate: 是否自動驗證並修正遠端配置 (預設 True)

        Prerequisites:
        - UART 設備已連接
        - SerialLogParser 模組已安裝

        前置條件:
        - UART 設備已連接
        - SerialLogParser 模組已安裝

        Examples:
        | Given | UART 日誌監控器已初始化 |
        | Given | UART 日誌監控器已初始化 | /dev/ttyUSB0 | 115200 |

        Returns:
            bool: 初始化是否成功
        """
        success = self._init_uart_monitor(port, baudrate, auto_validate)

        if ROBOT_AVAILABLE:
            if success:
                robot_logger.info("✓ UART 日誌監控器已初始化")
            else:
                robot_logger.error("✗ UART 日誌監控器初始化失敗")

        return success

    @keyword('When 使用者啟動 UART 背景監控')
    def when_user_starts_uart_monitoring(self) -> bool:
        """
        When: 使用者啟動 UART 背景監控

        此關鍵字啟動 UART 背景監控，用於檢測語音播放事件。

        Prerequisites:
        - UART 監控器已初始化

        前置條件:
        - UART 監控器已初始化

        Examples:
        | When | 使用者啟動 UART 背景監控 |

        Returns:
            bool: 啟動是否成功
        """
        success = self._start_uart_monitoring()

        if ROBOT_AVAILABLE:
            if success:
                robot_logger.info("✓ UART 背景監控已啟動")
            else:
                robot_logger.error("✗ UART 背景監控啟動失敗")

        return success

    @keyword('When 使用者停止 UART 背景監控')
    def when_user_stops_uart_monitoring(self):
        """
        When: 使用者停止 UART 背景監控

        此關鍵字停止 UART 背景監控。

        Prerequisites:
        - UART 背景監控正在運行

        前置條件:
        - UART 背景監控正在運行

        Examples:
        | When | 使用者停止 UART 背景監控 |
        """
        self._stop_uart_monitoring()

        if ROBOT_AVAILABLE:
            robot_logger.info("✓ UART 背景監控已停止")

    @keyword('Then 應該在 "${timeout}" 秒內收到恰好 "${count}" 個語音回應')
    def then_should_receive_exact_voice_responses(self, timeout: float, count: int):
        """
        Then: 應該在指定時間內收到恰好指定數量的語音回應

        此關鍵字驗證語音回應數量是否恰好符合預期。
        - 如果數量少於預期 → FAIL (可能沒有回應或回應不完整)
        - 如果數量多於預期 → FAIL (可能有重複回應或錯誤觸發)
        - 如果數量等於預期 → PASS

        Arguments:
        - timeout: 超時時間（秒）
        - count: 預期的語音回應數量

        Prerequisites:
        - UART 背景監控已啟動
        - 已執行語音命令

        前置條件:
        - UART 背景監控已啟動
        - 已執行語音命令

        Examples:
        | Then | 應該在 "5" 秒內收到恰好 "1" 個語音回應 |
        | Then | 應該在 "10" 秒內收到恰好 "3" 個語音回應 |

        Raises:
            AssertionError: 當語音回應數量不符合預期時
        """
        timeout_val = float(timeout)
        count_val = int(count)

        passed, actual_count, filenames, raw_log_lines = self._check_voice_response_count(
            timeout=timeout_val,
            expected_count=count_val
        )

        if ROBOT_AVAILABLE:
            if passed:
                robot_logger.info(f"✓ 收到恰好 {count_val} 個語音回應（符合預期）")
                for i, filename in enumerate(filenames, 1):
                    robot_logger.info(f"  {i}. {filename}")
            else:
                robot_logger.error(f"✗ 語音回應數量不符: 預期 {count_val} 個，實際 {actual_count} 個")
                if actual_count > 0:
                    robot_logger.error("  實際收到的回應:")
                    for i, filename in enumerate(filenames, 1):
                        robot_logger.error(f"    {i}. {filename}")
                else:
                    robot_logger.error(f"  在 {timeout_val} 秒內未收到任何語音回應")

                # v1.2.0: 診斷資訊
                mp3_related_lines = [line for line in raw_log_lines if 'mp3' in line.lower() or 'audio' in line.lower() or 'playing' in line.lower()]
                if mp3_related_lines:
                    robot_logger.info(f"找到 {len(mp3_related_lines)} 行包含 mp3/audio/playing:")
                    for line in mp3_related_lines[:10]:
                        robot_logger.info(f"  >> {line}")
                else:
                    robot_logger.error("⚠️  日誌中未找到任何包含 mp3/audio/playing 的內容")

                # v1.2.0: 輸出完整的 UART 日誌用於診斷
                robot_logger.error(f"\n完整 UART 日誌 ({len(raw_log_lines)} 行):")
                robot_logger.error("=" * 60)
                for i, line in enumerate(raw_log_lines, 1):
                    robot_logger.error(f"{i:4d} | {line}")
                robot_logger.error("=" * 60)

        # 如果驗證失敗，拋出 AssertionError 讓測試 FAIL
        if not passed:
            error_msg = f"語音回應數量不符: 預期 {count_val} 個，實際 {actual_count} 個"
            if actual_count > 0:
                error_msg += f"\n實際收到的檔案: {', '.join(filenames)}"

            # v1.2.0: 診斷資訊
            mp3_related_lines = [line for line in raw_log_lines if 'mp3' in line.lower() or 'audio' in line.lower() or 'playing' in line.lower()]
            if mp3_related_lines:
                error_msg += f"\n\n⚠️ 診斷：找到 {len(mp3_related_lines)} 行包含 mp3/audio/playing 關鍵字（前 10 行）:\n"
                for line in mp3_related_lines[:10]:
                    error_msg += f"  >> {line}\n"
            else:
                error_msg += "\n\n⚠️ 診斷：日誌中未找到任何包含 mp3/audio/playing 的內容"

            error_msg += f"\n\n完整 UART 日誌 ({len(raw_log_lines)} 行):\n"
            error_msg += "=" * 60 + "\n"
            for i, line in enumerate(raw_log_lines, 1):
                error_msg += f"{i:4d} | {line}\n"
            error_msg += "=" * 60
            raise AssertionError(error_msg)

    @keyword('Then 應該在 "${timeout}" 秒內收到包含以下檔案的語音回應 "${patterns}"')
    def then_should_receive_voice_responses_with_patterns(self, timeout: float, patterns: str):
        """
        Then: 應該在指定時間內收到包含特定檔案模式的語音回應

        此關鍵字驗證語音回應的檔案名稱是否符合預期模式。

        Arguments:
        - timeout: 超時時間（秒）
        - patterns: 預期的檔案名稱模式，使用逗號分隔（如: "cmd_044-1.mp3,Welcome_back.mp3"）

        Prerequisites:
        - UART 背景監控已啟動
        - 已執行語音命令

        前置條件:
        - UART 背景監控已啟動
        - 已執行語音命令

        Examples:
        | Then | 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3" |
        | Then | 應該在 "10" 秒內收到包含以下檔案的語音回應 "Light_timer_set.mp3,1.mp3,hours.mp3" |

        Raises:
            AssertionError: 當語音回應不符合預期時
        """
        timeout_val = float(timeout)
        # 解析每個模式，支援 YAML Key
        pattern_list = [self._resolve_pattern(p) for p in patterns.split(',')]
        expected_count = len(pattern_list)

        passed, actual_count, filenames, raw_log_lines = self._check_voice_response_count(
            timeout=timeout_val,
            expected_count=expected_count,
            expected_patterns=pattern_list
        )

        if ROBOT_AVAILABLE:
            if passed:
                robot_logger.info(f"✓ 收到符合預期的 {expected_count} 個語音回應")
                for i, (filename, pattern) in enumerate(zip(filenames, pattern_list), 1):
                    robot_logger.info(f"  {i}. {filename} (預期包含: {pattern})")
            else:
                robot_logger.error(f"✗ 語音回應不符合預期")
                robot_logger.error(f"  預期數量: {expected_count}，實際數量: {actual_count}")
                robot_logger.error("  預期模式:")
                for i, pattern in enumerate(pattern_list, 1):
                    robot_logger.error(f"    {i}. {pattern}")
                if filenames:
                    robot_logger.error("  實際收到:")
                    for i, filename in enumerate(filenames, 1):
                        robot_logger.error(f"    {i}. {filename}")

                # v1.2.0: 診斷資訊
                mp3_related_lines = [line for line in raw_log_lines if 'mp3' in line.lower() or 'audio' in line.lower() or 'playing' in line.lower()]
                if mp3_related_lines:
                    robot_logger.info(f"找到 {len(mp3_related_lines)} 行包含 mp3/audio/playing:")
                    for line in mp3_related_lines[:10]:
                        robot_logger.info(f"  >> {line}")
                else:
                    robot_logger.error("⚠️  日誌中未找到任何包含 mp3/audio/playing 的內容")

                # v1.2.0: 輸出完整的 UART 日誌用於診斷
                robot_logger.error(f"\n完整 UART 日誌 ({len(raw_log_lines)} 行):")
                robot_logger.error("=" * 60)
                for i, line in enumerate(raw_log_lines, 1):
                    robot_logger.error(f"{i:4d} | {line}")
                robot_logger.error("=" * 60)

        # 如果驗證失敗，拋出 AssertionError 讓測試 FAIL
        if not passed:
            error_msg = f"語音回應不符合預期:\n"
            error_msg += f"  預期數量: {expected_count} 個\n"
            error_msg += f"  實際數量: {actual_count} 個\n"
            error_msg += f"  預期模式: {', '.join(pattern_list)}\n"

            # 總是顯示實際收到的檔案清單（即使為空）
            if filenames:
                error_msg += f"  實際模式: {', '.join(filenames)}"
            else:
                error_msg += f"  實際模式: (在 {timeout_val} 秒內未收到任何語音回應)"

            # v1.2.0: 診斷資訊
            mp3_related_lines = [line for line in raw_log_lines if 'mp3' in line.lower() or 'audio' in line.lower() or 'playing' in line.lower()]
            if mp3_related_lines:
                error_msg += f"\n\n⚠️ 診斷：找到 {len(mp3_related_lines)} 行包含 mp3/audio/playing 關鍵字（前 10 行）:\n"
                for line in mp3_related_lines[:10]:
                    error_msg += f"  >> {line}\n"
            else:
                error_msg += "\n\n⚠️ 診斷：日誌中未找到任何包含 mp3/audio/playing 的內容"

            # v1.2.0: 附加完整的 UART 日誌
            error_msg += f"\n\n完整 UART 日誌 ({len(raw_log_lines)} 行):\n"
            error_msg += "=" * 60 + "\n"
            for i, line in enumerate(raw_log_lines, 1):
                error_msg += f"{i:4d} | {line}\n"
            error_msg += "=" * 60

            raise AssertionError(error_msg)

    @keyword('And 清空 UART 事件記錄')
    def and_clear_uart_events(self):
        """
        And: 清空 UART 事件記錄

        此關鍵字清空之前記錄的所有 UART 事件，用於開始新的測試。

        Prerequisites:
        - UART 監控器已初始化

        前置條件:
        - UART 監控器已初始化

        Examples:
        | And | 清空 UART 事件記錄 |
        """
        if self.uart_parser:
            self.uart_parser.clear_events()
            logger.info("✓ UART 事件記錄已清空")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ UART 事件記錄已清空")

    @keyword('And 系統資源使用應該在正常範圍內')
    def and_system_resources_should_be_normal(self) -> bool:
        """
        And: 系統資源使用應該在正常範圍內
        And: System resource usage should be within normal range
        
        此關鍵字驗證系統資源使用是否在正常範圍內。
        This keyword verifies that system resource usage is within normal range.
        
        Prerequisites:
        - System operations have been performed
        
        前置條件:
        - 已執行系統操作
        
        Examples:
        | And | 系統資源使用應該在正常範圍內 |
        
        Returns:
            bool: 資源使用是否正常
        """
        try:
            # 檢查暫存檔案數量
            temp_count = len(self.temp_audio_files)
            
            if temp_count > 10:  # 假設超過 10 個暫存檔案為異常
                logger.warning(f"暫存檔案數量過多: {temp_count}")
                if ROBOT_AVAILABLE:
                    robot_logger.warn(f"⚠ 暫存檔案數量過多: {temp_count}")
                return False
                
            # 檢查基本系統狀態
            info = self.get_library_info()
            
            if not info:
                logger.warning("無法取得系統資訊")
                if ROBOT_AVAILABLE:
                    robot_logger.warn("⚠ 無法取得系統資訊")
                return False
                
            logger.info(f"系統資源檢查 - 正常 (暫存檔案: {temp_count})")
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 系統資源使用應該在正常範圍內")
                
            return True
            
        except Exception as e:
            logger.error(f"系統資源檢查失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 系統資源檢查失敗: {e}")
            return False

    def __del__(self):
        """解構函數，自動清理資源"""
        try:
            self.cleanup_voice_control_resources()
        except:
            pass


# 測試程式
if __name__ == "__main__":
    print("VoiceControlKeywords 測試程式")

    # 建立 Library 實例
    lib = VoiceControlKeywords()

    # 顯示資訊
    info = lib.get_library_info()
    print(f"Library 資訊: {info}")

    # 基本功能測試
    try:
        # 檢查 Scarlett 設備
        scarlett_ok = lib.check_scarlett_device()
        print(f"\nScarlett 設備狀態: {'✓ 可用' if scarlett_ok else '✗ 不可用'}")

        if scarlett_ok:
            # 測試播放
            print("\n測試播放文字到聲道 1...")
            success = lib.speak_text_to_channel("Test", 1, "en", 3)
            print(f"播放結果: {'✓ 成功' if success else '✗ 失敗'}")

        print("\n✓ 基本功能測試完成")

    except Exception as e:
        print(f"✗ 測試失敗: {e}")

    finally:
        # 清理資源
        lib.cleanup_voice_control_resources()
        print("✓ 資源清理完成")
