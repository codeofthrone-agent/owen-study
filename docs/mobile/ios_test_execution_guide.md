# iOS 真機測試執行指南

## 概述

本指南提供詳細的 iOS 真機測試執行步驟，涵蓋環境準備、設備連接、測試執行和結果分析的完整流程。

## 前置準備

### 1. 環境需求檢查

```bash
# 檢查系統版本
lsb_release -a

# 檢查可用記憶體
free -h

# 檢查磁碟空間
df -h .

# 確認專案目錄
pwd
```

### 2. 一鍵式環境設置

```bash
# 進入專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 執行完整環境設置
./scripts/setup_ios_testing.sh --install-deps --verbose

# 驗證設置結果
./scripts/setup_ios_testing.sh --verify-only
```

### 3. 手動環境驗證

```bash
# 檢查 Node.js 和 npm
node --version
npm --version

# 檢查 Appium 安裝
appium --version
appium driver list

# 檢查 iOS 工具
idevice_id --help
ideviceinfo --help

# 檢查 Python 環境
source .venv/bin/activate
python3 -c "import appium; print('Appium Python 客戶端可用')"
python3 -c "from AppiumLibrary import AppiumLibrary; print('AppiumLibrary 可用')"
```

## 設備準備

### 1. iOS 設備設定

#### 啟用開發者模式
1. 前往 **設定** > **隱私權與安全性** > **開發者模式**
2. 開啟開發者模式
3. 重新啟動設備
4. 確認開發者模式已啟用

#### 信任電腦連接
1. 使用 USB 傳輸線連接 iOS 設備到 Ubuntu 電腦
2. 在 iOS 設備上會彈出「信任這部電腦？」對話框
3. 點選「信任」
4. 輸入設備密碼確認

#### 啟用 Web Inspector (可選)
1. 前往 **設定** > **Safari** > **進階**
2. 開啟「Web Inspector」

### 2. 設備連接驗證

```bash
# 基本設備檢測
idevice_id -l

# 詳細設備資訊
ideviceinfo

# 使用專用檢查腳本
./scripts/check_ios_device.sh --verbose

# JSON 格式輸出
./scripts/check_ios_device.sh --json
```

### 3. 設備狀態確認

```bash
# 檢查設備名稱
ideviceinfo -k DeviceName

# 檢查 iOS 版本
ideviceinfo -k ProductVersion

# 檢查設備型號
ideviceinfo -k ProductType

# 檢查設備 UDID
idevice_id -l
```

## 測試執行

### 1. 啟動 Appium 伺服器

#### 背景啟動 (推薦)
```bash
# 使用專用啟動腳本
./scripts/start_appium.sh --background --port=4723

# 檢查 Appium 服務狀態
curl -X GET http://localhost:4723/wd/hub/status
```

#### 前景啟動 (除錯模式)
```bash
# 詳細日誌模式
appium --port 4723 --log-level debug

# 基本模式
appium --port 4723
```

### 2. 執行測試案例

#### 完整測試套件
```bash
# 執行所有 iOS 真機測試
robot tests/mobile/ios/ios_real_device_test.robot

# 產生詳細報告
robot --outputdir results/ios tests/mobile/ios/ios_real_device_test.robot
```

#### 特定測試案例
```bash
# 執行計算機應用測試
robot --test "Scenario: 自動檢測並連接 iOS 真機進行計算機應用測試" \
      tests/mobile/ios/ios_real_device_test.robot

# 執行設定應用測試
robot --test "Scenario: 測試 iOS 設定應用的系統資訊存取" \
      tests/mobile/ios/ios_real_device_test.robot

# 執行手勢操作測試
robot --test "Scenario: 驗證 iOS 設備的多點觸控和手勢操作" \
      tests/mobile/ios/ios_real_device_test.robot

# 執行設備旋轉測試
robot --test "Scenario: 測試設備旋轉和不同方向下的應用行為" \
      tests/mobile/ios/ios_real_device_test.robot
```

#### 標籤過濾
```bash
# 僅執行基本測試
robot --include smoke tests/mobile/ios/ios_real_device_test.robot

# 執行功能測試
robot --include functional tests/mobile/ios/ios_real_device_test.robot

# 執行手勢相關測試
robot --include gestures tests/mobile/ios/ios_real_device_test.robot

# 排除特定測試
robot --exclude orientation tests/mobile/ios/ios_real_device_test.robot
```

### 3. 測試配置自定義

#### 環境變數設定
```bash
# 指定特定設備
export IOS_UDID="your_device_udid_here"

# 指定應用程式
export IOS_BUNDLE_ID="com.apple.calculator"

# 設定超時時間
export APPIUM_TIMEOUT=60

# 執行測試
robot tests/mobile/ios/ios_real_device_test.robot
```

#### 動態變數傳遞
```bash
# 傳遞變數到測試
robot --variable PLATFORM:ios \
      --variable TEST_TIMEOUT:30 \
      --variable SCREENSHOT_DIR:results/screenshots/custom \
      tests/mobile/ios/ios_real_device_test.robot
```

## 結果分析

### 1. 測試報告檢視

```bash
# 開啟 HTML 報告
firefox results/report.html

# 開啟詳細日誌
firefox results/log.html

# 檢視 XML 結果
cat results/output.xml
```

### 2. 螢幕截圖檢視

```bash
# 查看截圖目錄
ls -la results/screenshots/ios/

# 使用圖片檢視器
eog results/screenshots/ios/*.png
```

### 3. 日誌分析

```bash
# 檢視 Appium 日誌
tail -f logs/appium.log

# 檢視系統日誌
sudo journalctl -f | grep -E "(usb|ios|appium)"

# 檢視測試執行日誌
grep -i "error\|fail\|exception" results/log.html
```

## 疑難排解

### 1. 常見問題

#### 設備未檢測到
```bash
# 重新啟動 USB 服務
sudo systemctl restart usbmuxd

# 檢查 USB 連接
lsusb | grep Apple

# 重新插拔設備
# 等待 5 秒後重新檢測
./scripts/check_ios_device.sh
```

#### Appium 連接失敗
```bash
# 檢查 Appium 伺服器狀態
curl -X GET http://localhost:4723/wd/hub/status

# 重新啟動 Appium
./scripts/stop_appium.sh
./scripts/start_appium.sh --background

# 清除 Appium 緩存
rm -rf ~/.appium/node_modules/.cache/
```

#### WebDriverAgent 啟動失敗
```bash
# 檢查設備開發者模式
ideviceinfo -k DeveloperModeStatus

# 在設備上手動信任開發者證書
# 設定 > 一般 > VPN 與裝置管理 > 開發者 App > 信任

# 增加啟動超時時間
export WDA_STARTUP_TIMEOUT=120000
```

#### 應用程式無法啟動
```bash
# 檢查 Bundle ID 是否正確
ideviceinstaller -l | grep calculator

# 對於系統應用使用標準 Bundle ID
export IOS_BUNDLE_ID="com.apple.calculator"

# 檢查應用程式權限
# 確保應用程式在設備上可正常啟動
```

### 2. 除錯模式

#### 啟用詳細日誌
```bash
# 設定環境變數
export APPIUM_LOG_LEVEL=debug
export LIBIRECOVERY_DEBUG_LEVEL=2

# 啟動詳細日誌 Appium
appium --port 4723 --log-level debug --log appium_debug.log

# 執行測試並記錄詳細輸出
robot --loglevel DEBUG tests/mobile/ios/ios_real_device_test.robot
```

#### 單步除錯
```bash
# 執行單一測試案例
robot --test "Given iOS 真機已自動檢測並配置" \
      tests/mobile/ios/ios_real_device_test.robot

# 使用 dryrun 檢查語法
robot --dryrun tests/mobile/ios/ios_real_device_test.robot
```

### 3. 效能最佳化

#### 調整配置以改善效能
```bash
# 設定效能相關環境變數
export APPIUM_NEW_COMMAND_TIMEOUT=120
export WDA_STARTUP_RETRIES=5
export SIMPLE_IS_VISIBLE_CHECK=true

# 執行測試
robot tests/mobile/ios/ios_real_device_test.robot
```

#### 並行執行 (多設備)
```bash
# 如果有多個 iOS 設備
# 設備 1
export IOS_UDID="device1_udid"
export APPIUM_PORT=4723
robot --outputdir results/device1 tests/mobile/ios/ios_real_device_test.robot &

# 設備 2  
export IOS_UDID="device2_udid"
export APPIUM_PORT=4724
robot --outputdir results/device2 tests/mobile/ios/ios_real_device_test.robot &

# 等待所有測試完成
wait
```

## 最佳實踐

### 1. 測試前檢查清單

- [ ] 系統環境已正確設置
- [ ] iOS 設備已連接並信任電腦
- [ ] 設備已啟用開發者模式
- [ ] Appium 伺服器正在執行
- [ ] 設備檢查腳本執行成功
- [ ] 測試應用程式可正常啟動

### 2. 測試執行最佳實踐

- 每次測試前確認設備連接狀態
- 使用背景模式啟動 Appium 以避免中斷
- 定期清理測試結果和截圖目錄
- 記錄測試環境配置供後續參考
- 使用標籤過濾執行相關測試案例

### 3. 結果管理

```bash
# 建立帶時間戳的結果目錄
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p results/ios_$TIMESTAMP

# 執行測試並儲存結果
robot --outputdir results/ios_$TIMESTAMP tests/mobile/ios/ios_real_device_test.robot

# 壓縮結果以供存檔
tar -czf results/ios_test_$TIMESTAMP.tar.gz results/ios_$TIMESTAMP/
```

## 參考資源

- [iOS 設備設置指南](ios_device_setup.md)
- [Appium iOS 驅動文檔](https://appium.io/docs/en/drivers/ios-xcuitest/)
- [libimobiledevice 工具文檔](https://libimobiledevice.org/)
- [Robot Framework 官方文檔](https://robotframework.org/)

---

**最後更新**: 2025-06-27  
**維護者**: Robot Framework Team
