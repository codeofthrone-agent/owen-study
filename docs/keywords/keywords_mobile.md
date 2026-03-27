# Mobile / Appium / SwitchBot 關鍵字文件

> 索引文件：[keywords_readme.md](../../keywords_readme.md)
> 
> 涵蓋模組：mobile_keywords、switchbot_keywords、DeviceControlKeywords、GestureControlKeywords、CustomAppiumKeywords
> 
> 最後更新：2026-03-27

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

