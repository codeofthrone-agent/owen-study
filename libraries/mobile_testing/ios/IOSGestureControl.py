"""iOS 手勢控制 stub 實作。

所有方法統一拋出 NotImplementedError，附帶明確的中文錯誤訊息。
"""
from libraries.mobile_testing.base.gesture_control_base import GestureControlBase


class IOSGestureControl(GestureControlBase):
    """iOS 手勢控制 - stub 實作（尚未實作）"""

    def long_press_element(self, locator, duration: int = 1000):
        raise NotImplementedError("iOS 長按元素尚未實作")

    def long_press_coordinates(self, x: int, y: int, duration: int = 1000):
        raise NotImplementedError("iOS 長按座標尚未實作")

    def swipe_direction(self, direction: str, percent: int = 75):
        raise NotImplementedError("iOS 滑動尚未實作")

    def swipe_in_area(self, left: int, top: int, width: int, height: int,
                      direction: str, percent: int = 75):
        raise NotImplementedError("iOS 區域滑動尚未實作")

    def tap_coordinates(self, x: int, y: int):
        raise NotImplementedError("iOS 座標點擊尚未實作")

    def double_tap_element(self, locator):
        raise NotImplementedError("iOS 雙擊尚未實作")

    def drag_element(self, locator, end_x: int, end_y: int, speed: int = 1000):
        raise NotImplementedError("iOS 拖曳尚未實作")
