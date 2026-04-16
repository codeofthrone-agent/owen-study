# Robot Framework 關鍵字說明文件索引 (Index)

> **最後更新日期**: 2026-04-07
>
> 本專案採用 Gherkin 風格 (Given-When-Then) 的中文關鍵字設計規範。為了方便查閱與維護，詳細的關鍵字說明已依模組拆分至以下子文件中。

## 📂 關鍵字模組索引

| 類別 | 詳細說明文件 | 涵蓋範圍與重點功能 |
| :--- | :--- | :--- |
| 🤖 **機器手臂** | [keywords_robot_arm.md](docs/keywords/keywords_robot_arm.md) | MyCobot 280 控制、YOLOv8 視覺偵測、按鈕燈號分析、ROI 校準。 |
| 📱 **移動測試** | [keywords_mobile.md](docs/keywords/keywords_mobile.md) | Appium 整合、iOS 真機測試、Android 裝置控制 (藍牙/WiFi/音量)、進階手勢。 |
| 🎤 **語音控制** | [keywords_voice_control.md](docs/keywords/keywords_voice_control.md) | Scarlett 4i4 聲道控制、TTS (Google/pyttsx3)、高品質錄音與比對、UART 日誌監控。 |
| ⚙️ **核心與通用** | [keywords_core.md](docs/keywords/keywords_core.md) | 通用 BDD 流程、Web/API 測試、SwitchBot 智慧插座控制、IP Camera 影像擷取。 |

---

## 🎯 設計規範與準則

所有的關鍵字開發均須遵循以下核心原則：

1.  **全面中文化**: Robot Framework 資源層級的關鍵字名稱必須使用中文。
2.  **Gherkin 結構**: 嚴格遵守 `Given` (前置條件)、`When` (執行動作)、`Then` (驗證結果)、`And` (附加描述) 的結構。
3.  **雙語文檔**: 在 `[Documentation]` 中 provide 中英文雙語描述、參數說明及實際範例。
4.  **抽象層級**: 關鍵字應描述「要做什麼」(What)，而非「如何做」(How)，隱藏底層技術定位符。

詳細設計規範請參閱：[Robot Framework Keyword 設計規範](docs/robot_arm_vision/keyword_design_guidelines.md)

---

## 🛠️ 維護檢查清單

每次修改關鍵字程式碼 (Python Library 或 Resource File) 後，請務必：

- [x] 更新對應的子文件 (`docs/keywords/keywords_*.md`)。
- [x] 使用 `robot.libdoc` 重新產生 HTML 版 API 文件 (存放於 `docs/api/` 下)。
- [x] 確保 `tests/` 目錄下有對應的 BDD 測試案例進行驗證。
- [x] 檢查 `keywords_readme.md` 索引是否需要調整。

---
**專案狀態**: ✅ 全模組 Gherkin 標準化 100% 完成
