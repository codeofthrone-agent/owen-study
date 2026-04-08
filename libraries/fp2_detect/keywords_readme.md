# Aqara FP2 空間狀態檢測 關鍵字說明文件 - Gherkin 風格

本文件詳細列出了使用 `fp2_homekit` (將 Aqara FP2 引入 HomeKit Local API) 進行空間狀態判定的 Robot Framework 關鍵字，全面符合專案的 Gherkin (Given-When-Then-And) 與雙語雙模規範。

---

## 載入函式庫

在 `.robot` 檔案中，請在 `*** Settings ***` 區段載入此模組：

```robotframework
*** Settings ***
Library    libraries.fp2_detect.FP2Keywords
```

---

## 📝 關鍵字文檔

```robotframework
Given FP2 空間雷達已連線 "${environment}" "${sensor_id}" "${mode}"
    [Documentation]    Given: 確認 FP2 空間感測器已就緒並完成配置
    ...                Given: Confirm the FP2 spatial sensor is ready and configured
    ...                
    ...                此關鍵字用於從 ipcam_config 載入指定的 fp2_sensor 設定，
    ...                並宣告接下來的 FP2 操作將使用何種判定模式 (如 'awning' 或 'slide')。
    ...                
    ...                Arguments:
    ...                - environment: 測試環境 (例如 'rv_car')
    ...                - sensor_id: 感測器的 ID (例如 'awning_fp2')
    ...                - mode: 判定模式 ('awning' 針對雨遮，'slide' 針對側推艙)
    ...                
    ...                Prerequisites:
    ...                - 必須在 yaml 中定義好該感測器，並在本地具有對應名稱 (alias) 的配對資料。
    ...                
    ...                Examples:
    ...                | Given | FP2 空間雷達已連線 "rv_car" "awning_fp2" "awning" |

When 取得 FP2 當前空間佔用狀態
    [Documentation]    When: 取得 FP2 當前空間佔用狀態
    ...                When: Get current space occupancy state from FP2
    ...                
    ...                此關鍵字會發出非同步單次查詢給 FP2 設備，取得各個偵測區域的即時資料，並根據當前模式判斷總體狀態。
    ...                
    ...                Arguments:
    ...                - 無
    ...                
    ...                Prerequisites:
    ...                - 必須先透過 'Given FP2 空間雷達已連線' 完成模式定義。
    ...                
    ...                Returns:
    ...                - string: 狀態字串 (如 'open', 'close')
    ...                
    ...                Examples:
    ...                | ${state}= | When | 取得 FP2 當前空間佔用狀態 |

Then FP2 空間狀態應該為 "${expected_state}"
    [Documentation]    Then: 驗證 FP2 空間狀態應符合預期狀態
    ...                Then: Verify the FP2 space state matches the expected state
    ...                
    ...                發出一次即時查詢，並與傳入的期望狀態比對。若不吻合，將拋出 AssertionError 以中斷測試。
    ...                
    ...                Arguments:
    ...                - expected_state: 預期的狀態字串 (例如: 'open' 代表展開/淨空, 'close' 代表收起/被佔用)
    ...                
    ...                Examples:
    ...                | Then | FP2 空間狀態應該為 "open" |

And 斷開 FP2 連線
    [Documentation]    And: 安全釋放 FP2 狀態與資源
    ...                And: Safely release FP2 states and resources
    ...                
    ...                此關鍵字重置系統內的 FP2 相依模式與變數。
    ...                
    ...                Examples:
    ...                | And | 斷開 FP2 連線 |
```

---

## 💡 Gherkin 測試案例範例

```robotframework
*** Test Cases ***
Scenario: 測試自動雨遮偵測系統狀態
    [Documentation]    使用 FP2 HomeKit 查詢雨遮是否已展開
    [Tags]    fp2    homekit    gherkin
    Given FP2 空間雷達已連線 "rv_car" "awning_fp2" "awning"
    
    # 觀察狀態 (若操作多機台可指定 sensor_id，預設將使用第一個連線的感測器)
    ${state}=    When 取得 FP2 當前空間佔用狀態
    Log    目前雨遮狀態: ${state}
    
    # 直接斷言 (預期預設是處於 close 狀態)
    Then FP2 空間狀態應該為 "close"
    
    [Teardown]    And 斷開 FP2 連線
```
