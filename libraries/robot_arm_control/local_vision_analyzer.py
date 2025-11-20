"""
本機視覺分析引擎 (Local Vision Analyzer)

功能:
- 多色彩檢測 (7+ 種顏色: 藍/白/紅/綠/黃/橙/紫)
- 多級亮度檢測 (0-100%, 11 級)
- 雙影像源支援 (RTSP / Socket)
- ArUco 標記校正
- 多幀平均處理 (解決 LED PWM 同步問題)

作者: Robot Automation Team
日期: 2025-11-17
版本: v4.0.0
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from loguru import logger


class LocalVisionAnalyzer:
    """本機視覺分析引擎

    負責所有影像分析功能，包括:
    - HSV 色彩檢測
    - 亮度檢測
    - 多幀平均
    - ROI 提取

    Attributes:
        color_ranges (dict): HSV 色彩範圍定義
        brightness_thresholds (dict): 亮度閾值定義 (0%-100%)
        image_source_manager (ImageSourceManager): 影像源管理器

    Example:
        >>> from image_source_manager import ImageSourceManager
        >>> analyzer = LocalVisionAnalyzer()
        >>> color, confidence, hsv = analyzer._detect_color_hsv(image)
        >>> print(f"檢測到顏色: {color}, 信心度: {confidence:.2f}")
    """

    def __init__(self, image_source_manager: Optional['ImageSourceManager'] = None):
        """初始化本機視覺分析引擎

        Args:
            image_source_manager: 影像源管理器實例 (可選)
        """
        self.image_source_manager = image_source_manager

        # 初始化色彩範圍
        self.color_ranges = self._init_color_ranges()

        # 初始化亮度閾值
        self.brightness_thresholds = self._init_brightness_thresholds()

        logger.info("LocalVisionAnalyzer 初始化完成")
        logger.debug(f"支援顏色: {list(self.color_ranges.keys())}")
        logger.debug(f"亮度級別: {list(self.brightness_thresholds.keys())}")

    def _init_color_ranges(self) -> Dict[str, Dict[str, Tuple[int, int, int]]]:
        """初始化 HSV 色彩範圍

        定義 7+ 種顏色的 HSV 範圍:
        - blue: 藍色 (H=110±10, S>150, V>150)
        - white: 白色 (S<50, V>200)
        - red: 紅色 (H=0±10 or H=170-180, S>150, V>150)
        - green: 綠色 (H=60±10, S>150, V>150)
        - yellow: 黃色 (H=30±10, S>150, V>150)
        - orange: 橙色 (H=15±10, S>150, V>150)
        - purple: 紫色 (H=140±10, S>150, V>150)

        Returns:
            dict: 色彩範圍定義 {color_name: {'lower': (H, S, V), 'upper': (H, S, V)}}

        Note:
            - OpenCV HSV 範圍: H(0-180), S(0-255), V(0-255)
            - 紅色使用雙範圍處理環繞問題
        """
        return {
            'blue': {
                'lower': (100, 150, 150),  # H=100-120, S>150, V>150
                'upper': (120, 255, 255)
            },
            'white': {
                'lower': (0, 0, 200),      # S<50, V>200
                'upper': (180, 50, 255)
            },
            'red': {
                'lower': (0, 150, 150),    # H=0-10, S>150, V>150
                'upper': (10, 255, 255),
                'lower2': (170, 150, 150), # H=170-180 (處理環繞)
                'upper2': (180, 255, 255)
            },
            'green': {
                'lower': (50, 150, 150),   # H=50-70, S>150, V>150
                'upper': (70, 255, 255)
            },
            'yellow': {
                'lower': (20, 150, 150),   # H=20-40, S>150, V>150
                'upper': (40, 255, 255)
            },
            'orange': {
                'lower': (5, 150, 150),    # H=5-25, S>150, V>150
                'upper': (25, 255, 255)
            },
            'purple': {
                'lower': (130, 150, 150),  # H=130-150, S>150, V>150
                'upper': (150, 255, 255)
            }
        }

    def _init_brightness_thresholds(self) -> Dict[int, Dict[str, int]]:
        """初始化亮度閾值

        定義 11 個亮度級別 (0%, 10%, 20%, ..., 100%)

        Returns:
            dict: 亮度閾值定義 {brightness_pct: {'min': value, 'max': value}}

        Example:
            >>> thresholds = analyzer._init_brightness_thresholds()
            >>> print(thresholds[50])  # {'min': 115, 'max': 140}
        """
        thresholds = {}

        for brightness_pct in range(0, 101, 10):
            # 計算對應的 V 值範圍
            # 使用 ±5% 的容差範圍
            center_value = int(255 * brightness_pct / 100)
            tolerance = int(255 * 0.05)  # 5% tolerance

            min_value = max(0, center_value - tolerance)
            max_value = min(255, center_value + tolerance)

            # 特殊處理邊界情況
            if brightness_pct == 0:
                min_value = 0
                max_value = int(255 * 0.05)
            elif brightness_pct == 100:
                min_value = int(255 * 0.95)
                max_value = 255

            thresholds[brightness_pct] = {
                'min': min_value,
                'max': max_value
            }

        return thresholds

    def _detect_color_hsv(self, image: np.ndarray) -> Tuple[str, float, Tuple[float, float, float]]:
        """使用 HSV 色彩空間檢測顏色

        Args:
            image: BGR 格式的輸入影像

        Returns:
            tuple: (detected_color, confidence, hsv_mean)
                - detected_color (str): 檢測到的顏色名稱 ('blue', 'white', 'red', ...)
                - confidence (float): 信心度 (0.0-1.0)
                - hsv_mean (tuple): 平均 HSV 值 (H, S, V)

        Example:
            >>> color, conf, hsv = analyzer._detect_color_hsv(blue_image)
            >>> print(f"顏色: {color}, 信心度: {conf:.2f}")
            顏色: blue, 信心度: 0.95
        """
        # 轉換為 HSV 色彩空間
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 計算平均 HSV 值
        hsv_mean = cv2.mean(hsv_image)[:3]
        h_mean, s_mean, v_mean = hsv_mean

        # 檢查是否為關閉狀態 (黑色)
        if v_mean < 50:
            return 'off', 1.0, hsv_mean

        # 檢測每種顏色的匹配度
        best_match = None
        best_confidence = 0.0

        for color_name, ranges in self.color_ranges.items():
            # 建立遮罩
            lower = np.array(ranges['lower'], dtype=np.uint8)
            upper = np.array(ranges['upper'], dtype=np.uint8)
            mask = cv2.inRange(hsv_image, lower, upper)

            # 如果有第二個範圍 (紅色環繞處理)
            if 'lower2' in ranges:
                lower2 = np.array(ranges['lower2'], dtype=np.uint8)
                upper2 = np.array(ranges['upper2'], dtype=np.uint8)
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                mask = cv2.bitwise_or(mask, mask2)

            # 計算匹配度 (匹配像素百分比)
            match_ratio = np.count_nonzero(mask) / mask.size

            if match_ratio > best_confidence:
                best_confidence = match_ratio
                best_match = color_name

        # 如果沒有找到匹配，返回 'unknown'
        if best_match is None or best_confidence < 0.3:
            return 'unknown', best_confidence, hsv_mean

        return best_match, best_confidence, hsv_mean

    def _detect_brightness(self, image: np.ndarray) -> Tuple[int, float]:
        """檢測影像亮度級別

        Args:
            image: BGR 格式的輸入影像

        Returns:
            tuple: (brightness_level, mean_value)
                - brightness_level (int): 亮度級別 (0, 10, 20, ..., 100)
                - mean_value (float): 平均亮度值 (0-255)

        Example:
            >>> level, value = analyzer._detect_brightness(image)
            >>> print(f"亮度級別: {level}%, 平均值: {value:.1f}")
            亮度級別: 50%, 平均值: 127.5
        """
        # 轉換為灰階
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # 計算平均亮度
        mean_value = np.mean(gray)

        # 找出最接近的亮度級別
        best_level = 0
        min_diff = float('inf')

        for brightness_pct, threshold in self.brightness_thresholds.items():
            # 計算與範圍中心的距離
            center = (threshold['min'] + threshold['max']) / 2
            diff = abs(mean_value - center)

            if diff < min_diff:
                min_diff = diff
                best_level = brightness_pct

        return best_level, mean_value

    def detect_panel_light(
        self,
        panel_type: str,
        roi_config: dict,
        image_source_config: dict,
        num_frames: int = 5,
        warmup_frames: int = 20,
        save_debug_images: bool = False,
        step_prefix: str = ""
    ) -> dict:
        """檢測面板燈光狀態 (完整檢測流程)

        Args:
            panel_type: 面板類型 ('3510a', '3611a', '3611c')
            roi_config: ROI 配置 (包含各按鈕的 ROI 座標)
            image_source_config: 影像源配置 (RTSP 或 Socket)
            num_frames: 多幀平均的幀數 (預設 5)
            warmup_frames: 預熱幀數 (預設 20)
            save_debug_images: 是否儲存除錯影像 (預設 False)
            step_prefix: 步驟命名前綴 (例如: "step2_before", "step5_after")。無呼叫的話不加

        Returns:
            dict: 檢測結果
                {
                    'button_id': {
                        'color': str,
                        'brightness': int,
                        'confidence': float,
                        'hsv_mean': tuple,
                        'brightness_value': float
                    },
                    ...
                }

        Raises:
            ValueError: 如果 image_source_manager 未設定
            RuntimeError: 如果影像擷取失敗

        Example:
            >>> config = {
            ...     'type': 'rtsp',
            ...     'url': 'rtsp://192.168.1.100:554/stream1'
            ... }
            >>> roi = {'light1': {'x': 100, 'y': 100, 'width': 50, 'height': 50}}
            >>> result = analyzer.detect_panel_light('3510a', roi, config)
            >>> print(result['light1']['color'])
            'blue'
        """
        if self.image_source_manager is None:
            raise ValueError("image_source_manager 未設定，請先初始化")

        try:
            # 1. 設定影像源
            source_type = image_source_config.get("type", "rtsp")
            self.image_source_manager.set_image_source(source_type, image_source_config)

            # 2. 擷取多幀影像並平均
            frames = self.image_source_manager.capture_multiple_frames(
                num_frames=num_frames,
                warmup_frames=warmup_frames
            )

            if not frames:
                raise RuntimeError("無法擷取影像: 接收到的影像列表為空")

            # 3. 計算平均影像
            avg_frame = np.mean(frames, axis=0).astype(np.uint8)

            # 4. 對每個 ROI 進行檢測
            results = {}
            for button_id, roi in roi_config.items():
                # 提取 ROI
                x, y, w, h = roi['x'], roi['y'], roi['width'], roi['height']
                roi_image = avg_frame[y:y+h, x:x+w]

                # 檢測色彩
                color, conf, hsv_mean = self._detect_color_hsv(roi_image)

                # 檢測亮度
                brightness_level, brightness_value = self._detect_brightness(roi_image)

                # 儲存除錯影像（如果需要）
                if save_debug_images:
                    debug_dir = Path("output/debug_images")
                    debug_dir.mkdir(parents=True, exist_ok=True)

                    import time
                    timestamp = time.strftime("%Y%m%d-%H%M%S")

                    # 建立檔名前綴 (包含步驟資訊)
                    prefix = f"{step_prefix}_" if step_prefix else ""

                    # 儲存完整影像（每個按鈕只儲存一次）
                    if button_id == list(roi_config.keys())[0]:  # 第一個按鈕時儲存完整影像
                        full_debug_path = debug_dir / f"{prefix}{panel_type}_full_{timestamp}.jpg"
                        cv2.imwrite(str(full_debug_path), avg_frame)
                        logger.debug(f"完整影像已儲存: {full_debug_path}")

                    # 儲存 ROI 影像
                    roi_debug_path = debug_dir / f"{prefix}{panel_type}_{button_id}_{timestamp}_roi.jpg"
                    cv2.imwrite(str(roi_debug_path), roi_image)
                    logger.debug(f"ROI 影像已儲存: {roi_debug_path}")

                # 組合結果
                results[button_id] = {
                    "color": color,
                    "brightness": brightness_level,
                    "confidence": conf,
                    "hsv_mean": hsv_mean,
                    "brightness_value": brightness_value,
                    "light_state": "on" if brightness_value > 50 else "off"
                }

            logger.info(f"面板 {panel_type} 檢測完成: {len(results)} 個按鈕")
            return results

        except Exception as e:
            logger.error(f"面板燈光檢測失敗: {e}")
            raise RuntimeError(f"檢測失敗: {e}")

    def detect_physical_light_brightness(
        self,
        roi_config: dict,
        image_source_config: dict,
        num_frames: int = 5,
        warmup_frames: int = 20,
        save_debug_images: bool = False,
        step_prefix: str = ""
    ) -> Tuple[dict, np.ndarray, np.ndarray]:
        """檢測實體燈光亮度

        Args:
            roi_config: ROI 配置字典 (單一 ROI 或多個 ROI)
                {
                    'x': int,
                    'y': int,
                    'width': int,
                    'height': int
                }
            image_source_config: 影像源配置
            num_frames: 多幀平均數量（預設 5）
            warmup_frames: 預熱幀數（預設 20）
            save_debug_images: 是否儲存除錯影像（預設 False）
            step_prefix: 步驟命名前綴 (例如: "step3_before", "step6_after")。無呼叫的話不加

        Returns:
            Tuple[dict, np.ndarray, np.ndarray]: 檢測結果、完整影像、ROI影像
                - dict: 檢測結果
                    {
                        "light_state": "on" | "off",
                        "brightness_level": 0-100,
                        "brightness_value": 0-255,
                        "confidence": 0.0-1.0
                    }
                - np.ndarray: 完整影像 (BGR)
                - np.ndarray: ROI 影像 (BGR)

        Raises:
            ValueError: image_source_manager 未設定
            RuntimeError: 檢測失敗

        Example:
            >>> analyzer = LocalVisionAnalyzer(image_source_manager)
            >>> config = {"type": "rtsp", "url": "rtsp://..."}
            >>> roi = {'x': 100, 'y': 100, 'width': 50, 'height': 50}
            >>> result, full_img, roi_img = analyzer.detect_physical_light_brightness(roi, config)
            >>> print(result['brightness_level'])
            50
        """
        if self.image_source_manager is None:
            raise ValueError("image_source_manager 未設定，請先初始化")

        try:
            # 1. 設定影像源
            source_type = image_source_config.get("type", "rtsp")
            self.image_source_manager.set_image_source(source_type, image_source_config)

            # 2. 擷取多幀影像並平均
            frames = self.image_source_manager.capture_multiple_frames(
                num_frames=num_frames,
                warmup_frames=warmup_frames
            )

            if not frames:
                raise RuntimeError("無法擷取影像: 接收到的影像列表為空")

            # 3. 計算平均影像
            avg_frame = np.mean(frames, axis=0).astype(np.uint8)

            # 4. 提取 ROI
            x, y, w, h = roi_config['x'], roi_config['y'], roi_config['width'], roi_config['height']
            roi_image = avg_frame[y:y+h, x:x+w]

            # 5. 檢測亮度
            brightness_level, brightness_value = self._detect_brightness(roi_image)

            # 6. 判定燈光狀態
            light_state = "on" if brightness_value > 50 else "off"

            # 7. 計算信心度（基於亮度值的穩定性）
            # 簡單方式：如果亮度值在門檻範圍內，信心度高
            threshold = self.brightness_thresholds.get(brightness_level)
            if threshold:
                # 計算亮度值與級別中心的距離
                center = (threshold['min'] + threshold['max']) / 2
                distance = abs(brightness_value - center)
                max_distance = (threshold['max'] - threshold['min']) / 2
                confidence = 1.0 - (distance / max_distance) if max_distance > 0 else 1.0
                confidence = max(0.0, min(1.0, confidence))
            else:
                confidence = 0.5

            # 8. 儲存除錯影像（如果需要）
            if save_debug_images:
                debug_dir = Path("output/debug_images")
                debug_dir.mkdir(parents=True, exist_ok=True)

                import time
                timestamp = time.strftime("%Y%m%d-%H%M%S")

                # 建立檔名前綴 (包含步驟資訊)
                prefix = f"{step_prefix}_" if step_prefix else ""

                # 儲存完整影像
                full_debug_path = debug_dir / f"{prefix}physical_light_full_{timestamp}.jpg"
                cv2.imwrite(str(full_debug_path), avg_frame)
                logger.debug(f"完整影像已儲存: {full_debug_path}")

                # 儲存 ROI 影像
                roi_debug_path = debug_dir / f"{prefix}physical_light_roi_{timestamp}.jpg"
                cv2.imwrite(str(roi_debug_path), roi_image)
                logger.debug(f"ROI 影像已儲存: {roi_debug_path}")

            result = {
                "light_state": light_state,
                "brightness_level": brightness_level,
                "brightness_value": float(brightness_value),
                "confidence": confidence
            }

            logger.info(f"實體燈光檢測完成: {light_state}, 亮度: {brightness_level}%")
            return result, avg_frame, roi_image

        except Exception as e:
            logger.error(f"實體燈光亮度檢測失敗: {e}")
            raise RuntimeError(f"檢測失敗: {e}")

    def detect_single_button(
        self,
        button_id: str,
        roi_config: dict,
        image_source_config: dict,
        num_frames: int = 5,
        warmup_frames: int = 20,
        save_debug_image: bool = False
    ) -> Tuple[dict, np.ndarray, np.ndarray]:
        """檢測單一按鈕燈光狀態（便捷方法）

        此方法是 detect_panel_light 的簡化版本，專門用於檢測單一按鈕。

        Args:
            button_id: 按鈕 ID (例如: 'light1', 'light2', 'bluetooth')
            roi_config: 單一按鈕的 ROI 配置
                {
                    'x': int,
                    'y': int,
                    'width': int,
                    'height': int
                }
            image_source_config: 影像源配置
                {
                    'type': 'rtsp' | 'socket',
                    'url': str,  # RTSP only
                    'host': str,  # Socket only
                    'port': int   # Socket only
                }
            num_frames: 多幀平均數量（預設 5）
            warmup_frames: 預熱幀數（預設 20）
            save_debug_image: 是否儲存除錯影像（預設 False）

        Returns:
            Tuple[dict, np.ndarray, np.ndarray]: 檢測結果、完整影像、ROI影像
                - dict: 檢測結果
                    {
                        "color": str,  # 顏色名稱
                        "brightness_level": int,  # 0-100%
                        "confidence": float,  # 0.0-1.0
                        "raw_brightness": float  # 0-255
                    }
                - np.ndarray: 完整影像 (BGR)
                - np.ndarray: ROI 影像 (BGR)

        Raises:
            ValueError: image_source_manager 未設定
            RuntimeError: 檢測失敗

        Example:
            >>> analyzer = LocalVisionAnalyzer(image_source_manager)
            >>> config = {"type": "rtsp", "url": "rtsp://..."}
            >>> roi = {'x': 100, 'y': 100, 'width': 50, 'height': 50}
            >>> result, full_img, roi_img = analyzer.detect_single_button('light1', roi, config)
            >>> print(f"顏色: {result['color']}, 亮度: {result['brightness_level']}%")
        """
        if self.image_source_manager is None:
            raise ValueError("image_source_manager 未設定，請先初始化")

        try:
            # 1. 設定影像源
            source_type = image_source_config.get("type", "rtsp")
            self.image_source_manager.set_image_source(source_type, image_source_config)

            # 2. 擷取多幀影像並平均
            frames = self.image_source_manager.capture_multiple_frames(
                num_frames=num_frames,
                warmup_frames=warmup_frames
            )

            if not frames:
                raise RuntimeError("無法擷取影像: 接收到的影像列表為空")

            # 3. 計算平均影像
            avg_frame = np.mean(frames, axis=0).astype(np.uint8)

            # 4. 提取 ROI
            x, y, w, h = roi_config['x'], roi_config['y'], roi_config['width'], roi_config['height']
            roi_image = avg_frame[y:y+h, x:x+w]

            # 5. 檢測色彩
            color, conf, hsv_mean = self._detect_color_hsv(roi_image)

            # 6. 檢測亮度
            brightness_level, brightness_value = self._detect_brightness(roi_image)

            # 7. 儲存除錯影像（如果需要）
            if save_debug_image:
                debug_dir = Path("output/debug_images")
                debug_dir.mkdir(parents=True, exist_ok=True)

                import time
                timestamp = time.strftime("%Y%m%d-%H%M%S")

                # 儲存完整影像
                full_debug_path = debug_dir / f"{button_id}_{timestamp}_full.jpg"
                cv2.imwrite(str(full_debug_path), avg_frame)
                logger.debug(f"完整影像已儲存: {full_debug_path}")

                # 儲存 ROI 影像
                roi_debug_path = debug_dir / f"{button_id}_{timestamp}_roi.jpg"
                cv2.imwrite(str(roi_debug_path), roi_image)
                logger.debug(f"ROI 影像已儲存: {roi_debug_path}")

            # 8. 組合結果
            result = {
                "color": color,
                "brightness_level": brightness_level,
                "confidence": conf,
                "raw_brightness": brightness_value
            }

            logger.info(f"按鈕 {button_id} 檢測完成: 顏色={color}, 亮度={brightness_level}%, 信心度={conf:.2f}")
            return result, avg_frame, roi_image

        except Exception as e:
            logger.error(f"按鈕檢測失敗 ({button_id}): {e}")
            raise RuntimeError(f"檢測失敗: {e}")


if __name__ == "__main__":
    # 簡單測試
    analyzer = LocalVisionAnalyzer()

    # 測試藍色檢測
    blue_image = np.zeros((100, 100, 3), dtype=np.uint8)
    blue_image[:, :] = [255, 0, 0]  # BGR: 藍色

    color, confidence, hsv_mean = analyzer._detect_color_hsv(blue_image)
    print(f"檢測到顏色: {color}, 信心度: {confidence:.2f}, HSV: {hsv_mean}")

    # 測試亮度檢測
    brightness_level, mean_value = analyzer._detect_brightness(blue_image)
    print(f"亮度級別: {brightness_level}%, 平均值: {mean_value:.1f}")
