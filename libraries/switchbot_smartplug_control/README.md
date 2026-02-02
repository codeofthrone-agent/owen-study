# SwitchBot 智慧插座控制模組

## 概述

本模組提供 SwitchBot 智慧插座的完整控制功能，使用 **SwitchBot 官方 HTTP API v1.1**（非第三方 SDK），整合至 Robot Framework 測試環境中，支援 Gherkin 風格的中文關鍵字與測試案例。

## 主要功能

### 核心控制功能
- ✅ **智慧插座開關控制** - 支援遠端開啟/關閉
- ✅ **設備狀態查詢** - 即時查詢插座開關狀態
- ✅ **設備資訊取得** - 查詢設備詳細資訊
- ✅ **電源重啟功能** - 執行設備重啟循環
- ✅ **所有設備列表** - 取得帳號下所有 SwitchBot 設備

### Robot Framework 整合
- ✅ **中文關鍵字支援** - 提供 Gherkin 風格的中文關鍵字
- ✅ **Given-When-Then-And 結構** - 完整的 BDD 測試語法支援
- ✅ **詳細錯誤處理** - 完善的異常處理與日誌記錄
- ✅ **環境變數管理** - 支援 .env 檔案與環境變數配置

### 命令列工具
- ✅ **設備查詢工具** (`get_device_id.py`) - 列出所有設備與 ID
- ✅ **插座控制工具** (`plug_control.py`) - 命令列開關控制
- ✅ **設備檢查工具** (`check_device.py`) - 檢查設備屬性與連線狀態

### 技術特點
- ✅ **官方 API** - 使用 SwitchBot 官方 HTTP API v1.1
- ✅ **無第三方依賴** - 不需要 pyswitchbot 等第三方 SDK
- ✅ **HMAC-SHA256 簽名** - 符合官方認證規範
- ✅ **UUID nonce** - 使用 UUID v4 作為 nonce（官方建議）

## 檔案結構

```
libraries/switchbot_smartplug_control/
├── SwitchBotSmartPlugLibrary.py    # Robot Framework Library 主檔案
├── switchbot_config.py             # 配置管理模組
├── .env.example                    # 環境變數範本檔案
├── get_device_id.py               # 設備查詢工具
├── plug_control.py                # 命令列控制工具
└── check_device.py                # 設備檢查工具

resources/
└── switchbot_keywords.robot       # Gherkin 風格中文關鍵字

tests/power_management/
└── switchbot_smartplug_test.robot # SwitchBot 測試案例集
```

## 安裝與設定

### 1. 安裝相依套件

```bash
# 使用 uv 安裝 (推薦)
uv pip install requests python-dotenv

# 或使用 pip 安裝
pip install requests python-dotenv
```

> **注意**: 本模組不需要安裝 `pyswitchbot` 套件，直接使用官方 HTTP API。

### 2. 設定 API 認證資訊

#### 步驟 1: 取得 SwitchBot API 認證資訊
1. 開啟 SwitchBot App
2. 進入「個人檔案」>「偏好設定」
3. 點擊「App 版本」10次開啟開發者選項
4. 複製 **Token** 和 **Secret**

#### 步驟 2: 建立環境變數檔案
```bash
# 複製範本檔案
cp libraries/switchbot_smartplug_control/.env.example libraries/switchbot_smartplug_control/.env

# 編輯 .env 檔案，填入您的 API 認證資訊
# SWITCHBOT_TOKEN=your_actual_token_here
# SWITCHBOT_SECRET=your_actual_secret_here
```

#### 步驟 3: 取得設備 ID
```bash
# 執行設備查詢工具
cd libraries/switchbot_smartplug_control
python get_device_id.py
```

範例輸出：
```
🔍 正在查詢 SwitchBot 設備...
✅ 成功找到 2 個設備:

📱 設備 1:
   名稱: 客廳插座
   ID: W0701600ABCD1234
   類型: Plug Mini (JP)
   狀態: 離線

📱 設備 2:
   名稱: 書房插座
   ID: W0701600EFGH5678
   類型: Plug Mini (JP)
   狀態: 在線
```

#### 步驟 4: 設定設備 ID
```bash
# 編輯 .env 檔案，加入設備 ID
echo "SWITCHBOT_DEVICE_ID=your_device_id_here" >> libraries/switchbot_smartplug_control/.env
```

## 使用方式

### 命令列工具使用

#### 1. 查詢設備狀態
```bash
cd libraries/switchbot_smartplug_control
python plug_control.py status
```

#### 2. 開啟插座
```bash
python plug_control.py on
```

#### 3. 關閉插座
```bash
python plug_control.py off
```

#### 4. 切換插座狀態
```bash
python plug_control.py toggle
```

### Robot Framework 測試案例

#### 基本使用範例
```robotframework
*** Settings ***
Library    libraries/switchbot_smartplug_control/SwitchBotSmartPlugLibrary.py
Resource   resources/switchbot_keywords.robot

*** Variables ***
${TEST_TOKEN}           your_switchbot_token_here
${TEST_SECRET}          your_switchbot_secret_here  
${TEST_DEVICE_ID}       your_device_id_here

*** Test Cases ***
測試智慧插座開啟功能
    [Tags]    smartplug    basic
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    When 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    And 設備資訊應該正確顯示    ${TEST_DEVICE_ID}
```

#### Gherkin 風格測試案例
```robotframework
Scenario: User Needs To Control Smart Plug Power
    [Documentation]    用戶需要控制智慧插座電源的完整流程
    [Tags]    smartplug    power    scenario
    
    Given 已設定SwitchBot API認證資訊    ${TEST_TOKEN}    ${TEST_SECRET}
    And 智慧插座系統已準備就緒
    And 已知智慧插座設備ID    ${TEST_DEVICE_ID}
    
    When 使用者查詢智慧插座目前狀態    ${TEST_DEVICE_ID}
    And 使用者開啟智慧插座    ${TEST_DEVICE_ID}
    And 等待設備狀態變更    ${TEST_DEVICE_ID}    2
    
    Then 智慧插座應該處於開啟狀態    ${TEST_DEVICE_ID}
    And 設備資訊應該正確顯示    ${TEST_DEVICE_ID}
    
    When 使用者關閉智慧插座    ${TEST_DEVICE_ID}
    And 等待設備狀態變更    ${TEST_DEVICE_ID}    2
    
    Then 智慧插座應該處於關閉狀態    ${TEST_DEVICE_ID}
    And 操作記錄應該完整保存
```

### 執行測試

#### 執行所有 SwitchBot 測試
```bash
robot tests/power_management/switchbot_smartplug_test.robot
```

#### 執行特定標籤的測試
```bash
robot --include smartplug tests/power_management/
robot --include gherkin tests/power_management/
```

#### 乾跑測試（語法檢查）
```bash
robot --dryrun tests/power_management/switchbot_smartplug_test.robot
```

## 主要關鍵字說明

### Given 關鍵字 (前置條件)
- **已設定SwitchBot API認證資訊** - 設定 API Token 和 Secret
- **已知智慧插座設備ID** - 設定要控制的設備 ID
- **智慧插座系統已準備就緒** - 檢查系統初始化狀態

### When 關鍵字 (操作動作)
- **使用者開啟智慧插座** - 開啟指定的智慧插座
- **使用者關閉智慧插座** - 關閉指定的智慧插座
- **使用者查詢智慧插座目前狀態** - 查詢插座目前狀態
- **等待設備狀態變更** - 等待設備狀態改變

### Then 關鍵字 (結果驗證)
- **智慧插座應該處於開啟狀態** - 驗證插座為開啟狀態
- **智慧插座應該處於關閉狀態** - 驗證插座為關閉狀態
- **設備資訊應該正確顯示** - 驗證設備資訊正確
- **操作記錄應該完整保存** - 檢查操作日誌記錄

### And 關鍵字 (連接詞)
- 可用於連接任何 Given/When/Then 關鍵字，保持測試案例的可讀性

## 錯誤處理與除錯

### 常見錯誤與解決方式

#### 1. 套件匯入錯誤
```
❌ 警告: requests 套件未安裝
```
**解決方式**:
```bash
pip install requests python-dotenv
```

#### 2. API 認證失敗
```
❌ 錯誤: 401 Unauthorized
```
**解決方式**: 檢查 Token 和 Secret 是否正確設定

#### 3. 設備無法連線
```
❌ 錯誤: 設備 [設備ID] 無法連線
```
**解決方式**: 
- 檢查設備是否在線
- 確認設備 ID 是否正確
- 檢查網路連線狀態

#### 4. 設備 ID 不存在
```
❌ 錯誤: 設備 [設備ID] 不存在
```
**解決方式**: 執行 `python get_device_id.py` 重新取得正確的設備 ID

### 除錯工具

#### 檢查設備狀態
```bash
python check_device.py
```

#### 查看詳細日誌
日誌檔案位置：`logs/switchbot_smartplug.log`
```bash
tail -f logs/switchbot_smartplug.log
```

#### 測試 API 連線
```bash
python -c "
from libraries.switchbot_smartplug_control.SwitchBotSmartPlugLibrary import SwitchBotSmartPlugLibrary
lib = SwitchBotSmartPlugLibrary()
lib.設定SwitchBot認證資訊('your_token', 'your_secret')
devices = lib.取得所有SwitchBot設備清單()
print(f'找到 {len(devices)} 個設備')
"
```

## 技術實作細節

### API 認證機制
- 使用 HMAC-SHA256 簽名驗證
- 時間戳記防重放攻擊
- 自動處理 API 請求頭設定

### 狀態管理
- 設備狀態快取機制
- 自動重新整理過期狀態
- 異常狀態自動重試

### 日誌記錄
- 多層級日誌輸出（DEBUG/INFO/WARNING/ERROR）
- Robot Framework 整合日誌
- 檔案與終端雙重輸出

## 擴展與客製化

### 新增自訂關鍵字
```python
@keyword("自訂智慧插座操作")
def custom_plug_operation(self, device_id: str, operation: str):
    """
    自訂智慧插座操作
    
    Args:
        device_id: 設備 ID
        operation: 操作類型
    """
    # 實作自訂邏輯
    pass
```

### 支援其他 SwitchBot 設備
本模組架構可擴展支援其他 SwitchBot 設備類型：
- SwitchBot Hub Mini
- SwitchBot Curtain
- SwitchBot Lock
- SwitchBot Thermometer

## 參考資源

- [SwitchBot API 官方文件](https://github.com/OpenWonderLabs/SwitchBotAPI) - 官方 HTTP API v1.1 文檔
- [Robot Framework 使用者指南](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)

## 技術實作說明

### API 認證機制

本模組使用 SwitchBot 官方 API v1.1 認證方式：

```python
# 簽名算法（HMAC-SHA256）
t = int(time.time() * 1000)  # 毫秒時間戳
nonce = str(uuid.uuid4())     # UUID v4 作為 nonce
string_to_sign = f"{token}{t}{nonce}"
sign = base64.b64encode(
    hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
).decode()

# HTTP Headers
headers = {
    "Authorization": token,
    "sign": sign,
    "nonce": nonce,
    "t": str(t),
    "Content-Type": "application/json; charset=utf8"
}
```

### 為什麼不使用第三方 SDK？

1. **pyswitchbot** - 這是藍牙控制套件，不適用於 HTTP API
2. **官方建議** - SwitchBot 官方文檔提供 HTTP API 範例，建議直接實作
3. **穩定性** - 直接使用 HTTP API 更加穩定，無第三方依賴問題

## 授權條款

本專案採用 MIT 授權條款。

---

**最後更新**: 2026-02-02
**版本**: v2.0.0
**狀態**: ✅ 生產就緒

### 版本歷程
- **v2.0.0** (2026-02-02): 重構為使用官方 HTTP API v1.1，移除第三方 SDK 依賴
- **v1.0.0** (2025-06-23): 初始版本
