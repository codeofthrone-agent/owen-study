#!/usr/bin/env python3
"""
音訊播放器 - AudioPlayer
支援自動切換 PipeWire 輸出設備並播放到 Scarlett 4i4 指定聲道
可與 Robot Framework 整合使用
"""

import sys
import subprocess
import os
from typing import Tuple, Optional
from pathlib import Path


class AudioPlayer:
    """音訊播放器類別 - 控制 Scarlett 4i4 聲道輸出"""

    def __init__(self):
        """初始化音訊播放器"""
        self.last_sink = None
        self.scarlett_available = self._check_scarlett_device()

    def _check_scarlett_device(self) -> bool:
        """
        檢查 Scarlett 4i4 設備是否可用

        Returns:
            設備是否可用
        """
        try:
            result = subprocess.run(
                ["wpctl", "status"],
                capture_output=True,
                text=True,
                check=True
            )
            return "Scarlett" in result.stdout
        except Exception as e:
            print(f"警告: 無法檢測 Scarlett 設備: {e}")
            return False

    def play_to_channel(self, audio_file: str, target_channel: int,
                       duration: int = 5) -> bool:
        """
        播放音訊到指定聲道

        Args:
            audio_file: 音訊檔案路徑
            target_channel: 目標邏輯聲道 (1-4)
            duration: 播放時長（秒），預設 5 秒

        Returns:
            bool: 是否成功

        Examples:
            >>> player = AudioPlayer()
            >>> player.play_to_channel("test.mp3", 1, 5)
            True
        """
        if not self._validate_inputs(audio_file, target_channel):
            return False

        # 配置路由參數
        sink_name, pan_filter, physical_output = self._configure_routing(target_channel)

        # 播放音訊
        # 直接指定 sink_name，不需要切換系統預設輸出
        return self._play_audio(audio_file, pan_filter, physical_output, duration, sink_name)

    def _validate_inputs(self, audio_file: str, target_channel: int) -> bool:
        """驗證輸入參數"""
        if not os.path.exists(audio_file):
            print(f"錯誤: 音訊檔案不存在: {audio_file}")
            return False

        if target_channel not in [1, 2, 3, 4]:
            print(f"錯誤: 目標邏輯聲道必須是 1 到 4 之間的數字，當前值: {target_channel}")
            return False

        return True

    def _configure_routing(self, target_channel: int) -> Tuple[str, str, int]:
        """
        根據目標聲道配置路由參數

        Args:
            target_channel: 目標聲道 (1-4)

        Returns:
            (sink_name, pan_filter, physical_output)
        """
        # 決定使用哪個虛擬設備
        if target_channel in [1, 2]:
            sink_name = "Scarlett_1-2"
        else:
            sink_name = "Scarlett_3-4"

        # 決定聲道映射（左或右）
        if target_channel in [1, 3]:
            pan_filter = "pan=stereo|c0=1*c0|c1=0*c0"
            physical_output = 1 if target_channel == 1 else 3
        else:
            pan_filter = "pan=stereo|c0=0*c0|c1=1*c0"
            physical_output = 2 if target_channel == 2 else 4

        return sink_name, pan_filter, physical_output

    def _switch_output_device(self, sink_name: str) -> bool:
        """
        切換系統預設輸出設備

        Args:
            sink_name: Sink 名稱

        Returns:
            是否成功
        """
        print(f"正在將系統預設輸出切換到: {sink_name} ...")

        try:
            result = subprocess.run(
                ["pactl", "set-default-sink", sink_name],
                capture_output=True,
                text=True,
                check=True
            )
            print("    ✅ 切換成功。")
            self.last_sink = sink_name
            return True
        except subprocess.CalledProcessError as e:
            print("❌ 錯誤：切換輸出設備失敗！")
            print(f"    原因: {e.stderr}")
            print("    請確認 setup_pipewire_routing_v3.sh 是否已成功執行。")
            return False

    def _play_audio(self, audio_file: str, pan_filter: str,
                   physical_output: int, duration: int, sink_name: str) -> bool:
        """
        播放音訊

        Args:
            audio_file: 音訊檔案路徑
            pan_filter: FFmpeg pan 濾鏡參數
            physical_output: 物理輸出編號
            duration: 播放時長（秒）

        Returns:
            bool: 播放是否成功
        """
        print(f"準備播放到邏輯聲道（物理輸出 {physical_output}）...")
        print(f"播放 {duration} 秒鐘...")

        # 構建 ffmpeg 命令
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", audio_file,
            "-t", str(duration),
            "-af", pan_filter,
            "-ar", "48000",
            "-ac", "2",
            "-f", "s16le",
            "-"
        ]

        # 構建 pacat 命令 (直接輸出到指定 sink)
        pacat_cmd = [
            "pacat",
            "--format=s16le",
            "--rate=48000",
            "--channels=2",
            "--device=" + sink_name
        ]

        try:
            # 使用管道連接 ffmpeg 和 aplay
            ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            pacat_process = subprocess.Popen(
                pacat_cmd,
                stdin=ffmpeg_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 關閉 ffmpeg 的 stdout（讓 aplay 接管）
            ffmpeg_process.stdout.close()

            # 等待兩個進程完成
            pacat_process.wait()
            ffmpeg_process.wait()

            if pacat_process.returncode == 0 and ffmpeg_process.returncode == 0:
                print("✅ 播放完畢。")
                return True
            else:
                print("❌ 播放失敗。")
                return False

        except Exception as e:
            print(f"❌ 播放失敗: {e}")
            return False

    def get_current_sink(self) -> Optional[str]:
        """
        獲取當前預設 sink

        Returns:
            當前 sink 名稱或 None
        """
        try:
            result = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def list_available_sinks(self) -> list:
        """
        列出所有可用的 sink

        Returns:
            sink 名稱列表
        """
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
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sinks.append(parts[1])
            return sinks
        except subprocess.CalledProcessError:
            return []


def play_audio_to_channel(audio_file: str, target_channel: int, duration: int = 5) -> bool:
    """
    播放音訊到指定聲道（便於 Robot Framework 調用的函數）

    Args:
        audio_file: 音訊檔案路徑
        target_channel: 目標邏輯聲道 (1-4)
        duration: 播放時長（秒），預設 5 秒

    Returns:
        bool: 是否成功
    """
    player = AudioPlayer()
    return player.play_to_channel(audio_file, target_channel, duration)


def main():
    """命令行入口函數"""
    if len(sys.argv) != 3:
        print("使用方法: python3 AudioPlayer.py <音訊檔案路徑> <目標邏輯聲道 (1-4)>")
        sys.exit(1)

    audio_file = sys.argv[1]
    try:
        target_channel = int(sys.argv[2])
    except ValueError:
        print("錯誤: 目標邏輯聲道必須是數字。")
        sys.exit(1)

    player = AudioPlayer()
    success = player.play_to_channel(audio_file, target_channel)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
