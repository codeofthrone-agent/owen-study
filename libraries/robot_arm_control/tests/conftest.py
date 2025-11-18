"""
pytest configuration file for robot_arm_control tests

提供共用的 fixtures 和測試工具
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from typing import Tuple


@pytest.fixture
def test_images_dir():
    """Fixture: 測試影像目錄路徑

    Returns:
        Path: 測試影像目錄的絕對路徑
    """
    return Path(__file__).parent / "fixtures" / "test_images"


@pytest.fixture
def blue_led_image() -> np.ndarray:
    """Fixture: 藍色 LED 測試影像

    模擬藍色 LED 燈光的影像（HSV: H=110±10, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的藍色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [255, 0, 0]  # BGR: 純藍色
    return image


@pytest.fixture
def white_led_image() -> np.ndarray:
    """Fixture: 白色 LED 測試影像

    模擬白色 LED 燈光的影像（S<50, V>200）

    Returns:
        np.ndarray: BGR 格式的白色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [255, 255, 255]  # BGR: 純白色
    return image


@pytest.fixture
def red_led_image() -> np.ndarray:
    """Fixture: 紅色 LED 測試影像

    模擬紅色 LED 燈光的影像（HSV: H=0±10 or H=170-180, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的紅色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [0, 0, 255]  # BGR: 純紅色
    return image


@pytest.fixture
def green_led_image() -> np.ndarray:
    """Fixture: 綠色 LED 測試影像

    模擬綠色 LED 燈光的影像（HSV: H=60±10, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的綠色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [0, 255, 0]  # BGR: 純綠色
    return image


@pytest.fixture
def yellow_led_image() -> np.ndarray:
    """Fixture: 黃色 LED 測試影像

    模擬黃色 LED 燈光的影像（HSV: H=30±10, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的黃色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [0, 255, 255]  # BGR: 純黃色
    return image


@pytest.fixture
def orange_led_image() -> np.ndarray:
    """Fixture: 橙色 LED 測試影像

    模擬橙色 LED 燈光的影像（HSV: H=15±10, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的橙色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [0, 165, 255]  # BGR: 橙色
    return image


@pytest.fixture
def purple_led_image() -> np.ndarray:
    """Fixture: 紫色 LED 測試影像

    模擬紫色 LED 燈光的影像（HSV: H=140±10, S>150, V>150）

    Returns:
        np.ndarray: BGR 格式的紫色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:, :] = [255, 0, 255]  # BGR: 紫色
    return image


@pytest.fixture
def off_led_image() -> np.ndarray:
    """Fixture: 關閉狀態 LED 測試影像

    模擬 LED 關閉的黑色影像（V<50）

    Returns:
        np.ndarray: BGR 格式的黑色影像 (100x100)
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # 已經是全黑 (0, 0, 0)
    return image


@pytest.fixture
def brightness_images() -> dict[str, np.ndarray]:
    """Fixture: 不同亮度的測試影像

    產生 0%, 10%, 20%, ..., 100% 亮度的測試影像

    Returns:
        dict[str, np.ndarray]: 亮度級別 -> 影像的字典
    """
    images = {}
    for brightness_pct in range(0, 101, 10):
        value = int(255 * brightness_pct / 100)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, :] = [value, value, value]
        images[f"{brightness_pct}%"] = image
    return images


@pytest.fixture
def mock_rtsp_url() -> str:
    """Fixture: 模擬 RTSP URL

    Returns:
        str: 測試用的 RTSP URL
    """
    return "rtsp://admin:admin@192.168.1.100:554/stream1"


@pytest.fixture
def mock_socket_config() -> dict:
    """Fixture: 模擬 Socket 配置

    Returns:
        dict: 測試用的 Socket 配置
    """
    return {
        "host": "10.42.0.180",
        "port": 9000,
        "timeout": 10
    }


@pytest.fixture
def mock_roi_config() -> dict:
    """Fixture: 模擬 ROI 配置

    Returns:
        dict: 測試用的 ROI 配置
    """
    return {
        "light1": {"x": 100, "y": 100, "width": 50, "height": 50},
        "light2": {"x": 200, "y": 100, "width": 50, "height": 50},
        "light3": {"x": 300, "y": 100, "width": 50, "height": 50},
        "bluetooth": {"x": 400, "y": 100, "width": 50, "height": 50}
    }


@pytest.fixture
def create_test_image():
    """Fixture Factory: 建立自訂顏色的測試影像

    Returns:
        function: 建立影像的工廠函式

    Example:
        >>> create_image = create_test_image
        >>> blue_image = create_image(color=(255, 0, 0), size=(100, 100))
    """
    def _create_image(color: Tuple[int, int, int] = (0, 0, 0),
                      size: Tuple[int, int] = (100, 100)) -> np.ndarray:
        """建立指定顏色和大小的影像

        Args:
            color: BGR 顏色值 (B, G, R)
            size: 影像大小 (height, width)

        Returns:
            np.ndarray: BGR 格式的影像
        """
        image = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        image[:, :] = color
        return image

    return _create_image


@pytest.fixture
def save_test_image(test_images_dir):
    """Fixture Factory: 儲存測試影像到 fixtures 目錄

    Returns:
        function: 儲存影像的工廠函式
    """
    def _save_image(image: np.ndarray, filename: str) -> Path:
        """儲存影像到測試目錄

        Args:
            image: 要儲存的影像
            filename: 檔案名稱（例如 "blue_led.jpg"）

        Returns:
            Path: 儲存的檔案路徑
        """
        filepath = test_images_dir / filename
        cv2.imwrite(str(filepath), image)
        return filepath

    return _save_image
