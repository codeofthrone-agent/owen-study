# 網頁測試自動化 — 調查報告

> 📅 更新日期：2026-04-07
> 🔍 調查範圍：最新工具、最佳實踐、效率最佳化策略

---

## 📑 目錄

1. [核心結論](#核心結論)
2. [工具比較矩陣](#工具比較矩陣)
3. [推薦技術棧](#推薦技術棧)
4. [標準自動化工作流 (SOP)](#標準自動化工作流-sop)
5. [批次效率最佳化](#批次效率最佳化)
6. [Pitfalls 與風險管理](#pitfalls-與風險管理)
7. [附錄：工具選擇決策樹](#附錄工具選擇決策樹)

---

## 🎯 核心結論

現代網頁測試自動化的趨勢是 **Agent-Driven Automation**——不再手寫脆弱的 CSS Selector / XPath，而是由 AI 理解頁面結構後動態操作。

**最佳實踐架構：**
- **UI 互動 / JS-Rendered 頁面** → `agent-browser` (Vercel 開源)
- **API / 資料驗證** → `curl`
- **大量並行測試** → `delegate_task` 平行委派

### 為何這樣最有效率？

| 優勢 | 說明 |
|------|------|
| ⚡ 效能 | Rust 二進制，啟動速度比 Playwright Python binding 快 3-5x |
| 🧠 AI 可觀測 | 回傳 accessibility snapshot，元素帶 `@eN` 自動編號，無需手寫 selector |
| 🔧 混合模式 | API 走 curl，UI 走 browser，各取所長 |
| 🔄 動態定位 | 不依賴固定 selector，即使網頁改版也能正確找到目標元素 |

---

## 📊 工具比較矩陣

| 工具 | 語言 | 速度 | AI 友善度 | 維護成本 | 適用場景 |
|------|------|------|-----------|----------|----------|
| **agent-browser** | Rust CLI | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 極低 | AI Agent 自動化 |
| Playwright | Node.js / Python | ⚡⚡⚡ | ⭐⭐ | 中 | 傳統 E2E 測試 |
| Puppeteer | Node.js | ⚡⚡⚡ | ⭐ | 高 | Chromium 專用 |
| Selenium | 多語言 | ⚡⚡ | ⭐ | 高 | 跨瀏覽器老專案 |
| Cypress | Node.js | ⚡⚡⚡ | ⭐⭐ | 中 | 前端單元+E2E |
| **curl** | CLI | ⚡⚡⚡⚡⚡ | N/A | 極低 | API 測試 |

---

## 🛠️ 推薦技術棧

### agent-browser (主要工具)

由 [Vercel Labs](https://github.com/vercel-labs/agent-browser) 開發的開源瀏覽器自動化 CLI。

**安裝：**
```bash
npm install -g agent-browser
agent-browser install  # 首次下載 Chrome for Testing
```

**命令對照表：**

| 操作 | 命令 |
|------|------|
| 導航 | `agent-browser open <url>` |
| 取得元素快照 | `agent-browser snapshot` |
| 點擊 | `agent-browser click @eN` |
| 填寫表單 | `agent-browser fill @eN "text"` |
| 鍵盤輸入 | `agent-browser key Enter` |
| 捲動 | `agent-browser scroll down` |
| 截圖 | `agent-browser screenshot --annotate` |
| 等待內容 | `agent-browser wait --text "Welcome"` |
| 批次模式 | `echo '[...]' \| agent-browser batch --json` |
| 關閉 | `agent-browser close` |

---

## 📋 標準自動化工作流 (SOP)

### Step 1：導航 + 建立地圖
```bash
agent-browser open "https://目標網址"
agent-browser snapshot
```
`snapshot` 回傳結構化的 accessibility tree，每個可互動元素標示 `@eN` 參考編號。

### Step 2：精準操作
```bash
# 點擊按鈕
agent-browser click @e15

# 填寫搜尋框
agent-browser fill @e20 "測試關鍵字"

# 送出表單
agent-browser key Enter
```

### Step 3：驗證結果
```bash
# 取得新的 snapshot 確認頁面變化
agent-browser snapshot

# 截圖比對（視覺驗證）
agent-browser screenshot --annotate
```

### Step 4：結束工作
```bash
agent-browser close
```

---

## ⚡ 批次效率最佳化

### 方法一：Batch Mode（無中間判斷的連續操作）

一次呼叫完成多個步驟，避免重複啟動 CLI 的開銷：

```bash
echo '[
  ["open", "https://example.com"],
  ["snapshot", "-i"],
  ["click", "@e5"],
  ["fill", "@e8", "hello@example.com"],
  ["key", "Enter"],
  ["wait", "2000"],
  ["screenshot", "result.png"]
]' | agent-browser batch --json
```

### 方法二：Agent 平行委派（多頁面/多帳號並測）

使用 `delegate_task` 將不同測試場景拆分，平行執行：
- 任務 A：測試登入流程
- 任務 B：測試搜尋功能
- 任務 C：測試結帳流程

### 方法三：混合模式（API + UI）

```
API 驗證 ← curl (秒回)
    ↓ 確認 API 正常
UI 測試 ← agent-browser (需要 JS 渲染才測)
    ↓ 驗證畫面
結果彙整 ← 自動化報告
```

---

## ⚠️ Pitfalls 與風險管理

| 風險 | 說明 | 解法 |
|------|------|------|
| **Stale Refs** | 頁面跳轉或動態更新後，舊的 `@eN` 編號失效 | 每次操作前重新 `snapshot` |
| **Session 持續** | `agent-browser` 維持 Chrome 狀態 | 測試完務必 `agent-browser close` |
| **首次執行** | 需先下載 Chrome | 執行 `agent-browser install` |
| **Viewport 太小** | 預設視窗可能影響 mobile 版面測試 | `agent-browser set viewport 1280 720` |
| **文字編碼** | 填表時含空格的文字需加引號 | `fill @e3 "hello world"` |
| **Console 存取** | 沒有內建 console reader | 用 JS eval workaround |
| **超時** | 重度 JS 頁面可能逾時 | terminal 呼叫需設 `timeout` 參數 |

---

## 🌿 附錄：工具選擇決策樹

```
需要測試網頁？
│
├─ 只有 API / JSON 資料？
│   └── 使用 → curl ✅
│       • 檢查 HTTP status
│       • 驗證 JSON response
│       • Webhook 測試
│
├─ 需要 JavaScript 渲染？
│   └── 使用 → agent-browser ✅
│       • SPA / React / Next.js
│       • 表單填寫 / 登入流程
│       • Session / Cookie 管理
│       • 截圖 / 視覺驗證
│
├─ 需要大量並行測試？
│   └── 使用 → delegate_task + agent-browser ✅
│       • 平行執行多個測試場景
│       • 各自獨立 Chrome 實例
│
└─ 靜態 HTML / 簡單爬蟲？
    └── 使用 → curl 或 Python requests ✅
```

---

## 💡 Key Principle

> **Don't script selectors, script intentions.**

舊時代的自動化：寫死 `driver.find_element(By.CSS, "#submit-btn")`  
→ **一旦網頁改版，全部測試掛掉。**

AI 時代的自動化：「點下 Submit 按鈕」  
→ **Agent 動態讀取 `snapshot`，自己找到當下正確的元素編號。**

這才是現代網頁測試自動化的護城河：**意圖驅動 (Intent-Driven) > Selection 驅動**。
