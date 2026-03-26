"""
RV 空間擴展標籤 PDF 產生器
開發日期: 2026-03-26

此腳本用於生成精確尺寸（預設 15x15 cm）的 ArUco 標籤 PDF 文件，
產生出來的 PDF 為 A4 尺寸，將標籤置中，方便直接張貼於 RV 車空間擴展牆面。

前置需求:
    uv pip install reportlab opencv-contrib-python

使用方式:
    # 預設產生 ID=0
    uv run python scripts/generate_aruco_pdf.py
    
    # 產生多個或是指定 ID 與外輸檔名
    uv run python scripts/generate_aruco_pdf.py --id 1 --output marker_1.pdf
"""

import sys
import argparse
from pathlib import Path
from loguru import logger
import tempfile
import os

try:
    import cv2
    import cv2.aruco as aruco
except ImportError:
    logger.error("缺少 OpenCV，請執行: uv pip install opencv-contrib-python")
    sys.exit(1)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
except ImportError:
    logger.error("缺少 reportlab，無法產生精確 PDF，請執行: uv pip install reportlab")
    sys.exit(1)

def generate_pdf(marker_id: int, output_path: str, size_cm: float = 15.0):
    """
    產生包含 ArUco 標籤的 A4 PDF 檔案
    """
    logger.info(f"準備產生 ArUco ID: {marker_id} (DICT_4X4_50)")
    
    # 1. 產生高解析度的 ArUco numpy 陣列影像
    # 設定為 1000x1000 像素以確保列印清晰度，這不影響它的物理公分大小
    pixel_size = 1000
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    marker_image = aruco.generateImageMarker(dictionary, marker_id, pixel_size)
    
    # 將影像寫入暫存檔供 reportlab 讀取
    temp_img_path = tempfile.mktemp(suffix='.png')
    cv2.imwrite(temp_img_path, marker_image)
    
    try:
        # 2. 建立 A4 PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4
        
        # 換算公分為點數 (Points)
        target_size_pts = size_cm * cm
        
        # 3. 計算置中座標
        x_offset = (page_width - target_size_pts) / 2
        y_offset = (page_height - target_size_pts) / 2
        
        # 4. 在 PDF 繪製注意事項與版權/標題文字
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_offset, y_offset + target_size_pts + 1.5 * cm, "RV Space Expansion Tracking Marker")
        
        c.setFont("Helvetica", 12)
        c.drawString(x_offset, y_offset + target_size_pts + 0.8 * cm, f"Type: DICT_4X4_50 | ID: {marker_id}")
        c.drawString(x_offset, y_offset + target_size_pts + 0.3 * cm, f"Target Physical Size: {size_cm}x{size_cm} cm")
        
        # 使用紅色畫出警告標語，提醒列印時不要縮放
        c.setFillColorRGB(0.8, 0, 0)
        c.drawString(x_offset, y_offset - 1.0 * cm, "IMPORTANT: Please print at 100% scale (Actual Size)")
        c.drawString(x_offset, y_offset - 1.5 * cm, "Do NOT select \"Fit to Page\" or the depth calibration will fail.")
        
        # 5. 繪製裁切黑白方塊 (Marker) 於正中間
        c.drawImage(temp_img_path, x_offset, y_offset, width=target_size_pts, height=target_size_pts)
        
        # 將外框畫出來方便工程師剪裁 (給標籤加上 1 point 寬度的灰色外剪裁線)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(1)
        c.rect(x_offset, y_offset, target_size_pts, target_size_pts)
        
        c.save()
        logger.info(f"✅ 成功產出實體尺寸為 {size_cm}x{size_cm} cm 的標籤檔: {output_path}")

    finally:
        # 清理暫存圖片
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

def main():
    parser = argparse.ArgumentParser(description="RV 空間擴展標籤 A4 列印檔 (PDF) 產生器")
    parser.add_argument("--id", type=int, default=0, help="ArUco 標籤編號 (預設為 0)")
    parser.add_argument("--size", type=float, default=15.0, help="列印出來的標籤寬長公分 (預設為 15.0)")
    parser.add_argument("--output", type=str, default="", help="輸出檔名 (預設為 marker_id_X.pdf)")
    args = parser.parse_args()

    # 自動決定輸出檔名
    output_path = args.output
    if not output_path:
        output_path = f"marker_id_{args.id}_{args.size}x{args.size}cm.pdf"

    # 取得絕對路徑，方便提示
    output_full_path = str(Path(output_path).resolve())
    
    try:
        generate_pdf(args.id, output_full_path, args.size)
    except Exception as e:
        logger.error(f"產生 PDF 失敗: {e}")

if __name__ == "__main__":
    main()
