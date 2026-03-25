"""測試 iOS stub 實作。

驗證項目：
1. 所有 IOSDeviceControl 方法拋出 NotImplementedError
2. 所有 IOSGestureControl 方法拋出 NotImplementedError
3. 錯誤訊息包含「iOS」+「功能名稱」+「尚未實作」
"""
import pytest
from unittest.mock import MagicMock


class TestIOSDeviceControlStub:
    """測試 IOSDeviceControl 所有方法拋出 NotImplementedError"""

    @pytest.fixture
    def ios_device(self):
        from libraries.mobile_testing.ios.IOSDeviceControl import IOSDeviceControl
        return IOSDeviceControl(driver=MagicMock())

    def test_enable_bluetooth(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*藍牙.*尚未實作"):
            ios_device.enable_bluetooth()

    def test_disable_bluetooth(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*藍牙.*尚未實作"):
            ios_device.disable_bluetooth()

    def test_enable_wifi(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*WiFi.*尚未實作"):
            ios_device.enable_wifi()

    def test_disable_wifi(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*WiFi.*尚未實作"):
            ios_device.disable_wifi()

    def test_enable_mobile_data(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*行動數據.*尚未實作"):
            ios_device.enable_mobile_data()

    def test_disable_mobile_data(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*行動數據.*尚未實作"):
            ios_device.disable_mobile_data()

    def test_enable_airplane_mode(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*飛航模式.*尚未實作"):
            ios_device.enable_airplane_mode()

    def test_disable_airplane_mode(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*飛航模式.*尚未實作"):
            ios_device.disable_airplane_mode()

    def test_volume_up(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*音量.*尚未實作"):
            ios_device.volume_up()

    def test_volume_down(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*音量.*尚未實作"):
            ios_device.volume_down()

    def test_volume_mute(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*靜音.*尚未實作"):
            ios_device.volume_mute()

    def test_set_media_volume(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*媒體音量.*尚未實作"):
            ios_device.set_media_volume(10)

    def test_background_app(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*背景.*尚未實作"):
            ios_device.background_app()

    def test_activate_app(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*啟動.*尚未實作"):
            ios_device.activate_app('com.example.app')

    def test_dismiss_from_recents(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*最近應用.*尚未實作"):
            ios_device.dismiss_from_recents()

    def test_force_stop_app(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*強制停止.*尚未實作"):
            ios_device.force_stop_app('com.example.app')

    # === 狀態查詢 stub ===

    def test_get_bluetooth_state(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*藍牙.*查詢.*尚未實作"):
            ios_device.get_bluetooth_state()

    def test_get_wifi_state(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*WiFi.*查詢.*尚未實作"):
            ios_device.get_wifi_state()

    def test_get_airplane_mode_state(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*飛航模式.*查詢.*尚未實作"):
            ios_device.get_airplane_mode_state()

    def test_get_media_volume(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*媒體音量.*查詢.*尚未實作"):
            ios_device.get_media_volume()

    def test_get_foreground_app(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*前景應用.*查詢.*尚未實作"):
            ios_device.get_foreground_app()

    # === 狀態斷言 stub ===

    def test_assert_bluetooth_on(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*藍牙.*斷言.*尚未實作"):
            ios_device.assert_bluetooth_on()

    def test_assert_bluetooth_off(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*藍牙.*斷言.*尚未實作"):
            ios_device.assert_bluetooth_off()

    def test_assert_wifi_on(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*WiFi.*斷言.*尚未實作"):
            ios_device.assert_wifi_on()

    def test_assert_wifi_off(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*WiFi.*斷言.*尚未實作"):
            ios_device.assert_wifi_off()

    def test_assert_airplane_mode_on(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*飛航模式.*斷言.*尚未實作"):
            ios_device.assert_airplane_mode_on()

    def test_assert_airplane_mode_off(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*飛航模式.*斷言.*尚未實作"):
            ios_device.assert_airplane_mode_off()

    def test_assert_media_volume(self, ios_device):
        with pytest.raises(NotImplementedError, match=r"iOS.*媒體音量.*斷言.*尚未實作"):
            ios_device.assert_media_volume(7)


class TestIOSGestureControlStub:
    """測試 IOSGestureControl 所有方法拋出 NotImplementedError"""

    @pytest.fixture
    def ios_gesture(self):
        from libraries.mobile_testing.ios.IOSGestureControl import IOSGestureControl
        return IOSGestureControl(driver=MagicMock())

    def test_long_press_element(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*長按.*尚未實作"):
            ios_gesture.long_press_element('id=element')

    def test_long_press_coordinates(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*長按座標.*尚未實作"):
            ios_gesture.long_press_coordinates(100, 200)

    def test_swipe_direction(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*滑動.*尚未實作"):
            ios_gesture.swipe_direction('up')

    def test_swipe_in_area(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*區域滑動.*尚未實作"):
            ios_gesture.swipe_in_area(0, 0, 100, 100, 'up')

    def test_tap_coordinates(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*座標點擊.*尚未實作"):
            ios_gesture.tap_coordinates(100, 200)

    def test_double_tap_element(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*雙擊.*尚未實作"):
            ios_gesture.double_tap_element('id=element')

    def test_drag_element(self, ios_gesture):
        with pytest.raises(NotImplementedError, match=r"iOS.*拖曳.*尚未實作"):
            ios_gesture.drag_element('id=element', 200, 300)
