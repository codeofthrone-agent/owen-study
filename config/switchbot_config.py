"""
SwitchBot 智慧插座配置模組
整合 .env 環境變數與系統配置
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 嘗試載入環境變數
try:
    from dotenv import load_dotenv
    # 載入專案根目錄和模組目錄的 .env 檔案
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / '.env')
    load_dotenv(project_root / 'libraries' / 'switchbot_smartplug_control' / '.env')
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# SwitchBot API 認證設定 (從環境變數讀取)
SWITCHBOT_CREDENTIALS = {
    'token': os.getenv('TOKEN') or os.getenv('SWITCHBOT_TOKEN'),
    'secret': os.getenv('SECRET') or os.getenv('SWITCHBOT_SECRET'),
    'device_id': os.getenv('DEVICE_ID') or os.getenv('SWITCHBOT_DEVICE_ID')
}

# SwitchBot API 配置
SWITCHBOT_API_CONFIG = {
    # API 基本設定
    'api_url': 'https://api.switch-bot.com/v1.1',
    'api_timeout': int(os.getenv('SWITCHBOT_API_TIMEOUT', '30')),
    'retry_attempts': int(os.getenv('SWITCHBOT_RETRY_ATTEMPTS', '3')),
    'retry_delay': int(os.getenv('SWITCHBOT_RETRY_DELAY', '2')),
    
    # 認證設定
    'token': SWITCHBOT_CREDENTIALS['token'],
    'secret': SWITCHBOT_CREDENTIALS['secret'],
    'default_device_id': SWITCHBOT_CREDENTIALS['device_id'],
    
    # 設備掃描設定
    'device_cache_duration': 300,  # 5分鐘
    'status_check_interval': 2,    # 2秒
    'status_timeout': 30,          # 30秒
    
    # 電源控制設定
    'power_on_delay': 1,           # 開啟後等待時間
    'power_off_delay': 1,          # 關閉後等待時間
    'restart_off_duration': 5,     # 重啟時關閉持續時間
}

# 日誌配置
SWITCHBOT_LOG_CONFIG = {
    'log_level': os.getenv('SWITCHBOT_LOG_LEVEL', 'INFO'),
    'log_file': 'switchbot_smartplug.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# 支援的設備類型
SUPPORTED_DEVICE_TYPES = [
    'Plug Mini (US)',
    'Plug Mini (JP)', 
    'Plug',
    'Smart Plug'
]

# 設備狀態映射
DEVICE_STATUS_MAPPING = {
    'on': ['on', 'true', '1', 'active'],
    'off': ['off', 'false', '0', 'inactive'],
    'unknown': ['unknown', 'error', 'unavailable']
}

# API 錯誤代碼映射
API_ERROR_CODES = {
    100: 'Success',
    101: 'API請求失敗',
    102: '認證失敗',
    103: '無效的API Token',
    104: '無效的設備ID',
    105: '設備不在線',
    106: '設備類型不支援',
    107: '設備忙碌中',
    108: '設備未回應',
    109: '命令執行失敗',
    110: '網路連線錯誤',
    190: '其他API錯誤'
}

# 路徑配置
SWITCHBOT_PATHS = {
    'project_root': Path(__file__).parent.parent,
    'logs': Path(__file__).parent.parent / 'logs',
    'config': Path(__file__).parent,
    'library': Path(__file__).parent.parent / 'libraries' / 'switchbot_smartplug_control',
    'tests': Path(__file__).parent.parent / 'tests' / 'power_management',
    'resources': Path(__file__).parent.parent / 'resources'
}

def get_switchbot_config() -> Dict[str, Any]:
    """
    取得完整的 SwitchBot 配置
    
    Returns:
        Dict: 包含所有配置的字典
    """
    return {
        'credentials': SWITCHBOT_CREDENTIALS,
        'api': SWITCHBOT_API_CONFIG,
        'logging': SWITCHBOT_LOG_CONFIG,
        'device_types': SUPPORTED_DEVICE_TYPES,
        'status_mapping': DEVICE_STATUS_MAPPING,
        'error_codes': API_ERROR_CODES,
        'paths': SWITCHBOT_PATHS
    }

def validate_switchbot_config() -> Dict[str, Any]:
    """
    驗證 SwitchBot 配置是否完整
    
    Returns:
        Dict: 驗證結果，包含 'valid' 布林值和 'errors' 列表
    """
    errors = []
    
    # 檢查必要的認證資訊
    if not SWITCHBOT_CREDENTIALS['token']:
        errors.append('缺少 SWITCHBOT_TOKEN 或 TOKEN 環境變數')
    
    if not SWITCHBOT_CREDENTIALS['secret']:
        errors.append('缺少 SWITCHBOT_SECRET 或 SECRET 環境變數')
    
    # 檢查路徑是否存在
    if not SWITCHBOT_PATHS['logs'].exists():
        SWITCHBOT_PATHS['logs'].mkdir(parents=True, exist_ok=True)
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'dotenv_available': DOTENV_AVAILABLE
    }

def get_device_id(device_id: Optional[str] = None) -> Optional[str]:
    """
    取得設備 ID，優先使用參數，其次使用環境變數
    
    Args:
        device_id: 指定的設備 ID
        
    Returns:
        str: 設備 ID 或 None
    """
    return device_id or SWITCHBOT_CREDENTIALS['device_id']

# 匯出主要配置供其他模組使用
__all__ = [
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
