"""
音訊系統配置管理
用於 Scarlett 4i4 四聲道獨立控制
"""
from pathlib import Path

# Scarlett 設備配置
SCARLETT_DEVICE_NAME = "Scarlett 4i4 4th Gen"
SCARLETT_CARD_PATTERN = "alsa_card.usb-Focusrite_Scarlett_4i4_4th_Gen*"

# 虛擬音訊設備名稱
VIRTUAL_SINKS = {
    "channels_1_2": "Scarlett_1-2",
    "channels_3_4": "Scarlett_3-4"
}

# 聲道映射
CHANNEL_MAPPING = {
    1: {"sink": "Scarlett_1-2", "physical_output": 1},
    2: {"sink": "Scarlett_1-2", "physical_output": 2},
    3: {"sink": "Scarlett_3-4", "physical_output": 3},
    4: {"sink": "Scarlett_3-4", "physical_output": 4}
}

# 測試配置
# 假設測試音訊檔案位於 libraries/voice_control 目錄下
TEST_AUDIO_FILE = Path(__file__).parent.parent / "libraries/voice_control/file_example_WAV_2MG.wav"
DEFAULT_DURATION = 5  # 秒
STRESS_TEST_ROUNDS = 3

# PipeWire 配置
PIPEWIRE_CONFIG = {
    "pro_audio_profile": "pro-audio",
    "sample_rate": 48000,
    "channels": 2,
    "format": "S16_LE"
}
