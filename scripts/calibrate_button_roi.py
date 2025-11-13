#!/usr/bin/env python3
# coding: utf-8
"""
ROI 校準工具 - 機器手臂視覺檢測系統

功能：
- 自動遍歷所有按鈕
- 連接伺服器進行截圖
- 互動式 ROI 選擇（cv2.selectROI）
- 自動更新 button_positions.yaml（保留註解）

使用方式：
    python3 calibrate_button_roi.py --host 10.42.0.180 --port 9000

依賴：
    - opencv-python
    - PyYAML
    - numpy
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
from typing import Dict, List, Tuple, Optional


class RobotArmClient:
    """機器手臂 Socket JSON 客戶端"""

    def __init__(self, host: str, port: int, timeout: float = 10.0):
        """初始化客戶端

        Args:
            host: 伺服器 IP
            port: 伺服器端口
            timeout: Socket 超時時間（秒）
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def connect(self):
        """連接到伺服器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print(f"✅ 已連接到伺服器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False

    def disconnect(self):
        """斷開連接"""
        if self.socket:
            try:
                self.socket.close()
                print("✅ 已斷開連接")
            except:
                pass
            self.socket = None

    def send_command(self, command: dict) -> dict:
        """發送 JSON 命令並接收結果

        Args:
            command: JSON 命令字典

        Returns:
            伺服器回應的 JSON 字典
        """
        try:
            # 發送命令
            cmd_str = json.dumps(command, ensure_ascii=False)
            self.socket.sendall(cmd_str.encode('utf-8'))

            # 接收回應
            response = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                # 嘗試解析 JSON，如果成功則完整接收
                try:
                    json.loads(response.decode('utf-8'))
                    break
                except json.JSONDecodeError:
                    continue

            result = json.loads(response.decode('utf-8'))
            return result

        except Exception as e:
            print(f"❌ 命令執行失敗: {e}")
            return {"status": "error", "message": str(e)}

    def move_to_angles(self, angles: List[float], speed: int = 50) -> bool:
        """移動到指定角度

        Args:
            angles: 6 個關節角度
            speed: 速度（1-100）

        Returns:
            是否成功
        """
        command = {
            "command": "move_to_angles",
            "angles": angles,
            "speed": speed
        }
        result = self.send_command(command)
        return result.get("status") == "success"

    def capture_image(self, num_frames: int = 5, image_format: str = "jpeg") -> Optional[np.ndarray]:
        """截圖並返回圖像

        Args:
            num_frames: 多幀平均數量
            image_format: 圖像格式

        Returns:
            OpenCV 圖像（numpy.ndarray）或 None
        """
        command = {
            "command": "capture_image",
            "num_frames": num_frames,
            "format": image_format
        }
        result = self.send_command(command)

        if result.get("status") != "success":
            print(f"❌ 截圖失敗: {result.get('message')}")
            return None

        # 解碼 Base64 圖像
        try:
            image_base64 = result.get("image_base64")
            image_bytes = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"❌ 圖像解碼失敗: {e}")
            return None


class ButtonROICalibrator:
    """按鈕 ROI 校準工具"""

    def __init__(self, config_path: str, client: RobotArmClient):
        """初始化校準工具

        Args:
            config_path: button_positions.yaml 路徑
            client: 機器手臂客戶端
        """
        self.config_path = Path(config_path)
        self.client = client
        self.config = None
        self.buttons = {}

    def load_config(self) -> bool:
        """載入配置檔案"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            self.buttons = self.config.get('buttons', {})
            print(f"✅ 已載入配置檔案: {self.config_path}")
            print(f"   找到 {len(self.buttons)} 個按鈕")
            return True
        except Exception as e:
            print(f"❌ 載入配置失敗: {e}")
            return False

    def save_config(self) -> bool:
        """儲存配置檔案（簡化版：直接用 PyYAML）"""
        try:
            # 直接儲存為 YAML（不保留原始註解）
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            print(f"✅ 配置已儲存: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存配置失敗: {e}")
            return False

    def calibrate_button(self, button_name: str, button_config: dict) -> bool:
        """校準單一按鈕

        Args:
            button_name: 按鈕名稱
            button_config: 按鈕配置

        Returns:
            是否成功
        """
        print(f"\n{'='*60}")
        print(f"校準按鈕: {button_name}")
        print(f"描述: {button_config.get('description', 'N/A')}")
        print(f"{'='*60}")

        # 獲取觀測角度（使用 camera_observe 或 up_angles）
        observe_angles = None
        if button_name == "camera_observe":
            observe_angles = button_config.get('down_angles')
        else:
            # 對於其他按鈕，使用 camera_observe 的角度
            camera_observe = self.buttons.get('camera_observe', {})
            observe_angles = camera_observe.get('down_angles')

            if not observe_angles:
                # 如果沒有 camera_observe，使用按鈕的 up_angles
                observe_angles = button_config.get('up_angles')

        if not observe_angles:
            print(f"❌ 找不到觀測角度")
            return False

        # 移動到觀測位置
        print(f"🤖 移動到觀測位置: {observe_angles}")
        if not self.client.move_to_angles(observe_angles, speed=50):
            print(f"❌ 移動失敗")
            return False

        # 等待穩定
        print("⏳ 等待穩定...")
        time.sleep(2.0)

        # 截圖
        print("📷 截圖中...")
        image = self.client.capture_image(num_frames=5)
        if image is None:
            print(f"❌ 截圖失敗")
            return False

        print(f"✅ 截圖成功，圖像尺寸: {image.shape[1]}x{image.shape[0]}")

        # 顯示圖像並選擇 ROI
        print("\n📌 請在視窗中框選按鈕的 ROI 區域")
        print("   - 滑鼠拖曳框選區域")
        print("   - 按 Enter 確認")
        print("   - 按 ESC 取消")

        # 使用 cv2.selectROI
        cv2.namedWindow(f"ROI 校準 - {button_name}", cv2.WINDOW_NORMAL)
        roi = cv2.selectROI(f"ROI 校準 - {button_name}", image, showCrosshair=True, fromCenter=False)
        cv2.destroyAllWindows()

        x, y, w, h = roi

        if w == 0 or h == 0:
            print("❌ 未選擇 ROI，跳過此按鈕")
            return False

        print(f"✅ ROI 已選擇: x={x}, y={y}, width={w}, height={h}")

        # 更新配置
        if 'vision' not in button_config:
            button_config['vision'] = {}

        button_config['vision']['observe_angles'] = observe_angles
        button_config['vision']['roi'] = {
            'x': int(x),
            'y': int(y),
            'width': int(w),
            'height': int(h)
        }
        button_config['vision']['brightness_threshold'] = 100  # 預設閾值
        button_config['vision']['expected_colors'] = ['blue', 'white', 'off']

        print(f"✅ 按鈕 {button_name} 校準完成")
        return True

    def calibrate_all(self, skip_existing: bool = False) -> int:
        """校準所有按鈕

        Args:
            skip_existing: 是否跳過已有 vision 配置的按鈕

        Returns:
            成功校準的按鈕數量
        """
        success_count = 0
        total_count = len(self.buttons)

        print(f"\n🚀 開始校準所有按鈕（共 {total_count} 個）")

        for i, (button_name, button_config) in enumerate(self.buttons.items(), 1):
            print(f"\n進度: {i}/{total_count}")

            # 跳過已校準的按鈕
            if skip_existing and 'vision' in button_config and 'roi' in button_config['vision']:
                print(f"⏭️  跳過已校準的按鈕: {button_name}")
                continue

            # 詢問是否校準此按鈕
            response = input(f"\n是否校準按鈕 '{button_name}'? (y/n/q): ").strip().lower()
            if response == 'q':
                print("⏹️  使用者中止校準")
                break
            elif response != 'y':
                print(f"⏭️  跳過按鈕: {button_name}")
                continue

            # 執行校準
            if self.calibrate_button(button_name, button_config):
                success_count += 1

                # 立即儲存配置
                self.save_config()
                print(f"💾 進度已保存（{success_count}/{total_count}）")

        return success_count


def main():
    parser = argparse.ArgumentParser(description='ROI 校準工具 - 機器手臂視覺檢測系統')
    parser.add_argument('--host', type=str, default='10.42.0.180',
                        help='伺服器 IP (預設: 10.42.0.180)')
    parser.add_argument('--port', type=int, default=9000,
                        help='伺服器端口 (預設: 9000)')
    parser.add_argument('--config', type=str,
                        default='config/robot_arm/button_positions.yaml',
                        help='配置檔案路徑')
    parser.add_argument('--skip-existing', action='store_true',
                        help='跳過已校準的按鈕')
    parser.add_argument('--timeout', type=float, default=10.0,
                        help='Socket 超時時間（秒）')

    args = parser.parse_args()

    print("=" * 60)
    print("ROI 校準工具 - 機器手臂視覺檢測系統")
    print("=" * 60)
    print(f"伺服器: {args.host}:{args.port}")
    print(f"配置檔: {args.config}")
    print("=" * 60)

    # 初始化客戶端
    client = RobotArmClient(args.host, args.port, args.timeout)
    if not client.connect():
        print("❌ 無法連接到伺服器，請確認伺服器正在運行")
        return 1

    try:
        # 初始化校準工具
        calibrator = ButtonROICalibrator(args.config, client)
        if not calibrator.load_config():
            return 1

        # 執行校準
        success_count = calibrator.calibrate_all(skip_existing=args.skip_existing)

        print(f"\n{'='*60}")
        print(f"✅ 校準完成！成功校準 {success_count} 個按鈕")
        print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中止校準")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
