# 網頁版 ROI 校準工具使用指南

## 📋 概述

這是一個基於 Flask 的網頁版 ROI（Region of Interest）校準工具，專為機器手臂視覺檢測系統設計。

**主要優勢：**
- ✅ 不需要 X11 display
- ✅ 支援遠端操作（透過瀏覽器）
- ✅ 直覺的拖拽式介面
- ✅ 即時預覽和標註
- ✅ 自動儲存到 YAML 配置

## 🚀 快速開始

### 1. 啟動 Web 伺服器

```bash
cd /home/thortron/Tools/robot-multiplatform-automation

# 使用預設參數啟動
python3 scripts/web_roi_calibrator.py

# 或指定完整參數
python3 scripts/web_roi_calibrator.py \
    --host 10.42.0.180 \
    --port 9000 \
    --web-port 5000 \
    --config config/robot_arm/button_positions.yaml
```

### 2. 開啟瀏覽器

在任何瀏覽器中開啟：
```
http://localhost:5000
```

如果您是從遠端電腦存取，請使用伺服器的 IP：
```
http://<伺服器IP>:5000
```

### 3. 使用介面校準 ROI

#### 步驟 1：選擇按鈕
- 在左側邊欄中點擊要校準的按鈕
- 已校準的按鈕會顯示綠色標記 ✅

#### 步驟 2：擷取影像
- 點擊「📷 擷取影像」按鈕
- 等待系統從機器手臂攝影機擷取畫面
- 影像會顯示在中央區域

#### 步驟 3：框選 ROI
- 在影像上**按住滑鼠左鍵**並拖曳
- 釋放滑鼠以完成選取
- 綠色矩形框會顯示選取區域
- 下方會顯示 ROI 座標（X, Y, 寬度, 高度）

#### 步驟 4：儲存 ROI
- 檢查 ROI 座標是否正確
- 點擊「💾 儲存 ROI」按鈕
- 系統會自動更新 `button_positions.yaml` 配置檔案

#### 步驟 5：重複校準其他按鈕
- 返回步驟 1，選擇下一個按鈕
- 重複以上流程直到完成所有按鈕

## 🎨 介面說明

### 側邊欄（左側）
- **按鈕列表**：顯示所有可校準的按鈕
- **已校準標記**：綠色左側邊框 + ✅ 符號
- **按鈕資訊**：顯示按鈕名稱和描述

### 主要區域（右側）
- **狀態列**：顯示當前選中的按鈕和機器手臂連接狀態
- **影像顯示**：Canvas 區域用於顯示和標註
- **ROI 資訊**：顯示框選的座標和尺寸
- **控制按鈕**：
  - 📷 擷取影像
  - 🗑️ 清除選取
  - 💾 儲存 ROI

## 📐 ROI 框選技巧

### 推薦尺寸
- **最小尺寸**：40x40 像素
- **推薦尺寸**：60x60 到 80x80 像素
- **注意事項**：確保 LED 燈完整包含在框內

### 框選建議
1. ✅ 將 LED 燈置於框選區域中心
2. ✅ 包含 LED 的完整光暈範圍
3. ❌ 避免包含其他光源或干擾物
4. ❌ 避免框選到螢幕邊緣或黑色區域

## 🛠️ 參數說明

### 命令列參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--host` | 10.42.0.180 | 機器手臂伺服器 IP |
| `--port` | 9000 | 機器手臂伺服器端口 |
| `--web-port` | 5000 | Web 伺服器端口 |
| `--config` | config/robot_arm/button_positions.yaml | 配置檔案路徑 |
| `--timeout` | 30.0 | Socket 超時時間（秒） |

### 範例

#### 使用不同的 Web 端口
```bash
python3 scripts/web_roi_calibrator.py --web-port 8080
```

#### 指定不同的機器手臂伺服器
```bash
python3 scripts/web_roi_calibrator.py --host 192.168.1.100 --port 9001
```

## 🔧 故障排除

### 問題 1: 無法連接到機器手臂伺服器

**症狀：** 狀態列顯示「❌ 連接失敗」

**解決方法：**
1. 確認機器手臂伺服器已啟動：
   ```bash
   # 在 Jetson Nano 上執行
   python3 scripts/robot_arm_server.py --host 10.42.0.180 --port 9000
   ```
2. 檢查網路連接：
   ```bash
   ping 10.42.0.180
   ```
3. 確認端口未被占用

### 問題 2: 擷取影像超時

**症狀：** 點擊「擷取影像」後長時間等待或失敗

**解決方法：**
1. 增加 timeout 參數：
   ```bash
   python3 scripts/web_roi_calibrator.py --timeout 60
   ```
2. 檢查攝影機是否正常工作（在 Jetson Nano 上測試）
3. 確認伺服器啟動時有加 `--enable-vision` 參數（或確認視覺功能已啟用）

### 問題 3: 瀏覽器無法開啟頁面

**症狀：** 訪問 http://localhost:5000 顯示無法連接

**解決方法：**
1. 確認 Web 伺服器已成功啟動（查看終端輸出）
2. 檢查防火牆設定是否阻擋端口 5000
3. 嘗試使用 127.0.0.1 代替 localhost：
   ```
   http://127.0.0.1:5000
   ```

### 問題 4: 儲存 ROI 失敗

**症狀：** 點擊「儲存 ROI」後顯示錯誤訊息

**解決方法：**
1. 確認有寫入 `button_positions.yaml` 的權限
2. 檢查配置檔案格式是否正確
3. 查看終端輸出的詳細錯誤訊息

## 📊 API 端點說明

### GET /api/buttons
取得所有按鈕列表

**回應範例：**
```json
{
  "success": true,
  "buttons": [
    {
      "name": "light1",
      "description": "燈光按鈕 1",
      "has_roi": true
    }
  ]
}
```

### POST /api/calibrate/prepare
準備校準（擷取影像）

**請求：**
```json
{
  "button_name": "light1"
}
```

**回應：**
```json
{
  "success": true,
  "button_name": "light1",
  "description": "燈光按鈕 1",
  "observe_angles": [1.40, 11.42, -134.47, 36.56, 1.66, -45.61],
  "image_base64": "...",
  "image_size": {"width": 640, "height": 480}
}
```

### POST /api/calibrate/save
儲存 ROI

**請求：**
```json
{
  "button_name": "light1",
  "roi": {
    "x": 150,
    "y": 200,
    "width": 60,
    "height": 60
  }
}
```

**回應：**
```json
{
  "success": true,
  "message": "按鈕 'light1' 的 ROI 已儲存"
}
```

### GET /api/status
取得機器手臂狀態

**回應：**
```json
{
  "success": true,
  "power_on": true,
  "angles": [1.40, 11.42, -134.47, 36.56, 1.66, -45.61]
}
```

## 🎯 完成校準後

### 驗證配置
```bash
# 查看配置檔案
cat config/robot_arm/button_positions.yaml

# 確認 ROI 資料已正確儲存
grep -A 5 "vision:" config/robot_arm/button_positions.yaml
```

### 執行測試
```bash
# 快速測試
uv run robot tests/robot_arm/vision_quick_test.robot

# 完整測試
uv run robot tests/robot_arm/vision_detection_test.robot
```

## 📝 版本資訊

- **版本**：v1.0
- **建立日期**：2025-11-14
- **技術棧**：
  - 後端：Flask 3.1.2
  - 前端：Vanilla JavaScript + HTML5 Canvas
  - 影像處理：OpenCV (cv2)
  - 配置管理：PyYAML

## 🆘 需要幫助？

如果遇到問題，請檢查：
1. 終端輸出的錯誤訊息
2. 瀏覽器開發者工具的 Console 頁籤
3. 確認所有前置條件（伺服器運行、網路連接等）

---

**提示：** 使用 `Ctrl+C` 停止 Web 伺服器
