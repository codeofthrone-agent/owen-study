#!/usr/bin/env python3
"""
語音控制關鍵字庫 - VoiceControlKeywords
整合 TTS 文字轉語音與 Scarlett 4i4 硬體聲道控制
為 Robot Framework 提供統一的語音輸出控制介面
"""

import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

# Robot Framework 支援
try:
    from robot.api.deco import keyword
    from robot.api import logger as robot_logger
    ROBOT_AVAILABLE = True
except ImportError:
    ROBOT_AVAILABLE = False
    # 建立假的 decorator
    def keyword(name=None, tags=None):
        def decorator(func):
            return func
        return decorator

# 內部模組匯入
try:
    from .TTSManager import TTSManager
    from .AudioPlayer import AudioPlayer
except ImportError:
    # 如果相對匯入失敗，嘗試絕對匯入
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from TTSManager import TTSManager
    from AudioPlayer import AudioPlayer

# 日誌
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


class VoiceControlKeywords:
    """
    語音控制關鍵字庫

    整合 TTS 與 Scarlett 4i4 硬體控制，提供：
    1. 文字轉語音並輸出到指定聲道
    2. TTS 引擎切換（gtts, pyttsx3）
    3. 語言與語速控制
    4. 多聲道測試功能

    Scope: GLOBAL
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'

    def __init__(self):
        """初始化語音控制關鍵字庫"""
        # 初始化核心模組
        self.tts_manager = TTSManager()
        self.audio_player = AudioPlayer()

        # 狀態管理
        self.last_audio_file = None
        self.temp_audio_files = []

        # 設定日誌
        self._setup_logging()

        if ROBOT_AVAILABLE:
            robot_logger.info("VoiceControlKeywords 初始化完成")
        else:
            print("VoiceControlKeywords 初始化完成 (非 Robot Framework 環境)")

    def _setup_logging(self) -> None:
        """設定日誌系統"""
        try:
            if LOGURU_AVAILABLE:
                logger.remove()
                logger.add(
                    "logs/voice_control_keywords.log",
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                    level="INFO",
                    rotation="10 MB",
                    retention="7 days",
                )
        except Exception as e:
            print(f"日誌設定失敗: {e}")

    # ===========================================
    # 主要 Robot Framework 關鍵字
    # ===========================================

    @keyword('播放文字到聲道')
    def speak_text_to_channel(self, text: str, channel: int,
                            language: str = 'en', duration: int = 5) -> bool:
        """
        將文字轉換為語音並播放到 Scarlett 4i4 的指定聲道

        這是核心關鍵字，整合了 TTS 生成與硬體聲道控制

        參數:
            text: 要播放的文字內容
            channel: 目標聲道 (1-4)
                1 = 物理輸出 1（左前）
                2 = 物理輸出 2（右前）
                3 = 物理輸出 3（左後/AUX 1）
                4 = 物理輸出 4（右後/AUX 2）
            language: 語言代碼（預設: en）
                en = 英文
                zh-TW = 繁體中文
                ja = 日文
            duration: 播放時長（秒，預設: 5）

        回傳:
            播放是否成功

        範例:
            | 播放文字到聲道 | Hello World | 1 |
            | 播放文字到聲道 | 測試語音 | 3 | zh-TW |
            | 播放文字到聲道 | テスト | 4 | ja | 10 |
        """
        try:
            logger.info(f"開始語音播放: '{text}' -> 聲道 {channel} ({language})")

            if ROBOT_AVAILABLE:
                robot_logger.info(f"將播放文字 '{text}' 到聲道 {channel}")

            # 步驟 1: 使用 TTS 生成音訊檔案
            audio_file = self.tts_manager.text_to_file(
                text=text,
                language=language,
                format='mp3'
            )

            if not audio_file:
                error_msg = "TTS 音訊生成失敗"
                logger.error(error_msg)
                if ROBOT_AVAILABLE:
                    robot_logger.error(error_msg)
                return False

            # 記錄生成的檔案
            self.last_audio_file = audio_file
            self.temp_audio_files.append(audio_file)

            logger.info(f"TTS 音訊檔案生成: {audio_file}")

            # 步驟 2: 播放到指定聲道
            success = self.audio_player.play_to_channel(
                audio_file=audio_file,
                target_channel=int(channel),
                duration=int(duration)
            )

            if success:
                logger.info(f"語音播放完成: 聲道 {channel}")
                if ROBOT_AVAILABLE:
                    robot_logger.info(f"✓ 聲道 {channel} 播放成功")
            else:
                logger.error(f"語音播放失敗: 聲道 {channel}")
                if ROBOT_AVAILABLE:
                    robot_logger.error(f"✗ 聲道 {channel} 播放失敗")

            return success

        except Exception as e:
            error_msg = f"播放文字到聲道失敗: {e}"
            logger.error(error_msg)
            if ROBOT_AVAILABLE:
                robot_logger.error(error_msg)
            return False

    @keyword('設定 TTS 引擎')
    def set_tts_engine(self, engine_name: str) -> bool:
        """
        切換 TTS 引擎

        參數:
            engine_name: 引擎名稱
                gtts = Google TTS（線上，品質高）
                pyttsx3 = 離線 TTS（離線，速度快）

        回傳:
            切換是否成功

        範例:
            | 設定 TTS 引擎 | gtts |
            | 設定 TTS 引擎 | pyttsx3 |
        """
        try:
            success = self.tts_manager.set_engine(engine_name)

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 引擎切換為: {engine_name}")
                else:
                    robot_logger.error(f"✗ TTS 引擎切換失敗: {engine_name}")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 引擎失敗: {e}")
            return False

    @keyword('設定 TTS 語言')
    def set_tts_language(self, language: str) -> bool:
        """
        設定 TTS 語言

        參數:
            language: 語言代碼
                en = 英文
                zh-TW = 繁體中文
                zh-CN = 簡體中文
                ja = 日文
                ko = 韓文

        回傳:
            設定是否成功

        範例:
            | 設定 TTS 語言 | en |
            | 設定 TTS 語言 | zh-TW |
        """
        try:
            success = self.tts_manager.set_language(language)

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 語言設定為: {language}")
                else:
                    robot_logger.error(f"✗ TTS 語言設定失敗")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 語言失敗: {e}")
            return False

    @keyword('設定 TTS 語速')
    def set_tts_speed(self, speed: float) -> bool:
        """
        設定 TTS 語速

        參數:
            speed: 語速（words per minute）
                120 = 慢速
                180 = 標準速度（預設）
                250 = 快速

        回傳:
            設定是否成功

        範例:
            | 設定 TTS 語速 | 150 |
            | 設定 TTS 語速 | 200 |
        """
        try:
            success = self.tts_manager.set_voice_speed(float(speed))

            if ROBOT_AVAILABLE:
                if success:
                    robot_logger.info(f"✓ TTS 語速設定為: {speed}")
                else:
                    robot_logger.error(f"✗ TTS 語速設定失敗")

            return success
        except Exception as e:
            logger.error(f"設定 TTS 語速失敗: {e}")
            return False

    @keyword('播放語音到所有聲道')
    def speak_to_all_channels(self, text: str, language: str = 'en',
                            duration: int = 3) -> Dict[int, bool]:
        """
        依序播放文字到所有 4 個聲道（測試用）

        參數:
            text: 要播放的文字
            language: 語言代碼（預設: en）
            duration: 每個聲道播放時長（秒，預設: 3）

        回傳:
            字典，鍵為聲道號，值為是否成功

        範例:
            | 播放語音到所有聲道 | Channel Test |
            | 播放語音到所有聲道 | 聲道測試 | zh-TW | 2 |
        """
        results = {}

        if ROBOT_AVAILABLE:
            robot_logger.info(f"開始測試所有聲道，文字: '{text}'")

        for channel in range(1, 5):
            logger.info(f"測試聲道 {channel}...")

            success = self.speak_text_to_channel(
                text=f"{text} {channel}",
                channel=channel,
                language=language,
                duration=duration
            )

            results[channel] = success

            if ROBOT_AVAILABLE:
                status = "成功" if success else "失敗"
                robot_logger.info(f"聲道 {channel}: {status}")

            # 聲道之間稍作停頓
            if channel < 4:
                time.sleep(1)

        return results

    @keyword('取得 TTS 引擎資訊')
    def get_tts_engine_info(self) -> Dict[str, Any]:
        """
        獲取 TTS 引擎資訊

        回傳:
            包含引擎資訊的字典

        範例:
            | ${info}= | 取得 TTS 引擎資訊 |
            | Log | 主要引擎: ${info['primary_engine']} |
        """
        return self.tts_manager.get_engine_info()

    @keyword('取得可用音訊設備')
    def get_available_sinks(self) -> list:
        """
        獲取可用的音訊輸出設備列表

        回傳:
            設備名稱列表

        範例:
            | ${sinks}= | 取得可用音訊設備 |
            | Log Many | @{sinks} |
        """
        return self.audio_player.list_available_sinks()

    @keyword('檢查 Scarlett 設備')
    def check_scarlett_device(self) -> bool:
        """
        檢查 Scarlett 4i4 設備是否可用

        回傳:
            設備是否可用

        範例:
            | ${available}= | 檢查 Scarlett 設備 |
            | Should Be True | ${available} | msg=Scarlett 設備不可用 |
        """
        available = self.audio_player.scarlett_available

        if ROBOT_AVAILABLE:
            if available:
                robot_logger.info("✓ Scarlett 4i4 設備可用")
            else:
                robot_logger.warn("✗ Scarlett 4i4 設備不可用")

        return available

    @keyword('清理語音控制資源')
    def cleanup_voice_control_resources(self) -> bool:
        """
        清理語音控制資源（暫存檔案等）

        回傳:
            清理是否成功

        範例:
            | 清理語音控制資源 |
        """
        try:
            # 清理 TTS 暫存檔案
            cleaned_count = self.tts_manager.cleanup_temp_files()

            # 清理本地記錄的暫存檔案
            self.temp_audio_files.clear()
            self.last_audio_file = None

            if ROBOT_AVAILABLE:
                robot_logger.info(f"✓ 清理了 {cleaned_count} 個暫存檔案")

            logger.info("語音控制資源清理完成")
            return True

        except Exception as e:
            logger.error(f"清理語音控制資源失敗: {e}")
            if ROBOT_AVAILABLE:
                robot_logger.error(f"✗ 資源清理失敗: {e}")
            return False

    def get_library_info(self) -> Dict[str, Any]:
        """
        獲取 Library 資訊

        Returns:
            Library 資訊字典
        """
        return {
            'version': self.ROBOT_LIBRARY_VERSION,
            'scope': self.ROBOT_LIBRARY_SCOPE,
            'tts_engine_info': self.tts_manager.get_engine_info(),
            'scarlett_available': self.audio_player.scarlett_available,
            'temp_files_count': len(self.temp_audio_files),
            'last_audio_file': self.last_audio_file,
        }

    def __del__(self):
        """解構函數，自動清理資源"""
        try:
            self.cleanup_voice_control_resources()
        except:
            pass


# 測試程式
if __name__ == "__main__":
    print("VoiceControlKeywords 測試程式")

    # 建立 Library 實例
    lib = VoiceControlKeywords()

    # 顯示資訊
    info = lib.get_library_info()
    print(f"Library 資訊: {info}")

    # 基本功能測試
    try:
        # 檢查 Scarlett 設備
        scarlett_ok = lib.check_scarlett_device()
        print(f"\nScarlett 設備狀態: {'✓ 可用' if scarlett_ok else '✗ 不可用'}")

        if scarlett_ok:
            # 測試播放
            print("\n測試播放文字到聲道 1...")
            success = lib.speak_text_to_channel("Test", 1, "en", 3)
            print(f"播放結果: {'✓ 成功' if success else '✗ 失敗'}")

        print("\n✓ 基本功能測試完成")

    except Exception as e:
        print(f"✗ 測試失敗: {e}")

    finally:
        # 清理資源
        lib.cleanup_voice_control_resources()
        print("✓ 資源清理完成")
