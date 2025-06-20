"""
TTS (Text-to-Speech) 管理模組
負責處理文字轉語音功能，支援多種 TTS 引擎
"""
import os
import io
import threading
import time
from typing import Optional, Dict, Any, Union
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

# 音訊播放
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False

# 配置匯入 - 處理相對/絕對匯入
try:
    # 嘗試從專案根目錄的 config 套件匯入
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.voice_config import TTS_CONFIG, LOGGING_CONFIG
except ImportError:
    try:
        from .voice_config import TTS_CONFIG, LOGGING_CONFIG
    except ImportError:
        # 如果失敗，嘗試直接匯入（向後相容）
        from voice_config import TTS_CONFIG, LOGGING_CONFIG

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
        self.is_speaking = False
        self.speaking_thread = None
        
        # 初始化日誌
        self._setup_logger()
        
        # 初始化音訊播放
        self._init_audio_player()
        
        # 初始化 TTS 引擎
        self._init_engines()
        
        logger.info(f"TTSManager 初始化完成，主要引擎: {self.primary_engine}")
    
    def _setup_logger(self) -> None:
        """設定日誌記錄器"""
        try:
            if not LOGURU_AVAILABLE:
                # 使用標準 logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    handlers=[
                        logging.FileHandler('logs/tts_manager.log'),
                        logging.StreamHandler()
                    ]
                )
                return
            
            # 移除預設處理器
            logger.remove()
            
            # 添加新的處理器
            logger.add(
                "logs/tts_manager.log",
                format=LOGGING_CONFIG['format'],
                level=LOGGING_CONFIG['level'],
                rotation=LOGGING_CONFIG['rotation'],
                retention=LOGGING_CONFIG['retention'],
                compression=LOGGING_CONFIG['compression'],
                backtrace=LOGGING_CONFIG['backtrace'],
                diagnose=LOGGING_CONFIG['diagnose'],
            )
            
        except Exception as e:
            print(f"日誌設定失敗: {e}")
    
    def _init_audio_player(self) -> None:
        """初始化音訊播放器"""
        self.audio_player = None
        
        # 優先使用 pygame
        if PYGAME_AVAILABLE:
            try:
                import pygame
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_player = 'pygame'
                logger.info("使用 pygame 作為音訊播放器")
                return
            except Exception as e:
                logger.warning(f"pygame 初始化失敗: {e}")
        
        # 備援使用 simpleaudio
        if SIMPLEAUDIO_AVAILABLE:
            self.audio_player = 'simpleaudio'
            logger.info("使用 simpleaudio 作為音訊播放器")
            return
        
        # 使用系統預設播放器
        self.audio_player = 'system'
        logger.warning("使用系統預設音訊播放器")
    
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
    
    def speak_text(self, text: str, language: Optional[str] = None, 
                  async_mode: bool = True) -> bool:
        """
        將文字轉換為語音並播放
        
        Args:
            text: 要轉換的文字
            language: 語言代碼 (例如: 'zh-TW', 'en-US')
            async_mode: 是否非同步播放
            
        Returns:
            播放是否成功
        """
        if not text or not text.strip():
            logger.warning("輸入文字為空")
            return False
        
        logger.info(f"開始語音合成: '{text}'")
        
        # 選擇引擎
        engine = self._select_engine()
        if not engine:
            logger.error("沒有可用的 TTS 引擎")
            return False
        
        # 執行語音合成
        if async_mode:
            self.speaking_thread = threading.Thread(
                target=self._speak_text_sync,
                args=(text, language, engine)
            )
            self.speaking_thread.start()
            return True
        else:
            return self._speak_text_sync(text, language, engine)
    
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
    
    def _speak_text_sync(self, text: str, language: Optional[str], 
                        engine: str) -> bool:
        """
        同步執行語音合成
        
        Args:
            text: 要轉換的文字
            language: 語言代碼
            engine: 使用的引擎
            
        Returns:
            執行是否成功
        """
        try:
            self.is_speaking = True
            
            if engine == 'gtts':
                return self._speak_with_gtts(text, language)
            elif engine == 'pyttsx3':
                return self._speak_with_pyttsx3(text)
            else:
                logger.error(f"不支援的引擎: {engine}")
                return False
                
        except Exception as e:
            logger.error(f"語音合成失敗: {e}")
            return False
        finally:
            self.is_speaking = False
    
    def _speak_with_gtts(self, text: str, language: Optional[str]) -> bool:
        """
        使用 Google TTS 進行語音合成
        
        Args:
            text: 要轉換的文字
            language: 語言代碼
            
        Returns:
            執行是否成功
        """
        try:
            lang = language or self.config['gtts']['language']
            slow = self.config['gtts']['slow']
            
            # 建立 gTTS 物件
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            # 保存到暫存檔案
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # 播放音訊
            success = self._play_audio_file(tmp_path)
            
            # 清理暫存檔案
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            
            if success:
                logger.info("Google TTS 播放完成")
            else:
                logger.error("Google TTS 播放失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"Google TTS 執行失敗: {e}")
            return False
    
    def _speak_with_pyttsx3(self, text: str) -> bool:
        """
        使用 pyttsx3 進行語音合成
        
        Args:
            text: 要轉換的文字
            
        Returns:
            執行是否成功
        """
        try:
            if not self.pyttsx3_engine:
                logger.error("pyttsx3 引擎未初始化")
                return False
            
            # 清空語音佇列
            self.pyttsx3_engine.stop()
            
            # 添加語音文字
            self.pyttsx3_engine.say(text)
            
            # 執行語音合成
            self.pyttsx3_engine.runAndWait()
            
            logger.info("pyttsx3 播放完成")
            return True
            
        except Exception as e:
            logger.error(f"pyttsx3 執行失敗: {e}")
            return False
    
    def _play_audio_file(self, file_path: str) -> bool:
        """
        播放音訊檔案
        
        Args:
            file_path: 音訊檔案路徑
            
        Returns:
            播放是否成功
        """
        try:
            if self.audio_player == 'pygame':
                return self._play_with_pygame(file_path)
            elif self.audio_player == 'simpleaudio':
                return self._play_with_simpleaudio(file_path)
            else:
                return self._play_with_system(file_path)
                
        except Exception as e:
            logger.error(f"音訊播放失敗: {e}")
            return False
    
    def _play_with_pygame(self, file_path: str) -> bool:
        """使用 pygame 播放音訊"""
        try:
            import pygame
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            return True
        except Exception as e:
            logger.error(f"pygame 播放失敗: {e}")
            return False
    
    def _play_with_simpleaudio(self, file_path: str) -> bool:
        """使用 simpleaudio 播放音訊"""
        try:
            # simpleaudio 主要支援 WAV 檔案
            # 需要先轉換 MP3 到 WAV
            logger.warning("simpleaudio 不直接支援 MP3，嘗試系統播放器")
            return self._play_with_system(file_path)
        except Exception as e:
            logger.error(f"simpleaudio 播放失敗: {e}")
            return False
    
    def _play_with_system(self, file_path: str) -> bool:
        """使用系統預設播放器"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", file_path], check=True)
            elif system == "Windows":
                subprocess.run(["start", file_path], shell=True, check=True)
            else:  # Linux
                subprocess.run(["aplay", file_path], check=True)
            
            return True
        except Exception as e:
            logger.error(f"系統播放器執行失敗: {e}")
            return False
    
    def stop_speaking(self) -> bool:
        """
        停止當前語音播放
        
        Returns:
            停止是否成功
        """
        try:
            if not self.is_speaking:
                return True
            
            # 停止 pyttsx3
            if self.pyttsx3_engine:
                self.pyttsx3_engine.stop()
            
            # 停止 pygame
            if self.audio_player == 'pygame':
                import pygame
                pygame.mixer.music.stop()
            
            self.is_speaking = False
            logger.info("語音播放已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止語音播放失敗: {e}")
            return False
    
    def is_engine_speaking(self) -> bool:
        """
        檢查是否正在播放語音
        
        Returns:
            是否正在播放
        """
        return self.is_speaking
    
    def set_language(self, language: str) -> bool:
        """
        設定 TTS 語言
        
        Args:
            language: 語言代碼
            
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
            'is_speaking': self.is_speaking,
            'audio_player': self.audio_player,
            'gtts_available': GTTS_AVAILABLE,
            'pyttsx3_available': PYTTSX3_AVAILABLE,
        }
    
    def cleanup(self) -> None:
        """清理 TTS 資源"""
        try:
            # 停止語音播放
            self.stop_speaking()
            
            # 等待播放執行緒結束
            if self.speaking_thread and self.speaking_thread.is_alive():
                self.speaking_thread.join(timeout=2.0)
            
            # 清理 pyttsx3 引擎
            if self.pyttsx3_engine:
                try:
                    self.pyttsx3_engine.stop()
                except Exception:
                    pass
            
            # 清理 pygame
            if self.audio_player == 'pygame':
                try:
                    import pygame
                    pygame.mixer.quit()
                except Exception:
                    pass
            
            logger.info("TTS 資源清理完成")
            
        except Exception as e:
            logger.error(f"TTS 資源清理失敗: {e}")
    
    def __del__(self) -> None:
        """解構函數，自動清理資源"""
        self.cleanup()
