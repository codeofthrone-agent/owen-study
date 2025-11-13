# 機器手臂視覺檢測 - ROI 校準操作指南

**文檔版本：** v1.0.0
**建立日期：** 2025-11-13
**適用系統：** MyCobot 280 視覺檢測系統

---

## 📋 目錄

- [前置準備](#前置準備)
- [快速開始](#快速開始)
- [詳細操作步驟](#詳細操作步驟)
- [常見問題](#常見問題)
- [進階操作](#進階操作)

---

## 🛠️ 前置準備

### 硬體需求

- ✅ MyCobot 280 機器手臂（已連接到 Jetson Nano）
- ✅ 攝影機已安裝於機器手臂末端（/dev/video0）
- ✅ Jetson Nano 已開機並連接網路（IP: 10.42.0.180）
- ✅ 測試機（Ubuntu 24.04）與 Jetson Nano 在同一網段

### 軟體需求

**在 Jetson Nano 上：**
```bash
# 啟動機器手臂伺服器
cd /path/to/robot-multiplatform-automation
python3 scripts/robot_arm_server.py --host 10.42.0.180 --port 9000
```

**在測試機上：**
```bash
# 安裝依賴
pip install opencv-python PyYAML numpy

# 或使用專案環境
cd /path/to/robot-multiplatform-automation
source .venv/bin/activate  # 如果使用虛擬環境
```

### 環境檢查

```bash
# 測試連接
ping 10.42.0.180

# 測試伺服器連接（使用 telnet）
telnet 10.42.0.180 9000
```

---

## 🚀 快速開始

### 基本用法

```bash
cd /path/to/robot-multiplatform-automation

# 校準所有按鈕
python3 scripts/calibrate_button_roi.py

# 跳過已校準的按鈕
python3 scripts/calibrate_button_roi.py --skip-existing

# 指定伺服器 IP 和端口
python3 scripts/calibrate_button_roi.py --host 10.42.0.180 --port 9000
```

### 完整命令參數

```bash
python3 scripts/calibrate_button_roi.py \
    --host 10.42.0.180 \              # 伺服器 IP
    --port 9000 \                      # 伺服器端口
    --config config/robot_arm/button_positions.yaml \  # 配置檔案路徑
    --skip-existing \                  # 跳過已校準的按鈕
    --timeout 10.0                     # Socket 超時時間（秒）
```

---

## 📝 詳細操作步驟

### 步驟 1：啟動伺服器

**在 Jetson Nano 上執行：**

```bash
# SSH 連接到 Jetson Nano
ssh user@10.42.0.180

# 啟動伺服器
cd /path/to/robot-multiplatform-automation
python3 scripts/robot_arm_server.py
```

**預期輸出：**
```
==================================================
MyCobot Robot Arm Server - Enhanced Version
==================================================
Server IP:   10.42.0.180
Server Port: 9000
Serial Port: /dev/ttyTHS1
Baud Rate:   1000000
==================================================
Press Ctrl+C to stop the server
==================================================
✅ 視覺檢測系統已啟用
Binding succeeded!
waiting connect!------------------
```

### 步驟 2：執行校準工具

**在測試機上執行：**

```bash
cd /path/to/robot-multiplatform-automation
python3 scripts/calibrate_button_roi.py
```

**預期輸出：**
```
============================================================
ROI 校準工具 - 機器手臂視覺檢測系統
============================================================
伺服器: 10.42.0.180:9000
配置檔: config/robot_arm/button_positions.yaml
============================================================
✅ 已連接到伺服器 10.42.0.180:9000
✅ 已載入配置檔案: config/robot_arm/button_positions.yaml
   找到 21 個按鈕

🚀 開始校準所有按鈕（共 21 個）
```

### 步驟 3：校準單一按鈕

對於每個按鈕，工具會執行以下流程：

#### 3.1 選擇是否校準

```
進度: 1/21

是否校準按鈕 'bluetooth'? (y/n/q):
```

**操作選項：**
- `y` - 校準此按鈕
- `n` - 跳過此按鈕
- `q` - 退出校準程式

#### 3.2 自動移動與截圖

```
============================================================
校準按鈕: bluetooth
描述: 藍牙控制按鈕
============================================================
🤖 移動到觀測位置: [0, -4, 0, -75.5, 2, -74.7]
⏳ 等待穩定...
📷 截圖中...
✅ 截圖成功，圖像尺寸: 640x480
```

**注意：**
- 機器手臂會自動移動到觀測位置
- 等待 2 秒讓系統穩定
- 自動進行 5 幀平均截圖

#### 3.3 選擇 ROI

```
📌 請在視窗中框選按鈕的 ROI 區域
   - 滑鼠拖曳框選區域
   - 按 Enter 確認
   - 按 ESC 取消
```

**ROI 選擇操作：**

1. **視窗會自動彈出**，顯示截圖畫面
2. **用滑鼠拖曳框選**按鈕所在的矩形區域
   - 左上角點擊並拖曳到右下角
   - 確保完整包含按鈕（建議留 10-20 像素邊距）
3. **調整框選範圍**（如需要）
   - 可以重新拖曳調整
4. **按 Enter 鍵確認**
   - 或按 ESC 取消（跳過此按鈕）

**ROI 選擇建議：**
- ✅ 框選範圍稍大於按鈕（留邊距）
- ✅ 確保完整包含 LED 燈光區域
- ✅ 避免包含鄰近按鈕
- ❌ 不要框選太大區域（增加誤判風險）

#### 3.4 確認與儲存

```
✅ ROI 已選擇: x=285, y=210, width=75, height=75
✅ 按鈕 bluetooth 校準完成
💾 進度已保存（1/21）
```

**自動儲存的配置：**
```yaml
bluetooth:
  name: "Bluetooth 按鈕"
  # ... 原有配置 ...
  vision:
    observe_angles: [0, -4, 0, -75.5, 2, -74.7]
    roi:
      x: 285
      y: 210
      width: 75
      height: 75
    brightness_threshold: 100
    expected_colors: [blue, white, off]
```

### 步驟 4：完成校準

當所有按鈕校準完成後：

```
============================================================
✅ 校準完成！成功校準 20 個按鈕
============================================================
✅ 已斷開連接
```

---

## ❓ 常見問題

### Q1: 連接失敗

**問題：**
```
❌ 連接失敗: [Errno 111] Connection refused
```

**解決方案：**
1. 確認伺服器正在運行：
   ```bash
   ssh user@10.42.0.180
   ps aux | grep robot_arm_server
   ```
2. 檢查防火牆設定
3. 確認 IP 和端口正確

### Q2: 截圖失敗

**問題：**
```
❌ 截圖失敗: 視覺檢測系統未啟用
```

**解決方案：**
1. 確認攝影機已連接：
   ```bash
   ls -l /dev/video0
   ```
2. 重啟伺服器並啟用視覺系統：
   ```bash
   python3 scripts/robot_arm_server.py --enable-vision
   ```

### Q3: 移動失敗

**問題：**
```
❌ 移動失敗
```

**解決方案：**
1. 確認機器手臂已上電
2. 檢查串口連接：
   ```bash
   ls -l /dev/ttyTHS1
   ```
3. 確認關節角度在安全範圍內

### Q4: ROI 視窗無法顯示

**問題：** 執行校準工具後沒有視窗彈出

**解決方案：**
1. 確認 X11 轉發已啟用（SSH 連接）：
   ```bash
   ssh -X user@10.42.0.180
   ```
2. 或直接在本地機器執行校準工具
3. 檢查 OpenCV 是否正確安裝：
   ```bash
   python3 -c "import cv2; print(cv2.__version__)"
   ```

### Q5: YAML 配置損壞

**問題：** 儲存後 YAML 格式錯誤

**解決方案：**
1. 從備份還原：
   ```bash
   cp config/robot_arm/button_positions.yaml.bak \
      config/robot_arm/button_positions.yaml
   ```
2. 手動建立備份：
   ```bash
   cp config/robot_arm/button_positions.yaml \
      config/robot_arm/button_positions.yaml.bak
   ```

---

## 🎯 進階操作

### 只校準特定按鈕

如果只需要重新校準部分按鈕，可以：

1. **手動跳過不需要的按鈕**（按 `n`）
2. **或先修改配置檔**，移除需要重新校準按鈕的 `vision` 區塊

### 調整預設參數

#### 修改亮度閾值

編輯 `scripts/calibrate_button_roi.py`:

```python
button_config['vision']['brightness_threshold'] = 120  # 預設 100
```

#### 修改截圖幀數

```python
image = self.client.capture_image(num_frames=10)  # 預設 5
```

#### 修改穩定等待時間

```python
time.sleep(3.0)  # 預設 2.0 秒
```

### 批次校準腳本

建立自動化腳本 `auto_calibrate.sh`:

```bash
#!/bin/bash
# 自動校準腳本

# 備份原始配置
cp config/robot_arm/button_positions.yaml \
   config/robot_arm/button_positions.yaml.bak

# 執行校準
python3 scripts/calibrate_button_roi.py --skip-existing

# 驗證配置
python3 -c "
import yaml
with open('config/robot_arm/button_positions.yaml') as f:
    config = yaml.safe_load(f)
    buttons_with_vision = [k for k, v in config['buttons'].items() if 'vision' in v]
    print(f'✅ 已校準 {len(buttons_with_vision)} 個按鈕')
"
```

### 驗證校準結果

建立簡單的測試腳本 `test_roi.py`:

```python
#!/usr/bin/env python3
import yaml

config_path = 'config/robot_arm/button_positions.yaml'

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

buttons = config['buttons']
total = len(buttons)
calibrated = sum(1 for b in buttons.values() if 'vision' in b and 'roi' in b.get('vision', {}))

print(f"總按鈕數: {total}")
print(f"已校準: {calibrated}")
print(f"未校準: {total - calibrated}")
print(f"完成度: {calibrated/total*100:.1f}%")

# 列出未校準的按鈕
uncalibrated = [name for name, cfg in buttons.items()
                if 'vision' not in cfg or 'roi' not in cfg.get('vision', {})]
if uncalibrated:
    print(f"\n未校準的按鈕:")
    for name in uncalibrated:
        print(f"  - {name}")
```

---

## 📊 ROI 配置範例

### 完整配置範例

```yaml
light1:
  name: "Light1 按鈕"
  description: "燈光控制 1"
  down_angles: [3.5, -60, -82, 25, 0, 0]
  up_angles: [3.5, -35, -82, 25, 0, 0]
  speed: 100
  count: 1
  lift_duration: 0.1
  press_duration: 0.5
  vision:
    observe_angles: [0, -4, 0, -75.5, 2, -74.7]
    roi:
      x: 285
      y: 210
      width: 75
      height: 75
    brightness_threshold: 100
    expected_colors: [blue, white, off]
```

### ROI 參數說明

| 參數 | 說明 | 範例值 |
|------|------|--------|
| `observe_angles` | 觀測位置的關節角度 | `[0, -4, 0, -75.5, 2, -74.7]` |
| `roi.x` | ROI 左上角 X 座標（像素） | `285` |
| `roi.y` | ROI 左上角 Y 座標（像素） | `210` |
| `roi.width` | ROI 寬度（像素） | `75` |
| `roi.height` | ROI 高度（像素） | `75` |
| `brightness_threshold` | 亮度閾值（0-255） | `100` |
| `expected_colors` | 預期顏色列表 | `[blue, white, off]` |

---

## 🔧 故障排除檢查清單

**執行校準前：**

- [ ] Jetson Nano 已開機並連接網路
- [ ] 機器手臂伺服器正在運行
- [ ] 攝影機已連接（/dev/video0）
- [ ] 機器手臂已上電（power_on）
- [ ] 測試機可以 ping 通 Jetson Nano
- [ ] Python 環境已安裝所需依賴

**執行校準中：**

- [ ] 觀測視窗正常顯示
- [ ] 機器手臂移動順暢
- [ ] 截圖清晰可見按鈕
- [ ] ROI 框選範圍合理

**執行校準後：**

- [ ] 配置檔案已更新
- [ ] YAML 格式正確
- [ ] 所有按鈕都有 vision 配置
- [ ] 備份原始配置檔案

---

## 📚 相關文檔

- [視覺檢測設計文檔](robot_arm_vision_detection_design.md)
- [機器手臂伺服器使用指南](robot_arm_server_usage.md)
- [按鈕配置說明](../libraries/robot_arm_control/BUTTON_SETUP_GUIDE.md)

---

**文檔維護：** 如有問題或建議，請更新此文檔並記錄變更日期。
