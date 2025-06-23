# 環境變數配置整合說明

本專案已將所有環境變數配置整合到統一的配置系統中。

## 📁 配置檔案結構

```
robot-test-project/
├── .env                    # 主要環境變數檔案 (請勿提交到版本控制)
├── .env.example           # 環境變數範例 (可安全提交)
├── .env.template          # 詳細配置範本
└── config/
    ├── __init__.py        # 統一配置匯出
    ├── voice_config.py    # 語音控制配置
    └── switchbot_config.py # SwitchBot 配置
```

## 🔧 設定方式

### 1. 複製範例檔案
```bash
cp .env.example .env
```

### 2. 編輯環境變數
```bash
nano .env
```

### 3. 填入必要配置
```properties
# SwitchBot 智慧插座 (必填)
TOKEN=your_switchbot_token_here
SECRET=your_switchbot_secret_here
DEVICE_ID=your_device_id_here

# 移動測試 (選填)
APPIUM_HOST=localhost
APPIUM_PORT=4723
IOS_DEVICE_NAME=iPhone 14
ANDROID_DEVICE_NAME=Android Emulator
```

## 📋 配置優先順序

系統會按以下順序讀取配置:

1. **專案根目錄 .env** (最高優先級)
2. **模組目錄 .env** (如 `libraries/switchbot_smartplug_control/.env`)
3. **系統環境變數** (最低優先級)

## 🎯 使用統一配置

在程式中使用統一配置:

```python
# 使用統一配置系統
from config.switchbot_config import SWITCHBOT_CREDENTIALS, SWITCHBOT_API_CONFIG
from config import get_config_value

# 取得配置
token = SWITCHBOT_CREDENTIALS['token']
api_timeout = SWITCHBOT_API_CONFIG['api_timeout']
```

## 🔒 安全注意事項

1. **`.env` 檔案已加入 `.gitignore`** - 不會意外提交敏感資訊
2. **使用範例檔案** - `.env.example` 和 `.env.template` 可安全提交
3. **權限控制** - 確保 `.env` 檔案只有必要使用者可讀取
4. **定期更新** - 定期更換 API Token 和 Secret

## 📖 快速開始

1. **SwitchBot 設定**:
   ```bash
   # 取得設備 ID
   pipenv run python libraries/switchbot_smartplug_control/get_device_id.py
   
   # 測試連接
   pipenv run python libraries/switchbot_smartplug_control/plug_control.py status
   ```

2. **移動測試設定**:
   ```bash
   # 啟動 Appium
   appium --port 4723
   
   # 執行移動測試
   robot tests/mobile/
   ```

3. **語音測試設定**:
   ```bash
   # 執行語音測試
   robot tests/physical_interaction/voice_test.robot
   ```

## 🛠️ 故障排除

### 找不到配置
- 確認 `.env` 檔案在專案根目錄
- 檢查環境變數名稱是否正確

### SwitchBot API 錯誤
- 驗證 TOKEN 和 SECRET 是否正確
- 確認 DEVICE_ID 存在於您的帳戶中

### 移動測試連接失敗
- 確認 Appium 伺服器已啟動
- 檢查設備是否已連接並授權

---

**更新日期**: 2025-06-23  
**整合完成**: SwitchBot 配置系統 ✅
