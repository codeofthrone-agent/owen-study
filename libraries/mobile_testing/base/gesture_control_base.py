"""手勢控制抽象基類。

定義跨平台統一的手勢控制介面，包含長按、滑動、座標點擊、
雙擊、拖曳共 7 個抽象方法。
Android 和 iOS 實作類別 MUST 繼承此基類並實作所有抽象方法。
"""
from abc import ABC, abstractmethod


class GestureControlBase(ABC):
    """手勢控制抽象基類 - 定義跨平台統一介面"""

    def __init__(self, driver):
        """初始化手勢控制基類。

        Args:
            driver: Appium WebDriver 實例
        """
        self.driver = driver

    # === 長按 ===

    @abstractmethod
    def long_press_element(self, locator, duration: int = 1000):
        """長按指定元素。

        Args:
            locator: 元素定位器
            duration: 長按持續時間（毫秒），預設 1000ms
        """
        ...

    @abstractmethod
    def long_press_coordinates(self, x: int, y: int, duration: int = 1000):
        """長按指定座標。

        Args:
            x: X 座標
            y: Y 座標
            duration: 長按持續時間（毫秒），預設 1000ms
        """
        ...

    # === 滑動 ===

    @abstractmethod
    def swipe_direction(self, direction: str, percent: int = 75):
        """向指定方向滑動螢幕。

        Args:
            direction: 滑動方向（up/down/left/right）
            percent: 滑動距離佔螢幕百分比，預設 75%
        """
        ...

    @abstractmethod
    def swipe_in_area(self, left: int, top: int, width: int, height: int,
                      direction: str, percent: int = 75):
        """在指定區域內滑動。

        Args:
            left: 區域左邊界 X 座標
            top: 區域上邊界 Y 座標
            width: 區域寬度
            height: 區域高度
            direction: 滑動方向（up/down/left/right）
            percent: 滑動距離佔區域百分比，預設 75%
        """
        ...

    # === 點擊 ===

    @abstractmethod
    def tap_coordinates(self, x: int, y: int):
        """點擊指定座標。

        Args:
            x: X 座標
            y: Y 座標
        """
        ...

    # === 雙擊 ===

    @abstractmethod
    def double_tap_element(self, locator):
        """雙擊指定元素。

        Args:
            locator: 元素定位器
        """
        ...

    # === 拖曳 ===

    @abstractmethod
    def drag_element(self, locator, end_x: int, end_y: int, speed: int = 1000):
        """拖曳元素到指定位置。

        Args:
            locator: 元素定位器
            end_x: 目標 X 座標
            end_y: 目標 Y 座標
            speed: 拖曳速度（毫秒），預設 1000
        """
        ...
