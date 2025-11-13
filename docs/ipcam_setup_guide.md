# IP Camera 燈光檢測系統安裝指南

本指南將協助您完成 IP Camera 燈光檢測系統的安裝與配置。

## 📋 系統需求

- Python 3.8+
- Ubuntu 24.04（推薦）或其他 Linux 發行版
- 支援 RTSP 協議的 IP Camera
- 網路連線（能連接到 IP Camera）

## 🔧 安裝步驟

### 1. 安裝必要的 Python 套件

#### 使用 pip 直接安裝

```bash
pip install opencv-python numpy loguru pyyaml python-dotenv
```

#### 或使用 pipenv（推薦）

```bash
# 進入專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 啟動 pipenv 環境
pipenv shell

# 安裝套件
pipenv install opencv-python numpy loguru pyyaml
# python-dotenv 已經在 Pipfile 中
```

### 2. 配置 IP Camera 認證資訊

#### 編輯 .env 文件

複製範例文件並編輯：

```bash
cp .env.example .env
nano .env  # 或使用您喜歡的編輯器
```

設定 IP Camera 的帳號密碼（所有攝影機共用）：

```bash
# IP Camera RTSP 認證（所有攝影機共用）
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_actual_password_here
```

**重要提醒:**
- 請將 `your_actual_password_here` 替換為實際的 IP Camera 密碼
- `.env` 文件已在 `.gitignore` 中，不會被提交到版本控制

### 3. 驗證配置

執行配置測試腳本：

```bash
python3 scripts/test_ipcam_config.py
```

預期輸出應該顯示：
- ✅ 環境變數已載入
- ✅ 三個攝影機配置正確（level1, level2, motor）
- ✅ RTSP URL 建構成功

### 4. 測試攝影機連線

#### 方法 A：使用 VLC 測試 RTSP 連線

```bash
# 安裝 VLC（如果尚未安裝）
sudo apt install vlc

# 測試連線（替換實際的帳密和 IP）
vlc rtsp://admin:password@192.168.165.184:554/live0
```

如果能看到影像，表示 RTSP 連線正常。

#### 方法 B：使用 Python 簡單測試

```python
import cv2

# 建立 RTSP URL（替換實際的帳密和 IP）
rtsp_url = "rtsp://admin:password@192.168.165.184:554/live0"

# 嘗試連線
cap = cv2.VideoCapture(rtsp_url)

if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✅ 成功擷取影像！")
        print(f"影像尺寸: {frame.shape}")
    else:
        print("❌ 無法讀取影像幀")
else:
    print("❌ 無法開啟 RTSP 串流")

cap.release()
```

## 🧪 執行測試

### 執行完整測試套件

```bash
# 執行所有 IP Camera 測試
robot tests/ipcam_testing/ipcam_light_detection_test.robot

# 輸出詳細日誌
robot --loglevel DEBUG --outputdir results/ipcam tests/ipcam_testing/

# 只執行煙霧測試（快速驗證）
robot --include smoke tests/ipcam_testing/
```

### 執行單一測試案例

```bash
robot --test "測試案例 01: 連接實驗室 Level1 攝影機" \
  tests/ipcam_testing/ipcam_light_detection_test.robot
```

## 🔍 故障排除

### 問題 1: ModuleNotFoundError: No module named 'cv2'

**解決方法:**

```bash
pip install opencv-python
# 或
pipenv install opencv-python
```

### 問題 2: 無法連接到 RTSP 串流

**檢查清單:**

1. **網路連通性**
   ```bash
   ping 192.168.165.184
   ```

2. **RTSP port 是否開啟**
   ```bash
   telnet 192.168.165.184 554
   # 或使用 nc
   nc -zv 192.168.165.184 554
   ```

3. **帳號密碼是否正確**
   - 確認 .env 中的 `IPCAM_PASSWORD` 正確
   - 測試使用瀏覽器登入攝影機管理介面

4. **防火牆設定**
   ```bash
   # 檢查防火牆狀態
   sudo ufw status

   # 如果需要開放 port 554
   sudo ufw allow 554/tcp
   ```

### 問題 3: 影像擷取成功但亮度判定不準確

**調整閾值:**

編輯 `config/ipcam_config.yaml`：

```yaml
light_detection:
  brightness_threshold:
    dark: 30      # 降低暗閾值
    bright: 120   # 降低亮閾值
```

**使用全圖分析:**

```robotframework
${亮度} =    計算亮度    region=full
```

### 問題 4: RTSP 串流延遲或卡頓

**調整配置:**

編輯 `config/ipcam_config.yaml`：

```yaml
light_detection:
  connection:
    rtsp_buffer_size: 1    # 減少緩衝
    frame_skip: 5          # 增加跳過幀數
```

**使用次串流（解析度較低但流暢）:**

```robotframework
擷取影像    /live1
```

## 📝 配置說明

### IP Camera 配置結構

```
config/
├── ipcam_config.yaml       # 攝影機 IP、port、串流路徑
└── ipcam_config.py         # 配置載入邏輯

.env                         # 認證資訊（帳號密碼）
```

### 配置優先順序

1. **YAML 中的 username/password** - 最高優先（個別覆寫）
2. **.env 中的 IPCAM_USERNAME/IPCAM_PASSWORD** - 共用預設值
3. **空字串** - 無認證

### 添加新的攝影機

編輯 `config/ipcam_config.yaml`：

```yaml
environments:
  laboratory:
    cameras:
      new_camera:           # 新增攝影機
        ip: "192.168.1.100"
        port: 554
        protocol: "rtsp"
        stream_path: "/live0"
        description: "新增的攝影機"
        # username/password 會自動從 .env 讀取
```

## 🎯 快速測試流程

```bash
# 1. 進入專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 2. 啟動虛擬環境
pipenv shell

# 3. 設定 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 4. 驗證配置
python3 scripts/test_ipcam_config.py

# 5. 執行測試（只測試連線）
robot --include connection tests/ipcam_testing/

# 6. 查看測試報告
firefox results/report.html
```

## 📚 相關文檔

- [IP Camera Library README](../libraries/ipcam_light_detection/README.md) - 完整 API 文檔
- [測試案例說明](../tests/ipcam_testing/ipcam_light_detection_test.robot) - 測試案例詳情
- [Robot Framework 關鍵字](../resources/ipcam_keywords.robot) - 可用關鍵字列表

## 💡 使用建議

1. **開發階段**: 使用 `--loglevel DEBUG` 查看詳細日誌
2. **生產環境**: 調整亮度閾值以符合實際環境
3. **多攝影機**: 可以並行執行測試以提高效率
4. **整合測試**: 搭配 SwitchBot 進行完整的燈光控制測試

## ✅ 安裝檢查清單

- [ ] Python 3.8+ 已安裝
- [ ] OpenCV、NumPy、Loguru、PyYAML 已安裝
- [ ] .env 文件已配置（IPCAM_USERNAME 和 IPCAM_PASSWORD）
- [ ] 能夠 ping 通 IP Camera
- [ ] RTSP port 554 可連接
- [ ] 使用 VLC 或 Python 測試過 RTSP 連線
- [ ] 配置測試腳本執行成功
- [ ] Robot Framework 測試案例執行成功

## 🆘 獲取幫助

如果遇到問題：

1. 檢查日誌：`results/log.html`
2. 執行診斷腳本：`python3 scripts/test_ipcam_config.py`
3. 查看文檔：`libraries/ipcam_light_detection/README.md`
4. 檢查網路連線和防火牆設定

---

**安裝完成後**，您就可以開始使用 IP Camera 進行自動化燈光檢測測試了！🎉
