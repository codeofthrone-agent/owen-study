# Claude ACP 跨電腦設定文件（Claude Code + acpx）

> 目的：讓另一台電腦可以**穩定**使用 Claude ACP（透過 `acpx` adapter）。

## 0) 已驗證版本（本機）

- Claude Code: `2.1.89`
- acpx: `0.5.3`
- Node.js: `v25.8.2`
- npm: `11.11.1`

> 建議新機至少維持同等主版號，避免 ACP 相容性差異。

---

## 1) 安裝必要元件

```bash
# 1) 安裝 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 2) 安裝 acpx（ACP adapter）
npm install -g acpx
```

確認安裝路徑與版本：

```bash
which claude
claude --version

which acpx
acpx --version
```

---

## 2) 登入 Claude

### A. Pro/Max 帳號登入（建議）

```bash
claude
# 第一次啟動會引導 browser OAuth 登入
```

### B. API key 方式（可選）

```bash
export ANTHROPIC_API_KEY='你的金鑰'
```

檢查登入狀態：

```bash
claude auth status --text
```

成功條件：要看到 Login method / Organization / Email。

---

## 3) ACP 連線冒煙測試（最重要）

```bash
acpx --timeout 60 claude exec "Reply exactly: ACP_OK"
```

成功條件：

- 輸出包含 `ACP_OK`
- 且流程有 `initialize`、`session/new`、`end_turn`

---

## 4) 你在 Hermes 中的標準呼叫方式

```bash
acpx --timeout 120 claude exec "<你的任務描述>"
```

建議加上 timeout，避免卡住時無限等待。

---

## 5) 常見錯誤與排除

### 問題 A：`claude: command not found`
- 原因：CLI 未安裝或 PATH 未載入
- 解法：
  1. 重新執行 `npm install -g @anthropic-ai/claude-code`
  2. 確認 `which claude`
  3. 重開 terminal（或重載 shell rc）

### 問題 B：`acpx: command not found`
- 原因：acpx 未安裝或 PATH 問題
- 解法：
  1. `npm install -g acpx`
  2. `which acpx`

### 問題 C：`auth` 相關錯誤 / 無法執行
- 原因：尚未登入或憑證失效
- 解法：
  1. 先跑 `claude auth status --text`
  2. 不正常就重新 `claude` 登入一次

### 問題 D：ACP 指令有回應但任務失敗
- 原因：通常是 prompt 不夠具體、timeout 太短或環境缺依賴
- 解法：
  1. 增加 timeout（例如 180）
  2. 縮小任務範圍重試
  3. 先單獨測 `claude` 本體，再測 `acpx`

---

## 6) 新機快速驗收清單（複製即用）

```bash
which claude && claude --version
which acpx && acpx --version
claude auth status --text
acpx --timeout 60 claude exec "Reply exactly: ACP_OK"
```

全部成功即可判定：**新機 Claude ACP 可用**。

---

## 7) 安全建議

- 不要把 `ANTHROPIC_API_KEY` 明文寫入可公開 repo。
- 若使用 shell profile 儲存金鑰，注意檔案權限（例如 `~/.zshrc`）。
- 共用電腦建議使用 OAuth，並定期檢查 `claude auth status`。

---

## 8) 結論

跨電腦可移植的最小集合只有三件事：

1. `claude` CLI 安裝成功
2. `acpx` adapter 安裝成功
3. `acpx ... "ACP_OK"` 冒煙測試通過

這三項都過，就代表 Claude ACP 主鏈路已打通。
