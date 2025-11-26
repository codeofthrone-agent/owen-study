# 多 RTSP 串流監控系統 使用說明

## 📺 系統概述

多 RTSP 串流監控系統是一個基於 Flask 的網頁應用程式，可以同時顯示多個 RTSP 影像串流。本系統已整合 `EnvironmentConfig`，可自動讀取專案中的環境配置（如 `ipcam_config.yaml`），並支援動態切換不同環境（如 `taipei_lab`, `rv_car` 等）。

## 🚀 快速開始

### 1. 環境需求
- Python 3.8+
- OpenCV (`cv2`)
- Flask
- python-dotenv（用於讀取 .env 文件）
- PyYAML

### 2. 啟動服務

#### 方式一：使用啟動腳本
```bash
# 給予執行權限
chmod +x scripts/start_multi_rtsp_viewer.sh

# 啟動（預設端口 5001）
./scripts/start_multi_rtsp_viewer.sh

# 自訂端口
./scripts/start_multi_rtsp_viewer.sh -p 8080

# 查看更多選項
./scripts/start_multi_rtsp_viewer.sh --help
```

#### 方式二：直接執行
```bash
# 使用 uv 環境
uv run python3 scripts/multi_rtsp_viewer.py --port 5002

# 或直接使用 Python
python3 scripts/multi_rtsp_viewer.py --port 5002
```

### 3. 存取網頁
- **本機存取**: http://localhost:5002
- **區網存取**: http://YOUR_IP:5002

## 🔐 認證設定

### 自動認證（推薦）
系統會自動讀取 `.env` 文件中的認證資訊，並透過 `EnvironmentConfig` 自動應用於所有 RTSP 串流：

```bash
# .env 文件範例
IPCAM_USERNAME=your_username
IPCAM_PASSWORD=your_password
```

## 🎛️ 功能特色

### 主要功能
- ✅ **多環境支援**：可透過網頁介面下拉選單，即時切換不同環境（例如：台北實驗室、RV Car）。
- ✅ **自動化配置**：直接讀取 `config/robot_arm/ipcam_config.yaml`，無需手動輸入 RTSP URL。
- ✅ **多串流同時顯示**：支援四格或更多攝影機同時監控，自動適應攝影機數量。
- 🔐 **自動認證**：自動處理 RTSP 帳號密碼。
- 📱 **響應式設計**：支援桌面、平板、手機等不同設備。
- 🔄 **即時更新**：可調整更新頻率（0.5-5秒）。

### 界面功能
- **環境選擇**：頂部下拉選單可選擇已定義的環境。
- **載入環境**：點擊「載入」按鈕即可切換至該環境的所有攝影機。
- **啟動/停止所有**：一鍵控制所有串流。
- **新增串流**：也可手動添加額外的 RTSP 串流。

## ⚙️ 配置說明

### 環境配置
本系統使用 `EnvironmentConfig` 統一管理配置。請確保 `config/robot_arm/ipcam_config.yaml` 或相關配置檔案已正確設定環境與攝影機資訊。

範例結構：
```yaml
environments:
  taipei_lab:
    name: "台北實驗室"
    cameras:
      level1:
        rtsp_url: "rtsp://192.168.165.184:554/live0"
      level2:
        rtsp_url: "rtsp://192.168.165.127:554/live0"
```

### 命令列參數
```bash
python3 scripts/multi_rtsp_viewer.py [選項]

選項:
  --port PORT           Web 伺服器端口 (預設: 5001)
  --no-default-config   不載入預設配置
  --max-workers NUM     最大工作線程數 (預設: 4)
  --interval SEC        預設更新頻率 (秒) (預設: 1.0)
  --stream-suffix PATH  RTSP 串流路徑後綴 (例如: stream1, live1) (預設: stream1)
  -h, --help           顯示說明
```

## 🔧 API 接口

系統提供 RESTful API 接口供程式整合：

### 環境管理
- `GET /api/environments` - 取得可用環境列表
- `POST /api/environments/<env_name>/load` - 載入指定環境
  - Body: `{"interval": 1.0, "suffix": "live1"}`

### 串流管理
- `GET /api/streams` - 取得所有串流資訊
- `POST /api/streams` - 新增串流
- `DELETE /api/streams/{stream_id}` - 刪除串流

### 串流控制
- `POST /api/streams/{stream_id}/start` - 啟動串流
- `POST /api/streams/{stream_id}/stop` - 停止串流
- `GET /api/streams/{stream_id}/frame` - 取得最新幀影像
- `POST /api/streams/start_all` - 啟動所有串流
- `POST /api/streams/stop_all` - 停止所有串流

## 🛠️ 故障排除

### 常見問題

#### 1. 找不到環境配置
**原因**：`EnvironmentConfig` 無法載入配置檔案。
**解決**：檢查 `config/robot_arm/` 下的 YAML 配置檔案是否存在且格式正確。

#### 2. "401 Unauthorized" 錯誤
**原因**：RTSP 需要認證但未提供正確的帳號密碼。
**解決**：確保 `.env` 文件包含正確的 `IPCAM_USERNAME` 和 `IPCAM_PASSWORD`。

#### 3. 影像顯示黑畫面
**原因**：串流存在但無法解碼影像。
**解決**：
- 嘗試使用 VLC 等播放器直接測試 RTSP URL。
- 檢查攝影機的編碼設定（建議使用 H.264）。

---

**版本**: v2.0 (2025-11-26)
**作者**: Robot Automation Team
**專案**: robot-multiplatform-automation