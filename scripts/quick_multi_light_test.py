#!/usr/bin/env python3
"""
多燈號陣列快速測試腳本

用於快速驗證多燈號陣列偵測系統是否正常運作。

使用方式:
    python3 quick_multi_light_test.py
"""

import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libraries.ipcam_light_detection.MultiLightDetection import MultiLightDetection
from loguru import logger


def main():
    """主測試流程"""

    print("\n" + "=" * 70)
    print("多燈號陣列偵測系統 - 快速測試")
    print("=" * 70 + "\n")

    try:
        # 步驟 1: 初始化
        print("📌 步驟 1: 初始化偵測器...")
        detector = MultiLightDetection('default_array')
        print(f"   ✅ 偵測器初始化成功")
        print(f"   陣列名稱: {detector.array_config['name']}")
        print(f"   環境: {detector.array_config['environment']}")
        print(f"   攝影機: {detector.array_config['camera']}")
        print(f"   布局: {detector.array_config['layout']['rows']}x{detector.array_config['layout']['cols']}")
        print(f"   ROI 區域數: {len(detector.roi_regions)}\n")

        # 步驟 2: 連接攝影機
        print("📌 步驟 2: 連接陣列攝影機...")
        detector.connect_array_camera()
        print("   ✅ 攝影機連接成功\n")

        # 步驟 3: 偵測所有燈號
        print("📌 步驟 3: 偵測所有燈號...")
        results = detector.detect_all_lights()
        print(f"   ✅ 偵測完成，共 {len(results)} 個燈號\n")

        # 步驟 4: 顯示摘要資訊
        print("📌 步驟 4: 統計摘要")
        summary = detector.get_light_status_summary()
        print(f"   總燈泡數: {summary['total_lights']}")
        print(f"   開啟數量: {summary['on_count']}")
        print(f"   關閉數量: {summary['off_count']}")
        print(f"   不確定數量: {summary['uncertain_count']}")
        print(f"   平均亮度: {summary['average_brightness']:.2f}")
        print(f"   等級分布: {summary['level_counts']}\n")

        # 步驟 5: 顯示個別燈號狀態
        print("📌 步驟 5: 個別燈號狀態")
        print("   " + "-" * 66)
        print(f"   {'名稱':<12} {'鍵值':<8} {'亮度':<10} {'等級':<12} {'狀態':<8}")
        print("   " + "-" * 66)

        for light_key, result in sorted(results.items()):
            status = "🟢 開啟" if result['is_on'] else "🔴 關閉"
            print(
                f"   {result['name']:<12} "
                f"{light_key:<8} "
                f"{result['brightness']:<10.2f} "
                f"{result['brightness_level']:<12} "
                f"{status:<8}"
            )

        print("   " + "-" * 66 + "\n")

        # 步驟 6: 儲存標註影像
        print("📌 步驟 6: 儲存視覺化影像...")
        output_path = "/tmp/multi_light_quick_test.jpg"
        detector.save_annotated_image(output_path)
        print(f"   ✅ 標註影像已儲存: {output_path}\n")

        # 步驟 7: 測試單一燈號偵測
        print("📌 步驟 7: 測試單一燈號偵測（燈泡 A1）...")
        single_result = detector.detect_single_light('0_0')
        print(f"   燈泡名稱: {single_result['name']}")
        print(f"   亮度值: {single_result['brightness']:.2f}")
        print(f"   亮度等級: {single_result['brightness_level']}")
        print(f"   是否開啟: {single_result['is_on']}")
        print(f"   是否關閉: {single_result['is_off']}\n")

        # 步驟 8: 清理
        print("📌 步驟 8: 清理資源...")
        detector.disconnect()
        print("   ✅ 攝影機已斷開\n")

        # 測試總結
        print("=" * 70)
        print("🎉 測試完成！系統運作正常。")
        print("=" * 70 + "\n")

        print("💡 接下來可以:")
        print("   1. 檢查儲存的影像: " + output_path)
        print("   2. 使用視覺化工具: python3 scripts/visualize_light_array.py --interactive")
        print("   3. 執行完整測試: robot tests/ipcam_testing/multi_light_array_test.robot")
        print("   4. 查看使用文檔: docs/multi_light_array_detection_guide.md\n")

        return 0

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ 測試失敗")
        print("=" * 70)
        print(f"\n錯誤訊息: {e}\n")

        # 常見問題排查提示
        print("🔍 故障排查提示:")
        print("   1. 確認 IP Camera 已開機並可連線")
        print("   2. 檢查 .env 中的 IPCAM_USERNAME 和 IPCAM_PASSWORD")
        print("   3. 確認 config/ipcam_config.yaml 配置正確")
        print("   4. 確認已安裝依賴: uv pip install -r requirements.txt")
        print("   5. 執行: export PYTHONPATH=\"${PYTHONPATH}:$(pwd)\"")
        print("   6. 查看詳細日誌: python3 -c 'from loguru import logger; logger.enable(__name__)'")
        print("\n")

        import traceback
        traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())
