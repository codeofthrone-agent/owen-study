"""
Unit tests for ImageSourceManager (影像源管理器)

遵循 TDD 原則開發：
1. Red - 寫失敗的測試
2. Green - 實作最小程度的程式碼讓測試通過
3. Refactor - 重構程式碼

測試範圍：
- Phase 1.3: ImageSourceManager 基礎功能
- 影像源設定與切換
- 影像擷取統一介面
"""

import pytest
import numpy as np
from typing import Optional


class TestImageSourceManagerInitialization:
    """測試 ImageSourceManager 初始化功能"""

    def test_manager_can_be_initialized(self):
        """測試：ImageSourceManager 應該可以被初始化

        Given 沒有提供任何參數
        When 初始化 ImageSourceManager
        Then 應該成功建立實例
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        assert manager is not None
        assert isinstance(manager, ImageSourceManager)

    def test_manager_has_current_source_attribute(self):
        """測試：ImageSourceManager 應該有 current_source 屬性

        Given ImageSourceManager 已初始化
        When 存取 current_source 屬性
        Then 初始值應該是 None
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        assert hasattr(manager, 'current_source')
        assert manager.current_source is None

    def test_manager_has_current_config_attribute(self):
        """測試：ImageSourceManager 應該有 current_config 屬性

        Given ImageSourceManager 已初始化
        When 存取 current_config 屬性
        Then 初始值應該是 None
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        assert hasattr(manager, 'current_config')
        assert manager.current_config is None


class TestSetImageSource:
    """測試設定影像源功能"""

    def test_set_rtsp_source_should_succeed(self, mock_rtsp_url):
        """測試：設定 RTSP 影像源應該成功

        Given ImageSourceManager 已初始化
        When 設定 RTSP 影像源
        Then 應該成功設定
        And current_source 應該是 'rtsp'
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        source_config = {
            "url": mock_rtsp_url,
            "timeout": 10
        }

        manager.set_image_source("rtsp", source_config)

        assert manager.current_source == "rtsp"
        assert manager.current_config == source_config

    def test_set_socket_source_should_succeed(self, mock_socket_config):
        """測試：設定 Socket 影像源應該成功

        Given ImageSourceManager 已初始化
        When 設定 Socket 影像源
        Then 應該成功設定
        And current_source 應該是 'socket'
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        manager.set_image_source("socket", mock_socket_config)

        assert manager.current_source == "socket"
        assert manager.current_config == mock_socket_config

    def test_set_invalid_source_should_raise_error(self):
        """測試：設定無效的影像源應該拋出錯誤

        Given ImageSourceManager 已初始化
        When 設定不支援的影像源類型
        Then 應該拋出 ValueError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(ValueError, match="不支援的影像源類型"):
            manager.set_image_source("usb", {"device": "/dev/video0"})

    def test_switch_between_sources_should_succeed(self, mock_rtsp_url, mock_socket_config):
        """測試：在不同影像源之間切換應該成功

        Given ImageSourceManager 已設定為 RTSP
        When 切換到 Socket 影像源
        Then 應該成功切換
        And current_source 應該是 'socket'
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        # 先設定 RTSP
        manager.set_image_source("rtsp", {"url": mock_rtsp_url, "timeout": 10})
        assert manager.current_source == "rtsp"

        # 切換到 Socket
        manager.set_image_source("socket", mock_socket_config)
        assert manager.current_source == "socket"


class TestGetCurrentSource:
    """測試取得當前影像源功能"""

    def test_get_current_source_when_not_set(self):
        """測試：未設定影像源時取得當前源應該返回 None

        Given ImageSourceManager 已初始化
        And 尚未設定任何影像源
        When 呼叫 get_current_source
        Then 應該返回 None
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        current = manager.get_current_source()

        assert current is None

    def test_get_current_source_after_set_rtsp(self, mock_rtsp_url):
        """測試：設定 RTSP 後應該返回正確的影像源資訊

        Given ImageSourceManager 已設定為 RTSP
        When 呼叫 get_current_source
        Then 應該返回包含 type 和 config 的字典
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        source_config = {"url": mock_rtsp_url, "timeout": 10}
        manager.set_image_source("rtsp", source_config)

        current = manager.get_current_source()

        assert current is not None
        assert current["type"] == "rtsp"
        assert current["config"] == source_config

    def test_get_current_source_after_set_socket(self, mock_socket_config):
        """測試：設定 Socket 後應該返回正確的影像源資訊

        Given ImageSourceManager 已設定為 Socket
        When 呼叫 get_current_source
        Then 應該返回包含 type 和 config 的字典
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        manager.set_image_source("socket", mock_socket_config)

        current = manager.get_current_source()

        assert current is not None
        assert current["type"] == "socket"
        assert current["config"] == mock_socket_config


class TestCaptureImage:
    """測試影像擷取功能（統一介面）"""

    def test_capture_image_without_source_should_raise_error(self):
        """測試：未設定影像源時擷取影像應該拋出錯誤

        Given ImageSourceManager 已初始化
        And 尚未設定任何影像源
        When 呼叫 capture_image
        Then 應該拋出 RuntimeError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(RuntimeError, match="尚未設定影像源"):
            manager.capture_image()

    @pytest.mark.skip(reason="需要 RTSPImageSource 實作（Phase 1.4）")
    def test_capture_image_from_rtsp_should_return_image(self, mock_rtsp_url):
        """測試：從 RTSP 擷取影像應該返回 numpy array

        Given ImageSourceManager 已設定為 RTSP
        When 呼叫 capture_image
        Then 應該返回 numpy array 格式的影像
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        manager.set_image_source("rtsp", {"url": mock_rtsp_url, "timeout": 10})

        image = manager.capture_image()

        assert isinstance(image, np.ndarray)
        assert len(image.shape) == 3  # BGR 格式
        assert image.shape[2] == 3

    @pytest.mark.skip(reason="需要 SocketImageSource 實作（Phase 1.5）")
    def test_capture_image_from_socket_should_return_image(self, mock_socket_config):
        """測試：從 Socket 擷取影像應該返回 numpy array

        Given ImageSourceManager 已設定為 Socket
        When 呼叫 capture_image
        Then 應該返回 numpy array 格式的影像
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        manager.set_image_source("socket", mock_socket_config)

        image = manager.capture_image()

        assert isinstance(image, np.ndarray)
        assert len(image.shape) == 3  # BGR 格式
        assert image.shape[2] == 3


class TestCaptureMultipleFrames:
    """測試多幀擷取功能（多幀平均）"""

    def test_capture_multiple_frames_without_source_should_raise_error(self):
        """測試：未設定影像源時擷取多幀應該拋出錯誤

        Given ImageSourceManager 已初始化
        And 尚未設定任何影像源
        When 呼叫 capture_multiple_frames
        Then 應該拋出 RuntimeError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(RuntimeError, match="尚未設定影像源"):
            manager.capture_multiple_frames(num_frames=5)

    @pytest.mark.skip(reason="需要 RTSPImageSource 實作（Phase 1.4）")
    def test_capture_multiple_frames_should_return_list(self, mock_rtsp_url):
        """測試：擷取多幀應該返回影像列表

        Given ImageSourceManager 已設定為 RTSP
        When 呼叫 capture_multiple_frames(num_frames=5)
        Then 應該返回包含 5 張影像的列表
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        manager.set_image_source("rtsp", {"url": mock_rtsp_url, "timeout": 10})

        frames = manager.capture_multiple_frames(num_frames=5)

        assert isinstance(frames, list)
        assert len(frames) == 5
        for frame in frames:
            assert isinstance(frame, np.ndarray)
            assert len(frame.shape) == 3

    @pytest.mark.skip(reason="需要 RTSPImageSource 實作（Phase 1.4）")
    def test_capture_multiple_frames_with_warmup(self, mock_rtsp_url):
        """測試：擷取多幀時應該支援預熱幀數

        Given ImageSourceManager 已設定為 RTSP
        When 呼叫 capture_multiple_frames(num_frames=5, warmup_frames=20)
        Then 應該先丟棄 20 幀，再擷取 5 幀
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()
        manager.set_image_source("rtsp", {"url": mock_rtsp_url, "timeout": 10})

        frames = manager.capture_multiple_frames(num_frames=5, warmup_frames=20)

        assert isinstance(frames, list)
        assert len(frames) == 5


class TestImageSourceValidation:
    """測試影像源配置驗證"""

    def test_rtsp_config_missing_url_should_raise_error(self):
        """測試：RTSP 配置缺少 URL 應該拋出錯誤

        Given ImageSourceManager 已初始化
        When 設定 RTSP 但缺少 url 鍵
        Then 應該拋出 ValueError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(ValueError, match="RTSP 配置必須包含 'url'"):
            manager.set_image_source("rtsp", {"timeout": 10})

    def test_socket_config_missing_host_should_raise_error(self):
        """測試：Socket 配置缺少 host 應該拋出錯誤

        Given ImageSourceManager 已初始化
        When 設定 Socket 但缺少 host 鍵
        Then 應該拋出 ValueError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(ValueError, match="Socket 配置必須包含 'host' 和 'port'"):
            manager.set_image_source("socket", {"port": 9000})

    def test_socket_config_missing_port_should_raise_error(self):
        """測試：Socket 配置缺少 port 應該拋出錯誤

        Given ImageSourceManager 已初始化
        When 設定 Socket 但缺少 port 鍵
        Then 應該拋出 ValueError
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        with pytest.raises(ValueError, match="Socket 配置必須包含 'host' 和 'port'"):
            manager.set_image_source("socket", {"host": "10.42.0.180"})


class TestImageSourceIntegration:
    """測試影像源整合功能"""

    def test_manager_should_have_rtsp_source_instance(self):
        """測試：Manager 應該有 RTSPImageSource 實例

        Given ImageSourceManager 已初始化
        When 存取內部的影像源實例
        Then 應該有 rtsp_source 屬性
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        assert hasattr(manager, 'rtsp_source')
        # RTSPImageSource 將在 Phase 1.4 實作

    def test_manager_should_have_socket_source_instance(self):
        """測試：Manager 應該有 SocketImageSource 實例

        Given ImageSourceManager 已初始化
        When 存取內部的影像源實例
        Then 應該有 socket_source 屬性
        """
        from libraries.robot_arm_control.image_source_manager import ImageSourceManager

        manager = ImageSourceManager()

        assert hasattr(manager, 'socket_source')
        # SocketImageSource 將在 Phase 1.5 實作


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
