"""
開發用途: RV 車內身縮空間 影像辨識庫初始化模組
開發日期: 2026-04-01
功能: 暴露 ipcam_ArUco_detection 底下的主要模組
使用方式: import libraries.ipcam_ArUco_detection
"""

from .ArUcoSpaceDetection import ArUcoSpaceDetection

__all__ = ["ArUcoSpaceDetection"]
