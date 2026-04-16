# 機器手臂視覺檢測關鍵字文件

> 索引文件：[keywords_readme.md](../../keywords_readme.md)
> 
> 最後更新：2026-03-27

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
- `../robot_arm_vision/vision_detection_local_spec.md` - 技術規格書
- `../robot_arm_vision/vision_detection_tdd_guide.md` - TDD 開發指南
- `../robot_arm_vision/vision_detection_quick_start_guide.md` - 快速上手指南
- `../keyword_design_guidelines.md` - BDD 關鍵字設計規範

**版本歷程:**
- v1.0.0 (2025-11-05): 基礎 Socket 控制
- v2.0.0 (2025-11-10): ArUco 標記檢測
- v3.0.0 (2025-11-13): Server-side 視覺檢測
- v4.0.0 (2025-11-18): 本機化視覺檢測
- v4.1.0 (2025-01-21): 伺服器端 YOLO 狀態驗證
- **v5.5.5 (2026-01-27): 關節移動追蹤與維護分析 ← 當前版本**

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
  - 技術規格: `../robot_arm_vision/vision_detection_local_spec.md`
  - 關鍵字設計: `../keyword_design_guidelines.md`
  - 快速上手: `../robot_arm_vision/vision_detection_quick_start_guide.md`
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

- **完整設計文檔**: `../robot_arm_vision/robot_arm_socket_control_design.md`
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

