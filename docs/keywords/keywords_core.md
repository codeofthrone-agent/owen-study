# 核心通用關鍵字文件

> 索引文件：[keywords_readme.md](../../keywords_readme.md)
> 
> 涵蓋模組：common_keywords、web_keywords、api_keywords、ipcam_keywords、DiskManagementKeywords
> 
> 最後更新：2026-03-27

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
- **安裝指南**: `../ipcam/ipcam_setup_guide.md`
- **快速開始**: `../ipcam/ipcam_quick_start.md`
- **測試案例**: `tests/ipcam_testing/ipcam_light_detection_test.robot`
- **模組摘要**: `../ipcam/ipcam_module_summary.md`

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

