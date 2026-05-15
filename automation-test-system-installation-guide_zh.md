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
| Version | `1.1` |
| Last Updated | `2026-05-15` |
| Change Summary | `初版` |

### SOP 使用方式
1. 請照章節順序做，不要跳過安全檢查。  
2. 每章做完，記得把對應 checklist 勾起來。  
3. 如果現場狀況跟文件不一樣，先暫停，並更新變更紀錄。  
4. 如果有不同或需要修整，請與我聯繫，我會儘快修正並協助。

---

## 1. 系統 Overview（System Overview）

### 章節總覽圖（圖1 + 圖2）
![System Layout](https://drive.google.com/uc?export=view&id=1_xDdE393fwM6hEDepC55_PjGOVfhiuoX)

*圖1：System Layout（空間分區與設備擺位全貌）*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*圖2：Network and Device Topology（控制板、Hub、相機、手臂與網路關係）*

> 本章建立系統整體觀，先確認空間佈局與網路拓樸，並完成 Wi‑Fi、IPCAM、Speaker/Scarlett 4i4、FP2 的安裝與驗收。

### SOP 區塊（Chapter 1）
- **Objective（目的）**：完成 Chapter 1 的現場基礎部署（Wi‑Fi、IPCAM、Speaker/Scarlett 4i4、FP2）並建立可驗收狀態。
- **Preconditions（前置條件）**：圖1/圖2可對照、設備與線材到位、IPCAM 已可設定 `qa_rpt`、現場電源點已確認。
- **Procedure（程序重點）**：依序執行 **Wi‑Fi 位置與配線配電 → IPCAM 觀測位擺設與配電 → Speaker 擺放與 Scarlett 4i4 配線 → FP2（Awning + Light4）定位安裝與配電**。
- **Verification（驗證方式）**：使用 Appendix C 單一總表逐項勾核位置、供電、配線與功能測試結果。
- **Pass Criteria（通過標準）**：四類設備均完成安裝，且 `qa_rpt`、影像串流、音訊輸出、FP2 觸發測試皆可正常驗證。
- **Exceptions（例外處理）**：若圖面與現場不一致、電源/配線受限或測試未通過，標記 `Blocked/Rework` 並記錄原因後再進入下一章。

### 1.1 Project Scope and Objectives
本文件用於指導建立一套可重複、可維護的自動化測試系統，目標如下：

- 建立穩定的硬體安裝與接線流程
- 讓控制板、Hub、機械手臂、相機與音訊設備可協同運作
- 建立標準化的驗收與故障排查流程
- 降低部署時間與重工風險

---

### 1.2 System Topology and Architecture Overview
系統由下列子系統構成：

- **控制/運算子系統**：主控設備、控制板（WF-3534 / 3611A / 3611C）
- **I/O 與資料子系統**：USB Hub、延長線、燒錄器與其他連接周邊
- **感測與執行子系統**：IPCAM、Speaker、分音器、FP2、RobotArm board、機械手臂
- **網路子系統**：Wi‑Fi Router、測試 SSID 與設備網路分群
- **空間部署子系統**：車體（或場域）分區部署與配線路徑

---

### 1.3 Wi‑Fi 位置評估與配電配線規劃
1. 先依圖1確認 Wi‑Fi 設備（Router / AP / Extender）候選位置，優先覆蓋「人員主要操作動線」與「IPCAM 實際安裝區位」。
2. 針對每個候選位置，同步評估：
   - 配電可行性（插座距離、延長線路徑、固定方式）
   - 配線可行性（是否可拉 LAN 網路線、走線是否安全）
3. 依現場條件選擇連線方案（擇一）：
   - **LAN 有線回程**：可拉線且路徑安全時優先採用。
   - **Wi‑Fi Extender 無線延伸**：不易拉線或需跨區延伸時採用。
4. 完成設備定位、供電與線材固定，避免跨越活動機構與高風險區域。
5. 啟用後確認 SSID 為 `qa_rpt`，並記錄最終位置、供電點與連線方案（LAN / Extender）。

**驗證標準**
- [ ] Wi‑Fi 設備位置符合圖1覆蓋需求
- [ ] 已完成「LAN 或 Extender」方案選擇並記錄原因
- [ ] 配線與配電完成且固定
- [ ] `qa_rpt` 可穩定連線
- [ ] IPCAM 與主控端皆可連上 `qa_rpt`（至少抽查 1 台 IPCAM）

---

### 1.4 IPCAM 定位與配電（出貨前已完成 Wi‑Fi 設定）
> 送場機器之 IPCAM 已預先完成 Wi‑Fi 設定，現場僅需定位、配電與連線確認。

1. IPCAM 上電後，先確認可載入既有 Wi‑Fi 設定（`qa_rpt`）。
2. 依 1.3 的網路方案執行：可拉線則優先 LAN；否則使用已規劃完成之 Wi‑Fi Extender 區域。
3. 依圖1觀測位置擺放每台 IPCAM，確認視角覆蓋對應區域。
4. 完成配電與線材固定，避免壓線、拉扯與高熱區。
5. 建立標籤與對照（`CAM-xx` + 實際區位）。
6. **當 1.3 與 1.4 全部完成後，請通知台北團隊，安排遠端連入監看並協助位置微調。**

**驗證標準**
- [ ] 每台 IPCAM 都在圖1指定觀測位置
- [ ] 每台 IPCAM 供電穩定、可上線
- [ ] 主控端可讀取全部串流
- [ ] 已通知台北並完成遠端監看連入

---

### 1.5 Speaker 擺放、配電與配線（接 Scarlett 4i4）
1. 依圖1完成 Speaker 擺放，確保提示音可覆蓋測試區。
2. 完成每顆 Speaker 的配電與固定。
3. 依規劃完成配線並接回音訊介面。
4. 設定 Scarlett 4i4 放置位置（可維護、散熱與走線安全）。
5. Speaker 輸出線接到 Scarlett 4i4 對應輸出埠，並貼標籤。

**驗證標準**
- [ ] Speaker 擺位符合圖1
- [ ] Speaker 配電與配線完成
- [ ] Scarlett 4i4 位置固定且接線清楚

---

### 1.6 FP2 Sensor 定位、安裝與配電（Awning + Light4）

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

## 2. 主機位置配置（依現場狀態）

### 章節附圖
![System Layout](https://drive.google.com/uc?export=view&id=1_xDdE393fwM6hEDepC55_PjGOVfhiuoX)

*圖：System Layout（主機位置應依現場可維護區與走線路徑配置）*

### SOP 區塊（Chapter 2）
- **Objective（目的）**：依現場條件確認主機最終位置，兼顧散熱、維護性與線材可達性。
- **Preconditions（前置條件）**：Chapter 1 完成、圖1可對照、主機/電源/網路接口可用。
- **Procedure（程序重點）**：依序執行 **候選位置評估 → 電源與網路可達性確認 → 關聯設備走線檢查 → 主機固定與標記**。
- **Verification（驗證方式）**：依 2.3 勾核主機可維護性、電源網路穩定性、線材固定狀態。
- **Pass Criteria（通過標準）**：主機位置不阻礙作業，且供電/網路/關聯走線皆穩定。
- **Exceptions（例外處理）**：若受空間、散熱或走線限制，標記 `Blocked/Rework`，記錄替代位置與原因。

### 2.1 目的
根據現場實際空間、散熱、維護動線與線材長度，決定主機最終放置位置。

### 2.2 配置原則
- 優先選擇乾燥、通風、可維護位置
- 避免高熱區、潮濕區、易碰撞區
- 需兼顧到 USB Hub、燒錄器、音訊介面、機械手臂控制線之走線長度
- 可快速觸達電源與網路接口

### 2.3 驗證標準
- [ ] 主機位置不阻礙操作與維修
- [ ] 主機電源與網路連接穩定
- [ ] 關聯線材長度合理且固定完成

---

## 3. 燒錄器 / USB 延長線 / USB Hub 配置（連回 PC）

### 章節附圖
![Wiring Detail](https://drive.google.com/uc?export=view&id=1XE3O7h17guDEkzzsTE8ZMLZFj0ecc8tY)

*圖：Wiring Detail（燒錄器、Hub、延長線回連 PC 參考）*

### SOP 區塊（Chapter 3）
- **Objective（目的）**：完成燒錄器、USB 延長線與 USB Hub 的穩定拓樸，確保可持續回連 PC。
- **Preconditions（前置條件）**：主機位置已確定、Hub 與燒錄器可上電、PC 端可執行裝置辨識。
- **Procedure（程序重點）**：依序執行 **設備定位 → USB 路徑鋪設 → 拓樸連接（燒錄器→Hub→延長線→PC）→（Optional）標籤建立 → PC 端辨識確認**。
- **Verification（驗證方式）**：依 3.3 勾核辨識率、連線穩定性與配線安全。
- **Pass Criteria（通過標準）**：所有目標裝置可被 PC 穩定辨識，且長時間無間歇斷線。
- **Exceptions（例外處理）**：若延長線長度/品質不足或訊號不穩，標記 `Rework` 並更換路徑或線材。

### 3.1 目的
完成燒錄器、USB 延長線與 USB Hub 的拓樸配置，確保可穩定回連 PC。

### 3.2 配置步驟
1. 確認燒錄器與 USB Hub 的安裝位置（靠近維護區，避免受拉扯）。
2. 依現場路徑鋪設 USB 延長線，避開門片、活動機構與高熱區。
3. 完成連接：`燒錄器 -> USB Hub -> USB 延長線 -> PC`。
4. （Optional）可依需求建立連接線與連接口標籤（如 `H1-P01`、`USB-EXT-01`、`BURNER-01`）。
5. 在 PC 端確認裝置可被辨識並維持穩定連線。

### 3.3 驗證標準
- [ ] 所有燒錄器都可在 PC 端辨識
- [ ] USB 延長線與 Hub 配線固定且安全
- [ ] 長時間連線無間歇斷線

---

## 4. 機械手臂及面板配置

### 章節附圖
![Robot Arm Assembly](https://drive.google.com/uc?export=view&id=1z1aUfe4O4kPEcjyr5Lg8QLkneW-JKC36)

*圖：Robot Arm Assembly（機械手臂與面板安裝參考）*

### SOP 區塊（Chapter 4）
- **Objective（目的）**：完成機械手臂與面板安裝，確保固定可靠、線材正確連接且可安全上電。
- **Preconditions（前置條件）**：底座安裝面可用、相關線材齊備、上電前安全規範已確認。
- **Procedure（程序重點）**：依序執行 **初次 USB-A ↔ USB-C 連接 → 手臂底座固定 → 面板安裝 → 線材全連接檢查 → 上電前最終檢查**。
- **Verification（驗證方式）**：依 4.3 與 4.4 勾核固定狀態、配線安全與上電規範。
- **Pass Criteria（通過標準）**：機械手臂活動範圍正常、面板位置正確、配線符合安全規範。
- **Exceptions（例外處理）**：若活動干涉、接頭鬆動或線材受壓，標記 `Blocked/Rework`，修正後再上電。

### 4.1 目的
完成機械手臂與面板（控制板）安裝，確保固定、配線與操作安全。

### 4.2 配置步驟
1. 初次安裝時，先連接手臂後方 **USB‑A** 到手臂末端 **USB‑C**。
2. 依圖面完成機械手臂底座固定，確認活動範圍無干涉。
3. 安裝面板（如 3611A / 3611C / WF-3534）至指定位置。
4. 檢查線材是否都已連接完成，並確認不壓線、不跨越活動件。
5. 進行上電前最終檢查。

### 4.3 驗證標準
- [ ] 機械手臂固定牢靠、活動範圍正常
- [ ] 面板安裝位置正確且可維護
- [ ] 配線完成且符合安全規範

### 4.4 Safety, Power Isolation, and Power-On Rules

1. **接線與鎖附期間不得上電**
2. 所有線材插接完成後，先做方向與端子檢查再上電
3. UART 接法必須遵守：
   - `G -> G`
   - `RX -> TX`
   - `TX -> RX`
4. 線材不得壓在活動機構、踏階、門片、翻板下方
5. 機械手臂固定完成後，確認介面朝外、活動範圍無干涉
6. 最後一步才接入主電源並開機

---

## 5. Overview Review Status

### SOP 區塊（Chapter 5）
- **Objective（目的）**：完成全章節最終驗收與狀態判定，形成可交付結果。
- **Preconditions（前置條件）**：Chapter 1~4 皆已完成並有對應勾核紀錄。
- **Procedure（程序重點）**：依序執行 **章節結果回顧 → 缺失項目補正/標記 → 最終狀態填報 → Owner 簽核**。
- **Verification（驗證方式）**：檢查 5.1 與 5.2 欄位是否完整（Status、Blocked Reason、Sign-off、Date）。
- **Pass Criteria（通過標準）**：所有必填欄位完整且狀態可追溯（Ready/Blocked/Rework）。
- **Exceptions（例外處理）**：若資料缺漏，暫標 `Rework` 並回補後再結案。

### 5.1 章節總檢查
- [ ] Chapter 1：Overview + Wi‑Fi/IPCAM/Speaker/Scarlett4i4/FP2 完成
- [ ] Chapter 2：主機位置確認完成
- [ ] Chapter 3：燒錄器/USB 延長線/Hub/PC 連接完成
- [ ] Chapter 4：機械手臂與面板配置完成

### 5.2 最終狀態標記
- **Status**：`Ready / Blocked / Rework`
- **Blocked Reason**：`<若有阻塞請填寫>`
- **Owner Sign-off**：`<Owner Name>`
- **Date**：`YYYY-MM-DD`

---

## Appendix C — 現場驗收示意圖與填寫表

### C.1 示意圖（依圖一邏輯，不含 Wi‑Fi）
（已移除圖片，現場請以 Chapter 1 的圖1：System Layout 為主）

### C.2 一頁紙列印版（大欄位打勾）
- 檔案：`docs/ch1_onsite_acceptance_onepage_zh.md`

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
