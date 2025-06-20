"""
本地語音驗證系統配置模組
包含所有系統設定參數與常數定義
"""
import os
from pathlib import Path
from typing import Dict, Any

# 專案根目錄 - 調整為從 config 資料夾向上一層
PROJECT_ROOT = Path(__file__).parent.parent

# 音訊處理配置
AUDIO_CONFIG: Dict[str, Any] = {
    # 基本音訊參數
    'sample_rate': 16000,      # 16kHz 語音優化取樣率
    'channels': 1,             # 單聲道
    'chunk_size': 1024,        # 緩衝區大小
    'format': 'int16',         # 音訊格式
    'device_index': None,      # 音訊裝置索引 (None=預設)
    
    # 錄音設定
    'default_record_duration': 10,  # 預設錄音時長(秒)
    'max_record_duration': 60,      # 最大錄音時長(秒)
    'min_record_duration': 1,       # 最小錄音時長(秒)
    
    # 緩衝與延遲設定
    'buffer_size': 2048,            # 音訊緩衝區大小
    'processing_delay': 0.1,        # 處理延遲(秒)
    'max_processing_delay': 0.5,    # 最大可接受延遲(秒)
}

# TTS 引擎配置
TTS_CONFIG: Dict[str, Any] = {
    # 引擎選擇
    'primary_engine': 'gtts',       # 主要引擎: gtts (Google TTS)
    'fallback_engine': 'pyttsx3',   # 備援引擎: pyttsx3 (離線)
    
    # Google TTS 設定
    'gtts': {
        'language': 'en',           # 預設語言 - 使用英文（避免 en-US deprecated 警告）
        'slow': False,              # 語速 (False=正常, True=慢)
        'timeout': 10,              # 網路超時(秒)
        'retry_attempts': 3,        # 重試次數
    },
    
    # pyttsx3 設定
    'pyttsx3': {
        'rate': 180,                # 語速 (words per minute) - 標準速度，清晰易懂
        'volume': 0.8,              # 音量 (0.0-1.0)
        'voice_id': 0,              # 語音ID (0=預設)
        'command_rate': 120,        # 指令語音的特殊語速 (更慢更清楚)
    },
    
    # 播放設定
    'playback': {
        'async_mode': True,         # 非同步播放
        'wait_for_completion': False, # 是否等待播放完成
        'max_playback_time': 30,    # 最大播放時間(秒)
    }
}

# 聲音檢測配置
DETECTION_CONFIG: Dict[str, Any] = {
    # 檢測參數
    'default_threshold': 0.75,      # 預設檢測閾值
    'min_threshold': 0.5,           # 最小閾值
    'max_threshold': 0.95,          # 最大閾值
    
    # 特徵提取參數
    'mfcc_features': 13,            # MFCC 特徵數量
    'window_size': 0.025,           # 窗口大小(秒)
    'hop_length': 0.01,             # 跳躍長度(秒)
    'n_fft': 512,                   # FFT 點數
    
    # MFCC 參數配置
    'mfcc': {
        'n_mfcc': 13,               # MFCC 係數數量
        'n_fft': 512,               # FFT 窗口大小
        'hop_length': 160,          # 跳躍長度 (10ms at 16kHz)
        'win_length': 400,          # 窗口長度 (25ms at 16kHz)
        'window': 'hann',           # 窗口函數
        'center': True,             # 是否中心化
        'pad_mode': 'constant',     # 填充模式
        'power': 2.0,               # 功率譜密度指數
        'lifter': 22,               # 倒譜提升係數
        'fmin': 0.0,                # 最小頻率
        'fmax': None,               # 最大頻率 (None = sr/2)
    },
    
    # 檢測窗口配置
    'window': {
        'size': 0.025,              # 窗口大小(秒)
        'overlap': 0.5,             # 重疊比例
        'step': 0.0125,             # 步進大小(秒)
    },
    
    # DTW (動態時間規整) 參數
    'dtw_radius': 1,                # DTW 半徑
    'dtw_step_pattern': 'symmetric2', # DTW 步驟模式
    'dtw_distance_only': False,     # 只計算距離
    
    # 檢測窗口設定
    'detection_window': 2.0,        # 檢測窗口(秒)
    'overlap_ratio': 0.5,           # 重疊比例
    'min_detection_length': 0.5,    # 最小檢測長度(秒)
    
    # 信心度計算
    'confidence_method': 'inverse_distance', # 信心度計算方法
    'max_distance': 100.0,          # 最大距離
    'confidence_smoothing': True,    # 信心度平滑
}

# Robot Framework 配置
ROBOT_CONFIG: Dict[str, Any] = {
    'library_scope': 'GLOBAL',      # Library 作用域
    'library_version': '1.0.0',     # Library 版本
    'auto_keywords': True,          # 自動關鍵字
    'doc_format': 'ROBOT',          # 文件格式
}

# 路徑配置 - 基於專案根目錄
PATHS: Dict[str, Path] = {
    'project_root': PROJECT_ROOT,
    'audio_samples': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'audio_samples',
    'reference_sounds': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'audio_samples' / 'reference_sounds',
    'recorded': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'audio_samples' / 'recorded',
    'temp': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'audio_samples' / 'temp',
    'logs': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'logs',
    'models': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'models',
    'test_data': PROJECT_ROOT / 'libraries' / 'local_voice_verifying' / 'test_data',
}

# 日誌配置
LOGGING_CONFIG: Dict[str, Any] = {
    'level': 'INFO',
    'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}',
    'rotation': '10 MB',
    'retention': '7 days',
    'compression': 'zip',
    'backtrace': True,              # 啟用回溯資訊
    'diagnose': True,               # 啟用診斷資訊
    'files': {
        'main': PATHS['logs'] / 'voice_library.log',
        'tts': PATHS['logs'] / 'tts_manager.log',
        'audio': PATHS['logs'] / 'audio_recorder.log',
        'detector': PATHS['logs'] / 'sound_detector.log',
    }
}

def get_config_value(config_dict: Dict[str, Any], key_path: str, default=None):
    """
    獲取配置值，支援巢狀鍵值
    
    Args:
        config_dict: 配置字典
        key_path: 鍵值路徑 (如 'tts.gtts.language')
        default: 預設值
        
    Returns:
        配置值或預設值
    """
    try:
        keys = key_path.split('.')
        value = config_dict
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def create_directories():
    """建立必要的目錄結構"""
    for path_name, path in PATHS.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"警告: 無法建立目錄 {path}: {e}")

# 在模組載入時自動建立目錄
create_directories()
