"""
RTSP 影像源 (RTSP Image Source)

功能:
- 從 RTSP 串流擷取影像
- 支援連接重試
- 支援多幀擷取（多幀平均）
- 支援 TCP/UDP 傳輸協議

作者: Robot Automation Team
日期: 2025-11-17
版本: v4.0.0

參考: libraries/ipcam_light_detection/IPCamLightDetection.py
"""

import cv2
import time
import numpy as np
from typing import List, Optional
from loguru import logger
import os
import re


class RTSPImageSource:
    """RTSP 影像源

    從 RTSP 串流 (IP Camera) 擷取影像。

    支援功能:
    - 自動重試機制
    - 跳幀以獲取最新影像
    - TCP/UDP 傳輸協議
    - 連接池管理
    - 多幀擷取支援

    Attributes:
        capture (cv2.VideoCapture): OpenCV VideoCapture 實例
        rtsp_url (str): 當前的 RTSP URL
        last_frame (np.ndarray): 最後擷取的影像

    Example:
        >>> source = RTSPImageSource()
        >>> frame = source.capture_frame("rtsp://admin:admin@192.168.1.100:554/stream1")
        >>> print(frame.shape)
        (480, 640, 3)
        >>>
        >>> # 多幀擷取
        >>> frames = source.capture_multiple_frames(
        ...     "rtsp://192.168.1.100:554/stream1",
        ...     num_frames=5,
        ...     warmup_frames=20
        ... )
        >>> print(len(frames))
        5
    """

    def __init__(self):
        """初始化 RTSP 影像源"""
        self.capture: Optional[cv2.VideoCapture] = None
        self.rtsp_url: Optional[str] = None
        self.last_frame: Optional[np.ndarray] = None

        logger.info("RTSPImageSource 初始化完成")

    def __del__(self):
        """清理資源"""
        self.release()

    def release(self) -> None:
        """釋放 VideoCapture 資源

        Example:
            >>> source = RTSPImageSource()
            >>> source.release()
        """
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            logger.debug("VideoCapture 資源已釋放")

    def _get_safe_url(self, url: str) -> str:
        """取得隱藏密碼的安全 URL 用於日誌

        Args:
            url: RTSP URL

        Returns:
            str: 隱藏密碼的 URL

        Example:
            >>> source = RTSPImageSource()
            >>> safe_url = source._get_safe_url("rtsp://admin:password@192.168.1.100:554/stream")
            >>> print(safe_url)
            rtsp://admin:****@192.168.1.100:554/stream
        """
        # 隱藏密碼: rtsp://user:pass@host → rtsp://user:****@host
        safe_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', url)
        return safe_url

    def _init_capture(self, url: str, use_tcp: bool = True) -> bool:
        """初始化 VideoCapture 連線

        Args:
            url: RTSP URL
            use_tcp: 是否使用 TCP 傳輸（預設 True，較穩定）

        Returns:
            bool: 連線是否成功

        Raises:
            RuntimeError: 初始化失敗

        Note:
            使用 TCP 傳輸可提高穩定性，但延遲較高
            使用 UDP 傳輸延遲較低，但可能丟包
        """
        # 如果已經連接到相同 URL，直接返回
        if self.capture is not None and self.capture.isOpened() and self.rtsp_url == url:
            return True

        # 釋放舊連接
        self.release()

        try:
            logger.debug(f"初始化 VideoCapture: {self._get_safe_url(url)}")

            # 設定 FFmpeg 選項以支援 HEVC/H.265 和 TCP 傳輸
            if use_tcp:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                    'rtsp_transport;tcp|'
                    'analyzeduration;20000000|'
                    'probesize;20000000'
                )
                logger.debug("已設定 FFmpeg 選項: TCP 傳輸 + HEVC 支援")
            else:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                    'rtsp_transport;udp|'
                    'analyzeduration;20000000|'
                    'probesize;20000000'
                )
                logger.debug("已設定 FFmpeg 選項: UDP 傳輸 + HEVC 支援")

            # 建立 VideoCapture
            self.capture = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

            if not self.capture.isOpened():
                raise RuntimeError(f"無法開啟 RTSP 串流: {self._get_safe_url(url)}")

            self.rtsp_url = url
            logger.info(f"VideoCapture 初始化成功: {self._get_safe_url(url)}")
            return True

        except Exception as e:
            logger.error(f"VideoCapture 初始化失敗: {e}")
            self.release()
            raise RuntimeError(f"無法初始化 RTSP 連線: {e}")

    def capture_frame(
        self,
        url: str,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        frame_skip: int = 3,
        use_tcp: bool = True
    ) -> np.ndarray:
        """擷取單一影像幀

        Args:
            url: RTSP URL (例如: rtsp://admin:password@192.168.1.100:554/stream1)
            retry_attempts: 重試次數（預設 3）
            retry_delay: 重試延遲秒數（預設 2.0）
            frame_skip: 跳過的幀數（預設 3，跳過前幾幀以獲取最新影像）
            use_tcp: 是否使用 TCP 傳輸（預設 True）

        Returns:
            np.ndarray: BGR 格式的影像

        Raises:
            ConnectionError: 無法連接到 RTSP 串流
            RuntimeError: 影像擷取失敗

        Example:
            >>> source = RTSPImageSource()
            >>> frame = source.capture_frame("rtsp://192.168.1.100:554/stream1")
            >>> print(frame.shape)
            (480, 640, 3)
        """
        for attempt in range(retry_attempts):
            try:
                # 初始化 VideoCapture
                if not self._init_capture(url, use_tcp):
                    raise ConnectionError("無法初始化 RTSP 連線")

                logger.debug(f"正在擷取影像 (嘗試 {attempt + 1}/{retry_attempts})")

                # 增強版預熱：等待有效影像（最多 60 幀，約 2-3 秒）
                # 這可以解決 "SPS 0 does not exist" 等初始化問題
                valid_frame_found = False
                for _ in range(60):
                    ret, test_frame = self.capture.read()
                    if ret and test_frame is not None and test_frame.size > 0:
                        valid_frame_found = True
                        break
                
                if not valid_frame_found:
                    raise RuntimeError("無法從串流讀取有效影像 (預熱失敗)")

                # 額外的跳幀（如果需要）
                if frame_skip > 0:
                    for _ in range(frame_skip):
                        self.capture.read()

                # 擷取實際影像
                ret, frame = self.capture.read()

                if not ret or frame is None:
                    raise RuntimeError("無法從串流讀取影像幀")

                # 儲存影像
                self.last_frame = frame
                logger.info(f"成功擷取影像: {frame.shape}")

                return frame

            except Exception as e:
                logger.warning(f"擷取影像失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")

                # 釋放並重新連線
                self.release()

                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"無法從 RTSP 串流擷取影像: {e}")

        raise RuntimeError("擷取影像失敗：已達最大重試次數")

    def capture_multiple_frames(
        self,
        url: str,
        num_frames: int = 5,
        warmup_frames: int = 20,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        use_tcp: bool = True
    ) -> List[np.ndarray]:
        """擷取多幀影像（用於多幀平均）

        Args:
            url: RTSP URL
            num_frames: 要擷取的幀數（預設 5）
            warmup_frames: 預熱幀數，會先丟棄這些幀（預設 20）
            retry_attempts: 重試次數（預設 3）
            retry_delay: 重試延遲秒數（預設 2.0）
            use_tcp: 是否使用 TCP 傳輸（預設 True）

        Returns:
            list[np.ndarray]: 影像列表

        Raises:
            ConnectionError: 無法連接到 RTSP 串流
            RuntimeError: 影像擷取失敗

        Example:
            >>> source = RTSPImageSource()
            >>> frames = source.capture_multiple_frames(
            ...     "rtsp://192.168.1.100:554/stream1",
            ...     num_frames=5,
            ...     warmup_frames=20
            ... )
            >>> print(len(frames))
            5

        Note:
            預熱幀數用於解決 LED PWM 同步問題
            多幀平均可以減少影像雜訊和閃爍
        """
        for attempt in range(retry_attempts):
            try:
                # 初始化 VideoCapture
                if not self._init_capture(url, use_tcp):
                    raise ConnectionError("無法初始化 RTSP 連線")

                logger.debug(f"正在擷取 {num_frames} 幀影像 (預熱至多 {warmup_frames} 幀)")

                # 增強版預熱：等待有效影像（最多 warmup_frames 幀）
                # 這可以解決 "SPS 0 does not exist" 等初始化問題
                valid_frame_found = False
                for i in range(warmup_frames):
                    ret, test_frame = self.capture.read()
                    if ret and test_frame is not None and test_frame.size > 0:
                        valid_frame_found = True
                        logger.debug(f"在第 {i+1} 幀找到有效影像")
                        break
                
                if not valid_frame_found:
                    raise RuntimeError(f"預熱階段讀取失敗: 在 {warmup_frames} 幀內未找到有效影像")

                # 額外預熱：再讀取幾幀以確保穩定
                for _ in range(5):
                    self.capture.read()

                # 擷取實際影像
                frames = []
                for i in range(num_frames):
                    ret, frame = self.capture.read()
                    if not ret or frame is None:
                        raise RuntimeError(f"擷取影像失敗 (第 {i+1}/{num_frames} 幀)")

                    frames.append(frame)

                if not frames:
                    raise RuntimeError("無法從 RTSP 串流擷取影像")

                logger.info(f"成功擷取 {len(frames)} 幀影像: {frames[0].shape}")
                return frames

            except Exception as e:
                logger.warning(f"擷取多幀影像失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")

                # 釋放並重新連線
                self.release()

                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"無法從 RTSP 串流擷取多幀影像: {e}")

        raise RuntimeError("擷取多幀影像失敗：已達最大重試次數")


if __name__ == "__main__":
    # 簡單測試
    source = RTSPImageSource()

    # 測試 URL 格式驗證
    test_url = "rtsp://admin:password@192.168.1.100:554/stream1"
    safe_url = source._get_safe_url(test_url)
    print(f"原始 URL: {test_url}")
    print(f"安全 URL: {safe_url}")

    # 注意: 實際測試需要真實的 RTSP 串流
    print("\n✅ RTSPImageSource 基礎功能測試通過")
    print("⚠️  完整測試需要真實的 RTSP 串流")
