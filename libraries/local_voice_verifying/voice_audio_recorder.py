"""
音訊錄製管理模組
負責處理音訊錄製、緩衝區管理和檔案保存功能
"""
import threading
import time
import wave
import numpy as np
from typing import Optional, List, Tuple, Any, Dict
from pathlib import Path
import tempfile
from datetime import datetime

# 音訊處理
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# 配置匯入 - 支援新的 config 套件結構
try:
    # 嘗試從專案根目錄的 config 套件匯入
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.voice_config import AUDIO_CONFIG, LOGGING_CONFIG, PATHS
except ImportError:
    try:
        from .voice_config import AUDIO_CONFIG, LOGGING_CONFIG, PATHS
    except ImportError:
        # 向後相容：嘗試直接匯入
        from voice_config import AUDIO_CONFIG, LOGGING_CONFIG, PATHS

# 日誌處理
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


class AudioRecorder:
    """
    音訊錄製管理器
    支援即時錄音、緩衝區管理和音訊檔案保存
    """
    
    def __init__(self):
        """初始化音訊錄製管理器"""
        self.config = AUDIO_CONFIG
        self.paths = PATHS
        
        # 音訊設備
        self.pyaudio_instance = None
        self.stream = None
        
        # 錄音狀態
        self.is_recording = False
        self.recording_thread = None
        self.audio_buffer = []
        self.recording_start_time = None
        self.recording_duration = 0
        
        # 音訊參數
        self.sample_rate = self.config['sample_rate']
        self.channels = self.config['channels']
        self.chunk_size = self.config['chunk_size']
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        
        # 初始化日誌
        self._setup_logger()
        
        # 初始化音訊設備
        self._init_audio_device()
        
        logger.info("AudioRecorder 初始化完成")
    
    def _setup_logger(self) -> None:
        """設定日誌記錄器"""
        try:
            if not LOGURU_AVAILABLE:
                # 使用標準 logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    handlers=[
                        logging.FileHandler('logs/audio_recorder.log'),
                        logging.StreamHandler()
                    ]
                )
                return
            
            # 移除預設處理器 (如果已存在)
            logger.remove()
            
            # 添加音訊錄製專用日誌
            logger.add(
                self.paths['logs'] / "audio_recorder.log",
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
    
    def _init_audio_device(self) -> bool:
        """
        初始化音訊設備
        
        Returns:
            初始化是否成功
        """
        try:
            if not PYAUDIO_AVAILABLE:
                logger.error("pyaudio 套件未安裝")
                return False
            
            # 初始化 PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # 檢查音訊設備
            device_count = self.pyaudio_instance.get_device_count()
            logger.info(f"偵測到 {device_count} 個音訊設備")
            
            # 尋找預設輸入設備
            default_input = self.pyaudio_instance.get_default_input_device_info()
            logger.info(f"預設輸入設備: {default_input['name']}")
            
            # 測試音訊格式支援
            self._test_audio_format()
            
            return True
            
        except Exception as e:
            logger.error(f"音訊設備初始化失敗: {e}")
            return False
    
    def _test_audio_format(self) -> bool:
        """
        測試音訊格式支援
        
        Returns:
            格式是否支援
        """
        try:
            # 測試錄音參數
            self.pyaudio_instance.is_format_supported(
                rate=self.sample_rate,
                input_device=None,
                input_channels=self.channels,
                input_format=self.format
            )
            
            logger.info(f"音訊格式支援確認: {self.sample_rate}Hz, {self.channels}聲道")
            return True
            
        except Exception as e:
            logger.warning(f"音訊格式測試失敗: {e}")
            # 嘗試調整參數
            return self._adjust_audio_parameters()
    
    def _adjust_audio_parameters(self) -> bool:
        """
        自動調整音訊參數
        
        Returns:
            調整是否成功
        """
        try:
            # 嘗試不同的取樣率
            sample_rates = [16000, 22050, 44100, 48000]
            for rate in sample_rates:
                try:
                    self.pyaudio_instance.is_format_supported(
                        rate=rate,
                        input_device=None,
                        input_channels=self.channels,
                        input_format=self.format
                    )
                    self.sample_rate = rate
                    logger.info(f"自動調整取樣率為: {rate}Hz")
                    return True
                except:
                    continue
            
            logger.error("無法找到支援的音訊格式")
            return False
            
        except Exception as e:
            logger.error(f"音訊參數調整失敗: {e}")
            return False
    
    def start_recording(self, duration: Optional[int] = None) -> bool:
        """
        開始音訊錄製
        
        Args:
            duration: 錄音時長(秒)，None 表示手動停止
            
        Returns:
            錄音是否成功開始
        """
        try:
            if self.is_recording:
                logger.warning("錄音已在進行中")
                return False
            
            if not self.pyaudio_instance:
                logger.error("音訊設備未初始化")
                return False
            
            # 設定錄音參數
            record_duration = duration or self.config['default_record_duration']
            
            # 清空緩衝區
            self.audio_buffer.clear()
            self.recording_start_time = datetime.now()
            
            # 建立音訊串流
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # 開始錄音執行緒
            self.is_recording = True
            self.recording_thread = threading.Thread(
                target=self._recording_loop,
                args=(record_duration,)
            )
            self.recording_thread.start()
            
            logger.info(f"開始錄音，預定時長: {record_duration}秒")
            return True
            
        except Exception as e:
            logger.error(f"開始錄音失敗: {e}")
            self.is_recording = False
            return False
    
    def _recording_loop(self, duration: int) -> None:
        """
        錄音迴圈
        
        Args:
            duration: 錄音時長
        """
        try:
            start_time = time.time()
            
            while self.is_recording:
                # 檢查時間限制
                if time.time() - start_time >= duration:
                    break
                
                # 讀取音訊數據
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # 轉換為 numpy 陣列
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # 添加到緩衝區
                    self.audio_buffer.append(audio_data)
                    
                except Exception as e:
                    logger.error(f"讀取音訊數據失敗: {e}")
                    break
            
            # 記錄實際錄音時長
            self.recording_duration = time.time() - start_time
            logger.info(f"錄音完成，實際時長: {self.recording_duration:.2f}秒")
            
        except Exception as e:
            logger.error(f"錄音迴圈錯誤: {e}")
        finally:
            self._stop_recording_stream()
    
    def stop_recording(self) -> bool:
        """
        停止音訊錄製
        
        Returns:
            停止是否成功
        """
        try:
            if not self.is_recording:
                logger.warning("目前沒有在錄音")
                return False
            
            # 設定停止標誌
            self.is_recording = False
            
            # 等待錄音執行緒結束
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            
            logger.info("錄音已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止錄音失敗: {e}")
            return False
    
    def _stop_recording_stream(self) -> None:
        """停止音訊串流"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            self.is_recording = False
            
        except Exception as e:
            logger.error(f"停止音訊串流失敗: {e}")
    
    def get_audio_data(self) -> np.ndarray:
        """
        獲取錄音數據
        
        Returns:
            音訊數據陣列
        """
        try:
            if not self.audio_buffer:
                logger.warning("音訊緩衝區為空")
                return np.array([])
            
            # 合併所有音訊片段
            audio_data = np.concatenate(self.audio_buffer)
            return audio_data
            
        except Exception as e:
            logger.error(f"獲取音訊數據失敗: {e}")
            return np.array([])
    
    def get_audio_buffer(self) -> List[np.ndarray]:
        """
        獲取音訊緩衝區
        
        Returns:
            音訊緩衝區列表
        """
        return self.audio_buffer.copy()
    
    def save_audio(self, filename: Optional[str] = None, 
                  output_dir: Optional[Path] = None) -> Optional[str]:
        """
        保存錄音檔案
        
        Args:
            filename: 檔案名稱
            output_dir: 輸出目錄
            
        Returns:
            保存的檔案路徑或 None
        """
        try:
            # 檢查是否有音訊數據
            audio_data = self.get_audio_data()
            if len(audio_data) == 0:
                logger.warning("沒有音訊數據可保存")
                return None
            
            # 設定檔案路徑
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
            
            if not output_dir:
                output_dir = self.paths['recorded']
            
            # 確保目錄存在
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / filename
            
            # 保存 WAV 檔案
            if SOUNDFILE_AVAILABLE:
                # 使用 soundfile 保存
                sf.write(
                    str(file_path),
                    audio_data,
                    self.sample_rate,
                    subtype='PCM_16'
                )
            else:
                # 使用 wave 保存
                self._save_with_wave(str(file_path), audio_data)
            
            logger.info(f"音訊檔案已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存音訊檔案失敗: {e}")
            return None
    
    def _save_with_wave(self, file_path: str, audio_data: np.ndarray) -> None:
        """
        使用 wave 模組保存音訊檔案
        
        Args:
            file_path: 檔案路徑
            audio_data: 音訊數據
        """
        try:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
                
        except Exception as e:
            logger.error(f"使用 wave 保存檔案失敗: {e}")
            raise
    
    def get_recording_info(self) -> Dict[str, Any]:
        """
        獲取錄音資訊
        
        Returns:
            錄音資訊字典
        """
        audio_data = self.get_audio_data()
        
        return {
            'is_recording': self.is_recording,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'buffer_count': len(self.audio_buffer),
            'total_samples': len(audio_data),
            'duration_seconds': len(audio_data) / self.sample_rate if len(audio_data) > 0 else 0,
            'recording_start_time': self.recording_start_time,
            'recording_duration': self.recording_duration,
            'audio_level': self._calculate_audio_level(audio_data),
        }
    
    def _calculate_audio_level(self, audio_data: np.ndarray) -> float:
        """
        計算音訊音量等級
        
        Args:
            audio_data: 音訊數據
            
        Returns:
            音量等級 (0-1)
        """
        try:
            if len(audio_data) == 0:
                return 0.0
            
            # 計算 RMS (Root Mean Square)
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            
            # 正規化到 0-1 範圍
            max_value = 32767.0  # 16-bit 最大值
            normalized_level = min(rms / max_value, 1.0)
            
            return normalized_level
            
        except Exception as e:
            logger.error(f"計算音訊等級失敗: {e}")
            return 0.0
    
    def is_recording_active(self) -> bool:
        """
        檢查是否正在錄音
        
        Returns:
            是否正在錄音
        """
        return self.is_recording
    
    def clear_buffer(self) -> None:
        """清空音訊緩衝區"""
        try:
            self.audio_buffer.clear()
            logger.info("音訊緩衝區已清空")
        except Exception as e:
            logger.error(f"清空緩衝區失敗: {e}")
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        """
        獲取音訊設備列表
        
        Returns:
            設備資訊列表
        """
        devices = []
        try:
            if not self.pyaudio_instance:
                return devices
            
            device_count = self.pyaudio_instance.get_device_count()
            
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                
                # 只保留輸入設備
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'max_input_channels': device_info['maxInputChannels'],
                        'default_sample_rate': device_info['defaultSampleRate'],
                        'is_default': i == self.pyaudio_instance.get_default_input_device_info()['index']
                    })
            
            return devices
            
        except Exception as e:
            logger.error(f"獲取設備列表失敗: {e}")
            return devices
    
    def set_input_device(self, device_index: int) -> bool:
        """
        設定輸入設備
        
        Args:
            device_index: 設備索引
            
        Returns:
            設定是否成功
        """
        try:
            if self.is_recording:
                logger.warning("錄音進行中，無法更改設備")
                return False
            
            # 測試設備是否可用
            device_info = self.pyaudio_instance.get_device_info_by_index(device_index)
            
            if device_info['maxInputChannels'] == 0:
                logger.error(f"設備 {device_index} 不支援音訊輸入")
                return False
            
            # 更新設備索引 (需要在建立串流時使用)
            self.input_device_index = device_index
            logger.info(f"輸入設備設定為: {device_info['name']}")
            return True
            
        except Exception as e:
            logger.error(f"設定輸入設備失敗: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理音訊資源"""
        try:
            # 停止錄音
            if self.is_recording:
                self.stop_recording()
            
            # 清理音訊串流
            self._stop_recording_stream()
            
            # 關閉 PyAudio
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            # 清空緩衝區
            self.audio_buffer.clear()
            
            logger.info("音訊資源清理完成")
            
        except Exception as e:
            logger.error(f"音訊資源清理失敗: {e}")
    
    def __del__(self) -> None:
        """解構函數，自動清理資源"""
        self.cleanup()
