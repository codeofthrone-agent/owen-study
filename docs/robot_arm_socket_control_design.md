# MyCobot 280 Socket 控制系統設計文檔

**建立日期**: 2025-11-05
**版本**: 1.0
**狀態**: 設計階段

---

## 1. 專案目標

建立基於 TCP/IP Socket 的 MyCobot 280 機器手臂控制系統，用於自動化按壓實體面板按鈕。系統採用 **方案 A：直接關鍵字方式**，提供直觀的 Robot Framework 測試關鍵字。

---

## 2. 核心設計原則

### 2.1 直接關鍵字方式（方案 A）

每個按鈕對應一個專屬的 Robot Framework 關鍵字，最直觀易用：

```robot
*** Test Cases ***
測試藍牙按鈕
    連接機器手臂    172.20.10.14    9000
    點擊藍牙按鈕
    點擊 Light3 按鈕
    長按 Retract 按鈕    秒數=10
    斷開機器手臂連接
```

### 2.2 按鈕分類

#### 一般點擊按鈕（20個）
- **藍牙與控制**: bluetooth, aux1, aux2, select
- **燈光控制**: light1, light2, light3, light4, light5, light6, light7, light8
- **電器控制**: tanker_heater, gas, water_pump, water_heater, hvac
- **門鎖**: door_lock

#### 長按按鈕（2個，可擴展）
- **機械控制**: retract（縮回，預設 7 秒）, extend（伸展，預設 7 秒）
- ⚠️ **待調整**: 未來長按功能會擴展到其他按鈕

---

## 3. 系統架構

### 3.1 目錄結構

```
robot-multiplatform-automation/
├── config/robot_arm/
│   ├── button_positions.yaml          # 按鈕位置配置
│   └── connection_config.yaml         # Socket 連接配置
│
├── libraries/robot_arm_control/
│   ├── __init__.py                    # 套件初始化
│   ├── button_config_loader.py        # YAML 配置載入器
│   ├── mycobot_socket_controller.py   # Socket 控制核心
│   └── RobotArmKeywords.py            # Robot Framework 關鍵字庫
│
├── resources/
│   └── robot_arm_keywords.robot       # Robot Framework 資源文件（可選）
│
├── tests/robot_arm/
│   ├── basic_button_test.robot        # 基礎按鈕測試
│   └── long_press_test.robot          # 長按測試
│
└── docs/
    └── robot_arm_socket_control_design.md  # 本文檔
```

### 3.2 技術棧

- **通訊協定**: TCP/IP Socket (基於 pymycobot 的 MyCobot280Socket)
- **配置管理**: YAML (PyYAML)
- **測試框架**: Robot Framework 7.3.1+
- **Python 版本**: 3.12
- **控制庫**: pymycobot

---

## 4. 配置系統設計

### 4.1 按鈕位置配置 (button_positions.yaml)

```yaml
# Robot Arm 連接配置
connection:
  socket:
    host: "172.20.10.14"  # MyCobot 280 的 IP 地址
    port: 9000            # 預設端口

# 全局預設值
defaults:
  speed: 100
  press_duration: 1.0
  lift_duration: 0.1
  count: 1

# 按鈕位置定義
buttons:
  bluetooth:
    name: "Bluetooth 按鈕"
    description: "藍牙控制按鈕"
    down_angles: [16.5, -51, -130, 73.7, 0, 0]
    up_angles: [16.5, -13, -130, 73.7, 0, 0]
    speed: 100
    count: 2
    lift_duration: 0.1
    press_duration: 1.0

  retract:
    name: "Retract 按鈕"
    description: "縮回控制"
    down_angles: [3.1, -68, -67, 22, 0, 0]
    up_angles: [3.1, -35, -67, 22, 0, 0]
    speed: 100
    count: 1
    lift_duration: 0.1
    press_duration: 7.0  # 長按 7 秒
```

### 4.2 連接配置 (connection_config.yaml)

```yaml
# MyCobot 280 Socket 連接配置
socket:
  host: "172.20.10.14"
  port: 9000
  timeout: 10  # 連接超時（秒）

# 備用串口配置（未來擴展）
serial:
  port: "/dev/ttyTHS1"
  baudrate: 1000000

# 運動參數
motion:
  default_speed: 100
  home_position: [0, 0, 0, 0, 0, 0]
  safe_position: [0, -90, -90, 0, 0, 0]
```

---

## 5. 核心模組設計

### 5.1 button_config_loader.py - 配置載入器

**功能**:
- 從 YAML 文件載入按鈕配置
- 驗證配置完整性
- 提供配置查詢接口

**主要方法**:
```python
class ButtonConfigLoader:
    def __init__(self, config_path: str)
    def load_config(self) -> dict
    def get_button_config(self, button_id: str) -> dict
    def get_connection_config(self) -> dict
    def list_all_buttons(self) -> list
    def validate_config(self) -> bool
```

### 5.2 mycobot_socket_controller.py - Socket 控制核心

**功能**:
- TCP/IP Socket 連接管理
- 發送角度指令
- 讀取當前狀態
- 等待移動完成

**主要方法**:
```python
class MyCobotSocketController:
    def __init__(self, host: str, port: int)
    def connect(self) -> bool
    def disconnect(self)
    def is_connected(self) -> bool

    # 運動控制
    def send_angles(self, angles: list, speed: int) -> bool
    def get_angles(self) -> list
    def is_moving(self) -> bool
    def wait_for_movement(self, timeout: float) -> bool

    # 輔助功能
    def go_to_home(self) -> bool
    def power_on(self) -> bool
    def power_off(self) -> bool
```

**內部使用 pymycobot**:
```python
from pymycobot import MyCobot280Socket

class MyCobotSocketController:
    def __init__(self, host: str, port: int):
        self.mc = MyCobot280Socket(host, port)
```

### 5.3 RobotArmKeywords.py - Robot Framework 關鍵字庫

**功能**:
- 提供 Robot Framework 關鍵字
- 22 個點擊按鈕關鍵字
- 2 個長按按鈕關鍵字（可擴展）
- 連接管理關鍵字

**關鍵字列表**:

#### 連接管理
```python
def 連接機器手臂(self, host: str, port: int = 9000)
def 斷開機器手臂連接(self)
def 回到初始位置(self)
```

#### 點擊按鈕（20個）
```python
def 點擊藍牙按鈕(self)
def 點擊AUX1按鈕(self)
def 點擊AUX2按鈕(self)
def 點擊Light1按鈕(self)
def 點擊Light2按鈕(self)
def 點擊Light3按鈕(self)
def 點擊Light4按鈕(self)
def 點擊Light5按鈕(self)
def 點擊Light6按鈕(self)
def 點擊Light7按鈕(self)
def 點擊Light8按鈕(self)
def 點擊DoorLock按鈕(self)
def 點擊Select按鈕(self)
def 點擊TankerHeater按鈕(self)
def 點擊Gas按鈕(self)
def 點擊WaterPump按鈕(self)
def 點擊WaterHeater按鈕(self)
def 點擊HVAC按鈕(self)
```

#### 長按按鈕（2個，可擴展）
```python
def 長按Retract按鈕(self, 秒數: int = 7)
def 長按Extend按鈕(self, 秒數: int = 7)
```

**內部實現邏輯**:
```python
def _press_button(self, button_id: str, custom_duration: float = None):
    """通用按壓邏輯"""
    config = self.config_loader.get_button_config(button_id)

    # 移動到按下位置
    self.controller.send_angles(config['down_angles'], config['speed'])
    self.controller.wait_for_movement()

    # 保持按壓
    duration = custom_duration or config['press_duration']
    time.sleep(duration)

    # 移動到抬起位置
    self.controller.send_angles(config['up_angles'], config['speed'])
    self.controller.wait_for_movement()
    time.sleep(config['lift_duration'])
```

---

## 6. 按鈕映射表

| 按鈕 ID | 中文名稱 | 關鍵字 | 類型 | 預設按壓時間 |
|---------|---------|--------|------|-------------|
| bluetooth | Bluetooth 按鈕 | 點擊藍牙按鈕 | 點擊 | 1.0 秒 |
| aux1 | AUX1 按鈕 | 點擊AUX1按鈕 | 點擊 | 1.0 秒 |
| aux2 | AUX2 按鈕 | 點擊AUX2按鈕 | 點擊 | 1.0 秒 |
| light1 | Light1 按鈕 | 點擊Light1按鈕 | 點擊 | 1.0 秒 |
| light2 | Light2 按鈕 | 點擊Light2按鈕 | 點擊 | 1.0 秒 |
| light3 | Light3 按鈕 | 點擊Light3按鈕 | 點擊 | 1.0 秒 |
| light4 | Light4 按鈕 | 點擊Light4按鈕 | 點擊 | 1.0 秒 |
| light5 | Light5 按鈕 | 點擊Light5按鈕 | 點擊 | 1.0 秒 |
| light6 | Light6 按鈕 | 點擊Light6按鈕 | 點擊 | 1.0 秒 |
| light7 | Light7 按鈕 | 點擊Light7按鈕 | 點擊 | 1.0 秒 |
| light8 | Light8 按鈕 | 點擊Light8按鈕 | 點擊 | 1.0 秒 |
| door_lock | Door Lock 按鈕 | 點擊DoorLock按鈕 | 點擊 | 1.0 秒 |
| select | Select 按鈕 | 點擊Select按鈕 | 點擊 | 1.0 秒 |
| tanker_heater | Tanker Heater 按鈕 | 點擊TankerHeater按鈕 | 點擊 | 1.0 秒 |
| gas | Gas 按鈕 | 點擊Gas按鈕 | 點擊 | 1.0 秒 |
| water_pump | Water Pump 按鈕 | 點擊WaterPump按鈕 | 點擊 | 1.0 秒 |
| water_heater | Water Heater 按鈕 | 點擊WaterHeater按鈕 | 點擊 | 1.0 秒 |
| hvac | HVAC 按鈕 | 點擊HVAC按鈕 | 點擊 | 1.0 秒 |
| retract | Retract 按鈕 | 長按Retract按鈕 | 長按 | 7.0 秒 |
| extend | Extend 按鈕 | 長按Extend按鈕 | 長按 | 7.0 秒 |

⚠️ **注意**: 長按功能未來會擴展到其他按鈕，目前僅 retract 和 extend 配置為長按。

---

## 7. 使用範例

### 7.1 基礎測試案例

```robot
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords

*** Variables ***
${ROBOT_IP}    172.20.10.14
${ROBOT_PORT}    9000

*** Test Cases ***
測試藍牙按鈕點擊
    [Documentation]    測試藍牙按鈕的點擊功能
    [Tags]    bluetooth    smoke

    Given 機器手臂已連接    ${ROBOT_IP}    ${ROBOT_PORT}
    When 點擊藍牙按鈕
    Then 機器手臂應該回到初始位置
    And 斷開機器手臂連接

測試燈光控制序列
    [Documentation]    測試多個燈光按鈕的連續點擊
    [Tags]    lights

    Given 機器手臂已連接    ${ROBOT_IP}    ${ROBOT_PORT}
    When 依序點擊燈光按鈕
    Then 所有燈光按鈕都應該被正確點擊
    And 斷開機器手臂連接

測試長按功能
    [Documentation]    測試長按按鈕功能
    [Tags]    long_press

    Given 機器手臂已連接    ${ROBOT_IP}    ${ROBOT_PORT}
    When 長按 Retract 按鈕    秒數=10
    Then 按鈕應該被按壓 10 秒
    And 斷開機器手臂連接

*** Keywords ***
機器手臂已連接
    [Arguments]    ${ip}    ${port}
    連接機器手臂    ${ip}    ${port}

依序點擊燈光按鈕
    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕
    點擊Light4按鈕
    點擊Light5按鈕
    點擊Light6按鈕
    點擊Light7按鈕
    點擊Light8按鈕

所有燈光按鈕都應該被正確點擊
    Log    所有燈光按鈕已成功點擊

機器手臂應該回到初始位置
    回到初始位置

按鈕應該被按壓 10 秒
    Log    按鈕已被按壓 10 秒
```

### 7.2 完整測試流程

```robot
*** Settings ***
Library    libraries.robot_arm_control.RobotArmKeywords
Suite Setup    連接機器手臂    172.20.10.14    9000
Suite Teardown    斷開機器手臂連接

*** Test Cases ***
完整面板測試
    [Documentation]    測試所有面板按鈕功能

    # 測試藍牙控制
    點擊藍牙按鈕
    點擊AUX1按鈕
    點擊AUX2按鈕

    # 測試燈光控制
    點擊Light1按鈕
    點擊Light2按鈕
    點擊Light3按鈕

    # 測試門鎖
    點擊DoorLock按鈕

    # 測試長按功能
    長按Retract按鈕
    長按Extend按鈕    秒數=5
```

---

## 8. 實施計劃

### 階段 1: 配置系統（已完成）
- ✅ 創建 `button_positions.yaml`
- ⏳ 創建 `connection_config.yaml`

### 階段 2: 核心控制器
1. 實作 `button_config_loader.py`
2. 實作 `mycobot_socket_controller.py`
3. 單元測試核心功能

### 階段 3: Robot Framework 整合
1. 實作 `RobotArmKeywords.py`
2. 實作 22 個點擊關鍵字
3. 實作 2 個長按關鍵字

### 階段 4: 測試與文檔
1. 創建測試案例 `basic_button_test.robot`
2. 創建長按測試 `long_press_test.robot`
3. 更新 `keywords_readme.md`
4. 撰寫使用指南

---

## 9. 依賴套件

### 必要套件
```bash
pipenv install pymycobot pyyaml
```

### 套件說明
- **pymycobot**: MyCobot 280 官方 Python 控制庫
- **pyyaml**: YAML 配置文件解析
- **robot-framework**: 已安裝 (7.3.1+)

---

## 10. 待辦事項與未來擴展

### 當前待辦
- [ ] 創建 `connection_config.yaml`
- [ ] 實作配置載入器
- [ ] 實作 Socket 控制器
- [ ] 實作 Robot Framework 關鍵字庫
- [ ] 創建測試範例
- [ ] 更新關鍵字文檔

### 未來擴展
- [ ] **長按功能擴展**: 將長按功能擴展到更多按鈕（目前只有 retract 和 extend）
- [ ] 支援自定義按壓次數（重複點擊）
- [ ] 支援按壓力度調整
- [ ] 增加錯誤恢復機制
- [ ] 增加運動軌跡記錄
- [ ] 支援多機器手臂並行控制
- [ ] 整合視覺定位系統
- [ ] 增加碰撞檢測功能

---

## 11. 注意事項

### 安全須知
1. 機器手臂運動範圍內不應有障礙物
2. 首次使用前需要校準座標
3. 建議先用低速測試確認位置正確
4. 設置急停機制

### 配置管理
1. 按鈕座標需要精確測量
2. 修改配置後需要驗證測試
3. 配置文件應該版本控制
4. 使用 `.env` 管理敏感配置（IP 地址等）

### 效能考量
1. Socket 連接超時設置合理值
2. 移動速度根據實際情況調整
3. 等待移動完成的超時時間適當設置
4. 避免頻繁連接/斷開連接

---

## 12. 參考資料

- [MyCobot 280 官方文檔](https://docs.elephantrobotics.com/docs/mycobot_280_jn_en/)
- [pymycobot TCP/IP 控制指南](https://docs.elephantrobotics.com/docs/mycobot_280_jn_en/3-FunctionsAndApplications/6.developmentGuide/python/7_TCPIP.html)
- [Robot Framework 用戶指南](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- 專案配置規範: `CLAUDE.md`
- 專案規格書: `spec.md`

---

**文檔結束**
