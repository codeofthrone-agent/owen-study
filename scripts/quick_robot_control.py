#!/usr/bin/env python3
"""
MyCobot 280 快速控制腳本 (v3 - Socket-based)
提供命令列方式快速控制機器手臂的基本功能
此版本使用 pymycobot Socket 連接進行控制

技術架構:
- pymycobot.MyCobot280Socket (TCP/IP Socket 連接)
- libraries.robot_arm_control.mycobot_socket_controller (Socket 控制器封裝)
- libraries.robot_arm_control.button_config_loader (配置管理)

版本歷史:
- v3.0 (2025-11-12): 改用 Socket 連接，移除對 library.robot 的依賴
- v2.0: 使用 library.robot.mycobot_controller
- v1.0: 原始版本
"""

import sys
import argparse
import time
import os
from pathlib import Path

# 將專案根目錄添加到 sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
    from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader
    LIBRARY_AVAILABLE = True
except ImportError as e:
    print(f"❌ 無法導入機器手臂控制庫: {e}")
    print("   請確認您在專案根目錄下，且 libraries/ 路徑正確。")
    LIBRARY_AVAILABLE = False

def connect_robot(host: str = None, port: int = None) -> MyCobotSocketController:
    """
    連接機器手臂 (使用 Socket 方式)

    Args:
        host (str, optional): 機器手臂 IP 地址。如果為 None，從配置文件讀取
        port (int, optional): Socket 端口。如果為 None，從配置文件讀取（預設 9000）

    Returns:
        MyCobotSocketController: 機器手臂控制器實例或 None
    """
    if not LIBRARY_AVAILABLE:
        return None

    print("🔌 正在初始化機器手臂 Socket 控制器...")

    # 從配置文件讀取預設值
    config_loader = ButtonConfigLoader()
    socket_config = config_loader.get_socket_config()

    if host is None:
        host = socket_config['host']
    if port is None:
        port = socket_config['port']

    print(f"   連接目標: {host}:{port}")

    controller = MyCobotSocketController(host, port)

    try:
        if controller.connect():
            print(f"✅ 連接成功")
            return controller
        else:
            print(f"❌ 連接失敗")
            return None
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")
        return None

def relax_robot(controller: MyCobotSocketController):
    """放鬆機器手臂（關閉電源）"""
    print("💤 正在放鬆所有伺服馬達...")
    if controller.power_off():
        print("✅ 機器手臂已放鬆，可以手動移動")
        print("⚠️  請小心操作，避免機器手臂突然掉落")
        return True
    else:
        print("❌ 操作失敗")
        return False

def power_on_robot(controller: MyCobotSocketController):
    """開啟機器手臂伺服馬達"""
    print("⚡️ 正在開啟所有伺服馬達...")
    if controller.power_on():
        print("✅ 機器手臂已上電")
        return True
    else:
        print("❌ 操作失敗")
        return False

def lock_robot(controller: MyCobotSocketController):
    """鎖定機器手臂於當前位置"""
    print("🔒 正在鎖定機器手臂於當前位置...")
    print("=" * 50)

    # 步驟 1: 確保已上電
    print("步驟 1/3: 檢查電源狀態...")
    if not controller.is_power_on():
        print("   ⚡️ 伺服馬達未上電，正在開啟電源...")
        if controller.power_on():
            print("   ✅ 伺服馬達已上電")
            time.sleep(1.5)  # 等待伺服馬達穩定
        else:
            print("   ❌ 上電失敗")
            return False
    else:
        print("   ✅ 伺服馬達已上電")

    # 步驟 2: 讀取當前角度
    print("\n步驟 2/3: 讀取當前位置...")
    current_angles = controller.get_angles()
    if current_angles is None:
        print("   ❌ 無法讀取當前角度")
        return False

    print(f"   當前角度: {[f'{a:.1f}' for a in current_angles]}")

    # 步驟 3: 發送相同角度以鎖定
    print("\n步驟 3/3: 鎖定於當前位置...")
    if controller.send_angles(current_angles, 80):
        time.sleep(1)
        final_angles = controller.get_angles()
        if final_angles:
            print(f"   ✅ 機器手臂已鎖定於: {[f'{a:.1f}' for a in final_angles]}")
        else:
            print("   ✅ 機器手臂已鎖定，但無法獲取最終角度。")
        print("=" * 50)
        return True
    else:
        print("   ❌ 鎖定失敗")
        print("=" * 50)
        return False

def add_position(controller: MyCobotSocketController):
    """記錄當前位置（鎖定→讀取→放鬆）"""
    print("📍 記錄當前位置...")
    print("=" * 50)

    # 1. 鎖定機器手臂
    print("🔒 正在鎖定機器手臂...")
    if not controller.is_power_on():
        controller.power_on()
        time.sleep(0.5)

    current_angles = controller.get_angles()
    if current_angles is None:
        print("❌ 無法讀取當前角度")
        return False

    # 發送相同角度以鎖定
    controller.send_angles(current_angles, 80)
    time.sleep(1)

    # 2. 讀取並顯示最終位置
    final_angles = controller.get_angles()
    # Socket 控制器沒有 get_coords() 方法
    final_coords = None

    # 驗證angles
    if final_angles is None or not isinstance(final_angles, list):
        print("❌ 無法讀取關節角度")
        return False

    print(f"✅ 機器手臂已鎖定於: {[f'{a:.1f}' for a in final_angles]}")

    # 驗證coords（可能會失敗，這是正常的）
    if final_coords is not None and isinstance(final_coords, list) and len(final_coords) == 6:
        print(f"   對應座標為: {[f'{c:.1f}' for c in final_coords]}")
    else:
        print(f"   對應座標: 讀取失敗（這在某些情況下是正常的）")

    # 3. 自動放鬆
    print("\n💤 自動放鬆機器手臂...")
    if controller.power_off():
        print("✅ 機器手臂已放鬆")
        print("=" * 50)
        return True
    else:
        print("❌ 放鬆失敗")
        return False

def home_robot(controller: MyCobotSocketController, speed=50):
    """機器手臂回歸原點"""
    print("🏠 正在回歸原點...")
    if controller.go_to_home(speed):
        current_angles = controller.get_angles()
        # Socket 控制器沒有 get_coords() 方法
        current_coords = None
        if current_angles:
            print(f"✅ 回歸完成，當前角度: {[f'{a:.1f}' for a in current_angles]}")
        else:
            print("✅ 回歸完成，但無法獲取當前角度。")
        if current_coords:
            print(f"   對應座標為: {[f'{c:.1f}' for c in current_coords]}")
        else:
            print("   無法獲取當前座標。")
        return True
    else:
        print("❌ 操作失敗")
        return False

def safe_position_robot(controller: MyCobotSocketController, speed=50):
    """機器手臂移動到安全位置 (移動到 [0, -90, -90, 0, 0, 0])"""
    print("🛡️ 正在移動到安全位置...")

    # Socket 控制器沒有 go_to_safe_position()，手動實現
    safe_position = [0, -90, -90, 0, 0, 0]
    if controller.send_angles(safe_position, speed):
        controller.wait_for_movement()
        current_angles = controller.get_angles()
        if current_angles:
            print(f"✅ 移動完成，當前角度: {[f'{a:.1f}' for a in current_angles]}")
        else:
            print("✅ 移動完成，但無法獲取當前角度。")
        return True
    else:
        print("❌ 操作失敗")
        return False

def show_status(controller: MyCobotSocketController):
    """顯示機器手臂狀態"""
    print("📊 機器手臂狀態:")
    print("=" * 50)

    try:
        angles = controller.get_angles()

        if angles:
            print("   關節角度 (度):")
            for i, angle in enumerate(angles, 1):
                print(f"     J{i}: {angle:8.2f}°")
        else:
            print("   關節角度: 讀取失敗")

        # Socket 控制器沒有 get_coords() 方法
        print("\n   座標位置: Socket 控制器不支援座標讀取")

        # 檢查電源狀態
        power_status = controller.is_power_on()
        print(f"\n   電源狀態: {'已開啟' if power_status else '已關閉'}")

        # 檢查移動狀態
        is_moving = controller.is_moving()
        print(f"   移動狀態: {'移動中' if is_moving else '靜止'}")

        print("=" * 50)
        return True

    except Exception as e:
        print(f"❌ 讀取狀態失敗: {e}")
        print("=" * 50)
        return False

def release_single_servo(controller: MyCobotSocketController, joint_id: int):
    """放鬆單一關節"""
    if not controller.mc:
        print("❌ 無法獲取機器手臂底層實例")
        return False

    print(f"💤 正在放鬆關節 J{joint_id}...")
    controller.mc.release_servo(joint_id)
    print(f"✅ 關節 J{joint_id} 已放鬆")
    return True

def release_multiple_servos(controller: MyCobotSocketController, joint_ids: list):
    """放鬆多個指定關節"""
    if not controller.mc:
        print("❌ 無法獲取機器手臂底層實例")
        return False

    print(f"💤 正在放鬆關節: {', '.join([f'J{j}' for j in joint_ids])}...")
    success = True
    for joint_id in joint_ids:
        try:
            controller.mc.release_servo(joint_id)
            print(f"   ✅ 關節 J{joint_id} 已放鬆")
            time.sleep(0.1)  # 短暫延遲以確保命令被執行
        except Exception as e:
            print(f"   ❌ 關節 J{joint_id} 放鬆失敗: {e}")
            success = False

    if success:
        print(f"✅ 所有指定關節已放鬆")
    else:
        print(f"⚠️  部分關節放鬆失敗")

    return success

def power_on_single_servo(controller: MyCobotSocketController, joint_id: int):
    """開啟單一關節伺服馬達"""
    if not controller.mc:
        print("❌ 無法獲取機器手臂底層實例")
        return False

    print(f"⚡️ 正在開啟關節 J{joint_id} 伺服馬達...")
    controller.mc.focus_servo(joint_id)
    print(f"✅ 關節 J{joint_id} 已上電")
    return True

def lock_multiple_joints(controller: MyCobotSocketController, joint_ids: list):
    """鎖定多個指定關節於當前角度"""
    if not controller.mc:
        print("❌ 無法獲取機器手臂底層實例")
        return False

    # 確保已上電
    if not controller.is_power_on():
        controller.power_on()
        time.sleep(0.5)

    # 獲取當前所有角度
    current_angles = controller.get_angles()
    if current_angles is None:
        print("❌ 無法讀取當前角度")
        return False

    print(f"🔒 正在鎖定關節: {', '.join([f'J{j}' for j in joint_ids])}...")
    print(f"   當前角度: {[f'{a:.1f}' for a in current_angles]}")

    success = True
    for joint_id in joint_ids:
        try:
            joint_index = joint_id - 1
            current_angle = current_angles[joint_index]
            # 發送當前角度以鎖定該關節
            controller.mc.send_angle(joint_id, current_angle, 80)
            print(f"   🔒 關節 J{joint_id} 鎖定於 {current_angle:.2f}°")
            time.sleep(0.1)  # 短暫延遲以確保命令被執行
        except Exception as e:
            print(f"   ❌ 關節 J{joint_id} 鎖定失敗: {e}")
            success = False

    if success:
        time.sleep(1)  # 等待所有關節穩定
        final_angles = controller.get_angles()
        if final_angles:
            print(f"✅ 所有指定關節已鎖定")
            print(f"   最終角度: {[f'{a:.1f}' for a in final_angles]}")
    else:
        print(f"⚠️  部分關節鎖定失敗")

    return success

def move_single_joint(controller: MyCobotSocketController, joint_id: int, angle: float, speed: int):
    """移動單一關節到指定角度"""
    if not controller.mc:
        print("❌ 無法獲取機器手臂底層實例")
        return False

    print(f"⚙️ 正在移動關節 J{joint_id} 到 {angle}°...")
    controller.mc.send_angle(joint_id, angle, speed)
    print(f"✅ 關節 J{joint_id} 移動指令已發送")
    return True

def move_all_joints(controller: MyCobotSocketController, angles: list, speed: int):
    """移動所有 6 個關節到指定角度"""
    if len(angles) != 6:
        print(f"❌ 錯誤: 需要 6 個角度值，但提供了 {len(angles)} 個")
        return False

    print("🎯 移動所有關節到指定角度")
    print("=" * 50)

    # 確保已上電
    if not controller.is_power_on():
        print("⚡️ 伺服馬達未上電，正在開啟...")
        controller.power_on()
        time.sleep(0.5)

    # 讀取當前角度
    current_angles = controller.get_angles()
    if current_angles:
        print("   當前角度: ", [f'{a:.2f}' for a in current_angles])
    else:
        print("   當前角度: 無法獲取")

    # 顯示目標角度
    print("   目標角度: ", [f'{a:.2f}' for a in angles])

    # 計算變化量
    if current_angles:
        deltas = [target - current for target, current in zip(angles, current_angles)]
        total_change = sum(abs(d) for d in deltas)
        print(f"   總變化量: {total_change:.2f}°")

    # 發送移動指令
    print(f"\n🚀 正在移動 (速度: {speed})...")
    if controller.send_angles(angles, speed):
        # 等待移動完成
        controller.wait_for_movement()

        # 讀取最終角度
        final_angles = controller.get_angles()
        if final_angles:
            print(f"✅ 移動完成")
            print("   最終角度: ", [f'{a:.2f}' for a in final_angles])

            # 計算誤差
            errors = [abs(final - target) for final, target in zip(final_angles, angles)]
            max_error = max(errors)
            if max_error > 2.0:
                print(f"   ⚠️  最大誤差: {max_error:.2f}° (J{errors.index(max_error)+1})")

            # Socket 控制器不支援座標讀取
            print(f"   末端座標: Socket 控制器不支援座標讀取")
        else:
            print("✅ 移動指令已發送，但無法獲取最終角度。")

        print("=" * 50)
        return True
    else:
        print("❌ 移動指令發送失敗")
        return False

def main():
    """主函數 - 解析命令列參數並執行相應操作"""
    parser = argparse.ArgumentParser(
        description='MyCobot 280 快速控制腳本 (v3 - Socket-based)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  快速解鎖所有機器手臂：
    python3 %(prog)s --relax

  放鬆指定多個關節 (J1, J2, J3, J4):
    python3 %(prog)s --release-joints 1,2,3,4

  鎖定指定多個關節 (J1, J2, J3, J4) 於當前角度:
    python3 %(prog)s --lock-joints 1,2,3,4

  放鬆單一關節 (J2):
    python3 %(prog)s --release-single 2

  快速鎖定所有關節：
    python3 %(prog)s --lock

  記錄當前位置（鎖定→顯示→放鬆）：
    python3 %(prog)s --add

  顯示關節角度和座標：
    python3 %(prog)s --status

  回到原點 (0,0,0,0,0,0):
    python3 %(prog)s --home

  移動單一關節 (J3 到 45度):
    python3 %(prog)s --move-single 3 --angle 45

  移動所有 6 個關節到指定角度:
    python3 %(prog)s --6angle 0 -45 -90 45 0 0
    python3 %(prog)s --6angle 14.23 -43.0 -128.58 63.45 1.49 2.72
        '''
        """
    )
    
    # 基本操作
    parser.add_argument('--relax', action='store_true', help='放鬆所有伺服馬達')
    parser.add_argument('--power-on', action='store_true', help='開啟所有伺服馬達')
    parser.add_argument('--lock', action='store_true', help='鎖定機器手臂於當前位置')
    parser.add_argument('--add', action='store_true', help='記錄當前位置（鎖定→顯示→放鬆）')
    parser.add_argument('--status', action='store_true', help='顯示關節角度和座標位置')
    parser.add_argument('--home', action='store_true', help='機器手臂回到原點')
    parser.add_argument('--safe', action='store_true', help='機器手臂移動到安全位置')

    # 6 關節移動
    parser.add_argument('--6angle', nargs=6, type=float, metavar=('J1', 'J2', 'J3', 'J4', 'J5', 'J6'),
                        help='移動所有 6 個關節到指定角度 (度)')

    # 多關節操作
    parser.add_argument('--release-joints', type=str, metavar='JOINTS', help='放鬆多個指定關節，用逗號分隔 (例如: 1,2,3,4)')
    parser.add_argument('--lock-joints', type=str, metavar='JOINTS', help='鎖定多個指定關節於當前角度，用逗號分隔 (例如: 1,2,3,4)')

    # 單一關節操作
    parser.add_argument('--release-single', type=int, metavar='JOINT', help='放鬆指定關節 (1-6)')
    parser.add_argument('--power-single', type=int, metavar='JOINT', help='開啟指定關節伺服馬達 (1-6)')
    parser.add_argument('--move-single', type=int, metavar='JOINT', help='移動指定關節 (1-6)')
    parser.add_argument('--angle', type=float, metavar='DEGREES', help='目標角度 (配合 --move-single)')
    parser.add_argument('--speed', type=int, default=50, metavar='SPEED', help='移動速度 1-100 (預設: 50)')
    
    # 連接設定
    parser.add_argument('--host', type=str, help='指定 IP 地址 (預設使用配置)')
    parser.add_argument('--port', type=int, help='指定 Socket 端口 (預設使用配置)')
    parser.add_argument('--dry-run', action='store_true', help='乾運行模式 (不實際連接)')

    args = parser.parse_args()

    # 檢查是否有指定任何操作
    if not any(vars(args).values()):
        parser.print_help()
        return 1

    if args.dry_run:
        print("🔧 乾運行模式 - 不會實際連接機器手臂。")
        return 0

    # 連接機器手臂
    controller = connect_robot(args.host, args.port)
    if not controller:
        return 1
    
    success = True
    try:
        if args.relax: success &= relax_robot(controller)
        if args.power_on: success &= power_on_robot(controller)
        if args.lock: success &= lock_robot(controller)
        if args.add: success &= add_position(controller)
        if args.status: success &= show_status(controller)
        if args.home: success &= home_robot(controller, args.speed)
        if args.safe: success &= safe_position_robot(controller, args.speed)

        # 6 關節移動
        if getattr(args, '6angle', None):
            success &= move_all_joints(controller, args.__dict__['6angle'], args.speed)

        if args.release_single: success &= release_single_servo(controller, args.release_single)

        if args.release_joints:
            try:
                # 解析逗號分隔的關節編號
                joint_ids = [int(j.strip()) for j in args.release_joints.split(',')]
                # 驗證關節編號範圍
                if all(1 <= j <= 6 for j in joint_ids):
                    success &= release_multiple_servos(controller, joint_ids)
                else:
                    print("❌ 關節編號必須在 1-6 範圍內")
                    success = False
            except ValueError:
                print("❌ 無效的關節編號格式，請使用逗號分隔的數字 (例如: 1,2,3,4)")
                success = False

        if args.lock_joints:
            try:
                # 解析逗號分隔的關節編號
                joint_ids = [int(j.strip()) for j in args.lock_joints.split(',')]
                # 驗證關節編號範圍
                if all(1 <= j <= 6 for j in joint_ids):
                    success &= lock_multiple_joints(controller, joint_ids)
                else:
                    print("❌ 關節編號必須在 1-6 範圍內")
                    success = False
            except ValueError:
                print("❌ 無效的關節編號格式，請使用逗號分隔的數字 (例如: 1,2,3,4)")
                success = False

        if args.power_single: success &= power_on_single_servo(controller, args.power_single)
        if args.move_single:
            if args.angle is None:
                print("❌ 使用 --move-single 時必須指定 --angle")
                success = False
            else:
                success &= move_single_joint(controller, args.move_single, args.angle, args.speed)
                
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷操作")
        success = False
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
        success = False
    finally:
        print("\n🔌 disconnecting...")
        controller.disconnect()
        print("✅ 操作完成")
    
    return 0 if success else 1

if __name__ == "__main__":
    if not LIBRARY_AVAILABLE:
        sys.exit(1)
    sys.exit(main())