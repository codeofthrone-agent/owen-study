# Gemini CLI + Chrome DevTools MCP：網站自動化完整流程

> 來源：Chrome DevTools MCP 官方 README / Tool Reference  
> https://github.com/ChromeDevTools/chrome-devtools-mcp

**立場（先說做什麼+為什麼）**：
我用官方 README + Tool Reference 來整理「Gemini CLI 串接 Chrome MCP 後，如何實際做網站自動化」，因為這是官方唯一能對齊工具名稱與設定方式的來源。

---

## 1) 你要達成的事情（白話）
- Gemini CLI 可以「指揮」Chrome 自動操作網頁
- Chrome DevTools MCP 讓 Gemini CLI 有一組「瀏覽器工具」（點擊、輸入、等待、截圖…）
- 這樣就能做 **網站自動化**（登入、表單、爬流程、截圖、檢查結果）

---

# 流程總覽（ASCII）
```
[安裝 Gemini CLI]
        |
        v
[安裝 Chrome DevTools MCP]
        |
        v
[Gemini CLI 設定 MCP]
        |
        v
[用 MCP 工具操作 Chrome]
        |
        v
[完成網站自動化]
```

---

# Step 0. 先決條件
- **Node.js >= 20.19**（官方需求）
- **Google Chrome / Chrome for Testing**
- **Gemini CLI 已可執行**

---

# Step 1. 安裝 Gemini CLI（擇一）
```bash
npx @google/gemini-cli
# 或
npm install -g @google/gemini-cli
# 或（macOS）
brew install gemini-cli
```

---

# Step 2. 安裝 Chrome DevTools MCP（Gemini CLI 內完成）
## ✅ 專案內（推薦）
```bash
gemini mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

## ✅ 全域（所有專案可用）
```bash
gemini mcp add -s user chrome-devtools npx chrome-devtools-mcp@latest
```

> 這是官方 README「Gemini CLI」段落給的正確命令。

---

# Step 3. 驗證 MCP 是否可用
進入 Gemini CLI 後，輸入：
```
列出可用的 MCP 工具
```
若看到 **chrome-devtools** 相關工具，代表完成。

---

# Step 4. 進行網站自動化（示範流程）

以下是「真正會動起來」的自動化動作步驟（工具名稱來自官方 Tool Reference）：

## ✅ 流程範例：
1. 開新頁面
2. 導航到網址
3. 擷取快照（拿到 uid）
4. 點擊 / 輸入 / 等待
5. 截圖
6. 關閉頁面

### ✅ Gemini CLI 提示詞範例
```
請用 MCP 工具完成以下自動化：
1) 開新分頁
2) 打開 https://example.com
3) 取得快照
4) 點擊登入按鈕
5) 輸入帳號密碼
6) 按 Enter
7) 等待文字 "Welcome" 出現
8) 截圖存檔
```

---

# Step 5. MCP 工具（你會常用的）
**導航 / 分頁**
- `new_page`：開新分頁
- `navigate_page`：跳網址
- `wait_for`：等文字出現
- `close_page`：關閉分頁

**互動**
- `take_snapshot`：抓取頁面元素 UID（後續點擊要用）
- `click`：點擊
- `fill`：填寫 input
- `type_text`：輸入文字
- `press_key`：按 Enter / Tab

**輸出**
- `take_screenshot`：截圖

---

# Step 6. 進階：如果你要控制「已登入 Chrome」
官方支援用 remote debugging port 連接「現有 Chrome」。

### ✅ macOS 啟動方式（官方 README）
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile-stable
```

### ✅ MCP 設定改成連已開 Chrome
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ]
    }
  }
}
```

⚠️ **警告**：開 remote debugging 會讓本機其他程式也有機會連上瀏覽器，請勿同時瀏覽敏感頁面。

---

# 風險表（非技術版）
| 風險 | 影響 | 緩解方式 |
|---|---|---|
| remote debugging 開著 | 瀏覽器可能被其他程式控制 | 用獨立 user-data-dir，測完就關 | 
| UID 會變 | 自動化點擊失效 | 每次操作前用 `take_snapshot` 重新抓 | 
| 站點有防機器人 | 自動化失敗 | 改用手動或更慢節奏操作 | 

---

# 小結
- **Gemini CLI + Chrome DevTools MCP 可以做到網站自動化**
- 官方提供的方式是 `gemini mcp add chrome-devtools npx chrome-devtools-mcp@latest`
- 自動化主要靠 MCP 工具（click / fill / wait / screenshot）

---

**Key Principle**：
> 先正確串 MCP，再用「snapshot → uid → click/fill」的節奏做自動化。 
