"""測試 DeviceControlBase 抽象基類。

驗證項目：
1. 抽象基類不可直接實例化
2. 子類必須實作所有 29 個抽象方法（16 控制 + 6 查詢 + 7 斷言）
3. 部分實作的子類不可實例化
"""
import pytest


class TestDeviceControlBaseAbstract:
    """測試抽象基類不可實例化"""

    def test_cannot_instantiate_directly(self):
        """直接實例化 DeviceControlBase 應拋出 TypeError"""
        from libraries.mobile_testing.base.device_control_base import DeviceControlBase

        with pytest.raises(TypeError):
            DeviceControlBase(driver=None)

    def test_has_all_abstract_methods(self):
        """DeviceControlBase 應定義 29 個抽象方法（16 控制 + 6 查詢 + 7 斷言）"""
        from libraries.mobile_testing.base.device_control_base import DeviceControlBase

        expected_methods = {
            # 藍牙控制
            'enable_bluetooth', 'disable_bluetooth',
            # 網路控制
            'enable_wifi', 'disable_wifi',
            'enable_mobile_data', 'disable_mobile_data',
            'enable_airplane_mode', 'disable_airplane_mode',
            # 音量控制
            'volume_up', 'volume_down', 'volume_mute', 'set_media_volume',
            # App 生命週期
            'background_app', 'activate_app',
            'dismiss_from_recents', 'force_stop_app',
            # 狀態查詢
            'get_bluetooth_state', 'get_wifi_state',
            'get_airplane_mode_state', 'get_media_volume',
            'get_foreground_app',
            # 狀態斷言
            'assert_bluetooth_on', 'assert_bluetooth_off',
            'assert_wifi_on', 'assert_wifi_off',
            'assert_airplane_mode_on', 'assert_airplane_mode_off',
            'assert_media_volume',
        }
        actual_abstract = DeviceControlBase.__abstractmethods__
        assert expected_methods == actual_abstract, (
            f"缺少或多出抽象方法。預期: {expected_methods}，實際: {actual_abstract}"
        )

    def test_partial_implementation_cannot_instantiate(self):
        """只實作部分抽象方法的子類不可實例化"""
        from libraries.mobile_testing.base.device_control_base import DeviceControlBase

        class PartialImpl(DeviceControlBase):
            def enable_bluetooth(self): pass
            def disable_bluetooth(self): pass

        with pytest.raises(TypeError):
            PartialImpl(driver=None)

    def test_full_implementation_can_instantiate(self):
        """實作所有抽象方法的子類可以實例化"""
        from libraries.mobile_testing.base.device_control_base import DeviceControlBase

        class FullImpl(DeviceControlBase):
            def enable_bluetooth(self): pass
            def disable_bluetooth(self): pass
            def enable_wifi(self): pass
            def disable_wifi(self): pass
            def enable_mobile_data(self): pass
            def disable_mobile_data(self): pass
            def enable_airplane_mode(self): pass
            def disable_airplane_mode(self): pass
            def volume_up(self): pass
            def volume_down(self): pass
            def volume_mute(self): pass
            def set_media_volume(self, level): pass
            def background_app(self, seconds=-1): pass
            def activate_app(self, package_or_bundle): pass
            def dismiss_from_recents(self): pass
            def force_stop_app(self, package_or_bundle): pass
            # 狀態查詢
            def get_bluetooth_state(self): return 'off'
            def get_wifi_state(self): return 'off'
            def get_airplane_mode_state(self): return 'off'
            def get_media_volume(self): return 0
            def get_foreground_app(self): return ''
            # 狀態斷言
            def assert_bluetooth_on(self): pass
            def assert_bluetooth_off(self): pass
            def assert_wifi_on(self): pass
            def assert_wifi_off(self): pass
            def assert_airplane_mode_on(self): pass
            def assert_airplane_mode_off(self): pass
            def assert_media_volume(self, expected): pass

        instance = FullImpl(driver=None)
        assert instance.driver is None


class TestGestureControlBaseAbstract:
    """測試手勢控制抽象基類不可實例化"""

    def test_cannot_instantiate_directly(self):
        """直接實例化 GestureControlBase 應拋出 TypeError"""
        from libraries.mobile_testing.base.gesture_control_base import GestureControlBase

        with pytest.raises(TypeError):
            GestureControlBase(driver=None)

    def test_has_all_abstract_methods(self):
        """GestureControlBase 應定義 7 個抽象方法"""
        from libraries.mobile_testing.base.gesture_control_base import GestureControlBase

        expected_methods = {
            'long_press_element', 'long_press_coordinates',
            'swipe_direction', 'swipe_in_area',
            'tap_coordinates',
            'double_tap_element',
            'drag_element',
        }
        actual_abstract = GestureControlBase.__abstractmethods__
        assert expected_methods == actual_abstract, (
            f"缺少或多出抽象方法。預期: {expected_methods}，實際: {actual_abstract}"
        )

    def test_full_implementation_can_instantiate(self):
        """實作所有抽象方法的子類可以實例化"""
        from libraries.mobile_testing.base.gesture_control_base import GestureControlBase

        class FullImpl(GestureControlBase):
            def long_press_element(self, locator, duration=1000): pass
            def long_press_coordinates(self, x, y, duration=1000): pass
            def swipe_direction(self, direction, percent=75): pass
            def swipe_in_area(self, left, top, width, height, direction, percent=75): pass
            def tap_coordinates(self, x, y): pass
            def double_tap_element(self, locator): pass
            def drag_element(self, locator, end_x, end_y, speed=1000): pass

        instance = FullImpl(driver=None)
        assert instance.driver is None
