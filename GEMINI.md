0. 閱讀CLAUDE.md以了解專案支援的模組與功能
1. 開發環境為ubuntu24系統，終端機指令請使用shell相容語法（例如使用 && 分隔指令）
2. 請勿直接產生專案架構以及相關設定，需使用指令方式建立專案架構
3. 產生程式的同時都需要提供函式級註解
4. 規劃專案時須提供使用框架的分析建議，並由用戶選擇最終使用的框架
5. 協調者模式(迴旋標模式)最後需將所以有任務完成報告記錄在任務報告檔案中(report.md)
6. 架構模式完成後需產生規格文件(spec.md)以及任務清單(todo.md),規格文件須包含流程圖、循序圖、關聯圖等相關UML
7. Code模式需遵循spec.md開發，每次修改程式前都需確認spec.md，任務完成後都需更新任務進度(todo.md) 
8. 最後完成專案需撰寫readme.md，內容包含專案描述、安裝及執行方式
10. 專案如果是使用 Robot Framework 進行測試，請在 tests/ 目錄下建立測試案例，並在 resources/ 目錄下建立關鍵字庫和測試資源
11. 每次修改完robot程式碼後，應更新 keywords_readme.md，並檢查是否有對應的測試案例
12. Robot Framework 測試案例應使用 Gherkin 語法，並遵循 Given-When-Then-And 的結構
13. [Documentation] 應包含每個關鍵字的詳細說明和使用範例
14. Robot Framework 關鍵字名稱應使用中文
15. 寫入日期應先檢查現在日期，並確保日期格式為 YYYY-MM-DD
16. All Document should using chinese
17. 所有的程式碼註解和文件都應使用中文
18. 虛擬環境 使用 uv run 指令啟動
19. 設定計畫時，將需要人工協助及實體裝置，測試及分析的區塊分別出來
20. 修改python 需要執行 python3 -m py_compile 進行基礎檢查


## Shell Tools Usage Guidelines
⚠️ **IMPORTANT**: Use the following specialized tools instead of traditional Unix commands: (Install if missing)
| Task Type | Must Use | Do Not Use |
|-----------|----------|------------|
| Find Files | `fd` | `find`, `ls -R` |
| Search Text | `rg` (ripgrep) | `grep`, `ag` |
| Analyze Code Structure | `ast-grep` | `grep`, `sed` |
| Interactive Selection | `fzf` | Manual filtering |
| Process JSON | `jq` | `python -m json.tool` |
| Process YAML/XML | `yq` | Manual parsing |
====