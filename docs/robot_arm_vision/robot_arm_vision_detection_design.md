# 機器手臂視覺檢測系統設計文檔

**文檔版本：** v1.0.0
**建立日期：** 2025-11-13
**專案：** robot-multiplatform-automation
**目標：** 整合視覺檢測功能到 robot_arm_server.py，實現按鈕燈光狀態檢測

---

## 📋 需求概述

### 核心需求
1. **機器手臂末端攝影機** - 觀測目標面板上的按鈕燈光
2. **檢測能力** - 區分藍色/白色/關閉三種狀態
3. **LED 掃描頻率處理** - 解決 LED 與攝影機同步問題
4. **單檔案整合** - 所有功能整合到 `robot_arm_server.py`（可接受 1000+ 行）
5. **Jetson Nano GPU 加速** - 本地處理，減少網路傳輸
6. **JSON over Socket** - 不使用 HTTP，純 Socket 通訊

### 系統環境
- **機器手臂：** MyCobot 280
- **運算平台：** Jetson Nano（10.42.0.180:9000）
- **攝影機：** /dev/video0（安裝於機器手臂末端）
- **面板配置：** 20 個按鈕（已有精確角度配置）
- **測試框架：** Robot Framework

---

## 🏗️ 系統架構

### 架構設計原則

**關鍵決策：客戶端管理配置，伺服器只執行命令**

- ✅ **伺服器 (Jetson Nano)：** 無狀態執行器，不讀取/儲存配置
- ✅ **客戶端 (測試機)：** 配置管理者，維護唯一的 `button_positions.yaml`
- ✅ **通訊協議：** JSON over Socket，客戶端傳入完整參數（ROI、角度等）
- ✅ **責任分離：** 伺服器=執行器，客戶端=控制器
- ✅ **單一真實來源：** 配置檔只有一份，避免同步問題

### 整體架構圖

```
┌─────────────────────────────────────────────────────────┐
│  Jetson Nano (10.42.0.180)                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │  robot_arm_server.py (單一檔案)                    │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Socket Server (Port 9000)                   │ │ │
│  │  │  - 二進制命令（機器手臂控制）                  │ │
│  │  │  - JSON 命令（視覺檢測）                       │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  VisionAnalyzer (視覺分析引擎)                │ │
│  │  │  - 多幀截圖與平均（解決 LED 掃描）            │ │
│  │  │  - HSV 顏色檢測（藍/白/關）                   │ │
│  │  │  - ROI 區域分析                               │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Serial Controller (串口控制)                 │ │
│  │  │  - /dev/ttyTHS1                               │ │
│  │  │  - 機器手臂移動控制                            │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  Camera Handler (攝影機控制)                  │ │
│  │  │  - /dev/video0                                │ │
│  │  │  - 線程安全的截圖                              │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                     │ │
│  │  ⚠️ 不讀取、不儲存任何配置檔案                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           ↕ Socket (JSON 含完整參數 / Binary)
┌─────────────────────────────────────────────────────────┐
│  Ubuntu 24.04 測試機 - 配置管理者                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  config/robot_arm/button_positions.yaml            │ │
│  │  - 唯一的配置來源                                   │ │
│  │  - 包含所有按鈕的 ROI、角度、閾值                   │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  calibrate_button_roi.py (校準工具)                │ │
│  │  - 連接伺服器進行截圖                               │ │
│  │  - 人工框選 ROI                                     │ │
│  │  - 直接更新本地 button_positions.yaml              │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Robot Framework + RobotArmKeywords                │ │
│  │  - 讀取 button_positions.yaml                      │ │
│  │  - 組裝完整的 JSON 命令（含 ROI）                   │ │
│  │  - 發送到伺服器執行                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 配置管理流程

#### **校準階段（一次性）：**
```
測試機 ──JSON: move_to_angles──> Jetson Nano
       <──────────────────────── (移動完成)

測試機 ──JSON: capture_image──> Jetson Nano
       <──Base64 圖像───────────

測試機: cv2.selectROI() (人工框選)
       ↓
測試機: 更新本地 button_positions.yaml
       (伺服器完全不知道 ROI 資訊)
```

#### **檢測階段（日常使用）：**
```
測試機: 讀取 button_positions.yaml
       ├─ ROI 座標
       ├─ 觀測角度
       └─ 亮度閾值
       ↓
測試機 ──JSON: detect_button──> Jetson Nano
       (含完整參數)               執行檢測
                                 (使用客戶端提供的 ROI)
       <──JSON: 檢測結果────────
```

---

## 🔧 核心模組設計

### 1. VisionAnalyzer 類別

**職責：** 視覺分析引擎，處理圖像並檢測按鈕狀態

```python
class VisionAnalyzer:
    """視覺分析引擎（藍/白/關 LED 檢測）"""

    def __init__(self, camera_device="/dev/video0"):
        """初始化視覺分析器

        Args:
            camera_device: 攝影機設備路徑
        """
        self.camera_device = camera_device
        self.camera_lock = threading.Lock()
        self.logger = logging.getLogger("VisionAnalyzer")

    def capture_multi_frame_average(self, num_frames=5) -> np.ndarray:
        """多幀平均截圖（解決 LED 掃描頻率問題）

        LED 與攝影機掃描不同步會導致閃爍或暗幀。
        透過多幀平均可以穩定檢測結果。

        Args:
            num_frames: 平均幀數（預設 5 幀）

        Returns:
            平均後的圖像 (numpy.ndarray)
        """
        pass

    def detect_button_state(self, image: np.ndarray, roi_config: dict) -> dict:
        """檢測單一按鈕狀態

        Args:
            image: 輸入圖像
            roi_config: ROI 配置 {"x": int, "y": int, "width": int, "height": int}

        Returns:
            {
                "light": "on" | "off",
                "color": "blue" | "white" | "off",
                "brightness": 0-255,
                "confidence": 0.0-1.0,
                "debug_info": {
                    "blue_ratio": float,
                    "white_ratio": float
                }
            }
        """
        pass

    def _extract_roi(self, image: np.ndarray, roi_config: dict) -> np.ndarray:
        """提取 ROI 區域"""
        pass

    def _detect_brightness(self, roi: np.ndarray) -> float:
        """檢測亮度（HSV V 通道）"""
        pass

    def _detect_color_hsv(self, roi: np.ndarray) -> Tuple[str, float]:
        """HSV 顏色檢測（藍 vs 白）

        Returns:
            (color_name, confidence)
        """
        pass
```

---

### 2. MycobotServer 擴展

**新增功能：**
1. 載入按鈕配置（YAML）
2. 處理 JSON 命令
3. 整合視覺分析

```python
class MycobotServer(object):

    def __init__(self, ...,
                 enable_vision=True,
                 button_config_path="config/robot_arm/button_positions.yaml"):
        """
        新增參數:
            enable_vision: 是否啟用視覺檢測
            button_config_path: 按鈕配置檔路徑
        """
        # ... 原有初始化 ...

        # 新增：視覺分析器
        if enable_vision:
            self.vision_analyzer = VisionAnalyzer(camera_device)
            self.button_config = self._load_button_config(button_config_path)
        else:
            self.vision_analyzer = None
            self.button_config = None

    def _load_button_config(self, config_path: str) -> dict:
        """載入按鈕配置（YAML）"""
        pass

    def connect(self):
        """主連接循環（擴展以支援 JSON）"""
        while self.is_running:
            # ... 原有的 accept 邏輯 ...

            while self.is_running:
                data = conn.recv(4096)  # 增加緩衝區（JSON 較大）

                if not data:
                    break

                # 1. 嘗試解析為 JSON
                try:
                    json_cmd = json.loads(data.decode('utf-8'))
                    if 'command' in json_cmd:
                        result = self._handle_json_command(json_cmd)
                        response = json.dumps(result, ensure_ascii=False)
                        conn.sendall(response.encode('utf-8'))
                        continue
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass  # 不是 JSON，繼續當二進制處理

                # 2. 原有的二進制命令處理
                command = list(data)
                # ... 原有邏輯 ...

    def _handle_json_command(self, cmd: dict) -> dict:
        """處理 JSON 命令"""
        command_type = cmd.get('command')

        if command_type == 'detect_button':
            return self._cmd_detect_button(cmd)
        elif command_type == 'detect_all_buttons':
            return self._cmd_detect_all_buttons(cmd)
        elif command_type == 'move_to_angles':
            return self._cmd_move_to_angles(cmd)
        elif command_type == 'capture_image':
            return self._cmd_capture_image(cmd)
        else:
            return {"status": "error", "message": f"Unknown command: {command_type}"}

    def _cmd_detect_button(self, cmd: dict) -> dict:
        """檢測單一按鈕狀態

        命令格式:
            {
                "command": "detect_button",
                "button_id": "light3",
                "auto_move": true,  # 是否自動移動到觀測位置
                "num_frames": 5      # 平均幀數（可選）
            }

        回應格式:
            {
                "status": "success" | "error",
                "button_id": "light3",
                "result": {
                    "light": "on",
                    "color": "blue",
                    "brightness": 180,
                    "confidence": 0.85
                },
                "timestamp": "2025-11-13T10:30:00"
            }
        """
        pass

    def _cmd_detect_all_buttons(self, cmd: dict) -> dict:
        """檢測所有按鈕（批次）"""
        pass

    def _cmd_move_to_angles(self, cmd: dict) -> dict:
        """移動到指定角度（用於校準工具）"""
        pass

    def _cmd_capture_image(self, cmd: dict) -> dict:
        """截圖並返回 Base64 編碼（用於除錯）"""
        pass
```

---

## 📐 配置檔案設計

### button_positions.yaml 擴展

```yaml
# 全局視覺配置
vision:
  camera_device: "/dev/video0"
  default_num_frames: 5          # 預設平均幀數
  default_brightness_threshold: 100
  capture_delay: 0.5              # 移動後等待時間（秒）

buttons:
  light3:
    name: "Light3 按鈕"
    description: "燈光控制 3"
    down_angles: [13, -58, -85, 23.8, 0, 0]
    up_angles: [13, -35, -85, 23.8, 0, 0]
    speed: 100

    # ===== 視覺檢測配置（由校準工具產生）=====
    vision:
      # 觀測位置（通常使用 up_angles）
      observe_angles: [13, -35, -85, 23.8, 0, 0]

      # ROI 區域座標（校準工具產生）
      roi:
        x: 285
        y: 210
        width: 75
        height: 75

      # 檢測參數
      brightness_threshold: 100     # 亮度閾值（區分開/關）
      expected_colors: [blue, white, off]  # 預期顏色

      # HSV 顏色範圍（可選，使用預設值）
      hsv_ranges:
        blue:
          lower: [100, 50, 50]
          upper: [130, 255, 255]
        white:
          lower: [0, 0, 200]
          upper: [180, 50, 255]
```

---

## 🎨 視覺檢測演算法

### 技術方案選擇：HSV vs YOLO

#### **方案對比**

| 維度 | 傳統 CV (HSV) ✅ 採用 | YOLO ❌ 不採用 |
|------|---------------------|---------------|
| **準確率** | 95%+ (穩定環境) | 98%+ (任何環境) |
| **開發時間** | 2-3 小時 | 1-2 週 |
| **訓練成本** | 無需訓練 | 需收集 500+ 張標註圖片 |
| **推理速度** | ~5ms (CPU) | ~50-100ms (Jetson Nano) |
| **記憶體使用** | ~50MB | ~500MB-1GB |
| **維護成本** | 低（調整閾值） | 中（重新訓練） |
| **環境適應性** | 中（需穩定光源） | 高（自動適應） |

#### **選擇 HSV 的理由**

1. **問題複雜度低：** 已知按鈕位置（ROI），只需三分類（藍/白/關）
2. **環境穩定：** 固定面板 + 穩定光源 + 固定相機角度
3. **開發效率：** 3 小時 vs 2 週
4. **性能優勢：** 11ms vs 100ms（快 9 倍）
5. **維護簡單：** 調整閾值 vs 重新訓練模型
6. **符合 KISS 原則：** Keep It Simple, Stupid

#### **YOLO 適用場景（本專案不適用）**

- ❌ 需要在複雜背景中找出按鈕（本專案已有精確位置）
- ❌ 需要同時檢測多種不同物體（本專案只檢測按鈕）
- ❌ 物體形狀、位置變化大（本專案按鈕位置固定）
- ❌ 環境光源不穩定（本專案光源穩定）

#### **風險管理**

如果 HSV 方案準確率 < 90%，Phase 5 提供以下備用方案：
- **改進策略 A：** 自適應 HSV（白平衡、動態閾值）
- **改進策略 B：** 輕量級 CNN 分類器（非 YOLO）
- **改進策略 C：** 混合方案（HSV + CNN）

---

### 1. LED 掃描頻率問題處理

**問題：**
- LED PWM 調光頻率：~100-200 Hz
- 攝影機幀率：30 FPS
- 不同步導致亮度不穩定

**解決方案：多幀平均**

```python
def capture_multi_frame_average(self, num_frames=5):
    """
    拍攝多幀圖像並平均，消除 LED 閃爍

    時間成本: 5 幀 @ 30 FPS ≈ 0.17 秒（可接受）
    """
    cap = cv2.VideoCapture(self.camera_device)

    # 設定攝影機參數
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    frames = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            frames.append(frame.astype(np.float32))
        time.sleep(0.01)  # 短暫延遲

    cap.release()

    if not frames:
        raise RuntimeError("無法截取圖像")

    # 平均所有幀
    avg_frame = np.mean(frames, axis=0).astype(np.uint8)
    return avg_frame
```

---

### 2. 藍/白/關 顏色檢測

**HSV 色彩空間優勢：**
- 對光照變化不敏感
- 易於定義顏色範圍
- V 通道直接表示亮度

**檢測流程：**

```
輸入圖像
    ↓
提取 ROI
    ↓
轉 HSV
    ↓
檢測亮度 (V 通道平均) ──→ 低於閾值? ──→ [關閉]
    ↓ 否
建立顏色遮罩
    ├─ 藍色遮罩 (H: 100-130)
    └─ 白色遮罩 (S: 0-50, V: 200-255)
    ↓
計算像素比例
    ↓
選擇最高比例 ──→ [藍色 / 白色 / 未知]
```

**程式碼：**

```python
def _detect_color_hsv(self, roi: np.ndarray) -> Tuple[str, float]:
    """HSV 顏色檢測"""
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    total_pixels = roi.shape[0] * roi.shape[1]

    # 藍色檢測
    blue_lower = np.array([100, 50, 50])
    blue_upper = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    blue_ratio = cv2.countNonZero(blue_mask) / total_pixels

    # 白色檢測（低飽和度 + 高亮度）
    white_lower = np.array([0, 0, 200])
    white_upper = np.array([180, 50, 255])
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    white_ratio = cv2.countNonZero(white_mask) / total_pixels

    # 判斷邏輯
    confidence_threshold = 0.3  # 至少 30% 像素符合

    if blue_ratio > white_ratio and blue_ratio > confidence_threshold:
        return "blue", blue_ratio
    elif white_ratio > confidence_threshold:
        return "white", white_ratio
    else:
        return "unknown", max(blue_ratio, white_ratio)
```

---

## 🛠️ ROI 校準工具設計

### calibrate_button_roi.py

**功能：**
1. 連接機器手臂（Socket JSON）
2. 依序移動到每個按鈕上方
3. 截圖並顯示
4. 使用者用滑鼠框選 ROI
5. 自動更新 `button_positions.yaml`

**使用流程：**

```bash
# 1. 啟動機器手臂伺服器（Jetson Nano）
ssh jetson@10.42.0.180
python3 scripts/robot_arm_server.py --enable-vision

# 2. 執行校準工具（測試機）
python3 scripts/calibrate_button_roi.py

# 輸出範例：
# ====================================
# 按鈕 ROI 校準工具 v1.0
# ====================================
# 連接到: 10.42.0.180:9000
# 載入配置: config/robot_arm/button_positions.yaml
# 找到 20 個按鈕
#
# [1/20] 校準按鈕: bluetooth (Bluetooth 按鈕)
#   → 移動到觀測位置...
#   → 等待穩定 (1.0 秒)...
#   → 截圖中...
#   → 請框選按鈕區域
#   ✅ ROI 已儲存: {"x": 280, "y": 200, "width": 80, "height": 80}
#
# [2/20] 校準按鈕: aux2 (AUX2 按鈕)
#   ...
#
# ====================================
# 校準完成！
# ====================================
# 已更新配置: config/robot_arm/button_positions.yaml
# 備份檔案: config/robot_arm/button_positions.yaml.backup
```

**核心功能：**

```python
class ButtonROICalibrator:
    def __init__(self, robot_ip="10.42.0.180", robot_port=9000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((robot_ip, robot_port))

    def send_json_command(self, cmd: dict) -> dict:
        """發送 JSON 命令並接收回應"""
        self.socket.sendall(json.dumps(cmd).encode('utf-8'))
        response = self.socket.recv(4096)
        return json.loads(response.decode('utf-8'))

    def move_and_capture(self, button_id: str, angles: List[float]):
        """移動並截圖"""
        # 1. 移動
        self.send_json_command({
            "command": "move_to_angles",
            "angles": angles,
            "speed": 50
        })
        time.sleep(1.0)  # 等待穩定

        # 2. 截圖（返回 Base64）
        result = self.send_json_command({
            "command": "capture_image",
            "format": "base64"
        })

        # 3. 解碼圖像
        img_data = base64.b64decode(result['image'])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image

    def select_roi_interactive(self, image, button_name):
        """互動式 ROI 選擇（OpenCV selectROI）"""
        print(f"\n框選 {button_name} 的 ROI 區域")
        print("提示: 滑鼠拖曳框選，Enter 確認，C 取消")

        roi = cv2.selectROI(f"校準 - {button_name}", image, fromCenter=False)
        cv2.destroyAllWindows()

        if roi[2] > 0 and roi[3] > 0:
            return {
                "x": int(roi[0]),
                "y": int(roi[1]),
                "width": int(roi[2]),
                "height": int(roi[3])
            }
        return None

    def save_to_yaml(self, config_path, roi_data):
        """儲存 ROI 到 YAML（保留註解）"""
        # 使用 ruamel.yaml 保留註解和格式
        pass
```

---

## 📝 JSON 命令協議規範

### 1. detect_button - 檢測單一按鈕

**請求：**
```json
{
  "command": "detect_button",
  "button_id": "light3",
  "auto_move": true,
  "num_frames": 5
}
```

**回應（成功）：**
```json
{
  "status": "success",
  "button_id": "light3",
  "result": {
    "light": "on",
    "color": "blue",
    "brightness": 180,
    "confidence": 0.85,
    "debug_info": {
      "blue_ratio": 0.85,
      "white_ratio": 0.12
    }
  },
  "timestamp": "2025-11-13T10:30:00"
}
```

**回應（失敗）：**
```json
{
  "status": "error",
  "message": "按鈕 'light99' 不存在於配置檔",
  "timestamp": "2025-11-13T10:30:00"
}
```

---

### 2. detect_all_buttons - 批次檢測

**請求：**
```json
{
  "command": "detect_all_buttons",
  "buttons": ["light1", "light2", "light3"],  // 可選，預設全部
  "auto_move": true
}
```

**回應：**
```json
{
  "status": "success",
  "results": {
    "light1": {
      "light": "off",
      "color": "off",
      "brightness": 45,
      "confidence": 1.0
    },
    "light2": {
      "light": "on",
      "color": "white",
      "brightness": 220,
      "confidence": 0.92
    },
    "light3": {
      "light": "on",
      "color": "blue",
      "brightness": 180,
      "confidence": 0.85
    }
  },
  "total_buttons": 3,
  "timestamp": "2025-11-13T10:30:05"
}
```

---

### 3. move_to_angles - 移動到指定角度

**請求：**
```json
{
  "command": "move_to_angles",
  "angles": [13, -35, -85, 23.8, 0, 0],
  "speed": 50
}
```

**回應：**
```json
{
  "status": "success",
  "message": "已移動到目標位置"
}
```

---

### 4. capture_image - 截圖（除錯用）

**請求：**
```json
{
  "command": "capture_image",
  "format": "base64",      // "base64" | "file"
  "num_frames": 5          // 可選
}
```

**回應：**
```json
{
  "status": "success",
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",  // Base64 編碼
  "format": "jpeg",
  "width": 640,
  "height": 480
}
```

---

## 🧪 測試計畫

### 單元測試

```python
# tests/test_vision_analyzer.py
import unittest
import cv2
import numpy as np
from scripts.robot_arm_server import VisionAnalyzer

class TestVisionAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = VisionAnalyzer()

    def test_detect_blue_led(self):
        """測試藍色 LED 檢測"""
        # 建立藍色測試圖像
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [255, 0, 0]  # BGR 藍色

        color, confidence = self.analyzer._detect_color_hsv(test_image)
        self.assertEqual(color, "blue")
        self.assertGreater(confidence, 0.8)

    def test_detect_white_led(self):
        """測試白色 LED 檢測"""
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        color, confidence = self.analyzer._detect_color_hsv(test_image)
        self.assertEqual(color, "white")

    def test_detect_off_led(self):
        """測試關閉狀態"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        brightness = self.analyzer._detect_brightness(test_image)
        self.assertLess(brightness, 50)
```

---

### Robot Framework 整合測試

```robotframework
*** Settings ***
Library    RobotArmKeywords    10.42.0.180    9000
Library    Collections

*** Test Cases ***
檢測單一按鈕狀態
    [Documentation]    測試 light3 按鈕的視覺檢測
    [Tags]    vision    single_button

    # 按下按鈕（應該會亮藍燈）
    按下按鈕    light3
    Sleep    1s

    # 檢測狀態
    ${result}=    檢測按鈕狀態    light3

    # 驗證
    Should Be Equal    ${result['light']}    on
    Should Be Equal    ${result['color']}    blue
    Should Be True    ${result['brightness']} > 100

    Log    檢測結果: ${result}

批次檢測所有燈光按鈕
    [Documentation]    批次檢測 8 個燈光按鈕
    [Tags]    vision    batch

    @{light_buttons}=    Create List
    ...    light1    light2    light3    light4
    ...    light5    light6    light7    light8

    # 批次檢測
    ${results}=    檢測多個按鈕    ${light_buttons}

    # 驗證每個按鈕
    FOR    ${button_id}    IN    @{light_buttons}
        ${state}=    Get From Dictionary    ${results}    ${button_id}
        Should Be True    '${state['color']}' in ['blue', 'white', 'off']
    END

燈光切換驗證
    [Documentation]    測試按鈕切換後的狀態變化
    [Tags]    vision    toggle

    # 1. 檢測初始狀態
    ${state_before}=    檢測按鈕狀態    light1
    Log    初始狀態: ${state_before}

    # 2. 按下按鈕
    按下按鈕    light1
    Sleep    1s

    # 3. 檢測變化後狀態
    ${state_after}=    檢測按鈕狀態    light1
    Log    變化後狀態: ${state_after}

    # 4. 驗證狀態已改變
    Should Not Be Equal    ${state_before['light']}    ${state_after['light']}
```

---

## 📊 性能指標

### 目標性能

| 指標 | 目標值 | 備註 |
|------|--------|------|
| 單一按鈕檢測時間 | < 2 秒 | 含移動 + 截圖 + 分析 |
| 批次檢測（20 按鈕） | < 40 秒 | 平均每個 2 秒 |
| 顏色檢測準確率 | > 95% | 穩定光源環境 |
| LED 閃爍誤判率 | < 5% | 使用 5 幀平均 |
| 記憶體使用 | < 500 MB | Jetson Nano 4GB |

### 效能優化策略

1. **GPU 加速（未來優化）**
   - OpenCV CUDA 編譯
   - GStreamer pipeline

2. **快取機制**
   - 攝影機參數快取
   - 按鈕配置快取

3. **並行處理**
   - 多執行緒截圖
   - 批次檢測使用執行緒池

---

## 🔒 錯誤處理

### 錯誤類型與處理

| 錯誤類型 | 處理策略 | 回應格式 |
|---------|---------|---------|
| 按鈕不存在 | 返回錯誤訊息 | `{"status": "error", "message": "..."}` |
| 攝影機無法開啟 | 重試 3 次，失敗返回錯誤 | 同上 |
| ROI 配置缺失 | 使用預設值或返回錯誤 | 同上 |
| 移動失敗 | 串口錯誤處理（原有機制） | 同上 |
| JSON 解析失敗 | 當作二進制命令處理 | N/A（降級處理）|

---

## 📁 檔案結構

```
robot-multiplatform-automation/
├── scripts/
│   ├── robot_arm_server.py              # 主伺服器（1000+ 行，含視覺檢測）
│   ├── calibrate_button_roi.py          # ROI 校準工具（新建）
│   └── test_vision_detection.py         # 視覺檢測測試腳本（新建）
│
├── config/robot_arm/
│   ├── button_positions.yaml            # 按鈕配置（擴展 vision 區塊）
│   └── button_positions.yaml.backup     # 校準前備份
│
├── libraries/robot_arm_control/
│   ├── RobotArmKeywords.py              # 擴展支援 JSON 命令
│   └── vision_keywords.py               # 視覺檢測關鍵字（新建）
│
├── tests/robot_arm/
│   ├── vision_detection_test.robot      # 視覺檢測測試案例（新建）
│   └── button_light_toggle_test.robot   # 燈光切換測試（新建）
│
└── docs/
    ├── robot_arm_vision_detection_design.md       # 本文檔
    └── robot_arm_vision_calibration_guide.md     # 校準操作指南（待建立）
```

---

## 🚀 實作階段規劃

### Phase 1: 核心視覺檢測（2-3 小時）- HSV 方案 ✅ 完成
- [x] 設計文檔完成
- [x] 實作 `VisionAnalyzer` 類別
  - [x] 多幀平均截圖（解決 LED 掃描頻率）
  - [x] HSV 顏色檢測（藍/白/關）
  - [x] ROI 提取與亮度檢測
- [x] 擴展 `MycobotServer` 支援 JSON 命令
  - [x] JSON 命令解析（與二進制命令並存）
  - [x] 實作 `detect_button` 命令（客戶端提供 ROI）
  - [x] 實作 `move_to_angles` 命令
  - [x] 實作 `capture_image` 命令
- [x] ~~載入 button_positions.yaml 配置~~（✅ 改由客戶端管理）

**預期成果：** ✅ 可透過 Socket JSON 命令檢測按鈕顏色（準確率目標 > 95%）

**設計變更：** ✅ 伺服器不讀取配置檔，客戶端傳入完整參數（ROI、角度等）

**實作摘要：**
- 完成日期：2025-11-13
- VisionAnalyzer 類別：298 行（lines 59-297）
- JSON 命令處理：194 行（lines 483-676）
- connect() 方法擴展：支援 JSON 與二進制雙協議
- 移除伺服器端配置讀取，實現完全無狀態設計

**JSON 命令範例：**
```json
// 檢測按鈕
{
  "command": "detect_button",
  "roi": {"x": 285, "y": 210, "width": 75, "height": 75, "brightness_threshold": 100},
  "observe_angles": [13, -35, -85, 23.8, 0, 0],
  "num_frames": 5
}

// 移動到角度
{
  "command": "move_to_angles",
  "angles": [0, -4, 0, -75.5, 2, -74.7],
  "speed": 50
}

// 截圖
{
  "command": "capture_image",
  "num_frames": 5,
  "format": "jpeg"
}
```

---

### Phase 2: ROI 校準工具（1-2 小時）✅ 完成
- [x] 建立 `calibrate_button_roi.py`
  - [x] Socket JSON 客戶端（RobotArmClient）
  - [x] 自動遍歷所有按鈕（ButtonROICalibrator）
  - [x] 互動式 ROI 選擇（cv2.selectROI）
  - [x] YAML 配置自動更新
- [x] 建立校準操作指南文檔

**預期成果：** ✅ 可快速完成 20 個按鈕的 ROI 校準（約 10-15 分鐘）

**實作摘要：**
- 完成日期：2025-11-13
- 校準工具：391 行（scripts/calibrate_button_roi.py）
- 操作指南：完整文檔（docs/robot_arm_vision_calibration_guide.md）
- 核心功能：
  - Socket JSON 通訊客戶端
  - 自動移動到觀測位置
  - 多幀平均截圖
  - OpenCV 互動式 ROI 選擇
  - 自動更新 YAML 配置
  - 支援跳過已校準按鈕
  - 即時進度保存

**使用範例：**
```bash
# 基本用法
python3 scripts/calibrate_button_roi.py

# 跳過已校準的按鈕
python3 scripts/calibrate_button_roi.py --skip-existing

# 指定伺服器
python3 scripts/calibrate_button_roi.py --host 10.42.0.180 --port 9000
```

---

### Phase 3: Robot Framework 整合（1 小時）
- [ ] 擴展 `RobotArmKeywords`
  - [ ] `檢測按鈕狀態` 關鍵字
  - [ ] `檢測多個按鈕` 關鍵字
  - [ ] `等待按鈕變為狀態` 關鍵字
- [ ] 撰寫測試案例
  - [ ] 單一按鈕檢測測試
  - [ ] 批次檢測測試
  - [ ] 燈光切換驗證測試

**預期成果：** Robot Framework 可直接使用視覺檢測關鍵字

---

### Phase 4: 測試與優化（2-3 小時）
- [ ] 執行 ROI 校準（20 個按鈕）
- [ ] 實際測試檢測準確率
  - [ ] 測試藍色 LED（100 次）
  - [ ] 測試白色 LED（100 次）
  - [ ] 測試關閉狀態（100 次）
- [ ] 調整 HSV 閾值（如需要）
- [ ] 效能優化
  - [ ] 測量單一按鈕檢測時間
  - [ ] 測量批次檢測時間
  - [ ] 記憶體使用監控

**驗收標準：**
- 藍色檢測準確率 > 95%
- 白色檢測準確率 > 95%
- 關閉檢測準確率 > 95%
- 單一按鈕檢測 < 2 秒
- 批次檢測（20 按鈕）< 40 秒

---

### Phase 5: 備用方案（如 HSV 準確率 < 90%）

**僅在 Phase 4 測試失敗時執行**

#### **改進策略 A：自適應 HSV**
- [ ] 實作白平衡校準
- [ ] 實作動態閾值調整
- [ ] 多區域採樣降噪

**成本：** +1-2 小時
**預期改進：** 準確率 +3-5%

---

#### **改進策略 B：輕量級 CNN 分類器**
- [ ] 收集訓練數據（每個按鈕 20 張圖）
- [ ] 訓練 MobileNetV2 分類器
- [ ] 部署到 Jetson Nano

**成本：** +2-3 天
**預期改進：** 準確率 +5-8%

**注意：** 目前不考慮 YOLO，因為：
1. 問題複雜度不需要（已知 ROI 位置）
2. 開發成本過高（需 2 週 + 3000 張標註圖）
3. 推理速度慢（100ms vs 11ms）
4. 維護成本高（新增按鈕需重新訓練）

---

#### **改進策略 C：混合方案**
- [ ] HSV 初步篩選（快速排除明顯案例）
- [ ] CNN 精細分類（處理邊界案例）

**成本：** +3-4 天
**預期改進：** 準確率 98%+，速度仍 < 50ms

---

### Phase 6: 進階功能（未來擴展）
- [ ] GPU 加速（OpenCV CUDA）
- [ ] 實時視訊串流監控
- [ ] 異常檢測（按鈕損壞、反光等）
- [ ] 自動化測試報告生成

---

## 📖 參考資料

### OpenCV 文檔
- [Color Space Conversions](https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html)
- [inRange Function](https://docs.opencv.org/4.x/d2/de8/group__core__array.html#ga48af0ab51e36436c5d04340e036ce981)
- [selectROI Function](https://docs.opencv.org/4.x/d7/dfc/group__highgui.html#ga0f8b9f3f5f5efe95f0e8ed8f1e9b1c25)

### HSV 色彩空間
- H (Hue): 色相 0-180
- S (Saturation): 飽和度 0-255
- V (Value): 亮度 0-255

### LED PWM 頻率
- 典型 LED PWM: 100-1000 Hz
- 攝影機幀率: 30 FPS
- 解決方案: 多幀平均或增加曝光時間

---

## ✅ 驗收標準

### 功能驗收
- [x] 設計文檔完成
- [ ] 可成功檢測藍色 LED（準確率 > 95%）
- [ ] 可成功檢測白色 LED（準確率 > 95%）
- [ ] 可成功檢測關閉狀態（準確率 > 95%）
- [ ] LED 閃爍問題已解決（多幀平均）
- [ ] 校準工具可正常運作
- [ ] Robot Framework 關鍵字可正常使用

### 效能驗收
- [ ] 單一按鈕檢測 < 2 秒
- [ ] 批次檢測 20 按鈕 < 40 秒
- [ ] 記憶體使用 < 500 MB

### 文檔驗收
- [x] 設計文檔完整
- [ ] 校準操作指南完成
- [ ] API 文檔完成
- [ ] 測試報告完成

---

**文檔狀態：** ✅ 已完成
**下一步：** 開始實作 Phase 1 - 核心視覺檢測

