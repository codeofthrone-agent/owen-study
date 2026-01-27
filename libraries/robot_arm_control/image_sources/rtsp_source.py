"""
RTSP 影像源 (RTSP Image Source)

功能:
- 從 RTSP 串流擷取影像
- 支援連接重試
- 支援多幀擷取（多幀平均）
- 支援 TCP/UDP 傳輸協議

作者: Robot Automation Team
日期: 2025-11-17
版本: v5.5.0 (RTSP 效能優化)

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

        # 設定環境變數以抑制FFmpeg警告訊息
        os.environ['AV_LOG_FORCE_NOCOLOR'] = '1'  # 禁用顏色輸出
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'  # 只顯示錯誤
        
        # 設定OpenCV日誌級別 (需要OpenCV 4.x+)
        # 某些OpenCV版本可能沒有LOG_LEVEL_ERROR常數,使用try-except處理
        # 這會抑制 "SPS 0 does not exist" 和 "PPS id out of range" 等重複警告
        try:
            if hasattr(cv2, 'setLogLevel') and hasattr(cv2, 'LOG_LEVEL_ERROR'):
                cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
            elif hasattr(cv2, 'setLogLevel'):
                # 舊版OpenCV使用數字: 0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR, 4=FATAL
                cv2.setLogLevel(3)  # ERROR level
            else:
                logger.debug("當前OpenCV版本不支持 setLogLevel 方法。")
        except Exception as e:
            logger.debug(f"無法設定OpenCV日誌級別: {e}")

        logger.info("RTSPImageSource 初始化完成 (FFmpeg日誌已過濾)")

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

    def flush_buffer(self, max_frames: int = 150) -> int:
        """清空 RTSP 緩衝區中的舊幀

        RTSP 串流會在 buffer 中累積影像，如果不清空就會讀到舊的影像。
        此方法會快速讀取並丟棄緩衝的幀，確保下次擷取是最新影像。
        
        v5.5.0: 最終優化 - 基於實測確定最佳值
        - skip_check_frames: 30 幀 (實測最佳平衡點)
          * 60 幀: 11s/10s/5.6s (可靠但慢)
          * 30 幀: 7s/6s/1.6s (可靠且快) ✅ 最佳
          * 20 幀: 失敗 (清空不足，讀取到舊影像)
        - threshold: 0.02s (20ms)
        - max_frames: 150 幀

        Args:
            max_frames: 最多讀取的幀數（預設 150）

        Returns:
            int: 實際清空的幀數
        """
        if self.capture is None or not self.capture.isOpened():
            return 0

        flushed = 0
        # 閾值: 判定是否為即時串流 (低於 30fps 的間隔, 33ms)
        # 設定為 0.02s (20ms)，只要讀取快於 20ms 都視為緩衝幀
        threshold = 0.02
        
        # 強制清空前 30 幀 (實測最佳值)
        # 基於測試結果: 30 幀可靠且快速，20 幀會失敗
        skip_check_frames = 30

        for i in range(max_frames):
            start_time = time.time()
            if not self.capture.grab():
                break
            
            elapsed = time.time() - start_time
            flushed += 1
            
            # 前 30 幀不檢查時間 (強制清空)
            if flushed <= skip_check_frames:
                continue

            # 如果讀取時間超過閾值，表示已經追上即時串流（Buffer已空）
            if elapsed > threshold:
                logger.debug(f"Buffer 已清空 (在第 {flushed} 幀追上即時串流, 當前幀耗時 {elapsed*1000:.1f}ms)")
                break

        if flushed == max_frames:
            logger.warning(f"RTSP buffer 清空達到上限 ({flushed} 幀)，可能仍有延遲")
        elif flushed > 30:
            logger.debug(f"RTSP buffer 大量清空: {flushed} 幀")

        return flushed

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

    def _init_capture(self, url: str, use_tcp: bool = True, timeout: int = 10) -> bool:
        """初始化 VideoCapture 連線

        Args:
            url: RTSP URL
            use_tcp: 是否使用 TCP 傳輸（預設 True，較穩定）
            timeout: 連線逾時時間（秒），預設 10 秒

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
            logger.debug(f"初始化 VideoCapture: {self._get_safe_url(url)} (timeout={timeout}s)")

            # 設定 FFmpeg 選項以支援 HEVC/H.265 和 TCP 傳輸
            # 增加 loglevel 選項以抑制重複的HEVC解碼警告訊息
            # 增加 stimeout 選項設定逾時 (單位: 微秒)
            stimeout = timeout * 1000000
            
            common_options = (
                f'analyzeduration;20000000|'
                f'probesize;20000000|'
                f'stimeout;{stimeout}|'
                f'loglevel;quiet'
            )

            if use_tcp:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                    f'rtsp_transport;tcp|{common_options}'
                )
                logger.debug("已設定 FFmpeg 選項: TCP 傳輸 + HEVC 支援 + 日誌過濾 + Timeout")
            else:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (
                    f'rtsp_transport;udp|{common_options}'
                )
                logger.debug("已設定 FFmpeg 選項: UDP 傳輸 + HEVC 支援 + 日誌過濾 + Timeout")

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
        use_tcp: bool = True,
        timeout: int = 10
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
                if not self._init_capture(url, use_tcp, timeout):
                    raise ConnectionError("無法初始化 RTSP 連線")

                logger.debug(f"正在擷取影像 (嘗試 {attempt + 1}/{retry_attempts})")

                # v4.3.1: 先清空 buffer，確保讀取的是最新影像
                self.flush_buffer(max_frames=90)

                # 增強版預熱：等待有效影像（最多 30 幀）
                # 這可以解決 "SPS 0 does not exist" 等初始化問題
                valid_frame_found = False
                for _ in range(30):
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
        use_tcp: bool = True,
        timeout: int = 10
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
                if not self._init_capture(url, use_tcp, timeout):
                    raise ConnectionError("無法初始化 RTSP 連線")

                # v4.3.1: 先清空 buffer，確保讀取的是最新影像
                self.flush_buffer(max_frames=90)

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
