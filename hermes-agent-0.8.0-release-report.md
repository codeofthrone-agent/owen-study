# Hermes Agent 0.8.0 發布調查報告（給非專業人員）

**立場（先說做什麼+為什麼）**：
我先用 GitHub 官方 API 直接查 Hermes Agent 的 Release 列表，因為這是最準確的「是否發布」來源，能避免新聞或社群貼文誤傳。

---

## 1) 結論（一句話）
**Hermes Agent v0.8.0 已發布**，在 GitHub 釋出頁面標題為 **「Hermes Agent v0.8.0 (v2026.4.8)」**，發佈日期為 **2026-04-08**。

**官方來源（GitHub Release API）**：
- API：`https://api.github.com/repos/NousResearch/hermes-agent/releases`
- 釋出頁面：`https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.8`

---

## 2) 給非專業人員的簡單解釋
可以把 Hermes Agent 想成「會用工具的 AI 助理」。
0.8.0 這次更新像是：
- **幫助你等任務完成的通知**（例如跑很久的測試、下載、訓練）
- **可以在聊天中臨時換腦袋（模型）**
- **更穩定、更安全，不容易出錯或中斷**

也就是：**更好用、更會提醒、比較不會出問題**。

---

## 3) 重點更新（白話版）
以下是 Release 內容裡最影響一般使用者的幾點（用白話翻譯）：

1. **任務完成自動通知**（Background Process Auto-Notifications）  
   - 以前你要自己一直問「好了沒」，現在任務跑完會主動通知你。

2. **聊天中換模型**（Live Model Switching /model）  
   - 你可以在對話中直接換 AI 模型，不用重開。

3. **更穩的安全防護**（Security Hardening）  
   - 防止亂改檔案、危險指令、路徑攻擊等。

4. **支援更多平台與修復大量 Bug**  
   - Telegram / Discord / Slack 等平台功能更完整，錯誤更少。

---

## 4) ASCII 流程圖（從「聽說發布」到「確認」）

```
[聽說 Hermes Agent 0.8.0 發布]
                |
                v
     [查官方 Release API]
                |
                v
  [找到 release: v0.8.0 (v2026.4.8)]
                |
                v
        [確認發布日期]
                |
                v
           [結論：已發布]
```

---

## 5) 重要證據（可驗證）
**GitHub Release API 回應中的關鍵欄位：**
- `tag_name`: `v2026.4.8`
- `name`: `Hermes Agent v0.8.0 (v2026.4.8)`
- `published_at`: `2026-04-08T11:56:44Z`

**來源指向：**
- API：`https://api.github.com/repos/NousResearch/hermes-agent/releases`
- Release 頁面：`https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.8`

---

## 6) 風險表（非技術角度）

| 風險 | 可能影響 | 緩解方式 |
|---|---|---|
| 更新太大，設定不相容 | 舊設定可能出錯 | 升級前先備份設定檔 |
| 新功能不熟 | 使用流程改變 | 先看 release 說明 + 小範圍測試 |
| 外部平台變動 | 某些平台功能暫時異常 | 先在一個平台試運行 |

---

## 7) 小結
Hermes Agent 0.8.0 **確定已發布**。此次版本屬於「**功能明顯進化 + 穩定性/安全性大幅提升**」的更新，非常值得留意。

---

**Key Principle**：
> 先用官方 Release API 確認事實，再決定要不要升級。 
