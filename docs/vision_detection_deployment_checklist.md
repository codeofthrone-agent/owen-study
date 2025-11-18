# 本機化視覺檢測系統 - 部署檢查清單

**版本**: v4.0.0
**日期**: 2025-11-18
**作者**: Robot Automation Team

---

## 📋 部署前檢查清單

### 1️⃣ 系統環境檢查

#### Python 環境
- [ ] Python 3.12 已安裝
- [ ] uv 套件管理工具已安裝
- [ ] 虛擬環境已建立 (`.venv/`)
- [ ] 所有相依套件已安裝 (`uv pip install -r requirements.txt`)

**驗證命令**:
```bash
python --version  # 應顯示 Python 3.12.x
uv --version      # 應顯示 uv 版本
source .venv/bin/activate
python -c "import cv2; import numpy; print('✅ OpenCV 已安裝')"
```

#### Robot Framework 環境
- [ ] Robot Framework 7.3.1+ 已安裝
- [ ] RobotArmKeywords 庫可正常匯入

**驗證命令**:
```bash
robot --version  # 應顯示 Robot Framework 7.3.1+
python -c "from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords; print('✅ RobotArmKeywords 可匯入')"
```

---

### 2️⃣ 硬體設備檢查

#### 機器手臂 (MyCobot 280)
- [ ] 機器手臂已連接並供電
- [ ] 機器手臂 Server 運行正常 (`robot_arm_server.py`)
- [ ] 網路連接正常 (可 ping 通機器手臂 IP)

**驗證命令**:
```bash
# 在 Jetson Nano 上啟動 Server
cd ~/server
./run_server.sh

# 在本機測試連接
ping 10.42.0.180  # 或 192.168.1.100 (依環境而定)
```

#### IP Camera (僅 taipei_lab 環境)
- [ ] IP Camera 已上電並連接網路
- [ ] RTSP 串流可存取
- [ ] 畫面清晰無遮擋

**驗證命令**:
```bash
# 測試 RTSP 串流
ffmpeg -i rtsp://10.42.0.100:554/stream1 -frames:v 1 test_frame.jpg
# 應產生 test_frame.jpg，檢查畫面是否正常
```

#### USB Camera (taoyuan_lab / rv_car 環境)
- [ ] USB Camera 已連接至機器手臂 Jetson Nano
- [ ] Camera 驅動正常運作
- [ ] 畫面品質符合需求

**驗證命令** (在 Jetson Nano 上):
```bash
# 列出可用 Camera
v4l2-ctl --list-devices

# 測試 Camera 擷取
ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 test.jpg
```

---

### 3️⃣ 網路環境檢查

#### 網路連通性
- [ ] 本機可連接到機器手臂 Server (10.42.0.180:9000 或 192.168.1.100:9000)
- [ ] 本機可連接到 RTSP Camera (10.42.0.100:554) - 僅 taipei_lab
- [ ] 網路延遲 < 50ms

**驗證命令**:
```bash
# 測試機器手臂連接
curl http://10.42.0.180:9000/health || echo "Server 未啟動"

# 測試 RTSP 連接 (taipei_lab)
ffprobe rtsp://10.42.0.100:554/stream1

# 測試網路延遲
ping -c 10 10.42.0.180
```

#### 防火牆設定
- [ ] 機器手臂 Server 端口 9000 已開放
- [ ] RTSP 端口 554 已開放 (taipei_lab)
- [ ] 無網路隔離或 VLAN 限制

---

### 4️⃣ 配置檔案檢查

#### 環境配置
- [ ] `config/robot_arm/environment_config.py` 參數正確
  - taipei_lab RTSP URL 正確
  - taoyuan_lab 機器手臂 IP 正確
  - rv_car 機器手臂 IP 正確
- [ ] 環境配置可正常載入

**驗證命令**:
```bash
python -c "
from config.robot_arm.environment_config import EnvironmentConfig
config = EnvironmentConfig.get_environment('taipei_lab')
print(f'✅ taipei_lab: {config[\"name\"]}')
config = EnvironmentConfig.get_environment('taoyuan_lab')
print(f'✅ taoyuan_lab: {config[\"name\"]}')
config = EnvironmentConfig.get_environment('rv_car')
print(f'✅ rv_car: {config[\"name\"]}')
"
```

#### YAML 按鈕配置
- [ ] `config/robot_arm/taipei_lab_buttons.yaml` 存在且格式正確
- [ ] `config/robot_arm/taoyuan_lab_buttons.yaml` 存在且格式正確
- [ ] `config/robot_arm/rv_car_buttons.yaml` 存在且格式正確
- [ ] ROI 座標已校準
- [ ] 觀測角度已記錄

**驗證命令**:
```bash
# 驗證 YAML 語法
python -c "
import yaml
from pathlib import Path

configs = [
    'config/robot_arm/taipei_lab_buttons.yaml',
    'config/robot_arm/taoyuan_lab_buttons.yaml',
    'config/robot_arm/rv_car_buttons.yaml'
]

for config_path in configs:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    print(f'✅ {config_path} 格式正確')
"
```

---

### 5️⃣ ROI 校準檢查

#### ROI 座標校準
- [ ] 已使用 `web_roi_calibrator.py` 校準所有按鈕 ROI
- [ ] ROI 區域完整覆蓋按鈕 LED
- [ ] ROI 區域不包含背景雜訊
- [ ] 所有 ROI 座標已更新至 YAML 配置

**校準步驟**:
```bash
# 啟動 ROI 校準工具
cd scripts
python web_roi_calibrator.py

# 瀏覽器開啟 http://localhost:5000
# 1. 選擇環境 (taipei_lab / taoyuan_lab / rv_car)
# 2. 選擇面板類型 (3510a / 3611a / 3611c)
# 3. 互動式框選每個按鈕 ROI
# 4. 儲存座標至 YAML 檔案
```

#### 觀測角度記錄
- [ ] 機器手臂觀測角度已測試
- [ ] 觀測角度可清晰拍攝按鈕
- [ ] 觀測角度避免反光/陰影
- [ ] 角度已記錄至 YAML 配置中的 `observe_angles`

**角度測試方法**:
```robotframework
# 測試觀測角度
Given 機器手臂已連接到遠端伺服器 "10.42.0.180" "9000"
When 用戶移動機器手臂到指定角度 [7.56, -35.59, -37.96, -15.73, -89.29, 6.06]
# 手動檢查畫面，確認按鈕清晰可見
```

---

### 6️⃣ HSV 顏色校準檢查

#### 環境專屬 HSV 調整
- [ ] taipei_lab 藍色 HSV 範圍已調整 (如有特殊光源)
- [ ] 其他環境使用預設 HSV 範圍
- [ ] HSV 調整已更新至 `environment_config.py`

**HSV 範圍參考** (預設值):
```python
COLOR_RANGES = {
    "blue": {"lower": [100, 50, 50], "upper": [130, 255, 255]},
    "white": {"lower": [0, 0, 200], "upper": [180, 30, 255]},
    "red": {"lower": [0, 50, 50], "upper": [10, 255, 255]},
    "green": {"lower": [40, 50, 50], "upper": [80, 255, 255]},
    "yellow": {"lower": [20, 50, 50], "upper": [35, 255, 255]},
    "orange": {"lower": [10, 50, 50], "upper": [20, 255, 255]},
    "purple": {"lower": [130, 50, 50], "upper": [160, 255, 255]},
}
```

**校準方法**:
```bash
# 使用 Python 腳本測試 HSV 範圍
cd libraries/robot_arm_control
python local_vision_analyzer.py

# 擷取影像並調整 HSV 範圍，直到顏色檢測準確
```

---

### 7️⃣ 功能測試檢查

#### 單元測試
- [ ] 所有 Python 單元測試通過

**驗證命令**:
```bash
# 執行所有單元測試
pytest libraries/robot_arm_control/tests/ -v

# 應看到:
# test_environment_config.py::TestEnvironmentConfig - 18 passed
# test_image_source_manager.py - X passed
# test_local_vision_analyzer.py - X passed
```

#### Robot Framework 測試
- [ ] 基礎測試案例通過
- [ ] 多環境測試案例通過
- [ ] 多色彩檢測測試案例通過
- [ ] 多級亮度檢測測試案例通過

**驗證命令**:
```bash
# 執行快速測試 (不需硬體)
robot --dryrun tests/robot_arm/

# 執行真機測試 (需硬體)
robot tests/robot_arm/basic_button_test.robot
robot tests/robot_arm/multi_environment_test.robot
robot tests/robot_arm/multi_color_detection_test.robot
robot tests/robot_arm/brightness_level_test.robot
```

---

### 8️⃣ 性能驗證

#### 檢測速度
- [ ] RTSP 影像源平均檢測時間 < 3 秒
- [ ] Socket 影像源平均檢測時間 < 1 秒
- [ ] 多幀平均處理順暢 (5-10 幀)

**性能測試**:
```bash
# 執行性能測試
robot --variable PERFORMANCE_TEST:true tests/robot_arm/performance_test.robot
```

#### 檢測準確度
- [ ] 顏色檢測成功率 > 95%
- [ ] 亮度檢測誤差 < ±10%
- [ ] 信心度 (confidence) > 0.85

---

### 9️⃣ 文檔完整性檢查

#### 核心文檔
- [ ] `libraries/robot_arm_control/README.md` 已更新至 v4.0.0
- [ ] `docs/vision_detection_local_migration_plan.md` 已完成
- [ ] `docs/vision_detection_local_spec.md` 已完成
- [ ] `docs/vision_detection_tdd_guide.md` 已完成
- [ ] `docs/vision_detection_deployment_checklist.md` (本文檔) 已完成

#### 使用者文檔
- [ ] 快速上手指南已撰寫
- [ ] 故障排除指南已撰寫
- [ ] API 文檔已產生 (libdoc)

**產生 API 文檔**:
```bash
# 產生 Robot Framework 關鍵字文檔
python -m robot.libdoc libraries/robot_arm_control/RobotArmKeywords.py \
    docs/RobotArmKeywords.html

# 開啟瀏覽器查看
xdg-open docs/RobotArmKeywords.html
```

---

### 🔟 CLAUDE.md 更新檢查

#### 專案說明更新
- [ ] `CLAUDE.md` 新增「本機化視覺檢測」章節
- [ ] 核心命令已更新
- [ ] 版本資訊已更新至 v4.0.0
- [ ] 架構圖已更新

**更新內容確認**:
- 新增 3 個環境說明 (taipei_lab / taoyuan_lab / rv_car)
- 新增影像源說明 (RTSP / Socket)
- 新增 6 個 BDD 關鍵字說明
- 新增常見問題與解決方案

---

## 🚀 部署執行清單

### Step 1: 環境設置
```bash
# 1. Clone 專案
git clone <repository_url>
cd robot-multiplatform-automation

# 2. 建立虛擬環境
uv venv
source .venv/bin/activate

# 3. 安裝相依套件
uv pip install -r requirements.txt

# 4. 驗證安裝
python -c "from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords; print('✅')"
```

### Step 2: 硬體設置
```bash
# 1. 啟動機器手臂 Server (在 Jetson Nano)
cd ~/server
./run_server.sh

# 2. 測試連接
ping 10.42.0.180

# 3. 測試 Camera (taipei_lab 需測試 RTSP)
ffmpeg -i rtsp://10.42.0.100:554/stream1 -frames:v 1 test.jpg
```

### Step 3: ROI 校準
```bash
# 1. 啟動校準工具
cd scripts
python web_roi_calibrator.py

# 2. 開啟瀏覽器 http://localhost:5000
# 3. 選擇環境並校準所有按鈕 ROI
# 4. 儲存座標至 YAML
```

### Step 4: 執行測試
```bash
# 1. 語法檢查
robot --dryrun tests/robot_arm/

# 2. 基礎測試
robot tests/robot_arm/basic_button_test.robot

# 3. 多環境測試
robot tests/robot_arm/multi_environment_test.robot

# 4. 檢查測試報告
xdg-open log.html
```

### Step 5: 驗證部署
```bash
# 1. 執行完整測試套件
robot tests/robot_arm/

# 2. 檢查測試結果
# - 所有測試通過率 > 95%
# - 無硬體連接錯誤
# - 檢測速度符合要求

# 3. 產生最終報告
robot --outputdir deployment_results tests/robot_arm/
```

---

## ✅ 部署驗收標準

### 功能驗收
- ✅ 所有 3 個環境可正常切換
- ✅ RTSP 影像源連接穩定
- ✅ Socket 影像源連接穩定
- ✅ 8 種顏色檢測準確
- ✅ 11 級亮度檢測準確
- ✅ ROI 校準精確
- ✅ 機器手臂移動順暢

### 性能驗收
- ✅ RTSP 檢測時間 < 3 秒
- ✅ Socket 檢測時間 < 1 秒
- ✅ 檢測成功率 > 95%
- ✅ 亮度誤差 < ±10%
- ✅ 信心度 > 0.85

### 文檔驗收
- ✅ 所有核心文檔完整
- ✅ 使用者文檔清晰易懂
- ✅ API 文檔自動產生
- ✅ 範例可執行

### 維護性驗收
- ✅ 程式碼結構清晰
- ✅ 測試覆蓋率充足
- ✅ 日誌記錄完整
- ✅ 錯誤處理健全

---

## 📞 支援與聯繫

**技術支援**: Robot Automation Team
**文檔版本**: v4.0.0
**最後更新**: 2025-11-18

---

**✨ 部署完成後，請將此清單歸檔並記錄實際部署結果！**
