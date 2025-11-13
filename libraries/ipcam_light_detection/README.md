# IP Camera 燈光檢測模組

基於 RTSP 串流的 IP Camera 燈光狀態檢測系統，提供影像擷取、亮度分析與燈光開關判定功能。

## 功能特色

- 📹 **RTSP 串流支援** - 透過 RTSP 協議連接 IP Camera
- 🔆 **亮度分析** - 自動計算影像亮度並判定燈光狀態
- 🔄 **多攝影機切換** - 支援多環境、多攝影機配置管理
- 🎯 **區域分析** - 可選擇全圖或中心區域進行亮度分析
- ⏱️ **狀態等待** - 等待燈光狀態變化（開啟/關閉）
- 🤖 **Robot Framework 整合** - 完整的中文關鍵字支援

## 系統需求

### 必要套件

```bash
pip install opencv-python numpy loguru pyyaml
```

### IP Camera 需求

- 支援 RTSP 協議
- RTSP URL 格式：`rtsp://[Username]:[Password]@[IP]:554/live0`
- 預設使用 port 554
- 支援主串流 (`/live0`) 和次串流 (`/live1`)

## 快速開始

### 1. 配置設定

#### 方法 A：使用 .env 文件（推薦 - 適合所有攝影機使用相同帳密）

編輯專案根目錄的 `.env` 文件：

```bash
# IP Camera RTSP 認證（所有攝影機共用）
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_password_here
```

YAML 配置保持簡潔：

```yaml
environments:
  laboratory:
    cameras:
      level1:
        ip: "192.168.165.184"
        port: 554
        protocol: "rtsp"
        stream_path: "/live0"
        # username 和 password 會自動從 .env 讀取
```

#### 方法 B：在 YAML 中單獨設定（適合個別攝影機需要不同帳密）

編輯 `config/ipcam_config.yaml`：

```yaml
environments:
  laboratory:
    cameras:
      level1:
        ip: "192.168.165.184"
        port: 554
        protocol: "rtsp"
        username: "admin"      # 覆寫 .env 的設定
        password: "password"   # 覆寫 .env 的設定
        stream_path: "/live0"
```

**配置優先順序：** YAML 設定 > .env 環境變數 > 空字串

### 2. Python 使用範例

```python
from libraries.ipcam_light_detection import IPCamLightDetection

# 初始化
detector = IPCamLightDetection()

# 連接攝影機
detector.connect_camera('laboratory', 'level1')

# 取得當前亮度
brightness = detector.get_current_brightness()
print(f"當前亮度: {brightness}")

# 判定燈光狀態
if detector.is_light_on():
    print("燈光已開啟")
else:
    print("燈光已關閉")

# 儲存影像
detector.save_last_image('/tmp/camera_snapshot.jpg')

# 斷開連線
detector.disconnect()
```

### 3. Robot Framework 使用範例

```robotframework
*** Settings ***
Resource    resources/ipcam_keywords.robot

*** Test Cases ***
檢測燈光狀態
    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態
    And 儲存當前攝影機影像    /tmp/light_status.jpg
```

## RTSP URL 格式說明

### 基本格式

```
rtsp://[IP]:[Port]/[StreamPath]
```

### 帶認證格式

```
rtsp://[Username]:[Password]@[IP]:[Port]/[StreamPath]
```

### 範例

```
# 無認證
rtsp://192.168.165.184:554/live0

# 有認證
rtsp://admin:password@192.168.165.184:554/live0

# 次串流（通常解析度較低）
rtsp://admin:password@192.168.165.184:554/live1
```

## 配置說明

### 環境配置 (`config/ipcam_config.yaml`)

```yaml
environments:
  laboratory:                      # 環境名稱
    description: "實驗室測試環境"
    cameras:
      level1:                      # 攝影機名稱
        ip: "192.168.165.184"      # IP 位址
        port: 554                  # RTSP 端口
        protocol: "rtsp"           # 協議類型
        username: "admin"          # 認證帳號
        password: "password"       # 認證密碼
        stream_path: "/live0"      # 串流路徑
        description: "Level 1 監控攝影機"
```

### 燈光檢測設定

```yaml
light_detection:
  brightness_threshold:
    dark: 50                       # 暗閾值（燈關閉）
    bright: 150                    # 亮閾值（燈開啟）

  image_processing:
    capture_delay: 1.0             # 擷取延遲（秒）
    analysis_region: "center"      # 分析區域
    sample_size: 100               # 採樣像素數

  connection:
    timeout: 10                    # 連線逾時（秒）
    retry_attempts: 3              # 重試次數
    retry_delay: 2                 # 重試間隔（秒）
    rtsp_buffer_size: 1            # RTSP 緩衝幀數
    frame_skip: 3                  # 跳過前 N 幀
```

## API 參考

### IPCamLightDetection 類別

#### connect_camera(environment, camera_name)
連接到指定的攝影機。

```python
detector.connect_camera('laboratory', 'level1')
```

#### capture_image(snapshot_path="")
從 IP Camera 擷取影像。

```python
image = detector.capture_image()           # 使用預設串流
image = detector.capture_image('/live1')   # 使用次串流
```

#### calculate_brightness(image=None, region='center')
計算影像亮度。

```python
brightness = detector.calculate_brightness()              # 使用最後擷取的影像
brightness = detector.calculate_brightness(image, 'full') # 分析全圖
```

#### get_current_brightness(snapshot_path="", region='center')
擷取影像並計算當前亮度。

```python
brightness = detector.get_current_brightness()
```

#### is_light_on(brightness=None, threshold=None)
判定燈光是否開啟。

```python
if detector.is_light_on():
    print("燈光開啟")
```

#### is_light_off(brightness=None, threshold=None)
判定燈光是否關閉。

```python
if detector.is_light_off():
    print("燈光關閉")
```

#### get_light_status()
取得完整的燈光狀態資訊。

```python
status = detector.get_light_status()
print(f"亮度: {status['brightness']}")
print(f"開啟: {status['is_on']}")
```

#### wait_for_light_change(expected_state, timeout=30, check_interval=1.0)
等待燈光狀態變化。

```python
# 等待燈光開啟
success = detector.wait_for_light_change('on', timeout=60)

# 等待燈光關閉
success = detector.wait_for_light_change('off', timeout=60)
```

#### save_last_image(file_path)
儲存最後擷取的影像。

```python
detector.save_last_image('/tmp/snapshot.jpg')
```

#### disconnect()
斷開攝影機連線並釋放資源。

```python
detector.disconnect()
```

## Robot Framework 關鍵字

### 連接攝影機

- `連接實驗室 Level1 攝影機`
- `連接實驗室 Level2 攝影機`
- `連接實驗室馬達區攝影機`
- `連接指定環境攝影機    ${environment}    ${camera_name}`

### 影像擷取與分析

- `取得當前燈光亮度`
- `擷取影像    ${stream_path}`
- `計算亮度    ${image}    ${region}`
- `儲存當前攝影機影像    ${file_path}`

### 燈光狀態判定

- `驗證燈光為開啟狀態`
- `驗證燈光為關閉狀態`
- `檢查燈光狀態並記錄`
- `燈光是否開啟`
- `燈光是否關閉`

### 亮度驗證

- `亮度應該大於指定值    ${value}`
- `亮度應該小於指定值    ${value}`
- `亮度應該在範圍內    ${min}    ${max}`

### 等待與變化偵測

- `等待燈光開啟    timeout=${timeout}    check_interval=${interval}`
- `等待燈光關閉    timeout=${timeout}    check_interval=${interval}`
- `比較兩次亮度變化    delay=${delay}`

### 資源管理

- `斷開攝影機連線`

## 測試執行

### 執行所有測試

```bash
robot tests/ipcam_testing/ipcam_light_detection_test.robot
```

### 執行特定標籤測試

```bash
# 執行煙霧測試
robot --include smoke tests/ipcam_testing/

# 執行連線測試
robot --include connection tests/ipcam_testing/

# 執行亮度分析測試
robot --include brightness tests/ipcam_testing/
```

### 輸出詳細日誌

```bash
robot --loglevel DEBUG --outputdir results/ipcam tests/ipcam_testing/
```

## 故障排除

### 問題：無法連接到 RTSP 串流

**可能原因:**
- IP Camera 未開啟或網路不通
- RTSP 服務未啟動
- 帳號密碼錯誤
- 防火牆阻擋 port 554

**解決方法:**
1. 使用 VLC 測試 RTSP URL 是否可播放
2. 檢查網路連線：`ping [IP]`
3. 檢查 port：`telnet [IP] 554`
4. 確認配置檔案中的帳號密碼正確

### 問題：影像擷取失敗

**可能原因:**
- 串流路徑錯誤（/live0 或 /live1）
- 網路頻寬不足
- OpenCV 版本問題

**解決方法:**
1. 嘗試使用次串流 `/live1`
2. 增加 `retry_attempts` 設定
3. 更新 OpenCV：`pip install --upgrade opencv-python`

### 問題：亮度判定不準確

**可能原因:**
- 閾值設定不符合實際環境
- 分析區域選擇不當
- 光線環境變化大

**解決方法:**
1. 調整 `brightness_threshold` 設定
2. 嘗試 `analysis_region: "full"` 分析全圖
3. 多次測量取平均值

### 問題：OpenCV 相關錯誤

**常見錯誤訊息:**
```
ImportError: No module named 'cv2'
```

**解決方法:**
```bash
pip install opencv-python
```

## 進階使用

### 自訂閾值

```python
# Python
is_on = detector.is_light_on(threshold=200)  # 使用自訂閾值 200

# Robot Framework
${是否開啟} =    燈光是否開啟    threshold=200
```

### 使用次串流

```python
# Python
image = detector.capture_image('/live1')

# Robot Framework
擷取影像    /live1
```

### 分析全圖亮度

```python
# Python
brightness = detector.calculate_brightness(region='full')

# Robot Framework
${亮度} =    計算亮度    region=full
```

### 持續監控燈光狀態

```python
import time

detector.connect_camera('laboratory', 'level1')

while True:
    status = detector.get_light_status()
    print(f"{status['timestamp']} - 亮度: {status['brightness']:.2f}, "
          f"狀態: {'開啟' if status['is_on'] else '關閉'}")
    time.sleep(5)
```

## 整合範例

### 搭配 SwitchBot 智慧插座

```robotframework
*** Test Cases ***
自動化燈光控制與驗證
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

## 目錄結構

```
libraries/ipcam_light_detection/
├── __init__.py                    # 模組初始化
├── IPCamLightDetection.py         # 主要 Library
└── README.md                      # 本說明文件

config/
├── ipcam_config.yaml              # YAML 配置文件
└── ipcam_config.py                # Python 配置模組

resources/
└── ipcam_keywords.robot           # Robot Framework 關鍵字

tests/ipcam_testing/
└── ipcam_light_detection_test.robot  # 測試案例
```

## 注意事項

1. **資源釋放**: 使用完畢後記得呼叫 `disconnect()` 釋放 VideoCapture 資源
2. **網路延遲**: RTSP 串流可能有延遲，建議設定適當的 `capture_delay`
3. **環境光源**: 測試環境應保持穩定，避免自然光干擾
4. **帳號安全**: 不要將帳號密碼提交到版本控制系統
5. **效能考量**: 頻繁擷取影像會消耗網路頻寬，建議設定適當間隔

## 授權與貢獻

本模組為 robot-multiplatform-automation 專案的一部分。

## 更新日誌

### v1.0.0 (2025-11-05)
- ✨ 首次發布
- 🎯 支援 RTSP 串流連線
- 🔆 實現燈光狀態檢測
- 🤖 完整 Robot Framework 整合
- 📝 中文關鍵字支援

## 相關資源

- [OpenCV 文件](https://docs.opencv.org/)
- [RTSP 協議規範](https://datatracker.ietf.org/doc/html/rfc2326)
- [Robot Framework 文件](https://robotframework.org/)
