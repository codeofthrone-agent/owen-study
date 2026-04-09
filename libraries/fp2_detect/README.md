# Aqara FP2 空間狀態檢測模組

基於 HomeKit Local API (HAP 協議) 的 Aqara FP2 毫米波雷達感測器狀態監聽系統，提供空間佔用即時檢測、多區域分析與雨遮狀態判定功能。

## 功能特色

- 📡 **本地協議** - 基於 HomeKit Local API，反應極快且無須依靠雲端輪詢
- 🎯 **多區域分析** - 支援將每個自訂網格定義為獨立感測區域
- 🌧️ **動態模式** - 支援「雨遮 (awning)」與「側推艙 (slide)」等特殊場景的防抖判定
- 🤖 **Robot Framework 整合** - 完整的雙語 Gherkin 中文關鍵字支援

## 系統需求

### 必要套件

```bash
uv pip install aiohomekit python-dotenv
```

### 硬體與網路環境需求

- Aqara FP2 感測器
- 感測器必須與執行主機處於同一個本地且互通的 Wi-Fi 網域內（支援 mDNS）

## 快速開始

### 1. 配置設定

編輯 `config/ipcam_config.yaml` 環境配置：

```yaml
environments:
  rv_car:
    fp2_sensors:
      awning_fp2:
        alias: "my_fp2_sensor"           # 對應 Aqara Home 設備名稱
        description: "RV 雨遮佔用雷達"
        awning_threshold: 2              # 雨遮模式閾值
```

編輯專案根目錄的 `.env` 文件，加入該設備 8 位數的 Setup Code：

```bash
# FP2 雷達感測器 HomeKit 配對碼
FP2_SETUP_CODE=129-99-964
# (也可針對個別設備使用 AWNING_FP2_SETUP_CODE 等專屬變數)
```

### 2. 設備配對與初始化 (CLI)

> [!IMPORTANT]
> - **硬體重新設置**：初次使用 FP2 或需要重新配對時，請先連續按下 FP2 實體按鈕 10 下（變為黃燈閃爍模式）。
> - **單一性**：目前 FP2 一次只能綁定與配對一個 HomeKit 控制端。

在連上同一個 Wi-Fi 網路後，進行硬體設備尋找與配對：

```bash
uv run python3 libraries/fp2_detect/fp2_homekit.py discover
```

一旦配對成功，本地將自動產生 `pairing_data.json` 憑證檔管理連線金鑰。

### 3. Python 監控範例

配對完成後，可直接透過指令即時監聽狀態或進入自動化體系：

```bash
uv run python3 libraries/fp2_detect/fp2_homekit.py monitor
```

### 4. Robot Framework 使用範例

```robotframework
*** Settings ***
Library    libraries.fp2_detect.FP2Keywords

*** Test Cases ***
檢測 RV 車雨遮狀態
    Given FP2 空間雷達已連線 "rv_car" "awning_fp2" "awning"
    When 取得 FP2 當前空間佔用狀態
    Then FP2 空間狀態應該為 "close"
    And 斷開 FP2 連線
```

## API 參考

### FP2StateManager 類別

負責維護 HomeKit 狀態與判定邏輯的核心。

- `get_status_once(...)`: 發起一次即時非同步狀態查詢。
- `check_state(...)`: 使用 `awning_threshold` 或 `slide_threshold` 分析多個區域的阻擋面積並彙總結果。

## Robot Framework 關鍵字

### 連線與配置管理

- `Given FP2 空間雷達已連線 "${environment}" "${sensor_id}" "${mode}"`

### 狀態擷取

- `When 取得 FP2 當前空間佔用狀態`
- `When 取得 FP2 當前空間佔用狀態 "${sensor_id}"`

### 狀態驗證

- `Then FP2 空間狀態應該為 "${expected_state}"`
- `Then FP2 空間狀態應該為 "${expected_state}" 於 "${sensor_id}"`

### 資源釋放

- `And 斷開 FP2 連線`

## 故障排除

### 問題：執行 discover 無法找到設備

**可能原因:**
- 手機、FP2 設備或電腦不在同一個 Wi-Fi 網域
- 防火牆屏蔽了 mDNS 廣播 (Port 5353)
- 設備已經被手機上的 Apple Home 配對搶走

**解決方法:**
1. 保證都在同個 2.4GHz 網段。
2. 狂按設備實體按鈕 10 下觸發重置後，再次執行 `discover`。

### 問題：看不到自訂的網格與區域

**解決方法:**
1. 打開手機上的 **Aqara Home App**
2. 點擊設備進入細節設定，開啟 **「名稱同步 (Name Synchronization)」**
3. 重新執行 monitor 程式碼便可讀取自定義的房間名稱。

## 目錄結構

```text
libraries/fp2_detect/
├── __init__.py                # 模組初始化
├── FP2Keywords.py             # Robot Framework 關鍵字層
├── fp2_homekit.py             # HomeKit 控制與狀態封裝核心
└── README.md                  # 本說明文件
```
