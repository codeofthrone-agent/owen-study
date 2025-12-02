#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Camera Light Detection Keywords
"""
import sys
from pathlib import Path
from typing import Dict, Optional
from robot.api.deco import keyword
from robot.api import logger
from datetime import datetime

# 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.ipcam_light_detection.IPCamKeywords
# 2. 作為檔案匯入: Library    ../libraries/ipcam_light_detection/IPCamKeywords.py
current_dir = Path(__file__).parent

try:
    # 方式 1: 絕對匯入（作為模組）
    from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
except ImportError:
    # 方式 2: 將當前目錄加入 sys.path，然後直接匯入
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from IPCamLightDetection import IPCamLightDetection

# Add project root to sys.path for config import
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from config.robot_arm.config_loader import ConfigLoader
from config.robot_arm.environment_config import EnvironmentConfig

class IPCamKeywords:
    """
    Keywords for IP Camera Light Detection
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # 儲存多個攝影機實體: {camera_name: IPCamLightDetection_instance}
        self.ipcams: Dict[str, IPCamLightDetection] = {}
        self.config_loader = None
        self.current_environment = None

    @property
    def ipcam(self) -> IPCamLightDetection:
        """
        取得預設攝影機實體 (為了向後相容)
        如果有多個攝影機，返回第一個；如果沒有，返回一個未連接的實體
        """
        if not self.ipcams:
            return IPCamLightDetection()
        return next(iter(self.ipcams.values()))

    @keyword("Given IP 攝影機已連接到攝影機")
    def given_the_ipcamera_is_connected_to(self, environment: str, camera_name: str = None):
        """
        Given: 連接到指定的 IP 攝影機
        Given: Connects to the specified IP camera(s).

        此關鍵字會連接到在指定環境中的 IP 攝影機。
        如果未指定 camera_name，將會連接該環境下的所有攝影機。

        Arguments:
        - environment: The environment where the camera is located (e.g., 'rv_car').
        - camera_name: (Optional) The name of the camera (e.g., 'cam1'). If None, connects to all cameras.

        Prerequisites:
        - The IP camera must be available on the network.

        Examples:
        | Given | IP 攝影機已連接到攝影機 | rv_car | cam1 |
        | Given | IP 攝影機已連接到攝影機 | rv_car |      |
        """
        self.current_environment = environment
        self.config_loader = ConfigLoader(environment)

        cameras_to_connect = []

        if camera_name:
            # 連接單一指定攝影機
            cameras_to_connect.append(camera_name)
        else:
            # 連接環境下所有攝影機
            try:
                camera_configs = EnvironmentConfig.get_cameras(environment)
                for cam_conf in camera_configs:
                    cameras_to_connect.append(cam_conf['id'])
                logger.info(f"Auto-connecting to all cameras in {environment}: {cameras_to_connect}")
            except Exception as e:
                logger.error(f"Failed to get cameras for environment {environment}: {e}")
                raise

        for cam_id in cameras_to_connect:
            try:
                if cam_id in self.ipcams:
                    logger.info(f"Camera {cam_id} already connected, skipping.")
                    continue

                new_ipcam = IPCamLightDetection()
                new_ipcam.連接攝影機(environment, cam_id)
                self.ipcams[cam_id] = new_ipcam
                logger.info(f"Successfully connected to IPCamera {cam_id} in {environment}")
            except Exception as e:
                logger.error(f"Failed to connect to camera {cam_id}: {e}")
                raise

    def _get_ipcam_for_light(self, voice_light_id: str) -> IPCamLightDetection:
        """
        根據語音燈光 ID 取得對應的攝影機實體
        """
        self._ensure_config_loader()
        
        # 1. 取得映射
        mapping = self.config_loader.get_voice_mapping(voice_light_id)
        if not mapping:
            raise ValueError(f"Unknown voice light ID: {voice_light_id}")
            
        env_light_id = mapping.get('environment_light')
        if not env_light_id:
            raise ValueError(f"No environment light mapping for {voice_light_id}")
            
        # 2. 取得燈光設定
        lights = self.config_loader.get_environment_lights()
        if env_light_id not in lights:
             raise ValueError(f"Environment light {env_light_id} not found in config")
        
        light_config = lights[env_light_id]
        
        # 3. 取得 Camera ID
        camera_id = light_config.get('camera_id')
        if not camera_id:
            # 向後相容：如果沒有指定 camera_id，且只有一個攝影機，就用那個
            if len(self.ipcams) == 1:
                camera_id = next(iter(self.ipcams.keys()))
                logger.info(f"No camera_id specified for {env_light_id}, using default: {camera_id}")
            else:
                raise ValueError(f"Light {env_light_id} configuration missing 'camera_id' and multiple cameras are connected.")

        # 4. 取得攝影機實體
        if camera_id not in self.ipcams:
             raise ValueError(f"Camera {camera_id} required for {env_light_id} is not connected. Connected cameras: {list(self.ipcams.keys())}")
             
        logger.info(f"Using camera {camera_id} for light {env_light_id}")
        return self.ipcams[camera_id]

    @keyword("When 檢查當前燈光亮度")
    def when_the_light_brightness_is_checked(self):
        """
        When: 檢查當前燈光亮度
        (Legacy keyword, uses default camera)
        """
        brightness = self.ipcam.取得當前亮度()
        logger.info(f"Current light brightness is {brightness}")
        return brightness

    @keyword("Then 燈光應該為開啟狀態")
    def then_the_light_should_be_on(self):
        """
        Then: 驗證燈光為開啟狀態
        (Legacy keyword, uses default camera)
        """
        is_on = self.ipcam.燈光是否開啟()
        if not is_on:
            raise AssertionError("Light is not on")
        logger.info("Light is on")

    @keyword("Then 燈光應該為關閉狀態")
    def then_the_light_should_be_off(self):
        """
        Then: 驗證燈光為關閉狀態
        (Legacy keyword, uses default camera)
        """
        is_off = self.ipcam.燈光是否關閉()
        if not is_off:
            raise AssertionError("Light is not off")
        logger.info("Light is off")

    @keyword("When 取得燈光狀態")
    def when_i_get_the_light_status(self):
        """
        When: 取得燈光狀態
        (Legacy keyword, uses default camera)
        """
        status = self.ipcam.取得燈光狀態()
        logger.info(f"Light status: {status}")
        return status

    @keyword("When 等待燈光開啟指定秒數")
    def when_i_wait_for_the_light_to_turn_on(self, timeout: int = 30):
        """
        When: 等待燈光開啟
        (Legacy keyword, uses default camera)
        """
        self.ipcam.等待燈光變化('on', timeout=int(timeout))
        logger.info("Waited for the light to turn on")

    @keyword("When 等待燈光關閉指定秒數")
    def when_i_wait_for_the_light_to_turn_off(self, timeout: int = 30):
        """
        When: 等待燈光關閉
        (Legacy keyword, uses default camera)
        """
        self.ipcam.等待燈光變化('off', timeout=int(timeout))
        logger.info("Waited for the light to turn off")

    @keyword("When 儲存當前攝影機影像到指定路徑")
    def when_i_save_the_current_camera_image_to(self, file_path: str):
        """
        When: 儲存當前攝影機影像
        (Legacy keyword, uses default camera)
        """
        self.ipcam.儲存最後影像(file_path)
        logger.info(f"Saved camera image to {file_path}")

    @keyword("Then 亮度應該大於指定值")
    def then_the_brightness_should_be_greater_than(self, expected_brightness: int):
        """
        Then: 驗證亮度大於指定值
        (Legacy keyword, uses default camera)
        """
        brightness = self.ipcam.取得當前亮度()
        if brightness <= int(expected_brightness):
            raise AssertionError(f"Brightness {brightness} is not greater than {expected_brightness}")
        logger.info(f"Brightness {brightness} is greater than {expected_brightness}")

    @keyword("Then 亮度應該小於指定值")
    def then_the_brightness_should_be_less_than(self, expected_brightness: int):
        """
        Then: 驗證亮度小於指定值
        (Legacy keyword, uses default camera)
        """
        brightness = self.ipcam.取得當前亮度()
        if brightness >= int(expected_brightness):
            raise AssertionError(f"Brightness {brightness} is not less than {expected_brightness}")
        logger.info(f"Brightness {brightness} is less than {expected_brightness}")

    @keyword("Then 亮度應該在指定範圍內")
    def then_the_brightness_should_be_between(self, min_brightness: int, max_brightness: int):
        """
        Then: 驗證亮度在範圍內
        (Legacy keyword, uses default camera)
        """
        brightness = self.ipcam.取得當前亮度()
        if not (int(min_brightness) <= brightness <= int(max_brightness)):
            raise AssertionError(f"Brightness {brightness} is not between {min_brightness} and {max_brightness}")
        logger.info(f"Brightness {brightness} is between {min_brightness} and {max_brightness}")

    def _ensure_config_loader(self):
        if self.config_loader is None:
            if self.current_environment:
                self.config_loader = ConfigLoader(self.current_environment)
            else:
                 raise RuntimeError("ConfigLoader not initialized. Please connect to camera first.")

    @keyword("When 儲存完整影像包含標註")
    def when_save_full_image_with_annotation(self, voice_light_id: str, file_path: str):
        """
        When: 儲存完整影像包含標註
        
        Args:
            voice_light_id: 語音指令 ID (例如: "light_one")
            file_path: 儲存路徑 (支援 {timestamp} 佔位符)
        """
        ipcam = self._get_ipcam_for_light(voice_light_id)
        
        # Get mapping and config again (already checked in _get_ipcam_for_light but needed for ROI)
        mapping = self.config_loader.get_voice_mapping(voice_light_id)
        env_light_id = mapping.get('environment_light')
        lights = self.config_loader.get_environment_lights()
        roi = lights[env_light_id]['roi']
             
        # Generate timestamp if needed
        if "{timestamp}" in file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = file_path.replace("{timestamp}", timestamp)

        # Always capture new image to ensure freshness
        ipcam.capture_image()
        ipcam.save_image_with_roi(file_path, roi)
        logger.info(f"Saved annotated image for {voice_light_id} to {file_path}")

    @keyword("When 儲存 ROI 影像")
    def when_save_roi_image(self, voice_light_id: str, file_path: str):
        """
        When: 儲存 ROI 影像
        
        Args:
            voice_light_id: 語音指令 ID (例如: "light_one")
            file_path: 儲存路徑 (支援 {timestamp} 佔位符)
        """
        ipcam = self._get_ipcam_for_light(voice_light_id)
        
        mapping = self.config_loader.get_voice_mapping(voice_light_id)
        env_light_id = mapping.get('environment_light')
        lights = self.config_loader.get_environment_lights()
        roi = lights[env_light_id]['roi']
             
        # Generate timestamp if needed
        if "{timestamp}" in file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = file_path.replace("{timestamp}", timestamp)

        # Always capture new image to ensure freshness
        ipcam.capture_image()
        ipcam.save_cropped_roi(file_path, roi)
        logger.info(f"Saved ROI image for {voice_light_id} to {file_path}")

    @keyword("Then 驗證環境燈光狀態")
    def then_verify_environment_light_status(self, voice_light_id: str, expected_state: str):
        """
        Then: 驗證環境燈光狀態
        
        Args:
            voice_light_id: 語音指令 ID (例如: "light_one")
            expected_state: 預期狀態 ('on' or 'off')
        """
        ipcam = self._get_ipcam_for_light(voice_light_id)
        
        mapping = self.config_loader.get_voice_mapping(voice_light_id)
        env_light_id = mapping.get('environment_light')
        lights = self.config_loader.get_environment_lights()
        light_config = lights[env_light_id]
        
        bright_threshold = light_config.get('bright_threshold')
        dark_threshold = light_config.get('dark_threshold')
        
        # 1. Capture image
        image = ipcam.capture_image()
        
        # 2. Crop to ROI
        roi = light_config['roi']
        cropped_image = ipcam.crop_roi(image, roi)
        
        # 3. Calculate brightness of cropped image
        brightness = ipcam.calculate_brightness(cropped_image, region='full')
        
        logger.info(f"Light {env_light_id} brightness: {brightness}")
        
        if expected_state.lower() == 'on':
            if bright_threshold and brightness < bright_threshold:
                 raise AssertionError(f"Light {env_light_id} should be ON (brightness {brightness} < {bright_threshold})")
            elif not bright_threshold and not ipcam.is_light_on(brightness):
                 raise AssertionError(f"Light {env_light_id} should be ON (brightness {brightness})")
        elif expected_state.lower() == 'off':
            if dark_threshold and brightness > dark_threshold:
                 raise AssertionError(f"Light {env_light_id} should be OFF (brightness {brightness} > {dark_threshold})")
            elif not dark_threshold and not ipcam.is_light_off(brightness):
                 raise AssertionError(f"Light {env_light_id} should be OFF (brightness {brightness})")
        else:
            raise ValueError(f"Invalid expected state: {expected_state}")
            
        logger.info(f"Verified light {env_light_id} is {expected_state}")

    @keyword("When 取得環境燈光亮度")
    def when_get_environment_light_brightness(self, voice_light_id: str):
        """
        When: 取得環境燈光亮度
        
        Args:
            voice_light_id: 語音指令 ID (例如: "light_one")
            
        Returns:
            float: 亮度值
        """
        ipcam = self._get_ipcam_for_light(voice_light_id)
        
        mapping = self.config_loader.get_voice_mapping(voice_light_id)
        env_light_id = mapping.get('environment_light')
        lights = self.config_loader.get_environment_lights()
        light_config = lights[env_light_id]
        
        # Capture image
        image = ipcam.capture_image()
        
        # Crop to ROI
        roi = light_config['roi']
        cropped_image = ipcam.crop_roi(image, roi)
        
        # Calculate brightness
        brightness = ipcam.calculate_brightness(cropped_image, region='full')
        
        logger.info(f"Light {env_light_id} brightness: {brightness}")
        return brightness

    @keyword("Then 驗證亮度變化")
    def then_verify_brightness_change(self, before_brightness: float, after_brightness: float, expected_change: str, min_delta: float = 10.0):
        """
        Then: 驗證亮度變化
        
        Args:
            before_brightness: 變化前亮度
            after_brightness: 變化後亮度
            expected_change: 'increase' (變亮) or 'decrease' (變暗)
            min_delta: 最小變化幅度 (預設 10.0)
        """
        before_val = float(before_brightness)
        after_val = float(after_brightness)
        delta = after_val - before_val
        min_delta_val = float(min_delta)
        
        logger.info(f"Brightness change: {before_val:.2f} -> {after_val:.2f} (Delta: {delta:.2f})")
        
        if expected_change.lower() in ['increase', '增加', '變亮', '+']:
            if delta < min_delta_val:
                raise AssertionError(f"Brightness should increase by at least {min_delta_val} (Actual delta: {delta:.2f}, {before_val:.2f} -> {after_val:.2f})")
        elif expected_change.lower() in ['decrease', '減少', '變暗', '-']:
            # For decrease, delta should be negative. e.g. -20.
            # We want the decrease amount to be at least min_delta.
            # So delta should be <= -min_delta.
            if delta > -min_delta_val:
                 raise AssertionError(f"Brightness should decrease by at least {min_delta_val} (Actual delta: {delta:.2f}, {before_val:.2f} -> {after_val:.2f})")
        else:
            raise ValueError(f"Invalid expected change: {expected_change}")
