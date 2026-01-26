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
from cv2 import aruco


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
        step_prefix: str = "",
        annotate_full_image: bool = True
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
            annotate_full_image: 是否在 full image 標註所有 ROI 框（預設 True）

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
        logger.info(f"🎬 detect_panel_light開始: panel_type={panel_type}, roi_config_keys={list(roi_config.keys())}, num_frames={num_frames}")
        
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

            # 4. 動態ArUco offset計算 (v4.2.0新增)
            # 檢查roi_config中是否有任何按鈕包含aruco_markers參考資料
            offset_x, offset_y = 0.0, 0.0
            aruco_offset_applied = False
            
            # 從任一按鈕的配置中取得aruco_markers(通常所有按鈕共用同一組markers)
            first_button_config = next(iter(roi_config.values()))
            logger.info(f"🔍 detect_panel_light: roi_config keys={list(roi_config.keys())}")
            logger.info(f"🔍 detect_panel_light: first_button_config type={type(first_button_config)}, keys={list(first_button_config.keys()) if isinstance(first_button_config, dict) else 'N/A'}")
            logger.info(f"🔍 detect_panel_light: has aruco_markers={'aruco_markers' in first_button_config if isinstance(first_button_config, dict) else False}")
            
            if isinstance(first_button_config, dict) and 'aruco_markers' in first_button_config:
                try:
                    logger.info(f"▶️ 開始計算ArUco offset,markers數量={len(first_button_config['aruco_markers'])}")
                    offset_x, offset_y = self._calculate_aruco_offset(
                        avg_frame, 
                        first_button_config['aruco_markers']
                    )
                    aruco_offset_applied = True
                    logger.info(f"✅ 應用ArUco offset校正: ({offset_x:.1f}, {offset_y:.1f}) 像素")
                except Exception as e:
                    logger.warning(f"ArUco offset計算失敗: {e}, 使用原始ROI座標")
                    offset_x, offset_y = 0.0, 0.0
            else:
                logger.info(f"⚠️ 跳過ArUco offset: first_button_config不符合條件")

            # 5. 對每個 ROI 進行檢測
            results = {}
            for button_id, button_config in roi_config.items():
                # 處理button_config結構相容性
                # - 新格式v4.2.0+: button_config = {'roi': {...}, 'aruco_markers': [...]}
                # - 舊格式v4.1.x: button_config = {'x': ..., 'y': ..., 'width': ..., 'height': ...}
                if isinstance(button_config, dict) and 'roi' in button_config:
                    # 新格式: 包含roi和aruco_markers的完整配置
                    roi = button_config['roi']
                else:
                    # 舊格式: 直接是roi座標(向後相容)
                    roi = button_config
                
                # 提取 ROI (應用ArUco offset)
                x = int(roi['x'] + offset_x)
                y = int(roi['y'] + offset_y)
                w, h = roi['width'], roi['height']
                
                # 確保ROI在影像範圍內
                x = max(0, min(x, avg_frame.shape[1] - w))
                y = max(0, min(y, avg_frame.shape[0] - h))
                
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
                        image_to_save = avg_frame
                        
                        # 標註所有按鈕的 ROI (如果啟用)
                        if annotate_full_image:
                            roi_list = []
                            for btn_id, btn_config in roi_config.items():
                                # 處理 button_config 結構相容性
                                if isinstance(btn_config, dict) and 'roi' in btn_config:
                                    roi = btn_config['roi']
                                else:
                                    roi = btn_config
                                
                                # 應用 ArUco offset
                                roi_list.append({
                                    'name': btn_id,
                                    'x': int(roi['x'] + offset_x),
                                    'y': int(roi['y'] + offset_y),
                                    'width': roi['width'],
                                    'height': roi['height'],
                                    'color': None  # 顏色會在檢測後才知道,這裡先設為 None
                                })
                            
                            image_to_save = self._draw_roi_annotations(avg_frame, roi_list)
                            logger.debug(f"已在 full image 標註 {len(roi_list)} 個 ROI")
                        
                        full_debug_path = debug_dir / f"{prefix}{panel_type}_full_{timestamp}.jpg"
                        cv2.imwrite(str(full_debug_path), image_to_save)
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
        step_prefix: str = "",
        annotate_full_image: bool = True
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
            annotate_full_image: 是否在 full image 標註 ROI 框（預設 True）

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
            logger.info(f"📸 擷取影像解析度: {avg_frame.shape[1]}x{avg_frame.shape[0]}")

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

                # 準備要儲存的 full image
                image_to_save = avg_frame
                
                # 標註 ROI (如果啟用)
                if annotate_full_image:
                    roi_list = [{
                        'name': 'ROI',
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'brightness': float(brightness_value),
                        'is_on': light_state == "on"
                    }]
                    image_to_save = self._draw_roi_annotations(avg_frame, roi_list)
                    logger.debug("已在 full image 標註 ROI")

                # 儲存完整影像 (含標註)
                full_debug_path = debug_dir / f"{prefix}physical_light_full_{timestamp}.jpg"
                cv2.imwrite(str(full_debug_path), image_to_save)
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
        save_debug_image: bool = False,
        apply_aruco_offset: bool = True,  # 新增參數:是否應用ArUco offset校正
        annotate_full_image: bool = True  # 新增參數:是否在 full image 標註 ROI
    ) -> Tuple[dict, np.ndarray, np.ndarray]:
        """檢測單一按鈕燈光狀態(便捷方法)

        此方法是 detect_panel_light 的簡化版本,專門用於檢測單一按鈕。
        
        v4.1.0 新增: Runtime動態ArUco offset校正
        當roi_config包含'aruco_markers'參考資料且apply_aruco_offset=True時,
        會在runtime自動檢測ArUco markers並計算位置偏移,補償機器手臂位置誤差。

        Args:
            button_id: 按鈕 ID (例如: 'light1', 'light2', 'bluetooth')
            roi_config: 完整的vision配置字典 (包含roi和aruco_markers)
                {
                    'roi': {
                        'x': int,
                        'y': int,
                        'width': int,
                        'height': int
                    },
                    'aruco_markers': List[Dict] (可選,用於offset校正),
                    'observe_angles': List[float] (可選)
                }
                注意: 從v4.2.0開始,應傳入button_config['vision']完整配置
                     而不只是button_config['vision']['roi']
            image_source_config: 影像源配置
                {
                    'type': 'rtsp' | 'socket',
                    'url': str,  # RTSP only
                    'host': str,  # Socket only
                    'port': int   # Socket only
                }
            num_frames: 多幀平均數量(預設 5)
            warmup_frames: 預熱幀數(預設 20)
            save_debug_image: 是否儲存除錯影像(預設 False)
            apply_aruco_offset: 是否應用ArUco offset校正(預設 True)
            annotate_full_image: 是否在 full image 標註 ROI 框（預設 True）

        Returns:
            Tuple[dict, np.ndarray, np.ndarray]: 檢測結果、完整影像、ROI影像
                - dict: 檢測結果
                    {
                        "color": str,  # 顏色名稱
                        "brightness_level": int,  # 0-100%
                        "confidence": float,  # 0.0-1.0
                        "raw_brightness": float,  # 0-255
                        "aruco_offset": [float, float]  # ArUco offset (如有應用)
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
            raise ValueError("image_source_manager 未設定,請先初始化")

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

            # 4. 動態ArUco offset計算 (新增功能)
            offset_x, offset_y = 0.0, 0.0
            has_aruco_offset = False  # 標記是否應用了ArUco offset
            # Runtime ArUco offset 校正
            if apply_aruco_offset and 'aruco_markers' in roi_config:
                try:
                    offset_x, offset_y = self._calculate_aruco_offset(
                        avg_frame, 
                        roi_config['aruco_markers']
                    )
                    has_aruco_offset = True
                except Exception as e:
                    logger.warning(f"ArUco offset計算失敗: {e}, 使用原始ROI座標")
                    offset_x, offset_y = 0.0, 0.0
            
            if has_aruco_offset and (offset_x != 0.0 or offset_y != 0.0):
                logger.info(f"應用ArUco offset校正: ({offset_x:.1f}, {offset_y:.1f}) 像素")

            # 5. 提取 ROI (應用offset)
            # 處理roi_config結構相容性: 
            # - 新格式v4.2.0+: roi_config = {'roi': {...}, 'aruco_markers': [...]}
            # - 舊格式v4.1.x: roi_config = {'x': ..., 'y': ..., 'width': ..., 'height': ...}
            if 'roi' in roi_config:
                # 新格式: 完整vision配置
                roi = roi_config['roi']
            else:
                # 舊格式: 直接是roi座標 (向後相容)
                roi = roi_config
            
            x = int(roi['x'] + offset_x)
            y = int(roi['y'] + offset_y)
            w, h = roi['width'], roi['height']
            
            # 確保ROI在影像範圍內
            x = max(0, min(x, avg_frame.shape[1] - w))
            y = max(0, min(y, avg_frame.shape[0] - h))
            
            roi_image = avg_frame[y:y+h, x:x+w]

            # 6. 檢測色彩
            color, conf, hsv_mean = self._detect_color_hsv(roi_image)

            # 7. 檢測亮度
            brightness_level, brightness_value = self._detect_brightness(roi_image)

            # 8. 儲存除錯影像(如果需要)
            if save_debug_image:
                debug_dir = Path("output/debug_images")
                debug_dir.mkdir(parents=True, exist_ok=True)

                import time
                timestamp = time.strftime("%Y%m%d-%H%M%S")

                # 準備要儲存的 full image
                image_to_save = avg_frame
                
                # 標註 ROI (如果啟用)
                if annotate_full_image:
                    roi_list = [{
                        'name': button_id,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'brightness': brightness_value,
                        'color': color
                    }]
                    image_to_save = self._draw_roi_annotations(avg_frame, roi_list)
                    logger.debug("已在 full image 標註 ROI")

                # 儲存完整影像 (含標註)
                full_debug_path = debug_dir / f"{button_id}_{timestamp}_full.jpg"
                cv2.imwrite(str(full_debug_path), image_to_save)
                logger.debug(f"完整影像已儲存: {full_debug_path}")

                # 儲存 ROI 影像
                roi_debug_path = debug_dir / f"{button_id}_{timestamp}_roi.jpg"
                cv2.imwrite(str(roi_debug_path), roi_image)
                logger.debug(f"ROI 影像已儲存: {roi_debug_path}")

            # 9. 組合結果
            result = {
                "color": color,
                "brightness_level": brightness_level,
                "confidence": conf,
                "raw_brightness": brightness_value
            }
            
            # 如果有應用ArUco offset,記錄在結果中
            if offset_x != 0.0 or offset_y != 0.0:
                result["aruco_offset"] = [offset_x, offset_y]

            logger.info(f"按鈕 {button_id} 檢測完成: 顏色={color}, 亮度={brightness_level}%, 信心度={conf:.2f}")
            return result, avg_frame, roi_image

        except Exception as e:
            logger.error(f"按鈕檢測失敗 ({button_id}): {e}")
            raise RuntimeError(f"檢測失敗: {e}")

    def _detect_aruco_markers(self, image: np.ndarray) -> List[Dict]:
        """檢測影像中的ArUco markers
        
        Args:
            image: BGR格式的輸入影像
            
        Returns:
            List[Dict]: 檢測到的markers列表,每個marker包含:
                {
                    'id': int,
                    'center': [float, float],
                    'corners': [[x, y], ...]
                }
        
        Example:
            >>> markers = analyzer._detect_aruco_markers(image)
            >>> if markers:
            >>>     print(f"檢測到 {len(markers)} 個ArUco markers")
        """
        try:
            # 使用OpenCV 4.7+ 的ArUco API
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
            parameters = aruco.DetectorParameters()
            detector = aruco.ArucoDetector(aruco_dict, parameters)
            
            # 檢測markers
            corners, ids, _ = detector.detectMarkers(image)
            
            markers = []
            if corners is not None and len(corners) > 0:
                for i, corner in enumerate(corners):
                    marker_id = int(ids[i][0]) if ids is not None and len(ids) > i else i
                    
                    # 計算中心點
                    center = np.mean(corner[0], axis=0)
                    
                    marker_info = {
                        'id': marker_id,
                        'center': [float(center[0]), float(center[1])],
                        'corners': corner[0].tolist()
                    }
                    markers.append(marker_info)
                    
                logger.debug(f"檢測到ArUco marker ID={marker_id}, center={marker_info['center']}")
            else:
                logger.debug("未檢測到任何ArUco markers")
                
            return markers
            
        except Exception as e:
            logger.warning(f"ArUco檢測失敗: {e}")
            return []

    def _calculate_aruco_offset(
        self, 
        image: np.ndarray, 
        reference_markers: List[Dict],
        min_common_markers: int = 1  # 修改預設值為 1，提高容錯
    ) -> Tuple[float, float]:
        """計算 ArUco markers 的位置偏移量
        
        功能強化 (v4.3.0):
        1. 支援雙 STag 中心定位邏輯 (自動計算兩點平均偏移)
        2. 增加 STag 正向檢查 (Orientation Check)
        
        Args:
            image: BGR 格式的輸入影像
            reference_markers: 參考 markers 列表
            min_common_markers: 最小共同 markers 數量
            
        Returns:
            Tuple[float, float]: (offset_x, offset_y)
        """
        try:
            # 1. 檢測當前影像中的 markers
            current_markers = self._detect_aruco_markers(image)
            
            if not current_markers:
                logger.debug("當前影像未檢測到 ArUco markers, 使用原始 ROI 座標")
                return 0.0, 0.0
            
            # 2. 建立映射
            current_dict = {m['id']: m for m in current_markers}
            reference_dict = {m['id']: m for m in reference_markers}
            
            # 3. 找出共同 ID
            common_ids = set(current_dict.keys()) & set(reference_dict.keys())
            
            if len(common_ids) < min_common_markers:
                logger.warning(
                    f"共同 markers 數量不足 ({len(common_ids)}/{min_common_markers}), "
                    f"使用原始 ROI 座標"
                )
                return 0.0, 0.0
            
            # 4. [新增] STag 正向檢查 (Orientation Check)
            # 檢查每個 marker 的旋轉角度
            for marker_id in common_ids:
                marker = current_dict[marker_id]
                corners = marker['corners'] # [TL, TR, BR, BL]
                
                # 計算頂邊向量 (TL -> TR)
                tl, tr = corners[0], corners[1]
                vector_x = tr[0] - tl[0]
                vector_y = tr[1] - tl[1]
                
                # 計算角度 (與水平軸夾角)
                angle_deg = np.degrees(np.arctan2(vector_y, vector_x))
                
                # 判斷是否"正向" (容許 ±30 度傾斜)
                # 假設相機與面板應該是大致水平對齊的
                if abs(angle_deg) > 30:
                    logger.warning(f"⚠️ Marker {marker_id} 方向異常: {angle_deg:.1f} 度 (非正向)")
                else:
                    logger.debug(f"Marker {marker_id} 方向正常: {angle_deg:.1f} 度")

            # 5. 計算偏移量
            # 對於雙 STag (Light1 等)，計算平均偏移量等同於計算中點的偏移量
            # Mean(Current) - Mean(Ref) = Mean(Offset)
            offsets_x = []
            offsets_y = []
            
            log_msg = "ArUco Offset 詳細資訊:\n"
            
            for marker_id in common_ids:
                curr_center = current_dict[marker_id]['center']
                ref_center = reference_dict[marker_id]['center']
                
                offset_x = curr_center[0] - ref_center[0]
                offset_y = curr_center[1] - ref_center[1]
                
                offsets_x.append(offset_x)
                offsets_y.append(offset_y)
                
                log_msg += f"  - Marker {marker_id}: 偏移 ({offset_x:.1f}, {offset_y:.1f})\n"
                
            avg_offset_x = float(np.mean(offsets_x))
            avg_offset_y = float(np.mean(offsets_y))
            
            # [新增] 針對雙 STag 的特殊 Log
            if len(common_ids) == 2:
                logger.info(f"✅ 檢測到雙 STag (ID: {list(common_ids)})，使用雙點幾何中心定位")
                
            logger.debug(log_msg)
            
            logger.info(
                f"ArUco 校正結果: 平均偏移 ({avg_offset_x:.1f}, {avg_offset_y:.1f}) px, "
                f"參考點數量: {len(common_ids)}"
            )
            
            return avg_offset_x, avg_offset_y
            
        except Exception as e:
            logger.error(f"計算 ArUco offset 失敗: {e}")
            import traceback
            traceback.print_exc()
            return 0.0, 0.0

    def _draw_roi_annotations(
        self,
        image: np.ndarray,
        roi_list: List[Dict],
        show_brightness: bool = True
    ) -> np.ndarray:
        """在影像上繪製 ROI 標註
        
        Args:
            image: BGR 格式的輸入影像
            roi_list: ROI 列表,每個項目包含:
                {
                    'name': str,          # ROI 名稱 (例如: "light1", "Level1 燈泡 1")
                    'x': int,             # ROI 左上角 x 座標
                    'y': int,             # ROI 左上角 y 座標
                    'width': int,         # ROI 寬度
                    'height': int,        # ROI 高度
                    'brightness': float,  # 亮度值 (可選)
                    'is_on': bool,        # 燈光是否開啟 (可選,用於顏色編碼)
                    'color': str          # 顏色名稱 (可選,用於按鈕檢測)
                }
            show_brightness: 是否顯示亮度數值 (預設 True)
            
        Returns:
            np.ndarray: 標註後的影像 (BGR)
            
        Example:
            >>> roi_list = [
            ...     {'name': 'light1', 'x': 100, 'y': 100, 'width': 50, 'height': 50, 
            ...      'brightness': 180.5, 'is_on': True},
            ...     {'name': 'light2', 'x': 200, 'y': 100, 'width': 50, 'height': 50, 
            ...      'brightness': 30.2, 'is_on': False}
            ... ]
            >>> annotated = analyzer._draw_roi_annotations(image, roi_list)
        """
        # 複製影像以避免修改原始影像
        annotated = image.copy()
        
        for roi_info in roi_list:
            x = roi_info['x']
            y = roi_info['y']
            w = roi_info['width']
            h = roi_info['height']
            name = roi_info.get('name', 'Unknown')
            
            # 取得檢測結果
            brightness = roi_info.get('brightness')
            is_on = roi_info.get('is_on')
            color_name = roi_info.get('color')
            
            # 根據狀態選擇顏色
            # - 綠色 (0, 255, 0): 燈開啟 或 按鈕亮度高
            # - 紅色 (0, 0, 255): 燈關閉 或 按鈕亮度低
            # - 藍色 (255, 0, 0): 有顏色資訊時使用藍色框
            # - 白色 (255, 255, 255): 預設顏色
            if is_on is not None:
                box_color = (0, 255, 0) if is_on else (0, 0, 255)
            elif color_name is not None:
                box_color = (255, 0, 0)  # 按鈕檢測用藍色
            else:
                box_color = (255, 255, 255)  # 預設白色
            
            # 繪製 ROI 矩形框 (線寬 6 - 加粗以更明顯)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), box_color, 6)
            
            # 繪製名稱標籤 (位置: ROI 左上角內側)
            label_y = y + 25 if y + 25 < image.shape[0] else y - 5
            cv2.putText(
                annotated,
                name,
                (x + 8, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,  # 字體大小從 0.5 增加到 0.8
                box_color,
                2,    # 線寬從 1 增加到 2
                cv2.LINE_AA
            )
            
            # 顯示亮度值或顏色 (如果有)
            if show_brightness:
                info_text = None
                if brightness is not None:
                    info_text = f"{brightness:.1f}"
                elif color_name is not None:
                    info_text = color_name
                
                if info_text:
                    info_y = label_y + 25 if label_y + 25 < image.shape[0] else label_y - 20
                    cv2.putText(
                        annotated,
                        info_text,
                        (x + 8, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,  # 字體大小從 0.4 增加到 0.6
                        box_color,
                        2,    # 線寬從 1 增加到 2
                        cv2.LINE_AA
                    )
        
        logger.debug(f"已標註 {len(roi_list)} 個 ROI 區域")
        return annotated


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
