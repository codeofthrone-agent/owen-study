#!/usr/bin/env python3
"""
生成精確尺寸的ArUco標記（無邊框、無標題）

用於手眼校準測試，確保列印尺寸精確
"""

import cv2
import numpy as np
import argparse
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# ArUco字典映射
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
}


def generate_aruco_marker_exact(marker_id, marker_size_mm, dictionary_name, output_file, with_border=True, border_width_mm=5):
    """
    生成精確尺寸的ArUco標記PDF

    Args:
        marker_id: 標記ID
        marker_size_mm: 標記尺寸（毫米）
        dictionary_name: ArUco字典名稱
        output_file: 輸出文件路徑
        with_border: 是否添加白色邊框
        border_width_mm: 邊框寬度（毫米）
    """
    if dictionary_name not in ARUCO_DICT:
        raise ValueError(f"未知的ArUco字典: {dictionary_name}")

    # 生成ArUco標記圖像
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[dictionary_name])

    # 生成高解析度圖像（每mm 20像素）
    pixels_per_mm = 20
    marker_pixels = int(marker_size_mm * pixels_per_mm)

    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_pixels)

    # 如果需要邊框，添加白色邊框
    if with_border:
        border_pixels = int(border_width_mm * pixels_per_mm)
        bordered_image = np.ones((marker_pixels + 2*border_pixels, marker_pixels + 2*border_pixels), dtype=np.uint8) * 255
        bordered_image[border_pixels:border_pixels+marker_pixels, border_pixels:border_pixels+marker_pixels] = marker_image
        marker_image = bordered_image
        total_size_mm = marker_size_mm + 2 * border_width_mm
    else:
        total_size_mm = marker_size_mm

    # 轉換為PIL圖像
    pil_image = Image.fromarray(marker_image)

    # 創建PDF（使用ReportLab以確保精確尺寸）
    c = canvas.Canvas(output_file, pagesize=(total_size_mm * mm, total_size_mm * mm))

    # 保存圖像到內存緩衝區
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # 使用ImageReader包裝
    img_reader = ImageReader(img_buffer)

    # 在PDF中繪製圖像（精確尺寸）
    c.drawImage(
        img_reader,
        0, 0,
        width=total_size_mm * mm,
        height=total_size_mm * mm,
        preserveAspectRatio=True
    )

    c.save()

    print(f"\n✅ 成功生成ArUco標記: {os.path.abspath(output_file)}")
    print(f"   字典: {dictionary_name}")
    print(f"   ID: {marker_id}")
    print(f"   標記尺寸: {marker_size_mm}mm × {marker_size_mm}mm")
    if with_border:
        print(f"   邊框寬度: {border_width_mm}mm")
        print(f"   總尺寸: {total_size_mm}mm × {total_size_mm}mm")
    print(f"\n⚠️  重要提示:")
    print(f"   1. 列印時必須選擇「實際尺寸」或「100%縮放」")
    print(f"   2. 不要選擇「適合頁面」")
    print(f"   3. 列印後用尺測量：標記應為 {marker_size_mm}mm × {marker_size_mm}mm")
    if with_border:
        print(f"   4. 含邊框總尺寸應為 {total_size_mm}mm × {total_size_mm}mm")


def main():
    parser = argparse.ArgumentParser(
        description="生成精確尺寸的ArUco標記PDF（用於校準測試）"
    )
    parser.add_argument("--id", type=int, required=True, help="標記ID")
    parser.add_argument("--size", type=float, required=True, help="標記尺寸（毫米）")
    parser.add_argument("--dict", type=str, default="DICT_4X4_100", help="ArUco字典")
    parser.add_argument("--output", type=str, required=True, help="輸出PDF文件名")
    parser.add_argument("--no-border", action="store_true", help="不添加白色邊框")
    parser.add_argument("--border-width", type=float, default=5, help="邊框寬度（毫米），預設5mm")

    args = parser.parse_args()

    # 創建輸出目錄
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    generate_aruco_marker_exact(
        marker_id=args.id,
        marker_size_mm=args.size,
        dictionary_name=args.dict,
        output_file=args.output,
        with_border=not args.no_border,
        border_width_mm=args.border_width
    )


if __name__ == "__main__":
    main()
