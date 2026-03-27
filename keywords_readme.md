# Robot Framework 關鍵字說明文件 - Gherkin 風格 (最新更新)

## 🚀 新增功能 (2026-02-09) - 任意移動與拍攝輔助關鍵字

為了解決定義新觀測點的需求，新增了兩個輔助關鍵字，允許直接控制機器手臂移動到指定角度並拍攝影像。

### ✅ 新增關鍵字 (RobotArmKeywords.py)

| 關鍵字 | 參數 | 說明 |
| :--- | :--- | :--- |
| `移動機器手臂到指定角度` | `angles` (list), `speed` (int=30) | 移動機器手臂到指定角度 (6個關節角度列表) |
| `拍攝並儲存影像` | `filename_tag` (str="capture") | 拍攝當前影像並儲存到 `output/debug_images/`，檔名包含時間戳記。 |

**使用範例:**
```robotframework
*** Variables ***
@{TARGET_ANGLES}    43.9    18.7    -92.5    -19.2    -4.7    -5.1

*** Test Cases ***
Move And Capture
    Given 連接機器手臂
    When 移動機器手臂到指定角度    ${TARGET_ANGLES}
    Then 拍攝並儲存影像    filename_tag=observation_pos_2
```

## 🚀 重大更新 (2026-02-02) - v2.0.0 SwitchBot 模組重構

### ✅ SwitchBot 智慧插座控制 - 改用官方 HTTP API

**更新概覽:**
- ✅ 移除第三方 SDK 依賴（pyswitchbot）
- ✅ 改用 SwitchBot 官方 HTTP API v1.1
- ✅ 實作官方 HMAC-SHA256 簽名算法
- ✅ 使用 UUID v4 作為 nonce（官方建議）
- ✅ 環境變數讀取改進（動態路徑偵測 .env）

**為什麼移除 pyswitchbot？**
- `pyswitchbot` 是**藍牙控制**套件，不是 HTTP API SDK
- SwitchBot 官方建議直接使用 HTTP API
- 減少第三方依賴，提高穩定性

**主要關鍵字（SwitchBotSmartPlugLibrary.py）:**

| 關鍵字 | 說明 |
|--------|------|
| `設定SwitchBot認證資訊` | 設定 API Token 和 Secret |
| `取得所有SwitchBot設備清單` | 取得帳號下所有設備 |
| `查詢設備資訊` | 查詢特定設備資訊 |
| `當開啟智慧插座` | 開啟指定智慧插座 |
| `當關閉智慧插座` | 關閉指定智慧插座 |
| `取得智慧插座狀態` | 查詢插座狀態 (on/off) |
| `那麼智慧插座狀態應該是開啟` | 驗證插座為開啟狀態 |
| `那麼智慧插座狀態應該是關閉` | 驗證插座為關閉狀態 |
| `等待設備狀態變更` | 等待狀態變更 |
| `執行設備電源重啟` | 電源重啟循環 |

**Gherkin 風格關鍵字（switchbot_keywords.robot）:**

| 類型 | 關鍵字 | 說明 |
|------|--------|------|
| Given | `已設定SwitchBot API認證資訊` | 前置條件：設定認證 |
| Given | `已知智慧插座設備ID` | 前置條件：確認設備 ID |
| Given | `智慧插座系統已準備就緒` | 前置條件：系統檢查 |
| When | `使用者開啟智慧插座` | 動作：開啟插座 |
| When | `使用者關閉智慧插座` | 動作：關閉插座 |
| When | `使用者查詢智慧插座狀態` | 動作：查詢狀態 |
| When | `使用者執行設備電源重啟` | 動作：電源重啟 |
| Then | `智慧插座應該處於開啟狀態` | 驗證：開啟狀態 |
| Then | `智慧插座應該處於關閉狀態` | 驗證：關閉狀態 |
| Then | `狀態查詢應該成功回傳` | 驗證：查詢成功 |
| And | `設備資訊應該正確顯示` | 驗證：設備資訊 |
| And | `操作記錄應該完整保存` | 驗證：日誌記錄 |

**環境變數設定:**
```bash
# 在 .env 檔案中設定
SWITCHBOT_TOKEN=your_token_here
SWITCHBOT_SECRET=your_secret_here
SWITCHBOT_DEVICE_ID=your_device_id_here
```

**相關檔案:**
- `libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py` - 主要 Library
- `resources/switchbot_keywords.robot` - Gherkin 風格關鍵字
- `tests/power_management/switchbot_smartplug_test.robot` - 測試案例

---

## 🚀 重大更新 (2026-01-29) - v5.6.0 YOLO 截圖傳送功能

### ✅ YOLO 檢測結果回傳與儲存
- **Client 端接收 YOLO 檢測圖片**
  - 現在可以將 Server 端 YOLO 檢測的結果圖片（含標註）回傳至 Client 端並儲存。
  - 主要用於測試失敗時的除錯分析，或蒐集特定狀態的樣本。
  - 圖片儲存路徑: `output/debug_images/`

### ✅ 關鍵字更新
- **`Then YOLO 應該檢測到按鈕 "${button_id}" 為 "${expected_state}"`**
  - 新增參數 `save_debug_image` (預設 False)。
  - 設定為 True 時，會強制下載並儲存 YOLO 檢測圖片。
  - 範例: `Then YOLO 應該檢測到按鈕 "light1" 為 "on"  save_debug_image=True`

- **`YOLO 僅檢測並儲存按鈕影像 "${button_id}" 預期狀態 "${expected_state}"`**
  - 新增關鍵字，專用於蒐集圖片而不進行驗證。
  - 自動下載並儲存圖片，檔名包含時間戳記與預期狀態。
  - 範例: `YOLO 僅檢測並儲存按鈕影像 "light1" 預期狀態 "off"`


## 🚀 重大更新 (2026-01-27) - v5.5.5 關節移動追蹤與維護分析

### ✅ 機器手臂維護分析 (Maintenance Analysis)
- **關節移動統計 (Joint Movement Tracking)**
  - 新增基於底層移動指令推算的關節移動追蹤功能。
  - 用於估算機器手臂各關節的累積磨損程度。
  - 支援 Gherkin 風格關鍵字進行統計數據的取得、記錄與重置。

### ✅ 新增關鍵字
- `取得關節移動統計`: 回傳 6 個關節的累積移動度數。
- `記錄關節移動統計`: 將當前累積的與移動數據寫入測試報告。
- `重置關節移動統計`: 清除目前的累積計數。

### ✅ 系統維護 (System Maintenance)
- **磁碟空間管理 (Disk Management)**
  - 新增磁碟空間監控與清理功能，防止 Debug 圖片佔用過多空間。
  - `Given 磁碟剩餘空間應大於 "${size_mb}" MB`: 檢查剩餘空間。
  - `When 清理超過 "${days}" 天前的 Debug 圖片`: 清理舊檔案。
  - `When 保留最新的 "${count}" 張 Debug 圖片`: 依數量限制保留檔案。

## 🚀 重大更新 (2026-01-27) - v5.5.0 RTSP 影像擷取效能優化 (最終版)

### ✅ 視覺檢測效能大幅提升
- **智慧緩衝區清空 (Smart Buffer Flush) - 最終優化**
  - 優化 `RTSPImageSource.flush_buffer` 機制，基於實測確定最佳參數
  - **最佳配置**: 強制清空前 30 幀 + 動態智慧退出
  - **效能數據** (實測對比):
    * 原始 (90 幀固定): ~15s (可靠但慢)
    * v5.5.0 (30 幀): **7s / 6s / 1.6s** (可靠且快) ✅ **最佳**
    * 測試 (20 幀): 失敗 (清空不足，讀取到舊影像)
  - **總體提升**: 平均檢測時間從 15s 降至 **5s**，提升 **67%**
  - 解決了固定清空導致的嚴重延遲問題，同時保證可靠性


## 🚀 重大更新 (2026-01-26) - v5.4.0 原子化按壓與 Socket 優化

### ✅ 機器手臂控制增強
- **原子化按壓指令 (Atomic Press)**
  - 在 Server 端實作 `press_button_angles` 指令，將 `down -> wait -> up` 動作序列原子化。
  - 解決了因網路延遲導致按壓時間不精確（過長）的問題。
  - 修改 `RobotArmKeywords.py` 中的 `_press_button` 方法，底層改用原子指令。

### ✅ Socket 通訊優化
- **Socket 緩衝區清空**
  - 在發送 JSON 指令前，新增自動清空 Socket 接收緩衝區的機制。
  - 解決了因硬體回應延遲導致 Raw Byte (0xfe...) 殘留在緩衝區，進而干擾 JSON 響應解析的問題。
  - 提升了 `scan_and_detect` 與原子按壓指令的通訊穩定性。

### ✅ 視覺除錯增強
- **原始影像保存**
  - `scan_and_detect` 功能現在除了保存標註後的影像外，也會保存原始影像（後綴 `_raw.jpg`）。
  - 方便後續重新標註或訓練模型使用。

## 🚀 重大更新 (2025-12-02) - v1.3.0 音訊路由驗證增強

### ✅ 音訊關鍵字增強
- **Given 音訊輸出聲道 "${channel}" 已準備就緒**
  - 新增自動路由驗證功能
  - 現在會檢查 PipeWire 虛擬 Sink (Scarlett_1-2 / Scarlett_3-4) 是否存在
  - 若路由未設定，將自動報錯並提示執行 `setup_pipewire_routing_v5.sh`

## 🚀 重大更新 (2025-12-02) - v1.4.0 語音命令日誌與交叉測試增強

### ✅ 語音控制關鍵字優化
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"**
  - 新增自動記錄語音命令完成時間 (`${command_end}`)
  - 格式: `YYYYMMDD_HHMMSS.f`
  - 方便後續計算響應時間，無需在測試案例中手動調用 `Get Current Date`

### ✅ 測試案例完善
- **tests/test_voice_commands_rv.robot**
  - 新增 Light 1 - Light 4 的完整交叉聲道測試
  - 涵蓋 Ch1->Ch2, Ch2->Ch3, Ch3->Ch1 的所有組合
  - 移除 `Then 語音應該成功播放到指定聲道` (改由 UART 回應驗證)

## 🚀 重大更新 (2025-11-18) - v4.0.0 本機化視覺檢測系統

### ✅ 機器手臂視覺檢測系統 - 本機化遷移完成

**更新概覽:**
- ✅ 影像判定從 Server 遷移至本機端（Client-side Vision Detection）
- ✅ 新增 32+ BDD 中文關鍵字（Given-When-Then 結構）
- ✅ 支援 3 個測試環境（Taipei LAB / Taoyuan LAB / RV Car）
- ✅ 雙影像源支援（RTSP IP Camera / Socket USB Camera）
- ✅ 8 種顏色檢測 + 11 級亮度檢測（0-100%，10% 步進）
- ✅ 環境專屬 YAML 配置管理

**核心架構變更:**
```
v3.0.0（舊版）: Client → Server（影像判定在 Jetson Nano）
v4.0.0（新版）: Client（本機影像判定）+ Server（僅提供影像截取）
```

**影像源用途區分:**
| 檢測目標 | 影像源類型 | 配置位置 | 用途 |
|---------|----------|---------|------|
| **面板按鈕 LED** | Socket | `buttons` → `type: "panel_light"` | 機器手臂 USB Camera |
| **環境燈光** | RTSP | `environment_lights` → `camera_id` | IP Camera (level2) |
| **YOLO 狀態驗證** | Socket/Server | `buttons` → `vision.observe_angles` | 伺服器端 YOLO 模型 |

**新增 BDD 關鍵字（32+）:**

**Given 關鍵字（前置條件）- 3 個:**
- `Given 測試環境設定為 "${environment}"` - 設定測試環境並自動載入全部按鈕配置（taipei_lab / taoyuan_lab / rv_car）
- `Given TTS 引擎已設定為 "${engine}"` - 設定 TTS 引擎
- `Given API 服務已在端點 "${endpoint}" 運行` - API 服務前置條件
- `Given 若 YOLO 檢測到按鈕 "${button_id}" 為 "${target_state}" 則點擊喚醒` - 條件式喚醒 (若狀態符合則點擊)

**When 關鍵字（執行動作）- 16 個:**
- `When 用戶連接到機器手臂 "${host}" "${port}"` - 建立連接
- `When 用戶中斷與機器手臂的連接` - 斷開連接
- `When 用戶移動機器手臂到初始位置` - 歸位操作
- `When 用戶按壓第 "${button_id}" 按鈕` - 按壓按鈕
- `When 用戶長按第 "${button_id}" 按鈕 "${duration}" 秒` - 長按按鈕
- `When 用戶檢測第 "${button_id}" 按鈕的燈光狀態` - 檢測面板按鈕 LED（Socket）
- `When 用戶檢測多個按鈕的燈光狀態 "${button_ids}"` - 批次檢測
- `When 用戶檢測環境燈光亮度 "${light_id}"` - 檢測環境燈光（RTSP）
- `When 使用者發送 GET 請求到 "${url}"` - API GET 請求
- `When 使用者發送 POST 請求到 "${url}" 帶資料 "${data}"` - API POST 請求
- 以及其他 6 個操作關鍵字...

**Then 關鍵字（驗證結果）- 12 個:**
- `Then 機器手臂操作應該成功完成` - 驗證操作成功
- `Then 按鈕燈光應該為 "${expected_color}" 色` - 驗證顏色 (HSV)
- `Then YOLO 應該檢測到按鈕 "${button_id}" 為 "${expected_state}"` - 驗證物件狀態 (YOLO + 180°翻轉)
- `Then 按鈕亮度應該為 "${expected_level}" %` - 驗證亮度
- `Then 檢測信心度應該大於 ${min_confidence}` - 驗證信心度
- `Then 環境燈光亮度應該為 "${expected_level}" %` - 驗證環境燈光
- `Given/When/Then/And 按鈕 "${button_id}" 的狀態應為 "${expected_state}"` - 視覺狀態驗證 (v4.3.0)
- `Then 回應狀態碼應該為 "${status_code}"` - API 驗證
- `Then 回應內容應該包含 "${expected_content}"` - 內容驗證
- 以及其他 5 個驗證關鍵字...

**Other 關鍵字（維護分析）- 3 個 (v5.5.5):**
- `取得關節移動統計` - 回傳每個關節的累積移動度數列表
- `記錄關節移動統計` - 記錄統計數據到日誌
- `重置關節移動統計` - 重置累計數據
- `Get YOLO Detection Status` - 取得 YOLO 檢測狀態 (不拋出例外)

**技術細節:**
- **LocalVisionAnalyzer**: 本機影像分析引擎（HSV 色彩空間 + 多幀平均）
- **ImageSourceManager**: 雙影像源管理（RTSP / Socket）
- **EnvironmentConfig**: 多環境配置管理系統
- **ConfigLoader**: YAML 配置統一載入器

**測試案例:**
- `tests/robot_arm/basic_button_test.robot` - 基礎按鈕測試
- `tests/robot_arm/multi_environment_test.robot` - 多環境測試
- `tests/robot_arm/multi_color_detection_test.robot` - 多色彩檢測
- `tests/robot_arm/brightness_level_test.robot` - 亮度檢測
- `tests/robot_arm/button_press_feedback_test.robot` - 按壓反饋測試

**相關文檔:**
- `docs/vision_detection_local_spec.md` - 技術規格書
- `docs/vision_detection_tdd_guide.md` - TDD 開發指南
- `docs/vision_detection_quick_start_guide.md` - 快速上手指南
- `docs/keyword_design_guidelines.md` - BDD 關鍵字設計規範

**版本歷程:**
- v1.0.0 (2025-11-05): 基礎 Socket 控制
- v2.0.0 (2025-11-10): ArUco 標記檢測
- v3.0.0 (2025-11-13): Server-side 視覺檢測
- v4.0.0 (2025-11-18): 本機化視覺檢測
- v4.1.0 (2025-01-21): 伺服器端 YOLO 狀態驗證
- **v5.5.5 (2026-01-27): 關節移動追蹤與維護分析 ← 當前版本**

---

## 🔧 最新維護更新 (2025-11-13)

### ✅ Mobile Keywords 英文關鍵字修復完成

**修復任務概覽:**
- ✅ 修復 `resources/mobile_keywords.robot` 中的英文關鍵字名稱
- ✅ 將所有 Then/And 英文關鍵字轉換為中文
- ✅ 更新相關引用和文檔

**修復的關鍵字清單:**
```robotframework
# 修復前 → 修復後
Then Element Text Should Be → Then 元素文字應該是
Then Element Should Be Visible → Then 元素應該可見  
Then Application Should Be Closed → Then 應用程式應該已關閉
Then User Should See Loading Complete → Then 使用者應該看到載入完成
Then Login Should Be Successful → Then 登入應該成功
And User Also Taps On Element → And 使用者同時點擊元素
And Application Is Still Running → And 應用程式仍在運行
And User Can See Element → And 使用者可以看到元素
And Screenshot Is Taken → And 截圖已擷取
```

**技術細節:**
- ✅ 更新了所有 Legacy Keywords 中的關鍵字引用
- ✅ 保持了完整的雙語文檔和參數說明
- ✅ 維護了向後相容性

**驗證結果:**
- ✅ Robot Framework 語法檢查通過
- ✅ 所有中文關鍵字可正常調用
- ✅ Legacy 關鍵字引用正確更新

### ✅ Multi-Light Keywords 模組匯入修復完成

**修復任務概覽:**
- ✅ 修復 `resources/multi_light_keywords.robot` 中的錯誤模組匯入路徑
- ✅ 解決 MultiLightKeywords 類別找不到的問題
- ✅ 確保多燈號陣列檢測關鍵字正常運作

**技術細節:**
```robotframework
# 問題匯入 (修復前)
Library    ../libraries/multimodal_detection/    WITH NAME    MultiLightLib

# 修復後匯入
Library    ../libraries/ipcam_light_detection/MultiLightKeywords.py    WITH NAME    MultiLightLib
```

**修復驗證:**
- ✅ 模組匯入測試通過: `MultiLightKeywords 匯入成功`
- ✅ Robot Framework 語法檢查通過
- ✅ 所有多燈號關鍵字可正常調用

**影響檔案:**
- `resources/multi_light_keywords.robot`: 匯入路徑修復
- `resources/mobile_keywords.robot`: 英文關鍵字名稱修復

**問題根因:**
1. **錯誤模組路徑**: 原先指向 `multimodal_detection` 模組，但 `MultiLightKeywords` 實際位於 `ipcam_light_detection` 模組
2. **英文關鍵字名稱**: 違反了項目的中文關鍵字標準化要求

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

## 📱 移動設備關鍵字庫 (resources/mobile_keywords.robot)

### Given Keywords (前置條件)
- `Given 使用者已準備好移動應用程式` - 設定移動應用程式測試環境
- `Given 應用程式已啟動` - 確認應用程式已成功啟動
- `Given 使用者在登入畫面` - 確認使用者位於登入畫面
- `Given 應用程式載入已完成` - 確認應用程式完全載入

### When Keywords (執行動作)
- `When 使用者點擊元素` - 使用者點擊指定元素
- `When 使用者輸入文字` - 使用者在指定欄位輸入文字
- `When 使用者滑動螢幕` - 使用者執行螢幕滑動操作
- `When 使用者登入應用程式` - 使用者執行登入操作
- `When 使用者擷取螢幕截圖` - 使用者擷取螢幕截圖
- `When 使用者等待元素` - 使用者等待指定元素出現

### Then Keywords (驗證結果) - Legacy English Keywords
- `Then Element Text Should Be` - 驗證元素文字內容
- `Then Element Should Be Visible` - 驗證元素可見性
- `Then Application Should Be Closed` - 驗證應用程式已關閉
- `Then User Should See Loading Complete` - 驗證載入完成
- `Then Login Should Be Successful` - 驗證登入成功

### And Keywords (附加驗證) - Legacy English Keywords
- `And User Also Taps On Element` - 額外點擊操作
- `And Application Is Still Running` - 確認應用程式仍在運行
- `And User Can See Element` - 確認使用者可以看到元素
- `And Screenshot Is Taken` - 確認螢幕截圖已擷取

---

## 🌐 通用關鍵字庫 (resources/common_keywords.robot)

### Given Keywords (前置條件)
- `系統已設定為 "${platform}" 平台模式` - 設定測試平台（mobile/web/api）
- `使用者擁有有效的登錄憑證` - 準備有效的使用者憑證
- `API 服務端點已經可以存取` - 確認 API 服務可用
- `機器手臂控制系統已經初始化` - 初始化機器手臂系統
- `實體設備 "${device_name}" 已經連接` - 確認實體設備連接

### When Keywords (執行動作)
- `使用者嘗試登錄到應用程式` - 執行跨平台登錄操作
- `使用者發送 API 請求進行身份驗證` - 執行 API 身份驗證
- `使用者操作機器手臂點擊實體按鈕 "${button_name}" 在座標 "${x}" "${y}" "${z}"` - 機器手臂點擊操作
- `使用者驗證頁面元素 "${locator}" 包含文字 "${expected_text}"` - 驗證頁面元素文字

### Then Keywords (驗證結果)
- `登錄應該成功並顯示正確的歡迎訊息` - 驗證登錄成功
- `API 回應應該包含成功訊息` - 驗證 API 回應
- `實體按鈕應該被成功觸發` - 驗證實體按鈕操作
- `頁面應該顯示預期的標題 "${expected_title}"` - 驗證頁面標題
- `元素文字應該符合預期值` - 驗證元素文字

### And Keywords (附加驗證)
- `實體設備狀態應該為正常` - 驗證實體設備狀態
- `使用者應該可以看到相應的 UI 回饋` - 驗證 UI 回饋
- `系統應該記錄相關的操作日誌` - 驗證日誌記錄

### Legacy Keywords (向後相容)
- `登錄應用程式` - 跨平台登錄執行
- `執行行動應用程式登錄` / `執行網頁應用程式登錄`
- `驗證頁面標題` / `驗證元素文字`
- `執行 API 登錄` / `點擊實體按鈕`
- `驗證實體物件存在`

---

## 🌐 網頁關鍵字庫 (resources/web_keywords.robot)

### Given Keywords (前置條件)
- `網頁瀏覽器已經啟動並導航到 "${url}"` - 啟動瀏覽器並導航
- `使用者可以看到網頁登錄表單` - 確認登錄表單存在
- `網頁應用程式已經載入完成` - 確認網頁完全載入

### When Keywords (執行動作)
- `使用者在網頁輸入使用者名稱 "${username}"` - 輸入使用者名稱
- `使用者在網頁輸入密碼 "${password}"` - 輸入密碼
- `使用者點擊網頁登錄按鈕` - 點擊登錄按鈕
- `使用者在網頁元素 "${locator}" 輸入文字 "${text}"` - 在指定元素輸入文字
- `使用者點擊網頁元素 "${locator}"` - 點擊指定元素

### Then Keywords (驗證結果)
- `網頁應該顯示歡迎訊息` - 驗證歡迎訊息
- `網頁應該顯示文字 "${text}"` - 驗證網頁文字
- `網頁元素 "${locator}" 應該存在` - 驗證元素存在
- `網頁標題應該為 "${title}"` - 驗證網頁標題

### And Keywords (附加驗證)
- `網頁應該不包含錯誤訊息` - 驗證無錯誤訊息
- `使用者應該可以正常導航網頁` - 驗證網頁導航
- `網頁載入應該在合理時間內完成` - 驗證載入效能

### Legacy Keywords (向後相容)
- `打開網頁瀏覽器` / `關閉網頁瀏覽器`
- `輸入文字到網頁元素` / `點擊網頁元素`
- `等待網頁包含文字` / `等待網頁包含元素`
- `網頁不包含文字` / `網頁不包含元素`

---

## 🔌 API 關鍵字庫 (resources/api_keywords.robot)

### Given Keywords (前置條件)
- `Given API 服務已在端點 "${url}" 運行` - 確認 API 服務運行
- `Given 使用者擁有有效的 API 憑證` - 準備 API 憑證
- `Given API 請求資料已準備包含 "${key}" 和 "${value}"` - 準備請求資料

### When Keywords (執行動作)
- `When 使用者發送 GET 請求到路徑 "${path}"` - 發送 GET 請求
- `When 使用者發送 POST 請求到路徑 "${path}" 包含登錄資料` - 發送 POST 登錄請求
- `When 使用者發送 POST 請求到路徑 "${path}" 包含資料 "${data}"` - 發送 POST 請求
- `When 使用者驗證 API 回應包含鍵值對 "${key}" 和 "${value}"` - 驗證回應鍵值對

### Then Keywords (驗證結果)
- `Then API 回應應該包含成功訊息 "${message}"` - 驗證成功訊息
- `Then API 回應狀態碼應該為成功` - 驗證狀態碼
- `Then API 回應應該包含鍵 "${key}" 且值為 "${value}"` - 驗證回應鍵值
- `Then API 回應應該是有效的 JSON 格式` - 驗證 JSON 格式

### And Keywords (附加驗證)
- `And API 回應時間應該在合理範圍內` - 驗證回應時間
- `And API 回應應該包含必要的標頭` - 驗證回應標頭
- `And API 會話應該正確建立並維持` - 驗證會話狀態

### Legacy Keywords (向後相容)
- `建立 API 會話` / `發送 GET 請求` / `發送 POST 請求`
- `驗證 JSON 響應包含鍵值對` / `驗證 JSON 響應包含多個鍵值對`
- `驗證 JSON 響應路徑值`

---

---

## AudioKeywords - 音訊硬體控制關鍵字 (libraries/voice_control/AudioKeywords.py)

用於控制 Focusrite Scarlett 4i4 音訊介面，支援 4 聲道獨立輸出測試。

### 引用方式
```robotframework
Resource    resources/audio_keywords.robot
```

### 常用關鍵字

#### Given Scarlett 音訊介面可用
檢查系統中是否已正確設定 Scarlett 4i4 的虛擬音訊設備 (Scarlett_1-2, Scarlett_3-4)。

#### When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}"
播放指定的音訊檔案到目標聲道 (1-4)。
- `audio_file`: 音訊檔案路徑
- `channel`: 目標聲道 (1, 2, 3, 4)
- `duration`: 播放時間 (秒)，預設 5 秒

#### When 使用者播放音訊檔案 "${audio_file}" 到聲道 "${channel}" 持續 "${duration}" 秒
播放指定的音訊檔案到目標聲道，並指定播放持續時間。
- `audio_file`: 音訊檔案路徑
- `channel`: 目標聲道 (1, 2, 3, 4)
- `duration`: 播放時間 (秒)

#### Then 預設音訊輸出應該是 "${expected_sink}"
驗證當前的系統預設音訊輸出設備。
- `expected_sink`: 預期的設備名稱 (如 "Scarlett_1-2")

#### 列出可用輸出設備
列出系統中所有可用的 PipeWire/PulseAudio 輸出設備並記錄到日誌。無參數。

**使用範例**:
```robotframework
列出可用輸出設備
```

#### 取得當前預設輸出設備
取得系統當前預設的音訊輸出設備名稱，回傳 sink 名稱字串。

**使用範例**:
```robotframework
${sink}=    取得當前預設輸出設備
Log    當前輸出設備: ${sink}
```

#### 取得聲道對應的輸出設備
依聲道編號 (1–4) 回傳對應的 Scarlett 虛擬設備名稱。
- `channel`: 聲道編號 (1, 2, 3, 4)

**使用範例**:
```robotframework
${device}=    取得聲道對應的輸出設備    1
Log    聲道 1 對應設備: ${device}
```

---

## 🎤 語音控制關鍵字 (libraries/voice_control/VoiceControlKeywords.py) ✅ **符合規範**

### 📋 模組資訊

- **庫名稱**: `VoiceControlKeywords`
- **控制設備**: Focusrite Scarlett 4i4 (第四代) USB 音效介面
- **功能**: Google TTS + 多聲道音訊播放控制 + UART 語音回應監控
- **總關鍵字數**: 26個 (6個 Given + 7個 When + 7個 Then + 6個 And)
- **符合規範狀態**: ✅ **完全符合** - 2025-11-12 UART 整合完成
- **建立日期**: 2025-11-11
- **重構日期**: 2025-11-11
- **UART 整合日期**: 2025-11-12 (v1.2.0)

### ✅ 規範符合性分析

| 評估項目 | 狀態 | 說明 |
|---------|------|------|
| **中文關鍵字名稱** | ✅ 符合 | 所有關鍵字使用中文命名 |
| **Gherkin 語法結構** | ✅ 符合 | 完整的 Given-When-Then-And 前綴 |
| **詳細文檔說明** | ✅ 符合 | 每個關鍵字有完整 Documentation |
| **測試案例覆蓋** | ✅ 符合 | 測試案例使用 Gherkin 結構 |
| **向後相容性** | ✅ 符合 | 保留 Legacy 關鍵字確保相容性 |

### 🎯 Gherkin 關鍵字清單 (新版本)

#### Given Keywords (前置條件)
- **Given 語音控制系統已成功初始化** - 確認語音控制系統已成功初始化，包括 TTS 管理器和音訊播放器
- **Given Scarlett 4i4 音效介面已正確連接** - 確認 Focusrite Scarlett 4i4 音效介面正確連接並可用
- **Given TTS 引擎已設定為 "${engine_name}"** - 設定並確認指定的 TTS 引擎已正確配置 (gtts/pyttsx3)
- **Given TTS 語言已設定為 "${language}"** - 設定並確認指定的 TTS 語言已正確配置 (en/zh-TW/ja)
- **Given TTS 語速已設定為 "${speed}"** - 設定並確認指定的 TTS 語速已正確配置 (wpm, 僅 pyttsx3)
- **Given 音訊輸出聲道 "${channel}" 已準備就緒** - 確認指定音訊輸出聲道已準備就緒 (含路由驗證) (1-4)
- **Given UART 日誌監控器已初始化** - 初始化 UART 監控器用於檢測語音回應 (v1.2.0 新增)

#### When Keywords (執行動作)
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"** - 使用者播放文字到指定聲道
- **When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"** - 使用者播放文字到指定聲道使用指定語言
- **When 使用者切換 TTS 引擎到 "${engine_name}"** - 使用者切換 TTS 引擎到指定引擎
- **When 使用者設定 TTS 語速為 "${speed}"** - 使用者設定 TTS 語速為指定值
- **When 使用者查詢當前 TTS 引擎資訊** - 使用者查詢當前 TTS 引擎資訊
- **When 使用者測試指定聲道 "${channel}" 的音訊輸出** - 使用者測試指定聲道的音訊輸出
- **When 使用者啟動 UART 背景監控** - 啟動 UART 背景監控以檢測語音回應 (v1.2.0 新增)
- **When 使用者停止 UART 背景監控** - 停止 UART 背景監控 (v1.2.0 新增)

#### Then Keywords (驗證結果)
- **Then 語音應該成功播放到指定聲道** - 驗證語音播放操作是否成功完成
- **Then TTS 引擎應該成功切換** - 驗證 TTS 引擎切換是否成功
- **Then 音訊輸出應該清晰無雜音** - 驗證音訊輸出品質是否符合標準
- **Then 系統應該回傳正確的 TTS 引擎資訊** - 驗證系統是否回傳正確的 TTS 引擎資訊
- **Then Scarlett 4i4 設備應該處於正常運作狀態** - 驗證 Scarlett 4i4 設備是否處於正常運作狀態
- **Then 應該在 "${timeout}" 秒內收到恰好 "${count}" 個語音回應** - 驗證 UART 日誌中語音回應的數量 (v1.2.0 新增)
- **Then 應該在 "${timeout}" 秒內收到包含以下檔案的語音回應 "${patterns}"** - 驗證 UART 日誌中語音回應的檔案名稱（支援多個檔案，逗號分隔） (v1.2.0 新增)
- **Then 應該在 "${timeout}" 秒內收到語音指令 "${command_keys}" 的回應** - 驗證 UART 日誌中語音回應是否符合指定的語音指令 Key（支援多個 Key，逗號分隔） (v1.4.1 新增)

#### And Keywords (附加驗證)
- **And 語音品質應該符合標準** - 驗證語音品質是否符合預定標準
- **And 沒有音訊延遲或中斷** - 驗證音訊播放過程中沒有延遲或中斷
- **And 暫存檔案應該正確清理** - 驗證暫存檔案是否正確清理
- **And 錯誤日誌應該為空** - 驗證系統錯誤日誌是否為空
- **And 系統資源使用應該在正常範圍內** - 驗證系統資源使用是否在正常範圍內
- **And 清空 UART 事件記錄** - 清空 UART 監控器的事件記錄 (v1.2.0 新增)

### 🔌 UART 語音回應監控功能 (v1.2.0 新增 - 2025-11-12)

**功能概述:**
整合 SerialLogParser 模組，透過 UART 串列埠監控 ASR Pro 語音助手的回應，用於驗證語音命令是否正確觸發語音回應。

**核心功能:**
- 背景監控 UART 串列埠日誌
- 檢測語音播放事件（Playing audio file / Playing voice command reply）
- 驗證語音回應數量（恰好 N 個回應）
- 驗證語音回應檔案名稱（檔案模式匹配）
- 完整日誌記錄與診斷輸出

**UART 監控關鍵字:**

1. **Given UART 日誌監控器已初始化** - 初始化 UART 監控器
   ```robotframework
   Given UART 日誌監控器已初始化
   Given UART 日誌監控器已初始化    /dev/ttyUSB0    115200
   ```

2. **When 使用者啟動 UART 背景監控** - 啟動背景監控
   ```robotframework
   When 使用者啟動 UART 背景監控
   ```

3. **Then 應該在 "${timeout}" 秒內收到恰好 "${count}" 個語音回應** - 驗證回應數量
   ```robotframework
   Then 應該在 "5" 秒內收到恰好 "1" 個語音回應
   Then 應該在 "10" 秒內收到恰好 "3" 個語音回應
   ```

4. **Then 應該在 "${timeout}" 秒內收到包含以下檔案的語音回應 "${patterns}"** - 驗證檔案名稱
   ```robotframework
   # 單一檔案
   Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3"

   # 多個檔案（逗號分隔）
   Then 應該在 "10" 秒內收到包含以下檔案的語音回應 "Light_timer_set.mp3,1.mp3,hours.mp3"
   ```

5. **And 清空 UART 事件記錄** - 清空事件記錄（用於測試間隔離）
   ```robotframework
   And 清空 UART 事件記錄
   ```

6. **When 使用者停止 UART 背景監控** - 停止監控
   ```robotframework
   When 使用者停止 UART 背景監控
   ```

**完整測試範例:**
```robotframework
*** Test Cases ***
Scenario: 測試 Off Grid Mode 語音指令
    [Documentation]    測試離網模式的語音指令與 UART 回應驗證
    [Tags]    voice    uart    asrpro

    # 前置條件
    Given 音訊輸出聲道 "1" 已準備就緒
    And 清空 UART 事件記錄

    # 啟動 UART 監控
    When 使用者啟動 UART 背景監控

    # 執行語音命令
    When 使用者播放文字 "hey power pro" 到聲道 "1"
    Sleep    2
    When 使用者播放文字 "Off Grid Mode" 到聲道 "1"

    # 驗證語音播放
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準

    # 驗證 UART 日誌中的語音回應（恰好 1 個回應）
    Then 應該在 "5" 秒內收到包含以下檔案的語音回應 "Off_grid_mode.mp3"
```

**支援的日誌格式:**
- `Playing audio file: xxx.mp3` - 基本音訊播放
- `Playing voice command reply: /path/to/xxx.mp3` - 語音命令回應

**失敗情境:**
- 數量不符：預期 1 個，實際 0 個或 2+ 個 → FAIL
- 檔案不符：預期 "Off_grid_mode.mp3"，實際 "Welcome_back.mp3" → FAIL
- 超時：在指定時間內未收到任何回應 → FAIL

**診斷功能:**
測試失敗時會自動輸出：
- 完整的 UART 日誌（所有行）
- 包含 mp3/audio/playing 關鍵字的行（診斷用）
- 預期與實際的檔案名稱比對

---

### 🎯 現代化完成 - 純 Gherkin 關鍵字架構

> **⚠️ 重要變更 (2025-11-11)**: Legacy 關鍵字已完全移除，voice_control 模組現在採用 100% Gherkin 中文關鍵字架構
> **🆕 最新功能 (2025-11-12 v1.2.0)**: 新增 UART 語音回應監控功能，支援 ASR Pro 語音命令測試

#### ✅ 核心語音播放功能 (現代化版本)
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"** - 文字轉語音並播放到指定聲道 (1-4)
- **When 使用者使用預設喇叭播放文字 "${text}"**
將文字轉換為語音並使用系統預設音訊輸出設備播放（不經過 Scarlett 4i4）。
- **跨平台支援**: 自動偵測作業系統
  - **macOS**: 使用 `afplay` 指令
  - **Linux**: 使用 `ffplay` 或 `aplay` 指令
- `text`: 要播放的文字
- **When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"** - 多語言文字轉語音播放

#### ✅ TTS 系統初始化與設定 (現代化版本)
- **Given 語音控制系統已成功初始化** - 初始化語音控制系統
- **Given TTS 引擎已設定為 "${engine_name}"** - 切換 TTS 引擎 (gtts/pyttsx3)
- **Given TTS 語言已設定為 "${language}"** - 設定語音語言 (zh-TW/en/ja)
- **Given 音訊輸出聲道 "${channel}" 已準備就緒** - 準備指定聲道輸出 (含路由驗證)

#### ✅ 設備連接與狀態驗證 (現代化版本)
- **Given Scarlett 4i4 音效介面已正確連接** - 檢查並確認 Scarlett 4i4 設備狀態
- **When 使用者查詢當前 TTS 引擎資訊** - 查詢當前 TTS 引擎狀態與配置
- **When 使用者測試指定聲道 "${channel}" 的音訊輸出** - 測試特定聲道的音訊輸出功能

#### ✅ 結果驗證與品質檢查 (現代化版本)
- **Then 語音應該成功播放到指定聲道** - 驗證語音播放成功
- **Then TTS 引擎應該成功切換** - 驗證 TTS 引擎切換成功
- **Then 音訊輸出應該清晰無雜音** - 驗證音訊品質
- **Then 系統應該回傳正確的 TTS 引擎資訊** - 驗證系統資訊查詢結果
- **Then Scarlett 4i4 設備應該處於正常運作狀態** - 驗證硬體設備狀態

#### ✅ 系統資源與品質管理 (現代化版本)
- **And 暫存檔案應該正確清理** - 自動清理暫存檔案和系統資源
- **And 語音品質應該符合標準** - 驗證語音品質標準
- **And 沒有音訊延遲或中斷** - 確保音訊播放流暢
- **And 錯誤日誌應該為空** - 確保系統無錯誤
- **And 系統資源使用應該在正常範圍內** - 監控系統資源使用情況

### 🚫 已移除的 Legacy 關鍵字 (不再支援)
> 以下 Legacy 關鍵字已於 2025-11-11 完全移除，請使用上述 Gherkin 關鍵字替代：

- ~~`播放文字到聲道`~~ → 使用 `When 使用者播放文字 "${text}" 到聲道 "${channel}"`
- ~~`設定 TTS 引擎`~~ → 使用 `Given TTS 引擎已設定為 "${engine_name}"`
- ~~`設定 TTS 語言`~~ → 使用 `Given TTS 語言已設定為 "${language}"`
- ~~`取得 TTS 引擎資訊`~~ → 使用 `When 使用者查詢當前 TTS 引擎資訊`
- ~~`檢查 Scarlett 設備`~~ → 使用 `Given Scarlett 4i4 音效介面已正確連接`
- ~~`清理語音控制資源`~~ → 使用 `And 暫存檔案應該正確清理`

### 🎯 使用範例

#### 現代化 Gherkin 測試案例範例
```robotframework
*** Test Cases ***
Scenario: 使用者需要通過 TTS 播放文字語音
    [Documentation]    使用現代化 Gherkin 關鍵字的完整測試場景
    [Tags]    voice    tts    gherkin    scarlett    modern
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    And Given TTS 引擎已設定為 "gtts"
    And Given 音訊輸出聲道 "1" 已準備就緒
    When 使用者播放文字 "Hello World" 到聲道 "1"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    And 沒有音訊延遲或中斷
    And 暫存檔案應該正確清理
```

#### 多語言與引擎切換範例
```robotframework
*** Test Cases ***
Scenario: 使用者切換 TTS 引擎並播放多語言文字
    [Documentation]    測試 TTS 引擎切換和多語言播放功能
    [Tags]    voice    tts    multilingual    engine_switch
    Given 語音控制系統已成功初始化
    And Given Scarlett 4i4 音效介面已正確連接
    When 使用者切換 TTS 引擎到 "pyttsx3"
    Then TTS 引擎應該成功切換
    When 使用者播放文字 "測試語音" 到聲道 "2" 使用語言 "zh-TW"
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
```

### � 重構成果總結

**重構前 (2025-11-11 之前):**
- ❌ 不符合 Gherkin 語法結構
- ✅ 關鍵字名稱使用中文
- ✅ 有詳細文檔
- ⚠️ 測試案例結構不一致

**重構後 (2025-11-11 完成):**
- ✅ **100% 符合專案規範** - 完整的 Gherkin 語法支援
- ✅ **完全現代化** - Legacy 關鍵字已完全移除，純 Gherkin 架構
- ✅ **提升可讀性** - Given-When-Then-And 結構更易理解
- ✅ **標準化測試** - 與其他模組保持一致的測試風格
- ✅ **功能完全保持** - 測試 100% 通過，無破壞性變更
- ✅ **現代化完成** - 成為專案中第二個 100% Gherkin 合規的模組

### 🔧 技術實作細節

- **主要類別**: `VoiceControlKeywords`
- **版本**: v1.2.0 (UART 整合版本)
- **關鍵字數量**: 26個 Gherkin 關鍵字 (純中文 + Gherkin 結構)
  - 6個 Given (前置條件)
  - 7個 When (執行動作)
  - 7個 Then (驗證結果)
  - 6個 And (附加驗證)
- **支援設備**:
  - Focusrite Scarlett 4i4 (第四代) - 音訊輸出
  - UART 串列埠 (預設 /dev/ttyUSB0, 115200 baud) - 語音回應監控
- **支援語言**: 英文 (en)、繁體中文 (zh-TW)、日文 (ja)
- **TTS 引擎**: Google TTS (gtts)、離線 TTS (pyttsx3)
- **整合模組**: SerialLogParser (UART 日誌解析)

### 🎯 Legacy 關鍵字移除完成 (2025年)

**✅ 完全移除的 Legacy 關鍵字:**
- `播放文字到聲道` → 改用 `When 使用者播放文字 "${text}" 到聲道 "${channel}"`
- `設定 TTS 引擎` → 改用 `Given TTS 引擎已設定為 "${engine_name}"`
- `取得 TTS 引擎資訊` → 改用 `When 使用者查詢當前 TTS 引擎資訊`
- `取得可用音訊設備` → 功能整合至 Gherkin 關鍵字
- `檢查 Scarlett 設備` → 改用 `Given Scarlett 4i4 音效介面已正確連接`
- `清理語音控制資源` → 改用 `And 暫存檔案應該正確清理`
- 其他 Legacy 關鍵字已轉為內部方法

**✅ 現代化完成狀態:**
- 所有 Robot Framework 測試檔案已更新使用新的 Gherkin 關鍵字
- Legacy @keyword 裝飾器已完全移除
- 舊功能保留為內部方法，供 Gherkin 關鍵字使用
- 測試套件 100% 通過，功能完全保持

### 📚 相關文檔

- **完整重構計劃**: `libraries/voice_control/GHERKIN_REFACTOR_PLAN.md` ✅ 已完成
- **模組 README**: `libraries/voice_control/README.md` ✅ 已更新
- **Python 關鍵字庫**: `libraries/voice_control/VoiceControlKeywords.py` ✅ v1.2.0 (UART 整合)
- **測試案例**:
  - `test_speak_text.robot` ✅ 100% Gherkin 格式 (基礎 TTS 測試)
  - `tests/test_asrpro_commands.robot` ✅ ASR Pro 語音命令測試 (UART 驗證)
- **備份檔案**: `libraries/voice_control/VoiceControlKeywords.py.backup` ✅ 已建立
- **UART 模組**: `libraries/multimodal_detection/SerialLogParser.py` ✅ v1.3.0 (支援雙格式)

**重構時間**: 約 2 小時 (實際完成時間: 2025-11-11)
**Legacy 移除時間**: 約 1.5 小時 (完成時間: 2025-11-11)
**UART 整合時間**: 約 3 小時 (完成時間: 2025-11-12)
**風險評估**: 無風險 (完整的診斷輸出與錯誤處理)
**測試狀態**: ✅ 所有功能測試通過，100% Gherkin 標準
**UART 測試**: ✅ Regex 修復完成，支援雙格式日誌  

---

## 📊 語音系統關鍵字 (test_speak_text.robot) ⚠️ **需要移動**

### Given Keywords (前置條件)
- `語音系統已經成功初始化` - 確保語音系統準備就緒

### When Keywords (執行動作)
- `使用者請求播放文字 "${text}"` - 使用者觸發 TTS 播放

### Then Keywords (驗證結果)
- `語音播放應該成功完成` - 驗證語音播放成功

### And Keywords (附加驗證)
- `測試執行結果應該被成功記錄` - 確認測試結果記錄

### Legacy Keywords (向後相容)
- `Voice System Has Been Initialized Successfully`
- `User Requests To Play Text "${text}"`
- `Speech Should Be Played Successfully`
- `Test Execution Results Should Be Recorded Successfully`

---

## 🔌 SwitchBot 智慧插座關鍵字 (resources/switchbot_keywords.robot) ✅ **[新增 2025-06-23]**

### 功能概述
提供 SwitchBot 智慧插座的完整控制功能，支援 Gherkin 風格的中文關鍵字，可實現：
- 智慧插座開關控制
- 設備狀態查詢與驗證  
- 電源管理操作
- 設備資訊取得

### Given Keywords (前置條件)
- `已設定SwitchBot API認證資訊` - 設定 SwitchBot API 的 Token 和 Secret
- `已知智慧插座設備ID` - 設定要控制的智慧插座設備 ID
- `智慧插座系統已準備就緒` - 檢查 SwitchBot API 連線與系統初始化狀態
- `已取得所有SwitchBot設備清單` - 取得帳號下所有 SwitchBot 設備資訊

### When Keywords (執行動作)  
- `使用者開啟智慧插座` - 開啟指定的智慧插座設備
- `使用者關閉智慧插座` - 關閉指定的智慧插座設備
- `使用者查詢智慧插座目前狀態` - 查詢智慧插座目前的開關狀態
- `使用者取得智慧插座設備資訊` - 取得智慧插座的詳細設備資訊
- `使用者執行智慧插座重啟` - 執行智慧插座的重啟操作（關閉->等待->開啟）

### Then Keywords (驗證結果)
- `智慧插座應該處於開啟狀態` - 驗證智慧插座處於開啟 (on) 狀態
- `智慧插座應該處於關閉狀態` - 驗證智慧插座處於關閉 (off) 狀態  
- `設備資訊應該正確顯示` - 驗證設備資訊包含正確的名稱、類型、狀態等
- `插座狀態查詢應該成功` - 驗證狀態查詢操作成功執行
- `智慧插座重啟應該成功完成` - 驗證重啟操作成功完成

### And Keywords (附加驗證與操作)
- `等待設備狀態變更` - 等待智慧插座狀態改變指定秒數
- `操作記錄應該完整保存` - 檢查操作日誌是否完整記錄
- `API認證應該有效` - 驗證 SwitchBot API 認證資訊有效性
- `設備清單應該包含目標設備` - 驗證設備清單包含指定的智慧插座

### 其他關鍵字（資源檔補充）

以下關鍵字定義於 `resources/switchbot_keywords.robot`，為 BDD 場景中額外支援的工具型關鍵字：

| 關鍵字名稱 | 類型 | 說明 |
|---|---|---|
| `等待智慧插座狀態變更` | And/When | 呼叫底層 `等待設備狀態變更`，等待插座狀態變化（秒） |
| `取得智慧插座狀態應該是` | Then | 取得當前狀態並驗證是否符合預期值（on/off） |
| `系統狀態應該保持穩定` | And | 驗證插座連線及整體系統在操作後仍保持穩定 |
| `設定測試環境變數` | （Suite Setup） | 設定測試所需環境變數（TOKEN、SECRET、DEVICE_ID）以利執行 |
| `清理測試環境` | （Suite Teardown） | 清理測試產生的暫存狀態與資源 |

### 使用範例
```robotframework
*** Test Cases ***
測試智慧插座基本控制
    [Tags]    smartplug    basic    gherkin
    Given 已設定SwitchBot API認證資訊    ${TOKEN}    ${SECRET}
    And 已知智慧插座設備ID    ${DEVICE_ID}
    And 智慧插座系統已準備就緒
    When 使用者開啟智慧插座    ${DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${DEVICE_ID}
    And 設備資訊應該正確顯示    ${DEVICE_ID}
    When 使用者關閉智慧插座    ${DEVICE_ID}
    Then 智慧插座應該處於關閉狀態    ${DEVICE_ID}
    And 操作記錄應該完整保存
```

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

## 移動應用程式測試 (Appium 整合)

### 移動應用程式 Gherkin 關鍵字

#### Given Keywords
```robot
移動應用程式測試環境已經設定完成
iOS 應用程式已經安裝在模擬器上
Android 應用程式已經安裝在模擬器上
使用者已在移動設備上啟動應用程式
```

#### When Keywords
```robot
使用者在移動應用程式中輸入文字到元素 "${locator}" 內容為 "${text}"
使用者點擊移動應用程式元素 "${locator}"
使用者向左滑動螢幕
使用者向右滑動螢幕
使用者等待移動應用程式頁面載入完成
```

#### Then Keywords
```robot
移動應用程式應該顯示文字 "${text}"
移動應用程式元素 "${locator}" 應該存在
移動應用程式應該導航到正確的頁面
應用程式標題應該顯示為 "${title}"
```

#### And Keywords
```robot
移動應用程式應該回應使用者操作
使用者應該可以進行正常的手勢操作
應用程式效能應該在可接受範圍內
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

## 🆕 最新更新 (2025年11月) - IP Camera 燈光檢測模組

### ✅ IP Camera 關鍵字庫 (resources/ipcam_keywords.robot)

**模組狀態**: ✅ 已完成並測試通過

**功能概述**: 基於 RTSP 串流的 IP Camera 影像分析與燈光狀態檢測系統

#### 連接管理關鍵字

**連接實驗室 Level1 攝影機**
```robotframework
Given 連接實驗室 Level1 攝影機
```
- 用途：連接到實驗室 Level 1 監控攝影機
- RTSP URL: rtsp://username:password@192.168.165.184:554/live0
- 支援 HEVC/H.265 編碼
- 自動從 .env 讀取認證資訊

**連接實驗室 Level2 攝影機**
```robotframework
Given 連接實驗室 Level2 攝影機
```
- 用途：連接到實驗室 Level 2 監控攝影機
- IP: 192.168.165.127

**連接實驗室馬達區攝影機**
```robotframework
Given 連接實驗室馬達區攝影機
```
- 用途：連接到實驗室馬達區監控攝影機
- IP: 10.42.0.39

**連接指定環境攝影機**
```robotframework
Given 連接指定環境攝影機    laboratory    level1
```
- 參數:
  - environment: 環境名稱 (laboratory, rv_vehicle)
  - camera_name: 攝影機名稱 (level1, level2, motor)
- 支援多環境配置切換

#### 影像擷取關鍵字

**取得當前燈光亮度**
```robotframework
${亮度} =    取得當前燈光亮度
Log    當前亮度: ${亮度}
```
- 回傳值：亮度數值 (0-255)
- 自動擷取影像並計算平均亮度
- 可配置分析區域 (中心/全圖)

**擷取影像**
```robotframework
${影像} =    擷取影像
${影像} =    擷取影像    /live1    # 使用次串流
```
- 參數：串流路徑 (可選)
- 回傳：影像陣列
- 支援主串流 (/live0) 和次串流 (/live1)

**儲存當前攝影機影像**
```robotframework
儲存當前攝影機影像    /tmp/screenshot.jpg
```
- 參數：檔案儲存路徑
- 格式：支援 JPG, PNG
- 自動創建目錄

#### 狀態判定關鍵字

**驗證燈光為開啟狀態**
```robotframework
Then 驗證燈光為開啟狀態
```
- 擷取影像並判定燈光狀態
- 若燈光未開啟則測試失敗
- 預設閾值: 150 (可配置)

**驗證燈光為關閉狀態**
```robotframework
Then 驗證燈光為關閉狀態
```
- 擷取影像並判定燈光狀態
- 若燈光未關閉則測試失敗
- 預設閾值: 50 (可配置)

**檢查燈光狀態並記錄**
```robotframework
${狀態} =    檢查燈光狀態並記錄
Log    亮度: ${狀態}[brightness]
Log    開啟: ${狀態}[is_on]
```
- 回傳：包含完整狀態資訊的字典
- 包含：亮度、開/關狀態、閾值、時間戳記等

#### 亮度驗證關鍵字

**亮度應該大於指定值**
```robotframework
Then 亮度應該大於指定值    150
```
- 驗證當前亮度大於指定值
- 測試失敗會顯示實際亮度

**亮度應該小於指定值**
```robotframework
Then 亮度應該小於指定值    50
```
- 驗證當前亮度小於指定值

**亮度應該在範圍內**
```robotframework
Then 亮度應該在範圍內    100    200
```
- 參數：最小亮度、最大亮度
- 驗證亮度在指定範圍內

#### 等待機制關鍵字

**等待燈光開啟**
```robotframework
When 等待燈光開啟    timeout=30    check_interval=1.0
```
- 參數:
  - timeout: 最長等待時間（秒），預設 30
  - check_interval: 檢查間隔（秒），預設 1.0
- 在時限內等待燈光變為開啟狀態

**等待燈光關閉**
```robotframework
When 等待燈光關閉    timeout=30
```
- 在時限內等待燈光變為關閉狀態
- 超時則測試失敗

**比較兩次亮度變化**
```robotframework
${變化} =    比較兩次亮度變化    delay=2.0
Log    亮度變化: ${變化}[difference]
```
- 參數：delay - 兩次測量間隔（秒）
- 回傳：包含兩次亮度和變化量的字典

**取得環境燈光亮度**
```robotframework
${brightness} =    When 取得環境燈光亮度    light_one
```
- 參數：light_id - 燈光 ID (定義於 YAML)
- 回傳：亮度數值 (float)
- 用途：取得指定燈光的當前亮度值，用於後續比較

**驗證亮度變化**
```robotframework
Then 驗證亮度變化    ${before}    ${after}    increase    10
Then 驗證亮度變化    ${before}    ${after}    decrease    10
# 支援中文參數
Then 驗證亮度變化    ${before}    ${after}    增加    10
Then 驗證亮度變化    ${before}    ${after}    減少    10
# 支援符號參數
Then 驗證亮度變化    ${before}    ${after}    +    10
Then 驗證亮度變化    ${before}    ${after}    -    10
```
- 參數：
  - before_brightness: 變化前亮度
  - after_brightness: 變化後亮度
  - expected_change: 預期變化方向 (increase/decrease/增加/減少/+/-)
  - min_delta: 最小變化量 (預設 10.0)
- 用途：驗證亮度是否發生顯著變化，適用於相對亮度檢查 (解決絕對閾值不準確問題)

#### 完整測試範例

```robotframework
*** Settings ***
Resource    ../../resources/ipcam_keywords.robot

*** Test Cases ***
完整燈光檢測流程
    [Documentation]    測試 IP Camera 燈光檢測的完整流程
    [Tags]    ipcam    light_detection    integration

    # 連接攝影機
    Given 連接實驗室 Level1 攝影機

    # 檢查初始狀態
    When 取得當前燈光亮度
    Then 驗證燈光為開啟狀態

    # 儲存截圖
    And 儲存當前攝影機影像    /tmp/initial_state.jpg

    # 詳細狀態記錄
    ${狀態} =    檢查燈光狀態並記錄
    Should Be True    ${狀態}[is_on]

    # 驗證亮度範圍
    And 亮度應該在範圍內    100    255
```

#### 整合測試範例（搭配 SwitchBot）

```robotframework
*** Test Cases ***
自動化燈光控制驗證
    [Documentation]    整合 SwitchBot 和 IP Camera 進行端到端測試
    [Tags]    integration    switchbot    ipcam

    # 確保初始狀態
    Given 智慧插座應為關閉狀態
    And 連接實驗室 Level1 攝影機
    And 驗證燈光為關閉狀態

    # 開啟電源並驗證
    When 開啟智慧插座
    And 等待 3 秒鐘
    Then 等待燈光開啟    timeout=10
    And 驗證燈光為開啟狀態
    And 儲存當前攝影機影像    /tmp/light_on.jpg

    # 關閉電源並驗證
    When 關閉智慧插座
    And 等待 3 秒鐘
    Then 等待燈光關閉    timeout=10
    And 驗證燈光為關閉狀態
    And 儲存當前攝影機影像    /tmp/light_off.jpg
```

### 技術架構

**RTSP 連線優化**:
- TCP 傳輸協議（提高穩定性）
- HEVC/H.265 編碼支援
- FFmpeg 後端自動配置
- 最小緩衝延遲（1 幀）

**亮度計算算法**:
```python
# 灰階轉換 → 區域選擇 → 平均值計算
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
brightness = float(np.mean(gray[center_region]))
```

**配置系統**:
- `.env` 統一認證管理
- YAML 多環境配置
- 可配置閾值和參數

### 測試狀態

**已驗證的攝影機**:
- ✅ level1 (192.168.165.184) - 1620×2592
- ✅ level2 (192.168.165.127) - 1620×2592
- ✅ motor (10.42.0.39) - 1620×2592

**成功率**: 3/3 (100%)

### 相關文檔

- **完整 API 文檔**: `libraries/ipcam_light_detection/README.md`
- **安裝指南**: `docs/ipcam_setup_guide.md`
- **快速開始**: `docs/ipcam_quick_start.md`
- **測試案例**: `tests/ipcam_testing/ipcam_light_detection_test.robot`
- **模組摘要**: `docs/ipcam_module_summary.md`

---

## 🤖 機器手臂視覺檢測關鍵字 (v4.0.0 - BDD 風格)

> ⚠️ **版本說明**: 本節為 v4.0.0（2025-11-18）最新版本，使用 BDD Given-When-Then 結構和本機化視覺檢測。
>
> 📌 **舊版本說明**: 如需查看 v1.0.0-v3.0.0 的舊式關鍵字（已棄用），請參考文件末尾的「歷史版本關鍵字」章節。

### 📋 模組資訊

- **庫名稱**: `RobotArmKeywords`
- **版本**: v4.0.0（本機化視覺檢測）
- **控制方式**: Socket 控制 + 本機視覺分析
- **支援型號**: MyCobot 280
- **總關鍵字數**: 32+ 個 BDD 中文關鍵字
- **關鍵字結構**: Given-When-Then（Gherkin 風格）
- **配置系統**:
  - 環境配置: `config/robot_arm/environment_config.py`
  - 台北實驗室: `config/robot_arm/taipei_lab_buttons.yaml`
  - 桃園實驗室: `config/robot_arm/taoyuan_lab_buttons.yaml`
  - RV Car: `config/robot_arm/rv_car_buttons.yaml`
- **測試案例**:
  - 基礎測試: `tests/robot_arm/basic_button_test.robot`
  - 多環境測試: `tests/robot_arm/multi_environment_test.robot`
  - 按壓反饋: `tests/robot_arm/button_press_feedback_test.robot`
  - 亮度檢測: `tests/robot_arm/brightness_level_test.robot`
- **設計文檔**:
  - 技術規格: `docs/vision_detection_local_spec.md`
  - 關鍵字設計: `docs/keyword_design_guidelines.md`
  - 快速上手: `docs/vision_detection_quick_start_guide.md`
- **最後更新**: 2025-11-18

### 🎯 使用說明

**v4.0.0 核心特性：**
- ✅ **本機化視覺檢測** - 影像分析在本機端執行，Server 只提供影像截取
- ✅ **雙影像源支援** - Socket（機器手臂 USB Camera）+ RTSP（IP Camera）
- ✅ **多環境配置** - 支援 3 個測試環境（Taipei LAB / Taoyuan LAB / RV Car）
- ✅ **8 種顏色檢測** - 藍/白/紅/綠/黃/橙/紫/關（HSV 色彩空間）
- ✅ **11 級亮度檢測** - 0-100%，10% 步進
- ✅ **BDD 中文關鍵字** - Given-When-Then 結構，完整中文命名

**使用前提：**
1. MyCobot 280 已開機並連接網路
2. Jetson Nano 上的 `robot_arm_server.py` 正在運行
3. 已選擇並設定測試環境（taipei_lab / taoyuan_lab / rv_car）
4. 按鈕已校準 ROI（Region of Interest）
5. 影像源已正確配置（Socket 或 RTSP）

### 📦 依賴安裝

```bash
pipenv install pymycobot pyyaml
```

### 🎯 BDD 關鍵字完整參考（RobotArmKeywords.py）

#### Given 關鍵字（前置條件）

| 關鍵字名稱 | 說明 |
|---|---|
| `Given 機器手臂已正確連接到控制面板` | 驗證 Socket 連線並回到初始位置，失敗則拋出 AssertionError |
| `Given 控制面板電源狀態為 "${power_state}"` | 設定測試的電源狀態前提（"on"/"off"） |
| `Given 機器手臂系統處於待命狀態` | 確認系統已連線且位於初始位置 |
| `Given 測試環境設定為 "${environment}"` | 載入指定環境的所有按鈕配置（taipei_lab / taoyuan_lab / rv_car） |
| `Given 面板類型設定為 "${panel_type}"` | 設定面板類型，用於篩選按鈕配置子集 |
| `Given 環境 IP Camera 已完成預熱連接` | 確認 RTSP IP Camera 連線就緒並完成暖機 |
| `Given 按鈕 "${button_id}" 的狀態應為 "${expected_state}"` | 以視覺方式驗證按鈕初始狀態（前置條件用） |

#### When 關鍵字（執行動作）

| 關鍵字名稱 | 說明 |
|---|---|
| `When 用戶透過機器手臂開啟第 "${light_number}" 號燈光` | 移動到對應燈光按鈕並執行點擊動作 |
| `When 用戶透過機器手臂切換藍牙連接` | 點擊藍牙按鈕 |
| `When 用戶透過機器手臂啟動 "${device_name}" 設備` | 依設備名稱找到對應按鈕並點擊 |
| `When 用戶透過機器手臂長按 "${button_type}" 按鈕 "${seconds}" 秒` | 長按指定按鈕 N 秒（如 Retract/Extend） |
| `When 用戶檢測面板按鈕 "${button_id}" 的顏色` | 拍攝 ROI 並返回 HSV 顏色分析結果 |
| `When 用戶檢測環境燈光亮度 "${light_id}"` | 透過 RTSP IP Camera 量測環境燈光亮度百分比 |
| `When 用戶檢測第 "${button_id}" 按鈕的燈光狀態` | 取得按鈕 LED 顏色（Socket 影像源） |
| `When 用戶檢測多個按鈕的燈光狀態` | 批次檢測多個按鈕並回傳結果字典 |
| `When 用戶等待按鈕 "${button_id}" 變為 "${expected_color}" 色` | 持續檢測直到按鈕顯示目標顏色或逾時 |
| `When 用戶連接到機器手臂` | 建立 Socket 連線（含預設主機/端口） |
| `When 用戶中斷與機器手臂的連接` | 斷開 Socket 連線並釋放資源 |
| `When 用戶按壓第 "${button_id}" 按鈕` | 原子化按壓（down→wait→up）單次 |
| `When 用戶按壓第 "${button_id}" 按鈕持續 "${duration}" 秒` | 原子化長按指定秒數 |

#### Then 關鍵字（驗證結果）

| 關鍵字名稱 | 說明 |
|---|---|
| `Then 機器手臂操作應該成功完成` | 驗證上一步操作回傳 True，失敗則拋出 AssertionError |
| `Then 控制面板應該顯示 "${expected_state}" 狀態` | 驗證面板整體狀態符合預期 |
| `Then 面板按鈕顏色應該為 "${expected_color}"` | 驗證最後一次按鈕顏色檢測結果符合預期 |
| `Then 環境燈光亮度應該為 "${expected_level}" %` | 驗證 IP Camera 亮度量測值符合預期百分比 |
| `Then 環境燈光狀態應該為 "${expected_state}"` | 驗證環境燈光為 "亮" 或 "暗" |
| `Then 按鈕燈光應該為 "${expected_color}" 色` | 驗證 LED 顏色 (HSV 分析) |
| `Then 雙重驗證面板按鈕 "${button_id}" 狀態應為 "${expected_state}"` | 以 HSV + YOLO 雙重驗證按鈕狀態 |
| `Then 上一步操作應該成功` | 驗證最後操作結果為成功 |
| `Then 驗證面板燈光狀態` | 批次驗證多個按鈕燈光狀態 |
| `Then 按鈕 "${button_id}" 的狀態應為 "${expected_state}"` | 視覺狀態驗證 (v4.3.0)，支援 Given/When/Then/And 前綴 |
| `YOLO 應該檢測到按鈕 "${button_id}" 為 "${expected_state}"` | 僅用 YOLO 模型驗證按鈕物理狀態 |
| `YOLO 僅檢測並儲存按鈕影像 "${button_id}" 預期狀態 "${expected_state}"` | 執行 YOLO 檢測並儲存標註影像（除錯/採樣用） |

#### And 關鍵字（附加驗證）

| 關鍵字名稱 | 說明 |
|---|---|
| `And 機器手臂應該返回待命位置` | 驗證手臂已歸位到初始角度 |
| `And 系統應該記錄完整操作歷程` | 驗證日誌已包含本次操作記錄 |
| `And 暫存檔案應該正確清理` | 驗證 output/debug_images/ 暫存影像已清除 |
| `And 按鈕 "${button_id}" 的狀態應為 "${expected_state}"` | 附加狀態驗證（與 Then 版本等效） |

#### 工具型關鍵字（無 BDD 前綴）

| 關鍵字名稱 | 說明 |
|---|---|
| `取得最後檢測結果` | 回傳最後一次單按鈕視覺檢測的完整結果字典 |
| `取得批次檢測結果` | 回傳最後一次批次按鈕檢測的結果列表 |
| `取得按鈕對應的環境燈光 ID` | 依按鈕 ID 查詢其對應的環境燈光 ID（YAML 配置） |
| `移動到面板觀測位置` | 移動手臂到全局面板觀測角度，適合批次拍攝 |
| `比較完整反饋結果` | 比對目前批次檢測結果與預期字典，輸出差異報告 |
| `取得關節移動統計` | 回傳 6 個關節累積移動度數列表（維護分析用） |
| `重置關節移動統計` | 清除所有關節移動累計數據 |
| `記錄關節移動統計` | 將關節移動統計寫入測試日誌（Robot Framework logger） |
| `Get YOLO Detection Status` | 取得 YOLO 檢測狀態字典，不拋出例外，適合條件判斷 |
| `若 YOLO 檢測到按鈕 "${button_id}" 為 "${target_state}" 則點擊喚醒` | 條件式喚醒：若按鈕狀態符合目標才執行點擊 |
| `移動機器手臂到指定角度` | 直接移動到 6 軸指定角度陣列，用於輔助定位 |
| `拍攝並儲存影像` | 拍攝當前影像並儲存到 `output/debug_images/`（含時間戳記） |

**Gherkin 範例（完整 BDD 測試案例）**:
```robotframework
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

*** Test Cases ***
驗證 Light1 按鈕開啟狀態
    Given 測試環境設定為    taipei_lab
    And 機器手臂已正確連接到控制面板
    And 環境 IP Camera 已完成預熱連接
    When 用戶透過機器手臂開啟第 "light1" 號燈光
    And 用戶檢測第 "light1" 按鈕的燈光狀態
    Then 按鈕燈光應該為 "blue" 色
    And 環境燈光狀態應該為 "亮"
    And 系統應該記錄完整操作歷程
    And 機器手臂應該返回待命位置
```

### 🔌 連接管理關鍵字 (3個)

#### 連接機器手臂

**用途**: 連接到機器手臂並開啟電源

**參數**:
- `host` (可選): 機器手臂 IP 地址，預設從配置文件讀取
- `port` (可選): Socket 端口，預設從配置文件讀取

**使用範例**:
```robotframework
# 使用配置文件中的 IP 和端口
連接機器手臂

# 使用指定 IP
連接機器手臂    192.168.1.100

# 指定 IP 和端口
連接機器手臂    192.168.1.100    9000
```

#### 斷開機器手臂連接

**用途**: 斷開與機器手臂的連接

**使用範例**:
```robotframework
斷開機器手臂連接
```

#### 回到初始位置

**用途**: 移動機器手臂到初始位置 [0, 0, 0, 0, 0, 0]

**參數**:
- `speed` (可選): 移動速度 (1-100)，預設 30

**使用範例**:
```robotframework
# 使用預設速度 30
回到初始位置

# 使用速度 50
回到初始位置    50
```

### 🔘 點擊按鈕關鍵字 (18個)

所有點擊按鈕關鍵字無需參數，直接調用即可。

#### 藍牙與控制按鈕
- **點擊藍牙按鈕** - 控制藍牙功能
- **點擊AUX1按鈕** - 輔助控制 1
- **點擊AUX2按鈕** - 輔助控制 2
- **點擊Select按鈕** - 選擇按鈕

#### 燈光控制按鈕 (8個)
- **點擊Light1按鈕** - 燈光控制 1
- **點擊Light2按鈕** - 燈光控制 2
- **點擊Light3按鈕** - 燈光控制 3
- **點擊Light4按鈕** - 燈光控制 4
- **點擊Light5按鈕** - 燈光控制 5
- **點擊Light6按鈕** - 燈光控制 6
- **點擊Light7按鈕** - 燈光控制 7
- **點擊Light8按鈕** - 燈光控制 8

#### 門鎖控制
- **點擊DoorLock按鈕** - 門鎖控制

#### 電器控制按鈕
- **點擊TankerHeater按鈕** - 水箱加熱器控制
- **點擊Gas按鈕** - 瓦斯控制
- **點擊WaterPump按鈕** - 水泵控制
- **點擊WaterHeater按鈕** - 熱水器控制
- **點擊HVAC按鈕** - 空調控制

**使用範例**:
```robotframework
*** Test Cases ***
測試燈光控制
    連接機器手臂
    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕
    斷開機器手臂連接
```

### ⏱️ 長按按鈕關鍵字 (2個)

⚠️ **注意**: 目前長按功能僅 Retract 和 Extend 按鈕配置為長按，未來會擴展到其他按鈕。

#### 長按Retract按鈕

**用途**: 長按 Retract（縮回）按鈕

**參數**:
- `秒數` (可選): 按壓時間，預設 7 秒

**使用範例**:
```robotframework
# 使用預設 7 秒
長按Retract按鈕

# 自定義按壓時間 10 秒
長按Retract按鈕    10

# 使用命名參數
長按Retract按鈕    秒數=10
```

#### 長按Extend按鈕

**用途**: 長按 Extend（伸展）按鈕

**參數**:
- `秒數` (可選): 按壓時間，預設 7 秒

**使用範例**:
```robotframework
# 使用預設 7 秒
長按Extend按鈕

# 自定義按壓時間 10 秒
長按Extend按鈕    10

# 使用命名參數
長按Extend按鈕    秒數=10
```

### 📝 完整測試範例

```robotframework
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

Suite Setup      連接機器手臂
Suite Teardown   清理並斷開連接

*** Test Cases ***
測試完整面板操作
    [Documentation]    測試所有面板按鈕功能
    [Tags]    full_panel    regression

    # 測試藍牙控制
    點擊藍牙按鈕
    點擊AUX1按鈕
    點擊AUX2按鈕

    # 測試燈光控制
    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕

    # 測試門鎖
    點擊DoorLock按鈕

    # 測試長按功能
    長按Retract按鈕
    長按Extend按鈕    10

*** Keywords ***
清理並斷開連接
    回到初始位置
    斷開機器手臂連接
```

### 🎛️ 按鈕配置

所有按鈕位置配置存放在 `config/robot_arm/button_positions.yaml`：

```yaml
connection:
  socket:
    host: "172.20.10.14"  # MyCobot 280 的 IP 地址
    port: 9000            # Socket 端口

defaults:
  speed: 100
  press_duration: 1.0
  lift_duration: 0.1

buttons:
  bluetooth:
    name: "Bluetooth 按鈕"
    down_angles: [16.5, -51, -130, 73.7, 0, 0]
    up_angles: [16.5, -13, -130, 73.7, 0, 0]
    speed: 100
    # ... 更多按鈕配置
```

### 🔧 故障排除

#### 連接失敗
```
ConnectionError: 無法連接到機器手臂 172.20.10.14:9000
```
**解決方法**:
1. 確認機器手臂電源已開啟
2. 檢查 MyCobot 280 Jetson Nano 上的 Server_280.py 是否運行
3. 驗證 IP 地址和端口配置
4. 測試網路連接: `ping 172.20.10.14`

#### 角度讀取失敗
```
RuntimeError: 連接測試失敗: 無法讀取角度資料
```
**解決方法**:
1. 重啟 Server_280.py
2. 重啟機器手臂
3. 檢查 USB 連接（MyCobot 280 Jetson Nano 端）

#### 移動超時
```
RuntimeError: 移動到初始位置超時
```
**解決方法**:
1. 檢查機器手臂是否有障礙物
2. 確認伺服馬達電源已開啟
3. 減慢移動速度

### 📚 相關文檔

- **完整設計文檔**: `docs/robot_arm_socket_control_design.md`
- **配置文件**: `config/robot_arm/button_positions.yaml`
- **核心控制器**: `libraries/robot_arm_control/mycobot_socket_controller.py`
- **配置載入器**: `libraries/robot_arm_control/button_config_loader.py`
- **關鍵字庫**: `libraries/robot_arm_control/RobotArmKeywords.py`
- **測試案例**: `tests/robot_arm/basic_button_test.robot`
- **MyCobot 官方文檔**: https://docs.elephantrobotics.com/

### 🚀 未來擴展

- [ ] 將長按功能擴展到更多按鈕
- [ ] 支援自定義按壓次數（重複點擊）
- [ ] 支援按壓力度調整
- [ ] 增加錯誤恢復機制
- [ ] 支援多機器手臂並行控制
- [ ] 整合視覺定位系統

---

**最後更新：** 2026年03月11日
**IP Camera 模組：** ✅ 已完成並測試通過
**機器手臂控制模組：** ✅ 已完成 Socket 控制系統
**Android 語音輸入模組：** ✅ 已完成（Stage 7 - IoT 語音控制場景）
**Android 裝置控制模組：** ✅ 已完成（Stage 4-6 - 藍牙/WiFi/飛航/音量/App 生命週期）
**Android 手勢控制模組：** ✅ 已完成（Stage 5 - 長按/滑動/點擊/雙擊/拖曳）
**總關鍵字數量：** 196個 (141個 Gherkin 中文 + 55個 Legacy)
**新增關鍵字：** 45個（23個裝置控制 + 10個手勢控制 + 8個語音輸入 + 4個 gesture resource）
**測試案例：** 45個 android-only BDD 測試（20個裝置控制 + 16個手勢 + 9個語音輸入）
**專案完成度：** 98% - Android 全平台測試整合完成

---

## 📱 跨平台裝置控制關鍵字（libraries/mobile_testing/DeviceControlKeywords.py）

此模組提供跨平台裝置控制關鍵字，透過 `resources/device_control_keywords.robot` 暴露為中文 BDD 關鍵字。

### 🎤 Stage 7：Android 語音輸入關鍵字（IoT 語音控制場景）

> **需求**：實體 Android 裝置 + Focusrite Scarlett 4i4 音訊硬體

| 關鍵字名稱 | BDD 前綴 | 說明 |
|---|---|---|
| `檢查音訊硬體就緒` | Given | 驗證 Scarlett 4i4 已連接且 PipeWire 路由已建立，未就緒立即拋出 RuntimeError 附帶診斷訊息 |
| `觸發系統語音搜尋` | When | 透過 ADB Intent 觸發系統級語音搜尋（備用方案，不依賴 App UI） |
| `點擊語音輸入按鈕` | When | 等待並點擊 App 內語音輸入按鈕，支援 accessibility_id / id / xpath 三種定位方式 |
| `觸發語音輸入並播放指令` | When | 完整語音觸發流程：硬體檢查 → 點擊按鈕 → 等待麥克風就緒（可配置延遲）→ 確認 UI → 播放語音指令（Scarlett 4i4） |
| `等待語音輸入結果` | When/Then | 等待 App UI 顯示語音辨識結果，返回辨識文字，逾時拋出 TimeoutError 附帶原因診斷 |
| `語音指令結果應包含` | Then | 驗證語音指令結果包含預期文字，不符拋出 AssertionError 附帶音量/距離調整建議 |

#### 使用範例

```robotframework
*** Settings ***
Resource    resources/device_control_keywords.robot

*** Test Cases ***
語音控制開啟客廳燈光
    Given 裝置控制已初始化    android
    And 音訊硬體已就緒
    When 使用者觸發語音輸入並播放指令
    ...    開啟客廳燈光    語音輸入    1    accessibility_id    1.5    2
    Then 語音指令結果應包含    燈光已開啟    com.example:id/tv_result    id    15
```

#### 語音觸發同步策略說明

```
觸發語音輸入並播放指令 執行流程：
┌─────────────────────────────────────────────────────────────────┐
│ 1. check_audio_hardware_ready()                                 │
│    └─ 驗證 Scarlett 4i4 + PipeWire（未就緒 → RuntimeError）      │
│ 2. click_voice_input_button(locator)                            │
│    └─ 等待按鈕出現並點擊（逾時 → TimeoutError）                   │
│ 3. time.sleep(mic_ready_delay)  # 預設 1.5 秒                  │
│ 4. _wait_for_voice_input_ui(voice_ui_locator)                   │
│    └─ 未出現 → 重試（max_retries 預設 2 次）→ TimeoutError        │
│ 5. VoiceControlKeywords.speak_text_to_channel(text, channel)    │
│    └─ 透過 Scarlett 4i4 播放語音指令                              │
└─────────────────────────────────────────────────────────────────┘
```

#### 相關資源

- **Python 實作**：`libraries/mobile_testing/android/AndroidDeviceControl.py`（Stage 7 方法）
- **Robot Framework 統一入口**：`libraries/mobile_testing/DeviceControlKeywords.py`
- **BDD 資源檔**：`resources/device_control_keywords.robot`
- **測試案例**：`tests/mobile/android/android_voice_input_test.robot`
- **語音硬體**：`libraries/voice_control/VoiceControlKeywords.py`（Scarlett 4i4 整合）

---

## 📱 裝置系統控制關鍵字（Stage 4–6：藍牙/WiFi/飛航/音量/App 生命週期）

> **更新日期**：2026-03-11（Stage 9–10 完成）

### BDD 資源檔關鍵字總覽（resources/device_control_keywords.robot）

| 關鍵字名稱 | BDD 前綴 | 說明 |
|---|---|---|
| `裝置控制已初始化` | Given | 初始化裝置控制模組（指定 android/ios 平台） |
| `藍牙已開啟` | Given | 確保藍牙為開啟狀態（前置條件） |
| `WiFi 已開啟` | Given | 確保 WiFi 為開啟狀態（前置條件） |
| `行動數據已關閉` | Given | 確保行動數據已關閉（前置條件） |
| `飛航模式已關閉` | Given | 確保飛航模式已關閉（前置條件） |
| `音訊硬體已就緒` | Given | 確認 Scarlett 4i4 + PipeWire 路由已建立 |
| `使用者開啟藍牙` | When | 透過 ADB 開啟藍牙（`bluetooth enable`） |
| `使用者關閉藍牙` | When | 透過 ADB 關閉藍牙 |
| `使用者開啟 WiFi` | When | 透過 ADB 開啟 WiFi |
| `使用者關閉 WiFi` | When | 透過 ADB 關閉 WiFi |
| `使用者開啟行動數據` | When | 透過 ADB 開啟行動數據（需 ioctl） |
| `使用者關閉行動數據` | When | 透過 ADB 關閉行動數據 |
| `使用者開啟飛航模式` | When | 透過 ADB settings put + Intent 廣播開啟飛航 |
| `使用者關閉飛航模式` | When | 透過 ADB 關閉飛航模式 |
| `使用者調高音量` | When | 按下 KEYCODE_VOLUME_UP 一次 |
| `使用者調低音量` | When | 按下 KEYCODE_VOLUME_DOWN 一次 |
| `使用者靜音` | When | 設定媒體音量為 0 |
| `使用者設定媒體音量為` | When | 設定媒體音量至指定值（0–15） |
| `使用者將應用程式置於背景` | When | 按下 HOME 鍵，可配置秒數後返回 |
| `使用者恢復應用程式` | When | 透過 package 重新啟動 App |
| `使用者從最近應用清除` | When | 開啟最近應用並向上滑動清除 |
| `使用者強制停止應用程式` | When | ADB force-stop 指定 package |

### Python Library 關鍵字（DeviceControlKeywords.py）

| 關鍵字名稱 | 類別 | 說明 |
|---|---|---|
| `初始化裝置控制` | Given | 平台初始化 |
| `開啟藍牙` / `關閉藍牙` | When | 藍牙控制 |
| `查詢藍牙狀態` | When | 回傳 on/off |
| `藍牙應該為開啟狀態` / `藍牙應該為關閉狀態` | Then | 藍牙驗證 |
| `開啟 WiFi` / `關閉 WiFi` | When | WiFi 控制 |
| `查詢 WiFi 狀態` | When | 回傳 on/off |
| `WiFi 應該為開啟狀態` / `WiFi 應該為關閉狀態` | Then | WiFi 驗證 |
| `開啟行動數據` / `關閉行動數據` | When | 行動數據控制 |
| `查詢行動數據狀態` | When | 回傳 on/off |
| `開啟飛航模式` / `關閉飛航模式` | When | 飛航模式控制 |
| `查詢飛航模式狀態` | When | 回傳 on/off |
| `飛航模式應該為開啟狀態` / `飛航模式應該為關閉狀態` | Then | 飛航驗證 |
| `調高音量` / `調低音量` / `靜音` | When | 音量控制 |
| `設定媒體音量` | When | 設定指定音量值 |
| `查詢媒體音量` | When | 回傳整數音量值（0–15） |
| `媒體音量應該為` | Then | 音量驗證 |
| `將應用程式置於背景` | When | App 置於背景 |
| `啟動應用程式` | When | 啟動指定 package |
| `從最近應用清除` | When | 從最近應用清除 App |
| `強制停止應用程式` | When | 強制停止 App |
| `前景應用程式應該為` | Then | 驗證前景 App |
| `前景應用程式不應該為` | Then | 驗證非前景 App |
| `查詢前景應用程式` | When | 回傳前景 package 名稱 |

### 相關測試案例
- `tests/mobile/android/android_device_control_test.robot`（20 個 BDD 測試案例，全部 `android-only`）

---

## 🖐️ 進階手勢控制關鍵字（libraries/mobile_testing/GestureControlKeywords.py）

> **更新日期**：2026-03-11（Stage 9–10 完成）

### BDD 資源檔關鍵字（resources/gesture_control_keywords.robot）

| 關鍵字名稱 | BDD 前綴 | 說明 |
|---|---|---|
| `手勢控制已初始化` | Given | 初始化手勢控制模組（指定 android/ios 平台） |
| `使用者長按元素` | When | 透過元素定位器執行長按（`mobile: longClickGesture`），可配置持續時間（ms） |
| `使用者長按座標` | When | 透過 (x, y) 座標執行長按，可配置持續時間 |
| `使用者滑動螢幕` | When | 依方向（up/down/left/right）滑動整個螢幕，可配置距離百分比 |
| `使用者在區域內滑動` | When | 在指定矩形區域（left/top/width/height）內精確滑動 |
| `使用者點擊座標` | When | 透過 `mobile: clickGesture` 精確點擊指定座標 |
| `使用者雙擊元素` | When | 對元素執行雙擊（`mobile: doubleClickGesture`） |
| `使用者拖曳元素到座標` | When | 將元素拖曳至目標座標（`mobile: dragGesture`），可配置速度 |
| `元素應該被長按` | Then | 長按操作驗證（呼叫尚未實作的 App 層驗證） |
| `元素應該被拖曳到座標` | Then | 拖曳操作驗證 |

### Python Library 關鍵字（GestureControlKeywords.py）

| 關鍵字名稱 | 說明 |
|---|---|
| `初始化手勢控制` | 依平台初始化 AndroidGestureControl / IOSGestureControl |
| `長按元素` | locator + duration(ms) |
| `長按座標` | x, y, duration(ms) |
| `滑動螢幕` | direction, percent |
| `在區域內滑動` | left, top, width, height, direction, percent |
| `點擊座標` | x, y |
| `雙擊元素` | locator |
| `拖曳元素` | locator, end_x, end_y, speed(ms)=1000 |

### 相關測試案例
- `tests/mobile/android/android_gesture_test.robot`（16 個 BDD 測試案例，全部 `android-only`）


---

## 🔊 本機語音驗證關鍵字（libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py）

> **更新日期**：2026-03-27

此模組提供「PC 播放語音 → 麥克風錄音 → 聲音特徵比對」的完整流程，用於驗證設備對喚醒詞的回應聲音。

### 引用方式
```robotframework
Library    ../libraries/local_voice_verifying/LocalVoiceVerifyingLibrary.py
```

### Python Library 關鍵字

| 關鍵字名稱 | 參數 | 說明 |
|---|---|---|
| `Speak And Detect` | `text`, `target_sound`, `duration=10` | 播放文字語音並同時錄音，比對是否檢測到目標聲音；回傳 True/False |
| `Start Voice Recording` | `duration=10` | 開始後台錄音，持續指定秒數 |
| `Stop Voice Recording` | — | 停止後台錄音並儲存音訊緩衝 |
| `Detect Target Sound` | `target_sound`, `threshold=0.7` | 比對已錄製的音訊是否包含目標聲音；回傳 True/False |
| `Get Detection Result` | — | 取得最後一次偵測結果（字典：sound、detected、confidence、timestamp） |
| `Set Detection Threshold` | `threshold` | 設定聲音比對的信心度閾值（0.0–1.0，預設 0.7） |
| `Load Reference Sound` | `sound_name` | 從 `libraries/local_voice_verifying/reference_sounds/` 載入參考聲音樣本 |
| `Set TTS Language` | `language` | 設定 TTS 語言（如 "zh-TW"、"en"） |
| `Set TTS Speed` | `speed` | 設定 TTS 語速（0.5–2.0，1.0 為正常） |
| `Speak Text` | `text`, `language=None` | 使用 gTTS 播放文字（不錄音） |
| `Cleanup Audio Resources` | — | 釋放所有音訊資源（錄音流、TTS 引擎） |

### 使用範例
```robotframework
*** Test Cases ***
驗證設備回應喚醒詞
    Load Reference Sound    登登
    Set Detection Threshold    0.75
    ${result}=    Speak And Detect    Hey Power Pro    登登    10
    Should Be True    ${result}    msg=未偵測到目標聲音「登登」
    ${detail}=    Get Detection Result
    Log    信心度：${detail}[confidence]
    [Teardown]    Cleanup Audio Resources
```

---

## 🤖 多感官檢測關鍵字（libraries/multimodal_detection/VoiceAssistantDetection.py）

> **更新日期**：2026-03-27

整合語音播放（VoiceControlKeywords）、IP Camera 視覺檢測（IPCamLightDetection）與 UART 日誌監控（SerialLogParser），提供語音助手多感官回應的一站式驗證。

### Python Library 關鍵字

| 關鍵字名稱 | 參數 | 說明 |
|---|---|---|
| `測試語音助理回應` | `wake_word`, `camera_env`, `camera_name`, `uart_port=None`, `uart_baudrate=115200`, `scarlett_channel=1`, `detection_timeout=10`, `require_both=True` | 執行完整的多感官回應測試：播放喚醒詞 → 同時偵測視覺亮度變化與 UART 日誌；回傳結果字典 |

**回傳字典欄位**：
- `overall_success` (bool)：整體測試是否通過
- `vision_detected` (bool)：視覺偵測是否成功
- `audio_detected` (bool)：聽覺（UART）偵測是否成功
- `vision_details` (str)：視覺檢測詳情
- `audio_details` (str)：聽覺檢測詳情
- `failure_reason` (str)：失敗原因摘要

### BDD 資源檔關鍵字（resources/voice_assistant_keywords.robot）

| 關鍵字名稱 | 類型 | 說明 |
|---|---|---|
| `測試語音助手完整回應` | When | 呼叫 `測試語音助理回應`，包裝成 BDD 風格；參數：喚醒詞、環境、攝影機、參考聲音（預設「登登」）、超時（預設 10 秒） |
| `驗證語音助手完整回應成功` | Then | 驗證結果字典中 vision_detected、audio_detected、overall_success 均為 True |
| `驗證視覺和聽覺都有回應` | Then | `驗證語音助手完整回應成功` 的別名關鍵字 |
| `記錄檢測詳細資料` | And | 將結果字典格式化輸出至測試日誌（視覺/聽覺/綜合判定） |
| `驗證檢測結果符合預期` | Then | 驗證結果字典中 vision_detected 和 audio_detected 是否符合預期布林值 |
| `設定檢測參數` | Given | 以 Suite Variable 設定環境、攝影機、參考聲音、超時等參數 |
| `等待語音助手恢復` | And | Sleep 指定秒數（預設 5 秒），等待語音助手回到待命狀態 |
| `清理檢測資源` | （Teardown） | 清理測試使用的資源（日誌記錄） |

**使用範例**:
```robotframework
*** Settings ***
Resource    resources/voice_assistant_keywords.robot

*** Test Cases ***
驗證語音助手對喚醒詞的完整回應
    Given 設定檢測參數    laboratory    level1    登登    10
    When 測試語音助手完整回應    Hey Power Pro    laboratory    level1
    Then 驗證語音助手完整回應成功    ${結果}
    And 記錄檢測詳細資料    ${結果}
    [Teardown]    清理檢測資源
```

---

## 📱 Appium 自訂擴充關鍵字（libraries/mobile_testing/common/CustomAppiumKeywords.py）

> **更新日期**：2026-03-27

封裝 Appium AppiumLibrary 的常用操作，並加入詳細的日誌記錄與錯誤處理，提供比原生 AppiumLibrary 更豐富的診斷資訊。

### 引用方式
```robotframework
Library    ../libraries/mobile_testing/common/CustomAppiumKeywords.py
```

### 關鍵字清單

| 關鍵字名稱 | 參數 | 說明 |
|---|---|---|
| `Open Application` | `remote_url`, `**desired_caps` | 開啟 Appium 連線並啟動 App（含詳細 capability 日誌） |
| `Close Application` | — | 關閉目前 Appium Session（含日誌） |
| `Click Element` | `locator` | 點擊元素（附記錄定位器與操作結果日誌） |
| `Input Text` | `locator`, `text` | 清除後輸入文字至元素 |
| `Get Text` | `locator` | 取得元素文字內容；回傳 str |
| `Element Should Be Visible` | `locator`, `message=None` | 驗證元素可見；不可見則拋出 AssertionError |
| `Wait Until Element Is Visible` | `locator`, `timeout=10` | 等待元素可見（最多 timeout 秒） |
| `Swipe` | `start_x`, `start_y`, `end_x`, `end_y`, `duration=1000` | 執行滑動手勢（ms 單位） |
| `Scroll Down` | `locator=None`, `duration=1000` | 向下滾動（可指定元素或螢幕整體） |
| `Scroll Up` | `locator=None`, `duration=1000` | 向上滾動 |
| `Take Screenshot` | `filename=None` | 擷取螢幕截圖並儲存（回傳路徑） |
| `Get Current Activity` | — | 取得目前 Android Activity 名稱（Android 專用） |

### 使用範例
```robotframework
*** Test Cases ***
基本 App 互動測試
    Open Application    http://localhost:4723    platformName=Android    app=/path/to/app.apk
    Wait Until Element Is Visible    accessibility_id=LoginButton    15
    Click Element    accessibility_id=LoginButton
    Input Text    id=username    testuser
    ${text}=    Get Text    id=greeting
    Element Should Be Visible    id=dashboard
    Take Screenshot    login_success
    Close Application
```

---

## 🖥️ 系統維護關鍵字（libraries/system_maintenance/DiskManagementKeywords.py）

> **更新日期**：2026-03-27（首次建立完整文件，功能於 v5.5.5 新增）

提供磁碟空間監控與 Debug 圖片清理功能，防止測試執行過程中 `output/debug_images/` 目錄佔用過多磁碟空間。

### 引用方式
```robotframework
Library    ../libraries/system_maintenance/DiskManagementKeywords.py
```

### 關鍵字清單

| 關鍵字名稱 | BDD 前綴 | 參數 | 說明 |
|---|---|---|---|
| `Given 磁碟剩餘空間應大於 '${size_mb}' MB` | Given | `size_mb` (int) | 取得磁碟可用空間（MB），若低於閾值則拋出 AssertionError，確保測試啟動前有足夠空間 |
| `When 清理超過 '${days}' 天前的 Debug 圖片` | When | `days` (int) | 刪除 `output/debug_images/` 中修改時間超過 N 天的圖片，回傳刪除檔案數 |
| `When 保留最新的 '${count}' 張 Debug 圖片` | When | `count` (int) | 依修改時間排序，僅保留最新 N 張圖片，刪除其餘，回傳刪除檔案數 |

### 使用範例
```robotframework
*** Settings ***
Library    ../libraries/system_maintenance/DiskManagementKeywords.py

*** Test Cases ***
機器手臂測試前磁碟健康檢查
    Given 磁碟剩餘空間應大於 '500' MB
    When 清理超過 '7' 天前的 Debug 圖片
    And 保留最新的 '100' 張 Debug 圖片
```

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

