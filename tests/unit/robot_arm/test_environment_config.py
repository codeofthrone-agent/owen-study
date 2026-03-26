"""
測試 EnvironmentConfig 類別

測試範圍:
- 環境配置取得
- 環境驗證
- 環境列表
- 錯誤處理

作者: Robot Automation Team
日期: 2025-11-17
"""

import pytest
from config.robot_arm.environment_config import EnvironmentConfig


class TestEnvironmentConfig:
    """測試 EnvironmentConfig 基礎功能"""

    def test_list_environments(self):
        """測試列出所有環境"""
        environments = EnvironmentConfig.list_environments()

        assert isinstance(environments, list)
        assert len(environments) == 3
        assert "taipei_lab" in environments
        assert "taoyuan_lab" in environments
        assert "rv_car" in environments

    def test_validate_environment_valid(self):
        """測試驗證有效環境"""
        assert EnvironmentConfig.validate_environment("taipei_lab") is True
        assert EnvironmentConfig.validate_environment("taoyuan_lab") is True
        assert EnvironmentConfig.validate_environment("rv_car") is True

    def test_validate_environment_invalid(self):
        """測試驗證無效環境"""
        assert EnvironmentConfig.validate_environment("unknown") is False
        assert EnvironmentConfig.validate_environment("") is False
        assert EnvironmentConfig.validate_environment("tokyo_lab") is False

    def test_get_taipei_lab_environment(self):
        """測試取得台北實驗室環境配置"""
        config = EnvironmentConfig.get_environment("taipei_lab")

        assert isinstance(config, dict)
        assert config["name"] == "台北實驗室"
        assert config["image_source"] == "mixed"  # ✨ v4.1.0: 支援混合模式
        # cameras 列表現在是空的，因為改由 ipcam_config.yaml 動態載入
        # assert len(config["cameras"]) == 3 
        assert config["robot_arm_host"] == "10.42.0.180"
        assert config["robot_arm_port"] == 9000
        assert "panel_types" in config
        assert "3510a" in config["panel_types"]
        assert "3611a" in config["panel_types"]
        assert "3611c" in config["panel_types"]
        assert config["button_config_path"] == "config/robot_arm/taipei_lab_buttons.yaml"

    def test_get_taoyuan_lab_environment(self):
        """測試取得桃園實驗室環境配置"""
        config = EnvironmentConfig.get_environment("taoyuan_lab")

        assert isinstance(config, dict)
        assert config["name"] == "桃園實驗室"
        assert config["image_source"] == "http"
        assert config["robot_arm_host"] == "192.168.1.100"
        assert config["robot_arm_port"] == 9000
        assert "panel_types" in config
        assert "3510a" in config["panel_types"]
        assert "3611a" in config["panel_types"]
        assert config["button_config_path"] == "config/robot_arm/taoyuan_lab_buttons.yaml"

    def test_get_rv_car_environment(self):
        """測試取得 RV Car 環境配置"""
        config = EnvironmentConfig.get_environment("rv_car")

        assert isinstance(config, dict)
        assert config["name"] == "RV Car 測試環境"
        assert config["image_source"] == "http"
        assert config["robot_arm_host"] == "10.42.0.180"
        assert config["robot_arm_port"] == 9000
        assert "panel_types" in config
        assert "3611c" in config["panel_types"]
        assert config["button_config_path"] == "config/robot_arm/rv_car_buttons.yaml"

    def test_image_source_values(self):
        """測試影像源值是否正確"""
        valid_sources = ["rtsp", "socket", "mixed", "http"]  # ✨ v4.1.0: 新增 mixed 模式

        for env_name in EnvironmentConfig.list_environments():
            config = EnvironmentConfig.get_environment(env_name)
            assert config["image_source"] in valid_sources

    def test_get_image_source_config_for_rtsp(self):
        """測試取得 RTSP 影像源配置"""
        config = EnvironmentConfig.get_environment("taipei_lab")

        # ✨ v4.1.0: 台北實驗室使用混合模式（RTSP + Socket）
        assert config["image_source"] == "mixed"
        # 驗證透過 get_cameras 能取得相機列表
        cameras = EnvironmentConfig.get_cameras("taipei_lab")
        assert len(cameras) >= 3

    def test_get_image_source_config_for_socket(self):
        """測試取得 Socket 影像源配置"""
        config = EnvironmentConfig.get_environment("taoyuan_lab")

        # 桃園實驗室使用 HTTP
        assert config["image_source"] == "http"
        assert "robot_arm_host" in config
        assert "robot_arm_port" in config

    def test_get_image_source_config_socket(self):
        """測試取得 Socket 影像源配置（可用於 ImageSourceManager）"""
        config = EnvironmentConfig.get_image_source_config("taoyuan_lab")

        assert config["type"] == "http"
        assert "host" in config
        assert "port" in config
        assert config["port"] == 8000 # Default HTTP port
        assert "num_frames" in config
        assert config["num_frames"] == 5

    def test_get_image_source_config_rv_car(self):
        """測試取得 RV Car 影像源配置"""
        config = EnvironmentConfig.get_image_source_config("rv_car")

        assert config["type"] == "http"
        assert config["host"] == "10.42.0.180"
        assert config["port"] == 8000
