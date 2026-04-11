# 自架 Proxy：OAuth → API Key Bridge 計畫（Gemini CLI OAuth for PhoneClaw）

> 目標：讓依賴 OAuth 的上游憑證可被 PhoneClaw / Appium 工具鏈以「API 相容端點」方式使用。  
> 注意：此方案有維運與安全成本，建議僅在「無法使用原生 API Key」時採用。

---

## 1. 問題定義

PhoneClaw 多數 provider 走 API Key 流程；若你現有是 Gemini CLI OAuth，直接接入通常不可行。  
解法是新增一層 Proxy：

- 對外：提供 OpenAI-compatible 或 Gemini-compatible API
- 對內：使用 OAuth access token 呼叫 Google Gemini API

---

## 2. 目標能力（MVP）

1. `POST /v1/chat/completions`（OpenAI-compatible）
2. 轉譯為 Gemini `generateContent` 請求
3. 支援 streaming（SSE）
4. OAuth token 自動刷新（refresh token）
5. 基本配額/速率限制/審計日誌

---

## 3. 架構草圖

```text
PhoneClaw / Internal Clients
        |
        |  (API Key -> Proxy Internal Key)
        v
OAuth Bridge Proxy (FastAPI/Node)
   - auth middleware
   - model routing
   - request/response transform
   - token manager (OAuth refresh)
        |
        |  Bearer <OAuth Access Token>
        v
Google Gemini API
```

---

## 4. 安全與合規原則

- 僅內網可訪問（VPN / allowlist）
- Proxy API Key 與 OAuth refresh token 分離管理
- refresh token 只存 KMS/Secret Manager（不可進 repo）
- 全部請求記錄 `trace_id`（不記錄敏感 prompt 原文可選）
- 增加硬性上限：QPS、每日 token budget、最大 context 長度

---

## 5. 分階段計畫

### Phase A（1~2 天）PoC

- [ ] FastAPI 起一個 `/healthz`
- [ ] 實作 `/v1/chat/completions` 非串流
- [ ] 固定模型轉譯（如 `gemini-2.5-pro`）
- [ ] 單一 refresh token 自動換 access token

交付：curl 可打通 + 基本日志

### Phase B（2~4 天）可用版

- [ ] Streaming 回傳
- [ ] 錯誤碼映射（429/5xx）
- [ ] 基本限流（IP + key）
- [ ] Prometheus metrics

交付：PhoneClaw 可指向 proxy endpoint 實際運行

### Phase C（1 週）生產化

- [ ] 多租戶 key/配額策略
- [ ] 審計報表
- [ ] 失敗重試與熔斷
- [ ] 灰度模型路由

---

## 6. API 轉譯規格（最小）

### 輸入（OpenAI 風格）

```json
{
  "model": "gemini-proxy",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.2,
  "stream": false
}
```

### 轉譯（Gemini）

- 將 messages flatten 成 Gemini contents
- system 指令轉為最前段 policy prompt
- temperature/top_p 參數映射

### 輸出（OpenAI 風格）

```json
{
  "id": "chatcmpl-proxy-...",
  "object": "chat.completion",
  "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."}}]
}
```

---

## 7. 技術選型建議

- Runtime：Python FastAPI（你現有 QA 工具鏈 Python 為主）
- Token 管理：`google-auth` + refresh token cache
- 部署：Docker + reverse proxy (Caddy/Nginx)
- 監控：Prometheus + Grafana

---

## 8. 風險與替代方案

### 風險

- OAuth token 流程更脆弱（過期/權限變更）
- Proxy 成為單點故障
- 合規風險高於 API Key 直連

### 替代

1. **首選**：直接 Gemini API Key（最低維護）
2. 次選：OpenRouter Key 路由 Gemini
3. 最後：自架 OAuth bridge（本文件方案）

---

## 9. 實施前檢查清單

- [ ] 是否真的不能改用 API Key？
- [ ] 是否可接受增加一個 24/7 維運服務？
- [ ] 是否有 Secret Manager / KMS？
- [ ] 是否有監控與 on-call？

---

*建議：若目標是 QA 穩定性，優先 API Key；OAuth bridge 僅在策略限制下採用。*