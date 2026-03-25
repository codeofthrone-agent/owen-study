"""測試 DeviceControlKeywords 平台分發邏輯。

驗證項目：
1. platform="android" → 建立 AndroidDeviceControl 實例
2. platform="ios" → 建立 IOSDeviceControl 實例
3. 無效平台 → ValueError
4. 未初始化就呼叫 → RuntimeError
"""
import pytest
from unittest.mock import MagicMock, patch


class TestDeviceControlDispatch:
    """測試 DeviceControlKeywords 平台分發"""

    def _create_keywords_with_mock_driver(self):
        """建立帶有 mock driver 的 DeviceControlKeywords 實例"""
        from libraries.mobile_testing.DeviceControlKeywords import DeviceControlKeywords

        kw = DeviceControlKeywords()
        # mock _get_driver 以避免依賴 Robot Framework BuiltIn
        kw._get_driver = MagicMock(return_value=MagicMock())
        return kw

    def test_android_dispatch(self):
        """platform='android' 應建立 AndroidDeviceControl 實例"""
        from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_device_control('android')
        assert isinstance(kw._impl, AndroidDeviceControl)

    def test_ios_dispatch(self):
        """platform='ios' 應建立 IOSDeviceControl 實例"""
        from libraries.mobile_testing.ios.IOSDeviceControl import IOSDeviceControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_device_control('ios')
        assert isinstance(kw._impl, IOSDeviceControl)

    def test_android_case_insensitive(self):
        """platform 參數應不區分大小寫"""
        from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_device_control('Android')
        assert isinstance(kw._impl, AndroidDeviceControl)

        kw.init_device_control('ANDROID')
        assert isinstance(kw._impl, AndroidDeviceControl)

    def test_invalid_platform_raises_value_error(self):
        """傳入不支援的平台應拋出 ValueError"""
        kw = self._create_keywords_with_mock_driver()
        with pytest.raises(ValueError, match="不支援的平台"):
            kw.init_device_control('windows')

    def test_uninitialized_raises_runtime_error(self):
        """未初始化就呼叫控制方法應拋出 RuntimeError"""
        from libraries.mobile_testing.DeviceControlKeywords import DeviceControlKeywords

        kw = DeviceControlKeywords()
        with pytest.raises(RuntimeError, match="尚未初始化"):
            kw.disable_wifi()

    def test_uninitialized_enable_bluetooth_raises(self):
        """未初始化就呼叫 enable_bluetooth 應拋出 RuntimeError"""
        from libraries.mobile_testing.DeviceControlKeywords import DeviceControlKeywords

        kw = DeviceControlKeywords()
        with pytest.raises(RuntimeError, match="尚未初始化"):
            kw.enable_bluetooth()

    def test_dispatch_delegates_to_impl(self):
        """初始化後呼叫關鍵字應正確委派至底層實作"""
        kw = self._create_keywords_with_mock_driver()
        kw.init_device_control('android')
        kw._impl.disable_wifi = MagicMock()
        kw.disable_wifi()
        kw._impl.disable_wifi.assert_called_once()

    def test_reinitialize_replaces_impl(self):
        """重新初始化應替換底層實作"""
        from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl
        from libraries.mobile_testing.ios.IOSDeviceControl import IOSDeviceControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_device_control('android')
        assert isinstance(kw._impl, AndroidDeviceControl)

        kw.init_device_control('ios')
        assert isinstance(kw._impl, IOSDeviceControl)
