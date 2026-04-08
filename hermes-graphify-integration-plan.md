# Hermes × Graphify 整合設計稿（含增量更新流程）

## 0) 目標與範圍
**目標**
- 讓 Hermes Agent 在「代碼/文檔/論文」上有**結構化圖譜索引**能力
- 支援 **行號級定位、跨文件/跨論文關聯追溯**
- 支援 **PR merge 後增量更新**，避免索引老化

**非目標**
- 不更換 Hermes 既有的語義檢索；是「增強層」
- 不強制所有 repo 都圖譜化（先做 PoC）

---

## 1) 系統架構（高階）
```
┌─────────────────────────────────────────────────────────────┐
│                         Hermes Agent                        │
│  (Tools: read/search/patch, delegate, terminal, etc.)        │
└───────────────┬─────────────────────────────────────────────┘
                │ query: user prompt / tool request
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Graphify Index Layer                     │
│  - AST Graph builder                                         │
│  - Semantic extractor                                        │
│  - Graph store (nodes/edges)                                 │
│  - Query API (BM25 / symbol / path / explain)                │
└───────────────┬─────────────────────────────────────────────┘
                │ pointers/locs (file, line, symbol, relation)
                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Hermes Retrieval + Reasoning                │
│  - map results → file paths                                  │
│  - read_file / search_files / patch                          │
│  - response synthesis                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2) 核心整合策略

### 2.1 Graphify 作為「索引層」
**目標**：把「repo / 文檔 / 論文」編成可查詢圖譜  
**Hermes 的角色**：
- 查詢 Graphify → 取得精準定位結果 → 再用 Hermes 現有 file tools 做深讀/修改

**查詢類型（對應 Graphify 能力）**
- **symbol/definition**：找函式/類別定義
- **path**：從論文段落 → 對應到實作檔案/行號
- **explain**：取得圖譜層的連結與語義解釋

### 2.2 增量更新（PR merge 後）
**目標**：只更新 changed files  
**觸發點**：
- CI / GitHub Actions / 手動指令（PoC 可手動）

**流程概念**
```
PR merged
   ├─> collect changed files (git diff --name-only)
   ├─> graphify update --files <list>
   └─> update graph store
```

---

## 3) 整合流程（詳細步驟）

### 3.1 初始建圖（首次索引）
1. Hermes 觸發 `graphify build`（repo 全量）
2. Graphify 產出圖譜（AST + semantic）
3. 存到 `graphify_store/`（本地或共享儲存）

**輸出**
- nodes/edges/metadata
- file/line/symbol 的索引映射

### 3.2 Hermes 查詢（標準路徑）
```
User prompt → Hermes 
   → graphify query (symbol / bm25 / path / explain)
   → return: file path + line ranges + relation nodes
   → Hermes read_file / search_files
   → LLM synthesis
```

### 3.3 增量更新（PR merge）
```
PR merged → changed files list
   ├─> graphify update --files
   └─> graph store updated
```

**關鍵點**
- 保持「語義 + AST」雙通道一致
- 更新後更新 metadata version / index timestamp

---

## 4) 實作建議（PoC → MVP → Scale）

### 4.1 PoC（1 個 repo）
**目的**：驗證 Graphify 是否可用在 Hermes pipeline  
**範圍**：
- 只做 build + query + explain  
- 不做自動化更新

### 4.2 MVP（多 repo + 增量更新）
**加入**：
- PR merge 觸發 `graphify update`
- 路徑映射 / file line 轉 Hermes read_file

### 4.3 Scale（組織級）
**加入**：
- 索引儲存共享（PVC / S3）
- 查詢快取
- 多 Hermes 實例共用圖譜

---

## 5) Hermes 內部設計擴充點

### 5.1 新增 Tool：`graphify_query`
**用途**：查圖譜 → 回傳定位結果  
**輸出 schema**：
```json
{
  "hits": [
    {"file": "src/foo.rs", "start": 120, "end": 165,
     "symbol": "Foo::bar", "score": 0.92, "relations": [...]} 
  ],
  "graph_version": "2026-04-08",
  "index_ts": "..."
}
```

### 5.2 新增 Tool：`graphify_update`
**用途**：增量更新  
**輸出**：成功/失敗 + 更新檔案數

### 5.3 Hermes Prompt Routing
- 若是「探索/關聯/跨文件」問題 → 先查 graphify
- 若是「明確 file」→ 直接 read_file

---

## 6) 資料流與觸發（ASCII Diagram）
```
            ┌────────────┐
User ──────►│ Hermes LLM │
            └─────┬──────┘
                  │
                  │ graphify_query
                  ▼
        ┌─────────────────────┐
        │ Graphify Index Store│
        └─────────┬───────────┘
                  │
                  ▼
        Hermes file tools → synthesis
```

**增量更新**：
```
PR merge
   └── git diff --name-only
       └── graphify_update --files
           └── index store refreshed
```

---

## 7) 風險表

| 風險 | 影響 | 緩解 |
|---|---|---|
| Graphify 索引過期 | Hermes 回答錯誤定位 | PR merge 強制 update |
| AST/語義解析失敗 | 無法定位 | fallback 到 Hermes 既有搜索 |
| 多 repo 儲存膨脹 | 成本上升 | 局部索引 + repo 分片 |
| 工具鏈依賴變動 | 整合中斷 | 版本鎖定 + health check |

---

## 8) 驗證標準（可量化）
- Query 是否能返回 **行號級定位**
- PR 合併後更新時間 < 1 min（小 repo）
- Hermes 在回答中引用的檔案與圖譜位置一致

---

## 9) 交付清單
- [ ] Graphify build + query + update 腳本  
- [ ] Hermes tool wrapper（graphify_query / graphify_update）  
- [ ] PR merge hook（GitHub Actions / CI）  
- [ ] 整合 demo （一個 repo）

---

## Key Principle
**Graphify 是「索引層」，Hermes 是「推理層」；讓結構化圖譜處理定位，讓 Hermes 專注理解與生成。**
