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

from .switchbot_config import (
    SWITCHBOT_CREDENTIALS,
    SWITCHBOT_API_CONFIG,
    SWITCHBOT_LOG_CONFIG,
    SUPPORTED_DEVICE_TYPES,
    DEVICE_STATUS_MAPPING,
    API_ERROR_CODES,
    SWITCHBOT_PATHS,
    get_switchbot_config,
    validate_switchbot_config,
    get_device_id
)

__all__ = [
    # Voice config
    'AUDIO_CONFIG',
    'TTS_CONFIG', 
    'DETECTION_CONFIG',
    'ROBOT_CONFIG',
    'PATHS',
    'LOGGING_CONFIG',
    'get_config_value',
    'create_directories',
    
    # SwitchBot config
    'SWITCHBOT_CREDENTIALS',
    'SWITCHBOT_API_CONFIG',
    'SWITCHBOT_LOG_CONFIG',
    'SUPPORTED_DEVICE_TYPES',
    'DEVICE_STATUS_MAPPING',
    'API_ERROR_CODES',
    'SWITCHBOT_PATHS',
    'get_switchbot_config',
    'validate_switchbot_config',
    'get_device_id'
]
