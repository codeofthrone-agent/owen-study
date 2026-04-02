# 影像辨識：RV 車內伸縮空間 ArUco 檢測框架

> **🚀 快速執行空間防抖監控測試**：`uv run python libraries/ipcam_ArUco_detection/ArUcoSpaceDetection.py`
## 1. 簡介與用途 (Introduction)
此函式庫 (`ipcam_ArUco_detection`) 負責處理攝影機 (IPCam) 的即時影像串流，並透過 OpenCV 與 ArUco 標記檢測技術，計算 RV 車內伸縮空間的動態狀態（例如：「收縮中」、「外推中」或「穩定」）。

本目錄主要包含：
1. **車內空間即時判斷邏輯**：透過比對 ArUco 標籤的面積變化，來推算出車體的伸縮狀態。
2. **標籤圖檔產出工具**：用於生成供攝影機辨識的 ArUco 標記圖片。

---

## 2. 核心運算邏輯 (Core Logic)

在目前的辨識模型中，採用了 **`DICT_4X4_50`** 字典，並指定追蹤 **Target ID: 17** 的標籤。

系統每 `0.5` 秒 (`CHECK_INTERVAL`) 進行一次截面積差異計算 (`diff = current_area - last_area`)，藉此判定伸縮機制的動態狀態。防抖動與變更標準如下：
*   **收縮中**：當面積變異 `diff > 140` (`MOVE_THRESHOLD`)。
*   **外推中**：當面積變異 `diff < -140`。
*   **穩定**：當面積變異絕對值小於 `60` (`STABLE_THRESHOLD`) 時才切回穩定狀態，確保連續影像不會因輕微震動（鏡頭晃動、車體微震）而造成判定跳動。

---

## 3. 檔案說明與用途 (File Structure)

*   `ArUco_Taoyuan_RV_Camera3.py`
    *   **這是什麼：** 開發者手動檢測用的畫面預覽腳本。
    *   **怎麼用：** 執行後會連線至 RTSP 攝影機，彈出影片視窗繪製標籤外框，並於終端機即時印出 `🔔 [11:22:33] 收縮中` 等狀態。
    *   **執行指令：**
        ```bash
        uv run python libraries/ipcam_ArUco_detection/ArUco_Taoyuan_RV_Camera3.py
        ```
*   `ArUco_Image Production.py`
    *   **這是什麼：** 單純的產圖小工具。
    *   **怎麼用：** 會自動生成帶白色外框 (20px) 的 ArUco 圖片（如 `marker_17.png`），供使用者列印出來貼在車上。
    *   **執行指令：**
        ```bash
        uv run python "libraries/ipcam_ArUco_detection/ArUco_Image Production.py"
        ```
*   `ArUcoSpaceDetection.py` (**未來擴充**)
    *   **這是什麼：** 正式的 Robot Framework 函式庫入口，準備用來把上面那個測試腳本（`Camera3.py`）變成具有固定架構的物件（Class）。
    *   **為什麼需要這個：** 因為自動化測試不能彈出「無窮盡播放的影片視窗」。它需要的是一個能靜默在背景執行，當測試腳本詢問「現在是在收縮還是穩定？」時，它能立刻回傳結果的標準工具。

---

## 4. 環境配置 (Dependencies)
請確保專案虛擬環境中已安裝下列套件：
*   `opencv-contrib-python` (注意：必須是 contrib 版，純 opencv-python 沒有支援最新的 aruco)
*   `numpy`

---

## 5. 未來發展與自動化整合 (Future Scope)
未來若要將此功能完美整合到測試環節，預期需將連線資訊拉出放在 `.env` 或是 `config` 目錄下（不要把 `USERNAME` 與 `PASSWORD` 寫在程式內），並能支援如以下的 Robot 測試語法：

```robotframework
*** Test Cases ***
驗證休旅車側帳收縮機制
    [Documentation]    測試側帳與內部空間收縮之影像檢測機制
    Given 啟動攝影機辨識系統
    When 啟動收縮與外推機制
    Then 車內空間狀態應轉為 "收縮中"
    And 車內空間狀態最終應為 "穩定"
```
