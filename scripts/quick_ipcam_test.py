#!/usr/bin/env python3
"""
快速測試 IP Camera RTSP 連線

直接測試三個攝影機是否能成功連接並擷取影像
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import cv2
    from config.ipcam_config import get_camera_url
    print("✅ 模組載入成功\n")
except ImportError as e:
    print(f"❌ 模組載入失敗: {e}")
    print("\n請安裝必要套件: pip install opencv-python pyyaml python-dotenv")
    sys.exit(1)


def test_camera(camera_name: str, ip: str):
    """測試單一攝影機連線"""
    print(f"{'=' * 60}")
    print(f"測試攝影機: {camera_name} ({ip})")
    print(f"{'=' * 60}")

    try:
        # 建立 RTSP URL
        rtsp_url = get_camera_url('laboratory', camera_name)

        # 隱藏密碼顯示
        safe_url = rtsp_url
        if '@' in rtsp_url:
            parts = rtsp_url.split('@')
            auth_part = parts[0].split('://')[-1]
            if ':' in auth_part:
                username = auth_part.split(':')[0]
                safe_url = rtsp_url.replace(auth_part, f"{username}:****")

        print(f"RTSP URL: {safe_url}")
        print("正在連接...")

        # 設定 FFmpeg 選項以支援 HEVC/H.265 和 TCP 傳輸
        import os
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|analyzeduration;20000000|probesize;20000000'
        print("  已設定 FFmpeg 選項: TCP 傳輸 + HEVC 支援")

        # 建立 VideoCapture
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print("❌ 無法開啟 RTSP 串流")
            print("   可能原因:")
            print("   1. 網路無法連接到該 IP")
            print("   2. RTSP 服務未啟動")
            print("   3. 帳號密碼錯誤")
            print("   4. 串流路徑錯誤")
            return False

        print("✅ RTSP 連線成功")
        print("正在擷取影像幀（可能需要幾秒鐘）...")

        # 設定緩衝區大小
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # 跳過前幾幀讓串流穩定
        print("  跳過前 10 幀以穩定串流...")
        for i in range(10):
            ret, _ = cap.read()
            if not ret:
                print(f"    警告: 第 {i+1} 幀讀取失敗")

        # 嘗試讀取實際測試幀
        print("  開始讀取測試幀...")
        success_count = 0
        test_frames = 5
        for i in range(test_frames):
            ret, frame = cap.read()
            if ret and frame is not None:
                success_count += 1
                print(f"    ✓ 幀 {i+1}/{test_frames} 成功 (尺寸: {frame.shape})")
            else:
                print(f"    ✗ 幀 {i+1}/{test_frames} 失敗")

        cap.release()

        if success_count > 0:
            print(f"✅ 成功擷取 {success_count}/5 幀影像")
            if success_count == 5:
                print(f"   影像尺寸: {frame.shape}")
                print("   ✨ 攝影機工作正常！")
            else:
                print("   ⚠️  部分幀擷取失敗，可能網路不穩定")
            return True
        else:
            print("❌ 無法擷取影像幀")
            print("   串流可能已中斷或格式不支援")
            return False

    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        return False
    finally:
        print()


def main():
    """主測試流程"""
    print("\n" + "🎥" * 30)
    print("   IP Camera RTSP 連線快速測試")
    print("🎥" * 30 + "\n")

    cameras = [
        ('level1', '192.168.165.184'),
        ('level2', '192.168.165.127'),
        ('motor', '10.42.0.39'),
    ]

    results = {}

    for camera_name, ip in cameras:
        results[camera_name] = test_camera(camera_name, ip)

    # 顯示總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)

    for camera_name, success in results.items():
        status = "✅ 正常" if success else "❌ 失敗"
        print(f"{camera_name:15s} {status}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n成功: {success_count}/{total_count}")

    if success_count == total_count:
        print("\n🎉 所有攝影機測試通過！可以執行 Robot Framework 測試了。")
        print("\n下一步:")
        print("  robot --include smoke tests/ipcam_testing/")
        return 0
    elif success_count > 0:
        print("\n⚠️  部分攝影機測試失敗，請檢查失敗的攝影機連線。")
        return 1
    else:
        print("\n❌ 所有攝影機測試失敗，請檢查:")
        print("  1. 網路連線")
        print("  2. .env 中的帳號密碼")
        print("  3. 攝影機是否開啟")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
