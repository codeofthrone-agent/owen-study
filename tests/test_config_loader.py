"""
ConfigLoader 單元測試

測試 ConfigLoader 的核心功能：
- YAML 配置載入
- 按鈕配置存取
- 環境燈光配置存取
- 快取機制
- 錯誤處理

作者: Robot Automation Team
日期: 2025-11-18
版本: v1.0.0
"""

import pytest
from config.robot_arm.config_loader import ConfigLoader
from config.robot_arm.environment_config import EnvironmentConfig


class TestConfigLoader:
    """ConfigLoader 測試類別"""

    def test_init_valid_environment(self):
        """測試：初始化有效環境"""
        loader = ConfigLoader("taipei_lab")
        assert loader.env_name == "taipei_lab"
        assert loader._env_config is not None
        assert loader._yaml_config is not None

    def test_init_invalid_environment(self):
        """測試：初始化無效環境應拋出 ValueError"""
        with pytest.raises(ValueError, match="未知環境"):
            ConfigLoader("invalid_env")

    def test_get_buttons_taipei_lab(self):
        """測試：取得台北實驗室按鈕配置"""
        loader = ConfigLoader("taipei_lab")
        buttons = loader.get_buttons()

        assert isinstance(buttons, dict)
        assert len(buttons) == 13
        assert "light1" in buttons
        assert "light2" in buttons
        assert "bluetooth" in buttons

    def test_get_button_valid(self):
        """測試：取得特定按鈕配置"""
        loader = ConfigLoader("taipei_lab")
        light1 = loader.get_button("light1")

        assert isinstance(light1, dict)
        assert light1["name"] == "Light1 按鈕"
        assert light1["type"] == "panel_light"
        assert "down_angles" in light1
        assert "up_angles" in light1
        assert "vision" in light1

    def test_get_button_invalid(self):
        """測試：取得不存在的按鈕應拋出 ValueError"""
        loader = ConfigLoader("taipei_lab")
        with pytest.raises(ValueError, match="按鈕不存在"):
            loader.get_button("invalid_button")

    def test_get_environment_lights_taipei_lab(self):
        """測試：取得台北實驗室環境燈光配置"""
        loader = ConfigLoader("taipei_lab")
        lights = loader.get_environment_lights()

        assert isinstance(lights, dict)
        assert len(lights) == 31
        assert "level1_light_1" in lights

    def test_get_environment_light_valid(self):
        """測試：取得特定環境燈光配置"""
        loader = ConfigLoader("taipei_lab")
        light_config = loader.get_environment_light("level1_light_1")

        assert isinstance(light_config, dict)
        assert light_config["type"] == "single_light"
        assert light_config["camera_id"] == "level1"
        assert "roi" in light_config

    def test_get_environment_light_invalid(self):
        """測試：取得不存在的環境燈光應拋出 ValueError"""
        loader = ConfigLoader("taipei_lab")
        with pytest.raises(ValueError, match="環境燈光不存在"):
            loader.get_environment_light("invalid_light")

    def test_get_connection_config(self):
        """測試：取得連接配置"""
        loader = ConfigLoader("taipei_lab")
        conn = loader.get_connection_config()

        assert isinstance(conn, dict)
        assert "socket" in conn
        assert "serial" in conn
        assert conn["socket"]["host"] == "10.42.0.180"
        assert conn["socket"]["port"] == 9000

    def test_get_defaults(self):
        """測試：取得預設參數"""
        loader = ConfigLoader("taipei_lab")
        defaults = loader.get_defaults()

        assert isinstance(defaults, dict)
        assert defaults["speed"] == 100
        assert defaults["press_duration"] == 1.0
        assert defaults["lift_duration"] == 0.1
        assert defaults["count"] == 1

    def test_get_metadata(self):
        """測試：取得元資料"""
        loader = ConfigLoader("taipei_lab")
        metadata = loader.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["version"] == "4.2.0"
        assert metadata["total_buttons"] == 13
        assert metadata["total_environment_lights"] == 31

    def test_list_button_ids(self):
        """測試：列出所有按鈕 ID"""
        loader = ConfigLoader("taipei_lab")
        button_ids = loader.list_button_ids()

        assert isinstance(button_ids, list)
        assert len(button_ids) == 13
        assert "light1" in button_ids
        assert "bluetooth" in button_ids

    def test_list_environment_light_ids(self):
        """測試：列出所有環境燈光 ID"""
        loader = ConfigLoader("taipei_lab")
        light_ids = loader.list_environment_light_ids()

        assert isinstance(light_ids, list)
        assert len(light_ids) == 31
        assert "level1_light_1" in light_ids

    def test_get_button_by_type_panel_light(self):
        """測試：根據類型篩選按鈕（面板燈光）"""
        loader = ConfigLoader("taipei_lab")
        panel_lights = loader.get_button_by_type("panel_light")

        assert isinstance(panel_lights, dict)
        assert len(panel_lights) == 8
        assert all(btn["type"] == "panel_light" for btn in panel_lights.values())

    def test_get_button_by_type_control(self):
        """測試：根據類型篩選按鈕（控制按鈕）"""
        loader = ConfigLoader("taipei_lab")
        control_buttons = loader.get_button_by_type("control")

        assert isinstance(control_buttons, dict)
        assert len(control_buttons) == 5
        assert all(btn["type"] == "control" for btn in control_buttons.values())

    def test_get_full_config(self):
        """測試：取得完整配置"""
        loader = ConfigLoader("taipei_lab")
        config = loader.get_full_config()

        assert isinstance(config, dict)
        assert "environment" in config
        assert "env_config" in config
        assert "buttons" in config
        assert "environment_lights" in config
        assert "connection" in config
        assert "defaults" in config
        assert "metadata" in config

    def test_cache_mechanism(self):
        """測試：快取機制"""
        # 清除快取
        ConfigLoader.clear_cache()

        # 第一次載入
        loader1 = ConfigLoader("taipei_lab")
        assert "taipei_lab" in ConfigLoader._cache

        # 第二次載入（應從快取載入）
        loader2 = ConfigLoader("taipei_lab")
        assert loader1._yaml_config == loader2._yaml_config

    def test_reload(self):
        """測試：重新載入配置"""
        loader = ConfigLoader("taipei_lab")

        # 重新載入
        loader.reload()

        # 驗證配置仍然正確
        buttons = loader.get_buttons()
        assert len(buttons) == 13

    def test_rv_car_buttons(self):
        """測試：RV Car 按鈕配置"""
        loader = ConfigLoader("rv_car")
        buttons = loader.get_buttons()

        assert len(buttons) == 7
        assert "hvac" in buttons
        assert "water_pump" in buttons

    def test_rv_car_environment_lights(self):
        """測試：RV Car 環境燈光配置"""
        loader = ConfigLoader("rv_car")
        lights = loader.get_environment_lights()

        assert len(lights) == 13
        assert "area1_light_1" in lights

    def test_taoyuan_lab_empty(self):
        """測試：桃園實驗室（空配置）"""
        loader = ConfigLoader("taoyuan_lab")
        buttons = loader.get_buttons()
        lights = loader.get_environment_lights()

        assert len(buttons) == 0
        assert len(lights) == 0

    def test_deep_copy_protection(self):
        """測試：深拷貝保護（避免外部修改影響原始配置）"""
        loader = ConfigLoader("taipei_lab")

        # 取得按鈕配置並修改
        buttons1 = loader.get_buttons()
        buttons1["light1"]["name"] = "Modified Name"

        # 再次取得，應該是原始值
        buttons2 = loader.get_buttons()
        assert buttons2["light1"]["name"] == "Light1 按鈕"

    def test_repr(self):
        """測試：字串表示"""
        loader = ConfigLoader("taipei_lab")
        repr_str = repr(loader)

        assert "ConfigLoader" in repr_str
        assert "taipei_lab" in repr_str
        assert "buttons=13" in repr_str
        assert "lights=31" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
