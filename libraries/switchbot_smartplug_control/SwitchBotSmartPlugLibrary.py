"""
SwitchBot 智慧插座控制 Robot Framework Library

提供 SwitchBot 智慧插座的控制功能，包括開關、狀態查詢等操作
支援 Robot Framework 測試案例中的電源管理和設備控制需求
"""
import os
import sys
import hmac
import hashlib
import base64
import time
import json
import logging
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

# 外部依賴
try:
    import requests
    SWITCHBOT_AVAILABLE = True
except ImportError:
    SWITCHBOT_AVAILABLE = False
    print("警告: requests 套件未安裝，請執行 'pipenv install requests'")

# 內部模組匯入 - 處理相對/絕對匯入
try:
    # 嘗試從專案根目錄的 config 套件匯入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    project_root = os.path.abspath(project_root)  # 正規化路徑
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from config.switchbot_config import (
        SWITCHBOT_API_CONFIG,
        SWITCHBOT_LOG_CONFIG, 
        SWITCHBOT_CREDENTIALS,
        SWITCHBOT_PATHS,
        SUPPORTED_DEVICE_TYPES,
        DEVICE_STATUS_MAPPING,
        API_ERROR_CODES,
        validate_switchbot_config,
        get_device_id
    )
    from config.voice_config import create_directories
    CONFIG_AVAILABLE = True
except ImportError:
    # 如果無法匯入配置，使用預設值
    CONFIG_AVAILABLE = False
    SWITCHBOT_PATHS = {
        'logs': 'logs',
        'config': 'config'
    }
    SWITCHBOT_API_CONFIG = {
        'api_url': 'https://api.switch-bot.com/v1.1',
        'api_timeout': 30,
        'retry_attempts': 3
    }
    SWITCHBOT_LOG_CONFIG = {
        'log_level': 'INFO',
        'log_file': 'switchbot_smartplug.log'
    }
    def create_directories():
        pass
    def validate_switchbot_config():
        return {'valid': False, 'errors': ['配置模組不可用']}
    def get_device_id(device_id=None):
        return device_id

class SwitchBotSmartPlugLibrary:
    """
    SwitchBot 智慧插座控制 Robot Framework Library
    
    提供完整的 SwitchBot 智慧插座控制功能，包括：
    - 設備連接與認證
    - 智慧插座開關控制
    - 設備狀態查詢
    - 電源管理功能
    - 設備資訊獲取
    - 錯誤處理與重試機制
    
    Example:
    | Library | libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py |
    | 設定SwitchBot認證資訊 | ${TOKEN} | ${SECRET} |
    | 當開啟智慧插座 | ${DEVICE_ID} |
    | 那麼智慧插座狀態應該是開啟 | ${DEVICE_ID} |
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        """
        初始化 SwitchBot 智慧插座控制庫
        
        設定基本配置、日誌記錄和必要的目錄結構
        """
        # 建立必要目錄
        create_directories()
        
        # 設定日誌
        self._setup_logging()
        
        # 初始化變數
        self.token = None
        self.secret = None
        self.client = None
        self.devices_cache = {}
        self.last_device_scan = None
        
        # 從統一配置載入設定
        self._load_config()
        
        self.logger.info("SwitchBot 智慧插座控制庫初始化完成")
    
    def _setup_logging(self):
        """設定日誌記錄"""
        if CONFIG_AVAILABLE:
            log_dir = Path(SWITCHBOT_PATHS.get('logs', 'logs'))
            log_config = SWITCHBOT_LOG_CONFIG
        else:
            log_dir = Path('logs')
            log_config = {'log_level': 'INFO', 'log_file': 'switchbot_smartplug.log'}
            
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / log_config['log_file']
        
        # 設定日誌格式
        log_format = log_config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('SwitchBotSmartPlug')
        self.logger.info("SwitchBot 智慧插座日誌系統啟動")
    
    def _load_config(self):
        """從統一配置系統載入設定"""
        if CONFIG_AVAILABLE:
            # 使用統一配置系統
            self.token = SWITCHBOT_CREDENTIALS.get('token')
            self.secret = SWITCHBOT_CREDENTIALS.get('secret')
            
            if self.token and self.secret:
                self.logger.info("從統一配置系統載入 SwitchBot 認證資訊")
                self._initialize_client()
            else:
                validation = validate_switchbot_config()
                if not validation['valid']:
                    self.logger.warning(f"配置驗證失敗: {', '.join(validation['errors'])}")
        else:
            # 回退到環境變數
            self._load_env_config()
    
    def _load_env_config(self):
        """從環境變數或 .env 檔案載入配置 (回退方案)"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        self.token = os.getenv('TOKEN') or os.getenv('SWITCHBOT_TOKEN')
        self.secret = os.getenv('SECRET') or os.getenv('SWITCHBOT_SECRET')
        
        if self.token and self.secret:
            self.logger.info("從環境變數載入 SwitchBot 認證資訊")
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化 SwitchBot 客戶端"""
        try:
            if not SWITCHBOT_AVAILABLE:
                raise ImportError("SwitchBot 套件未安裝")
            
            self.client = SwitchBot(token=self.token, secret=self.secret)
            self.logger.info("SwitchBot 客戶端初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"SwitchBot 客戶端初始化失敗: {e}")
            return False
    
    def _get_sign(self, token: str, secret: str, nonce: int) -> str:
        """
        產生 SwitchBot API 簽名
        
        Args:
            token: SwitchBot API Token
            secret: SwitchBot API Secret
            nonce: 時間戳記
            
        Returns:
            Base64 編碼的簽名字串
        """
        string_to_sign = f'{token}{int(nonce)}'.encode('utf-8')
        signature = base64.b64encode(
            hmac.new(
                secret.encode('utf-8'), 
                msg=string_to_sign, 
                digestmod=hashlib.sha256
            ).digest()
        )
        return signature.decode('utf-8')
    
    # === Robot Framework Keywords ===
    
    @keyword("設定SwitchBot認證資訊")
    def set_switchbot_credentials(self, token: str, secret: str) -> bool:
        """
        設定 SwitchBot API 認證資訊
        
        設定 SwitchBot API 的 Token 和 Secret，用於後續的設備控制操作
        
        Args:
            token: SwitchBot API Token
            secret: SwitchBot API Secret
            
        Returns:
            bool: 設定是否成功
            
        Example:
        | 設定SwitchBot認證資訊 | ${TOKEN} | ${SECRET} |
        """
        try:
            self.token = token
            self.secret = secret
            
            if self._initialize_client():
                self.logger.info("SwitchBot 認證資訊設定成功")
                if ROBOT_AVAILABLE:
                    robot_logger.info("SwitchBot 認證資訊設定成功")
                return True
            else:
                raise Exception("客戶端初始化失敗")
                
        except Exception as e:
            error_msg = f"設定 SwitchBot 認證資訊失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword("取得所有SwitchBot設備清單")
    def get_all_devices(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        取得所有 SwitchBot 設備清單
        
        獲取與帳戶關聯的所有 SwitchBot 設備資訊，包括設備 ID、名稱、類型等
        
        Args:
            force_refresh: 是否強制重新掃描設備（預設 False）
            
        Returns:
            List[Dict]: 設備清單，每個設備包含 deviceId, deviceName, deviceType 等資訊
            
        Example:
        | ${devices} | 取得所有SwitchBot設備清單 |
        | ${devices} | 取得所有SwitchBot設備清單 | force_refresh=True |
        """
        try:
            if not self.client:
                raise Exception("SwitchBot 客戶端尚未初始化，請先設定認證資訊")
            
            # 檢查快取
            current_time = time.time()
            if (not force_refresh and 
                self.devices_cache and 
                self.last_device_scan and 
                (current_time - self.last_device_scan) < 300):  # 5分鐘快取
                self.logger.info("使用快取的設備清單")
                return self.devices_cache.get('devices', [])
            
            # 使用直接 API 呼叫以獲得更好的控制
            url = "https://api.switch-bot.com/v1.1/devices"
            t = int(time.time() * 1000)
            sign = self._get_sign(self.token, self.secret, t)
            
            headers = {
                "Authorization": self.token,
                "sign": sign,
                "nonce": str(t),
                "t": str(t),
                "Content-Type": "application/json; charset=utf8"
            }
            
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if result.get("statusCode") == 100:
                devices = result.get("body", {}).get("deviceList", [])
                infrared_devices = result.get("body", {}).get("infraredRemoteList", [])
                
                all_devices = devices + infrared_devices
                
                # 更新快取
                self.devices_cache = {'devices': all_devices}
                self.last_device_scan = current_time
                
                self.logger.info(f"成功取得 {len(all_devices)} 個設備")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"找到 {len(all_devices)} 個 SwitchBot 設備")
                
                return all_devices
            else:
                error_msg = f"API 錯誤: {result.get('message', '未知錯誤')}"
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"取得設備清單失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return []
    
    @keyword("查詢設備資訊")
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """
        查詢特定設備的詳細資訊
        
        根據設備 ID 查詢設備的詳細資訊，包括名稱、類型、狀態等
        
        Args:
            device_id: 設備 ID
            
        Returns:
            Dict: 設備資訊字典
            
        Example:
        | ${device_info} | 查詢設備資訊 | ${DEVICE_ID} |
        """
        try:
            devices = self.get_all_devices()
            
            for device in devices:
                if device.get('deviceId') == device_id:
                    self.logger.info(f"找到設備: {device.get('deviceName')} ({device_id})")
                    if ROBOT_AVAILABLE:
                        robot_logger.info(f"設備資訊: {device.get('deviceName')} - {device.get('deviceType')}")
                    return device
            
            error_msg = f"找不到設備 ID: {device_id}"
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"查詢設備資訊失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return {}
    
    @keyword("當開啟智慧插座")
    def turn_on_smart_plug(self, device_id: str) -> bool:
        """
        開啟智慧插座
        
        將指定的智慧插座設定為開啟狀態
        
        Args:
            device_id: 智慧插座設備 ID
            
        Returns:
            bool: 操作是否成功
            
        Example:
        | 當開啟智慧插座 | ${DEVICE_ID} |
        """
        try:
            if not self.client:
                raise Exception("SwitchBot 客戶端尚未初始化")
            
            device = self.client.device(id=device_id)
            device.command("turnOn")
            
            self.logger.info(f"智慧插座 {device_id} 已開啟")
            if ROBOT_AVAILABLE:
                robot_logger.info(f"智慧插座 {device_id} 開啟成功")
            
            return True
            
        except Exception as e:
            error_msg = f"開啟智慧插座失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword("當關閉智慧插座")
    def turn_off_smart_plug(self, device_id: str) -> bool:
        """
        關閉智慧插座
        
        將指定的智慧插座設定為關閉狀態
        
        Args:
            device_id: 智慧插座設備 ID
            
        Returns:
            bool: 操作是否成功
            
        Example:
        | 當關閉智慧插座 | ${DEVICE_ID} |
        """
        try:
            if not self.client:
                raise Exception("SwitchBot 客戶端尚未初始化")
            
            device = self.client.device(id=device_id)
            device.command("turnOff")
            
            self.logger.info(f"智慧插座 {device_id} 已關閉")
            if ROBOT_AVAILABLE:
                robot_logger.info(f"智慧插座 {device_id} 關閉成功")
            
            return True
            
        except Exception as e:
            error_msg = f"關閉智慧插座失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword("取得智慧插座狀態")
    def get_smart_plug_status(self, device_id: str) -> str:
        """
        取得智慧插座目前狀態
        
        查詢指定智慧插座的目前電源狀態
        
        Args:
            device_id: 智慧插座設備 ID
            
        Returns:
            str: 插座狀態 ("on", "off", "unknown")
            
        Example:
        | ${status} | 取得智慧插座狀態 | ${DEVICE_ID} |
        """
        try:
            if not self.client:
                raise Exception("SwitchBot 客戶端尚未初始化")
            
            device = self.client.device(id=device_id)
            status = device.status()
            
            power_state = status.get('power', 'unknown')
            
            self.logger.info(f"智慧插座 {device_id} 狀態: {power_state}")
            if ROBOT_AVAILABLE:
                robot_logger.info(f"智慧插座狀態: {power_state}")
            
            return power_state
            
        except Exception as e:
            error_msg = f"取得智慧插座狀態失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return "unknown"
    
    @keyword("那麼智慧插座狀態應該是開啟")
    def verify_smart_plug_is_on(self, device_id: str) -> bool:
        """
        驗證智慧插座狀態為開啟
        
        檢查指定智慧插座是否處於開啟狀態
        
        Args:
            device_id: 智慧插座設備 ID
            
        Returns:
            bool: 狀態是否為開啟
            
        Example:
        | 那麼智慧插座狀態應該是開啟 | ${DEVICE_ID} |
        """
        try:
            status = self.get_smart_plug_status(device_id)
            is_on = status.lower() == "on"
            
            if is_on:
                self.logger.info(f"驗證成功: 智慧插座 {device_id} 狀態為開啟")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"驗證成功: 智慧插座狀態為開啟")
            else:
                error_msg = f"驗證失敗: 智慧插座 {device_id} 狀態為 {status}，預期為 on"
                raise AssertionError(error_msg)
            
            return is_on
            
        except Exception as e:
            error_msg = f"驗證智慧插座開啟狀態失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            raise AssertionError(error_msg)
    
    @keyword("那麼智慧插座狀態應該是關閉")
    def verify_smart_plug_is_off(self, device_id: str) -> bool:
        """
        驗證智慧插座狀態為關閉
        
        檢查指定智慧插座是否處於關閉狀態
        
        Args:
            device_id: 智慧插座設備 ID
            
        Returns:
            bool: 狀態是否為關閉
            
        Example:
        | 那麼智慧插座狀態應該是關閉 | ${DEVICE_ID} |
        """
        try:
            status = self.get_smart_plug_status(device_id)
            is_off = status.lower() == "off"
            
            if is_off:
                self.logger.info(f"驗證成功: 智慧插座 {device_id} 狀態為關閉")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"驗證成功: 智慧插座狀態為關閉")
            else:
                error_msg = f"驗證失敗: 智慧插座 {device_id} 狀態為 {status}，預期為 off"
                raise AssertionError(error_msg)
            
            return is_off
            
        except Exception as e:
            error_msg = f"驗證智慧插座關閉狀態失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            raise AssertionError(error_msg)
    
    @keyword("等待設備狀態變更")
    def wait_for_device_status_change(self, device_id: str, expected_status: str, timeout: int = 30) -> bool:
        """
        等待設備狀態變更到指定狀態
        
        在指定時間內等待設備狀態變更到預期狀態
        
        Args:
            device_id: 設備 ID
            expected_status: 預期狀態 ("on" 或 "off")
            timeout: 超時時間（秒），預設 30 秒
            
        Returns:
            bool: 是否在超時前達到預期狀態
            
        Example:
        | 等待設備狀態變更 | ${DEVICE_ID} | on | 30 |
        """
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current_status = self.get_smart_plug_status(device_id)
                
                if current_status.lower() == expected_status.lower():
                    self.logger.info(f"設備 {device_id} 狀態已變更為 {expected_status}")
                    if ROBOT_AVAILABLE:
                        robot_logger.info(f"設備狀態變更成功: {expected_status}")
                    return True
                
                time.sleep(2)  # 每2秒檢查一次
            
            error_msg = f"設備 {device_id} 在 {timeout} 秒內未變更到狀態 {expected_status}"
            raise TimeoutError(error_msg)
            
        except Exception as e:
            error_msg = f"等待設備狀態變更失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False
    
    @keyword("執行設備電源重啟")
    def restart_device_power(self, device_id: str, off_duration: int = 5) -> bool:
        """
        執行設備電源重啟
        
        先關閉設備，等待指定時間後再開啟，模擬電源重啟
        
        Args:
            device_id: 設備 ID
            off_duration: 關閉持續時間（秒），預設 5 秒
            
        Returns:
            bool: 重啟操作是否成功
            
        Example:
        | 執行設備電源重啟 | ${DEVICE_ID} | 10 |
        """
        try:
            # 先關閉設備
            if not self.turn_off_smart_plug(device_id):
                raise Exception("關閉設備失敗")
            
            # 等待狀態變更為關閉
            if not self.wait_for_device_status_change(device_id, "off", 30):
                self.logger.warning("設備狀態未確認為關閉，但繼續重啟流程")
            
            # 等待指定時間
            self.logger.info(f"等待 {off_duration} 秒後重新開啟設備")
            time.sleep(off_duration)
            
            # 重新開啟設備
            if not self.turn_on_smart_plug(device_id):
                raise Exception("開啟設備失敗")
            
            # 等待狀態變更為開啟
            if not self.wait_for_device_status_change(device_id, "on", 30):
                raise Exception("設備重啟後未能成功開啟")
            
            self.logger.info(f"設備 {device_id} 電源重啟完成")
            if ROBOT_AVAILABLE:
                robot_logger.info("設備電源重啟完成")
            
            return True
            
        except Exception as e:
            error_msg = f"設備電源重啟失敗: {e}"
            self.logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False


# 為了向後相容，提供別名
SwitchBotLib = SwitchBotSmartPlugLibrary

if __name__ == "__main__":
    # 測試程式碼
    lib = SwitchBotSmartPlugLibrary()
    print("SwitchBot 智慧插座控制庫測試")
    
    # 這裡可以添加基本的測試邏輯
    if lib.token and lib.secret:
        devices = lib.get_all_devices()
        print(f"找到 {len(devices)} 個設備")
        for device in devices:
            print(f"  - {device.get('deviceName')} ({device.get('deviceId')})")
    else:
        print("未設定認證資訊，請設定 SWITCHBOT_TOKEN 和 SWITCHBOT_SECRET 環境變數")
