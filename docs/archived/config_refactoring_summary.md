# 配置系統重構總結

**版本**: v4.1.0
**日期**: 2025-11-18
**狀態**: Phase 1-2 已完成，Phase 3-5 進行中

---

## 📋 問題分析

### 原始問題

1. **影像源配置不正確**
   - `environment_config.py` 只配置單一 RTSP URL
   - 實際上 taipei_lab 有 3 個 IP Camera (level1, level2, motor)
   - 應該從 `ipcam_config.yaml` 讀取多個 camera 配置

2. **按鈕配置來源錯誤**
   - 新建的 `taipei_lab_buttons.yaml` 是空配置
   - 實際按鈕資訊在 `button_positions.yaml` 中
   - 需要從 `button_positions.yaml` 遷移實際數據

3. **燈光檢測配置分散**
   - 實體燈光資訊在 `ipcam_config.yaml` 的 `multi_light_arrays` 中
   - 應該整合到環境配置系統

4. **環境定義不一致**
   - `ipcam_config.yaml`: laboratory vs rv_vehicle
   - `environment_config.py`: taipei_lab, taoyuan_lab, rv_car
   - 命名不一致，需要統一映射

---

## ✅ Phase 4: 物理環境燈光配置整合 (已完成)

### 完成時間
2025-11-18 17:30-18:00

### 成果

1. **taipei_lab 燈光陣列整合**:
   - ✅ 遷移 12 個燈泡配置 (3x4 網格)
   - ✅ 明確指定使用 level2 Camera (192.168.165.127)
   - ✅ 使用相對座標 ROI (0.0-1.0)，方便不同解析度
   - ✅ 4 級亮度分級 (off/dim/medium/bright)

2. **rv_car 車載燈光整合**:
   - ✅ 新增 4 個車載燈光配置
   - ✅ headlight_left, headlight_right, taillight, interior_light
   - ✅ 使用 Socket 影像源 (RV Car 無固定 IP Camera)
   - ✅ 使用絕對座標 ROI

3. **設計特點**:
   - ✅ 明確區分「控制面板按鈕 LED」和「物理環境燈光」
   - ✅ 每個燈光配置包含 environment、camera_id、image_source
   - ✅ taipei_lab 使用 RTSP (level2)，rv_car 使用 Socket
   - ✅ 支援未來擴展 (可添加更多環境燈光)

---

## ✅ Phase 3: 按鈕數據遷移 (已完成)

### 完成時間
2025-11-18 16:00-17:30

### 成果

1. **建立按鈕分類表** (`docs/button_classification_table.md`):
   - 分析 36 個按鈕與觀測點
   - taipei_lab: 13 個按鈕 (8 個 panel_light + 5 個 control)
   - rv_car: 7 個按鈕 + 16 個觀測點
   - taoyuan_lab: 0 個按鈕

2. **完成 taipei_lab_buttons.yaml 遷移**:
   - ✅ 遷移 13 個按鈕配置
   - ✅ 保留 ArUco 參考數據 (light1, light2)
   - ✅ 統一觀測角度 `[1.75, 9.93, -134.73, 34.45, 2.19, -45.08]`
   - ✅ 特殊按壓參數已標註 (count=2, press_duration=0.5/7.0, lift_duration=0.5)

3. **完成 rv_car_buttons.yaml 遷移**:
   - ✅ 遷移 7 個 RV 控制按鈕
   - ✅ 遷移 12 個觀測點 (有 ROI)
   - ✅ 4 個觀測點設定為 vision: null (僅角度，無 ROI)
   - ✅ 特殊長按 (7 秒) 與多次按壓 (4 次) 已標註

4. **YAML 格式驗證**:
   - ✅ taipei_lab_buttons.yaml - 13 個按鈕，格式正確
   - ✅ rv_car_buttons.yaml - 7 個按鈕 + 12 個觀測點，格式正確

---

## ✅ Phase 1-2: 環境命名統一與多 Camera 支援（已完成）

### 完成時間
2025-11-18 14:00-15:30

### 主要變更

#### 1. 環境名稱映射
```python
ENVIRONMENT_MAPPING = {
    "taipei_lab": {
        "ipcam_env": "laboratory",
        "display_name": "台北實驗室",
        "location": "Taipei Laboratory"
    },
    "taoyuan_lab": {
        "ipcam_env": None,  # 無 IP Camera
        "display_name": "桃園實驗室",
        "location": "Taoyuan Laboratory"
    },
    "rv_car": {
        "ipcam_env": "rv_vehicle",
        "display_name": "RV Car 測試環境",
        "location": "RV Vehicle"
    }
}
```

#### 2. 多 Camera 支援

**taipei_lab 配置**:
```python
"cameras": [
    {
        "id": "level1",
        "ip": "192.168.165.184",
        "rtsp_url": "rtsp://192.168.165.184:554/live0",
        "description": "Level 1 監控攝影機",
        "purpose": "panel_detection"
    },
    {
        "id": "level2",
        "ip": "192.168.165.127",
        "rtsp_url": "rtsp://192.168.165.127:554/live0",
        "description": "Level 2 監控攝影機",
        "purpose": "light_array_detection"
    },
    {
        "id": "motor",
        "ip": "10.42.0.39",
        "rtsp_url": "rtsp://10.42.0.39:554/live0",
        "description": "馬達區域監控攝影機",
        "purpose": "motor_monitoring"
    }
],
"default_camera": "level1"
```

#### 3. 新增 API 方法

| 方法 | 功能 | 新增版本 |
|------|------|---------|
| `get_cameras(env_name)` | 取得所有 Camera 列表 | v4.1.0 |
| `get_camera(env_name, camera_id)` | 取得特定 Camera | v4.1.0 |
| `get_default_camera(env_name)` | 取得預設 Camera | v4.1.0 |
| `get_image_source_config(env_name, camera_id=None)` | 支援指定 Camera 的影像源配置 | v4.1.0 更新 |

#### 4. 混合影像源模式

taipei_lab 支援混合模式：
- **RTSP Camera**: 用於固定視角監控 (level1, level2, motor)
- **Socket 機器手臂**: 用於動態視角按鈕檢測

```python
"image_source": "mixed",
"robot_arm_image_source": "socket"
```

### 測試結果

```bash
$ python config/robot_arm/environment_config.py

=== 測試 EnvironmentConfig v4.1.0 ===

taipei_lab:
  Cameras: 3 個
    - level1: Level 1 監控攝影機
    - level2: Level 2 監控攝影機
    - motor: 馬達區域監控攝影機
  預設 Camera: level1
  預設影像源: socket (機器手臂)

多 Camera 存取測試:
  ✅ get_cameras() 正常
  ✅ get_camera(camera_id) 正常
  ✅ get_default_camera() 正常
  ✅ get_image_source_config(camera_id) 正常
```

### 影響範圍

**修改檔案**:
- `config/robot_arm/environment_config.py` (v4.0.0 → v4.1.0)

**相容性**:
- ✅ 向下相容：原有 API 仍可使用
- ✅ 新增功能：新 API 不影響現有程式碼
- ⚠️ 需更新：RobotArmKeywords 需更新以支援多 Camera

---

## 🔄 Phase 3: button_positions.yaml 數據遷移（進行中）

### 目標
將 `button_positions.yaml` 中的實際按鈕數據遷移到環境專屬 YAML 檔案。

### 數據來源分析

#### button_positions.yaml 結構
```yaml
buttons:
  light1:
    name: "Light1 按鈕"
    down_angles: [3.5, -60, -82, 25, 0, 0]
    up_angles: [3.5, -35, -82, 25, 0, 0]
    vision:
      observe_angles: [1.93, 8.34, -135.0, 33.57, 2.63, -44.56]
      roi: {x: 197, y: 205, width: 71, height: 67}
      aruco_marker_id: 0
  # ... 更多按鈕
```

#### 遷移策略

**識別環境**:
- 根據按鈕名稱判斷屬於哪個環境
- RV Car 專用按鈕：hvac, water_pump, tanker_heater, gas, extend, retract 等
- 實驗室按鈕：light1-8, bluetooth, door_lock, select, aux1-2 等

**遷移步驟**:
1. 分析所有按鈕的用途
2. 分類到對應環境
3. 轉換為新格式
4. 更新到對應 YAML 檔案

### 新格式範例

```yaml
# taipei_lab_buttons.yaml
environment: "taipei_lab"
panel_types: ["3510a", "3611a", "3611c"]

panels:
  "3611a":
    buttons:
      light1:
        name: "Light1 按鈕"
        type: "panel_light"
        down_angles: [3.5, -60, -82, 25, 0, 0]
        up_angles: [3.5, -35, -82, 25, 0, 0]
        roi: {x: 197, y: 205, width: 71, height: 67}
        observe_angles: [1.93, 8.34, -135.0, 33.57, 2.63, -44.56]
        aruco_marker_id: 0
        expected_colors: ["blue", "white"]
        press_duration: 0.5
        lift_duration: 0.1
```

### 待辦事項

- [ ] 分析所有按鈕屬於哪個環境
- [ ] 建立按鈕分類表
- [ ] 轉換數據格式
- [ ] 更新 taipei_lab_buttons.yaml
- [ ] 更新 rv_car_buttons.yaml
- [ ] 驗證遷移完整性

---

## 🔄 Phase 4: ipcam_config.yaml 整合（待執行）

### 目標
將 `ipcam_config.yaml` 中的燈光陣列配置整合到環境配置系統。

### 數據來源

#### ipcam_config.yaml - multi_light_arrays
```yaml
multi_light_arrays:
  default_array:
    name: "實驗室燈泡陣列"
    environment: "laboratory"
    camera: "level1"
    layout:
      rows: 3
      cols: 4
      total_lights: 12
    manual_roi:
      - [0, 0, 0.00, 0.00, 0.25, 0.33]  # 燈泡 A1
      - [0, 1, 0.25, 0.00, 0.50, 0.33]  # 燈泡 A2
      # ...
    light_configs:
      "0_0":
        name: "燈泡 A1"
        bright_threshold: 150
        dark_threshold: 50
```

### 整合方案

#### 新增到 taipei_lab_buttons.yaml
```yaml
physical_lights:
  light_array_level1:
    name: "Level 1 燈泡陣列"
    camera_id: "level1"
    type: "light_array"
    layout:
      rows: 3
      cols: 4
      total_lights: 12
    lights:
      "0_0":
        name: "燈泡 A1"
        roi_relative: [0.00, 0.00, 0.25, 0.33]
        brightness_levels: [0, 50, 100]
        bright_threshold: 150
        dark_threshold: 50
      # ... 其他燈泡
```

### 待辦事項

- [ ] 分析 multi_light_arrays 配置
- [ ] 設計整合格式
- [ ] 更新 taipei_lab_buttons.yaml
- [ ] 更新 EnvironmentConfig 支援燈光陣列查詢
- [ ] 建立相容層（保持 ipcam_config.yaml 可用）

---

## 🔄 Phase 5: ConfigLoader 統一載入器（待執行）

### 目標
建立統一配置載入器，整合多個配置來源。

### 設計草案

```python
# config/robot_arm/config_loader.py

class ConfigLoader:
    """統一配置載入器

    整合以下配置來源：
    - environment_config.py (環境定義)
    - {env}_buttons.yaml (按鈕與燈光配置)
    - ipcam_config.yaml (Camera 詳細配置)
    """

    def __init__(self, env_name: str):
        self.env_name = env_name
        self.env_config = EnvironmentConfig.get_environment(env_name)
        self.button_config = self._load_button_config()
        self.ipcam_config = self._load_ipcam_config()

    def get_all_cameras(self) -> List[Dict]:
        """取得所有 Camera 配置（含 ipcam_config 詳細資訊）"""
        pass

    def get_camera_with_lights(self, camera_id: str) -> Dict:
        """取得 Camera 及其關聯的燈光陣列"""
        pass

    def get_panel_buttons(self, panel_type: str) -> Dict:
        """取得面板所有按鈕配置"""
        pass

    def get_physical_lights(self) -> Dict:
        """取得所有實體燈光配置"""
        pass
```

### 使用範例

```python
# 在 RobotArmKeywords 中使用
from config.robot_arm.config_loader import ConfigLoader

loader = ConfigLoader("taipei_lab")

# 取得所有 Camera
cameras = loader.get_all_cameras()

# 取得 level2 Camera 及其燈光陣列
camera_info = loader.get_camera_with_lights("level2")

# 取得 3611a 面板所有按鈕
buttons = loader.get_panel_buttons("3611a")
```

### 待辦事項

- [ ] 設計 ConfigLoader 類別架構
- [ ] 實作 YAML 載入邏輯
- [ ] 實作 ipcam_config 整合
- [ ] 實作快取機制
- [ ] 撰寫單元測試
- [ ] 更新 RobotArmKeywords 使用 ConfigLoader

---

## 📊 RobotArmKeywords 更新計畫

### 新增關鍵字

```robotframework
*** Keywords ***
Given 測試環境設定為 "${environment}" 使用攝影機 "${camera_id}"
    [Documentation]    設定環境並選擇特定 Camera
    [Arguments]    ${environment}    ${camera_id}=default
    # 使用 ConfigLoader 載入配置
    # 設定指定的 Camera

Given 切換到攝影機 "${camera_id}"
    [Documentation]    在當前環境中切換 Camera
    [Arguments]    ${camera_id}
    # 切換 ImageSourceManager 到指定 Camera

When 用戶使用 "${camera_id}" 檢測燈光陣列
    [Documentation]    使用特定 Camera 檢測燈光陣列
    [Arguments]    ${camera_id}
    # 使用指定 Camera 進行燈光陣列檢測
```

### 更新現有關鍵字

```python
@keyword('Given 測試環境設定為 "${environment}"')
def given_test_environment_is(self, environment: str, camera_id: str = None):
    """設定測試環境（更新支援 camera_id）

    Args:
        environment: taipei_lab / taoyuan_lab / rv_car
        camera_id: Camera 識別碼（可選，預設使用 default camera）
    """
    # 使用新的 ConfigLoader
    self.config_loader = ConfigLoader(environment)

    # 設定影像源
    if camera_id:
        img_config = EnvironmentConfig.get_image_source_config(environment, camera_id)
    else:
        img_config = EnvironmentConfig.get_image_source_config(environment)

    self.image_source_manager.set_image_source(
        img_config["type"], img_config
    )
```

---

## 🎯 待補充項目

### 1. RV Car Camera 配置

根據使用者提到 "rv_car 也有多個 RTSP"，需要補充：

```python
"rv_car": {
    "cameras": [
        {
            "id": "front",
            "rtsp_url": "rtsp://?.?.?.?:554/stream1",
            "description": "前方攝影機",
            "purpose": "front_view"
        },
        {
            "id": "rear",
            "rtsp_url": "rtsp://?.?.?.?:554/stream1",
            "description": "後方攝影機",
            "purpose": "rear_view"
        },
        # 待補充更多...
    ],
    "default_camera": "front"
}
```

**待確認**:
- [ ] RV Car 有幾個 Camera？
- [ ] 各 Camera 的 IP 地址？
- [ ] 各 Camera 的用途？

### 2. 按鈕分類表

需要建立完整的按鈕分類表，識別每個按鈕屬於哪個環境和面板。

**待執行**:
- [ ] 分析 button_positions.yaml 所有按鈕
- [ ] 建立分類對照表
- [ ] 確認遷移策略

---

## 📝 測試計畫

### 單元測試

```python
# tests/test_environment_config_v4_1.py

def test_get_cameras():
    """測試取得多 Camera"""
    cameras = EnvironmentConfig.get_cameras("taipei_lab")
    assert len(cameras) == 3
    assert cameras[0]["id"] == "level1"

def test_get_camera_by_id():
    """測試取得特定 Camera"""
    camera = EnvironmentConfig.get_camera("taipei_lab", "level2")
    assert camera["rtsp_url"] == "rtsp://192.168.165.127:554/live0"

def test_get_default_camera():
    """測試取得預設 Camera"""
    camera = EnvironmentConfig.get_default_camera("taipei_lab")
    assert camera["id"] == "level1"

def test_get_image_source_with_camera():
    """測試取得指定 Camera 的影像源配置"""
    config = EnvironmentConfig.get_image_source_config("taipei_lab", "motor")
    assert config["type"] == "rtsp"
    assert config["camera_id"] == "motor"
```

### 整合測試

```robotframework
# tests/robot_arm/test_multi_camera.robot

*** Test Cases ***
測試台北實驗室多 Camera 切換
    Given 測試環境設定為 "taipei_lab"

    # 測試預設 Camera (Socket 機器手臂)
    When 用戶檢測面板按鈕 "light1" 的顏色
    Then 面板按鈕顏色應該為 "blue"

    # 切換到 level1 Camera
    Given 切換到攝影機 "level1"
    When 用戶使用 "level1" 檢測燈光陣列
    Then 燈光陣列檢測應該成功

    # 切換到 level2 Camera
    Given 切換到攝影機 "level2"
    When 用戶使用 "level2" 檢測燈光陣列
    Then 燈光陣列檢測應該成功
```

---

## 🚧 已知限制

1. **RV Car Camera 配置待補充**
   - 目前 cameras 為空列表
   - 需要實際 Camera IP 資訊

2. **button_positions.yaml 遷移未完成**
   - 新 YAML 檔案為空或示例數據
   - 需要人工整理分類

3. **ipcam_config.yaml 尚未整合**
   - 燈光陣列配置仍在 ipcam_config.yaml
   - 需要設計整合方案

4. **RobotArmKeywords 尚未更新**
   - 尚未支援多 Camera 選擇
   - 需要新增 Camera 切換關鍵字

---

## 📅 時程規劃

| Phase | 預估時間 | 狀態 |
|-------|---------|------|
| Phase 1-2 | 1.5 小時 | ✅ 已完成 |
| Phase 3 | 2 小時 | 🔄 待執行 |
| Phase 4 | 1.5 小時 | ⏸️ 待執行 |
| Phase 5 | 2 小時 | ⏸️ 待執行 |
| 測試驗證 | 1 小時 | ⏸️ 待執行 |
| 文檔更新 | 0.5 小時 | ⏸️ 待執行 |

**總計**: 約 8.5 小時（已完成 1.5 小時）

---

## 🎯 下一步行動

### 立即執行（高優先級）
1. ✅ 建立此總結文檔
2. ⏭️ 補充 RV Car Camera 配置
3. ⏭️ 分析 button_positions.yaml 按鈕分類

### 可延後執行（中優先級）
4. 遷移 button_positions.yaml 數據
5. 整合 ipcam_config.yaml 燈光陣列
6. 建立 ConfigLoader 類別

### 最後執行（低優先級）
7. 更新 RobotArmKeywords 支援多 Camera
8. 撰寫完整測試
9. 更新文檔

---

**最後更新**: 2025-11-18 15:45
**下次檢查點**: Phase 3 完成後
