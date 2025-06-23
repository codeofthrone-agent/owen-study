"""
Appium 配置管理模組

此模組管理 Appium 測試的設備配置、連接設定和測試環境設定。
支援 iOS 和 Android 兩個平台的測試配置。

Author: Robot Framework Team
Date: 2025-06-23
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class AppiumConfig:
    """Appium 配置管理類別"""
    
    def __init__(self):
        """初始化 Appium 配置"""
        self.project_root = Path(__file__).parent.parent.parent
        self.appium_server = self._get_appium_server_config()
        self.ios_config = self._get_ios_config()
        self.android_config = self._get_android_config()
    
    def _get_appium_server_config(self) -> Dict[str, Any]:
        """
        獲取 Appium 伺服器配置
        
        Returns:
            Dict[str, Any]: Appium 伺服器配置字典
        """
        return {
            'host': os.getenv('APPIUM_HOST', 'localhost'),
            'port': int(os.getenv('APPIUM_PORT', '4723')),
            'timeout': int(os.getenv('APPIUM_TIMEOUT', '30')),
            'command_timeout': int(os.getenv('APPIUM_COMMAND_TIMEOUT', '60')),
        }
    
    def _get_ios_config(self) -> Dict[str, Any]:
        """
        獲取 iOS 測試配置
        
        Returns:
            Dict[str, Any]: iOS 配置字典
        """
        return {
            'platformName': 'iOS',
            'automationName': 'XCUITest',
            'deviceName': os.getenv('IOS_DEVICE_NAME', 'iPhone 14'),
            'platformVersion': os.getenv('IOS_PLATFORM_VERSION', '16.0'),
            'bundleId': os.getenv('IOS_BUNDLE_ID', ''),
            'app': os.getenv('IOS_APP_PATH', ''),
            'udid': os.getenv('IOS_UDID', ''),
            'xcodeOrgId': os.getenv('IOS_XCODE_ORG_ID', ''),
            'xcodeSigningId': os.getenv('IOS_XCODE_SIGNING_ID', ''),
            'newCommandTimeout': 60,
            'wdaStartupRetries': 3,
            'wdaStartupRetryInterval': 10000,
        }
    
    def _get_android_config(self) -> Dict[str, Any]:
        """
        獲取 Android 測試配置
        
        Returns:
            Dict[str, Any]: Android 配置字典
        """
        return {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': os.getenv('ANDROID_DEVICE_NAME', 'Android Emulator'),
            'platformVersion': os.getenv('ANDROID_PLATFORM_VERSION', '11'),
            'appPackage': os.getenv('ANDROID_APP_PACKAGE', ''),
            'appActivity': os.getenv('ANDROID_APP_ACTIVITY', ''),
            'app': os.getenv('ANDROID_APP_PATH', ''),
            'udid': os.getenv('ANDROID_UDID', ''),
            'newCommandTimeout': 60,
            'autoGrantPermissions': True,
            'noReset': False,
            'fullReset': False,
        }
    
    def get_capability(self, platform: str, **kwargs) -> Dict[str, Any]:
        """
        獲取指定平台的 Appium 能力配置
        
        Args:
            platform (str): 平台名稱 ('ios' 或 'android')
            **kwargs: 額外的配置參數
        
        Returns:
            Dict[str, Any]: Appium 能力配置
        
        Raises:
            ValueError: 當平台不支援時
        """
        if platform.lower() == 'ios':
            capabilities = self.ios_config.copy()
        elif platform.lower() == 'android':
            capabilities = self.android_config.copy()
        else:
            raise ValueError(f"不支援的平台: {platform}")
        
        # 更新自定義參數
        capabilities.update(kwargs)
        
        return capabilities
    
    def get_server_url(self) -> str:
        """
        獲取 Appium 伺服器 URL
        
        Returns:
            str: Appium 伺服器完整 URL
        """
        return f"http://{self.appium_server['host']}:{self.appium_server['port']}/wd/hub"
    
    def validate_config(self, platform: str) -> bool:
        """
        驗證指定平台的配置是否完整
        
        Args:
            platform (str): 平台名稱
        
        Returns:
            bool: 配置是否有效
        """
        try:
            capabilities = self.get_capability(platform)
            
            if platform.lower() == 'ios':
                required_fields = ['bundleId'] if not capabilities.get('app') else []
            else:  # android
                required_fields = ['appPackage', 'appActivity'] if not capabilities.get('app') else []
            
            for field in required_fields:
                if not capabilities.get(field):
                    print(f"警告: {platform} 配置缺少必要欄位: {field}")
                    return False
            
            return True
        except Exception as e:
            print(f"配置驗證失敗: {e}")
            return False


# 全域配置實例
appium_config = AppiumConfig()
