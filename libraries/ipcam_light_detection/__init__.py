"""
IP Camera 燈光檢測模組

提供基於 IP Camera 的燈光狀態檢測功能，包括：
- 單燈號檢測（IPCamLightDetection）
- 影像擷取與分析
- 亮度分析與強弱判定
- 燈光開關狀態判定

注意: 多燈號陣列檢測已整合至 libraries/robot_arm_control/local_vision_analyzer.py
"""

from .IPCamLightDetection import IPCamLightDetection

__all__ = ['IPCamLightDetection']
__version__ = '1.2.0'
