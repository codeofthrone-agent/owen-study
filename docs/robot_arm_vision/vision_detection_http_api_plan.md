# 視覺檢測 HTTP API Server 重構計畫

**版本:** v4.2.0
**日期:** 2025-11-18
**狀態:** 📋 規劃中
**優先級:** 中

---

## 📋 執行摘要

將 `robot_arm_server.py` 重構為**雙協議服務器**：
- **Socket (9000)**: 專注機器手臂控制（pymycobot 協議）
- **HTTP API (8000)**: 專注影像傳輸（RESTful API）

---

## 🎯 目標

### 核心目標
1. **職責分離**: Socket 控制 vs HTTP 影像
2. **並發安全**: 兩個獨立通道，互不干擾
3. **擴展性強**: RESTful API 易於添加新功能
4. **向後兼容**: 保持現有 Socket 控制功能

### 非目標
- ❌ 不移除現有 Socket 影像功能（保持向後兼容）
- ❌ 不需要修改機器手臂控制協議
- ❌ 不增加額外硬體需求

---

## 🏗️ 架構設計

### 當前架構 (v4.1.1)

```
┌─────────────────────────────────────────────────────────┐
│                  robot_arm_server.py                    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Socket Server (9000)                   │    │
│  │  - 機器手臂控制命令（pymycobot 二進制）        │    │
│  │  - JSON 影像請求 (capture_image)               │    │
│  │  - 單一客戶端限制                              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  問題：                                                  │
│  ⚠️  控制與影像混用同一 Socket                          │
│  ⚠️  並發風險（同時控制+截圖）                          │
│  ⚠️  單一客戶端限制                                      │
└─────────────────────────────────────────────────────────┘
```

### 目標架構 (v4.2.0)

```
┌──────────────────────────────────────────────────────────────────┐
│                     robot_arm_server.py                          │
│                                                                   │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Socket Server (9000)   │  │   HTTP API Server (8000)     │  │
│  │  - 機器手臂控制         │  │   - RESTful 影像 API         │  │
│  │  - pymycobot 協議       │  │   - GET /api/v1/capture      │  │
│  │  - 單一客戶端           │  │   - 多客戶端並發支援         │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
│         ↓                              ↓                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │          CameraCapture (共用影像截取引擎)              │     │
│  │          - 多幀平均                                     │     │
│  │          - Base64 編碼                                  │     │
│  │          - 線程安全                                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                            ↓                                     │
│                     USB Camera (/dev/video0)                     │
└──────────────────────────────────────────────────────────────────┘

客戶端架構：
┌───────────────────────────────────────────────────────────────┐
│                   RobotArmKeywords                            │
│                                                                │
│  ┌────────────────────┐         ┌─────────────────────────┐  │
│  │ MyCobotSocket      │         │  HTTPImageSource        │  │
│  │ Controller         │         │  - GET /api/v1/capture  │  │
│  │ - Socket (9000)    │         │  - HTTP (8000)          │  │
│  │ - 機器手臂控制      │         │  - 影像截取              │  │
│  └────────────────────┘         └─────────────────────────┘  │
│                                                                │
│  優點：                                                        │
│  ✅ 職責分離                                                   │
│  ✅ 並發安全                                                   │
│  ✅ 易於測試（curl / Postman）                                 │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔧 技術規格

### HTTP API 端點設計

#### 1. GET /api/v1/health
**用途:** 健康檢查

**Response:**
```json
{
  "status": "ok",
  "version": "4.2.0",
  "camera": {
    "available": true,
    "device": "/dev/video0"
  },
  "robot_arm": {
    "connected": true,
    "power_on": true
  }
}
```

#### 2. GET /api/v1/capture
**用途:** 截取單一影像（多幀平均）

**Query Parameters:**
- `num_frames` (int, default=5): 多幀平均數量
- `format` (str, default="jpeg"): 影像格式 ("jpeg" | "png")
- `warmup_frames` (int, default=20): 預熱幀數

**Response:**
```json
{
  "status": "success",
  "image_base64": "<base64_encoded_image>",
  "metadata": {
    "num_frames": 5,
    "format": "jpeg",
    "timestamp": "2025-11-18T15:30:45.123Z",
    "shape": [480, 640, 3]
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "無法截取圖像: Camera not available"
}
```

#### 3. GET /api/v1/capture/multiple
**用途:** 截取多張影像（連續截圖）

**Query Parameters:**
- `num_images` (int, default=5): 影像數量
- `num_frames_per_image` (int, default=5): 每張影像的多幀平均數量
- `format` (str, default="jpeg"): 影像格式

**Response:**
```json
{
  "status": "success",
  "images": [
    {
      "index": 0,
      "image_base64": "<base64_encoded_image>",
      "timestamp": "2025-11-18T15:30:45.123Z"
    },
    {
      "index": 1,
      "image_base64": "<base64_encoded_image>",
      "timestamp": "2025-11-18T15:30:45.223Z"
    }
  ],
  "metadata": {
    "total_images": 5,
    "format": "jpeg"
  }
}
```

---

## 💻 實作計畫

### Phase 1: HTTP API Server 基礎架構
- [ ] 安裝 `flask` 或 `fastapi` (推薦 Flask - 簡單輕量)
- [ ] 創建 `HTTPAPIServer` 類別
- [ ] 實作 `/api/v1/health` 端點
- [ ] 實作 `/api/v1/capture` 端點
- [ ] 實作 `/api/v1/capture/multiple` 端點
- [ ] 線程安全改造 `CameraCapture`

### Phase 2: 雙協議整合
- [ ] 修改 `robot_arm_server.py` 主程式
- [ ] 使用 `threading` 同時運行 Socket + HTTP
- [ ] 共用 `CameraCapture` 實例（線程鎖保護）
- [ ] 保持向後兼容（Socket JSON 命令保留）

### Phase 3: 客戶端重構
- [ ] 創建 `HTTPImageSource` 類別
- [ ] 修改 `ImageSourceManager` 支援 HTTP 源
- [ ] 修改 `EnvironmentConfig` 新增 `http` 影像源類型
- [ ] 更新 YAML 配置檔案

### Phase 4: 測試與驗證
- [ ] 單元測試（HTTP API）
- [ ] 整合測試（Socket + HTTP 並發）
- [ ] 效能測試（並發截圖）
- [ ] 更新文檔與範例

---

## 📝 程式碼範例

### robot_arm_server.py (HTTP API 部分)

```python
from flask import Flask, jsonify, request
import threading
import logging

class HTTPAPIServer:
    """HTTP API Server for vision detection"""

    def __init__(self, camera_capture, host="0.0.0.0", port=8000):
        self.camera_capture = camera_capture
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.logger = logging.getLogger("HTTPAPIServer")

        # 註冊路由
        self.app.route('/api/v1/health')(self.health)
        self.app.route('/api/v1/capture')(self.capture_image)
        self.app.route('/api/v1/capture/multiple')(self.capture_multiple)

    def health(self):
        """健康檢查"""
        return jsonify({
            "status": "ok",
            "version": "4.2.0",
            "camera": {
                "available": True,
                "device": self.camera_capture.camera_device
            }
        })

    def capture_image(self):
        """截取單一影像"""
        try:
            num_frames = request.args.get('num_frames', default=5, type=int)
            image_format = request.args.get('format', default='jpeg', type=str)

            # 截取影像
            image = self.camera_capture.capture_multi_frame_average(
                num_frames=num_frames
            )

            # Base64 編碼
            import cv2
            import base64
            _, buffer = cv2.imencode(f'.{image_format}', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                "status": "success",
                "image_base64": image_base64,
                "metadata": {
                    "num_frames": num_frames,
                    "format": image_format,
                    "shape": list(image.shape)
                }
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def capture_multiple(self):
        """截取多張影像"""
        try:
            num_images = request.args.get('num_images', default=5, type=int)
            num_frames_per_image = request.args.get(
                'num_frames_per_image', default=5, type=int
            )
            image_format = request.args.get('format', default='jpeg', type=str)

            images = []
            for i in range(num_images):
                image = self.camera_capture.capture_multi_frame_average(
                    num_frames=num_frames_per_image
                )

                # Base64 編碼
                import cv2
                import base64
                _, buffer = cv2.imencode(f'.{image_format}', image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')

                images.append({
                    "index": i,
                    "image_base64": image_base64,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                })

            return jsonify({
                "status": "success",
                "images": images,
                "metadata": {
                    "total_images": num_images,
                    "format": image_format
                }
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def run(self):
        """啟動 HTTP Server"""
        self.logger.info(f"HTTP API Server 啟動於 {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)

# 主程式整合
if __name__ == "__main__":
    # 初始化 Camera
    camera_capture = CameraCapture(camera_device="/dev/video0")

    # 啟動 Socket Server (Thread 1)
    socket_server = MycobotServer(...)
    socket_thread = threading.Thread(target=socket_server.connect, daemon=True)
    socket_thread.start()

    # 啟動 HTTP API Server (Thread 2)
    http_server = HTTPAPIServer(camera_capture, host="0.0.0.0", port=8000)
    http_thread = threading.Thread(target=http_server.run, daemon=True)
    http_thread.start()

    # 保持主程式運行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("伺服器關閉")
```

### HTTPImageSource 類別

```python
"""
HTTP 影像源 (HTTP Image Source)
"""
import requests
import base64
import numpy as np
import cv2
from typing import List, Optional
from loguru import logger


class HTTPImageSource:
    """HTTP API 影像源

    從 robot_arm_server HTTP API 擷取影像。

    Attributes:
        base_url (str): HTTP API 基礎 URL
        timeout (float): HTTP 請求超時時間
        last_image (np.ndarray): 最後擷取的影像
    """

    def __init__(self, base_url: str = "http://10.42.0.180:8000", timeout: float = 30.0):
        """初始化 HTTP 影像源

        Args:
            base_url: HTTP API 基礎 URL
            timeout: HTTP 請求超時時間（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.last_image: Optional[np.ndarray] = None

        logger.info(f"HTTPImageSource 初始化完成: {self.base_url}")

    def request_image(
        self,
        num_frames: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        image_format: str = "jpeg"
    ) -> np.ndarray:
        """請求單一影像

        Args:
            num_frames: Server 端多幀平均數量
            retry_attempts: 重試次數
            retry_delay: 重試延遲（秒）
            image_format: 影像格式 ("jpeg" | "png")

        Returns:
            np.ndarray: BGR 格式的影像

        Raises:
            ConnectionError: HTTP 請求失敗
            RuntimeError: 影像解碼失敗
        """
        url = f"{self.base_url}/api/v1/capture"
        params = {
            "num_frames": num_frames,
            "format": image_format
        }

        for attempt in range(retry_attempts):
            try:
                logger.debug(f"HTTP 請求影像 (嘗試 {attempt + 1}/{retry_attempts})")

                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()
                if data.get("status") != "success":
                    raise RuntimeError(f"Server 回應錯誤: {data.get('message')}")

                # 解碼 Base64 影像
                image_base64 = data.get("image_base64")
                image_bytes = base64.b64decode(image_base64)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image is None:
                    raise RuntimeError("cv2.imdecode 返回 None")

                self.last_image = image
                logger.info(f"成功擷取影像: {image.shape}")
                return image

            except Exception as e:
                logger.warning(f"HTTP 請求失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"無法從 HTTP API 擷取影像: {e}")

        raise RuntimeError("請求影像失敗：已達最大重試次數")

    def request_multiple_images(
        self,
        num_images: int = 5,
        num_frames_per_image: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 2.0,
        image_format: str = "jpeg"
    ) -> List[np.ndarray]:
        """請求多張影像

        Args:
            num_images: 影像數量
            num_frames_per_image: 每張影像的 Server 端多幀平均數量
            retry_attempts: 重試次數
            retry_delay: 重試延遲（秒）
            image_format: 影像格式 ("jpeg" | "png")

        Returns:
            list[np.ndarray]: 影像列表

        Raises:
            ConnectionError: HTTP 請求失敗
        """
        url = f"{self.base_url}/api/v1/capture/multiple"
        params = {
            "num_images": num_images,
            "num_frames_per_image": num_frames_per_image,
            "format": image_format
        }

        for attempt in range(retry_attempts):
            try:
                logger.debug(f"HTTP 請求多張影像 (嘗試 {attempt + 1}/{retry_attempts})")

                response = requests.get(url, params=params, timeout=self.timeout * 2)
                response.raise_for_status()

                data = response.json()
                if data.get("status") != "success":
                    raise RuntimeError(f"Server 回應錯誤: {data.get('message')}")

                # 解碼所有影像
                images = []
                for img_data in data.get("images", []):
                    image_base64 = img_data.get("image_base64")
                    image_bytes = base64.b64decode(image_base64)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if image is None:
                        raise RuntimeError("cv2.imdecode 返回 None")

                    images.append(image)

                logger.info(f"成功擷取 {len(images)} 張影像: {images[0].shape}")
                return images

            except Exception as e:
                logger.warning(f"HTTP 請求失敗 (嘗試 {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"無法從 HTTP API 擷取多張影像: {e}")

        raise RuntimeError("請求多張影像失敗：已達最大重試次數")
```

---

## 🧪 測試策略

### 1. HTTP API 測試（使用 curl）

```bash
# 健康檢查
curl http://10.42.0.180:8000/api/v1/health

# 截取單一影像
curl "http://10.42.0.180:8000/api/v1/capture?num_frames=5&format=jpeg" > response.json

# 提取 Base64 影像並解碼
jq -r '.image_base64' response.json | base64 -d > test_image.jpg
```

### 2. 並發測試（Socket + HTTP 同時運行）

```bash
# Terminal 1: 機器手臂控制
python3 -c "
from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
controller = MyCobotSocketController('10.42.0.180', 9000)
controller.connect()
controller.get_angles()
"

# Terminal 2: 同時截圖
curl "http://10.42.0.180:8000/api/v1/capture?num_frames=5"
```

### 3. Robot Framework 測試

```robotframework
*** Test Cases ***
HTTP 影像源測試
    [Documentation]    測試 HTTP API 影像截取
    Given 測試環境設定為 "taipei_lab_http"
    When 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 上一步操作應該成功
    And 檢測信心度應該大於 0.8
```

---

## 📊 效能評估

### 預期效能

| 指標 | Socket (v4.1.1) | HTTP (v4.2.0) |
|------|----------------|---------------|
| 單張影像截取 | ~0.5s | ~0.6s |
| 5張影像截取 | ~2.5s | ~2.8s |
| 並發支援 | ❌ 單一客戶端 | ✅ 多客戶端 |
| 工具測試 | ❌ 需自定義腳本 | ✅ curl/Postman |
| 職責分離 | ❌ 混用 | ✅ 獨立通道 |

### 資源消耗

- **額外記憶體:** ~50MB（Flask）
- **額外CPU:** ~5%（HTTP 處理）
- **網路頻寬:** 與 Socket 相同

---

## 🚀 部署檢查清單

### Server 端（Jetson Nano）

- [ ] 安裝 Flask: `pip install flask`
- [ ] 更新 `robot_arm_server.py`
- [ ] 測試 HTTP API 端點
- [ ] 設定防火牆允許 8000 端口
- [ ] 更新 systemd 服務檔案

### Client 端（Ubuntu 24.04）

- [ ] 創建 `HTTPImageSource` 類別
- [ ] 修改 `ImageSourceManager`
- [ ] 更新 `EnvironmentConfig`
- [ ] 更新 YAML 配置檔案
- [ ] 執行測試案例驗證

---

## 📚 相關文檔

- [vision_detection_local_spec.md](vision_detection_local_spec.md) - 技術規格
- [vision_detection_deployment_checklist.md](vision_detection_deployment_checklist.md) - 部署清單
- [CLAUDE.md](../CLAUDE.md) - 專案總文檔

---

## 📅 時程規劃

| Phase | 預計時間 | 狀態 |
|-------|---------|------|
| Phase 1: HTTP API 基礎 | 2-3 小時 | 📋 待開始 |
| Phase 2: 雙協議整合 | 1-2 小時 | 📋 待開始 |
| Phase 3: 客戶端重構 | 2-3 小時 | 📋 待開始 |
| Phase 4: 測試與驗證 | 2-3 小時 | 📋 待開始 |
| **總計** | **7-11 小時** | |

---

## ✅ 成功標準

1. ✅ HTTP API 正常運行（健康檢查通過）
2. ✅ Socket 控制不受影響（向後兼容）
3. ✅ 並發測試通過（Socket + HTTP 同時運行）
4. ✅ 所有現有測試案例通過
5. ✅ 文檔更新完整

---

**最後更新:** 2025-11-18
**負責人:** Robot Automation Team
**審核狀態:** 待審核
