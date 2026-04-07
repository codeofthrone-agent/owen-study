# 專案提案：使用 HomeKit Controller 讀取光照與空間變化

## 1. 目的與背景 (Intent)
本專案的主要目的是開發一個 Python 獨立程式，用以讀取智慧感測器（如 Aqara FP2）的環境數據。
我們將聚焦於獲取三種關鍵資訊：
- **光照度 (Illuminance)**
- **物件移動 (Motion)**
- **空間變化/人員存在 (Occupancy/Presence)**

## 2. 技術方案評估 (Technical Approach)
經過評估 **Aqara Open API** 與 **HomeKit Controller (`aiohomekit`)**：
- **Aqara Open API**：官方未提供直接的本地端 Python SDK，通常需依賴雲端或非官方的逆向 API，長期維護成本較高且穩定性不足。
- **HomeKit Controller (`aiohomekit`)**：Aqara FP2 支援 HomeKit 協定。使用 Python 的 `aiohomekit` 模組可以透過區網（Local LAN）直接與設備綁定（Pairing），以 Controller 角色訂閱設備的 Characteristic 狀態更新（如 `OccupancySensor` 與 `LightSensor`），實現**完全本地化、低延遲**的感測器讀取。

因此，**建議採用 `aiohomekit` (HomeKit Controller)** 作為核心技術，這能確保資料安全性及感測速度。

## 3. 實作範圍 (Scope)
- **環境建置**：安裝 `aiohomekit` 等相關 Python 套件。
- **設備發現與綁定 (Discovery & Pairing)**：撰寫腳本發現在同一區網內的 HomeKit 設備，並透過 Setup Code 完成配對，取得配對憑證 (Pairing Data)。
- **資料讀取與訂閱 (Data Subscription)**：撰寫主要程式邏輯，透過配對憑證連線至設備，找出對應的光照度與存在感測服務，並設定事件回呼 (Event Callback) 以即時接收空間變化與光照度更新。

## 4. 非目標 (Non-Goals)
- 本專案初期不包含反向控制設備（如開關燈），僅聚焦於**讀取 (Read/Subscribe)** 感測器狀態。
- 不涵蓋 Home Assistant 等現成系統架構的複雜部署，主要專注於針對本次需求的**獨立 Python 腳本 (Standalone Python Script)** 開發。

## 5. 驗證條件 (Verification Plan)
- [ ] 執行設備發現腳本時，能夠在終端機列印出區網內支援 HomeKit 的 Aqara FP2 設備。
- [ ] 能透過輸入 8 碼 Setup Code 成功綁定並儲存配對憑證。
- [ ] 執行主體腳本時，若感測器偵測到人員移動 (Occupancy/Motion) 或光線變化 (Illuminance)，能夠在終端機即時非同步地列印出對應的數值更新。
