# 影像判定本機化 TDD 開發指南

**文件版本**: v1.0.0
**建立日期**: 2025-11-16
**專案**: Robot Framework 多平台自動化測試系統
**開發方法**: Test-Driven Development (TDD)

---

## 📋 目錄

1. [TDD 開發流程](#tdd-開發流程)
2. [測試環境設置](#測試環境設置)
3. [Phase 1: LocalVisionAnalyzer TDD](#phase-1-localvisionanalyzer-tdd)
4. [Phase 2: ImageSourceManager TDD](#phase-2-imagesourcemanager-tdd)
5. [Phase 3: 多色彩檢測 TDD](#phase-3-多色彩檢測-tdd)
6. [Phase 4: 多級亮度檢測 TDD](#phase-4-多級亮度檢測-tdd)
7. [Phase 5: Robot Framework 整合 TDD](#phase-5-robot-framework-整合-tdd)
8. [測試工具與最佳實踐](#測試工具與最佳實踐)

---

## TDD 開發流程

### TDD 三步驟循環

```
┌──────────────┐
│   1. Red     │  編寫失敗的測試
│  (寫測試)   │  → 測試應該失敗（因為功能尚未實作）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  2. Green    │  實作最小功能
│ (寫程式碼)  │  → 讓測試通過
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 3. Refactor  │  重構程式碼
│  (重構)      │  → 保持測試通過，改善程式碼品質
└──────┬───────┘
       │
       │ 重複循環
       └─────────┐
                 │
                 ▼
```

### TDD 開發原則

1. **先寫測試，後寫程式碼**
2. **每次只測試一個功能**
3. **測試應該獨立且可重複**
4. **測試應該快速執行**
5. **測試失敗訊息應該清晰明確**

---

## 測試環境設置

### 安裝測試相依套件

```bash
# 進入專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 安裝測試套件
uv pip install pytest pytest-cov pytest-mock pytest-asyncio

# 安裝影像處理套件（如果尚未安裝）
uv pip install opencv-python numpy
```

### 建立測試目錄結構

```bash
mkdir -p libraries/robot_arm_control/tests
mkdir -p libraries/robot_arm_control/tests/fixtures
mkdir -p libraries/robot_arm_control/tests/mocks
```

### 目錄結構

```
libraries/robot_arm_control/
├── __init__.py
├── LocalVisionAnalyzer.py
├── ImageSourceManager.py
├── image_sources/
│   ├── __init__.py
│   ├── rtsp_source.py
│   ├── usb_camera_source.py
│   └── socket_image_source.py
└── tests/
    ├── __init__.py
    ├── conftest.py                    # pytest 配置與 fixtures
    ├── test_local_vision_analyzer.py  # LocalVisionAnalyzer 測試
    ├── test_image_source_manager.py   # ImageSourceManager 測試
    ├── test_color_detection.py        # 色彩檢測測試
    ├── test_brightness_detection.py   # 亮度檢測測試
    ├── fixtures/
    │   ├── test_images/               # 測試用影像
    │   │   ├── blue_led.png
    │   │   ├── white_led.png
    │   │   ├── red_led.png
    │   │   └── brightness_*.png
    │   └── config/                    # 測試用配置
    │       └── test_button_config.yaml
    └── mocks/
        └── mock_image_source.py       # 模擬影像源
```

---

## Phase 1: LocalVisionAnalyzer TDD

### 測試案例 1.1: 初始化與顏色範圍設定

#### Step 1: Red (編寫測試)

**檔案**: `libraries/robot_arm_control/tests/test_local_vision_analyzer.py`

```python
import pytest
import numpy as np
from libraries.robot_arm_control.LocalVisionAnalyzer import LocalVisionAnalyzer
from libraries.robot_arm_control.ImageSourceManager import ImageSourceManager


class TestLocalVisionAnalyzer:
    """LocalVisionAnalyzer 單元測試"""

    def test_init_should_create_instance(self):
        """測試：初始化應該成功建立實例"""
        # Arrange
        image_source_manager = ImageSourceManager()

        # Act
        analyzer = LocalVisionAnalyzer(image_source_manager)

        # Assert
        assert analyzer is not None
        assert analyzer.image_source_manager == image_source_manager

    def test_init_should_load_color_ranges(self):
        """測試：初始化應該載入 HSV 顏色範圍"""
        # Arrange
        image_source_manager = ImageSourceManager()

        # Act
        analyzer = LocalVisionAnalyzer(image_source_manager)

        # Assert
        assert analyzer.color_ranges is not None
        assert 'blue' in analyzer.color_ranges
        assert 'white' in analyzer.color_ranges
        assert analyzer.color_ranges['blue']['lower'] == [100, 50, 50]
        assert analyzer.color_ranges['blue']['upper'] == [130, 255, 255]

    def test_init_should_load_brightness_thresholds(self):
        """測試：初始化應該載入亮度門檻"""
        # Arrange
        image_source_manager = ImageSourceManager()

        # Act
        analyzer = LocalVisionAnalyzer(image_source_manager)

        # Assert
        assert analyzer.brightness_thresholds is not None
        assert 0 in analyzer.brightness_thresholds
        assert 100 in analyzer.brightness_thresholds
        assert len(analyzer.brightness_thresholds) == 11  # 0-100, 每 10 一級
```

#### Step 2: Green (實作功能)

**檔案**: `libraries/robot_arm_control/LocalVisionAnalyzer.py`

```python
import numpy as np
import cv2
from typing import Dict, Tuple, Optional
from loguru import logger


class LocalVisionAnalyzer:
    """本機視覺分析引擎

    支援:
    - 多色彩檢測: 藍/白/紅/綠/黃/橙/紫
    - 多級亮度檢測: 0-100% (11 級)
    - 雙影像源: RTSP/Socket
    - ArUco 標記校正
    """

    def __init__(self, image_source_manager):
        """初始化

        Args:
            image_source_manager: 影像源管理器實例
        """
        self.image_source_manager = image_source_manager
        self.color_ranges = self._init_color_ranges()
        self.brightness_thresholds = self._init_brightness_thresholds()
        logger.info("LocalVisionAnalyzer 初始化完成")

    def _init_color_ranges(self) -> Dict:
        """初始化 HSV 顏色範圍

        Returns:
            顏色範圍字典
        """
        return {
            'blue': {
                'lower': [100, 50, 50],
                'upper': [130, 255, 255]
            },
            'white': {
                'lower': [0, 0, 200],
                'upper': [180, 50, 255]
            }
            # 其他顏色將在 Phase 3 新增
        }

    def _init_brightness_thresholds(self) -> Dict:
        """初始化 11 級亮度門檻 (0-100%)

        Returns:
            亮度門檻字典 {level: (min_percent, max_percent)}
        """
        thresholds = {}
        for level in range(0, 101, 10):
            if level == 0:
                thresholds[level] = (0, 5)
            elif level == 100:
                thresholds[level] = (96, 100)
            else:
                thresholds[level] = (level - 5, level + 5)
        return thresholds
```

#### Step 3: Refactor (重構)

- 檢查程式碼是否符合 PEP 8 風格
- 新增 Docstring
- 提取常數

---

### 測試案例 1.2: 色彩檢測邏輯

#### Step 1: Red (編寫測試)

```python
import cv2
import numpy as np


class TestLocalVisionAnalyzer:
    # ... 前面的測試 ...

    def test_detect_color_blue_should_return_blue(self):
        """測試：藍色影像應該檢測為藍色"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立純藍色影像 (H=110, S=255, V=255)
        blue_image = np.zeros((100, 100, 3), dtype=np.uint8)
        blue_image[:, :] = [255, 0, 0]  # BGR: 純藍色

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(blue_image)

        # Assert
        assert detected_color == 'blue'
        assert confidence > 0.9  # 高信心度
        assert 100 <= hsv_mean[0] <= 130  # H 在藍色範圍

    def test_detect_color_white_should_return_white(self):
        """測試：白色影像應該檢測為白色"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立純白色影像
        white_image = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(white_image)

        # Assert
        assert detected_color == 'white'
        assert confidence > 0.9
        assert hsv_mean[1] < 50  # S (飽和度) 低
        assert hsv_mean[2] > 200  # V (明度) 高

    def test_detect_color_no_match_should_return_none(self):
        """測試：無匹配顏色應該返回 None"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立黑色影像（無法匹配任何顏色）
        black_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(black_image)

        # Assert
        assert detected_color is None or confidence < 0.3
```

#### Step 2: Green (實作功能)

```python
class LocalVisionAnalyzer:
    # ... 前面的程式碼 ...

    def _detect_color_hsv(self, roi_image: np.ndarray) -> Tuple[Optional[str], float, list]:
        """HSV 色彩檢測

        Args:
            roi_image: ROI 影像 (BGR 格式)

        Returns:
            (detected_color, confidence, hsv_mean)
        """
        # 1. 轉換色彩空間
        hsv_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

        # 2. 初始化結果
        best_color = None
        max_confidence = 0.0
        total_pixels = roi_image.shape[0] * roi_image.shape[1]

        # 3. 對每種顏色進行檢測
        for color_name, color_range in self.color_ranges.items():
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])

            # 建立遮罩
            mask = cv2.inRange(hsv_image, lower, upper)

            # 計算匹配像素數量
            matched_pixels = cv2.countNonZero(mask)

            # 計算信心度
            confidence = matched_pixels / total_pixels

            # 更新最佳結果
            if confidence > max_confidence:
                max_confidence = confidence
                best_color = color_name

        # 4. 計算 HSV 平均值
        hsv_mean = [
            np.mean(hsv_image[:, :, 0]),
            np.mean(hsv_image[:, :, 1]),
            np.mean(hsv_image[:, :, 2])
        ]

        # 5. 返回結果
        return (best_color, max_confidence, hsv_mean)
```

---

### 測試案例 1.3: 亮度檢測邏輯

#### Step 1: Red (編寫測試)

```python
class TestLocalVisionAnalyzer:
    # ... 前面的測試 ...

    def test_detect_brightness_level_0_percent(self):
        """測試：暗影像應該檢測為 0% 亮度"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立接近黑色的影像 (亮度約 5/255 = 2%)
        dark_image = np.ones((100, 100, 3), dtype=np.uint8) * 5

        # Act
        brightness_level, confidence, raw_brightness = analyzer._detect_brightness_level(dark_image)

        # Assert
        assert brightness_level == 0
        assert confidence > 0.8
        assert raw_brightness < 15  # 原始值 < 15

    def test_detect_brightness_level_50_percent(self):
        """測試：中等亮度影像應該檢測為 50% 亮度"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立中等亮度影像 (約 128/255 = 50%)
        medium_image = np.ones((100, 100, 3), dtype=np.uint8) * 128

        # Act
        brightness_level, confidence, raw_brightness = analyzer._detect_brightness_level(medium_image)

        # Assert
        assert brightness_level == 50
        assert confidence > 0.8
        assert 115 <= raw_brightness <= 140  # 50% 範圍

    def test_detect_brightness_level_100_percent(self):
        """測試：亮影像應該檢測為 100% 亮度"""
        # Arrange
        analyzer = LocalVisionAnalyzer(ImageSourceManager())

        # 建立純白影像
        bright_image = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Act
        brightness_level, confidence, raw_brightness = analyzer._detect_brightness_level(bright_image)

        # Assert
        assert brightness_level == 100
        assert confidence > 0.9
        assert raw_brightness > 240  # 原始值 > 240
```

#### Step 2: Green (實作功能)

```python
class LocalVisionAnalyzer:
    # ... 前面的程式碼 ...

    def _detect_brightness_level(self, roi_image: np.ndarray) -> Tuple[int, float, int]:
        """亮度級別檢測

        Args:
            roi_image: ROI 影像 (BGR 格式)

        Returns:
            (brightness_level, confidence, raw_brightness)
        """
        # 1. 轉換為灰階
        gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)

        # 2. 計算平均亮度
        raw_brightness = np.mean(gray_image)

        # 3. 轉換為百分比
        brightness_percent = (raw_brightness / 255.0) * 100

        # 4. 查找最接近的亮度級別
        closest_level = 0
        min_difference = float('inf')

        for level in range(0, 101, 10):
            difference = abs(brightness_percent - level)
            if difference < min_difference:
                min_difference = difference
                closest_level = level

        # 5. 計算信心度
        threshold_range = self.brightness_thresholds[closest_level]
        lower_bound, upper_bound = threshold_range

        if lower_bound <= brightness_percent <= upper_bound:
            # 在範圍內，高信心度
            confidence = 1.0 - (min_difference / 10.0)
        else:
            # 超出範圍，低信心度
            confidence = max(0.0, 1.0 - (min_difference / 20.0))

        # 6. 返回結果
        return (closest_level, confidence, round(raw_brightness))
```

---

## Phase 2: ImageSourceManager TDD

### 測試案例 2.1: 影像源切換

#### Step 1: Red (編寫測試)

**檔案**: `libraries/robot_arm_control/tests/test_image_source_manager.py`

```python
import pytest
from libraries.robot_arm_control.ImageSourceManager import ImageSourceManager


class TestImageSourceManager:
    """ImageSourceManager 單元測試"""

    def test_init_should_create_instance(self):
        """測試：初始化應該成功建立實例"""
        # Act
        manager = ImageSourceManager()

        # Assert
        assert manager is not None
        assert manager.current_source_type is None

    def test_set_image_source_rtsp_should_succeed(self):
        """測試：設定 RTSP 影像源應該成功"""
        # Arrange
        manager = ImageSourceManager()
        config = {
            "url": "rtsp://10.42.0.100:554/stream",
            "timeout": 10
        }

        # Act
        manager.set_image_source("rtsp", config)

        # Assert
        assert manager.current_source_type == "rtsp"
        assert manager.current_config == config

    def test_set_image_source_usb_should_succeed(self):
        """測試：設定 USB 影像源應該成功"""
        # Arrange
        manager = ImageSourceManager()
        config = {
            "device": "/dev/video0",
            "width": 640,
            "height": 480
        }

        # Act
        manager.set_image_source("usb", config)

        # Assert
        assert manager.current_source_type == "usb"
        assert manager.current_config == config

    def test_set_image_source_invalid_type_should_raise_error(self):
        """測試：設定無效影像源類型應該拋出錯誤"""
        # Arrange
        manager = ImageSourceManager()

        # Act & Assert
        with pytest.raises(ValueError, match="不支援的影像源"):
            manager.set_image_source("invalid_type", {})
```

#### Step 2: Green (實作功能)

**檔案**: `libraries/robot_arm_control/ImageSourceManager.py`

```python
from typing import Optional, Dict
import numpy as np
from loguru import logger


class ImageSourceManager:
    """影像源管理器

    統一管理:
    - RTSP 串流
    - USB 攝影機
    - Socket 影像
    """

    SUPPORTED_SOURCES = ["rtsp", "usb", "socket"]

    def __init__(self):
        """初始化影像源管理器"""
        self.current_source_type: Optional[str] = None
        self.current_config: Optional[Dict] = None
        logger.info("ImageSourceManager 初始化完成")

    def set_image_source(self, source_type: str, source_config: dict):
        """設定影像源

        Args:
            source_type: "rtsp" | "usb" | "socket"
            source_config: 源配置字典

        Raises:
            ValueError: 不支援的影像源類型
        """
        if source_type not in self.SUPPORTED_SOURCES:
            raise ValueError(
                f"不支援的影像源: {source_type}\\n"
                f"支援的影像源: {', '.join(self.SUPPORTED_SOURCES)}"
            )

        self.current_source_type = source_type
        self.current_config = source_config

        logger.info(f"影像源已設定為: {source_type}")

    def capture_image(
        self,
        num_frames: int = 5,
        warmup_frames: int = 20
    ) -> np.ndarray:
        """擷取影像（多幀平均）

        Args:
            num_frames: 用於平均的幀數
            warmup_frames: 預熱幀數

        Returns:
            平均後的影像 (numpy.ndarray, BGR)

        Raises:
            RuntimeError: 影像源未設定或擷取失敗
        """
        if self.current_source_type is None:
            raise RuntimeError("影像源尚未設定，請先呼叫 set_image_source()")

        # TODO: 實作影像擷取邏輯（Phase 2 後續任務）
        raise NotImplementedError("capture_image() 尚未實作")
```

---

## Phase 3: 多色彩檢測 TDD

### 測試案例 3.1: 紅色檢測（跨越 0 度問題）

#### Step 1: Red (編寫測試)

**檔案**: `libraries/robot_arm_control/tests/test_color_detection.py`

```python
import pytest
import numpy as np
import cv2
from libraries.robot_arm_control.LocalVisionAnalyzer import LocalVisionAnalyzer
from libraries.robot_arm_control.ImageSourceManager import ImageSourceManager


class TestColorDetection:
    """色彩檢測單元測試"""

    @pytest.fixture
    def analyzer(self):
        """Fixture: 建立 LocalVisionAnalyzer 實例"""
        return LocalVisionAnalyzer(ImageSourceManager())

    def test_detect_red_color_should_handle_hue_wraparound(self, analyzer):
        """測試：紅色檢測應該處理 H 跨越 0 度問題"""
        # Arrange
        # 建立純紅色影像 (H≈0 或 180, S=255, V=255)
        red_image = np.zeros((100, 100, 3), dtype=np.uint8)
        red_image[:, :] = [0, 0, 255]  # BGR: 純紅色

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(red_image)

        # Assert
        assert detected_color == 'red'
        assert confidence > 0.9
        # H 應該接近 0 或 180
        assert (hsv_mean[0] < 10) or (hsv_mean[0] > 170)

    def test_detect_green_color_should_return_green(self, analyzer):
        """測試：綠色影像應該檢測為綠色"""
        # Arrange
        green_image = np.zeros((100, 100, 3), dtype=np.uint8)
        green_image[:, :] = [0, 255, 0]  # BGR: 純綠色

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(green_image)

        # Assert
        assert detected_color == 'green'
        assert confidence > 0.9
        assert 40 <= hsv_mean[0] <= 80  # H 在綠色範圍

    def test_detect_yellow_color_should_return_yellow(self, analyzer):
        """測試：黃色影像應該檢測為黃色"""
        # Arrange
        yellow_image = np.zeros((100, 100, 3), dtype=np.uint8)
        yellow_image[:, :] = [0, 255, 255]  # BGR: 純黃色

        # Act
        detected_color, confidence, hsv_mean = analyzer._detect_color_hsv(yellow_image)

        # Assert
        assert detected_color == 'yellow'
        assert confidence > 0.9
        assert 20 <= hsv_mean[0] <= 40  # H 在黃色範圍
```

#### Step 2: Green (實作功能)

修改 `LocalVisionAnalyzer._init_color_ranges()`:

```python
def _init_color_ranges(self) -> Dict:
    """初始化 HSV 顏色範圍"""
    return {
        'blue': {
            'lower': [100, 50, 50],
            'upper': [130, 255, 255]
        },
        'white': {
            'lower': [0, 0, 200],
            'upper': [180, 50, 255]
        },
        'red': {
            # 紅色跨越 H=0 度，需要兩個範圍
            'lower1': [0, 50, 50],
            'upper1': [10, 255, 255],
            'lower2': [170, 50, 50],
            'upper2': [180, 255, 255]
        },
        'green': {
            'lower': [40, 50, 50],
            'upper': [80, 255, 255]
        },
        'yellow': {
            'lower': [20, 50, 50],
            'upper': [40, 255, 255]
        },
        'orange': {
            'lower': [10, 50, 50],
            'upper': [20, 255, 255]
        },
        'purple': {
            'lower': [130, 50, 50],
            'upper': [160, 255, 255]
        }
    }
```

修改 `LocalVisionAnalyzer._detect_color_hsv()`:

```python
def _detect_color_hsv(self, roi_image: np.ndarray) -> Tuple[Optional[str], float, list]:
    """HSV 色彩檢測（支援紅色跨越 0 度）"""
    hsv_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

    best_color = None
    max_confidence = 0.0
    total_pixels = roi_image.shape[0] * roi_image.shape[1]

    for color_name, color_range in self.color_ranges.items():
        # 處理紅色（兩個範圍）
        if color_name == 'red':
            lower1 = np.array(color_range['lower1'])
            upper1 = np.array(color_range['upper1'])
            lower2 = np.array(color_range['lower2'])
            upper2 = np.array(color_range['upper2'])

            mask1 = cv2.inRange(hsv_image, lower1, upper1)
            mask2 = cv2.inRange(hsv_image, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            # 其他顏色（單一範圍）
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])
            mask = cv2.inRange(hsv_image, lower, upper)

        matched_pixels = cv2.countNonZero(mask)
        confidence = matched_pixels / total_pixels

        if confidence > max_confidence:
            max_confidence = confidence
            best_color = color_name

    hsv_mean = [
        np.mean(hsv_image[:, :, 0]),
        np.mean(hsv_image[:, :, 1]),
        np.mean(hsv_image[:, :, 2])
    ]

    return (best_color, max_confidence, hsv_mean)
```

---

## Phase 4: 多級亮度檢測 TDD

### 測試案例 4.1: 11 級亮度檢測

#### Step 1: Red (編寫測試)

**檔案**: `libraries/robot_arm_control/tests/test_brightness_detection.py`

```python
import pytest
import numpy as np
from libraries.robot_arm_control.LocalVisionAnalyzer import LocalVisionAnalyzer
from libraries.robot_arm_control.ImageSourceManager import ImageSourceManager


class TestBrightnessDetection:
    """亮度檢測單元測試"""

    @pytest.fixture
    def analyzer(self):
        return LocalVisionAnalyzer(ImageSourceManager())

    @pytest.mark.parametrize("brightness_level,expected_raw_value", [
        (0, 12),    # 0% → 約 12/255
        (10, 25),   # 10% → 約 25/255
        (20, 51),   # 20% → 約 51/255
        (30, 76),   # 30% → 約 76/255
        (40, 102),  # 40% → 約 102/255
        (50, 127),  # 50% → 約 127/255
        (60, 153),  # 60% → 約 153/255
        (70, 178),  # 70% → 約 178/255
        (80, 204),  # 80% → 約 204/255
        (90, 229),  # 90% → 約 229/255
        (100, 250), # 100% → 約 250/255
    ])
    def test_detect_brightness_level_all_levels(self, analyzer, brightness_level, expected_raw_value):
        """測試：應該正確檢測所有 11 級亮度"""
        # Arrange
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * expected_raw_value

        # Act
        detected_level, confidence, raw_brightness = analyzer._detect_brightness_level(test_image)

        # Assert
        assert detected_level == brightness_level
        assert confidence > 0.8
        assert abs(raw_brightness - expected_raw_value) < 10  # 允許 ±10 誤差
```

**說明**:
- 使用 `@pytest.mark.parametrize` 進行參數化測試
- 一次測試所有 11 級亮度
- 減少重複程式碼

---

## Phase 5: Robot Framework 整合 TDD

### 測試案例 5.1: 環境設定關鍵字

#### Step 1: Red (編寫測試)

**檔案**: `tests/robot_arm/test_keywords_unit.py`

```python
import pytest
from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords


class TestRobotArmKeywords:
    """RobotArmKeywords 單元測試"""

    @pytest.fixture
    def keywords(self):
        return RobotArmKeywords()

    def test_given_test_environment_is_taipei_lab_should_succeed(self, keywords):
        """測試：設定台北實驗室環境應該成功"""
        # Act
        keywords.given_test_environment_is("taipei_lab")

        # Assert
        assert keywords.current_environment == "taipei_lab"
        assert keywords.env_config is not None
        assert keywords.env_config["name"] == "台北實驗室"
        assert keywords.env_config["image_source"] == "rtsp"

    def test_given_test_environment_is_invalid_should_raise_error(self, keywords):
        """測試：設定無效環境應該拋出錯誤"""
        # Act & Assert
        with pytest.raises(ValueError, match="未知環境"):
            keywords.given_test_environment_is("invalid_env")

    def test_given_panel_type_is_3611a_should_succeed(self, keywords):
        """測試：設定面板類型應該成功"""
        # Arrange
        keywords.given_test_environment_is("taipei_lab")

        # Act
        keywords.given_panel_type_is("3611a")

        # Assert
        assert keywords.current_panel_type == "3611a"
        assert keywords.button_config is not None

    def test_given_panel_type_not_supported_should_raise_error(self, keywords):
        """測試：設定不支援的面板類型應該拋出錯誤"""
        # Arrange
        keywords.given_test_environment_is("taipei_lab")

        # Act & Assert
        with pytest.raises(ValueError, match="不支援面板類型"):
            keywords.given_panel_type_is("unsupported_panel")
```

---

## 測試工具與最佳實踐

### pytest Fixtures

**檔案**: `libraries/robot_arm_control/tests/conftest.py`

```python
import pytest
import numpy as np
import cv2
from pathlib import Path


@pytest.fixture
def test_images_dir():
    """Fixture: 測試影像目錄路徑"""
    return Path(__file__).parent / "fixtures" / "test_images"


@pytest.fixture
def blue_led_image(test_images_dir):
    """Fixture: 藍色 LED 測試影像"""
    image_path = test_images_dir / "blue_led.png"
    if image_path.exists():
        return cv2.imread(str(image_path))
    else:
        # 如果檔案不存在，動態產生
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, :] = [255, 0, 0]  # 純藍色
        return image


@pytest.fixture
def mock_image_source():
    """Fixture: 模擬影像源"""
    class MockImageSource:
        def __init__(self):
            self.capture_count = 0

        def capture_image(self, num_frames=5, warmup_frames=20):
            self.capture_count += 1
            # 返回模擬影像
            return np.ones((480, 640, 3), dtype=np.uint8) * 128

    return MockImageSource()
```

### 執行測試

```bash
# 執行所有測試
pytest libraries/robot_arm_control/tests/

# 執行特定測試檔案
pytest libraries/robot_arm_control/tests/test_local_vision_analyzer.py

# 執行特定測試類別
pytest libraries/robot_arm_control/tests/test_local_vision_analyzer.py::TestLocalVisionAnalyzer

# 執行特定測試案例
pytest libraries/robot_arm_control/tests/test_local_vision_analyzer.py::TestLocalVisionAnalyzer::test_init_should_create_instance

# 產生覆蓋率報告
pytest --cov=libraries/robot_arm_control --cov-report=html libraries/robot_arm_control/tests/

# 執行並顯示詳細輸出
pytest -v -s libraries/robot_arm_control/tests/
```

### TDD 最佳實踐

1. **測試命名規範**:
   - `test_<function>_<scenario>_should_<expected_result>`
   - 例如：`test_detect_color_blue_should_return_blue`

2. **Arrange-Act-Assert (AAA) 模式**:
   ```python
   def test_example(self):
       # Arrange (準備測試資料)
       analyzer = LocalVisionAnalyzer(...)

       # Act (執行待測功能)
       result = analyzer.detect_color(...)

       # Assert (驗證結果)
       assert result == expected_value
   ```

3. **測試獨立性**:
   - 每個測試應該獨立運行
   - 不依賴其他測試的執行順序
   - 使用 fixtures 共享測試資料

4. **測試覆蓋率目標**:
   - 單元測試覆蓋率 > 80%
   - 關鍵邏輯覆蓋率 > 95%

5. **Mock 使用時機**:
   - 外部依賴（網路、檔案系統）
   - 耗時操作（影像擷取）
   - 不穩定資源（硬體設備）

---

## 完整 TDD 開發範例

### 範例：實作 `detect_panel_light()` 方法

#### 1. 編寫測試（Red）

```python
def test_detect_panel_light_should_return_color_and_brightness(self, analyzer):
    """測試：detect_panel_light 應該返回顏色與亮度"""
    # Arrange
    panel_type = "3611a"
    roi_config = {"x": 100, "y": 200, "width": 50, "height": 50}
    image_source_config = {"source_type": "rtsp", "url": "rtsp://..."}

    # Act
    result = analyzer.detect_panel_light(
        panel_type=panel_type,
        roi_config=roi_config,
        image_source_config=image_source_config
    )

    # Assert
    assert "light_state" in result
    assert "color" in result
    assert "brightness_level" in result
    assert "confidence" in result
    assert result["light_state"] in ["on", "off"]
    assert result["brightness_level"] >= 0
    assert result["brightness_level"] <= 100
```

#### 2. 實作功能（Green）

```python
def detect_panel_light(
    self,
    panel_type: str,
    roi_config: dict,
    image_source_config: dict,
    num_frames: int = 5,
    warmup_frames: int = 20,
    save_debug_images: bool = False
) -> dict:
    """檢測面板燈光狀態"""
    # 1. 擷取影像
    image = self.image_source_manager.capture_image(num_frames, warmup_frames)

    # 2. 提取 ROI
    roi_image = self._extract_roi(image, roi_config)

    # 3. 檢測顏色
    color, color_confidence, hsv_mean = self._detect_color_hsv(roi_image)

    # 4. 檢測亮度
    brightness_level, brightness_confidence, raw_brightness = self._detect_brightness_level(roi_image)

    # 5. 判定燈光狀態
    light_state = "on" if brightness_level > 10 else "off"

    # 6. 組裝結果
    return {
        "light_state": light_state,
        "color": color,
        "brightness_level": brightness_level,
        "confidence": min(color_confidence, brightness_confidence),
        "hsv_mean": hsv_mean,
        "pixel_count": roi_image.shape[0] * roi_image.shape[1],
        "raw_data": {
            "raw_brightness": raw_brightness,
            "color_confidence": color_confidence,
            "brightness_confidence": brightness_confidence
        }
    }
```

#### 3. 重構（Refactor）

```python
def detect_panel_light(self, panel_type: str, roi_config: dict, ...) -> dict:
    """檢測面板燈光狀態（重構後）"""
    # 提取方法：影像擷取與 ROI 提取
    roi_image = self._capture_and_extract_roi(roi_config, num_frames, warmup_frames)

    # 提取方法：檢測邏輯
    detection_result = self._perform_detection(roi_image)

    # 提取方法：結果組裝
    return self._assemble_result(detection_result, roi_image)
```

---

## 總結

本 TDD 開發指南提供了：

✅ **完整的 TDD 流程** - Red-Green-Refactor 循環
✅ **詳細的測試案例** - 覆蓋所有核心功能
✅ **實用的測試工具** - pytest fixtures, parametrize
✅ **最佳實踐** - AAA 模式、測試命名、覆蓋率

遵循本指南，您將能夠：
- 以 TDD 方式開發高品質程式碼
- 確保測試覆蓋率 > 80%
- 快速定位與修復問題
- 安全地重構程式碼

**下一步**: 開始 Phase 1 - LocalVisionAnalyzer 開發！

---

**文件版本歷史**:
- v1.0.0 (2025-11-16): 初版建立
