#!/usr/bin/env python3
"""
RTSP 診斷腳本

用於診斷為何無法連接到特定攝影機 (例如: 192.168.165.136)
只測試目前配置的路徑以及最常見的替代路徑，避免嘗試過多無效路徑。

Target: taipei_lab -> motor (192.168.165.136)
"""

import sys
import time
import os
import cv2
from pathlib import Path

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 嘗試載入 .env (如果不依賴 config.ipcam_config 的自動載入)
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

try:
    from config.ipcam_config import get_camera_url, get_camera_config
except ImportError:
    print("無法載入 config.ipcam_config，請確認環境設定。")
    sys.exit(1)

def check_rtsp_stream(url: str, description: str):
    """使用 OpenCV 檢查 RTSP 串流是否可用 (嘗試 TCP 和 UDP)"""
    import re
    safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', url)
    
    protocols = [('tcp', 'rtsp_transport;tcp|stimeout;5000000'), 
                 ('udp', 'rtsp_transport;udp|stimeout;5000000')]
    
    for proto_name, option in protocols:
        print(f"測試路徑 [{description}] [{proto_name.upper()}]: {safe_url}")
        
        # 設定環境變數
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = option
        
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            print(f"  ❌ [{proto_name.upper()}] 無法開啟連線 (isOpened=False)")
            cap.release()
            continue
        
        # 嘗試讀取
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            print(f"  ✅ [{proto_name.upper()}] 成功讀取影像! 尺寸: {frame.shape}")
            cap.release()
            return True
        else:
            print(f"  ⚠️  [{proto_name.upper()}] 連線已開啟但無法讀取影像 (ret={ret})")
        
        cap.release()
    
    return False

def main():
    print("=== RTSP 連線診斷工具 ===")
    
    env_name = "taipei_lab"
    cam_name = "motor"
    
    print(f"目標攝影機: {env_name} -> {cam_name}")
    
    try:
        config = get_camera_config(env_name, cam_name)
        ip = config.get('ip')
        print(f"IP: {ip}")
    except Exception as e:
        print(f"無法取得攝影機設定: {e}")
        # Fallback if config fails
        ip = "192.168.165.136"
        print(f"使用預設 IP: {ip}")

    # 0. Sanity Check: 測試已知可用的 level1 攝影機
    print("\n--- 0. Sanity Check: Test Level 1 Config (192.168.165.184) ---")
    try:
        level1_url = get_camera_url(env_name, "level1")
        if check_rtsp_stream(level1_url, "Level 1 (/live0)"):
            print("✅ Level 1 連線成功！腳本與環境配置功能正常。")
        else:
            print("⚠️ Level 1 連線失敗！請檢查網路或帳號密碼設定。")
            print("   (這意味著連 motor 失敗可能也是因為這原因)")
    except Exception as e:
        print(f"  Sanity check error: {e}")

    # 1. 測試目前配置的路徑
    print("\n--- 1. 測試目前配置 (Target: motor) ---")
    try:
        current_url = get_camera_url(env_name, cam_name)
        if check_rtsp_stream(current_url, "Configured Path (/live0)"):
            print("\n🎉 目前配置有效！可能之前是網路暫時性問題。")
            return
    except Exception as e:
        print(f"  ❌ 測試過程發生錯誤: {e}")

    # 2. 測試常見替代路徑
    print("\n--- 2. 測試常見替代路徑 ---")
    # 從 ipcam_config 取得 URL 並替換路徑部分
    # 為了確保使用正確的帳號密碼，我們使用 get_camera_url 並帶入 override
    
    alternative_paths = [
        "/live0",       # Default
        "/live1",       # Common alternative
        "/stream1",     # Generic
        "/stream2",
        "/h264",        # Generic
        "/unicast",     # Generic
        "/live/ch0",    # TP-Link / Vivotek
        "/live/ch1",
        "/Streaming/Channels/101", # Hikvision
        "/cam/realmonitor?channel=1&subtype=0", # Dahua
        "/axis-media/media.amp", # Axis
        "/video",
        "/media/video1",
        "/onvif-media/media.amp",
        "/12",          # Some generic cameras
        "/11",
    ]
    
    found = False
    for path in alternative_paths:
        try:
            # get_camera_url 接受 stream_path 作為第三個位置參數 (基於 test_ipcam_config.py 的用法)
            test_url = get_camera_url(env_name, cam_name, path)
            if check_rtsp_stream(test_url, f"Path: {path}"):
                print(f"\n🎉 找到可用路徑！建議修改配置與此一致: {path}")
                found = True
                break
        except Exception as e:
            print(f"  錯誤: {e}")
            
    if not found:
        print("\n❌ 所有測試路徑均失敗。可能是網路不通、IP 錯誤、Port 錯誤或帳號密碼錯誤。")
        print(f"請 ping {ip} 確認網路連通性。")
        
        # 額外建議
        print("\n建議排查:")
        print("1. 確認攝影機電源開啟")
        print("2. 確認 .env 中的 IPCAM_PASSWORD 正確")
        print("3. 確認該攝影機未被其他連線佔用 (RTSP通常有限制連線數)")

if __name__ == "__main__":
    main()
