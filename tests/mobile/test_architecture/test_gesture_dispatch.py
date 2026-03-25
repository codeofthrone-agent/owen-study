"""測試 GestureControlKeywords 平台分發邏輯。

驗證項目：
1. platform="android" → 建立 AndroidGestureControl 實例
2. platform="ios" → 建立 IOSGestureControl 實例
3. 無效平台 → ValueError
4. 未初始化就呼叫 → RuntimeError
"""
import pytest
from unittest.mock import MagicMock


class TestGestureControlDispatch:
    """測試 GestureControlKeywords 平台分發"""

    def _create_keywords_with_mock_driver(self):
        """建立帶有 mock driver 的 GestureControlKeywords 實例"""
        from libraries.mobile_testing.GestureControlKeywords import GestureControlKeywords

        kw = GestureControlKeywords()
        kw._get_driver = MagicMock(return_value=MagicMock())
        return kw

    def test_android_dispatch(self):
        """platform='android' 應建立 AndroidGestureControl 實例"""
        from libraries.mobile_testing.android.AndroidGestureControl import AndroidGestureControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_gesture_control('android')
        assert isinstance(kw._impl, AndroidGestureControl)

    def test_ios_dispatch(self):
        """platform='ios' 應建立 IOSGestureControl 實例"""
        from libraries.mobile_testing.ios.IOSGestureControl import IOSGestureControl

        kw = self._create_keywords_with_mock_driver()
        kw.init_gesture_control('ios')
        assert isinstance(kw._impl, IOSGestureControl)

    def test_invalid_platform_raises_value_error(self):
        """傳入不支援的平台應拋出 ValueError"""
        kw = self._create_keywords_with_mock_driver()
        with pytest.raises(ValueError, match="不支援的平台"):
            kw.init_gesture_control('windows')

    def test_uninitialized_raises_runtime_error(self):
        """未初始化就呼叫手勢方法應拋出 RuntimeError"""
        from libraries.mobile_testing.GestureControlKeywords import GestureControlKeywords

        kw = GestureControlKeywords()
        with pytest.raises(RuntimeError, match="尚未初始化"):
            kw.swipe_direction('up')

    def test_uninitialized_long_press_raises(self):
        """未初始化就呼叫 long_press_element 應拋出 RuntimeError"""
        from libraries.mobile_testing.GestureControlKeywords import GestureControlKeywords

        kw = GestureControlKeywords()
        with pytest.raises(RuntimeError, match="尚未初始化"):
            kw.long_press_element('id=some_element')

    def test_dispatch_delegates_to_impl(self):
        """初始化後呼叫關鍵字應正確委派至底層實作"""
        kw = self._create_keywords_with_mock_driver()
        kw.init_gesture_control('android')
        kw._impl.swipe_direction = MagicMock()
        kw.swipe_direction('up')
        kw._impl.swipe_direction.assert_called_once_with('up', 75)
