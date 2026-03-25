"""
Appium 配置管理模組

此模組管理 Appium 測試的設備配置、連接設定和測試環境設定。
支援 iOS 和 Android 兩個平台的測試配置。
新增支援 iOS 真機測試和自動設備檢測功能。

Author: Robot Framework Team
Date: 2025-06-27 (Updated for iOS real device support)
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# 匯入 iOS 專用配置（如果可用）
try:
    from .ios_config import device_manager, get_ios_capabilities
    IOS_REAL_DEVICE_SUPPORT = True
except ImportError:
    IOS_REAL_DEVICE_SUPPORT = False
    print("警告: iOS 真機支援不可用，將使用模擬器配置")

# 匯入 Android 專用配置
from .android_config import (
    android_device_manager,
    get_android_capabilities,
)


class AppiumConfig:
    """Appium 配置管理類別"""
    
    def __init__(self):
        """初始化 Appium 配置"""
        self.project_root = Path(__file__).parent.parent.parent
        self.appium_server = self._get_appium_server_config()
        
        # iOS 真機支援
        self.ios_real_device_support = IOS_REAL_DEVICE_SUPPORT
        if self.ios_real_device_support:
            print("✅ iOS 真機支援已啟用")

        self.ios_config = self._get_ios_config()
        self.android_config = self._get_android_config()
        android_device_manager.validate_relaxed_security()
    
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
        # 基礎配置（適用於模擬器）
        base_config = {
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
        
        # 如果支援真機，添加真機專用配置
        if self.ios_real_device_support:
            base_config.update({
                'useNewWDA': False,
                'wdaLaunchTimeout': 120000,
                'wdaConnectionTimeout': 240000,
                'autoAcceptAlerts': True,
                'autoDismissAlerts': False,
                'nativeInstrumentsLib': True,
                'shouldUseTestManagerForVisibilityDetection': False,
                'reducedMotion': True,
                'simpleIsVisibleCheck': True,
                'useJSONSource': True,
                'shouldUseCompactResponses': False,
            })
        
        return base_config
    
    def _get_android_config(self) -> Dict[str, Any]:
        """
        獲取 Android 測試配置

        Returns:
            Dict[str, Any]: Android 配置字典
        """
        return get_android_capabilities()
    
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
            # 優先使用 iOS 真機配置（如果可用且有設備連接）
            if self.ios_real_device_support and self._should_use_real_device(**kwargs):
                capabilities = self._get_ios_real_device_capabilities(**kwargs)
            else:
                capabilities = self.ios_config.copy()
        elif platform.lower() == 'android':
            capabilities = self.android_config.copy()
        else:
            raise ValueError(f"不支援的平台: {platform}")
        
        # 更新自定義參數
        capabilities.update(kwargs)
        
        return capabilities
    
    def _should_use_real_device(self, **kwargs) -> bool:
        """
        判斷是否應該使用 iOS 真機
        
        Args:
            **kwargs: 配置參數
            
        Returns:
            bool: 是否使用真機
        """
        # 如果明確指定了 UDID，使用真機
        if kwargs.get('udid') or os.getenv('IOS_UDID'):
            return True
        
        # 如果設定了使用真機的環境變數
        if os.getenv('USE_REAL_DEVICE', '').lower() in ['true', '1', 'yes']:
            return True
        
        # 檢查是否有連接的設備
        try:
            if device_manager:
                devices = device_manager.get_connected_devices()
                return len(devices) > 0
        except Exception:
            pass
        
        return False
    
    def _get_ios_real_device_capabilities(self, **kwargs) -> Dict[str, Any]:
        """
        獲取 iOS 真機測試配置
        
        Args:
            **kwargs: 額外配置參數
            
        Returns:
            Dict[str, Any]: iOS 真機配置
        """
        try:
            # 使用 iOS 專用配置管理器
            udid = kwargs.get('udid') or os.getenv('IOS_UDID')
            return get_ios_capabilities(udid)
        except Exception as e:
            print(f"獲取 iOS 真機配置失敗: {e}")
            print("回退到基本 iOS 配置")
            return self.ios_config.copy()
    
    def get_connected_ios_devices(self) -> list:
        """
        獲取已連接的 iOS 設備列表
        
        Returns:
            list: 設備資訊列表
        """
        if not self.ios_real_device_support:
            return []
        
        try:
            return device_manager.refresh_device_list()
        except Exception as e:
            print(f"獲取 iOS 設備列表失敗: {e}")
            return []
    
    def validate_ios_environment(self) -> bool:
        """
        驗證 iOS 測試環境
        
        Returns:
            bool: 環境是否有效
        """
        if not self.ios_real_device_support:
            print("警告: iOS 真機支援不可用")
            return True  # 模擬器環境仍可使用
        
        try:
            from .ios_config import validate_ios_environment
            return validate_ios_environment()
        except Exception as e:
            print(f"iOS 環境驗證失敗: {e}")
            return False
    
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
