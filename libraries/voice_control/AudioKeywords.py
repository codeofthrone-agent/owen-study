#!/usr/bin/env python3
"""
Robot Framework 音频测试关键字库
提供更多测试相关的自定义关键字
"""

from ultimate_play import AudioPlayer, play_audio_to_channel
import subprocess
from typing import List, Dict


class AudioKeywords:
    """音频测试关键字库"""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.current_sink = None

    def play_audio_to_channel(self, audio_file: str, channel: int, duration: int = 5) -> bool:
        """
        播放音频到指定声道

        参数:
        - audio_file: 音频文件路径
        - channel: 目标声道 (1-4)
        - duration: 播放时长（秒）

        返回: True表示成功，False表示失败
        """
        return play_audio_to_channel(audio_file, int(channel), int(duration))

    def get_current_default_sink(self) -> str:
        """获取当前默认音频输出设备"""
        try:
            result = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                check=True
            )
            self.current_sink = result.stdout.strip()
            return self.current_sink
        except subprocess.CalledProcessError:
            return ""

    def verify_sink_is(self, expected_sink: str) -> bool:
        """
        验证当前默认sink是否为期望值

        参数:
        - expected_sink: 期望的sink名称

        返回: True表示匹配，False表示不匹配
        """
        current = self.get_current_default_sink()
        return current == expected_sink

    def list_available_sinks(self) -> List[str]:
        """列出所有可用的音频输出设备"""
        try:
            result = subprocess.run(
                ["pactl", "list", "short", "sinks"],
                capture_output=True,
                text=True,
                check=True
            )
            sinks = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # 格式: ID NAME ...
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sinks.append(parts[1])
            return sinks
        except subprocess.CalledProcessError:
            return []

    def check_scarlett_sinks_exist(self) -> bool:
        """检查 Scarlett 虚拟设备是否存在"""
        sinks = self.list_available_sinks()
        has_1_2 = "Scarlett_1-2" in sinks
        has_3_4 = "Scarlett_3-4" in sinks
        return has_1_2 and has_3_4

    def get_sink_for_channel(self, channel: int) -> str:
        """
        根据声道号返回应该使用的sink名称

        参数:
        - channel: 声道号 (1-4)

        返回: sink名称
        """
        if int(channel) in [1, 2]:
            return "Scarlett_1-2"
        else:
            return "Scarlett_3-4"

    def test_all_channels_sequentially(self, audio_file: str, duration: int = 5) -> Dict[int, bool]:
        """
        依次测试所有4个声道

        参数:
        - audio_file: 音频文件路径
        - duration: 每个声道播放时长（秒）

        返回: 字典，键为声道号，值为是否成功
        """
        results = {}
        for channel in range(1, 5):
            print(f"正在测试声道 {channel}...")
            success = play_audio_to_channel(audio_file, channel, int(duration))
            results[channel] = success
            print(f"声道 {channel} 测试{'成功' if success else '失败'}")
        return results

    def verify_all_channels_passed(self, results: Dict[int, bool]) -> bool:
        """
        验证所有声道测试是否都通过

        参数:
        - results: test_all_channels_sequentially 的返回结果

        返回: True表示全部通过，False表示有失败
        """
        return all(results.values())
