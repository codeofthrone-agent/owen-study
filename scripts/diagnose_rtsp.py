#!/usr/bin/env python3
"""
RTSP 連線診斷工具

開發用途：
    診斷指定攝影機的 RTSP 連線問題，包含：
    1. Sanity Check：先測試已知正常攝影機確認環境
    2. 測試目前設定的 RTSP 路徑
    3. 自動掃描 16 種常見替代路徑
    4. 同時測試 TCP 和 UDP 兩種傳輸協議

日期：2026-03-26

功能：
    - 從 config.ipcam_config 讀取攝影機設定（不硬編碼帳密）
    - 支援 CLI 參數指定環境與攝影機名稱
    - 測試 TCP / UDP 雙協議
    - 掃描常見 RTSP 替代路徑
    - 提供排查建議

使用方式：
    # 基本用法（使用預設 taipei_lab → motor）
    uv run python scripts/diagnose_rtsp.py

    # 指定環境與攝影機
    uv run python scripts/diagnose_rtsp.py --env taipei_lab --camera level1
    uv run python scripts/diagnose_rtsp.py --env laboratory --camera motor

    # 跳過 Sanity Check
    uv run python scripts/diagnose_rtsp.py --env laboratory --camera level2 --no-sanity

    # 列出可用環境
    uv run python scripts/diagnose_rtsp.py --list-envs
"""

import sys
import time
import os
import cv2
import argparse
from pathlib import Path

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 載入 .env 環境變數
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

try:
    from config.ipcam_config import (
        get_camera_url,
        get_camera_config,
        list_available_environments,
        list_available_cameras,
    )
except ImportError:
    print("❌ 無法載入 config.ipcam_config，請確認環境設定。")
    sys.exit(1)


def check_rtsp_stream(url: str, description: str) -> bool:
    """
    使用 OpenCV 檢查 RTSP 串流是否可用，同時測試 TCP 和 UDP 傳輸協議。

    Args:
        url:         完整的 RTSP URL（含帳密）
        description: 用於顯示的描述文字

    Returns:
        bool: 任一協議成功即回傳 True
    """
    import re
    safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', url)

    protocols = [
        ('tcp', 'rtsp_transport;tcp|stimeout;5000000'),
        ('udp', 'rtsp_transport;udp|stimeout;5000000'),
    ]

    for proto_name, option in protocols:
        print(f"  測試 [{description}] [{proto_name.upper()}]: {safe_url}")

        # 設定 FFmpeg 傳輸選項
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = option

        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            print(f"    ❌ [{proto_name.upper()}] 無法開啟連線 (isOpened=False)")
            cap.release()
            continue

        # 嘗試讀取一幀以確認串流有效
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            print(f"    ✅ [{proto_name.upper()}] 成功讀取影像！尺寸: {frame.shape}")
            cap.release()
            return True
        else:
            print(f"    ⚠️  [{proto_name.upper()}] 連線已開啟但無法讀取影像 (ret={ret})")

        cap.release()

    return False


def run_sanity_check(env_name: str) -> bool:
    """
    執行環境 Sanity Check：找到第一個可用攝影機並測試連線。
    用途是確認網路環境與帳密設定正確，與目標攝影機無關。

    Args:
        env_name: 環境名稱（例如：taipei_lab）

    Returns:
        bool: Sanity Check 成功與否
    """
    print("\n--- Sanity Check: 確認環境連線正常 ---")
    try:
        cameras = list_available_cameras(env_name)
        if not cameras:
            print(f"  ⚠️  環境 {env_name} 下無攝影機設定，跳過 Sanity Check")
            return True

        # 取第一台攝影機做 Sanity Check
        sanity_cam = cameras[0]
        sanity_url = get_camera_url(env_name, sanity_cam)
        print(f"  使用攝影機: {env_name} → {sanity_cam}")

        if check_rtsp_stream(sanity_url, f"Sanity ({sanity_cam})"):
            print("  ✅ Sanity Check 通過！腳本與環境設定正常。")
            return True
        else:
            print("  ⚠️  Sanity Check 失敗，後續測試結果可能不準確。")
            print("     請先確認：網路連線、.env 帳號密碼、攝影機電源。")
            return False

    except Exception as e:
        print(f"  ❌ Sanity Check 錯誤: {e}")
        return False


def run_target_check(env_name: str, cam_name: str) -> bool:
    """
    測試目標攝影機的目前設定路徑。

    Args:
        env_name: 環境名稱
        cam_name: 攝影機名稱

    Returns:
        bool: 目前設定路徑是否可用
    """
    print(f"\n--- 測試目前設定路徑 ({env_name} → {cam_name}) ---")
    try:
        config = get_camera_config(env_name, cam_name)
        ip = config.get('ip', 'N/A')
        print(f"  攝影機 IP: {ip}")

        current_url = get_camera_url(env_name, cam_name)
        if check_rtsp_stream(current_url, "已設定路徑"):
            print("\n  🎉 目前設定路徑有效！可能之前是暫時性問題。")
            return True
        else:
            print("\n  ❌ 目前設定路徑無法連線，繼續掃描替代路徑...")
            return False

    except Exception as e:
        print(f"  ❌ 測試目標攝影機發生錯誤: {e}")
        return False


def scan_alternative_paths(env_name: str, cam_name: str) -> str | None:
    """
    掃描 16 種常見 RTSP 替代路徑，找到有效路徑即停止。

    Args:
        env_name: 環境名稱
        cam_name: 攝影機名稱

    Returns:
        str | None: 找到的有效路徑，若全部失敗則回傳 None
    """
    print("\n--- 掃描常見替代路徑 ---")

    alternative_paths = [
        "/live0",                              # 常見預設
        "/live1",                              # 常見次串流
        "/stream1",                            # 通用
        "/stream2",
        "/h264",
        "/unicast",
        "/live/ch0",                           # TP-Link / Vivotek
        "/live/ch1",
        "/Streaming/Channels/101",             # Hikvision
        "/cam/realmonitor?channel=1&subtype=0",# Dahua
        "/axis-media/media.amp",               # Axis
        "/video",
        "/media/video1",
        "/onvif-media/media.amp",
        "/12",
        "/11",
    ]

    for path in alternative_paths:
        try:
            test_url = get_camera_url(env_name, cam_name, path)
            if check_rtsp_stream(test_url, f"路徑 {path}"):
                print(f"\n  🎉 找到可用路徑：{path}")
                print(f"     建議更新 config/ipcam_config.yaml 中 {cam_name} 的 stream_path 為 {path}")
                return path
        except Exception as e:
            print(f"  ⚠️  路徑 {path} 測試錯誤: {e}")

    return None


def list_envs_and_cameras():
    """印出所有可用的環境與攝影機清單，供使用者參考。"""
    print("\n=== 可用環境與攝影機清單 ===")
    try:
        envs = list_available_environments()
        for env in envs:
            cameras = list_available_cameras(env)
            print(f"\n📍 {env}:")
            for cam in cameras:
                print(f"   - {cam}")
    except Exception as e:
        print(f"❌ 無法列出環境清單: {e}")


def main():
    """主程式進入點：解析 CLI 參數並依序執行診斷流程。"""
    parser = argparse.ArgumentParser(
        description="RTSP 連線診斷工具 - 診斷攝影機串流連線問題",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python scripts/diagnose_rtsp.py
  python scripts/diagnose_rtsp.py --env taipei_lab --camera level1
  python scripts/diagnose_rtsp.py --env laboratory --camera motor --no-sanity
  python scripts/diagnose_rtsp.py --list-envs
        """
    )
    parser.add_argument(
        '--env',
        type=str,
        default='taipei_lab',
        help='目標環境名稱（預設: taipei_lab）'
    )
    parser.add_argument(
        '--camera',
        type=str,
        default='motor',
        help='目標攝影機名稱（預設: motor）'
    )
    parser.add_argument(
        '--no-sanity',
        action='store_true',
        help='跳過 Sanity Check 步驟'
    )
    parser.add_argument(
        '--list-envs',
        action='store_true',
        help='列出所有可用環境與攝影機清單後結束'
    )

    args = parser.parse_args()

    # 列出環境模式
    if args.list_envs:
        list_envs_and_cameras()
        return 0

    env_name = args.env
    cam_name = args.camera

    print("=" * 55)
    print("  🔍 RTSP 連線診斷工具")
    print("=" * 55)
    print(f"  目標: {env_name} → {cam_name}")
    print("=" * 55)

    # 步驟 1：Sanity Check
    if not args.no_sanity:
        run_sanity_check(env_name)

    # 步驟 2：測試目前設定路徑
    if run_target_check(env_name, cam_name):
        return 0

    # 步驟 3：掃描替代路徑
    found_path = scan_alternative_paths(env_name, cam_name)

    # 步驟 4：最終結論
    print("\n" + "=" * 55)
    if found_path:
        print(f"✅ 診斷完成：找到可用路徑 {found_path}")
    else:
        try:
            config = get_camera_config(env_name, cam_name)
            ip = config.get('ip', 'N/A')
        except Exception:
            ip = 'N/A'

        print("❌ 所有路徑均無法連線，建議排查：")
        print(f"   1. ping {ip}  確認網路連通性")
        print("   2. 確認攝影機電源已開啟")
        print("   3. 確認 .env 中 IPCAM_PASSWORD 正確")
        print("   4. 確認攝影機未被其他程式佔用（RTSP 通常限制連線數）")
        print("   5. 使用 VLC 手動測試 RTSP URL")
    print("=" * 55)

    return 0 if found_path else 1


if __name__ == "__main__":
    sys.exit(main())
