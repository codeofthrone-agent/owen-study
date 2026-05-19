# 自動化測試系統安裝文件  
**Automation Test System Installation Guide**

> 文件類型：Standard Operating Procedure (SOP)  
> 版本：v1.2（Draft）  
> 最後更新：2026-05-15  
> 適用範圍：WFCO PwrPro 自動化測試環境（機械手臂 + 控制板 + Hub + IPCAM + Speaker + Wi‑Fi）

### SOP 文件控制
| 欄位 | 內容 |
|---|---|
| Owner | `Owen ke` |
| Version | `v1.2` |
| Last Updated | `2026-05-15` |
| Change Summary | `v1.2：同步中英版架構，補強新手安裝指引與驗收標準` |

### SOP 使用方式
1. 請照章節順序做，不要跳過安全檢查。  
2. 每章做完，記得把對應 checklist 勾起來。  
3. 如果現場狀況跟文件不一樣，先暫停，並更新變更紀錄。  
4. 如果有不同或需要修整，請與我聯繫，我會儘快修正並協助。

### 安全先看（Safety First，請先讀）
- **接線與機械鎖附期間，禁止上電。**
- 上電前必做「線材方向、端子對應、活動件干涉」三項檢查。
- 任何一步出現不確定，先停手並標記 `Blocked`，不要硬做。

---

## 0. 開工前準備（新手建議先完成）

### 0.1 你會完成什麼
完成安裝前的設備盤點、工具確認、角色分工與風險確認，避免做到一半缺料或卡關。

### 0.2 設備與工具盤點（開始前打勾）
- [ ] 主機（Host PC）
- [ ] Wi‑Fi 設備（Router/AP/Extender，依現場擇一或混用）
- [ ] IPCAM：本次寄出 5 台（CAM1~CAM5）
  - CAM1~CAM3：固定用於監控環境
  - CAM4~CAM5：依現場需求安裝；若暫不使用，請標記後妥善存放/先收起來
- [ ] Speaker + Scarlett 4i4
- [ ] FP2 Sensor
- [ ] 機械手臂與控制板（WF-3534 / 3611A / 3611C）
- [ ] USB Hub、USB 延長線、燒錄器
- [ ] USB 連接線（依設備介面準備 USB-A / USB-C 等規格）
- [ ] UART 線材（建議預留備品）
- [ ] 鍵盤、滑鼠、外接螢幕（可接入 PC 或機械手臂端，用於修正網路問題）
- [ ] 線材標籤、束帶、固定座、絕緣膠帶
- [ ] 基本工具（螺絲起子、剪線鉗、萬用電表）

### 0.3 角色與聯絡
- 現場安裝負責人：`<填寫>`
- 驗收簽核人：`<填寫>`
- 台北團隊聯絡窗口：`<owen.ke>`

### 0.4 時間預估（參考）
- Chapter 1（Overview）：15~25 分鐘
- Chapter 2（安裝作業）：90~150 分鐘
- Chapter 3（主機位置）：20~40 分鐘
- Chapter 4（燒錄器/USB/Hub）：30~50 分鐘
- Chapter 5（機械手臂/面板）：45~75 分鐘
- Chapter 6（最終驗收）：15~30 分鐘
- **總計（單人參考）**：約 3.5~6 小時（依現場配線難度與返工次數而變動）

### 0.5 開始條件（全部滿足才開工）
- [ ] 圖1、圖2可正常查看
- [ ] `qa_rpt` 已完成既有設定確認（沿用現有設定，不進行 reset）
- [ ] 施工區已清空，無人員絆倒風險
- [ ] 已確認「未上電」狀態

### 0.6 帳號與密碼資訊（施工用）
> 建議：此區塊僅保留於內部版本文件；對外分享時請移除或遮罩。

- 通用登入密碼：`thortron`
- Wi‑Fi 測試帳密：`SSID: qa_rpt / Password: 12345678`
- 適用範圍：現場安裝/維護階段，用於登入 PC、相關設備與網路連線確認
- 使用原則：若帳密有變更，請同步更新本文件與交接紀錄

---

## 1. 系統 Overview（System Overview）

### 章節總覽圖（圖1 + 圖2）
![System Layout](https://drive.google.com/uc?export=view&id=1NMFMvyxQza_j-wfTMYb3aPwnLLS1jNVp)

*圖1：System Layout（空間分區與設備擺位全貌）*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*圖2：Network and Device Topology（控制板、Hub、相機、手臂與網路關係）*

> 本章建立系統整體觀，先確認空間佈局與網路拓樸，作為後續安裝章節的閱讀基礎。

### SOP 區塊（Chapter 1）
- **Objective（目的）**：建立閱讀者對系統、元件與章節流程的一致理解。
- **Preconditions（前置條件）**：圖1/圖2可對照，且讀者已完成 Chapter 0 開工前準備。
- **Procedure（程序重點）**：先看圖面與元件邊界，再確認章節導讀。
- **Verification（驗證方式）**：確認讀者可指出本章與安裝章（Chapter 2）之差異。
- **Pass Criteria（通過標準）**：讀者清楚 Chapter 1 僅為 overview，不含實體安裝。
- **Exceptions（例外處理）**：若現場人員仍有章節混淆，先口頭對齊後再進入 Chapter 2。

### 1.1 本章目的（Overview）
本章提供系統背景與閱讀地圖，協助安裝人員先理解整體架構，再進入後續實作章節：

- 說明本文件用途與使用邏輯
- 說明本次安裝會接觸到的元件邊界
- 提供章節導讀（先看哪章、做完要去哪章）
- 本章不執行實體安裝動作

---

### 1.2 系統元件與邊界（閱讀理解）
本節用於理解系統，非現場操作步驟。

**名詞速讀（首次閱讀先看這裡）**
- **AP（Access Point）**：無線基地台，負責提供 Wi‑Fi 訊號。
- **Extender**：Wi‑Fi 延伸器，用來把訊號帶到較遠區域。
- **Backhaul（回程）**：延伸設備回到主網路的連線方式（有線或無線）。
- **IPCAM**：網路攝影機，可透過網路看即時畫面。
- **Scarlett 4i4**：音訊介面，負責把主機音訊送到喇叭。

- **網路佈建**：Wi‑Fi Router / AP / Extender（僅到可連線）
- **影像設備**：IPCAM（僅到定位、供電、串流可開）
- **音訊設備**：Speaker + Scarlett 4i4（僅到配線完成）
- **感測設備**：FP2（僅到定位、供電、可觸發）
- **空間與走線**：安全固定、避開活動件與高風險區

不在本章範圍：
- 現場安裝動作
- 功能驗證與長時間穩定性測試
- 完整故障排查流程

---

### 1.3 章節導讀（先看再做）
- **Chapter 2：安裝作業（Wi‑Fi / IPCAM / Speaker / FP2）**
- **Chapter 3：主機位置配置**
- **Chapter 4：燒錄器 / USB 延長線 / USB Hub 配置**
- **Chapter 5：機械手臂及面板配置**
- **Chapter 6：最終驗收與交付狀態**

---

## 2. 安裝作業（Wi‑Fi / IPCAM / Speaker / FP2）

### SOP 區塊（Chapter 2）
- **Objective（目的）**：完成 Chapter 2 的現場基礎安裝（Wi‑Fi、IPCAM、Speaker/Scarlett 4i4、FP2）。
- **Preconditions（前置條件）**：Chapter 1 已閱讀完成，圖1/圖2可對照，設備與線材到位。
- **Procedure（程序重點）**：依序執行 **Wi‑Fi → IPCAM → Speaker/Scarlett 4i4 → FP2**。
- **Verification（驗證方式）**：逐項完成安裝檢核（非最終驗收）。
- **Pass Criteria（通過標準）**：四類設備安裝完成並具備基本可用條件。
- **Exceptions（例外處理）**：若現場受限或測試未通過，標記 `Blocked/Rework` 並記錄原因。
- **Handoff（交接）**：當 Chapter 2 全部接線與安裝完成後，更新安裝紀錄並進入下一章節。

### 2.0.1 Chapter 2 完成後紀錄（精簡）
1. 勾選本章所有驗證項目。
2. 補上必要照片（全景、配線、主機畫面）。
3. 若有未完成項目，標記 `Blocked/Rework` 並填原因。
---

### 2.1 Wi‑Fi 位置評估與配電配線規劃
1. 先依圖1確認 Wi‑Fi 設備（Router / AP〔無線基地台〕/ Extender〔訊號延伸器〕）候選位置，優先覆蓋「人員主要操作動線」與「IPCAM〔網路攝影機〕實際安裝區位」。
2. 針對每個候選位置，同步評估：
   - 配電可行性（插座距離、延長線路徑、固定方式）
   - 配線可行性（是否可拉 LAN 網路線、走線是否安全）
3. 依現場條件選擇連線方案（擇一）：
   - **LAN 有線回程**：可拉線且路徑安全時優先採用。
   - **Wi‑Fi Extender 無線延伸**：不易拉線或需跨區延伸時採用。
4. 完成設備定位、供電與線材固定，避免跨越活動機構與高風險區域。
5. 啟用後以 `SSID: qa_rpt / Password: 12345678` 進行連線測試，確認可正常上網與內部設備互通，再記錄最終位置、供電點與連線方案（LAN / Extender）。

**驗證標準**
- [ ] Wi‑Fi 設備位置符合圖1覆蓋需求
- [ ] 已完成「LAN 或 Extender」方案選擇並記錄原因
- [ ] 配線與配電完成且固定
- [ ] `qa_rpt` 可穩定連線（連續 5 分鐘不中斷）
- [ ] IPCAM 與主控端皆可連上 `qa_rpt`（至少抽查 1 台 IPCAM）

---

### 2.2 IPCAM 定位與配電（出貨前已完成 Wi‑Fi 設定）
> 送場機器之 IPCAM 已預先完成 Wi‑Fi 設定，現場僅需定位、配電與連線確認。

1. IPCAM 上電後，先確認可載入既有 Wi‑Fi 設定（`qa_rpt`）。
2. 依 2.1 的網路方案執行：可拉線則優先 LAN；否則使用已規劃完成之 Wi‑Fi Extender 區域。
3. 依圖1觀測位置擺放每台 IPCAM，確認視角覆蓋對應區域。
4. 完成配電與線材固定，避免壓線、拉扯與高熱區。
5. 建立標籤與對照（`CAM-xx` + 實際區位）。
6. 當 2.1 與 2.2 全部完成後，更新 IPCAM 安裝與定位紀錄（含 CAM 編號與區位）。

### 2.2.1 IPCAM 管理 App 安裝與成員加入（SwitchBot）
> 目的：讓現場安裝者也能在管理 App 看到 IPCAM，協助定位、角度調整與後續維護。

1. 先於現場手機安裝 **SwitchBot App**（iOS App Store / Android Google Play），可掃描下列 QRCode，或直接於商店搜尋 `SwitchBot`：

   **iOS App QRCode**
   ![SwitchBot iOS App QRCode](https://drive.google.com/uc?export=view&id=17n35QZWyTbHJy0GDqlHboSMO4687_RNg)

   **Android App QRCode**
   ![SwitchBot Android App QRCode](https://drive.google.com/uc?export=view&id=1Q0BiGCnpj7GSRbQi1v3ywKmp8nkmkEaA)
2. 以現場可用帳號登入 App，確認可進入「家庭」頁面。
3. 由管理者手機進入 SwitchBot「家庭成員邀請」頁面。
4. **統一使用「邀請碼」方式**加入（本文件目前邀請碼：`UDQ9TN`）。
5. 受邀者加入後，請立即確認可查看 CAM1~CAM3 影像（必要時含 CAM4~CAM5）。
6. 若受邀者看不到裝置，先檢查是否加入到正確「家庭/群組」，再以最新邀請碼重試。
> ⚠️ **邀請碼時效提醒**  
> 目前邀請碼：`UDQ9TN`  
> 若邀請碼已過期，請聯繫：`owen.ke@thortron.com` 更新邀請資訊。

**驗證標準**
- [ ] 每台 IPCAM 都在圖1指定觀測位置
- [ ] 每台 IPCAM 供電穩定、可上線（連續 5 分鐘可存取）
- [ ] 主控端可讀取全部串流（每路至少觀察 30 秒、無明顯卡頓）
- [ ] CAM1~CAM5 安裝/定位紀錄完整（含未安裝原因）
- [ ] 現場安裝者已成功加入管理 App，且可查看必要 IPCAM 影像

---

### 2.3 Speaker 擺放、配電與配線（接 Scarlett 4i4〔音訊介面〕）
1. 依圖1完成 Speaker 擺放，並先以「安裝可達、可固定、可維護」為主。
2. 完成每顆 Speaker 的配電與固定。
3. 依規劃完成配線並接回音訊介面。
4. 設定 Scarlett 4i4 放置位置（可維護、散熱與走線安全）。
5. Speaker 輸出線接到 Scarlett 4i4 對應輸出埠，並貼標籤。

> 註：本章為安裝章，2.3 不執行音訊正確性測試；播放/覆蓋範圍等功能測試請留到後續章節。

**驗證標準**
- [ ] Speaker 擺位符合圖1
- [ ] Speaker 配電與配線完成
- [ ] Scarlett 4i4 位置固定且接線清楚

---

### 2.4 FP2 Sensor〔感測器〕定位、安裝與配電（Awning + Light4）

#### 附圖：安裝朝向與覆蓋範圍
![FP2 安裝朝向與覆蓋範圍](https://drive.google.com/uc?export=view&id=1WVI5SHkc_YI7gLS-H1U6NgtyR1xQtuyX)

1. FP2 主要用於偵測 **Awning + Light4**，先依圖1定位目標偵測區。
2. 依附圖確認安裝朝向與覆蓋範圍，並依現場實際狀況調整到合適位置。
3. 使用 FP2 磁鐵特性進行試貼定位，確認偵測正確後再固定。
4. 完成配電與線材固定，保留可拆裝維護空間。
5. 執行 Awning + Light4 觸發測試，記錄觸發成功區域。

**驗證標準**
- [ ] FP2 位置可穩定偵測 Awning + Light4
- [ ] 安裝方式可快速拆裝（磁吸）
- [ ] 配電完成且線材安全

---

## 3. 主機位置配置（依現場狀態）

### 章節附圖
![System Layout](https://drive.google.com/uc?export=view&id=1NMFMvyxQza_j-wfTMYb3aPwnLLS1jNVp)

*圖：System Layout（主機位置應依現場可維護區與走線路徑配置）*

### SOP 區塊（Chapter 3）
- **Objective（目的）**：依現場條件確認主機最終位置，兼顧散熱、維護性與線材可達性。
- **Preconditions（前置條件）**：Chapter 1 完成、圖1可對照、主機/電源/網路接口可用。
- **Procedure（程序重點）**：依序執行 **候選位置評估 → 電源與網路可達性確認 → 關聯設備走線檢查 → 主機固定與標記**。
- **Verification（驗證方式）**：依 3.3 勾核主機可維護性、電源網路穩定性、線材固定狀態。
- **Pass Criteria（通過標準）**：主機位置不阻礙作業，且供電/網路/關聯走線皆穩定。
- **Exceptions（例外處理）**：若受空間、散熱或走線限制，標記 `Blocked/Rework`，記錄替代位置與原因。

### 3.1 目的
根據現場實際空間、散熱、維護動線與線材長度，決定主機最終放置位置。

### 3.2 配置原則
- 優先選擇乾燥、通風、可維護位置
- 避免高熱區、潮濕區、易碰撞區
- 需兼顧到 USB Hub、燒錄器、音訊介面、機械手臂控制線之走線長度
- 可快速觸達電源與網路接口

### 3.3 驗證標準
- [ ] 主機位置不阻礙操作與維修
- [ ] 主機電源與網路連接穩定
- [ ] 關聯線材長度合理且固定完成

---

## 4. 燒錄器〔Burner〕 / USB 延長線 / USB Hub〔集線器〕配置（連回 PC）

### 章節附圖
![Wiring Detail](https://drive.google.com/uc?export=view&id=1XE3O7h17guDEkzzsTE8ZMLZFj0ecc8tY)

*圖：Wiring Detail（燒錄器、Hub、延長線回連 PC 參考）*

### SOP 區塊（Chapter 4）
- **Objective（目的）**：完成燒錄器、USB 延長線與 USB Hub 的穩定拓樸，確保可持續回連 PC。
- **Preconditions（前置條件）**：主機位置已確定、Hub 與燒錄器可上電、PC 端可執行裝置辨識。
- **Procedure（程序重點）**：依序執行 **設備定位 → USB 路徑鋪設 → 拓樸連接（燒錄器→Hub→延長線→PC）→（Optional）標籤建立 → PC 端辨識確認**。
- **Verification（驗證方式）**：依 4.3 勾核辨識率、連線穩定性與配線安全。
- **Pass Criteria（通過標準）**：所有目標裝置可被 PC 穩定辨識，且長時間無間歇斷線。
- **Exceptions（例外處理）**：若延長線長度/品質不足或訊號不穩，標記 `Rework` 並更換路徑或線材。

### 4.1 目的
完成燒錄器、USB 延長線與 USB Hub 的拓樸配置，確保可穩定回連 PC。

### 4.2 配置步驟
1. 確認燒錄器與 USB Hub 的安裝位置（靠近維護區，避免受拉扯）。
2. 依現場路徑鋪設 USB 延長線，避開門片、活動機構與高熱區。
3. 完成連接：`燒錄器 -> USB Hub -> USB 延長線 -> PC`。
4. （Optional）可依需求建立連接線與連接口標籤（如 `H1-P01`、`USB-EXT-01`、`BURNER-01`）。
5. 在 PC 端確認裝置可被辨識並維持穩定連線。

### 4.3 驗證標準
- [ ] 所有燒錄器都可在 PC 端辨識
- [ ] USB 延長線與 Hub 配線固定且安全
- [ ] 長時間連線無間歇斷線（觀察 10 分鐘）

---

## 5. 機械手臂及面板配置

### 章節附圖
![Robot Arm Assembly](https://drive.google.com/uc?export=view&id=1z1aUfe4O4kPEcjyr5Lg8QLkneW-JKC36)

*圖：Robot Arm Assembly（機械手臂與面板安裝參考）*

### SOP 區塊（Chapter 5）
- **Objective（目的）**：完成機械手臂與面板安裝，確保固定可靠、線材正確連接且可安全上電。
- **Preconditions（前置條件）**：底座安裝面可用、相關線材齊備、上電前安全規範已確認。
- **Procedure（程序重點）**：依序執行 **初次 USB-A ↔ USB-C 連接 → 手臂底座固定 → 面板安裝 → 線材全連接檢查 → 上電前最終檢查**。
- **Verification（驗證方式）**：依 5.3、5.4 與 5.5 勾核固定狀態、配線安全、上電規範與測試情境位置切換。
- **Pass Criteria（通過標準）**：機械手臂活動範圍正常、面板位置正確、配線符合安全規範。
- **Exceptions（例外處理）**：若活動干涉、接頭鬆動或線材受壓，標記 `Blocked/Rework`，修正後再上電。

### 5.1 目的
完成機械手臂與面板（控制板）安裝，確保固定、配線與操作安全。

### 5.2 配置步驟
1. 初次安裝時，先連接手臂後方 **USB‑A** 到手臂末端 **USB‑C**。
2. 依圖面完成機械手臂底座固定，確認活動範圍無干涉。
3. 安裝面板（如 3611A / 3611C / WF-3534）至指定位置。
4. 檢查線材是否都已連接完成，並確認不壓線、不跨越活動件。
5. 進行上電前最終檢查。

### 5.3 驗證標準
- [ ] 機械手臂固定牢靠、活動範圍正常
- [ ] 面板安裝位置正確且可維護
- [ ] 配線完成且符合安全規範

### 5.4 Safety, Power Isolation, and Power-On Rules

1. **接線與鎖附期間不得上電**
2. 所有線材插接完成後，先做方向與端子檢查再上電
3. UART 接法必須遵守：
   - `G -> G`
   - `RX -> TX`
   - `TX -> RX`
4. 線材不得壓在活動機構、踏階、門片、翻板下方
5. 機械手臂固定完成後，確認介面朝外、活動範圍無干涉
6. 最後一步才接入主電源並開機

### 5.5 3611A/3511A 安裝位置切換規則（依測試目的）
1. **語音測試**：請將 `3611A/3511A` 放回原本牆上位置。
2. **機械手臂點擊測試**：當機械手臂設定完整後，若需由手臂進行點擊測試，請將 `3611A` 安裝到機械手臂基座。
3. 每次切換位置後，請更新標記與拍照紀錄，避免後續人員誤判。

---

## 6. 最終驗收與交付狀態（Final Acceptance & Handover）

### SOP 區塊（Chapter 6）
- **Objective（目的）**：完成全章節最終驗收與狀態判定，形成可交付結果。
- **Preconditions（前置條件）**：Chapter 1~5 皆已完成並有對應勾核紀錄。
- **Procedure（程序重點）**：依序執行 **章節結果回顧 → 缺失項目補正/標記 → 最終狀態填報 → Owner 簽核**。
- **Verification（驗證方式）**：檢查 6.1 與 6.2 欄位是否完整（Status、Blocked Reason、Sign-off、Date）。
- **Pass Criteria（通過標準）**：所有必填欄位完整且狀態可追溯（Ready/Blocked/Rework）。
- **Exceptions（例外處理）**：若資料缺漏，暫標 `Rework` 並回補後再結案。

### 6.1 章節總檢查
- [ ] Chapter 1：Overview（說明）完成
- [ ] Chapter 2：Wi‑Fi/IPCAM/Speaker/Scarlett4i4/FP2 安裝完成
- [ ] Chapter 3：主機位置確認完成
- [ ] Chapter 4：燒錄器/USB 延長線/Hub/PC 連接完成
- [ ] Chapter 5：機械手臂與面板配置完成
- [ ] Chapter 2 安裝紀錄與照片已更新完成

### 6.2 最終狀態標記
- **Status**：`Ready / Blocked / Rework`
- **Blocked Reason**：`<若有阻塞請填寫>`
- **Owner Sign-off**：`<Owner Name>`
- **Date**：`YYYY-MM-DD`

---


## 7. 新手常見問題與快速排除（Troubleshooting）

| 症狀 | 可能原因 | 先做這 1 步 | 若仍失敗 |
|---|---|---|---|
| 看不到 `qa_rpt` | Wi‑Fi 未上電/位置太遠 | 先確認 Router/AP 電源與指示燈 | 改用 Extender 或調整位置後重測 |
| IPCAM 無串流 | 網路未連上或供電不穩 | 先重插電源並確認連線到 `qa_rpt` | 記錄 CAM 編號，標記 `Blocked` 並交由後續測試章節處理 |
| PC 偵測不到燒錄器 | USB 路徑或接頭鬆脫 | 依 `燒錄器 -> Hub -> 延長線 -> PC` 重插一次 | 更換延長線或 Hub 埠位 |
| 機械手臂動作異常 | 線材干涉/接法錯誤 | 立即斷電，檢查 UART 對應與活動範圍 | 標記 `Blocked`，完成修正後再上電 |

---


## Appendix C — 現場驗收示意圖與填寫表

### C.1 示意圖（依圖一邏輯，不含 Wi‑Fi）
（已移除圖片，現場請以 Chapter 1 的圖1：System Layout 為主）

### C.2 一頁紙列印版（大欄位打勾）
- 檔案：`docs/ch2_onsite_acceptance_onepage_zh.md`（若尚未改名，請先沿用既有 ch1 檔名）

### C.3 現場驗收完整表（單一總表）

| 類別 | 項目ID/名稱 | 圖一區位 | 實際位置 | 配電完成(Y/N) | 配線/連接狀態 | 功能測試結果 | 驗收結果(Pass/Fail) | 備註 |
|---|---|---|---|---|---|---|---|---|
| Wi‑Fi | WIFI-01 Router/AP |  |  |  | 有線/Extender | SSID `qa_rpt` 連線：正常/異常 |  |  |
| Wi‑Fi | WIFI-EXT-01 Extender（如有） |  |  |  | 有線/Extender | 訊號延伸：正常/異常 |  |  |
| IPCAM | CAM-01 |  |  |  | 有線/Extender | 串流：正常/異常 |  |  |
| IPCAM | CAM-02 |  |  |  | 有線/Extender | 串流：正常/異常 |  |  |
| IPCAM | CAM-03 |  |  |  | 有線/Extender | 串流：正常/異常 |  |  |
| IPCAM | CAM-04 |  |  |  | 有線/Extender | 串流：正常/異常 |  |  |
| Speaker | SPK-01 |  |  |  | 接至 Scarlett 4i4 埠位： | 播放：正常/異常 |  |  |
| Speaker | SPK-02 |  |  |  | 接至 Scarlett 4i4 埠位： | 播放：正常/異常 |  |  |
| Speaker | SPK-03 |  |  |  | 接至 Scarlett 4i4 埠位： | 播放：正常/異常 |  |  |
| Audio Interface | Scarlett 4i4 |  |  |  | 輸入/輸出配線完成(Y/N) | 音訊路由：正常/異常 |  |  |
| Sensor | SEN-FP2-01（Awning + Light4） |  |  |  | 磁吸安裝(Y/N) | 觸發：正常/異常 |  |  |
| 主機 | Host PC |  |  |  | Hub/燒錄器回連完成(Y/N) | 裝置辨識：正常/異常 |  |  |
| 機械手臂/面板 | Robot Arm + Panels |  |  |  | 線材安全檢查(Y/N) | 動作/通訊：正常/異常 |  |  |

| Owner | Date | Final Status |
|---|---|---|
|  |  | Ready / Blocked / Rework |

---

## Appendix A — Recommended Naming Convention
- Device：`CAM-01`, `SPK-01`, `ARM-CTRL-01`
- Hub Port：`H1-P01`, `H2-P03`
- Cable：`C-001`, `UART-01`, `USB-EXT-01`
- Node：`WF-3611-A`, `WF-3611-C`, `WF-3611-B`

## Appendix B — Document Control
- 作者：`<Owner Name>`
- 審核：`<Reviewer Name>`
- 生效日：`YYYY-MM-DD`
- 版本歷程：  
  - v1.0 初版


## Appendix D — 術語白話解釋（給第一次安裝的人）
- **Backhaul（回程）**：主網路回到核心設備的連線方式，可是有線 LAN 或無線延伸。
- **Extender**：Wi‑Fi 延伸器，用來把訊號帶到較遠區域。
- **IPCAM**：網路攝影機，可透過網路看即時畫面。
- **Scarlett 4i4**：音訊介面，負責把主機音訊送到喇叭。
- **FP2**：感測器，本案用於偵測 Awning + Light4 觸發行為。
- **Burner（燒錄器）**：用於燒錄/連接板子的 USB 裝置。
- **Blocked / Rework**：
  - `Blocked`：目前卡住，無法繼續，需外部支援。
  - `Rework`：可繼續但需返工重做。

---


