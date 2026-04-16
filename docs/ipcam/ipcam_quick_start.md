# IP Camera 燈光檢測 - 快速開始

## 🚀 5 分鐘快速設置

### 步驟 1: 安裝依賴套件（1 分鐘）

```bash
pipenv shell
pipenv install opencv-python numpy loguru pyyaml
```

### 步驟 2: 配置認證資訊（1 分鐘）

編輯 `.env` 文件：

```bash
# IP Camera RTSP 認證（所有攝影機共用）
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_password_here
```

### 步驟 3: 驗證配置（1 分鐘）

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 scripts/test_ipcam_config.py
```

### 步驟 4: 執行測試（2 分鐘）

```bash
robot --include smoke tests/ipcam_testing/
```

完成！🎉

## 📋 IP Camera 資訊

### 實驗室環境

| 名稱 | IP 位址 | RTSP URL 格式 |
|------|---------|---------------|
| Level1 | 192.168.165.184 | `rtsp://[user]:[pass]@192.168.165.184:554/live0` |
| Level2 | 192.168.165.127 | `rtsp://[user]:[pass]@192.168.165.127:554/live0` |
| Motor | 10.42.0.39 | `rtsp://[user]:[pass]@10.42.0.39:554/live0` |

## 💡 常用命令

### Python 使用

```python
from libraries.ipcam_light_detection import IPCamLightDetection

detector = IPCamLightDetection()
detector.connect_camera('laboratory', 'level1')
brightness = detector.get_current_brightness()
print(f"亮度: {brightness}")
```

### Robot Framework 使用

```robotframework
*** Test Cases ***
檢測燈光
    Given 連接實驗室 Level1 攝影機
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態
```

## 🎯 核心功能

- ✅ **RTSP 串流連線** - 支援主串流 `/live0` 和次串流 `/live1`
- ✅ **亮度分析** - 自動計算影像亮度（0-255）
- ✅ **燈光判定** - 根據閾值判定燈光開關狀態
- ✅ **狀態等待** - 等待燈光狀態變化（超時機制）
- ✅ **多攝影機** - 支援多環境、多攝影機切換

## 🔧 配置文件

### .env（認證資訊）
```
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_password
```

### config/ipcam_config.yaml（攝影機資訊）
```yaml
environments:
  laboratory:
    cameras:
      level1:
        ip: "192.168.165.184"
        port: 554
        protocol: "rtsp"
        stream_path: "/live0"
```

## 📚 更多資訊

- 完整文檔：[libraries/ipcam_light_detection/README.md](../libraries/ipcam_light_detection/README.md)
- 安裝指南：[docs/ipcam_setup_guide.md](./ipcam_setup_guide.md)
- 測試案例：[tests/ipcam_testing/ipcam_light_detection_test.robot](../tests/ipcam_testing/ipcam_light_detection_test.robot)
