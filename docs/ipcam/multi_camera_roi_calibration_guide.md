# 多 Camera ROI 校準指南

## 概述

本指南說明如何為多個 RTSP Camera 來源標注多個 ROI 區塊，實現靈活的環境燈光檢測配置。

**版本**: v5.0.0
**日期**: 2025-11-26
**作者**: Robot Automation Team

---

## 功能特色

✅ **多環境支援**
- 支援 `taipei_lab`, `rv_car`, `taoyuan_lab` 等多個測試環境
- 可透過網頁介面即時切換環境

✅ **多 Camera 支援**
- 支援多個 RTSP IP Camera（level1, level2, motor）
- 自動整合 `EnvironmentConfig` 處理 RTSP 認證

✅ **多 ROI 區塊**
- 同一個 Camera 可以標注多個不同的 ROI 區塊
- 每個 ROI 區塊有獨立的名稱、用途和配置

✅ **統一校準介面**
- 使用 `web_roi_calibrator.py` 網頁工具進行視覺化校準
- 自動判斷影像來源（Socket 或 RTSP）
- 支援拖曳選取 ROI 區域

---

## 配置結構

### 環境燈光配置 (environment_lights)

位置：`config/robot_arm/taipei_lab_buttons.yaml` (範例)

```yaml
environment_lights:
  # ROI 區塊 1: 燈泡陣列（使用 level2 Camera）
  light_array:
    name: "實驗室燈泡陣列"
    type: "light_array"
    environment: "taipei_lab"
    camera_id: "level2"  # 指定使用哪個 Camera (對應 ipcam_config.yaml)
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
    
    roi:
      x: 200
      y: 150
      width: 100
      height: 100

    bright_threshold: 150
    dark_threshold: 50
```

### 配置說明

**必填欄位：**
- `name`: 顯示名稱（中文）
- `type`: 類型（`light_array` / `single_light`）
- `camera_id`: Camera 識別碼（需對應 `EnvironmentConfig` 中的設定）
- `roi`: ROI 區域座標（`{x, y, width, height}`）

**選填欄位：**
- `environment`: 環境名稱（預設：taipei_lab）
- `camera_purpose`: 用途說明
- `bright_threshold`: 亮度閾值（預設：150）
- `dark_threshold`: 暗度閾值（預設：50）

---

## 使用 ROI 校準工具

### 1. 啟動校準工具

```bash
cd scripts
# 啟動工具 (預設端口 5000)
python web_roi_calibrator.py

# 指定預設環境 (可選)
python web_roi_calibrator.py --environment taipei_lab
```

成功啟動後會顯示：
```
✅ 成功載入 3 個環境配置
🎯 預設環境: 台北實驗室 (可透過前端切換)
🔌 機器手臂連線資訊:
   台北實驗室: 10.42.0.180:9000
   ...
🚀 Web 伺服器已啟動
```

### 2. 開啟瀏覽器

訪問：http://localhost:5000

您會看到左側列表顯示當前環境的所有項目。您可以透過頂部的下拉選單切換不同環境。

```
📋 按鈕列表
-----------------------
light1
  按壓開關 Light1
  🔘 按鈕
  📷 socket
  ✅ 已校準

panel_status_led
  面板狀態指示燈
  💡 環境燈光
  📷 rtsp (level1)
  ⚠️  待校準
```

### 3. 校準步驟

#### Step 1: 選擇要校準的環境燈光
- 點擊左側列表中的環境燈光項目（例如：`panel_status_led`）
- 頂部狀態列會顯示：`當前按鈕: panel_status_led (💡 環境燈光)`

#### Step 2: 擷取 RTSP 影像
- 點擊 `📷 擷取影像` 按鈕
- 系統會：
  1. 根據 `camera_id` 自動取得 RTSP URL（含認證）
  2. 連接 Camera 並擷取影像
  3. 顯示在 Canvas 上

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

對每個環境燈光重複 Step 1-5。

---

## 驗證配置

### 檢查 YAML 檔案

```bash
# 查看 panel_status_led 的 ROI
grep -A 10 "panel_status_led:" config/robot_arm/taipei_lab_buttons.yaml
```

### 統計 Camera 使用情況

```bash
python3 -c "
import yaml
with open('config/robot_arm/taipei_lab_buttons.yaml', 'r') as f:
    config = yaml.safe_load(f)
# ... (略)
"
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
```

---

## 故障排除

### 問題 1: RTSP 連接失敗
**解決方案：**
1. 檢查 `.env` 檔案中的帳號密碼是否正確
2. 確認 `ipcam_config.yaml` 中的 IP 位址正確
3. 確保網路連線正常

### 問題 2: 找不到 Camera
**解決方案：**
檢查 `camera_id` 是否在 `ipcam_config.yaml` 中定義。

### 問題 3: ROI 未顯示在網頁上
**解決方案：**
確認 YAML 中 ROI 配置正確，且 `web_roi_calibrator.py` 已重新載入配置（重啟服務）。

---

**版本歷史：**
- v5.0.0 (2025-11-26): 支援多環境配置、移除 `--config` 參數
- v4.2.0 (2025-11-19): 新增多 Camera 多 ROI 支援、RTSP 認證功能
- v4.1.0 (2025-11-18): 本機化視覺檢測系統
