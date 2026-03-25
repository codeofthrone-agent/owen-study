"""Android 裝置系統控制實作。

開發用途：
    透過 Appium mobile: shell 命令（ADB shell）控制 Android 實體裝置的系統層級功能，
    包含藍牙、WiFi、行動數據、飛航模式、音量控制、App 生命週期管理，以及
    IoT 語音控制場景的語音輸入整合（Stage 7）。

開發日期：2026-03-11

功能說明：
    - 藍牙控制：開啟/關閉裝置藍牙（ADB svc bluetooth）
    - 網路控制：WiFi/行動數據/飛航模式 開啟與關閉
    - 音量控制：調高/調低/靜音/設定媒體音量（0-15）
    - App 生命週期：置於背景、啟動前景、清除最近應用、強制停止
    - 狀態查詢：查詢藍牙/WiFi/飛航模式/音量/前景應用程式狀態
    - 狀態斷言：斷言各狀態是否符合預期（失敗時拋出 AssertionError 附帶實際值）
    - 語音輸入（Stage 7）：
        * 硬體就緒檢查（Scarlett 4i4 + PipeWire 路由）
        * 觸發系統語音搜尋（ADB Intent）
        * 點擊 App 內語音輸入按鈕（UI 定位）
        * 語音觸發與播放同步策略（含重試機制）
        * 等待語音輸入結果（元素文字變化偵測）
        * 語音指令結果驗證

使用方式：
    from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl
    ctrl = AndroidDeviceControl(appium_driver)
    ctrl.disable_wifi()
    ctrl.assert_wifi_off()
    ctrl.trigger_voice_search()

依賴：
    - Appium UiAutomator2 driver
    - Appium server 需啟用 --relaxed-security 以允許 mobile: shell
    - 目標裝置需開啟 USB 調試且已授權 ADB
    - 語音輸入功能需 Focusrite Scarlett 4i4 + PipeWire 路由設定

已知限制：
    - 藍牙配對無法純 API 完成，需 UI 自動化
    - 非 root 裝置部分功能（如行動數據）可能需要 io.appium.settings APK
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Union

from robot.api import logger

from libraries.mobile_testing.base.device_control_base import DeviceControlBase


class AndroidDeviceControl(DeviceControlBase):
    """Android 裝置系統控制實作。"""

    SHELL_TIMEOUT_MS = 10000

    # =========================================================================
    # 私有輔助方法
    # =========================================================================

    def _adb_shell(
        self,
        command: str,
        args: Optional[List[str]] = None,
        timeout_ms: Optional[int] = None,
    ) -> str:
        """透過 Appium `mobile: shell` 執行 ADB 命令並回傳 stdout。"""

        payload = {
            'command': command,
            'args': args or [],
            'includeStderr': True,
            'timeout': timeout_ms or self.SHELL_TIMEOUT_MS,
        }
        logger.debug(f"[ADB] 執行命令：{command} {args or []}")
        result = self.driver.execute_script('mobile: shell', payload)

        output: Union[str, None] = None
        if isinstance(result, dict):
            output = result.get('stdout') or result.get('output') or ''
            stderr = result.get('stderr') or ''
            if not output and stderr:
                output = stderr
        elif result is not None:
            output = str(result)
        else:
            output = ''

        cleaned = (output or '').strip()
        logger.debug(f"[ADB] 命令輸出：{cleaned!r}")
        return cleaned

    # =========================================================================
    # 藍牙控制（Stage 5.2）
    # =========================================================================

    def enable_bluetooth(self):
        """開啟藍牙。

        透過 ADB svc bluetooth enable 指令開啟裝置藍牙。
        若 ADB 命令失敗（非 root 裝置權限不足），自動回退至 Settings UI 自動化。

        Prerequisites:
        - Appium session 已建立，relaxed-security 已啟用

        Examples:
        | enable_bluetooth |
        """
        try:
            self._adb_shell('svc', ['bluetooth', 'enable'])
            logger.info("藍牙已開啟（ADB）")
        except Exception as e:
            logger.warn(f"ADB 藍牙命令失敗，回退至 UI 自動化：{e}")
            self._bluetooth_via_settings(enable=True)

    def disable_bluetooth(self):
        """關閉藍牙。

        透過 ADB svc bluetooth disable 指令關閉裝置藍牙。
        若 ADB 命令失敗（非 root 裝置權限不足），自動回退至 Settings UI 自動化。

        Examples:
        | disable_bluetooth |
        """
        try:
            self._adb_shell('svc', ['bluetooth', 'disable'])
            logger.info("藍牙已關閉（ADB）")
        except Exception as e:
            logger.warn(f"ADB 藍牙命令失敗，回退至 UI 自動化：{e}")
            self._bluetooth_via_settings(enable=False)

    def _bluetooth_via_settings(self, enable: bool):
        """透過 Android Settings UI 自動化操作藍牙開關（非 root 回退方案）。

        🧑‍💻 注意：此方法依賴 Settings UI 佈局，需在實機上驗證並可能需要調整定位器。

        Args:
            enable: True 開啟藍牙，False 關閉藍牙
        """
        action = "開啟" if enable else "關閉"
        logger.info(f"嘗試透過 Settings UI {action}藍牙")
        # 開啟 Android 藍牙設定頁面
        self._adb_shell('am', [
            'start', '-a', 'android.settings.BLUETOOTH_SETTINGS'
        ])
        time.sleep(1.5)
        # 🧑‍💻 以下定位器需在實機驗證：不同 Android 版本/廠牌的 Settings UI 不同
        try:
            switch = self.driver.find_element(
                'android uiautomator',
                'new UiSelector().className("android.widget.Switch")'
            )
            is_checked = switch.get_attribute('checked') == 'true'
            if enable and not is_checked:
                switch.click()
                logger.info(f"藍牙已透過 UI 開啟")
            elif not enable and is_checked:
                switch.click()
                logger.info(f"藍牙已透過 UI 關閉")
            else:
                logger.info(f"藍牙已經是{'開啟' if enable else '關閉'}狀態")
        except Exception as ui_err:
            raise RuntimeError(
                f"藍牙 UI 自動化失敗：{ui_err}。"
                "請確認裝置 Settings 介面佈局，或手動操作藍牙。"
            ) from ui_err
        finally:
            # 返回前一頁面
            self.driver.press_keycode(4)  # KEYCODE_BACK

    # =========================================================================
    # 網路控制（Stage 5.3-5.5）
    # =========================================================================

    def enable_wifi(self):
        """開啟 WiFi。

        透過 ADB svc wifi enable 指令開啟 WiFi。

        Examples:
        | enable_wifi |
        """
        self._adb_shell('svc', ['wifi', 'enable'])
        logger.info("WiFi 已開啟")

    def disable_wifi(self):
        """關閉 WiFi。

        透過 ADB svc wifi disable 指令關閉 WiFi。

        Examples:
        | disable_wifi |
        """
        self._adb_shell('svc', ['wifi', 'disable'])
        logger.info("WiFi 已關閉")

    def enable_mobile_data(self):
        """開啟行動數據。

        透過 io.appium.settings 輔助 App 啟動命令開啟行動數據。
        需要目標裝置已安裝 io.appium.settings APK（Appium 自動安裝）。

        Examples:
        | enable_mobile_data |
        """
        self._adb_shell(
            'am',
            ['start', '-n', 'io.appium.settings/.Settings', '--es', 'data', 'on'],
        )
        logger.info("行動數據已開啟")

    def disable_mobile_data(self):
        """關閉行動數據。

        透過 io.appium.settings 輔助 App 啟動命令關閉行動數據。

        Examples:
        | disable_mobile_data |
        """
        self._adb_shell(
            'am',
            ['start', '-n', 'io.appium.settings/.Settings', '--es', 'data', 'off'],
        )
        logger.info("行動數據已關閉")

    def enable_airplane_mode(self):
        """開啟飛航模式。

        先設定全域設定值，再透過廣播通知系統更新網路狀態。

        Examples:
        | enable_airplane_mode |
        """
        self._adb_shell('settings', ['put', 'global', 'airplane_mode_on', '1'])
        self._adb_shell(
            'am',
            [
                'broadcast',
                '-a',
                'android.intent.action.AIRPLANE_MODE',
                '--ez',
                'state',
                'true',
            ],
        )
        logger.info("飛航模式已開啟")

    def disable_airplane_mode(self):
        """關閉飛航模式。

        先設定全域設定值，再透過廣播通知系統更新網路狀態。

        Examples:
        | disable_airplane_mode |
        """
        self._adb_shell('settings', ['put', 'global', 'airplane_mode_on', '0'])
        self._adb_shell(
            'am',
            [
                'broadcast',
                '-a',
                'android.intent.action.AIRPLANE_MODE',
                '--ez',
                'state',
                'false',
            ],
        )
        logger.info("飛航模式已關閉")

    # =========================================================================
    # 音量控制（Stage 5.6）
    # =========================================================================

    def volume_up(self):
        """調高音量一級。

        透過按鍵碼 24（KEYCODE_VOLUME_UP）調高媒體音量。

        Examples:
        | volume_up |
        """
        self.driver.press_keycode(24)
        logger.info("音量已調高")

    def volume_down(self):
        """調低音量一級。

        透過按鍵碼 25（KEYCODE_VOLUME_DOWN）調低媒體音量。

        Examples:
        | volume_down |
        """
        self.driver.press_keycode(25)
        logger.info("音量已調低")

    def volume_mute(self):
        """靜音。

        透過按鍵碼 164（KEYCODE_VOLUME_MUTE）靜音。

        Examples:
        | volume_mute |
        """
        self.driver.press_keycode(164)
        logger.info("已靜音")

    def set_media_volume(self, level: int):
        """設定媒體音量到指定值。

        Arguments:
        - level: 音量等級（0-15）

        Examples:
        | set_media_volume | 7 |
        """
        self._adb_shell(
            'media', ['volume', '--stream', '3', '--set', str(int(level))]
        )
        logger.info(f"媒體音量已設定為 {level}")

    # =========================================================================
    # App 生命週期（Stage 5.7-5.8）
    # =========================================================================

    def background_app(self, seconds: int = -1):
        """將應用程式置於背景。

        使用 background_app(-1) 強制置於背景（無限期），
        避免 Android 上傳入正數秒數會導致 App 重啟的問題。

        Arguments:
        - seconds: 僅接受 -1（無限期），忽略其他值

        Examples:
        | background_app |
        | background_app | -1 |
        """
        self.driver.background_app(-1)
        logger.info("應用程式已置於背景")

    def activate_app(self, package_or_bundle: str):
        """啟動或恢復應用程式至前景。

        Arguments:
        - package_or_bundle: Android package name（如 com.example.app）

        Examples:
        | activate_app | com.example.app |
        """
        self.driver.activate_app(package_or_bundle)
        logger.info(f"應用程式已恢復至前景：{package_or_bundle}")

    def dismiss_from_recents(self):
        """從最近應用列表中清除 App。

        步驟：
        1. 按下按鍵碼 187（KEYCODE_APP_SWITCH）開啟最近應用列表
        2. 執行向上滑動手勢清除當前應用卡片

        Examples:
        | dismiss_from_recents |
        """
        size = self.driver.get_window_size()
        self.driver.press_keycode(187)
        self.driver.execute_script('mobile: swipeGesture', {
            'left': 0,
            'top': 0,
            'width': size['width'],
            'height': size['height'],
            'direction': 'up',
            'percent': 0.75,
        })
        logger.info("已從最近應用列表清除 App")

    def force_stop_app(self, package_or_bundle: str):
        """強制停止應用程式。

        Arguments:
        - package_or_bundle: Android package name（如 com.example.app）

        Examples:
        | force_stop_app | com.example.app |
        """
        try:
            self.driver.terminate_app(package_or_bundle)
        except Exception as err:  # pragma: no cover - Fallback path
            logger.warn(f"terminate_app 失敗，改用 ADB force-stop：{err}")
            self._adb_shell('am', ['force-stop', package_or_bundle])
        logger.info(f"應用程式已強制停止：{package_or_bundle}")

    # =========================================================================
    # 狀態查詢方法（Stage 5.9）
    # =========================================================================

    def get_bluetooth_state(self) -> str:
        """查詢藍牙開關狀態。

        透過 ADB settings get global bluetooth_on 查詢目前藍牙狀態。

        Examples:
        | ${state}= | get_bluetooth_state |
        | Should Be Equal | ${state} | on |

        Returns:
            str: 'on' 表示已開啟，'off' 表示已關閉
        """
        raw = self._adb_shell('settings', ['get', 'global', 'bluetooth_on'])
        logger.debug(f"藍牙狀態原始值：{raw!r}")
        return 'on' if raw == '1' else 'off'

    def get_wifi_state(self) -> str:
        """查詢 WiFi 開關狀態。

        透過 ADB settings get global wifi_on 查詢目前 WiFi 狀態。

        Examples:
        | ${state}= | get_wifi_state |

        Returns:
            str: 'on' 表示已開啟，'off' 表示已關閉
        """
        raw = self._adb_shell('settings', ['get', 'global', 'wifi_on'])
        logger.debug(f"WiFi 狀態原始值：{raw!r}")
        return 'on' if raw == '1' else 'off'

    def get_airplane_mode_state(self) -> str:
        """查詢飛航模式開關狀態。

        透過 ADB settings get global airplane_mode_on 查詢目前飛航模式狀態。

        Examples:
        | ${state}= | get_airplane_mode_state |

        Returns:
            str: 'on' 表示已開啟，'off' 表示已關閉
        """
        raw = self._adb_shell('settings', ['get', 'global', 'airplane_mode_on'])
        logger.debug(f"飛航模式狀態原始值：{raw!r}")
        return 'on' if raw == '1' else 'off'

    def get_mobile_data_state(self) -> str:
        """查詢行動數據開關狀態。"""
        raw = self._adb_shell('settings', ['get', 'global', 'mobile_data'])
        logger.debug(f"行動數據狀態原始值：{raw!r}")
        return 'on' if raw == '1' else 'off'

    def get_media_volume(self) -> int:
        """查詢目前媒體音量等級。

        透過 ADB media volume --stream 3 --get 查詢媒體音量（Stream 3 = STREAM_MUSIC）。

        Examples:
        | ${volume}= | get_media_volume |
        | Should Be Equal As Integers | ${volume} | 7 |

        Returns:
            int: 目前媒體音量等級（0-15）
        """
        raw = self._adb_shell('media', ['volume', '--stream', '3', '--get'])
        logger.debug(f"媒體音量原始輸出：{raw!r}")
        # 輸出格式：volume is X  或  Current volume: X
        match = re.search(r'\d+', raw)
        if match:
            return int(match.group())
        raise RuntimeError(f"無法解析媒體音量輸出：{raw!r}")

    def get_foreground_app(self) -> str:
        """查詢目前前景應用程式的 package name。

        透過 ADB dumpsys activity activities 取得 mResumedActivity 資訊。

        Examples:
        | ${pkg}= | get_foreground_app |
        | Should Contain | ${pkg} | com.example |

        Returns:
            str: 前景應用程式的 package name，查詢失敗時回傳空字串
        """
        raw = self._adb_shell('dumpsys', ['activity', 'activities'])
        logger.debug(f"前景應用原始輸出：{raw!r}")
        match = None
        for line in raw.splitlines():
            if 'mResumedActivity' in line:
                match = re.search(r'u0\s+([\w.]+)/', line)
                if match:
                    break
        if match:
            return match.group(1)
        parts = raw.split()
        for part in parts:
            if '/' in part and '.' in part.split('/')[0]:
                return part.split('/')[0]
        logger.warn(f"無法解析前景應用程式，原始輸出：{raw!r}")
        return ''

    # =========================================================================
    # 狀態斷言方法（Stage 5.10）
    # =========================================================================

    def assert_bluetooth_on(self):
        """斷言藍牙目前為開啟狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_bluetooth_on |
        """
        actual = self.get_bluetooth_state()
        if actual != 'on':
            raise AssertionError(
                f"藍牙應為開啟狀態，但實際為：'{actual}'"
            )

    def assert_bluetooth_off(self):
        """斷言藍牙目前為關閉狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_bluetooth_off |
        """
        actual = self.get_bluetooth_state()
        if actual != 'off':
            raise AssertionError(
                f"藍牙應為關閉狀態，但實際為：'{actual}'"
            )

    def assert_wifi_on(self):
        """斷言 WiFi 目前為開啟狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_wifi_on |
        """
        actual = self.get_wifi_state()
        if actual != 'on':
            raise AssertionError(
                f"WiFi 應為開啟狀態，但實際為：'{actual}'"
            )

    def assert_wifi_off(self):
        """斷言 WiFi 目前為關閉狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_wifi_off |
        """
        actual = self.get_wifi_state()
        if actual != 'off':
            raise AssertionError(
                f"WiFi 應為關閉狀態，但實際為：'{actual}'"
            )

    def assert_airplane_mode_on(self):
        """斷言飛航模式目前為開啟狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_airplane_mode_on |
        """
        actual = self.get_airplane_mode_state()
        if actual != 'on':
            raise AssertionError(
                f"飛航模式應為開啟狀態，但實際為：'{actual}'"
            )

    def assert_airplane_mode_off(self):
        """斷言飛航模式目前為關閉狀態。

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | assert_airplane_mode_off |
        """
        actual = self.get_airplane_mode_state()
        if actual != 'off':
            raise AssertionError(
                f"飛航模式應為關閉狀態，但實際為：'{actual}'"
            )

    def assert_mobile_data_on(self):
        """斷言行動數據為開啟狀態。"""
        actual = self.get_mobile_data_state()
        if actual != 'on':
            raise AssertionError(
                f"行動數據應為開啟狀態，但實際為：'{actual}'"
            )

    def assert_mobile_data_off(self):
        """斷言行動數據為關閉狀態。"""
        actual = self.get_mobile_data_state()
        if actual != 'off':
            raise AssertionError(
                f"行動數據應為關閉狀態，但實際為：'{actual}'"
            )

    def assert_media_volume(self, expected: int):
        """斷言媒體音量等級符合預期值。

        Arguments:
        - expected: 預期媒體音量等級（0-15）

        失敗時拋出 AssertionError，附帶實際音量值。

        Examples:
        | assert_media_volume | 7 |
        """
        actual = self.get_media_volume()
        if actual != int(expected):
            raise AssertionError(
                f"媒體音量應為 {expected}，但實際為：{actual}"
            )

    def assert_app_in_foreground(self, package: str):
        """斷言指定應用程式目前在前景執行。

        Arguments:
        - package: Android package name（如 com.example.app）

        失敗時拋出 AssertionError，附帶實際前景應用程式名稱。

        Examples:
        | assert_app_in_foreground | com.example.app |
        """
        actual = self.get_foreground_app()
        if package not in actual:
            raise AssertionError(
                f"前景應用程式應為 '{package}'，但實際為：'{actual}'"
            )

    # =========================================================================
    # Stage 7：語音輸入（IoT 語音控制場景）
    # =========================================================================

    def check_audio_hardware_ready(self) -> None:
        """檢查 Scarlett 4i4 音訊硬體與 PipeWire 路由是否就緒。

        播放語音指令前必須先呼叫此方法，確保硬體已連接且虛擬設備已建立。
        未就緒時立即拋出 RuntimeError 附帶診斷訊息，避免後續無意義的等待。

        Prerequisites:
        - VoiceControlKeywords 已可匯入（libraries/voice_control）

        Examples:
        | check_audio_hardware_ready |

        Raises:
            RuntimeError: Scarlett 4i4 未連接或 PipeWire 路由未設定
        """
        try:
            from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords
            from libraries.voice_control.AudioPlayer import AudioPlayer
        except ImportError as exc:
            raise RuntimeError(
                f"無法匯入 VoiceControlKeywords，請確認 libraries/voice_control 已安裝：{exc}"
            ) from exc

        # 直接透過 AudioPlayer 取得 Scarlett 狀態（避免建立完整 VoiceControlKeywords 實例）
        try:
            player = AudioPlayer()
            scarlett_ok = player.scarlett_available
        except Exception as exc:
            raise RuntimeError(
                f"AudioPlayer 初始化失敗：{exc}\n"
                "診斷建議：請確認 PipeWire/ALSA 服務正在運行（systemctl --user status pipewire）"
            ) from exc

        if not scarlett_ok:
            raise RuntimeError(
                "Scarlett 4i4 未偵測到，請檢查：\n"
                "  1. USB 連接是否牢固（lsusb | grep Focusrite）\n"
                "  2. 驅動是否已載入（aplay -l | grep Scarlett）\n"
                "  3. 使用者是否在 audio 群組（groups | grep audio）"
            )

        # 確認 PipeWire 虛擬設備已建立（ch1 代表 Scarlett_1-2 路由）
        routing_ok, routing_info = player.verify_routing(1)
        if not routing_ok:
            raise RuntimeError(
                "PipeWire 虛擬設備未建立或路由設定不完整，請執行：\n"
                "  cd libraries/voice_control && ./setup_pipewire_routing_v5.sh\n"
                f"  路由診斷：{routing_info}"
            )

        logger.info("✓ 音訊硬體就緒：Scarlett 4i4 已連接，PipeWire 路由已建立")

    def trigger_voice_search(self) -> None:
        """透過 Android Intent 觸發系統級語音搜尋。

        使用 ADB am start 啟動 android.intent.action.VOICE_COMMAND，
        作為不依賴 App UI 的備用語音觸發方案。

        Prerequisites:
        - ADB relaxed-security 已啟用

        Examples:
        | trigger_voice_search |
        """
        self._adb_shell(
            'am start',
            args=['-a', 'android.intent.action.VOICE_COMMAND'],
        )
        logger.info("系統語音搜尋已觸發（android.intent.action.VOICE_COMMAND）")

    def click_voice_input_button(
        self,
        locator: str,
        locator_type: str = 'accessibility_id',
        timeout: float = 10.0,
    ) -> None:
        """等待並點擊 App 內語音輸入按鈕，觸發 App 內建語音輸入功能。

        支援三種定位方式：
        - accessibility_id：透過 Accessibility ID 定位（推薦）
        - id：透過元素 resource-id 定位
        - xpath：透過 XPath 定位

        Arguments:
        - locator: 元素定位器字串
        - locator_type: 定位方式（accessibility_id / id / xpath），預設 accessibility_id
        - timeout: 等待元素出現的最長秒數（預設 10.0 秒）

        Prerequisites:
        - Appium session 已建立，App 已在前景

        Examples:
        | click_voice_input_button | 語音輸入 | accessibility_id |
        | click_voice_input_button | com.example:id/btn_mic | id |
        | click_voice_input_button | //button[@text='mic'] | xpath | 15 |

        Raises:
            TimeoutError: 指定秒數內找不到語音輸入按鈕
        """
        from appium.webdriver.common.appiumby import AppiumBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException

        locator_map: Dict[str, str] = {
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'id': AppiumBy.ID,
            'xpath': AppiumBy.XPATH,
        }
        by = locator_map.get(locator_type.lower())
        if by is None:
            raise ValueError(
                f"不支援的定位方式：'{locator_type}'，支援：{list(locator_map.keys())}"
            )

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            logger.info(f"✓ 語音輸入按鈕已點擊（{locator_type}='{locator}'）")
        except TimeoutException as exc:
            raise TimeoutError(
                f"語音輸入按鈕未出現（{locator_type}='{locator}'），"
                f"已等待 {timeout} 秒\n"
                "建議檢查：定位器是否正確、App 是否在前景、頁面是否已完全載入"
            ) from exc

    def _wait_for_voice_input_ui(
        self,
        voice_ui_locator: Optional[str],
        voice_ui_locator_type: str,
        timeout: float,
    ) -> bool:
        """等待語音輸入 UI 出現（麥克風動畫/聆聽指示器）。

        Arguments:
        - voice_ui_locator: 語音輸入 UI 元素定位器，為 None 時跳過確認（直接返回 True）
        - voice_ui_locator_type: 定位方式
        - timeout: 等待秒數

        Returns:
            bool: True 表示 UI 已出現，False 表示超時
        """
        if voice_ui_locator is None:
            return True

        from appium.webdriver.common.appiumby import AppiumBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException

        locator_map: Dict[str, str] = {
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'id': AppiumBy.ID,
            'xpath': AppiumBy.XPATH,
        }
        by = locator_map.get(voice_ui_locator_type.lower(), AppiumBy.ACCESSIBILITY_ID)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, voice_ui_locator))
            )
            logger.info(f"✓ 語音輸入 UI 已出現（{voice_ui_locator_type}='{voice_ui_locator}'）")
            return True
        except TimeoutException:
            return False

    def trigger_voice_and_play(
        self,
        voice_text: str,
        button_locator: str,
        channel: int = 1,
        button_locator_type: str = 'accessibility_id',
        mic_ready_delay: float = 1.5,
        max_retries: int = 2,
        voice_ui_locator: Optional[str] = None,
        voice_ui_locator_type: str = 'accessibility_id',
        language: str = 'zh-TW',
    ) -> None:
        """語音觸發與播放同步策略：點擊語音按鈕後等待麥克風就緒再播放指令。

        執行流程：
          1. 硬體就緒檢查（Scarlett 4i4 + PipeWire）
          2. 點擊 App 語音輸入按鈕
          3. 等待 mic_ready_delay 秒（讓麥克風初始化）
          4. 確認語音輸入 UI 已出現（若提供 voice_ui_locator）
          5. 播放語音指令（透過 Scarlett 4i4 至指定聲道）

        若語音輸入 UI 未出現則重試點擊，超過 max_retries 次後拋出 TimeoutError。

        Arguments:
        - voice_text: 要播放的語音指令文字（如「開啟客廳燈光」）
        - button_locator: App 語音輸入按鈕的定位器
        - channel: Scarlett 4i4 聲道編號（1-4），預設 1
        - button_locator_type: 按鈕定位方式（accessibility_id/id/xpath），預設 accessibility_id
        - mic_ready_delay: 點擊按鈕後等待麥克風就緒的秒數（預設 1.5）
        - max_retries: 語音輸入 UI 未出現時的最大重試次數（預設 2）
        - voice_ui_locator: 語音輸入 UI 元素定位器（用於確認麥克風已啟動），可為 None
        - voice_ui_locator_type: 語音輸入 UI 定位方式，預設 accessibility_id
        - language: TTS 語言（預設 zh-TW）

        Prerequisites:
        - Appium session 已建立，App 已在前景
        - Scarlett 4i4 已連接，PipeWire 路由已設定

        Examples:
        | trigger_voice_and_play | 開啟客廳燈光 | 語音輸入 | 1 | accessibility_id | 1.5 | 2 |
        | trigger_voice_and_play | 關閉風扇 | com.example:id/btn_mic | 2 | id |

        Raises:
            RuntimeError: Scarlett 4i4 或 PipeWire 未就緒
            TimeoutError: App 語音輸入 UI 未啟動
        """
        # 步驟 1：硬體就緒檢查
        self.check_audio_hardware_ready()

        # 步驟 2-4：點擊按鈕並確認語音輸入 UI（含重試機制）
        attempt = 0
        while True:
            self.click_voice_input_button(
                button_locator,
                locator_type=button_locator_type,
                timeout=10.0,
            )
            time.sleep(mic_ready_delay)

            ui_ready = self._wait_for_voice_input_ui(
                voice_ui_locator,
                voice_ui_locator_type,
                timeout=mic_ready_delay,
            )
            if ui_ready:
                break

            attempt += 1
            if attempt > max_retries:
                raise TimeoutError(
                    f"App 語音輸入未啟動，已重試 {attempt} 次\n"
                    "建議檢查：App 是否回應點擊、語音輸入 UI 定位器是否正確"
                )
            logger.warning(f"語音輸入 UI 未出現，進行第 {attempt} 次重試...")

        # 步驟 5：播放語音指令
        from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords
        voice_ctrl = VoiceControlKeywords()
        success = voice_ctrl.speak_text_to_channel(
            text=voice_text,
            channel=channel,
            language=language,
        )
        if not success:
            raise RuntimeError(
                f"語音指令播放失敗：'{voice_text}'（聲道 {channel}）\n"
                "建議確認 Scarlett 4i4 路由設定與 TTS 引擎狀態"
            )
        logger.info(f"✓ 語音指令已播放：'{voice_text}'（聲道 {channel}）")

    def wait_voice_input_result(
        self,
        result_locator: str,
        result_locator_type: str = 'id',
        timeout: float = 10.0,
    ) -> str:
        """等待 App UI 顯示語音辨識結果（偵測元素文字變化）。

        等待指定元素出現，並回傳其文字內容。
        若在逾時時間內元素未出現，拋出 TimeoutError 附帶診斷訊息。

        Arguments:
        - result_locator: 結果顯示區域的定位器
        - result_locator_type: 定位方式（id/xpath/accessibility_id），預設 id
        - timeout: 等待秒數（預設 10.0）

        Prerequisites:
        - 語音指令已播放完成

        Examples:
        | result = wait_voice_input_result | com.example:id/tv_result | id | 10 |
        | result = wait_voice_input_result | //TextView[@text] | xpath | 15 |

        Returns:
            str: 語音辨識結果文字

        Raises:
            TimeoutError: 指定逾時內未取得語音辨識結果
        """
        from appium.webdriver.common.appiumby import AppiumBy
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException

        locator_map: Dict[str, str] = {
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'id': AppiumBy.ID,
            'xpath': AppiumBy.XPATH,
        }
        by = locator_map.get(result_locator_type.lower(), AppiumBy.ID)

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, result_locator))
            )
            result_text = element.text or ''
            logger.info(f"✓ 語音辨識結果：'{result_text}'")
            return result_text
        except TimeoutException as exc:
            raise TimeoutError(
                f"語音辨識逾時：App 在 {timeout} 秒內未回應\n"
                "可能原因：\n"
                "  1) 麥克風未接收到聲音（確認音量與距離）\n"
                "  2) App 語音辨識失敗（確認網路連線）\n"
                "  3) 音訊輸出通道不正確（確認 Scarlett 路由）\n"
                f"  4) 結果定位器不正確（{result_locator_type}='{result_locator}'）"
            ) from exc

    def assert_voice_result_contains(
        self,
        expected: str,
        result_locator: str,
        result_locator_type: str = 'id',
        timeout: float = 10.0,
    ) -> None:
        """驗證語音指令執行結果包含預期文字。

        先呼叫 wait_voice_input_result 取得實際結果，再比對是否包含預期文字。
        若不包含，拋出 AssertionError 附帶實際結果與調整建議。

        Arguments:
        - expected: 預期回應文字（如「燈光已開啟」）
        - result_locator: 結果顯示區域的定位器
        - result_locator_type: 定位方式，預設 id
        - timeout: 等待秒數（預設 10.0）

        Examples:
        | assert_voice_result_contains | 燈光已開啟 | com.example:id/tv_result | id | 10 |
        | assert_voice_result_contains | 風扇已關閉 | //TextView[@resource-id='result'] | xpath |

        Raises:
            TimeoutError: 逾時未取得結果
            AssertionError: 結果不符預期，附帶實際值與調整建議
        """
        actual = self.wait_voice_input_result(
            result_locator=result_locator,
            result_locator_type=result_locator_type,
            timeout=timeout,
        )
        if expected not in actual:
            raise AssertionError(
                f"語音辨識結果不符：\n"
                f"  預期包含：'{expected}'\n"
                f"  實際為：'{actual}'\n"
                "建議：\n"
                "  1) 確認音訊輸出音量（建議媒體音量 > 5）\n"
                "  2) 確認麥克風與裝置距離（建議 < 30cm）\n"
                "  3) 確認 Scarlett 4i4 聲道路由設定正確"
            )
        logger.info(f"✓ 語音指令驗證通過：結果包含 '{expected}'")
