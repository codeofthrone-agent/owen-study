# 多模態檢測模組

整合語音、視覺與序列埠日誌的多感官檢測系統，提供語音助理、IoT 設備與系統配置的全方位測試功能。

## 功能特色

- 🎤 **語音助理檢測** - 整合語音輸出、視覺檢測與 UART 日誌檢測
- 👁️ **視覺檢測整合** - 結合 IP Camera 亮度檢測進行視覺回饋驗證
- 📡 **序列埠監控** - UART 日誌即時解析與聲音播放狀態檢測
- 🔧 **遠端配置驗證** - 遠端系統設定檔案的完整性驗證
- 🔄 **多模態同步** - 多個感測器的同步檢測與邏輯驗證
- 🤖 **Robot Framework 整合** - 完整的中文關鍵字支援

## 系統需求

### 必要套件

```bash
pip install pyserial loguru pyyaml python-dotenv pathlib
```

### 硬體需求

- UART/Serial 介面（用於日誌監控）
- IP Camera（用於視覺檢測）
- 音訊播放設備（用於語音觸發）
- 語音助理或 IoT 設備（測試目標）

## 快速開始

### 1. 配置設定

編輯專案根目錄的 `.env` 文件：

```bash
# UART 設定
UART_PORT=/dev/ttyS0
UART_BAUDRATE=115200

# 語音助理設定
SCARLETT_CHANNEL=1

# 遠端系統配置
REMOTE_HOST=192.168.1.100
REMOTE_USER=admin
REMOTE_PASSWORD=password
```

### 2. Python 使用範例

```python
from libraries.multimodal_detection import VoiceAssistantDetection

# 初始化語音助理檢測
detector = VoiceAssistantDetection()

# 執行完整的語音助理檢測
result = detector.test_voice_assistant_response(
    wake_word="Hey Assistant",
    camera_env="living_room",
    camera_name="main_cam",
    scarlett_channel=1,
    uart_port="/dev/ttyS0"
)

# 檢查結果
if result["overall_success"]:
    print("語音助理回應測試成功!")
    print(f"視覺檢測: {result['vision_detected']}")
    print(f"聽覺檢測: {result['audio_detected']}")
else:
    print(f"測試失敗: {result['failure_reason']}")
```

### 3. Robot Framework 使用範例

```robotframework
*** Settings ***
Resource    resources/multimodal_keywords.robot

*** Test Cases ***
語音助理多模態測試
    Given 初始化多模態檢測系統
    When 執行語音助理回應測試
    ...    wake_word=Hey Assistant
    ...    camera_env=living_room
    ...    camera_name=main_cam
    ...    scarlett_channel=1
    ...    uart_port=/dev/ttyS0
    Then 驗證語音助理回應成功
    And 檢查視覺檢測結果
    And 檢查聽覺檢測結果

UART 日誌監控測試
    Given 開始 UART 日誌監控    /dev/ttyS0
    When 觸發系統事件
    Then 驗證日誌包含預期內容    audio_playing
    And 停止 UART 監控

遠端系統配置驗證
    Given 連接遠端系統    192.168.1.100
    When 驗證系統配置檔案    /etc/config.json
    Then 配置檔案應該有效
    And 所有必要參數應該存在
```

## API 參考

### VoiceAssistantDetection 類別

#### test_voice_assistant_response(wake_word, camera_env, camera_name, scarlett_channel, uart_port)
執行完整的語音助理多模態檢測。

```python
result = detector.test_voice_assistant_response(
    wake_word="Hey Power Pro",
    camera_env="laboratory", 
    camera_name="level1",
    scarlett_channel=1,
    uart_port="/dev/ttyS0"
)
```

**回傳結果結構:**
```python
{
    "overall_success": True/False,     # 整體測試結果
    "vision_detected": True/False,     # 視覺檢測結果
    "audio_detected": True/False,      # 聽覺檢測結果
    "failure_reason": "錯誤原因",       # 失敗原因（如有）
    "execution_time": 12.34,          # 執行時間（秒）
    "timestamp": "2025-11-11 10:30:45" # 測試時間戳記
}
```

### SerialLogParser 類別

#### start_monitoring(port, baudrate=115200)
開始監控 UART 序列埠日誌。

```python
from libraries.multimodal_detection import SerialLogParser

parser = SerialLogParser()
parser.start_monitoring("/dev/ttyS0", baudrate=115200)
```

#### stop_monitoring()
停止 UART 監控並返回收集的日誌。

```python
logs = parser.stop_monitoring()
```

#### check_audio_playing(timeout=30)
檢測 UART 日誌中的音訊播放狀態。

```python
is_playing = parser.check_audio_playing(timeout=30)
```

### RemoteSystemConfigValidator 類別

#### connect(host, username, password, port=22)
連接到遠端系統。

```python
from libraries.multimodal_detection import RemoteSystemConfigValidator

validator = RemoteSystemConfigValidator()
validator.connect("192.168.1.100", "admin", "password")
```

#### validate_config_file(file_path)
驗證遠端配置檔案。

```python
is_valid = validator.validate_config_file("/etc/config.json")
```

#### check_system_status()
檢查遠端系統狀態。

```python
status = validator.check_system_status()
```

#### execute_command(command)
在遠端系統執行指令。

```python
result = validator.execute_command("systemctl status audio-service")
```

## Robot Framework 關鍵字

### 語音助理檢測

- `測試語音助理回應    wake_word=${wake_word}    camera_env=${env}    camera_name=${name}    scarlett_channel=${channel}    uart_port=${port}`
- `驗證語音助理回應成功`
- `檢查視覺檢測結果`
- `檢查聽覺檢測結果`
- `取得語音助理測試結果`

### UART 日誌監控

- `開始 UART 日誌監控    ${port}    baudrate=${baudrate}`
- `停止 UART 監控`
- `檢查 UART 日誌內容    ${expected_content}`
- `驗證日誌包含預期內容    ${pattern}`
- `等待 UART 日誌訊息    ${pattern}    timeout=${timeout}`

### 遠端系統驗證

- `連接遠端系統    ${host}    ${username}    ${password}    port=${port}`
- `驗證系統配置檔案    ${file_path}`
- `配置檔案應該有效`
- `所有必要參數應該存在`
- `檢查系統服務狀態    ${service_name}`
- `執行遠端指令    ${command}`
- `斷開遠端連線`

### 多模態整合

- `初始化多模態檢測系統`
- `同步檢測多個感測器`
- `驗證多模態檢測結果`
- `產生檢測報告    ${output_path}`

### 系統狀態檢查

- `檢查硬體連線狀態`
- `驗證所有感測器就緒`
- `重設檢測系統`
- `清理檢測資源`

## 配置說明

### 語音助理配置

```python
VOICE_ASSISTANT_CONFIG = {
    "wake_words": ["Hey Assistant", "OK Google", "Alexa"],
    "response_timeout": 30,
    "detection_threshold": 0.8,
    "retry_attempts": 3,
    "channels": {
        1: "主要語音頻道",
        2: "備用語音頻道"
    }
}
```

### UART 監控配置

```python
UART_CONFIG = {
    "port": "/dev/ttyS0",
    "baudrate": 115200,
    "timeout": 1.0,
    "buffer_size": 8192,
    "log_patterns": {
        "audio_playing": r"audio.*playing|sound.*start",
        "audio_stopped": r"audio.*stop|sound.*end",
        "system_ready": r"system.*ready|init.*complete"
    }
}
```

### 視覺檢測整合

```python
VISION_INTEGRATION = {
    "brightness_change_threshold": 20,
    "detection_timeout": 15,
    "stable_duration": 2.0,
    "region": "center",
    "retry_interval": 1.0
}
```

### 遠端系統配置

```python
REMOTE_CONFIG = {
    "connection_timeout": 10,
    "command_timeout": 30,
    "config_paths": [
        "/etc/config.json",
        "/opt/app/settings.yaml",
        "/var/lib/app/runtime.conf"
    ],
    "required_services": [
        "audio-service",
        "voice-assistant",
        "network-manager"
    ]
}
```

## 測試執行

### 執行所有測試

```bash
robot tests/multimodal_detection/multimodal_test_suite.robot
```

### 執行特定類型測試

```bash
# 語音助理測試
robot --include voice_assistant tests/multimodal_detection/

# UART 監控測試
robot --include uart_monitoring tests/multimodal_detection/

# 遠端配置驗證測試
robot --include remote_config tests/multimodal_detection/
```

### 詳細日誌輸出

```bash
robot --loglevel DEBUG --outputdir results/multimodal tests/multimodal_detection/
```

## 故障排除

### 問題：UART 連接失敗

**可能原因:**
- 序列埠權限不足
- 設備未連接
- 波特率設定錯誤

**解決方法:**
```bash
# 檢查序列埠權限
sudo chmod 666 /dev/ttyS0

# 檢查設備連接
ls -la /dev/tty*

# 測試序列埠通信
screen /dev/ttyS0 115200
```

### 問題：語音檢測失敗

**可能原因:**
- 音訊設備未就緒
- 語音助理未啟動
- 網路連線問題

**解決方法:**
1. 檢查音訊設備狀態
2. 重啟語音助理服務
3. 確認網路連線穩定
4. 調整檢測閾值

### 問題：視覺檢測不準確

**可能原因:**
- IP Camera 連線問題
- 光線環境變化
- 亮度閾值設定不當

**解決方法:**
1. 檢查 IP Camera 連線
2. 調整環境光線
3. 重新校準亮度閾值
4. 使用不同的檢測區域

### 問題：遠端連線失敗

**可能原因:**
- SSH 服務未啟動
- 防火牆阻擋
- 認證資訊錯誤

**解決方法:**
```bash
# 檢查 SSH 服務狀態
sudo systemctl status ssh

# 測試連線
ssh user@host

# 檢查防火牆規則
sudo ufw status
```

## 進階使用

### 自訂檢測模式

```python
# 自訂多模態檢測邏輯
def custom_detection_logic(vision_result, audio_result, uart_result):
    """
    自訂檢測邏輯：任一模態成功即視為成功
    """
    return any([vision_result, audio_result, uart_result])

# 應用自訂邏輯
detector.set_detection_logic(custom_detection_logic)
```

### 批次測試

```python
# 批次語音指令測試
wake_words = ["Hey Assistant", "OK Google", "Alexa"]
results = []

for wake_word in wake_words:
    result = detector.test_voice_assistant_response(
        wake_word=wake_word,
        camera_env="living_room",
        camera_name="main_cam"
    )
    results.append(result)

# 分析結果
success_rate = sum(1 for r in results if r["overall_success"]) / len(results)
print(f"成功率: {success_rate:.2%}")
```

### 即時監控

```python
# 即時多模態監控
def real_time_monitoring():
    detector.start_continuous_monitoring()
    
    while True:
        status = detector.get_current_status()
        print(f"視覺: {status['vision']}, 聽覺: {status['audio']}, UART: {status['uart']}")
        time.sleep(1)
        
        if detector.detect_anomaly():
            print("檢測到異常事件!")
            break
```

### 效能分析

```python
# 效能基準測試
import time

start_time = time.time()
result = detector.test_voice_assistant_response(...)
end_time = time.time()

print(f"檢測時間: {end_time - start_time:.2f} 秒")
print(f"視覺檢測延遲: {result.get('vision_latency', 0):.2f} 秒")
print(f"聽覺檢測延遲: {result.get('audio_latency', 0):.2f} 秒")
```

## 整合範例

### 搭配 CI/CD 流程

```yaml
# GitHub Actions 範例
name: Multimodal Detection Tests
on: [push, pull_request]

jobs:
  multimodal-test:
    runs-on: self-hosted  # 需要硬體設備
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: pip install -r requirements.txt
      
    - name: Run multimodal tests
      run: |
        robot --outputdir results tests/multimodal_detection/
        
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: results/
```

### 搭配 TestLink 整合

```robotframework
*** Test Cases ***
語音助理整合測試
    [Tags]    integration    voice_assistant
    [Documentation]    測試語音助理的完整互動流程
    
    Given 執行語音助理回應測試    wake_word=Hey Assistant
    When 驗證多模態檢測結果
    Then 上傳測試結果至 TestLink
    And 更新測試案例狀態
    And 產生詳細測試報告
```

## 檔案結構

```
libraries/multimodal_detection/
├── __init__.py                          # 模組初始化
├── VoiceAssistantDetection.py           # 語音助理檢測
├── SerialLogParser.py                   # UART 日誌解析器
├── RemoteSystemConfigValidator.py       # 遠端系統配置驗證
├── logs/                                # 日誌檔案
└── README.md                            # 本說明文件

resources/
└── multimodal_keywords.robot            # Robot Framework 關鍵字

tests/multimodal_detection/
├── voice_assistant_test.robot           # 語音助理測試
├── uart_monitoring_test.robot           # UART 監控測試
├── remote_config_test.robot             # 遠端配置測試
└── integration_test.robot               # 整合測試
```

## 效能建議

### 檢測優化

1. **並行處理**: 多個感測器並行檢測
2. **快取機制**: 重複使用連線和設定
3. **逾時設定**: 合理設定各模態的逾時時間
4. **資源釋放**: 及時釋放不需要的資源

### 準確度提升

1. **閾值調整**: 根據環境調整檢測閾值
2. **多次驗證**: 重要檢測進行多次確認
3. **環境校準**: 定期校準檢測環境
4. **異常處理**: 完善的異常處理機制

## 注意事項

1. **硬體依賴**: 需要實際的硬體設備支援
2. **環境穩定**: 測試環境應保持穩定
3. **同步精度**: 注意多模態間的時序同步
4. **資源管理**: 正確管理 UART、網路等資源
5. **權限要求**: 確保有足夠的系統權限

## 授權與貢獻

本模組為 robot-multiplatform-automation 專案的一部分。

## 更新日誌

### v1.0.0 (2025-11-11)
- ✨ 首次發布
- 🎤 語音助理多模態檢測功能
- 👁️ 視覺檢測整合
- 📡 UART 日誌監控
- 🔧 遠端系統配置驗證
- 🤖 完整 Robot Framework 整合
- 📝 中文關鍵字支援

## 相關資源

- [PySerial 文件](https://pyserial.readthedocs.io/)
- [語音助理 API 文件](https://developers.google.com/assistant)
- [UART 通信協議](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Robot Framework 文件](https://robotframework.org/)