"""
ConfigLoader 統一載入器 (Unified Configuration Loader)

功能:
- 載入環境專屬 YAML 配置檔案
- 管理按鈕配置（buttons）與環境燈光配置（environment_lights）
- 提供快取機制，避免重複讀取檔案
- 整合 EnvironmentConfig，提供統一存取介面
- 支援配置驗證與錯誤處理

作者: Robot Automation Team
日期: 2025-11-18
版本: v1.0.0

Example:
    >>> from config.robot_arm.config_loader import ConfigLoader
    >>>
    >>> # 載入台北實驗室配置
    >>> loader = ConfigLoader("taipei_lab")
    >>> buttons = loader.get_buttons()
    >>> print(len(buttons))
    13
    >>>
    >>> # 取得特定按鈕
    >>> light1 = loader.get_button("light1")
    >>> print(light1["name"])
    'Light1 按鈕'
    >>>
    >>> # 取得環境燈光
    >>> lights = loader.get_environment_lights()
    >>> print(len(lights))
    1
"""

import copy
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from loguru import logger

from config.robot_arm.environment_config import EnvironmentConfig


class ConfigLoader:
    """配置載入器

    負責載入和管理環境專屬的 YAML 配置檔案，包括按鈕配置、
    環境燈光配置等。提供快取機制和統一的存取介面。

    Attributes:
        env_name (str): 環境名稱
        _config_cache (dict): 配置快取
        _env_config (dict): 環境配置
        _yaml_config (dict): YAML 配置

    Example:
        >>> loader = ConfigLoader("taipei_lab")
        >>> buttons = loader.get_buttons()
        >>> lights = loader.get_environment_lights()
    """

    # 類別級別快取（所有實例共享）
    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, env_name: str):
        """初始化配置載入器

        Args:
            env_name: 環境名稱 ("taipei_lab" | "taoyuan_lab" | "rv_car")

        Raises:
            ValueError: 未知環境名稱
            FileNotFoundError: 配置檔案不存在
        """
        # 驗證環境是否存在
        if not EnvironmentConfig.validate_environment(env_name):
            available = ", ".join(EnvironmentConfig.list_environments())
            raise ValueError(
                f"未知環境: {env_name}\n"
                f"可用環境: {available}"
            )

        self.env_name = env_name
        self._env_config = EnvironmentConfig.get_environment(env_name)
        self._yaml_config: Optional[Dict[str, Any]] = None

        # 載入 YAML 配置
        self._load_yaml_config()

        logger.info(
            f"ConfigLoader 初始化完成: {env_name} "
            f"({self._env_config['name']})"
        )

    def _load_yaml_config(self) -> None:
        """載入 YAML 配置檔案

        從快取載入或從檔案系統讀取 YAML 配置。

        Raises:
            FileNotFoundError: 配置檔案不存在
            yaml.YAMLError: YAML 格式錯誤
        """
        # 檢查快取
        if self.env_name in ConfigLoader._cache:
            self._yaml_config = ConfigLoader._cache[self.env_name]
            logger.debug(f"從快取載入配置: {self.env_name}")
            return

        # 取得配置檔案路徑
        config_path = self._env_config["button_config_path"]

        # 轉換為絕對路徑（從專案根目錄）
        project_root = Path(__file__).parent.parent.parent
        full_path = project_root / config_path

        # 檢查檔案是否存在
        if not full_path.exists():
            raise FileNotFoundError(
                f"配置檔案不存在: {full_path}\n"
                f"環境: {self.env_name}\n"
                f"預期路徑: {config_path}"
            )

        # 讀取 YAML 檔案
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            # 驗證基本結構
            self._validate_yaml_structure(yaml_data, full_path)

            # 存入快取
            ConfigLoader._cache[self.env_name] = yaml_data
            self._yaml_config = yaml_data

            logger.info(
                f"成功載入配置: {full_path} "
                f"(按鈕: {len(yaml_data.get('buttons', {}))}, "
                f"燈光: {len(yaml_data.get('environment_lights', {}))})"
            )

        except yaml.YAMLError as e:
            logger.error(f"YAML 格式錯誤: {full_path}\n{e}")
            raise
        except Exception as e:
            logger.error(f"載入配置失敗: {full_path}\n{e}")
            raise

    def _validate_yaml_structure(self, yaml_data: Dict[str, Any], file_path: Path) -> None:
        """驗證 YAML 配置結構

        Args:
            yaml_data: YAML 資料
            file_path: 檔案路徑（用於錯誤訊息）

        Raises:
            ValueError: 配置結構不正確
        """
        # 必要欄位
        required_fields = ["environment", "connection", "defaults", "buttons"]

        for field in required_fields:
            if field not in yaml_data:
                raise ValueError(
                    f"配置檔案缺少必要欄位: {field}\n"
                    f"檔案: {file_path}"
                )

        # 驗證環境名稱一致性
        yaml_env_name = yaml_data["environment"].get("name")
        if yaml_env_name != self.env_name:
            logger.warning(
                f"YAML 中的環境名稱 ({yaml_env_name}) "
                f"與請求的環境 ({self.env_name}) 不一致"
            )

        # 驗證 buttons 是字典
        if not isinstance(yaml_data["buttons"], dict):
            raise ValueError(
                f"buttons 必須是字典格式\n"
                f"檔案: {file_path}"
            )

        logger.debug(f"YAML 結構驗證通過: {file_path}")

    def get_buttons(self) -> Dict[str, Dict[str, Any]]:
        """取得所有按鈕配置

        Returns:
            dict: 按鈕配置字典，key 為按鈕 ID，value 為按鈕配置

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> buttons = loader.get_buttons()
            >>> print(len(buttons))
            13
            >>> print(list(buttons.keys())[:3])
            ['light1', 'light2', 'light3']
        """
        if self._yaml_config is None:
            return {}

        return copy.deepcopy(self._yaml_config.get("buttons", {}))

    def get_button(self, button_id: str) -> Dict[str, Any]:
        """取得特定按鈕配置

        Args:
            button_id: 按鈕 ID（例如: "light1", "hvac"）

        Returns:
            dict: 按鈕配置

        Raises:
            ValueError: 按鈕不存在

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> light1 = loader.get_button("light1")
            >>> print(light1["name"])
            'Light1 按鈕'
            >>> print(light1["down_angles"])
            [3.5, -60, -82, 25, 0, 0]
        """
        buttons = self.get_buttons()

        if button_id not in buttons:
            available = list(buttons.keys())
            raise ValueError(
                f"按鈕不存在: {button_id}\n"
                f"環境: {self.env_name}\n"
                f"可用按鈕: {', '.join(available)}"
            )

        return copy.deepcopy(buttons[button_id])

    def get_environment_lights(self) -> Dict[str, Dict[str, Any]]:
        """取得所有環境燈光配置

        Returns:
            dict: 環境燈光配置字典，key 為燈光 ID，value 為燈光配置

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> lights = loader.get_environment_lights()
            >>> print(len(lights))
            1
            >>> print(list(lights.keys()))
            ['light_array']
        """
        if self._yaml_config is None:
            return {}

        return copy.deepcopy(self._yaml_config.get("environment_lights", {}))

    def get_environment_light(self, light_id: str) -> Dict[str, Dict[str, Any]]:
        """取得特定環境燈光配置

        Args:
            light_id: 燈光 ID（例如: "light_array", "headlight_left"）

        Returns:
            dict: 燈光配置

        Raises:
            ValueError: 燈光不存在

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> light_array = loader.get_environment_light("light_array")
            >>> print(light_array["name"])
            '實驗室燈泡陣列'
            >>> print(light_array["layout"])
            {'rows': 3, 'cols': 4, 'total_lights': 12}
        """
        lights = self.get_environment_lights()

        if light_id not in lights:
            available = list(lights.keys())
            raise ValueError(
                f"環境燈光不存在: {light_id}\n"
                f"環境: {self.env_name}\n"
                f"可用燈光: {', '.join(available) if available else '無'}"
            )

        return copy.deepcopy(lights[light_id])

    def get_connection_config(self) -> Dict[str, Any]:
        """取得連接配置

        Returns:
            dict: 連接配置，包含 socket 和 serial 配置

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> conn = loader.get_connection_config()
            >>> print(conn["socket"]["host"])
            '10.42.0.180'
            >>> print(conn["serial"]["port"])
            '/dev/ttyTHS1'
        """
        if self._yaml_config is None:
            return {}

        return copy.deepcopy(self._yaml_config.get("connection", {}))

    def get_defaults(self) -> Dict[str, Any]:
        """取得預設參數

        Returns:
            dict: 預設參數，包含 speed、press_duration 等

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> defaults = loader.get_defaults()
            >>> print(defaults["speed"])
            100
            >>> print(defaults["press_duration"])
            1.0
        """
        if self._yaml_config is None:
            return {}

        return copy.deepcopy(self._yaml_config.get("defaults", {}))

    def get_metadata(self) -> Dict[str, Any]:
        """取得配置元資料

        Returns:
            dict: 元資料，包含 version、total_buttons 等

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> metadata = loader.get_metadata()
            >>> print(metadata["version"])
            '4.1.0'
            >>> print(metadata["total_buttons"])
            13
        """
        if self._yaml_config is None:
            return {}

        return copy.deepcopy(self._yaml_config.get("metadata", {}))

    def list_button_ids(self) -> List[str]:
        """列出所有按鈕 ID

        Returns:
            list[str]: 按鈕 ID 列表

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> button_ids = loader.list_button_ids()
            >>> print(button_ids[:3])
            ['light1', 'light2', 'light3']
        """
        buttons = self.get_buttons()
        return list(buttons.keys())

    def list_environment_light_ids(self) -> List[str]:
        """列出所有環境燈光 ID

        Returns:
            list[str]: 燈光 ID 列表

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> light_ids = loader.list_environment_light_ids()
            >>> print(light_ids)
            ['light_array']
        """
        lights = self.get_environment_lights()
        return list(lights.keys())

    def get_button_by_type(self, button_type: str) -> Dict[str, Dict[str, Any]]:
        """根據類型篩選按鈕

        Args:
            button_type: 按鈕類型（panel_light, control, rv_control, observe_position）

        Returns:
            dict: 符合類型的按鈕配置字典

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> panel_lights = loader.get_button_by_type("panel_light")
            >>> print(len(panel_lights))
            8
        """
        buttons = self.get_buttons()
        filtered = {
            btn_id: btn_config
            for btn_id, btn_config in buttons.items()
            if btn_config.get("type") == button_type
        }
        return filtered

    def reload(self) -> None:
        """重新載入配置

        清除快取並重新從檔案載入配置。

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> # 修改 YAML 檔案後...
            >>> loader.reload()
        """
        # 清除快取
        if self.env_name in ConfigLoader._cache:
            del ConfigLoader._cache[self.env_name]

        # 重新載入
        self._load_yaml_config()
        logger.info(f"配置已重新載入: {self.env_name}")

    @staticmethod
    def clear_cache() -> None:
        """清除所有快取

        Example:
            >>> ConfigLoader.clear_cache()
        """
        ConfigLoader._cache.clear()
        logger.info("所有配置快取已清除")

    def get_full_config(self) -> Dict[str, Any]:
        """取得完整配置（包含 EnvironmentConfig 和 YAML 配置）

        Returns:
            dict: 完整配置，包含：
                - environment: 環境資訊
                - env_config: EnvironmentConfig 配置
                - buttons: 按鈕配置
                - environment_lights: 環境燈光配置
                - connection: 連接配置
                - defaults: 預設參數
                - metadata: 元資料

        Example:
            >>> loader = ConfigLoader("taipei_lab")
            >>> config = loader.get_full_config()
            >>> print(config.keys())
            dict_keys(['environment', 'env_config', 'buttons', 'environment_lights', 'connection', 'defaults', 'metadata'])
        """
        return {
            "environment": self._yaml_config.get("environment", {}) if self._yaml_config else {},
            "env_config": self._env_config,
            "buttons": self.get_buttons(),
            "environment_lights": self.get_environment_lights(),
            "connection": self.get_connection_config(),
            "defaults": self.get_defaults(),
            "metadata": self.get_metadata()
        }

    def __repr__(self) -> str:
        """字串表示

        Returns:
            str: ConfigLoader 的字串表示
        """
        button_count = len(self.get_buttons())
        light_count = len(self.get_environment_lights())
        return (
            f"ConfigLoader(env='{self.env_name}', "
            f"buttons={button_count}, lights={light_count})"
        )


if __name__ == "__main__":
    # 簡單測試
    print("=== 測試 ConfigLoader v1.0.0 ===\n")

    # 測試所有環境
    for env_name in EnvironmentConfig.list_environments():
        try:
            print(f"載入環境: {env_name}")
            loader = ConfigLoader(env_name)

            # 基本資訊
            print(f"  {loader}")

            # 按鈕資訊
            buttons = loader.get_buttons()
            print(f"  按鈕數量: {len(buttons)}")
            if buttons:
                first_btn_id = list(buttons.keys())[0]
                first_btn = loader.get_button(first_btn_id)
                print(f"    第一個按鈕: {first_btn_id} - {first_btn['name']}")

            # 環境燈光資訊
            lights = loader.get_environment_lights()
            print(f"  環境燈光數量: {len(lights)}")
            if lights:
                first_light_id = list(lights.keys())[0]
                first_light = loader.get_environment_light(first_light_id)
                print(f"    第一個燈光: {first_light_id} - {first_light['name']}")

            # 連接配置
            conn = loader.get_connection_config()
            print(f"  Socket: {conn['socket']['host']}:{conn['socket']['port']}")

            # 元資料
            metadata = loader.get_metadata()
            if metadata:
                print(f"  版本: {metadata.get('version', 'N/A')}")

            print()

        except FileNotFoundError as e:
            print(f"  ⚠️ 配置檔案不存在: {e}")
            print()

    # 測試按鈕類型篩選
    print("=" * 50)
    print("\n=== 測試按鈕類型篩選 ===\n")

    taipei_loader = ConfigLoader("taipei_lab")
    panel_lights = taipei_loader.get_button_by_type("panel_light")
    print(f"taipei_lab 面板燈光按鈕: {len(panel_lights)} 個")
    for btn_id, btn in list(panel_lights.items())[:3]:
        print(f"  - {btn_id}: {btn['name']}")

    print("\n" + "=" * 50)
    print("✅ ConfigLoader v1.0.0 測試通過")
