# TestLink 整合模組設置指南

## 📋 概述

本文檔提供 TestLink 整合模組的完整設置與使用指南。

**建置日期:** 2025-11-10
**版本:** v1.0.0
**狀態:** ✅ 已完成

---

## 🎯 已完成項目

### ✅ 核心功能
- [x] TestLink API Client 實作 (XML-RPC 直接呼叫)
- [x] TestLinkConnector Robot Framework Library
- [x] 統一配置管理系統 (config/testlink_config.py)
- [x] 中文 Gherkin 風格關鍵字
- [x] 批次回報功能
- [x] 完整錯誤處理與重試機制

### ✅ 文檔與測試
- [x] 模組 README.md
- [x] 使用範例 (examples/testlink_example.robot)
- [x] 整合測試案例 (tests/testlink_integration/)
- [x] 單元測試 (libraries/testlink_integration/tests/)
- [x] 驗證腳本 (scripts/verify_testlink_integration.py)

### ✅ 配置與依賴
- [x] requirements.txt 更新
- [x] .env.example 更新
- [x] 專案結構完整

---

## 🏗️ 檔案結構

```
robot-multiplatform-automation/
├── libraries/testlink_integration/     # TestLink 整合模組
│   ├── __init__.py
│   ├── README.md                       # 模組說明文檔
│   ├── TestLinkConnector.py            # Robot Framework Library
│   ├── api_client/                     # API 客戶端
│   │   ├── __init__.py
│   │   └── testlink_api.py             # XML-RPC API 封裝
│   ├── tests/                          # 單元測試
│   │   ├── __init__.py
│   │   └── test_connector.py
│   └── examples/                       # 使用範例
│       └── testlink_example.robot
│
├── config/
│   └── testlink_config.py              # 統一配置系統
│
├── resources/
│   └── testlink_keywords.robot         # 中文 Gherkin 關鍵字
│
├── tests/testlink_integration/         # 整合測試
│   └── testlink_integration_test.robot
│
├── scripts/
│   └── verify_testlink_integration.py  # 驗證腳本
│
├── docs/
│   └── testlink_integration_setup_guide.md  # 本文檔
│
├── requirements.txt                    # 已更新
└── .env.example                        # 已更新 TestLink 配置
```

---

## 🚀 安裝步驟

### 1. 安裝依賴套件

```bash
# 使用 uv（推薦）
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

**注意:** TestLink 整合使用 Python 內建的 `xmlrpc.client`，無需額外安裝第三方 TestLink 套件。

### 2. 配置環境變數

複製 `.env.example` 為 `.env`:

```bash
cp .env.example .env
```

編輯 `.env` 檔案，添加 TestLink 配置:

```env
# TestLink 整合配置
TESTLINK_API_URL=http://your-testlink-server/testlink/lib/api/xmlrpc/v1/xmlrpc.php
TESTLINK_API_KEY=your_api_key_here
TESTLINK_PROJECT_NAME=Robot Automation Project
TESTLINK_TEST_PLAN_NAME=Automated Test Plan
TESTLINK_BUILD_NAME=Build 1.0
```

### 3. 取得 TestLink API Key

1. 登入 TestLink
2. 點擊右上角個人頭像 → "My Settings"
3. 在 "API interface" 區塊中：
   - 勾選 "Enable API key"
   - 點擊 "Generate a new key" 或查看現有 Key
4. 複製 API Key 到 `.env` 檔案

### 4. 驗證安裝

```bash
# 執行驗證腳本
python3 scripts/verify_testlink_integration.py
```

預期輸出:
```
✅ 所有驗證項目通過！TestLink 整合模組已就緒。
```

---

## 📖 快速開始

### 最簡單的測試案例

建立 `my_testlink_test.robot`:

```robotframework
*** Settings ***
Library    libraries.testlink_integration.TestLinkConnector
Resource   resources/testlink_keywords.robot

*** Test Cases ***
我的第一個 TestLink 測試
    Given TestLink 服務已連接
    When 回報測試案例 "TEST-001" 的執行結果為 "PASS"
    Then TestLink 應該記錄測試結果
```

執行測試:

```bash
robot my_testlink_test.robot
```

---

## 🔧 使用方式

### 1. 基本測試結果回報

```robotframework
*** Test Cases ***
回報測試成功
    Given TestLink 服務已連接
    When 回報測試案例 "TEST-001" 的執行結果為 "PASS"
    Then TestLink 應該記錄測試結果

回報測試失敗
    Given TestLink 服務已連接
    When 回報測試案例 "TEST-002" 的執行結果為 "FAIL" 並附註 "斷言失敗"
    Then TestLink 應該記錄測試結果
```

### 2. 批次回報測試結果

```robotframework
*** Test Cases ***
批次回報
    Given TestLink 服務已連接

    # 建立結果列表
    ${results}=    建立測試結果列表
    ${results}=    添加測試結果    ${results}    TEST-001    PASS
    ${results}=    添加測試結果    ${results}    TEST-002    FAIL    notes=錯誤
    ${results}=    添加測試結果    ${results}    TEST-003    PASS    duration=2.5

    # 批次回報
    ${stats}=    When 批次回報多個測試結果到 TestLink    ${results}
    Then 批次回報應該全部成功    ${stats}
```

### 3. 查詢測試案例

```robotframework
*** Test Cases ***
查詢測試案例資訊
    Given TestLink 服務已連接

    ${info}=    When 查詢測試案例 "TEST-001" 的資訊
    Log    測試案例名稱: ${info['name']}
    Log    測試案例 ID: ${info['testcase_id']}

    Then 測試案例 "TEST-001" 應該存在於 TestLink
```

---

## 📚 完整文檔

### 模組文檔
詳細的模組說明和 API 參考，請查看:
- [libraries/testlink_integration/README.md](../libraries/testlink_integration/README.md)

### 使用範例
10 個完整的使用範例，請查看:
- [libraries/testlink_integration/examples/testlink_example.robot](../libraries/testlink_integration/examples/testlink_example.robot)

### 整合測試
完整的整合測試案例:
- [tests/testlink_integration/testlink_integration_test.robot](../tests/testlink_integration/testlink_integration_test.robot)

---

## 🎯 關鍵字列表

### Given 關鍵字（前置條件）
- `Given TestLink 服務已連接`
- `Given TestLink 服務已連接到專案 "${project_name}"`
- `Given TestLink 連接狀態為正常`

### When 關鍵字（執行動作）
- `When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}"`
- `When 回報測試案例 "${test_case_id}" 的執行結果為 "${status}" 並附註 "${notes}"`
- `When 批次回報多個測試結果到 TestLink`
- `When 查詢測試案例 "${test_case_id}" 的資訊`

### Then 關鍵字（結果驗證）
- `Then TestLink 應該記錄測試結果`
- `Then 測試案例 "${test_case_id}" 的最後執行狀態應為 "${expected_status}"`
- `Then 測試案例 "${test_case_id}" 應該存在於 TestLink`
- `Then 批次回報應該全部成功`

### And 關鍵字（附加條件）
- `And 記錄當前 TestLink 專案資訊`
- `And 驗證 TestLink 連接正常`

### 輔助關鍵字
- `建立測試結果列表`
- `添加測試結果`

---

## ⚙️ 配置參數

### 環境變數

| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `TESTLINK_API_URL` | ✅ | `http://localhost/testlink/...` | TestLink API 端點 URL |
| `TESTLINK_API_KEY` | ✅ | - | TestLink API 金鑰 |
| `TESTLINK_PROJECT_NAME` | ❌ | `Robot Automation Project` | 專案名稱 |
| `TESTLINK_TEST_PLAN_NAME` | ❌ | `Automated Test Plan` | 測試計畫名稱 |
| `TESTLINK_BUILD_NAME` | ❌ | `Build 1.0` | Build 名稱 |
| `TESTLINK_API_TIMEOUT` | ❌ | `30` | API 逾時（秒） |
| `TESTLINK_API_RETRY_COUNT` | ❌ | `3` | API 重試次數 |
| `TESTLINK_API_RETRY_DELAY` | ❌ | `2` | 重試延遲（秒） |

### 測試狀態映射

| Robot Framework 狀態 | TestLink 狀態 |
|---------------------|---------------|
| `PASS` | `p` (passed) |
| `FAIL` | `f` (failed) |
| `BLOCKED` | `b` (blocked) |
| `SKIP` | `b` (blocked) |

---

## 🐛 疑難排解

### 問題 1: 連接 TestLink 失敗

**錯誤訊息:**
```
ConnectionError: 無法連接到 TestLink
```

**解決方法:**
1. 確認 TestLink 服務正在運行
2. 檢查 `TESTLINK_API_URL` 是否正確
3. 確認網路連接正常
4. 使用瀏覽器訪問 TestLink 確認可連接

### 問題 2: API Key 無效

**錯誤訊息:**
```
RuntimeError: API 呼叫失敗: Invalid API Key
```

**解決方法:**
1. 確認 API Key 已在 TestLink 中啟用
2. 重新產生 API Key
3. 確認 `.env` 檔案中的 `TESTLINK_API_KEY` 正確

### 問題 3: 找不到專案或測試計畫

**錯誤訊息:**
```
ValueError: 找不到專案: 我的專案
```

**解決方法:**
1. 確認專案名稱拼寫正確（區分大小寫）
2. 確認用戶有權限訪問該專案
3. 在 TestLink 介面中確認專案存在

### 問題 4: 模組匯入錯誤

**錯誤訊息:**
```
ModuleNotFoundError: No module named 'loguru'
```

**解決方法:**
```bash
# 安裝依賴套件
uv pip install -r requirements.txt

# 或
pip install loguru python-dotenv
```

---

## ✅ 驗證檢查清單

### 安裝驗證
- [ ] Python 3.12+ 已安裝
- [ ] 所有依賴套件已安裝 (`uv pip install -r requirements.txt`)
- [ ] `.env` 檔案已配置
- [ ] 驗證腳本執行成功 (`python3 scripts/verify_testlink_integration.py`)

### TestLink 環境驗證
- [ ] TestLink 服務正在運行
- [ ] API Key 已產生並配置
- [ ] 測試專案已建立
- [ ] 測試計畫已建立
- [ ] 測試案例已加入測試計畫

### 功能驗證
- [ ] 能成功連接到 TestLink
- [ ] 能回報單一測試結果
- [ ] 能批次回報測試結果
- [ ] 能查詢測試案例資訊
- [ ] 整合測試全部通過

---

## 🎓 進階主題

### 整合到 CI/CD

```yaml
# .github/workflows/test.yml 範例
name: Robot Framework Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -r requirements.txt

      - name: Run tests with TestLink integration
        env:
          TESTLINK_API_URL: ${{ secrets.TESTLINK_API_URL }}
          TESTLINK_API_KEY: ${{ secrets.TESTLINK_API_KEY }}
        run: |
          robot tests/testlink_integration/
```

### 自訂測試結果處理

```python
# custom_listener.py
from libraries.testlink_integration import TestLinkConnector

class TestLinkListener:
    """自動回報測試結果的 Robot Framework Listener"""

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.connector = TestLinkConnector()
        self.connector.connect_to_testlink()

    def end_test(self, data, result):
        """測試案例結束時自動回報"""
        test_id = result.tags.get('testlink_id')
        if test_id:
            status = 'PASS' if result.passed else 'FAIL'
            self.connector.report_test_result(
                test_id,
                status,
                notes=result.message
            )
```

使用方式:
```bash
robot --listener custom_listener.py tests/
```

---

## 📞 支援與貢獻

### 問題回報
如遇到問題，請提供以下資訊：
1. 錯誤訊息完整內容
2. 驗證腳本執行結果
3. Robot Framework 版本
4. TestLink 版本

### 貢獻指南
歡迎貢獻！請遵循專案編碼規範：
- ✅ 所有關鍵字使用中文
- ✅ 遵循 Gherkin 語法
- ✅ 完整的中文註解
- ✅ 提供測試案例

---

## 📝 版本記錄

### v1.0.0 (2025-11-10)
- ✅ 初始版本發布
- ✅ 完整的 TestLink 整合功能
- ✅ 中文 Gherkin 風格關鍵字
- ✅ 統一配置管理
- ✅ 完整文檔與範例

---

## 🔗 相關資源

- [TestLink 官方網站](https://testlink.org/)
- [TestLink API 文檔](https://testlink.org/api/)
- [Robot Framework 官方網站](https://robotframework.org/)
- [專案 CLAUDE.md](../CLAUDE.md)
- [專案 README.md](../README.md)

---

**建置團隊:** Robot Framework Automation Team
**最後更新:** 2025-11-10
**文檔版本:** v1.0.0
