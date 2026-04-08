"""
開發用途: Aqara FP2 空間雷達影像辨識與狀態讀取模組
開發日期: 2026-04-08
功能: 暴露 fp2_detect 底下的主要模組 (FP2Keywords)
使用方式: import libraries.fp2_detect
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from FP2Keywords import FP2Keywords
except ImportError:
    from .FP2Keywords import FP2Keywords

__all__ = ["FP2Keywords"]
