"""
RV 擴展艙深度標籤面積計算校正工具
開發日期: 2026-03-26

提供在畫面上即時搜尋特定的 ArUco 標籤並計算面積，
幫助工程師得知在「完全收合」與「完全擴充」的物理極限點情況下，
標籤所對應攝影機畫素面積分別為多少，以供後續填寫入 YAML 配置中。

使用方式:
    uv run python scripts/rv_expansion_calibrator.py --target slide_out_wall
"""
import sys
import time
from pathlib import Path
from loguru import logger
import argparse

# 將專案根目錄加入路徑中
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from libraries.rv_space_detection.IPCamExpansionDetection import IPCamExpansionDetection

def main():
    parser = argparse.ArgumentParser(description="RV 空間擴展標籤追蹤校正工具")
    parser.add_argument("--target", type=str, default="slide_out_wall", help="目標標籤名稱 (必須已定義於 ipcam_config.yaml 中)")
    args = parser.parse_args()

    detector = IPCamExpansionDetection()
    try:
        logger.info(f"開始連接 RV攝影機以校正標籤區域：{args.target}...")
        detector.connect_for_expansion_target(args.target)
        
        print("\n" + "=" * 60)
        print("          📸 標籤面積視覺檢測校正程序 (Ctrl+C 結束)        ")
        print("=" * 60)
        print("💡 請利用此工具協助取得面積極限值：")
        print("   1. 先將擴展艙完全「收合」，紀錄此時 terminal 穩定輸出的面積數字")
        print("   2. 再將擴展艙完全「展開」，紀錄此時另一組輸出的較小面積數字")
        print("   3. 將這兩組數字分別填入 ipcam_config.yaml 的 collapsed_area 與 expanded_area")
        print("-" * 60 + "\n")
        
        while True:
            try:
                frame = detector.capture_image()
                area = detector.get_marker_area(frame)
                if area > 0:
                    print(f"[{time.strftime('%H:%M:%S')}] ✅ OpenCV ArUco 追蹤成功! 相對物理深度換算面積: {area:.1f} px^2")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ⚠️ 無法辨識到指定 ID 的標籤，請調整鏡頭或檢查光線遮蔽。")
                time.sleep(1)
            except Exception as loop_e:
                logger.warning(f"計算期間發生警告 (可能遺失畫格): {loop_e}")
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\n結束校正程序。")
    except Exception as e:
        logger.error(f"連線或校正啟動失敗: {e}")
    finally:
        detector.disconnect()

if __name__ == "__main__":
    main()
