# iOS 真機測試環境設置指南

## 概述

本指南詳細說明如何在 Ubuntu 24.04 系統上設置 iOS 真機測試環境，使用 Appium 進行自動化測試。

## 系統需求

### 硬體需求
- **主機系統**: Ubuntu 24.04 LTS
- **iOS 設備**: iPhone/iPad (iOS 13.0+)
- **USB 傳輸線**: Lightning 或 USB-C 傳輸線
- **記憶體**: 建議 8GB RAM 以上
- **儲存空間**: 至少 10GB 可用空間

### 軟體需求
- Node.js 18.x 或更高版本
- Appium 2.x
- libimobiledevice 工具
- Python 3.8+

## 安裝步驟

### 1. 系統依賴安裝

```bash
# 更新系統套件
sudo apt update && sudo apt upgrade -y

# 安裝基礎依賴
sudo apt install -y curl wget git build-essential

# 安裝 Node.js (如果尚未安裝)
sudo apt install -y nodejs npm

# 安裝 iOS 設備工具
sudo apt install -y libimobiledevice-utils usbmuxd libgtk-3-dev libnotify-dev libnss3 libxss1 libasound2t64
```

### 2. Appium 安裝

```bash
# 全域安裝 Appium
sudo npm install -g appium@next

# 安裝 iOS 驅動程式
appium driver install xcuitest

# 驗證安裝
appium --version
appium driver list
```

### 3. Python 環境設置

```bash
# 進入專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 啟動虛擬環境
source .venv/bin/activate

# 安裝 Python 套件
pip install Appium-Python-Client>=3.0.0 robotframework-appiumlibrary robotframework>=6.0
```

## iOS 設備準備

### 1. iOS 設備設定

1. **啟用開發者模式**:
   - 前往 **設定** > **隱私權與安全性** > **開發者模式**
   - 開啟開發者模式並重新啟動設備

2. **信任電腦**:
   - 將 iOS 設備連接到 Ubuntu 電腦
   - 在設備上點選「信任這部電腦」

3. **啟用 Web Inspector**:
   - 前往 **設定** > **Safari** > **進階**
   - 開啟「Web Inspector」

### 2. 設備連接驗證

```bash
# 檢查設備連接狀態
idevice_id -l

# 獲取設備資訊
ideviceinfo

# 獲取設備 UDID
idevice_id -l
```

### 3. 應用程式準備

對於測試應用程式，您需要：

1. **開發版應用** (.ipa 檔案):
   - 使用開發證書簽署的應用程式
   - 包含設備 UDID 的配置檔案

2. **或使用系統應用**:
   - Safari、設定、計算機等系統內建應用
   - 不需要額外安裝

## 配置設置

### 1. 環境變數設定

創建或更新 `.env` 檔案：

```bash
# iOS 測試配置
IOS_DEVICE_NAME=iPhone_15_Pro
IOS_PLATFORM_VERSION=17.0
IOS_UDID=your_device_udid_here
IOS_BUNDLE_ID=com.apple.calculator
IOS_XCODE_ORG_ID=your_team_id
IOS_XCODE_SIGNING_ID=iPhone Developer

# Appium 伺服器配置
APPIUM_HOST=localhost
APPIUM_PORT=4723
APPIUM_TIMEOUT=30
APPIUM_COMMAND_TIMEOUT=60
```

### 2. 設備配置檔案

更新 `config/mobile/appium_config.py` 中的 iOS 配置：

```python
def _get_ios_config(self) -> Dict[str, Any]:
    return {
        'platformName': 'iOS',
        'automationName': 'XCUITest',
        'deviceName': os.getenv('IOS_DEVICE_NAME', 'iPhone'),
        'platformVersion': os.getenv('IOS_PLATFORM_VERSION', '17.0'),
        'udid': os.getenv('IOS_UDID', ''),
        'bundleId': os.getenv('IOS_BUNDLE_ID', 'com.apple.calculator'),
        'xcodeOrgId': os.getenv('IOS_XCODE_ORG_ID', ''),
        'xcodeSigningId': os.getenv('IOS_XCODE_SIGNING_ID', ''),
        'newCommandTimeout': 60,
        'wdaStartupRetries': 3,
        'wdaStartupRetryInterval': 10000,
        'useNewWDA': False,
        'noReset': True,
        'fullReset': False,
    }
```

## 測試執行

### 1. 啟動 Appium 伺服器

```bash
# 背景啟動 Appium
./scripts/start_appium.sh --background

# 或前景啟動（用於除錯）
appium --port 4723 --log-level debug
```

### 2. 連接設備測試

```bash
# 驗證設備連接
python3 -c "
import subprocess
result = subprocess.run(['idevice_id', '-l'], capture_output=True, text=True)
if result.returncode == 0 and result.stdout.strip():
    print(f'iOS 設備已連接: {result.stdout.strip()}')
else:
    print('未檢測到 iOS 設備')
"
```

### 3. 執行測試案例

```bash
# 執行基本 iOS 測試
robot --variable PLATFORM:ios tests/mobile/ios/ios_app_test.robot

# 執行特定測試案例
robot --test "Scenario: User Launches iOS Application Successfully" tests/mobile/ios/ios_app_test.robot

# 產生詳細報告
robot --outputdir results/ios tests/mobile/ios/
```

## 疑難排解

### 常見問題與解決方案

#### 1. 設備無法檢測

**問題**: `idevice_id -l` 顯示錯誤或無設備

**解決方案**:
```bash
# 重新啟動 usbmuxd 服務
sudo systemctl restart usbmuxd

# 檢查 USB 連接
lsusb | grep Apple

# 重新插拔設備
```

#### 2. WebDriverAgent 啟動失敗

**問題**: Appium 無法啟動 WebDriverAgent

**解決方案**:
```bash
# 確認設備開發者模式已啟用
# 檢查 Xcode 組織 ID 和簽署 ID 設定
# 在設備上手動信任開發者證書
```

#### 3. 應用程式無法啟動

**問題**: Bundle ID 錯誤或應用程式未安裝

**解決方案**:
```bash
# 列出設備上安裝的應用程式
ideviceinstaller -l

# 檢查 Bundle ID 是否正確
# 對於系統應用，使用標準 Bundle ID (如 com.apple.calculator)
```

#### 4. 連接超時

**問題**: Appium 連接設備超時

**解決方案**:
```python
# 增加超時設定
capabilities.update({
    'newCommandTimeout': 120,
    'wdaStartupRetries': 5,
    'wdaStartupRetryInterval': 15000
})
```

### 日誌檢查

```bash
# Appium 伺服器日誌
tail -f logs/appium.log

# 系統 USB 日誌
sudo journalctl -f | grep usb

# libimobiledevice 除錯
export LIBIRECOVERY_DEBUG_LEVEL=2
ideviceinfo
```

## 進階配置

### 1. 多設備支援

```python
# 配置多個 iOS 設備
IOS_DEVICES = {
    'device1': {
        'udid': 'device1_udid',
        'deviceName': 'iPhone_15_Pro',
        'platformVersion': '17.0'
    },
    'device2': {
        'udid': 'device2_udid', 
        'deviceName': 'iPad_Air',
        'platformVersion': '17.0'
    }
}
```

### 2. 效能最佳化

```python
# 效能調整配置
capabilities.update({
    'skipLogCapture': True,
    'reducedMotion': True,
    'simpleIsVisibleCheck': True,
    'useJSONSource': True,
    'shouldUseCompactResponses': False
})
```

### 3. 安全性設定

```bash
# 建立專用測試用戶（可選）
sudo useradd -m iostest
sudo usermod -aG plugdev iostest

# 設定 udev 規則
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="05ac", MODE="0666"' | sudo tee /etc/udev/rules.d/99-ios-device.rules
sudo udevadm control --reload-rules
```

## 自動化腳本

### 設備檢查腳本

```bash
#!/bin/bash
# scripts/check_ios_device.sh

echo "檢查 iOS 設備連接狀態..."

# 檢查 libimobiledevice 工具
if ! command -v idevice_id &> /dev/null; then
    echo "錯誤: libimobiledevice-utils 未安裝"
    exit 1
fi

# 檢查設備連接
DEVICES=$(idevice_id -l 2>/dev/null)
if [ -z "$DEVICES" ]; then
    echo "警告: 未檢測到 iOS 設備"
    echo "請確認:"
    echo "1. 設備已連接並解鎖"
    echo "2. 已信任此電腦"
    echo "3. 已啟用開發者模式"
    exit 1
fi

echo "已檢測到 iOS 設備:"
echo "$DEVICES"

# 獲取設備資訊
for UDID in $DEVICES; do
    echo "設備 UDID: $UDID"
    DEVICE_NAME=$(ideviceinfo -u "$UDID" -k DeviceName 2>/dev/null)
    PRODUCT_VERSION=$(ideviceinfo -u "$UDID" -k ProductVersion 2>/dev/null)
    echo "設備名稱: $DEVICE_NAME"
    echo "iOS 版本: $PRODUCT_VERSION"
    echo "---"
done

echo "iOS 設備檢查完成 ✅"
```

### 環境驗證腳本

```bash
#!/bin/bash
# scripts/verify_ios_environment.sh

echo "驗證 iOS 測試環境..."

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# 檢查 Appium
if ! command -v appium &> /dev/null; then
    echo "❌ Appium 未安裝"
    exit 1
fi
echo "✅ Appium: $(appium --version)"

# 檢查 XCUITest 驅動
if ! appium driver list | grep -q "xcuitest.*installed"; then
    echo "❌ XCUITest 驅動未安裝"
    exit 1
fi
echo "✅ XCUITest 驅動已安裝"

# 檢查 Python 套件
if ! python3 -c "import appium" 2>/dev/null; then
    echo "❌ Appium Python 客戶端未安裝"
    exit 1
fi
echo "✅ Appium Python 客戶端已安裝"

# 檢查 iOS 設備工具
if ! command -v idevice_id &> /dev/null; then
    echo "❌ libimobiledevice-utils 未安裝"
    exit 1
fi
echo "✅ libimobiledevice-utils 已安裝"

echo "iOS 測試環境驗證完成 ✅"
```

## 參考資源

- [Appium 官方文檔](https://appium.io/docs/)
- [XCUITest 驅動程式](https://appium.io/docs/en/drivers/ios-xcuitest/)
- [libimobiledevice 工具](https://libimobiledevice.org/)
- [iOS WebDriverAgent](https://github.com/appium/WebDriverAgent)

---

**最後更新**: 2025-06-27
**維護者**: Robot Framework Team
