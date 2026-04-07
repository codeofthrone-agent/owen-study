# IPCam ArUco Detection 關鍵字說明文件 - Gherkin 風格

本文件詳細列出了使用 IP Camera 結合 ArUco 影像辨識進行空間狀態判定所提供的 Robot Framework 關鍵字，已全面改寫為 Gherkin 風格（Given-When-Then-And）並符合專案雙語規範。

---

## 載入函式庫

在 `.robot` 檔案中，請在 `*** Settings ***` 區段載入此模組：

```robotframework
*** Settings ***
Library    libraries.ipcam_ArUco_detection.ArUcoSpaceDetection
```

---

## 📝 關鍵字文檔

```robotframework
Given 專屬攝影機已連線 "${environment}" "${camera_name}"
    [Documentation]    Given: 建立 IP Camera 影像串流與 ArUco 設定連線
    ...                Given: Establish IP Camera streaming and ArUco setting connection
    ...                
    ...                This keyword connects to the specified IP camera and loads
    ...                its custom ArUco detection anti-jitter parameters from YAML.
    ...                
    ...                此關鍵字將連接至指定的 IP 攝影機，並從 YAML 載入專屬的 
    ...                ArUco 防抖動門檻參數。
    ...                
    ...                Arguments:
    ...                - environment: Deployment environment (e.g., 'rv_car')
    ...                - environment: 部署環境名稱（預設為 'rv_car'）
    ...                - camera_name: Camera name/id (e.g., 'rv_motor')
    ...                - camera_name: 攝影機代號（例如 'rv_motor' 或 'cam3'）
    ...                
    ...                Prerequisites:
    ...                - config/ipcam_config.yaml must have the target camera defined.
    ...                
    ...                前置條件:
    ...                - 必須在 config/ipcam_config.yaml 中定義好該台攝影機。
    ...                
    ...                Examples:
    ...                | Given | 專屬攝影機已連線 "rv_car" "rv_motor" |

When 取得當前車內空間狀態
    [Documentation]    When: 擷取並辨識目前空間的伸縮狀態
    ...                When: Capture and detect the current space telescopic state
    ...                
    ...                This keyword captures the current ArUco tag size and returns
    ...                the space state via a moving average and confidence scoring algorithm.
    ...                
    ...                此關鍵字透過滑動平均與連續信心打分演算法，分析畫面中
    ...                ArUco 標籤大小變化並回傳車內當前的空間狀態判斷。
    ...                
    ...                Returns:
    ...                - string: Status corresponding to "穩定", "收縮中", or "外推中".
    ...                - 字串: 回傳 "穩定", "收縮中", 或 "外推中"。
    ...                
    ...                Prerequisites:
    ...                - Camera must be connected via `Given 專屬攝影機已連線`
    ...                
    ...                前置條件:
    ...                - 必須先透過 `Given 專屬攝影機已連線` 建立連線。
    ...                
    ...                Examples:
    ...                | When | 取得當前車內空間狀態 |

When 觀察並記錄空間動態 "${duration_sec}" 秒
    [Documentation]    When: 持續監控畫面動態狀態轉換
    ...                When: Continuously monitor screen dynamic state transitions
    ...                
    ...                This keyword monitors the space state over a designated number 
    ...                of seconds, recording all state changes (deduplicated).
    ...                
    ...                此關鍵字在指定的時長內，持續監控畫面的動態狀態轉換，
    ...                並記錄這段時間內發生過的所有狀態變化（去除重複狀態）。
    ...                
    ...                Arguments:
    ...                - duration_sec: Number of seconds to observe.
    ...                - duration_sec: 要持續觀察的秒數。
    ...                
    ...                Returns:
    ...                - list: Sequence of states recorded (e.g. ['穩定', '收縮中']).
    ...                - 列表: 紀錄的狀態序列（例如 ['穩定', '收縮中']）。
    ...                
    ...                Prerequisites:
    ...                - Camera must be connected.
    ...                
    ...                前置條件:
    ...                - 必須先建立攝影機連線。
    ...                
    ...                Examples:
    ...                | When | 觀察並記錄空間動態 "30" 秒 |

And 斷開攝影機連線
    [Documentation]    And: 安全釋放資源，切斷即時 RTSP 影像連線
    ...                And: Safely release resources and cut RTSP connection
    ...                
    ...                This keyword safely releases all OpenCV streaming resources.
    ...                Recommended to be used in Teardown.
    ...                
    ...                此關鍵字安全釋放資源，切斷與攝影機的即時 RTSP 影像連線。
    ...                建議在 Teardown 區段統一呼叫。
    ...                
    ...                Examples:
    ...                | And | 斷開攝影機連線 |
```

---

## 💡 Gherkin 測試案例範例

```robotframework
*** Test Cases ***
Scenario: 測試 RV 車庫縮放監測
    [Documentation]    Gherkin 風格的車庫空間監測與動態紀錄
    [Tags]    ipcam    aruco    gherkin
    Given 專屬攝影機已連線 "rv_car" "rv_motor"
    When 取得當前車內空間狀態
    And 觀察並記錄空間動態 "10" 秒
    [Teardown]    斷開攝影機連線
```
