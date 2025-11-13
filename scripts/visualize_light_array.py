#!/usr/bin/env python3
"""
燈號陣列視覺化與調試工具

用於視覺化檢查燈號陣列的 ROI 劃分和偵測結果。

使用方式:
    python3 visualize_light_array.py --array default_array --output /tmp/visualization.jpg
    python3 visualize_light_array.py --interactive  # 互動模式

功能:
    - 顯示 ROI 區域劃分
    - 標註每個燈泡的名稱、亮度和狀態
    - 產生偵測結果圖表
    - 互動式調整 ROI 區域（計劃中）
"""

import sys
import argparse
from pathlib import Path

# 加入專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
from loguru import logger
from libraries.ipcam_light_detection.MultiLightDetection import MultiLightDetection


def visualize_array(array_name: str, output_path: str = None, interactive: bool = False):
    """
    視覺化燈號陣列

    Args:
        array_name (str): 陣列配置名稱
        output_path (str, optional): 輸出影像路徑
        interactive (bool): 是否啟用互動模式
    """
    try:
        logger.info(f"初始化燈號陣列偵測器: {array_name}")
        detector = MultiLightDetection(array_name)

        logger.info("連接陣列攝影機...")
        detector.connect_array_camera()

        logger.info("偵測所有燈號...")
        results = detector.detect_all_lights()

        logger.info("產生視覺化影像...")

        # 取得當前影像
        image = detector.current_image.copy()
        height, width = image.shape[:2]

        # 建立視覺化圖層
        overlay = image.copy()

        # 繪製每個 ROI
        for light_key, result in sorted(results.items()):
            roi_info = detector.roi_regions[light_key]
            x_min, y_min, x_max, y_max = roi_info['roi_absolute']

            # 根據狀態選擇顏色
            if result['is_on']:
                color = (0, 255, 0)  # 綠色（開啟）
                status_text = "ON"
            else:
                color = (0, 0, 255)  # 紅色（關閉）
                status_text = "OFF"

            # 繪製 ROI 矩形（帶半透明背景）
            cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), color, 2)

            # 繪製填充矩形（作為文字背景）
            text_bg_y = y_min - 60 if y_min > 60 else y_max + 10
            cv2.rectangle(
                overlay,
                (x_min, text_bg_y),
                (x_max, text_bg_y + 50),
                color,
                -1  # 填充
            )

            # 燈泡名稱
            cv2.putText(
                overlay,
                result['name'],
                (x_min + 5, text_bg_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # 亮度值
            brightness_text = f"{result['brightness']:.1f}"
            cv2.putText(
                overlay,
                brightness_text,
                (x_min + 5, text_bg_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

            # 狀態文字
            cv2.putText(
                overlay,
                status_text,
                (x_min + 5, y_min + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            # 亮度等級
            level_text = result['brightness_level'].upper()
            cv2.putText(
                overlay,
                level_text,
                (x_min + 5, y_min + 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )

        # 混合原始影像和覆蓋層（0.7 透明度）
        alpha = 0.7
        visualized = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

        # 新增標題資訊
        summary = detector.get_light_status_summary()
        title_text = [
            f"Array: {detector.array_config['name']}",
            f"Total: {summary['total_lights']} | ON: {summary['on_count']} | OFF: {summary['off_count']}",
            f"Avg Brightness: {summary['average_brightness']:.1f}"
        ]

        # 繪製標題背景
        title_height = 80
        cv2.rectangle(visualized, (0, 0), (width, title_height), (0, 0, 0), -1)

        # 繪製標題文字
        y_offset = 25
        for line in title_text:
            cv2.putText(
                visualized,
                line,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y_offset += 25

        # 儲存或顯示
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_file), visualized)
            logger.info(f"✅ 視覺化影像已儲存: {output_file}")

        if interactive:
            logger.info("顯示互動視窗（按 Q 鍵關閉）")
            cv2.imshow("Light Array Visualization", visualized)
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
            cv2.destroyAllWindows()

        # 斷開連線
        detector.disconnect()

        # 輸出文字報告
        print("\n" + "=" * 70)
        print("燈號陣列偵測報告")
        print("=" * 70)
        print(f"\n陣列名稱: {detector.array_config['name']}")
        print(f"環境: {detector.array_config['environment']}")
        print(f"攝影機: {detector.array_config['camera']}")
        print(f"布局: {detector.array_config['layout']['rows']}x{detector.array_config['layout']['cols']}")
        print(f"\n總燈泡數: {summary['total_lights']}")
        print(f"開啟數量: {summary['on_count']}")
        print(f"關閉數量: {summary['off_count']}")
        print(f"平均亮度: {summary['average_brightness']:.2f}")
        print(f"等級分布: {summary['level_counts']}")

        print("\n個別燈號狀態:")
        print("-" * 70)
        print(f"{'名稱':<12} {'鍵值':<8} {'亮度':<10} {'等級':<10} {'狀態':<8}")
        print("-" * 70)

        for light_key, result in sorted(results.items()):
            status = "開啟" if result['is_on'] else "關閉"
            print(
                f"{result['name']:<12} "
                f"{light_key:<8} "
                f"{result['brightness']:<10.2f} "
                f"{result['brightness_level']:<10} "
                f"{status:<8}"
            )

        print("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"視覺化失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description="燈號陣列視覺化與調試工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 基本使用（儲存影像）
  python3 visualize_light_array.py --array default_array --output /tmp/viz.jpg

  # 互動模式
  python3 visualize_light_array.py --interactive

  # 指定陣列並顯示互動視窗
  python3 visualize_light_array.py --array custom_array --output result.jpg --interactive
        """
    )

    parser.add_argument(
        '--array',
        type=str,
        default='default_array',
        help='陣列配置名稱（預設: default_array）'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='輸出影像路徑（例如: /tmp/visualization.jpg）'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='啟用互動模式（顯示視窗）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細日誌'
    )

    args = parser.parse_args()

    # 設定日誌級別
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    # 執行視覺化
    visualize_array(
        array_name=args.array,
        output_path=args.output,
        interactive=args.interactive
    )


if __name__ == "__main__":
    main()
