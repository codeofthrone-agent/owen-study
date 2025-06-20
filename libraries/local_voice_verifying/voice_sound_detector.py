"""
聲音檢測管理模組
負責處理聲音特徵提取、相似度比對和目標聲音檢測
"""
import os
import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
import pickle
import json
from datetime import datetime

# 音訊分析
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import scipy.signal
    import scipy.spatial.distance
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

# 配置匯入 - 支援新的 config 套件結構
try:
    # 嘗試從專案根目錄的 config 套件匯入
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.voice_config import DETECTION_CONFIG, AUDIO_CONFIG, PATHS, LOGGING_CONFIG
except ImportError:
    try:
        from .voice_config import DETECTION_CONFIG, AUDIO_CONFIG, PATHS, LOGGING_CONFIG
    except ImportError:
        from voice_config import DETECTION_CONFIG, AUDIO_CONFIG, PATHS, LOGGING_CONFIG

# 日誌處理
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


class SoundDetector:
    """
    聲音檢測管理器
    支援 MFCC 特徵提取、DTW 比對和即時聲音檢測
    """
    
    def __init__(self):
        """初始化聲音檢測管理器"""
        self.config = DETECTION_CONFIG
        self.audio_config = AUDIO_CONFIG
        self.paths = PATHS
        
        # 檢測參數
        self.threshold = self.config['default_threshold']
        self.sample_rate = self.audio_config['sample_rate']
        
        # 特徵提取參數
        self.mfcc_config = self.config['mfcc']
        self.window_config = self.config['window']
        
        # 參考聲音庫
        self.reference_sounds: Dict[str, Dict[str, Any]] = {}
        self.reference_features: Dict[str, np.ndarray] = {}
        
        # 檢測歷史
        self.detection_history: List[Dict[str, Any]] = []
        self.last_detection_result: Optional[Dict[str, Any]] = None
        
        # 初始化日誌
        self._setup_logger()
        
        # 初始化特徵提取器
        self._init_feature_extractor()
        
        logger.info("SoundDetector 初始化完成")
    
    def _setup_logger(self) -> None:
        """設定日誌記錄器"""
        try:
            if not LOGURU_AVAILABLE:
                # 使用標準 logging
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    handlers=[
                        logging.FileHandler('logs/sound_detector.log'),
                        logging.StreamHandler()
                    ]
                )
                return
            
            # 移除預設處理器 (如果已存在)
            logger.remove()
            
            # 添加聲音檢測專用日誌
            logger.add(
                self.paths['logs'] / "sound_detector.log",
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
    
    def _init_feature_extractor(self) -> bool:
        """
        初始化特徵提取器
        
        Returns:
            初始化是否成功
        """
        try:
            if not LIBROSA_AVAILABLE:
                logger.error("librosa 套件未安裝，無法進行音訊分析")
                return False
            
            if not SCIPY_AVAILABLE:
                logger.warning("scipy 套件未安裝，部分功能可能受限")
            
            if not SKLEARN_AVAILABLE:
                logger.warning("sklearn 套件未安裝，使用基本相似度計算")
            
            logger.info("特徵提取器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"特徵提取器初始化失敗: {e}")
            return False
    
    def load_reference_sound(self, sound_name: str, 
                           file_path: Optional[str] = None) -> bool:
        """
        載入參考聲音檔案
        
        Args:
            sound_name: 聲音名稱標識
            file_path: 音訊檔案路徑
            
        Returns:
            載入是否成功
        """
        try:
            if not file_path:
                # 嘗試從預設目錄載入
                reference_dir = self.paths['reference_sounds']
                possible_files = [
                    reference_dir / f"{sound_name}.wav",
                    reference_dir / f"{sound_name}.mp3",
                    reference_dir / f"{sound_name}.m4a",
                ]
                
                file_path = None
                for f in possible_files:
                    if f.exists():
                        file_path = str(f)
                        break
                
                if not file_path:
                    logger.error(f"找不到參考聲音檔案: {sound_name}")
                    return False
            
            # 載入音訊檔案
            audio_data, sr = self._load_audio_file(file_path)
            if audio_data is None:
                return False
            
            # 提取特徵
            features = self.extract_mfcc_features(audio_data, sr)
            if features is None:
                return False
            
            # 儲存參考聲音
            self.reference_sounds[sound_name] = {
                'file_path': file_path,
                'audio_data': audio_data,
                'sample_rate': sr,
                'features': features,
                'loaded_time': datetime.now(),
                'feature_shape': features.shape,
            }
            
            self.reference_features[sound_name] = features
            
            logger.info(f"參考聲音 '{sound_name}' 載入成功，特徵維度: {features.shape}")
            return True
            
        except Exception as e:
            logger.error(f"載入參考聲音失敗: {e}")
            return False
    
    def _load_audio_file(self, file_path: str) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """
        載入音訊檔案
        
        Args:
            file_path: 音訊檔案路徑
            
        Returns:
            (音訊數據, 取樣率) 或 (None, None)
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"音訊檔案不存在: {file_path}")
                return None, None
            
            if LIBROSA_AVAILABLE:
                # 使用 librosa 載入
                audio_data, sr = librosa.load(file_path, sr=None)
                
                # 重新取樣到目標取樣率
                if sr != self.sample_rate:
                    audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
                    sr = self.sample_rate
                
                return audio_data, sr
            
            elif SOUNDFILE_AVAILABLE:
                # 使用 soundfile 載入
                audio_data, sr = sf.read(file_path)
                
                # 如果是立體聲，轉換為單聲道
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                return audio_data, sr
            
            else:
                logger.error("無可用的音訊載入庫")
                return None, None
                
        except Exception as e:
            logger.error(f"載入音訊檔案失敗: {e}")
            return None, None
    
    def extract_mfcc_features(self, audio_data: np.ndarray, 
                             sample_rate: Optional[int] = None) -> Optional[np.ndarray]:
        """
        提取 MFCC 特徵
        
        Args:
            audio_data: 音訊數據
            sample_rate: 取樣率
            
        Returns:
            MFCC 特徵陣列或 None
        """
        try:
            if not LIBROSA_AVAILABLE:
                logger.error("librosa 未安裝，無法提取 MFCC 特徵")
                return None
            
            if sample_rate is None:
                sample_rate = self.sample_rate
            
            # 確保音訊數據不為空
            if len(audio_data) == 0:
                logger.warning("音訊數據為空")
                return None
            
            # 提取 MFCC 特徵
            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=self.mfcc_config['n_mfcc'],
                n_fft=self.mfcc_config['n_fft'],
                hop_length=self.mfcc_config['hop_length'],
                win_length=self.mfcc_config['win_length'],
                window=self.mfcc_config['window'],
                center=self.mfcc_config['center'],
                pad_mode=self.mfcc_config['pad_mode']
            )
            
            # 計算 delta 和 delta-delta 特徵
            delta_mfcc = librosa.feature.delta(mfcc)
            delta2_mfcc = librosa.feature.delta(mfcc, order=2)
            
            # 合併特徵
            features = np.concatenate([mfcc, delta_mfcc, delta2_mfcc], axis=0)
            
            # 轉置以符合 (時間, 特徵) 格式
            features = features.T
            
            logger.debug(f"MFCC 特徵提取完成，維度: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"MFCC 特徵提取失敗: {e}")
            return None
    
    def calculate_dtw_distance(self, features1: np.ndarray, 
                              features2: np.ndarray) -> float:
        """
        計算動態時間規整 (DTW) 距離
        
        Args:
            features1: 第一組特徵
            features2: 第二組特徵
            
        Returns:
            DTW 距離
        """
        try:
            if not SCIPY_AVAILABLE:
                # 使用簡單的歐幾里得距離作為備援
                return self._calculate_simple_distance(features1, features2)
            
            # 實作簡化的 DTW 算法
            return self._dtw_distance(features1, features2)
            
        except Exception as e:
            logger.error(f"DTW 距離計算失敗: {e}")
            return float('inf')
    
    def _dtw_distance(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        實作 DTW 距離計算
        
        Args:
            features1: 第一組特徵
            features2: 第二組特徵
            
        Returns:
            DTW 距離
        """
        try:
            m, n = len(features1), len(features2)
            
            # 建立距離矩陣
            distance_matrix = np.full((m, n), float('inf'))
            
            # 計算特徵間的歐幾里得距離
            for i in range(m):
                for j in range(n):
                    distance_matrix[i, j] = np.linalg.norm(features1[i] - features2[j])
            
            # 建立累積距離矩陣
            dtw_matrix = np.full((m + 1, n + 1), float('inf'))
            dtw_matrix[0, 0] = 0
            
            # 計算 DTW 路徑
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    cost = distance_matrix[i-1, j-1]
                    dtw_matrix[i, j] = cost + min(
                        dtw_matrix[i-1, j],      # 插入
                        dtw_matrix[i, j-1],      # 刪除
                        dtw_matrix[i-1, j-1]     # 匹配
                    )
            
            # 正規化距離
            dtw_distance = dtw_matrix[m, n] / (m + n)
            
            return dtw_distance
            
        except Exception as e:
            logger.error(f"DTW 計算錯誤: {e}")
            return float('inf')
    
    def _calculate_simple_distance(self, features1: np.ndarray, 
                                  features2: np.ndarray) -> float:
        """
        計算簡單距離（備援方法）
        
        Args:
            features1: 第一組特徵
            features2: 第二組特徵
            
        Returns:
            距離值
        """
        try:
            # 調整特徵長度
            min_len = min(len(features1), len(features2))
            f1 = features1[:min_len]
            f2 = features2[:min_len]
            
            # 計算平均歐幾里得距離
            distance = np.mean(np.linalg.norm(f1 - f2, axis=1))
            
            return distance
            
        except Exception as e:
            logger.error(f"簡單距離計算失敗: {e}")
            return float('inf')
    
    def calculate_similarity_score(self, features1: np.ndarray, 
                                  features2: np.ndarray) -> float:
        """
        計算相似度分數
        
        Args:
            features1: 第一組特徵
            features2: 第二組特徵
            
        Returns:
            相似度分數 (0-1)
        """
        try:
            if SKLEARN_AVAILABLE:
                # 使用餘弦相似度
                f1_mean = np.mean(features1, axis=0).reshape(1, -1)
                f2_mean = np.mean(features2, axis=0).reshape(1, -1)
                
                similarity = cosine_similarity(f1_mean, f2_mean)[0, 0]
                
                # 確保範圍在 0-1
                similarity = max(0, min(1, (similarity + 1) / 2))
                
            else:
                # 使用距離轉換為相似度
                distance = self.calculate_dtw_distance(features1, features2)
                
                # 將距離轉換為相似度 (0-1)
                similarity = 1 / (1 + distance)
            
            return similarity
            
        except Exception as e:
            logger.error(f"相似度計算失敗: {e}")
            return 0.0
    
    def detect_sound_in_audio(self, audio_data: np.ndarray, 
                             target_sound: str,
                             sample_rate: Optional[int] = None) -> Tuple[bool, float, Dict[str, Any]]:
        """
        在音訊中檢測目標聲音
        
        Args:
            audio_data: 音訊數據
            target_sound: 目標聲音名稱
            sample_rate: 取樣率
            
        Returns:
            (檢測到, 信心度, 詳細資訊)
        """
        try:
            if target_sound not in self.reference_features:
                logger.error(f"參考聲音 '{target_sound}' 未載入")
                return False, 0.0, {'error': 'Reference sound not loaded'}
            
            if sample_rate is None:
                sample_rate = self.sample_rate
            
            # 提取音訊特徵
            features = self.extract_mfcc_features(audio_data, sample_rate)
            if features is None:
                return False, 0.0, {'error': 'Feature extraction failed'}
            
            # 獲取參考特徵
            reference_features = self.reference_features[target_sound]
            
            # 計算相似度
            similarity = self.calculate_similarity_score(features, reference_features)
            
            # 判斷是否檢測到
            detected = similarity >= self.threshold
            
            # 建立詳細資訊
            details = {
                'target_sound': target_sound,
                'similarity_score': similarity,
                'threshold': self.threshold,
                'detected': detected,
                'audio_length': len(audio_data),
                'sample_rate': sample_rate,
                'feature_shape': features.shape,
                'detection_time': datetime.now(),
            }
            
            # 記錄檢測結果
            self.last_detection_result = details
            self.detection_history.append(details.copy())
            
            # 限制歷史記錄數量
            if len(self.detection_history) > 100:
                self.detection_history = self.detection_history[-100:]
            
            logger.info(f"聲音檢測完成: {target_sound}, 相似度: {similarity:.3f}, 檢測到: {detected}")
            
            return detected, similarity, details
            
        except Exception as e:
            logger.error(f"聲音檢測失敗: {e}")
            return False, 0.0, {'error': str(e)}
    
    def detect_sound_in_windows(self, audio_data: np.ndarray,
                               target_sound: str,
                               sample_rate: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        使用滑動窗口檢測聲音
        
        Args:
            audio_data: 音訊數據
            target_sound: 目標聲音名稱
            sample_rate: 取樣率
            
        Returns:
            檢測結果列表
        """
        try:
            if sample_rate is None:
                sample_rate = self.sample_rate
            
            # 計算窗口參數
            window_samples = int(self.window_config['size'] * sample_rate)
            hop_samples = int(window_samples * (1 - self.window_config['overlap']))
            
            results = []
            
            # 滑動窗口檢測
            for start in range(0, len(audio_data) - window_samples, hop_samples):
                end = start + window_samples
                window_audio = audio_data[start:end]
                
                # 檢測當前窗口
                detected, confidence, details = self.detect_sound_in_audio(
                    window_audio, target_sound, sample_rate
                )
                
                # 添加窗口資訊
                details.update({
                    'window_start': start / sample_rate,
                    'window_end': end / sample_rate,
                    'window_index': len(results),
                })
                
                results.append(details)
            
            logger.info(f"滑動窗口檢測完成，總窗口數: {len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"滑動窗口檢測失敗: {e}")
            return []
    
    def set_detection_threshold(self, threshold: float) -> bool:
        """
        設定檢測閾值
        
        Args:
            threshold: 檢測閾值 (0-1)
            
        Returns:
            設定是否成功
        """
        try:
            if not (0 <= threshold <= 1):
                logger.error(f"無效的閾值: {threshold}，應在 0-1 範圍內")
                return False
            
            self.threshold = threshold
            logger.info(f"檢測閾值設定為: {threshold}")
            return True
            
        except Exception as e:
            logger.error(f"設定檢測閾值失敗: {e}")
            return False
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        獲取檢測統計資訊
        
        Returns:
            統計資訊字典
        """
        try:
            if not self.detection_history:
                return {'total_detections': 0}
            
            total_detections = len(self.detection_history)
            successful_detections = sum(1 for d in self.detection_history if d['detected'])
            
            confidences = [d['similarity_score'] for d in self.detection_history]
            
            stats = {
                'total_detections': total_detections,
                'successful_detections': successful_detections,
                'success_rate': successful_detections / total_detections,
                'average_confidence': np.mean(confidences),
                'max_confidence': np.max(confidences),
                'min_confidence': np.min(confidences),
                'current_threshold': self.threshold,
                'loaded_references': list(self.reference_sounds.keys()),
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"獲取統計資訊失敗: {e}")
            return {'error': str(e)}
    
    def save_reference_features(self, output_file: Optional[str] = None) -> bool:
        """
        保存參考特徵到檔案
        
        Args:
            output_file: 輸出檔案路徑
            
        Returns:
            保存是否成功
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = str(self.paths['models'] / f"reference_features_{timestamp}.pkl")
            
            # 確保目錄存在
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存特徵
            with open(output_file, 'wb') as f:
                pickle.dump(self.reference_sounds, f)
            
            logger.info(f"參考特徵已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存參考特徵失敗: {e}")
            return False
    
    def load_reference_features(self, input_file: str) -> bool:
        """
        從檔案載入參考特徵
        
        Args:
            input_file: 輸入檔案路徑
            
        Returns:
            載入是否成功
        """
        try:
            if not os.path.exists(input_file):
                logger.error(f"特徵檔案不存在: {input_file}")
                return False
            
            # 載入特徵
            with open(input_file, 'rb') as f:
                self.reference_sounds = pickle.load(f)
            
            # 重建特徵字典
            self.reference_features = {}
            for name, data in self.reference_sounds.items():
                self.reference_features[name] = data['features']
            
            logger.info(f"參考特徵已載入，共 {len(self.reference_sounds)} 個聲音")
            return True
            
        except Exception as e:
            logger.error(f"載入參考特徵失敗: {e}")
            return False
    
    def get_last_detection_result(self) -> Optional[Dict[str, Any]]:
        """
        獲取最後一次檢測結果
        
        Returns:
            檢測結果字典或 None
        """
        return self.last_detection_result
    
    def clear_detection_history(self) -> None:
        """清空檢測歷史"""
        self.detection_history.clear()
        self.last_detection_result = None
        logger.info("檢測歷史已清空")
    
    def cleanup(self) -> None:
        """清理檢測器資源"""
        try:
            # 清空參考聲音
            self.reference_sounds.clear()
            self.reference_features.clear()
            
            # 清空檢測歷史
            self.clear_detection_history()
            
            logger.info("聲音檢測器資源清理完成")
            
        except Exception as e:
            logger.error(f"聲音檢測器資源清理失敗: {e}")
    
    def __del__(self) -> None:
        """解構函數，自動清理資源"""
        self.cleanup()
