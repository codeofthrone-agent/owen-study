# 自動化測試系統安裝文件  
**Automation Test System Installation Guide**

> 文件類型：Standard Operating Procedure (SOP)  
> 版本：v1.1（Draft）  
> 最後更新：2026-05-08  
> 適用範圍：WFCO PwrPro 自動化測試環境（機械手臂 + 控制板 + Hub + IPCAM + Speaker + Wi‑Fi）

### SOP 文件控制
| 欄位 | 內容 |
|---|---|
| Owner | `<Owner Name>` |
| Reviewer | `<Reviewer Name>` |
| 生效日 | `YYYY-MM-DD` |
| 變更類型 | 章首總覽圖重排 + SOP 格式化 |

### SOP 使用方式
1. 依章節順序執行，禁止跳過安全檢查。  
2. 每章完成後，需勾選對應 checklist。  
3. 若現場條件與文件不符，先停作業並更新變更紀錄。

---

## 1. 系統 Overview（System Overview）

### 章節總覽圖（圖1 + 圖2）
![System Layout](https://drive.google.com/uc?export=view&id=1ZMmWd5I4OJ7QmjIPW4ioC2KNTBS-2iXt)

*圖1：System Layout（空間分區與設備擺位全貌）*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*圖2：Network and Device Topology（控制板、Hub、相機、手臂與網路關係）*

> 本章建立系統整體觀，先確認「空間佈局 + 網路拓樸」兩層基準，再進入接線與組裝程序。

### SOP 區塊（Chapter 1）
- **Objective（目的）**：定義系統邊界、網路拓樸與部署前提。
- **Preconditions（前置條件）**：設備清單、線材與工具齊備，且尚未上電。
- **Procedure（程序重點）**：完成範圍確認 → 拓樸核對 → 依 System Layout 完成擺設與接線。
- **Verification（驗證方式）**：以章末規則核對命名、線序與上電前安全條件。
- **Pass Criteria（通過標準）**：架構、擺設與接線確認完成，且無高風險未決項。
- **Exceptions（例外處理）**：若現場拓樸或設備與文件不符，立即停作業並更新變更紀錄。

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
- **I/O 與資料子系統**：USB Hub、延長線、影像與其他擴充周邊
- **感測與執行子系統**：IPCAM、Speaker、分音器、FP2、RobotArm board、機械手臂
- **網路子系統**：Wi‑Fi Router、測試 SSID 與設備網路分群
- **空間部署子系統**：車體（或場域）分區部署與配線路徑

---

### 1.3 Setup Wi‑Fi 位置、配線與配電
1. 先依圖1確認 Wi‑Fi 設備（Router / AP / Extender）放置位置，優先覆蓋主通道與 IPCAM 區域。
2. 完成電源配置（插座、延長線、固定方式），確保設備有穩定供電。
3. 完成網路配線（WAN/LAN）並固定線材，避免跨越活動機構。
4. 依現場需求二選一：
   - 直接接入網路線（有線回程）
   - 設定 Wi‑Fi Extender（無線延伸）
5. 啟用後確認 SSID 為 `qa_rpt`，並記錄設備位置與配線路徑。

**驗證標準**
- [ ] Wi‑Fi 設備位置符合圖1覆蓋需求
- [ ] 配線與配電完成且固定
- [ ] `qa_rpt` 可穩定連線

---

### 1.4 IPCAM 擺設與配電（依圖1觀測位置）
> IPCAM 先完成 Wi‑Fi/上電設定，再依圖1觀測位放置。

1. IPCAM 上電後確認已完成 SSID 設定（`qa_rpt`）。
2. 若現場允許，優先接入網路線；否則使用已配置完成之 Wi‑Fi Extender 區域。
3. 依圖1觀測位置擺放每台 IPCAM，確認視角覆蓋對應區域。
4. 完成配電與線材固定，避免壓線、拉扯與高熱區。
5. 建立標籤與對照（`CAM-xx` + 實際區位）。

**驗證標準**
- [ ] 每台 IPCAM 都在圖1指定觀測位置
- [ ] 每台 IPCAM 供電穩定、可上線
- [ ] 主控端可讀取全部串流

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
1. FP2 主要用於偵測 **Awning + Light4**，先依圖1定位目標偵測區。
2. 依附圖確認安裝朝向與覆蓋範圍：
   - https://drive.google.com/file/d/1WTaFEssc_zN6jul7jczow6FFsiC27zGp/view?usp=drive_link
3. 使用 FP2 磁鐵特性進行試貼定位，確認偵測正確後再固定。
4. 完成配電與線材固定，保留可拆裝維護空間。
5. 執行 Awning + Light4 觸發測試，記錄觸發成功區域。

**驗證標準**
- [ ] FP2 位置可穩定偵測 Awning + Light4
- [ ] 安裝方式可快速拆裝（磁吸）
- [ ] 配電完成且線材安全

---

### 1.7 Safety, Power Isolation, and Power-On Rules

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

## 2. 主機位置配置（依現場狀態）

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

### 3.1 目的
完成燒錄器、USB 延長線與 USB Hub 的拓樸配置，確保可穩定回連 PC。

### 3.2 配置步驟
1. 確認燒錄器與 USB Hub 的安裝位置（靠近維護區，避免受拉扯）。
2. 依現場路徑鋪設 USB 延長線，避開門片、活動機構與高熱區。
3. 完成連接：`燒錄器 -> USB Hub -> USB 延長線 -> PC`。
4. 建立埠位標籤（如 `H1-P01`、`USB-EXT-01`、`BURNER-01`）。
5. 在 PC 端確認裝置可被辨識並維持穩定連線。

### 3.3 驗證標準
- [ ] 所有燒錄器都可在 PC 端辨識
- [ ] USB 延長線與 Hub 配線固定且安全
- [ ] 長時間連線無間歇斷線

---

## 4. 機械手臂及面板配置

### 4.1 目的
完成機械手臂與面板（控制板）安裝，確保固定、配線與操作安全。

### 4.2 配置步驟
1. 依圖面完成機械手臂底座固定，確認活動範圍無干涉。
2. 安裝面板（如 3611A / 3611C / WF-3534）至指定位置。
3. 完成對應配線與標籤，保留必要 service loop。
4. 檢查線材不壓線、不跨越活動件。
5. 進行上電前最終檢查。

### 4.3 驗證標準
- [ ] 機械手臂固定牢靠、活動範圍正常
- [ ] 面板安裝位置正確且可維護
- [ ] 配線完成且符合安全規範

---

## 5. Overview Review Status

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
