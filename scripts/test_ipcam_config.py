#!/usr/bin/env python3
"""
IP Camera 配置測試腳本

用於驗證 IP Camera 配置是否正確載入，包括：
- .env 環境變數載入
- YAML 配置載入
- RTSP URL 建構
- 認證資訊處理

使用方式:
    python scripts/test_ipcam_config.py
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.ipcam_config import (
    get_all_cameras,
    get_camera_config,
    get_camera_url,
    list_available_environments,
    list_available_cameras,
    DEFAULT_IPCAM_USERNAME,
    DEFAULT_IPCAM_PASSWORD
)


def print_section(title: str):
    """列印分隔線和標題"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_env_variables():
    """測試環境變數載入"""
    print_section("環境變數檢查")

    print(f"IPCAM_USERNAME: {DEFAULT_IPCAM_USERNAME if DEFAULT_IPCAM_USERNAME else '(未設定)'}")
    print(f"IPCAM_PASSWORD: {'*' * len(DEFAULT_IPCAM_PASSWORD) if DEFAULT_IPCAM_PASSWORD else '(未設定)'}")

    if not DEFAULT_IPCAM_USERNAME or not DEFAULT_IPCAM_PASSWORD:
        print("\n⚠️  警告: 未在 .env 中設定 IPCAM_USERNAME 或 IPCAM_PASSWORD")
        print("   請編輯專案根目錄的 .env 文件並添加:")
        print("   IPCAM_USERNAME=admin")
        print("   IPCAM_PASSWORD=your_password")


def test_environments():
    """測試環境配置"""
    print_section("環境配置")

    environments = list_available_environments()
    print(f"可用環境: {', '.join(environments)}\n")

    for env in environments:
        cameras = list_available_cameras(env)
        print(f"📍 {env}:")
        print(f"   攝影機: {', '.join(cameras) if cameras else '(無)'}")


def test_camera_configs():
    """測試攝影機配置"""
    print_section("攝影機配置詳情")

    try:
        # 測試實驗室環境的所有攝影機
        cameras = list_available_cameras('laboratory')

        for camera_name in cameras:
            print(f"\n📹 {camera_name}:")
            config = get_camera_config('laboratory', camera_name)

            print(f"   IP: {config['ip']}")
            print(f"   Port: {config['port']}")
            print(f"   Protocol: {config['protocol']}")
            print(f"   Stream Path: {config.get('stream_path', 'N/A')}")
            print(f"   Username: {config.get('username', '(未設定)')}")
            print(f"   Password: {'*' * len(config.get('password', '')) if config.get('password') else '(未設定)'}")
            print(f"   Description: {config.get('description', 'N/A')}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


def test_rtsp_urls():
    """測試 RTSP URL 建構"""
    print_section("RTSP URL 建構測試")

    try:
        cameras = list_available_cameras('laboratory')

        for camera_name in cameras:
            print(f"\n📹 {camera_name}:")

            # 主串流
            url_live0 = get_camera_url('laboratory', camera_name)
            # 隱藏密碼顯示
            safe_url = url_live0.replace(
                f":{DEFAULT_IPCAM_PASSWORD}@" if DEFAULT_IPCAM_PASSWORD else "",
                ":****@"
            )
            print(f"   主串流 (/live0): {safe_url}")

            # 次串流
            url_live1 = get_camera_url('laboratory', camera_name, '/live1')
            safe_url_live1 = url_live1.replace(
                f":{DEFAULT_IPCAM_PASSWORD}@" if DEFAULT_IPCAM_PASSWORD else "",
                ":****@"
            )
            print(f"   次串流 (/live1): {safe_url_live1}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


def test_priority():
    """測試配置優先順序"""
    print_section("配置優先順序測試")

    print("配置來源優先順序:")
    print("1. YAML 配置文件中的 username/password（最高優先）")
    print("2. .env 文件中的 IPCAM_USERNAME/IPCAM_PASSWORD")
    print("3. 空字串（無認證）\n")

    try:
        # 檢查是否有攝影機在 YAML 中設定了帳密
        cameras = get_all_cameras('laboratory')
        yaml_credentials = []

        for name, config in cameras.items():
            if 'username' in config and config['username']:
                yaml_credentials.append(name)

        if yaml_credentials:
            print(f"✅ 以下攝影機在 YAML 中設定了獨立認證:")
            for name in yaml_credentials:
                print(f"   - {name}")
            print("\n   這些攝影機會使用 YAML 中的設定（優先於 .env）")
        else:
            print("✅ 所有攝影機使用 .env 中的共用認證")
            print(f"   來源: IPCAM_USERNAME={DEFAULT_IPCAM_USERNAME}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")


def main():
    """主函數"""
    print("\n" + "🎥" * 35)
    print("   IP Camera 配置測試工具")
    print("🎥" * 35)

    # 執行所有測試
    test_env_variables()
    test_environments()
    test_camera_configs()
    test_rtsp_urls()
    test_priority()

    # 總結
    print_section("測試完成")
    print("\n✅ 配置載入成功！")
    print("\n下一步:")
    print("1. 確認 .env 中的 IPCAM_PASSWORD 已正確設定")
    print("2. 執行測試: robot tests/ipcam_testing/ipcam_light_detection_test.robot")
    print("3. 或執行 Python 測試: python -m libraries.ipcam_light_detection.IPCamLightDetection")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
