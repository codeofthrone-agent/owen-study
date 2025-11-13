#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Camera Light Detection Keywords
"""
import sys
from pathlib import Path
from robot.api.deco import keyword
from robot.api import logger

# 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.ipcam_light_detection.IPCamKeywords
# 2. 作為檔案匯入: Library    ../libraries/ipcam_light_detection/IPCamKeywords.py
try:
    # 方式 1: 絕對匯入（作為模組）
    from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
except ImportError:
    # 方式 2: 將當前目錄加入 sys.path，然後直接匯入
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from IPCamLightDetection import IPCamLightDetection

class IPCamKeywords:
    """
    Keywords for IP Camera Light Detection
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.ipcam = IPCamLightDetection()

    @keyword("Given IP 攝影機已連接到攝影機")
    def given_the_ipcamera_is_connected_to(self, environment: str, camera_name: str):
        """
        Given: 連接到指定的 IP 攝影機
        Given: Connects to the specified IP camera.

        此關鍵字會連接到在指定環境中的特定 IP 攝影機。
        This keyword connects to a specific IP camera in the given environment.

        Arguments:
        - environment: The environment where the camera is located (e.g., 'laboratory').
        - camera_name: The name of the camera (e.g., 'level1').

        Prerequisites:
        - The IP camera must be available on the network.

        Examples:
        | Given | IP 攝影機已連接到攝影機 | laboratory | level1 |
        """
        self.ipcam.連接攝影機(environment, camera_name)
        logger.info(f"Connected to IPCamera {camera_name} in {environment}")

    @keyword("When 檢查當前燈光亮度")
    def when_the_light_brightness_is_checked(self):
        """
        When: 檢查當前燈光亮度
        When: Checks the current light brightness.

        此關鍵字會擷取影像並計算當前亮度值。
        This keyword captures an image and calculates the current brightness value.

        Returns:
        - The brightness value (0-255).

        Examples:
        | ${brightness}= | When 檢查當前燈光亮度 |
        """
        brightness = self.ipcam.取得當前亮度()
        logger.info(f"Current light brightness is {brightness}")
        return brightness

    @keyword("Then 燈光應該為開啟狀態")
    def then_the_light_should_be_on(self):
        """
        Then: 驗證燈光為開啟狀態
        Then: Verifies that the light is on.

        此關鍵字會驗證當前燈光為開啟狀態（亮度高於閾值）。
        This keyword verifies that the current light is on (brightness is above the threshold).

        Prerequisites:
        - A brightness check has been performed.

        Examples:
        | Then 燈光應該為開啟狀態 |
        """
        is_on = self.ipcam.燈光是否開啟()
        if not is_on:
            raise AssertionError("Light is not on")
        logger.info("Light is on")

    @keyword("Then 燈光應該為關閉狀態")
    def then_the_light_should_be_off(self):
        """
        Then: 驗證燈光為關閉狀態
        Then: Verifies that the light is off.

        此關鍵字會驗證當前燈光為關閉狀態（亮度低於閾值）。
        This keyword verifies that the current light is off (brightness is below the threshold).

        Prerequisites:
        - A brightness check has been performed.

        Examples:
        | Then 燈光應該為關閉狀態 |
        """
        is_off = self.ipcam.燈光是否關閉()
        if not is_off:
            raise AssertionError("Light is not off")
        logger.info("Light is off")

    @keyword("When 取得燈光狀態")
    def when_i_get_the_light_status(self):
        """
        When: 取得燈光狀態
        When: Gets the current light status.

        此關鍵字會檢查燈光狀態並詳細記錄所有資訊。
        This keyword checks the light status and logs all information.

        Returns:
        - A dictionary containing the light status information.

        Examples:
        | ${status}= | When 取得燈光狀態 |
        """
        status = self.ipcam.取得燈光狀態()
        logger.info(f"Light status: {status}")
        return status

    @keyword("When 等待燈光開啟指定秒數")
    def when_i_wait_for_the_light_to_turn_on(self, timeout: int = 30):
        """
        When: 等待燈光開啟
        When: Waits for the light to turn on.

        此關鍵字會等待燈光變為開啟狀態。
        This keyword waits for the light to turn on.

        Arguments:
        - timeout: The maximum time to wait in seconds.

        Examples:
        | When 等待燈光開啟 30 秒 |
        """
        self.ipcam.等待燈光變化('on', timeout=int(timeout))
        logger.info("Waited for the light to turn on")

    @keyword("When 等待燈光關閉指定秒數")
    def when_i_wait_for_the_light_to_turn_off(self, timeout: int = 30):
        """
        When: 等待燈光關閉
        When: Waits for the light to turn off.

        此關鍵字會等待燈光變為關閉狀態。
        This keyword waits for the light to turn off.

        Arguments:
        - timeout: The maximum time to wait in seconds.

        Examples:
        | When 等待燈光關閉 30 秒 |
        """
        self.ipcam.等待燈光變化('off', timeout=int(timeout))
        logger.info("Waited for the light to turn off")

    @keyword("When 儲存當前攝影機影像到指定路徑")
    def when_i_save_the_current_camera_image_to(self, file_path: str):
        """
        When: 儲存當前攝影機影像
        When: Saves the current camera image.

        此關鍵字會儲存當前攝影機影像到指定檔案路徑。
        This keyword saves the current camera image to the specified file path.

        Arguments:
        - file_path: The path to save the image to.

        Examples:
        | When 儲存當前攝影機影像到 "/tmp/image.jpg" |
        """
        self.ipcam.儲存最後影像(file_path)
        logger.info(f"Saved camera image to {file_path}")

    @keyword("Then 亮度應該大於指定值")
    def then_the_brightness_should_be_greater_than(self, expected_brightness: int):
        """
        Then: 驗證亮度大於指定值
        Then: Verifies that the brightness is greater than the expected value.

        此關鍵字會驗證當前亮度大於指定值。
        This keyword verifies that the current brightness is greater than the specified value.

        Arguments:
        - expected_brightness: The expected minimum brightness value.

        Examples:
        | Then 亮度應該大於 100 |
        """
        brightness = self.ipcam.取得當前亮度()
        if brightness <= int(expected_brightness):
            raise AssertionError(f"Brightness {brightness} is not greater than {expected_brightness}")
        logger.info(f"Brightness {brightness} is greater than {expected_brightness}")

    @keyword("Then 亮度應該小於指定值")
    def then_the_brightness_should_be_less_than(self, expected_brightness: int):
        """
        Then: 驗證亮度小於指定值
        Then: Verifies that the brightness is less than the expected value.

        此關鍵字會驗證當前亮度小於指定值。
        This keyword verifies that the current brightness is less than the specified value.

        Arguments:
        - expected_brightness: The expected maximum brightness value.

        Examples:
        | Then 亮度應該小於 50 |
        """
        brightness = self.ipcam.取得當前亮度()
        if brightness >= int(expected_brightness):
            raise AssertionError(f"Brightness {brightness} is not less than {expected_brightness}")
        logger.info(f"Brightness {brightness} is less than {expected_brightness}")

    @keyword("Then 亮度應該在指定範圍內")
    def then_the_brightness_should_be_between(self, min_brightness: int, max_brightness: int):
        """
        Then: 驗證亮度在範圍內
        Then: Verifies that the brightness is within the specified range.

        此關鍵字會驗證當前亮度在指定範圍內。
        This keyword verifies that the current brightness is within the specified range.

        Arguments:
        - min_brightness: The minimum brightness value.
        - max_brightness: The maximum brightness value.

        Examples:
        | Then 亮度應該在 50 和 150 之間 |
        """
        brightness = self.ipcam.取得當前亮度()
        if not (int(min_brightness) <= brightness <= int(max_brightness)):
            raise AssertionError(f"Brightness {brightness} is not between {min_brightness} and {max_brightness}")
        logger.info(f"Brightness {brightness} is between {min_brightness} and {max_brightness}")
