# 研究報告：MemPalace AI Memory System 與 LLM-Wiki Skill

**調查日期:** 2026-04-07  
**調查者:** zero  
**調查對象:** 
1. [`milla-jovovich/mempalace`](https://github.com/milla-jovovich/mempalace) — AI memory system
2. [`NousResearch/hermes-agent#5100`](https://github.com/NousResearch/hermes-agent/pull/5100) — Karpathy LLM-Wiki skill 整合

---

## 一、MemPalace — The AI Memory System

### 基本資訊

| 欄位 | 值 |
|------|-----|
| 版本 | 3.0.0 |
| 語言 | Python 3.9+ |
| Stars | 4,075 🌟 |
| Forks | 403 |
| License | MIT |
| 最後更新 | 2026-04-06 |
| 依賴 | chromadb>=0.4.0, pyyaml>=6.0 (zero API dependency) |

### 核心主張

MemPalace 解決的問題：**AI 對話中產生的所有決策、除錯過程、架構辯論在 session 結尾就消失。**

其他記憶系統的方法是讓 AI 自己判斷什麼值得記憶，結果往往丟失脈絡。MemPalace 採取不同策略：**「store everything, then make it findable」** — 保留所有原詞，用結構讓它可搜尋。

古希臘演說家的記憶宮殿方法：將想法放在想像建築的房間中。走入建築、找到想法。MemPalace 將同一原理套用在 AI 記憶上：對話被組織成 wings（人和專案）、halls（記憶類型）、rooms（具體想法）。

### 三大支柱

```
┌─────────────────────────────────────────────────────────┐
│                    MEMPALACE                             │
├──────────────────┬──────────────┬───────────────────────┤
│   The Palace      │    AAAK      │   Knowledge Graph     │
│  結構化記憶宮      │  30x 壓縮     │  時間實體關係圖        │
│                  │  零 decoder   │  SQLite (非 Neo4j)    │
│  wing→room→hall  │  任何 LLM     │  有效性時間窗口        │
│  →closet→drawer  │  可讀          │  invalidate 機制      │
└──────────────────┴──────────────┴───────────────────────┘
```

**The Palace — 記憶宮殿結構：**

```
  ┌─────────────────────────────────────────────────────────────┐
  │  WING: Person / Project (可任意擴展)                         │
  │                                                            │
  │    ┌──────────┐  ──hall──  ┌──────────┐                    │
  │    │  Room A  │            │  Room B  │  (專題房間)          │
  │    └────┬─────┘            └──────────┘                    │
  │         │                                                  │
  │         ▼                                                  │
  │    ┌──────────┐      ┌──────────┐                          │
  │    │  Closet  │ ───▶ │  Drawer  │ (壓縮摘要 → 原始檔案)      │
  │    └──────────┘      └──────────┘                          │
  └─────────┼──────────────────────────────────────────────────┘
            │ tunnel (跨 wing 連接同主題房間)
            ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  WING: 另一個 Person / Project                               │
  │    ┌──────────┐  ──hall──  ┌──────────┐                    │
  │    │  Room A  │            │  Room C  │                    │
  └─────────────────────────────────────────────────────────────┘
```

| 結構單位 | 說明 |
|----------|------|
| **Wings** | 人或專案的分類維度，可以任意擴展 |
| **Rooms** | wing 內的具體主題（auth-migration, graphql-switch, ci-pipeline） |
| **Halls** | 五種固定記憶類型的走廊：facts, events, discoveries, preferences, advice |
| **Tunnels** | 跨 wing 的房間交叉引用（同一主題在不同 wing 出現時自動連接） |
| **Closets** | 壓縮摘要，指向原始內容 |
| **Drawers** | 原始 verbatim 檔案，從不刪除 |

**Halls 是固定的記憶類型：**
- `hall_facts` — 決策、選擇、鎖定的事實
- `hall_events` — 會議、里程碑、除錯過程
- `hall_discoveries` — 突破、新洞察
- `hall_preferences` — 習慣、偏好、意見
- `hall_advice` — 推薦和解決方案

### AAAK 壓縮方言

AAAK 是無損壓縮的速記語言，**30x 壓縮率**，任何讀文字的 LLM 無需 decoder 就能理解。支援 Claude, GPT, Gemini, Llama, Mistral。完全離線可用。

```
English (~1000 tokens):
  Priya manages the Driftwood team: Kai (backend, 3 years), Soren (frontend),
  Maya (infrastructure), and Leo (junior, started last month). They're building
  a SaaS analytics platform. Current sprint: auth migration to Clerk.
  Kai recommended Clerk over Auth0 based on pricing and DX.

AAAK (~120 tokens):
  TEAM: PRI(lead) | KAI(backend,3yr) SOR(frontend) MAY(infra) LEO(junior,new)
  PROJ: DRIFTWOOD(saas.analytics) | SPRINT: auth.migration→clerk
  DECISION: KAI.rec:clerk>auth0(pricing+dx) | ★★★★
```

相同資訊，8x 更少的 tokens。AI 自動從 MCP server 學會 AAAK，不需要手動設定。

### Memory Stack（四層記憶體）

| 層 | 內容 | 大小 | 時機 |
|----|------|------|------|
| **L0** | Identity — AI 自己是誰？ | ~50 tokens | 永遠載入 |
| **L1** | Critical facts — 團隊、專案、偏好 | ~120 tokens (AAAK) | 永遠載入 |
| **L2** | Room recall — 近況、當前專案 | 按需 | 主題觸發 |
| **L3** | Deep search — 全宮殿語意搜尋 | 按需 | 明確要求時 |

**Wake-up 總計只需要 ~170 tokens。**

### 基準測試結果

#### LongMemEval

| 模式 | 分數 | API 需求 |
|------|------|----------|
| Raw (ChromaDB only) | **96.6%** R@5 | Zero |
| Hybrid + Haiku rerank | **100%** (500/500) R@5 | ~500 calls |

#### 其他基準

| 基準 | 分數 | API 需求 |
|------|------|----------|
| LoCoMo R@10 (Raw, session level) | 60.3% | Zero |
| Personal palace R@10 (Heuristic) | 85% | Zero |
| **Palace 結構影響** (wing+room filtering) | **+34%** R@10 | Zero |

#### vs 公開競品

| 系統 | LongMemEval R@5 | API | 費用 |
|------|-----------------|-----|------|
| **MemPalace (hybrid)** | **100%** | Optional | Free |
| Supermemory ASMR | ~99% | Yes | — |
| **MemPalace (raw)** | **96.6%** | **None** | **Free** |
| Mastra | 94.87% | Yes (GPT) | API costs |
| Mem0 | ~85% | Yes | $19–249/mo |
| Zep | ~85% | Yes | $25/mo+ |

### Knowledge Graph

Temporal entity-relationship triples — 像 Zep Graphiti，但是 SQLite 而非 Neo4j。本機、免費。

```python
from mempalace.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
kg.add_triple("Kai", "works_on", "Orion", valid_from="2025-06-01")
kg.add_triple("Maya", "assigned_to", "auth-migration", valid_from="2026-01-15")
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")

# Historical queries 仍能返回舊狀態
kg.query_entity("Kai", as_of="2026-02-01")
```

| Feature | MemPalace | Zep (Graphiti) |
|---------|-----------|----------------|
| Storage | SQLite (local) | Neo4j (cloud) |
| Cost | Free | $25/mo+ |
| Temporal validity | ✓ | ✓ |
| Self-hosted | Always | Enterprise only |
| Privacy | Everything local | SOC 2, HIPAA |

### 矛盾檢測

MemPalace 會在資訊送達前攔截錯誤：

```
Input:  "Soren finished the auth migration"
Output: 🔴 AUTH-MIGRATION: attribution conflict — Maya was assigned, not Soren

Input:  "Kai has been here 2 years"
Output: 🟡 KAI: wrong_tenure — records show 3 years (started 2023-04)

Input:  "The sprint ends Friday"
Output: 🟡 SPRINT: stale_date — current sprint ends Thursday (updated 2 days ago)
```

### MCP Server — 19 個 Tools

| 類別 | Tools |
|------|-------|
| **Palace (read)** | status, list_wings, list_rooms, get_taxonomy, search, check_duplicate, get_aaak_spec |
| **Palace (write)** | add_drawer, delete_drawer |
| **Knowledge Graph** | kg_query, kg_add, kg_invalidate, kg_timeline, kg_stats |
| **Navigation** | traverse, find_tunnels, graph_stats |
| **Agent Diary** | diary_write, diary_read |

### Auto-Save Hooks

提供 Claude Code 的 auto-save hooks：
- **Save Hook** — 每 15 則訊息觸發結構化儲存
- **PreCompact Hook** — context 壓縮前緊急儲存

### 檔案結構

```
mempalace/
├── mempalace/
│   ├── cli.py                 # CLI 入口
│   ├── mcp_server.py          # MCP server — 19 tools + AAAK auto-teach
│   ├── knowledge_graph.py     # temporal entity graph
│   ├── palace_graph.py        # room navigation graph
│   ├── dialect.py             # AAAK compression — 30x lossless
│   ├── miner.py               # project file ingest
│   ├── convo_miner.py         # conversation ingest
│   ├── searcher.py            # semantic search (ChromaDB)
│   ├── layers.py              # 4-layer memory stack
│   ├── onboarding.py          # guided setup
│   ├── entity_registry.py     # entity code registry
│   ├── entity_detector.py     # auto-detect people and projects
│   └── split_mega_files.py    # split concatenated transcripts
├── benchmarks/                # reproducible benchmark runners
├── hooks/                     # Claude Code auto-save hooks
├── examples/                  # usage examples
└── tests/                     # test suite
```

---

## 二、NousResearch/hermes-agent #5100 — Karpathy LLM-Wiki

### PR 基本資訊

| 欄位 | 值 |
|------|-----|
| PR 狀態 | **CLOSED** (已關閉，未合併) |
| 作者 | teknium1 (Teknium, NousResearch 創始者) |
| 變更 | `skills/research/llm-wiki/SKILL.md` (+274, -0) |
| 建立 | 2026-04-04 |
| 最後更新 | 2026-04-07 |

### 背景與靈感

基於 Andrej Karpathy 的 [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。核心理念：**教導 agent 建立和維護持久化、互相連結的 markdown 知識庫。**

### 與傳統 RAG 的差異

```
┌──────────────────┬──────────────────────────────────────────┐
│   Traditional RAG │   LLM-Wiki (Karpathy Pattern)            │
├──────────────────┼──────────────────────────────────────────┤
│ 每次查詢重新發現  │ 編譯一次，持續更新                        │
│ 無狀態           │ 狀態持續累積                              │
│ Cross-ref: none  │ Cross-ref: 已經存在                       │
│ 矛盾: 未檢測      │ 矛盾: 已被標記                            │
│ 綜合: 每輪重建    │ 綜合: 反映所有已攝取內容                   │
└──────────────────┴──────────────────────────────────────────┘
```

### 三層架構

```
wiki/
├── SCHEMA.md           # 約定、結構規則、領域配置
├── index.md            # 內容目錄 — 每頁一句摘要
├── log.md              # 編年動作紀錄 (append-only)
├── raw/                # L1: 不可變原始素材
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams
├── entities/           # L2: 實體頁 (people, orgs, products)
├── concepts/           # L2: 概念/主題頁
├── comparisons/        # L2: 並列分析頁
└── queries/            # L2: 有價值的查詢結果
```

| Layer | 說明 |
|-------|------|
| **L1 — Raw Sources** | 不可變。Agent 只讀不寫 |
| **L2 — The Wiki** | Agent 擁有的 markdown 檔案，建立、更新、交叉引用 |
| **L3 — The Schema** | `SCHEMA.md` 定義結構和約定 |

### 三大核心操作

| 操作 | 流程 |
|------|------|
| **Ingest** | 捕獲原始來源 → 寫摘要 → 更新實體/概念頁 → 交叉引用 → 更新 index + log |
| **Query** | 讀 index → 讀相關頁 → 綜合答案 → 有價值的結果寫回 wiki |
| **Lint** | 掃描矛盾 → 找孤兒頁 → 檢查過時內容 → 識別數據缺口 → 驗證 index 完整性 |

### 勞動分工

**人類：** 策劃原始來源、指導分析方向  
**Agent：** 摘錄、交叉引用、歸檔、維護一致性

### YAML Frontmatter 約定

每個 wiki 頁面都有 frontmatter：

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [tag1, tag2]
sources: [raw/articles/source-name.md]
---
```

### Obsidian 整合

Wiki 目錄本身就是一個 Obsidian vault：
- `[[wikilinks]]` 渲染為可點擊連結
- Graph View 視覺化知識網絡
- YAML frontmatter 驅動 Dataview 查詢

### 常見陷阱

- **永不修改 `raw/` 中的檔案** — 原始來源是永恆不變的，更正應在 wiki 頁面上
- **永遠更新 index.md 和 log.md** — 忽略會導致 wiki 退化
- **不要建立沒有交叉引用的頁面** — 孤立的頁面是隱形的
- **Frontmatter 是必需的** — 它支援搜尋、過濾和過時偵測
- **摘要要簡短** — wiki 頁面應在 30 秒內可掃描完畢
- **大批量更新前先請示** — 如果 ingest 會影響 10+ 現有頁面，先確認範圍

---

## 三、比較分析

| 維度 | MemPalace | LLM-Wiki (PR #5100) |
|------|-----------|---------------------|
| **形式** | Python package (`pip install`) | Hermes Agent skill (SKILL.md) |
| **儲存** | ChromaDB vector DB + SQLite KG | 純 Markdown 檔案 |
| **壓縮** | AAAK 方言 (30x) | 無特殊壓縮 |
| **結構** | Wing→Room→Hall→Closet→Drawer | SCHEMA→Index→Entities→Concepts |
| **AI 整合** | MCP server (19 tools) | Agent 直接讀寫檔案 |
| **離線能力** | 完全離線 | 完全離線 |
| **知識圖** | SQLite temporal KG | Wikilinks 交叉引用 |
| **矛盾檢測** | 有 (attribution conflict, stale date) | 有 (lint 掃描) |
| **依賴** | chromadb, pyyaml | 無（標準 Python） |
| **與 Agent 關係** | AI 透過 MCP 呼叫 | Agent 本身就是 wiki 維護者 |

---

## 四、與我們的 Multi-Agent Ecosystem 整合分析

### MemPalace 整合潛力

```
┌─────────────────────────────────────────────────────┐
│                 Hermes Agent                         │
│                      │                                │
│        native-mcp skill │                              │
│                      │                                │
│                      ▼                                │
│  ┌──────────────────────────────────────────┐        │
│  │         MemPalace (MCP Server)           │        │
│  │                                          │        │
│  │  19 tools → search/diary/KG/navigation   │        │
│  │  AAAK compression → 跨 agent messaging    │        │
│  │  Specialist agents → subagent specialization│      │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

1. **Agent 共享記憶層** — 19 MCP tools 透過 `native-mcp` skill 直接接入
2. **AAAK 壓縮** — 作為 agent 間訊息壓縮格式，減少 context window 消耗
3. **Specialist Agents** — reviewer/architect/ops 模式與 multi-agent routing 重疊
4. **Claude Code Hooks** — auto-save hooks 可直接整合

### LLM-Wiki 整合潛力

1. **各 Agent 的個人知識庫** — 每個 profile 一個 wiki 目錄 (`LLM_WIKI_PATH`)
2. **Obsidian 整合** — 透過現有 `obsidian` skill 操作
3. **與 MemPalace 互補** — MemPalace 處理語意搜尋/跨 agent 共享，LLM-Wiki 處理個別領域知識

---

## 五、風險與考量

| 風險項目 | MemPalace | LLM-Wiki |
|----------|-----------|----------|
| **維護者可信度** | `milla-jovovich` 是虛構帳號（演員名），背後團隊不明 | teknium1 是 NousResearch 創始者，高度可信 |
| **PR 狀態** | N/A | PR #5100 已關閉，未合併進主分支 |
| **成熟度** | v3.0.0，有 benchmark 數據支持 | 全新 skill，尚未經實戰驗證 |
| **Benchmark 可重複性** | 聲稱 96.6%/100%，有 reproducible runners | 無 benchmark |
| **與現有系統衝突** | ChromaDB 可能與我們現有 stack 衝突 | 純 markdown，無衝突風險 |
| **4075 stars** | 短期內飆升，可能是組織性推廣 | PR 只有一個 commit |

---

## 六、建議

### 短線（可立即行動）

1. **提取 LLM-Wiki SKILL.md** — PR 雖關閉但內容可手動安裝到 Hermes Agent skills
2. **測試 MemPalace MCP server** — 用 `native-mcp` skill 連接，評估 tool quality
3. **設定個人 wiki** — 選擇一個領域測試 LLM-Wiki 的三層架構

### 中線（規劃中）

4. **AAAK 壓縮評估** — 測試 AAAK 在我們的 agent messaging 中的實用性
5. **Specialist Agents 原型** — 用 MemPalace 的 agent diary 模式設計 reviewer/architect/ops agents
6. **Knowledge Graph 整合** — 與 `hermes_state.py` (FTS5 SQLite) 的兼容性評估

### 關鍵原則

> **記憶系統應該「寫一次、持續更新、交叉引用」而非「每次查詢重新發現」。**
> 
> MemPalace 的 palace 結構帶來 **+34% 檢索提升** — 結構本身就是產品。
> LLM-Wiki 的三層架構確保知識隨時間增值而非退化。
> 
> **兩者不衝突，可以並行** — MemPalace 處理結構化語意搜尋和跨 agent 記憶共享，LLM-Wiki 處理 agent 個別領域的編譯知識。

