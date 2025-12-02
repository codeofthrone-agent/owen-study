#!/usr/bin/env python3
# coding: utf-8
"""
網頁版 ROI 校準工具 - 機器手臂視覺檢測系統

功能：
- 提供網頁介面進行 ROI 標註
- 不需要 X11 display
- 支援遠端操作
- 自動整合現有的機器手臂控制系統

版本：v1.0 (2025-11-14)
作者：Claude Code

使用方式：
    python3 web_roi_calibrator.py --host 10.42.0.180 --port 9000
    然後在瀏覽器開啟: http://localhost:5000
"""

import socket
import json
import base64
import cv2
import numpy as np
import yaml
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2.aruco as aruco

# 確保能匯入專案模組
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
from config.robot_arm.environment_config import EnvironmentConfig

# 嘗試載入 python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv 未安裝，無法讀取 .env 文件")
    print("   可使用: pip install python-dotenv 來安裝")

def load_env_variables():
    """載入環境變數"""
    if DOTENV_AVAILABLE:
        # 嘗試從多個位置載入 .env 文件
        project_root = Path(__file__).parent.parent
        env_paths = [
            project_root / ".env",
            Path.cwd() / ".env",
            Path(".env")
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✅ 載入環境變數: {env_path}")
                return True
        
        print("⚠️  未找到 .env 文件")
    return False

app = Flask(__name__)

# 全域變數 - 多環境支援
global_configs = {}  # 儲存所有環境配置 {env_name: config_data}
global_calibrators = {}  # 儲存所有環境的校準器 {env_name: WebButtonROICalibrator}
current_environment = None  # 當前選擇的環境
global_client = None  # 機器手臂客戶端(按需建立)
is_connected = False  # 連線狀態


class HybridRobotArmClient:
    """混合式機器手臂客戶端（供 Web 版本使用）"""

    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.controller = MyCobotSocketController(host, port)
        self.socket: Optional[socket.socket] = None
        self.timeout = timeout

    def connect(self) -> bool:
        """連接機器手臂並檢查狀態"""
        print("🔌 嘗試連接機器手臂...")
        if self.controller.connect():
            if hasattr(self.controller.mc, 'sock') and self.controller.mc.sock:
                self.socket = self.controller.mc.sock
                self.socket.settimeout(self.timeout)
                
                # 檢查連接狀態
                try:
                    power_status = self.controller.is_power_on()
                    print(f"✅ 連接成功，電源狀態: {'已上電' if power_status else '未上電'}")
                    
                    # 嘗試讀取角度以驗證通信
                    angles = self.controller.get_angles()
                    if angles and all(isinstance(a, (int, float)) for a in angles):
                        print(f"✅ 通信正常，當前角度: {[round(a, 2) for a in angles]}")
                    else:
                        print("⚠️  連接成功但角度讀取異常，可能需要檢查手臂狀態")
                    
                    return True
                except Exception as e:
                    print(f"⚠️  連接成功但狀態檢查失敗: {e}")
                    return True  # 仍然返回成功，讓使用者可以嘗試操作
        print("❌ 連接失敗")
        return False

    def disconnect(self):
        self.controller.disconnect()
        self.socket = None

    def power_on(self) -> bool:
        return self.controller.power_on()

    def power_off(self) -> bool:
        return self.controller.power_off()

    def get_angles(self) -> Optional[List[float]]:
        """讀取角度，增加錯誤處理"""
        try:
            angles = self.controller.get_angles()
            if angles is None:
                print("⚠️  角度讀取返回 None")
                return None
            
            # 檢查角度數據有效性
            if isinstance(angles, (int, float)) and angles == -1:
                print("⚠️  角度讀取返回 -1，可能手臂未上電或通信異常")
                return None
            
            if not isinstance(angles, (list, tuple)) or len(angles) != 6:
                print(f"⚠️  角度數據格式錯誤: {angles} (type: {type(angles)})")
                return None
            
            # 檢查每個角度值
            valid_angles = []
            for i, angle in enumerate(angles):
                if not isinstance(angle, (int, float)):
                    print(f"⚠️  關節 {i+1} 角度值無效: {angle} (type: {type(angle)})")
                    return None
                valid_angles.append(float(angle))
            
            return valid_angles
            
        except Exception as e:
            print(f"❌ 讀取角度時發生異常: {e}")
            return None

    def send_angles(self, angles, speed) -> bool:
        return self.controller.send_angles(angles, speed)

    def is_power_on(self) -> bool:
        return self.controller.is_power_on()

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
            print(f"🔍 OpenCV 版本: {cv_version}")
            
            # 嘗試不同的 ArUco API 方法
            aruco_dict = None
            detector = None
            corners = None
            ids = None
            
            # 方法 1: OpenCV 4.11+ 最新版 API（ArucoDetector 類）
            try:
                if hasattr(aruco, 'ArucoDetector') and hasattr(aruco, 'getPredefinedDictionary'):
                    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
                    parameters = aruco.DetectorParameters()
                    detector = aruco.ArucoDetector(aruco_dict, parameters)
                    print("✓ 使用最新版 ArUco API (ArucoDetector)")
                    
                    # 使用 ArucoDetector 進行檢測
                    corners, ids, _ = detector.detectMarkers(image)
            except Exception as e:
                print(f"⚠️ 最新版 API (ArucoDetector) 失敗: {e}")
                
            # 方法 2: OpenCV 4.7-4.10 新版 API
            if aruco_dict is None or corners is None:
                try:
                    if hasattr(aruco, 'getPredefinedDictionary') and hasattr(aruco, 'detectMarkers'):
                        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
                        if hasattr(aruco, 'DetectorParameters'):
                            parameters = aruco.DetectorParameters()
                        else:
                            parameters = aruco.DetectorParameters_create()
                        print("✓ 使用新版 ArUco API (getPredefinedDictionary)")
                        
                        # 直接使用 detectMarkers 函數
                        corners, ids, _ = aruco.detectMarkers(image, aruco_dict, parameters=parameters)
                except Exception as e:
                    print(f"⚠️ 新版 API 失敗: {e}")
                
            # 方法 3: OpenCV 4.0-4.6 舊版 API
            if aruco_dict is None or corners is None:
                try:
                    if hasattr(aruco, 'Dictionary_get'):
                        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
                        parameters = aruco.DetectorParameters_create()
                        print("✓ 使用舊版 ArUco API (Dictionary_get)")
                        
                        corners, ids, _ = aruco.detectMarkers(image, aruco_dict, parameters=parameters)
                except Exception as e:
                    print(f"⚠️ 舊版 API 失敗: {e}")
            
            # 方法 4: 備用方案
            if aruco_dict is None or corners is None:
                try:
                    # 嘗試直接創建字典
                    aruco_dict = aruco.Dictionary(aruco.DICT_4X4_50)
                    parameters = aruco.DetectorParameters()
                    print("✓ 使用備用 ArUco API (Dictionary)")
                    
                    # 嘗試不同的檢測方法
                    try:
                        corners, ids, _ = aruco.detectMarkers(image, aruco_dict)
                    except:
                        # 如果上述都失敗，嘗試更簡單的方法
                        print("🔍 嘗試簡單檢測方法...")
                        corners, ids = [], None
                except Exception as e:
                    print(f"⚠️ 備用 API 失敗: {e}")
            
            # 檢查結果有效性
            if corners is None:
                print("❌ 所有 ArUco API 都無法檢測")
                return {
                    "success": False,
                    "error": f"無法初始化 ArUco 檢測器 (OpenCV {cv_version})",
                    "markers_count": 0,
                    "markers": []
                }
            
            result = {
                "success": True,
                "markers_count": len(corners) if corners is not None else 0,
                "markers": []
            }
            
            if corners is not None and len(corners) > 0:
                print(f"🎯 檢測到 {len(corners)} 個 ArUco 標記")
                
                for i, corner in enumerate(corners):
                    marker_id = int(ids[i][0]) if ids is not None and len(ids) > i else i
                    
                    # 計算標記中心
                    center = np.mean(corner[0], axis=0)
                    
                    # 簡化版標記資訊（避免複雜的姿態估計）
                    marker_info = {
                        "id": marker_id,
                        "center": [float(center[0]), float(center[1])],
                        "corners": corner[0].tolist(),
                        "center_x": float(center[0]),  # 為了向後相容
                        "center_y": float(center[1])   # 為了向後相容
                    }
                    
                    # 可選：嘗試姿態估計（如果失敗就跳過）
                    try:
                        # 簡化的相機內參
                        camera_matrix = np.array([
                            [600, 0, 320],
                            [0, 600, 240],
                            [0, 0, 1]
                        ], dtype=np.float32)
                        
                        dist_coeffs = np.zeros((4, 1))
                        
                        # 嘗試姿態估計（如果可用）
                        if hasattr(aruco, 'estimatePoseSingleMarkers'):
                            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
                                [corner], marker_size, camera_matrix, dist_coeffs
                            )
                            
                            marker_info["position"] = {
                                "x": float(tvecs[0][0][0]),
                                "y": float(tvecs[0][0][1]),
                                "z": float(tvecs[0][0][2])
                            }
                            marker_info["rotation"] = {
                                "x": float(rvecs[0][0][0]),
                                "y": float(rvecs[0][0][1]),
                                "z": float(rvecs[0][0][2])
                            }
                    except Exception as pose_error:
                        # 姿態估計失敗是正常的，不影響基本檢測
                        marker_info["position"] = None
                        marker_info["rotation"] = None
                    
                    result["markers"].append(marker_info)
            else:
                print("🔍 未檢測到任何 ArUco 標記")
                    
            return result
            
        except Exception as e:
            print(f"❌ ArUco 檢測總體失敗: {e}")
            import traceback
            traceback.print_exc()
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
            
            # 尋找共同的標記 ID
            current_ids = {}
            reference_ids = {}
            
            # 處理當前標記
            for m in current_markers:
                if "id" in m:
                    # 支援新格式 (center) 和舊格式 (center_x, center_y)
                    if "center" in m:
                        current_ids[m["id"]] = {
                            "center_x": m["center"][0],
                            "center_y": m["center"][1]
                        }
                    elif "center_x" in m and "center_y" in m:
                        current_ids[m["id"]] = {
                            "center_x": m["center_x"],
                            "center_y": m["center_y"]
                        }
            
            # 處理參考標記
            for m in reference_markers:
                if "id" in m:
                    # 支援新格式 (center) 和舊格式 (center_x, center_y)
                    if "center" in m:
                        reference_ids[m["id"]] = {
                            "center_x": m["center"][0],
                            "center_y": m["center"][1]
                        }
                    elif "center_x" in m and "center_y" in m:
                        reference_ids[m["id"]] = {
                            "center_x": m["center_x"],
                            "center_y": m["center_y"]
                        }
            
            common_ids = set(current_ids.keys()) & set(reference_ids.keys())
            
            if not common_ids:
                print("⚠️  沒有找到共同的 ArUco 標記 ID")
                return None
            
            print(f"📍 找到 {len(common_ids)} 個共同標記: {list(common_ids)}")
            
            # 計算位移偏差
            total_offset_x = 0
            total_offset_y = 0
            valid_markers = 0
            
            for marker_id in common_ids:
                current_center = current_ids[marker_id]
                reference_center = reference_ids[marker_id]
                
                offset_x = current_center["center_x"] - reference_center["center_x"]
                offset_y = current_center["center_y"] - reference_center["center_y"]
                
                total_offset_x += offset_x
                total_offset_y += offset_y
                valid_markers += 1
                
                print(f"   標記 {marker_id}: 偏移 ({offset_x:.1f}, {offset_y:.1f})")
            
            if valid_markers == 0:
                return None
            
            # 平均偏移量
            avg_offset_x = total_offset_x / valid_markers
            avg_offset_y = total_offset_y / valid_markers
            
            # 計算偏移距離
            offset_distance = np.sqrt(avg_offset_x**2 + avg_offset_y**2)
            
            # 位置校正閾值（可調整）
            correction_threshold = 10.0  # 像素
            
            result = {
                "offset_x": float(avg_offset_x),
                "offset_y": float(avg_offset_y),
                "offset_distance": float(offset_distance),
                "common_markers": int(len(common_ids)),
                "needs_correction": bool(offset_distance > correction_threshold),
                "threshold": float(correction_threshold)
            }
            
            print(f"📐 位置校正結果: 平均偏移=({avg_offset_x:.1f}, {avg_offset_y:.1f}), 距離={offset_distance:.1f}")
            print(f"   需要校正: {'是' if result['needs_correction'] else '否'} (閾值: {correction_threshold})")
            
            return result
            
        except Exception as e:
            print(f"❌ 計算位置校正失敗: {e}")
            import traceback
            traceback.print_exc()
            return None

    def capture_image(self, num_frames: int = 5, image_format: str = "jpeg", max_retries: int = 3) -> Optional[np.ndarray]:
        """使用底層 socket 發送自訂的 capture_image JSON 命令（改進版）"""
        if not self.socket:
            print("❌ Socket 未連接")
            return None

        # 重試機制
        for retry in range(max_retries):
            try:
                print(f"📷 開始截圖 (第 {retry + 1}/{max_retries} 次嘗試)")
                
                command = {
                    "command": "capture_image",
                    "num_frames": num_frames,
                    "format": image_format
                }
                
                # 設定較長的超時時間
                self.socket.settimeout(45.0)  # 增加到 45 秒
                cmd_str = json.dumps(command, ensure_ascii=False)
                self.socket.sendall(cmd_str.encode('utf-8'))
                print(f"✓ 已發送截圖命令: {len(cmd_str)} bytes")

                response = b""
                start_time = time.time()
                last_progress_time = start_time

                while True:
                    elapsed = time.time() - start_time
                    if elapsed > 45.0:  # 總超時時間
                        raise socket.timeout(f"整體接收超時（45s）")

                    try:
                        # 設定較小的 chunk timeout，但不要太小
                        self.socket.settimeout(8.0)  # 增加到 8 秒
                        chunk = self.socket.recv(8192)  # 減小接收緩衝區
                        
                        if not chunk:
                            print("🔚 伺服器關閉連接")
                            break
                            
                        response += chunk
                        
                        # 進度顯示
                        current_time = time.time()
                        if current_time - last_progress_time > 3.0:  # 每 3 秒顯示進度
                            print(f"📥 接收中... {len(response):,} bytes")
                            last_progress_time = current_time

                        # 嘗試解析 JSON - 更智能的檢查
                        if len(response) > 100:  # 至少接收一些數據再檢查
                            try:
                                # 先檢查是否包含完整的 JSON 結尾標記
                                decoded_response = response.decode('utf-8', errors='ignore')
                                
                                # 檢查是否有 JSON 開始標記
                                if '{"status"' in decoded_response:
                                    # 檢查是否有完整的 image_base64 結束標記
                                    if (('"image_base64"' in decoded_response and 
                                        decoded_response.count('"') >= 6 and  # 至少應該有足夠的引號
                                        (decoded_response.endswith('"}') or '"}' in decoded_response[-50:]))):
                                        
                                        print(f"✓ 偵測到完整響應: {len(response):,} bytes")
                                        break
                                    elif '"status": "error"' in decoded_response:
                                        print(f"✓ 偵測到錯誤響應: {len(response):,} bytes")
                                        break
                                
                            except UnicodeDecodeError:
                                continue

                    except socket.timeout:
                        # 檢查是否有部分響應
                        if len(response) > 100:
                            try:
                                result = json.loads(response.decode('utf-8', errors='ignore'))
                                if isinstance(result, dict) and "status" in result:
                                    print(f"⚠️  部分超時但有響應: {len(response):,} bytes")
                                    break
                            except:
                                pass
                        
                        print(f"⏱️  接收超時，已接收: {len(response):,} bytes")
                        if retry < max_retries - 1:
                            print("   將重試...")
                            break
                        else:
                            raise

                # 解析響應
                if len(response) == 0:
                    print("❌ 沒有接收到任何數據")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

                try:
                    # 改進的 JSON 解析
                    decoded_response = response.decode('utf-8', errors='ignore')
                    
                    # 方法 1: 直接解析
                    try:
                        result = json.loads(decoded_response)
                    except json.JSONDecodeError as e:
                        # 方法 2: 尋找完整的 JSON 物件
                        print(f"⚠️  直接解析失敗: {e}")
                        json_start = decoded_response.find('{"status"')
                        if json_start >= 0:
                            # 尋找對應的結束括號
                            brace_count = 0
                            json_end = -1
                            for i in range(json_start, len(decoded_response)):
                                if decoded_response[i] == '{':
                                    brace_count += 1
                                elif decoded_response[i] == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            
                            if json_end > json_start:
                                json_part = decoded_response[json_start:json_end]
                                print(f"🔍 嘗試解析提取的 JSON: {len(json_part)} 字符")
                                result = json.loads(json_part)
                            else:
                                raise json.JSONDecodeError("無法找到完整的 JSON 物件", decoded_response, 0)
                        else:
                            raise json.JSONDecodeError("無法找到 JSON 開始標記", decoded_response, 0)
                            
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    print(f"   響應長度: {len(response):,} bytes")
                    print(f"   響應前 200 字符: {decoded_response[:200]}")
                    print(f"   響應後 200 字符: {decoded_response[-200:]}")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

                # 檢查響應狀態
                if not isinstance(result, dict):
                    print(f"❌ 響應格式錯誤，預期字典但得到: {type(result)}")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

                if result.get("status") != "success":
                    error_msg = result.get("message", "未知錯誤")
                    print(f"❌ 伺服器錯誤: {error_msg}")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

                image_base64 = result.get("image_base64")
                if not image_base64:
                    print("❌ 響應中沒有影像數據")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

                # 解碼影像
                try:
                    image_bytes = base64.b64decode(image_base64)
                    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    
                    if image is None:
                        print("❌ OpenCV 解碼失敗")
                        if retry < max_retries - 1:
                            time.sleep(1)
                            continue
                        return None
                    
                    # 檢查影像是否全黑
                    if np.mean(image) < 5:  # 平均亮度太低
                        print("⚠️  警告：截圖可能全黑（平均亮度過低）")
                        if retry < max_retries - 1:
                            print("   將重試...")
                            time.sleep(2)  # 等待較長時間
                            continue
                    
                    print(f"✅ 截圖成功: {image.shape[1]}x{image.shape[0]}, 平均亮度: {np.mean(image):.1f}")
                    return image
                    
                except Exception as e:
                    print(f"❌ 影像解碼失敗: {e}")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None

            except socket.timeout as e:
                print(f"⏱️  Socket 超時 (第 {retry + 1} 次): {e}")
                if retry < max_retries - 1:
                    print("   重新嘗試...")
                    time.sleep(2)
                    continue
                else:
                    print("❌ 達到最大重試次數")
                    return None
                    
            except Exception as e:
                print(f"❌ 截圖失敗 (第 {retry + 1} 次): {e}")
                if retry < max_retries - 1:
                    print("   重新嘗試...")
                    time.sleep(1)
                    continue
                else:
                    import traceback
                    traceback.print_exc()
                    return None

        print("❌ 所有重試都失敗")
        return None


class WebButtonROICalibrator:
    """網頁版按鈕 ROI 校準工具"""

    def __init__(self, config_path: str, client: Optional['HybridRobotArmClient'] = None):
        """初始化校準工具

        Args:
            config_path: YAML 配置檔案路徑
            client: HybridRobotArmClient 實例(可選,支援延遲初始化)
        """
        self.config_path = Path(config_path)
        self.client = client
        self.config = None
        self.buttons = {}
        self.environment_lights = {}
        self.current_image = None
        self.current_button_name = None
        self.current_item_type = None

    def set_client(self, client: 'HybridRobotArmClient'):
        """設定機器手臂客戶端(用於延遲初始化)"""
        self.client = client

    def load_config(self) -> bool:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.buttons = self.config.get('buttons', {})
            self.environment_lights = self.config.get('environment_lights', {})
            print(f"✅ 載入配置成功: {len(self.buttons)} 個按鈕, {len(self.environment_lights)} 個環境燈光")
            return True
        except Exception as e:
            print(f"載入配置失敗: {e}")
            return False

    def save_config(self) -> bool:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=None, sort_keys=False)
            return True
        except Exception as e:
            print(f"儲存配置失敗: {e}")
            return False

    def get_button_list(self) -> List[Dict]:
        item_list = []
        for name, config in self.buttons.items():
            vision_config = config.get('vision')
            has_roi = vision_config is not None and 'roi' in vision_config
            item_list.append({
                'name': name,
                'type': 'button',
                'description': config.get('description', 'N/A'),
                'has_roi': has_roi,
                'image_source': 'socket'
            })
        for name, config in self.environment_lights.items():
            has_roi = 'roi' in config and config['roi']  # ✅ 修正：確保 roi 不為空
            camera_id = config.get('camera_id', 'unknown')  # ✅ 修正：使用 camera_id 而非 camera_ip
            light_type = config.get('type', 'unknown')
            sub_count = len(config.get('lights', [])) if light_type == 'light_array' else 0

            item_list.append({
                'name': name,
                'type': 'environment_light',
                'description': config.get('name', 'N/A'),
                'has_roi': has_roi,
                'image_source': f'rtsp ({camera_id})',
                'light_type': light_type,
                'sub_count': sub_count
            })

        return item_list

    def prepare_calibration(self, button_name: str, item_type: str = 'button', capture_image: bool = True) -> Optional[Dict]:
        """準備校準：讀取角度並截圖（✨ v4.2.0 支援按鈕和環境燈光）

        Args:
            button_name: 按鈕或環境燈光名稱
            item_type: 'button' 或 'environment_light'
            capture_image: 是否截取影像 (預設 True)

        Returns:
            Dict: 包含影像、角度、現有 ROI 等資訊
        """
        # 根據類型取得配置
        if item_type == 'button':
            if button_name not in self.buttons:
                return {"success": False, "error": f"按鈕 '{button_name}' 不存在"}
            config = self.buttons[button_name]
            print(f"📋 準備校準按鈕: {button_name}")
        elif item_type == 'environment_light':
            if button_name not in self.environment_lights:
                return {"success": False, "error": f"環境燈光 '{button_name}' 不存在"}
            config = self.environment_lights[button_name]
            print(f"📋 準備校準環境燈光: {button_name}")
        else:
            return {"success": False, "error": f"不支援的項目類型: {item_type}"}

        self.current_button_name = button_name
        self.current_item_type = item_type
        button_config = config

        # 只有按鈕需要檢查手臂電源和讀取角度
        observe_angles = None
        if item_type == 'button':
            try:
                if not self.client.is_power_on():
                    return {"success": False, "error": "手臂電源未開啟，請先開啟手臂電源"}
            except Exception as e:
                print(f"⚠️  無法檢查電源狀態: {e}")

            try:
                observe_angles = self.client.get_angles()
                if observe_angles:
                    print(f"✅ 當前手臂角度: {[round(a, 2) for a in observe_angles]}")
                else:
                    observe_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            except Exception as e:
                print(f"⚠️  讀取手臂角度失敗: {str(e)}")
                observe_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # 根據類型截取影像
        image = None # Initialize image to None
        image_base64 = None
        if capture_image:
            if item_type == 'button':
                print("📷 使用 Socket 截取機器手臂影像...")
                image = self.client.capture_image(num_frames=5)
                if image is not None:
                    _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
            elif item_type == 'environment_light':
                print("📷 使用 RTSP 截取環境燈光影像...")
            elif item_type == 'environment_light':
                print("📷 使用 RTSP 截取環境燈光影像...")
                
                # ✨ v4.2.0: 使用 EnvironmentConfig 取得 Camera 資訊 (包含認證)
                env_name = self.config.get('environment', {}).get('name', 'taipei_lab')
                camera_id = config.get('camera_id')
                
                if not camera_id:
                    # 相容性 fallback: 如果沒有 camera_id 但有 camera_ip (舊設定)
                    camera_ip = config.get('camera_ip')
                    if camera_ip:
                        print(f"⚠️  警告: 使用舊版 camera_ip 設定: {camera_ip}")
                        # 簡單構建 URL (不含認證，除非環境變數有)
                        import os
                        username = os.getenv("IPCAM_USERNAME", "")
                        password = os.getenv("IPCAM_PASSWORD", "")
                        if username and password:
                            test_url = f"rtsp://{username}:{password}@{camera_ip}:554/live0"
                        else:
                            test_url = f"rtsp://{camera_ip}:554/live0"
                        stream_paths = [test_url] # 模擬列表
                    else:
                        return {"success": False, "error": "環境燈光缺少 camera_id 配置"}
                else:
                    try:
                        cam_config = EnvironmentConfig.get_camera(env_name, camera_id)
                        # EnvironmentConfig 已經處理好認證和 URL
                        test_url = cam_config['rtsp_url']
                        transport = cam_config.get('transport', 'tcp')
                        print(f"   取得 Camera URL: {test_url} (Transport: {transport})")
                        stream_paths = [test_url]
                    except ValueError as e:
                        return {"success": False, "error": str(e)}

                cap = None
                successful_path = None

                # 設定傳輸協議
                if transport == 'udp':
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
                    print("   設定 FFmpeg 選項: UDP 傳輸")
                else:
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
                    print("   設定 FFmpeg 選項: TCP 傳輸")

                for rtsp_url in stream_paths:
                    print(f"   嘗試連接: {rtsp_url.replace(os.getenv('IPCAM_PASSWORD', ''), '******') if os.getenv('IPCAM_PASSWORD') else rtsp_url}")

                    cap = cv2.VideoCapture(rtsp_url)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                    if cap.isOpened():
                        # 測試讀取幀 (嘗試多次以等待 Keyframe)
                        print(f"   ⏳ 已連接，正在等待影像 (最多 200 幀)...")
                        frame_read_success = False
                        for _ in range(200):  # 嘗試讀取 200 幀 (約 10 秒)
                            ret, test_frame = cap.read()
                            if ret and test_frame is not None and test_frame.size > 0:
                                print(f"   ✅ 成功讀取影像: ({test_frame.shape[1]}x{test_frame.shape[0]})")
                                successful_path = rtsp_url
                                frame_read_success = True
                                break
                            time.sleep(0.05)
                        
                        if frame_read_success:
                            break
                        else:
                            print(f"   ⚠️  連接成功但無法讀取有效幀 (超時)")
                            cap.release()
                            cap = None
                    else:
                        print(f"   ⚠️  無法連接")
                        if cap:
                            cap.release()
                        cap = None
                    
                    if frame_read_success:
                        image = test_frame
                        break
                    
                    # 如果失敗，等待後重試
                    print(f"   ⏳ 等待 1 秒後重試...")
                    time.sleep(1.0)

        self.current_image = image

        # ArUco 標記檢測（僅按鈕需要）
        aruco_result = None
        if item_type == 'button' and image is not None:
            aruco_result = self.detect_aruco_and_adjust_position(image, button_config)

        try:
            if image is not None:
                if image.size == 0: return {"success": False, "error": "截圖影像為空"}
                if np.mean(image) < 10: print("⚠️  警告：影像很暗，可能是攝影機或光線問題")
                _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
                image_base64 = base64.b64encode(buffer).decode('utf-8')
        except Exception as e: return {"success": False, "error": f"影像編碼失敗: {str(e)}"}

        existing_roi = None
        if item_type == 'button':
            vision_config = button_config.get('vision')
            if vision_config and 'roi' in vision_config:
                existing_roi = vision_config['roi']
        elif item_type == 'environment_light':
            if 'roi' in button_config and button_config['roi']:
                existing_roi = button_config['roi']
        if existing_roi: print(f"✅ 找到已存在的 ROI: {existing_roi}")

        return {
            "success": True, "button_name": button_name, "description": button_config.get('description', 'N/A'),
            "observe_angles": [round(a, 2) for a in observe_angles] if observe_angles else None,
            "image_base64": image_base64,
            "image_size": {"width": image.shape[1], "height": image.shape[0]} if image is not None else None,
            "existing_roi": existing_roi,
            "aruco_info": aruco_result
        }

    def save_roi(self, button_name: str, roi: Dict, item_type: str = 'button') -> Dict:
        if item_type == 'button':
            if button_name not in self.buttons: return {"success": False, "error": f"按鈕 '{button_name}' 不存在"}
            config = self.buttons[button_name]
        elif item_type == 'environment_light':
            if button_name not in self.environment_lights: return {"success": False, "error": f"環境燈光 '{button_name}' 不存在"}
            config = self.environment_lights[button_name]
        else: return {"success": False, "error": f"不支援的類型: {item_type}"}

        observe_angles = None
        if item_type == 'button':
            observe_angles = self.client.get_angles()
            if not observe_angles: return {"success": False, "error": "無法讀取當前手臂角度"}

        if item_type == 'button':
            if 'vision' not in config: config['vision'] = {}
            config['vision']['observe_angles'] = [round(a, 2) for a in observe_angles] if observe_angles else None
            config['vision']['roi'] = {'x': int(roi['x']), 'y': int(roi['y']), 'width': int(roi['width']), 'height': int(roi['height'])} # Changed to int
        else:
            config['roi'] = {'x': int(roi['x']), 'y': int(roi['y']), 'width': int(roi['width']), 'height': int(roi['height'])} # Changed to int
            if observe_angles: config['observe_angles'] = [round(a, 2) for a in observe_angles]

        if self.save_config(): return {"success": True, "message": f"{item_type.capitalize()} '{button_name}' 的 ROI 已儲存"}
        return {"success": False, "error": "儲存配置失敗"}

    def detect_aruco_and_adjust_position(self, image: np.ndarray, button_config: Dict) -> Dict:
        try:
            aruco_result = self.client.detect_aruco_markers(image)
            if not aruco_result["success"]: return {"aruco_detected": False, "error": aruco_result.get("error", "ArUco 檢測失敗"), "correction_needed": False}
            markers_count = aruco_result["markers_count"]
            print(f"🎯 檢測到 {markers_count} 個 ArUco 標記")
            reference_markers = None
            has_reference = False
            if 'aruco_reference' in button_config:
                reference_markers = button_config['aruco_reference'].get('markers', [])
                has_reference = bool(reference_markers)
            correction_info = None
            correction_needed = False
            if reference_markers and aruco_result["markers"]:
                correction_info = self.client.calculate_position_correction(aruco_result["markers"], reference_markers)
                if correction_info:
                    print(f"📏 位置偏移: X={correction_info['offset_x']:.1f}, Y={correction_info['offset_y']:.1f}, 距離={correction_info['offset_distance']:.1f}")
                    correction_needed = bool(correction_info.get("needs_correction", False))
                    if correction_needed: print("⚠️  建議進行位置校正")
            return {
                "aruco_detected": True, "markers_count": int(markers_count), "markers": aruco_result["markers"],
                "correction_info": correction_info, "correction_needed": correction_needed, "has_reference": has_reference
            }
        except Exception as e:
            print(f"⚠️  ArUco 處理失敗: {e}")
            return {"aruco_detected": False, "error": str(e), "correction_needed": False}

    def save_aruco_reference(self, button_name: str, aruco_markers: List[Dict]) -> Dict:
        print(f"🔖 嘗試儲存 ArUco 參考位置: 按鈕={button_name}, 標記數量={len(aruco_markers) if aruco_markers else 0}")
        if button_name not in self.buttons: return {"success": False, "error": f"按鈕 '{button_name}' 不存在"}
        button_config = self.buttons[button_name]
        angles = None
        try:
            angles = self.client.get_angles()
            if angles: print(f"✅ 成功讀取手臂角度: {[round(a, 2) for a in angles]}")
            else: angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        except Exception as e: 
            print(f"⚠️  讀取角度時發生異常: {e}，使用預設值")
            angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        if 'aruco_reference' not in button_config: button_config['aruco_reference'] = {}
        button_config['aruco_reference'] = {'angles': [round(a, 2) for a in angles], 'markers': aruco_markers, 'timestamp': time.time()}
        
        if self.save_config(): return {"success": True, "message": f"按鈕 '{button_name}' 的 ArUco 參考位置已儲存"}
        return {"success": False, "error": "儲存配置失敗"}


@app.route('/')
def index():
    return render_template('roi_annotator.html')

@app.route('/api/environments', methods=['GET'])
def get_environments():
    """取得所有可用環境列表"""
    global global_configs, global_calibrators, current_environment, is_connected, global_client
    
    try:
        environments = []
        for env_name, config in global_configs.items():
            connection_config = config.get('connection', {}).get('socket', {})
            calibrator = global_calibrators.get(env_name)
            
            environments.append({
                'name': env_name,
                'display_name': config.get('environment', {}).get('display_name', env_name),
                'robot_arm_host': connection_config.get('host', 'N/A'),
                'robot_arm_port': connection_config.get('port', 9000),
                'total_buttons': len(calibrator.buttons) if calibrator else 0,
                'total_lights': len(calibrator.environment_lights) if calibrator else 0
            })
        
        return jsonify({
            'success': True,
            'environments': environments,
            'current_environment': current_environment,
            'is_connected': is_connected,
            'connection_info': {
                'host': global_client.controller.host if global_client else None,
                'port': global_client.controller.port if global_client else None
            } if is_connected else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'取得環境列表失敗: {str(e)}'})

@app.route('/api/buttons', methods=['GET'])
def get_buttons():
    """取得按鈕列表(支援環境參數)"""
    global global_calibrators, current_environment
    
    # 從 URL 參數讀取環境,或使用當前環境
    env_name = request.args.get('environment', current_environment)
    
    if not env_name:
        return jsonify({'success': False, 'error': '未指定環境'})
    
    calibrator = global_calibrators.get(env_name)
    if calibrator is None:
        return jsonify({'success': False, 'error': f'環境 {env_name} 不存在'})
    
    button_list = calibrator.get_button_list()
    return jsonify({'success': True, 'buttons': button_list, 'environment': env_name})

@app.route('/api/calibrate/prepare', methods=['POST'])
def prepare_calibration():
    global global_calibrators, current_environment
    data = request.json
    button_name = data.get('button_name')
    item_type = data.get('item_type', 'button')  # ✨ 支援環境燈光
    capture_image = data.get('capture_image', True)
    env_name = data.get('environment')

    if not button_name: return jsonify({"success": False, "error": "缺少按鈕名稱"})
    
    # 優先使用請求中的環境參數，否則使用當前環境
    target_env = env_name if env_name else current_environment
    calibrator = global_calibrators.get(target_env)
    
    if calibrator is None: return jsonify({"success": False, "error": f"環境 {target_env} 校準器未初始化"})

    try:
        result = calibrator.prepare_calibration(button_name, item_type, capture_image)
        print(f"✅ 校準準備結果: type={item_type}, success={result.get('success')}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ 校準準備發生異常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"校準準備失敗: {str(e)}"})

@app.route('/api/calibrate/save', methods=['POST'])
def save_roi():
    global global_calibrators, current_environment
    data = request.json
    button_name = data.get('button_name')
    roi = data.get('roi')
    item_type = data.get('item_type', 'button')
    env_name = data.get('environment')

    if not button_name or not roi: return jsonify({"success": False, "error": "缺少必要參數"})
    
    # 優先使用請求中的環境參數，否則使用當前環境
    target_env = env_name if env_name else current_environment
    calibrator = global_calibrators.get(target_env)
    
    if calibrator is None: return jsonify({"success": False, "error": f"環境 {target_env} 校準器未初始化"})

    result = calibrator.save_roi(button_name, roi, item_type)
    return jsonify(result)


@app.route('/api/robot_arm/connect', methods=['POST'])
def connect_robot_arm():
    """連接機器手臂"""
    global global_client, is_connected, current_environment, global_calibrators, global_configs
    
    try:
        data = request.json
        env_name = data.get('environment')
        
        if not env_name:
            return jsonify({'success': False, 'error': '未指定環境'})
        
        if env_name not in global_configs:
            return jsonify({'success': False, 'error': f'環境 {env_name} 不存在'})
        
        # 如果已連線,先斷開
        if is_connected and global_client:
            global_client.disconnect()
            is_connected = False
        
        # 從配置讀取機器手臂連線資訊
        config = global_configs[env_name]
        connection_config = config.get('connection', {}).get('socket', {})
        host = connection_config.get('host')
        port = connection_config.get('port', 9000)
        
        if not host:
            return jsonify({'success': False, 'error': f'環境 {env_name} 缺少機器手臂連線配置'})
        
        print(f"🔌 正在連接到 {env_name} 機器手臂: {host}:{port}...")
        
        # 建立新的客戶端
        global_client = HybridRobotArmClient(host, port, timeout=30.0)
        
        if not global_client.connect():
            global_client = None
            return jsonify({
                'success': False,
                'error': f'無法連接到機器手臂 {host}:{port}',
                'host': host,
                'port': port
            })
        
        # 設定當前環境
        current_environment = env_name
        is_connected = True
        
        # 將客戶端注入到對應的校準器
        calibrator = global_calibrators.get(env_name)
        if calibrator:
            calibrator.set_client(global_client)
        
        # 讀取當前角度
        angles = None
        try:
            angles = global_client.get_angles()
        except Exception as e:
            print(f"⚠️  角度讀取失敗: {e}")
        
        env_display_name = config.get('environment', {}).get('display_name', env_name)
        
        return jsonify({
            'success': True,
            'message': f'已連接到 {env_display_name} 機器手臂',
            'environment': env_name,
            'host': host,
            'port': port,
            'angles': [round(a, 2) for a in angles] if angles else None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'連線失敗: {str(e)}'})

@app.route('/api/robot_arm/disconnect', methods=['POST'])
def disconnect_robot_arm():
    """斷開機器手臂連線"""
    global global_client, is_connected, current_environment
    
    try:
        if not is_connected or not global_client:
            return jsonify({'success': False, 'error': '目前未連線'})
        
        print("⚡ 斷開機器手臂連線...")
        global_client.disconnect()
        global_client = None
        is_connected = False
        
        # 保留當前環境選擇,但移除客戶端
        for calibrator in global_calibrators.values():
            calibrator.set_client(None)
        
        return jsonify({'success': True, 'message': '已斷開機器手臂連線'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'斷線失敗: {str(e)}'})

@app.route('/api/arm/move', methods=['POST'])
def move_arm():
    if global_client is None: return jsonify({"success": False, "error": "客戶端未初始化"})
    data = request.json
    angles_str = data.get('angles')
    speed = data.get('speed', 30)

    if not angles_str: return jsonify({"success": False, "error": "缺少角度參數"})
    
    try:
        angles = [float(a.strip()) for a in angles_str.split(',')]
        if len(angles) != 6: return jsonify({"success": False, "error": "角度參數必須是6個數字"})
        
        try:
            power_status = global_client.is_power_on()
            if not power_status: return jsonify({"success": False, "error": "手臂電源未開啟，請先開啟電源"})
            print("✅ 手臂電源已開啟")
        except Exception as e:
            print(f"⚠️  無法確認電源狀態: {e}，嘗試繼續移動...")

        try:
            before_angles = global_client.get_angles()
            if before_angles: print(f"📍 移動前角度: {[round(a, 2) for a in before_angles]}")
        except Exception as e: print(f"⚠️  無法讀取移動前角度: {e}")

        success = global_client.send_angles(angles, speed)
        if success:
            print("✅ 移動指令發送成功")
            print("⏳ 等待手臂移動...")
            time.sleep(3)
            try:
                current_angles = global_client.get_angles()
                if current_angles:
                    angles_formatted = [round(a, 2) for a in current_angles]
                    return jsonify({"success": True, "message": "手臂移動完成", "angles": angles_formatted})
                else: return jsonify({"success": True, "message": "移動指令已發送，但無法確認最終位置", "angles": None})
            except Exception as e: return jsonify({"success": True, "message": "移動指令已發送，但角度讀取失敗", "angles": None})
        else: return jsonify({"success": False, "error": "發送移動指令失敗"})
    except Exception as e: return jsonify({"success": False, "error": f"移動手臂時發生錯誤: {str(e)}"})


@app.route('/api/status', methods=['GET'])
def get_status():
    """取得機器手臂狀態（靜默模式，不輸出錯誤日誌）"""
    if global_client is None:
        return jsonify({"success": False, "error": "客戶端未初始化"})

    # 靜默檢查電源狀態
    try:
        power_status = global_client.is_power_on()
    except Exception:
        power_status = False

    # 完全跳過角度讀取（避免觸發 loguru 錯誤日誌）
    # 前端的狀態列不需要即時角度資訊，只需要電源狀態
    angles_formatted = None

    return jsonify({
        "success": True,
        "power_on": power_status,
        "angles": angles_formatted
    })


@app.route('/api/aruco/save_reference', methods=['POST'])
def save_aruco_reference():
    global global_calibrators, current_environment
    data = request.json
    env_name = data.get('environment')
    
    # 優先使用請求中的環境參數，否則使用當前環境
    target_env = env_name if env_name else current_environment
    calibrator = global_calibrators.get(target_env)
    
    if calibrator is None: return jsonify({"success": False, "error": f"環境 {target_env} 校準器未初始化"})
    
    button_name = data.get('button_name')
    aruco_markers = data.get('aruco_markers')

    if not button_name or not aruco_markers: return jsonify({"success": False, "error": "缺少必要參數"})
    try:
        result = calibrator.save_aruco_reference(button_name, aruco_markers)
        return jsonify(result)
    except Exception as e: return jsonify({"success": False, "error": f"儲存 ArUco 參考失敗: {str(e)}"})


@app.route('/api/aruco/detect', methods=['POST'])
def detect_aruco():
    if global_client is None: return jsonify({"success": False, "error": "客戶端未初始化"})
    try:
        image = global_client.capture_image(num_frames=3)
        if image is None: return jsonify({"success": False, "error": "無法獲取截圖", "aruco_detected": False, "markers_count": 0, "correction_needed": False})
        aruco_result = global_client.detect_aruco_markers(image)
        if not aruco_result["success"]: return jsonify({"success": False, "error": aruco_result.get("error", "ArUco 檢測失敗"), "aruco_detected": False, "markers_count": 0, "correction_needed": False})
        
        response = {
            "success": True, "aruco_detected": True, "markers_count": aruco_result.get("markers_count", 0),
            "markers": aruco_result.get("markers", []), "correction_needed": False, "has_reference": False, "correction_info": None
        }
        return jsonify(response)
    except Exception as e: return jsonify({"success": False, "error": f"ArUco 檢測失敗: {str(e)}", "aruco_detected": False, "markers_count": 0, "correction_needed": False})


@app.route('/api/aruco/calculate_correction', methods=['POST'])
def calculate_correction():
    if global_client is None: return jsonify({"success": False, "error": "客戶端未初始化"})
    data = request.json
    current_markers = data.get('current_markers')
    reference_markers = data.get('reference_markers')

    if not current_markers or not reference_markers: return jsonify({"success": False, "error": "缺少標記數據"})
    try:
        result = global_client.calculate_position_correction(current_markers, reference_markers)
        return jsonify(result if result else {"success": False, "error": "無法計算校正"})
    except Exception as e: return jsonify({"success": False, "error": f"計算位置校正失敗: {str(e)}"})


@app.route('/api/image/capture', methods=['POST'])
def capture_image():
    if global_client is None: return jsonify({"success": False, "error": "客戶端未初始化"})
    try:
        image = global_client.capture_image(num_frames=3)
        if image is None: return jsonify({"success": False, "error": "截圖失敗"})
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({"success": True, "image_base64": image_base64, "image_size": {"width": image.shape[1], "height": image.shape[0]}})
    except Exception as e: return jsonify({"success": False, "error": f"截圖失敗: {str(e)}"})


@app.route('/api/image/capture_rtsp', methods=['POST'])
def capture_rtsp_image():
    """RTSP 影像擷取（支援 TCP 傳輸和多種串流路徑）"""
    data = request.json
    rtsp_url = data.get('rtsp_url')
    num_frames = data.get('num_frames', 5)

    if not rtsp_url:
        return jsonify({"success": False, "error": "缺少 RTSP URL"})

    try:
        import cv2
        import os

        # 直接使用提供的 RTSP URL，不嘗試其他路徑以確保解析度一致
        print(f"📡 嘗試連接 RTSP: {rtsp_url.replace(os.getenv('IPCAM_PASSWORD', ''), '***')}")

        cap = None
        successful_url = None
        
        # 嘗試連接
        # 根據 EnvironmentConfig 設定傳輸協議
        from config.robot_arm.environment_config import EnvironmentConfig
        # 嘗試從 URL 反查 Camera 配置以取得 transport 設定
        # 這是一個簡化的做法，理想情況下應該從前端傳遞 transport 參數
        transport = 'udp' # 預設 UDP (為了相容性)
        
        # 嘗試解析環境和 Camera ID (如果可能)
        # 這裡我們簡單地預設使用 UDP，因為這是此工具的主要修復目標
        # 但如果能從 EnvironmentConfig 獲取會更好
        
        if transport == 'udp':
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
        else:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
            
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)  # Increase buffer size for stability

        if cap.isOpened():
            print(f"   ⏳ 已連接，正在等待影像 (最多 60 幀)...")
            
            # 嘗試連續讀取直到獲得有效影像 (取代原本的 sleep 5s)
            # 對於 UDP 串流，必須持續讀取 buffer 才能獲得最新影像
            frame_read_success = False
            for i in range(60):  # 嘗試讀取 60 幀 (約 2-3 秒)
                ret, test_frame = cap.read()
                if ret and test_frame is not None and test_frame.size > 0:
                    # 讀到第一幀後，再多讀幾幀確保穩定 (HEVC 預熱)
                    if i > 5: 
                        print(f"✅ 成功連接並讀取影像: {rtsp_url} (Frame {i})")
                        successful_url = rtsp_url
                        frame_read_success = True
                        break
                import time
                time.sleep(0.05)
            
            if not frame_read_success:
                print(f"⚠️  連接成功但無法讀取有效幀 (Timeout): {rtsp_url}")
                cap.release()
                cap = None
        else:
            print(f"⚠️  無法連接: {rtsp_url}")
            if cap:
                cap.release()
            cap = None

        if not cap or not successful_url:
            return jsonify({"success": False, "error": f"無法連接 RTSP: {rtsp_url}"})

        # 跳過前 5 幀（穩定連接）
        print(f"   正在跳過前 5 幀...")
        for _ in range(5):
            cap.read()

        # 擷取多幀並平均
        print(f"   正在擷取 {num_frames} 幀影像...")
        frames = []
        for i in range(num_frames):
            ret, frame = cap.read()
            if ret and frame is not None:
                frames.append(frame)
                print(f"   ✅ 成功擷取第 {i+1} 幀")
            else:
                print(f"   ⚠️  第 {i+1} 幀擷取失敗")

        cap.release()

        if not frames:
            return jsonify({"success": False, "error": "無法擷取任何幀"})

        # 平均多幀影像
        avg_frame = np.mean(frames, axis=0).astype(np.uint8)
        _, buffer = cv2.imencode('.jpg', avg_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        print(f"✅ RTSP 截圖成功: {avg_frame.shape[1]}x{avg_frame.shape[0]}, 使用 {len(frames)} 幀")
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "image_size": {"width": avg_frame.shape[1], "height": avg_frame.shape[0]},
            "num_frames": len(frames),
            "stream_path": successful_url.split('/')[-1]  # 回傳成功的串流路徑
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"RTSP 截圖失敗: {str(e)}"})


@app.route('/api/environment_config', methods=['GET'])
def get_environment_config():
    try:
        from config.robot_arm.environment_config import EnvironmentConfig
        # 優先從 URL 參數讀取環境，否則使用當前全域環境
        environment = request.args.get('environment', current_environment)
        cameras = EnvironmentConfig.get_cameras(environment)
        camera_list = []
        for camera_config in cameras:
            camera_list.append({
                "id": camera_config.get("id", "unknown"), "rtsp_url": camera_config.get("rtsp_url", ""),
                "description": camera_config.get("description", f"Camera {camera_config.get('id', 'unknown')}")
            })
        return jsonify({"success": True, "environment": environment, "cameras": camera_list})
    except Exception as e: return jsonify({"success": False, "error": f"取得環境配置失敗: {str(e)}"})


def main():
    global global_client, global_configs, global_calibrators, current_environment, is_connected

    parser = argparse.ArgumentParser(description='網頁版 ROI 校準工具 - 多環境支援')
    parser.add_argument('--web-port', type=int, default=5000, help='Web 伺服器端口')
    parser.add_argument('--environment', type=str, choices=['taipei_lab', 'rv_car', 'taoyuan_lab'],
                        help='預設環境(可選,啟動時不自動連線)')
    parser.add_argument('--skip-arm-check', action='store_true', 
                        help='保留參數以向後相容,多環境模式下無效')

    args = parser.parse_args()

    print("=" * 60)
    print("🌐 網頁版 ROI 校準工具 (多環境版)")
    print("=" * 60)
    print()

    # 載入環境變數
    load_env_variables()

    # 定義環境配置檔案
    config_files = {
        'taipei_lab': 'config/robot_arm/taipei_lab_buttons.yaml',
        'rv_car': 'config/robot_arm/rv_car_buttons.yaml',
        'taoyuan_lab': 'config/robot_arm/taoyuan_lab_buttons.yaml'
    }

    # 載入所有環境配置
    print("📂 載入環境配置...")
    loaded_count = 0
    for env_name, config_path in config_files.items():
        try:
            config_full_path = project_root / config_path
            print(f"   載入 {env_name}: {config_path}")
            
            with open(config_full_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            global_configs[env_name] = config_data
            
            # 建立校準器(不注入客戶端)
            calibrator = WebButtonROICalibrator(str(config_full_path), client=None)
            if calibrator.load_config():
                global_calibrators[env_name] = calibrator
                loaded_count += 1
                
                env_display = config_data.get('environment', {}).get('display_name', env_name)
                button_count = len(calibrator.buttons)
                light_count = len(calibrator.environment_lights)
                print(f"   ✅ {env_display}: {button_count} 個按鈕, {light_count} 個燈光")
            else:
                print(f"   ⚠️  {env_name} 配置載入失敗")
                
        except FileNotFoundError:
            print(f"   ⚠️  找不到配置檔案: {config_path}")
        except Exception as e:
            print(f"   ❌ {env_name} 載入錯誤: {e}")

    if loaded_count == 0:
        print("\n❌ 沒有成功載入任何環境配置")
        return 1

    print(f"\n✅ 成功載入 {loaded_count} 個環境配置")
    
    # 設定預設環境(不連線)
    if args.environment and args.environment in global_configs:
        current_environment = args.environment
        print(f"🎯 預設環境: {global_configs[current_environment].get('environment', {}).get('display_name', current_environment)}")
    else:
        # 預設選擇第一個成功載入的環境
        current_environment = list(global_calibrators.keys())[0]
        print(f"🎯 預設環境: {global_configs[current_environment].get('environment', {}).get('display_name', current_environment)} (可透過前端切換)")
    
    print()
    
    # 顯示所有環境的連線資訊
    print("🔌 機器手臂連線資訊:")
    for env_name, config in global_configs.items():
        connection_config = config.get('connection', {}).get('socket', {})
        host = connection_config.get('host', 'N/A')
        port = connection_config.get('port', 9000)
        env_display = config.get('environment', {}).get('display_name', env_name)
        print(f"   {env_display}: {host}:{port}")
    print()
    print("💡 提示: 機器手臂將在前端選擇環境後按需連線")
    print()

    print("=" * 60)
    print("🚀 Web 伺服器已啟動")
    print("=" * 60)
    print()
    print(f"📍 請在瀏覽器中開啟: http://localhost:{args.web_port}")
    print(f"🌐 或從其他設備訪問: http://{get_local_ip()}:{args.web_port}")
    print()
    print("功能說明：")
    print("  🦾 手臂移動：輸入角度並點擊移動按鈕")
    print("  📷 截圖標註：選擇按鈕後擷取影像並框選 ROI")
    print("  💾 儲存配置：標註完成後儲存到配置檔案")
    print()
    print("疑難排解：")
    print("  - 如果截圖全黑：檢查攝影機連接和光線")
    print("  - 如果角度讀取失敗：確認手臂電源已開啟")
    print("  - 如果移動失敗：檢查手臂連接和電源狀態")
    print()
    print("按 Ctrl+C 停止伺服器")
    print("=" * 60)
    print()

    try:
        app.run(host='0.0.0.0', port=args.web_port, debug=False)
    except KeyboardInterrupt:
        print("\n\n⏹️  伺服器已停止")
    finally:
        if global_client:
            global_client.disconnect()

    return 0


def get_local_ip():
    """獲取本機 IP 位址"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


if __name__ == "__main__":
    sys.exit(main())