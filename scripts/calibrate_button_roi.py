#!/usr/bin/env python3
# coding: utf-8
"""
ROI 校準工具 - 機器手臂視覺檢測系統 (v3 - Refactored)

功能：
- 預覽模式：擷取當前畫面存檔，輔助手動定位。
- 互動式控制：使用可靠的函式庫進行鎖定/釋放，方便手動調整。
- 儲存當前姿態：校準時自動儲存當前的手臂角度作為觀測點。
- 互動式 ROI 選擇（cv2.selectROI）
- 自動更新 button_positions.yaml

版本歷史:
- v3.0 (2025-11-13): 重構客戶端，改用 MyCobotSocketController 為核心，從根本上解決連線穩定性問題。
- v2.0 (2025-11-13): 增加鎖定/釋放功能。
- v1.0: 初始版本，包含預覽與校準功能。

使用方式：
    python3 calibrate_button_roi.py --host 10.42.0.180 --port 9000
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
import struct
from pathlib import Path
from typing import Dict, List, Optional

# 確保能從 libraries/ 導入模組
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
except ImportError as e:
    print(f"❌ 關鍵函式庫導入失敗: {e}")
    print("   請確認您在專案根目錄下，且 `libraries/robot_arm_control/mycobot_socket_controller.py` 檔案存在。")
    sys.exit(1)


class HybridRobotArmClient:
    """
    混合式機器手臂客戶端
    - 使用 MyCobotSocketController 處理標準命令以確保穩定性
    - 使用底層 Socket 發送自訂的 JSON 命令 (例如：影像擷取)
    """

    def __init__(self, host: str, port: int, timeout: float = 10.0):
        print("🦾 初始化混合式機器手臂客戶端...")
        self.controller = MyCobotSocketController(host, port)
        self.socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        if self.controller.connect():
            # 從已連接的 pymycobot 實例中獲取底層 socket
            if hasattr(self.controller.mc, 'sock') and self.controller.mc.sock:
                self.socket = self.controller.mc.sock
                print("✅ 成功獲取底層 socket，可發送自訂 JSON 指令。")
                return True
            else:
                print("❌ 致命錯誤：無法從控制器中獲取底層 socket。")
                self.controller.disconnect()
                return False
        return False

    def disconnect(self):
        self.controller.disconnect()
        self.socket = None
        print("🔌 已斷開混合式客戶端連接。")

    # --- Wrapper Methods (代理到可靠的 Controller) ---
    def power_on(self) -> bool: return self.controller.power_on()
    def power_off(self) -> bool: return self.controller.power_off()
    def get_angles(self) -> Optional[List[float]]: return self.controller.get_angles()
    def send_angles(self, angles, speed) -> bool: return self.controller.send_angles(angles, speed)
    def is_power_on(self) -> bool: return self.controller.is_power_on()

    # --- Custom JSON Command Method ---
    def capture_image(self, num_frames: int = 5, image_format: str = "jpeg") -> Optional[np.ndarray]:
        """使用底層 socket 發送自訂的 capture_image JSON 命令"""
        if not self.socket:
            print("❌ 無法擷取影像，底層 socket 不可用。")
            return None

        command = {
            "command": "capture_image",
            "num_frames": num_frames,
            "format": image_format
        }
        try:
            cmd_str = json.dumps(command, ensure_ascii=False)
            self.socket.sendall(cmd_str.encode('utf-8'))
            
            response = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk: break
                response += chunk
                try:
                    # 嘗試解析，直到收到一個完整的 JSON 物件
                    result = json.loads(response.decode('utf-8'))
                    # 檢查是否是我們期望的回應
                    if "status" in result and "image_base64" in result:
                        break
                except json.JSONDecodeError:
                    continue
            
            result = json.loads(response.decode('utf-8'))

            if result.get("status") != "success":
                print(f"❌ 截圖失敗: {result.get('message')}")
                return None
            
            image_base64 = result.get("image_base64")
            image_bytes = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"❌ 影像處理失敗: {e}")
            return None


class ButtonROICalibrator:
    """按鈕 ROI 校準工具"""

    def __init__(self, config_path: str, client: HybridRobotArmClient):
        self.config_path = Path(config_path)
        self.client = client
        self.config = None
        self.buttons = {}

    def load_config(self) -> bool:
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
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"✅ 配置已儲存: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ 儲存配置失敗: {e}")
            return False

    def calibrate_button(self, button_name: str, button_config: dict) -> bool:
        print(f"\n{'='*60}")
        print(f"校準按鈕: {button_name}")
        print(f"描述: {button_config.get('description', 'N/A')}")
        print(f"{'='*60}")

        print("🤖 正在讀取當前手臂角度作為觀測位置...")
        observe_angles = self.client.get_angles()
        if not observe_angles:
            print("❌ 無法讀取當前手臂角度，請確保手臂已上電並鎖定。")
            return False
        print(f"   觀測角度: {[f'{a:.2f}' for a in observe_angles]}")

        print("📷 截圖中...")
        image = self.client.capture_image(num_frames=5)
        if image is None:
            print(f"❌ 截圖失敗")
            return False
        print(f"✅ 截圖成功，圖像尺寸: {image.shape[1]}x{image.shape[0]}")

        print("\n📌 請在視窗中框選按鈕的 ROI 區域")
        print("   - 滑鼠拖曳框選區域")
        print("   - 按 Enter 或 s 鍵儲存")
        print("   - 按 r 鍵重選")
        print("   - 按 ESC 或 q 鍵取消")

        window_name = f"ROI 校準 - {button_name}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        roi = cv2.selectROI(window_name, image, showCrosshair=True, fromCenter=False)
        cv2.destroyAllWindows()
        x, y, w, h = roi

        if w == 0 or h == 0:
            print("❌ 未選擇 ROI，跳過此按鈕")
            return False

        print(f"✅ ROI 已選擇: x={x}, y={y}, width={w}, height={h}")

        if 'vision' not in button_config:
            button_config['vision'] = {}
        button_config['vision']['observe_angles'] = [round(a, 2) for a in observe_angles]
        button_config['vision']['roi'] = {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
        button_config['vision']['brightness_threshold'] = 100
        button_config['vision']['expected_colors'] = ['blue', 'white', 'off']

        print(f"✅ 按鈕 {button_name} 校準完成")
        return True

    def calibrate_all(self, skip_existing: bool = False) -> int:
        success_count = 0
        total_count = len(self.buttons)
        print(f"\n🚀 開始校準流程（共 {total_count} 個按鈕）")

        for i, (button_name, button_config) in enumerate(self.buttons.items(), 1):
            print(f"\n進度: {i}/{total_count}")

            if skip_existing and 'vision' in button_config and 'roi' in button_config['vision']:
                print(f"⏭️  跳過已校準的按鈕: {button_name}")
                continue

            response = input(f"\n是否校準按鈕 '{button_name}'? (y/n/q): ").strip().lower()
            if response == 'q':
                print("⏹️  使用者中止校準")
                break
            elif response != 'y':
                print(f"⏭️  跳過按鈕: {button_name}")
                continue

            if self.calibrate_button(button_name, button_config):
                success_count += 1
                self.save_config()
                print(f"💾 進度已保存（{success_count} 校準成功）")
        return success_count


def preview_and_save(client: HybridRobotArmClient, output_path: str = "tmp_screen.jpg"):
    print("\n📷 正在擷取預覽畫面...")
    image = client.capture_image(num_frames=5)
    if image is None:
        print("❌ 擷取預覽畫面失敗。")
        return
    try:
        cv2.imwrite(output_path, image)
        print(f"✅ 預覽畫面已儲存至 '{output_path}'。")
        print("   您現在可以查看此圖片來輔助您手動調整機器手臂位置。")
    except Exception as e:
        print(f"❌ 儲存圖片失敗: {e}")

def lock_robot(client: HybridRobotArmClient):
    """使用可靠的方法鎖定手臂於當前位置"""
    print("\n🔒 正在鎖定手臂於當前位置...")
    if not client.is_power_on():
        client.power_on()
    
    current_angles = client.get_angles()
    if current_angles:
        if client.send_angles(current_angles, 80):
            print(f"✅ 手臂已鎖定於: {[f'{a:.1f}' for a in current_angles]}")
        else:
            print("❌ 鎖定失敗：發送角度指令時發生錯誤。")
    else:
        print("❌ 鎖定失敗：無法讀取當前角度。")


def main():
    parser = argparse.ArgumentParser(description='ROI 校準工具 - 機器手臂視覺檢測系統 (v3 - Refactored)')
    parser.add_argument('--host', type=str, default='10.42.0.180', help='伺服器 IP (預設: 10.42.0.180)')
    parser.add_argument('--port', type=int, default=9000, help='伺服器端口 (預設: 9000)')
    parser.add_argument('--config', type=str, default='config/robot_arm/button_positions.yaml', help='配置檔案路徑')
    parser.add_argument('--skip-existing', action='store_true', help='跳過已校準的按鈕')
    parser.add_argument('--timeout', type=float, default=10.0, help='Socket 超時時間（秒）')

    args = parser.parse_args()

    print("=" * 60)
    print("ROI 校準工具 - 機器手臂視覺檢測系統 (v3 - Refactored)")
    print("=" * 60)
    print(f"伺服器: {args.host}:{args.port}")
    print(f"配置檔: {args.config}")
    print("=" * 60)

    client = HybridRobotArmClient(args.host, args.port, args.timeout)
    if not client.connect():
        return 1

    try:
        while True:
            choice = input("\nEnter 'p' (preview), 'c' (calibrate), 'r' (release), 'l' (lock), 'q' (quit): ").lower()
            if choice == 'q':
                break
            elif choice == 'p':
                preview_and_save(client)
            elif choice == 'c':
                calibrator = ButtonROICalibrator(args.config, client)
                if not calibrator.load_config(): return 1
                success_count = calibrator.calibrate_all(skip_existing=args.skip_existing)
                print(f"\n{'='*60}\n✅ 校準完成！成功校準 {success_count} 個按鈕\n{'='*60}")
                break
            elif choice == 'r':
                client.power_off()
            elif choice == 'l':
                lock_robot(client)
            else:
                print("❌ 無效的選擇，請重新輸入。")

    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中止操作")
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
