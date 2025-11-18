# 機器手臂按鈕設置與場景切換指南

**版本**: 1.0.0
**日期**: 2025-11-06

本文檔詳細說明如何新增按鈕配置以及如何在不同測試場景之間切換。

---

## 📋 目錄

- [新增按鈕完整流程](#新增按鈕完整流程)
- [場景配置管理](#場景配置管理)
- [多場景切換方案](#多場景切換方案)
- [實戰範例](#實戰範例)
- [常見問題](#常見問題)

---

## 新增按鈕完整流程

### 步驟 1: 準備工作

#### 1.1 確認硬體連接

```bash
# 檢查網路連接
ping <mycobot_ip>

# 檢查 Socket Server 運行狀態
ssh user@<mycobot_ip>
ps aux | grep robot_arm_server.py

# 如果未運行，啟動 Server
python3 ~/scripts/robot_arm_server.py
```

#### 1.2 準備示教工具

**方法 A: 使用 myBlockly（圖形化介面）**

1. 開啟瀏覽器訪問: `http://<mycobot_ip>:5000`
2. 連接機器手臂
3. 使用「拖動示教」模式手動移動機器手臂

**方法 B: 使用 Python 腳本**

創建示教腳本 `scripts/teach_button_position.py`:

```python
#!/usr/bin/env python3
"""
機器手臂按鈕位置示教工具
用於記錄新按鈕的上下位置角度
"""

import sys
import time
from pathlib import Path

# 將專案根目錄加入 sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader


def main():
    print("=" * 60)
    print("機器手臂按鈕位置示教工具")
    print("=" * 60)
    print()

    # 讀取連接配置
    config_loader = ButtonConfigLoader()
    socket_config = config_loader.get_socket_config()
    host = socket_config['host']
    port = socket_config['port']

    print(f"連接到機器手臂: {host}:{port}")
    print()

    # 連接機器手臂
    controller = MyCobotSocketController(host, port)

    try:
        controller.connect()

        # 確保電源開啟
        if not controller.is_power_on():
            print("正在開啟伺服馬達電源...")
            controller.power_on()

        print("✅ 連接成功！")
        print()
        print("請使用以下方式移動機器手臂:")
        print("1. 使用 myBlockly 拖動示教")
        print("2. 或手動解鎖馬達後移動")
        print()

        # 記錄按鈕位置
        button_name = input("請輸入按鈕名稱 (例如: my_new_button): ").strip()
        if not button_name:
            print("❌ 按鈕名稱不能為空")
            return

        print()
        print(f"正在記錄「{button_name}」的位置...")
        print()

        # 記錄抬起位置
        input("請將機器手臂移動到按鈕【上方位置】(抬起位置)，然後按 Enter 鍵...")
        up_angles = controller.get_angles()
        print(f"✅ 抬起位置已記錄: {[round(a, 1) for a in up_angles]}")
        print()

        # 記錄按下位置
        input("請將機器手臂移動到【按下按鈕位置】，然後按 Enter 鍵...")
        down_angles = controller.get_angles()
        print(f"✅ 按下位置已記錄: {[round(a, 1) for a in down_angles]}")
        print()

        # 生成配置
        print("=" * 60)
        print("📝 請將以下配置添加到 config/robot_arm/button_positions.yaml:")
        print("=" * 60)
        print()
        print(f"  {button_name}:")
        print(f"    name: \"{button_name.replace('_', ' ').title()} 按鈕\"")
        print(f"    description: \"請填寫按鈕功能說明\"")
        print(f"    down_angles: {[round(a, 1) for a in down_angles]}")
        print(f"    up_angles: {[round(a, 1) for a in up_angles]}")
        print(f"    speed: 100")
        print(f"    count: 1")
        print(f"    lift_duration: 0.1")
        print(f"    press_duration: 1.0")
        print()
        print("=" * 60)

        # 測試按壓
        test = input("是否測試按壓動作？(y/n): ").strip().lower()
        if test == 'y':
            print()
            print("⚠️  注意: 請確認機器手臂周圍無障礙物！")
            confirm = input("確認開始測試？(y/n): ").strip().lower()
            if confirm == 'y':
                print()
                print("測試按壓動作...")

                # 移動到抬起位置
                print("1. 移動到抬起位置...")
                controller.send_angles(up_angles, 100)
                controller.wait_for_movement()
                time.sleep(0.5)

                # 移動到按下位置
                print("2. 移動到按下位置...")
                controller.send_angles(down_angles, 100)
                controller.wait_for_movement()
                time.sleep(1.0)  # 保持按壓 1 秒

                # 回到抬起位置
                print("3. 回到抬起位置...")
                controller.send_angles(up_angles, 100)
                controller.wait_for_movement()
                time.sleep(0.1)

                print("✅ 測試完成！")

        # 回到初始位置
        print()
        go_home = input("是否回到初始位置？(y/n): ").strip().lower()
        if go_home == 'y':
            print("回到初始位置...")
            controller.go_to_home()

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

    finally:
        controller.disconnect()
        print()
        print("✅ 已斷開連接")


if __name__ == "__main__":
    main()
```

使用方式:

```bash
# 給予執行權限
chmod +x scripts/teach_button_position.py

# 執行示教工具
python scripts/teach_button_position.py
```

---

### 步驟 2: 記錄按鈕位置

#### 2.1 手動移動機器手臂

1. **移動到抬起位置**（按鈕上方，未接觸按鈕）
   - 使用 myBlockly 拖動示教
   - 或解鎖馬達手動移動

2. **記錄抬起位置角度**
   ```python
   up_angles = controller.get_angles()
   print(f"抬起位置: {up_angles}")
   ```

3. **移動到按下位置**（按壓按鈕狀態）
   - 確認按鈕被完全按下
   - 不要過度下壓避免損壞

4. **記錄按下位置角度**
   ```python
   down_angles = controller.get_angles()
   print(f"按下位置: {down_angles}")
   ```

#### 2.2 角度格式說明

MyCobot 280 有 6 個關節，角度格式為:

```python
[J1, J2, J3, J4, J5, J6]

# 範例
up_angles = [16.5, -13, -130, 73.7, 0, 0]
down_angles = [16.5, -51, -130, 73.7, 0, 0]
```

**各關節功能**:
- **J1**: 基座旋轉（左右轉）
- **J2**: 大臂俯仰（上下移動，通常控制按壓深度）
- **J3**: 小臂俯仰
- **J4**: 腕部旋轉
- **J5**: 腕部俯仰
- **J6**: 末端旋轉

**關鍵提示**:
- 通常只需調整 J2 角度來控制按壓深度
- J1 控制左右位置
- J3, J4, J5, J6 維持姿態

---

### 步驟 3: 更新配置文件

#### 3.1 編輯 button_positions.yaml

打開 `config/robot_arm/button_positions.yaml`，在 `buttons:` 區塊中新增:

```yaml
buttons:
  # ... 現有按鈕配置 ...

  # 新增的按鈕
  my_new_button:
    name: "新按鈕"                    # 顯示名稱（中文）
    description: "新按鈕的功能說明"    # 功能描述
    down_angles: [16.5, -51, -130, 73.7, 0, 0]  # 從步驟 2 獲得
    up_angles: [16.5, -13, -130, 73.7, 0, 0]    # 從步驟 2 獲得
    speed: 100                        # 移動速度 (1-100)
    count: 1                          # 按壓次數
    lift_duration: 0.1                # 抬起後等待時間（秒）
    press_duration: 1.0               # 按壓保持時間（秒）
```

#### 3.2 配置參數調整建議

根據不同按鈕類型調整參數:

**一般按鈕** (單次點擊):
```yaml
  light_switch:
    name: "電燈開關"
    description: "控制房間電燈"
    down_angles: [10, -50, -120, 70, 0, 0]
    up_angles: [10, -20, -120, 70, 0, 0]
    speed: 100
    count: 1              # 按 1 次
    lift_duration: 0.1
    press_duration: 1.0   # 保持 1 秒
```

**需要多次點擊的按鈕**:
```yaml
  power_button:
    name: "電源按鈕"
    description: "設備電源開關（需要按 3 次）"
    down_angles: [5, -55, -110, 65, 0, 0]
    up_angles: [5, -25, -110, 65, 0, 0]
    speed: 100
    count: 3              # 按 3 次
    lift_duration: 0.5    # 每次抬起等待 0.5 秒
    press_duration: 1.0
```

**長按按鈕**:
```yaml
  emergency_button:
    name: "緊急按鈕"
    description: "緊急停止按鈕（需要長按）"
    down_angles: [0, -60, -100, 60, 0, 0]
    up_angles: [0, -30, -100, 60, 0, 0]
    speed: 100
    count: 1
    lift_duration: 0.1
    press_duration: 5.0   # 長按 5 秒
```

---

### 步驟 4: 新增 Robot Framework 關鍵字

#### 4.1 編輯 RobotArmKeywords.py

打開 `libraries/robot_arm_control/RobotArmKeywords.py`，新增關鍵字:

**一般點擊按鈕**:

```python
# 在「點擊按鈕關鍵字」區塊新增

@keyword("點擊新按鈕")
def click_my_new_button(self):
    """
    點擊新按鈕

    Examples:
        | 點擊新按鈕 |
    """
    self._press_button('my_new_button')
```

**長按按鈕**:

```python
# 在「長按按鈕關鍵字」區塊新增

@keyword("長按緊急按鈕")
def long_press_emergency_button(self, 秒數: int = 5):
    """
    長按緊急按鈕

    Args:
        秒數: 按壓時間（秒），預設 5 秒

    Examples:
        | 長按緊急按鈕 |           # 使用預設 5 秒
        | 長按緊急按鈕 | 秒數=10 |  # 自定義 10 秒
        | 長按緊急按鈕 | 10 |       # 位置參數 10 秒
    """
    self._press_button('emergency_button', custom_duration=float(秒數))
```

#### 4.2 更新關鍵字統計

在 `RobotArmKeywords.py` 最底部的測試代碼中更新按鈕列表:

```python
# 測試用例
if __name__ == "__main__":
    # ... 略 ...

    print("【點擊按鈕】(21個)")  # 更新數量
    buttons = [
        'bluetooth', 'aux1', 'aux2',
        'light1', 'light2', 'light3', 'light4', 'light5', 'light6', 'light7', 'light8',
        'door_lock', 'select', 'tanker_heater', 'gas', 'water_pump', 'water_heater', 'hvac',
        'my_new_button'  # 新增
    ]
    # ... 略 ...
```

---

### 步驟 5: 測試新按鈕

#### 5.1 語法驗證

```bash
# 檢查語法是否正確
robot --dryrun tests/robot_arm/basic_button_test.robot
```

#### 5.2 創建測試案例

創建 `tests/robot_arm/test_new_button.robot`:

```robot
*** Settings ***
Documentation    測試新增按鈕功能
Library          libraries.robot_arm_control.RobotArmKeywords

Suite Setup      連接機器手臂
Suite Teardown   清理資源

*** Test Cases ***
測試新按鈕
    [Documentation]    測試新增的按鈕是否能正確按壓
    [Tags]    new_button    smoke

    Given 機器手臂已就緒
    When 執行按壓新按鈕
    Then 按壓動作應該成功完成

*** Keywords ***
機器手臂已就緒
    Log    機器手臂已就緒

執行按壓新按鈕
    點擊新按鈕

按壓動作應該成功完成
    Log    ✅ 按壓成功

清理資源
    回到初始位置
    斷開機器手臂連接
```

#### 5.3 執行測試

```bash
# ⚠️ 注意: 執行前確認機器手臂周圍無障礙物！

# 執行測試
robot tests/robot_arm/test_new_button.robot

# 查看詳細日誌
robot --loglevel DEBUG tests/robot_arm/test_new_button.robot
```

#### 5.4 調整優化

根據測試結果調整配置:

**問題 1: 沒有按到按鈕**
- 增加下壓深度（減小 J2 角度）
  ```yaml
  down_angles: [10, -55, -120, 70, 0, 0]  # J2 從 -50 改為 -55
  ```

**問題 2: 按壓太用力**
- 減少下壓深度（增大 J2 角度）
  ```yaml
  down_angles: [10, -45, -120, 70, 0, 0]  # J2 從 -50 改為 -45
  ```

**問題 3: 位置偏移**
- 調整左右位置（調整 J1 角度）
  ```yaml
  down_angles: [12, -50, -120, 70, 0, 0]  # J1 從 10 改為 12
  ```

---

## 場景配置管理

### 場景概念

不同的測試環境（實驗室、生產線、客戶現場）可能有不同的:
- 按鈕佈局
- MyCobot IP 地址
- 按鈕位置座標

需要能夠快速切換配置。

---

### 方案 1: 多配置文件管理（推薦）

#### 目錄結構

```
config/robot_arm/
├── button_positions.yaml              # 當前使用的配置（軟連結）
├── scenes/                            # 場景配置目錄
│   ├── lab_scene.yaml                # 實驗室場景
│   ├── production_scene.yaml         # 生產線場景
│   ├── customer_site_scene.yaml      # 客戶現場場景
│   └── README.md                     # 場景說明文檔
└── switch_scene.sh                   # 場景切換腳本
```

#### 創建場景配置文件

**實驗室場景** (`config/robot_arm/scenes/lab_scene.yaml`):

```yaml
# 實驗室場景配置
# 地點: 研發實驗室
# MyCobot IP: 10.42.0.180
# 測試面板: RV 控制面板 v1.0

connection:
  socket:
    host: "10.42.0.180"  # 實驗室 MyCobot IP
    port: 9000

defaults:
  speed: 100
  press_duration: 1.0
  lift_duration: 0.1
  count: 1

buttons:
  bluetooth:
    name: "Bluetooth 按鈕"
    description: "藍牙控制按鈕"
    down_angles: [16.5, -51, -130, 73.7, 0, 0]
    up_angles: [16.5, -13, -130, 73.7, 0, 0]
    speed: 100
    count: 2

  # ... 實驗室的其他按鈕 ...
```

**生產線場景** (`config/robot_arm/scenes/production_scene.yaml`):

```yaml
# 生產線場景配置
# 地點: 生產測試站
# MyCobot IP: 192.168.1.100
# 測試面板: RV 控制面板 v2.0（位置略有不同）

connection:
  socket:
    host: "192.168.1.100"  # 生產線 MyCobot IP
    port: 9000

defaults:
  speed: 80  # 生產線使用較慢速度確保穩定
  press_duration: 1.5
  lift_duration: 0.2
  count: 1

buttons:
  bluetooth:
    name: "Bluetooth 按鈕"
    description: "藍牙控制按鈕"
    down_angles: [18.0, -53, -128, 72.0, 0, 0]  # 位置略有調整
    up_angles: [18.0, -15, -128, 72.0, 0, 0]
    speed: 80
    count: 2

  # ... 生產線的其他按鈕 ...
```

**客戶現場場景** (`config/robot_arm/scenes/customer_site_scene.yaml`):

```yaml
# 客戶現場場景配置
# 地點: 客戶測試環境
# MyCobot IP: 172.20.10.14
# 測試面板: 客戶提供的實車面板

connection:
  socket:
    host: "172.20.10.14"  # 客戶現場 MyCobot IP
    port: 9000

defaults:
  speed: 60  # 客戶現場使用更保守的速度
  press_duration: 2.0
  lift_duration: 0.3
  count: 1

buttons:
  # 客戶現場可能有不同的按鈕佈局
  main_power:
    name: "主電源"
    description: "車輛主電源開關"
    down_angles: [20.0, -48, -125, 70.0, 0, 0]
    up_angles: [20.0, -18, -125, 70.0, 0, 0]
    speed: 60

  # ... 客戶現場的其他按鈕 ...
```

#### 場景切換腳本

創建 `config/robot_arm/switch_scene.sh`:

```bash
#!/bin/bash
# 場景切換腳本
# 用於切換不同的按鈕位置配置

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCENES_DIR="${SCRIPT_DIR}/scenes"
TARGET_FILE="${SCRIPT_DIR}/button_positions.yaml"

function show_usage() {
    echo "使用方式: $0 <scene_name>"
    echo ""
    echo "可用場景:"
    echo "  lab           - 實驗室場景"
    echo "  production    - 生產線場景"
    echo "  customer      - 客戶現場場景"
    echo ""
    echo "範例:"
    echo "  $0 lab              # 切換到實驗室場景"
    echo "  $0 production       # 切換到生產線場景"
}

function switch_scene() {
    local scene_name=$1
    local scene_file=""

    case "$scene_name" in
        lab)
            scene_file="${SCENES_DIR}/lab_scene.yaml"
            ;;
        production)
            scene_file="${SCENES_DIR}/production_scene.yaml"
            ;;
        customer)
            scene_file="${SCENES_DIR}/customer_site_scene.yaml"
            ;;
        *)
            echo "❌ 錯誤: 未知的場景名稱 '$scene_name'"
            echo ""
            show_usage
            exit 1
            ;;
    esac

    # 檢查場景文件是否存在
    if [ ! -f "$scene_file" ]; then
        echo "❌ 錯誤: 場景文件不存在: $scene_file"
        exit 1
    fi

    # 備份當前配置
    if [ -f "$TARGET_FILE" ] && [ ! -L "$TARGET_FILE" ]; then
        backup_file="${TARGET_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "📦 備份當前配置到: $backup_file"
        cp "$TARGET_FILE" "$backup_file"
    fi

    # 刪除舊的軟連結或文件
    rm -f "$TARGET_FILE"

    # 創建新的軟連結
    ln -s "$scene_file" "$TARGET_FILE"

    echo "✅ 成功切換到場景: $scene_name"
    echo "📄 配置文件: $scene_file"
    echo ""

    # 顯示場景配置資訊
    echo "場景資訊:"
    grep "^# " "$scene_file" | head -5
    echo ""

    # 顯示 IP 地址
    echo "MyCobot IP 地址:"
    grep "host:" "$scene_file" | head -1
}

# 主程式
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

switch_scene "$1"
```

給予執行權限:

```bash
chmod +x config/robot_arm/switch_scene.sh
```

#### 使用場景切換

```bash
# 切換到實驗室場景
./config/robot_arm/switch_scene.sh lab

# 切換到生產線場景
./config/robot_arm/switch_scene.sh production

# 切換到客戶現場場景
./config/robot_arm/switch_scene.sh customer

# 查看當前使用的場景
ls -l config/robot_arm/button_positions.yaml
```

---

### 方案 2: 環境變數控制

#### 設置環境變數

在專案根目錄 `.env` 文件中:

```bash
# Robot Arm 場景配置
ROBOT_ARM_SCENE=lab  # 可選: lab, production, customer
```

#### 修改 ButtonConfigLoader

編輯 `libraries/robot_arm_control/button_config_loader.py`:

```python
import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from loguru import logger
from dotenv import load_dotenv

class ButtonConfigLoader:
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置載入器

        Args:
            config_path: YAML 配置文件路徑。如果為 None，根據環境變數選擇場景
        """
        if config_path is None:
            # 載入 .env 文件
            load_dotenv()

            # 讀取場景設定
            scene = os.getenv('ROBOT_ARM_SCENE', 'lab')

            # 根據場景選擇配置文件
            project_root = Path(__file__).resolve().parent.parent.parent
            scenes_dir = project_root / "config" / "robot_arm" / "scenes"

            scene_files = {
                'lab': scenes_dir / "lab_scene.yaml",
                'production': scenes_dir / "production_scene.yaml",
                'customer': scenes_dir / "customer_site_scene.yaml"
            }

            if scene not in scene_files:
                logger.warning(f"未知場景 '{scene}'，使用預設實驗室場景")
                scene = 'lab'

            config_path = scene_files[scene]
            logger.info(f"使用場景配置: {scene} ({config_path})")

        self.config_path = Path(config_path)
        self.config: Dict = {}
        self._load_config()
```

#### 使用方式

```bash
# 設定環境變數
export ROBOT_ARM_SCENE=production

# 執行測試（會自動使用 production 場景）
robot tests/robot_arm/basic_button_test.robot

# 或在 .env 中設定
echo "ROBOT_ARM_SCENE=customer" >> .env
robot tests/robot_arm/basic_button_test.robot
```

---

### 方案 3: Robot Framework 變數控制

#### 創建場景變數文件

**實驗室場景** (`tests/robot_arm/variables/lab_vars.yaml`):

```yaml
ROBOT_IP: "10.42.0.180"
ROBOT_PORT: 9000
SCENE_NAME: "實驗室"
```

**生產線場景** (`tests/robot_arm/variables/production_vars.yaml`):

```yaml
ROBOT_IP: "192.168.1.100"
ROBOT_PORT: 9000
SCENE_NAME: "生產線"
```

#### 在測試案例中使用

```robot
*** Settings ***
Library          libraries.robot_arm_control.RobotArmKeywords
Variables        tests/robot_arm/variables/lab_vars.yaml  # 選擇場景

*** Test Cases ***
測試藍牙按鈕
    Log    當前場景: ${SCENE_NAME}
    連接機器手臂    ${ROBOT_IP}    ${ROBOT_PORT}
    點擊藍牙按鈕
    斷開機器手臂連接
```

#### 執行時指定場景

```bash
# 使用實驗室場景
robot --variablefile tests/robot_arm/variables/lab_vars.yaml tests/robot_arm/

# 使用生產線場景
robot --variablefile tests/robot_arm/variables/production_vars.yaml tests/robot_arm/

# 使用客戶現場場景
robot --variablefile tests/robot_arm/variables/customer_vars.yaml tests/robot_arm/
```

---

## 實戰範例

### 範例 1: 新增「電源按鈕」並測試

#### 1. 使用示教工具記錄位置

```bash
python scripts/teach_button_position.py
```

輸出:
```
請輸入按鈕名稱: power_button
請將機器手臂移動到按鈕【上方位置】，然後按 Enter 鍵...
✅ 抬起位置已記錄: [8.0, -20.0, -100.0, 65.0, 0.0, 0.0]
請將機器手臂移動到【按下按鈕位置】，然後按 Enter 鍵...
✅ 按下位置已記錄: [8.0, -55.0, -100.0, 65.0, 0.0, 0.0]
```

#### 2. 添加到配置文件

編輯 `config/robot_arm/button_positions.yaml`:

```yaml
buttons:
  # ... 現有按鈕 ...

  power_button:
    name: "電源按鈕"
    description: "設備主電源開關"
    down_angles: [8.0, -55.0, -100.0, 65.0, 0.0, 0.0]
    up_angles: [8.0, -20.0, -100.0, 65.0, 0.0, 0.0]
    speed: 100
    count: 1
    lift_duration: 0.1
    press_duration: 1.5  # 電源按鈕按壓 1.5 秒
```

#### 3. 添加 Robot 關鍵字

編輯 `libraries/robot_arm_control/RobotArmKeywords.py`:

```python
@keyword("點擊電源按鈕")
def click_power_button(self):
    """
    點擊電源按鈕

    Examples:
        | 點擊電源按鈕 |
    """
    self._press_button('power_button')
```

#### 4. 創建測試案例

創建 `tests/robot_arm/test_power_button.robot`:

```robot
*** Settings ***
Documentation    測試電源按鈕功能
Library          libraries.robot_arm_control.RobotArmKeywords

*** Test Cases ***
測試電源開關
    [Documentation]    測試電源按鈕的開啟和關閉
    [Tags]    power

    連接機器手臂

    # 按第一次（開啟）
    點擊電源按鈕
    Sleep    2s    # 等待設備啟動

    # 按第二次（關閉）
    點擊電源按鈕
    Sleep    1s

    回到初始位置
    斷開機器手臂連接
```

#### 5. 執行測試

```bash
robot tests/robot_arm/test_power_button.robot
```

---

### 範例 2: 切換到生產線場景

#### 1. 創建生產線場景配置

```bash
# 複製實驗室配置作為模板
cp config/robot_arm/scenes/lab_scene.yaml config/robot_arm/scenes/production_scene.yaml
```

編輯 `config/robot_arm/scenes/production_scene.yaml`:

```yaml
# 生產線場景配置
connection:
  socket:
    host: "192.168.1.100"  # 修改為生產線 IP
    port: 9000

# 調整按鈕位置（如果有差異）
buttons:
  power_button:
    down_angles: [8.2, -56.0, -102.0, 66.0, 0.0, 0.0]  # 微調
    up_angles: [8.2, -22.0, -102.0, 66.0, 0.0, 0.0]
    # ... 其他參數 ...
```

#### 2. 切換場景

```bash
# 切換到生產線場景
./config/robot_arm/switch_scene.sh production

# 確認切換成功
ls -l config/robot_arm/button_positions.yaml
```

#### 3. 執行測試

```bash
# 現在會使用生產線場景的配置
robot tests/robot_arm/basic_button_test.robot
```

---

## 常見問題

### Q1: 如何快速驗證新按鈕配置是否正確？

**A**: 使用 dry-run 和測試腳本:

```bash
# 1. 語法檢查
robot --dryrun tests/robot_arm/test_new_button.robot

# 2. 使用 Python 快速測試
python3 << EOF
from libraries.robot_arm_control.RobotArmKeywords import RobotArmKeywords

robot = RobotArmKeywords()
robot.connect_robot_arm()
robot.click_my_new_button()  # 測試新按鈕
robot.go_to_home_position()
robot.disconnect_robot_arm()
EOF
```

### Q2: 如何處理多個測試環境的 IP 地址？

**A**: 使用環境變數或配置文件:

```bash
# 方法 1: 環境變數
export MYCOBOT_IP=<your_mycobot_ip>
robot tests/robot_arm/

# 方法 2: 使用場景切換腳本（推薦）
./config/robot_arm/switch_scene.sh production
```

### Q3: 場景配置檔案太多了，如何管理？

**A**: 使用清晰的命名和文檔:

```
config/robot_arm/scenes/
├── README.md                          # 場景說明文檔
├── lab_scene.yaml                    # 實驗室（開發測試）
├── production_line_1_scene.yaml      # 生產線 1 號站
├── production_line_2_scene.yaml      # 生產線 2 號站
├── customer_site_a_scene.yaml        # 客戶 A 現場
└── customer_site_b_scene.yaml        # 客戶 B 現場
```

在 `README.md` 中記錄每個場景的詳細資訊:

```markdown
# 場景配置說明

## lab_scene.yaml
- **用途**: 研發實驗室開發測試
- **地點**: 公司 3 樓實驗室
- **IP**: 10.42.0.180
- **面板**: RV 控制面板 v1.0 (SN: RV001)
- **最後更新**: 2025-11-06

## production_line_1_scene.yaml
- **用途**: 生產線測試站 1 號
- **地點**: 工廠 A 棟
- **IP**: 192.168.1.100
- **面板**: 生產測試面板 v2.0
- **最後更新**: 2025-11-05
```

### Q4: 如何在測試報告中顯示當前使用的場景？

**A**: 在測試案例中添加場景資訊:

```robot
*** Settings ***
Library          libraries.robot_arm_control.RobotArmKeywords
Suite Setup      顯示場景資訊

*** Keywords ***
顯示場景資訊
    ${scene}=    Get Environment Variable    ROBOT_ARM_SCENE    lab
    Log    當前測試場景: ${scene}    console=yes
    Set Suite Metadata    場景    ${scene}
```

### Q5: 能否在一個測試中使用多個場景？

**A**: 可以，透過 RobotArmKeywords 的初始化參數:

```robot
*** Settings ***
Library          libraries.robot_arm_control.RobotArmKeywords
...              config/robot_arm/scenes/lab_scene.yaml
...              AS    LabRobot

Library          libraries.robot_arm_control.RobotArmKeywords
...              config/robot_arm/scenes/production_scene.yaml
...              AS    ProductionRobot

*** Test Cases ***
跨場景測試
    # 使用實驗室機器手臂
    LabRobot.連接機器手臂
    LabRobot.點擊藍牙按鈕
    LabRobot.斷開機器手臂連接

    # 使用生產線機器手臂
    ProductionRobot.連接機器手臂
    ProductionRobot.點擊藍牙按鈕
    ProductionRobot.斷開機器手臂連接
```

---

## 總結

### 新增按鈕的關鍵步驟

1. ✅ **示教記錄** - 使用工具記錄抬起和按下位置
2. ✅ **配置添加** - 在 YAML 文件中添加按鈕定義
3. ✅ **關鍵字實現** - 在 RobotArmKeywords.py 中添加關鍵字
4. ✅ **測試驗證** - 創建測試案例並執行
5. ✅ **調整優化** - 根據測試結果微調位置

### 場景切換的推薦方案

| 方案 | 適用場景 | 優點 | 缺點 |
|------|---------|------|------|
| **多配置文件 + 切換腳本** | 頻繁切換場景 | 直觀、快速、易管理 | 需要維護多個文件 |
| **環境變數控制** | CI/CD 自動化 | 靈活、適合自動化 | 需要修改程式碼 |
| **Robot 變數文件** | Robot Framework 專案 | 與 RF 整合良好 | 僅適用於 RF 測試 |

**建議**: 使用**方案 1（多配置文件 + 切換腳本）**，最直觀且易於維護。

---

**文檔結束**
