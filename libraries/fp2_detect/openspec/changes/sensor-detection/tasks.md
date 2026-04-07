# 實作任務清單：使用 HomeKit Controller 讀取光照與空間變化

- [ ] **1. 環境建置**
  - [ ] 建立 `requirements.txt` 或 `pyproject.toml` 並加入 `aiohomekit` 依賴。
  - [ ] 確認執行環境支援 mDNS/zeroconf 以供 HomeKit 設備發現。

- [ ] **2. 設備發現與綁定**
  - [ ] 撰寫 `discover.py`：使用 `aiohomekit` 於區網內掃描支援 HomeKit 的設備（如 Aqara FP2）。
  - [ ] 撰寫 `pair.py`：提示使用者輸入設備的 8 位數 Setup Code，完成綁定流程，並將 Pairing Data 妥善存於本地 JSON 檔案。

- [ ] **3. 資料讀取與訂閱**
  - [ ] 撰寫主程式 `main.py`：載入 JSON 綁定憑證並連線至目標設備。
  - [ ] 檢索連線設備的 Accessory 結構，定位到 `OccupancySensor` 與 `LightSensor` Services。
  - [ ] 透過 `aiohomekit` 的事件訂閱機制 (Event Subscription) 註冊 Characteristic 更新的 Callback。
  - [ ] 啟動 Async Event Loop 持續監聽，當有人員移動或光線變化時，在終端機即時輸出日誌。
