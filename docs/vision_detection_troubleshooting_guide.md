# 本機化視覺檢測系統 - 故障排除指南

**版本**: v4.0.0
**日期**: 2025-11-18
**作者**: Robot Automation Team

---

## 🔧 故障排除流程

遇到問題時，請按照以下順序進行排查：

```
1. 檢查錯誤訊息 → 2. 查看日誌 → 3. 驗證硬體連接 → 4. 檢查配置 → 5. 諮詢文檔
```

---

## ⚠️ 常見錯誤與解決方案

### 錯誤 1: 環境設定失敗

**錯誤訊息**:
```
ValueError: 未知環境: taipei_labb
可用環境: taipei_lab, taoyuan_lab, rv_car
```

**原因**: 環境名稱拼寫錯誤

**解決方案**:
```robotframework
# ❌ 錯誤
Given 測試環境設定為 "taipei_labb"

# ✅ 正確
Given 測試環境設定為 "taipei_lab"
```

**驗證**:
```bash
# 列出所有可用環境
python -c "
from config.robot_arm.environment_config import EnvironmentConfig
print(EnvironmentConfig.list_environments())
"
```

---

### 錯誤 2: 面板類型不支援

**錯誤訊息**:
```
ValueError: 當前環境不支援面板類型: 3611b
```

**原因**: 選擇的面板類型在當前環境中不存在

**解決方案**:

檢查環境支援的面板類型：

| 環境 | 支援面板類型 |
|------|-------------|
| taipei_lab | 3510a, 3611a, 3611c |
| taoyuan_lab | 3510a, 3611a |
| rv_car | 3611c |

```robotframework
# ❌ 錯誤 - rv_car 不支援 3611a
Given 測試環境設定為 "rv_car"
And 面板類型設定為 "3611a"

# ✅ 正確
Given 測試環境設定為 "rv_car"
And 面板類型設定為 "3611c"
```

---

### 錯誤 3: 機器手臂連接失敗

**錯誤訊息**:
```
ConnectionError: 無法連接到機器手臂伺服器 10.42.0.180:9000
```

**可能原因**:
1. 機器手臂 Server 未啟動
2. IP 地址錯誤
3. 網路不通
4. 防火牆阻擋

**診斷步驟**:

**Step 1: 檢查 Server 狀態**
```bash
# 在 Jetson Nano 上檢查
ps aux | grep robot_arm_server

# 如果沒有運行，啟動它
cd ~/server
./run_server.sh
```

**Step 2: 測試網路連接**
```bash
# 測試 ping
ping 10.42.0.180

# 測試端口
telnet 10.42.0.180 9000
# 或
nc -zv 10.42.0.180 9000
```

**Step 3: 測試 API**
```bash
# 測試健康檢查端點
curl http://10.42.0.180:9000/health

# 應該回傳: {"status": "ok"}
```

**Step 4: 檢查防火牆**
```bash
# 在 Jetson Nano 上
sudo ufw status
sudo ufw allow 9000/tcp
```

**Step 5: 檢查 Server 日誌**
```bash
# 在 Jetson Nano 上
tail -f ~/server/server.log
```

---

### 錯誤 4: RTSP 串流連接失敗

**錯誤訊息**:
```
RTSPConnectionError: 無法連接到 RTSP 串流: rtsp://10.42.0.100:554/stream1
Timeout after 10 seconds
```

**可能原因**:
1. IP Camera 未開機
2. RTSP URL 錯誤
3. 網路不通
4. Camera 達到最大連接數

**診斷步驟**:

**Step 1: 測試 RTSP 串流**
```bash
# 使用 FFmpeg 測試
ffmpeg -i rtsp://10.42.0.100:554/stream1 -frames:v 1 test.jpg

# 檢查是否產生 test.jpg
ls -lh test.jpg
```

**Step 2: 測試網路**
```bash
# Ping Camera
ping 10.42.0.100

# Telnet 測試端口
telnet 10.42.0.100 554
```

**Step 3: 檢查 RTSP URL**
```bash
# 常見 RTSP URL 格式
rtsp://ip:port/stream1           # Hikvision
rtsp://ip:port/Streaming/Channels/101  # Dahua
rtsp://ip:port/live              # 通用

# 使用 VLC 測試
vlc rtsp://10.42.0.100:554/stream1
```

**Step 4: 增加超時時間**

編輯 `config/robot_arm/environment_config.py`:
```python
"taipei_lab": {
    # ...
    "rtsp_url": "rtsp://10.42.0.100:554/stream1",
    "rtsp_timeout": 20,  # 增加超時時間到 20 秒
}
```

**Step 5: 重啟 Camera**
```bash
# 重啟 IP Camera 電源
# 或透過 Web 介面重啟
```

---

### 錯誤 5: Socket 影像源連接失敗

**錯誤訊息**:
```
SocketImageSourceError: 無法從 Socket 取得影像
Connection refused
```

**可能原因**:
1. 機器手臂 Server 未運行
2. USB Camera 未連接
3. Camera 權限問題

**診斷步驟**:

**Step 1: 檢查 Server**
```bash
# 在 Jetson Nano 上
ps aux | grep robot_arm_server
```

**Step 2: 檢查 USB Camera**
```bash
# 在 Jetson Nano 上列出 Camera
v4l2-ctl --list-devices

# 測試 Camera
ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 test.jpg
```

**Step 3: 檢查權限**
```bash
# 在 Jetson Nano 上
ls -l /dev/video0

# 加入 video 群組
sudo usermod -a -G video $USER
# 重新登入生效
```

**Step 4: 測試 Server Camera API**
```bash
# 請求影像
curl -X POST http://10.42.0.180:9000/capture_image \
  -H "Content-Type: application/json" \
  -d '{"num_frames": 1}' \
  -o camera_test.jpg
```

---

### 錯誤 6: 按鈕配置不存在

**錯誤訊息**:
```
ValueError: 按鈕 'light4' 不存在於當前面板配置
```

**原因**: YAML 配置中沒有該按鈕

**解決方案**:

**Step 1: 檢查按鈕 ID**

查看 YAML 配置檔案 (例如 `config/robot_arm/taipei_lab_buttons.yaml`):
```yaml
panels:
  "3611a":
    buttons:
      light1: {...}  # ✅ 存在
      light2: {...}  # ✅ 存在
      light3: {...}  # ✅ 存在
      # light4 不存在 ❌
```

**Step 2: 新增按鈕配置**
```yaml
panels:
  "3611a":
    buttons:
      light4:  # 新增 light4
        name: "燈光按鈕 4"
        type: "panel_light"
        roi:
          x: 200
          y: 300
          width: 100
          height: 100
        observe_angles: [5, -35, -38, -15, -89, 6]
        expected_colors: ["blue"]
```

**Step 3: 使用 ROI 校準工具**
```bash
cd scripts
python web_roi_calibrator.py
# 校準新按鈕的 ROI 座標
```

---

### 錯誤 7: 顏色檢測不準確

**錯誤訊息**:
```
AssertionError: ❌ 面板按鈕顏色不符預期！
   預期顏色: blue
   實際顏色: white
   信心度: 0.92
```

**可能原因**:
1. HSV 顏色範圍不適合當前光源
2. ROI 區域包含背景
3. 按鈕實際顏色確實不是預期顏色

**診斷步驟**:

**Step 1: 確認按鈕實際狀態**
```bash
# 檢查 debug 影像
ls -lh output/debug_*.jpg

# 開啟影像確認按鈕顏色
xdg-open output/debug_latest.jpg
```

**Step 2: 調整 HSV 範圍**

使用 Python 腳本測試 HSV 範圍:
```python
import cv2
import numpy as np

# 載入影像
image = cv2.imread('output/debug_latest.jpg')
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 測試不同的 HSV 範圍
lower_blue = np.array([95, 50, 50])
upper_blue = np.array([135, 255, 255])

mask = cv2.inRange(hsv, lower_blue, upper_blue)
cv2.imwrite('hsv_test_mask.jpg', mask)
```

**Step 3: 更新環境專屬 HSV**

編輯 `config/robot_arm/environment_config.py`:
```python
"taipei_lab": {
    "hsv_adjustments": {
        "blue": {
            "lower": [95, 50, 50],    # 調整這裡
            "upper": [135, 255, 255]   # 調整這裡
        }
    }
}
```

**Step 4: 重新校準 ROI**

如果 ROI 包含太多背景：
```bash
cd scripts
python web_roi_calibrator.py
# 重新框選，縮小 ROI 區域
```

---

### 錯誤 8: 亮度檢測誤差過大

**錯誤訊息**:
```
AssertionError: ❌ 實體燈光亮度不符預期！
   預期亮度: 50%
   實際亮度: 72%
   誤差: 22% (允許 ±10%)
```

**可能原因**:
1. 環境光線變化
2. ROI 區域包含非燈光區域
3. 亮度計算參數需調整

**診斷步驟**:

**Step 1: 確認環境光線穩定**
```bash
# 關閉其他燈光
# 避免陽光直射
# 確保環境光線穩定
```

**Step 2: 調整 ROI 區域**
```bash
# 確保 ROI 只包含燈光本身
cd scripts
python web_roi_calibrator.py
```

**Step 3: 調整亮度檢測參數**

編輯 `libraries/robot_arm_control/local_vision_analyzer.py`:
```python
def detect_physical_light_brightness(self, ...):
    # 調整平均亮度的權重
    brightness_value = np.mean(roi_hsv[:, :, 2])  # V channel
    # 可改為使用最大值或中位數
    # brightness_value = np.max(roi_hsv[:, :, 2])
    # brightness_value = np.median(roi_hsv[:, :, 2])
```

**Step 4: 增加容許誤差**

如果環境光線確實變化大：
```robotframework
# 使用自定義驗證
When 用戶檢測實體燈光亮度 "ceiling_light_1"
${actual} =    Get Detection Result    brightness_level
Should Be True    ${actual} >= 40 and ${actual} <= 60    # 允許 ±10%
```

---

### 錯誤 9: YAML 配置格式錯誤

**錯誤訊息**:
```
yaml.scanner.ScannerError: while scanning a simple key
  in "taipei_lab_buttons.yaml", line 25, column 1
could not find expected ':'
```

**原因**: YAML 語法錯誤（縮排、冒號、引號等）

**診斷步驟**:

**Step 1: 驗證 YAML 語法**
```bash
# 使用 Python 驗證
python -c "
import yaml
with open('config/robot_arm/taipei_lab_buttons.yaml', 'r') as f:
    yaml.safe_load(f)
print('✅ YAML 格式正確')
"
```

**Step 2: 常見 YAML 錯誤**

```yaml
# ❌ 錯誤 - 縮排不一致 (混用 tab 和空格)
panels:
  "3611a":
	buttons:  # ← 這裡用 tab

# ✅ 正確 - 統一使用 2 空格
panels:
  "3611a":
    buttons:

# ❌ 錯誤 - 缺少冒號
panels:
  "3611a"
    buttons

# ✅ 正確
panels:
  "3611a":
    buttons:

# ❌ 錯誤 - 引號不匹配
name: "燈光按鈕 1'

# ✅ 正確
name: "燈光按鈕 1"
```

**Step 3: 使用線上 YAML 驗證工具**
- https://www.yamllint.com/
- 貼上 YAML 內容檢查語法

---

### 錯誤 10: 記憶體不足

**錯誤訊息**:
```
MemoryError: Unable to allocate array
```

**可能原因**:
1. 多幀平均使用過多幀數
2. 影像解析度過高
3. 系統記憶體不足

**解決方案**:

**Step 1: 減少幀數**
```python
# 調整檢測參數
results = self.local_vision.detect_panel_light(
    num_frames=3,      # 減少到 3 幀
    warmup_frames=5    # 減少預熱幀數
)
```

**Step 2: 降低影像解析度**

在 Jetson Nano Server 上調整 Camera 解析度:
```python
# robot_arm_server.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 降低寬度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 降低高度
```

**Step 3: 檢查系統記憶體**
```bash
# 查看記憶體使用
free -h

# 清理快取
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

---

## 🔍 診斷工具

### 1️⃣ 日誌分析

**查看 Robot Framework 日誌**:
```bash
# 開啟詳細日誌
xdg-open log.html

# 搜尋關鍵字: ERROR, FAIL, Exception
```

**Python 日誌位置**:
```bash
# LocalVisionAnalyzer 日誌
libraries/robot_arm_control/logs/vision_analyzer.log

# ImageSourceManager 日誌
libraries/robot_arm_control/logs/image_source.log
```

### 2️⃣ Debug 影像

**檢查 debug 影像**:
```bash
# debug 影像位置
ls -lh output/debug_*.jpg

# 最新 debug 影像
xdg-open output/debug_latest.jpg

# ROI 區域影像
xdg-open output/roi_*.jpg
```

### 3️⃣ 網路診斷

**完整網路診斷腳本**:
```bash
#!/bin/bash
# network_diagnostics.sh

echo "=== 機器手臂連接測試 ==="
ping -c 3 10.42.0.180
curl http://10.42.0.180:9000/health

echo ""
echo "=== RTSP Camera 連接測試 ==="
ping -c 3 10.42.0.100
ffprobe rtsp://10.42.0.100:554/stream1

echo ""
echo "=== 端口測試 ==="
nc -zv 10.42.0.180 9000
nc -zv 10.42.0.100 554

echo ""
echo "✅ 診斷完成"
```

### 4️⃣ 環境驗證腳本

**建立驗證腳本 `verify_environment.sh`**:
```bash
#!/bin/bash
# verify_environment.sh

echo "=== 1. Python 環境檢查 ==="
python --version
source .venv/bin/activate
python -c "import cv2; import numpy; print('✅ OpenCV 已安裝')"

echo ""
echo "=== 2. 配置檔案檢查 ==="
python -c "
from config.robot_arm.environment_config import EnvironmentConfig
import yaml

# 檢查環境配置
for env in EnvironmentConfig.list_environments():
    config = EnvironmentConfig.get_environment(env)
    print(f'✅ {env}: {config[\"name\"]}')

# 檢查 YAML 檔案
configs = [
    'config/robot_arm/taipei_lab_buttons.yaml',
    'config/robot_arm/taoyuan_lab_buttons.yaml',
    'config/robot_arm/rv_car_buttons.yaml'
]
for cfg in configs:
    with open(cfg, 'r') as f:
        yaml.safe_load(f)
    print(f'✅ {cfg} 格式正確')
"

echo ""
echo "=== 3. 網路連接檢查 ==="
ping -c 2 10.42.0.180 > /dev/null && echo "✅ 機器手臂網路通暢" || echo "❌ 機器手臂網路不通"
ping -c 2 10.42.0.100 > /dev/null && echo "✅ Camera 網路通暢" || echo "❌ Camera 網路不通"

echo ""
echo "=== 4. 硬體服務檢查 ==="
curl -s http://10.42.0.180:9000/health > /dev/null && echo "✅ 機器手臂 Server 運行" || echo "❌ 機器手臂 Server 未運行"

echo ""
echo "✅ 環境驗證完成"
```

執行驗證:
```bash
chmod +x verify_environment.sh
./verify_environment.sh
```

---

## 📋 錯誤代碼對照表

| 錯誤代碼 | 錯誤類型 | 嚴重程度 | 常見原因 |
|---------|---------|---------|---------|
| `ENV-001` | 環境設定錯誤 | 中 | 環境名稱拼寫錯誤 |
| `ENV-002` | 面板類型錯誤 | 中 | 面板不支援 |
| `CONN-001` | 機器手臂連接失敗 | 高 | Server 未啟動 |
| `CONN-002` | RTSP 連接失敗 | 高 | Camera 未開機 |
| `CONN-003` | Socket 連接失敗 | 高 | USB Camera 問題 |
| `CFG-001` | 按鈕配置不存在 | 中 | YAML 缺少按鈕 |
| `CFG-002` | YAML 格式錯誤 | 高 | 語法錯誤 |
| `DET-001` | 顏色檢測失敗 | 低 | HSV 範圍需調整 |
| `DET-002` | 亮度檢測誤差大 | 低 | 環境光線變化 |
| `SYS-001` | 記憶體不足 | 高 | 系統資源不足 |

---

## 🆘 緊急故障處理

### 情境 1: 測試完全無法執行

**快速修復流程**:
```bash
# 1. 重啟所有服務
# 在 Jetson Nano
killall robot_arm_server
cd ~/server && ./run_server.sh

# 2. 重建虛擬環境
cd /home/thortron/Tools/robot-multiplatform-automation
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. 驗證環境
python -c "from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords; print('✅')"

# 4. 執行最簡單的測試
robot --dryrun tests/robot_arm/basic_button_test.robot
```

### 情境 2: 檢測結果完全錯誤

**重新校準流程**:
```bash
# 1. 清除舊配置
mv config/robot_arm/taipei_lab_buttons.yaml config/robot_arm/taipei_lab_buttons.yaml.backup

# 2. 重新校準 ROI
cd scripts
python web_roi_calibrator.py

# 3. 測試單一按鈕
robot --test "檢測 Light1 按鈕為藍色" tests/robot_arm/basic_button_test.robot

# 4. 檢查 debug 影像
xdg-open output/debug_latest.jpg
```

---

## 📞 尋求協助

### 收集問題資訊

在尋求協助前，請收集以下資訊：

**1. 環境資訊**:
```bash
# 系統資訊
uname -a
python --version
robot --version

# 套件版本
pip list | grep -E "opencv|numpy|robotframework"
```

**2. 錯誤日誌**:
```bash
# Robot Framework 日誌
cat log.html | grep -A 10 "FAIL"

# Python 日誌
tail -100 libraries/robot_arm_control/logs/vision_analyzer.log
```

**3. 配置檔案**:
```bash
# 環境配置
cat config/robot_arm/environment_config.py

# YAML 配置
cat config/robot_arm/taipei_lab_buttons.yaml
```

**4. 網路狀態**:
```bash
# 連接測試
./verify_environment.sh > environment_report.txt
```

### 提問模板

```markdown
## 問題描述
[簡短描述問題]

## 環境資訊
- 作業系統: Ubuntu 24.04
- Python 版本: 3.12.x
- Robot Framework 版本: 7.3.1
- RobotArmKeywords 版本: v4.0.0

## 重現步驟
1. [步驟 1]
2. [步驟 2]
3. [步驟 3]

## 錯誤訊息
```
[貼上完整錯誤訊息]
```

## 已嘗試的解決方法
- [方法 1]
- [方法 2]

## 附件
- 日誌檔案: log.html
- Debug 影像: debug_latest.jpg
- 環境報告: environment_report.txt
```

---

## 📚 延伸閱讀

- [快速上手指南](vision_detection_quick_start_guide.md)
- [部署檢查清單](vision_detection_deployment_checklist.md)
- [完整 API 文檔](RobotArmKeywords.html)
- [TDD 開發指南](vision_detection_tdd_guide.md)

---

**技術支援**: Robot Automation Team
**文檔版本**: v4.0.0
**最後更新**: 2025-11-18

---

**💡 小提示**: 90% 的問題都可以透過檢查日誌、驗證硬體連接、和確認配置來解決！
