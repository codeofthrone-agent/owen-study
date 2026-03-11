"""跨平台裝置控制 - Robot Framework Library 統一入口。

開發用途：
    作為 Robot Framework 的 Library 統一入口，根據 platform 參數自動分發至
    Android 或 iOS 對應的平台實作類別。Driver 透過 BuiltIn().get_library_instance()
    自動從已載入的 AppiumLibrary 取得，使用者無需手動傳入 driver。

開發日期：2026-03-11

功能說明：
    - 初始化與平台分發：根據 platform 選擇 Android/iOS 實作
    - 藍牙控制關鍵字：開啟/關閉藍牙、狀態查詢與斷言
    - 網路控制關鍵字：WiFi/行動數據/飛航模式 開啟與關閉、狀態查詢與斷言
    - 音量控制關鍵字：調高/調低/靜音/設定媒體音量、音量查詢與斷言
    - App 生命週期關鍵字：置於背景、啟動前景、清除最近應用、強制停止
    - 前景應用查詢與斷言

使用方式（Robot Framework）：
    *** Settings ***
    Library    AppiumLibrary
    Library    libraries/mobile_testing/DeviceControlKeywords.py

    *** Test Cases ***
    範例：關閉 WiFi 並驗證
        Given 裝置控制已初始化    android
        When 使用者關閉 WiFi
        Then WiFi 應該為關閉狀態
"""
from robot.api.deco import keyword


class DeviceControlKeywords:
    """跨平台裝置控制統一入口（Robot Framework Library）

    使用方式：
        Library    libraries/mobile_testing/DeviceControlKeywords.py

        初始化裝置控制    android
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._impl = None

    def _get_driver(self):
        """從已載入的 AppiumLibrary 或 CustomAppiumKeywords 自動取得 driver。"""
        from robot.libraries.BuiltIn import BuiltIn

        try:
            appium_lib = BuiltIn().get_library_instance('AppiumLibrary')
            return appium_lib._current_application()
        except RuntimeError:
            pass
        try:
            custom_lib = BuiltIn().get_library_instance('CustomAppiumKeywords')
            return custom_lib.driver
        except RuntimeError:
            pass
        raise RuntimeError(
            "無法取得 WebDriver。請確保已載入 AppiumLibrary 或 "
            "CustomAppiumKeywords，且已開啟應用程式。"
        )

    def _get_impl(self):
        """取得底層平台實作，未初始化時拋出 RuntimeError。"""
        if self._impl is None:
            raise RuntimeError("尚未初始化，請先呼叫「初始化裝置控制」")
        return self._impl

    # =========================================================================
    # 初始化
    # =========================================================================

    @keyword("初始化裝置控制")
    def init_device_control(self, platform: str):
        """初始化裝置控制，自動從 AppiumLibrary 取得 driver。

        Given: 裝置控制系統已初始化
        Given: Device control system is initialized

        Arguments:
        - platform: 目標平台（android 或 ios）

        Prerequisites:
        - AppiumLibrary 或 CustomAppiumKeywords 已載入且已開啟應用程式

        Examples:
        | Given | 裝置控制已初始化 | android |
        | 初始化裝置控制 | android |
        """
        from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl
        from libraries.mobile_testing.ios.IOSDeviceControl import IOSDeviceControl

        driver = self._get_driver()
        platform_lower = platform.lower()
        if platform_lower == 'android':
            self._impl = AndroidDeviceControl(driver)
        elif platform_lower == 'ios':
            self._impl = IOSDeviceControl(driver)
        else:
            raise ValueError(f"不支援的平台: {platform}（支援: android, ios）")

    # =========================================================================
    # 藍牙控制
    # =========================================================================

    @keyword("開啟藍牙")
    def enable_bluetooth(self):
        """開啟裝置藍牙。

        When: 使用者開啟藍牙
        When: User enables bluetooth

        Examples:
        | When | 使用者開啟藍牙 |
        | 開啟藍牙 |
        """
        self._get_impl().enable_bluetooth()

    @keyword("關閉藍牙")
    def disable_bluetooth(self):
        """關閉裝置藍牙。

        When: 使用者關閉藍牙
        When: User disables bluetooth

        Examples:
        | When | 使用者關閉藍牙 |
        """
        self._get_impl().disable_bluetooth()

    @keyword("查詢藍牙狀態")
    def get_bluetooth_state(self) -> str:
        """查詢裝置藍牙目前的開關狀態。

        Examples:
        | ${state}= | 查詢藍牙狀態 |
        | Should Be Equal | ${state} | on |

        Returns:
            str: 'on' 表示已開啟，'off' 表示已關閉
        """
        return self._get_impl().get_bluetooth_state()

    @keyword("藍牙應該為開啟狀態")
    def assert_bluetooth_on(self):
        """斷言藍牙目前為開啟狀態。

        Then: 藍牙應該為開啟狀態
        Then: Bluetooth should be enabled

        失敗時拋出 AssertionError，附帶實際狀態值。

        Examples:
        | Then | 藍牙應該為開啟狀態 |
        """
        self._get_impl().assert_bluetooth_on()

    @keyword("藍牙應該為關閉狀態")
    def assert_bluetooth_off(self):
        """斷言藍牙目前為關閉狀態。

        Then: 藍牙應該為關閉狀態
        Then: Bluetooth should be disabled

        Examples:
        | Then | 藍牙應該為關閉狀態 |
        """
        self._get_impl().assert_bluetooth_off()

    # =========================================================================
    # 網路控制
    # =========================================================================

    @keyword("開啟 WiFi")
    def enable_wifi(self):
        """開啟裝置 WiFi。

        Examples:
        | When | 使用者開啟 WiFi |
        """
        self._get_impl().enable_wifi()

    @keyword("關閉 WiFi")
    def disable_wifi(self):
        """關閉裝置 WiFi。

        Examples:
        | When | 使用者關閉 WiFi |
        """
        self._get_impl().disable_wifi()

    @keyword("查詢 WiFi 狀態")
    def get_wifi_state(self) -> str:
        """查詢裝置 WiFi 目前的開關狀態。

        Examples:
        | ${state}= | 查詢 WiFi 狀態 |

        Returns:
            str: 'on' 或 'off'
        """
        return self._get_impl().get_wifi_state()

    @keyword("WiFi 應該為開啟狀態")
    def assert_wifi_on(self):
        """斷言 WiFi 目前為開啟狀態。

        Then: WiFi 應該為開啟狀態

        Examples:
        | Then | WiFi 應該為開啟狀態 |
        """
        self._get_impl().assert_wifi_on()

    @keyword("WiFi 應該為關閉狀態")
    def assert_wifi_off(self):
        """斷言 WiFi 目前為關閉狀態。

        Then: WiFi 應該為關閉狀態

        Examples:
        | Then | WiFi 應該為關閉狀態 |
        """
        self._get_impl().assert_wifi_off()

    @keyword("開啟行動數據")
    def enable_mobile_data(self):
        """開啟裝置行動數據。

        Examples:
        | When | 使用者開啟行動數據 |
        """
        self._get_impl().enable_mobile_data()

    @keyword("關閉行動數據")
    def disable_mobile_data(self):
        """關閉裝置行動數據。

        Examples:
        | When | 使用者關閉行動數據 |
        """
        self._get_impl().disable_mobile_data()

    @keyword("查詢行動數據狀態")
    def get_mobile_data_state(self) -> str:
        """查詢行動數據開關狀態。"""
        impl = self._get_impl()
        getter = getattr(impl, 'get_mobile_data_state', None)
        if getter is None:
            raise NotImplementedError("當前平台尚未實作行動數據狀態查詢")
        return getter()

    @keyword("行動數據應該為開啟狀態")
    def assert_mobile_data_on(self):
        """斷言行動數據為開啟狀態。"""
        impl = self._get_impl()
        if hasattr(impl, 'assert_mobile_data_on'):
            impl.assert_mobile_data_on()
            return
        if self.get_mobile_data_state() != 'on':
            raise AssertionError("行動數據應為開啟狀態")

    @keyword("行動數據應該為關閉狀態")
    def assert_mobile_data_off(self):
        """斷言行動數據為關閉狀態。"""
        impl = self._get_impl()
        if hasattr(impl, 'assert_mobile_data_off'):
            impl.assert_mobile_data_off()
            return
        if self.get_mobile_data_state() != 'off':
            raise AssertionError("行動數據應為關閉狀態")

    @keyword("開啟飛航模式")
    def enable_airplane_mode(self):
        """開啟裝置飛航模式。

        Examples:
        | When | 使用者開啟飛航模式 |
        """
        self._get_impl().enable_airplane_mode()

    @keyword("關閉飛航模式")
    def disable_airplane_mode(self):
        """關閉裝置飛航模式。

        Examples:
        | When | 使用者關閉飛航模式 |
        """
        self._get_impl().disable_airplane_mode()

    @keyword("查詢飛航模式狀態")
    def get_airplane_mode_state(self) -> str:
        """查詢裝置飛航模式目前的開關狀態。

        Examples:
        | ${state}= | 查詢飛航模式狀態 |

        Returns:
            str: 'on' 或 'off'
        """
        return self._get_impl().get_airplane_mode_state()

    @keyword("飛航模式應該為開啟狀態")
    def assert_airplane_mode_on(self):
        """斷言飛航模式目前為開啟狀態。

        Then: 飛航模式應該為開啟狀態

        Examples:
        | Then | 飛航模式應該為開啟狀態 |
        """
        self._get_impl().assert_airplane_mode_on()

    @keyword("飛航模式應該為關閉狀態")
    def assert_airplane_mode_off(self):
        """斷言飛航模式目前為關閉狀態。

        Then: 飛航模式應該為關閉狀態

        Examples:
        | Then | 飛航模式應該為關閉狀態 |
        """
        self._get_impl().assert_airplane_mode_off()

    # =========================================================================
    # 音量控制
    # =========================================================================

    @keyword("調高音量")
    def volume_up(self):
        """調高裝置音量一級。

        Examples:
        | When | 使用者調高音量 |
        """
        self._get_impl().volume_up()

    @keyword("調低音量")
    def volume_down(self):
        """調低裝置音量一級。

        Examples:
        | When | 使用者調低音量 |
        """
        self._get_impl().volume_down()

    @keyword("靜音")
    def volume_mute(self):
        """將裝置靜音。

        Examples:
        | When | 使用者靜音 |
        """
        self._get_impl().volume_mute()

    @keyword("設定媒體音量")
    def set_media_volume(self, level: int):
        """設定裝置媒體音量到指定值。

        Arguments:
        - level: 音量等級（0-15）

        Examples:
        | When | 使用者設定媒體音量 | 7 |
        | 設定媒體音量 | 7 |
        """
        self._get_impl().set_media_volume(int(level))

    @keyword("查詢媒體音量")
    def get_media_volume(self) -> int:
        """查詢目前媒體音量等級。

        Examples:
        | ${volume}= | 查詢媒體音量 |

        Returns:
            int: 目前媒體音量等級（0-15）
        """
        return self._get_impl().get_media_volume()

    @keyword("媒體音量應該為")
    def assert_media_volume(self, level: int):
        """斷言媒體音量等級符合預期值。

        Then: 媒體音量應該為 ${level}

        Arguments:
        - level: 預期媒體音量等級（0-15）

        Examples:
        | Then | 媒體音量應該為 | 7 |
        """
        self._get_impl().assert_media_volume(int(level))

    # =========================================================================
    # App 生命週期
    # =========================================================================

    @keyword("將應用程式置於背景")
    def background_app(self, seconds: int = -1):
        """將當前應用程式置於背景。

        Arguments:
        - seconds: 等待秒數後恢復，-1 表示無限期（預設）

        Examples:
        | When | 使用者將應用程式置於背景 |
        """
        self._get_impl().background_app(int(seconds))

    @keyword("啟動應用程式")
    def activate_app(self, package_or_bundle: str):
        """啟動或恢復應用程式至前景。

        Arguments:
        - package_or_bundle: Android package name 或 iOS bundle ID

        Examples:
        | When | 使用者啟動應用程式 | com.example.app |
        | 啟動應用程式 | com.example.app |
        """
        self._get_impl().activate_app(package_or_bundle)

    @keyword("從最近應用清除")
    def dismiss_from_recents(self):
        """從最近應用列表中滑掉清除 App。

        Examples:
        | When | 使用者從最近應用清除 |
        """
        self._get_impl().dismiss_from_recents()

    @keyword("強制停止應用程式")
    def force_stop_app(self, package_or_bundle: str):
        """強制停止應用程式。

        Arguments:
        - package_or_bundle: Android package name 或 iOS bundle ID

        Examples:
        | When | 使用者強制停止應用程式 | com.example.app |
        """
        self._get_impl().force_stop_app(package_or_bundle)

    @keyword("查詢前景應用程式")
    def get_foreground_app(self) -> str:
        """查詢目前前景應用程式的 package name。

        Examples:
        | ${pkg}= | 查詢前景應用程式 |

        Returns:
            str: 前景應用程式的 package name
        """
        return self._get_impl().get_foreground_app()

    @keyword("應用程式應該在前景")
    def assert_app_in_foreground(self, package_or_bundle: str):
        """斷言指定應用程式目前在前景執行。

        Then: 應用程式應該在前景 ${package}

        Arguments:
        - package_or_bundle: Android package name 或 iOS bundle ID

        Examples:
        | Then | 應用程式應該在前景 | com.example.app |
        """
        self._get_impl().assert_app_in_foreground(package_or_bundle)

    # =========================================================================
    # Stage 7：語音輸入（IoT 語音控制場景）
    # =========================================================================

    @keyword("檢查音訊硬體就緒")
    def check_audio_hardware_ready(self):
        """檢查 Scarlett 4i4 音訊硬體與 PipeWire 路由是否就緒。

        Given: 音訊硬體已就緒
        Given: Audio hardware is ready

        播放語音指令前必須先執行，確保 Scarlett 4i4 已連接且虛擬設備已建立。
        未就緒時立即拋出 RuntimeError 附帶診斷訊息，避免後續無意義的等待。

        Prerequisites:
        - libraries/voice_control 模組已安裝

        Examples:
        | Given | 音訊硬體已就緒 |
        | 檢查音訊硬體就緒 |

        Raises:
            RuntimeError: Scarlett 4i4 未連接或 PipeWire 路由未設定
        """
        self._get_impl().check_audio_hardware_ready()

    @keyword("觸發系統語音搜尋")
    def trigger_voice_search(self):
        """透過 Android Intent 觸發系統級語音搜尋。

        When: 使用者觸發系統語音搜尋
        When: User triggers system voice search

        使用 ADB am start -a android.intent.action.VOICE_COMMAND，
        作為不依賴 App UI 的備用語音觸發方案。

        Prerequisites:
        - ADB relaxed-security 已啟用，平台為 android

        Examples:
        | When | 使用者觸發系統語音搜尋 |
        | 觸發系統語音搜尋 |
        """
        self._get_impl().trigger_voice_search()

    @keyword("點擊語音輸入按鈕")
    def click_voice_input_button(
        self,
        locator: str,
        locator_type: str = 'accessibility_id',
        timeout: float = 10.0,
    ):
        """等待並點擊 App 內語音輸入按鈕，觸發 App 內建語音輸入功能。

        When: 使用者點擊語音輸入按鈕 "${locator}"
        When: User clicks voice input button

        支援三種定位方式：
        - accessibility_id：透過 Accessibility ID 定位（推薦）
        - id：透過元素 resource-id 定位
        - xpath：透過 XPath 定位

        Arguments:
        - locator: 元素定位器字串
        - locator_type: 定位方式（accessibility_id / id / xpath），預設 accessibility_id
        - timeout: 等待元素出現的最長秒數（預設 10.0）

        Examples:
        | When | 使用者點擊語音輸入按鈕 | 語音輸入 |
        | 點擊語音輸入按鈕 | 語音輸入 | accessibility_id |
        | 點擊語音輸入按鈕 | com.example:id/btn_mic | id |
        | 點擊語音輸入按鈕 | //button[@text='mic'] | xpath | 15 |

        Raises:
            TimeoutError: 指定秒數內找不到語音輸入按鈕
        """
        self._get_impl().click_voice_input_button(
            locator=locator,
            locator_type=locator_type,
            timeout=float(timeout),
        )

    @keyword("觸發語音輸入並播放指令")
    def trigger_voice_and_play(
        self,
        voice_text: str,
        button_locator: str,
        channel: int = 1,
        button_locator_type: str = 'accessibility_id',
        mic_ready_delay: float = 1.5,
        max_retries: int = 2,
        voice_ui_locator: str = '',
        voice_ui_locator_type: str = 'accessibility_id',
        language: str = 'zh-TW',
    ):
        """語音觸發與播放同步策略：點擊語音按鈕後等待麥克風就緒再播放指令。

        When: 使用者觸發語音輸入並播放指令 "${voice_text}"
        When: User triggers voice input and plays voice command

        執行流程：
          1. 硬體就緒檢查（Scarlett 4i4 + PipeWire）
          2. 點擊 App 語音輸入按鈕
          3. 等待 mic_ready_delay 秒
          4. 確認語音輸入 UI（若提供 voice_ui_locator）
          5. 播放語音指令（透過 Scarlett 4i4）

        Arguments:
        - voice_text: 要播放的語音指令文字（如「開啟客廳燈光」）
        - button_locator: App 語音輸入按鈕的定位器
        - channel: Scarlett 4i4 聲道編號（1-4），預設 1
        - button_locator_type: 按鈕定位方式，預設 accessibility_id
        - mic_ready_delay: 等待麥克風就緒秒數（預設 1.5）
        - max_retries: 語音 UI 未出現時最大重試次數（預設 2）
        - voice_ui_locator: 語音輸入 UI 定位器（空字串表示不確認）
        - voice_ui_locator_type: 語音 UI 定位方式，預設 accessibility_id
        - language: TTS 語言（預設 zh-TW）

        Examples:
        | When | 使用者觸發語音輸入並播放指令 | 開啟客廳燈光 | 語音輸入 |
        | 觸發語音輸入並播放指令 | 開啟客廳燈光 | 語音輸入 | 1 | accessibility_id | 1.5 | 2 |
        | 觸發語音輸入並播放指令 | 關閉風扇 | com.example:id/btn_mic | 2 | id |

        Raises:
            RuntimeError: 硬體未就緒或語音播放失敗
            TimeoutError: App 語音輸入未啟動
        """
        # voice_ui_locator 空字串轉 None
        ui_locator = voice_ui_locator if voice_ui_locator else None
        self._get_impl().trigger_voice_and_play(
            voice_text=voice_text,
            button_locator=button_locator,
            channel=int(channel),
            button_locator_type=button_locator_type,
            mic_ready_delay=float(mic_ready_delay),
            max_retries=int(max_retries),
            voice_ui_locator=ui_locator,
            voice_ui_locator_type=voice_ui_locator_type,
            language=language,
        )

    @keyword("等待語音輸入結果")
    def wait_voice_input_result(
        self,
        result_locator: str,
        result_locator_type: str = 'id',
        timeout: float = 10.0,
    ) -> str:
        """等待 App UI 顯示語音辨識結果。

        When/Then: 等待語音輸入結果 "${result_locator}"
        When/Then: Wait for voice input result

        Arguments:
        - result_locator: 結果顯示區域的定位器
        - result_locator_type: 定位方式（id/xpath/accessibility_id），預設 id
        - timeout: 等待秒數（預設 10.0）

        Examples:
        | ${result}= | 等待語音輸入結果 | com.example:id/tv_result |
        | ${result}= | 等待語音輸入結果 | //TextView[@resource-id='result'] | xpath | 15 |

        Returns:
            str: 語音辨識結果文字

        Raises:
            TimeoutError: 逾時未取得語音辨識結果，附帶可能原因診斷
        """
        return self._get_impl().wait_voice_input_result(
            result_locator=result_locator,
            result_locator_type=result_locator_type,
            timeout=float(timeout),
        )

    @keyword("語音指令結果應包含")
    def assert_voice_result_contains(
        self,
        expected: str,
        result_locator: str,
        result_locator_type: str = 'id',
        timeout: float = 10.0,
    ):
        """驗證語音指令執行結果包含預期文字。

        Then: 語音指令結果應包含 "${expected}"
        Then: Voice command result should contain expected text

        Arguments:
        - expected: 預期回應文字（如「燈光已開啟」）
        - result_locator: 結果顯示區域的定位器
        - result_locator_type: 定位方式，預設 id
        - timeout: 等待秒數（預設 10.0）

        Examples:
        | Then | 語音指令結果應包含 | 燈光已開啟 | com.example:id/tv_result |
        | 語音指令結果應包含 | 風扇已關閉 | //TextView[@resource-id='result'] | xpath |

        Raises:
            TimeoutError: 逾時未取得結果
            AssertionError: 結果不符預期，附帶實際值與音量/距離調整建議
        """
        self._get_impl().assert_voice_result_contains(
            expected=expected,
            result_locator=result_locator,
            result_locator_type=result_locator_type,
            timeout=float(timeout),
        )
