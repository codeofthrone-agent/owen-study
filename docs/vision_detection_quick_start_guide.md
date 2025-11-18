# 本機化視覺檢測系統 - 快速上手指南

**版本**: v4.0.0
**日期**: 2025-11-18
**作者**: Robot Automation Team

---

## 🎯 簡介

本機化視覺檢測系統讓您可以在 **Robot Framework** 測試案例中，使用 **BDD 中文關鍵字** 進行按鈕 LED 顏色檢測和實體燈光亮度檢測。

**支援功能**:
- ✅ **3 個測試環境**: taipei_lab (RTSP), taoyuan_lab (Socket), rv_car (Socket)
- ✅ **8 種顏色檢測**: 藍/白/紅/綠/黃/橙/紫/關
- ✅ **11 級亮度檢測**: 0-100% (10% 步進)
- ✅ **雙影像源**: RTSP (IP Camera) / Socket (USB Camera)
- ✅ **32+ BDD 關鍵字**: Given-When-Then 中文關鍵字

---

## 🚀 快速開始 (5 分鐘)

### Step 1: 環境設置

```bash
# 1. 確保在專案根目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 2. 啟動虛擬環境
source .venv/bin/activate

# 3. 驗證安裝
python -c "from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords; print('✅ 環境正常')"
```

### Step 2: 啟動機器手臂 Server

**在 Jetson Nano 上**:
```bash
cd ~/server
./run_server.sh

# 應該看到:
# Server running on 0.0.0.0:9000
```

**在本機測試連接**:
```bash
# 測試機器手臂連接
curl http://10.42.0.180:9000/health

# 應該回傳: {"status": "ok"}
```

### Step 3: 第一個測試案例

建立測試檔案 `my_first_vision_test.robot`:

```robotframework
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

*** Test Cases ***
我的第一個視覺檢測測試
    [Documentation]    檢測 taipei_lab 環境的 3611a 面板 light1 按鈕顏色
    [Tags]    vision    taipei_lab

    # Step 1: 設定環境
    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"
    And 機器手臂已連接到遠端伺服器 "10.42.0.180" "9000"

    # Step 2: 執行檢測
    When 用戶檢測面板按鈕 "light1" 的顏色

    # Step 3: 驗證結果
    Then 面板按鈕顏色應該為 "blue"
    And 視覺檢測信心度應該大於 0.85

    # Step 4: 清理
    [Teardown]    斷開機器手臂連接
```

### Step 4: 執行測試

```bash
# 執行測試
robot my_first_vision_test.robot

# 查看測試報告
xdg-open log.html
```

**成功輸出範例**:
```
==============================================================================
My First Vision Test
==============================================================================
我的第一個視覺檢測測試 :: 檢測 taipei_lab 環境的 3611a 面板 light1 按鈕顏色 | PASS |
------------------------------------------------------------------------------
My First Vision Test                                                  | PASS |
1 test, 1 passed, 0 failed
==============================================================================
```

🎉 **恭喜！您已完成第一個視覺檢測測試！**

---

## 📚 核心概念

### 1️⃣ 三個環境

| 環境 | 影像源 | 機器手臂 IP | 用途 |
|------|--------|-------------|------|
| **taipei_lab** | RTSP (IP Camera) | 10.42.0.180 | 台北實驗室，支援 3 種面板 |
| **taoyuan_lab** | Socket (USB Camera) | 192.168.1.100 | 桃園實驗室，支援 2 種面板 |
| **rv_car** | Socket (USB Camera) | 10.42.0.180 | RV Car 測試，支援車燈檢測 |

### 2️⃣ 面板類型

- **3510a**: 小型面板 (音量控制按鈕)
- **3611a**: 中型面板 (燈光控制按鈕，最常用)
- **3611c**: 大型面板 (電源/模式按鈕，RV Car 專用)

### 3️⃣ 檢測類型

**面板按鈕顏色檢測**:
- 8 種顏色: `blue`, `white`, `red`, `green`, `yellow`, `orange`, `purple`, `off`
- 使用 HSV 色彩空間檢測
- 信心度 (confidence) 通常 > 0.9

**實體燈光亮度檢測**:
- 11 級亮度: 0%, 10%, 20%, ..., 90%, 100%
- 容許誤差 ±10%
- 適用於天花板燈、桌燈、車燈等

---

## 🔧 常用測試模式

### 模式 1: 單一按鈕顏色檢測

```robotframework
*** Test Cases ***
檢測 Light1 按鈕為藍色
    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"
    And 機器手臂已連接到遠端伺服器 "10.42.0.180" "9000"

    When 用戶檢測面板按鈕 "light1" 的顏色
    Then 面板按鈕顏色應該為 "blue"
```

### 模式 2: 多個按鈕顏色檢測

```robotframework
*** Test Cases ***
檢測多個按鈕顏色
    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"
    And 機器手臂已連接到遠端伺服器 "10.42.0.180" "9000"

    # Light1 應為藍色
    When 用戶檢測面板按鈕 "light1" 的顏色
    Then 面板按鈕顏色應該為 "blue"

    # Light2 應為紅色
    When 用戶檢測面板按鈕 "light2" 的顏色
    Then 面板按鈕顏色應該為 "red"

    # Light3 應為綠色
    When 用戶檢測面板按鈕 "light3" 的顏色
    Then 面板按鈕顏色應該為 "green"
```

### 模式 3: 實體燈光亮度檢測

```robotframework
*** Test Cases ***
檢測天花板燈亮度
    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"

    # 檢測亮度為 50%
    When 用戶檢測實體燈光亮度 "ceiling_light_1"
    Then 實體燈光亮度應該為 "50" %
```

### 模式 4: 多環境測試

```robotframework
*** Test Cases ***
測試台北實驗室環境
    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"
    When 用戶檢測面板按鈕 "light1" 的顏色
    Then 面板按鈕顏色應該為 "blue"

測試桃園實驗室環境
    Given 測試環境設定為 "taoyuan_lab"
    And 面板類型設定為 "3611a"
    When 用戶檢測面板按鈕 "light1" 的顏色
    Then 面板按鈕顏色應該為 "blue"

測試 RV Car 環境
    Given 測試環境設定為 "rv_car"
    And 面板類型設定為 "3611c"
    When 用戶檢測面板按鈕 "power" 的顏色
    Then 面板按鈕顏色應該為 "blue"
```

---

## 🎨 完整關鍵字列表

### Given 關鍵字 (環境設定)

```robotframework
Given 測試環境設定為 "${environment}"
# 設定測試環境: taipei_lab, taoyuan_lab, rv_car

Given 面板類型設定為 "${panel_type}"
# 設定面板類型: 3510a, 3611a, 3611c

Given 機器手臂已連接到遠端伺服器 "${host}" "${port}"
# 連接機器手臂 Server
```

### When 關鍵字 (執行動作)

```robotframework
When 用戶檢測面板按鈕 "${button_id}" 的顏色
# 執行面板按鈕顏色檢測
# button_id: light1, light2, light3, bluetooth, power, mode, 等

When 用戶檢測實體燈光亮度 "${light_id}"
# 執行實體燈光亮度檢測
# light_id: ceiling_light_1, desk_lamp, headlight_left, 等
```

### Then 關鍵字 (驗證結果)

```robotframework
Then 面板按鈕顏色應該為 "${expected_color}"
# 驗證顏色: blue, white, red, green, yellow, orange, purple, off

Then 實體燈光亮度應該為 "${expected_level}" %
# 驗證亮度: 0, 10, 20, ..., 90, 100

Then 視覺檢測信心度應該大於 ${min_confidence}
# 驗證信心度 (通常設定 0.85)
```

---

## 🛠️ ROI 校準指南

在使用視覺檢測前，您需要先校準每個按鈕的 ROI (Region of Interest) 座標。

### Step 1: 啟動校準工具

```bash
cd scripts
python web_roi_calibrator.py

# 瀏覽器自動開啟 http://localhost:5000
```

### Step 2: 選擇環境與面板

1. 選擇環境 (taipei_lab / taoyuan_lab / rv_car)
2. 選擇面板類型 (3510a / 3611a / 3611c)
3. 點擊「載入影像」

### Step 3: 框選按鈕 ROI

1. 使用滑鼠在影像上拖曳框選按鈕 LED 區域
2. 確保 ROI 完整覆蓋按鈕，但不包含背景
3. 記錄 ROI 座標 (x, y, width, height)

### Step 4: 記錄觀測角度

1. 移動機器手臂到可清晰拍攝按鈕的角度
2. 使用 `When 用戶取得當前角度` 取得角度值
3. 記錄角度到 YAML 配置的 `observe_angles`

### Step 5: 更新 YAML 配置

編輯對應環境的 YAML 檔案 (例如 `config/robot_arm/taipei_lab_buttons.yaml`):

```yaml
panels:
  "3611a":
    buttons:
      light1:
        name: "燈光按鈕 1"
        type: "panel_light"
        roi:
          x: 320        # ← 更新這些值
          y: 200
          width: 100
          height: 100
        observe_angles: [7.56, -35.59, -37.96, -15.73, -89.29, 6.06]  # ← 更新角度
        expected_colors: ["blue", "white"]
```

---

## 📊 測試報告解讀

執行測試後，開啟 `log.html` 查看詳細報告：

### 成功案例
```
✅ 面板按鈕顏色檢測成功
   檢測顏色: blue
   信心度: 0.95
   亮度: 245
   HSV 值: (110, 180, 245)
```

### 失敗案例
```
❌ 面板按鈕顏色不符預期！
   預期顏色: blue
   實際顏色: white
   信心度: 0.92
   亮度: 250
   HSV 值: (5, 10, 250)

建議: 檢查按鈕實際狀態，或調整 HSV 顏色範圍
```

### 亮度檢測結果
```
✅ 實體燈光亮度檢測成功
   實際亮度: 52%
   預期亮度: 50%
   誤差: 2% (允許 ±10%)
   信心度: 0.88
```

---

## 🔍 常見問題 (FAQ)

### Q1: 如何切換環境？

**A**: 使用 `Given 測試環境設定為 "${environment}"` 關鍵字：

```robotframework
Given 測試環境設定為 "taipei_lab"    # RTSP 影像源
Given 測試環境設定為 "taoyuan_lab"  # Socket 影像源
Given 測試環境設定為 "rv_car"       # Socket 影像源
```

### Q2: 顏色檢測不準確怎麼辦？

**A**: 調整環境專屬 HSV 範圍：

1. 編輯 `config/robot_arm/environment_config.py`
2. 修改 `hsv_adjustments` 參數：

```python
"taipei_lab": {
    "hsv_adjustments": {
        "blue": {
            "lower": [95, 50, 50],   # 調整這裡
            "upper": [135, 255, 255]
        }
    }
}
```

### Q3: RTSP 連接失敗怎麼辦？

**A**: 檢查以下項目：

```bash
# 1. 測試 RTSP 串流
ffmpeg -i rtsp://10.42.0.100:554/stream1 -frames:v 1 test.jpg

# 2. 檢查網路連接
ping 10.42.0.100

# 3. 確認 IP Camera 已開機
```

### Q4: Socket 影像源連接失敗？

**A**: 確認機器手臂 Server 運行正常：

```bash
# 在 Jetson Nano 上檢查
ps aux | grep robot_arm_server

# 測試連接
curl http://10.42.0.180:9000/health
```

### Q5: ROI 座標如何確認正確？

**A**: 使用 debug 模式查看框選結果：

```robotframework
When 用戶檢測面板按鈕 "light1" 的顏色
# 檢查 output/ 目錄下的 debug 影像
# 應該看到 ROI 框選區域
```

### Q6: 支援哪些顏色？

**A**: 目前支援 8 種顏色：
- `blue` - 藍色
- `white` - 白色
- `red` - 紅色
- `green` - 綠色
- `yellow` - 黃色
- `orange` - 橘色
- `purple` - 紫色
- `off` - 關閉 (黑色)

### Q7: 如何新增自定義顏色？

**A**: 編輯 `libraries/robot_arm_control/local_vision_analyzer.py`:

```python
COLOR_RANGES = {
    # ... 現有顏色 ...
    "pink": {  # 新增粉紅色
        "lower": [160, 50, 50],
        "upper": [180, 255, 255]
    }
}
```

### Q8: 測試案例執行太慢？

**A**: 調整檢測參數以提升速度：

```python
# 在 RobotArmKeywords.py 中調整
detect_panel_light(
    num_frames=3,      # 減少幀數 (預設 5)
    warmup_frames=10   # 減少預熱 (預設 20)
)
```

---

## 🎓 進階使用

### 自定義 HSV 範圍

如果預設 HSV 範圍不適合您的環境光源，可以自定義：

```python
# config/robot_arm/environment_config.py
"taipei_lab": {
    "hsv_adjustments": {
        "blue": {"lower": [95, 50, 50], "upper": [135, 255, 255]},
        "red": {"lower": [0, 100, 100], "upper": [10, 255, 255]}
    }
}
```

### 多幀平均參數調整

```python
# 調整多幀平均參數以平衡速度與準確度
results = self.local_vision.detect_panel_light(
    panel_type=self.current_panel_type,
    roi_config=roi_config,
    num_frames=5,         # 增加幀數提升穩定性
    warmup_frames=20,     # 增加預熱幀數
    save_debug_images=True  # 儲存 debug 影像
)
```

### 批次檢測多個按鈕

```robotframework
*** Test Cases ***
批次檢測所有燈光按鈕
    [Documentation]    一次檢測 3611a 面板所有按鈕

    Given 測試環境設定為 "taipei_lab"
    And 面板類型設定為 "3611a"
    And 機器手臂已連接到遠端伺服器 "10.42.0.180" "9000"

    FOR    ${button}    IN    light1    light2    light3    bluetooth
        When 用戶檢測面板按鈕 "${button}" 的顏色
        Then 視覺檢測應該成功
        Log    ${button} 檢測完成
    END
```

---

## 📞 技術支援

**遇到問題？**
1. 查看 [故障排除指南](vision_detection_troubleshooting_guide.md)
2. 查看 [完整 API 文檔](RobotArmKeywords.html)
3. 查看測試案例範例: `tests/robot_arm/`

**需要協助？**
- 技術支援: Robot Automation Team
- 文檔版本: v4.0.0
- 最後更新: 2025-11-18

---

**🎉 現在您已經掌握本機化視覺檢測系統的基本使用方法！開始撰寫您的第一個測試案例吧！**
