"""跨平台手勢控制 - Robot Framework Library 統一入口。

根據初始化時傳入的 platform 參數，自動分發至對應的平台實作類別。
Driver 透過 BuiltIn().get_library_instance() 自動從 AppiumLibrary 取得。
"""
from robot.api.deco import keyword


class GestureControlKeywords:
    """跨平台手勢控制統一入口

    使用方式：
        Library    libraries/mobile_testing/GestureControlKeywords.py

        初始化手勢控制    android
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._impl = None

    def _get_driver(self):
        """從已載入的 AppiumLibrary 或 CustomAppiumKeywords 自動取得 driver"""
        from robot.libraries.BuiltIn import BuiltIn

        try:
            appium_lib = BuiltIn().get_library_instance('AppiumLibrary')
            return appium_lib._current_application()
        except RuntimeError:
            pass
        try:
            custom_lib = BuiltIn().get_library_instance('CustomAppiumKeywords')
            return custom_lib.driver
        except RuntimeError:
            pass
        raise RuntimeError(
            "無法取得 WebDriver。請確保已載入 AppiumLibrary 或 "
            "CustomAppiumKeywords，且已開啟應用程式。"
        )

    def _get_impl(self):
        """取得底層平台實作，未初始化時拋出 RuntimeError"""
        if self._impl is None:
            raise RuntimeError("尚未初始化，請先呼叫「初始化手勢控制」")
        return self._impl

    # === 初始化 ===

    @keyword("初始化手勢控制")
    def init_gesture_control(self, platform: str):
        """初始化手勢控制，自動從 AppiumLibrary 取得 driver。

        Args:
            platform: 目標平台（android 或 ios）
        """
        from libraries.mobile_testing.android.AndroidGestureControl import AndroidGestureControl
        from libraries.mobile_testing.ios.IOSGestureControl import IOSGestureControl

        driver = self._get_driver()
        platform_lower = platform.lower()
        if platform_lower == 'android':
            self._impl = AndroidGestureControl(driver)
        elif platform_lower == 'ios':
            self._impl = IOSGestureControl(driver)
        else:
            raise ValueError(f"不支援的平台: {platform}（支援: android, ios）")

    # === 長按 ===

    @keyword("長按元素")
    def long_press_element(self, locator, duration: int = 1000):
        """長按指定元素。

        Args:
            locator: 元素定位器（如 id=xxx, xpath=xxx）
            duration: 長按持續時間（毫秒），預設 1000
        """
        self._get_impl().long_press_element(locator, int(duration))

    @keyword("長按座標")
    def long_press_coordinates(self, x: int, y: int, duration: int = 1000):
        """長按指定座標。

        Args:
            x: X 座標
            y: Y 座標
            duration: 長按持續時間（毫秒），預設 1000
        """
        self._get_impl().long_press_coordinates(int(x), int(y), int(duration))

    # === 滑動 ===

    @keyword("滑動螢幕")
    def swipe_direction(self, direction: str, percent: int = 75):
        """向指定方向滑動螢幕。

        Args:
            direction: 滑動方向（up/down/left/right）
            percent: 滑動距離百分比，預設 75
        """
        self._get_impl().swipe_direction(direction, int(percent))

    @keyword("在區域內滑動")
    def swipe_in_area(self, left: int, top: int, width: int, height: int,
                      direction: str, percent: int = 75):
        """在指定區域內滑動。

        Args:
            left: 區域左邊界
            top: 區域上邊界
            width: 區域寬度
            height: 區域高度
            direction: 滑動方向
            percent: 滑動距離百分比，預設 75
        """
        self._get_impl().swipe_in_area(
            int(left), int(top), int(width), int(height),
            direction, int(percent)
        )

    # === 點擊 ===

    @keyword("點擊座標")
    def tap_coordinates(self, x: int, y: int):
        """點擊指定座標。

        Args:
            x: X 座標
            y: Y 座標
        """
        self._get_impl().tap_coordinates(int(x), int(y))

    # === 雙擊 ===

    @keyword("雙擊元素")
    def double_tap_element(self, locator):
        """雙擊指定元素。

        Args:
            locator: 元素定位器
        """
        self._get_impl().double_tap_element(locator)

    # === 拖曳 ===

    @keyword("拖曳元素")
    def drag_element(self, locator, end_x: int, end_y: int, speed: int = 1000):
        """拖曳元素到指定位置。

        Args:
            locator: 元素定位器
            end_x: 目標 X 座標
            end_y: 目標 Y 座標
            speed: 拖曳速度（毫秒，預設 1000）
        """
        self._get_impl().drag_element(locator, int(end_x), int(end_y), int(speed))
