"""
TTS (Text-to-Speech) 管理模組 - voice_control 專用版本
負責處理文字轉語音功能，支援多種 TTS 引擎
專為 Scarlett 4i4 音訊輸出設計
"""
import os
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

# TTS 引擎
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# 配置匯入
try:
    import sys
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from config.voice_config import TTS_CONFIG, LOGGING_CONFIG
except ImportError as e:
    print(f"警告: 無法匯入配置: {e}")
    # 使用預設配置
    TTS_CONFIG = {
        'primary_engine': 'gtts',
        'fallback_engine': 'pyttsx3',
        'gtts': {'language': 'en', 'slow': False},
        'pyttsx3': {'rate': 180, 'volume': 0.8, 'voice_id': 0}
    }
    LOGGING_CONFIG = {'level': 'INFO'}

# 日誌處理
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


class TTSManager:
    """
    TTS 管理器類別
    支援 Google TTS 和 pyttsx3 引擎
    專為 voice_control 音訊輸出設計
    """

    def __init__(self, engine: Optional[str] = None):
        """
        初始化 TTS 管理器

        Args:
            engine: TTS 引擎名稱 ('gtts' 或 'pyttsx3')
        """
        self.config = TTS_CONFIG
        self.primary_engine = engine or self.config['primary_engine']
        self.fallback_engine = self.config['fallback_engine']

        # 引擎狀態
        self.current_engine = None
        self.gtts_engine = None
        self.pyttsx3_engine = None

        # 暫存檔案管理
        self.temp_dir = Path(__file__).parent / 'temp_audio'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.temp_files = []

        # 初始化日誌
        self._setup_logger()

        # 初始化 TTS 引擎
        self._init_engines()

        logger.info(f"TTSManager 初始化完成，主要引擎: {self.primary_engine}")

    def _setup_logger(self) -> None:
        """設定日誌記錄器"""
        try:
            if not LOGURU_AVAILABLE:
                # 使用標準 logging
                import logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    handlers=[
                        logging.FileHandler('logs/voice_control_tts.log'),
                        logging.StreamHandler()
                    ]
                )
                return

            # 移除預設處理器
            logger.remove()

            # 添加新的處理器
            logger.add(
                "logs/voice_control_tts.log",
                format=LOGGING_CONFIG.get('format', '{time} | {level} | {message}'),
                level=LOGGING_CONFIG.get('level', 'INFO'),
                rotation="10 MB",
                retention="7 days",
                compression="zip",
            )

        except Exception as e:
            print(f"日誌設定失敗: {e}")

    def _init_engines(self) -> None:
        """初始化 TTS 引擎"""
        # 嘗試初始化主要引擎
        if self.primary_engine == 'gtts' and GTTS_AVAILABLE:
            self._init_gtts()
        elif self.primary_engine == 'pyttsx3' and PYTTSX3_AVAILABLE:
            self._init_pyttsx3()
        else:
            logger.warning(f"主要引擎 {self.primary_engine} 不可用")

        # 嘗試初始化備援引擎
        if self.fallback_engine == 'pyttsx3' and PYTTSX3_AVAILABLE:
            self._init_pyttsx3()
        elif self.fallback_engine == 'gtts' and GTTS_AVAILABLE:
            self._init_gtts()

    def _init_gtts(self) -> bool:
        """
        初始化 Google TTS 引擎

        Returns:
            初始化是否成功
        """
        try:
            if not GTTS_AVAILABLE:
                logger.error("gTTS 套件未安裝")
                return False

            # 測試 gTTS 連線
            test_tts = gTTS(text="test", lang=self.config['gtts']['language'])
            self.gtts_engine = True
            logger.info("Google TTS 引擎初始化成功")
            return True

        except Exception as e:
            logger.error(f"Google TTS 引擎初始化失敗: {e}")
            return False

    def _init_pyttsx3(self) -> bool:
        """
        初始化 pyttsx3 引擎

        Returns:
            初始化是否成功
        """
        try:
            if not PYTTSX3_AVAILABLE:
                logger.error("pyttsx3 套件未安裝")
                return False

            self.pyttsx3_engine = pyttsx3.init()

            # 設定語音屬性
            self.pyttsx3_engine.setProperty('rate', self.config['pyttsx3']['rate'])
            self.pyttsx3_engine.setProperty('volume', self.config['pyttsx3']['volume'])

            # 選擇語音
            voices = self.pyttsx3_engine.getProperty('voices')
            if voices and len(voices) > self.config['pyttsx3']['voice_id']:
                voice = voices[self.config['pyttsx3']['voice_id']]
                self.pyttsx3_engine.setProperty('voice', voice.id)

            logger.info("pyttsx3 引擎初始化成功")
            return True

        except Exception as e:
            logger.error(f"pyttsx3 引擎初始化失敗: {e}")
            return False

    def text_to_file(self, text: str, output_file: Optional[str] = None,
                    language: Optional[str] = None, format: str = 'mp3') -> Optional[str]:
        """
        將文字轉換為音訊檔案（不播放）

        這是 voice_control 專用方法，用於生成音訊檔案供 AudioPlayer 播放

        Args:
            text: 要轉換的文字
            output_file: 輸出檔案路徑（可選，預設自動生成暫存檔案）
            language: 語言代碼（可選，預設使用配置）
            format: 輸出格式 ('mp3' 或 'wav')

        Returns:
            生成的音訊檔案路徑，失敗時回傳 None

        Examples:
            >>> tts = TTSManager()
            >>> audio_file = tts.text_to_file("Hello World", language='en')
            >>> # 使用 AudioPlayer 播放到特定聲道
        """
        if not text or not text.strip():
            logger.warning("輸入文字為空")
            return None

        logger.info(f"開始文字轉檔案: '{text}' (格式: {format})")

        # 選擇引擎
        engine = self._select_engine()
        if not engine:
            logger.error("沒有可用的 TTS 引擎")
            return None

        # 生成輸出檔案路徑
        if output_file is None:
            suffix = f'.{format}'
            output_file = tempfile.mktemp(suffix=suffix, dir=self.temp_dir)
            self.temp_files.append(output_file)

        # 執行轉換
        try:
            if engine == 'gtts':
                return self._text_to_file_gtts(text, output_file, language)
            elif engine == 'pyttsx3':
                return self._text_to_file_pyttsx3(text, output_file)
            else:
                logger.error(f"不支援的引擎: {engine}")
                return None
        except Exception as e:
            logger.error(f"文字轉檔案失敗: {e}")
            return None

    def _text_to_file_gtts(self, text: str, output_file: str,
                          language: Optional[str]) -> Optional[str]:
        """
        使用 Google TTS 將文字轉為檔案

        Args:
            text: 要轉換的文字
            output_file: 輸出檔案路徑
            language: 語言代碼

        Returns:
            輸出檔案路徑或 None
        """
        try:
            lang = language or self.config['gtts']['language']
            slow = self.config['gtts']['slow']

            # 建立 gTTS 物件
            tts = gTTS(text=text, lang=lang, slow=slow)

            # 保存到檔案
            tts.save(output_file)

            if os.path.exists(output_file):
                logger.info(f"Google TTS 檔案生成成功: {output_file}")
                return output_file
            else:
                logger.error("Google TTS 檔案生成失敗")
                return None

        except Exception as e:
            logger.error(f"Google TTS 檔案生成失敗: {e}")
            return None

    def _text_to_file_pyttsx3(self, text: str, output_file: str) -> Optional[str]:
        """
        使用 pyttsx3 將文字轉為檔案

        Args:
            text: 要轉換的文字
            output_file: 輸出檔案路徑

        Returns:
            輸出檔案路徑或 None
        """
        try:
            if not self.pyttsx3_engine:
                logger.error("pyttsx3 引擎未初始化")
                return None

            # pyttsx3 的 save_to_file 方法
            self.pyttsx3_engine.save_to_file(text, output_file)
            self.pyttsx3_engine.runAndWait()

            if os.path.exists(output_file):
                logger.info(f"pyttsx3 檔案生成成功: {output_file}")
                return output_file
            else:
                logger.error("pyttsx3 檔案生成失敗")
                return None

        except Exception as e:
            logger.error(f"pyttsx3 檔案生成失敗: {e}")
            return None

    def _select_engine(self) -> Optional[str]:
        """
        選擇可用的 TTS 引擎

        Returns:
            引擎名稱或 None
        """
        # 嘗試主要引擎
        if self.primary_engine == 'gtts' and self.gtts_engine:
            return 'gtts'
        elif self.primary_engine == 'pyttsx3' and self.pyttsx3_engine:
            return 'pyttsx3'

        # 嘗試備援引擎
        if self.fallback_engine == 'gtts' and self.gtts_engine:
            logger.warning("使用備援引擎: Google TTS")
            return 'gtts'
        elif self.fallback_engine == 'pyttsx3' and self.pyttsx3_engine:
            logger.warning("使用備援引擎: pyttsx3")
            return 'pyttsx3'

        return None

    def set_language(self, language: str) -> bool:
        """
        設定 TTS 語言

        Args:
            language: 語言代碼 (例如: 'en', 'zh-TW', 'ja')

        Returns:
            設定是否成功
        """
        try:
            # 更新 gTTS 語言設定
            self.config['gtts']['language'] = language
            logger.info(f"TTS 語言設定為: {language}")
            return True
        except Exception as e:
            logger.error(f"設定 TTS 語言失敗: {e}")
            return False

    def set_engine(self, engine_name: str) -> bool:
        """
        切換 TTS 引擎

        Args:
            engine_name: 引擎名稱 ('gtts' 或 'pyttsx3')

        Returns:
            切換是否成功
        """
        try:
            if engine_name == 'gtts' and self.gtts_engine:
                self.primary_engine = 'gtts'
                logger.info("TTS 引擎切換為: Google TTS")
                return True
            elif engine_name == 'pyttsx3' and self.pyttsx3_engine:
                self.primary_engine = 'pyttsx3'
                logger.info("TTS 引擎切換為: pyttsx3")
                return True
            else:
                logger.error(f"引擎 {engine_name} 不可用")
                return False
        except Exception as e:
            logger.error(f"切換 TTS 引擎失敗: {e}")
            return False

    def set_voice_speed(self, speed: float) -> bool:
        """
        設定語音速度

        Args:
            speed: 語音速度 (pyttsx3: words per minute, gTTS: slow=True/False)

        Returns:
            設定是否成功
        """
        try:
            # 更新 pyttsx3 語速
            if self.pyttsx3_engine:
                self.pyttsx3_engine.setProperty('rate', int(speed))
                self.config['pyttsx3']['rate'] = int(speed)

            # 更新 gTTS 語速 (將數值轉換為 slow 參數)
            self.config['gtts']['slow'] = speed < 150

            logger.info(f"語音速度設定為: {speed}")
            return True
        except Exception as e:
            logger.error(f"設定語音速度失敗: {e}")
            return False

    def get_available_engines(self) -> list:
        """
        獲取可用的 TTS 引擎列表

        Returns:
            可用引擎列表
        """
        engines = []
        if self.gtts_engine:
            engines.append('gtts')
        if self.pyttsx3_engine:
            engines.append('pyttsx3')
        return engines

    def get_engine_info(self) -> Dict[str, Any]:
        """
        獲取 TTS 引擎資訊

        Returns:
            引擎資訊字典
        """
        return {
            'primary_engine': self.primary_engine,
            'fallback_engine': self.fallback_engine,
            'current_engine': self.current_engine,
            'available_engines': self.get_available_engines(),
            'temp_files_count': len(self.temp_files),
            'gtts_available': GTTS_AVAILABLE,
            'pyttsx3_available': PYTTSX3_AVAILABLE,
        }

    def cleanup_temp_files(self) -> int:
        """
        清理本此執行期間產生的暫存音訊檔案
        (只清理 self.temp_files 列表中的檔案)

        Returns:
            清理的檔案數量
        """
        cleaned_count = 0
        for temp_file in self.temp_files[:]:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    cleaned_count += 1
                self.temp_files.remove(temp_file)
            except Exception as e:
                logger.warning(f"清理暫存檔案失敗 {temp_file}: {e}")

        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 個暫存音訊檔案")

        return cleaned_count

    def cleanup_all_temp_files(self) -> int:
        """
        清理 temp_audio 目錄下的所有檔案
        (用於初始化時清理舊的暫存檔)

        Returns:
            清理的檔案數量
        """
        cleaned_count = 0
        if not self.temp_dir.exists():
            return 0

        try:
            for file_path in self.temp_dir.glob('*'):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"無法刪除檔案 {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"初始化清理: 刪除了 {cleaned_count} 個舊的暫存音訊檔案")
                
        except Exception as e:
            logger.error(f"清理暫存目錄失敗: {e}")

        return cleaned_count

    def cleanup(self) -> None:
        """清理 TTS 資源"""
        try:
            # 清理暫存檔案
            self.cleanup_temp_files()

            # 清理 pyttsx3 引擎
            if self.pyttsx3_engine:
                try:
                    self.pyttsx3_engine.stop()
                except Exception:
                    pass

            logger.info("TTS 資源清理完成")

        except Exception as e:
            logger.error(f"TTS 資源清理失敗: {e}")

    def __del__(self) -> None:
        """解構函數，自動清理資源"""
        self.cleanup()


# 測試程式
if __name__ == "__main__":
    print("TTSManager 測試程式")

    # 建立 TTS 管理器
    tts = TTSManager()

    # 顯示可用引擎
    print(f"可用引擎: {tts.get_available_engines()}")

    # 測試文字轉檔案
    print("\n測試文字轉檔案功能...")
    audio_file = tts.text_to_file("Hello World", language='en')
    if audio_file:
        print(f"✓ 音訊檔案生成成功: {audio_file}")
        print(f"檔案大小: {os.path.getsize(audio_file)} bytes")
    else:
        print("✗ 音訊檔案生成失敗")

    # 清理資源
    tts.cleanup()
    print("\n✓ 資源清理完成")
