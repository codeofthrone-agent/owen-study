# ArUco Space Detection 關鍵字參考手冊 (Keyword README)

**建立日期:** 2026-04-07
**對應模組:** `libraries.ipcam_ArUco_detection.ArUcoSpaceDetection`

本文件詳細列出了使用 IP Camera 結合 ArUco 影像辨識進行空間狀態判定所提供的 Robot Framework 關鍵字。測試撰寫人員可參閱此手冊將相關動作寫入 `.robot` 測試腳本中。

---

## 載入函式庫

在 `.robot` 檔案中，請在 `*** Settings ***` 區段載入此模組：

```robotframework
*** Settings ***
Library    libraries.ipcam_ArUco_detection.ArUcoSpaceDetection
```

---

## 關鍵字清單

### 1. 連接攝影機

*   **說明**: 建立 IP Camera 的影像串流連線。執行時會自動往 `config/ipcam_config.yaml` 讀取並套用對應的攝影機網址與專屬的 ArUco 防抖門檻設定。請確保必須先呼叫此關鍵字才能進行後續狀態判定。
*   **參數**:
    *   `environment` (字串, 必填): 部署環境名稱（預設為 `rv_car`）。
    *   `camera_name` (字串, 必填): 攝影機代號（例如 `rv_motor`, `cam3` 等）。
*   **使用範例**:
    ```robotframework
    *** Test Cases ***
    初始化車內攝影機
        Given 連接攝影機    environment=rv_car    camera_name=rv_motor
    ```

### 2. 取得當前車內空間狀態

*   **說明**: 即時抓取影像現有的 ArUco 標籤大小，並經過「滑動平均」及「連續信心打分」後，回傳車內當前的空間狀態判斷。
*   **回傳值**: 字串 (可能為 `"穩定"`, `"收縮中"`, `"外推中"`)
*   **使用範例**:
    ```robotframework
    *** Test Cases ***
    檢查車廂起步狀態
        When 取得當前車內空間狀態
        Then 結果應為穩定
    ```

### 3. 觀察並記錄空間動態

*   **說明**: 在指定的時長內，持續監控畫面的動態狀態轉換，並記錄這段時間內發生過的所有狀態變化（去除重複狀態）。適合用在動作觸發後，去監測這幾秒內是否發生過「收縮中」或「外推中」的情境。
*   **參數**:
    *   `duration_sec` (整數, 選填, 預設=10): 要持續觀察的秒數。
*   **回傳值**: 列表 List (例如 `['穩定', '收縮中', '穩定']`)
*   **使用範例**:
    ```robotframework
    *** Test Cases ***
    觸發關閉按鈕並監控收縮
        # 假設前面有關閉按鈕動作
        When 觀察並記錄空間動態    duration_sec=30
        Then 記錄列表中應包含收縮中狀態
    ```

### 4. 斷開攝影機連線

*   **說明**: 安全釋放資源，切斷與攝影機的即時 RTSP 影像連線。建議在 `Teardown` 區段統一呼叫，避免記憶體洩漏與頻寬浪費。
*   **使用範例**:
    ```robotframework
    *** Test Cases ***
    清理測試環境
        [Teardown]    斷開攝影機連線
    ```
