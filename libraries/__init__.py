"""
Robot Framework 測試庫集合
========================

這個套件包含所有自定義的 Robot Framework 測試庫：

- robot_arm_control: 機器手臂控制庫
- voice_control: 語音控制庫  
- mobile_testing: 手機測試庫
- switchbot_smartplug_control: SwitchBot 智慧插座控制庫
- ipcam_light_detection: IP 攝影機燈光檢測庫
- testlink_integration: TestLink 整合庫
- local_voice_verifying: 本地語音驗證庫
- multimodal_detection: 多模態檢測庫

建立日期: 2025-11-12
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Robot Automation Team"
__description__ = "Robot Framework 測試庫集合"

# 匯出所有主要模組
__all__ = [
    "robot_arm_control",
    "voice_control", 
    "mobile_testing",
    "switchbot_smartplug_control",
    "ipcam_light_detection",
    "testlink_integration",
    "local_voice_verifying",
    "multimodal_detection"
]