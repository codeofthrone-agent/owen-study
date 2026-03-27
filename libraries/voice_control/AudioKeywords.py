#!/usr/bin/env python3
"""
Robot Framework 音訊測試關鍵字庫 (AudioKeywords)
遵循 BDD (Given-When-Then) 規範，提供音訊設備和播放相關的測試關鍵字。
"""

import subprocess
from pathlib import Path
from typing import List, Dict

# Robot Framework API
from robot.api.deco import keyword
from robot.api import logger
import time

try:
    from config.audio_config import VIRTUAL_SINKS
except ImportError:
    # Fallback if config import fails (e.g. running standalone)
    VIRTUAL_SINKS = {
        "channels_1_2": "Scarlett_1-2",
        "channels_3_4": "Scarlett_3-4"
    }

# Internal imports
try:
    from .ultimate_play import play_audio_to_channel

except ImportError:
    # Fallback for direct execution or Robot Framework import
    from ultimate_play import play_audio_to_channel


class AudioKeywords:
    """
    音訊測試關鍵字庫
    
    提供檢查音訊設備狀態、驗證輸出以及播放音訊等 Gherkin 風格的關鍵字。
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    # ===========================================
    # 內部輔助方法 (Private Helper Methods)
    # ===========================================

    def _get_current_default_sink(self) -> str:
        """獲取當前預設音訊輸出設備 (sink)"""
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
        """列出所有可用的音訊輸出設備 (sinks)"""
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

    @keyword('Given Scarlett 音訊介面可用')
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
        | Given | Scarlett 音訊介面可用 |
        """
        # Retry logic for robustness
        max_retries = 3
        sinks = []
        for i in range(max_retries):
            sinks = self._list_available_sinks()
            has_1_2 = VIRTUAL_SINKS["channels_1_2"] in sinks
            has_3_4 = VIRTUAL_SINKS["channels_3_4"] in sinks
            
            if has_1_2 and has_3_4:
                break
            
            logger.info(f"Attempt {i+1}/{max_retries}: Sinks not found. Retrying in 1s...")
            time.sleep(1)
            
        has_1_2 = VIRTUAL_SINKS["channels_1_2"] in sinks
        has_3_4 = VIRTUAL_SINKS["channels_3_4"] in sinks
        
        if not (has_1_2 and has_3_4):
            logger.info(f"Available sinks found: {sinks}")
            raise AssertionError(
                f"Scarlett audio interface not fully available. "
                f"Found '{VIRTUAL_SINKS['channels_1_2']}': {has_1_2}. "
                f"Found '{VIRTUAL_SINKS['channels_3_4']}': {has_3_4}."
            )
        logger.info("Verified that Scarlett virtual sinks are available.")

    # ===========================================
    # Gherkin 風格關鍵字 - When (執行動作)
    # ===========================================

    @keyword('When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}"')
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
        | When | 使用者播放音訊檔案 "/path/to/sound.wav" 到聲道 "1" |
        | When | 使用者播放音訊檔案 "${SOUND_FILE}" 到聲道 "3" |
        """
        success = play_audio_to_channel(audio_file, int(channel), int(duration))
        if not success:
            raise AssertionError(f"Failed to play audio file '{audio_file}' to channel {channel}.")
        logger.info(f"Successfully played '{audio_file}' to channel {channel} for {duration} seconds.")

    @keyword('When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}" 持續 "${duration}" 秒')
    def when_user_plays_audio_file_to_channel_with_duration(self, audio_file: str, channel: int, duration: int):
        """
        When: 使用者播放音訊檔案至指定聲道並指定持續時間
        When: User plays an audio file to a specified channel for a specific duration

        此關鍵字將指定的音訊檔案播放到 Scarlett 設備的特定聲道，並指定播放持續時間。
        This keyword plays the specified audio file to a specific channel of the Scarlett device for a specific duration.

        Arguments:
        - `audio_file`: Path to the audio file to be played.
        - `channel`: The target channel number (1-4).
        - `duration`: The playback duration in seconds.

        Examples:
        | When | 使用者播放音訊檔案 "${SOUND_FILE}" 到聲道 "1" 持續 "5" 秒 |
        """
        self.when_user_plays_audio_file_to_channel(audio_file, channel, duration)

    # ===========================================
    # 輔助關鍵字 (Helper Keywords)
    # ===========================================

    @keyword('列出可用輸出設備')
    def list_available_sinks(self) -> List[str]:
        """
        列出系統中所有可用的音訊輸出設備 (sinks)。
        Returns: List of sink names.
        """
        return self._list_available_sinks()

    @keyword('取得當前預設輸出設備')
    def get_current_default_sink(self) -> str:
        """
        取得當前系統預設的音訊輸出設備名稱。
        Returns: Default sink name.
        """
        return self._get_current_default_sink()

    @keyword('取得聲道對應的輸出設備')
    def get_channel_output_sink(self, channel: int) -> str:
        """
        根據設定檔取得指定聲道應該對應的輸出設備名稱。
        
        Arguments:
        - channel: 聲道編號 (1-4)
        
        Returns:
        - Sink name (e.g., "Scarlett_1-2")
        """
        # 這裡我們需要讀取 config/audio_config.py 中的 CHANNEL_MAPPING
        try:
            from config.audio_config import CHANNEL_MAPPING
        except ImportError:
            logger.error("Failed to import CHANNEL_MAPPING from config.audio_config")
            return "Unknown"

        mapping = CHANNEL_MAPPING.get(int(channel))
        if not mapping:
            raise ValueError(f"Channel {channel} not found in CHANNEL_MAPPING")
        return mapping["sink"]


    @keyword('Then 預設音訊輸出應該是 "${expected_sink}"')
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
        | Then | 預設音訊輸出應該是 "Scarlett_1-2" |
        | Then | 預設音訊輸出應該是 "alsa_output.pci-0000_00_1f.3.analog-stereo" |
        """
        # Retry logic for sink verification
        max_retries = 3
        current_sink = ""
        for i in range(max_retries):
            current_sink = self._get_current_default_sink()
            if current_sink == expected_sink:
                break
            logger.info(f"Attempt {i+1}/{max_retries}: Sink mismatch ('{current_sink}' != '{expected_sink}'). Retrying in 1s...")
            time.sleep(1)

        if current_sink != expected_sink:
            raise AssertionError(
                f"Default audio output device mismatch. "
                f"Expected: '{expected_sink}', Actual: '{current_sink}'."
            )
        logger.info(f"Verified that default audio output is '{current_sink}'.")


