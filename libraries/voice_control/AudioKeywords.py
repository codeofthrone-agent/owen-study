#!/usr/bin/env python3
"""
Robot Framework 音频测试关键字库 (AudioKeywords)
遵循 BDD (Given-When-Then) 规范，提供音频设备和播放相关的测试关键字。
"""

import subprocess
from typing import List, Dict

# Robot Framework API
from robot.api.deco import keyword
from robot.api import logger

from .ultimate_play import play_audio_to_channel


class AudioKeywords:
    """
    音频测试关键字库
    
    提供检查音频设备状态、验证输出以及播放音频等 Gherkin 风格的关键字。
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    # ===========================================
    # 内部辅助方法 (Private Helper Methods)
    # ===========================================

    def _get_current_default_sink(self) -> str:
        """获取当前默认音频输出设备 (sink)"""
        try:
            result = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                check=True
            )
            sink_name = result.stdout.strip()
            logger.info(f"Current default audio sink is '{sink_name}'.")
            return sink_name
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to get default sink: {e}")
            return ""

    def _list_available_sinks(self) -> List[str]:
        """列出所有可用的音频输出设备 (sinks)"""
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
            logger.info(f"Available sinks: {sinks}")
            return sinks
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to list available sinks: {e}")
            return []

    # ===========================================
    # Gherkin 風格關鍵字 - Given (前置條件)
    # ===========================================

    @keyword('Given Scarlett Audio Interface Is Available')
    def given_scarlett_audio_interface_is_available(self):
        """
        Given: 檢查 Scarlett 虛擬音訊介面是否存在
        Given: Checks if the Scarlett virtual audio interfaces exist

        此關鍵字驗證名為 'Scarlett_1-2' 和 'Scarlett_3-4' 的音訊輸出設備 (sink) 是否都存在於系統中。
        This keyword verifies that audio sinks named 'Scarlett_1-2' and 'Scarlett_3-4' are both available in the system.

        Prerequisites:
        - PulseAudio or PipeWire is running.
        - Scarlett device drivers and configuration are properly set up.

        Examples:
        | Given | Scarlett Audio Interface Is Available |
        """
        sinks = self._list_available_sinks()
        has_1_2 = "Scarlett_1-2" in sinks
        has_3_4 = "Scarlett_3-4" in sinks
        
        if not (has_1_2 and has_3_4):
            raise AssertionError(
                f"Scarlett audio interface not fully available. "
                f"Found 'Scarlett_1-2': {has_1_2}. "
                f"Found 'Scarlett_3-4': {has_3_4}."
            )
        logger.info("Verified that 'Scarlett_1-2' and 'Scarlett_3-4' sinks are available.")

    # ===========================================
    # Gherkin 風格關鍵字 - When (執行動作)
    # ===========================================

    @keyword('When User Plays Audio File "${audio_file}" To Channel "${channel}"')
    def when_user_plays_audio_file_to_channel(self, audio_file: str, channel: int, duration: int = 5):
        """
        When: 使用者播放音訊檔案至指定聲道
        When: User plays an audio file to a specified channel

        此關鍵字將指定的音訊檔案播放到 Scarlett 設備的特定聲道。
        This keyword plays the specified audio file to a specific channel of the Scarlett device.

        Arguments:
        - `audio_file`: Path to the audio file to be played.
        - `channel`: The target channel number (1-4).
        - `duration`: The playback duration in seconds (default is 5).

        Prerequisites:
        - Scarlett audio interface must be available.
        - The audio file must exist and be in a supported format (e.g., wav, mp3).

        Examples:
        | When | User Plays Audio File "/path/to/sound.wav" To Channel "1" |
        | When | User Plays Audio File "${SOUND_FILE}" To Channel "3" |
        """
        success = play_audio_to_channel(audio_file, int(channel), int(duration))
        if not success:
            raise AssertionError(f"Failed to play audio file '{audio_file}' to channel {channel}.")
        logger.info(f"Successfully played '{audio_file}' to channel {channel} for {duration} seconds.")

    # ===========================================
    # Gherkin 風格關鍵字 - Then (驗證結果)
    # ===========================================

    @keyword('Then Default Audio Output Should Be "${expected_sink}"')
    def then_default_audio_output_should_be(self, expected_sink: str):
        """
        Then: 驗證預設音訊輸出設備
        Then: Verify the default audio output device

        此關鍵字檢查當前的預設音訊輸出設備 (sink) 是否為預期的名稱。
        This keyword checks if the current default audio output device (sink) matches the expected name.

        Arguments:
        - `expected_sink`: The expected name of the default sink.

        Prerequisites:
        - PulseAudio or PipeWire is running.

        Examples:
        | Then | Default Audio Output Should Be "Scarlett_1-2" |
        | Then | Default Audio Output Should Be "alsa_output.pci-0000_00_1f.3.analog-stereo" |
        """
        current_sink = self._get_current_default_sink()
        if current_sink != expected_sink:
            raise AssertionError(
                f"Default audio output device mismatch. "
                f"Expected: '{expected_sink}', Actual: '{current_sink}'."
            )
        logger.info(f"Verified that default audio output is '{current_sink}'.")
