"""
IP Camera 燈光檢測 Library

提供基於 IP Camera 影像分析的燈光狀態檢測功能。

主要功能:
    - 從 IP Camera 擷取影像
    - 分析影像亮度
    - 判定燈光開關狀態
    - 支援多環境配置切換

使用範例:
    from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection

    detector = IPCamLightDetection()
    detector.connect_camera('laboratory', 'level1')
    brightness = detector.get_current_brightness()
    is_on = detector.is_light_on()

Robot Framework 使用範例:
    *** Settings ***
    Library    libraries/ipcam_light_detection/IPCamLightDetection.py

    *** Test Cases ***
    檢查燈光狀態
        連接攝影機    laboratory    level1
        ${亮度} =    取得當前亮度
        ${狀態} =    燈光是否開啟
        Should Be True    ${亮度} > 100
"""

import sys
import time
import numpy as np
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from loguru import logger

# OpenCV 導入（必需）
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.error("OpenCV 未安裝，IP Camera 功能無法使用。請執行: pip install opencv-python")
    raise ImportError("opencv-python 是必需的依賴套件")

# 支援兩種匯入方式：
# 1. 作為模組匯入: from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
# 2. 作為檔案匯入: import IPCamLightDetection
try:
    # 方式 1: 絕對匯入（作為模組）
    from config.ipcam_config import (
        get_camera_config,
        get_camera_url,
        get_brightness_threshold,
        get_connection_config,
        LIGHT_DETECTION_CONFIG
    )
except ImportError:
    # 方式 2: 將專案根目錄加入 sys.path，然後直接匯入
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # 回到專案根目錄
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from config.ipcam_config import (
        get_camera_config,
        get_camera_url,
        get_brightness_threshold,
        get_connection_config,
        LIGHT_DETECTION_CONFIG
    )


class IPCamLightDetection:
    """
    IP Camera 燈光檢測類別

    用於連接 IP Camera、擷取影像並分析燈光狀態。

    Attributes:
        environment (str): 當前環境名稱
        camera_name (str): 當前攝影機名稱
        camera_config (dict): 當前攝影機配置
        session (requests.Session): HTTP 連線 session
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self, environment: str = 'laboratory'):
        """
        初始化 IP Camera 燈光檢測器

        Args:
            environment (str): 預設環境，預設為 'laboratory'
        """
        self.environment = environment
        self.camera_name: Optional[str] = None
        self.camera_config: Optional[Dict[str, Any]] = None
        self.capture: Optional[cv2.VideoCapture] = None
        self.rtsp_url: Optional[str] = None
        self.last_image: Optional[np.ndarray] = None
        self.connection_config = get_connection_config()

        logger.info(f"初始化 IP Camera 燈光檢測器，預設環境: {environment}")

    def connect_camera(self, environment: str, camera_name: str):
        """
        連接到指定的攝影機

        Args:
            environment (str): 環境名稱 (如: 'laboratory', 'rv_vehicle')
            camera_name (str): 攝影機名稱 (如: 'level1', 'level2', 'motor')

        Raises:
            ValueError: 環境或攝影機不存在
            ConnectionError: 無法連接到 RTSP 串流

        Robot Framework 使用:
            連接攝影機    laboratory    level1
        """
        try:
            # 釋放舊的連線
            if self.capture is not None:
                self.capture.release()
                self.capture = None

            self.environment = environment
            self.camera_name = camera_name
            self.camera_config = get_camera_config(environment, camera_name)

            # 建立 RTSP URL
            self.rtsp_url = get_camera_url(environment, camera_name)

            logger.info(
                f"準備連接攝影機: {environment}/{camera_name} "
                f"(IP: {self.camera_config['ip']}, Protocol: {self.camera_config.get('protocol', 'unknown')})"
            )

            # 初始化 VideoCapture（延遲到實際擷取時）
            logger.info(f"RTSP URL: {self._get_safe_url()}")

        except ValueError as e:
            logger.error(f"連接攝影機失敗: {e}")
            raise

    def _get_safe_url(self) -> str:
        """取得隱藏密碼的安全 URL 用於日誌"""
        if not self.rtsp_url:
            return "N/A"

        # 隱藏密碼
        import re
        safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', self.rtsp_url)
        return safe_url

    def _init_capture(self) -> bool:
        """
        初始化 VideoCapture 連線

        Returns:
            bool: 連線是否成功
        """
        if self.capture is not None and self.capture.isOpened():
            return True

        if not self.rtsp_url:
            raise RuntimeError("尚未設定 RTSP URL，請先呼叫 connect_camera()")

        try:
            logger.debug(f"初始化 VideoCapture: {self._get_safe_url()}")

            # 設定 FFmpeg 選項以支援 HEVC/H.265 和 TCP 傳輸
            # 參考: https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html
            import os
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|analyzeduration;20000000|probesize;20000000'
            logger.debug("已設定 FFmpeg 選項: TCP 傳輸 + HEVC 支援")

            self.capture = cv2.VideoCapture(self.rtsp_url)

            # 設定緩衝區大小（僅保留最新幀）
            buffer_size = self.connection_config.get('rtsp_buffer_size', 1)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

            # 檢查連線是否成功
            if not self.capture.isOpened():
                logger.error("VideoCapture 初始化失敗")
                return False

            logger.info("VideoCapture 初始化成功")
            return True

        except Exception as e:
            logger.error(f"初始化 VideoCapture 失敗: {e}")
            return False

    def 連接攝影機(self, environment: str, camera_name: str):
        """連接到指定的攝影機（中文別名）"""
        return self.connect_camera(environment, camera_name)

    def capture_image(self, snapshot_path: str = "") -> np.ndarray:
        """
        從 IP Camera 擷取影像（支援 RTSP 串流）

        Args:
            snapshot_path (str): 串流路徑（可選），預設使用配置中的 stream_path

        Returns:
            np.ndarray: 影像陣列 (BGR 格式)

        Raises:
            ConnectionError: 無法連接到攝影機
            RuntimeError: 影像擷取失敗

        Robot Framework 使用:
            ${影像} =    擷取影像
            ${影像} =    擷取影像    /live1
        """
        if not self.camera_config:
            raise RuntimeError("尚未連接攝影機，請先呼叫 connect_camera()")

        retry_attempts = self.connection_config.get('retry_attempts', 3)
        retry_delay = self.connection_config.get('retry_delay', 2)
        frame_skip = self.connection_config.get('frame_skip', 3)

        # 如果指定了不同的串流路徑，重新建立連線
        if snapshot_path:
            original_url = self.rtsp_url
            self.rtsp_url = get_camera_url(self.environment, self.camera_name, snapshot_path)
            if self.capture is not None:
                self.capture.release()
                self.capture = None

        # 重試機制
        for attempt in range(retry_attempts):
            try:
                # 初始化 VideoCapture
                if not self._init_capture():
                    raise ConnectionError("無法初始化 RTSP 連線")

                logger.debug(f"正在擷取影像 (嘗試 {attempt + 1}/{retry_attempts})")

                # 跳過前幾幀以獲取最新影像
                for _ in range(frame_skip):
                    ret, _ = self.capture.read()
                    if not ret:
                        break

                # 擷取實際影像
                ret, frame = self.capture.read()

                if not ret or frame is None:
                    raise RuntimeError("無法從串流讀取影像幀")

                # 儲存影像
                self.last_image = frame
                logger.info(f"成功擷取影像: {frame.shape}")

                # 還原原始 URL（如果有更改）
                if snapshot_path and 'original_url' in locals():
                    self.rtsp_url = original_url

                return frame

            except Exception as e:
                logger.warning(f"擷取影像失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")

                # 釋放並重新連線
                if self.capture is not None:
                    self.capture.release()
                    self.capture = None

                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    # 還原原始 URL（如果有更改）
                    if snapshot_path and 'original_url' in locals():
                        self.rtsp_url = original_url
                    raise ConnectionError(f"無法從攝影機擷取影像: {e}")

        raise RuntimeError("擷取影像失敗：已達最大重試次數")

    def 擷取影像(self, snapshot_path: str = "") -> np.ndarray:
        """從 IP Camera 擷取影像（中文別名）"""
        return self.capture_image(snapshot_path)

    def calculate_brightness(self, image: Optional[np.ndarray] = None, region: str = 'center') -> float:
        """
        計算影像亮度

        Args:
            image (np.ndarray, optional): 影像陣列，若未提供則使用最後擷取的影像
            region (str): 分析區域，'center'（中心區域）或 'full'（全圖）

        Returns:
            float: 平均亮度值 (0-255)

        Raises:
            ValueError: 無影像可分析

        Robot Framework 使用:
            ${亮度} =    計算亮度    region=center
        """
        if image is None:
            if self.last_image is None:
                raise ValueError("無影像可分析，請先擷取影像")
            image = self.last_image

        # 轉換為灰階
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # 選擇分析區域
        if region == 'center':
            # 分析中心 50% 區域
            h, w = gray.shape
            center_h, center_w = h // 4, w // 4
            gray = gray[center_h:center_h*3, center_w:center_w*3]

        # 計算平均亮度
        brightness = float(np.mean(gray))
        logger.debug(f"影像亮度: {brightness:.2f} (區域: {region})")

        return brightness

    def 計算亮度(self, image: Optional[np.ndarray] = None, region: str = 'center') -> float:
        """計算影像亮度（中文別名）"""
        return self.calculate_brightness(image, region)

    def get_current_brightness(self, snapshot_path: str = "", region: str = 'center') -> float:
        """
        取得當前亮度（擷取影像並計算亮度）

        Args:
            snapshot_path (str): 串流路徑（可選）
            region (str): 分析區域

        Returns:
            float: 當前亮度值

        Robot Framework 使用:
            ${當前亮度} =    取得當前亮度
        """
        # 延遲以確保影像穩定
        capture_delay = LIGHT_DETECTION_CONFIG.get('image_processing', {}).get('capture_delay', 1.0)
        time.sleep(capture_delay)

        image = self.capture_image(snapshot_path)
        return self.calculate_brightness(image, region)

    def 取得當前亮度(self, snapshot_path: str = "", region: str = 'center') -> float:
        """取得當前亮度（中文別名）"""
        return self.get_current_brightness(snapshot_path, region)

    def is_light_on(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        """
        判定燈光是否開啟

        Args:
            brightness (float, optional): 亮度值，若未提供則擷取當前亮度
            threshold (float, optional): 亮度閾值，若未提供則使用配置中的 'bright' 閾值

        Returns:
            bool: True 表示燈光開啟，False 表示燈光關閉

        Robot Framework 使用:
            ${燈光開啟} =    燈光是否開啟
            Should Be True    ${燈光開啟}
        """
        if brightness is None:
            brightness = self.get_current_brightness()

        if threshold is None:
            threshold = get_brightness_threshold('bright')

        is_on = brightness >= threshold
        logger.info(f"燈光判定: {'開啟' if is_on else '關閉'} (亮度: {brightness:.2f}, 閾值: {threshold})")

        return is_on

    def 燈光是否開啟(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        """判定燈光是否開啟（中文別名）"""
        return self.is_light_on(brightness, threshold)

    def is_light_off(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        """
        判定燈光是否關閉

        Args:
            brightness (float, optional): 亮度值，若未提供則擷取當前亮度
            threshold (float, optional): 亮度閾值，若未提供則使用配置中的 'dark' 閾值

        Returns:
            bool: True 表示燈光關閉，False 表示燈光開啟

        Robot Framework 使用:
            ${燈光關閉} =    燈光是否關閉
            Should Be True    ${燈光關閉}
        """
        if brightness is None:
            brightness = self.get_current_brightness()

        if threshold is None:
            threshold = get_brightness_threshold('dark')

        is_off = brightness <= threshold
        logger.info(f"燈光判定: {'關閉' if is_off else '開啟'} (亮度: {brightness:.2f}, 閾值: {threshold})")

        return is_off

    def 燈光是否關閉(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        """判定燈光是否關閉（中文別名）"""
        return self.is_light_off(brightness, threshold)

    def get_light_status(self) -> Dict[str, Any]:
        """
        取得完整的燈光狀態資訊

        Returns:
            Dict[str, Any]: 包含亮度、開關狀態等資訊的字典

        Robot Framework 使用:
            ${狀態} =    取得燈光狀態
            Log    亮度: ${狀態}[brightness]
            Log    開啟: ${狀態}[is_on]
        """
        brightness = self.get_current_brightness()
        bright_threshold = get_brightness_threshold('bright')
        dark_threshold = get_brightness_threshold('dark')

        status = {
            'brightness': brightness,
            'is_on': brightness >= bright_threshold,
            'is_off': brightness <= dark_threshold,
            'bright_threshold': bright_threshold,
            'dark_threshold': dark_threshold,
            'camera': f"{self.environment}/{self.camera_name}",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.info(f"燈光狀態: {status}")
        return status

    def 取得燈光狀態(self) -> Dict[str, Any]:
        """取得完整的燈光狀態資訊（中文別名）"""
        return self.get_light_status()

    def save_last_image(self, file_path: str):
        """
        儲存最後擷取的影像

        Args:
            file_path (str): 儲存路徑

        Robot Framework 使用:
            儲存最後影像    /path/to/image.jpg
        """
        if self.last_image is None:
            raise ValueError("無影像可儲存，請先擷取影像")

        # 確保目錄存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # 使用 OpenCV 儲存
        cv2.imwrite(file_path, self.last_image)

        logger.info(f"影像已儲存至: {file_path}")

    def 儲存最後影像(self, file_path: str):
        """儲存最後擷取的影像（中文別名）"""
        return self.save_last_image(file_path)

    def wait_for_light_change(self, expected_state: str, timeout: int = 30, check_interval: float = 1.0) -> bool:
        """
        等待燈光狀態變化

        Args:
            expected_state (str): 預期狀態 'on' 或 'off'
            timeout (int): 最長等待時間（秒）
            check_interval (float): 檢查間隔（秒）

        Returns:
            bool: True 表示在時限內達到預期狀態，False 表示逾時

        Robot Framework 使用:
            ${成功} =    等待燈光變化    on    timeout=30    check_interval=1.0
            Should Be True    ${成功}
        """
        start_time = time.time()
        expected_state = expected_state.lower()

        while time.time() - start_time < timeout:
            if expected_state == 'on' and self.is_light_on():
                logger.info(f"燈光已開啟 (耗時: {time.time() - start_time:.2f} 秒)")
                return True
            elif expected_state == 'off' and self.is_light_off():
                logger.info(f"燈光已關閉 (耗時: {time.time() - start_time:.2f} 秒)")
                return True

            time.sleep(check_interval)

        logger.warning(f"等待燈光變化逾時 ({timeout} 秒)")
        return False

    def 等待燈光變化(self, expected_state: str, timeout: int = 30, check_interval: float = 1.0) -> bool:
        """等待燈光狀態變化（中文別名）"""
        return self.wait_for_light_change(expected_state, timeout, check_interval)

    def disconnect(self):
        """
        斷開攝影機連線並釋放資源

        Robot Framework 使用:
            斷開攝影機連線
        """
        if self.capture is not None:
            logger.info("釋放 VideoCapture 資源")
            self.capture.release()
            self.capture = None

    def 斷開攝影機連線(self):
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
    print("IP Camera 燈光檢測測試")
    print("=" * 60)

    try:
        detector = IPCamLightDetection()
        print("\n✅ 初始化成功")

        print("\n測試連接攝影機...")
        detector.connect_camera('laboratory', 'level1')
        print("✅ 連接成功")

        print("\n測試擷取影像...")
        try:
            image = detector.capture_image()
            print(f"✅ 影像擷取成功: {image.shape}")
        except Exception as e:
            print(f"⚠️  影像擷取失敗（可能攝影機未啟動）: {e}")

        print("\n測試亮度計算...")
        try:
            brightness = detector.get_current_brightness()
            print(f"✅ 當前亮度: {brightness:.2f}")

            is_on = detector.is_light_on(brightness)
            print(f"✅ 燈光狀態: {'開啟' if is_on else '關閉'}")

            status = detector.get_light_status()
            print(f"✅ 完整狀態: {status}")
        except Exception as e:
            print(f"⚠️  亮度計算失敗（可能攝影機未啟動）: {e}")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")

    print("\n" + "=" * 60)
