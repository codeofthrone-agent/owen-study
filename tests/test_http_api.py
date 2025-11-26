"""
HTTP API Server 單元測試
-----------------------
此測試檔案用於驗證運行在機器手臂端 (Raspberry Pi) 的 `HTTPAPIServer` 功能。
該 Server 提供 HTTP 介面，允許外部客戶端（如自動化測試腳本）透過網路截取攝影機影像。

測試範圍：
- 健康檢查端點 (/health)
- 單張影像截取 (/api/v1/capture)
- 多張影像截取 (/api/v1/capture/multiple)
- 參數驗證與錯誤處理

注意：
此測試使用 `MockCameraCapture` 模擬攝影機硬體，因此不需要實際連接攝影機或機器手臂。
"""

import pytest
import threading
import time
import requests
import cv2
import numpy as np
import logging
from unittest.mock import MagicMock, Mock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.robot_arm_server import HTTPAPIServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockCameraCapture:
    """模擬攝影機截取類別，用於測試環境"""
    def __init__(self):
        # 建立一個帶有綠色矩形的測試影像 (640x480)
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(self.frame, (100, 100), (200, 200), (0, 255, 0), -1)

    def capture_multi_frame_average(self, num_frames=5, warmup_frames=0):
        """模擬多幀平均截取，直接返回預設測試影像"""
        return self.frame.copy()

@pytest.fixture(scope="module")
def server():
    """Pytest Fixture: 啟動並管理測試用的 HTTP API Server"""
    host = "127.0.0.1"
    port = 8001  # 使用不同於預設 (8000) 的端口以避免衝突
    camera_capture = MockCameraCapture()
    camera_lock = threading.Lock()
    
    # 初始化並啟動 Server
    server = HTTPAPIServer(host, port, camera_capture, camera_lock, logger)
    server.start()
    
    # 等待 Server 啟動
    time.sleep(1)
    
    yield server
    
    # 測試結束後停止 Server
    server.stop()

def test_health_endpoint(server):
    """
    測試健康檢查端點 (/health)
    
    驗證項目:
    1. HTTP 狀態碼為 200
    2. 回傳狀態為 "healthy"
    3. 版本號正確 (4.2.0)
    4. Vision 服務狀態為 True
    """
    url = f"http://{server.host}:{server.port}/health"
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "4.2.0"
    assert data["services"]["vision"] is True

def test_capture_endpoint(server):
    """
    測試單張影像截取端點 (/api/v1/capture)
    
    驗證項目:
    1. 能夠成功截取影像
    2. 回傳包含 image_base64 資料
    3. metadata 中的格式正確
    """
    url = f"http://{server.host}:{server.port}/api/v1/capture"
    params = {"num_frames": 1, "format": "jpeg"}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_base64" in data
    assert data["metadata"]["format"] == "jpeg"

def test_capture_multiple_endpoint(server):
    """
    測試多張影像截取端點 (/api/v1/capture/multiple)
    
    驗證項目:
    1. 能夠一次請求多張影像 (count=3)
    2. 回傳的 images 列表長度正確
    3. metadata 中的 count 正確
    """
    url = f"http://{server.host}:{server.port}/api/v1/capture/multiple"
    params = {"count": 3, "num_frames": 1, "format": "jpeg"}
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "images" in data
    assert len(data["images"]) == 3
    assert data["metadata"]["count"] == 3

def test_invalid_params(server):
    """
    測試參數驗證與錯誤處理
    
    驗證項目:
    1. num_frames 超出範圍時回傳 400 錯誤
    2. format 不支援時回傳 400 錯誤
    """
    url = f"http://{server.host}:{server.port}/api/v1/capture"
    
    # 測試無效的 num_frames (超過上限)
    response = requests.get(url, params={"num_frames": 100})
    assert response.status_code == 400
    
    # 測試無效的 format
    response = requests.get(url, params={"format": "bmp"})
    assert response.status_code == 400

