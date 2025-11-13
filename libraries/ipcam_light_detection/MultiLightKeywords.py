#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi Light Array Detection Keywords
"""
import sys
from pathlib import Path
from robot.api.deco import keyword
from robot.api import logger

# 智慧匯入機制 - 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.ipcam_light_detection.MultiLightKeywords
# 2. 作為檔案匯入: Library    ../libraries/ipcam_light_detection/MultiLightKeywords.py
try:
    # 方式 1: 絕對匯入（作為模組）
    from libraries.ipcam_light_detection import MultiLightDetection
except ImportError:
    try:
        # 方式 2: 相對匯入
        from . import MultiLightDetection
    except ImportError:
        # 方式 3: 將專案根目錄加入 sys.path
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent  # 回到專案根目錄
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        # 方式 4: 直接匯入
        try:
            from libraries.ipcam_light_detection import MultiLightDetection
        except ImportError:
            # 方式 5: 當前目錄直接匯入
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
            import MultiLightDetection

class MultiLightKeywords:
    """
    Keywords for Multi Light Array Detection
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.multi_light = MultiLightDetection("default_array")

    @keyword("Given 多燈號陣列攝影機已連接")
    def given_the_multi_light_array_camera_is_connected_to_the_array(self, array_name: str):
        """
        Given: Connects to the specified multi-light array camera.
        """
        self.multi_light.連接陣列攝影機(array_name)
        logger.info(f"Connected to multi-light array camera for array {array_name}")

    @keyword("When 偵測並記錄所有燈號狀態")
    def when_all_light_statuses_are_detected_and_logged(self):
        """
        When: Detects and logs the status of all lights in the array.
        """
        result = self.multi_light.偵測所有燈號(capture_new_image=True)
        summary = self.multi_light.取得燈號狀態摘要()
        logger.info(f"Multi-light array detection summary: {summary}")
        return result

    @keyword("When 偵測並記錄指定燈號狀態")
    def when_the_status_of_light_is_detected_and_logged(self, light_key: str):
        """
        When: Detects and logs the status of a single light.
        """
        status = self.multi_light.偵測單一燈號(light_key)
        logger.info(f"Status of light {light_key}: {status}")
        return status

    @keyword("Then 燈號應該為開啟狀態")
    def then_the_light_should_be_on(self, light_key: str):
        """
        Then: Verifies that the specified light is on.
        """
        status = self.multi_light.偵測單一燈號(light_key)
        if not status['is_on']:
            raise AssertionError(f"Light {light_key} is not on. Status: {status}")
        logger.info(f"Light {light_key} is on.")

    @keyword("Then 燈號應該為關閉狀態")
    def then_the_light_should_be_off(self, light_key: str):
        """
        Then: Verifies that the specified light is off.
        """
        status = self.multi_light.偵測單一燈號(light_key)
        if not status['is_off']:
            raise AssertionError(f"Light {light_key} is not off. Status: {status}")
        logger.info(f"Light {light_key} is off.")

    @keyword("Then 燈號亮度等級應該為指定值")
    def then_the_brightness_level_of_light_should_be(self, light_key: str, expected_level: int):
        """
        Then: Verifies the brightness level of the specified light.
        """
        status = self.multi_light.偵測單一燈號(light_key)
        if status['brightness_level'] != expected_level:
            raise AssertionError(f"Brightness level of light {light_key} is {status['brightness_level']}, not {expected_level}. Status: {status}")
        logger.info(f"Brightness level of light {light_key} is {expected_level}.")

    @keyword("Then 開啟燈號數量應該為指定值")
    def then_the_number_of_on_lights_should_be(self, expected_count: int):
        """
        Then: Verifies the number of lights that are on.
        """
        summary = self.multi_light.取得燈號狀態摘要()
        if summary['on_count'] != int(expected_count):
            raise AssertionError(f"Number of on lights is {summary['on_count']}, not {expected_count}. Summary: {summary}")
        logger.info(f"Number of on lights is {expected_count}.")

    @keyword("Then 關閉燈號數量應該為指定值")
    def then_the_number_of_off_lights_should_be(self, expected_count: int):
        """
        Then: Verifies the number of lights that are off.
        """
        summary = self.multi_light.取得燈號狀態摘要()
        if summary['off_count'] != int(expected_count):
            raise AssertionError(f"Number of off lights is {summary['off_count']}, not {expected_count}. Summary: {summary}")
        logger.info(f"Number of off lights is {expected_count}.")

    @keyword("When 儲存標註陣列影像到指定路徑")
    def when_the_annotated_array_image_is_saved_to(self, file_path: str):
        """
        When: Saves the annotated array image.
        """
        self.multi_light.儲存標註影像(file_path, show_brightness=True)
        logger.info(f"Annotated array image saved to {file_path}")

    @keyword("When 等待指定燈號開啟")
    def when_i_wait_for_light_to_turn_on(self, light_key: str, timeout: int = 30):
        """
        When: Waits for a specific light to turn on.
        """
        success = self.multi_light.等待燈號模式(**{light_key: True}, timeout=int(timeout))
        if not success:
            raise AssertionError(f"Timed out waiting for light {light_key} to turn on.")
        logger.info(f"Light {light_key} turned on.")

    @keyword("When 等待指定燈號關閉")
    def when_i_wait_for_light_to_turn_off(self, light_key: str, timeout: int = 30):
        """
        When: Waits for a specific light to turn off.
        """
        success = self.multi_light.等待燈號模式(**{light_key: False}, timeout=int(timeout))
        if not success:
            raise AssertionError(f"Timed out waiting for light {light_key} to turn off.")
        logger.info(f"Light {light_key} turned off.")

    @keyword("And 陣列攝影機已斷開連接")
    def and_the_array_camera_is_disconnected(self):
        """
        And: Disconnects the array camera.
        """
        self.multi_light.斷開陣列攝影機連線()
        logger.info("Disconnected from the array camera.")
