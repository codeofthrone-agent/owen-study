"""
IP Camera 配置管理模組

負責載入和管理 IP Camera 的環境配置，支援多環境切換（實驗室、RV 車等）。

使用範例:
    from config.ipcam_config import get_camera_config, get_all_cameras, LIGHT_DETECTION_CONFIG

    # 取得特定環境的攝影機配置
    lab_cameras = get_all_cameras('taipei_lab')

    # 取得單一攝影機配置
    level1_config = get_camera_config('taipei_lab', 'level1')

    # 取得燈光檢測設定
    threshold = LIGHT_DETECTION_CONFIG['brightness_threshold']['bright']
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger
from dotenv import load_dotenv


# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# 載入 .env 環境變數
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    logger.debug(f"已載入環境變數: {ENV_FILE}")
else:
    logger.warning(f".env 文件不存在: {ENV_FILE}")

# YAML 配置文件路徑
CONFIG_FILE = PROJECT_ROOT / "config" / "ipcam_config.yaml"

# 從環境變數讀取共用的 IP Camera 認證資訊
DEFAULT_IPCAM_USERNAME = os.getenv('IPCAM_USERNAME', '')
DEFAULT_IPCAM_PASSWORD = os.getenv('IPCAM_PASSWORD', '')


def load_config() -> Dict[str, Any]:
    """
    載入 IP Camera YAML 配置文件

    Returns:
        Dict[str, Any]: 完整的配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML 格式錯誤
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.info(f"成功載入 IP Camera 配置: {CONFIG_FILE}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"YAML 配置文件格式錯誤: {e}")
        raise


# 載入配置
try:
    _CONFIG = load_config()
except Exception as e:
    logger.error(f"無法載入 IP Camera 配置: {e}")
    _CONFIG = {
        'environments': {},
        'light_detection': {
            'brightness_threshold': {'dark': 50, 'bright': 150},
            'image_processing': {
                'capture_delay': 1.0,
                'analysis_region': 'center',
                'sample_size': 100
            },
            'connection': {
                'timeout': 10,
                'retry_attempts': 3,
                'retry_delay': 2
            }
        }
    }


# 環境配置
ENVIRONMENTS = _CONFIG.get('environments', {})

# 燈光檢測配置
LIGHT_DETECTION_CONFIG = _CONFIG.get('light_detection', {})


def get_all_cameras(environment: str = 'taipei_lab') -> Dict[str, Dict[str, Any]]:
    """
    取得指定環境的所有攝影機配置

    Args:
        environment (str): 環境名稱，預設為 'taipei_lab'
                          可選值: 'taipei_lab', 'rv_car'

    Returns:
        Dict[str, Dict[str, Any]]: 該環境所有攝影機的配置字典

    Raises:
        ValueError: 環境不存在

    使用範例:
        >>> cameras = get_all_cameras('taipei_lab')
        >>> print(cameras['level1']['ip'])
        '192.168.165.184'
    """
    if environment not in ENVIRONMENTS:
        available = ', '.join(ENVIRONMENTS.keys())
        raise ValueError(f"環境 '{environment}' 不存在。可用環境: {available}")

    return ENVIRONMENTS[environment].get('cameras', {})


def get_camera_config(environment: str, camera_name: str) -> Dict[str, Any]:
    """
    取得特定攝影機的配置

    Args:
        environment (str): 環境名稱 (如: 'taipei_lab', 'rv_car')
        camera_name (str): 攝影機名稱 (如: 'level1', 'level2', 'motor')

    Returns:
        Dict[str, Any]: 攝影機配置字典，包含 ip, port, protocol 等資訊

    配置優先順序:
        1. YAML 配置文件中的 username/password（若有設定）
        2. .env 文件中的 IPCAM_USERNAME/IPCAM_PASSWORD（共用認證）
        3. 空字串（無認證）

    Raises:
        ValueError: 環境或攝影機不存在

    使用範例:
        >>> config = get_camera_config('taipei_lab', 'level1')
        >>> print(f"攝影機 URL: {config['protocol']}://{config['ip']}:{config['port']}")
        '攝影機 URL: rtsp://192.168.165.184:554'
    """
    cameras = get_all_cameras(environment)

    if camera_name not in cameras:
        available = ', '.join(cameras.keys())
        raise ValueError(
            f"攝影機 '{camera_name}' 在環境 '{environment}' 中不存在。"
            f"可用攝影機: {available}"
        )

    config = cameras[camera_name].copy()  # 複製以避免修改原始配置

    # 如果 YAML 中沒有設定 username/password，使用環境變數的預設值
    if not config.get('username'):
        config['username'] = DEFAULT_IPCAM_USERNAME
    if not config.get('password'):
        config['password'] = DEFAULT_IPCAM_PASSWORD

    return config


def get_all_fp2_sensors(environment: str = 'taipei_lab') -> Dict[str, Dict[str, Any]]:
    """
    取得指定環境的所有 FP2 雷達感測器配置

    Args:
        environment (str): 環境名稱，預設為 'taipei_lab'

    Returns:
        Dict[str, Dict[str, Any]]: 該環境所有 FP2 雷達的配置字典

    Raises:
        ValueError: 環境不存在
    """
    if environment not in ENVIRONMENTS:
        available = ', '.join(ENVIRONMENTS.keys())
        raise ValueError(f"環境 '{environment}' 不存在。可用環境: {available}")

    return ENVIRONMENTS[environment].get('fp2_sensors', {})


def get_fp2_config(environment: str, sensor_id: str) -> Dict[str, Any]:
    """
    取得特定 FP2 雷達感測器的配置

    Args:
        environment (str): 環境名稱 (如: 'rv_car')
        sensor_id (str): 感測器 ID (如: 'awning_fp2')

    Returns:
        Dict[str, Any]: FP2 配置字典，包含 alias, setup_code, description 等

    Raises:
        ValueError: 環境或感測器不存在
    """
    sensors = get_all_fp2_sensors(environment)

    if sensor_id not in sensors:
        available = ', '.join(sensors.keys()) if sensors else '無'
        raise ValueError(
            f"FP2 感測器 '{sensor_id}' 在環境 '{environment}' 中不存在。"
            f"可用感測器: {available}"
        )

    config = sensors[sensor_id].copy()
    
    # 從環境變數注入 setup_code (支援專屬如 AWNING_FP2_SETUP_CODE 或共用的 FP2_SETUP_CODE)
    if not config.get('setup_code'):
        specific_env_key = f"{sensor_id.upper()}_SETUP_CODE"
        config['setup_code'] = os.getenv(specific_env_key) or os.getenv('FP2_SETUP_CODE', '')

    return config


def get_camera_url(environment: str, camera_name: str, path: str = "") -> str:
    """
    建立攝影機的完整 URL（支援 HTTP 和 RTSP）

    Args:
        environment (str): 環境名稱
        camera_name (str): 攝影機名稱
        path (str): API 路徑，若為空且為 RTSP 則使用 stream_path

    Returns:
        str: 完整的攝影機 URL

    使用範例:
        >>> # HTTP 範例
        >>> url = get_camera_url('taipei_lab', 'level1', '/snapshot')
        >>> print(url)
        'http://192.168.165.184:80/snapshot'

        >>> # RTSP 範例
        >>> url = get_camera_url('taipei_lab', 'level1')
        >>> print(url)
        'rtsp://username:password@192.168.165.184:554/live0'
    """
    config = get_camera_config(environment, camera_name)

    protocol = config.get('protocol', 'http')
    ip = config['ip']
    port = config.get('port', 80 if protocol == 'http' else 554)
    username = config.get('username', '')
    password = config.get('password', '')

    # 建立 RTSP URL
    if protocol.lower() == 'rtsp':
        # 如果沒有指定 path，使用 stream_path
        if not path:
            path = config.get('stream_path', '/live0')

        # 確保 path 以 / 開頭
        if not path.startswith('/'):
            path = f"/{path}"

        # 如果有帳號密碼，加入認證資訊
        if username:
            auth = f"{username}:{password}@" if password else f"{username}@"
            return f"{protocol}://{auth}{ip}:{port}{path}"
        else:
            return f"{protocol}://{ip}:{port}{path}"

    # 建立 HTTP URL
    else:
        # 確保 path 以 / 開頭
        if path and not path.startswith('/'):
            path = f"/{path}"

        return f"{protocol}://{ip}:{port}{path}"


def get_brightness_threshold(level: str = 'bright') -> int:
    """
    取得亮度閾值

    Args:
        level (str): 亮度等級，'dark' 或 'bright'

    Returns:
        int: 亮度閾值

    使用範例:
        >>> bright_threshold = get_brightness_threshold('bright')
        >>> print(bright_threshold)
        150
    """
    thresholds = LIGHT_DETECTION_CONFIG.get('brightness_threshold', {})
    return thresholds.get(level, 100)


def get_connection_config() -> Dict[str, Any]:
    """
    取得連線配置

    Returns:
        Dict[str, Any]: 連線配置字典

    使用範例:
        >>> conn_config = get_connection_config()
        >>> timeout = conn_config['timeout']
        >>> print(f"連線逾時: {timeout} 秒")
        '連線逾時: 10 秒'
    """
    return LIGHT_DETECTION_CONFIG.get('connection', {})


def list_available_environments() -> list:
    """
    列出所有可用的環境

    Returns:
        list: 環境名稱列表

    使用範例:
        >>> envs = list_available_environments()
        >>> print(envs)
        ['taipei_lab', 'rv_car']
    """
    return list(ENVIRONMENTS.keys())


def list_available_cameras(environment: str) -> list:
    """
    列出指定環境的所有攝影機

    Args:
        environment (str): 環境名稱

    Returns:
        list: 攝影機名稱列表

    使用範例:
        >>> cameras = list_available_cameras('taipei_lab')
        >>> print(cameras)
        ['level1', 'level2', 'motor']
    """
    cameras = get_all_cameras(environment)
    return list(cameras.keys())


# 便利常數：實驗室環境的攝影機配置
try:
    LABORATORY_CAMERAS = get_all_cameras('taipei_lab')
    LEVEL1_CONFIG = get_camera_config('taipei_lab', 'level1')
    LEVEL2_CONFIG = get_camera_config('taipei_lab', 'level2')
    MOTOR_CONFIG = get_camera_config('taipei_lab', 'motor')
except ValueError:
    logger.warning("實驗室環境配置不完整，使用預設空配置")
    LABORATORY_CAMERAS = {}
    LEVEL1_CONFIG = {}
    LEVEL2_CONFIG = {}
    MOTOR_CONFIG = {}


if __name__ == "__main__":
    # 測試配置載入
    print("=" * 50)
    print("IP Camera 配置測試")
    print("=" * 50)

    # 列出所有環境
    print("\n可用環境:")
    for env in list_available_environments():
        print(f"  - {env}")
        cameras = list_available_cameras(env)
        if cameras:
            print(f"    攝影機: {', '.join(cameras)}")

    # 測試實驗室環境配置
    print("\n實驗室環境配置:")
    try:
        for camera_name in ['level1', 'level2', 'motor']:
            config = get_camera_config('taipei_lab', camera_name)
            url = get_camera_url('taipei_lab', camera_name, '/snapshot')
            print(f"\n  {camera_name}:")
            print(f"    IP: {config['ip']}")
            print(f"    描述: {config.get('description', 'N/A')}")
            print(f"    URL: {url}")
    except ValueError as e:
        print(f"錯誤: {e}")

    # 顯示燈光檢測配置
    print("\n燈光檢測配置:")
    print(f"  暗閾值: {get_brightness_threshold('dark')}")
    print(f"  亮閾值: {get_brightness_threshold('bright')}")
    print(f"  連線逾時: {get_connection_config()['timeout']} 秒")
    print(f"  重試次數: {get_connection_config()['retry_attempts']}")

    print("\n" + "=" * 50)
