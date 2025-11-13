"""
IP Camera 燈光檢測模組

提供基於 IP Camera 的燈光狀態檢測功能，包括：
- 單燈號檢測（IPCamLightDetection）
- 多燈號陣列檢測（MultiLightDetection）
- 影像擷取與分析
- 亮度分析與強弱判定
- 燈光開關狀態判定
"""

from .IPCamLightDetection import IPCamLightDetection
from .MultiLightDetection import MultiLightDetection

__all__ = ['IPCamLightDetection', 'MultiLightDetection']
__version__ = '1.1.0'
