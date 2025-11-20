"""
HTTP Image Source (v4.2.0)

功能:
- 透過 HTTP API 從 Robot Arm Server 獲取影像
- 支援單張影像截取 (GET /api/v1/capture)
- 支援多張影像截取 (GET /api/v1/capture/multiple)
- 自動處理 Base64 解碼與 OpenCV 格式轉換

作者: Robot Automation Team
日期: 2025-11-19
版本: v4.2.0
"""

import requests
import cv2
import numpy as np
import base64
import time
from typing import Optional, List, Dict, Any
from loguru import logger

class HTTPImageSource:
    """HTTP 影像源客戶端

    負責與 Robot Arm Server 的 HTTP API 進行通訊，獲取影像數據。
    """

    def __init__(self):
        """初始化 HTTP 影像源"""
        self.session = requests.Session()
        logger.info("HTTPImageSource initialized")

    def request_image(
        self,
        host: str,
        port: int,
        num_frames: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[np.ndarray]:
        """請求單張影像 (GET /api/v1/capture)

        Args:
            host: Server IP
            port: Server Port (default: 8000)
            num_frames: 多幀平均數量 (default: 5)
            retry_attempts: 重試次數
            retry_delay: 重試間隔 (秒)

        Returns:
            np.ndarray: BGR 影像數據，失敗則返回 None
        """
        url = f"http://{host}:{port}/api/v1/capture"
        params = {
            "num_frames": num_frames,
            "format": "jpeg"
        }

        for attempt in range(retry_attempts):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status") != "success":
                    raise ValueError(f"Server returned error: {data.get('message')}")

                image_base64 = data.get("image_base64")
                if not image_base64:
                    raise ValueError("No image data received")

                # Decode Base64 to image
                image_data = base64.b64decode(image_base64)
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image is None:
                    raise ValueError("Failed to decode image")

                return image

            except Exception as e:
                logger.warning(f"HTTP capture failed (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)

        logger.error("All HTTP capture attempts failed")
        return None

    def request_multiple_images(
        self,
        host: str,
        port: int,
        num_images: int = 5,
        num_frames_per_image: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ) -> List[np.ndarray]:
        """請求多張影像 (GET /api/v1/capture/multiple)

        Args:
            host: Server IP
            port: Server Port (default: 8000)
            num_images: 需要的影像數量
            num_frames_per_image: 每張影像的多幀平均數量
            retry_attempts: 重試次數
            retry_delay: 重試間隔 (秒)

        Returns:
            List[np.ndarray]: 影像列表，失敗則返回空列表
        """
        url = f"http://{host}:{port}/api/v1/capture/multiple"
        params = {
            "count": num_images,
            "num_frames": num_frames_per_image,
            "format": "jpeg"
        }

        for attempt in range(retry_attempts):
            try:
                response = self.session.get(url, params=params, timeout=30) # Longer timeout for multiple images
                response.raise_for_status()

                data = response.json()
                if data.get("status") != "success":
                    raise ValueError(f"Server returned error: {data.get('message')}")

                images_base64 = data.get("images", [])
                if not images_base64:
                    raise ValueError("No image list received")

                images = []
                for b64_str in images_base64:
                    image_data = base64.b64decode(b64_str)
                    nparr = np.frombuffer(image_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is not None:
                        images.append(img)
                    else:
                        logger.warning("Failed to decode one of the images")

                if len(images) != num_images:
                    logger.warning(f"Expected {num_images} images, got {len(images)}")

                return images

            except Exception as e:
                logger.warning(f"HTTP multiple capture failed (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)

        logger.error("All HTTP multiple capture attempts failed")
        return []
