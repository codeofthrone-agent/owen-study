# IP Camera 燈光檢測模組 - 功能摘要

## 📹 模組概述

IP Camera 燈光檢測模組已完成開發並測試通過 ✅

基於 RTSP 串流的 IP Camera 影像分析系統，支援實時燈光狀態檢測與自動化測試。

## 🎯 主要功能

- **RTSP 串流連線**: 支援 H.264/HEVC 編碼，TCP 傳輸協議
- **影像擷取**: 實時從 IP Camera 獲取高清影像（1620×2592）
- **亮度分析**: 自動計算影像平均亮度（0-255）
- **燈光判定**: 基於可配置閾值判定燈光開/關狀態
- **狀態等待**: 支援等待燈光狀態變化（超時機制）
- **多攝影機管理**: 支援多環境、多攝影機配置切換
- **中文關鍵字**: 完整的 Robot Framework 中文關鍵字支援

## 📁 檔案結構

```
libraries/ipcam_light_detection/
├── __init__.py                    # 模組初始化
├── IPCamLightDetection.py         # 主要 Library（500+ 行）
└── README.md                      # 完整 API 文檔

config/
├── ipcam_config.yaml              # YAML 配置（攝影機 IP、端口等）
└── ipcam_config.py                # Python 配置管理（環境變數整合）

resources/
└── ipcam_keywords.robot           # Robot Framework 關鍵字（20+ 個）

tests/ipcam_testing/
└── ipcam_light_detection_test.robot  # 測試案例（10 個）

scripts/
├── test_ipcam_config.py           # 配置測試工具
└── quick_ipcam_test.py            # 快速連線測試

docs/
├── ipcam_setup_guide.md           # 完整安裝指南
└── ipcam_quick_start.md           # 5 分鐘快速開始

.env                                # 認證資訊（IPCAM_USERNAME/PASSWORD）
```

## 🔧 配置方式

### 統一認證管理（推薦）

所有攝影機使用相同帳號密碼，集中在 `.env` 管理：

```bash
# .env
IPCAM_USERNAME=thortron_qa
IPCAM_PASSWORD=your_password_here
```

### YAML 配置

```yaml
# config/ipcam_config.yaml
environments:
  laboratory:
    cameras:
      level1:
        ip: "192.168.165.184"
        port: 554
        protocol: "rtsp"
        stream_path: "/live0"
        # username/password 自動從 .env 讀取
```

## 🚀 快速使用

### Python 直接使用

```python
from libraries.ipcam_light_detection import IPCamLightDetection

detector = IPCamLightDetection()
detector.connect_camera('laboratory', 'level1')
brightness = detector.get_current_brightness()
is_on = detector.is_light_on()
print(f"亮度: {brightness}, 燈光: {'開啟' if is_on else '關閉'}")
```

### Robot Framework 使用

```robotframework
*** Test Cases ***
檢測燈光狀態
    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態
    And 儲存當前攝影機影像    /tmp/light_status.jpg
```

## ✅ 測試狀態

### 測試通過的攝影機

| 攝影機 | IP 地址 | 狀態 | 影像尺寸 |
|--------|---------|------|----------|
| level1 | 192.168.165.184 | ✅ 正常 | 1620 × 2592 |
| level2 | 192.168.165.127 | ✅ 正常 | 1620 × 2592 |
| motor  | 10.42.0.39      | ✅ 正常 | 1620 × 2592 |

**成功率: 3/3 (100%)**

### 執行測試命令

```bash
# 設定環境
pipenv shell
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 執行測試
pipenv run robot --include smoke tests/ipcam_testing/
```

## 🔑 核心技術

### RTSP 連線優化

```python
# FFmpeg 選項設定（支援 HEVC/H.265）
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = \
    'rtsp_transport;tcp|analyzeduration;20000000|probesize;20000000'
```

- **TCP 傳輸**: 提高穩定性（vs UDP）
- **大緩衝區分析**: 確保正確識別 HEVC 串流
- **最小延遲**: 緩衝區設為 1 幀，實時性優先

### 亮度計算算法

```python
# 灰階轉換 → 區域選擇 → 平均值計算
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
if region == 'center':
    h, w = gray.shape
    center_h, center_w = h // 4, w // 4
    gray = gray[center_h:center_h*3, center_w:center_w*3]
brightness = float(np.mean(gray))
```

## 📋 Robot Framework 關鍵字列表

### 連接管理
- `連接實驗室 Level1 攝影機`
- `連接實驗室 Level2 攝影機`
- `連接實驗室馬達區攝影機`
- `連接指定環境攝影機`
- `斷開攝影機連線`

### 影像擷取
- `擷取影像`
- `取得當前燈光亮度`
- `儲存當前攝影機影像`
- `計算亮度`

### 狀態判定
- `驗證燈光為開啟狀態`
- `驗證燈光為關閉狀態`
- `檢查燈光狀態並記錄`
- `燈光是否開啟`
- `燈光是否關閉`

### 亮度驗證
- `亮度應該大於指定值`
- `亮度應該小於指定值`
- `亮度應該在範圍內`

### 等待機制
- `等待燈光開啟`
- `等待燈光關閉`
- `比較兩次亮度變化`

## 📦 依賴套件

```bash
pip install opencv-python numpy loguru pyyaml python-dotenv
```

## 🎓 學習資源

- **完整文檔**: `libraries/ipcam_light_detection/README.md`
- **安裝指南**: `docs/ipcam_setup_guide.md`
- **快速開始**: `docs/ipcam_quick_start.md`
- **測試案例**: `tests/ipcam_testing/ipcam_light_detection_test.robot`

## 🔗 整合範例

### 搭配 SwitchBot 自動化測試

```robotframework
*** Test Cases ***
自動化燈光控制驗證
    # 開啟電源
    Given 智慧插座應為關閉狀態
    When 開啟智慧插座
    And 等待 3 秒鐘

    # 驗證燈光
    And 連接實驗室 Level1 攝影機
    Then 等待燈光開啟    timeout=10
    And 驗證燈光為開啟狀態

    # 關閉電源
    When 關閉智慧插座
    And 等待 3 秒鐘
    Then 等待燈光關閉    timeout=10
    And 驗證燈光為關閉狀態
```

## 📊 開發時程

- **2025-11-05**: 完成開發與測試 ✅
- **測試環境**: Ubuntu 24.04
- **Python 版本**: 3.12
- **OpenCV 版本**: 4.12.0.88

## 🎉 完成狀態

✅ YAML 配置系統
✅ .env 認證整合
✅ RTSP 串流連線（支援 HEVC）
✅ 影像擷取與處理
✅ 亮度計算與分析
✅ 燈光狀態判定
✅ Robot Framework 整合
✅ 中文關鍵字支援
✅ 完整測試案例（10 個）
✅ 三個攝影機測試通過
✅ 完整文檔

**模組狀態: 生產就緒 (Production Ready)** 🚀
