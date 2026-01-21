#!/usr/bin/env python3
# coding:utf-8
import socket
import sys
import serial
import time
import logging
import logging.handlers
import re
import subprocess
import fcntl
import struct
import traceback
import threading
import json
import yaml
from typing import Optional, Dict, List, Tuple
import numpy as np
import cv2
import cv2.aruco as aruco
import base64
from flask import Flask, jsonify, request
from werkzeug.serving import make_server
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available, GPIO functionality disabled")

"""
Instructions for use:

Please update pymycobot to the latest version before use.

`pip install pymycobot --upgrade`

Please change the parameters passed in the last line of the Server.py file, MycobotServer, based on your model.


The default model is the 280PI.

    The default parameters are:

        serial_num: /dev/ttyAMA0

        baud: 1000000


Enhanced features:
    - Auto reconnection on serial disconnect
    - Heartbeat mechanism for connection monitoring
    - Improved error handling and logging
    - Thread-safe serial operations
    - Vision detection system for button LED color detection (Blue/White/Off)
    - JSON command protocol for vision and control operations
"""

has_return = [0x01,0x02,0x03,0x04,0x09,0x12, 0x14, 0x15, 0x17,0x1B, 0x20,0x23, 0x27, 0x2A,0x2B,0x2D,0x2E, 0x3B,0x3D, 0x40,0x42,0x43,0x44,0x4A, 0x4B,0x50,0x51,0x53,0x62,0x65,0x69,0x90,0x91,0x92,0xC0, 0xC3,0x82,0x84,0x86,0x88,0x8A,0xD0,0xD1,0xD5,0xE1,0xE2,0xE3,0xE4,0xE5,0XE6, 0xB0]


# ==================== HTTP API Server (v4.2.0) ====================
# 職責分離架構：Socket (控制) + HTTP (影像)
#
# 端點:
# - GET  /health                      - 健康檢查
# - GET  /api/v1/capture              - 單張影像截取
# - GET  /api/v1/capture/multiple     - 多張影像截取

class HTTPAPIServer:
    """HTTP API Server (v4.3.0) - Flask Implementation with YOLO support"""

    def __init__(self, host, port, camera_capture, camera_lock, logger, yolo_detector=None):
        self.host = host
        self.port = port
        self.camera_capture = camera_capture
        self.camera_lock = camera_lock
        self.logger = logger
        self.yolo_detector = yolo_detector
        self.app = Flask(__name__)
        self.server = None
        self.server_thread = None
        self.ctx = None

        # Configure Flask logger
        self.app.logger.handlers = self.logger.handlers
        self.app.logger.setLevel(self.logger.level)

        # Register routes
        self.app.add_url_rule('/health', 'health', self.health, methods=['GET'])
        self.app.add_url_rule('/api/v1/health', 'api_health', self.health, methods=['GET'])
        self.app.add_url_rule('/api/v1/capture', 'capture', self.capture, methods=['GET'])
        self.app.add_url_rule('/api/v1/capture/multiple', 'capture_multiple', self.capture_multiple, methods=['GET'])

        # YOLO endpoint (v4.3.0)
        if yolo_detector:
            self.app.add_url_rule('/api/v1/yolo/detect', 'yolo_detect', self.yolo_detect, methods=['GET'])

    def start(self):
        """Start HTTP API Server in a separate thread"""
        self.server_thread = threading.Thread(target=self._run, daemon=True)
        self.server_thread.start()
        self.logger.info(f"✅ HTTP API Server (Flask) started at http://{self.host}:{self.port}")
        self.logger.info(f"   Endpoints:")
        self.logger.info(f"   - GET /health")
        self.logger.info(f"   - GET /api/v1/capture?num_frames=5&format=jpeg")
        self.logger.info(f"   - GET /api/v1/capture/multiple?count=5&num_frames=5&format=jpeg")
        if self.yolo_detector:
            self.logger.info(f"   - GET /api/v1/yolo/detect?num_frames=5&confidence=0.5&save_image=true")

    def _run(self):
        try:
            self.server = make_server(self.host, self.port, self.app, threaded=True)
            self.ctx = self.app.app_context()
            self.ctx.push()
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"HTTP API Server error: {e}")

    def stop(self):
        """Stop HTTP API Server"""
        if self.server:
            self.server.shutdown()
            self.server_thread.join(timeout=5)
            self.logger.info("HTTP API Server stopped")

    def health(self):
        return jsonify({
            "status": "healthy",
            "version": "4.2.0",
            "services": {
                "vision": self.camera_capture is not None
            }
        })

    def capture(self):
        if not self.camera_capture:
            return jsonify({"status": "error", "message": "Vision system not available"}), 503

        try:
            num_frames = int(request.args.get('num_frames', 5))
            image_format = request.args.get('format', 'jpeg')

            if not (1 <= num_frames <= 20):
                return jsonify({"status": "error", "message": "num_frames must be between 1 and 20"}), 400
            if image_format not in ['jpeg', 'png']:
                return jsonify({"status": "error", "message": "format must be 'jpeg' or 'png'"}), 400

            with self.camera_lock:
                avg_frame = self.camera_capture.capture_multi_frame_average(
                    num_frames=num_frames,
                    warmup_frames=0
                )

                if avg_frame is None:
                    return jsonify({"status": "error", "message": "Failed to capture image"}), 500

                ext = '.jpg' if image_format == 'jpeg' else '.png'
                _, buffer = cv2.imencode(ext, avg_frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                "status": "success",
                "image_base64": image_base64,
                "metadata": {
                    "num_frames": num_frames,
                    "format": image_format,
                    "shape": avg_frame.shape[:2]
                }
            })

        except Exception as e:
            self.logger.error(f"Capture error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    def capture_multiple(self):
        if not self.camera_capture:
            return jsonify({"status": "error", "message": "Vision system not available"}), 503

        try:
            count = int(request.args.get('count', 5))
            num_frames = int(request.args.get('num_frames', 5))
            image_format = request.args.get('format', 'jpeg')

            if not (1 <= count <= 10):
                return jsonify({"status": "error", "message": "count must be between 1 and 10"}), 400
            if not (1 <= num_frames <= 20):
                return jsonify({"status": "error", "message": "num_frames must be between 1 and 20"}), 400
            if image_format not in ['jpeg', 'png']:
                return jsonify({"status": "error", "message": "format must be 'jpeg' or 'png'"}), 400

            images_base64 = []
            with self.camera_lock:
                for i in range(count):
                    avg_frame = self.camera_capture.capture_multi_frame_average(
                        num_frames=num_frames,
                        warmup_frames=0
                    )

                    if avg_frame is None:
                        return jsonify({"status": "error", "message": f"Failed to capture image {i+1}/{count}"}), 500

                    ext = '.jpg' if image_format == 'jpeg' else '.png'
                    _, buffer = cv2.imencode(ext, avg_frame)
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
                    images_base64.append(image_base64)

                    if i < count - 1:
                        time.sleep(0.05)

            return jsonify({
                "status": "success",
                "images": images_base64,
                "metadata": {
                    "count": count,
                    "num_frames": num_frames,
                    "format": image_format
                }
            })

        except Exception as e:
            self.logger.error(f"Multiple capture error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    def yolo_detect(self):
        """YOLO 物件檢測 HTTP 端點 (v4.3.0)"""
        if not self.yolo_detector:
            return jsonify({"status": "error", "message": "YOLO detection not available"}), 503

        try:
            # 解析參數
            num_frames = int(request.args.get('num_frames', 5))
            confidence = float(request.args.get('confidence', 0.85))
            save_image = request.args.get('save_image', 'true').lower() == 'true'
            return_image = request.args.get('return_image', 'false').lower() == 'true'

            # 參數驗證
            if not (1 <= num_frames <= 20):
                return jsonify({"status": "error", "message": "num_frames must be between 1 and 20"}), 400
            if not (0.0 <= confidence <= 1.0):
                return jsonify({"status": "error", "message": "confidence must be between 0.0 and 1.0"}), 400

            # 執行檢測（使用與 camera_lock 相同的鎖）
            with self.camera_lock:
                # 1. 截取圖像
                avg_frame = self.camera_capture.capture_multi_frame_average(
                    num_frames=num_frames,
                    warmup_frames=0
                )

                if avg_frame is None:
                    return jsonify({"status": "error", "message": "Failed to capture image"}), 500

                # 2. 執行 YOLO 檢測
                import time
                start_time = time.time()
                detections = self.yolo_detector.detect(avg_frame, confidence=confidence)
                inference_time = (time.time() - start_time) * 1000

                # 3. 準備響應
                response_data = {
                    "status": "success",
                    "detections": detections,
                    "metadata": {
                        "num_frames": num_frames,
                        "confidence_threshold": confidence,
                        "inference_time_ms": round(inference_time, 2),
                        "num_detections": len(detections)
                    }
                }

                # 4. 儲存圖片（如果需要）
                if save_image:
                    try:
                        original_path, annotated_path = self.yolo_detector.save_results(
                            avg_frame, detections
                        )
                        response_data["image_path"] = original_path
                        response_data["annotated_image_path"] = annotated_path
                    except Exception as e:
                        self.logger.warning(f"Failed to save images: {e}")
                        response_data["save_error"] = str(e)

                # 5. 返回圖片 base64（如果需要）
                if return_image:
                    try:
                        # 原始圖
                        _, buffer = cv2.imencode('.jpg', avg_frame)
                        response_data["image_base64"] = base64.b64encode(buffer).decode('utf-8')

                        # 標註圖
                        annotated_image = self.yolo_detector.draw_boxes(avg_frame, detections)
                        _, buffer = cv2.imencode('.jpg', annotated_image)
                        response_data["annotated_image_base64"] = base64.b64encode(buffer).decode('utf-8')
                    except Exception as e:
                        self.logger.warning(f"Failed to encode images: {e}")
                        response_data["encoding_error"] = str(e)

            return jsonify(response_data)

        except ValueError as e:
            return jsonify({"status": "error", "message": f"Invalid parameter: {str(e)}"}), 400
        except Exception as e:
            self.logger.error(f"YOLO detection error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500


# ==================== CameraCapture 類別 ====================
# v4.0.0 更新：移除影像判定邏輯，只保留影像截取功能
# 影像分析已遷移至本機端 LocalVisionAnalyzer

class CameraCapture:
    """影像截取引擎 - 提供基礎影像截取功能

    功能：
    - 多幀平均截圖（解決 LED 掃描頻率問題）
    - Base64 影像編碼
    """

    def __init__(self, camera_device="/dev/video0", logger=None):
        """初始化影像截取器

        Args:
            camera_device: 攝影機設備路徑
            logger: 日誌記錄器（可選）
        """
        self.camera_device = camera_device
        self.logger = logger or logging.getLogger("CameraCapture")
        self.camera_lock = threading.Lock()

        self.logger.info(f"CameraCapture 初始化完成，攝影機: {camera_device}")

    def capture_multi_frame_average(self, num_frames=5, warmup_frames=20) -> np.ndarray:
        """多幀平均截圖（解決 LED 掃描頻率與自動曝光問題）

        - LED PWM 調光頻率與攝影機幀率不同步會導致亮度不穩定。
        - 攝影機啟動時需要時間穩定自動曝光。

        Args:
            num_frames: 用於平均的幀數（預設 5 幀）。
            warmup_frames: 用於預熱的幀數（預設 10 幀），讓自動曝光穩定。

        Returns:
            平均後的圖像 (numpy.ndarray)

        Raises:
            RuntimeError: 無法截取圖像
        """
        with self.camera_lock:
            cap = cv2.VideoCapture(self.camera_device)

            if not cap.isOpened():
                raise RuntimeError(f"無法開啟攝影機: {self.camera_device}")

            # 設定攝影機參數
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            # 新增：相機預熱階段，讓自動曝光穩定
            self.logger.debug(f"相機預熱中，讀取並捨棄 {warmup_frames} 幀...")
            for _ in range(warmup_frames):
                cap.read()
            self.logger.debug("相機預熱完成。")

            # 讀取幀用於平均
            frames = []
            for i in range(num_frames):
                ret, frame = cap.read()
                if ret and frame is not None:
                    frames.append(frame.astype(np.float32))
                time.sleep(0.01)  # 短暫延遲避免連續讀取同一幀

            cap.release()

            if not frames:
                raise RuntimeError("無法截取任何圖像幀")

            # 平均所有幀
            avg_frame = np.mean(frames, axis=0).astype(np.uint8)
            self.logger.debug(f"多幀平均截圖完成 ({len(frames)}/{num_frames} 幀)")

            return avg_frame

    # ========== v4.0.0 已移除的方法 ==========
    # 以下影像判定方法已遷移至本機端 LocalVisionAnalyzer：
    # - detect_button_state()
    # - _extract_roi()
    # - _detect_brightness()
    # - _detect_color_hsv()
    # Server 只保留影像截取與 ArUco 檢測功能

    def detect_aruco_markers(self, image: np.ndarray, marker_size: float = 0.05) -> Dict:
        """檢測 ArUco 標記並計算位置資訊（支援所有 OpenCV 版本）
        
        Args:
            image: 輸入影像
            marker_size: 標記實際大小（公尺）
            
        Returns:
            包含檢測到的標記資訊的字典
        """
        try:
            # 檢查 OpenCV 版本並使用適當的 API
            cv_version = cv2.__version__
            self.logger.debug(f"🔍 OpenCV 版本: {cv_version}")
            
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
            parameters = aruco.DetectorParameters()
            detector = aruco.ArucoDetector(aruco_dict, parameters)
            self.logger.debug("✓ 使用最新版 ArUco API (ArucoDetector)")
            
            # 使用 ArucoDetector 進行檢測
            corners, ids, _ = detector.detectMarkers(image)
            
            result = {
                "success": True,
                "markers_count": len(corners) if corners is not None else 0,
                "markers": []
            }
            
            if corners is not None and len(corners) > 0:
                self.logger.info(f"🎯 檢測到 {len(corners)} 個 ArUco 標記")
                
                for i, corner in enumerate(corners):
                    marker_id = int(ids[i][0]) if ids is not None and len(ids) > i else i
                    
                    # 計算標記中心
                    center = np.mean(corner[0], axis=0)
                    
                    marker_info = {
                        "id": marker_id,
                        "center": [float(center[0]), float(center[1])],
                        "corners": corner[0].tolist(),
                    }
                    result["markers"].append(marker_info)
            else:
                self.logger.debug("🔍 未檢測到任何 ArUco 標記")
                    
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ArUco 檢測失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "markers_count": 0,
                "markers": []
            }

    def calculate_position_correction(self, current_markers: List[Dict], 
                                    reference_markers: List[Dict]) -> Optional[Dict]:
        """計算位置校正資訊
        
        Args:
            current_markers: 當前檢測到的標記
            reference_markers: 參考位置的標記
            
        Returns:
            位置校正資訊或 None
        """
        try:
            if not current_markers or not reference_markers:
                return None
            
            current_ids = {m["id"]: {"center_x": m["center"][0], "center_y": m["center"][1]} for m in current_markers}
            reference_ids = {m["id"]: {"center_x": m["center"][0], "center_y": m["center"][1]} for m in reference_markers}
            
            common_ids = set(current_ids.keys()) & set(reference_ids.keys())
            
            if not common_ids:
                self.logger.warning("⚠️  沒有找到共同的 ArUco 標記 ID")
                return None
            
            self.logger.info(f"📍 找到 {len(common_ids)} 個共同標記: {list(common_ids)}")
            
            total_offset_x = 0
            total_offset_y = 0
            
            for marker_id in common_ids:
                offset_x = current_ids[marker_id]["center_x"] - reference_ids[marker_id]["center_x"]
                offset_y = current_ids[marker_id]["center_y"] - reference_ids[marker_id]["center_y"]
                total_offset_x += offset_x
                total_offset_y += offset_y
            
            avg_offset_x = total_offset_x / len(common_ids)
            avg_offset_y = total_offset_y / len(common_ids)
            
            result = {
                "offset_x": float(avg_offset_x),
                "offset_y": float(avg_offset_y),
                "common_markers": int(len(common_ids)),
            }
            
            self.logger.info(f"📐 位置校正結果: 平均偏移=({avg_offset_x:.1f}, {avg_offset_y:.1f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 計算位置校正失敗: {e}")
            return None

# ==================== get_logger 函數 ====================

def get_logger(name, log_level=logging.INFO):
    """獲取配置好的日誌記錄器

    Args:
        name: 日誌記錄器名稱
        log_level: 日誌級別 (預設: INFO)
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s"
    #DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

    formatter = logging.Formatter(LOG_FORMAT)
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    save = logging.handlers.RotatingFileHandler(
        "server.log", maxBytes=10485760, backupCount=3)
    save.setFormatter(formatter)

    logger.addHandler(save)
    logger.addHandler(console)
    return logger


class MycobotServer(object):

    def __init__(self, host, port, serial_num = "/dev/ttyAMA0", baud = 1000000,
                 reconnect_interval = 2, max_reconnect_attempts = 5,
                 read_timeout = 0.2, socket_timeout = 30.0, log_level = logging.INFO,
                 camera_device = "/dev/video0", enable_vision = True,
                 enable_http = True, http_port = 8000,
                 enable_yolo = True, yolo_model_path = "models/best_20260106.pt",
                 yolo_confidence = 0.85, yolo_device = "cuda"):
        """Server class with enhanced error handling and auto-reconnection

        Args:
            host: server ip address.
            port: server port (Socket protocol, default: 9000).
            serial_num: serial number of the robot.The default is /dev/ttyAMA0.
            baud: baud rate of the serial port.The default is 1000000.
            reconnect_interval: seconds between reconnection attempts.
            max_reconnect_attempts: maximum reconnection attempts before giving up.
            read_timeout: serial read timeout in seconds (default: 0.2).
            socket_timeout: socket receive timeout in seconds (default: 30.0).
            log_level: logging level (default: logging.INFO).
            camera_device: camera device path (default: /dev/video0).
            enable_vision: enable vision detection system (default: True).
            enable_http: enable HTTP API Server (v4.2.0, default: False).
            http_port: HTTP API Server port (default: 8000).
            enable_yolo: enable YOLO object detection (default: True).
            yolo_model_path: path to YOLO model file (default: models/best_20260106.pt).
            yolo_confidence: YOLO confidence threshold (default: 0.5).
            yolo_device: YOLO inference device, "cuda" or "cpu" (default: cuda).

        """
        if GPIO_AVAILABLE:
            try:
                GPIO.setwarnings(False)
            except Exception as e:
                print(f"GPIO initialization warning: {e}")

        self.logger = get_logger("AS", log_level)
        self.mc: Optional[serial.Serial] = None
        self.serial_num = serial_num
        self.baud = baud
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.read_timeout = read_timeout
        self.socket_timeout = socket_timeout
        self.serial_lock = threading.RLock()  # Use RLock to prevent deadlocks
        self.serial_lock_file = None  # 用於文件鎖
        self.is_running = True

        # 影像截取系統配置（v4.0.0：影像判定已移至本機端）
        self.camera_device = camera_device
        self.enable_vision = enable_vision
        self.camera_capture = None
        self.camera_lock = threading.Lock()  # v4.2.0: Camera 執行緒鎖（Socket + HTTP 共用）

        # HTTP API Server 配置（v4.2.0）
        self.enable_http = enable_http
        self.http_port = http_port
        self.http_server = None

        # YOLO 物件檢測配置（v4.3.0）
        self.enable_yolo = enable_yolo
        self.yolo_model_path = yolo_model_path
        self.yolo_confidence = yolo_confidence
        self.yolo_device = yolo_device
        self.yolo_detector = None

        # 全局偏移補償系統 (v5.0.0 De-IK)
        self.global_offsets = [0.0] * 6
        self.correction_enabled = False
        # 使用絕對路徑，確保從任何目錄啟動都能找到配置檔
        import os
        self.offset_config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", "global_offset.json"
        )
        # self._load_global_offsets()

        # STag 視覺偏移系統 (v5.1.0 Phase 13.5)
        self.stag_offset = [0.0, 0.0, 0.0]      # [x, y, z] in mm (位置空間)
        self.stag_enabled = False                # STag 偏移啟用狀態
        self.stag_reference = {}                 # 參考標記資訊

        # 初始化 socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.logger.info(f"Server bound to {host}:{port}")
        print("Binding succeeded!")
        self.s.listen(1)

        # 初始化串口連接 (包含獨佔鎖檢查)
        if not self._init_serial():
            self.logger.error("伺服器啟動失敗，因為無法取得序列埠的獨佔存取權。")
            self.shutdown()
            sys.exit(1)

        # ==================== 自動歸位功能已禁用 ====================
        # 根據與官方 Server.py 的比對，此處的自動歸位邏輯可能是導致通訊問題的根源。
        # 官方伺服器是一個純粹的被動橋樑，不主動發送任何指令。
        # 我們的伺服器在啟動時主動歸位，可能導致機器手臂韌體進入異常狀態。
        # 現在我們將此功能禁用，將歸位職責完全交還給客戶端。
        # =================================================================

        # 初始化影像截取系統（v4.0.0：只提供影像截取，判定在本機端）
        if self.enable_vision:
            try:
                self.camera_capture = CameraCapture(camera_device, self.logger)
                self.logger.info("✅ 影像截取系統已啟用（影像判定在本機端執行）")
            except Exception as e:
                self.logger.warning(f"⚠️ 影像截取系統初始化失敗: {e}")
                self.logger.warning("   伺服器將以無視覺模式運行")
                self.enable_vision = False

        # 初始化 FK/IK 運動學系統（v5.1.0 Phase 13.5）
        self.fk_calculator = None
        self.ik_solver = None
        if self.enable_vision:  # 只在 Vision 啟用時載入（STag 偏移依賴 Vision）
            try:
                # 確保專案根目錄在 sys.path
                import os
                project_root = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..'
                ))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                from library.planning.dh_fk_calculator_original import DHForwardKinematics
                from library.planning.ik_solver import IKSolver

                self.fk_calculator = DHForwardKinematics()
                self.ik_solver = IKSolver(self.fk_calculator)  # 使用共享的 FK 實例
                self.logger.info("✅ FK/IK 運動學系統已整合 (Phase 13.5)")
                self.logger.info("   FK 精度: XY 0.2%, Z 3.85mm std")
                self.logger.info("   IK 精度: < 5mm (Phase 12)")

            except Exception as e:
                self.logger.warning(f"⚠️ FK/IK 系統載入失敗: {e}")
                self.logger.warning("   STag 偏移功能將不可用（不影響現有功能）")
                self.fk_calculator = None
                self.ik_solver = None

        # 初始化 STag 檢測器（v5.1.0 Phase 13.5B）
        self.stag_detector = None
        if self.enable_vision:
            try:
                from library.vision.stag_detector import StagCoordinateSystem, STAG_AVAILABLE

                if STAG_AVAILABLE:
                    # 載入全域視覺設定
                    import os
                    app_config_path = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'config', 'app', 'app.yaml'
                    )
                    
                    marker_size_m = 0.05  # 預設 50mm
                    stag_hd = 11
                    
                    if os.path.exists(app_config_path):
                        try:
                            with open(app_config_path, 'r', encoding='utf-8') as f:
                                app_config = yaml.safe_load(f)
                                vision_cfg = app_config.get('vision', {})
                                marker_size_mm = vision_cfg.get('marker_size', 50.0)
                                marker_size_m = marker_size_mm / 1000.0
                                stag_hd = vision_cfg.get('stag_hd_library', 11)
                                self.logger.info(f"✅ 從 {app_config_path} 載入標記尺寸: {marker_size_mm}mm")
                        except Exception as e:
                            self.logger.warning(f"⚠️ 讀取 app.yaml 失敗: {e}，使用預設值")
                    else:
                        self.logger.warning(f"⚠️ 找不到 {app_config_path}，使用預設值")

                    # 載入攝影機校正參數
                    camera_intrinsics_path = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'config', 'camera_intrinsics.npz'
                    )

                    camera_matrix = None
                    dist_coeffs = None

                    if os.path.exists(camera_intrinsics_path):
                        calib_data = np.load(camera_intrinsics_path)
                        camera_matrix = calib_data.get('mtx')
                        dist_coeffs = calib_data.get('dist')
                        self.logger.info(f"✅ 載入攝影機校正參數: {camera_intrinsics_path}")
                    else:
                        self.logger.warning("⚠️ 未找到攝影機校正參數，使用預設值")

                    # 初始化 STag 檢測器
                    self.stag_detector = StagCoordinateSystem(
                        camera_matrix=camera_matrix,
                        dist_coeffs=dist_coeffs,
                        marker_size=marker_size_m,
                        library_hd=stag_hd
                    )
                    self.logger.info(f"✅ STag 檢測器已整合 (Phase 13.5B), Size: {marker_size_m*1000:.1f}mm")
                else:
                    self.logger.warning("⚠️ stag-python 模組未安裝，STag 檢測器不可用")

            except Exception as e:
                self.logger.warning(f"⚠️ STag 檢測器載入失敗: {e}")
                self.stag_detector = None

        # 初始化 YOLO 物件檢測系統（v4.3.0）- 在 HTTP Server 之前初始化
        if self.enable_yolo:
            if not self.enable_vision or not self.camera_capture:
                self.logger.warning("⚠️ YOLO 檢測需要 Vision 系統，但 Vision 系統未啟用")
                self.logger.warning("   YOLO 檢測功能將不會啟動")
                self.enable_yolo = False
            else:
                try:
                    from library.vision.yolo_detector import YOLODetector
                    self.yolo_detector = YOLODetector(
                        model_path=self.yolo_model_path,
                        confidence=self.yolo_confidence,
                        device=self.yolo_device,
                        logger=self.logger
                    )
                    self.logger.info("✅ YOLO 物件檢測系統已啟用")
                    self.logger.info(f"   模型: {self.yolo_model_path}")
                    self.logger.info(f"   裝置: {self.yolo_device}")
                except Exception as e:
                    self.logger.error(f"❌ YOLO 檢測系統初始化失敗: {e}")
                    self.logger.warning("   伺服器將繼續運行（無 YOLO 功能）")
                    self.enable_yolo = False

        # 初始化 HTTP API Server（v4.3.0）- 在 YOLO 初始化之後
        if self.enable_http:
            try:
                self.http_server = HTTPAPIServer(
                    host=host,
                    port=self.http_port,
                    camera_capture=self.camera_capture,
                    camera_lock=self.camera_lock,
                    logger=self.logger,
                    yolo_detector=self.yolo_detector if self.enable_yolo else None
                )
                self.http_server.start()
                self.logger.info("✅ HTTP API Server 已啟用")
                self.logger.info(f"   HTTP 端口: {self.http_port}")
                if self.yolo_detector:
                    self.logger.info("   YOLO 端點: /api/v1/yolo/detect")
            except Exception as e:
                self.logger.error(f"❌ HTTP API Server 初始化失敗: {e}")
                self.logger.warning("   伺服器將繼續運行（無 HTTP API 功能）")
                self.enable_http = False

        # 啟動連接處理
        self.connect()

    def _load_global_offsets(self):
        """載入全局偏移補償設定"""
        try:
            import os
            if not os.path.exists(self.offset_config_path):
                self.logger.warning(f"偏移設定檔不存在: {self.offset_config_path}")
                return

            with open(self.offset_config_path, 'r') as f:
                config = json.load(f)
                
            self.global_offsets = config.get("joint_offsets", [0.0]*6)
            self.correction_enabled = config.get("enabled_by_default", True)
            
            self.logger.info(f"✅ 已載入全局偏移補償: {self.global_offsets}")
            self.logger.info(f"   補償啟用狀態: {self.correction_enabled}")
            
        except Exception as e:
            self.logger.error(f"載入偏移設定失敗: {e}")

    def _init_serial(self):
        """初始化串口連接"""
        # 嘗試獲取文件鎖，防止多重存取
        try:
            self.serial_lock_file = open(self.serial_num, 'r')  # 使用只讀模式，避免清空設備文件
            fcntl.flock(self.serial_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.logger.info(f"成功獲取序列埠 '{self.serial_num}' 的獨佔鎖。")
        except (IOError, BlockingIOError):
            self.logger.error(f"❌ 序列埠 '{self.serial_num}' 已被另一個程序鎖定。")
            
            # 新增：檢測佔用程序的 PID
            try:
                result = subprocess.run(['lsof', '-t', self.serial_num], capture_output=True, text=True, check=True)
                pids = result.stdout.strip().split('\n')
                if pids and pids[0]:
                    self.logger.error(f"   佔用程序 PID: {', '.join(pids)}")
                    self.logger.error("   💡 您可以執行以下指令來終止佔用程序:")
                    self.logger.error(f"      kill -9 {' '.join(pids)}")
                else:
                    self.logger.error("   無法確定佔用程序的 PID，但埠已被鎖定。")
            except (FileNotFoundError, subprocess.CalledProcessError):
                self.logger.error("   無法執行 'lsof' 來查找佔用程序。請手動檢查。")

            if self.serial_lock_file:
                self.serial_lock_file.close()
                self.serial_lock_file = None
            return False
        except Exception as e:
            self.logger.error(f"獲取文件鎖時發生未預期錯誤: {e}")
            return False

        try:
            if self.mc and self.mc.is_open:
                self.mc.close()
            self.mc = serial.Serial(self.serial_num, self.baud, timeout=0.1)
            self.logger.info(f"序列埠 {self.serial_num} 開啟成功")

            # 啟動時自動 power on 伺服馬達
            try:
                time.sleep(0.1)  # 等待串口穩定
                power_on_command = [0xfe, 0xfe, 0x02, 0x10, 0xfa]  # power_on 指令
                self.mc.write(power_on_command)
                self.mc.flush()
                self.logger.info("已發送伺服馬達上電指令 (power_on)")
                time.sleep(0.3)  # 等待馬達上電
            except Exception as e:
                self.logger.warning(f"發送上電指令失敗: {e}")

            return True
        except Exception as e:
            self.logger.error(f"開啟序列埠失敗: {e}")
            return False

    def _reconnect_serial(self):
        """嘗試重新連接串口"""
        for attempt in range(self.max_reconnect_attempts):
            self.logger.warning(f"嘗試重新連接串口 (第 {attempt + 1}/{self.max_reconnect_attempts} 次)")
            time.sleep(self.reconnect_interval)

            if self._init_serial():
                self.logger.info("串口重新連接成功")
                return True

        self.logger.error("達到最大重連次數後，串口重連失敗")
        return False

    def _check_serial_health(self):
        """檢查串口健康狀態"""
        try:
            if not self.mc or not self.mc.is_open:
                return False
            # 檢查是否可以訪問串口
            return True
        except Exception as e:
            self.logger.error(f"串口健康檢查失敗: {e}")
            return False

    def _is_moving(self) -> bool:
        """檢查機器手臂是否正在移動"""
        with self.serial_lock:
            is_moving_cmd = [0xfe, 0xfe, 0x02, 0x2b, 0xfa]
            try:
                self.write(is_moving_cmd)
                # is_moving 指令有回應
                response = self.read(is_moving_cmd)
                if response and len(response) >= 5 and response[3] == 0x2b:
                    return bool(response[4])
            except Exception as e:
                self.logger.error(f"檢查 is_moving 狀態失敗: {e}")
        return False  # 發生錯誤時，預設為未移動

    def get_angles(self):
        """讀取當前手臂角度 (已扣除全局偏移)

        Returns:
            list: 6 個關節角度 [j1, j2, j3, j4, j5, j6]，失敗時返回 [None] * 6
        """
        with self.serial_lock:
            # MyCobot 280 get_angles 命令: 0xfe 0xfe 0x02 0x20 0xfa
            # ProtocolCode.GET_ANGLES = 0x20 (注意：不是 0x10，0x10 是 POWER_ON)
            get_angles_cmd = [0xfe, 0xfe, 0x02, 0x20, 0xfa]
            try:
                self.write(get_angles_cmd)
                response = self.read(get_angles_cmd)

                # 預期回應: [0xfe, 0xfe, len, 0x20, j1_h, j1_l, ..., j6_h, j6_l, 0xfa]
                # 處理忙碌回應: b'\xfe\xfe\x03\x20\x01\xfa'
                if response == b'\xfe\xfe\x03\x20\x01\xfa':
                    self.logger.debug("機器手臂忙碌中 (Busy)，無法讀取角度")
                    return [None] * 6

                # 總長度應該是 16 bytes: header(2) + len(1) + cmd(1) + 6*angles(12) + footer(1)
                if response and len(response) >= 16 and response[3] == 0x20:
                    angles = []
                    for i in range(6):
                        # 讀取每個關節的高位和低位字節
                        high_byte = response[4 + i * 2]
                        low_byte = response[5 + i * 2]
                        # 組合成 int16，然後除以 100 轉換為角度
                        angle_int = (high_byte << 8) | low_byte
                        # 處理負數（int16 範圍）
                        if angle_int > 32767:
                            angle_int -= 65536
                        angle = angle_int / 100.0
                        angles.append(angle)
                    
                    # 應用反向全局補償 (Raw - Offset)
                    # 這樣 get_angles 回傳的就是邏輯角度，與 send_angles (Logical + Offset) 對應
                    if self.correction_enabled and len(self.global_offsets) == 6:
                        angles = [a - o for a, o in zip(angles, self.global_offsets)]
                        
                    return angles
                else:
                    self.logger.warning(f"讀取角度回應格式錯誤: {response}")
                    return [None] * 6
            except Exception as e:
                self.logger.error(f"讀取角度失敗: {e}")
                return [None] * 6

    def _wait_for_movement(self, timeout: float = 15.0, interval: float = 0.2):
        """等待機器手臂移動完成"""
        start_time = time.time()
        self.logger.info("等待機器手臂移動完成...")
        while time.time() - start_time < timeout:
            if not self._is_moving():
                elapsed = time.time() - start_time
                self.logger.info(f"✓ 移動完成 (耗時: {elapsed:.2f} 秒)")
                return True
            time.sleep(interval)
        
        self.logger.warning(f"⚠️ 等待移動超時 ({timeout} 秒)")
        return False

    def _wait_for_arrival(self, target_angles: List[float], timeout: float = 5.0, threshold: float = 1.5) -> bool:
        """
        動態等待手臂到達目標位置
        優化策略：使用 is_moving 檢查代替 get_angles 輪詢，減少通訊負擔。
        """
        # 1. 給硬體足夠時間開始移動 (從 0.1 改為 0.5)
        # 避免 is_moving 還沒變成 True 就被誤判為已停止
        time.sleep(0.5)
        
        start = time.time()
        
        # 2. 輪詢 is_moving 狀態
        while time.time() - start < timeout:
            if not self._is_moving():
                # 手臂已停止移動
                break
            time.sleep(0.1)
            
        # 3. 移動結束後，檢查最終位置 (如果讀得到)
        # 這裡不強求一定要讀到，只要不移動了就視為到達，由後續的 verify 步驟做確認
        current = self.get_angles()
        if current and None not in current:
            error = np.max(np.abs(np.array(current) - np.array(target_angles)))
            if error < threshold:
                self.logger.debug(f"✓ 到達目標 (誤差: {error:.2f}°)")
                return True
            else:
                self.logger.warning(f"⚠️ 移動停止但未達目標 (誤差: {error:.2f}°)")
                return False
        
        # 如果讀不到角度，但 is_moving 為 False，我們假設它到了 (盲操作)
        # 這是在通訊不穩時的最佳妥協
        return True

    def _load_zone_config(self, stag_id: int) -> Optional[Dict]:
        """
        載入 Zone 配置檔

        Args:
            stag_id: STag ID

        Returns:
            dict: Zone 配置，包含 id, pos, rpy, angles；如果找不到返回 None
        """
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config', 'calibration_zones', f'zone_{stag_id}.json'
        )

        if not os.path.exists(path):
            self.logger.warning(f"Zone 配置不存在: {path}")
            return None

        try:
            with open(path, 'r') as f:
                data = json.load(f)
                station = data["physical_parameters"]["fixed_station_pose"]
                return {
                    'id': stag_id,
                    'pos': np.array(station["coords_xyz"]),
                    'rpy': np.array(station["coords_rpy"]),
                    'angles': station.get("joint_angles", None)
                }
        except Exception as e:
            self.logger.error(f"載入 Zone 配置失敗: {e}")
            return None

    def _get_angles_with_retry(self, max_retries=3, delay=1.0) -> Optional[List[float]]:
        """
        嘗試多次讀取角度，專門用於動作完成後的最終確認。
        包含緩衝區清空與延遲機制。
        """
        import time as time_module
        
        # 1. 初始靜置，讓串口訊號穩定
        time_module.sleep(delay)

        for i in range(max_retries):
            # 2. 清空緩衝區 (確保讀到最新狀態，而非堆積的 Busy 訊號)
            with self.serial_lock:
                if self.mc and self.mc.is_open:
                    self.mc.reset_input_buffer()
            
            # 3. 嘗試讀取
            angles = self.get_angles()
            if angles and None not in angles:
                return angles
            
            self.logger.warning(f"角度讀取重試 {i+1}/{max_retries}...")
            time_module.sleep(delay)
            
        return None

    def _generate_click_sequence(self, target_6dof: List[float], approach_height: float = 30.0) -> List[Dict]:
        """
        生成點擊序列

        Args:
            target_6dof: 目標 6DOF 座標 [x, y, z, rx, ry, rz]
            approach_height: 接近高度 (mm)

        Returns:
            list: 點擊序列 [{"action": ..., "coords": ...}, ...]
        """
        x, y, z, rx, ry, rz = target_6dof
        return [
            {"action": "approach", "coords": [x, y, z + approach_height, rx, ry, rz],
             "description": f"移動到接近位置 (Z+{approach_height}mm)"},
            {"action": "click", "coords": [x, y, z, rx, ry, rz],
             "description": "下壓點擊"},
            {"action": "retract", "coords": [x, y, z + approach_height, rx, ry, rz],
             "description": f"抬起到安全位置 (Z+{approach_height}mm)"},
        ]

    def _execute_click_with_fallback(self, target_6dof: List[float],
                                      fallback_angles: Optional[List[float]] = None,
                                      fallback_lift_offset: List[float] = [10.0, 15.0],
                                      approach_height: float = 30.0,
                                      click_duration: float = 0.1,
                                      speed: int = 20,
                                      z_offset: float = 0.0,
                                      initial_angles: Optional[List[float]] = None,
                                      wrist_first: bool = False) -> Dict:
        """
        執行點擊序列（支援 IK 失敗時的 Fallback，及 IK 引導與手腕優先）

        Args:
            target_6dof: 目標 6DOF 座標
            fallback_angles: 預錄的點擊角度（可選）
            fallback_lift_offset: Fallback 時 J2/J3 抬高偏移 [j2_off, j3_off]
            approach_height: 接近高度 (mm)
            click_duration: 點擊停留時間 (秒)
            speed: 移動速度
            z_offset: Z 軸微調 (mm)
            initial_angles: IK 初始猜測角度 (可選)
            wrist_first: 是否在第一步先對準手腕 (可選)

        Returns:
            dict: 執行結果
        """
        import time as time_module
        start_time = time_module.time()

        # 應用 z_offset
        adjusted_target = list(target_6dof)
        if z_offset != 0:
            adjusted_target[2] += z_offset
            self.logger.info(f"🔧 應用 Z 軸微調: {z_offset}mm")

        # ⚠️ 警告：目前 IK Solver 只支援 XYZ 位置，RPY 姿態會被忽略
        rpy = adjusted_target[3:6] if len(adjusted_target) >= 6 else [0, 0, 0]
        if any(abs(r) > 0.1 for r in rpy) and rpy != [-180.0, 0.0, 0.0]:
            self.logger.warning(f"⚠️ IK 限制: RPY 姿態 {rpy} 被忽略，僅使用 XYZ 位置求解")

        # 生成點擊序列
        click_sequence = self._generate_click_sequence(adjusted_target, approach_height)

        # 檢查 IK Solver 是否可用
        if not self.ik_solver:
            if fallback_angles:
                self.logger.warning("⚠️ IK Solver 不可用，使用 Fallback 模式")
                return self._execute_fallback_click(fallback_angles, fallback_lift_offset,
                                                    click_duration, speed)
            else:
                return {"status": "error", "message": "IK Solver 不可用且無 fallback_angles"}

        # 嘗試 IK 求解所有步驟
        solved_sequences = []
        
        # 決定 IK 的初始猜測
        # 第一步 (Approach) 使用 initial_angles (如果有的話) 或當前角度
        current_angles_raw = self.get_angles()
        
        if initial_angles:
            current_guess = initial_angles
        elif current_angles_raw and None not in current_angles_raw:
            current_guess = current_angles_raw
        else:
            self.logger.warning("無法取得有效當前角度，IK 使用零位作為初始猜測")
            current_guess = [0.0] * 6

        for i, step in enumerate(click_sequence):
            try:
                # 使用 IK 求解器計算角度 (solve_ik 返回 (angles, error))
                # 注意: IKSolver.solve_ik 只接受 (x,y,z) 作為目標
                angles, ik_error = self.ik_solver.solve_ik(
                    step['coords'][:3],  # 取前三個值 (x, y, z)
                    initial_guess=current_guess
                )
                
                if angles is None:
                    raise ValueError(f"IK 求解失敗 (error: {ik_error:.2f}mm)")

                # 檢查 IK 誤差 (Phase 12 目標 < 5mm)
                if ik_error > 5.0:
                    raise ValueError(f"IK 誤差過大: {ik_error:.2f}mm")

                solved_sequences.append({
                    'action': step['action'],
                    'angles': angles,
                    'coords': step['coords'],
                    'description': step['description']
                })
                # 下一步的猜測使用上一步的結果，保證連續性
                current_guess = angles

            except Exception as e:
                self.logger.warning(f"⚠️ IK 求解失敗 ({step['action']}): {e}")

                # 嘗試 Fallback
                if fallback_angles:
                    self.logger.info("🔄 切換到 Fallback 模式")
                    return self._execute_fallback_click(fallback_angles, fallback_lift_offset,
                                                        click_duration, speed)
                else:
                    return {
                        "status": "error",
                        "message": f"IK 求解失敗且無 fallback_angles: {str(e)}",
                        "step": step['action'],
                        "target_coords": step['coords']
                    }

        # 執行 IK 求解成功的序列
        self.logger.info("🚀 開始執行點擊序列 (IK 模式)")
        steps_completed = 0

        for i, step in enumerate(solved_sequences):
            self.logger.info(f"  [{i+1}/{len(solved_sequences)}] {step['description']}")

            # 第一步 (Approach) 支援手腕優先 (Wrist First)
            if i == 0 and wrist_first and current_angles_raw and None not in current_angles_raw:
                self.logger.info("    -> 預先對準手腕 (J4-J6)")
                # 保持 J1-J3 不動，只移動 J4-J6
                intermediate_angles = [
                    current_angles_raw[0], current_angles_raw[1], current_angles_raw[2],
                    step['angles'][3], step['angles'][4], step['angles'][5]
                ]
                self._send_angles_internal(intermediate_angles, speed)
                self._wait_for_arrival(intermediate_angles, threshold=2.0)
                time_module.sleep(0.2)

            # 發送角度命令
            self._send_angles_internal(step['angles'], speed)

            # 等待到達
            self._wait_for_arrival(step['angles'], threshold=1.5)

            # 點擊動作需要停留
            if step['action'] == 'click':
                time_module.sleep(click_duration)

            steps_completed += 1

        total_time = time_module.time() - start_time
        
        # 最終確認：強制讀取當前位置
        final_angles = self._get_angles_with_retry(max_retries=3)
        final_coords = None
        
        if final_angles:
            if self.fk_calculator:
                try:
                    xyz = self.fk_calculator.forward_kinematics(final_angles)
                    # 轉換為標準 Python float 避免 JSON 序列化問題
                    final_coords = [float(c) for c in xyz] + [0.0, 0.0, 0.0]
                except:
                    pass
        
        self.logger.info(f"✅ 點擊完成 (IK 模式, 耗時: {total_time:.2f}s)")

        result = {
            "status": "success",
            "method": "ik",
            "steps_completed": steps_completed,
            "final_angles": final_angles,
            "final_coords": final_coords,
            "total_time_sec": round(total_time, 2)
        }

        # 如果有非預設 RPY，加入警告
        if any(abs(r) > 0.1 for r in rpy) and rpy != [-180.0, 0.0, 0.0]:
            result["rpy_warning"] = f"RPY 姿態 {rpy} 被忽略，僅使用 XYZ 位置求解"

        return result

    def _execute_fallback_click(self, fallback_angles: List[float],
                                 lift_offset: List[float] = [10.0, 15.0],
                                 click_duration: float = 0.1,
                                 speed: int = 20) -> Dict:
        """
        執行 Fallback 模式點擊（使用預錄角度 + J2/J3 調整抬高）

        Args:
            fallback_angles: 預錄的點擊角度
            lift_offset: J2/J3 抬高偏移 [j2_off, j3_off]
            click_duration: 點擊停留時間 (秒)
            speed: 移動速度

        Returns:
            dict: 執行結果
        """
        import time as time_module
        start_time = time_module.time()

        # 計算抬高位置的角度
        approach_angles = list(fallback_angles)
        approach_angles[1] += lift_offset[0]  # J2
        approach_angles[2] += lift_offset[1]  # J3

        self.logger.info("🚀 開始執行點擊序列 (Fallback 模式)")
        self.logger.info(f"   抬高偏移: J2+{lift_offset[0]}°, J3+{lift_offset[1]}°")

        # 1. Approach: 移動到抬高位置
        self.logger.info("  [1/3] 移動到抬高位置")
        self._send_angles_internal(approach_angles, speed)
        self._wait_for_arrival(approach_angles, threshold=1.5)

        # 2. Click: 下壓到目標位置
        self.logger.info("  [2/3] 下壓點擊")
        self._send_angles_internal(fallback_angles, speed)
        self._wait_for_arrival(fallback_angles, threshold=1.5)
        time_module.sleep(click_duration)

        # 3. Retract: 抬起
        self.logger.info("  [3/3] 抬起")
        self._send_angles_internal(approach_angles, speed)
        self._wait_for_arrival(approach_angles, threshold=1.5)

        total_time = time_module.time() - start_time
        
        # 最終確認
        final_angles = self._get_angles_with_retry(max_retries=3)
        final_coords = None
        if final_angles and self.fk_calculator:
            try:
                xyz = self.fk_calculator.forward_kinematics(final_angles)
                final_coords = list(xyz) + [0.0, 0.0, 0.0]
            except:
                pass

        self.logger.info(f"✅ 點擊完成 (Fallback 模式, 耗時: {total_time:.2f}s)")

        return {
            "status": "success",
            "method": "fallback",
            "fallback_reason": "IK 求解失敗或 IK Solver 不可用",
            "steps_completed": 3,
            "final_angles": final_angles,
            "final_coords": final_coords,
            "total_time_sec": round(total_time, 2),
            "warning": "使用預錄角度，精度可能受影響"
        }

    def _send_angles_internal(self, angles: List[float], speed: int) -> bool:
        """
        內部發送角度命令（應用全局補償）

        直接構建 MyCobot 協議命令並發送，避免創建新的 serial 連接。

        協議格式:
        - Header: 0xFE 0xFE
        - Length: 0x0E (14 bytes: 1 command + 12 angles + 1 speed)
        - Command: 0x22 (SEND_ANGLES)
        - Data: 6 個角度 (每個 2 bytes, int16 * 100, big-endian) + 1 byte speed
        - Footer: 0xFA

        Args:
            angles: 目標角度 (邏輯角度)
            speed: 移動速度 (1-100)

        Returns:
            bool: 是否成功
        """
        import struct

        try:
            # 應用全局補償
            final_angles = list(angles)
            if self.correction_enabled:
                final_angles = [a + o for a, o in zip(angles, self.global_offsets)]
                self.logger.info(f"🔧 角度補償: {[round(a,2) for a in angles]} + {self.global_offsets}")
                self.logger.info(f"   -> 發送角度: {[round(a,2) for a in final_angles]}")
            else:
                self.logger.info(f"📤 發送角度 (無補償): {[round(a,2) for a in final_angles]}")

            # 構建 send_angles 命令
            # Header
            command = [0xFE, 0xFE]

            # Length: command(1) + angles(12) + speed(1) + footer(1) = 15
            command.append(0x0F)

            # Command code: SEND_ANGLES = 0x22
            command.append(0x22)

            # Data: 6 angles as int16 * 100 (big-endian)
            for angle in final_angles:
                angle_int = int(angle * 100)
                # 處理負數 (轉換為 unsigned 16-bit)
                if angle_int < 0:
                    angle_int = angle_int + 65536
                # Big-endian: high byte first
                command.append((angle_int >> 8) & 0xFF)
                command.append(angle_int & 0xFF)

            # Speed (1 byte)
            command.append(speed & 0xFF)

            # Footer
            command.append(0xFA)

            # 發送命令
            with self.serial_lock:
                if not self.mc or not self.mc.is_open:
                    self.logger.error("串口未開啟")
                    return False

                self.mc.write(bytes(command))
                self.mc.flush()

            self.logger.info(f"✓ 角度命令已發送，速度: {speed}")
            self.logger.debug(f"   命令: {[hex(b) for b in command]}")
            return True

        except Exception as e:
            self.logger.error(f"發送角度失敗: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return False

    # ==================== JSON 命令處理方法 ====================

    def _handle_json_command(self, cmd: dict) -> dict:
        """處理 JSON 命令"""
        try:
            command_type = cmd.get("command")

            if not command_type:
                return {"status": "error", "message": "缺少 'command' 欄位"}

            # 控制命令
            if command_type == "move_to_angles":
                return self._cmd_move_to_angles(cmd)
            elif command_type == "get_angles":
                return self._cmd_get_angles(cmd)
            elif command_type == "get_coords":
                return self._cmd_get_coords(cmd)
            
            # 補償命令 (v5.0.0)
            elif command_type == "reload_offset":
                self._load_global_offsets()
                return {"status": "success", "offsets": self.global_offsets, "enabled": self.correction_enabled}
            elif command_type == "set_correction":
                self.correction_enabled = bool(cmd.get("enable", True))
                return {"status": "success", "enabled": self.correction_enabled}
            elif command_type == "get_correction_status":
                return {"status": "success", "enabled": self.correction_enabled, "offsets": self.global_offsets}

            # 控制命令 (v5.3.0 Power Control)
            elif command_type == "power_on":
                return self._cmd_power_on(cmd)
            elif command_type == "power_off":
                return self._cmd_power_off(cmd)

            # 視覺命令
            elif command_type == "capture_image":
                return self._cmd_capture_image(cmd)
            elif command_type == "yolo_detect":
                return self._cmd_yolo_detect(cmd)

            # STag 偏移命令 (v5.1.0 Phase 13.5)
            elif command_type == "calculate_stag_offset":
                return self._cmd_calculate_stag_offset(cmd)
            elif command_type == "move_to_angles_with_stag":
                return self._cmd_move_to_angles_with_stag(cmd)
            elif command_type == "enable_stag_offset":
                self.stag_enabled = bool(cmd.get("enable", True))
                return {"status": "success", "enabled": self.stag_enabled}
            elif command_type == "get_stag_offset":
                return {
                    "status": "success",
                    "enabled": self.stag_enabled,
                    "offset": self.stag_offset
                }
            elif command_type == "clear_stag_offset":
                self.stag_offset = [0.0, 0.0, 0.0]
                self.stag_enabled = False
                return {
                    "status": "success",
                    "offset": self.stag_offset,
                    "enabled": False
                }
            elif command_type == "diagnose_stag_offset":
                return self._cmd_diagnose_stag_offset(cmd)

            # 座標點擊控制命令 (v5.2.0 Phase 1)
            elif command_type == "move_to_coords":
                return self._cmd_move_to_coords(cmd)
            elif command_type == "click_target":
                return self._cmd_click_target(cmd)
            elif command_type == "click_relative_to_stag":
                return self._cmd_click_relative_to_stag(cmd)

            else:
                return {"status": "error", "message": f"未知的命令類型: {command_type}"}

        except Exception as e:
            self.logger.error(f"JSON 命令處理失敗: {e}")
            return {"status": "error", "message": str(e)}

    # ========== v4.0.0 已移除的命令 ==========
    # _cmd_detect_button() 已移除，影像判定已遷移至本機端
    # Server 只提供影像截取功能（capture_image）

    def _cmd_get_angles(self, cmd: dict) -> dict:
        """讀取當前手臂角度

        Args:
            cmd: {
                "command": "get_angles"
            }

        Returns:
            {
                "status": "success" | "error",
                "angles": [j1, j2, j3, j4, j5, j6],  # 成功時
                "message": str
            }
        """
        try:
            angles = self.get_angles()

            # 檢查是否有無效角度
            if not angles or None in angles:
                return {
                    "status": "error",
                    "message": "讀取角度失敗",
                    "angles": angles
                }

            return {
                "status": "success",
                "angles": angles,
                "message": "讀取角度成功"
            }

        except Exception as e:
            self.logger.error(f"讀取角度失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_get_coords(self, cmd: dict) -> dict:
        """讀取當前手臂座標 (6DOF)

        Args:
            cmd: {
                "command": "get_coords"
            }

        Returns:
            {
                "status": "success" | "error",
                "coords": [x, y, z, rx, ry, rz],
                "angles": [...],
                "message": str
            }
        """
        try:
            # 1. 獲取角度
            angles = self.get_angles()
            if not angles or None in angles:
                return {
                    "status": "error",
                    "message": "讀取角度失敗，無法計算座標",
                    "angles": angles
                }

            # 2. 檢查 FK 計算器
            if not self.fk_calculator:
                return {
                    "status": "error",
                    "message": "FK 計算器未載入，無法計算座標",
                    "angles": angles
                }

            # 3. 計算 FK (座標 + 姿態)
            # forward_kinematics 只返回 xyz，我们需要 full 才能拿 RPY
            # 假設 fk_calculator 有 forward_kinematics_full 或類似方法
            # 檢查 library/planning/dh_fk_calculator_original.py
            
            # 暫時先用 forward_kinematics 拿 XYZ
            xyz = self.fk_calculator.forward_kinematics(angles)
            
            # TODO: 如果需要 RPY，需要 FK 支援。目前先填 0.0 或擴充 FK
            # 查看 function_spec.md，DHForwardKinematics 有 forward_kinematics_full
            
            try:
                # 嘗試調用完整 FK
                fk_result = self.fk_calculator.forward_kinematics_full(angles)
                # fk_result 格式: {'position': [x,y,z], 'rotation_matrix': ..., 'rpy': [rx,ry,rz]}
                
                coords = [float(c) for c in xyz] + [0.0, 0.0, 0.0] # Fallback
                
                if isinstance(fk_result, dict) and 'rpy' in fk_result:
                     coords = [float(c) for c in xyz] + [float(r) for c in fk_result['rpy']]
                
            except Exception:
                # 如果沒有 full 方法，就只回傳 XYZ + 000
                coords = [float(c) for c in xyz] + [0.0, 0.0, 0.0]

            return {
                "status": "success",
                "coords": [round(c, 2) for c in coords],
                "angles": angles,
                "message": "讀取座標成功"
            }

        except Exception as e:
            self.logger.error(f"讀取座標失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_power_on(self, cmd: dict) -> dict:
        """開啟伺服馬達 (Power On)"""
        try:
            power_on_command = [0xfe, 0xfe, 0x02, 0x10, 0xfa]
            self.write(power_on_command)
            time.sleep(0.1) # Wait for effect
            self.logger.info("已執行 Power On 指令")
            return {"status": "success", "message": "已開啟伺服馬達"}
        except Exception as e:
            self.logger.error(f"Power On 失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_power_off(self, cmd: dict) -> dict:
        """關閉伺服馬達 (Power Off / Release)"""
        try:
            power_off_command = [0xfe, 0xfe, 0x02, 0x11, 0xfa]
            self.write(power_off_command)
            time.sleep(0.1)
            self.logger.info("已執行 Power Off 指令")
            return {"status": "success", "message": "已關閉伺服馬達"}
        except Exception as e:
            self.logger.error(f"Power Off 失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_move_to_angles(self, cmd: dict) -> dict:
        """移動到指定角度 (支援自動補償)

        使用 _send_angles_internal 發送命令，會自動應用全局補償。
        """
        try:
            angles = cmd.get("angles")
            if not angles or len(angles) != 6:
                return {"status": "error", "message": "angles 參數必須包含 6 個關節角度"}

            speed = cmd.get("speed", 50)

            self.logger.info(f"移動到角度: {angles}, 速度: {speed}")

            # 使用 _send_angles_internal 發送命令（會自動應用補償）
            success = self._send_angles_internal(angles, speed)

            if success:
                # 計算補償後的角度用於返回
                final_angles = list(angles)
                if self.correction_enabled:
                    final_angles = [a + o for a, o in zip(angles, self.global_offsets)]
                return {"status": "success", "message": "已發送移動命令", "target_angles": final_angles}
            else:
                return {"status": "error", "message": "發送角度命令失敗"}

        except Exception as e:
            self.logger.error(f"移動命令失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_capture_image(self, cmd: dict) -> dict:
        """截圖並返回 Base64 編碼

        Args:
            cmd: {
                "command": "capture_image",
                "num_frames": int,  # 可選，多幀平均數量（預設 5）
                "format": "jpeg" | "png"  # 可選，預設 jpeg
            }

        Returns:
            {
                "status": "success" | "error",
                "image_base64": str,  # Base64 編碼的圖像
                "format": "jpeg" | "png",
                "message": str
            }
        """
        if not self.enable_vision or not self.camera_capture:
            return {"status": "error", "message": "影像截取系統未啟用"}

        try:
            import base64

            # 多幀平均截圖
            num_frames = cmd.get("num_frames", 5)
            image = self.camera_capture.capture_multi_frame_average(num_frames)

            # 編碼為指定格式
            image_format = cmd.get("format", "jpeg").lower()
            if image_format == "jpeg":
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                success, buffer = cv2.imencode('.jpg', image, encode_param)
            elif image_format == "png":
                success, buffer = cv2.imencode('.png', image)
            else:
                return {"status": "error", "message": f"不支援的圖像格式: {image_format}"}

            if not success:
                return {"status": "error", "message": "圖像編碼失敗"}

            # Base64 編碼
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            return {
                "status": "success",
                "image_base64": image_base64,
                "format": image_format,
                "message": "截圖成功"
            }

        except Exception as e:
            self.logger.error(f"截圖失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_yolo_detect(self, cmd: dict) -> dict:
        """YOLO 物件檢測（v4.3.0）

        Args:
            cmd: {
                "command": "yolo_detect",
                "num_frames": int,       # 可選，多幀平均數量（預設 5）
                "confidence": float,     # 可選，信心度閾值（預設使用模型預設值）
                "save_image": bool,      # 可選，是否儲存圖片（預設 true）
                "return_image": bool     # 可選，是否返回圖片 base64（預設 false）
            }

        Returns:
            {
                "status": "success" | "error",
                "detections": [         # 檢測結果列表
                    {
                        "class": str,
                        "confidence": float,
                        "bbox": {"x": int, "y": int, "w": int, "h": int}
                    }
                ],
                "image_path": str,           # 原始圖路徑（如果 save_image=true）
                "annotated_image_path": str, # 標註圖路徑（如果 save_image=true）
                "image_base64": str,         # 原始圖 base64（如果 return_image=true）
                "annotated_image_base64": str, # 標註圖 base64（如果 return_image=true）
                "metadata": {
                    "model": str,
                    "inference_time_ms": float,
                    "num_frames": int,
                    "num_detections": int
                },
                "message": str
            }
        """
        if not self.enable_yolo or not self.yolo_detector:
            return {"status": "error", "message": "YOLO 檢測系統未啟用"}

        if not self.enable_vision or not self.camera_capture:
            return {"status": "error", "message": "影像截取系統未啟用"}

        try:
            import time

            # 解析參數
            num_frames = cmd.get("num_frames", 5)
            confidence = cmd.get("confidence", None)  # None 表示使用模型預設值
            save_image = cmd.get("save_image", True)
            return_image = cmd.get("return_image", False)

            # 1. 使用現有的多幀平均截圖功能
            self.logger.info(f"正在截取圖像（{num_frames} 幀平均）...")
            image = self.camera_capture.capture_multi_frame_average(num_frames)

            if image is None:
                return {"status": "error", "message": "圖像截取失敗"}

            # 2. 執行 YOLO 檢測
            start_time = time.time()
            detections = self.yolo_detector.detect(image, confidence=confidence)
            inference_time = (time.time() - start_time) * 1000  # 毫秒

            self.logger.info(f"YOLO 檢測完成：檢測到 {len(detections)} 個物件")

            # 3. 準備返回結果
            result = {
                "status": "success",
                "detections": detections,
                "metadata": {
                    "model": self.yolo_model_path,
                    "inference_time_ms": round(inference_time, 2),
                    "num_frames": num_frames,
                    "num_detections": len(detections)
                },
                "message": f"檢測完成，找到 {len(detections)} 個物件"
            }

            # 4. 儲存圖片（如果需要）
            if save_image:
                try:
                    original_path, annotated_path = self.yolo_detector.save_results(
                        image, detections
                    )
                    result["image_path"] = original_path
                    result["annotated_image_path"] = annotated_path
                except Exception as e:
                    self.logger.warning(f"圖片儲存失敗: {e}")
                    result["save_error"] = str(e)

            # 5. 返回圖片 base64（如果需要）
            if return_image:
                try:
                    # 原始圖
                    _, buffer = cv2.imencode('.jpg', image)
                    result["image_base64"] = base64.b64encode(buffer).decode('utf-8')

                    # 標註圖
                    annotated_image = self.yolo_detector.draw_boxes(image, detections)
                    _, buffer = cv2.imencode('.jpg', annotated_image)
                    result["annotated_image_base64"] = base64.b64encode(buffer).decode('utf-8')
                except Exception as e:
                    self.logger.warning(f"圖片編碼失敗: {e}")
                    result["encoding_error"] = str(e)

            return result

        except Exception as e:
            self.logger.error(f"YOLO 檢測失敗: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    # ==================== STag 偏移命令處理方法 (v5.1.0 Phase 13.5) ====================

    def _cmd_calculate_stag_offset(self, cmd: dict) -> dict:
        """計算 STag 偏移

        Args:
            cmd: {
                "command": "calculate_stag_offset",
                "marker_id": int,                         # 目標 STag ID
                "reference_position": [x, y, z],          # 參考位置 (mm)
                "observe_angles": [j1, j2, j3, j4, j5, j6],  # 可選：觀測角度
                "num_frames": int                         # 可選：平均幀數（預設 5）
            }

        Returns:
            {
                "status": "success" | "error",
                "offset": [dx, dy, dz],
                "detected_position": [x, y, z],
                "reference_position": [x, y, z],
                "marker_id": int,
                "detection_mode": "real" | "sample"
            }
        """
        marker_id = cmd.get("marker_id", 0)
        reference_pos = cmd.get("reference_position", [150.0, 80.0, 120.0])
        num_frames = cmd.get("num_frames", 5)

        # 檢查 STag 檢測器是否可用
        if not self.stag_detector:
            # STag 檢測器不可用，返回示例數據用於測試框架
            self.logger.warning("⚠️ STag 檢測器不可用，返回示例偏移數據")
            detected_pos = [
                reference_pos[0] + 2.5,
                reference_pos[1] - 1.8,
                reference_pos[2] + 0.3
            ]
            offset = [
                detected_pos[0] - reference_pos[0],
                detected_pos[1] - reference_pos[1],
                detected_pos[2] - reference_pos[2]
            ]
            self.stag_offset = offset
            return {
                "status": "success",
                "offset": offset,
                "detected_position": detected_pos,
                "reference_position": reference_pos,
                "marker_id": marker_id,
                "detection_mode": "sample",
                "message": "偏移計算完成（示例數據，STag 檢測器不可用）"
            }

        # 檢查攝影機是否可用
        if not self.camera_capture:
            return {
                "status": "error",
                "message": "攝影機不可用",
                "offset": [0.0, 0.0, 0.0]
            }

        try:
            # 擷取影像
            self.logger.info(f"📷 擷取影像進行 STag 檢測 (marker_id={marker_id}, frames={num_frames})")
            with self.camera_lock:
                image = self.camera_capture.capture_multi_frame_average(num_frames)

            if image is None:
                return {
                    "status": "error",
                    "message": "影像擷取失敗",
                    "offset": [0.0, 0.0, 0.0]
                }

            # 執行 STag 檢測
            results = self.stag_detector.detect_markers(image)

            if results['markers_found'] == 0:
                self.logger.warning(f"⚠️ 未檢測到任何 STag 標記")
                return {
                    "status": "error",
                    "message": "未檢測到 STag 標記",
                    "offset": [0.0, 0.0, 0.0],
                    "markers_found": 0
                }

            # 尋找指定的 marker_id
            target_marker = None
            for marker in results['markers']:
                if marker['id'] == marker_id:
                    target_marker = marker
                    break

            if not target_marker:
                detected_ids = [m['id'] for m in results['markers']]
                self.logger.warning(f"⚠️ 未找到 marker_id={marker_id}，已檢測到: {detected_ids}")
                return {
                    "status": "error",
                    "message": f"未找到 marker_id={marker_id}",
                    "detected_ids": detected_ids,
                    "offset": [0.0, 0.0, 0.0]
                }

            # 提取檢測到的位置 (相機座標系，單位：米 → 毫米)
            pos_3d = target_marker['position_3d']
            detected_pos = [
                pos_3d['x'] * 1000.0,  # 米 → 毫米
                pos_3d['y'] * 1000.0,
                pos_3d['z'] * 1000.0
            ]

            # 計算偏移（檢測位置 - 參考位置）
            offset = [
                detected_pos[0] - reference_pos[0],
                detected_pos[1] - reference_pos[1],
                detected_pos[2] - reference_pos[2]
            ]

            # 存儲偏移值與參考資訊
            self.stag_offset = offset
            self.stag_reference = {
                "marker_id": marker_id,
                "reference_position": reference_pos,
                "detected_position": detected_pos,
                "detection_quality": target_marker.get('detection_quality', 1.0),
                "distance_mm": target_marker.get('distance_mm', 0)
            }

            self.logger.info(f"✅ STag 偏移計算完成:")
            self.logger.info(f"   Marker ID: {marker_id}")
            self.logger.info(f"   參考位置: {reference_pos}")
            self.logger.info(f"   檢測位置: [{detected_pos[0]:.2f}, {detected_pos[1]:.2f}, {detected_pos[2]:.2f}]")
            self.logger.info(f"   偏移量: [{offset[0]:.2f}, {offset[1]:.2f}, {offset[2]:.2f}] mm")

            return {
                "status": "success",
                "offset": offset,
                "detected_position": detected_pos,
                "reference_position": reference_pos,
                "marker_id": marker_id,
                "detection_mode": "real",
                "detection_quality": target_marker.get('detection_quality', 1.0),
                "distance_mm": target_marker.get('distance_mm', 0),
                "message": "STag 偏移計算完成"
            }

        except Exception as e:
            self.logger.error(f"❌ STag 偏移計算失敗: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "message": f"STag 偏移計算異常: {str(e)}",
                "offset": [0.0, 0.0, 0.0]
            }

    def _cmd_move_to_angles_with_stag(self, cmd: dict) -> dict:
        """帶 STag 偏移的移動命令

        Args:
            cmd: {
                "command": "move_to_angles_with_stag",
                "angles": [j1, j2, j3, j4, j5, j6],
                "speed": int,
                "apply_stag": bool  # 是否應用 STag 偏移
            }

        Returns:
            {
                "status": "success" | "error",
                "final_angles": [...],
                "stag_applied": bool,
                "ik_error": float,  # 如果應用了 STag
                "fallback": bool    # 如果 IK 失敗回退
            }
        """
        try:
            # 1. 檢查是否應用 STag 偏移
            apply_stag = cmd.get("apply_stag", False)

            if not apply_stag or not self.stag_enabled:
                # 不應用 STag，直接調用原始命令
                self.logger.info("不應用 STag 偏移，使用原始角度")
                return self._cmd_move_to_angles(cmd)

            # 2. 檢查 FK/IK 是否可用
            if not self.fk_calculator or not self.ik_solver:
                return {
                    "status": "error",
                    "message": "FK/IK 系統未載入，STag 偏移功能不可用"
                }

            # 3. 執行 FK → 偏移 → IK 流程
            angles = cmd.get("angles")
            if not angles or len(angles) != 6:
                return {"status": "error", "message": "angles 參數必須包含 6 個關節角度"}

            try:
                # 3.1 FK: 角度 → 位置
                target_pos = self.fk_calculator.forward_kinematics(angles)
                self.logger.info(f"📍 FK 計算目標位置: {target_pos}")

                # 3.2 應用 STag 偏移（位置空間）
                corrected_pos = [
                    target_pos[0] + self.stag_offset[0],
                    target_pos[1] + self.stag_offset[1],
                    target_pos[2] + self.stag_offset[2]
                ]
                self.logger.info(f"🎯 STag 校正後位置: {corrected_pos}")
                self.logger.info(f"   偏移量: {self.stag_offset}")

                # 3.3 IK: 位置 → 角度
                corrected_angles, ik_error = self.ik_solver.solve_ik(
                    corrected_pos,
                    initial_guess=angles,
                    tolerance=5.0
                )

                self.logger.info(f"🔧 IK 求解誤差: {ik_error:.2f}mm")

                # 3.4 錯誤檢查：IK 失敗或誤差過大時回退
                if ik_error > 5.0:  # Phase 12 IK 精度目標 < 5mm
                    self.logger.warning(f"⚠️ IK 誤差過大 ({ik_error:.2f}mm > 5mm)，回退到原始角度")
                    result = self._cmd_move_to_angles(cmd)
                    result["stag_applied"] = False
                    result["fallback"] = True
                    result["fallback_reason"] = f"IK error {ik_error:.2f}mm exceeds 5mm threshold"
                    return result

                # 3.5 使用校正後的角度調用現有命令
                corrected_cmd = cmd.copy()
                corrected_cmd["angles"] = corrected_angles
                result = self._cmd_move_to_angles(corrected_cmd)

                # 3.6 附加 STag 資訊
                if result.get("status") == "success":
                    result["stag_applied"] = True
                    result["ik_error"] = round(ik_error, 2)
                    result["original_angles"] = angles
                    result["corrected_angles"] = corrected_angles
                    result["position_offset"] = self.stag_offset
                    self.logger.info(f"✅ STag 偏移移動成功，IK 誤差: {ik_error:.2f}mm")

                return result

            except Exception as e:
                self.logger.error(f"STag 偏移處理失敗: {e}")
                self.logger.warning("回退到原始命令")
                # 發生任何錯誤時，回退到原始命令
                result = self._cmd_move_to_angles(cmd)
                result["stag_applied"] = False
                result["fallback"] = True
                result["fallback_reason"] = str(e)
                return result

        except Exception as e:
            self.logger.error(f"move_to_angles_with_stag 失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_diagnose_stag_offset(self, cmd: dict) -> dict:
        """診斷 STag 偏移是否合理

        Returns:
            {
                "status": "success",
                "offset": [x, y, z],
                "magnitude": float,          # 偏移量大小（mm）
                "is_reasonable": bool,       # 是否在合理範圍內
                "warning": str | None,       # 警告訊息
                "enabled": bool
            }
        """
        import math

        offset = self.stag_offset
        magnitude = math.sqrt(sum(o**2 for o in offset))

        # 判斷是否合理（經驗閾值）
        is_reasonable = magnitude < 20.0  # 偏移 > 20mm 可能有問題
        warning = None

        if magnitude > 20.0:
            warning = f"偏移量過大 ({magnitude:.2f}mm)，可能校準錯誤"
            self.logger.warning(f"⚠️ {warning}")
        elif magnitude < 0.5:
            warning = f"偏移量極小 ({magnitude:.2f}mm)，可能不需要偏移"
            self.logger.info(f"ℹ️ {warning}")
        else:
            self.logger.info(f"✅ 偏移量合理: {magnitude:.2f}mm")

        return {
            "status": "success",
            "offset": offset,
            "magnitude": round(magnitude, 2),
            "is_reasonable": is_reasonable,
            "warning": warning,
            "enabled": self.stag_enabled
        }

    # ==================== Phase 1: 座標點擊控制命令 (v5.2.0) ====================

    def _cmd_move_to_coords(self, cmd: dict) -> dict:
        """
        移動到指定座標（使用 IK 求解）

        Args:
            cmd: {
                "command": "move_to_coords",
                "coords": [x, y, z, rx, ry, rz],  # 6DOF 座標
                "speed": int,                     # 可選，預設 20
                "initial_angles": [j1,...,j6]     # 可選，IK 初始猜測
            }

        Returns:
            {
                "status": "success" | "error",
                "target_coords": [...],
                "solved_angles": [...],
                "ik_error_mm": float
            }
        """
        try:
            coords = cmd.get("coords")
            if not coords or len(coords) != 6:
                return {"status": "error", "message": "coords 參數必須包含 6 個座標值 [x, y, z, rx, ry, rz]"}

            speed = cmd.get("speed", 20)
            wrist_first = bool(cmd.get("wrist_first", False))
            
            # 獲取當前角度作為 IK 初始猜測
            current_angles_raw = self.get_angles()
            # 嚴格檢查：如果是 None 或包含 None，則使用零位
            if not current_angles_raw or None in current_angles_raw:
                self.logger.warning("無法取得有效當前角度，IK 使用零位作為初始猜測")
                initial_guess = [0.0] * 6
            else:
                initial_guess = current_angles_raw

            if cmd.get("initial_angles"):
                initial_guess = cmd.get("initial_angles")

            # 檢查 IK Solver
            if not self.ik_solver:
                return {"status": "error", "message": "IK Solver 不可用"}

            # IK 求解
            self.logger.info(f"🎯 移動到座標: {coords} (wrist_first={wrist_first})")

            # ⚠️ 警告：目前 IK Solver 只支援 XYZ 位置，RPY 姿態會被忽略
            rpy = coords[3:6] if len(coords) >= 6 else [0, 0, 0]
            if any(abs(r) > 0.1 for r in rpy) and rpy != [-180.0, 0.0, 0.0]:
                self.logger.warning(f"⚠️ IK 限制: RPY 姿態 {rpy} 被忽略，僅使用 XYZ 位置求解")

            try:
                solved_angles, ik_error = self.ik_solver.solve_ik(
                    coords[:3],  # 取前三個值 (x, y, z)
                    initial_guess=initial_guess
                )

                if solved_angles is None:
                    return {"status": "error", "message": f"IK 求解失敗: 無解 (誤差: {ik_error:.2f}mm)"}
                
                # 檢查 IK 誤差 (Phase 12 目標 < 5mm)
                if ik_error > 5.0:
                    self.logger.warning(f"⚠️ IK 誤差過大: {ik_error:.2f}mm")
                    
            except Exception as e:
                return {"status": "error", "message": f"IK 求解異常: {str(e)}"}

            # 確保機器手臂已上電
            self._cmd_power_on({})

            # --- 兩段式移動邏輯 ---
            if wrist_first and current_angles_raw and None not in current_angles_raw:
                self.logger.info("第一階段: 預先對準手腕 (J4, J5, J6)")
                # 保持 J1-J3 不動，只移動 J4-J6
                intermediate_angles = [
                    current_angles_raw[0], current_angles_raw[1], current_angles_raw[2],
                    solved_angles[3], solved_angles[4], solved_angles[5]
                ]
                self._send_angles_internal(intermediate_angles, speed)
                self._wait_for_arrival(intermediate_angles, threshold=2.0)
                time.sleep(0.2)

            self.logger.info("第二階段: 移動到目標位置")
            self._send_angles_internal(solved_angles, speed)
            self._wait_for_arrival(solved_angles, threshold=1.5)

            # 最終確認：強制讀取當前位置
            final_angles = self._get_angles_with_retry(max_retries=3)
            final_coords = None
            
            if final_angles:
                # 計算實際座標
                if self.fk_calculator:
                    try:
                        xyz = self.fk_calculator.forward_kinematics(final_angles)
                        # 轉換為標準 Python float 避免 JSON 序列化問題
                        final_coords = [float(c) for c in xyz] + [0.0, 0.0, 0.0]
                        self.logger.info(f"📍 最終確認位置: {[round(c, 2) for c in final_coords[:3]]}")
                    except:
                        pass
            else:
                self.logger.warning("⚠️ 無法確認最終位置")

            self.logger.info(f"✅ 移動完成，IK 誤差: {ik_error:.2f}mm")

            result = {
                "status": "success",
                "target_coords": coords,
                "solved_angles": [round(a, 2) for a in solved_angles],
                "final_angles": final_angles,
                "final_coords": final_coords,
                "ik_error_mm": round(ik_error, 2)
            }

            # 如果有非預設 RPY，加入警告
            if any(abs(r) > 0.1 for r in rpy) and rpy != [-180.0, 0.0, 0.0]:
                result["rpy_warning"] = f"RPY 姿態 {rpy} 被忽略，僅使用 XYZ 位置求解"

            return result

        except Exception as e:
            self.logger.error(f"move_to_coords 失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_click_target(self, cmd: dict) -> dict:
        """
        執行點擊目標（approach → click → retract）

        Args:
            cmd: {
                "command": "click_target",
                "coords": [x, y, z, rx, ry, rz],      # 目標 6DOF 座標
                "fallback_angles": [j1,...,j6],      # 可選，預錄角度
                "fallback_lift_offset": [j2, j3],    # 可選，Fallback 抬高偏移
                "approach_height": float,            # 可選，預設 30.0
                "click_duration": float,             # 可選，預設 0.1
                "speed": int,                        # 可選，預設 20
                "z_offset": float,                   # 可選，預設 0.0
                "initial_angles": [j1,...,j6],       # 可選，IK 初始猜測
                "wrist_first": bool                  # 可選，是否先對準手腕
            }

        Returns:
            {
                "status": "success" | "error",
                "method": "ik" | "fallback",
                "steps_completed": int,
                "total_time_sec": float
            }
        """
        try:
            coords = cmd.get("coords")
            if not coords or len(coords) != 6:
                return {"status": "error", "message": "coords 參數必須包含 6 個座標值 [x, y, z, rx, ry, rz]"}

            # 解析參數
            fallback_angles = cmd.get("fallback_angles")
            fallback_lift_offset = cmd.get("fallback_lift_offset", [10.0, 15.0])
            approach_height = cmd.get("approach_height", 30.0)
            click_duration = cmd.get("click_duration", 0.1)
            speed = cmd.get("speed", 20)
            z_offset = cmd.get("z_offset", 0.0)
            initial_angles = cmd.get("initial_angles")
            wrist_first = bool(cmd.get("wrist_first", False))

            # 參數驗證
            if approach_height <= 0:
                return {"status": "error", "message": "參數驗證失敗: approach_height 必須 > 0"}
            if click_duration < 0:
                return {"status": "error", "message": "參數驗證失敗: click_duration 必須 >= 0"}

            self.logger.info(f"🎯 點擊目標: {coords[:3]} (wrist_first={wrist_first})")

            # 執行點擊
            result = self._execute_click_with_fallback(
                target_6dof=coords,
                fallback_angles=fallback_angles,
                fallback_lift_offset=fallback_lift_offset,
                approach_height=approach_height,
                click_duration=click_duration,
                speed=speed,
                z_offset=z_offset,
                initial_angles=initial_angles,
                wrist_first=wrist_first
            )

            return result

        except Exception as e:
            self.logger.error(f"click_target 失敗: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    def _cmd_click_relative_to_stag(self, cmd: dict) -> dict:
        """
        點擊 STag 相對位置

        Args:
            cmd: {
                "command": "click_relative_to_stag",
                "stag_id": int,                      # STag ID
                "offset": [dx, dy, dz],              # 相對偏移 (mm)
                "target_rpy": [rx, ry, rz],          # 可選，目標姿態
                "approach_height": float,            # 可選，預設 30.0
                "click_duration": float,             # 可選，預設 0.1
                "speed": int,                        # 可選，預設 20
                "z_offset": float,                   # 可選，預設 0.0
                "wrist_first": bool                  # 可選，是否先對準手腕
            }

        Returns:
            {
                "status": "success" | "error",
                "stag_id": int,
                "stag_base_position": [x, y, z],
                "calculated_target": [x, y, z, rx, ry, rz],
                "method": "ik" | "fallback",
                "steps_completed": int
            }
        """
        try:
            stag_id = cmd.get("stag_id")
            if stag_id is None:
                return {"status": "error", "message": "缺少 stag_id 參數"}

            offset = cmd.get("offset")
            if not offset or len(offset) != 3:
                return {"status": "error", "message": "offset 參數必須包含 3 個值 [dx, dy, dz]"}

            # 載入 Zone 配置
            zone = self._load_zone_config(stag_id)
            if not zone:
                return {"status": "error", "message": f"Zone 配置不存在: zone_{stag_id}.json"}

            # 解析參數
            target_rpy = cmd.get("target_rpy") or list(zone['rpy'])
            approach_height = cmd.get("approach_height", 30.0)
            click_duration = cmd.get("click_duration", 0.1)
            speed = cmd.get("speed", 20)
            z_offset = cmd.get("z_offset", 0.0)
            wrist_first = bool(cmd.get("wrist_first", False))

            # 計算絕對座標
            base_pos = zone['pos']
            target_pos = [
                base_pos[0] + offset[0],
                base_pos[1] + offset[1],
                base_pos[2] + offset[2]
            ]
            target_6dof = target_pos + list(target_rpy)

            self.logger.info(f"🎯 STag {stag_id} 相對點擊:")
            self.logger.info(f"   基準位置: {list(base_pos)}")
            self.logger.info(f"   偏移: {offset}")
            self.logger.info(f"   目標: {target_6dof}")

            # 使用 Zone 中的角度作為 fallback
            # ⚠️ 注意：fallback_angles 是 Zone 中心點的角度，不包含 offset 偏移
            fallback_angles = zone.get('angles')
            fallback_lift_offset = cmd.get("fallback_lift_offset", [10.0, 15.0])

            # 檢查是否有非零偏移量
            has_offset = any(abs(o) > 0.1 for o in offset)
            if has_offset and fallback_angles:
                self.logger.warning(f"⚠️ Fallback 警告: 偏移量 {offset} 將被忽略！")
                self.logger.warning(f"   Fallback 模式只能點擊 Zone {stag_id} 中心位置")

            # 執行點擊
            result = self._execute_click_with_fallback(
                target_6dof=target_6dof,
                fallback_angles=fallback_angles,
                fallback_lift_offset=fallback_lift_offset,
                approach_height=approach_height,
                click_duration=click_duration,
                speed=speed,
                z_offset=z_offset,
                # 對於相對點擊，如果 Zone 有預錄角度，我們也可以試著用它當作 IK 初始猜測
                initial_angles=fallback_angles, 
                wrist_first=wrist_first
            )

            # 附加 STag 資訊
            if result.get("status") == "success":
                result["stag_id"] = stag_id
                result["stag_base_position"] = [round(p, 2) for p in base_pos]
                result["calculated_target"] = [round(c, 2) for c in target_6dof]

                # 如果使用 Fallback 且有偏移量，加入警告
                if result.get("method") == "fallback" and has_offset:
                    result["offset_warning"] = f"偏移量 {offset} 被忽略，實際點擊 Zone {stag_id} 中心位置"
                    self.logger.warning(f"⚠️ {result['offset_warning']}")

            return result

        except Exception as e:
            self.logger.error(f"click_relative_to_stag 失敗: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    def connect(self):
        """主連接循環，處理客戶端請求"""
        while self.is_running:
            conn = None
            try:
                self.logger.info("等待客戶端連接...")
                print("waiting connect!------------------")
                self.s.settimeout(1.0)  # 設置 accept 超時，允許定期檢查 is_running

                try:
                    conn, addr = self.s.accept()
                except socket.timeout:
                    continue  # 超時後繼續循環，檢查 is_running

                self.logger.info(f"客戶端已連接，來自 {addr}")
                conn.settimeout(self.socket_timeout)  # 使用可配置的超時時間

                while self.is_running:
                    try:
                        print("waiting data--------")
                        data = conn.recv(1024)

                        if not data:
                            self.logger.info("客戶端斷開連接（無數據）")
                            print("close disconnect!")
                            break

                        # 嘗試解析為 JSON 命令
                        try:
                            data_str = data.decode('utf-8')
                            json_cmd = json.loads(data_str)

                            # 如果是 JSON 且包含 "command" 欄位，則處理為 JSON 命令
                            if isinstance(json_cmd, dict) and "command" in json_cmd:
                                self.logger.info(f"收到 JSON 命令: {json_cmd['command']}")
                                result = self._handle_json_command(json_cmd)

                                # 返回 JSON 結果
                                result_str = json.dumps(result, ensure_ascii=False)
                                conn.sendall(result_str.encode('utf-8'))
                                continue

                        except (UnicodeDecodeError, json.JSONDecodeError):
                            # 不是 JSON 格式，按原有二進制命令處理
                            pass

                        command = list(data)

                        # 驗證命令長度
                        if len(command) < 4:
                            self.logger.warning(f"命令長度不足（{len(command)} bytes），忽略此命令")
                            continue

                        # 檢查串口健康狀態
                        if not self._check_serial_health():
                            self.logger.warning("串口不健康，嘗試重新連接")
                            if not self._reconnect_serial():
                                error_msg = "串口不可用"
                                conn.sendall(str.encode(error_msg))
                                break

                        # 確保串口開啟
                        with self.serial_lock:
                            if self.mc and not self.mc.is_open:
                                try:
                                    self.mc.open()
                                    self.logger.info("串口已重新開啟")
                                except Exception as e:
                                    self.logger.error(f"無法重新開啟串口: {e}")
                                    if not self._reconnect_serial():
                                        error_msg = f"串口錯誤: {str(e)}"
                                        conn.sendall(str.encode(error_msg))
                                        break

                            self.logger.info("收到命令: {}".format([hex(v) for v in command]))

                            # 處理 GPIO 命令（如果可用）
                            if GPIO_AVAILABLE and len(command) > 3:
                                try:
                                    if command[3] == 170:
                                        if command[4] == 0:
                                            GPIO.setmode(GPIO.BCM)
                                        else:
                                            GPIO.setmode(GPIO.BOARD)
                                    elif command[3] == 171:
                                        if command[5]:
                                            GPIO.setup(command[4], GPIO.OUT)
                                        else:
                                            GPIO.setup(command[4], GPIO.IN)
                                    elif command[3] == 172:
                                        GPIO.output(command[4], command[5])
                                    elif command[3] == 173:
                                        res = bytes([GPIO.input(command[4])])
                                        conn.sendall(res)
                                        continue
                                except Exception as e:
                                    self.logger.error(f"GPIO 命令錯誤: {e}")

                            # 寫入串口命令
                            try:
                                self.write(command)
                            except serial.SerialException as e:
                                self.logger.error(f"串口寫入錯誤: {e}")
                                if not self._reconnect_serial():
                                    error_msg = f"串口寫入失敗: {str(e)}"
                                    conn.sendall(str.encode(error_msg))
                                    break
                                # 重試寫入
                                self.write(command)

                            # 讀取回應
                            if len(command) > 3 and command[3] in has_return:
                                try:
                                    res = self.read(command)
                                    if res:
                                        self.logger.info("回應數據: {}".format([hex(v) for v in res]))
                                        conn.sendall(res)
                                    else:
                                        self.logger.warning("未收到回應數據")
                                except serial.SerialException as e:
                                    self.logger.error(f"串口讀取錯誤: {e}")
                                    if not self._reconnect_serial():
                                        error_msg = f"串口讀取失敗: {str(e)}"
                                        conn.sendall(str.encode(error_msg))
                                        break

                    except socket.timeout:
                        self.logger.warning("Socket 接收超時")
                        continue
                    except Exception as e:
                        self.logger.error(f"命令處理錯誤: {traceback.format_exc()}")
                        try:
                            conn.sendall(str.encode(f"錯誤: {str(e)}"))
                        except:
                            pass
                        break

            except KeyboardInterrupt:
                self.logger.info("伺服器被使用者中斷")
                self.is_running = False
                break
            except Exception as e:
                self.logger.error(f"連接錯誤: {traceback.format_exc()}")
            finally:
                if conn:
                    try:
                        conn.close()
                        self.logger.info("客戶端連接已關閉")
                    except:
                        pass

        # 清理資源
        self._cleanup()

    def write(self, command):
        """寫入命令到串口"""
        with self.serial_lock:
            if not self.mc or not self.mc.is_open:
                raise serial.SerialException("串口未開啟")
            try:
                self.mc.write(command)
                self.mc.flush()
                self.logger.debug(f"命令已寫入: {[hex(v) for v in command]}")
            except serial.SerialException as e:
                self.logger.error(f"寫入失敗: {e}")
                raise

    def read(self, command, max_retries=3):
        """讀取串口回應，增加錯誤處理、重試和指令碼驗證機制"""
        with self.serial_lock:
            if not self.mc or not self.mc.is_open:
                raise serial.SerialException("串口未開啟")

            for retry in range(max_retries):
                try:
                    datas = b""
                    data_len = -1
                    k = 0
                    pre = 0
                    t = time.time()
                    wait_time = self.read_timeout  # 使用可配置的讀取超時時間

                    while time.time() - t < wait_time:
                        try:
                            data = self.mc.read(1)  # 一次讀取一個字節

                            if not data:  # 沒有數據
                                time.sleep(0.001)  # 短暫等待
                                continue

                            k += 1
                            if data_len == 1 and data == b"\xfa":
                                datas += data
                                # 處理指令回顯 (echo)
                                if [i for i in datas] == command:
                                    datas = b''
                                    data_len = -1
                                    k = 0
                                    pre = 0
                                    continue
                                
                                # 驗證回應的指令碼是否與請求的指令碼相符
                                if len(datas) > 3 and datas[3] == command[3]:
                                    # 指令碼相符，是有效的回應
                                    break
                                else:
                                    # 指令碼不符，記錄並丟棄此封包，繼續監聽
                                    self.logger.warning(f"收到不匹配的回應。期望指令碼 {hex(command[3])}，收到: {[hex(v) for v in datas]}")
                                    datas = b''
                                    data_len = -1
                                    k = 0
                                    pre = 0
                                    continue

                            elif len(datas) == 2:
                                data_len = struct.unpack("b", data)[0]
                                datas += data
                            elif len(datas) > 2 and data_len > 0:
                                datas += data
                                data_len -= 1
                            elif data == b"\xfe":
                                if datas == b"":
                                    datas += data
                                    pre = k
                                else:
                                    if k - 1 == pre:
                                        datas += data
                                    else:
                                        datas = b"\xfe"
                                        pre = k
                        except serial.SerialException as e:
                            self.logger.error(f"數據收集過程中發生讀取錯誤: {e}")
                            raise

                    # while 迴圈結束，如果 datas 有內容，表示收到了有效回應
                    if datas:
                        return datas

                    if retry < max_retries - 1:
                        self.logger.warning(f"未收到有效數據，重試 {retry + 1}/{max_retries}")
                        time.sleep(0.05)
                    else:
                        self.logger.warning("所有重試後仍未收到有效數據")
                        return b''

                except serial.SerialException as e:
                    if retry < max_retries - 1:
                        self.logger.warning(f"讀取時發生串口異常，重試 {retry + 1}/{max_retries}: {e}")
                        time.sleep(0.1)
                    else:
                        self.logger.error(f"所有重試後串口讀取失敗: {e}")
                        raise

            return b''

    def re_data_2(self, command):
        """解析命令字串（舊版兼容，未使用）"""
        r2 = re.compile(r'[[](.*?)[]]')
        data_str = re.findall(r2, command)[0]
        data_list = data_str.split(",")
        data_list = [int(i) for i in data_list]
        return data_list

    def _cleanup(self):
        """清理資源"""
        self.logger.info("正在清理資源...")
        try:
            if self.mc and self.mc.is_open:
                # 釋放伺服馬達
                try:
                    power_off_command = [0xfe, 0xfe, 0x02, 0x11, 0xfa] # power_off 指令
                    self.write(power_off_command)
                    self.logger.info("已發送伺服馬達斷電指令 (power_off)")
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"關閉時發送斷電指令失敗: {e}")

                self.mc.close()
                self.logger.info("串口已關閉")
        except Exception as e:
            self.logger.error(f"關閉串口時發生錯誤: {e}")

        try:
            self.s.close()
            self.logger.info("Socket 已關閉")
        except Exception as e:
            self.logger.error(f"關閉 Socket 時發生錯誤: {e}")

        # 釋放文件鎖
        if self.serial_lock_file:
            try:
                fcntl.flock(self.serial_lock_file, fcntl.LOCK_UN)
                self.serial_lock_file.close()
                self.logger.info("序列埠文件鎖已釋放")
            except Exception as e:
                self.logger.error(f"釋放文件鎖時發生錯誤: {e}")

        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                self.logger.info("GPIO 已清理")
            except Exception as e:
                self.logger.error(f"清理 GPIO 時發生錯誤: {e}")

    def shutdown(self):
        """優雅關閉伺服器"""
        self.logger.info("正在關閉伺服器...")
        self.is_running = False

        # 停止 HTTP API Server（v4.2.0）
        if self.http_server:
            try:
                self.http_server.stop()
            except Exception as e:
                self.logger.error(f"停止 HTTP API Server 時發生錯誤: {e}")

        self._cleanup()


def get_ip_address(ifname='wlan0'):
    """獲取網路介面 IP 地址，支援備用介面"""
    interfaces = [ifname, 'eth0', 'wlan0', 'en0', 'eth1']

    for iface in interfaces:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(iface, encoding="utf8"))
            )[20:24])
            s.close()
            print(f"Using network interface: {iface}")
            return ip
        except Exception as e:
            continue

    # 如果所有介面都失敗，使用 localhost
    print("Warning: Could not find network interface, using localhost")
    return "0.0.0.0"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='MyCobot Robot Arm Server')
    parser.add_argument('--host', type=str, default=None,
                        help='Server host IP (default: auto-detect)')
    parser.add_argument('--port', type=int, default=9000,
                        help='Server port (default: 9000)')
    parser.add_argument('--serial', type=str, default='/dev/ttyTHS1',
                        help='Serial port device (default: /dev/ttyTHS1)')
    parser.add_argument('--baud', type=int, default=1000000,
                        help='Serial baud rate (default: 1000000)')
    parser.add_argument('--interface', type=str, default='wlan0',
                        help='Network interface for auto IP detection (default: wlan0)')
    parser.add_argument('--reconnect-interval', type=int, default=2,
                        help='Reconnection interval in seconds (default: 2)')
    parser.add_argument('--max-reconnect-attempts', type=int, default=5,
                        help='Maximum reconnection attempts (default: 5)')
    parser.add_argument('--read-timeout', type=float, default=0.2,
                        help='Serial read timeout in seconds (default: 0.2)')
    parser.add_argument('--socket-timeout', type=float, default=30.0,
                        help='Socket receive timeout in seconds (default: 30.0)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--disable-vision', action='store_true',
                        help='Disable vision detection system (default: enabled)')
    parser.add_argument('--enable-http', action='store_true',
                        help='Enable HTTP API Server (v4.2.0, default: disabled)')
    parser.add_argument('--http-port', type=int, default=8000,
                        help='HTTP API Server port (default: 8000)')

    args = parser.parse_args()

    # 轉換日誌級別
    log_level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR
    }
    log_level = log_level_map[args.log_level]

    # 獲取 IP 地址
    if args.host:
        HOST = args.host
    else:
        HOST = get_ip_address(args.interface)

    PORT = args.port

    print("=" * 50)
    print("MyCobot Robot Arm Server - Enhanced Version (v4.2.0)")
    print("=" * 50)
    print(f"Server IP:        {HOST}")
    print(f"Socket Port:      {PORT}")
    print(f"Serial Port:      {args.serial}")
    print(f"Baud Rate:        {args.baud}")
    print(f"Vision Enabled:   {not args.disable_vision}")
    print(f"HTTP API Enabled: {args.enable_http}")
    if args.enable_http:
        print(f"HTTP API Port:    {args.http_port}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        server = MycobotServer(
            HOST, PORT,
            args.serial,
            args.baud,
            reconnect_interval=args.reconnect_interval,
            max_reconnect_attempts=args.max_reconnect_attempts,
            read_timeout=args.read_timeout,
            socket_timeout=args.socket_timeout,
            log_level=log_level,
            enable_vision=not args.disable_vision,
            enable_http=args.enable_http,
            http_port=args.http_port
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()
