# TestLink 整合模組

## 📋 概述

TestLink Integration Library 提供與 TestLink 測試管理系統的完整整合功能，讓 Robot Framework 測試案例可以自動回報執行結果到 TestLink。

**主要特色：**
- ✅ 統一配置管理（符合專案規範）
- ✅ 中文 Gherkin 風格關鍵字
- ✅ XML-RPC API 直接呼叫（無第三方依賴）
- ✅ 完整的錯誤處理與重試機制
- ✅ 批次操作支援
- ✅ 詳細的日誌記錄

---

## 🚀 快速開始

### 1. 環境設置

#### 安裝相依套件

```bash
# 使用 uv
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

#### 配置 TestLink 連接

複製 `.env.example` 為 `.env` 並填入 TestLink 資訊：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
# TestLink 整合配置
TESTLINK_API_URL=http://your-testlink-server/testlink/lib/api/xmlrpc/v1/xmlrpc.php
TESTLINK_API_KEY=your_api_key_here
TESTLINK_PROJECT_NAME=你的專案名稱
TESTLINK_TEST_PLAN_NAME=你的測試計畫
TESTLINK_BUILD_NAME=Build 1.0
```

**如何取得 TestLink API Key：**
1. 登入 TestLink
2. 點擊右上角個人頭像 → "My Settings"
3. 在 "API interface" 區塊中，勾選 "Enable API key"
4. 產生或查看 API Key
5. 複製 API Key 到 `.env` 檔案

### 2. 基本使用

#### 最簡單的測試案例

```robotframework
*** Settings ***
Library    libraries.testlink_integration.TestLinkConnector
Resource   resources/testlink_keywords.robot

*** Test Cases ***
我的第一個 TestLink 整合測試
    Given TestLink 服務已連接
    When 回報測試案例 "TEST-001" 的執行結果為 "PASS"
    Then TestLink 應該記錄測試結果
```

#### 執行測試

```bash
robot tests/testlink_integration/testlink_integration_test.robot
```

---

## 📚 關鍵字說明

### Given 關鍵字（前置條件）

#### `Given TestLink 服務已連接`
連接到 TestLink 並初始化專案、測試計畫、Build。

```robotframework
Given TestLink 服務已連接
```

#### `Given TestLink 服務已連接到專案 "${project_name}"`
連接到指定的 TestLink 專案。

```robotframework
Given TestLink 服務已連接到專案 "我的專案"
```

### When 關鍵字（執行動作）

#### `When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}"`
回報測試案例的執行結果。

**參數：**
- `test_case_id`: 測試案例外部 ID（例如：TEST-001）
- `status`: 測試狀態（PASS, FAIL, BLOCKED, SKIP）

```robotframework
When 回報測試案例 "TEST-001" 的執行結果為 "PASS"
When 回報測試案例 "TEST-002" 的執行結果為 "FAIL"
```

#### `When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}" 並附註 "${notes}"`
回報測試結果並附加備註。

```robotframework
When 回報測試案例 "TEST-001" 的執行結果為 "FAIL" 並附註 "斷言失敗：預期值不符"
```

### Then 關鍵字（結果驗證）

#### `Then TestLink 應該記錄測試結果`
驗證 TestLink 已成功記錄測試結果。

```robotframework
Then TestLink 應該記錄測試結果
```

#### `Then 測試案例 "${test_case_id}" 應該存在於 TestLink`
驗證測試案例存在。

```robotframework
Then 測試案例 "TEST-001" 應該存在於 TestLink
```

---

## 🔧 進階使用

### 批次回報測試結果

```robotframework
*** Test Cases ***
批次回報多個測試結果
    [Documentation]    示範如何批次回報多個測試結果

    Given TestLink 服務已連接

    # 建立測試結果列表
    ${results}=    建立測試結果列表
    ${results}=    添加測試結果    ${results}    TEST-001    PASS
    ${results}=    添加測試結果    ${results}    TEST-002    FAIL    notes=斷言失敗
    ${results}=    添加測試結果    ${results}    TEST-003    PASS    duration=2.5

    # 批次回報
    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}
    Then 批次回報應該全部成功    ${stats}
```

### 使用 Python 語法建立結果列表

```robotframework
*** Test Cases ***
使用 Python 建立結果列表
    Given TestLink 服務已連接

    # 使用 Python 語法建立結果列表
    ${results}=    Evaluate    [
    ...    {'test_case_id': 'TEST-001', 'status': 'PASS'},
    ...    {'test_case_id': 'TEST-002', 'status': 'FAIL', 'notes': '錯誤訊息'},
    ...    {'test_case_id': 'TEST-003', 'status': 'PASS', 'duration': 1.5}
    ...    ]

    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}
    Log    回報統計: ${stats}
```

### 查詢測試案例資訊

```robotframework
*** Test Cases ***
查詢並驗證測試案例
    Given TestLink 服務已連接

    # 查詢測試案例資訊
    ${info}=    When 查詢測試案例 "TEST-001" 的資訊
    Log    測試案例名稱: ${info['name']}
    Log    測試案例 ID: ${info['testcase_id']}

    # 驗證測試案例存在
    Then 測試案例 "TEST-001" 應該存在於 TestLink
```

### 連接到不同的專案和測試計畫

```robotframework
*** Test Cases ***
動態切換專案
    # 連接到專案 A
    Given TestLink 服務已連接到專案 "專案 A"
    When 回報測試案例 "PROJECT_A-001" 的執行結果為 "PASS"

    # 連接到專案 B（需要重新連接）
    連接到 TestLink    project_name=專案 B    test_plan_name=Sprint 2
    When 回報測試案例 "PROJECT_B-001" 的執行結果為 "PASS"
```

---

## 🏗️ 架構說明

### 目錄結構

```
libraries/testlink_integration/
├── __init__.py                     # 套件初始化
├── README.md                       # 本文檔
├── TestLinkConnector.py            # Robot Framework Library
├── api_client/                     # API 客戶端
│   ├── __init__.py
│   └── testlink_api.py             # TestLink XML-RPC API 封裝
├── tests/                          # 單元測試
│   ├── __init__.py
│   └── test_connector.py
└── examples/                       # 使用範例
    └── testlink_example.robot

config/
└── testlink_config.py              # 統一配置（專案根目錄）

resources/
└── testlink_keywords.robot         # 中文 Gherkin 關鍵字
```

### 設計架構

```
┌──────────────────────────────────────┐
│   Robot Framework 測試案例           │
│   (tests/*.robot)                    │
└──────────────┬───────────────────────┘
               │ 使用中文關鍵字
               ▼
┌──────────────────────────────────────┐
│   testlink_keywords.robot            │
│   (中文 Gherkin 風格關鍵字)           │
└──────────────┬───────────────────────┘
               │ 呼叫 Library 方法
               ▼
┌──────────────────────────────────────┐
│   TestLinkConnector.py               │
│   (Robot Framework Library)          │
└──────────────┬───────────────────────┘
               │ 使用 API Client
               ▼
┌──────────────────────────────────────┐
│   TestLinkAPIClient                  │
│   (testlink_api.py)                  │
└──────────────┬───────────────────────┘
               │ XML-RPC 呼叫
               ▼
┌──────────────────────────────────────┐
│   TestLink Server                    │
│   (XML-RPC API)                      │
└──────────────────────────────────────┘
```

---

## ⚙️ 配置說明

### 配置優先順序

1. **系統環境變數**（最高優先）
2. **專案根目錄 .env 檔案**
3. **配置檔案中的預設值**

### 完整配置參數

| 參數 | 環境變數 | 預設值 | 說明 |
|------|---------|--------|------|
| API URL | `TESTLINK_API_URL` | `http://localhost/testlink/...` | TestLink API 端點 |
| API Key | `TESTLINK_API_KEY` | `''` | TestLink API 金鑰（必填） |
| 專案名稱 | `TESTLINK_PROJECT_NAME` | `Robot Automation Project` | 專案名稱 |
| 測試計畫 | `TESTLINK_TEST_PLAN_NAME` | `Automated Test Plan` | 測試計畫名稱 |
| Build 名稱 | `TESTLINK_BUILD_NAME` | `Build 1.0` | Build 名稱 |
| API 逾時 | `TESTLINK_API_TIMEOUT` | `30` | API 逾時時間（秒） |
| 重試次數 | `TESTLINK_API_RETRY_COUNT` | `3` | API 重試次數 |
| 重試延遲 | `TESTLINK_API_RETRY_DELAY` | `2` | 重試延遲（秒） |

### 驗證配置

```bash
# 驗證 TestLink 配置
python config/testlink_config.py
```

輸出範例：
```
TestLink 配置摘要:
{
  "api_url": "http://localhost/testlink/lib/api/xmlrpc/v1/xmlrpc.php",
  "api_key": "1234abcd...",
  "project_name": "Robot Automation Project",
  "test_plan_name": "Automated Test Plan",
  "build_name": "Build 1.0",
  "timeout": 30,
  "retry_count": 3
}

✅ 配置驗證成功
```

---

## 🐛 疑難排解

### 常見問題

#### 1. 連接 TestLink 失敗

**錯誤訊息：**
```
ConnectionError: 無法連接到 TestLink
```

**解決方法：**
- 確認 TestLink 服務正在運行
- 檢查 `TESTLINK_API_URL` 是否正確
- 確認網路連接正常
- 使用瀏覽器訪問 TestLink 確認可連接

#### 2. API Key 無效

**錯誤訊息：**
```
RuntimeError: API 呼叫失敗: Invalid API Key
```

**解決方法：**
- 確認 API Key 已在 TestLink 中啟用
- 重新產生 API Key
- 確認 `.env` 檔案中的 `TESTLINK_API_KEY` 正確

#### 3. 找不到專案或測試計畫

**錯誤訊息：**
```
ValueError: 找不到專案: 我的專案
```

**解決方法：**
- 確認專案名稱拼寫正確（區分大小寫）
- 確認用戶有權限訪問該專案
- 在 TestLink 介面中確認專案存在

#### 4. 測試案例不存在

**錯誤訊息：**
```
ValueError: 找不到測試案例: TEST-001
```

**解決方法：**
- 確認測試案例已加入測試計畫
- 檢查測試案例外部 ID 是否正確
- 確認測試案例未被刪除

### 除錯模式

啟用詳細日誌：

```bash
# 設定日誌級別
export TESTLINK_LOG_LEVEL=DEBUG

# 執行測試
robot --loglevel DEBUG tests/testlink_integration/
```

查看日誌檔案：
```bash
# TestLink 整合日誌
tail -f logs/testlink_integration.log

# Robot Framework 日誌
less log.html
```

---

## 📖 API 參考

### TestLinkConnector 類別

#### 連接方法

```python
connect_to_testlink(project_name=None, test_plan_name=None, build_name=None) -> bool
```

連接到 TestLink 並初始化。

**參數：**
- `project_name` (str, optional): 專案名稱
- `test_plan_name` (str, optional): 測試計畫名稱
- `build_name` (str, optional): Build 名稱

**回傳：**
- `bool`: 連接是否成功

#### 回報方法

```python
report_test_result(test_case_external_id, status, notes="", duration=0) -> Dict
```

回報測試結果到 TestLink。

**參數：**
- `test_case_external_id` (str): 測試案例外部 ID
- `status` (str): 測試狀態（PASS, FAIL, BLOCKED, SKIP）
- `notes` (str, optional): 測試備註
- `duration` (float, optional): 執行時間（分鐘）

**回傳：**
- `Dict`: API 回應結果

---

## 🤝 貢獻指南

### 開發環境設置

```bash
# 安裝開發依賴
uv pip install pytest pytest-cov

# 執行單元測試
pytest libraries/testlink_integration/tests/ -v

# 執行測試覆蓋率檢查
pytest libraries/testlink_integration/tests/ --cov=libraries/testlink_integration
```

### 編碼規範

- ✅ 所有函式必須有中文註解
- ✅ Robot Framework 關鍵字必須使用中文
- ✅ 遵循 Gherkin 語法（Given-When-Then）
- ✅ 使用 loguru 進行日誌記錄
- ✅ 完善的錯誤處理

---

## 📝 變更記錄

### v1.0.0 (2025-11-10)
- ✅ 初始版本發布
- ✅ 支援基本連接與回報功能
- ✅ 中文 Gherkin 風格關鍵字
- ✅ 統一配置管理系統
- ✅ 完整的文檔與範例

---

## 📄 授權

本模組為 Robot Framework 多平台自動化測試系統的一部分。

---

## 🔗 相關資源

- [TestLink 官方文檔](https://testlink.org/)
- [TestLink API 文檔](https://testlink.org/api/)
- [Robot Framework 官方文檔](https://robotframework.org/)
- [專案 GitHub Repository](https://github.com/your-repo)

---

**作者：** Robot Framework Automation Team
**維護：** [Your Team]
**最後更新：** 2025-11-10
