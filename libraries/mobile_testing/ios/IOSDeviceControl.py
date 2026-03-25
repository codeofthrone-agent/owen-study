"""iOS 裝置控制 stub 實作。

所有方法統一拋出 NotImplementedError，附帶明確的中文錯誤訊息。
後續補齊 iOS 實作時，逐一替換 stub 方法即可。
"""
from libraries.mobile_testing.base.device_control_base import DeviceControlBase


class IOSDeviceControl(DeviceControlBase):
    """iOS 裝置控制 - stub 實作（尚未實作）"""

    def enable_bluetooth(self):
        raise NotImplementedError("iOS 藍牙控制尚未實作")

    def disable_bluetooth(self):
        raise NotImplementedError("iOS 藍牙控制尚未實作")

    def enable_wifi(self):
        raise NotImplementedError("iOS WiFi 控制尚未實作")

    def disable_wifi(self):
        raise NotImplementedError("iOS WiFi 控制尚未實作")

    def enable_mobile_data(self):
        raise NotImplementedError("iOS 行動數據控制尚未實作")

    def disable_mobile_data(self):
        raise NotImplementedError("iOS 行動數據控制尚未實作")

    def enable_airplane_mode(self):
        raise NotImplementedError("iOS 飛航模式控制尚未實作")

    def disable_airplane_mode(self):
        raise NotImplementedError("iOS 飛航模式控制尚未實作")

    def volume_up(self):
        raise NotImplementedError("iOS 音量控制尚未實作")

    def volume_down(self):
        raise NotImplementedError("iOS 音量控制尚未實作")

    def volume_mute(self):
        raise NotImplementedError("iOS 靜音控制尚未實作")

    def set_media_volume(self, level: int):
        raise NotImplementedError("iOS 媒體音量設定尚未實作")

    def background_app(self, seconds: int = -1):
        raise NotImplementedError("iOS 背景應用控制尚未實作")

    def activate_app(self, package_or_bundle: str):
        raise NotImplementedError("iOS 啟動應用控制尚未實作")

    def dismiss_from_recents(self):
        raise NotImplementedError("iOS 最近應用清除尚未實作")

    def force_stop_app(self, package_or_bundle: str):
        raise NotImplementedError("iOS 強制停止應用尚未實作")

    # === 狀態查詢 ===

    def get_bluetooth_state(self) -> str:
        raise NotImplementedError("iOS 藍牙狀態查詢尚未實作")

    def get_wifi_state(self) -> str:
        raise NotImplementedError("iOS WiFi 狀態查詢尚未實作")

    def get_airplane_mode_state(self) -> str:
        raise NotImplementedError("iOS 飛航模式狀態查詢尚未實作")

    def get_media_volume(self) -> int:
        raise NotImplementedError("iOS 媒體音量查詢尚未實作")

    def get_foreground_app(self) -> str:
        raise NotImplementedError("iOS 前景應用查詢尚未實作")

    # === 狀態斷言 ===

    def assert_bluetooth_on(self):
        raise NotImplementedError("iOS 藍牙狀態斷言尚未實作")

    def assert_bluetooth_off(self):
        raise NotImplementedError("iOS 藍牙狀態斷言尚未實作")

    def assert_wifi_on(self):
        raise NotImplementedError("iOS WiFi 狀態斷言尚未實作")

    def assert_wifi_off(self):
        raise NotImplementedError("iOS WiFi 狀態斷言尚未實作")

    def assert_airplane_mode_on(self):
        raise NotImplementedError("iOS 飛航模式斷言尚未實作")

    def assert_airplane_mode_off(self):
        raise NotImplementedError("iOS 飛航模式斷言尚未實作")

    def assert_media_volume(self, expected: int):
        raise NotImplementedError("iOS 媒體音量斷言尚未實作")
