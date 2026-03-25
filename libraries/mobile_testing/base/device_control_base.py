"""裝置系統控制抽象基類。

定義跨平台統一的裝置控制介面，包含藍牙、WiFi、行動數據、
飛航模式、音量控制、App 生命週期管理的控制方法（16 個）、
狀態查詢方法（6 個）與狀態斷言方法（7 個），共 29 個抽象方法。
Android 和 iOS 實作類別 MUST 繼承此基類並實作所有抽象方法。
"""
from abc import ABC, abstractmethod


class DeviceControlBase(ABC):
    """裝置系統控制抽象基類 - 定義跨平台統一介面"""

    def __init__(self, driver):
        """初始化裝置控制基類。

        Args:
            driver: Appium WebDriver 實例
        """
        self.driver = driver

    # === 藍牙控制 ===

    @abstractmethod
    def enable_bluetooth(self):
        """開啟藍牙"""
        ...

    @abstractmethod
    def disable_bluetooth(self):
        """關閉藍牙"""
        ...

    # === 網路控制 ===

    @abstractmethod
    def enable_wifi(self):
        """開啟 WiFi"""
        ...

    @abstractmethod
    def disable_wifi(self):
        """關閉 WiFi"""
        ...

    @abstractmethod
    def enable_mobile_data(self):
        """開啟行動數據"""
        ...

    @abstractmethod
    def disable_mobile_data(self):
        """關閉行動數據"""
        ...

    @abstractmethod
    def enable_airplane_mode(self):
        """開啟飛航模式"""
        ...

    @abstractmethod
    def disable_airplane_mode(self):
        """關閉飛航模式"""
        ...

    # === 音量控制 ===

    @abstractmethod
    def volume_up(self):
        """調高音量一級"""
        ...

    @abstractmethod
    def volume_down(self):
        """調低音量一級"""
        ...

    @abstractmethod
    def volume_mute(self):
        """靜音"""
        ...

    @abstractmethod
    def set_media_volume(self, level: int):
        """設定媒體音量到指定值。

        Args:
            level: 音量等級（0-15）
        """
        ...

    # === App 生命週期 ===

    @abstractmethod
    def background_app(self, seconds: int = -1):
        """將應用程式置於背景。

        Args:
            seconds: 等待秒數後恢復。-1 表示無限期置於背景。
        """
        ...

    @abstractmethod
    def activate_app(self, package_or_bundle: str):
        """啟動或恢復應用程式至前景。

        Args:
            package_or_bundle: Android package name 或 iOS bundle ID
        """
        ...

    @abstractmethod
    def dismiss_from_recents(self):
        """從最近應用列表中清除 App"""
        ...

    @abstractmethod
    def force_stop_app(self, package_or_bundle: str):
        """強制停止應用程式。

        Args:
            package_or_bundle: Android package name 或 iOS bundle ID
        """
        ...

    # === 狀態查詢 ===

    @abstractmethod
    def get_bluetooth_state(self) -> str:
        """查詢藍牙開關狀態。

        Returns:
            'on' 表示已開啟，'off' 表示已關閉
        """
        ...

    @abstractmethod
    def get_wifi_state(self) -> str:
        """查詢 WiFi 開關狀態。

        Returns:
            'on' 表示已開啟，'off' 表示已關閉
        """
        ...

    @abstractmethod
    def get_airplane_mode_state(self) -> str:
        """查詢飛航模式開關狀態。

        Returns:
            'on' 表示已開啟，'off' 表示已關閉
        """
        ...

    @abstractmethod
    def get_media_volume(self) -> int:
        """查詢目前媒體音量等級。

        Returns:
            目前媒體音量等級（0-15）
        """
        ...

    @abstractmethod
    def get_foreground_app(self) -> str:
        """查詢目前前景應用程式的 package name。

        Returns:
            前景應用程式的 package name
        """
        ...

    # === 狀態斷言 ===

    @abstractmethod
    def assert_bluetooth_on(self):
        """斷言藍牙目前為開啟狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_bluetooth_off(self):
        """斷言藍牙目前為關閉狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_wifi_on(self):
        """斷言 WiFi 目前為開啟狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_wifi_off(self):
        """斷言 WiFi 目前為關閉狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_airplane_mode_on(self):
        """斷言飛航模式目前為開啟狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_airplane_mode_off(self):
        """斷言飛航模式目前為關閉狀態。失敗時拋出 AssertionError。"""
        ...

    @abstractmethod
    def assert_media_volume(self, expected: int):
        """斷言媒體音量等級符合預期值。失敗時拋出 AssertionError。

        Args:
            expected: 預期媒體音量等級（0-15）
        """
        ...
