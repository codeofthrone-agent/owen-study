# Gemini CLI（不透過 Hermes）安裝與使用流程

> 來源：google-gemini/gemini-cli 官方 README（GitHub）
> https://github.com/google-gemini/gemini-cli

## 目標
讓你在**不透過 Hermes**的情況下，直接用 Gemini CLI 在本機終端機操作。

---

# 流程總覽

```
[安裝 Gemini CLI]
        |
        v
[啟動 gemini]
        |
        v
[完成登入/金鑰設定]
        |
        v
[開始提問/自動化]
```

---

# Step 0. 先決條件
- 已安裝 **Node.js**（因為 CLI 透過 npm/npx 安裝）
- macOS / Linux / Windows 皆可

---

# Step 1. 安裝 Gemini CLI（擇一）

## 方式 A：免安裝（npx 直接跑）
```bash
npx @google/gemini-cli
```

## 方式 B：全域安裝（npm）
```bash
npm install -g @google/gemini-cli
```

## 方式 C：Homebrew（macOS / Linux）
```bash
brew install gemini-cli
```

## 方式 D：MacPorts（macOS）
```bash
sudo port install gemini-cli
```

## 方式 E：Conda（限制環境用）
```bash
conda create -y -n gemini_env -c conda-forge nodejs
conda activate gemini_env
npm install -g @google/gemini-cli
```

---

# Step 2. 啟動 Gemini CLI
```bash
gemini
```

首次執行會提示你進行登入 / 設定。

---

# Step 3. 驗證方式（擇一）

## ✅ 方法 1：Google OAuth 登入（最簡單）
```bash
gemini
```
接著按照瀏覽器登入流程完成 OAuth。

如需指定 Google Cloud Project：
```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
gemini
```

---

## ✅ 方法 2：使用 Gemini API Key
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
gemini
```

取得金鑰：
https://aistudio.google.com/apikey

---

## ✅ 方法 3：使用 Vertex AI
```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=true
gemini
```

---

# Step 4. 基本使用

## 互動模式
```bash
gemini
# 進入互動模式後直接輸入問題
```

## 單次指令模式
```bash
gemini -p "請幫我摘要這份 README"
```

## 指定模型
```bash
gemini -m gemini-2.5-flash
```

## JSON 輸出
```bash
gemini -p "請總結重點" --output-format json
```

---

# Step 5. MCP 伺服器（如果你要接工具）
Gemini CLI 的 MCP 設定寫在：
```
~/.gemini/settings.json
```

之後就能在 Gemini CLI 內使用 MCP 工具。

（詳細設定請參考官方文件：
https://www.geminicli.com/docs/tools/mcp-server ）

---

# Step 6. 確認是否成功
```bash
gemini -p "回答我：2+2=?"
```
若能輸出答案，表示安裝 + 驗證完成。

---

# 常見問題

**Q1：gemini 指令找不到？**  
A：請確認 npm 全域 bin 在 PATH，或用 `npx @google/gemini-cli` 直接跑。

**Q2：登入卡住？**  
A：重新 `gemini` 啟動並完成 OAuth 流程。

---

**Key Principle**：
> 先安裝 → 再啟動 → 再完成驗證，成功後才能用自動化。
