# 自動化測試系統安裝文件  
**Automation Test System Installation Guide**

> 版本：v1.0（Draft）  
> 最後更新：2026-05-08  
> 適用範圍：WFCO PwrPro 自動化測試環境（機械手臂 + 控制板 + Hub + IPCAM + Speaker + Wi‑Fi）

---

## 1. 系統 Overview（System Overview）

### 章節總覽圖（圖1 + 圖2）
![System Layout](https://drive.google.com/uc?export=view&id=1ZMmWd5I4OJ7QmjIPW4ioC2KNTBS-2iXt)

*圖1：System Layout（空間分區與設備擺位全貌）*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*圖2：Network and Device Topology（控制板、Hub、相機、手臂與網路關係）*

> 本章建立系統整體觀，先完成「空間佈局 + 網路拓樸 + 外設安裝基準」，再進入接線與組裝程序。

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
- **I/O 與資料子系統**：USB Hub、延長線、microSD 裝置組
- **感測與執行子系統**：IPCAM、Speaker、分音器、FP2、RobotArm board、機械手臂
- **網路子系統**：Wi‑Fi Router、測試 SSID 與設備網路分群
- **空間部署子系統**：車體（或場域）分區部署與配線路徑

---

### 1.3 IPCAM 擺設與接線（依 System Layout）
> 依圖1（System Layout）先定點位、再走線，禁止先接線再找位置。

1. 依圖1將 IPCAM 分配到對應區位（入口 / 主通道 / 手臂作業區 / 死角補盲區）。
2. 每台 IPCAM 安裝後，先確認視角覆蓋該區主要路徑，再鎖固。
3. 線路沿圖1標示的櫃體後方或線槽路徑回收至 Hub，不可跨越活動機構。
4. 於 Hub 端建立埠位對照：`CAM-xx -> Hx-Pxx`，同步貼標到相機端與 Hub 端。
5. 依圖2拓樸完成網路接入（SSID：`qa_rpt`），確認主控可讀取串流。

**驗證標準（擺設 + 接線）**
- [ ] 每台 IPCAM 位置與圖1區位一致
- [ ] 每台 IPCAM 的線路可追溯到唯一 Hub 埠位
- [ ] 主控端可讀取全部串流且無明顯掉幀

---

### 1.4 Speaker / 分音器 擺設與接線（依 System Layout）
> Speaker 先依圖1分區擺設，再依圖2拓樸做分音器配線。

1. Speaker 依圖1分區均勻放置，優先覆蓋測試提示可聽區，避免集中單側。
2. 分音器（Audio Splitter）安裝於主音源與 Speaker 分支之間，固定於可維護區。
3. 依圖1既有線路通道完成配線：主音源 -> 分音器輸入 -> 各 Speaker 輸出。
4. 建立配線對照：`AUD-SPLIT-01-OUTx -> SPK-0x`，並將標籤貼於兩端。
5. 逐路播放測試音（OUT1~OUTn），確認每一路對應正確 Speaker。

**驗證標準（擺設 + 接線）**
- [ ] Speaker 實際位置與圖1分區一致
- [ ] 分音器每個輸出埠皆有對應 Speaker 且標籤一致
- [ ] 任一路測試音都能在預期分區聽到，不串路

---

### 1.5 FP2（Sensor）擺設與接線（依 System Layout）
> FP2 安裝需以圖1主要感測區為準，不可只依現場方便位置。

1. 依圖1將 FP2 安裝在主要感測區可覆蓋位置（避開大型金屬面與強反射面）。
2. 確認安裝角度可覆蓋對應區域動線，不被櫃體、門片、手臂遮擋。
3. 依圖1路徑完成供電與通訊線路，並回收到指定 Hub/閘道節點。
4. 依圖2拓樸完成配對與命名：`SEN-FP2-01`（若多顆依序編號）。
5. 以區域走動測試驗證觸發結果與圖1感測區一致。

**驗證標準（擺設 + 接線）**
- [ ] FP2 實際位置與圖1感測區規劃一致
- [ ] FP2 線路可追溯到指定 Hub/閘道節點
- [ ] 觸發事件可對應到正確區域，無明顯誤報/漏報

---

### 1.6 Network Architecture and Prerequisites

#### A. 基本網路設定
- 測試 Wi‑Fi SSID：`qa_rpt`
- 測試 Wi‑Fi Password：`12345678`

> 實務建議：部署前建立「正式版」與「Lab版」兩組憑證，避免測試網外流。

#### B. IP 規劃建議
- Router/Gateway：固定 IP（例：192.168.50.1）
- 控制主機：固定 IP（或 DHCP reservation）
- IPCAM：固定 IP / 保留 DHCP 租約
- 機械手臂控制節點：固定 IP

#### C. 帳密保管規範
- 不將明文密碼寫在公開文件
- 正式文件以 `***` 遮蔽，憑證放安全保管庫
- 變更網路憑證時需同步更新驗收腳本

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

## 2. Control Boards and Hubs Wiring Guide

### 2.1 Control Board Roles and Interface Map
- **3611A / 3611C**：分區控制/介面板
- **WF-3534**：板間連接與控制匯流節點
- **RobotArm board**：手臂控制相關邏輯板

---

### 2.2 Hub Topology and Port Allocation
建議採「主 Hub -> 子 Hub -> 終端裝置」分層：

- 主 Hub：連接主控機與主要 I/O
- 子 Hub A：microSD 群組 x2
- 子 Hub B：microSD 群組 x6
- 子 Hub C：影像/周邊擴充（依實際）

> 每個埠位請建立唯一標籤：`H1-P01`, `H1-P02`, `H2-P01`...

---

### 2.3 Cable and Connector Standards
- USB Type‑A：一般資料/周邊連接
- L-Type C to A：板對板或控制板對介面盒
- UART：板間通訊，需交叉 RX/TX
- 延長線：超過 5m 需評估供電與訊號品質

---

### 2.4 Wiring Rules and Direction Requirements
接線方向規則（依圖示）：

- `First Right`
- `First Top`
- `First Bottom`

方向規則必須和實際板件型號一致；不同板可能有不同第一腳位方向。  
如未確認，禁止強插。

#### 接線特寫與方向參考
![Wiring Detail](https://drive.google.com/uc?export=view&id=1XE3O7h17guDEkzzsTE8ZMLZFj0ecc8tY)

---

### 2.5 Wiring Labels, Node IDs, and Routing Table

#### A. 節點命名（範例）
- `WF-3611-A`（左側/入口區）
- `WF-3611-C`（中右/走道區）
- `WF-3611-B`, `WF-3610-B`, `WF-3511-B`（Pass-thru storage）

#### B. 配線表模板（建議）
| Cable ID | Source | Destination | Connector Type | Route | Label | Status |
|---|---|---|---|---|---|---|
| C-001 | WF-3534 | 3611A | USB-C(A角) | 左中櫃後 | WF-3611A-L1 | Installed |
| C-002 | WF-3534 | 3611C | USB-C(A角) | 中央走道下 | WF-3611C-L1 | Installed |
| C-003 | UART-01 | Control Header | G/RX/TX | 板間短距離 | UART-X | Verify |

---

### 2.6 Verification Checklist for Board-to-Hub Connections
- [ ] 所有 Hub 有供電
- [ ] 主控機可識別 Hub 與讀卡裝置
- [ ] UART 線序正確（G/G，RX/TX 交叉）
- [ ] 線材標籤已貼妥
- [ ] 無鬆脫、無過度彎折、無夾線

---

### 2.7 Common Wiring Errors and Quick Recovery
| 症狀 | 可能原因 | 快速處置 |
|---|---|---|
| 裝置無法被辨識 | Hub 埠位接錯/供電不足 | 改接主 Hub、確認電源 |
| 串口無回應 | RX/TX 沒交叉或接反 | 重新核對線序 |
| 不穩定斷線 | 延長線過長/訊號衰減 | 改短線、改有源延長器 |
| 啟動後設備離線 | 網路未入同一 SSID | 重連 `qa_rpt`、檢查 DHCP |

---

## 3. Robotic Arm and Base Hardware Assembly

### 3.1 Assembly Preparation
- 確認底板、固定座、雙面膠、螺絲齊全
- 準備 3611A / 3611C / WF-3534 與線材
- 確認機械手臂包裝內螺絲規格

---

### 3.2 Step-by-Step Assembly

#### Step 1 — 固定座與膠貼定位
- 撕除膠帶保護層
- 將固定座貼至指定位置（避開預留孔位）

#### Step 2 — 安裝 3611A / 3611C
- 將兩片面板插入對應槽位
- 使用螺絲固定（勿過扭）

#### Step 3 — 板件接線
- 連接 WF-3534、L 型 Type‑C/Type‑A、UART
- UART 依 `G/G, RX/TX 交叉` 原則接線

#### Step 4 — 翻面與機械手臂固定
- 後側線材接妥後翻面
- 將手臂放上底板，**介面朝外**
- 鎖附固定螺絲

#### Step 5 — 上電前最終檢查
- 檢查手臂活動範圍、線材餘量、固定點
- 完成後才允許接入電源

#### 機械手臂組裝流程圖
![Robot Arm Assembly](https://drive.google.com/uc?export=view&id=1z1aUfe4O4kPEcjyr5Lg8QLkneW-JKC36)

---

### 3.3 Mechanical and Cable Safety Notes
- 線材需留 service loop，避免手臂運動拉扯
- 線材不可跨越高熱區（HVAC）與鋒利邊緣
- 線束與活動件至少保留 20~30mm 安全距離（可依現場調整）

---

## 4. Device Spatial Deployment and Positioning

### 4.1 Zoning Strategy
依場域分區部署（Zone 1~4）：
- Zone 1：客廳/主動線
- Zone 2：廚房/中段
- Zone 3：衛浴/過道
- Zone 4：臥室/前艙

---

### 4.2 Device Placement Guidelines
#### IPCAM
- 優先覆蓋入口、主通道、手臂作業區
- 避免逆光、鏡面反射、遮擋死角

#### Speaker
- 分區部署，避免集中單側
- 距離控制板與高干擾線束保持間距

#### RobotArm board
- 優先放在可維護區域（如 pass-thru storage 附近）
- 需便於檢修與重新插拔

---

### 4.3 Routing Constraints
- 不走潮濕區裸露路徑
- 不穿越頻繁開合的門片/翻板邊
- 盡量沿既有櫃體後方、地板下或固定線槽走線

---

### 4.4 Maintenance Accessibility
- 節點標籤朝外
- 保留測試點可觸達
- 每個區域至少保留一個可開啟檢修窗口

---

## 5. Commissioning, Validation, and Troubleshooting

### 5.1 Pre-Power Checklist
- [ ] 所有螺絲已固定
- [ ] 線序與方向核對完成
- [ ] Hub 與控制板連接完成
- [ ] 網路設定確認（SSID/密碼）
- [ ] 手臂活動區無干涉
- [ ] 安全人員已確認可上電

---

### 5.2 Power-On Sequence
1. 啟動路由器與網路設備  
2. 啟動主控與 Hub  
3. 啟動控制板與手臂系統  
4. 確認音訊設備指示燈（綠燈）  
5. 驗證 IPCAM 與喇叭在線狀態

---

### 5.3 Functional Validation
- **網路**：所有設備可進入 `qa_rpt`
- **板件**：3611A/3611C/WF-3534 通訊正常
- **UART**：回應正常，無封包錯誤
- **影像**：相機串流可讀
- **音訊**：喇叭可觸發播放/提示
- **手臂**：可完成基礎動作且無異音/抖動

---

### 5.4 Common Failures and Recovery
| Failure | Checkpoint | Action |
|---|---|---|
| Router 正常但設備離線 | SSID/密碼/DHCP | 重新配網、重啟設備 |
| 板件無通訊 | UART 線序 | 重接 RX/TX |
| 裝置間歇掉線 | Hub 供電/延長線 | 改善供電、縮短線長 |
| 手臂動作異常 | 固定點/線束干涉 | 重新理線與校正姿態 |

---

### 5.5 Acceptance Criteria and Handover
驗收完成需達成：

- [ ] 全部關鍵設備在線且可控制
- [ ] 連續運作測試通過（建議 >= 30 分鐘）
- [ ] 接線表、埠位表、節點表已更新
- [ ] 現場照片與版本紀錄已歸檔
- [ ] 故障排除SOP已交接

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
