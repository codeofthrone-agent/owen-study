# 多燈號陣列偵測系統

## 📖 簡介

**多燈號陣列偵測系統**是專為檢測紙箱分隔燈泡陣列而設計的智慧視覺偵測解決方案。

### 核心特色

✨ **同時偵測多個燈泡** - 支援 N×M 陣列配置（預設 3×4，共 12 個燈泡）
🎯 **精準 ROI 劃分** - 使用相對座標系統，自適應不同影像解析度
💡 **明滅與強弱判定** - 四級亮度分類（關閉、微弱、中等、明亮）
🖼️ **視覺化調試工具** - 即時顯示 ROI 區域與偵測結果
🔄 **狀態變化偵測** - 支援等待特定燈號模式，便於自動化測試

---

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝 uv (若尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境並安裝依賴
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 設定環境變數
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. 配置 IP Camera

在專案根目錄建立 `.env` 檔案：

```bash
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_password
```

### 3. 執行快速測試

```bash
python3 scripts/quick_multi_light_test.py
```

### 4. 視覺化檢查

```bash
python3 scripts/visualize_light_array.py --interactive
```

---

## 💻 Python 使用範例

### 基礎範例

```python
from libraries.ipcam_light_detection import MultiLightDetection

# 初始化偵測器
detector = MultiLightDetection('default_array')

# 連接攝影機
detector.connect_array_camera()

# 偵測所有燈號
results = detector.detect_all_lights()

# 查看結果
for light_key, result in results.items():
    print(f"{result['name']}: {result['brightness']:.2f} - {result['brightness_level']}")

# 儲存標註影像
detector.save_annotated_image('/tmp/result.jpg')

# 斷開連線
detector.disconnect()
```

### 進階範例：等待燈號模式

```python
# 定義預期模式（鍵值：True=開啟, False=關閉）
pattern = {
    '0_0': True,   # 燈泡 A1 應開啟
    '0_1': False,  # 燈泡 A2 應關閉
    '1_0': True,   # 燈泡 B1 應開啟
}

# 等待燈號符合預期模式（最長等待 30 秒）
success = detector.wait_for_light_pattern(pattern, timeout=30)

if success:
    print("✅ 燈號模式已符合預期")
else:
    print("❌ 等待逾時")
```

---

## 🤖 Robot Framework 使用範例

### 基礎測試案例

```robotframework
*** Settings ***
Resource    resources/multi_light_keywords.robot

*** Test Cases ***
測試燈號陣列
    Given 連接預設陣列攝影機
    When 偵測所有燈號並記錄
    Then 驗證陣列開啟數量    5
    And 儲存陣列標註影像    test_result.jpg
```

### 驗證單一燈號

```robotframework
*** Test Cases ***
驗證燈泡 A1 狀態
    Given 連接預設陣列攝影機
    When 偵測單一燈號並記錄    0_0
    Then 驗證燈號為開啟狀態    0_0
    And 驗證燈號亮度等級    0_0    bright
```

### 等待燈號變化

```robotframework
*** Test Cases ***
等待燈號開啟測試
    Given 連接預設陣列攝影機
    When 等待燈號開啟    0_0    timeout=30
    Then 驗證燈號為開啟狀態    0_0
```

---

## ⚙️ 配置說明

### 陣列配置（`config/ipcam_config.yaml`）

```yaml
multi_light_arrays:
  default_array:
    name: "實驗室燈泡陣列"
    environment: "laboratory"
    camera: "level1"

    layout:
      rows: 3               # 行數
      cols: 4               # 列數
      total_lights: 12      # 總燈泡數

    roi_detection:
      method: "manual"      # 偵測方式：auto / manual
      margin_ratio: 0.05    # ROI 邊界內縮比例

    manual_roi:
      # 格式：[row, col, x_min, y_min, x_max, y_max]
      - [0, 0, 0.00, 0.00, 0.25, 0.33]
      - [0, 1, 0.25, 0.00, 0.50, 0.33]
      # ... (其他 ROI)

    light_configs:
      "0_0":
        name: "燈泡 A1"
        bright_threshold: 150
        dark_threshold: 50

    brightness_levels:
      off: [0, 50]
      dim: [51, 100]
      medium: [101, 180]
      bright: [181, 255]
```

### ROI 座標系統

使用**相對座標**（0.0 - 1.0），與影像解析度無關：

```
座標範圍：
- x_min, x_max: 0.0（最左）~ 1.0（最右）
- y_min, y_max: 0.0（最上）~ 1.0（最下）

範例：3×4 陣列均勻劃分
┌─────────┬─────────┬─────────┬─────────┐
│ (0,0)   │ (0,1)   │ (0,2)   │ (0,3)   │
│ 0.00-   │ 0.25-   │ 0.50-   │ 0.75-   │
│ 0.25    │ 0.50    │ 0.75    │ 1.00    │
├─────────┼─────────┼─────────┼─────────┤
│ (1,0)   │ (1,1)   │ (1,2)   │ (1,3)   │
├─────────┼─────────┼─────────┼─────────┤
│ (2,0)   │ (2,1)   │ (2,2)   │ (2,3)   │
└─────────┴─────────┴─────────┴─────────┘
```

---

## 🔧 ROI 調校指南

### 步驟 1：初步配置

使用均勻劃分作為起點（見上方配置範例）。

### 步驟 2：視覺化檢查

```bash
python3 scripts/visualize_light_array.py --interactive
```

檢查項目：
- ✅ ROI 框是否對準燈泡中心
- ✅ 是否包含紙箱邊緣（應避免）
- ✅ 是否跨越多個燈泡（應避免）

### 步驟 3：微調座標

根據視覺化結果調整 `config/ipcam_config.yaml`：

```yaml
# 範例：燈泡 A1 的 ROI 往右移 0.02，往下移 0.01
- [0, 0, 0.02, 0.01, 0.23, 0.32]
```

### 步驟 4：調整內縮比例

如果紙箱邊緣干擾偵測：

```yaml
roi_detection:
  margin_ratio: 0.08  # 增加內縮（預設 0.05）
```

### 步驟 5：驗證

```bash
robot tests/ipcam_testing/multi_light_array_test.robot
```

---

## 📊 API 參考

### MultiLightDetection 類別

#### 建構函數

```python
detector = MultiLightDetection(array_name='default_array')
```

#### 主要方法

| 方法 | 說明 |
|------|------|
| `connect_array_camera()` | 連接陣列攝影機 |
| `capture_array_image()` | 擷取陣列影像 |
| `detect_single_light(light_key)` | 偵測單一燈號 |
| `detect_all_lights()` | 偵測所有燈號 |
| `get_light_status_summary()` | 取得統計摘要 |
| `save_annotated_image(path)` | 儲存標註影像 |
| `wait_for_light_pattern(pattern, timeout)` | 等待燈號模式 |
| `disconnect()` | 斷開連線 |

#### 回傳資料結構

##### detect_single_light() 回傳值

```python
{
    'light_key': '0_0',
    'row': 0,
    'col': 0,
    'name': '燈泡 A1',
    'brightness': 178.5,
    'brightness_level': 'medium',
    'is_on': True,
    'is_off': False,
    'bright_threshold': 150,
    'dark_threshold': 50,
    'timestamp': '2025-11-06 10:30:45'
}
```

##### get_light_status_summary() 回傳值

```python
{
    'total_lights': 12,
    'on_count': 5,
    'off_count': 7,
    'uncertain_count': 0,
    'level_counts': {'off': 7, 'medium': 3, 'bright': 2},
    'average_brightness': 95.3,
    'timestamp': '2025-11-06 10:30:45'
}
```

---

## 🛠️ 命令列工具

### visualize_light_array.py

視覺化與調試工具。

#### 基本使用

```bash
python3 scripts/visualize_light_array.py --output /tmp/viz.jpg
```

#### 互動模式

```bash
python3 scripts/visualize_light_array.py --interactive
```

#### 完整參數

```bash
python3 scripts/visualize_light_array.py \
    --array default_array \
    --output result.jpg \
    --interactive \
    --verbose
```

### quick_multi_light_test.py

快速功能驗證腳本。

```bash
python3 scripts/quick_multi_light_test.py
```

---

## 🧪 測試執行

### 執行所有測試

```bash
robot tests/ipcam_testing/multi_light_array_test.robot
```

### 執行特定測試

```bash
robot --test "測試案例 02: 偵測所有燈號狀態" \
      tests/ipcam_testing/multi_light_array_test.robot
```

### 標籤篩選

```bash
# 只執行核心偵測測試
robot --include detection tests/ipcam_testing/multi_light_array_test.robot

# 跳過需要手動操作的測試
robot --exclude manual tests/ipcam_testing/multi_light_array_test.robot
```

---

## 🐛 故障排除

### 常見問題

#### 1. 無法連接攝影機

**症狀：** `ConnectionError: 無法連接到 RTSP 串流`

**解決方案：**
- 確認 IP Camera 可 ping 通
- 檢查 `.env` 中的帳號密碼
- 測試 RTSP URL：
  ```bash
  ffmpeg -i rtsp://user:pass@192.168.165.184:554/live0 -frames:v 1 test.jpg
  ```

#### 2. ROI 區域偏移

**症狀：** ROI 框沒有對準燈泡

**解決方案：**
- 使用視覺化工具檢查：
  ```bash
  python3 scripts/visualize_light_array.py --interactive
  ```
- 調整 `config/ipcam_config.yaml` 中的 ROI 座標

#### 3. ModuleNotFoundError

**症狀：** `ModuleNotFoundError: No module named 'config'`

**解決方案：**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📚 相關文件

- **完整使用指南：** [docs/multi_light_array_detection_guide.md](../../docs/multi_light_array_detection_guide.md)
- **專案 README：** [README.md](../../README.md)
- **開發規範：** [.github/copilot-instructions.md](../../.github/copilot-instructions.md)

---

## 📝 版本資訊

- **版本：** 1.1.0
- **最後更新：** 2025-11-06
- **作者：** Robot Framework 多平台自動化測試系統
- **授權：** 專案內部使用

---

## 🎯 後續規劃

- [ ] 實作自動 ROI 偵測（邊緣檢測）
- [ ] 支援不規則陣列配置
- [ ] 新增顏色檢測功能
- [ ] 支援動態燈號變化錄影
- [ ] 整合機器學習模型提升準確度
