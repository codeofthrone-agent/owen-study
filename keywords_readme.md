# Robot Framework 關鍵字說明文件 - Gherkin 風格 (最新更新)

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

**Given 關鍵字（前置條件）- 4 個:**
- `Given 測試環境設定為 "${environment}"` - 設定測試環境（taipei_lab / taoyuan_lab / rv_car）
- `Given 面板類型設定為 "${panel_type}"` - 設定面板類型（3510a / 3611a / 3611c）
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
- **詳細說明**: 100% 覆蓋  
- **使用範例**: 100% 覆蓋
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
- **Given 音訊輸出聲道 "${channel}" 已準備就緒** - 確認指定音訊輸出聲道已準備就緒 (含路由驗證) (1-4)
- **Given UART 日誌監控器已初始化** - 初始化 UART 監控器用於檢測語音回應 (v1.2.0 新增)

#### When Keywords (執行動作)
- **When 使用者播放文字 "${text}" 到聲道 "${channel}"** - 使用者播放文字到指定聲道
- **When 使用者播放文字 "${text}" 到聲道 "${channel}" 使用語言 "${language}"** - 使用者播放文字到指定聲道使用指定語言
- **When 使用者切換 TTS 引擎到 "${engine_name}"** - 使用者切換 TTS 引擎到指定引擎
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
2. **voice_control (VoiceControlKeywords.py)**: 26個純 Gherkin 中文關鍵字 (v1.2.0 - 含 UART 監控功能)

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

**最後更新：** 2025年11月06日
**IP Camera 模組：** ✅ 已完成並測試通過
**機器手臂控制模組：** ✅ 已完成 Socket 控制系統
**總關鍵字數量：** 138個 (93個 Gherkin 中文 + 45個 Legacy)
**新增關鍵字：** 23個機器手臂控制關鍵字
**專案完成度：** 92% - 機器手臂 Socket 控制系統全面完成
