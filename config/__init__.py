"""
配置模組套件
"""
from .voice_config import (
    AUDIO_CONFIG,
    TTS_CONFIG,
    DETECTION_CONFIG,
    ROBOT_CONFIG,
    PATHS,
    LOGGING_CONFIG,
    get_config_value,
    create_directories
)

__all__ = [
    'AUDIO_CONFIG',
    'TTS_CONFIG', 
    'DETECTION_CONFIG',
    'ROBOT_CONFIG',
    'PATHS',
    'LOGGING_CONFIG',
    'get_config_value',
    'create_directories'
]
