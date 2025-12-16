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
import os
import contextlib

# 設定環境變數以抑制 OpenCV 和 FFmpeg 的日誌輸出
# 必須在 import cv2 之前設定
os.environ['OPENCV_LOG_LEVEL'] = 'OFF'
os.environ['OPENCV_FFMPEG_DEBUG'] = '0'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['FFREPORT'] = 'file=/dev/null:level=0'  # 抑制 FFmpeg stderr 輸出

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


import threading

class FrameReader(threading.Thread):
    """
    背景執行緒影像讀取器
    持續從 RTSP 串流讀取影像，確保隨時能取得最新的一幀
    """
    def __init__(self, rtsp_url: str, connection_config: dict, transport: str = 'tcp'):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.connection_config = connection_config
        self.transport = transport
        self.latest_frame = None
        self.running = False
        self.lock = threading.Lock()
        self.daemon = True
        self.connected = False

    def run(self):
        self.running = True
        self._read_loop()

    def _read_loop(self):
        # 設定 FFmpeg 選項
        # 加入 loglevel;quiet 以抑制 FFmpeg 輸出
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = f'rtsp_transport;{self.transport}|analyzeduration;10000000|probesize;10000000|loglevel;quiet'
        
        # 再次確保日誌級別被設定 (雖然模組層級已設定，但 FrameReader 可能在不同 context)
        try:
            cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)
        except AttributeError:
            pass # 舊版 OpenCV 可能不支援
        
        while self.running:
            try:
                print(f"FrameReader: Opening RTSP stream with transport={self.transport}")
                print(f"FrameReader: Env Options={os.environ.get('OPENCV_FFMPEG_CAPTURE_OPTIONS')}")
                
                cap = cv2.VideoCapture(self.rtsp_url)
                buffer_size = self.connection_config.get('rtsp_buffer_size', 1)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

                if not cap.isOpened():
                    logger.error("FrameReader: 無法開啟 RTSP 串流，5秒後重試...")
                    time.sleep(5)
                    continue

                logger.info("FrameReader: RTSP 連線建立，開始暖身...")
                
                # 暖身
                warmup_frames = 30
                for _ in range(warmup_frames):
                    cap.read()
                
                logger.info("FrameReader: 暖身完成，開始持續讀取影像")
                self.connected = True

                while self.running and cap.isOpened():
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        with self.lock:
                            self.latest_frame = frame
                    else:
                        logger.warning("FrameReader: 讀取失敗或影像為空，嘗試重新連線...")
                        break
                
                self.connected = False
                cap.release()
                
            except Exception as e:
                logger.error(f"FrameReader 發生錯誤: {e}")
                self.connected = False
                time.sleep(2)

    def get_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def stop(self):
        self.running = False
        self.join(timeout=2.0)


class IPCamLightDetection:
    """
    IP Camera 燈光檢測類別
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self, environment: str = 'taipei_lab'):
        self.environment = environment
        self.camera_name: Optional[str] = None
        self.camera_config: Optional[Dict[str, Any]] = None
        self.frame_reader: Optional[FrameReader] = None
        self.rtsp_url: Optional[str] = None
        self.last_image: Optional[np.ndarray] = None
        self.connection_config = get_connection_config()

        logger.info(f"初始化 IP Camera 燈光檢測器，預設環境: {environment}")

    def connect_camera(self, environment: str, camera_name: str):
        try:
            self.disconnect()

            self.environment = environment
            self.camera_name = camera_name
            self.camera_config = get_camera_config(environment, camera_name)
            self.rtsp_url = get_camera_url(environment, camera_name)

            logger.info(f"準備連接攝影機: {environment}/{camera_name}")
            logger.info(f"RTSP URL: {self._get_safe_url()}")

            # 取得傳輸協定設定 (預設 udp)
            primary_transport = self.camera_config.get('transport', 'udp')
            # 決定 fallback 順序
            transports = [primary_transport]
            if primary_transport == 'udp':
                transports.append('tcp')
            else:
                transports.append('udp')

            last_error = None
            
            for transport in transports:
                logger.info(f"嘗試使用 {transport.upper()} 協定連接...")
                try:
                    self._connect_with_transport(transport)
                    logger.info(f"成功使用 {transport.upper()} 協定建立連線")
                    return
                except Exception as e:
                    logger.warning(f"使用 {transport.upper()} 連接失敗: {e}")
                    last_error = e
                    self.disconnect() # 確保清理資源
            
            raise RuntimeError(f"無法連接到攝影機 {camera_name} (所有嘗試皆失敗). 最後錯誤: {last_error}")

        except ValueError as e:
            logger.error(f"連接攝影機失敗: {e}")
            raise

    def _connect_with_transport(self, transport: str):
        """
        嘗試使用指定傳輸協定連接
        """
        # 啟動背景讀取執行緒
        self.frame_reader = FrameReader(self.rtsp_url, self.connection_config, transport)
        self.frame_reader.start()
        
        # 等待連線建立 (最多等待 10 秒)
        # 可以從 config 讀取 timeout，這裡先維持原本邏輯
        timeout = self.connection_config.get('timeout', 10)
        check_interval = 0.5
        max_attempts = int(timeout / check_interval)

        for _ in range(max_attempts):
            if self.frame_reader.connected and self.frame_reader.get_frame() is not None:
                return
            time.sleep(check_interval)
        
        raise RuntimeError("RTSP 連線逾時")

    def _get_safe_url(self) -> str:
        if not self.rtsp_url:
            return "N/A"
        import re
        safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', self.rtsp_url)
        return safe_url

    def capture_image(self, snapshot_path: str = "") -> np.ndarray:
        if not self.frame_reader:
             raise RuntimeError("尚未連接攝影機，請先呼叫 connect_camera()")

        if snapshot_path:
            logger.warning("使用 snapshot_path 時將暫時不使用背景執行緒 (尚未實作完整支援)")
            # 這裡可以實作臨時的單次擷取邏輯，但目前先忽略，假設都使用主串流

        # 直接從背景執行緒取得最新影像
        frame = self.frame_reader.get_frame()
        
        if frame is None:
            # 嘗試重試幾次
            for i in range(5):
                time.sleep(0.2)
                frame = self.frame_reader.get_frame()
                if frame is not None:
                    break
        
        if frame is None:
            raise RuntimeError("無法從背景執行緒取得影像 (可能是連線中斷或尚未建立)")

        self.last_image = frame
        logger.info(f"成功取得最新影像: {frame.shape}")
        return frame

    def disconnect(self):
        if self.frame_reader:
            logger.info("停止 FrameReader 背景執行緒...")
            self.frame_reader.stop()
            self.frame_reader = None

    # ... (保留其他方法如 calculate_brightness, is_light_on 等，不需要修改) ...
    
    def 連接攝影機(self, environment: str, camera_name: str):
        return self.connect_camera(environment, camera_name)

    def 擷取影像(self, snapshot_path: str = "") -> np.ndarray:
        return self.capture_image(snapshot_path)

    def calculate_brightness(self, image: Optional[np.ndarray] = None, region: str = 'center') -> float:
        if image is None:
            if self.last_image is None:
                raise ValueError("無影像可分析，請先擷取影像")
            image = self.last_image

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        if region == 'center':
            h, w = gray.shape
            center_h, center_w = h // 4, w // 4
            gray = gray[center_h:center_h*3, center_w:center_w*3]

        brightness = float(np.mean(gray))
        logger.debug(f"影像亮度: {brightness:.2f} (區域: {region})")
        return brightness

    def 計算亮度(self, image: Optional[np.ndarray] = None, region: str = 'center') -> float:
        return self.calculate_brightness(image, region)

    def get_current_brightness(self, snapshot_path: str = "", region: str = 'center') -> float:
        capture_delay = LIGHT_DETECTION_CONFIG.get('image_processing', {}).get('capture_delay', 1.0)
        time.sleep(capture_delay)
        image = self.capture_image(snapshot_path)
        return self.calculate_brightness(image, region)

    def 取得當前亮度(self, snapshot_path: str = "", region: str = 'center') -> float:
        return self.get_current_brightness(snapshot_path, region)

    def is_light_on(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        if brightness is None:
            brightness = self.get_current_brightness()
        if threshold is None:
            threshold = get_brightness_threshold('bright')
        is_on = brightness >= threshold
        logger.info(f"燈光判定: {'開啟' if is_on else '關閉'} (亮度: {brightness:.2f}, 閾值: {threshold})")
        return is_on

    def 燈光是否開啟(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        return self.is_light_on(brightness, threshold)

    def is_light_off(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        if brightness is None:
            brightness = self.get_current_brightness()
        if threshold is None:
            threshold = get_brightness_threshold('dark')
        is_off = brightness <= threshold
        logger.info(f"燈光判定: {'關閉' if is_off else '開啟'} (亮度: {brightness:.2f}, 閾值: {threshold})")
        return is_off

    def 燈光是否關閉(self, brightness: Optional[float] = None, threshold: Optional[float] = None) -> bool:
        return self.is_light_off(brightness, threshold)

    def get_light_status(self) -> Dict[str, Any]:
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
        return self.get_light_status()

    def draw_roi(self, image: np.ndarray, roi: Dict[str, int], color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        x, y, w, h = roi['x'], roi['y'], roi['width'], roi['height']
        return cv2.rectangle(image.copy(), (x, y), (x + w, y + h), color, thickness)

    def crop_roi(self, image: np.ndarray, roi: Dict[str, int]) -> np.ndarray:
        x, y, w, h = roi['x'], roi['y'], roi['width'], roi['height']
        return image[y:y+h, x:x+w]

    def save_image_with_roi(self, file_path: str, roi: Dict[str, int]):
        if self.last_image is None:
            raise ValueError("無影像可儲存，請先擷取影像")
        annotated_image = self.draw_roi(self.last_image, roi)
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(file_path, annotated_image)
        logger.info(f"標註影像已儲存至: {file_path}")

    def save_cropped_roi(self, file_path: str, roi: Dict[str, int]):
        if self.last_image is None:
            raise ValueError("無影像可儲存，請先擷取影像")
        cropped_image = self.crop_roi(self.last_image, roi)
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(file_path, cropped_image)
        logger.info(f"ROI 影像已儲存至: {file_path}")

    def save_last_image(self, file_path: str):
        if self.last_image is None:
            raise ValueError("無影像可儲存，請先擷取影像")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(file_path, self.last_image)
        logger.info(f"影像已儲存至: {file_path}")

    def 儲存最後影像(self, file_path: str):
        return self.save_last_image(file_path)

    def wait_for_light_change(self, expected_state: str, timeout: int = 30, check_interval: float = 1.0) -> bool:
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
        return self.wait_for_light_change(expected_state, timeout, check_interval)

    def disconnect(self):
        if self.frame_reader:
            logger.info("停止 FrameReader 背景執行緒...")
            self.frame_reader.stop()
            self.frame_reader = None

    def 斷開攝影機連線(self):
        return self.disconnect()

    def __del__(self):
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
        detector.connect_camera('taipei_lab', 'level1')
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
