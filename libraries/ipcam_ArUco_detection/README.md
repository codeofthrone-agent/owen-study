# IPCam ArUco 空間追蹤檢測模組

結合 IP Camera 即時 RTSP 影像串流與 OpenCV ArUco 電腦視覺辨識，用以高精度檢測 RV 露營車內「擴展艙 (slide-out)」或實體空間放大縮小的動態變化，並內建高門檻歷史防抖判定機制。

## 功能特色

- 📹 **RTSP 串流支援** - 直接透過 RTSP 協議拉取即時監控攝影機畫面
- 🎯 **ArUco 空間檢測** - 透過測量特定 Marker 視覺網格面積的變化幅度計算空間遠近狀態
- 🛡️ **極致防抖演算法** - 內建 `history_size` 滑動平均加上 `confidence_required` 連續信心達標機制，排除車內人員飄過或光源改變造成的誤判
- 🔄 **多攝影機切換** - 支援同時連線並單獨控制多環境、多攝影機配置
- 🤖 **Robot Framework 整合** - 完全相容 Gherkin 語法（Given-When-Then）與中文語意

## 系統需求

### 必要套件

```bash
uv pip install opencv-python numpy opencv-contrib-python
```

### 系統配置與標籤需求

- 支援 RTSP 的 IP 攝影機
- 現場空間需黏貼 **ArUco標籤（DICT_4X4_50）** 供攝影機捕捉
- 解析度：穩定接收 IP Camera 的 RTSP 直播畫面

## 快速開始

### 1. 配置設定

編輯 `config/ipcam_config.yaml` 環境配置，定義欲連線攝影機之 ArUco 參數：

```yaml
environments:
  rv_car:
    cameras:
      taoyuan_4F:                        # 攝影機名稱
        ip: "10.42.0.25"
        port: 554
        protocol: "rtsp"
        stream_path: "/live0"
        # -- 新增專屬的 ArUco 防抖設定區塊 --
        aruco:
          name: "rv_motor 高門檻防抖"
          target_id: 1                   # ArUco Marker ID
          history_size: 15               # 收集多少歷史資料後才做判定
          move_threshold: 3500           # 判定區域變更（縮放）的基礎門檻面積
          stable_threshold: 1500         # （進階）靜止不動狀態判定容差
          confidence_required: 10        # 要連續判定成功多少次才確實驗證結果（防抖）
```

*(帳戶與密碼將一併由最外層的 `.env` 中 `IPCAM_USERNAME`、`IPCAM_PASSWORD` 輔助提供)*

### 2. Python 監控與使用範例

可直接透過底下主程式進入手動開發驗證測試：

```bash
uv run python3 libraries/ipcam_ArUco_detection/ArUcoSpaceDetection.py
```

如果你是在 Python 專案中使用，可以：

```python
from libraries.ipcam_ArUco_detection.ArUcoSpaceDetection import ArUcoSpaceDetection

detector = ArUcoSpaceDetection()
detector.connect_camera('rv_car', 'taoyuan_4F')

# 取得當下的一幀判定
state = detector.get_current_space_state()
print(f"目前空間狀態: {state}")

# 動態連續監控 10 秒（適合動態擴展過程）
history = detector.monitor_space_changes(duration_sec=10)
print(history)

detector.disconnect() # 記得歸還攝影機資源
```

### 3. Robot Framework 使用範例

```robotframework
*** Settings ***
Library    libraries.ipcam_ArUco_detection.ArUcoKeywords

*** Test Cases ***
檢測 RV 車庫縮放動態
    [Documentation]    Gherkin 風格的車庫空間監測、動態紀錄與狀態驗證
    [Tags]    ipcam    aruco    gherkin
    Given 專屬攝影機已連線 "rv_car" "taoyuan_4F"
    
    # 狀態直接提取與驗證
    When 取得當前車內空間狀態
    Then 車內空間狀態應該為 "close"
    
    # 時段觀察與紀錄驗證
    ${history}=    When 觀察並記錄空間動態 "10" 秒
    Then 動態觀察狀態應包含 "moving"    ${history}
    
    [Teardown]    And 斷開攝影機連線
```

## API 參考

### ArUcoSpaceDetection 類別

負責核心的 RTSP 擷取、影像處理、以及防抖演算法分析。

- `connect_camera(environment, camera_name)`: 解析 YAML、套用參數、建立 OpenCV VideoCapture。
- `get_current_space_state()`: 取一幀分析 ID，應用面積歷史滑動與信心指標。
- `monitor_space_changes(duration_sec)`: 同步卡頓執行指定秒數，回傳這段時間內所有的狀態變化軌跡列表。

## Robot Framework 關鍵字

在 `.robot` 檔案中，請在 `*** Settings ***` 區段載入模組：`Library    libraries.ipcam_ArUco_detection.ArUcoKeywords`

### 連線與配置管理

- `Given 專屬攝影機已連線 "${environment}" "${camera_name}"`

### 狀態擷取與觀察

- `When 取得當前車內空間狀態`
- `When 觀察並記錄空間動態 "${duration_sec}" 秒`

### 狀態驗證

- `Then 車內空間狀態應該為 "${expected_state}"`
- `Then 動態觀察狀態應包含 "${expected_state}"`

### 資源釋放

- `And 斷開攝影機連線`

## 故障排除

### 問題：連線成功但 get_current_space_state 始終無法判定為展開/收縮

**可能原因:**
- `history_size` 或 `confidence_required` 設太高，還沒累積夠影像樣本就超時。
- 光源太暗，ArUco tag 辨識失敗，可觀察 Terminal 中的錯誤 Log 了解是否被棄圖。

**解決方法:**
1. 打開 `ipcam_config.yaml`。
2. 調低 `move_threshold` 讓系統更靈敏，或調低 `confidence_required` 來降低防抖強度。

### 問題：無法連上 RTSP

**解決方法:**
1. 確保電腦和攝影機處於同一網路。
2. 確認 `.env` 內配置的密碼正確且未被改變。

## 目錄結構

```text
libraries/ipcam_ArUco_detection/
├── __init__.py                     # 模組初始化
├── ArUcoKeywords.py                # Robot Framework 關鍵字暴露層
├── ArUcoSpaceDetection.py          # 電腦視覺、連線、防抖算法核心
├── ArUco_Taoyuan_RV_Camera3.py     # 整合測試與歷史實驗腳本
├── README.md                       # 本說明文件
└── marker_1.png                    # Demo 用標籤參考圖片
```
