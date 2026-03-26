"""
RV 車空間擴展偵測核心模組
開發日期: 2026-03-26

提供基於 OpenCV ArUco 標籤深度的空間擴展狀態檢測功能，
適用於推斷 Slide-out 或 Awning 的實體相對位置變化。

使用方式:
    detector = IPCamExpansionDetection()
    detector.connect_for_expansion_target('slide_out_wall')
    area = detector.get_marker_area(detector.capture_image())
    print(f"目前拉伸艙標籤面積為: {area}")
"""

import time
import numpy as np
from pathlib import Path
from loguru import logger
import os

try:
    import cv2
    import cv2.aruco as aruco
except ImportError:
    logger.error("OpenCV 未安裝或未支援 ArUco，請執行: pip install opencv-contrib-python")
    raise ImportError("本模組需要 opencv-contrib-python 才能支援 ArUco 標籤解析")

from config.ipcam_config import get_space_expansion_target, get_camera_url, get_connection_config
# 引入共用的 FrameReader 確保影像穩定擷取
from libraries.ipcam_light_detection.IPCamLightDetection import FrameReader

class IPCamExpansionDetection:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self):
        self.frame_reader = None
        self.target_config = None
        self.camera_url = None

    def connect_for_expansion_target(self, target_name: str):
        """
        連線至指定的空間擴充目標所在的攝影機即時影像。
        
        Args:
            target_name (str): 目標名稱（必須存在於 config 檔中的 targets），例如 'slide_out_wall'
        """
        self.disconnect()
        self.target_config = get_space_expansion_target(target_name)
        
        env = self.target_config.get('environment', 'rv_car')
        cam = self.target_config.get('camera_name', 'cam1')
        self.camera_url = get_camera_url(env, cam)
        
        logger.info(f"準備連接攝影機 {cam} (環境: {env}) 以偵測標籤目標: {target_name}")
        connection_config = get_connection_config()
        
        # 開啟背景執行緒進行推流
        self.frame_reader = FrameReader(self.camera_url, connection_config, 'udp')
        self.frame_reader.start()

        # 等待連線
        timeout = connection_config.get('timeout', 10)
        check_interval = 0.5
        max_attempts = int(timeout / check_interval)

        for _ in range(max_attempts):
            if self.frame_reader.connected and self.frame_reader.get_frame() is not None:
                logger.info(f"成功連結該攝影機，準備開始辨識 ArUco 標籤 (dict_name: {self.target_config.get('aruco_dict')})")
                return
            time.sleep(check_interval)
            
        raise RuntimeError(f"攝影機 {cam} 連線逾時，擷取畫面失敗。")

    def capture_image(self) -> np.ndarray:
        """擷取單幀畫格"""
        if not self.frame_reader:
            raise RuntimeError("尚未連接攝影機。請呼叫 connect_for_expansion_target()")
        
        for _ in range(3):
            frame = self.frame_reader.get_frame()
            if frame is not None:
                return frame
            time.sleep(0.2)
            
        raise RuntimeError("無法從即時串流中取得影像畫格")
        
    def get_marker_area(self, image: np.ndarray) -> float:
        """
        計算 ArUco 標籤在傳入影像中的像素面積。
        利用 OpenCV findContours / contourArea 公式換算，
        此面積與鏡頭之間的實際距離呈平方反比關係。
        """
        aruco_dict_name = self.target_config.get('aruco_dict', 'DICT_4X4_50')
        dictionary = aruco.getPredefinedDictionary(getattr(aruco, aruco_dict_name))
        parameters = aruco.DetectorParameters()
        detector = aruco.ArucoDetector(dictionary, parameters)

        # 將影像轉灰階提升辨識效率
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)
        
        if ids is None:
            logger.warning("影片中無法辨識到任何 ArUco 標籤")
            return 0.0

        target_id = self.target_config['marker_id']
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id == target_id:
                # corners[i] 的形狀是 (1, 4, 2)
                pts = corners[i][0]
                area = cv2.contourArea(pts)
                logger.debug(f"成功定位目標標籤 ID {target_id}，當前計算面積為: {area:.1f} px^2")
                return area
                
        logger.warning(f"畫面中有找到其他標籤，但沒有找到指定的 target_id: {target_id}")
        return 0.0

    def verify_expansion_state(self, expected_state: str) -> bool:
        """
        驗證實體空間狀態 ('collapsed' 或 'expanded') 是否達標。
        
        此方法會比較當前的標籤面積以及 yaml 中的註冊基準值，
        符合容許值內即為驗證通過，否則觸發 AssertionError 以強制測試中斷。
        """
        if not self.target_config:
            raise RuntimeError("尚未綁定擴充測量目標，請呼叫 connect_for_expansion_target")
        
        # 對畫面分析並取得最新標籤區塊
        area = self.get_marker_area(self.capture_image())
        if area == 0.0:
            raise AssertionError("無法在畫面中找到用於辨識擴充深度的實體標籤，請檢查是否遮蔽")

        threshold_ratio = self.target_config.get('threshold_percentage', 15) / 100.0

        if expected_state.lower() == 'collapsed':
            baseline = self.target_config['collapsed_area']
        elif expected_state.lower() == 'expanded':
            baseline = self.target_config['expanded_area']
        else:
            raise ValueError(f"不支援的擴展狀態描述: {expected_state} (應傳入 collapsed 或 expanded)")

        # 計算落差比例
        diff_ratio = abs(area - baseline) / baseline
        
        if diff_ratio <= threshold_ratio:
            logger.info(f"驗證通過：RV 車空間狀態相符為 '{expected_state}' (當前面積 {area:.1f}, 基準 {baseline})")
            return True
        else:
            raise AssertionError(f"RV 車的目標物件未達 '{expected_state}' 狀態極限：\n"
                                 f"落差過大！當前計算面積 {area:.1f}，預期基準值為 {baseline}。\n"
                                 f"(兩者相差 {diff_ratio*100:.1f}%，超過了設定的容許誤差 {threshold_ratio*100:.1f}%)")

    def disconnect(self):
        """中斷並釋放連接端"""
        if self.frame_reader:
            self.frame_reader.stop()
            self.frame_reader = None

    def __del__(self):
        try:
            self.disconnect()
        except Exception:
            pass
