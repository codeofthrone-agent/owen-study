# IPCam ArUco Detection 關鍵字說明文件 - Gherkin 風格

本文件詳細列出了使用 IP Camera 結合 ArUco 影像辨識進行空間狀態判定所提供的 Robot Framework 關鍵字，已全面改寫為 Gherkin 風格（Given-When-Then-And）並符合專案雙語規範與多實體架構。

---

## 載入函式庫

在 `.robot` 檔案中，請在 `*** Settings ***` 區段載入此模組：

```robotframework
*** Settings ***
Library    libraries.ipcam_ArUco_detection.ArUcoKeywords
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
    ...                ArUco 防抖動門檻參數。支援同時擁有多機連線。
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
    ...                | Given | 專屬攝影機已連線 "rv_car" "camera3" |

When 取得當前車內空間狀態
    [Documentation]    When: 擷取並辨識目前空間的擴充/收合狀態
    ...                When: Get current space state based on ArUco marker
    ...                
    ...                This keyword captures the current ArUco tag size and returns
    ...                the space state via a moving average and confidence scoring algorithm.
    ...                
    ...                此關鍵字透過滑動平均與連續信心打分演算法，分析畫面中
    ...                ArUco 標籤大小變化並回傳車內當前的空間狀態判斷。
    ...                
    ...                Returns:
    ...                - string: Status corresponding to "open", "close", "moving", or "unknown".
    ...                - 字串: 回傳狀態如 "open", "close", "moving" 等。
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
    ...                並記錄這段時間內發生過的所有狀態變化（依時間順序）。
    ...                
    ...                Arguments:
    ...                - duration_sec: Number of seconds to observe.
    ...                - duration_sec: 要持續觀察的秒數。
    ...                
    ...                Returns:
    ...                - list: Sequence of states recorded (e.g. ['close', 'moving']).
    ...                - 列表: 紀錄的狀態序列（例如 ['close', 'moving']）。
    ...                
    ...                Prerequisites:
    ...                - Camera must be connected.
    ...                
    ...                前置條件:
    ...                - 必須先建立攝影機連線。
    ...                
    ...                Examples:
    ...                | ${history}= | When | 觀察並記錄空間動態 "5" 秒 |

Then 車內空間狀態應該為 "${expected_state}"
    [Documentation]    Then: 驗證車內空間狀態應符合預期狀態
    ...                Then: Verify the current space state matches the expected state
    ...                
    ...                此關鍵字會立刻取得車內空間狀態，並與預期字串做比對。如果不吻合，將拋出 AssertionError 中止測試。
    ...                This keyword asserts the current space status matches the passed-in expected state. Fails the test specifically if they diverge.
    ...                
    ...                Arguments:
    ...                - expected_state: 預期的狀態字串 (如: 'open', 'close', 'moving')
    ...                
    ...                Examples:
    ...                | Then | 車內空間狀態應該為 "open" |

Then 動態觀察狀態應包含 "${expected_state}"
    [Documentation]    Then: 驗證觀察紀錄中應包含指定狀態
    ...                Then: Verify the monitoring history includes the expected state
    ...                
    ...                此關鍵字會檢查前一步驟 (When 觀察並記錄空間動態) 所回傳的歷史紀錄，驗證是否包含期望的狀態。
    ...                This keyword verifies if the previously retrieved history of states includes the expected specific state.
    ...                
    ...                Arguments:
    ...                - expected_state: 預期的狀態字串
    ...                - history: 來自當前上下文的前一步觀察結果
    ...                
    ...                Examples:
    ...                | ${history}= | When 觀察並記錄空間動態 "5" 秒 |
    ...                | Then | 動態觀察狀態應包含 "moving" | ${history} |

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
Scenario: 測試 RV 車庫縮放監測與驗證
    [Documentation]    Gherkin 風格的車庫空間監測、動態紀錄與狀態驗證
    [Tags]    ipcam    aruco    gherkin
    Given 專屬攝影機已連線 "rv_car" "camera3"
    
    # 狀態直接提取與驗證
    When 取得當前車內空間狀態
    Then 車內空間狀態應該為 "close"
    
    # 時段觀察與紀錄驗證
    ${history}=    When 觀察並記錄空間動態 "10" 秒
    Then 動態觀察狀態應包含 "moving"    ${history}
    
    [Teardown]    And 斷開攝影機連線
```
