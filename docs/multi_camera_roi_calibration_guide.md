# 多 Camera ROI 校準指南

## 概述

本指南說明如何為多個 RTSP Camera 來源標注多個 ROI 區塊，實現靈活的環境燈光檢測配置。

**版本**: v4.2.0
**日期**: 2025-11-19
**作者**: Robot Automation Team

---

## 功能特色

✅ **多 Camera 支援**
- 支援多個 RTSP IP Camera（level1, level2, motor）
- 每個 Camera 自動包含 RTSP 認證資訊

✅ **多 ROI 區塊**
- 同一個 Camera 可以標注多個不同的 ROI 區塊
- 每個 ROI 區塊有獨立的名稱、用途和配置

✅ **統一校準介面**
- 使用 web_roi_calibrator.py 網頁工具進行視覺化校準
- 自動判斷影像來源（Socket 或 RTSP）
- 支援拖曳選取 ROI 區域

---

## 配置結構

### 環境燈光配置 (environment_lights)

位置：`config/robot_arm/taipei_lab_buttons.yaml`

```yaml
environment_lights:
  # ROI 區塊 1: 燈泡陣列（使用 level2 Camera）
  light_array:
    name: "實驗室燈泡陣列"
    type: "light_array"
    environment: "taipei_lab"
    camera_id: "level2"  # 指定使用哪個 Camera
    camera_ip: "192.168.165.127"
    camera_purpose: "light_array_detection"

    # ROI 配置（絕對像素座標）
    roi:
      x: 100
      y: 50
      width: 500
      height: 400

    # 個別燈泡配置（可選）
    lights:
      "0_0":
        name: "燈泡 A1"
        roi: [0.00, 0.00, 0.25, 0.33]  # 相對座標
        bright_threshold: 150

  # ROI 區塊 2: 面板狀態指示燈（同樣使用 level1 Camera）
  panel_status_led:
    name: "面板狀態指示燈"
    type: "single_light"
    environment: "taipei_lab"
    camera_id: "level1"  # 使用 level1 Camera
    camera_ip: "192.168.165.184"

    roi:
      x: 200
      y: 150
      width: 100
      height: 100

    bright_threshold: 150
    dark_threshold: 50

  # ROI 區塊 3: 電源指示燈（level1 Camera 的第二個 ROI）
  power_indicator:
    name: "電源指示燈"
    type: "single_light"
    camera_id: "level1"  # 同一個 Camera，不同的 ROI
    camera_ip: "192.168.165.184"

    roi:
      x: 50
      y: 450
      width: 80
      height: 80

  # ROI 區塊 4: 馬達運轉指示燈（使用 motor Camera）
  motor_running_indicator:
    name: "馬達運轉指示燈"
    type: "single_light"
    camera_id: "motor"  # 使用 motor Camera
    camera_ip: "10.42.0.39"

    roi:
      x: 300
      y: 200
      width: 120
      height: 120
```

### 配置說明

**必填欄位：**
- `name`: 顯示名稱（中文）
- `type`: 類型（`light_array` / `single_light`）
- `camera_id`: Camera 識別碼（`level1` / `level2` / `motor`）
- `roi`: ROI 區域座標（`{x, y, width, height}`）

**選填欄位：**
- `environment`: 環境名稱（預設：taipei_lab）
- `camera_ip`: Camera IP（用於文檔說明）
- `camera_purpose`: 用途說明
- `bright_threshold`: 亮度閾值（預設：150）
- `dark_threshold`: 暗度閾值（預設：50）

---

## 使用 ROI 校準工具

### 1. 啟動校準工具

```bash
cd scripts
python web_roi_calibrator.py --config config/robot_arm/taipei_lab_buttons.yaml
```

成功啟動後會顯示：
```
✅ 找到 13 個按鈕, 4 個環境燈光
🌐 Web 伺服器已啟動: http://0.0.0.0:5000
```

### 2. 開啟瀏覽器

訪問：http://localhost:5000

您會看到左側列表顯示所有項目：

```
📋 按鈕列表
-----------------------
light1
  按壓開關 Light1
  🔘 按鈕
  📷 socket
  ✅ 已校準

light_array
  實驗室燈泡陣列
  💡 環境燈光
  📷 rtsp (level2)
  ✅ 已校準

panel_status_led
  面板狀態指示燈
  💡 環境燈光
  📷 rtsp (level1)
  ⚠️  待校準

power_indicator
  電源指示燈
  💡 環境燈光
  📷 rtsp (level1)
  ⚠️  待校準

motor_running_indicator
  馬達運轉指示燈
  💡 環境燈光
  📷 rtsp (motor)
  ⚠️  待校準
```

### 3. 校準步驟

#### Step 1: 選擇要校準的環境燈光
- 點擊左側列表中的環境燈光項目（例如：`panel_status_led`）
- 頂部狀態列會顯示：`當前按鈕: panel_status_led (💡 環境燈光)`

#### Step 2: 擷取 RTSP 影像
- 點擊 `📷 擷取影像` 按鈕
- 系統會：
  1. 從 `camera_id` 解析出 Camera（例如：level1）
  2. 呼叫 `/api/environment_config` 取得 RTSP URL（自動包含認證）
  3. 呼叫 `/api/image/capture_rtsp` 擷取影像
  4. 顯示在 Canvas 上

#### Step 3: 拖曳選取 ROI
- 在 Canvas 上按住滑鼠左鍵
- 拖曳繪製矩形框
- 釋放滑鼠完成選取
- 綠色矩形框會顯示選取的區域

#### Step 4: 檢查 ROI 座標
- 下方 `📐 ROI 座標` 區塊會顯示：
  ```
  X: 200    Y: 150
  寬度: 100  高度: 100
  ```

#### Step 5: 儲存 ROI
- 點擊 `💾 儲存 ROI` 按鈕
- 成功後會顯示：`✅ 環境燈光 "panel_status_led" 的 ROI 已成功儲存！`
- 配置會自動寫入 YAML 檔案
- 左側列表會更新為 `✅ 已校準`

### 4. 重複校準其他 ROI 區塊

對每個環境燈光重複 Step 1-5，例如：
- `power_indicator`（level1 Camera 的另一個區域）
- `motor_running_indicator`（motor Camera）

---

## 驗證配置

### 檢查 YAML 檔案

```bash
# 查看 panel_status_led 的 ROI
grep -A 10 "panel_status_led:" config/robot_arm/taipei_lab_buttons.yaml

# 預期輸出：
# panel_status_led:
#   name: "面板狀態指示燈"
#   type: "single_light"
#   ...
#   roi:
#     x: 200
#     y: 150
#     width: 100
#     height: 100
```

### 統計 Camera 使用情況

```bash
python3 -c "
import yaml

with open('config/robot_arm/taipei_lab_buttons.yaml', 'r') as f:
    config = yaml.safe_load(f)

env_lights = config.get('environment_lights', {})

camera_rois = {}
for name, light in env_lights.items():
    camera_id = light.get('camera_id', 'unknown')
    if camera_id not in camera_rois:
        camera_rois[camera_id] = []
    camera_rois[camera_id].append(name)

for camera, rois in sorted(camera_rois.items()):
    print(f'📷 {camera}: {len(rois)} 個 ROI 區塊')
    for roi_name in rois:
        print(f'   - {roi_name}')
"
```

預期輸出：
```
📷 level1: 2 個 ROI 區塊
   - panel_status_led
   - power_indicator
📷 level2: 1 個 ROI 區塊
   - light_array
📷 motor: 1 個 ROI 區塊
   - motor_running_indicator
```

---

## 在 Robot Framework 中使用

### 範例測試案例

```robotframework
*** Test Cases ***
檢測面板狀態指示燈
    [Documentation]    使用 level1 Camera 檢測面板狀態指示燈

    Given 測試環境設定為 "taipei_lab"

    # 檢測面板狀態指示燈（自動使用 level1 RTSP）
    ${result}=    When 用戶檢測實體燈光亮度 "panel_status_led"

    # 驗證結果
    Then 實體燈光應該為 "bright" 狀態
    Log To Console    亮度: ${result['brightness_level']}%

檢測多個環境燈光
    [Documentation]    同時檢測多個 Camera 的多個 ROI 區塊

    Given 測試環境設定為 "taipei_lab"

    # Level1 Camera - 面板狀態指示燈
    ${panel_led}=    When 用戶檢測實體燈光亮度 "panel_status_led"

    # Level1 Camera - 電源指示燈（同一個 Camera）
    ${power_led}=    When 用戶檢測實體燈光亮度 "power_indicator"

    # Level2 Camera - 燈泡陣列
    ${light_array}=    When 用戶檢測實體燈光亮度 "light_array"

    # Motor Camera - 馬達指示燈
    ${motor_led}=    When 用戶檢測實體燈光亮度 "motor_running_indicator"

    # 驗證所有燈光
    Log To Console    面板 LED: ${panel_led['light_state']}
    Log To Console    電源 LED: ${power_led['light_state']}
    Log To Console    燈泡陣列: ${light_array['light_state']}
    Log To Console    馬達 LED: ${motor_led['light_state']}
```

---

## 架構說明

### RTSP URL 自動認證

系統會自動從 `.env` 讀取認證資訊並構建 RTSP URL：

**.env 檔案：**
```bash
IPCAM_USERNAME=thortron_qa
IPCAM_PASSWORD=WHtYpiU6lh_McQf
```

**自動生成的 RTSP URL：**
```
rtsp://thortron_qa:WHtYpiU6lh_McQf@192.168.165.184:554/live0  # level1
rtsp://thortron_qa:WHtYpiU6lh_McQf@192.168.165.127:554/live0  # level2
rtsp://thortron_qa:WHtYpiU6lh_McQf@10.42.0.39:554/live0        # motor
```

### 影像來源判斷流程

```
用戶選擇項目
  ↓
判斷 item_type
  ├─ button → 使用 Socket（機器手臂攝像頭）
  └─ environment_light → 檢查 image_source
       ↓
    包含 "rtsp" → 使用 RTSP 截圖
       ├─ 解析 camera_id
       ├─ 取得 RTSP URL（含認證）
       └─ 呼叫 /api/image/capture_rtsp
```

---

## 故障排除

### 問題 1: RTSP 連接失敗（401 Unauthorized）

**症狀：**
```
[rtsp @ 0x...] method DESCRIBE failed: 401 Unauthorized
```

**解決方案：**
1. 檢查 `.env` 檔案中的帳號密碼是否正確
2. 驗證 RTSP URL：
   ```bash
   python3 -c "
   from config.robot_arm.environment_config import EnvironmentConfig
   cameras = EnvironmentConfig.get_cameras('taipei_lab')
   print(cameras[0]['rtsp_url'])
   "
   ```
3. 確認輸出包含認證資訊（`rtsp://username:password@...`）

### 問題 2: 找不到 Camera

**症狀：**
```
找不到 Camera: level3
```

**解決方案：**
檢查 `camera_id` 是否正確，可用的 Camera：
- taipei_lab: `level1`, `level2`, `motor`

### 問題 3: ROI 未顯示在網頁上

**症狀：**
點擊項目後沒有顯示已存在的 ROI

**解決方案：**
1. 確認 YAML 中 ROI 配置正確
2. 檢查 `has_roi` 標記：
   ```bash
   python3 -c "
   import yaml
   with open('config/robot_arm/taipei_lab_buttons.yaml', 'r') as f:
       config = yaml.safe_load(f)
   light = config['environment_lights']['panel_status_led']
   print('有 ROI:', 'roi' in light)
   print('ROI 值:', light.get('roi'))
   "
   ```

### 問題 4: RTSP 影像 ROI 框選位置不正確（✅ 已修復 v4.2.0）

**症狀：**
- 使用 RTSP 影像源時，拖曳框選的 ROI 區域與實際位置不符
- 綠色矩形框顯示在錯誤的位置
- 儲存後座標與預期不一致

**原因：**
Canvas 元素的 CSS 顯示尺寸與內部像素解析度不一致，導致滑鼠座標未正確轉換。

**修復內容（v4.2.0）：**
新增 `getCanvasCoordinates()` 函式，自動計算縮放比例並轉換座標：
```javascript
// 計算縮放比例
scaleX = canvas.width / rect.width
scaleY = canvas.height / rect.height

// 轉換為 Canvas 內部像素座標
canvasX = displayX * scaleX
canvasY = displayY * scaleY
```

**驗證修復：**
1. 重新啟動 web_roi_calibrator
2. 選擇 RTSP 影像源（例如：`panel_status_led`）
3. 擷取影像後，拖曳框選 ROI
4. 綠色矩形框應精確對應滑鼠拖曳的區域
5. 儲存後，重新載入該項目，黃色矩形框應顯示在相同位置

---

## 擴展指南

### 新增更多 ROI 區塊

編輯 `config/robot_arm/taipei_lab_buttons.yaml`：

```yaml
environment_lights:
  # 新增區塊：使用 level1 Camera 的第三個 ROI
  alarm_indicator:
    name: "警報指示燈"
    type: "single_light"
    camera_id: "level1"
    camera_ip: "192.168.165.184"
    roi:
      x: 0
      y: 0
      width: 100
      height: 100
```

重新啟動 web_roi_calibrator，新項目會自動出現在列表中。

### 新增其他環境

1. 複製 `taipei_lab_buttons.yaml` 為 `your_env_buttons.yaml`
2. 修改 `environment_lights` 區塊
3. 在 `environment_config.py` 中註冊新環境
4. 使用 `--config` 參數載入：
   ```bash
   python web_roi_calibrator.py --config config/robot_arm/your_env_buttons.yaml
   ```

---

## 總結

✅ 支援多個 RTSP Camera 來源
✅ 每個 Camera 可標注多個 ROI 區塊
✅ 統一的網頁校準介面
✅ 自動 RTSP 認證處理
✅ 完整的 Robot Framework 整合

**下一步：**
- 實際硬體測試
- 驗證 8 張 debug 影像（4 Socket + 4 RTSP）
- 完成所有環境燈光的 ROI 校準

---

**版本歷史：**
- v4.2.0 (2025-11-19): 新增多 Camera 多 ROI 支援、RTSP 認證功能、修復 ROI 框選座標問題
- v4.1.1 (2025-11-18): Socket 連接共用修復
- v4.1.0 (2025-11-18): 本機化視覺檢測系統
