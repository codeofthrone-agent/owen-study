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
21. 執行 Robot Framework 測試時，應使用 `uv run robot` 指令。
22. `libraries/` 目錄下的每一個子目錄（代表一個獨立的函式庫）都應包含一個 `README.md` 檔案，用以說明該函式庫的用途、API 和目前開發進度。


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

---

# Robot Framework Keyword 設計規範

## 1. 總體原則

本文件旨在為專案建立一套統一、高品質的 Robot Framework Keyword 設計標準。所有新的和重構的 Keyword 都應遵循此規範。

我們的核心目標是：
- **提升測試案例的可讀性**：讓非技術人員也能理解測試案例的意圖。
- **增強測試案例的穩定性與可維護性**：將業務邏輯與技術實現分離。
- **促進團隊協作**：提供一致的風格和清晰的文件。

**最佳實踐範本**: `libraries/voice_control/VoiceControlKeywords.py`

---

## 2. Gherkin / BDD 整合

所有測試案例應遵循 Gherkin 語法，利用 `Given-When-Then` 的結構來描述業務場景。Keyword 的設計必須服務於此結構。

- **`Given` (給定)**: 用於設定系統的 **前置條件** 或 **狀態**。
  - *範例*: `Given TTS 引擎已設定為 "gtts"`
  - *目的*: 建立一個已知的、穩定的測試起點。

- **`When` (當)**: 用於觸發一個 **核心業務動作** 或 **用戶操作**。
  - *範例*: `When 使用者播放文字 "Hello" 到聲道 "1"`
  - *目的*: 模擬使用者或系統執行的單一關鍵行為。

- **`Then` (那麼)**: 用於 **驗證** `When` 步驟所產生的 **結果** 或 **狀態變化**。
  - *範例*: `Then 語音應該成功播放到指定聲道`
  - *目的*: 斷言測試的預期結果是否達成。

- **`And` (而且)** / **`But` (但是)**: 用於 **串連** 多個同類型的步驟，避免重複使用 `Given`, `When`, `Then`。
  - *範例*: 
    ```robotframework
    Then 語音應該成功播放到指定聲道
    And 語音品質應該符合標準
    ```

---

## 3. 命名規範

Keyword 的命名是可讀性的關鍵。

- **使用完整的業務描述性語句**: Keyword 名稱應該像一個句子，清楚地說明其執行的操作。
- **中英雙語支持**: 為了團隊的可讀性，Python Library 中的 Keyword 應同時提供中文和英文名稱。
  ```python
  @keyword('Given 語音控制系統已成功初始化')
  def given_voice_control_system_initialized(self):
      # ...
  ```
- **動詞開頭**: 英文函式名稱建議以動詞開頭，並遵循 `given_...`, `when_...`, `then_...` 的模式。

---

## 4. 抽象層級 (Abstraction Level)

這是最重要的原則之一。

- **業務層級抽象**: Keyword 應該描述 **"做什麼" (What)**，而不是 **"如何做" (How)**。
  - **好的例子 (業務層級)**:
    - `User Logs In With Valid Credentials`
    - `Search For Product "Robot"`
    - `Verify Shopping Cart Contains "Robot"`
  - **壞的例子 (技術實現層級)**:
    - `Input Text To Element "id:username"`
    - `Click Button "xpath=//button[@type='submit']"`
    - `Element Text Should Be "css:.cart-item" "Robot"`

- **封裝複雜性**: 將所有 API 呼叫、UI 操作、資料庫查詢等技術細節封裝在 Keyword 的 Python 實現中。測試案例 (`.robot` 檔案) 中不應出現任何技術定位符 (如 XPath, CSS Selector) 或 API 端點。

---

## 5. 文件註解 (Docstring) 標準

清晰的文件是可維護性的保障。每個在 Python Library 中定義的 Keyword **必須** 包含完整的 Docstring。

Docstring 應包含以下部分：

1.  **功能描述**: 一段簡潔的描述，說明 Keyword 的作用。建議提供中英雙語。
2.  **參數 (`Arguments`)**: 如果 Keyword 接受參數，需清楚列出每個參數的名稱、類型和意義。
3.  **前置條件 (`Prerequisites`)**: 執行此 Keyword 前需要滿足的條件。
4.  **範例 (`Examples`)**: 提供一或多個在 `.robot` 檔案中的使用範例。
5.  **回傳值 (`Returns`)**: 如果有回傳值，說明其意義。

**範本**:
```python
@keyword('Given TTS 引擎已設定為 "${engine_name}"')
def given_tts_engine_set_to(self, engine_name: str) -> bool:
    """
    Given: 確認 TTS 引擎已設定為指定引擎
    Given: Confirm TTS engine is set to specified engine
    
    此關鍵字設定並確認指定的 TTS 引擎已正確配置。
    This keyword sets and confirms the specified TTS engine is properly configured.
    
    Arguments:
    - engine_name: TTS 引擎名稱 (gtts/pyttsx3)
    
    Prerequisites:
    - Voice control system is initialized
    
    Examples:
    | Given | TTS 引擎已設定為 "gtts" |
    
    Returns:
        bool: 設定是否成功
    """
    # ...
```

---

## 6. 職責與錯誤處理

- **單一職責原則**: 每個 Keyword 只應負責一件核心任務。
- **錯誤處理**:
  - **驗證型 Keyword (`Then`, `And`)**: 在驗證失敗時，**必須** 使用 `raise AssertionError("描述性的錯誤訊息")` 來明確地失敗測試案例。
  - **動作型 Keyword (`When`)**: 在執行失敗時，應記錄詳細的錯誤日誌，並可選擇性地回傳 `False` 或拋出異常，取決於是否希望失敗立即中止測試。

---

## 7. 結構與工具

- **Python Library**: 複雜的邏輯、狀態管理和與外部系統的互動應在 Python Library (`.py`) 中實現。
- **Resource Files**: 簡單的、由其他 Keyword 組合而成的 User Keywords 可以在 Resource 檔案 (`.robot`) 中定義，但同樣需要遵循 BDD 和高抽象層級的原則。
- **工具**:
  - **`robotidy`**: 用於自動格式化 `.robot` 檔案，保持風格一致。
  - **`libdoc`**: 使用 `python -m robot.libdoc YourLibrary.py docs/YourLibrary.html` 來產生和預覽 Keyword 文件，檢查 Docstring 是否完整、清晰。