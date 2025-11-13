"""
多燈號陣列檢測 Library

提供基於 IP Camera 影像分析的多燈號陣列檢測功能，支援紙箱分隔的燈泡陣列。

主要功能:
    - 多燈號 ROI 區域管理
    - 同時計算多個燈泡的亮度
    - 判定每個燈泡的明滅狀態與強弱等級
    - 支援燈泡陣列視覺化與調試

使用範例:
    from libraries.ipcam_light_detection import MultiLightDetection

    detector = MultiLightDetection('default_array')
    detector.connect_array_camera()
    results = detector.detect_all_lights()
    print(f"燈泡 A1 亮度: {results['0_0']['brightness']}")

Robot Framework 使用範例:
    *** Settings ***
    Library    libraries/ipcam_light_detection/MultiLightDetection.py

    *** Test Cases ***
    檢查燈泡陣列狀態
        連接陣列攝影機    default_array
        ${結果} =    偵測所有燈號
        Log Dictionary    ${結果}
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from loguru import logger

# OpenCV 導入
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.error("OpenCV 未安裝，多燈號檢測功能無法使用")
    raise ImportError("opencv-python 是必需的依賴套件")

# 從 config 導入配置
try:
    from config.ipcam_config import load_config
except ImportError:
    logger.error("無法導入 ipcam_config，請確認 PYTHONPATH 設定正確")
    raise

# 從單燈號檢測繼承基礎功能
from .IPCamLightDetection import IPCamLightDetection


class MultiLightDetection:
    """
    多燈號陣列檢測類別

    用於同時檢測多個燈泡的明滅狀態，支援紙箱分隔的燈泡陣列。

    Attributes:
        array_name (str): 陣列配置名稱
        array_config (dict): 陣列配置資訊
        base_detector (IPCamLightDetection): 基礎 IP Camera 檢測器
        roi_regions (dict): ROI 區域字典
        latest_results (dict): 最新檢測結果
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self, array_name: str = 'default_array'):
        """
        初始化多燈號陣列檢測器

        Args:
            array_name (str): 陣列配置名稱，預設為 'default_array'
        """
        self.array_name = array_name
        self.array_config: Optional[Dict[str, Any]] = None
        self.base_detector: Optional[IPCamLightDetection] = None
        self.roi_regions: Dict[str, Dict[str, Any]] = {}
        self.latest_results: Dict[str, Dict[str, Any]] = {}
        self.current_image: Optional[np.ndarray] = None

        # 載入陣列配置
        self._load_array_config()

        logger.info(f"初始化多燈號陣列檢測器: {array_name}")

    def _load_array_config(self):
        """載入陣列配置文件"""
        try:
            config = load_config()
            multi_arrays = config.get('multi_light_arrays', {})

            if self.array_name not in multi_arrays:
                available = ', '.join(multi_arrays.keys())
                raise ValueError(
                    f"陣列配置 '{self.array_name}' 不存在。"
                    f"可用配置: {available}"
                )

            self.array_config = multi_arrays[self.array_name]
            logger.info(f"已載入陣列配置: {self.array_name}")

            # 建立 ROI 區域
            self._build_roi_regions()

        except Exception as e:
            logger.error(f"載入陣列配置失敗: {e}")
            raise

    def _build_roi_regions(self):
        """建立 ROI 區域字典"""
        layout = self.array_config.get('layout', {})
        roi_detection = self.array_config.get('roi_detection', {})
        manual_roi = self.array_config.get('manual_roi', [])
        light_configs = self.array_config.get('light_configs', {})

        method = roi_detection.get('method', 'manual')
        margin_ratio = roi_detection.get('margin_ratio', 0.05)

        if method == 'manual':
            # 使用手動定義的 ROI
            for roi_data in manual_roi:
                row, col, x_min, y_min, x_max, y_max = roi_data
                key = f"{row}_{col}"

                # 套用邊界內縮
                x_range = x_max - x_min
                y_range = y_max - y_min
                x_min += x_range * margin_ratio
                y_min += y_range * margin_ratio
                x_max -= x_range * margin_ratio
                y_max -= y_range * margin_ratio

                # 取得個別燈泡配置
                light_config = light_configs.get(key, {})

                self.roi_regions[key] = {
                    'row': row,
                    'col': col,
                    'name': light_config.get('name', f"燈泡_{row}{col}"),
                    'roi_relative': [x_min, y_min, x_max, y_max],
                    'roi_absolute': None,  # 將在擷取影像後計算
                    'bright_threshold': light_config.get('bright_threshold', 150),
                    'dark_threshold': light_config.get('dark_threshold', 50)
                }

            logger.info(f"已建立 {len(self.roi_regions)} 個 ROI 區域")

        else:
            # TODO: 實作自動 ROI 偵測
            raise NotImplementedError("自動 ROI 偵測尚未實作")

    def connect_array_camera(self):
        """
        連接陣列配置中指定的攝影機

        Raises:
            ValueError: 陣列配置缺少必要資訊
            ConnectionError: 無法連接到攝影機

        Robot Framework 使用:
            連接陣列攝影機    default_array
        """
        if not self.array_config:
            raise ValueError("陣列配置尚未載入")

        environment = self.array_config.get('environment')
        camera = self.array_config.get('camera')

        if not environment or not camera:
            raise ValueError("陣列配置缺少 environment 或 camera 資訊")

        # 建立基礎檢測器
        self.base_detector = IPCamLightDetection(environment)
        self.base_detector.connect_camera(environment, camera)

        logger.info(f"已連接陣列攝影機: {environment}/{camera}")

    def 連接陣列攝影機(self, array_name: Optional[str] = None):
        """
        連接陣列配置中指定的攝影機（中文別名）

        Args:
            array_name (str, optional): 陣列配置名稱，若指定則重新載入配置
        """
        if array_name and array_name != self.array_name:
            self.array_name = array_name
            self._load_array_config()

        return self.connect_array_camera()

    def _update_absolute_roi(self, image_shape: Tuple[int, int]):
        """
        根據影像尺寸更新絕對 ROI 座標

        Args:
            image_shape (Tuple[int, int]): 影像形狀 (height, width)
        """
        height, width = image_shape[:2]

        for key, roi_info in self.roi_regions.items():
            x_min, y_min, x_max, y_max = roi_info['roi_relative']

            # 轉換為絕對座標（像素）
            abs_x_min = int(x_min * width)
            abs_y_min = int(y_min * height)
            abs_x_max = int(x_max * width)
            abs_y_max = int(y_max * height)

            roi_info['roi_absolute'] = [abs_x_min, abs_y_min, abs_x_max, abs_y_max]

    def capture_array_image(self) -> np.ndarray:
        """
        擷取陣列影像

        Returns:
            np.ndarray: 影像陣列

        Raises:
            RuntimeError: 尚未連接攝影機

        Robot Framework 使用:
            ${影像} =    擷取陣列影像
        """
        if not self.base_detector:
            raise RuntimeError("尚未連接攝影機，請先呼叫 connect_array_camera()")

        image = self.base_detector.capture_image()
        self.current_image = image

        # 更新絕對 ROI 座標
        self._update_absolute_roi(image.shape)

        logger.info(f"已擷取陣列影像: {image.shape}")
        return image

    def 擷取陣列影像(self) -> np.ndarray:
        """擷取陣列影像（中文別名）"""
        return self.capture_array_image()

    def calculate_light_brightness(self, light_key: str, image: Optional[np.ndarray] = None) -> float:
        """
        計算單個燈泡的亮度

        Args:
            light_key (str): 燈泡鍵值（格式：row_col，如 "0_0"）
            image (np.ndarray, optional): 影像陣列，若未提供則使用最新影像

        Returns:
            float: 平均亮度值 (0-255)

        Raises:
            ValueError: 燈泡鍵值不存在或無影像可分析

        Robot Framework 使用:
            ${亮度} =    計算燈泡亮度    0_0
        """
        if light_key not in self.roi_regions:
            raise ValueError(f"燈泡鍵值 '{light_key}' 不存在")

        if image is None:
            if self.current_image is None:
                raise ValueError("無影像可分析，請先擷取影像")
            image = self.current_image

        roi_info = self.roi_regions[light_key]
        x_min, y_min, x_max, y_max = roi_info['roi_absolute']

        # 裁切 ROI 區域
        roi = image[y_min:y_max, x_min:x_max]

        # 轉換為灰階
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi

        # 計算平均亮度
        brightness = float(np.mean(gray))

        logger.debug(f"燈泡 {roi_info['name']} ({light_key}) 亮度: {brightness:.2f}")
        return brightness

    def 計算燈泡亮度(self, light_key: str, image: Optional[np.ndarray] = None) -> float:
        """計算單個燈泡的亮度（中文別名）"""
        return self.calculate_light_brightness(light_key, image)

    def get_brightness_level(self, brightness: float) -> str:
        """
        根據亮度值判定亮度等級

        Args:
            brightness (float): 亮度值 (0-255)

        Returns:
            str: 亮度等級（'off', 'dim', 'medium', 'bright'）

        Robot Framework 使用:
            ${等級} =    取得亮度等級    ${亮度值}
        """
        brightness_levels = self.array_config.get('brightness_levels', {
            'off': [0, 50],
            'dim': [51, 100],
            'medium': [101, 180],
            'bright': [181, 255]
        })

        for level, (min_val, max_val) in brightness_levels.items():
            if min_val <= brightness <= max_val:
                return level

        return 'unknown'

    def 取得亮度等級(self, brightness: float) -> str:
        """根據亮度值判定亮度等級（中文別名）"""
        return self.get_brightness_level(brightness)

    def detect_single_light(self, light_key: str, image: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        偵測單個燈泡的完整狀態

        Args:
            light_key (str): 燈泡鍵值
            image (np.ndarray, optional): 影像陣列

        Returns:
            Dict[str, Any]: 包含亮度、狀態、等級等資訊的字典

        Robot Framework 使用:
            ${狀態} =    偵測單一燈號    0_0
            Log    亮度: ${狀態}[brightness]
            Log    是否開啟: ${狀態}[is_on]
        """
        roi_info = self.roi_regions[light_key]
        brightness = self.calculate_light_brightness(light_key, image)

        bright_threshold = roi_info['bright_threshold']
        dark_threshold = roi_info['dark_threshold']
        level = self.get_brightness_level(brightness)

        result = {
            'light_key': light_key,
            'row': roi_info['row'],
            'col': roi_info['col'],
            'name': roi_info['name'],
            'brightness': brightness,
            'brightness_level': level,
            'is_on': brightness >= bright_threshold,
            'is_off': brightness <= dark_threshold,
            'bright_threshold': bright_threshold,
            'dark_threshold': dark_threshold,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.debug(f"燈泡 {roi_info['name']} 狀態: {result}")
        return result

    def 偵測單一燈號(self, light_key: str, image: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """偵測單個燈泡的完整狀態（中文別名）"""
        return self.detect_single_light(light_key, image)

    def detect_all_lights(self, capture_new_image: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        偵測所有燈泡的狀態

        Args:
            capture_new_image (bool): 是否擷取新影像，預設為 True

        Returns:
            Dict[str, Dict[str, Any]]: 所有燈泡的狀態字典，鍵值為 light_key

        Robot Framework 使用:
            ${所有狀態} =    偵測所有燈號
            Log Dictionary    ${所有狀態}
        """
        if capture_new_image:
            self.capture_array_image()

        results = {}
        for light_key in self.roi_regions.keys():
            results[light_key] = self.detect_single_light(light_key, self.current_image)

        self.latest_results = results

        # 統計摘要
        total = len(results)
        on_count = sum(1 for r in results.values() if r['is_on'])
        off_count = sum(1 for r in results.values() if r['is_off'])

        logger.info(
            f"陣列偵測完成: 總數={total}, 開啟={on_count}, 關閉={off_count}"
        )

        return results

    def 偵測所有燈號(self, capture_new_image: bool = True) -> Dict[str, Dict[str, Any]]:
        """偵測所有燈泡的狀態（中文別名）"""
        return self.detect_all_lights(capture_new_image)

    def get_light_status_summary(self) -> Dict[str, Any]:
        """
        取得燈號陣列狀態摘要

        Returns:
            Dict[str, Any]: 包含統計資訊的摘要字典

        Robot Framework 使用:
            ${摘要} =    取得燈號狀態摘要
            Log    開啟數量: ${摘要}[on_count]
        """
        if not self.latest_results:
            logger.warning("尚無檢測結果，執行一次完整檢測")
            self.detect_all_lights()

        total = len(self.latest_results)
        on_count = sum(1 for r in self.latest_results.values() if r['is_on'])
        off_count = sum(1 for r in self.latest_results.values() if r['is_off'])

        # 亮度等級統計
        level_counts = {}
        for result in self.latest_results.values():
            level = result['brightness_level']
            level_counts[level] = level_counts.get(level, 0) + 1

        summary = {
            'total_lights': total,
            'on_count': on_count,
            'off_count': off_count,
            'uncertain_count': total - on_count - off_count,
            'level_counts': level_counts,
            'average_brightness': sum(r['brightness'] for r in self.latest_results.values()) / total,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        return summary

    def 取得燈號狀態摘要(self) -> Dict[str, Any]:
        """取得燈號陣列狀態摘要（中文別名）"""
        return self.get_light_status_summary()

    def save_annotated_image(self, file_path: str, show_brightness: bool = True):
        """
        儲存標註的陣列影像（標示 ROI 框和亮度值）

        Args:
            file_path (str): 儲存路徑
            show_brightness (bool): 是否顯示亮度數值

        Robot Framework 使用:
            儲存標註影像    /path/to/annotated.jpg    show_brightness=True
        """
        if self.current_image is None:
            raise ValueError("無影像可儲存，請先擷取影像")

        # 複製影像以避免修改原始影像
        annotated = self.current_image.copy()

        for light_key, roi_info in self.roi_regions.items():
            x_min, y_min, x_max, y_max = roi_info['roi_absolute']

            # 取得檢測結果
            if light_key in self.latest_results:
                result = self.latest_results[light_key]
                brightness = result['brightness']
                is_on = result['is_on']

                # 根據狀態選擇顏色（綠色=開啟，紅色=關閉）
                color = (0, 255, 0) if is_on else (0, 0, 255)
            else:
                brightness = None
                color = (255, 255, 255)

            # 繪製 ROI 矩形
            cv2.rectangle(annotated, (x_min, y_min), (x_max, y_max), color, 2)

            # 顯示燈泡名稱
            cv2.putText(
                annotated,
                roi_info['name'],
                (x_min + 5, y_min + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )

            # 顯示亮度值
            if show_brightness and brightness is not None:
                cv2.putText(
                    annotated,
                    f"{brightness:.1f}",
                    (x_min + 5, y_min + 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    color,
                    1
                )

        # 確保目錄存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # 儲存影像
        cv2.imwrite(file_path, annotated)
        logger.info(f"標註影像已儲存至: {file_path}")

    def 儲存標註影像(self, file_path: str, show_brightness: bool = True):
        """儲存標註的陣列影像（中文別名）"""
        return self.save_annotated_image(file_path, show_brightness)

    def wait_for_light_pattern(
        self,
        expected_pattern: Dict[str, bool],
        timeout: int = 30,
        check_interval: float = 1.0
    ) -> bool:
        """
        等待燈號陣列符合預期模式

        Args:
            expected_pattern (Dict[str, bool]): 預期模式，鍵為 light_key，值為 True（開啟）或 False（關閉）
            timeout (int): 最長等待時間（秒）
            check_interval (float): 檢查間隔（秒）

        Returns:
            bool: True 表示在時限內達到預期模式，False 表示逾時

        使用範例:
            pattern = {'0_0': True, '0_1': False, '1_0': True}
            success = detector.wait_for_light_pattern(pattern, timeout=30)

        Robot Framework 使用:
            ${模式} =    Create Dictionary    0_0=True    0_1=False
            ${成功} =    等待燈號模式    ${模式}    timeout=30
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            results = self.detect_all_lights(capture_new_image=True)

            # 檢查是否符合預期模式
            match = True
            for light_key, expected_on in expected_pattern.items():
                if light_key not in results:
                    logger.warning(f"燈泡鍵值 '{light_key}' 不存在")
                    match = False
                    break

                actual_on = results[light_key]['is_on']
                if actual_on != expected_on:
                    match = False
                    break

            if match:
                elapsed = time.time() - start_time
                logger.info(f"燈號模式已符合預期 (耗時: {elapsed:.2f} 秒)")
                return True

            time.sleep(check_interval)

        logger.warning(f"等待燈號模式逾時 ({timeout} 秒)")
        return False

    def 等待燈號模式(
        self,
        expected_pattern: Dict[str, bool],
        timeout: int = 30,
        check_interval: float = 1.0
    ) -> bool:
        """等待燈號陣列符合預期模式（中文別名）"""
        return self.wait_for_light_pattern(expected_pattern, timeout, check_interval)

    def disconnect(self):
        """
        斷開攝影機連線並釋放資源

        Robot Framework 使用:
            斷開陣列攝影機連線
        """
        if self.base_detector:
            self.base_detector.disconnect()
            self.base_detector = None
        logger.info("已斷開陣列攝影機連線")

    def 斷開陣列攝影機連線(self):
        """斷開攝影機連線並釋放資源（中文別名）"""
        return self.disconnect()

    def __del__(self):
        """析構函數：確保資源被釋放"""
        try:
            self.disconnect()
        except:
            pass


if __name__ == "__main__":
    # 測試程式
    print("=" * 60)
    print("多燈號陣列檢測測試")
    print("=" * 60)

    try:
        detector = MultiLightDetection('default_array')
        print("\n✅ 初始化成功")

        print("\n陣列配置資訊:")
        print(f"  名稱: {detector.array_config['name']}")
        print(f"  環境: {detector.array_config['environment']}")
        print(f"  攝影機: {detector.array_config['camera']}")
        print(f"  布局: {detector.array_config['layout']['rows']}x{detector.array_config['layout']['cols']}")
        print(f"  ROI 區域數: {len(detector.roi_regions)}")

        print("\n測試連接攝影機...")
        try:
            detector.connect_array_camera()
            print("✅ 連接成功")

            print("\n測試擷取影像並偵測...")
            results = detector.detect_all_lights()

            print("\n偵測結果:")
            for light_key, result in sorted(results.items()):
                status = "開啟" if result['is_on'] else "關閉"
                print(
                    f"  {result['name']} ({light_key}): "
                    f"亮度={result['brightness']:.2f}, "
                    f"狀態={status}, "
                    f"等級={result['brightness_level']}"
                )

            print("\n統計摘要:")
            summary = detector.get_light_status_summary()
            print(f"  總燈泡數: {summary['total_lights']}")
            print(f"  開啟數量: {summary['on_count']}")
            print(f"  關閉數量: {summary['off_count']}")
            print(f"  平均亮度: {summary['average_brightness']:.2f}")
            print(f"  等級分布: {summary['level_counts']}")

            print("\n儲存標註影像...")
            output_path = "/tmp/multi_light_test.jpg"
            detector.save_annotated_image(output_path)
            print(f"✅ 標註影像已儲存: {output_path}")

        except Exception as e:
            print(f"⚠️  攝影機連接或偵測失敗（可能攝影機未啟動）: {e}")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
