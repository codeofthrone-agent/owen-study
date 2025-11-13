"""
iOS 真機測試配置

此模組提供 iOS 真機測試的專用配置和工具函式。
支援多設備管理、自動設備檢測和測試環境驗證。

Author: Robot Framework Team
Date: 2025-06-27
"""

import os
import subprocess
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path


class iOSDeviceManager:
    """iOS 設備管理器"""
    
    def __init__(self):
        """初始化 iOS 設備管理器"""
        self.connected_devices: List[Dict[str, str]] = []
        self.default_timeout = 30
    
    def check_libimobiledevice_tools(self) -> bool:
        """
        檢查 libimobiledevice 工具是否可用
        
        Returns:
            bool: 工具是否可用
        """
        required_tools = ['idevice_id', 'ideviceinfo', 'idevicename']
        
        for tool in required_tools:
            try:
                result = subprocess.run([tool, '--help'], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode != 0:
                    print(f"警告: {tool} 工具不可用")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"錯誤: {tool} 工具未找到")
                return False
        
        return True
    
    def get_connected_devices(self) -> List[str]:
        """
        獲取已連接的 iOS 設備 UDID 列表
        
        Returns:
            List[str]: 設備 UDID 列表
        """
        try:
            result = subprocess.run(['idevice_id', '-l'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                devices = [line.strip() for line in result.stdout.strip().split('\n') 
                          if line.strip()]
                return devices
            else:
                print(f"獲取設備列表失敗: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("獲取設備列表超時")
            return []
        except Exception as e:
            print(f"獲取設備列表時發生錯誤: {e}")
            return []
    
    def get_device_info(self, udid: str) -> Dict[str, str]:
        """
        獲取指定設備的詳細資訊
        
        Args:
            udid (str): 設備 UDID
            
        Returns:
            Dict[str, str]: 設備資訊字典
        """
        device_info = {
            'udid': udid,
            'deviceName': 'Unknown',
            'productVersion': 'Unknown',
            'productType': 'Unknown',
            'serialNumber': 'Unknown'
        }
        
        info_keys = {
            'DeviceName': 'deviceName',
            'ProductVersion': 'productVersion', 
            'ProductType': 'productType',
            'SerialNumber': 'serialNumber'
        }
        
        for key, attr in info_keys.items():
            try:
                result = subprocess.run(['ideviceinfo', '-u', udid, '-k', key],
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
                
                if result.returncode == 0:
                    device_info[attr] = result.stdout.strip()
                    
            except subprocess.TimeoutExpired:
                print(f"獲取設備 {udid} 的 {key} 資訊超時")
            except Exception as e:
                print(f"獲取設備 {udid} 的 {key} 資訊時發生錯誤: {e}")
        
        return device_info
    
    def refresh_device_list(self) -> List[Dict[str, str]]:
        """
        刷新並獲取所有已連接設備的詳細資訊
        
        Returns:
            List[Dict[str, str]]: 設備資訊列表
        """
        self.connected_devices = []
        device_udids = self.get_connected_devices()
        
        for udid in device_udids:
            device_info = self.get_device_info(udid)
            self.connected_devices.append(device_info)
        
        return self.connected_devices
    
    def get_primary_device(self) -> Optional[Dict[str, str]]:
        """
        獲取主要測試設備（第一個連接的設備）
        
        Returns:
            Optional[Dict[str, str]]: 主要設備資訊，如果沒有設備則為 None
        """
        devices = self.refresh_device_list()
        return devices[0] if devices else None
    
    def wait_for_device(self, timeout: int = 60) -> bool:
        """
        等待 iOS 設備連接
        
        Args:
            timeout (int): 等待超時時間（秒）
            
        Returns:
            bool: 是否有設備連接
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            devices = self.get_connected_devices()
            if devices:
                print(f"檢測到 iOS 設備: {devices[0]}")
                return True
            
            print("等待 iOS 設備連接...")
            time.sleep(2)
        
        print(f"等待 {timeout} 秒後仍未檢測到 iOS 設備")
        return False
    
    def validate_device_for_testing(self, udid: str) -> bool:
        """
        驗證設備是否適合進行測試
        
        Args:
            udid (str): 設備 UDID
            
        Returns:
            bool: 設備是否可用於測試
        """
        device_info = self.get_device_info(udid)
        
        # 檢查設備是否可訪問
        if device_info['deviceName'] == 'Unknown':
            print(f"設備 {udid} 不可訪問，可能已鎖定或未信任此電腦")
            return False
        
        # 檢查 iOS 版本（建議 iOS 13.0+）
        try:
            ios_version = device_info['productVersion']
            major_version = int(ios_version.split('.')[0])
            
            if major_version < 13:
                print(f"警告: iOS 版本 {ios_version} 可能不完全支援，建議使用 iOS 13.0+")
                return False
                
        except (ValueError, IndexError):
            print(f"無法解析 iOS 版本: {device_info['productVersion']}")
        
        return True


class iOSTestConfig:
    """iOS 測試配置管理器"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        初始化 iOS 測試配置
        
        Args:
            project_root (str, optional): 專案根目錄路徑
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent.parent
        
        self.device_manager = iOSDeviceManager()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        載入 iOS 測試配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            # Appium 伺服器配置
            'appium': {
                'host': os.getenv('APPIUM_HOST', 'localhost'),
                'port': int(os.getenv('APPIUM_PORT', '4723')),
                'timeout': int(os.getenv('APPIUM_TIMEOUT', '30'))
            },
            
            # iOS 基本配置
            'ios': {
                'platformName': 'iOS',
                'automationName': 'XCUITest',
                'deviceName': os.getenv('IOS_DEVICE_NAME', 'iPhone'),
                'platformVersion': os.getenv('IOS_PLATFORM_VERSION', '17.0'),
                'udid': os.getenv('IOS_UDID', ''),
                'bundleId': os.getenv('IOS_BUNDLE_ID', 'com.apple.calculator'),
                'xcodeOrgId': os.getenv('IOS_XCODE_ORG_ID', ''),
                'xcodeSigningId': os.getenv('IOS_XCODE_SIGNING_ID', ''),
            },
            
            # WebDriverAgent 配置
            'wda': {
                'newCommandTimeout': 60,
                'wdaStartupRetries': 3,
                'wdaStartupRetryInterval': 10000,
                'useNewWDA': False,
                'wdaLaunchTimeout': 120000,
                'wdaConnectionTimeout': 240000,
            },
            
            # 測試行為配置
            'behavior': {
                'noReset': True,
                'fullReset': False,
                'autoAcceptAlerts': True,
                'autoDismissAlerts': False,
                'nativeInstrumentsLib': True,
                'shouldUseTestManagerForVisibilityDetection': False,
            },
            
            # 效能配置
            'performance': {
                'skipLogCapture': False,
                'reducedMotion': True,
                'simpleIsVisibleCheck': True,
                'useJSONSource': True,
                'shouldUseCompactResponses': False,
            }
        }
    
    def get_capabilities_for_device(self, udid: str = None) -> Dict[str, Any]:
        """
        獲取指定設備的 Appium capabilities
        
        Args:
            udid (str, optional): 設備 UDID，如果未提供則使用主要設備
            
        Returns:
            Dict[str, Any]: Appium capabilities
        """
        if not udid:
            device = self.device_manager.get_primary_device()
            if not device:
                raise ValueError("未檢測到 iOS 設備，請確認設備已連接")
            udid = device['udid']
        
        # 獲取設備資訊
        device_info = self.device_manager.get_device_info(udid)
        
        # 構建 capabilities
        capabilities = {}
        capabilities.update(self.config['ios'])
        capabilities.update(self.config['wda'])
        capabilities.update(self.config['behavior'])
        capabilities.update(self.config['performance'])
        
        # 更新設備特定資訊
        capabilities.update({
            'udid': udid,
            'deviceName': device_info['deviceName'],
            'platformVersion': device_info['productVersion'],
        })
        
        return capabilities
    
    def get_appium_server_url(self) -> str:
        """
        獲取 Appium 伺服器 URL
        
        Returns:
            str: Appium 伺服器完整 URL
        """
        host = self.config['appium']['host']
        port = self.config['appium']['port']
        return f"http://{host}:{port}/wd/hub"
    
    def validate_environment(self) -> bool:
        """
        驗證 iOS 測試環境
        
        Returns:
            bool: 環境是否有效
        """
        print("驗證 iOS 測試環境...")
        
        # 檢查 libimobiledevice 工具
        if not self.device_manager.check_libimobiledevice_tools():
            print("❌ libimobiledevice 工具檢查失敗")
            return False
        print("✅ libimobiledevice 工具檢查通過")
        
        # 檢查設備連接
        devices = self.device_manager.refresh_device_list()
        if not devices:
            print("❌ 未檢測到 iOS 設備")
            return False
        print(f"✅ 檢測到 {len(devices)} 個 iOS 設備")
        
        # 驗證主要設備
        primary_device = devices[0]
        if not self.device_manager.validate_device_for_testing(primary_device['udid']):
            print("❌ 主要測試設備驗證失敗")
            return False
        print(f"✅ 主要測試設備驗證通過: {primary_device['deviceName']}")
        
        return True
    
    def generate_test_report(self) -> Dict[str, Any]:
        """
        生成測試環境報告
        
        Returns:
            Dict[str, Any]: 測試環境報告
        """
        devices = self.device_manager.refresh_device_list()
        
        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'environment': {
                'libimobiledevice_available': self.device_manager.check_libimobiledevice_tools(),
                'appium_server_url': self.get_appium_server_url(),
            },
            'devices': devices,
            'config': self.config
        }


# 全域配置實例
ios_config = iOSTestConfig()
device_manager = iOSDeviceManager()


# 便利函式
def get_connected_ios_devices() -> List[Dict[str, str]]:
    """獲取已連接的 iOS 設備列表"""
    return device_manager.refresh_device_list()


def get_ios_capabilities(udid: str = None) -> Dict[str, Any]:
    """獲取 iOS 測試 capabilities"""
    return ios_config.get_capabilities_for_device(udid)


def validate_ios_environment() -> bool:
    """驗證 iOS 測試環境"""
    return ios_config.validate_environment()


def wait_for_ios_device(timeout: int = 60) -> bool:
    """等待 iOS 設備連接"""
    return device_manager.wait_for_device(timeout)
