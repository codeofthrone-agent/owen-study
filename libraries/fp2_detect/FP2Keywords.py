#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aqara FP2 Detection Keywords
"""
import sys
from pathlib import Path
from robot.api.deco import keyword
from robot.api import logger
import asyncio

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from fp2_homekit import get_status_once
except ImportError as e:
    logger.warn(f"Failed to import fp2_homekit: {e}")

class FP2Keywords:
    """
    Keywords for Aqara FP2 HomeKit Space Detection
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # 鍵為 sensor_id，值為該感測器的狀態 { "mode": str, "alias": str }
        self.sensors = {}

    @keyword('Given FP2 空間雷達已連線 "${environment}" "${sensor_id}" "${mode}"')
    def given_fp2_connected(self, environment: str, sensor_id: str, mode: str):
        """
        Given: 確認 FP2 空間感測器已就緒並完成配置
        Given: Confirm the FP2 spatial sensor is ready and configured
        
        此關鍵字用於從 ipcam_config 載入指定的 fp2_sensor 設定，
        並宣告接下來的 FP2 操作將使用何種判定模式。
        
        Arguments:
        - environment: 測試環境 (例如 'rv_car')
        - sensor_id: 感測器的 ID (例如 'awning_fp2')
        - mode: 判定模式 ('awning' 針對雨遮，'slide' 針對側推艙)
        
        Prerequisites:
        - 必須在 yaml 中定義好該感測器，並在本地具有對應名稱 (alias) 的配對資料。
        
        Examples:
        | Given | FP2 空間雷達已連線 "rv_car" "awning_fp2" "awning" |
        """
        try:
            # sys.path 剛才已幫忙加入父目錄，以防萬一再處理一次也可
            # 引入 get_fp2_config 
            from config.ipcam_config import get_fp2_config
            sensor_config = get_fp2_config(environment, sensor_id)
        except Exception as e:
            raise RuntimeError(f"載入 FP2 設定失敗: {e}")

        alias = sensor_config.get("alias", "my_fp2_sensor")
        self.sensors[sensor_id] = {
            "mode": mode,
            "alias": alias,
            "environment": environment,
            "config": sensor_config
        }
        logger.info(f"FP2 '{sensor_id}' (Alias: {alias}) 已宣告為連線就緒狀態 (模式: {mode})")

    @keyword('When 取得 FP2 當前空間佔用狀態')
    @keyword('When 取得 FP2 當前空間佔用狀態 "${sensor_id}"')
    def when_get_fp2_current_space_state(self, sensor_id: str = None) -> str:
        """
        When: 取得 FP2 當前空間佔用狀態
        When: Get current space occupancy state from FP2
        
        此關鍵字會發出非同步單次查詢給 FP2 設備，取得區域即時資料，並判斷總體狀態。
        
        Arguments:
        - sensor_id: 感測器 ID (若未指定，預設為第一台)
        """
        sensor = self._get_target_sensor(sensor_id)
        result = asyncio.run(get_status_once(
            sensor["alias"], sensor["mode"], sensor.get("config", {}),
            pairing_file=sensor["config"].get("pairing_file", "pairing_data.json")
        ))

        if "error" in result:
             raise RuntimeError(f"查詢 FP2 狀態失敗: {result['error']}")
             
        state = result["state_id"]
        
        # 快取最新的狀態給 Then 使用，避免重複查詢造成的網路延遲
        sensor["cached_state"] = state
        
        logger.info(f"FP2 當前空間佔用狀態為: {state} (被佔用區域: {result['occupied_zones_count']}/{result['total_zones']})")
        return state

    @keyword('Then FP2 空間狀態應該為 "${expected_state}"')
    @keyword('Then FP2 空間狀態應該為 "${expected_state}" 於 "${sensor_id}"')
    def then_fp2_space_state_should_be(self, expected_state: str, sensor_id: str = None):
        """
        Then: 驗證 FP2 空間狀態應符合預期狀態
        Then: Verify the FP2 space state matches the expected state
        
        Arguments:
        - expected_state: 預期的狀態字串 (如: 'open' 代表展開/淨空, 'close' 代表收起/被佔用)
        - sensor_id: 感測器 ID (若未指定，預設為第一台)
        """
        sensor = self._get_target_sensor(sensor_id)
        
        # 優先使用快取狀態，避免重複呼叫 get_status_once 造成延遲與設備負擔
        if "cached_state" in sensor:
            actual_state = sensor["cached_state"]
            logger.info(f"使用快取的狀態: {actual_state} 進行驗證")
            # 清空快取確保後續若有其他獨立 Then 時能重新查詢最新的狀態
            del sensor["cached_state"]
        else:
            result = asyncio.run(get_status_once(
                sensor["alias"], sensor["mode"], sensor.get("config", {}),
                pairing_file=sensor["config"].get("pairing_file", "pairing_data.json")
            ))
            if "error" in result:
                 raise RuntimeError(f"查詢 FP2 狀態失敗: {result['error']}")
            actual_state = result["state_id"]
            
        if actual_state != expected_state:
             raise AssertionError(f"FP2 狀態驗證失敗！預期應為: {expected_state}，但實際為: {actual_state}")
             
        logger.info(f"驗證通過：FP2 空間狀態確實為 {expected_state}")

    @keyword('And 斷開 FP2 連線')
    def and_disconnect_fp2(self, sensor_id: str = None):
        """
        And: 安全釋放 FP2 狀態與資源
        And: Safely release FP2 states and resources
        """
        if sensor_id is None:
            self.sensors.clear()
            logger.info("所有 FP2 連線狀態已清空與斷開。")
        else:
            if sensor_id in self.sensors:
                del self.sensors[sensor_id]
                logger.info(f"FP2 '{sensor_id}' 連線狀態已斷開。")

    def _get_target_sensor(self, sensor_id: str = None):
        """取得目標感測器配置的 Helper"""
        if not self.sensors:
            raise RuntimeError("尚未初始化任何 FP2，請先使用 'Given FP2 空間雷達已連線'")
        
        if sensor_id is None:
             # 回傳字典中的第一個
             return list(self.sensors.values())[0]
        
        if sensor_id not in self.sensors:
             raise RuntimeError(f"FP2 '{sensor_id}' 尚未連線")
             
        return self.sensors[sensor_id]
