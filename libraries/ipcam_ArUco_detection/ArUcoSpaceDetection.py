"""
開發用途: 處理 IPCam 畫面中的 ArUco 標記檢測，用以計算 RV 車庫伸縮空間。
開發日期: 2026-04-02
功能: 將 ArUco 檢測邏輯封裝為支援 Robot Framework 的物件導向類別 (Class)。
使用方式: 
    from libraries.ipcam_ArUco_detection.ArUcoSpaceDetection import ArUcoSpaceDetection
    detector = ArUcoSpaceDetection()
    detector.connect_camera('rv_car', 'cam3')
    state = detector.get_current_space_state()
"""

import cv2
import numpy as np
from cv2 import aruco
import os
import time
import sys
import logging
from collections import deque

# 加入系統路徑以便匯入 config，這樣 Robot 框架就能順利找到設定
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.ipcam_config import get_camera_url

class ArUcoSpaceDetection:
    """
    IP Camera RV 車內空間檢測類別 (這就是物件導向的威力！)
    """

    # 供 Robot Framework 識別的屬性，告訴 Robot 這是一個共用的全域函式庫
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self, target_id: int = 17):
        """
        1. 打造機器 (初始化階段)
        """
        self.logger = logging.getLogger(__name__)
        
        # --- 核心關鍵：平滑與信心參數 (移植自使用者的調校) ---
        self.target_id = target_id
        self.history_size = 15       # 視窗大小
        self.move_threshold = 3500   # 觸發移動的門檻
        self.stable_threshold = 1500 # 回到穩定的緩衝門檻
        self.confidence_required = 10# 信心機制：狀態必須連續出現幾次才算數
        
        # --- 存放機器的「記憶」與「狀態」 ---
        self.area_history = deque(maxlen=self.history_size)
        self.last_stable_area = None
        self.last_state = "穩定"     # 對應到原來的 current_state
        self.pending_state = "穩定"
        self.state_count = 0
        
        # --- OpenCV 相關連線物件 ---
        self.cap = None
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters()
        
        # 相容新舊版 OpenCV 防呆機制，避免出現 AttributeError 或是 UnboundLocalError
        if hasattr(aruco, 'ArucoDetector'):
            self.aruco_detector = aruco.ArucoDetector(self.aruco_dict, self.parameters)
        else:
            self.aruco_detector = None
            
        self.logger.info(f"🚀 終極穩定 ArUco 空間追蹤器初始化完成 (Target ID: {self.target_id})")

    def connect_camera(self, environment: str = 'rv_car', camera_name: str = 'cam3'):
        """
        2. 第二步：連線按鈕 
        當被呼叫時，我們去請 YAML 提供網址，並且打開 OpenCV 串流。
        """
        try:
            # 向設定中心請求 URL
            rtsp_url = get_camera_url(environment, camera_name)
            self.logger.info(f"準備連線至攝影機 {environment}/{camera_name}...")
            
            # 設定連線協定 (完全移植您腳本原本的 TCP 設定)
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|stimeout;5000000|probesize;30000000|analyzeduration;30000000"
            )
            
            self.cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            if not self.cap.isOpened():
                raise RuntimeError(f"❌ 無法開啟串流 (URL 錯誤或網路不通)")
                
            self.logger.info("✅ 攝影機連線成功！")
        except Exception as e:
            self.logger.error(f"連線攝影機失敗: {e}")
            raise

    # 👇 Robot Framework 使用的中文接口 (就像給 Robot 一個中文快捷鍵)
    def 連接攝影機(self, environment: str, camera_name: str):
        self.connect_camera(environment, camera_name)

    def get_current_space_state(self) -> str:
        """
        3. 第三步：狀態查詢按鈕
        加入了 deque 平均數與 confidence 連續計數的高階防抖邏輯！
        """
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError("攝影機尚未連線，請先呼叫 connect_camera()")

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.logger.warning("取得影像失敗，回傳前次狀態。")
            return self.last_state

        # 進行標籤檢測 (新舊版 OpenCV 安全寫法)
        if hasattr(self, 'aruco_detector') and self.aruco_detector is not None:
            corners, ids, _ = self.aruco_detector.detectMarkers(frame)
        else:
            corners, ids, _ = aruco.detectMarkers(frame, self.aruco_dict, parameters=self.parameters)
        
        if ids is not None and self.target_id in ids.flatten():
            # 找到我們的目標標籤
            idx = np.where(ids.flatten() == self.target_id)[0][0]
            curr_area = cv2.contourArea(corners[idx])
            self.area_history.append(curr_area)

            # 當收集滿足夠的歷史資料才開始判定
            if len(self.area_history) == self.history_size:
                avg_area = sum(self.area_history) / len(self.area_history)
                
                if self.last_stable_area is None:
                    self.last_stable_area = avg_area
                
                diff = avg_area - self.last_stable_area
                
                # --- 核心邏輯：信心判定 ---
                temp_state = self.last_state
                if diff > self.move_threshold:
                    temp_state = "收縮中"
                elif diff < -self.move_threshold:
                    temp_state = "外推中"
                elif abs(diff) < self.stable_threshold:
                    temp_state = "穩定"

                # 如果偵測到的臨時狀態跟目前真正的狀態不一樣，開始累積「狀態變更的信心」
                if temp_state != self.last_state:
                    if temp_state == self.pending_state:
                        self.state_count += 1
                    else:
                        self.pending_state = temp_state
                        self.state_count = 1
                    
                    # 只有連續達標 CONFIDENCE_REQUIRED 次，我們才正式公佈狀態改變
                    if self.state_count >= self.confidence_required:
                        old_state = self.last_state
                        self.last_state = temp_state
                        self.last_stable_area = avg_area  # 更新基準點
                        self.state_count = 0
                        self.logger.info(f"🔔 狀態切換： {old_state} -> {self.last_state} (Diff: {diff:.1f})")
                else:
                    self.state_count = 0  # 狀態跳回跟目前一樣，計數歸零
                
        # 即使畫面上沒有標籤，或沒有達到變更門檻，都直接回傳當下的狀態即可
        return self.last_state

    # 👇 Robot Framework 使用的中文查詢接口
    def 取得當前車內空間狀態(self) -> str:
        return self.get_current_space_state()

    def monitor_space_changes(self, duration_sec: int = 10) -> list:
        """
        4. 第四步：連續監控按鈕
        在指定的秒數內（例如 10 秒），程式會自己不斷檢查空間狀態，
        只要有人移動（收縮、外推、穩定），它就會記錄下來，最後交出一份「完整歷史報告」。
        """
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError("攝影機尚未連線，請先呼叫 connect_camera()")

        self.logger.info(f"開始連續監控空間狀態，預計監控 {duration_sec} 秒...")
        
        # 開啟這段時間內，我們先記下現在的狀態當作起點
        history = [self.last_state]
        start_time = time.time()

        # 為了避免畫面延遲 (清空舊的影像庫存)
        for _ in range(5):
            self.cap.read()

        while time.time() - start_time < duration_sec:
            # 這裡我們全速（約 30 FPS）執行狀態拉取，這樣您的 15 幀記憶與 10 次信心機制才會在此時限內快速發生效用
            current_state = self.get_current_space_state()
            
            # 如果發現狀態不一樣了（例如 穩定 -> 收縮中），就把它記進歷史名單！
            if current_state != history[-1]:
                history.append(current_state)
                
        self.logger.info(f"監控結束！這 {duration_sec} 秒內發生的所有動態為：{history}")
        return history

    # 👇 Robot Framework 使用的中文監控接口
    def 觀察並記錄空間動態(self, duration_sec: int = 10) -> list:
        return self.monitor_space_changes(duration_sec)

    def disconnect(self):
        """
        關閉攝影機連線，釋放資源 (好處是可以把記憶體還給電腦)
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("已斷開攝影機連線。")

    def 斷開攝影機連線(self):
        self.disconnect()

if __name__ == "__main__":
    # ========== 開發者測試區塊 ==========
    # 要體驗 Class 類別的「遙控器呼叫方式」，您可以直接執行這個腳本
    logging.basicConfig(level=logging.INFO)
    
    print("\n[測試開始] 初始化機器...")
    detector = ArUcoSpaceDetection(target_id=17)
    
    print("[測試連線] 按下連線按鈕...")
    # 這邊因為我們 yaml 裡面您改回 172 了，所以這裡去連 rv_car 的 cam3 就是 172
    detector.connect_camera('rv_car', 'rv_motor')
    
    print("\n[測試運作] --- 啟動連續監控功能 (30 秒) ---")
    # 這邊模擬：機器人按下「開始連續監控 30 秒」，然後去喝口水
    # 只要這 30 秒內您在鏡頭前面晃動標籤，它都會通通錄下來！
    history_report = detector.觀察並記錄空間動態(duration_sec=30)
    
    print(f"\n[報告出爐] 這 10 秒內產生的所有移動紀錄為：")
    print(history_report)
    # 以後 Robot 就可以判斷：如果 history_report 裡面有 "收縮中"，代表測試成功！
        
    print("\n[測試結束] 按下斷線按鈕...")
    detector.disconnect()
