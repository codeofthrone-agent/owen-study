"""
影像源管理器 (Image Source Manager)

功能:
- 管理雙影像源 (RTSP / Socket)
- 提供統一的影像擷取介面
- 支援影像源切換
- 支援多幀平均擷取

作者: Robot Automation Team
日期: 2025-11-17
版本: v4.2.0
"""

import sys
from pathlib import Path
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger

# 確保可以匯入 image_sources 模組
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


class ImageSourceManager:
    """影像源管理器

    職責:
    - 統一管理雙影像源（RTSP / Socket）
    - 提供統一的影像擷取介面
    - 支援多幀平均截圖
    - 影像源切換與配置驗證

    支援的影像源:
    - RTSP: 遠端 IP Camera（rtsp://...）
    - Socket: MyCobot 280 Jetson Nano USB Camera（透過 Socket 傳輸）
    - HTTP: MyCobot 280 Jetson Nano USB Camera（透過 HTTP API 傳輸，v4.2.0 新增）

    Attributes:
        rtsp_source: RTSP 影像源實例（Phase 1.4 實作）
        socket_source: Socket 影像源實例（Phase 1.5 實作）
        current_source (str): 當前使用的影像源類型 ('rtsp' | 'socket' | None)
        current_config (dict): 當前影像源的配置

    Example:
        >>> manager = ImageSourceManager()
        >>>
        >>> # 設定 RTSP 影像源
        >>> manager.set_image_source("rtsp", {
        ...     "url": "rtsp://10.42.0.100:554/stream1",
        ...     "timeout": 10
        ... })
        >>>
        >>> # 設定 Socket 影像源
        >>> manager.set_image_source("socket", {
        ...     "host": "10.42.0.180",
        ...     "port": 9000
        ... })
        >>>
        >>> # 設定 HTTP 影像源 (v4.2.0)
        >>> manager.set_image_source("http", {
        ...     "host": "10.42.0.180",
        ...     "port": 8000
        ... })
        >>>
        >>> # 擷取單一影像（Phase 1.4-1.5 實作）
        >>> image = manager.capture_image()
        >>>
        >>> # 擷取多幀影像（多幀平均）
        >>> frames = manager.capture_multiple_frames(num_frames=5, warmup_frames=20)
    """

    def __init__(self, shared_socket=None):
        """初始化影像源管理器

        Args:
            shared_socket: 共用的 Socket 連接（來自 MyCobotSocketController）
                          用於 Socket 影像源，避免建立多個連接到同一 Server

        建立 RTSP 和 Socket 影像源的實例
        """
        # Phase 1.4 完成 - RTSPImageSource
        try:
            # 嘗試絕對匯入（作為模組）
            from libraries.robot_arm_control.image_sources.rtsp_source import RTSPImageSource
        except ImportError:
            try:
                # 嘗試相對匯入
                from .image_sources.rtsp_source import RTSPImageSource
            except ImportError:
                # 回退到直接匯入（當 sys.path 包含 libraries/robot_arm_control 時）
                from image_sources.rtsp_source import RTSPImageSource
        self.rtsp_source = RTSPImageSource()

        # Phase 1.5 完成 - SocketImageSource（支援共用 Socket）
        try:
            from libraries.robot_arm_control.image_sources.socket_image_source import SocketImageSource
        except ImportError:
            try:
                from .image_sources.socket_image_source import SocketImageSource
            except ImportError:
                from image_sources.socket_image_source import SocketImageSource
        self.socket_source = SocketImageSource(shared_socket=shared_socket)

        # Phase 3 完成 - HTTPImageSource (v4.2.0)
        try:
            from libraries.robot_arm_control.image_sources.http_image_source import HTTPImageSource
        except ImportError:
            try:
                from .image_sources.http_image_source import HTTPImageSource
            except ImportError:
                from image_sources.http_image_source import HTTPImageSource
        self.http_source = HTTPImageSource()

        # 當前使用的影像源
        self.current_source: Optional[str] = None
        self.current_config: Optional[Dict[str, Any]] = None

        logger.info(f"ImageSourceManager 初始化完成 (shared_socket={shared_socket is not None})")

    def set_image_source(self, source_type: str, source_config: Dict[str, Any]) -> None:
        """設定影像源

        Args:
            source_type: 影像源類型 ("rtsp" | "socket")
            source_config: 源配置字典
                - RTSP: {"url": "rtsp://...", "timeout": 10, "transport": "udp"}
                - Socket: {"host": "10.42.0.180", "port": 9000}
                - HTTP: {"host": "10.42.0.180", "port": 8000}

        Raises:
            ValueError: 不支援的影像源類型
            ValueError: 配置缺少必要欄位

        Example:
            >>> manager = ImageSourceManager()
            >>>
            >>> # 設定 RTSP
            >>> manager.set_image_source("rtsp", {
            ...     "url": "rtsp://10.42.0.100:554/stream1",
            ...     "timeout": 10
            ... })
            >>>
            >>> # 設定 Socket
            >>> manager.set_image_source("socket", {
            ...     "host": "10.42.0.180",
            ...     "port": 9000
            ... })
        """
        # 驗證影像源類型
        if source_type not in ["rtsp", "socket", "http"]:
            raise ValueError(f"不支援的影像源類型: {source_type}。支援的類型: 'rtsp', 'socket', 'http'")

        # 驗證配置完整性
        self._validate_source_config(source_type, source_config)

        # 設定當前影像源
        self.current_source = source_type
        self.current_config = source_config

        logger.info(f"影像源已設定為: {source_type}")
        logger.debug(f"配置: {source_config}")

    def _validate_source_config(self, source_type: str, source_config: Dict[str, Any]) -> None:
        """驗證影像源配置的完整性

        Args:
            source_type: 影像源類型
            source_config: 源配置字典

        Raises:
            ValueError: 配置缺少必要欄位
        """
        if source_type == "rtsp":
            if "url" not in source_config:
                raise ValueError("RTSP 配置必須包含 'url' 欄位")

        elif source_type == "socket":
            if "host" not in source_config or "port" not in source_config:
                raise ValueError("Socket 配置必須包含 'host' 和 'port' 欄位")

        elif source_type == "http":
            if "host" not in source_config or "port" not in source_config:
                raise ValueError("HTTP 配置必須包含 'host' 和 'port' 欄位")

    def get_current_source(self) -> Optional[Dict[str, Any]]:
        """取得當前影像源資訊

        Returns:
            dict: 包含 type 和 config 的字典，如果未設定則返回 None
                {
                    "type": "rtsp" | "socket",
                    "config": {...}
                }

        Example:
            >>> manager = ImageSourceManager()
            >>> manager.set_image_source("rtsp", {"url": "rtsp://..."})
            >>> current = manager.get_current_source()
            >>> print(current["type"])
            'rtsp'
        """
        if self.current_source is None:
            return None

        return {
            "type": self.current_source,
            "config": self.current_config
        }

    def capture_image(self) -> np.ndarray:
        """擷取單一影像（統一介面）

        根據當前設定的影像源類型，呼叫對應的影像源進行擷取。

        Returns:
            np.ndarray: BGR 格式的影像

        Raises:
            RuntimeError: 尚未設定影像源
            RuntimeError: 影像擷取失敗

        Example:
            >>> manager = ImageSourceManager()
            >>> manager.set_image_source("rtsp", {"url": "rtsp://..."})
            >>> image = manager.capture_image()
            >>> print(image.shape)
            (480, 640, 3)

        Note:
            此方法將在 Phase 1.4-1.5 完整實作
        """
        if self.current_source is None:
            raise RuntimeError("尚未設定影像源，請先呼叫 set_image_source()")

        # Phase 1.4-1.5 實作實際的影像擷取
        if self.current_source == "rtsp":
            # Phase 1.4 完成 - RTSP 影像擷取
            url = self.current_config["url"]
            timeout = self.current_config.get("timeout", 10)
            transport = self.current_config.get("transport", "tcp")
            use_tcp = (transport.lower() != "udp")

            return self.rtsp_source.capture_frame(
                url=url,
                retry_attempts=3,
                retry_delay=2.0,
                frame_skip=3,
                use_tcp=use_tcp,
                timeout=timeout
            )

        elif self.current_source == "socket":
            # Phase 1.5 完成 - Socket 影像擷取
            host = self.current_config["host"]
            port = self.current_config["port"]
            num_frames = self.current_config.get("num_frames", 5)

            return self.socket_source.request_image(
                host=host,
                port=port,
                num_frames=num_frames,
                retry_attempts=3,
                retry_delay=2.0
            )

        elif self.current_source == "http":
            # Phase 3 完成 - HTTP 影像擷取
            host = self.current_config["host"]
            port = self.current_config["port"]
            num_frames = self.current_config.get("num_frames", 5)

            return self.http_source.request_image(
                host=host,
                port=port,
                num_frames=num_frames,
                retry_attempts=3,
                retry_delay=1.0
            )

    def capture_multiple_frames(
        self,
        num_frames: int = 5,
        warmup_frames: int = 20
    ) -> List[np.ndarray]:
        """擷取多幀影像（用於多幀平均）

        Args:
            num_frames: 要擷取的幀數（預設 5）
            warmup_frames: 預熱幀數，會先丟棄這些幀（預設 20）

        Returns:
            list[np.ndarray]: 影像列表

        Raises:
            RuntimeError: 尚未設定影像源
            RuntimeError: 影像擷取失敗

        Example:
            >>> manager = ImageSourceManager()
            >>> manager.set_image_source("rtsp", {"url": "rtsp://..."})
            >>> frames = manager.capture_multiple_frames(num_frames=5, warmup_frames=20)
            >>> print(len(frames))
            5

        Note:
            此方法將在 Phase 1.4-1.5 完整實作
            預熱幀數用於解決 LED PWM 同步問題
        """
        if self.current_source is None:
            raise RuntimeError("尚未設定影像源，請先呼叫 set_image_source()")

        # Phase 1.4-1.5 實作實際的多幀擷取
        if self.current_source == "rtsp":
            # Phase 1.4 完成 - RTSP 多幀擷取
            url = self.current_config["url"]
            timeout = self.current_config.get("timeout", 10)
            transport = self.current_config.get("transport", "tcp")
            use_tcp = (transport.lower() != "udp")

            return self.rtsp_source.capture_multiple_frames(
                url=url,
                num_frames=num_frames,
                warmup_frames=warmup_frames,
                retry_attempts=3,
                retry_delay=2.0,
                use_tcp=use_tcp,
                timeout=timeout
            )

        elif self.current_source == "socket":
            # Phase 1.5 完成 - Socket 多幀擷取
            host = self.current_config["host"]
            port = self.current_config["port"]
            num_frames_per_image = self.current_config.get("num_frames", 5)

            return self.socket_source.request_multiple_images(
                host=host,
                port=port,
                num_images=num_frames,
                num_frames_per_image=num_frames_per_image,
                retry_attempts=3,
                retry_delay=2.0
            )

        elif self.current_source == "http":
            # Phase 3 完成 - HTTP 多幀擷取
            host = self.current_config["host"]
            port = self.current_config["port"]
            num_frames_per_image = self.current_config.get("num_frames", 5)

            return self.http_source.request_multiple_images(
                host=host,
                port=port,
                num_images=num_frames,
                num_frames_per_image=num_frames_per_image,
                retry_attempts=3,
                retry_delay=1.0
            )


if __name__ == "__main__":
    # 簡單測試
    manager = ImageSourceManager()

    # 測試 RTSP 設定
    manager.set_image_source("rtsp", {
        "url": "rtsp://10.42.0.100:554/stream1",
        "timeout": 10
    })
    print(f"當前影像源: {manager.get_current_source()}")

    # 測試 Socket 設定
    manager.set_image_source("socket", {
        "host": "10.42.0.180",
        "port": 9000
    })
    print(f"當前影像源: {manager.get_current_source()}")

    print("✅ ImageSourceManager 基礎功能測試通過")
