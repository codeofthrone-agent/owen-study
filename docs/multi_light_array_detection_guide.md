# 多燈號陣列偵測系統使用指南

## 📋 目錄

1. [系統概述](#系統概述)
2. [架構設計](#架構設計)
3. [安裝與設定](#安裝與設定)
4. [配置說明](#配置說明)
5. [使用方式](#使用方式)
6. [Python API](#python-api)
7. [Robot Framework 關鍵字](#robot-framework-關鍵字)
8. [視覺化工具](#視覺化工具)
9. [ROI 調校指南](#roi-調校指南)
10. [故障排除](#故障排除)

---

## 系統概述

**多燈號陣列偵測系統**專為偵測紙箱分隔的燈泡陣列而設計，能夠：

- 🎯 **同時偵測多個燈泡**：支援 N×M 陣列配置（預設 3×4）
- 💡 **明滅與強弱判定**：判定每個燈泡的開關狀態與亮度等級（關閉、微弱、中等、明亮）
- 📊 **ROI 區域管理**：自動或手動劃分每個燈泡的 ROI（Region of Interest）
- 🖼️ **視覺化調試**：產生帶有標註的影像，方便調校與驗證
- 🔄 **狀態變化偵測**：等待燈號模式變化，支援自動化測試

### 應用場景

- 工控面板燈號陣列測試
- 多燈號警示系統驗證
- LED 顯示器像素測試
- 實體按鈕面板狀態回饋

---

## 架構設計

### 核心模組

```
多燈號陣列偵測系統
├── MultiLightDetection.py          # 核心偵測引擎
├── IPCamLightDetection.py          # 基礎 IP Camera 偵測（繼承）
├── multi_light_keywords.robot      # Robot Framework 關鍵字集
├── visualize_light_array.py        # 視覺化調試工具
└── ipcam_config.yaml               # 配置文件
```

### 設計模式

#### 1. ROI 分割演算法

系統使用**相對座標系統**（0.0 - 1.0）定義每個燈泡的 ROI 區域：

```yaml
manual_roi:
  # 格式：[row, col, x_min, y_min, x_max, y_max]
  - [0, 0, 0.00, 0.00, 0.25, 0.33]  # 第 0 行第 0 列
  - [0, 1, 0.25, 0.00, 0.50, 0.33]  # 第 0 行第 1 列
```

**優點：**
- 與影像解析度無關
- 容易調整與維護
- 支援不同攝影機角度

#### 2. 亮度分級系統

系統將亮度（0-255）劃分為 4 個等級：

| 等級 | 範圍 | 說明 |
|------|------|------|
| `off` | 0-50 | 關閉 |
| `dim` | 51-100 | 微弱 |
| `medium` | 101-180 | 中等 |
| `bright` | 181-255 | 明亮 |

---

## 安裝與設定

### 1. 系統需求

- Ubuntu 24.04（主要開發環境）
- Python 3.12+
- IP Camera 支援 RTSP 協議
- 紙箱分隔的燈泡陣列

### 2. 安裝依賴套件

```bash
# 進入專案根目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 安裝 uv (若尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境並安裝所有相依套件
uv venv
source .venv/bin/activate

# 安裝專案依賴（包含 opencv-python、loguru、pyyaml、numpy 等）
uv pip install -r requirements.txt

# 或使用 uv run 直接執行（自動管理環境）
uv run python3 scripts/quick_multi_light_test.py
```

### 3. 環境變數設定

在專案根目錄建立 `.env` 檔案：

```bash
# IP Camera 認證資訊
IPCAM_USERNAME=admin
IPCAM_PASSWORD=your_password_here
```

### 4. 設定 PYTHONPATH

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 配置說明

### 配置文件位置

所有配置位於 `config/ipcam_config.yaml`

### 基本配置範例

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
      margin_ratio: 0.05    # ROI 邊界內縮比例（避免紙箱邊緣）

    manual_roi:
      # [row, col, x_min, y_min, x_max, y_max]
      - [0, 0, 0.00, 0.00, 0.25, 0.33]
      - [0, 1, 0.25, 0.00, 0.50, 0.33]
      # ... (其他 ROI 定義)

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

### ROI 座標系統說明

#### 相對座標（0.0 - 1.0）

- `x_min`: 左邊界（0.0 = 最左側，1.0 = 最右側）
- `y_min`: 上邊界（0.0 = 最上方，1.0 = 最下方）
- `x_max`: 右邊界
- `y_max`: 下邊界

#### 範例：3×4 陣列均勻劃分

```
┌─────────┬─────────┬─────────┬─────────┐
│ (0,0)   │ (0,1)   │ (0,2)   │ (0,3)   │  第 0 行
│ 0.00-   │ 0.25-   │ 0.50-   │ 0.75-   │  y: 0.00-0.33
│ 0.25    │ 0.50    │ 0.75    │ 1.00    │
├─────────┼─────────┼─────────┼─────────┤
│ (1,0)   │ (1,1)   │ (1,2)   │ (1,3)   │  第 1 行
│         │         │         │         │  y: 0.33-0.67
├─────────┼─────────┼─────────┼─────────┤
│ (2,0)   │ (2,1)   │ (2,2)   │ (2,3)   │  第 2 行
│         │         │         │         │  y: 0.67-1.00
└─────────┴─────────┴─────────┴─────────┘
```

---

## 使用方式

### 方式一：Python API

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

# 取得摘要資訊
summary = detector.get_light_status_summary()
print(f"開啟數量: {summary['on_count']}")
print(f"關閉數量: {summary['off_count']}")

# 儲存標註影像
detector.save_annotated_image('/tmp/array_result.jpg')

# 斷開連線
detector.disconnect()
```

### 方式二：Robot Framework

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

### 方式三：視覺化工具

```bash
# 基本使用
python3 scripts/visualize_light_array.py --array default_array --output /tmp/viz.jpg

# 互動模式
python3 scripts/visualize_light_array.py --interactive

# 詳細日誌
python3 scripts/visualize_light_array.py --verbose --output result.jpg
```

---

## Python API

### MultiLightDetection 類別

#### 初始化

```python
detector = MultiLightDetection(array_name='default_array')
```

#### 主要方法

##### 連接攝影機

```python
detector.connect_array_camera()
```

##### 擷取影像

```python
image = detector.capture_array_image()
```

##### 偵測單一燈號

```python
result = detector.detect_single_light('0_0')
# result = {
#     'light_key': '0_0',
#     'row': 0,
#     'col': 0,
#     'name': '燈泡 A1',
#     'brightness': 178.5,
#     'brightness_level': 'medium',
#     'is_on': True,
#     'is_off': False,
#     'bright_threshold': 150,
#     'dark_threshold': 50,
#     'timestamp': '2025-11-06 10:30:45'
# }
```

##### 偵測所有燈號

```python
results = detector.detect_all_lights(capture_new_image=True)
# results = {
#     '0_0': {...},
#     '0_1': {...},
#     ...
# }
```

##### 取得狀態摘要

```python
summary = detector.get_light_status_summary()
# summary = {
#     'total_lights': 12,
#     'on_count': 5,
#     'off_count': 7,
#     'uncertain_count': 0,
#     'level_counts': {'off': 7, 'medium': 3, 'bright': 2},
#     'average_brightness': 95.3,
#     'timestamp': '2025-11-06 10:30:45'
# }
```

##### 等待燈號模式

```python
pattern = {'0_0': True, '0_1': False, '1_0': True}
success = detector.wait_for_light_pattern(pattern, timeout=30)
```

##### 儲存標註影像

```python
detector.save_annotated_image('/tmp/result.jpg', show_brightness=True)
```

---

## Robot Framework 關鍵字

### 連接相關

| 關鍵字 | 說明 |
|--------|------|
| `連接預設陣列攝影機` | 連接預設配置的陣列攝影機 |
| `連接指定陣列攝影機 ${array_name}` | 連接指定名稱的陣列攝影機 |
| `斷開陣列攝影機` | 斷開連線並釋放資源 |

### 偵測相關

| 關鍵字 | 說明 |
|--------|------|
| `偵測所有燈號並記錄` | 偵測所有燈號並記錄到日誌 |
| `偵測單一燈號並記錄 ${light_key}` | 偵測單一燈號並記錄 |
| `擷取陣列影像` | 擷取陣列影像 |
| `取得燈號狀態摘要` | 取得統計摘要資訊 |

### 驗證相關

| 關鍵字 | 說明 |
|--------|------|
| `驗證燈號為開啟狀態 ${light_key}` | 驗證燈號為開啟 |
| `驗證燈號為關閉狀態 ${light_key}` | 驗證燈號為關閉 |
| `驗證燈號亮度等級 ${light_key} ${level}` | 驗證亮度等級 |
| `驗證陣列開啟數量 ${count}` | 驗證開啟數量 |
| `驗證陣列關閉數量 ${count}` | 驗證關閉數量 |

### 等待相關

| 關鍵字 | 說明 |
|--------|------|
| `等待燈號開啟 ${light_key}` | 等待燈號開啟 |
| `等待燈號關閉 ${light_key}` | 等待燈號關閉 |
| `等待陣列全部開啟` | 等待所有燈號開啟 |
| `等待陣列全部關閉` | 等待所有燈號關閉 |

### 其他

| 關鍵字 | 說明 |
|--------|------|
| `儲存陣列標註影像 ${filename}` | 儲存標註影像 |
| `比較兩次陣列亮度變化 ${delay}` | 比較亮度變化 |

---

## 視覺化工具

### 功能說明

`visualize_light_array.py` 提供以下功能：

1. **ROI 視覺化**：顯示每個燈泡的 ROI 區域
2. **狀態標註**：標註燈泡名稱、亮度、狀態、等級
3. **互動模式**：即時顯示視窗，按 Q 鍵關閉
4. **文字報告**：輸出完整的統計報告

### 使用範例

#### 基本使用

```bash
python3 scripts/visualize_light_array.py \
    --array default_array \
    --output /tmp/visualization.jpg
```

#### 互動模式

```bash
python3 scripts/visualize_light_array.py --interactive
```

#### 詳細日誌

```bash
python3 scripts/visualize_light_array.py \
    --verbose \
    --output result.jpg \
    --interactive
```

### 輸出範例

```
======================================================================
燈號陣列偵測報告
======================================================================

陣列名稱: 實驗室燈泡陣列
環境: laboratory
攝影機: level1
布局: 3x4

總燈泡數: 12
開啟數量: 5
關閉數量: 7
平均亮度: 95.32
等級分布: {'off': 7, 'medium': 3, 'bright': 2}

個別燈號狀態:
----------------------------------------------------------------------
名稱         鍵值     亮度        等級        狀態
----------------------------------------------------------------------
燈泡 A1      0_0      178.50     medium     開啟
燈泡 A2      0_1      35.20      off        關閉
燈泡 A3      0_2      220.80     bright     開啟
...
======================================================================
```

---

## ROI 調校指南

### 步驟 1：初步設定

使用均勻劃分作為初始配置：

```yaml
manual_roi:
  # 3 行 × 4 列 = 12 個燈泡
  - [0, 0, 0.00, 0.00, 0.25, 0.33]
  - [0, 1, 0.25, 0.00, 0.50, 0.33]
  - [0, 2, 0.50, 0.00, 0.75, 0.33]
  - [0, 3, 0.75, 0.00, 1.00, 0.33]
  # ... (依此類推)
```

### 步驟 2：視覺化檢查

```bash
python3 scripts/visualize_light_array.py --interactive
```

檢查項目：
- ✅ ROI 框是否對準燈泡中心
- ✅ ROI 框是否包含紙箱邊緣（應避免）
- ✅ ROI 框是否跨越多個燈泡（應避免）

### 步驟 3：微調 ROI

根據視覺化結果調整座標：

```yaml
# 範例：如果燈泡 A1 的 ROI 偏左，調整 x_min 和 x_max
- [0, 0, 0.02, 0.01, 0.23, 0.32]  # 往右移 0.02，往下移 0.01
```

### 步驟 4：調整邊界內縮

如果紙箱邊緣干擾偵測，增加 `margin_ratio`：

```yaml
roi_detection:
  margin_ratio: 0.08  # 增加內縮比例（預設 0.05）
```

### 步驟 5：驗證

執行測試案例驗證調校結果：

```bash
robot tests/ipcam_testing/multi_light_array_test.robot
```

---

## 故障排除

### 問題 1：無法連接攝影機

**症狀：** `ConnectionError: 無法連接到 RTSP 串流`

**解決方案：**
1. 確認 IP Camera 已開機並可 ping 通
2. 檢查 `.env` 中的帳號密碼是否正確
3. 確認 RTSP 端口（預設 554）未被防火牆阻擋
4. 測試 RTSP URL：
   ```bash
   ffmpeg -i rtsp://username:password@192.168.165.184:554/live0 -frames:v 1 test.jpg
   ```

### 問題 2：ROI 區域偏移

**症狀：** ROI 框沒有對準燈泡

**解決方案：**
1. 使用視覺化工具檢查：
   ```bash
   python3 scripts/visualize_light_array.py --interactive
   ```
2. 調整 `config/ipcam_config.yaml` 中的 ROI 座標
3. 增加 `margin_ratio` 避免紙箱邊緣干擾

### 問題 3：亮度判定錯誤

**症狀：** 明明開啟的燈被判定為關閉

**解決方案：**
1. 檢查實際亮度值：
   ```python
   detector = MultiLightDetection()
   detector.connect_array_camera()
   result = detector.detect_single_light('0_0')
   print(f"實際亮度: {result['brightness']}")
   ```
2. 調整閾值：
   ```yaml
   light_configs:
     "0_0":
       bright_threshold: 120  # 降低閾值
       dark_threshold: 40
   ```

### 問題 4：影像擷取失敗

**症狀：** `RuntimeError: 無法從串流讀取影像幀`

**解決方案：**
1. 增加重試次數和延遲：
   ```yaml
   connection:
     retry_attempts: 5
     retry_delay: 3
   ```
2. 調整 `frame_skip`：
   ```yaml
   connection:
     frame_skip: 5  # 跳過更多幀
   ```

### 問題 5：ModuleNotFoundError

**症狀：** `ModuleNotFoundError: No module named 'config'`

**解決方案：**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 進階配置

### 自訂燈泡名稱

```yaml
light_configs:
  "0_0":
    name: "電源指示燈"
  "0_1":
    name: "網路連線燈"
  "0_2":
    name: "錯誤警告燈"
```

### 個別燈泡閾值

```yaml
light_configs:
  "0_0":
    bright_threshold: 180  # 較高要求
    dark_threshold: 30
  "0_1":
    bright_threshold: 120  # 較低要求（可能是微弱的 LED）
    dark_threshold: 50
```

### 自訂亮度分級

```yaml
brightness_levels:
  off: [0, 30]
  very_dim: [31, 70]
  dim: [71, 120]
  medium: [121, 180]
  bright: [181, 230]
  very_bright: [231, 255]
```

---

## 測試執行

### 執行所有測試

```bash
robot tests/ipcam_testing/multi_light_array_test.robot
```

### 執行特定測試

```bash
robot --test "測試案例 02: 偵測所有燈號狀態" \
      tests/ipcam_testing/multi_light_array_test.robot
```

### 使用標籤篩選

```bash
# 只執行基本偵測測試
robot --include detection tests/ipcam_testing/multi_light_array_test.robot

# 跳過需要手動操作的測試
robot --exclude manual tests/ipcam_testing/multi_light_array_test.robot
```

### 產生詳細報告

```bash
robot --outputdir results/multi_light \
      --loglevel DEBUG \
      tests/ipcam_testing/multi_light_array_test.robot
```

---

## 附錄

### 支援的陣列配置

| 配置名稱 | 行數 | 列數 | 總燈泡數 |
|----------|------|------|----------|
| `default_array` | 3 | 4 | 12 |

### 燈泡鍵值對應表（3×4 陣列）

| 位置 | 鍵值 | 預設名稱 |
|------|------|----------|
| 第 0 行第 0 列 | `0_0` | 燈泡 A1 |
| 第 0 行第 1 列 | `0_1` | 燈泡 A2 |
| 第 0 行第 2 列 | `0_2` | 燈泡 A3 |
| 第 0 行第 3 列 | `0_3` | 燈泡 A4 |
| 第 1 行第 0 列 | `1_0` | 燈泡 B1 |
| ... | ... | ... |
| 第 2 行第 3 列 | `2_3` | 燈泡 C4 |

### 相關檔案路徑

| 類型 | 路徑 |
|------|------|
| 核心 Library | `libraries/ipcam_light_detection/MultiLightDetection.py` |
| Robot 關鍵字 | `resources/multi_light_keywords.robot` |
| 配置文件 | `config/ipcam_config.yaml` |
| 測試案例 | `tests/ipcam_testing/multi_light_array_test.robot` |
| 視覺化工具 | `scripts/visualize_light_array.py` |
| 使用文檔 | `docs/multi_light_array_detection_guide.md` |

---

## 聯絡與回饋

如有問題或建議，請參考：
- 專案 README: `README.md`
- 開發規範: `.github/copilot-instructions.md`
- 任務清單: `todo.md`

---

**文件版本：** 1.0.0
**最後更新：** 2025-11-06
**適用系統：** Robot Framework 多平台自動化測試系統
