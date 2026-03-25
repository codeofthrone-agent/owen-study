"""Android 手勢控制實作。

使用 Appium 2.x mobile: 命令執行手勢操作。
完整實作將在 Stage 6 由人類協作驗證。
"""
from robot.api import logger

from libraries.mobile_testing.base.gesture_control_base import GestureControlBase


class AndroidGestureControl(GestureControlBase):
    """Android 手勢控制實作（Appium 2.x mobile: 命令）"""

    def long_press_element(self, locator, duration: int = 1000):
        """長按指定元素（mobile: longClickGesture）

        Args:
            locator: 元素定位器
            duration: 長按持續時間（毫秒）
        """
        logger.info(f"長按元素: {locator}，持續 {duration}ms")
        element = self.driver.find_element(*self._parse_locator(locator))
        self.driver.execute_script('mobile: longClickGesture', {
            'elementId': element.id,
            'duration': duration,
        })

    def long_press_coordinates(self, x: int, y: int, duration: int = 1000):
        """長按指定座標（mobile: longClickGesture）

        Args:
            x: X 座標
            y: Y 座標
            duration: 長按持續時間（毫秒）
        """
        logger.info(f"長按座標: ({x}, {y})，持續 {duration}ms")
        self.driver.execute_script('mobile: longClickGesture', {
            'x': int(x),
            'y': int(y),
            'duration': duration,
        })

    def swipe_direction(self, direction: str, percent: int = 75):
        """向指定方向滑動螢幕（mobile: swipeGesture）

        Args:
            direction: 滑動方向（up/down/left/right）
            percent: 滑動距離百分比
        """
        logger.info(f"滑動螢幕: 方向={direction}，百分比={percent}%")
        size = self.driver.get_window_size()
        self.driver.execute_script('mobile: swipeGesture', {
            'left': 0,
            'top': 0,
            'width': size['width'],
            'height': size['height'],
            'direction': direction,
            'percent': self._normalize_percent(percent),
        })

    def swipe_in_area(self, left: int, top: int, width: int, height: int,
                      direction: str, percent: int = 75):
        """在指定區域內滑動（mobile: swipeGesture）

        Args:
            left: 區域左邊界
            top: 區域上邊界
            width: 區域寬度
            height: 區域高度
            direction: 滑動方向
            percent: 滑動距離百分比
        """
        logger.info(f"區域滑動: 區域=({left},{top},{width},{height})，方向={direction}，百分比={percent}%")
        self.driver.execute_script('mobile: swipeGesture', {
            'left': int(left),
            'top': int(top),
            'width': int(width),
            'height': int(height),
            'direction': direction,
            'percent': self._normalize_percent(percent),
        })

    def tap_coordinates(self, x: int, y: int):
        """點擊指定座標（mobile: clickGesture）

        Args:
            x: X 座標
            y: Y 座標
        """
        logger.info(f"點擊座標: ({x}, {y})")
        self.driver.execute_script('mobile: clickGesture', {
            'x': int(x),
            'y': int(y),
        })

    def double_tap_element(self, locator):
        """雙擊指定元素（mobile: doubleClickGesture）

        Args:
            locator: 元素定位器
        """
        logger.info(f"雙擊元素: {locator}")
        element = self.driver.find_element(*self._parse_locator(locator))
        self.driver.execute_script('mobile: doubleClickGesture', {
            'elementId': element.id,
        })

    def drag_element(self, locator, end_x: int, end_y: int, speed: int = 1000):
        """拖曳元素到指定位置（mobile: dragGesture）

        Args:
            locator: 元素定位器
            end_x: 目標 X 座標
            end_y: 目標 Y 座標
        """
        logger.info(f"拖曳元素: {locator} → ({end_x}, {end_y})，速度={speed}")
        element = self.driver.find_element(*self._parse_locator(locator))
        self.driver.execute_script('mobile: dragGesture', {
            'elementId': element.id,
            'endX': int(end_x),
            'endY': int(end_y),
            'speed': max(1, int(speed)),
        })

    @staticmethod
    def _parse_locator(locator: str):
        """解析定位器字串為 (by, value) 元組。

        支援格式：id=xxx, xpath=xxx, accessibility_id=xxx, class=xxx

        Args:
            locator: 定位器字串

        Returns:
            (by, value) 元組
        """
        from appium.webdriver.common.appiumby import AppiumBy

        if '=' not in locator:
            raise ValueError(f"無效的定位器格式: {locator}，應為 'type=value'")

        by_type, value = locator.split('=', 1)
        by_map = {
            'id': AppiumBy.ID,
            'xpath': AppiumBy.XPATH,
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'class': AppiumBy.CLASS_NAME,
        }
        by = by_map.get(by_type.lower())
        if by is None:
            raise ValueError(
                f"不支援的定位器類型: {by_type}（支援: {', '.join(by_map.keys())}）"
            )
        return by, value

    @staticmethod
    def _normalize_percent(percent: int) -> float:
        """將百分比整數轉換為 0~1 之間的小數"""
        return max(0.05, min(1.0, int(percent) / 100))
