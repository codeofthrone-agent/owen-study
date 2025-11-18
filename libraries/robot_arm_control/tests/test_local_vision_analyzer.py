"""
Unit tests for LocalVisionAnalyzer (本機視覺分析引擎)

遵循 TDD 原則開發：
1. Red - 寫失敗的測試
2. Green - 實作最小程度的程式碼讓測試通過
3. Refactor - 重構程式碼

測試範圍：
- Phase 1.2: LocalVisionAnalyzer 基礎類別
- 色彩範圍初始化
- 亮度閾值初始化
- 影像源管理整合
"""

import pytest
import numpy as np
from typing import Optional


class TestLocalVisionAnalyzerInitialization:
    """測試 LocalVisionAnalyzer 初始化功能"""

    def test_analyzer_can_be_initialized(self):
        """測試：LocalVisionAnalyzer 應該可以被初始化

        Given 沒有提供任何參數
        When 初始化 LocalVisionAnalyzer
        Then 應該成功建立實例
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        assert analyzer is not None
        assert isinstance(analyzer, LocalVisionAnalyzer)

    def test_analyzer_has_color_ranges_attribute(self):
        """測試：LocalVisionAnalyzer 應該有 color_ranges 屬性

        Given LocalVisionAnalyzer 已初始化
        When 存取 color_ranges 屬性
        Then 應該是一個字典
        And 應該包含所有支援的顏色
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        assert hasattr(analyzer, 'color_ranges')
        assert isinstance(analyzer.color_ranges, dict)

        # 應該支援至少 7 種顏色
        expected_colors = ['blue', 'white', 'red', 'green', 'yellow', 'orange', 'purple']
        for color in expected_colors:
            assert color in analyzer.color_ranges, f"缺少顏色: {color}"

    def test_analyzer_has_brightness_thresholds_attribute(self):
        """測試：LocalVisionAnalyzer 應該有 brightness_thresholds 屬性

        Given LocalVisionAnalyzer 已初始化
        When 存取 brightness_thresholds 屬性
        Then 應該是一個字典
        And 應該包含 11 個亮度級別 (0%, 10%, ..., 100%)
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        assert hasattr(analyzer, 'brightness_thresholds')
        assert isinstance(analyzer.brightness_thresholds, dict)

        # 應該有 11 個級別
        assert len(analyzer.brightness_thresholds) == 11

        # 驗證每個級別
        for brightness_pct in range(0, 101, 10):
            assert brightness_pct in analyzer.brightness_thresholds

    def test_analyzer_can_accept_image_source_manager(self):
        """測試：LocalVisionAnalyzer 應該可以接受 ImageSourceManager

        Given 已建立 ImageSourceManager 實例
        When 使用 ImageSourceManager 初始化 LocalVisionAnalyzer
        Then 應該成功建立實例
        And 應該可以存取 image_source_manager 屬性
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        image_source_manager = ImageSourceManager()
        analyzer = LocalVisionAnalyzer(image_source_manager=image_source_manager)

        assert analyzer is not None
        assert hasattr(analyzer, 'image_source_manager')
        assert analyzer.image_source_manager is image_source_manager


class TestColorRangesConfiguration:
    """測試色彩範圍配置"""

    def test_blue_color_range_is_valid(self):
        """測試：藍色範圍應該符合 HSV 規格

        Given LocalVisionAnalyzer 已初始化
        When 存取藍色範圍
        Then H 應該在 110±10 範圍
        And S 應該 >150
        And V 應該 >150
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        blue_range = analyzer.color_ranges['blue']

        assert 'lower' in blue_range
        assert 'upper' in blue_range

        lower = blue_range['lower']
        upper = blue_range['upper']

        # HSV 格式驗證
        assert len(lower) == 3
        assert len(upper) == 3

        # H 範圍: 100-120 (110±10)
        assert lower[0] >= 100 and lower[0] <= 110
        assert upper[0] >= 110 and upper[0] <= 120

        # S 範圍: >150
        assert lower[1] >= 150

        # V 範圍: >150
        assert lower[2] >= 150

    def test_white_color_range_is_valid(self):
        """測試：白色範圍應該符合 HSV 規格

        Given LocalVisionAnalyzer 已初始化
        When 存取白色範圍
        Then S 應該 <50
        And V 應該 >200
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        white_range = analyzer.color_ranges['white']

        lower = white_range['lower']
        upper = white_range['upper']

        # S 範圍: <50
        assert upper[1] <= 50

        # V 範圍: >200
        assert lower[2] >= 200

    def test_red_color_range_handles_hue_wraparound(self):
        """測試：紅色範圍應該處理 HSV H 值的環繞問題

        Given LocalVisionAnalyzer 已初始化
        When 存取紅色範圍
        Then 應該有兩個範圍（0±10 和 170-180）
        Or 應該使用單一範圍處理環繞
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        red_range = analyzer.color_ranges['red']

        # 可能是雙範圍或單範圍
        assert 'lower' in red_range
        assert 'upper' in red_range

        # 如果是雙範圍，應該有 lower2 和 upper2
        if 'lower2' in red_range:
            assert 'upper2' in red_range

    @pytest.mark.parametrize("color", ['green', 'yellow', 'orange', 'purple'])
    def test_all_colors_have_valid_ranges(self, color):
        """測試：所有顏色應該有有效的 HSV 範圍

        Given LocalVisionAnalyzer 已初始化
        When 存取任意顏色的範圍
        Then 應該有 lower 和 upper 鍵
        And 每個值應該是長度為 3 的 tuple/list
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        color_range = analyzer.color_ranges[color]

        assert 'lower' in color_range
        assert 'upper' in color_range

        lower = color_range['lower']
        upper = color_range['upper']

        assert len(lower) == 3
        assert len(upper) == 3

        # 每個值應該在有效範圍內
        # H: 0-180, S: 0-255, V: 0-255
        assert 0 <= lower[0] <= 180
        assert 0 <= lower[1] <= 255
        assert 0 <= lower[2] <= 255

        assert 0 <= upper[0] <= 180
        assert 0 <= upper[1] <= 255
        assert 0 <= upper[2] <= 255


class TestBrightnessThresholdsConfiguration:
    """測試亮度閾值配置"""

    @pytest.mark.parametrize("brightness_pct", [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    def test_brightness_threshold_exists(self, brightness_pct):
        """測試：每個亮度級別應該有對應的閾值

        Given LocalVisionAnalyzer 已初始化
        When 存取特定亮度級別
        Then 應該有對應的閾值範圍
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        assert brightness_pct in analyzer.brightness_thresholds

        threshold = analyzer.brightness_thresholds[brightness_pct]
        assert 'min' in threshold
        assert 'max' in threshold

    def test_brightness_thresholds_are_ordered(self):
        """測試：亮度閾值應該遞增排列

        Given LocalVisionAnalyzer 已初始化
        When 比較相鄰的亮度級別
        Then 較高級別的 min 值應該大於較低級別
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        for i in range(0, 91, 10):
            current_brightness = i
            next_brightness = i + 10

            current_max = analyzer.brightness_thresholds[current_brightness]['max']
            next_min = analyzer.brightness_thresholds[next_brightness]['min']

            # 確保沒有重疊或間隙
            assert current_max <= next_min

    def test_brightness_0_percent_is_darkest(self):
        """測試：0% 亮度應該對應最暗的閾值

        Given LocalVisionAnalyzer 已初始化
        When 存取 0% 亮度閾值
        Then min 應該接近 0
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        threshold_0 = analyzer.brightness_thresholds[0]
        assert threshold_0['min'] == 0

    def test_brightness_100_percent_is_brightest(self):
        """測試：100% 亮度應該對應最亮的閾值

        Given LocalVisionAnalyzer 已初始化
        When 存取 100% 亮度閾值
        Then max 應該接近 255
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        threshold_100 = analyzer.brightness_thresholds[100]
        assert threshold_100['max'] == 255


class TestColorDetection:
    """測試色彩檢測功能（Phase 1.2 核心功能）"""

    def test_detect_color_blue_should_return_blue(self, blue_led_image):
        """測試：藍色影像應該檢測為藍色

        Given 一張純藍色的影像
        When 執行色彩檢測
        Then 應該返回 'blue'
        And 信心度應該 >0.9
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(blue_led_image)

        assert detected_color == 'blue'
        assert confidence > 0.9

    def test_detect_color_white_should_return_white(self, white_led_image):
        """測試：白色影像應該檢測為白色

        Given 一張純白色的影像
        When 執行色彩檢測
        Then 應該返回 'white'
        And 信心度應該 >0.9
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(white_led_image)

        assert detected_color == 'white'
        assert confidence > 0.9

    def test_detect_color_off_should_return_off(self, off_led_image):
        """測試：黑色影像應該檢測為 'off'

        Given 一張全黑的影像
        When 執行色彩檢測
        Then 應該返回 'off'
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()

        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(off_led_image)

        assert detected_color == 'off'

    @pytest.mark.parametrize("color_fixture,expected_color", [
        ('red_led_image', 'red'),
        ('green_led_image', 'green'),
        ('yellow_led_image', 'yellow'),
        ('orange_led_image', 'orange'),
        ('purple_led_image', 'purple'),
    ])
    def test_detect_all_colors(self, color_fixture, expected_color, request):
        """測試：所有顏色應該被正確檢測

        Given 一張指定顏色的影像
        When 執行色彩檢測
        Then 應該返回正確的顏色名稱
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        color_image = request.getfixturevalue(color_fixture)

        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(color_image)

        assert detected_color == expected_color


class TestBrightnessDetection:
    """測試亮度檢測功能（Phase 1.2 核心功能）"""

    @pytest.mark.parametrize("brightness_pct", [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    def test_detect_brightness_levels(self, brightness_pct, brightness_images):
        """測試：應該正確檢測各種亮度級別

        Given 一張指定亮度的影像
        When 執行亮度檢測
        Then 應該返回正確的亮度級別
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        test_image = brightness_images[f"{brightness_pct}%"]

        detected_brightness, mean_value = analyzer._detect_brightness(test_image)

        assert detected_brightness == brightness_pct

    def test_brightness_detection_returns_mean_value(self, brightness_images):
        """測試：亮度檢測應該返回平均亮度值

        Given 一張 50% 亮度的影像
        When 執行亮度檢測
        Then 應該返回接近 127 的平均值
        """
        from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer

        analyzer = LocalVisionAnalyzer()
        test_image = brightness_images["50%"]

        detected_brightness, mean_value = analyzer._detect_brightness(test_image)

        # 50% 亮度對應 255 * 0.5 = 127.5
        assert 125 <= mean_value <= 130


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
