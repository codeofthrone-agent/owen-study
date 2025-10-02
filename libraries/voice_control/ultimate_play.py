#!/usr/bin/env python3
"""
音频播放脚本 - Python版本
支持自动切换PipeWire输出设备并播放到指定声道
可与 Robot Framework 集成使用
"""

import sys
import subprocess
import os
from typing import Tuple


class AudioPlayer:
    """音频播放器类"""

    def __init__(self, audio_file: str, target_channel: int):
        """
        初始化音频播放器

        Args:
            audio_file: 音频文件路径
            target_channel: 目标逻辑声道 (1-4)
        """
        self.audio_file = audio_file
        self.target_channel = target_channel
        self.sink_name = ""
        self.pan_filter = ""
        self.physical_output = 0

    def validate_inputs(self) -> bool:
        """验证输入参数"""
        if not os.path.exists(self.audio_file):
            print(f"错误: 音频文件不存在: {self.audio_file}")
            return False

        if self.target_channel not in [1, 2, 3, 4]:
            print(f"错误: 目标逻辑声道必须是 1 到 4 之间的数字，当前值: {self.target_channel}")
            return False

        return True

    def configure_routing(self) -> None:
        """根据目标声道配置路由参数"""
        # 决定使用哪个虚拟设备
        if self.target_channel in [1, 2]:
            self.sink_name = "Scarlett_1-2"
        else:
            self.sink_name = "Scarlett_3-4"

        # 决定声道映射（左或右）
        if self.target_channel in [1, 3]:
            self.pan_filter = "pan=stereo|c0=1*c0|c1=0*c0"
            self.physical_output = 1 if self.target_channel == 1 else 3
        else:
            self.pan_filter = "pan=stereo|c0=0*c0|c1=1*c0"
            self.physical_output = 2 if self.target_channel == 2 else 4

    def switch_output_device(self) -> bool:
        """切换系统默认输出设备"""
        print(f"(步骤 1/3) 正在将系统默认输出切换到: {self.sink_name} ...")

        try:
            result = subprocess.run(
                ["pactl", "set-default-sink", self.sink_name],
                capture_output=True,
                text=True,
                check=True
            )
            print("    ✅ 切换成功。")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ 错误：切换输出设备失败！")
            print(f"    原因: {e.stderr}")
            print("    请确认 setup_pipewire_routing_v3.sh 是否已成功执行。")
            return False

    def play_audio(self, duration: int = 5) -> bool:
        """
        播放音频

        Args:
            duration: 播放时长（秒），默认5秒

        Returns:
            bool: 播放是否成功
        """
        print(f"(步骤 2/3) 准备播放到逻辑声道 {self.target_channel}...")
        print(f"    - 声音应从【物理输出 {self.physical_output}】播放出来。")
        print(f"(步骤 3/3) 播放 {duration} 秒钟...")

        # 构建 ffmpeg 命令
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", self.audio_file,
            "-t", str(duration),
            "-af", self.pan_filter,
            "-ar", "48000",
            "-ac", "2",
            "-f", "s16le",
            "-"
        ]

        # 构建 aplay 命令
        aplay_cmd = [
            "aplay",
            "-f", "S16_LE",
            "-r", "48000",
            "-c", "2"
        ]

        try:
            # 使用管道连接 ffmpeg 和 aplay
            ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            aplay_process = subprocess.Popen(
                aplay_cmd,
                stdin=ffmpeg_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 关闭 ffmpeg 的 stdout（让 aplay 接管）
            ffmpeg_process.stdout.close()

            # 等待两个进程完成
            aplay_process.wait()
            ffmpeg_process.wait()

            if aplay_process.returncode == 0 and ffmpeg_process.returncode == 0:
                print("✅ 播放完毕。")
                return True
            else:
                print("❌ 播放失败。")
                return False

        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False

    def run(self, duration: int = 5) -> bool:
        """
        执行完整的播放流程

        Args:
            duration: 播放时长（秒），默认5秒

        Returns:
            bool: 是否成功
        """
        if not self.validate_inputs():
            return False

        self.configure_routing()

        if not self.switch_output_device():
            return False

        return self.play_audio(duration)


def play_audio_to_channel(audio_file: str, target_channel: int, duration: int = 5) -> bool:
    """
    播放音频到指定声道（便于 Robot Framework 调用的函数）

    Args:
        audio_file: 音频文件路径
        target_channel: 目标逻辑声道 (1-4)
        duration: 播放时长（秒），默认5秒

    Returns:
        bool: 是否成功
    """
    player = AudioPlayer(audio_file, target_channel)
    return player.run(duration)


def main():
    """命令行入口函数"""
    if len(sys.argv) != 3:
        print("使用方法: python3 ultimate_play.py <音频文件路径> <目标逻辑声道 (1-4)>")
        sys.exit(1)

    audio_file = sys.argv[1]
    try:
        target_channel = int(sys.argv[2])
    except ValueError:
        print("错误: 目标逻辑声道必须是数字。")
        sys.exit(1)

    player = AudioPlayer(audio_file, target_channel)
    success = player.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
