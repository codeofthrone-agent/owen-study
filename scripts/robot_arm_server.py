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
import cv2
import numpy as np

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


# ==================== VisionAnalyzer 類別 ====================

class VisionAnalyzer:
    """視覺分析引擎 - 藍/白/關 LED 檢測（HSV 方案）

    功能：
    - 多幀平均截圖（解決 LED 掃描頻率問題）
    - HSV 顏色檢測（藍色/白色）
    - 亮度檢測（關閉狀態）
    - ROI 區域分析
    """

    def __init__(self, camera_device="/dev/video0", logger=None):
        """初始化視覺分析器

        Args:
            camera_device: 攝影機設備路徑
            logger: 日誌記錄器（可選）
        """
        self.camera_device = camera_device
        self.logger = logger or logging.getLogger("VisionAnalyzer")
        self.camera_lock = threading.Lock()

        # HSV 顏色範圍配置
        self.color_ranges = {
            'blue': {
                'lower': np.array([100, 50, 50]),
                'upper': np.array([130, 255, 255])
            },
            'white': {
                'lower': np.array([0, 0, 200]),
                'upper': np.array([180, 50, 255])
            }
        }

        self.logger.info(f"VisionAnalyzer 初始化完成，攝影機: {camera_device}")

    def capture_multi_frame_average(self, num_frames=5, warmup_frames=10) -> np.ndarray:
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

    def detect_button_state(self, image: np.ndarray, roi_config: dict) -> dict:
        """檢測單一按鈕狀態

        Args:
            image: 輸入圖像 (BGR 格式)
            roi_config: ROI 配置
                {
                    "x": int,
                    "y": int,
                    "width": int,
                    "height": int,
                    "brightness_threshold": int (可選，預設 100)
                }

        Returns:
            {
                "light": "on" | "off",
                "color": "blue" | "white" | "off" | "unknown",
                "brightness": 0-255,
                "confidence": 0.0-1.0,
                "debug_info": {
                    "blue_ratio": float,
                    "white_ratio": float,
                    "roi_size": [width, height]
                }
            }
        """
        try:
            # 1. 提取 ROI
            roi = self._extract_roi(image, roi_config)

            # 2. 檢測亮度
            brightness = self._detect_brightness(roi)

            # 3. 判斷開/關
            threshold = roi_config.get('brightness_threshold', 100)

            if brightness < threshold:
                return {
                    "light": "off",
                    "color": "off",
                    "brightness": int(brightness),
                    "confidence": 1.0,
                    "debug_info": {
                        "blue_ratio": 0.0,
                        "white_ratio": 0.0,
                        "roi_size": [roi.shape[1], roi.shape[0]]
                    }
                }

            # 4. 顏色檢測（HSV）
            color, confidence, debug_info = self._detect_color_hsv(roi)

            return {
                "light": "on",
                "color": color,
                "brightness": int(brightness),
                "confidence": confidence,
                "debug_info": {
                    **debug_info,
                    "roi_size": [roi.shape[1], roi.shape[0]]
                }
            }

        except Exception as e:
            self.logger.error(f"按鈕狀態檢測失敗: {e}")
            return {
                "light": "error",
                "color": "error",
                "brightness": 0,
                "confidence": 0.0,
                "debug_info": {"error": str(e)}
            }

    def _extract_roi(self, image: np.ndarray, roi_config: dict) -> np.ndarray:
        """提取 ROI 區域

        Args:
            image: 完整圖像
            roi_config: ROI 配置 {"x": int, "y": int, "width": int, "height": int}

        Returns:
            ROI 圖像
        """
        x = roi_config['x']
        y = roi_config['y']
        w = roi_config['width']
        h = roi_config['height']

        # 邊界檢查
        img_h, img_w = image.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        roi = image[y:y+h, x:x+w]

        if roi.size == 0:
            raise ValueError(f"ROI 區域無效: x={x}, y={y}, w={w}, h={h}")

        return roi

    def _detect_brightness(self, roi: np.ndarray) -> float:
        """檢測亮度（使用 HSV 的 V 通道）

        Args:
            roi: ROI 圖像

        Returns:
            平均亮度 (0-255)
        """
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])  # V channel
        return brightness

    def _detect_color_hsv(self, roi: np.ndarray) -> Tuple[str, float, dict]:
        """HSV 顏色檢測（藍 vs 白）

        Args:
            roi: ROI 圖像

        Returns:
            (color_name, confidence, debug_info)
            - color_name: "blue" | "white" | "unknown"
            - confidence: 0.0-1.0
            - debug_info: {"blue_ratio": float, "white_ratio": float}
        """
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        total_pixels = roi.shape[0] * roi.shape[1]

        # 藍色檢測
        blue_mask = cv2.inRange(hsv,
                                 self.color_ranges['blue']['lower'],
                                 self.color_ranges['blue']['upper'])
        blue_ratio = cv2.countNonZero(blue_mask) / total_pixels

        # 白色檢測（低飽和度 + 高亮度）
        white_mask = cv2.inRange(hsv,
                                  self.color_ranges['white']['lower'],
                                  self.color_ranges['white']['upper'])
        white_ratio = cv2.countNonZero(white_mask) / total_pixels

        # 判斷邏輯
        confidence_threshold = 0.3  # 至少 30% 像素符合

        debug_info = {
            "blue_ratio": float(blue_ratio),
            "white_ratio": float(white_ratio)
        }

        if blue_ratio > white_ratio and blue_ratio > confidence_threshold:
            return "blue", float(blue_ratio), debug_info
        elif white_ratio > confidence_threshold:
            return "white", float(white_ratio), debug_info
        else:
            return "unknown", max(blue_ratio, white_ratio), debug_info


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
                 camera_device = "/dev/video0", enable_vision = True):
        """Server class with enhanced error handling and auto-reconnection

        Args:
            host: server ip address.
            port: server port.
            serial_num: serial number of the robot.The default is /dev/ttyAMA0.
            baud: baud rate of the serial port.The default is 1000000.
            reconnect_interval: seconds between reconnection attempts.
            max_reconnect_attempts: maximum reconnection attempts before giving up.
            read_timeout: serial read timeout in seconds (default: 0.2).
            socket_timeout: socket receive timeout in seconds (default: 30.0).
            log_level: logging level (default: logging.INFO).
            camera_device: camera device path (default: /dev/video0).
            enable_vision: enable vision detection system (default: True).

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

        # 視覺檢測系統配置
        self.camera_device = camera_device
        self.enable_vision = enable_vision
        self.vision_analyzer = None

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

        # 初始化視覺檢測系統
        if self.enable_vision:
            try:
                self.vision_analyzer = VisionAnalyzer(camera_device, self.logger)
                self.logger.info("✅ 視覺檢測系統已啟用")
            except Exception as e:
                self.logger.warning(f"⚠️ 視覺檢測系統初始化失敗: {e}")
                self.logger.warning("   伺服器將以無視覺模式運行")
                self.enable_vision = False

        # 啟動連接處理
        self.connect()

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

    # ==================== JSON 命令處理方法 ====================

    def _handle_json_command(self, cmd: dict) -> dict:
        """處理 JSON 命令（客戶端提供所有參數，伺服器不讀取配置）

        Args:
            cmd: JSON 命令字典
                {
                    "command": "detect_button" | "move_to_angles" | "capture_image",
                    ... (其他參數依命令而定)
                }

        Returns:
            dict: 命令執行結果
        """
        try:
            command_type = cmd.get("command")

            if not command_type:
                return {"status": "error", "message": "缺少 'command' 欄位"}

            if command_type == "detect_button":
                return self._cmd_detect_button(cmd)
            elif command_type == "move_to_angles":
                return self._cmd_move_to_angles(cmd)
            elif command_type == "capture_image":
                return self._cmd_capture_image(cmd)
            else:
                return {"status": "error", "message": f"未知的命令類型: {command_type}"}

        except Exception as e:
            self.logger.error(f"JSON 命令處理失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_detect_button(self, cmd: dict) -> dict:
        """檢測按鈕狀態（客戶端提供 ROI、觀測角度等完整參數）

        Args:
            cmd: {
                "command": "detect_button",
                "roi": {"x": int, "y": int, "width": int, "height": int, "brightness_threshold": int},
                "observe_angles": [j1, j2, j3, j4, j5, j6],  # 可選，如果需要先移動
                "num_frames": int  # 可選，多幀平均數量（預設 5）
            }

        Returns:
            {
                "status": "success" | "error",
                "result": {...},  # detect_button_state 的結果
                "message": str
            }
        """
        if not self.enable_vision or not self.vision_analyzer:
            return {"status": "error", "message": "視覺檢測系統未啟用"}

        try:
            # 1. 移動到觀測位置（如果提供）
            if "observe_angles" in cmd:
                move_result = self._cmd_move_to_angles({
                    "command": "move_to_angles",
                    "angles": cmd["observe_angles"],
                    "speed": cmd.get("speed", 50)
                })

                if move_result["status"] != "success":
                    return {"status": "error", "message": f"移動到觀測位置失敗: {move_result['message']}"}

                # 等待穩定
                time.sleep(0.5)

            # 2. 多幀平均截圖
            num_frames = cmd.get("num_frames", 5)
            image = self.vision_analyzer.capture_multi_frame_average(num_frames)

            # 3. 檢測按鈕狀態
            roi_config = cmd.get("roi")
            if not roi_config:
                return {"status": "error", "message": "缺少 'roi' 參數"}

            result = self.vision_analyzer.detect_button_state(image, roi_config)

            return {
                "status": "success",
                "result": result,
                "message": f"按鈕檢測完成: {result['color']}"
            }

        except Exception as e:
            self.logger.error(f"按鈕檢測失敗: {e}")
            return {"status": "error", "message": str(e)}

    def _cmd_move_to_angles(self, cmd: dict) -> dict:
        """移動到指定角度

        Args:
            cmd: {
                "command": "move_to_angles",
                "angles": [j1, j2, j3, j4, j5, j6],
                "speed": int  # 可選，預設 50
            }

        Returns:
            {
                "status": "success" | "error",
                "message": str
            }
        """
        try:
            angles = cmd.get("angles")
            if not angles or len(angles) != 6:
                return {"status": "error", "message": "angles 參數必須包含 6 個關節角度"}

            speed = cmd.get("speed", 50)

            # 構建 send_angles 命令（參考 pymycobot 協議）
            # 格式: [0xfe, 0xfe, len, 0x52, j1_h, j1_l, j2_h, j2_l, ..., j6_h, j6_l, speed, 0xfa]
            command_bytes = [0xfe, 0xfe, 0x0f, 0x52]  # header + length + cmd_id

            for angle in angles:
                # 將角度轉換為 int16 (角度 * 100)
                angle_int = int(angle * 100)
                high_byte = (angle_int >> 8) & 0xff
                low_byte = angle_int & 0xff
                command_bytes.extend([high_byte, low_byte])

            command_bytes.append(speed)
            command_bytes.append(0xfa)  # footer

            # 發送命令
            with self.serial_lock:
                self.write(command_bytes)

            self.logger.info(f"移動到角度: {angles}, 速度: {speed}")
            return {"status": "success", "message": f"已發送移動命令"}

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
        if not self.enable_vision or not self.vision_analyzer:
            return {"status": "error", "message": "視覺檢測系統未啟用"}

        try:
            import base64

            # 多幀平均截圖
            num_frames = cmd.get("num_frames", 5)
            image = self.vision_analyzer.capture_multi_frame_average(num_frames)

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
    print("MyCobot Robot Arm Server - Enhanced Version")
    print("=" * 50)
    print(f"Server IP:   {HOST}")
    print(f"Server Port: {PORT}")
    print(f"Serial Port: {args.serial}")
    print(f"Baud Rate:   {args.baud}")
    print(f"Vision Enabled: {not args.disable_vision}")
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
            enable_vision=not args.disable_vision
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()
