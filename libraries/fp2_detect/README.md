# Aqara FP2 空間狀態檢測模組

基於 HomeKit Local API (HAP 協議) 的 Aqara FP2 毫米波雷達感測器狀態監聽系統，提供空間佔用即時檢測、多區域分析與雨遮狀態判定功能。

## 功能特色

- 📡 **本地協議** - 基於 HomeKit Local API，反應極快且無須依靠雲端輪詢
- 🎯 **多區域分析** - 支援將每個自訂網格定義為獨立感測區域
- 🌧️ **動態模式** - 支援「雨遮 (awning)」與「側推艙 (slide)」等特殊場景的防抖判定
- 🤖 **Robot Framework 整合** - 完整的雙語 Gherkin 中文關鍵字支援
- 🏢 **企業網路支援** - macOS 使用 `dns-sd`、Linux 使用 `avahi-browse` 繞過 mDNS 封鎖
- 📦 **多台 FP2** - 透過 `--pairing-file` 管理多台設備的獨立配對資料

## 系統需求

### 必要套件

```bash
uv pip install aiohomekit python-dotenv
```

### Linux 額外需求

```bash
sudo apt install avahi-utils
```

### 硬體與網路環境需求

- Aqara FP2 感測器
- 感測器必須與執行主機處於同一個本地 Wi-Fi 網域內
- 企業網路封鎖 mDNS 亦可使用（系統自動改用 dns-sd / avahi-browse）

## 快速開始

### 1. 配置設定

編輯 `config/ipcam_config.yaml` 環境配置：

```yaml
environments:
  rv_car:
    fp2_sensors:
      awning_fp2:
        alias: "us_fp2"                  # 必須與 pair 時的 --alias 一致
        pairing_file: "libraries/fp2_detect/us_pairing_data.json"
        description: "RV 雨遮佔用雷達"
        awning_threshold: 2
        slide_threshold: 1
```

### 2. 設備配對 (CLI)

> [!IMPORTANT]
> - 初次配對或重新配對前，長按 FP2 背面 reset 鍵 **5 秒**直到黃燈快閃。
> - FP2 一次只能與一個 HomeKit 控制端配對。

```bash
# 單台（預設）
uv run python -u libraries/fp2_detect/fp2_homekit.py pair

# 多台 FP2：指定 alias 與配對檔案
uv run python -u libraries/fp2_detect/fp2_homekit.py pair \
  --alias us_fp2 \
  --pairing-file libraries/fp2_detect/us_pairing_data.json

# Setup Code 也可直接帶入（不寫入 .env）
uv run python -u libraries/fp2_detect/fp2_homekit.py pair \
  --alias us_fp2 \
  --pairing-file libraries/fp2_detect/us_pairing_data.json \
  --setup-code 12345678
```

配對成功後，配對資料自動儲存至指定的 `*_pairing_data.json`。

### 3. 即時監控 (CLI)

```bash
# 雨遮模式（預設）
uv run python -u libraries/fp2_detect/fp2_homekit.py monitor \
  --alias us_fp2 \
  --pairing-file libraries/fp2_detect/us_pairing_data.json

# 側推艙模式
uv run python -u libraries/fp2_detect/fp2_homekit.py monitor \
  --alias us_fp2 \
  --pairing-file libraries/fp2_detect/us_pairing_data.json \
  --mode slide
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

## 多台 FP2 管理

每台 FP2 使用獨立的 alias 與 pairing file：

| 設備 | alias | pairing file |
|------|-------|--------------|
| 美國實驗室 | `us_fp2` | `us_pairing_data.json` |
| 台北實驗室 | `tpe_fp2` | `tpe_pairing_data.json` |

`ipcam_config.yaml` 對應設定：

```yaml
fp2_sensors:
  awning_fp2:
    alias: "us_fp2"
    pairing_file: "libraries/fp2_detect/us_pairing_data.json"
  slide_fp2:
    alias: "tpe_fp2"
    pairing_file: "libraries/fp2_detect/tpe_pairing_data.json"
```

## 連線邏輯

```
monitor / get_status_once
  ├─ 嘗試 pairing_data.json 中儲存的 IP 直連（15 秒 timeout）
  │    └─ 成功 → 直接使用（FP2 未重啟時最快）
  └─ 失敗（FP2 重啟 / IP 變更）
       ├─ macOS: dns-sd -B / -L / -G
       └─ Linux: avahi-browse -r
            └─ 找到後自動更新 pairing_data.json，下次直連
```

## CLI 指令參考

```
action:
  discover      掃描區網內所有 HomeKit 設備
  pair          自動發現並配對 FP2（需 FP2 處於配對模式）
  pair-ip       手動指定 IP/Port/Device ID 配對
  monitor       即時監聽佔用狀態

選項:
  --alias           配對名稱，多台 FP2 時區分用（預設: my_fp2_sensor）
  --pairing-file    配對資料檔案路徑（預設: pairing_data.json）
  --mode            awning（雨遮）或 slide（側推艙），預設 awning
  --setup-code      8 位配對碼，也可設 FP2_SETUP_CODE 環境變數
  --ip              pair-ip 專用：FP2 IP 位址
  --port            pair-ip 專用：FP2 Port
  --device-id       pair-ip 專用：格式 XX:XX:XX:XX:XX:XX
```

## Robot Framework 關鍵字

| 關鍵字 | 說明 |
|--------|------|
| `Given FP2 空間雷達已連線 "${environment}" "${sensor_id}" "${mode}"` | 載入設定並宣告連線就緒 |
| `When 取得 FP2 當前空間佔用狀態` | 查詢目前狀態 |
| `When 取得 FP2 當前空間佔用狀態 "${sensor_id}"` | 查詢指定感測器狀態 |
| `Then FP2 空間狀態應該為 "${expected_state}"` | 驗證狀態（open / close） |
| `Then FP2 空間狀態應該為 "${expected_state}" 於 "${sensor_id}"` | 驗證指定感測器狀態 |
| `And 斷開 FP2 連線` | 釋放資源 |

## 故障排除

### discover 找不到設備

企業/辦公室網路通常封鎖 mDNS。先用系統工具確認：

```bash
# macOS
dns-sd -B _hap._tcp local

# Linux
avahi-browse _hap._tcp
```

若系統工具找得到但 Python 找不到，是 zeroconf 函式庫問題；若系統工具也找不到，是網路層問題（mDNS multicast 被封鎖）。

### 配對後 pairing_data.json 是空的 `{}`

通常是配對流程中途失敗。重置 FP2（長按 reset 5 秒）後重新執行 `pair`。

### 看不到自訂網格與區域

1. 打開 **Aqara Home App**
2. 點擊設備 → 細節設定 → 開啟 **「名稱同步 (Name Synchronization)」**
3. 重新執行 `monitor`

## 目錄結構

```text
libraries/fp2_detect/
├── __init__.py                    # 模組初始化
├── FP2Keywords.py                 # Robot Framework 關鍵字層
├── fp2_homekit.py                 # HomeKit 控制與狀態封裝核心
├── us_pairing_data.json           # 美國實驗室 FP2 配對資料
├── tpe_pairing_data.json          # 台北實驗室 FP2 配對資料
└── README.md                      # 本說明文件
```
