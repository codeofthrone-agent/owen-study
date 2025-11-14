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
from typing import Dict, List, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory

# 確保能匯入專案模組
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController

app = Flask(__name__)

# 全域變數
global_client = None
global_calibrator = None


class HybridRobotArmClient:
    """混合式機器手臂客戶端（供 Web 版本使用）"""

    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.controller = MyCobotSocketController(host, port)
        self.socket: Optional[socket.socket] = None
        self.timeout = timeout

    def connect(self) -> bool:
        if self.controller.connect():
            if hasattr(self.controller.mc, 'sock') and self.controller.mc.sock:
                self.socket = self.controller.mc.sock
                self.socket.settimeout(self.timeout)
                return True
        return False

    def disconnect(self):
        self.controller.disconnect()
        self.socket = None

    def power_on(self) -> bool:
        return self.controller.power_on()

    def power_off(self) -> bool:
        return self.controller.power_off()

    def get_angles(self) -> Optional[List[float]]:
        return self.controller.get_angles()

    def send_angles(self, angles, speed) -> bool:
        return self.controller.send_angles(angles, speed)

    def is_power_on(self) -> bool:
        return self.controller.is_power_on()

    def capture_image(self, num_frames: int = 5, image_format: str = "jpeg") -> Optional[np.ndarray]:
        """使用底層 socket 發送自訂的 capture_image JSON 命令"""
        if not self.socket:
            return None

        command = {
            "command": "capture_image",
            "num_frames": num_frames,
            "format": image_format
        }
        try:
            self.socket.settimeout(self.timeout)
            cmd_str = json.dumps(command, ensure_ascii=False)
            self.socket.sendall(cmd_str.encode('utf-8'))

            response = b""
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    raise socket.timeout(f"整體接收超時（{self.timeout}s）")

                try:
                    chunk = self.socket.recv(65536)
                    if not chunk:
                        break
                    response += chunk

                    try:
                        result = json.loads(response.decode('utf-8'))
                        if "status" in result:
                            if "image_base64" in result or result.get("status") == "error":
                                break
                    except json.JSONDecodeError:
                        continue

                except socket.timeout:
                    if len(response) > 0:
                        try:
                            result = json.loads(response.decode('utf-8'))
                            if "status" in result:
                                break
                        except:
                            pass
                    raise

            result = json.loads(response.decode('utf-8'))

            if result.get("status") != "success":
                return None

            image_base64 = result.get("image_base64")
            if not image_base64:
                return None

            image_bytes = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"影像處理失敗: {e}")
            return None


class WebButtonROICalibrator:
    """網頁版按鈕 ROI 校準工具"""

    def __init__(self, config_path: str, client: HybridRobotArmClient):
        self.config_path = Path(config_path)
        self.client = client
        self.config = None
        self.buttons = {}
        self.current_image = None
        self.current_button_name = None

    def load_config(self) -> bool:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.buttons = self.config.get('buttons', {})
            return True
        except Exception as e:
            print(f"載入配置失敗: {e}")
            return False

    def save_config(self) -> bool:
        """儲存配置（保留原始格式，只更新 vision 區塊）"""
        try:
            # 讀取原始檔案內容
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 使用 ruamel.yaml 保留格式（如果可用），否則使用基本方法
            try:
                from ruamel.yaml import YAML
                yaml_handler = YAML()
                yaml_handler.preserve_quotes = True
                yaml_handler.default_flow_style = None

                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml_handler.dump(self.config, f)
            except ImportError:
                # ruamel.yaml 不可用，使用基本的 yaml.dump
                # 注意：這會改變格式，但至少能儲存資料
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=None, sort_keys=False)

            return True
        except Exception as e:
            print(f"儲存配置失敗: {e}")
            return False

    def get_button_list(self) -> List[Dict]:
        """取得所有按鈕資訊"""
        button_list = []
        for name, config in self.buttons.items():
            has_roi = 'vision' in config and 'roi' in config.get('vision', {})
            button_list.append({
                'name': name,
                'description': config.get('description', 'N/A'),
                'has_roi': has_roi
            })
        return button_list

    def prepare_calibration(self, button_name: str) -> Optional[Dict]:
        """準備校準：讀取角度並截圖"""
        if button_name not in self.buttons:
            return {"success": False, "error": f"按鈕 '{button_name}' 不存在"}

        self.current_button_name = button_name
        button_config = self.buttons[button_name]

        # 讀取當前手臂角度
        try:
            observe_angles = self.client.get_angles()
            if not observe_angles:
                return {"success": False, "error": "無法讀取當前手臂角度"}
        except Exception as e:
            return {"success": False, "error": f"讀取手臂角度失敗: {str(e)}"}

        # 截圖
        image = self.client.capture_image(num_frames=5)
        if image is None:
            return {"success": False, "error": "截圖失敗"}

        self.current_image = image

        # 將影像轉為 Base64 以便傳送到前端
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "success": True,
            "button_name": button_name,
            "description": button_config.get('description', 'N/A'),
            "observe_angles": [round(a, 2) for a in observe_angles],
            "image_base64": image_base64,
            "image_size": {"width": image.shape[1], "height": image.shape[0]}
        }

    def save_roi(self, button_name: str, roi: Dict) -> Dict:
        """儲存 ROI 資料"""
        if button_name not in self.buttons:
            return {"success": False, "error": f"按鈕 '{button_name}' 不存在"}

        button_config = self.buttons[button_name]

        # 讀取當前角度（如果之前讀取失敗）
        observe_angles = self.client.get_angles()
        if not observe_angles:
            return {"success": False, "error": "無法讀取當前手臂角度"}

        # 更新配置
        if 'vision' not in button_config:
            button_config['vision'] = {}

        button_config['vision']['observe_angles'] = [round(a, 2) for a in observe_angles]
        button_config['vision']['roi'] = {
            'x': int(roi['x']),
            'y': int(roi['y']),
            'width': int(roi['width']),
            'height': int(roi['height'])
        }

        # 儲存配置
        if self.save_config():
            return {
                "success": True,
                "message": f"按鈕 '{button_name}' 的 ROI 已儲存"
            }
        else:
            return {"success": False, "error": "儲存配置失敗"}


# Flask 路由

@app.route('/')
def index():
    """首頁"""
    return render_template('roi_annotator.html')

@app.route('/api/buttons', methods=['GET'])
def get_buttons():
    """取得所有按鈕列表"""
    if global_calibrator is None:
        return jsonify({"success": False, "error": "校準器未初始化"})

    button_list = global_calibrator.get_button_list()
    return jsonify({"success": True, "buttons": button_list})

@app.route('/api/calibrate/prepare', methods=['POST'])
def prepare_calibration():
    """準備校準：截圖並取得影像"""
    data = request.json
    button_name = data.get('button_name')

    if not button_name:
        return jsonify({"success": False, "error": "缺少按鈕名稱"})

    if global_calibrator is None:
        return jsonify({"success": False, "error": "校準器未初始化"})

    result = global_calibrator.prepare_calibration(button_name)
    return jsonify(result)

@app.route('/api/calibrate/save', methods=['POST'])
def save_roi():
    """儲存 ROI"""
    data = request.json
    button_name = data.get('button_name')
    roi = data.get('roi')

    if not button_name or not roi:
        return jsonify({"success": False, "error": "缺少必要參數"})

    if global_calibrator is None:
        return jsonify({"success": False, "error": "校準器未初始化"})

    result = global_calibrator.save_roi(button_name, roi)
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def get_status():
    """取得系統狀態"""
    if global_client is None:
        return jsonify({"success": False, "error": "客戶端未初始化"})

    try:
        power_status = global_client.is_power_on()
    except Exception as e:
        power_status = False

    try:
        angles = global_client.get_angles()
        angles_formatted = [round(a, 2) for a in angles] if angles else None
    except Exception as e:
        # 讀取角度失敗（例如返回 -1），仍然返回成功但角度為 None
        angles_formatted = None

    return jsonify({
        "success": True,
        "power_on": power_status,
        "angles": angles_formatted
    })


def main():
    global global_client, global_calibrator

    parser = argparse.ArgumentParser(description='網頁版 ROI 校準工具')
    parser.add_argument('--host', type=str, default='10.42.0.180', help='機器手臂伺服器 IP')
    parser.add_argument('--port', type=int, default=9000, help='機器手臂伺服器端口')
    parser.add_argument('--web-port', type=int, default=5000, help='Web 伺服器端口')
    parser.add_argument('--config', type=str, default='config/robot_arm/button_positions.yaml',
                        help='按鈕配置檔案路徑')
    parser.add_argument('--timeout', type=float, default=30.0, help='Socket 超時時間（秒）')

    args = parser.parse_args()

    print("=" * 60)
    print("🌐 網頁版 ROI 校準工具")
    print("=" * 60)
    print()

    # 建立客戶端
    print(f"🔌 正在連接到機器手臂伺服器 {args.host}:{args.port}...")
    global_client = HybridRobotArmClient(args.host, args.port, timeout=args.timeout)

    if not global_client.connect():
        print("❌ 連接失敗，請確認伺服器已啟動。")
        return 1

    print("✅ 連接成功")
    print()

    # 載入配置
    print(f"📂 載入配置檔案: {args.config}")
    global_calibrator = WebButtonROICalibrator(args.config, global_client)

    if not global_calibrator.load_config():
        print("❌ 載入配置失敗")
        global_client.disconnect()
        return 1

    print(f"✅ 找到 {len(global_calibrator.buttons)} 個按鈕")
    print()

    # 啟動 Web 伺服器
    print("=" * 60)
    print("🚀 Web 伺服器已啟動")
    print("=" * 60)
    print()
    print(f"📍 請在瀏覽器中開啟: http://localhost:{args.web_port}")
    print()
    print("提示：")
    print("  - 選擇要校準的按鈕")
    print("  - 在影像上拖曳滑鼠框選 ROI")
    print("  - 點擊「儲存 ROI」按鈕")
    print()
    print("按 Ctrl+C 停止伺服器")
    print("=" * 60)
    print()

    try:
        app.run(host='0.0.0.0', port=args.web_port, debug=False)
    except KeyboardInterrupt:
        print("\n\n⏹️  伺服器已停止")
    finally:
        global_client.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
