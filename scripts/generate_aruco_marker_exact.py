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
from reportlab.lib.pagesizes import A4
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


def generate_combined_pdf(marker_ids, marker_size_mm, dictionary_name, output_file, with_border=True, border_width_mm=5, page_size=A4):
    """
    生成包含多個ArUco標記的單一PDF文件
    """
    if dictionary_name not in ARUCO_DICT:
        raise ValueError(f"未知的ArUco字典: {dictionary_name}")

    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[dictionary_name])
    c = canvas.Canvas(output_file, pagesize=page_size)
    page_width, page_height = page_size

    if with_border:
        total_marker_size_mm = marker_size_mm + 2 * border_width_mm
    else:
        total_marker_size_mm = marker_size_mm
    
    total_marker_size_pt = total_marker_size_mm * mm

    spacing = 10 * mm
    cols = int((page_width - 2 * spacing) / (total_marker_size_pt + spacing))
    if cols == 0: cols = 1

    x_margin = (page_width - (cols * total_marker_size_pt + (cols - 1) * spacing)) / 2
    y_margin = y_margin = (page_height - ( (len(marker_ids) + cols - 1) // cols * (total_marker_size_pt + spacing)))/2


    for i, marker_id in enumerate(marker_ids):
        pixels_per_mm = 20
        marker_pixels = int(marker_size_mm * pixels_per_mm)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_pixels)

        if with_border:
            border_pixels = int(border_width_mm * pixels_per_mm)
            bordered_image = np.ones((marker_pixels + 2*border_pixels, marker_pixels + 2*border_pixels), dtype=np.uint8) * 255
            bordered_image[border_pixels:border_pixels+marker_pixels, border_pixels:border_pixels+marker_pixels] = marker_image
            marker_image = bordered_image

        pil_image = Image.fromarray(marker_image)
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        row = i // cols
        col = i % cols
        
        x_pos = x_margin + col * (total_marker_size_pt + spacing)
        y_pos = page_height - y_margin - (row + 1) * total_marker_size_pt - row * spacing
        
        c.drawImage(
            img_reader,
            x_pos, y_pos,
            width=total_marker_size_pt,
            height=total_marker_size_pt,
            preserveAspectRatio=True
        )
        c.drawString(x_pos, y_pos - 12, f"ID: {marker_id}, Size: {marker_size_mm}mm")

    c.save()
    print(f"\n✅ 成功生成合併的ArUco標記PDF: {os.path.abspath(output_file)}")
    print(f"   頁面上有 {len(marker_ids)} 個標記")


def main():
    parser = argparse.ArgumentParser(
        description="生成精確尺寸的ArUco標記PDF（用於校準測試）"
    )
    parser.add_argument("--id", type=int, nargs='+', required=True, help="一個或多個標記ID (例如: 1 2 3 4)")
    parser.add_argument("--size", type=float, required=True, help="標記尺寸（毫米）")
    parser.add_argument("--dict", type=str, default="DICT_4X4_100", help="ArUco字典")
    parser.add_argument("--output", type=str, required=True, help="輸出PDF文件名。如果提供多個ID且未使用--combine，請使用 '{id}' 作為ID的佔位符。")
    parser.add_argument("--no-border", action="store_true", help="不添加白色邊框")
    parser.add_argument("--border-width", type=float, default=5, help="邊框寬度（毫米），預設5mm")
    parser.add_argument("--combine", action="store_true", help="將所有ID合併到一個A4 PDF文件中")

    args = parser.parse_args()

    if args.combine:
        generate_combined_pdf(
            marker_ids=args.id,
            marker_size_mm=args.size,
            dictionary_name=args.dict,
            output_file=args.output,
            with_border=not args.no_border,
            border_width_mm=args.border_width
        )
    else:
        for marker_id in args.id:
            if len(args.id) > 1:
                output_file = args.output.format(id=marker_id)
            else:
                output_file = args.output

            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            generate_aruco_marker_exact(
                marker_id=marker_id,
                marker_size_mm=args.size,
                dictionary_name=args.dict,
                output_file=output_file,
                with_border=not args.no_border,
                border_width_mm=args.border_width
            )


if __name__ == "__main__":
    main()
