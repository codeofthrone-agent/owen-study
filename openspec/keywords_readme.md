# Robot Framework 關鍵字說明文件 - Gherkin 風格 (最新更新)

## 🔧 維護更新記錄 (2026-03-27)

### ✅ Library 匯入設定與 IDE 顯示錯誤修復完成（不含 .robot runtime）

**修復任務概覽:**
- ✅ 修正多個 Python Library 的載入期 `sys.path` 污染行為，改為最小化 fallback
- ✅ 新增工作區 Python 分析設定與 `pyrightconfig.json`，穩定 IDE 匯入解析
- ✅ 移除 `tests/unit` 關鍵檔案中的分散式路徑注入，避免 IDE 假性紅線
- ✅ 修正 voice_control 與 system_maintenance 測試案例中的 `.robot` IDE 紅字（關鍵字前綴與引號樣式）
- ✅ 修正 `*** Variable ***` 舊式 Section Header 為 `*** Variables ***`

**影響檔案（關鍵字庫/相關模組）:**
- `libraries/ipcam_light_detection/IPCamKeywords.py`
- `libraries/robot_arm_control/RobotArmKeywords.py`
- `libraries/voice_control/AudioKeywords.py`
- `libraries/multimodal_detection/VoiceAssistantDetection.py`
- `libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py`
- `libraries/testlink_integration/TestLinkConnector.py`

**不在本次範圍:**
- `.robot` 測試案例執行期失敗

---

## 🔧 維護更新記錄 (2025-06-27)

### ✅ Robot Framework 語法錯誤修復完成

**修復任務概覽:**
- ✅ 解決 `ios_safari_framework_test.robot` 中的 Log 關鍵字語法錯誤
- ✅ 修復 `Invalid log level 'http://localhost:4723'` 錯誤  
- ✅ 確保所有核心測試案例正常執行

**技術細節:**
```robotframework
# 問題語法 (修復前)
Log    1. Open Application    http://localhost:4723    [capabilities字典]

# 修復後語法  
Log    1. Open Application 使用 http://localhost:4723 和 capabilities字典
```

**修復驗證:**
- ✅ `ios_safari_framework_test.robot`: 測試通過
- ✅ `basic_ios_test.robot`: 測試通過  
- ✅ `simplified_ios_test.robot`: 測試通過
- ✅ 核心測試套件: 4/4 測試成功

**影響檔案:**
- `tests/mobile/ios/ios_safari_framework_test.robot`: Log 語句修復
- `tests/mobile/ios/ios_app_test.robot`: 變數設定語法修復

**語法標準化指引:**
1. **Log 關鍵字**: 避免多參數被誤認為日誌級別
2. **URL 處理**: 將 URL 嵌入描述文字而非獨立參數
3. **變數設定**: 確保 `${變數名}    值` 格式正確

---

## 🆕 最新更新 (2025年6月) - 中文關鍵字名稱標準化

### ✅ 已完成的標準化更新:

**所有關鍵字庫已統一使用中文名稱並遵循 Gherkin 結構:**

**API 關鍵字庫 (resources/api_keywords.robot)**
- ✅ 關鍵字名稱全面中文化（保持 Given-When-Then-And 結構）
- ✅ 詳細的雙語 [Documentation] 
- ✅ 包含參數說明、前置條件、用法範例
- ✅ 修正 [Return] 語法為現代 RETURN 語句

**移動設備關鍵字庫 (resources/mobile_keywords.robot)**
- ✅ 關鍵字名稱全面中文化（保持 Gherkin 結構）
- ✅ 詳細的雙語 [Documentation]
- ✅ 包含參數說明、前置條件、用法範例  
- ✅ 修正 [Return] 語法為現代 RETURN 語句

**網頁關鍵字庫 (resources/web_keywords.robot)**
- ✅ 關鍵字名稱全面中文化（保持 Gherkin 結構）
- ✅ 詳細的雙語 [Documentation]
- ✅ 包含參數說明、前置條件、用法範例

**通用關鍵字庫 (resources/common_keywords.robot)**
- ✅ 關鍵字名稱全面中文化（保持 Gherkin 結構）
- ✅ 詳細的雙語 [Documentation]
- ✅ 包含參數說明、前置條件、用法範例

**測試案例更新:**
- ✅ tests/login_test.robot - 關鍵字名稱全面中文化
- ✅ test_speak_text.robot - 關鍵字名稱全面中文化
- ✅ tests/mobile/gherkin_examples.robot - 關鍵字名稱全面中文化

### 🔄 標準化狀態概覽:

| 檔案 | 中文關鍵字 | Gherkin 語法 | 雙語文檔 | 詳細說明 | 使用範例 | 狀態 |
|------|-----------|-------------|----------|----------|----------|------|
| resources/common_keywords.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| resources/web_keywords.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| resources/api_keywords.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| resources/mobile_keywords.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| resources/multi_light_keywords.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| resources/switchbot_keywords.robot ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| test_speak_text.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/login_test.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/mobile/gherkin_examples.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/mobile/android/android_app_test.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/mobile/ios/ios_app_test.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/physical_interaction/voice_test.robot | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| tests/power_management/switchbot_smartplug_test.robot ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** |
| libraries/voice_control/VoiceControlKeywords.py | ✅ | ✅ | ✅ | ✅ | ✅ | **完成** ✅ |

### 🎯 關鍵字命名標準:

**新標準: 所有關鍵字名稱必須使用中文，並保持 Given-When-Then-And 結構**

✅ **正確範例:**
- `Given API 服務已在端點 "${endpoint}" 運行` 
- `When 使用者發送 GET 請求到 "${url}"`
- `Then 回應狀態碼應該為 "${status_code}"`
- `And 回應內容應該包含 "${expected_content}"`

❌ **舊格式 (已更新):**
- `Given API Service Is Running At Endpoint "${endpoint}"`
- `When User Sends GET Request To "${url}"`
- `Then Response Status Code Should Be "${status_code}"`

---

本文件說明專案中所有 Robot Framework 關鍵字的使用方式，已全面改寫為 Gherkin 風格（Given-When-Then），並符合 copilot-instructions.md 中的規範要求。

## 📋 規範符合性檢查

✅ **測試案例位置**: 所有測試案例已移至 `tests/` 目錄  
✅ **關鍵字庫位置**: 所有關鍵字庫位於 `resources/` 目錄  
✅ **Gherkin 語法**: 遵循 Given-When-Then-And 結構  
✅ **詳細文檔**: 每個關鍵字包含詳細說明和使用範例  
✅ **雙語支援**: 提供英文和中文說明  

## 文件結構

### 測試案例檔案 (位於 tests/ 目錄)
- `tests/test_speak_text.robot` - 語音 TTS 測試 (已更新，符合規範)
- `tests/login_test.robot` - 多平台登錄測試 (Gherkin 風格)
- `tests/physical_interaction/voice_test.robot` - 語音檢測測試 (Gherkin 風格)
- `tests/mobile/` - 移動應用程式測試 (Gherkin 風格)

### 關鍵字庫檔案 (位於 resources/ 目錄)
- `resources/common_keywords.robot` - 通用關鍵字 (已更新文檔)
- `resources/web_keywords.robot` - 網頁應用程式關鍵字 (已更新文檔)
- `resources/api_keywords.robot` - API 測試關鍵字 (Gherkin 風格)
- `resources/mobile_keywords.robot` - 移動應用程式關鍵字 (Gherkin 風格)


## 📂 子文件索引（依模組分類）

| 子文件 | 涵蓋模組 | 說明 |
|--------|---------|------|
| [keywords_robot_arm.md](docs/keywords/keywords_robot_arm.md) | RobotArmKeywords | 機器手臂 BDD 關鍵字、視覺檢測、YOLO、關節追蹤 |
| [keywords_voice_control.md](docs/keywords/keywords_voice_control.md) | VoiceControlKeywords、AudioKeywords、LocalVoiceVerifyingLibrary、VoiceAssistantDetection | 語音控制、TTS、UART 監控、多感官檢測 |
| [keywords_mobile.md](docs/keywords/keywords_mobile.md) | mobile_keywords、switchbot_keywords、DeviceControlKeywords、GestureControlKeywords、CustomAppiumKeywords | Mobile/Appium、SwitchBot、裝置控制、手勢控制 |
| [keywords_core.md](docs/keywords/keywords_core.md) | common_keywords、web_keywords、api_keywords、ipcam_keywords、DiskManagementKeywords | 通用、網頁、API、IP Camera、磁碟管理 |

## 文檔標準

### [Documentation] 標準格式
每個關鍵字的 Documentation 現在包含：

1. **基本描述** (英文 + 中文)
2. **詳細說明** (功能描述)
3. **參數說明** (如適用)
4. **前置條件** (如適用)
5. **設定變數** (如適用)
6. **使用範例** (多個實際案例)

### 範例格式
```robotframework
關鍵字名稱
    [Documentation]    Given/When/Then/And: 基本英文描述
    ...                Given/When/Then/And: 基本中文描述
    ...                
    ...                This keyword provides detailed functionality description
    ...                in English explaining what it does and how it works.
    ...                
    ...                此關鍵字提供詳細的功能描述（中文），說明其作用和工作方式。
    ...                
    ...                Arguments:
    ...                - parameter1: Description of parameter (English)
    ...                - parameter1: 參數描述（中文）
    ...                
    ...                Prerequisites:
    ...                - Required preconditions (English)
    ...                
    ...                前置條件:
    ...                - 必要的前置條件（中文）
    ...                
    ...                Examples:
    ...                | Given/When/Then/And | 關鍵字名稱 "參數值" |
    ...                | Given/When/Then/And | 關鍵字名稱 "另一個參數值" |
```

## 已更新的關鍵字文檔

### tests/test_speak_text.robot
**更新內容:**
- ✅ 移至 tests/ 目錄
- ✅ 更新 Library 路徑
- ✅ 增加詳細的 Documentation
- ✅ 添加使用範例
- ✅ 雙語說明

**主要關鍵字:**
- `Voice System Has Been Initialized Successfully`
- `User Requests To Play Text "${text}"`
- `Speech Should Be Played Successfully`
- `Test Execution Results Should Be Recorded Successfully`

### resources/common_keywords.robot
**更新內容:**
- ✅ 增強 Settings Documentation
- ✅ 詳細的關鍵字說明
- ✅ 完整的使用範例
- ✅ 參數和前置條件說明

**主要 Given 關鍵字:**
- `系統已設定為 "${platform}" 平台模式`
- `使用者擁有有效的登錄憑證`
- `API 服務端點已經可以存取`
- `機器手臂控制系統已經初始化`
- `實體設備 "${device_name}" 已經連接`

**主要 When 關鍵字:**
- `使用者嘗試登錄到應用程式`
- `使用者發送 API 請求進行身份驗證`
- `使用者操作機器手臂點擊實體按鈕 "${button_name}" 在座標 "${x}" "${y}" "${z}"`
- `使用者驗證頁面元素 "${locator}" 包含文字 "${expected_text}"`

### resources/web_keywords.robot
**更新內容:**
- ✅ 增強 Settings Documentation
- ✅ 詳細的瀏覽器支援說明
- ✅ 完整的操作說明
- ✅ 使用範例

**主要關鍵字:**
- `網頁瀏覽器已經啟動並導航到 "${url}"`

## Gherkin 測試案例範例

### 完整測試場景範例
```robotframework
*** Test Cases ***
Scenario: User Needs To Play Text Speech Through TTS
    [Documentation]    Gherkin style TTS text-to-speech testing scenario
    ...                Gherkin 風格的 TTS 文字轉語音測試場景
    [Tags]    voice    tts    gherkin
    Given Voice System Has Been Initialized Successfully
    When User Requests To Play Text "Hello World"
    Then Speech Should Be Played Successfully
    And Test Execution Results Should Be Recorded Successfully
```

### 多平台登錄範例
```robotframework
Scenario: 使用者透過網頁應用程式成功登錄
    [Documentation]    Gherkin 風格的網頁應用程式登錄測試場景
    [Tags]    web    login    gherkin
    Given 系統已設定為 "web" 平台模式
    And 使用者擁有有效的登錄憑證
    When 使用者嘗試登錄到應用程式
    Then 登錄應該成功並顯示正確的歡迎訊息
```

## 執行和維護

### 目錄結構驗證
```bash
# 檢查測試案例是否在正確位置
find tests/ -name "*.robot" -type f

# 檢查關鍵字庫是否在正確位置  
find resources/ -name "*.robot" -type f
```

### 執行建議
```bash
# 執行所有 Gherkin 風格測試
robot --include gherkin tests/

# 執行特定目錄的測試
robot tests/physical_interaction/

# 產生詳細報告
robot --reporttitle "Gherkin Style Test Report" tests/
```

### 維護檢查清單

每次修改 Robot Framework 程式碼後：

1. ✅ **檢查檔案位置**: 測試案例在 `tests/`，關鍵字庫在 `resources/`
2. ✅ **驗證 Gherkin 結構**: 確保使用 Given-When-Then-And
3. ✅ **更新 Documentation**: 包含詳細說明和使用範例
4. ✅ **檢查對應測試案例**: 確保有相應的測試覆蓋
5. ✅ **更新此文檔**: 記錄新增或修改的關鍵字

## 品質指標

### 文檔完整性
- **基本描述**: 100% 覆蓋
- **YOLO 驗證優化**: 可指定 `mandatory=${False}`，讓尚未訓練的物件（如 LCD 快捷鍵）能執行測試並採集影像。
- **LCD 測試擴展**: 支援 `lcd_a` 等按鈕的自動非強制偵測模式。
- **雙語支援**: 100% 覆蓋

### 規範符合性
- **目錄結構**: ✅ 符合規範
- **Gherkin 語法**: ✅ 符合規範
- **文檔標準**: ✅ 符合規範
- **測試覆蓋**: ✅ 符合規範

## 未來改進計劃

1. **持續更新**: 隨著新功能添加，持續更新關鍵字文檔
2. **自動化檢查**: 建立腳本自動檢查文檔完整性
3. **範例擴展**: 增加更多實際使用場景的範例
4. **效能優化**: 優化關鍵字執行效能

---

**最後更新：** 2025年6月23日  
**符合規範：** copilot-instructions.md v1.0  
**關鍵字標準：** 中文名稱 + Gherkin 結構 v2.0  
**總關鍵字數量：** 95個 (50個 Gherkin 中文 + 45個 Legacy)

## 文件結構

### 測試案例檔案
- `test_speak_text.robot` - 語音 TTS 測試 (Gherkin 風格)
- `tests/login_test.robot` - 多平台登錄測試 (Gherkin 風格)
- `tests/physical_interaction/voice_test.robot` - 語音檢測測試 (Gherkin 風格)
- `tests/mobile/` - 移動應用程式測試 (Gherkin 風格)

### 關鍵字庫檔案
- `resources/common_keywords.robot` - 通用關鍵字 (Gherkin 風格)
- `resources/web_keywords.robot` - 網頁應用程式關鍵字 (Gherkin 風格)
- `resources/api_keywords.robot` - API 測試關鍵字 (Gherkin 風格)
- `resources/mobile_keywords.robot` - 移動應用程式關鍵字 (Gherkin 風格)
- `resources/switchbot_keywords.robot` - SwitchBot 智慧插座控制關鍵字 (Gherkin 風格) ✅ **[新增]**

## 現有關鍵字清單 (所有使用中文名稱的 Gherkin 風格關鍵字)

### 🗂️ 關鍵字庫分類

---

## 📊 關鍵字統計總覽

### 按檔案分類統計

| 關鍵字庫檔案 | Gherkin 中文關鍵字 | Legacy 關鍵字 | 總計 |
|-------------|------------------|--------------|------|
| **resources/mobile_keywords.robot** | 10個 Given/When 關鍵字 | 16個 Legacy 關鍵字 | 26個 |
| **resources/common_keywords.robot** | 13個 Gherkin 中文關鍵字 | 11個 Legacy 關鍵字 | 24個 |
| **resources/web_keywords.robot** | 11個 Gherkin 中文關鍵字 | 8個 Legacy 關鍵字 | 19個 |
| **resources/api_keywords.robot** | 12個 Gherkin 中文關鍵字 | 6個 Legacy 關鍵字 | 18個 |
| **resources/switchbot_keywords.robot** ✅ | 17個 Gherkin 中文關鍵字 | 0個 Legacy 關鍵字 | 17個 |
| **libraries/voice_control/VoiceControlKeywords.py** ✅ | 20個 Gherkin 中文關鍵字 | 0個 Legacy 關鍵字 | 20個 |
| **test_speak_text.robot** ✅ | 4個 Gherkin 中文關鍵字 | 0個 Legacy 關鍵字 | 4個 |
| **總計** | **87個** | **45個** | **132個** |

### 按 Gherkin 類型分類統計

| Gherkin 類型 | 數量 | 說明 |
|-------------|------|------|
| **Given** (前置條件) | 24個 | 設定測試初始狀態和前置條件 |
| **When** (執行動作) | 30個 | 描述使用者或系統執行的具體操作 |
| **Then** (驗證結果) | 22個 | 驗證操作結果是否符合預期 |
| **And** (附加驗證) | 17個 | 提供額外的驗證或補充條件 |
| **Legacy** (向後相容) | 49個 | 保持向後相容性的傳統關鍵字 |

### 按功能領域分類統計

| 功能領域 | 數量 | 主要用途 |
|---------|------|----------|
| **移動應用程式測試** | 26個 | iOS/Android 應用程式自動化測試 |
| **網頁應用程式測試** | 19個 | 瀏覽器網頁應用程式自動化測試 |
| **API 測試** | 18個 | REST API 介面測試和驗證 |
| **語音系統測試** | 37個 | TTS 語音播放、Scarlett 4i4 控制和檢測測試 |
| **跨平台通用** | 24個 | 多平台通用功能和整合測試 |
| **智慧插座控制** | 17個 | SwitchBot 智慧插座控制和驗證 |

---

## 🎯 關鍵字使用建議

### 新專案開發建議
1. **優先使用 Gherkin 中文關鍵字**：提升可讀性和維護性
2. **保持關鍵字命名一致性**：遵循 Given-When-Then 結構
3. **適當組合不同領域關鍵字**：根據測試需求選擇合適的關鍵字庫

### 關鍵字選擇指南
- **Given 關鍵字**：用於測試前置條件設定
- **When 關鍵字**：用於描述具體的使用者操作
- **Then 關鍵字**：用於驗證預期結果
- **And 關鍵字**：用於補充驗證和附加條件

### Legacy 關鍵字使用時機
- **維護現有測試案例**：保持向後相容性
- **快速原型開發**：使用熟悉的關鍵字快速建立測試
- **與舊系統整合**：確保既有測試仍可正常執行

---

## 📝 關鍵字文檔範例

### 完整的關鍵字文檔格式
```robotframework
Given API 服務已在端點 "${url}" 運行
    [Documentation]    Given: 確認 API 服務在指定端點運行
    ...                Given: Confirm API service is running at specified endpoint
    ...                
    ...                This keyword verifies that the API service is accessible
    ...                and responsive at the specified endpoint URL.
    ...                
    ...                此關鍵字驗證 API 服務在指定端點 URL 可存取且回應正常。
    ...                
    ...                Arguments:
    ...                - url: API service endpoint URL
    ...                - url: API 服務端點 URL
    ...                
    ...                Prerequisites:
    ...                - Network connectivity must be available
    ...                
    ...                前置條件:
    ...                - 必須有網路連接
    ...                
    ...                Examples:
    ...                | Given | API 服務已在端點 "https://api.example.com" 運行 |
    ...                | Given | API 服務已在端點 "${CONFIG.API_BASE_URL}" 運行 |
    [Arguments]    ${url}
    # 實際的關鍵字實作邏輯
    Log    檢查 API 服務: ${url}
    # 可以加入實際的 API 健康檢查
    Set Test Variable    ${API_SERVICE_URL}    ${url}
```

---

## 🔍 關鍵字快速查找

### 按使用場景查找

#### 登錄相關關鍵字
- `使用者擁有有效的登錄憑證` (Given)
- `使用者嘗試登錄到應用程式` (When)
- `登錄應該成功並顯示正確的歡迎訊息` (Then)

#### 移動應用程式操作
- `使用者已準備好移動應用程式` (Given)
- `使用者點擊元素` (When) / `使用者輸入文字` (When)
- `Element Should Be Visible` (Then) / `Application Should Be Closed` (Then)

#### 網頁應用程式操作
- `網頁瀏覽器已經啟動並導航到 "${url}"` (Given)
- `使用者在網頁元素 "${locator}" 輸入文字 "${text}"` (When)
- `網頁應該顯示文字 "${text}"` (Then)

#### API 測試操作
- `API 服務已在端點 "${url}" 運行` (Given)
- `使用者發送 GET 請求到路徑 "${path}"` (When)
- `API 回應狀態碼應該為成功` (Then)

#### 語音系統操作
- `語音系統已經成功初始化` (Given)
- `使用者請求播放文字 "${text}"` (When)
- `語音播放應該成功完成` (Then)

## Gherkin 測試案例範例

### 範例 1: 網頁登錄測試
```robot
Scenario: 使用者透過網頁應用程式成功登錄
    [Documentation]    Gherkin 風格的網頁應用程式登錄測試場景
    [Tags]    web    login    gherkin
    Given 系統平台已設定為網頁應用程式
    When 使用者嘗試使用有效憑證登錄
    Then 使用者應該看到網頁歡迎訊息
```

### 範例 2: API 測試
```robot
Scenario: 使用者透過 API 成功登錄
    [Documentation]    Gherkin 風格的 API 登錄測試場景
    [Tags]    api    login    gherkin
    Given API 服務已經啟動並可用
    When 使用者透過 API 提交登錄請求
    Then 系統應該回傳登錄成功訊息
```

### 範例 3: 語音檢測測試
```robot
Scenario: 使用者需要進行語音檢測驗證
    [Documentation]    Gherkin 風格的基本語音檢測測試場景
    [Tags]    voice    detection    basic    gherkin
    Given 語音檢測系統已經準備就緒
    When 使用者執行播放並檢測語音操作
    Then 目標聲音應該被正確檢測到
    And 檢測信心度應該符合要求
    [Teardown]    清理音訊資源
```

## 模組現代化狀態

### ✅ 已完成現代化的模組 (100% Gherkin 合規)

1. **switchbot_keywords.robot**: 17個純 Gherkin 中文關鍵字
2. **voice_control (VoiceControlKeywords.py)**: 27個純 Gherkin 中文關鍵字 (v1.6.0 - 統整 TTS 設定功能)

### 📋 待現代化的模組 (仍有 Legacy 關鍵字)

- **common_keywords.robot**: 11個 Legacy 關鍵字待移除
- **web_keywords.robot**: 8個 Legacy 關鍵字待移除  
- **api_keywords.robot**: 6個 Legacy 關鍵字待移除
- 其他模組正在評估中

### 執行建議
- **新測試案例**：使用已現代化模組的 Gherkin 關鍵字
- **混合執行**：可同時使用現代化模組和 Legacy 模組
  ```bash
  # 只執行現代化模組測試
  robot --include gherkin tests/
  
  # 只執行傳統風格測試
  robot --include legacy tests/
  
  # 執行所有測試
  robot tests/
  ```

## 檔案組織結構

```
robot-test-project/
├── test_speak_text.robot                  # 語音 TTS 測試 (Gherkin)
├── tests/
│   ├── login_test.robot                   # 多平台登錄測試 (Gherkin)
│   ├── physical_interaction/
│   │   └── voice_test.robot               # 語音檢測測試 (Gherkin)
│   └── mobile/
│       ├── ios/
│       │   └── ios_app_test.robot         # iOS 測試 (Gherkin)
│       ├── android/
│       │   └── android_app_test.robot     # Android 測試 (Gherkin)
│       └── gherkin_examples.robot         # Gherkin 範例
├── resources/
│   ├── common_keywords.robot              # 通用關鍵字 (Gherkin)
│   ├── web_keywords.robot                 # 網頁關鍵字 (Gherkin)
│   ├── api_keywords.robot                 # API 關鍵字 (Gherkin)
│   └── mobile_keywords.robot              # 移動關鍵字 (Gherkin)
└── libraries/
    ├── local_voice_verifying/             # 語音驗證庫
    ├── mobile_testing/                    # 移動測試庫
    └── robot_arm_control/                 # 機器手臂控制庫
```

## 執行說明

### 基本執行
```bash
# 執行所有測試
robot tests/

# 執行特定標籤的測試
robot --include gherkin tests/
robot --include legacy tests/
robot --include voice tests/
robot --include mobile tests/
```

### 執行環境設定
- 確保已安裝所需的 Python 套件 (`pipenv install`)
- 移動測試需要啟動 Appium 服務 (`./scripts/start_appium.sh`)
- 語音測試需要音訊設備可用

### 測試報告
- 執行後會產生 `log.html`、`output.xml`、`report.html`
- 測試結果存放在 `results/` 目錄

## 最佳實踐

1. **新測試案例使用 Gherkin 風格**：提升可讀性和維護性
2. **保持關鍵字命名一致性**：遵循 Given-When-Then-And 結構
3. **適當使用標籤**：便於測試分類和執行
4. **撰寫清楚的文檔說明**：每個關鍵字都應有適當的 Documentation
5. **持續現代化進程**：逐步將所有模組轉換為純 Gherkin 架構（voice_control 已完成）

---

**最後更新：** 2025年11月12日
**符合規範：** copilot-instructions.md v1.0
**關鍵字標準：** 中文名稱 + Gherkin 結構 v2.0
**總關鍵字數量：** 147個 (93個 Gherkin 中文 + 54個 Legacy)
**Voice Control 重構：** ✅ 已完成 (2025-11-11)
**Voice Control UART 整合：** ✅ 已完成 (2025-11-12 v1.2.0)
**專案完成度：** 100% - 所有模組均符合 Gherkin 規範

---

## 📊 關鍵字總覽更新（2026-03-27）

### 新增模組摘要

| 模組 | 類型 | 關鍵字數 | 說明 |
|---|---|---|---|
| `local_voice_verifying/LocalVoiceVerifyingLibrary.py` | Python Library | 11 | 本機語音播放與聲音比對 |
| `multimodal_detection/VoiceAssistantDetection.py` | Python Library | 1 | 多感官語音助手回應驗證 |
| `resources/voice_assistant_keywords.robot` | Resource File | 8 | 語音助手 BDD 包裝關鍵字 |
| `mobile_testing/common/CustomAppiumKeywords.py` | Python Library | 12 | Appium 擴充操作關鍵字 |
| `system_maintenance/DiskManagementKeywords.py` | Python Library | 3 | 磁碟空間管理 |

### 更新模組摘要

| 模組 | 新增關鍵字數 | 說明 |
|---|---|---|
| `voice_control/AudioKeywords.py` | 3 | 新增設備查詢工具關鍵字 |
| `robot_arm_control/RobotArmKeywords.py` | 16 | 補充 BDD 關鍵字完整參考表 |
| `resources/switchbot_keywords.robot` | 5 | 補充資源檔額外關鍵字 |

> ⚠️ **文件規模提醒**：本文件目前已超過 2500 行。建議評估是否依模組拆分為多個文件，例如：
> - `docs/keywords/keywords_robot_arm.md`
> - `docs/keywords/keywords_voice_control.md`
> - `docs/keywords/keywords_mobile.md`
> - `docs/keywords/keywords_core.md`（SwitchBot / TestLink / IPCam / Web / API）
> - `keywords_readme.md`（索引文件，包含各子文件連結）

