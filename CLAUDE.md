# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> 完整歷史版本與詳細參考：`docs/CLAUDE_full_reference.md`

## 工作原則

- **優先使用 Subagents 工具**：在執行複雜的文件處理、腳本編寫或系統操作時，應優先考慮使用 `shell`, `fs`, `scripting` 等專門的 subagents 工具。這些工具能更精確地處理大型文件與複雜邏輯，減少手動錯誤並提升自動化效率。

## 專案概述

基於 Robot Framework 的多平台自動化測試系統，整合移動應用測試（iOS/Android）、語音控制、電源管理（SwitchBot）、機器手臂視覺檢測、多感官檢測、TestLink 整合。

## 關鍵文件索引

| 文件 | 用途 |
|------|------|
| `spec.md` | 系統規格書（UML 圖表），修改前必讀 |
| `todo.md` | 任務清單與進度追蹤，完成任務後更新 |
| `keywords_readme.md` | Robot Framework 關鍵字總覽，修改關鍵字後更新 |
| `docs/keyword_design_guidelines.md` | BDD 關鍵字設計規範（命名、Docstring、抽象層級） |
| `docs/CLAUDE_full_reference.md` | 本檔精簡前的完整版（含版本歷史、故障排除、子系統詳細說明） |
| `openspec/` | openspec 規格驅動開發目錄（proposal → design → spec → tasks） |

**子系統文檔（需要時查閱）：**

| 子系統 | Library README | 設計/規格文檔 | 操作指南 |
|--------|---------------|--------------|----------|
| 機器手臂視覺檢測 | `libraries/robot_arm_control/README.md` | `docs/robot_arm_vision_detection_design.md` | `docs/vision_detection_quick_start_guide.md` |
| ROI 校準工具 | — | — | `docs/robot_arm_vision_calibration_guide.md` |
| TestLink 整合 | `libraries/testlink_integration/README.md` | — | `docs/testlink_integration_setup_guide.md` |
| 移動測試 | `libraries/mobile_testing/README.md` | — | `docs/ios_device_setup.md` |
| 語音控制 | `libraries/voice_control/README.md` | `docs/voice_control_tts_migration.md` | `docs/voice_control_keywords.md` |
| 聲音檢測 | `libraries/local_voice_verifying/README.md` | — | — |
| 多感官檢測 | `libraries/multimodal_detection/README.md` | `docs/vision_detection_local_spec.md` | `docs/vision_detection_troubleshooting_guide.md` |
| IP Camera | `libraries/ipcam_light_detection/README.md` | — | — |
| SwitchBot | `libraries/switchbot_smartplug_control/README.md` | — | — |

**Resource 資源檔與 Library 對應：**

| Resource 檔 | 包裝的 Library |
|-------------|---------------|
| `resources/robot_arm_keywords.robot` | `robot_arm_control` |
| `resources/voice_control_keywords.robot` | `voice_control` |
| `resources/mobile_keywords.robot` | `mobile_testing` |
| `resources/testlink_keywords.robot` | `testlink_integration` |
| `resources/switchbot_keywords.robot` | `switchbot_smartplug_control` |
| `resources/ipcam_keywords.robot` | `ipcam_light_detection` |
| `resources/multimodal_keywords.robot` | `multimodal_detection` |
| `resources/device_control_keywords.robot` | `mobile_testing` (裝置控制) |
| `resources/gesture_control_keywords.robot` | `mobile_testing` (手勢控制) |
| `resources/common_keywords.robot` | 通用關鍵字 |
| `resources/api_keywords.robot` | API 測試 |
| `resources/web_keywords.robot` | Web 測試 |

## 開發環境

- **OS:** Ubuntu 24.04（主要）/ macOS（開發）
- **Python:** 3.12
- **相依性管理:** uv
- **測試框架:** Robot Framework 7.3.1+

## 核心命令

```bash
# 環境設置
uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# 執行測試
robot tests/path/to/test.robot
robot --test "測試案例名稱" tests/path/to/test.robot
robot --include tag_name tests/
robot --dryrun tests/path/to/test.robot          # 語法檢查

# 單元測試
pytest tests/test_xxx.py -v

# 產生關鍵字文檔
python -m robot.libdoc libraries/xxx/XxxKeywords.py docs/XxxKeywords.html
```

## 目錄結構

```
robot-multiplatform-automation/
├── config/                      # 統一配置管理（所有配置集中於此）
│   ├── voice_config.py
│   ├── switchbot_config.py
│   ├── testlink_config.py
│   ├── robot_arm/               # 機器手臂環境配置 + YAML
│   └── mobile/                  # Appium / iOS / Android 配置
├── libraries/                   # 自定義 Robot Framework Libraries
│   ├── local_voice_verifying/   # 聲音檢測與驗證
│   ├── voice_control/           # TTS + Scarlett 4i4 音訊輸出
│   ├── switchbot_smartplug_control/
│   ├── testlink_integration/    # TestLink XML-RPC API
│   ├── robot_arm_control/       # 機器手臂視覺檢測（BDD 關鍵字）
│   ├── mobile_testing/          # 移動測試（iOS/Android）
│   └── multimodal_detection/    # 多感官檢測整合
├── resources/                   # Robot Framework .robot 資源檔
├── tests/                       # 測試案例
├── scripts/                     # 輔助腳本
├── docs/                        # 文檔
└── results/                     # 測試輸出
```

## 配置系統

所有配置集中在 `config/` 目錄，優先順序：
1. 系統環境變數（最高）
2. 專案根目錄 `.env`（參考 `.env.example` 建立）
3. 配置檔案預設值

敏感資訊（API Key、Token）一律存放於 `.env`，不得寫入程式碼。

**環境專屬配置（機器手臂視覺檢測）：**
- `config/robot_arm/taipei_lab_buttons.yaml` — 台北實驗室
- `config/robot_arm/taoyuan_lab_buttons.yaml` — 桃園實驗室
- `config/robot_arm/rv_car_buttons.yaml` — RV Car

## 編碼規範

### Robot Framework BDD 規範（必遵守）

1. **Gherkin 語法** — 所有測試案例使用 Given-When-Then-And
2. **中文關鍵字** — 所有關鍵字名稱使用中文
3. **業務層級抽象** — 描述「做什麼」而非「如何做」
4. **RETURN 語句** — 使用現代 `RETURN`，禁用舊式 `[Return]`
5. **詳細 [Documentation]** — 含說明和使用範例

```robotframework
# 正確
Given 機器手臂已連接到遠端伺服器
When 用戶檢測第 "light1" 按鈕的燈光狀態
Then 按鈕燈光應該為 "blue" 色

# 錯誤 — 英文、技術層級暴露
Click Element "xpath=//button[@id='submit']"
Send Angles To Robot [10, 20, 30, 40, 50, 60]
```

完整設計指南：`docs/keyword_design_guidelines.md`

最佳實踐範本：
- `libraries/robot_arm_control/RobotArmKeywords.py`
- `libraries/testlink_integration/TestLinkConnector.py`

### Python 規範

- 函式須有中文 docstring
- 配置統一從 `config` 模組匯入
- 日誌使用 loguru
- 完善的異常處理

### 通用規範

- 日期格式 `YYYY-MM-DD`，寫入前先確認當前日期
- 所有文件和註解使用中文
- 使用 `robotidy` 格式化 Robot Framework 程式碼

## 重要設計決策

- **配置管理統一化** — 所有配置集中 `config/`，禁止在 `libraries/` 中建立獨立配置
- **避免第三方 API 封裝** — 直接使用標準庫（如 `xmlrpc.client`、`requests`），避免過時套件
- **機器手臂定位** — MyCobot 280 是**測試工具**（非被測對象）
- **Socket 控制架構** — 統一透過 TCP Socket (port 9000) 控制機器手臂

## 開發工作流程

### 修改程式碼前
1. 確認 `spec.md` 中的系統規格
2. 確認現有程式碼結構

### 修改程式碼後
1. 更新 `todo.md` 進度
2. 若修改 Robot 關鍵字，更新 `keywords_readme.md`

### 檔案變更規範
- 優先編輯現有檔案，避免建立非必要檔案
- 禁止主動建立 .md 或 README（除非明確要求）
- 新檔案須符合既定目錄結構

### 工作模式
- **協調者模式** — 任務報告記錄在 `report.md`
- **架構模式** — 產生 `spec.md`（含 UML）+ `todo.md`（區分人工/自動化任務）
- **Code 模式** — 遵循規範 → 完成後更新追蹤文件

## Robot Framework 注意事項

```robotframework
# Log 關鍵字陷阱 — URL 會被誤認為日誌級別
# 錯誤
Log    1. Open Application    http://localhost:4723    [capabilities]
# 正確
Log    1. Open Application 使用 http://localhost:4723 和 capabilities 字典
```

## Shell Tools Usage Guidelines

| Task Type | Must Use | Do Not Use |
|-----------|----------|------------|
| Find Files | `fd` | `find`, `ls -R` |
| Search Text | `rg` (ripgrep) | `grep`, `ag` |
| Analyze Code Structure | `ast-grep` | `grep`, `sed` |
| Interactive Selection | `fzf` | Manual filtering |
| Process JSON | `jq` | `python -m json.tool` |
| Process YAML/XML | `yq` | Manual parsing |
