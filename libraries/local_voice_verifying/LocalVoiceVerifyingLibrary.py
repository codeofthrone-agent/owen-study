"""
本地語音驗證 Robot Framework Library

提供語音合成、錄音和聲音檢測功能的 Robot Framework 關鍵字
支援 "PC 利用 google tts 發出聲音 Hey Power Pro 並同時錄音 檢測 是否收到 登登的聲音" 的測試需求
"""
import threading
import time
import os
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime

# Robot Framework
try:
    from robot.api.deco import keyword
    from robot.api import logger as robot_logger
    ROBOT_AVAILABLE = True
except ImportError:
    ROBOT_AVAILABLE = False
    # 如果 Robot Framework 不可用，建立假的 decorator
    def keyword(name=None, tags=None):
        def decorator(func):
            return func
        return decorator

# 內部模組匯入 - 處理相對/絕對匯入
try:
    # 嘗試從專案根目錄的 config 套件匯入
    import sys
    import os
    # 獲取當前檔案的目錄，然後向上兩級到專案根目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    project_root = os.path.abspath(project_root)  # 正規化路徑
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from config.voice_config import (
        ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG, DETECTION_CONFIG, 
        PATHS, get_config_value, create_directories
    )
    # 匯入其他模組
    from .voice_tts_manager import TTSManager
    from .voice_audio_recorder import AudioRecorder  
    from .voice_sound_detector import SoundDetector
except ImportError:
    try:
        # 嘗試相對匯入
        from .voice_tts_manager import TTSManager
        from .voice_audio_recorder import AudioRecorder  
        from .voice_sound_detector import SoundDetector
        from .voice_config import (
            ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG, DETECTION_CONFIG, 
            PATHS, get_config_value, create_directories
        )
    except ImportError:
        # 如果相對匯入失敗，嘗試絕對匯入
        try:
            from voice_tts_manager import TTSManager
            from voice_audio_recorder import AudioRecorder
            from voice_sound_detector import SoundDetector
            
            # 最後嘗試從 config 套件匯入（萬一路徑不對）
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..')
            project_root = os.path.abspath(project_root)
            
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
                
            from config.voice_config import (
                ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG, DETECTION_CONFIG,
                PATHS, get_config_value, create_directories
            )
        except ImportError as e:
            # 如果所有匯入都失敗，給出詳細錯誤訊息
            raise ImportError(f"無法匯入配置模組。請確認 config/voice_config.py 檔案存在。錯誤: {e}")

# 日誌
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)


class LocalVoiceVerifyingLibrary:
    """
    本地語音驗證 Robot Framework Library
    
    提供以下主要功能：
    1. 文字轉語音 (TTS) 播放
    2. 即時音訊錄製
    3. 聲音檢測與識別
    4. 整合式語音檢測流程
    
    Scope: GLOBAL
    """
    
    ROBOT_LIBRARY_SCOPE = ROBOT_CONFIG['library_scope']
    ROBOT_LIBRARY_VERSION = ROBOT_CONFIG['library_version']
    ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'
    
    def __init__(self):
        """初始化本地語音驗證 Library"""
        # 建立必要目錄
        create_directories()
        
        # 初始化核心模組
        self.tts_manager: Optional[TTSManager] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.sound_detector: Optional[SoundDetector] = None
        
        # 狀態管理
        self.is_initialized = False
        self.current_operation = None
        self.operation_thread = None
        
        # 檢測結果
        self.last_detection_result: Optional[Dict[str, Any]] = None
        self.detection_history: List[Dict[str, Any]] = []
        
        # 設定日誌
        self._setup_logging()
        
        # 自動初始化
        self._initialize_modules()
        
        if ROBOT_AVAILABLE:
            robot_logger.info("LocalVoiceVerifyingLibrary 初始化完成")
        else:
            print("LocalVoiceVerifyingLibrary 初始化完成 (非 Robot Framework 環境)")
    
    def _setup_logging(self) -> None:
        """設定日誌系統"""
        try:
            if LOGURU_AVAILABLE:
                # 移除預設處理器
                logger.remove()
                
                # 添加檔案日誌
                logger.add(
                    PATHS['logs'] / "voice_library.log",
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
                    level="INFO",
                    rotation="10 MB",
                    retention="30 days",
                    compression="zip",
                )
                
                # 添加控制台輸出 (只顯示重要訊息)
                logger.add(
                    lambda msg: print(msg),
                    level="WARNING",
                    format="{level} | {message}"
                )
            else:
                # 使用標準 logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    handlers=[
                        logging.FileHandler('logs/voice_library.log'),
                        logging.StreamHandler()
                    ]
                )
            
        except Exception as e:
            print(f"日誌設定失敗: {e}")
    
    def _initialize_modules(self) -> bool:
        """
        初始化所有核心模組
        
        Returns:
            初始化是否成功
        """
        try:
            logger.info("開始初始化核心模組...")
            
            # 初始化 TTS 管理器
            self.tts_manager = TTSManager()
            
            # 初始化音訊錄製器
            self.audio_recorder = AudioRecorder()
            
            # 初始化聲音檢測器
            self.sound_detector = SoundDetector()
            
            self.is_initialized = True
            logger.info("所有核心模組初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"模組初始化失敗: {e}")
            self.is_initialized = False
            return False
    
    # ===========================================
    # 主要 Robot Framework 關鍵字
    # ===========================================
    
    @keyword('Speak And Detect')
    def speak_and_detect(self, text: str, target_sound: str, 
                        duration: int = 10) -> bool:
        """
        播放指定文字並同時檢測目標聲音
        
        這是核心關鍵字，實現 "PC 利用 google tts 發出聲音 Hey Power Pro 並同時錄音 檢測 是否收到 登登的聲音" 的功能
        
        Args:
            text: 要播放的文字內容（例如："Hey Power Pro"）
            target_sound: 要檢測的目標聲音名稱（例如："登登"）
            duration: 錄音持續時間（秒），預設 10 秒
            
        Returns:
            檢測結果 True/False
            
        Examples:
            | Speak And Detect | Hey Power Pro | 登登 | 10 |
            | ${result} = | Speak And Detect | Hello World | 登登 |
        """
        try:
            if not self._check_initialization():
                return False
            
            logger.info(f"開始語音檢測流程: 播放='{text}', 檢測='{target_sound}', 時長={duration}秒")
            
            # 載入參考聲音
            if not self._ensure_reference_sound_loaded(target_sound):
                return False
            
            # 執行檢測流程
            success = self._execute_detection_cycle(text, target_sound, duration)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ 成功檢測到聲音: {target_sound}")
                else:
                    robot_logger.warn(f"✗ 未檢測到聲音: {target_sound}")
            
            return success
            
        except Exception as e:
            error_msg = f"Speak And Detect 執行失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    def _execute_detection_cycle(self, text: str, target_sound: str, 
                                duration: int) -> bool:
        """
        執行完整的檢測循環
        
        Args:
            text: TTS 文字
            target_sound: 目標聲音
            duration: 錄音時長
            
        Returns:
            檢測是否成功
        """
        try:
            # 1. 開始錄音
            if not self.audio_recorder.start_recording(duration):
                logger.error("無法開始錄音")
                return False
            
            # 等待錄音穩定
            time.sleep(0.5)
            
            # 2. 播放 TTS
            if not self.tts_manager.speak_text(text, async_mode=True):
                logger.error("TTS 播放失敗")
                self.audio_recorder.stop_recording()
                return False
            
            # 3. 等待錄音完成
            start_time = time.time()
            while self.audio_recorder.is_recording_active() and (time.time() - start_time) < duration + 5:
                time.sleep(0.1)
            
            # 4. 停止錄音
            self.audio_recorder.stop_recording()
            
            # 5. 獲取錄音數據
            audio_data = self.audio_recorder.get_audio_data()
            if len(audio_data) == 0:
                logger.error("錄音數據為空")
                return False
            
            # 6. 檢測聲音
            detected, confidence, details = self.sound_detector.detect_sound_in_audio(
                audio_data, target_sound
            )
            
            # 7. 保存檢測結果
            self.last_detection_result = details
            self.detection_history.append(details)
            
            # 8. 保存錄音檔案 (用於除錯)
            audio_file = self.audio_recorder.save_audio()
            if audio_file:
                details['audio_file'] = audio_file
            
            logger.info(f"檢測完成: 檢測到={detected}, 信心度={confidence:.3f}")
            return detected
            
        except Exception as e:
            logger.error(f"檢測循環執行失敗: {e}")
            return False
    
    def _ensure_reference_sound_loaded(self, sound_name: str) -> bool:
        """
        確保參考聲音已載入
        
        Args:
            sound_name: 聲音名稱
            
        Returns:
            載入是否成功
        """
        try:
            # 檢查是否已載入
            if sound_name in self.sound_detector.reference_features:
                return True
            
            # 嘗試載入參考聲音
            success = self.sound_detector.load_reference_sound(sound_name)
            
            if not success:
                logger.warning(f"參考聲音 '{sound_name}' 載入失敗，嘗試建立範例檔案")
                self._create_sample_reference_sound(sound_name)
                success = self.sound_detector.load_reference_sound(sound_name)
            
            return success
            
        except Exception as e:
            logger.error(f"載入參考聲音失敗: {e}")
            return False
    
    def _create_sample_reference_sound(self, sound_name: str) -> None:
        """建立範例參考聲音檔案（用於測試）"""
        try:
            # 這裡可以建立一個簡單的範例音訊檔案
            # 在實際使用時，使用者應該提供真實的參考聲音
            reference_dir = PATHS['reference_sounds']
            reference_dir.mkdir(parents=True, exist_ok=True)
            
            sample_file = reference_dir / f"{sound_name}_sample.txt"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(f"請將 '{sound_name}' 的參考音訊檔案放置在此目錄下\n")
                f.write(f"支援的格式: .wav, .mp3, .m4a\n")
                f.write(f"建議檔名: {sound_name}.wav\n")
            
            logger.info(f"已建立參考聲音指引檔案: {sample_file}")
            
        except Exception as e:
            logger.error(f"建立範例參考聲音失敗: {e}")
    
    @keyword('Start Voice Recording')
    def start_voice_recording(self, duration: int = 10) -> bool:
        """
        開始音訊錄製
        
        Args:
            duration: 錄音時長（秒），預設 10 秒
            
        Returns:
            錄音是否成功開始
            
        Examples:
            | Start Voice Recording | 15 |
            | Start Voice Recording |
        """
        try:
            if not self._check_initialization():
                return False
            
            success = self.audio_recorder.start_recording(duration)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ 開始錄音，時長: {duration}秒")
                else:
                    robot_logger.error("✗ 錄音開始失敗")
            
            return success
            
        except Exception as e:
            error_msg = f"Start Voice Recording 失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword('Stop Voice Recording')
    def stop_voice_recording(self) -> str:
        """
        停止音訊錄製
        
        Returns:
            錄音檔案路徑，失敗時回傳空字串
            
        Examples:
            | ${file_path} = | Stop Voice Recording |
        """
        try:
            if not self._check_initialization():
                return ""
            
            # 嘗試停止錄音 (如果還在錄音中)
            # 注意：如果錄音已自動完成，stop_recording() 會返回 False，但音訊數據仍可用
            self.audio_recorder.stop_recording()
            
            # 檢查是否有音訊數據可保存
            audio_data = self.audio_recorder.get_audio_data()
            if len(audio_data) == 0:
                if ROBOT_AVAILABLE:
                    robot_logger.error("✗ 沒有音訊數據可保存")
                return ""
            
            # 保存錄音檔案
            file_path = self.audio_recorder.save_audio()
            
            if ROBOT_AVAILABLE:
                if file_path:
                    robot_logger.info(f"✓ 錄音已停止並保存: {file_path}")
                else:
                    robot_logger.error("✗ 錄音保存失敗")
            
            return file_path or ""
            
        except Exception as e:
            error_msg = f"Stop Voice Recording 失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return ""
    
    @keyword('Detect Target Sound')
    def detect_target_sound(self, target_sound: str, 
                           audio_file: Optional[str] = None) -> bool:
        """
        檢測指定聲音
        
        Args:
            target_sound: 目標聲音名稱
            audio_file: 音訊檔案路徑（可選，預設使用當前錄音）
            
        Returns:
            檢測結果 True/False
            
        Examples:
            | ${detected} = | Detect Target Sound | 登登 |
            | ${detected} = | Detect Target Sound | 登登 | /path/to/audio.wav |
        """
        try:
            if not self._check_initialization():
                return False
            
            # 載入參考聲音
            if not self._ensure_reference_sound_loaded(target_sound):
                return False
            
            # 獲取音訊數據
            if audio_file:
                # 從檔案載入
                audio_data, sr = self.sound_detector._load_audio_file(audio_file)
                if audio_data is None:
                    return False
            else:
                # 使用當前錄音
                audio_data = self.audio_recorder.get_audio_data()
                if len(audio_data) == 0:
                    logger.error("沒有可用的音訊數據")
                    return False
                sr = self.audio_recorder.sample_rate
            
            # 執行檢測
            detected, confidence, details = self.sound_detector.detect_sound_in_audio(
                audio_data, target_sound, sr
            )
            
            # 保存結果
            self.last_detection_result = details
            
            if ROBOT_AVAILABLE:
                if detected:
                    robot_logger.info(f"✓ 檢測到聲音: {target_sound}, 信心度: {confidence:.3f}")
                else:
                    robot_logger.info(f"✗ 未檢測到聲音: {target_sound}, 信心度: {confidence:.3f}")
            
            return detected
            
        except Exception as e:
            error_msg = f"Detect Target Sound 失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword('Get Detection Result')
    def get_detection_result(self) -> Dict[str, Any]:
        """
        獲取最後一次檢測的詳細結果
        
        Returns:
            包含檢測詳細資訊的字典
            
        Examples:
            | ${result} = | Get Detection Result |
            | Should Be True | ${result['detected']} |
            | Should Be True | ${result['confidence']} > 0.7 |
        """
        try:
            if self.last_detection_result is None:
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'error': 'No detection result available'
                }
            
            return self.last_detection_result.copy()
            
        except Exception as e:
            logger.error(f"Get Detection Result 失敗: {e}")
            return {'error': str(e)}
    
    # ===========================================
    # 輔助關鍵字
    # ===========================================
    
    @keyword('Set Detection Threshold')
    def set_detection_threshold(self, threshold: float) -> bool:
        """
        設定聲音檢測閾值
        
        Args:
            threshold: 檢測閾值 (0.0-1.0)
            
        Returns:
            設定是否成功
            
        Examples:
            | Set Detection Threshold | 0.8 |
        """
        try:
            if not self._check_initialization():
                return False
            
            success = self.sound_detector.set_detection_threshold(threshold)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ 檢測閾值設定為: {threshold}")
                else:
                    robot_logger.error(f"✗ 檢測閾值設定失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"Set Detection Threshold 失敗: {e}")
            return False
    
    @keyword('Load Reference Sound')
    def load_reference_sound(self, sound_name: str, file_path: str) -> bool:
        """
        載入參考聲音檔案
        
        Args:
            sound_name: 聲音名稱標識
            file_path: 參考聲音檔案路徑
            
        Returns:
            載入是否成功
            
        Examples:
            | Load Reference Sound | 登登 | /path/to/dengdeng.wav |
        """
        try:
            if not self._check_initialization():
                return False
            
            success = self.sound_detector.load_reference_sound(sound_name, file_path)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ 參考聲音載入成功: {sound_name}")
                else:
                    robot_logger.error(f"✗ 參考聲音載入失敗: {sound_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Load Reference Sound 失敗: {e}")
            return False
    
    @keyword('Set TTS Language')
    def set_tts_language(self, language: str = 'en') -> bool:
        """
        設定 TTS 語言
        
        Args:
            language: 語言代碼 (例如: 'en', 'zh-TW')
            
        Returns:
            設定是否成功
            
        Examples:
            | Set TTS Language | en |
            | Set TTS Language | zh-TW |
        """
        try:
            if not self._check_initialization():
                return False
            
            success = self.tts_manager.set_language(language)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 語言設定為: {language}")
                else:
                    robot_logger.error(f"✗ TTS 語言設定失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"Set TTS Language 失敗: {e}")
            return False
    
    @keyword('Set TTS Speed')
    def set_tts_speed(self, speed: float = 1.0) -> bool:
        """
        設定 TTS 播放速度
        
        Args:
            speed: 播放速度倍率
            
        Returns:
            設定是否成功
            
        Examples:
            | Set TTS Speed | 1.5 |
            | Set TTS Speed | 0.8 |
        """
        try:
            if not self._check_initialization():
                return False
            
            success = self.tts_manager.set_voice_speed(speed * 150)  # 轉換為 words per minute
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 速度設定為: {speed}x")
                else:
                    robot_logger.error(f"✗ TTS 速度設定失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"Set TTS Speed 失敗: {e}")
            return False
    
    @keyword('Speak Text')
    def speak_text(self, text: str) -> bool:
        """
        播放指定的文字內容
        
        Args:
            text: 要播放的文字內容
            
        Returns:
            播放是否成功
            
        Examples:
            | Speak Text | Hey Power Pro |
            | Speak Text | Hello World |
        """
        try:
            if not self._check_initialization():
                return False
            
            logger.info(f"開始播放文字: '{text}'")
            
            # 使用 TTS 管理器播放文字
            success = self.tts_manager.speak_text(text, async_mode=False)
            
            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ 文字播放成功: {text}")
                else:
                    robot_logger.error(f"✗ 文字播放失敗: {text}")
            
            return success
            
        except Exception as e:
            error_msg = f"Speak Text 失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword('Cleanup Audio Resources')
    def cleanup_audio_resources(self) -> bool:
        """
        清理音訊資源
        
        Returns:
            清理是否成功
            
        Examples:
            | Cleanup Audio Resources |
        """
        try:
            success = True
            
            # 清理各個模組
            if self.tts_manager:
                self.tts_manager.cleanup()
            
            if self.audio_recorder:
                self.audio_recorder.cleanup()
            
            if self.sound_detector:
                self.sound_detector.cleanup()
            
            # 清理檢測歷史
            self.detection_history.clear()
            self.last_detection_result = None
            
            if ROBOT_AVAILABLE:
                robot_logger.info("✓ 音訊資源清理完成")
            
            return success
            
        except Exception as e:
            error_msg = f"Cleanup Audio Resources 失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    # ===========================================
    # 內部輔助方法
    # ===========================================
    
    def _check_initialization(self) -> bool:
        """檢查模組是否已初始化"""
        if not self.is_initialized:
            error_msg = "Library 尚未正確初始化"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
        return True
    
    def get_library_info(self) -> Dict[str, Any]:
        """
        獲取 Library 資訊
        
        Returns:
            Library 資訊字典
        """
        try:
            return {
                'version': self.ROBOT_LIBRARY_VERSION,
                'scope': self.ROBOT_LIBRARY_SCOPE,
                'is_initialized': self.is_initialized,
                'tts_available': self.tts_manager is not None,
                'recorder_available': self.audio_recorder is not None,
                'detector_available': self.sound_detector is not None,
                'detection_history_count': len(self.detection_history),
                'last_detection_time': self.last_detection_result.get('detection_time') if self.last_detection_result else None,
            }
            
        except Exception as e:
            logger.error(f"獲取 Library 資訊失敗: {e}")
            return {'error': str(e)}
    
    def __del__(self):
        """解構函數，自動清理資源"""
        try:
            self.cleanup_audio_resources()
        except:
            pass


# 如果直接執行此檔案，進行基本測試
if __name__ == "__main__":
    print("LocalVoiceVerifyingLibrary 基本測試")
    
    # 建立 Library 實例
    lib = LocalVoiceVerifyingLibrary()
    
    # 顯示資訊
    info = lib.get_library_info()
    print(f"Library 資訊: {info}")
    
    # 基本功能測試 (需要有音訊設備)
    try:
        # 測試 TTS 設定
        lib.set_tts_language('zh-TW')
        lib.set_tts_speed(1.0)
        
        # 測試閾值設定
        lib.set_detection_threshold(0.75)
        
        print("✓ 基本功能測試通過")
        
    except Exception as e:
        print(f"✗ 基本功能測試失敗: {e}")
    
    finally:
        # 清理資源
        lib.cleanup_audio_resources()
        print("✓ 資源清理完成")
