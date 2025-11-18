"""
Socket 影像源 (Socket Image Source)

功能:
- 從 MyCobot 280 Jetson Nano Server 擷取影像
- 透過 Socket 傳輸 (JSON 協議)
- 支援 Base64 影像編碼/解碼
- 支援多幀擷取（多幀平均）

作者: Robot Automation Team
日期: 2025-11-17
版本: v4.0.0

參考: scripts/robot_arm_server.py (_cmd_capture_image)
"""

import socket
import json
import base64
import time
import numpy as np
import cv2
from typing import List, Optional
from loguru import logger


class SocketImageSource:
    """Socket 影像源

    從 MyCobot 280 Jetson Nano Server (MycobotServer) 透過 Socket 擷取影像。

    支援功能:
    - Socket 連接管理
    - JSON 命令發送 (capture_image)
    - Base64 影像解碼
    - 自動重試機制
    - 多幀擷取支援

    Attributes:
        socket: Socket 連接實例
        host (str): Server 主機位址
        port (int): Server 端口
        timeout (float): Socket 超時時間（秒）
        last_image (np.ndarray): 最後擷取的影像

    Example:
        >>> source = SocketImageSource()
        >>> image = source.request_image("10.42.0.180", 9000)
        >>> print(image.shape)
        (480, 640, 3)
        >>>
        >>> # 多幀擷取
        >>> images = source.request_multiple_images(
        ...     "10.42.0.180", 9000,
        ...     num_images=5
        ... )
        >>> print(len(images))
        5
    """

    def __init__(self, shared_socket: Optional[socket.socket] = None):
        """初始化 Socket 影像源

        Args:
            shared_socket: 共用的 Socket 連接（來自 MyCobotSocketController）
                          如果提供，則直接使用此 Socket，不建立新連接
        """
        self.socket: Optional[socket.socket] = shared_socket
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.timeout: float = 30.0  # Socket 超時時間（與 Server 一致）
        self.last_image: Optional[np.ndarray] = None
        self.is_shared_socket: bool = shared_socket is not None  # 標記是否為共用 Socket

        logger.info(f"SocketImageSource 初始化完成 (shared_socket={shared_socket is not None})")

    def __del__(self):
        """清理資源"""
        self.disconnect()

    def disconnect(self) -> None:
        """斷開 Socket 連接

        Note:
            如果使用共用 Socket（is_shared_socket=True），則不會關閉連接，
            因為連接由外部管理（MyCobotSocketController）

        Example:
            >>> source = SocketImageSource()
            >>> source.disconnect()
        """
        if self.socket is not None and not self.is_shared_socket:
            # 只在非共用 Socket 時關閉
            try:
                self.socket.close()
                logger.debug("Socket 連接已關閉")
            except Exception as e:
                logger.warning(f"關閉 Socket 時發生錯誤: {e}")
            finally:
                self.socket = None
        elif self.is_shared_socket:
            logger.debug("使用共用 Socket，不關閉連接")

    def _connect(self, host: str, port: int) -> bool:
        """建立 Socket 連接

        Args:
            host: Server 主機位址
            port: Server 端口

        Returns:
            bool: 連接是否成功

        Raises:
            ConnectionError: 連接失敗
        """
        # 如果使用共用 Socket，直接返回（不建立新連接）
        if self.is_shared_socket:
            if self.socket is None:
                raise ConnectionError("共用 Socket 為 None，無法使用")
            logger.debug(f"使用共用 Socket 連接: {host}:{port}")
            self.host = host
            self.port = port
            return True

        # 如果已經連接到相同 host:port，直接返回
        if self.socket is not None and self.host == host and self.port == port:
            return True

        # 斷開舊連接
        self.disconnect()

        try:
            logger.debug(f"正在連接到 {host}:{port}")

            # 建立新的 Socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((host, port))

            self.host = host
            self.port = port

            logger.info(f"Socket 連接成功: {host}:{port}")
            return True

        except Exception as e:
            logger.error(f"Socket 連接失敗: {e}")
            self.disconnect()
            raise ConnectionError(f"無法連接到 {host}:{port}: {e}")

    def _send_json_command(self, command: dict) -> dict:
        """發送 JSON 命令到 Server

        Args:
            command: JSON 命令字典

        Returns:
            dict: Server 回應的 JSON 字典

        Raises:
            RuntimeError: 命令發送失敗或回應無效
        """
        try:
            # 發送 JSON 命令
            command_str = json.dumps(command)
            logger.debug(f"發送命令: {command}")

            self.socket.sendall(command_str.encode('utf-8'))

            # 接收回應（大型資料可能需要分批接收）
            response_data = b""
            while True:
                try:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk

                    # 嘗試解析 JSON，如果成功則接收完成
                    try:
                        response = json.loads(response_data.decode('utf-8'))
                        logger.debug(f"收到回應: status={response.get('status')}")
                        return response
                    except json.JSONDecodeError:
                        # 還沒接收完整，繼續接收
                        continue

                except socket.timeout:
                    # 超時，檢查是否已有完整資料
                    if response_data:
                        try:
                            response = json.loads(response_data.decode('utf-8'))
                            return response
                        except json.JSONDecodeError:
                            raise RuntimeError("接收 JSON 回應超時且資料不完整")
                    else:
                        raise RuntimeError("接收 JSON 回應超時")

            # 如果迴圈正常結束（連接關閉），解析最後的資料
            if response_data:
                response = json.loads(response_data.decode('utf-8'))
                return response
            else:
                raise RuntimeError("Server 關閉連接且無回應資料")

        except Exception as e:
            logger.error(f"JSON 命令發送失敗: {e}")
            raise RuntimeError(f"無法發送命令或接收回應: {e}")

    def _decode_base64_image(self, image_base64: str) -> np.ndarray:
        """解碼 Base64 影像為 numpy array

        Args:
            image_base64: Base64 編碼的影像字串

        Returns:
            np.ndarray: BGR 格式的影像

        Raises:
            RuntimeError: 解碼失敗
        """
        try:
            # Base64 解碼
            image_bytes = base64.b64decode(image_base64)

            # 轉換為 numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)

            # 解碼為 OpenCV 影像（BGR）
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                raise RuntimeError("cv2.imdecode 返回 None")

            return image

        except Exception as e:
            logger.error(f"Base64 影像解碼失敗: {e}")
            raise RuntimeError(f"無法解碼 Base64 影像: {e}")

    def request_image(
        self,
        host: str,
        port: int,
        num_frames: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        image_format: str = "jpeg"
    ) -> np.ndarray:
        """請求單一影像

        Args:
            host: Server 主機位址 (例如: "10.42.0.180")
            port: Server 端口 (例如: 9000)
            num_frames: Server 端多幀平均數量（預設 5）
            retry_attempts: 重試次數（預設 3）
            retry_delay: 重試延遲秒數（預設 2.0）
            image_format: 影像格式 ("jpeg" | "png")，預設 "jpeg"

        Returns:
            np.ndarray: BGR 格式的影像

        Raises:
            ConnectionError: 無法連接到 Server
            RuntimeError: 影像擷取失敗

        Example:
            >>> source = SocketImageSource()
            >>> image = source.request_image("10.42.0.180", 9000)
            >>> print(image.shape)
            (480, 640, 3)
        """
        for attempt in range(retry_attempts):
            try:
                # 連接到 Server
                if not self._connect(host, port):
                    raise ConnectionError("無法連接到 Server")

                logger.debug(f"請求影像 (嘗試 {attempt + 1}/{retry_attempts})")

                # 發送 capture_image 命令
                command = {
                    "command": "capture_image",
                    "num_frames": num_frames,
                    "format": image_format
                }

                response = self._send_json_command(command)

                # 檢查回應狀態
                if response.get("status") != "success":
                    error_msg = response.get("message", "未知錯誤")
                    raise RuntimeError(f"Server 回應錯誤: {error_msg}")

                # 解碼 Base64 影像
                image_base64 = response.get("image_base64")
                if not image_base64:
                    raise RuntimeError("Server 回應缺少 image_base64 欄位")

                image = self._decode_base64_image(image_base64)

                # 儲存影像
                self.last_image = image
                logger.info(f"成功擷取影像: {image.shape}")

                return image

            except Exception as e:
                logger.warning(f"請求影像失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")

                # 斷開連接
                self.disconnect()

                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"無法從 Socket 擷取影像: {e}")

        raise RuntimeError("請求影像失敗：已達最大重試次數")

    def request_multiple_images(
        self,
        host: str,
        port: int,
        num_images: int = 5,
        num_frames_per_image: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        image_format: str = "jpeg"
    ) -> List[np.ndarray]:
        """請求多張影像（用於多幀平均）

        Note:
            此方法會多次呼叫 request_image()，每次請求一張影像。
            每張影像本身已經是 Server 端的多幀平均結果（num_frames_per_image）。

        Args:
            host: Server 主機位址
            port: Server 端口
            num_images: 要請求的影像數量（預設 5）
            num_frames_per_image: 每張影像的 Server 端多幀平均數量（預設 5）
            retry_attempts: 重試次數（預設 3）
            retry_delay: 重試延遲秒數（預設 2.0）
            image_format: 影像格式 ("jpeg" | "png")，預設 "jpeg"

        Returns:
            list[np.ndarray]: 影像列表

        Raises:
            ConnectionError: 無法連接到 Server
            RuntimeError: 影像擷取失敗

        Example:
            >>> source = SocketImageSource()
            >>> images = source.request_multiple_images(
            ...     "10.42.0.180", 9000,
            ...     num_images=5,
            ...     num_frames_per_image=5
            ... )
            >>> print(len(images))
            5

        Note:
            由於每次請求都已經是多幀平均，不需要預熱階段。
            如果需要更穩定的結果，可以增加 num_frames_per_image。
        """
        images = []

        for i in range(num_images):
            try:
                logger.debug(f"請求第 {i+1}/{num_images} 張影像")

                image = self.request_image(
                    host=host,
                    port=port,
                    num_frames=num_frames_per_image,
                    retry_attempts=retry_attempts,
                    retry_delay=retry_delay,
                    image_format=image_format
                )

                images.append(image)

                # v4.1.1 新增：增加微小延遲避免 TCP 粘包
                time.sleep(0.05)

            except Exception as e:
                logger.error(f"擷取第 {i+1}/{num_images} 張影像失敗: {e}")
                raise RuntimeError(f"無法擷取多張影像: {e}")

        logger.info(f"成功擷取 {len(images)} 張影像: {images[0].shape}")
        return images


if __name__ == "__main__":
    # 簡單測試
    source = SocketImageSource()

    # 注意: 實際測試需要 MycobotServer 正在運行
    print("✅ SocketImageSource 基礎功能測試通過")
    print("⚠️  完整測試需要 MycobotServer 正在運行")
