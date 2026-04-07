# Aqara FP2 空間佔用與雨遮偵測系統

專案使用 **HomeKit Local API (HAP 協議)** 來即時監聽 Aqara FP2 毫米波雷達感測器的狀態。
此系統能偵測「空間佔用（Occupancy）」變化，並支援多區域（Zone）組合判定，適用於**雨遮展開偵測**或**露營車內部空間活動偵測**。

## 為什麼選擇 HomeKit 路線？

過去嘗試過 Aqara Cloud API (Polling) 與 MQTT (Push)，但發現：
- Cloud API 輪詢有延遲，且區域即時狀態暴露不完整。
- Aqara MQTT OpenAPI 不推送區域佔用（Zone Presence）事件。
- **HomeKit（本地 HAP 協議）**：不僅能在本地網路（離線）執行，且能將 Aqara App 中設定的每一個「偵測區域」當作獨立的「佔用感測器（Occupancy Sensor）」即時推送狀態，延遲最低且資訊最完整。

## 系統需求

- Python 3.8+
- Aqara FP2 感測器（需在同一個本地網路）
- 透過 `uv` 管理套件模組

## 安裝與執行

本專案將所有功能整合於單一腳本 `fp2_homekit.py`。

### 1. 設定環境變數

在專案根目錄建立 `.env` 檔案，填入 FP2 設備機身或包裝盒上的 8 位數 HomeKit Setup Code：
```ini
fp2_setup_code=12999964
```

### 2. 初始化與配對

> [!IMPORTANT]
> - **硬體重新設置**：**初次使用 FP2 或需要重新設置時，請連續按下 FP2 實體按鈕 10 下**。
> - **確保裝置在同一個網路**：你的電腦、FP2 感測器以及手機必須連線至同一個 2.4GHz 或混合 Wi-Fi 網路，否則 mDNS 廣播將無法通訊。

**初次使用程式碼（配對流程）**

初次使用程式碼需要先進行配對，**使用時機是在 FP2 設置 Wi-Fi 成功時**執行此代碼：

```bash
uv run python3 fp2_homekit.py discover
```
*腳本會掃描網段內的 HomeKit 設備。如果找到「尚未配對」的 FP2，它會自動讀取 `.env` 中的密碼進行配對，終端機將**顯示配對成功**，並在目錄下產生 `pairing_data.json` 檔案。*

> **其他配對與除錯方法（保留）**：
> - FP2 一次只能被一個系統配對。如果設備顯示已配對，但你無法控制，請先在 FP2 設備上**連續按下實體按鈕 10 次（黃燈閃爍）**解除舊配對（此舉不會清除 Wi-Fi 設定）。
> - 你也可以使用 `uv run python3 fp2_homekit.py pair` 強制執行配對流程。

### 3. 監控與使用

配對成功之後，後面就可以直接執行 monitor 進行監控：

```bash
uv run python3 fp2_homekit.py monitor
```

執行後會即時列出所有偵測到的區域，並監控「🛑 空間被佔用（偵測到物體/雨遮）」與「⚪ 空間淨空」的事件。
預設邏輯為：**當有 ≥ 2 個區域同時被佔用時，判定為「🌧️ 雨遮展開」**。

## 進階：如何讓更多區域同步到 HomeKit？

預設情況下，FP2 可能只會暴露「整體空間 (Zone 01)」給 HomeKit。
要在 `fp2_homekit.py monitor` 中看到你自訂的區域（如：左側雨遮、右側區域），請完成以下操作：

1. 打開手機上的 **Aqara Home App**。
2. 進入 FP2 設定 > **偵測區域配置**，畫出並儲存你需要的網格區域。
3. 點擊右上角 `...` 進入設備設定，開啟 **「名稱同步 (Name Synchronization)」**。
4. （視需要）在設備資訊中點擊「同步到 Apple Home」。
5. 重新執行 `uv run python fp2_homekit.py monitor`，新的區域就會自動出現並開始監控！
