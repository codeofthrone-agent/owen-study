# 影像判定本機化遷移計畫

**文件版本**: v1.0.0
**建立日期**: 2025-11-16
**專案**: Robot Framework 多平台自動化測試系統
**目標**: 將影像判定功能從 MyCobot 280 Jetson Nano Server 遷移至 Ubuntu 本機端

---

## 📋 目錄

1. [專案背景](#專案背景)
2. [遷移目標](#遷移目標)
3. [現有架構分析](#現有架構分析)
4. [新架構設計](#新架構設計)
5. [模組化設計](#模組化設計)
6. [配置系統設計](#配置系統設計)
7. [分階段實施計畫](#分階段實施計畫)
8. [測試策略](#測試策略)
9. [風險管理](#風險管理)
10. [驗收標準](#驗收標準)

---

## 專案背景

### 當前痛點

1. **影像判定在 Server 端執行**
   - 延遲較高（網路傳輸 + Server 處理）
   - 調整 HSV 參數需修改 Server 程式碼並重啟服務
   - 除錯困難（無法即時查看中間影像）

2. **缺乏多環境支援**
   - Taipei LAB、Taoyuan LAB、RV Car 環境需要不同配置
   - 環境切換需要手動修改程式碼

3. **功能限制**
   - 目前僅支援藍/白兩種顏色
   - 僅支援開/關兩種亮度狀態
   - 缺乏實體燈光多級亮度檢測 (0-100%)

### 業務需求

1. **多種面板類型支援**
   - 3510a、3611a、3611c（實體按鈕）
   - 未來觸控螢幕面板

2. **多環境支援**
   - Taipei LAB（主要測試環境）
   - Taoyuan LAB（次要測試環境）
   - RV Car（車載測試環境）

3. **多功能檢測**
   - **面板燈光**: 開/關、顏色（藍/白/紅/綠）
   - **實體燈光**: 開/關、亮度 (0%, 10%, 20%, ..., 100%)

4. **雙影像來源**
   - RTSP 串流影像（新增，支援遠端 IP Camera）
   - Socket 影像（從機器手臂 Server 請求影像）
   - ❌ USB Camera（不支援，USB 攝影機由 Server 端管理）

---

## 遷移目標

### 技術目標

✅ **本機化影像判定**
- 將 `VisionAnalyzer` 從 Server 遷移至本機
- 支援雙影像源（RTSP / Socket）
- 保留向後相容性（現有測試案例無需修改）

✅ **多色彩檢測**
- 支援 7+ 種顏色：藍、白、紅、綠、黃、橙、紫
- 可擴充 HSV 顏色範圍配置

✅ **多級亮度檢測**
- 支援 11 級亮度：0%, 10%, 20%, ..., 100%
- 允許 ±10% 誤差範圍

✅ **多環境配置管理**
- YAML 配置檔案驅動
- 一行關鍵字切換環境

### 業務目標

✅ **提升測試效率**
- 減少影像判定延遲 50%+
- 支援並行測試（多環境同時執行）

✅ **降低維護成本**
- 統一配置管理（無需修改程式碼）
- 詳細日誌與中間影像輸出（易於除錯）

✅ **提升測試覆蓋率**
- 支援更多面板類型
- 支援更多檢測場景（色彩、亮度）

---

## 現有架構分析

### Client-Server 架構

```
┌─────────────────────────────────────────────────────────────┐
│                    Ubuntu 本機 (Client)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Robot Framework Tests                                  │ │
│  │  - tests/robot_arm/*.robot                            │ │
│  │  - 17 個測試案例                                       │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │ RobotArmKeywords v3.0.0                                │ │
│  │  - 26 個 BDD 風格中文關鍵字                            │ │
│  │  - When 用戶檢測第 "light1" 按鈕的燈光狀態             │ │
│  │  - Then 按鈕燈光應該為 "blue" 色                       │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │ JSON 命令                                │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │ MyCobotSocketController                                │ │
│  │  - TCP/IP Socket (Port 9000)                          │ │
│  │  - JSON 協議通訊                                       │ │
│  └────────────────┬───────────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────────┘
                    │ Socket (JSON over TCP)
┌───────────────────▼──────────────────────────────────────────┐
│              MyCobot 280 Jetson Nano Server                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ MycobotServer (robot_arm_server.py:462-1275)           │ │
│  │  - 接收 JSON 命令分發                                  │ │
│  │  - 控制機器手臂移動 (Serial /dev/ttyUSB0)             │ │
│  │  - 呼叫 VisionAnalyzer                                 │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │ VisionAnalyzer ⚡ (robot_arm_server.py:59-432)         │ │
│  │                                                         │ │
│  │  核心功能:                                              │ │
│  │  ✓ 多幀平均截圖 (5 frames + 20 warmup)                │ │
│  │  ✓ HSV 色彩檢測 (藍/白)                                │ │
│  │  ✓ 亮度檢測 (開/關)                                    │ │
│  │  ✓ ArUco 標記位置校正                                  │ │
│  │  ✓ ROI 區域提取與分析                                  │ │
│  │                                                         │ │
│  │  限制:                                                  │ │
│  │  ✗ 僅支援 USB Camera (/dev/video0)                    │ │
│  │  ✗ 僅支援 2 種顏色 (藍/白)                             │ │
│  │  ✗ 僅支援 2 種亮度狀態 (開/關)                         │ │
│  │  ✗ HSV 參數寫死在程式碼中                              │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │ Hardware Access                                        │ │
│  │  - USB Camera (/dev/video0)                           │ │
│  │  - MyCobot 280 (Serial /dev/ttyUSB0)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 現有資料流

#### 視覺檢測命令流程

```
1. Robot Framework Test
   ↓ 呼叫關鍵字
2. RobotArmKeywords.when_user_detects_button_light_state("light1")
   ↓ 讀取 YAML 配置
3. 載入 button_positions.yaml → ROI 座標、觀測角度
   ↓ 構建 JSON 命令
4. JSON Command:
   {
     "command": "detect_button",
     "roi": {"x": 100, "y": 200, "width": 50, "height": 50},
     "observe_angles": [10, 20, 30, 40, 50, 60],
     "num_frames": 5,
     "warmup_frames": 20
   }
   ↓ Socket 傳送
5. MyCobotSocketController.send() → TCP/IP Socket
   ↓ 網路傳輸
6. MycobotServer.handle_command()
   ↓ 命令分發
7. 機器手臂移動到 observe_angles
   ↓ 硬體控制
8. VisionAnalyzer.capture_multi_frame_average()
   ↓ USB Camera 擷取
9. VisionAnalyzer.detect_button_state()
   ↓ HSV 色彩分析
10. JSON Response:
    {
      "status": "success",
      "result": {
        "light": "on",
        "color": "blue",
        "confidence": 0.95,
        "raw_data": {...}
      }
    }
    ↓ Socket 回傳
11. RobotArmKeywords 接收結果
    ↓ 儲存到 self.last_detection_result
12. Then 關鍵字驗證結果
```

### 現有模組職責

| 模組 | 檔案位置 | 行數 | 主要職責 |
|------|----------|------|----------|
| **VisionAnalyzer** | `scripts/robot_arm_server.py` | 59-432 (374 行) | 視覺分析引擎（⚡ 需遷移） |
| **MycobotServer** | `scripts/robot_arm_server.py` | 462-1275 (814 行) | Socket 伺服器、命令分發、手臂控制 |
| **RobotArmKeywords** | `libraries/robot_arm_control/RobotArmKeywords.py` | 1305 行 | 26 個 BDD 關鍵字 |
| **MyCobotSocketController** | `libraries/robot_arm_control/mycobot_socket_controller.py` | 428 行 | TCP/IP Socket 連接管理 |

### 現有 HSV 顏色範圍

```python
# scripts/robot_arm_server.py:81-90
self.color_ranges = {
    'blue': {
        'lower': np.array([100, 50, 50]),   # H: 100-130, S: 50-255, V: 50-255
        'upper': np.array([130, 255, 255])
    },
    'white': {
        'lower': np.array([0, 0, 200]),     # H: 0-180, S: 0-50, V: 200-255
        'upper': np.array([180, 50, 255])
    }
}
```

### 現有按鈕配置範例

```yaml
# config/robot_arm/button_positions.yaml
buttons:
  light1:
    name: "燈光按鈕 1"
    roi:
      x: 320
      y: 200
      width: 100
      height: 100
    observe_angles: [7.56, -35.59, -37.96, -15.73, -89.29, 6.06]
    aruco_marker_id: 0
    expected_color: "blue"
```

---

## 新架構設計

### 本機化架構（階段一）

```
┌─────────────────────────────────────────────────────────────┐
│                    Ubuntu 本機 (Client)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Robot Framework Tests                                  │ │
│  │  - 保留現有 17 個測試案例                              │ │
│  │  - 新增多環境測試案例                                  │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │ EnhancedRobotArmKeywords v4.0.0 ⚡ (擴充版)           │ │
│  │                                                         │ │
│  │  保留現有 26 個關鍵字 + 新增:                          │ │
│  │  ✓ Given 測試環境設定為 "${environment}"               │ │
│  │  ✓ Given 面板類型設定為 "${panel_type}"                │ │
│  │  ✓ When 用戶檢測面板按鈕 "${id}" 的顏色                │ │
│  │  ✓ When 用戶檢測實體燈光亮度 "${id}"                   │ │
│  │  ✓ Then 面板按鈕顏色應該為 "${color}"                  │ │
│  │  ✓ Then 實體燈光亮度應該為 "${level}" %                │ │
│  └────┬─────────────────────────────┬───────────────────┘ │
│       │                             │                      │
│       │ (機器手臂控制)              │ (影像判定 - 本機化)  │
│       │                             │                      │
│  ┌────▼─────────────┐       ┌───────▼─────────────────┐  │
│  │ Socket Controller│       │ LocalVisionAnalyzer ⚡   │  │
│  │ (保留不變)       │       │                          │  │
│  │ - 機器手臂移動   │       │  新功能:                 │  │
│  │ - 串口通訊       │       │  ✓ 多幀平均截圖          │  │
│  │                  │       │  ✓ 多色彩 HSV 檢測       │  │
│  │                  │       │    (藍/白/紅/綠/黃/橙/紫)│  │
│  │                  │       │  ✓ 多級亮度檢測          │  │
│  │                  │       │    (0-100%, 11 級)       │  │
│  │                  │       │  ✓ ArUco 標記校正        │  │
│  │                  │       │  ✓ 多影像源支援          │  │
│  │                  │       │  ✓ 詳細日誌與除錯輸出   │  │
│  └────┬─────────────┘       └───────┬─────────────────┘  │
│       │                             │                      │
│       │                     ┌───────▼─────────────────┐  │
│       │                     │ ImageSourceManager ⚡    │  │
│       │                     │                          │  │
│       │                     │  影像源支援:             │  │
│       │                     │  ✓ RTSP Stream 擷取      │  │
│       │                     │  ✓ USB Camera 擷取       │  │
│       │                     │  ✓ Socket Image 接收     │  │
│       │                     │  ✓ 統一多幀平均介面     │  │
│       │                     └───────┬─────────────────┘  │
│       │                             │                      │
│       │                     ┌───────▼─────────────────┐  │
│       │                     │ EnvironmentManager ⚡    │  │
│       │                     │                          │  │
│       │                     │  環境配置:               │  │
│       │                     │  ✓ Taipei LAB            │  │
│       │                     │  ✓ Taoyuan LAB           │  │
│       │                     │  ✓ RV Car                │  │
│       │                     │  ✓ YAML 配置驅動         │  │
│       │                     └─────────────────────────┘  │
│       │                                                    │
└───────┼────────────────────────────────────────────────────┘
        │ Socket (JSON)
        │ 影像源連接 (RTSP/Socket)
        │
┌───────▼────────────────────────────────────────────────────┐
│              外部資源 (MyCobot 280 Jetson Nano / IP Camera)            │
│  ┌────────────────────┐      ┌─────────────────────────┐  │
│  │ MycobotServer      │      │ IP Camera (RTSP)        │  │
│  │ (輕量化)           │      │  - rtsp://10.42.0.x:554 │  │
│  │                    │      │  - H.264 編碼           │  │
│  │  保留功能:         │      └─────────────────────────┘  │
│  │  ✓ 機器手臂控制   │                                    │
│  │  ✓ 串口通訊       │      ┌─────────────────────────┐  │
│  │                    │      │ 已移除 USB Camera 支援       │  │
│  │  移除功能:         │      │  - /dev/video0          │  │
│  │  ✗ VisionAnalyzer │      │  - 640x480 @ 30fps      │  │
│  │                    │      └─────────────────────────┘  │
│  └────────────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

### 資料流（新架構）

#### 視覺檢測命令流程（本機化）

```
1. Robot Framework Test
   ↓
2. Given 測試環境設定為 "taipei_lab"
   ↓ 載入環境配置
3. EnvironmentConfig.get_environment("taipei_lab")
   → {
       "image_source": "rtsp",
       "rtsp_url": "rtsp://10.42.0.100:554/stream",
       "robot_arm_host": "10.42.0.180",
       "button_config_path": "config/robot_arm/taipei_lab_buttons.yaml"
     }
   ↓
4. Given 面板類型設定為 "3611a"
   ↓ 載入面板配置
5. 讀取 taipei_lab_buttons.yaml (panel_type: "3611a")
   ↓
6. When 用戶檢測面板按鈕 "light1" 的顏色
   ↓ 本機執行（無需 Socket）
7. LocalVisionAnalyzer.detect_panel_light()
   ↓ 影像擷取
8. ImageSourceManager.capture_image(source_type="rtsp", ...)
   ↓ RTSP 串流擷取
9. RTSPImageSource.capture_multi_frame()
   → 多幀平均 (5 frames + 20 warmup)
   ↓ 返回平均影像
10. LocalVisionAnalyzer.detect_button_state()
    ↓ HSV 色彩分析（本機）
11. 結果:
    {
      "light_state": "on",
      "color": "blue",
      "brightness_level": 80,
      "confidence": 0.95,
      "raw_data": {...}
    }
    ↓ 儲存結果
12. Then 面板按鈕顏色應該為 "blue"
    ↓ 驗證（本機）
13. ✅ 測試通過
```

**關鍵差異**:
- ❌ 不再透過 Socket 發送視覺檢測命令
- ✅ 影像擷取與分析全部在本機執行
- ✅ 支援雙影像源（RTSP / Socket）
- ✅ 機器手臂控制仍透過 Socket（保留）

---

## 模組化設計

### 核心模組架構

```
libraries/robot_arm_control/
├── RobotArmKeywords.py              # 擴充版（v4.0.0）
├── LocalVisionAnalyzer.py           # ⚡ 新增：本機視覺分析器
├── ImageSourceManager.py            # ⚡ 新增：影像源管理器
├── image_sources/                   # ⚡ 新增：影像源實作
│   ├── __init__.py
│   ├── rtsp_source.py              # RTSP 串流影像源
│   └── socket_image_source.py      # Socket 影像源
├── mycobot_socket_controller.py     # 保留不變
└── tests/                           # ⚡ 新增：單元測試
    ├── test_local_vision_analyzer.py
    ├── test_image_source_manager.py
    └── test_color_detection.py

config/robot_arm/
├── environment_config.py            # ⚡ 新增：環境配置管理
├── button_positions.yaml            # 現有（通用配置）
├── taipei_lab_buttons.yaml          # ⚡ 新增：台北實驗室配置
├── taoyuan_lab_buttons.yaml         # ⚡ 新增：桃園實驗室配置
└── rv_car_buttons.yaml              # ⚡ 新增：RV Car 配置
```

### 模組 1: LocalVisionAnalyzer

**檔案**: `libraries/robot_arm_control/LocalVisionAnalyzer.py`

**職責**:
- 本機視覺分析引擎（從 Server 的 `VisionAnalyzer` 遷移）
- 多色彩 HSV 檢測
- 多級亮度檢測
- ArUco 標記校正
- ROI 區域分析

**核心 API**:

```python
class LocalVisionAnalyzer:
    """本機視覺分析引擎

    支援:
    - 多色彩檢測: 藍/白/紅/綠/黃/橙/紫
    - 多級亮度檢測: 0-100% (11 級)
    - 雙影像源: RTSP/Socket
    - ArUco 標記校正
    """

    def __init__(self, image_source_manager: ImageSourceManager):
        """初始化

        Args:
            image_source_manager: 影像源管理器實例
        """
        self.image_source_manager = image_source_manager
        self.color_ranges = self._init_color_ranges()
        self.brightness_thresholds = self._init_brightness_thresholds()

    def detect_panel_light(
        self,
        panel_type: str,
        roi_config: dict,
        image_source_config: dict,
        num_frames: int = 5,
        warmup_frames: int = 20,
        save_debug_images: bool = False
    ) -> dict:
        """檢測面板燈光狀態

        Args:
            panel_type: 面板型號 ("3510a", "3611a", "3611c")
            roi_config: ROI 配置字典
            image_source_config: 影像源配置
            num_frames: 用於平均的幀數
            warmup_frames: 預熱幀數
            save_debug_images: 是否儲存除錯影像

        Returns:
            {
                "light_state": "on" | "off",
                "color": "blue" | "white" | "red" | "green" | None,
                "brightness_level": 0-100,
                "confidence": 0.0-1.0,
                "hsv_mean": [H, S, V],
                "pixel_count": int,
                "raw_data": {...}
            }

        Raises:
            ValueError: 參數錯誤
            RuntimeError: 檢測失敗
        """
        pass

    def detect_physical_light_brightness(
        self,
        roi_config: dict,
        image_source_config: dict,
        num_frames: int = 5,
        warmup_frames: int = 20
    ) -> dict:
        """檢測實體燈光亮度

        Returns:
            {
                "light_state": "on" | "off",
                "brightness_level": 0-100,
                "confidence": 0.0-1.0,
                "raw_brightness": 0-255
            }
        """
        pass

    def _init_color_ranges(self) -> dict:
        """初始化 HSV 顏色範圍

        Returns:
            {
                "blue": {"lower": [100, 50, 50], "upper": [130, 255, 255]},
                "white": {...},
                "red": {...},  # 特殊處理（跨越 0 度）
                "green": {...},
                "yellow": {...},
                "orange": {...},
                "purple": {...}
            }
        """
        pass

    def _init_brightness_thresholds(self) -> dict:
        """初始化 11 級亮度門檻

        Returns:
            {
                0: (0, 25),
                10: (26, 35),
                20: (36, 45),
                ...
                100: (95, 100)
            }
        """
        pass

    def _detect_color_hsv(self, roi_image: np.ndarray) -> tuple:
        """HSV 色彩檢測

        Args:
            roi_image: ROI 影像 (BGR)

        Returns:
            (detected_color: str, confidence: float, hsv_mean: list)
        """
        pass

    def _detect_brightness_level(self, roi_image: np.ndarray) -> tuple:
        """亮度級別檢測

        Args:
            roi_image: ROI 影像 (BGR)

        Returns:
            (brightness_level: int, confidence: float, raw_brightness: int)
        """
        pass
```

**TDD 測試案例**（詳見 `vision_detection_tdd_guide.md`）:
- `test_init_color_ranges`: 驗證 HSV 顏色範圍初始化
- `test_init_brightness_thresholds`: 驗證亮度門檻初始化
- `test_detect_color_blue`: 測試藍色檢測
- `test_detect_color_red`: 測試紅色檢測（跨越 0 度）
- `test_detect_brightness_0_percent`: 測試 0% 亮度
- `test_detect_brightness_100_percent`: 測試 100% 亮度

---

### 模組 2: ImageSourceManager

**檔案**: `libraries/robot_arm_control/ImageSourceManager.py`

**職責**:
- 統一管理雙影像源
- 提供統一的影像擷取介面
- 支援多幀平均截圖

**核心 API**:

```python
class ImageSourceManager:
    """影像源管理器

    統一管理:
    - RTSP 串流
    - USB 攝影機
    - Socket 影像
    """

    def __init__(self):
        """初始化影像源管理器"""
        self.rtsp_source = RTSPImageSource()
        self.usb_source = USBCameraSource()
        self.socket_source = SocketImageSource()
        self.current_source = None
        self.current_config = None

    def set_image_source(self, source_type: str, source_config: dict):
        """設定影像源

        Args:
            source_type: "rtsp" | "socket"
            source_config: 源配置字典
                - RTSP: {"url": "rtsp://...", "timeout": 10}
                - Socket: {"host": "10.42.0.180", "port": 9000}

        Raises:
            ValueError: 不支援的影像源類型
        """
        pass

    def capture_image(
        self,
        num_frames: int = 5,
        warmup_frames: int = 20
    ) -> np.ndarray:
        """擷取影像（多幀平均）

        Args:
            num_frames: 用於平均的幀數
            warmup_frames: 預熱幀數

        Returns:
            平均後的影像 (numpy.ndarray, BGR)

        Raises:
            RuntimeError: 影像源未設定或擷取失敗
        """
        pass

    def capture_single_frame(self) -> np.ndarray:
        """擷取單一幀（用於快速檢測）

        Returns:
            單一幀影像 (numpy.ndarray, BGR)
        """
        pass
```

**影像源實作**:

#### RTSPImageSource

```python
class RTSPImageSource:
    """RTSP 串流影像源

    支援:
    - RTSP 串流擷取
    - 多幀平均
    - 連接重試機制
    """

    def capture_multi_frame(
        self,
        rtsp_url: str,
        num_frames: int,
        warmup_frames: int,
        timeout: int = 10
    ) -> np.ndarray:
        """從 RTSP 串流擷取多幀平均影像

        Args:
            rtsp_url: RTSP URL (e.g., "rtsp://10.42.0.100:554/stream")
            num_frames: 用於平均的幀數
            warmup_frames: 預熱幀數
            timeout: 連接超時（秒）

        Returns:
            平均後的影像

        Raises:
            RuntimeError: 連接失敗或擷取失敗
        """
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            raise RuntimeError(f"無法連接 RTSP 串流: {rtsp_url}")

        # 預熱階段
        for _ in range(warmup_frames):
            cap.read()

        # 多幀平均
        frames = []
        for _ in range(num_frames):
            ret, frame = cap.read()
            if ret and frame is not None:
                frames.append(frame.astype(np.float32))
            time.sleep(0.033)  # ~30fps

        cap.release()

        if not frames:
            raise RuntimeError("無法從 RTSP 串流擷取影像")

        avg_frame = np.mean(frames, axis=0).astype(np.uint8)
        return avg_frame
```

#### SocketImageSource

```python
class SocketImageSource:
    """Socket 影像源（從機器手臂 Server 請求影像）"""

    def request_image(self, host: str, port: int) -> np.ndarray:
        """透過 Socket 請求 Server 傳回原始影像

        Args:
            host: Server IP
            port: Server Port

        Returns:
            影像 (numpy.ndarray, BGR)

        Note:
            需要 Server 支援 "capture_image" 命令
        """
        import socket
        import base64

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        # 發送請求
        command = {"command": "capture_image"}
        sock.sendall(json.dumps(command).encode('utf-8'))

        # 接收回應
        response = sock.recv(1048576)  # 1MB buffer
        sock.close()

        result = json.loads(response.decode('utf-8'))
        if result["status"] != "success":
            raise RuntimeError("Server 影像擷取失敗")

        # 解碼 base64 影像
        image_data = base64.b64decode(result["image"])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return image
```

---

### 模組 3: EnvironmentManager

**檔案**: `config/robot_arm/environment_config.py`

**職責**:
- 管理多環境配置
- 提供環境切換介面
- 載入環境專屬配置

**核心 API**:

```python
class EnvironmentConfig:
    """環境配置管理

    支援環境:
    - taipei_lab: 台北實驗室
    - taoyuan_lab: 桃園實驗室
    - rv_car: RV Car 測試環境
    """

    ENVIRONMENTS = {
        "taipei_lab": {
            "name": "台北實驗室",
            "image_source": "rtsp",
            "rtsp_url": "rtsp://10.42.0.100:554/stream",
            "robot_arm_host": "10.42.0.180",
            "robot_arm_port": 9000,
            "panel_types": ["3510a", "3611a", "3611c"],
            "button_config_path": "config/robot_arm/taipei_lab_buttons.yaml",
            "hsv_adjustments": {
                # 可選：環境專屬 HSV 調整
                "blue": {"lower": [95, 50, 50], "upper": [135, 255, 255]}
            }
        },
        "taoyuan_lab": {
            "name": "桃園實驗室",
            "image_source": "socket",
            "robot_arm_host": "192.168.1.100",
            "robot_arm_port": 9000,
            "panel_types": ["3510a", "3611a"],
            "button_config_path": "config/robot_arm/taoyuan_lab_buttons.yaml",
            "note": "使用 Socket 影像源（從機器手臂 Server 請求影像）"
        },
        "rv_car": {
            "name": "RV Car 測試環境",
            "image_source": "socket",
            "robot_arm_host": "10.42.0.180",
            "robot_arm_port": 9000,
            "panel_types": ["3611c"],
            "button_config_path": "config/robot_arm/rv_car_buttons.yaml"
        }
    }

    @staticmethod
    def get_environment(env_name: str) -> dict:
        """取得環境配置

        Args:
            env_name: 環境名稱

        Returns:
            環境配置字典

        Raises:
            ValueError: 未知環境
        """
        if env_name not in EnvironmentConfig.ENVIRONMENTS:
            available = ", ".join(EnvironmentConfig.ENVIRONMENTS.keys())
            raise ValueError(
                f"未知環境: {env_name}\n"
                f"可用環境: {available}"
            )
        return EnvironmentConfig.ENVIRONMENTS[env_name]

    @staticmethod
    def list_environments() -> list:
        """列出所有環境名稱"""
        return list(EnvironmentConfig.ENVIRONMENTS.keys())

    @staticmethod
    def validate_environment(env_name: str) -> bool:
        """驗證環境是否存在"""
        return env_name in EnvironmentConfig.ENVIRONMENTS
```

---

### 模組 4: EnhancedRobotArmKeywords

**檔案**: `libraries/robot_arm_control/RobotArmKeywords.py`（擴充現有）

**新增關鍵字**:

#### 環境管理關鍵字

```python
@keyword('Given 測試環境設定為 "${environment}"')
def given_test_environment_is(self, environment: str):
    """設定測試環境

    支援環境:
    - taipei_lab: 台北實驗室
    - taoyuan_lab: 桃園實驗室
    - rv_car: RV Car 測試環境

    Args:
        environment: 環境名稱

    Example:
        | Given | 測試環境設定為 "taipei_lab" |

    Raises:
        ValueError: 未知環境
    """
    from config.robot_arm.environment_config import EnvironmentConfig

    env_config = EnvironmentConfig.get_environment(environment)
    self.current_environment = environment
    self.env_config = env_config

    # 初始化影像源
    self.image_source_manager = ImageSourceManager()

    source_type = env_config["image_source"]
    if source_type == "rtsp":
        source_config = {
            "url": env_config["rtsp_url"],
            "timeout": env_config.get("rtsp_timeout", 10)
        }
    elif source_type == "socket":
        source_config = {
            "host": env_config["robot_arm_host"],
            "port": env_config["robot_arm_port"]
        }
    else:
        raise ValueError(f"不支援的影像源: {source_type}")

    self.image_source_manager.set_image_source(source_type, source_config)

    # 初始化視覺分析器
    self.local_vision = LocalVisionAnalyzer(self.image_source_manager)

    # 套用環境專屬 HSV 調整（如果有）
    if "hsv_adjustments" in env_config:
        self.local_vision.update_color_ranges(env_config["hsv_adjustments"])

    logger.info(f"✅ 測試環境已切換至: {env_config['name']}")
    logger.info(f"   影像源: {source_type}")
    logger.info(f"   機器手臂: {env_config['robot_arm_host']}:{env_config['robot_arm_port']}")


@keyword('Given 面板類型設定為 "${panel_type}"')
def given_panel_type_is(self, panel_type: str):
    """設定面板類型

    Args:
        panel_type: 面板型號 ("3510a", "3611a", "3611c")

    Example:
        | Given | 面板類型設定為 "3611a" |

    Raises:
        ValueError: 當前環境不支援該面板類型
    """
    if panel_type not in self.env_config["panel_types"]:
        raise ValueError(
            f"當前環境 '{self.current_environment}' 不支援面板類型: {panel_type}\n"
            f"支援的面板: {', '.join(self.env_config['panel_types'])}"
        )

    self.current_panel_type = panel_type

    # 載入對應的按鈕配置
    config_path = self.env_config["button_config_path"]
    self.button_config = self._load_panel_button_config(config_path, panel_type)

    logger.info(f"✅ 面板類型已設定為: {panel_type}")
    logger.info(f"   載入配置: {config_path}")
```

#### 多色彩檢測關鍵字

```python
@keyword('When 用戶檢測面板按鈕 "${button_id}" 的顏色')
def when_user_detects_panel_button_color(self, button_id: str) -> dict:
    """檢測面板按鈕顏色

    支援顏色: 藍/白/紅/綠/黃/橙/紫

    Args:
        button_id: 按鈕 ID（定義在環境配置中）

    Returns:
        檢測結果字典

    Example:
        | When | 用戶檢測面板按鈕 "light1" 的顏色 |

    Raises:
        ValueError: 按鈕不存在
        RuntimeError: 檢測失敗
    """
    button_config = self._get_button_config(button_id)

    # 先移動機器手臂到觀測角度（如果需要）
    if "observe_angles" in button_config:
        self._move_to_observe_position(button_config["observe_angles"])

    # 本機執行視覺檢測
    result = self.local_vision.detect_panel_light(
        panel_type=self.current_panel_type,
        roi_config=button_config["roi"],
        image_source_config=self.image_source_manager.current_config,
        num_frames=5,
        warmup_frames=20,
        save_debug_images=True  # 儲存除錯影像
    )

    # 儲存結果供 Then 關鍵字驗證
    self.last_detection_result = result

    logger.info(
        f"📸 檢測結果: {result['color']} "
        f"(亮度: {result['brightness_level']}%, 信心度: {result['confidence']:.2f})"
    )

    return result


@keyword('Then 面板按鈕顏色應該為 "${expected_color}"')
def then_panel_button_color_should_be(self, expected_color: str):
    """驗證面板按鈕顏色

    Args:
        expected_color: 預期顏色 ("blue", "white", "red", "green", 等)

    Example:
        | Then | 面板按鈕顏色應該為 "blue" |

    Raises:
        AssertionError: 顏色不符預期
    """
    if not self.last_detection_result:
        raise RuntimeError("尚未執行檢測，請先呼叫 'When 用戶檢測...' 關鍵字")

    actual_color = self.last_detection_result.get("color")
    confidence = self.last_detection_result.get("confidence", 0.0)

    if actual_color != expected_color:
        raise AssertionError(
            f"❌ 面板按鈕顏色不符預期！\n"
            f"   預期: {expected_color}\n"
            f"   實際: {actual_color}\n"
            f"   信心度: {confidence:.2f}\n"
            f"   HSV 平均: {self.last_detection_result.get('hsv_mean')}"
        )

    logger.info(f"✅ 面板按鈕顏色驗證通過: {actual_color} (信心度: {confidence:.2f})")
```

#### 亮度檢測關鍵字

```python
@keyword('When 用戶檢測實體燈光亮度 "${light_id}"')
def when_user_detects_physical_light_brightness(self, light_id: str) -> dict:
    """檢測實體燈光亮度

    支援 11 級亮度: 0%, 10%, 20%, ..., 100%

    Args:
        light_id: 燈光 ID（定義在環境配置中）

    Returns:
        檢測結果字典

    Example:
        | When | 用戶檢測實體燈光亮度 "ceiling_light_1" |

    Raises:
        ValueError: 燈光不存在
        RuntimeError: 檢測失敗
    """
    light_config = self._get_light_config(light_id)

    # 移動機器手臂到觀測位置（如果需要）
    if "observe_angles" in light_config:
        self._move_to_observe_position(light_config["observe_angles"])

    # 本機執行亮度檢測
    result = self.local_vision.detect_physical_light_brightness(
        roi_config=light_config["roi"],
        image_source_config=self.image_source_manager.current_config,
        num_frames=5,
        warmup_frames=20
    )

    self.last_detection_result = result

    logger.info(
        f"💡 檢測結果: {result['brightness_level']}% "
        f"(原始亮度: {result['raw_brightness']}, 信心度: {result['confidence']:.2f})"
    )

    return result


@keyword('Then 實體燈光亮度應該為 "${expected_level}" %')
def then_physical_light_brightness_should_be(self, expected_level: str):
    """驗證實體燈光亮度

    允許 ±10% 誤差範圍

    Args:
        expected_level: 預期亮度百分比 (0-100)

    Example:
        | Then | 實體燈光亮度應該為 "80" % |

    Raises:
        AssertionError: 亮度不符預期
    """
    if not self.last_detection_result:
        raise RuntimeError("尚未執行檢測，請先呼叫 'When 用戶檢測...' 關鍵字")

    expected_level = int(expected_level)
    actual_level = self.last_detection_result.get("brightness_level")

    # 允許 ±10% 誤差
    error_margin = 10
    error = abs(actual_level - expected_level)

    if error > error_margin:
        raise AssertionError(
            f"❌ 實體燈光亮度不符預期！\n"
            f"   預期: {expected_level}%\n"
            f"   實際: {actual_level}%\n"
            f"   誤差: {error}% (允許 ±{error_margin}%)\n"
            f"   原始亮度: {self.last_detection_result.get('raw_brightness')}/255"
        )

    logger.info(
        f"✅ 實體燈光亮度驗證通過: {actual_level}% "
        f"(預期 {expected_level}%, 誤差 {error}%)"
    )
```

---

## 配置系統設計

### 環境配置檔案範例

#### taipei_lab_buttons.yaml

```yaml
# 台北實驗室 - 按鈕配置
environment: "taipei_lab"
panel_types:
  - "3510a"
  - "3611a"
  - "3611c"

# 3611a 面板配置
panels:
  "3611a":
    buttons:
      light1:
        name: "燈光按鈕 1"
        type: "panel_light"
        roi:
          x: 320
          y: 200
          width: 100
          height: 100
        observe_angles: [7.56, -35.59, -37.96, -15.73, -89.29, 6.06]
        aruco_marker_id: 0
        expected_colors: ["blue", "white"]

      light2:
        name: "燈光按鈕 2"
        type: "panel_light"
        roi:
          x: 450
          y: 200
          width: 100
          height: 100
        observe_angles: [10, -30, -40, -15, -90, 5]
        aruco_marker_id: 0
        expected_colors: ["red", "green"]

      bluetooth:
        name: "藍牙按鈕"
        type: "panel_light"
        roi:
          x: 200
          y: 300
          width: 80
          height: 80
        observe_angles: [5, -35, -38, -15, -89, 6]
        aruco_marker_id: 0
        expected_colors: ["blue"]

  "3611c":
    buttons:
      power:
        name: "電源按鈕"
        type: "panel_light"
        roi:
          x: 300
          y: 150
          width: 90
          height: 90
        observe_angles: [8, -36, -38, -16, -88, 7]
        expected_colors: ["blue", "white", "red"]

# 實體燈光配置
physical_lights:
  ceiling_light_1:
    name: "天花板燈 1"
    type: "physical_light"
    roi:
      x: 100
      y: 50
      width: 150
      height: 150
    observe_angles: [0, 0, 0, 0, 0, 0]  # 不需移動機器手臂
    brightness_levels: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

  desk_lamp:
    name: "桌燈"
    type: "physical_light"
    roi:
      x: 400
      y: 100
      width: 120
      height: 120
    observe_angles: [0, 0, 0, 0, 0, 0]
    brightness_levels: [0, 50, 100]  # 僅支援 3 級
```

#### taoyuan_lab_buttons.yaml

```yaml
# 桃園實驗室 - 按鈕配置
environment: "taoyuan_lab"
panel_types:
  - "3510a"
  - "3611a"

# 3611a 面板配置（與 Taipei 可能略有差異）
panels:
  "3611a":
    buttons:
      light1:
        name: "燈光按鈕 1"
        type: "panel_light"
        roi:
          x: 310  # 略有差異（攝影機角度不同）
          y: 210
          width: 100
          height: 100
        observe_angles: [8, -36, -38, -16, -88, 7]
        expected_colors: ["blue", "white"]

      # ... 其他按鈕

# HSV 顏色範圍調整（桃園實驗室光源略暖）
hsv_adjustments:
  blue:
    lower: [95, 50, 50]   # H 稍微放寬
    upper: [135, 255, 255]
  white:
    lower: [0, 0, 190]    # V 閾值降低（較暗）
    upper: [180, 55, 255]
```

#### rv_car_buttons.yaml

```yaml
# RV Car - 按鈕配置
environment: "rv_car"
panel_types:
  - "3611c"

panels:
  "3611c":
    buttons:
      power:
        name: "電源按鈕"
        type: "panel_light"
        roi:
          x: 300
          y: 150
          width: 90
          height: 90
        observe_angles: [0, 0, 0, 0, 0, 0]  # RV Car 可能機器手臂固定
        expected_colors: ["blue", "white", "red"]

      mode:
        name: "模式切換按鈕"
        type: "panel_light"
        roi:
          x: 420
          y: 150
          width: 90
          height: 90
        observe_angles: [0, 0, 0, 0, 0, 0]
        expected_colors: ["green", "red"]
```

---

## 分階段實施計畫

### Phase 1: 本機視覺分析器基礎建設 (2-3 天)

**目標**: 建立核心視覺分析器與影像源管理器

**任務清單**:

1. ✅ **建立 LocalVisionAnalyzer 類別**
   - 從 `robot_arm_server.py` 的 `VisionAnalyzer` 遷移核心邏輯
   - 保留多幀平均截圖功能
   - 保留 HSV 色彩檢測功能
   - 保留 ArUco 標記校正功能
   - **檔案**: `libraries/robot_arm_control/LocalVisionAnalyzer.py`
   - **TDD**: 編寫單元測試（詳見 TDD Guide）

2. ✅ **建立 ImageSourceManager 類別**
   - 實作統一影像源管理介面
   - **檔案**: `libraries/robot_arm_control/ImageSourceManager.py`
   - **TDD**: 測試影像源切換邏輯

3. ✅ **實作 RTSP 影像擷取**
   - 參考 `IPCamLightDetection` 的 RTSP 實作
   - 支援多幀平均
   - 支援連接重試
   - **檔案**: `libraries/robot_arm_control/image_sources/rtsp_source.py`
   - **TDD**: 測試 RTSP 連接與擷取

4. ✅ **實作 Socket 影像源**
   - 透過 Socket 請求 Server 傳回原始影像
   - **檔案**: `libraries/robot_arm_control/image_sources/socket_image_source.py`
   - **Server 端調整**: 新增 `capture_image` 命令

6. ✅ **整合測試**
   - 驗證所有影像源可正常運作
   - 驗證多幀平均邏輯正確
   - **測試案例**: `tests/robot_arm_control/test_image_source_integration.py`

**驗收標準**:
- ✅ LocalVisionAnalyzer 可從 RTSP 擷取影像
- ✅ 多幀平均邏輯與 Server 端一致
- ✅ 單元測試覆蓋率 > 80%

---

### Phase 2: 多色彩與多級亮度檢測 (2-3 天)

**目標**: 擴充色彩檢測能力與亮度級別

**任務清單**:

7. ✅ **擴充 HSV 顏色範圍**
   - 新增紅色檢測（處理 H 跨越 0 度問題）
   - 新增綠色檢測
   - 新增黃色檢測
   - 新增橙色檢測
   - 新增紫色檢測
   - **修改**: `LocalVisionAnalyzer._init_color_ranges()`
   - **TDD**: 每種顏色獨立測試

8. ✅ **實作多級亮度檢測**
   - 定義 11 級亮度門檻 (0-100%)
   - 實作亮度級別判定邏輯
   - **修改**: `LocalVisionAnalyzer._init_brightness_thresholds()`
   - **修改**: `LocalVisionAnalyzer._detect_brightness_level()`
   - **TDD**: 測試每個亮度級別

9. ✅ **實作 detect_panel_light()**
   - 整合色彩檢測 + 亮度檢測
   - 支援多面板類型
   - **TDD**: 測試不同面板類型

10. ✅ **實作 detect_physical_light_brightness()**
    - 專注於實體燈光亮度檢測
    - **TDD**: 測試 0-100% 亮度範圍

11. ✅ **HSV 參數調整工具（可選）**
    - 建立 HSV 參數調整 GUI 工具
    - 快速標定新顏色的 HSV 範圍
    - **檔案**: `scripts/hsv_calibration_tool.py`

**驗收標準**:
- ✅ 支援 7+ 種顏色檢測
- ✅ 支援 11 級亮度檢測
- ✅ 紅色檢測正確處理 H 跨越 0 度
- ✅ 單元測試覆蓋率 > 85%

---

### Phase 3: 環境管理與配置系統 (1-2 天)

**目標**: 建立多環境配置管理系統

**任務清單**:

12. ✅ **建立 EnvironmentConfig 類別**
    - 定義 3 個環境配置（Taipei / Taoyuan / RV Car）
    - **檔案**: `config/robot_arm/environment_config.py`
    - **TDD**: 測試環境取得與驗證

13. ✅ **建立環境專屬 YAML 配置**
    - **檔案**: `config/robot_arm/taipei_lab_buttons.yaml`
    - **檔案**: `config/robot_arm/taoyuan_lab_buttons.yaml`
    - **檔案**: `config/robot_arm/rv_car_buttons.yaml`

14. ✅ **擴充 RobotArmKeywords**
    - 新增 `Given 測試環境設定為 "${environment}"`
    - 新增 `Given 面板類型設定為 "${panel_type}"`
    - **修改**: `libraries/robot_arm_control/RobotArmKeywords.py`
    - **TDD**: 測試環境切換邏輯

15. ✅ **新增多色彩檢測關鍵字**
    - `When 用戶檢測面板按鈕 "${button_id}" 的顏色`
    - `Then 面板按鈕顏色應該為 "${expected_color}"`
    - **TDD**: 測試關鍵字邏輯

16. ✅ **新增亮度檢測關鍵字**
    - `When 用戶檢測實體燈光亮度 "${light_id}"`
    - `Then 實體燈光亮度應該為 "${expected_level}" %`
    - **TDD**: 測試關鍵字邏輯

**驗收標準**:
- ✅ 可透過關鍵字切換 3 個環境
- ✅ 每個環境載入正確的配置檔案
- ✅ 環境專屬 HSV 調整生效
- ✅ 關鍵字文檔完整（Docstring）

---

### Phase 4: Robot Framework 整合測試 (2-3 天)

**目標**: 編寫完整的 Robot Framework 測試案例並進行真機測試

**任務清單**:

17. ✅ **編寫多環境測試案例**
    - **檔案**: `tests/robot_arm/multi_environment_test.robot`
    - 測試台北實驗室 3611a 面板
    - 測試桃園實驗室實體燈光
    - 測試 RV Car 多色彩檢測

18. ✅ **編寫多色彩檢測測試案例**
    - **檔案**: `tests/robot_arm/multi_color_detection_test.robot`
    - 測試藍/白/紅/綠所有顏色

19. ✅ **編寫多級亮度檢測測試案例**
    - **檔案**: `tests/robot_arm/brightness_level_test.robot`
    - 測試 0%, 50%, 100% 亮度

20. ✅ **真機測試與調整**
    - 在實際環境中運行測試
    - 調整 HSV 參數（如需要）
    - 調整亮度門檻（如需要）
    - 記錄測試結果

21. ✅ **性能優化**
    - 優化 RTSP 連接速度
    - 優化多幀平均性能
    - 減少不必要的日誌輸出

22. ✅ **錯誤處理完善**
    - 影像源連接失敗處理
    - 網路超時處理
    - 詳細錯誤訊息

**驗收標準**:
- ✅ 所有 Robot Framework 測試案例通過
- ✅ 真機測試成功率 > 95%
- ✅ 平均檢測時間 < 3 秒（RTSP）
- ✅ 平均檢測時間 < 1 秒（USB）

---

### Phase 5: 文檔與交付 (1 天)

**目標**: 完整文檔與知識轉移

**任務清單**:

23. ✅ **編寫完整文檔**
    - **檔案**: `docs/vision_detection_local_migration_summary.md`
    - 架構說明
    - 使用指南
    - 故障排除

24. ✅ **更新 CLAUDE.md**
    - 新增本機化視覺檢測章節
    - 更新核心命令
    - 更新架構圖

25. ✅ **編寫使用指南**
    - **檔案**: `docs/vision_detection_local_usage_guide.md`
    - 快速開始
    - 環境設定
    - 常見問題

26. ✅ **編寫 API 文檔**
    - 使用 libdoc 產生 Robot Framework 關鍵字文檔
    - 使用 Sphinx 產生 Python API 文檔

27. ✅ **範例專案**
    - **目錄**: `examples/vision_detection/`
    - 簡單範例
    - 進階範例
    - 多環境範例

**驗收標準**:
- ✅ 文檔完整且易懂
- ✅ 新手可根據文檔完成設置
- ✅ API 文檔自動產生
- ✅ 範例專案可執行

---

## 測試策略

### TDD 開發流程

遵循 **Test-Driven Development (TDD)** 原則：

```
1. 編寫測試 (Red) → 2. 實作功能 (Green) → 3. 重構 (Refactor)
```

詳細測試案例請參閱 [TDD 開發指南](vision_detection_tdd_guide.md)

### 測試金字塔

```
         ╱╲
        ╱  ╲      E2E 測試 (10%)
       ╱────╲     - Robot Framework 整合測試
      ╱      ╲    - 真機測試
     ╱────────╲
    ╱          ╲  整合測試 (30%)
   ╱────────────╲ - 影像源整合測試
  ╱              ╲- 環境配置測試
 ╱────────────────╲
╱                  ╲ 單元測試 (60%)
────────────────────- LocalVisionAnalyzer
                     - ImageSourceManager
                     - EnvironmentConfig
```

### 單元測試（60%）

**測試框架**: pytest

**測試檔案**:
- `tests/robot_arm_control/test_local_vision_analyzer.py`
- `tests/robot_arm_control/test_image_source_manager.py`
- `tests/robot_arm_control/test_color_detection.py`
- `tests/robot_arm_control/test_brightness_detection.py`

**測試範圍**:
- HSV 顏色範圍初始化
- 亮度門檻初始化
- 色彩檢測邏輯
- 亮度檢測邏輯
- ArUco 校正邏輯
- 影像源切換邏輯

**測試策略**:
- 使用模擬影像（不依賴真實硬體）
- 使用已知 HSV 值的測試圖片
- 使用 pytest fixtures 管理測試資料

### 整合測試（30%）

**測試檔案**:
- `tests/robot_arm_control/test_image_source_integration.py`
- `tests/robot_arm_control/test_environment_integration.py`

**測試範圍**:
- RTSP 影像擷取與分析
- USB Camera 影像擷取與分析
- 環境切換完整流程
- 配置載入與套用

**測試策略**:
- 使用真實 RTSP 串流（測試環境）
- 使用 USB 攝影機（如果可用）
- 驗證端到端流程

### E2E 測試（10%）

**測試框架**: Robot Framework

**測試檔案**:
- `tests/robot_arm/multi_environment_test.robot`
- `tests/robot_arm/multi_color_detection_test.robot`
- `tests/robot_arm/brightness_level_test.robot`

**測試範圍**:
- 完整的業務流程測試
- 真實環境測試
- 多環境切換測試

**測試策略**:
- 在實際環境中運行
- 驗證所有關鍵字正常運作
- 記錄真實性能數據

---

## 風險管理

### 技術風險

#### 風險 1: RTSP 串流不穩定

**描述**: RTSP 串流可能因網路問題導致連接失敗或影像延遲

**影響**: 中等

**緩解措施**:
- 實作連接重試機制（最多 3 次）
- 設定合理超時時間（10 秒）
- 提供備用影像源（USB Camera）
- 詳細錯誤日誌

**應急計畫**:
- 如果 RTSP 連接失敗，自動切換到 USB Camera
- 提供手動切換影像源的關鍵字

#### 風險 2: HSV 參數在不同環境差異大

**描述**: 不同實驗室的光源可能導致 HSV 參數需大幅調整

**影響**: 高

**緩解措施**:
- 支援環境專屬 HSV 調整（在 YAML 配置中）
- 提供 HSV 參數調整工具
- 詳細文檔說明如何標定 HSV 參數

**應急計畫**:
- 建立 HSV 參數資料庫（記錄各環境最佳參數）
- 提供視覺化工具輔助調整

#### 風險 3: 多幀平均性能問題

**描述**: RTSP 多幀平均可能較慢（網路延遲）

**影響**: 中等

**緩解措施**:
- 提供可配置的幀數（預設 5 幀，可調整為 3 幀）
- 優化影像擷取邏輯（減少等待時間）
- 使用 FFmpeg 硬體加速（如果可用）

**應急計畫**:
- 提供快速模式（單幀檢測，犧牲準確度）
- 針對不同影像源提供不同預設參數

### 專案風險

#### 風險 4: 向後相容性問題

**描述**: 遷移可能影響現有測試案例

**影響**: 低

**緩解措施**:
- 保留所有現有關鍵字（向後相容）
- 現有測試案例無需修改即可運行
- 新功能透過新關鍵字提供

**驗證方法**:
- 運行所有現有測試案例
- 確保通過率 100%

#### 風險 5: 文檔不足導致使用困難

**描述**: 新架構複雜度增加，文檔不足導致使用困難

**影響**: 中等

**緩解措施**:
- 詳細的使用指南
- 豐富的範例專案
- 完整的 API 文檔
- FAQ 章節

**應急計畫**:
- 提供 1-1 使用培訓
- 建立內部知識庫

---

## 驗收標準

### 功能驗收標準

#### 1. 本機視覺分析器

- ✅ 支援 RTSP 影像擷取
- ✅ 支援 USB Camera 影像擷取
- ✅ 支援 Socket 影像擷取（可選）
- ✅ 支援多幀平均截圖
- ✅ 支援 ArUco 標記校正

#### 2. 多色彩檢測

- ✅ 支援至少 7 種顏色：藍、白、紅、綠、黃、橙、紫
- ✅ 紅色檢測正確處理 H 跨越 0 度
- ✅ 色彩檢測信心度 > 0.9（在理想條件下）

#### 3. 多級亮度檢測

- ✅ 支援 11 級亮度：0%, 10%, 20%, ..., 100%
- ✅ 亮度檢測允許 ±10% 誤差
- ✅ 亮度檢測信心度 > 0.85

#### 4. 多環境支援

- ✅ 支援台北實驗室配置
- ✅ 支援桃園實驗室配置
- ✅ 支援 RV Car 配置
- ✅ 一行關鍵字即可切換環境

#### 5. Robot Framework 整合

- ✅ 新增至少 6 個新關鍵字
- ✅ 保留所有現有 26 個關鍵字
- ✅ 所有關鍵字遵循 BDD 風格
- ✅ 所有關鍵字有完整 Docstring

### 測試驗收標準

#### 1. 單元測試

- ✅ 單元測試覆蓋率 > 80%
- ✅ 所有單元測試通過
- ✅ 測試執行時間 < 1 分鐘

#### 2. 整合測試

- ✅ 所有整合測試通過
- ✅ RTSP 連接成功率 > 95%

#### 3. Robot Framework 測試

- ✅ 所有現有測試案例通過（向後相容）
- ✅ 所有新測試案例通過
- ✅ 真機測試成功率 > 95%

### 性能驗收標準

#### 1. 影像擷取性能

- ✅ RTSP 單次擷取時間 < 2 秒
- ✅ 多幀平均（5 幀）時間 < 3 秒（RTSP）

#### 2. 檢測性能

- ✅ 色彩檢測時間 < 0.5 秒
- ✅ 亮度檢測時間 < 0.3 秒
- ✅ 完整檢測流程 < 5 秒（含機器手臂移動）

### 文檔驗收標準

#### 1. 使用文檔

- ✅ 完整的遷移計畫文檔
- ✅ 完整的技術規格文檔
- ✅ 完整的 TDD 開發指南
- ✅ 完整的使用指南

#### 2. API 文檔

- ✅ Robot Framework 關鍵字文檔（libdoc）
- ✅ Python API 文檔（Sphinx）
- ✅ 所有公開 API 有 Docstring

#### 3. 範例專案

- ✅ 至少 3 個完整範例
- ✅ 範例可直接執行
- ✅ 範例涵蓋主要使用場景

---

## 總結

本遷移計畫旨在將影像判定功能從 MyCobot 280 Jetson Nano Server 遷移至 Ubuntu 本機端，提升測試效率、降低維護成本、擴充檢測能力。

**關鍵優勢**:
- 🚀 **低延遲**: 本機執行，減少網路傳輸
- 🎨 **多色彩**: 支援 7+ 種顏色檢測
- 💡 **多亮度**: 支援 11 級亮度檢測
- 🌍 **多環境**: 統一介面，配置驅動
- 📹 **雙影像源**: RTSP / Socket 兩種來源
- 🔧 **易維護**: 詳細日誌、除錯影像、HSV 調整工具

**實施時程**: 8-12 天（5 個 Phase）

**風險等級**: 中等（已有完善緩解措施）

**投資回報**: 高（長期節省測試時間與維護成本）

---

**文件版本歷史**:
- v1.0.0 (2025-11-16): 初版建立
