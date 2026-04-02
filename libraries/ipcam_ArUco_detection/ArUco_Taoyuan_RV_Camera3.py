import cv2
import numpy as np
from cv2 import aruco
import os
import time
from collections import deque

import sys

# 自動載入上層的 config 模組，取得最新機密資訊
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config.ipcam_config import get_camera_url

# --- 1. 連線設定 ---
try:
    # 向設定中心請求 'rv_car' 環境的 'rv_motor' 完整 RTSP URL (已自動含帳密)
    RTSP_URL = get_camera_url('rv_car', 'rv_motor')
except Exception as e:
    print(f"❌ 無法取得攝影機設定: {e}")
    exit(1)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"

# --- 2. 參數調整 (核心關鍵) ---
target_id = 17
# 增加視窗大小，平滑感更強
HISTORY_SIZE = 15  
# 提高門檻，過濾掉更大幅度的抖動
MOVE_THRESHOLD = 3500    
STABLE_THRESHOLD = 1500  
# 【信心機制】狀態必須連續出現幾次才算數
CONFIDENCE_REQUIRED = 10 

area_history = deque(maxlen=HISTORY_SIZE)
last_stable_area = None
current_state = "穩定"
pending_state = "穩定"
state_count = 0

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

print(f"🚀 終極穩定監控啟動！目標 ID: {target_id}")

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue

        corners, ids, _ = aruco.detectMarkers(frame, aruco.getPredefinedDictionary(aruco.DICT_4X4_50))
        
        if ids is not None and target_id in ids.flatten():
            idx = np.where(ids.flatten() == target_id)[0][0]
            curr_area = cv2.contourArea(corners[idx])
            area_history.append(curr_area)

            if len(area_history) == HISTORY_SIZE:
                avg_area = sum(area_history) / len(area_history)
                
                if last_stable_area is None:
                    last_stable_area = avg_area
                
                diff = avg_area - last_stable_area
                
                # --- 核心邏輯：信心判定 ---
                temp_state = current_state
                if diff > MOVE_THRESHOLD:
                    temp_state = "收縮中"
                elif diff < -MOVE_THRESHOLD:
                    temp_state = "外推中"
                elif abs(diff) < STABLE_THRESHOLD:
                    temp_state = "穩定"

                # 如果偵測到的狀態跟目前不一樣，開始累積「信心」
                if temp_state != current_state:
                    if temp_state == pending_state:
                        state_count += 1
                    else:
                        pending_state = temp_state
                        state_count = 1
                    
                    # 只有連續達標 CONFIDENCE_REQUIRED 次，才真的換狀態
                    if state_count >= CONFIDENCE_REQUIRED:
                        current_state = temp_state
                        last_stable_area = avg_area # 更新基準點
                        state_count = 0
                        print(f"🔔 [{time.strftime('%H:%M:%S')}] 狀態切換 -> {current_state} (Diff: {diff:.1f})")
                else:
                    state_count = 0 # 回到跟目前一樣的狀態，計數歸零

            # 視覺化
            cv2.polylines(frame, [corners[idx].astype(np.int32)], True, (0, 255, 0), 2)

        # 顯示
        cv2.putText(frame, f"State: {current_state}", (20, 50), 2, 1, (0, 255, 255), 2)
        cv2.imshow('RV Monitor Max Stable', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cap.release()
    cv2.destroyAllWindows()