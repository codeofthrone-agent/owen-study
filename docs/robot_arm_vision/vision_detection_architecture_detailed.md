# 影像判定本機化架構詳細說明

**文件版本**: v1.0.0
**建立日期**: 2025-11-16
**目的**: 詳細說明新架構設計，釐清 MycobotServer 的職責與影像來源

---

## 📋 目錄

1. [您的需求確認](#您的需求確認)
2. [新架構設計（Mermaid）](#新架構設計mermaid)
3. [MycobotServer 職責詳解](#mycobotserver-職責詳解)
4. [影像來源流程](#影像來源流程)
5. [通訊協議設計](#通訊協議設計)
6. [與規劃的對比](#與規劃的對比)

---

## 您的需求確認

根據您的說明，MycobotServer（遠端主機）的職責應為：

### ✅ **MycobotServer 職責**

1. **機器手臂控制**
   - 接收 Socket 命令控制手臂移動
   - 控制 MyCobot 280 機器手臂（透過 Serial `/dev/ttyUSB0`）

2. **影像傳輸**
   - 使用 **本機** `/dev/video0`（MyCobot 280 Jetson Nano 上的 USB Camera）
   - 透過 Socket 傳輸影像到 Ubuntu 本機端

### ✅ **Ubuntu 本機端職責**

1. **影像判定**
   - 接收來自 MycobotServer 的影像（透過 Socket）
   - 或接收來自 IP Camera 的影像（透過 RTSP）
   - 執行 HSV 色彩檢測、亮度檢測

2. **測試控制**
   - 發送手臂控制命令到 MycobotServer
   - 執行 Robot Framework 測試案例

---

## 新架構設計（Mermaid）

### 完整系統架構圖

```mermaid
graph TB
    subgraph Ubuntu["Ubuntu 本機端 (10.42.0.X)"]
        RF[Robot Framework Tests]
        KW[RobotArmKeywords]
        LVA[LocalVisionAnalyzer<br/>本機視覺分析引擎]
        ISM[ImageSourceManager<br/>影像源管理器]

        subgraph ImageSources["影像源 (雙來源)"]
            RTSP[RTSPImageSource<br/>RTSP 串流影像]
            SOCK[SocketImageSource<br/>Socket 影像接收]
        end

        SC[MyCobotSocketController<br/>手臂控制]

        RF --> KW
        KW --> LVA
        KW --> SC
        LVA --> ISM
        ISM --> RTSP
        ISM --> SOCK
    end

    subgraph JetsonNano["MycobotServer<br/> 10.42.0.180:9000 MyCobot_280_Jetson_Nano"]
        MS[MycobotServer<br/>Socket 伺服器]
        ARM[機器手臂控制<br/>Serial /dev/ttyUSB0]
        CAM[USB Camera<br/>/dev/video0]

        MS --> ARM
        MS --> CAM
    end

    subgraph External["外部資源"]
        IPCAM[IP Camera<br/>rtsp://10.42.0.100:554]
    end

    %% Ubuntu → MyCobot 280 Jetson Nano 通訊
    SC -->|手臂控制命令<br/>JSON| MS
    SOCK -->|請求影像<br/>capture_image| MS
    MS -->|回傳影像<br/>Base64| SOCK

    %% Ubuntu → IP Camera 通訊
    RTSP -->|RTSP Stream| IPCAM

    %% MyCobot 280 Jetson Nano 內部
    ARM -.->|控制| MyCobot[MyCobot 280]
    CAM -.->|擷取| USBCam[USB 攝影機]

    style MS fill:#ff9999
    style LVA fill:#99ff99
    style ISM fill:#9999ff
    style CAM fill:#ffff99
```

### 循序圖：完整檢測流程

```mermaid
sequenceDiagram
    participant Test as Robot Framework<br/>Test
    participant KW as RobotArmKeywords
    participant LVA as LocalVisionAnalyzer<br/>(本機)
    participant ISM as ImageSourceManager
    participant SOCK as SocketImageSource
    participant MS as MycobotServer<br/>(MyCobot 280 Jetson Nano)
    participant CAM as USB Camera<br/>(/dev/video0)

    Note over Test,CAM: 場景：使用 Socket 影像源檢測按鈕

    Test->>KW: When 用戶檢測面板按鈕 "light1" 的顏色

    Note over KW: 1. 控制手臂移動到觀測位置
    KW->>MS: JSON: {"command": "move_angles", "angles": [...]}
    MS->>MS: 控制 MyCobot 280 移動
    MS-->>KW: {"status": "success"}

    Note over KW,ISM: 2. 本機請求影像
    KW->>LVA: detect_panel_light(...)
    LVA->>ISM: capture_image(num_frames=5)

    Note over ISM,MS: 3. Socket 影像擷取流程
    ISM->>SOCK: capture_image()

    loop 多幀平均 (5 幀)
        SOCK->>MS: JSON: {"command": "capture_image"}
        MS->>CAM: cv2.VideoCapture("/dev/video0")
        CAM-->>MS: frame (numpy array)
        MS->>MS: 編碼為 Base64
        MS-->>SOCK: JSON: {"status": "success",<br/>"image": "base64..."}
        SOCK->>SOCK: 解碼 Base64 → numpy array
        SOCK->>SOCK: 累積幀
    end

    SOCK->>SOCK: 計算多幀平均
    SOCK-->>ISM: avg_frame (numpy array)

    ISM-->>LVA: avg_frame

    Note over LVA: 4. 本機執行視覺分析
    LVA->>LVA: 提取 ROI
    LVA->>LVA: HSV 色彩檢測
    LVA->>LVA: 亮度檢測

    LVA-->>KW: {"color": "blue", "confidence": 0.95, ...}

    KW-->>Test: detection_result

    Test->>KW: Then 面板按鈕顏色應該為 "blue"
    KW->>KW: 驗證結果
    KW-->>Test: ✅ 驗證通過
```

### 影像來源對比圖

```mermaid
graph LR
    subgraph Source1["影像源 1: RTSP"]
        IPCAM[IP Camera<br/>遠端網路攝影機]
        RTSP_URL[rtsp://10.42.0.100:554/stream]

        IPCAM --> RTSP_URL
    end

    subgraph Source2["影像源 2: Socket"]
        RPI[MyCobot 280 Jetson Nano<br/>MycobotServer]
        USBCAM[USB Camera<br/>/dev/video0]
        SOCKET[Socket<br/>10.42.0.180:9000]

        USBCAM --> RPI
        RPI --> SOCKET
    end

    subgraph Ubuntu["Ubuntu 本機端"]
        ISM[ImageSourceManager]
        RTSP_SRC[RTSPImageSource]
        SOCK_SRC[SocketImageSource]
        LVA[LocalVisionAnalyzer]

        ISM --> RTSP_SRC
        ISM --> SOCK_SRC
        RTSP_SRC --> LVA
        SOCK_SRC --> LVA
    end

    RTSP_URL -.->|RTSP 串流| RTSP_SRC
    SOCKET -.->|Base64 影像| SOCK_SRC

    style USBCAM fill:#ffff99
    style RPI fill:#ff9999
    style LVA fill:#99ff99
```

---

## MycobotServer 職責詳解

### 原始職責（遷移前）

```python
# scripts/robot_arm_server.py - 原始版本
class MycobotServer:
    """
    職責：
    1. Socket 伺服器（監聽 Port 9000）
    2. 機器手臂控制（Serial /dev/ttyUSB0）
    3. 視覺分析（VisionAnalyzer）⚡ 需移除
    """

    def handle_command(self, command):
        if command["command"] == "detect_button":
            # ❌ 在 Server 端執行視覺檢測
            result = self.vision_analyzer.detect_button_state(...)
            return result
        elif command["command"] == "move_angles":
            # ✅ 控制手臂移動
            self.mycobot.send_angles(...)
```

### 新職責（遷移後）

```python
# scripts/robot_arm_server.py - 新版本（輕量化）
class MycobotServer:
    """
    職責：
    1. Socket 伺服器（監聽 Port 9000）
    2. 機器手臂控制（Serial /dev/ttyUSB0）
    3. 影像傳輸（USB Camera /dev/video0）⚡ 新增
    """

    def handle_command(self, command):
        if command["command"] == "capture_image":
            # ✅ 新增：擷取並傳輸影像
            return self.capture_and_encode_image()
        elif command["command"] == "move_angles":
            # ✅ 保留：控制手臂移動
            return self.move_angles(command["angles"])
        elif command["command"] == "move_coords":
            # ✅ 保留：控制手臂座標
            return self.move_coords(command["coords"])

    def capture_and_encode_image(self) -> dict:
        """
        擷取 USB Camera 影像並編碼為 Base64

        流程:
        1. 開啟 /dev/video0
        2. 讀取單一幀
        3. 編碼為 JPEG
        4. 轉為 Base64 字串
        5. 回傳 JSON

        Returns:
            {
                "status": "success",
                "image": "base64_encoded_string",
                "width": 640,
                "height": 480,
                "timestamp": "2025-11-16T12:34:56"
            }
        """
        import cv2
        import base64
        from datetime import datetime

        # 1. 開啟 USB Camera
        cap = cv2.VideoCapture("/dev/video0")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            return {
                "status": "error",
                "message": "無法開啟 /dev/video0"
            }

        # 2. 讀取單一幀
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {
                "status": "error",
                "message": "無法讀取影像"
            }

        # 3. 編碼為 JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

        if not ret:
            return {
                "status": "error",
                "message": "無法編碼影像"
            }

        # 4. 轉為 Base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # 5. 回傳 JSON
        return {
            "status": "success",
            "image": image_base64,
            "width": frame.shape[1],
            "height": frame.shape[0],
            "timestamp": datetime.now().isoformat()
        }
```

---

## 影像來源流程

### 流程 1: RTSP 串流影像（IP Camera）

```
┌─────────────────────────────────────────────────────────┐
│  場景：使用遠端 IP Camera 檢測                          │
└─────────────────────────────────────────────────────────┘

1. Ubuntu 本機端
   └─> ImageSourceManager.set_image_source("rtsp", {...})
       └─> 設定 RTSP URL: rtsp://10.42.0.100:554/stream

2. 請求影像
   └─> ImageSourceManager.capture_image(num_frames=5)
       └─> RTSPImageSource.capture_multi_frame()
           │
           ├─> cv2.VideoCapture(rtsp_url)  # 開啟 RTSP 串流
           │
           ├─> 預熱 20 幀（捨棄）
           │
           ├─> 讀取 5 幀
           │   ├─> frame_1
           │   ├─> frame_2
           │   ├─> frame_3
           │   ├─> frame_4
           │   └─> frame_5
           │
           └─> avg_frame = np.mean([frame_1, ..., frame_5])

3. 本機視覺分析
   └─> LocalVisionAnalyzer.detect_panel_light(avg_frame)
       ├─> HSV 色彩檢測
       └─> 亮度檢測

優點：
✅ 直接從網路攝影機擷取（低延遲）
✅ 不依賴 MyCobot 280 Jetson Nano 的處理能力
✅ 適合固定位置的 IP Camera

缺點：
❌ 需要 IP Camera 支援 RTSP
❌ 網路頻寬需求較高（~2-5 Mbps）
```

### 流程 2: Socket 影像（從 MycobotServer）

```
┌─────────────────────────────────────────────────────────┐
│  場景：使用機器手臂上的 USB Camera 檢測                │
└─────────────────────────────────────────────────────────┘

1. Ubuntu 本機端
   └─> ImageSourceManager.set_image_source("socket", {...})
       └─> 設定 Socket: 10.42.0.180:9000

2. 請求影像（多幀平均，5 幀）
   └─> ImageSourceManager.capture_image(num_frames=5)
       └─> SocketImageSource.capture_multi_frame()
           │
           └─> FOR i = 1 TO 5:
               │
               ├─> 發送 JSON 到 MycobotServer:
               │   {
               │     "command": "capture_image"
               │   }
               │
               ├─> MycobotServer 處理:
               │   ├─> cv2.VideoCapture("/dev/video0")
               │   ├─> ret, frame = cap.read()
               │   ├─> _, buffer = cv2.imencode('.jpg', frame)
               │   └─> image_base64 = base64.b64encode(buffer)
               │
               ├─> 接收 JSON 回應:
               │   {
               │     "status": "success",
               │     "image": "base64_encoded_jpeg_string",
               │     "width": 640,
               │     "height": 480
               │   }
               │
               ├─> 解碼 Base64:
               │   ├─> image_data = base64.b64decode(json["image"])
               │   ├─> nparr = np.frombuffer(image_data, np.uint8)
               │   └─> frame_i = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
               │
               └─> frames.append(frame_i)

           └─> avg_frame = np.mean(frames, axis=0)

3. 本機視覺分析
   └─> LocalVisionAnalyzer.detect_panel_light(avg_frame)
       ├─> HSV 色彩檢測
       └─> 亮度檢測

優點：
✅ 使用機器手臂上的 USB Camera（視角跟隨手臂）
✅ 不需額外 IP Camera 硬體
✅ 適合動態移動的檢測場景

缺點：
❌ 網路傳輸 Base64 影像（較大，~100-200 KB/幀）
❌ MycobotServer 需處理影像編碼（CPU 負擔）
❌ 延遲稍高（網路 + 編碼/解碼）
```

---

## 通訊協議設計

### JSON 命令格式

#### 1. 手臂控制命令

```json
// Ubuntu → MycobotServer
{
  "command": "move_angles",
  "angles": [10.5, -20.3, 30.1, -15.8, -90.0, 5.2]
}

// MycobotServer → Ubuntu
{
  "status": "success",
  "message": "手臂已移動到指定角度"
}
```

#### 2. 影像擷取命令（新增）

```json
// Ubuntu → MycobotServer
{
  "command": "capture_image"
}

// MycobotServer → Ubuntu
{
  "status": "success",
  "image": "/9j/4AAQSkZJRgABAQEAYABgAAD...",  // Base64 編碼的 JPEG
  "width": 640,
  "height": 480,
  "timestamp": "2025-11-16T14:30:25.123456",
  "encoding": "jpeg",
  "quality": 95
}
```

#### 3. 錯誤回應

```json
{
  "status": "error",
  "message": "無法開啟 /dev/video0",
  "error_code": "CAMERA_NOT_FOUND"
}
```

### Socket 通訊流程

```python
# Ubuntu 本機端 - SocketImageSource
class SocketImageSource:
    def request_image(self, host: str, port: int) -> np.ndarray:
        """請求單一影像"""
        import socket
        import json
        import base64

        # 1. 建立 Socket 連接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        # 2. 發送命令
        command = {"command": "capture_image"}
        sock.sendall(json.dumps(command).encode('utf-8'))

        # 3. 接收回應
        response_data = b""
        while True:
            chunk = sock.recv(1048576)  # 1MB buffer
            if not chunk:
                break
            response_data += chunk
            try:
                # 嘗試解析 JSON
                response = json.loads(response_data.decode('utf-8'))
                break
            except json.JSONDecodeError:
                # JSON 不完整，繼續接收
                continue

        sock.close()

        # 4. 檢查狀態
        if response["status"] != "success":
            raise RuntimeError(f"影像擷取失敗: {response['message']}")

        # 5. 解碼 Base64 影像
        image_data = base64.b64decode(response["image"])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return image

    def capture_multi_frame(self, host: str, port: int, num_frames: int = 5) -> np.ndarray:
        """多幀平均擷取"""
        frames = []

        for i in range(num_frames):
            frame = self.request_image(host, port)
            frames.append(frame.astype(np.float32))
            time.sleep(0.05)  # 短暫延遲避免過載

        avg_frame = np.mean(frames, axis=0).astype(np.uint8)
        return avg_frame
```

---

## 與規劃的對比

### ✅ **您的需求**

| 需求 | 規劃是否符合 | 說明 |
|------|-------------|------|
| MycobotServer 可操控手臂移動 | ✅ 符合 | `move_angles`, `move_coords` 命令 |
| MycobotServer 可傳輸 /dev/video0 | ✅ 符合 | `capture_image` 命令（新增） |
| 本機端執行視覺分析 | ✅ 符合 | LocalVisionAnalyzer 在 Ubuntu 執行 |
| 支援 RTSP 影像源 | ✅ 符合 | RTSPImageSource |
| 支援 Socket 影像源 | ✅ 符合 | SocketImageSource |

### ✅ **架構對齊確認**

```
您的理解：
┌──────────────────────────────────────────────────────┐
│ MycobotServer (MyCobot 280 Jetson Nano)                         │
│  1. 操控手臂移動                                     │
│  2. 傳輸 /dev/video0 影像到 Socket                   │
└──────────────────────────────────────────────────────┘
                      ↓ Socket (JSON)
┌──────────────────────────────────────────────────────┐
│ Ubuntu 本機端                                         │
│  - 接收影像                                          │
│  - 執行視覺分析（HSV 色彩、亮度檢測）                │
└──────────────────────────────────────────────────────┘

規劃的設計：
✅ 完全相同！
```

### 🎯 **關鍵確認點**

1. **MycobotServer 的 USB Camera**
   - ✅ 使用 MyCobot 280 Jetson Nano 本機的 `/dev/video0`
   - ✅ **不是** Ubuntu 本機的 USB Camera
   - ✅ 透過 Socket 傳輸到 Ubuntu

2. **影像判定位置**
   - ✅ 在 **Ubuntu 本機端** 執行（LocalVisionAnalyzer）
   - ❌ **不在** MyCobot 280 Jetson Nano 執行

3. **雙影像源**
   - ✅ **RTSP**: 遠端 IP Camera（固定位置）
   - ✅ **Socket**: MyCobot 280 Jetson Nano 的 USB Camera（跟隨手臂移動）

---

## 總結

### ✅ **規劃與您的需求完全一致**

您的需求：
> "MycobotServer 是遠端主機，會使用 /dev/video0（遠端主機的 video0），整合到 MycobotServer socket"

規劃的設計：
- ✅ MycobotServer 在 MyCobot 280 Jetson Nano 執行
- ✅ 使用 MyCobot 280 Jetson Nano 的 `/dev/video0`
- ✅ 透過 Socket 傳輸影像到 Ubuntu
- ✅ Ubuntu 本機端執行視覺分析

### 📊 **架構對比表**

| 項目 | 原架構（遷移前） | 新架構（遷移後） |
|------|------------------|------------------|
| **視覺分析位置** | MyCobot 280 Jetson Nano | Ubuntu 本機 |
| **USB Camera 位置** | MyCobot 280 Jetson Nano `/dev/video0` | MyCobot 280 Jetson Nano `/dev/video0` |
| **影像傳輸方式** | 無（Server 本地處理） | Socket (Base64 JSON) |
| **手臂控制** | Socket 命令 | Socket 命令（不變） |
| **RTSP 支援** | 無 | 新增 |

### 🚀 **下一步**

文檔已完全符合您的需求！可以開始實施：

1. **Phase 1**: 實作 SocketImageSource（接收 MycobotServer 的影像）
2. **Server 端**: 新增 `capture_image` 命令到 MycobotServer
3. **測試**: 驗證影像傳輸與視覺分析

需要我進一步說明任何部分嗎？

---

**文件版本歷史**:
- v1.0.0 (2025-11-16): 初版建立，詳細說明架構設計

---

## RTSP 影像分析工作流程

### 總體流程概述

整個流程的核心是**透過 RTSP 串流獲取即時影像，在影像中定位感興趣的區域 (ROI)，分析此區域的視覺特徵（如顏色、亮度），並將分析結果回傳給 Robot Framework 測試案例，用於斷言 (Assert) 某個物理操作是否成功。**

例如，當機械手臂按下一個按鈕後，系統會啟動影像分析來確認按鈕上的指示燈是否從「熄滅」變為「亮起」。

### 流程文字圖解

```
[Robot Framework]            [Python Libraries]                                [Hardware]
-----------------            ------------------                                ----------

+-------------------+      +-------------------------+      +---------------------+
| RobotArmKeywords.py | ---> | local_vision_analyzer.py| ---> | ImageSourceManager.py |
| (高階業務邏輯)      |      | (核心影像分析)            |      | (影像來源抽象層)      |
+-------------------+      +-------------------------+      +---------------------+
        ^                            |                                |
        | (回傳分析結果)               | (分析顏色/亮度)                    |
        | {color, brightness}        |                                |
        |                            v (擷取影像)                       v (選擇RTSP來源)
        |                      +------------------------+      +-------------------+
        +----------------------+   _calculate_aruco_offset | ---> | rtsp_source.py    |
                               | (Aruco動態校準ROI)       |      | (使用OpenCV擷取)    |
                               +------------------------+      +-------------------+
                                                                       |
                                                                       v (讀取影像串流)
                                                                +--------------+
                                                                |  IP Camera   |
                                                                +--------------+
```

### 詳細步驟分解

1.  **設定載入與初始化 (Configuration & Initialization)**
    *   **起點**：流程由 `config/robot_arm/environment_config.py` 中的 `EnvironmentConfig` 類別驅動。
    *   **過程**：
        *   它讀取主要的硬體設定檔 `config/ipcam_config.yaml`，獲取攝影機的 IP 位址、RTSP 串流路徑等資訊。
        *   同時，它會從 `.env` 檔案載入敏感資訊（如攝影機的帳號密碼）。
        *   最後，它將這些資訊組合成一個完整的 RTSP URL (例如 `rtsp://user:pass@192.168.1.100/stream1`)，並準備好影像來源的設定。

2.  **影像來源管理 (Image Source Management)**
    *   **核心元件**：`libraries/robot_arm_control/image_source_manager.py` 中的 `ImageSourceManager` 類別。
    *   **作用**：這是一個抽象層(工廠模式)，它根據上一步的設定來決定使用哪種影像來源。在目前的情境下，它會實例化 `RTSPImageSource`。這種設計讓未來擴充其他影像來源（如 USB 攝影機）變得容易。

3.  **影像串流擷取 (Stream Capture)**
    *   **核心元件**：`libraries/robot_arm_control/image_sources/rtsp_source.py` 中的 `RTSPImageSource` 類別。
    *   **過程**：
        *   內部使用 `cv2.VideoCapture(RTSP_URL)` 來連接到 IP Camera 的影像串流。
        *   為了確保影像穩定，它會智慧地**跳過初始的幾幀畫面 (warmup frames)**。
        *   當分析器需要影像時，它會擷取多幀畫面。

4.  **核心影像分析 (Core Image Analysis)**
    *   **核心引擎**：`libraries/robot_arm_control/local_vision_analyzer.py` 中的 `LocalVisionAnalyzer` 類別。這是整個流程的大腦。
    *   **詳細過程**：
        *   **降噪**：它從 `ImageSourceManager` 取得多幀影像，並將它們**平均 (averaging)**，以減少單一畫面的雜訊干擾。
        *   **動態校準 (Dynamic Calibration)**：這是此系統的一個亮點。它首先在影像中偵測 **ArUco 標記** (`_calculate_aruco_offset`)。透過 ArUco 標記的實際位置與預期位置的偏差，它可以即時計算出 ROI 的精確偏移量。這大大增強了系統對攝影機輕微移動或畫面抖動的容忍度。
        *   **ROI 分析**：根據校準後的座標，它從降噪後的影像中切割出真正感興趣的區域 (ROI)。
        *   **特徵提取**：
            *   **顏色偵測 (`_detect_color_hsv`)**：將 ROI 轉換到 HSV 色彩空間，並根據預先定義的顏色範圍判斷主要顏色。
            *   **亮度偵測 (`_detect_brightness`)**：將 ROI 轉換為灰階，並計算像素平均值來判斷亮度。

5.  **結果整合與應用 (Result Integration & Application)**
    *   **消費端**：`libraries/robot_arm_control/RobotArmKeywords.py` 中的 Robot Framework 關鍵字。
    *   **過程**：
        *   像 `then_panel_button_color_should_be` 這樣的關鍵字會呼叫 `LocalVisionAnalyzer` 的分析方法。
        *   分析器回傳一個包含結果的字典，例如 `{'color': 'red', 'brightness': 210}`。
        *   關鍵字接著使用這些結果進行斷言，例如 `Should Be Equal As Strings    ${result['color']}    red`，從而完成測試案例的驗證。
