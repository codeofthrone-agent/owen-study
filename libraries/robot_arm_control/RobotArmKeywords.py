"""
Robot Arm Keywords - MyCobot 280 Robot Framework 關鍵字庫
採用 BDD (Gherkin) 風格，提供機器手臂控制的完整測試關鍵字
"""

import time
import sys
import socket
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from robot.api import logger
from robot.api.deco import keyword

# 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.robot_arm_control.RobotArmKeywords
# 2. 作為檔案匯入: Library    ../../libraries/robot_arm_control/RobotArmKeywords.py
try:
    # 方式 1: 絕對匯入（作為模組）
    from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader
    from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
    from libraries.robot_arm_control.local_vision_analyzer import LocalVisionAnalyzer
    from libraries.robot_arm_control.image_source_manager import ImageSourceManager
    from config.robot_arm.environment_config import EnvironmentConfig
except ImportError:
    # 方式 2: 將當前目錄加入 sys.path，然後直接匯入
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    # 加入專案根目錄到 sys.path
    project_root = current_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from button_config_loader import ButtonConfigLoader
    from mycobot_socket_controller import MyCobotSocketController
    from local_vision_analyzer import LocalVisionAnalyzer
    from image_source_manager import ImageSourceManager
    from config.robot_arm.environment_config import EnvironmentConfig


class RobotArmKeywords:
    """
    MyCobot 280 機器手臂控制關鍵字庫 - BDD 風格

    採用雙層架構設計（Voice Control 模式），所有關鍵字遵循 Gherkin 語法。

    🎯 核心功能：
    - 連接管理（連接、斷開、回到初始位置）
    - BDD Given 關鍵字（3 個）- 前置條件驗證
    - BDD When 關鍵字（4 個）- 執行動作
    - BDD Then 關鍵字（2 個）- 預期結果驗證
    - BDD And 關鍵字（3 個）- 附加驗證

    📊 關鍵字統計：
    - 傳統關鍵字: 3 個（連接管理）
    - BDD 關鍵字: 12 個（Given 3 + When 4 + Then 2 + And 3）
    - 總計: 15 個關鍵字

    🔄 v2.0.0 更新日誌（2025-11-12）：
    - ✅ 全面改用 BDD 風格關鍵字
    - ✅ 移除傳統的點擊/長按按鈕關鍵字
    - ✅ 採用雙層架構設計（與 Voice Control 模式一致）
    - ✅ 完整支援 Gherkin 語法（Given-When-Then-And）
    - ✅ 所有關鍵字使用中文命名

    📚 使用範例：
        *** Test Cases ***
        Scenario: 透過機器手臂控制燈光
            Given 機器手臂已正確連接到控制面板
            And 控制面板電源狀態為 "ON"

            When 用戶透過機器手臂開啟第 "1" 號燈光

            Then 機器手臂操作應該成功完成
            And 機器手臂應該返回待命位置

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '4.0.0'  # v4.0.0: 新增環境管理、多色彩檢測、亮度檢測

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化關鍵字庫

        Args:
            config_path: 配置文件路徑，如果為 None 則使用預設路徑
        """
        self.config_loader = ButtonConfigLoader(config_path)
        self.controller: Optional[MyCobotSocketController] = None
        self._last_operation_success = False  # 記錄最後一次操作是否成功
        self._last_detection_result = None  # 記錄最後一次視覺檢測結果
        self._last_batch_detection_results = None  # 記錄批次檢測結果

        # v4.0.0 新增：環境管理
        self.current_environment: Optional[str] = None  # 當前環境名稱
        self.env_config: Optional[Dict[str, Any]] = None  # 當前環境配置
        self.image_source_config: Optional[Dict[str, Any]] = None  # 影像源配置
        self.current_panel_type: Optional[str] = None  # 當前面板類型
        self.panel_button_config: Optional[Dict[str, Any]] = None  # 面板按鈕配置
        self.image_source_manager: Optional[ImageSourceManager] = None  # 影像源管理器
        self.local_vision: Optional[LocalVisionAnalyzer] = None  # 本機視覺分析器

        logger.info(f"RobotArmKeywords 初始化完成 (v{self.ROBOT_LIBRARY_VERSION})")

    # ==================== 連接管理關鍵字 ====================

    @keyword("連接機器手臂")
    def connect_robot_arm(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        連接到機器手臂

        Args:
            host: 機器手臂 IP 地址。如果為 None，從配置文件讀取
            port: Socket 端口。如果為 None，從配置文件讀取（預設 9000）

        Examples:
            | 連接機器手臂 |                           # 使用配置文件中的 IP 和端口
            | 連接機器手臂 | 192.168.1.100 |          # 使用指定 IP，端口從配置讀取
            | 連接機器手臂 | 192.168.1.100 | 9000 |   # 指定 IP 和端口

        Raises:
            ConnectionError: 如果連接失敗
        """
        # 從配置文件讀取預設值
        socket_config = self.config_loader.get_socket_config()

        if host is None:
            host = socket_config['host']
        if port is None:
            port = socket_config['port']

        logger.info(f"正在連接機器手臂: {host}:{port}")

        # 創建控制器並連接
        self.controller = MyCobotSocketController(host, int(port))
        self.controller.connect()

        # 確保電源已開啟
        if not self.controller.is_power_on():
            logger.info("伺服馬達電源未開啟，正在開啟...")
            self.controller.power_on()

        logger.info("✅ 機器手臂連接成功")

    @keyword("斷開機器手臂連接")
    def disconnect_robot_arm(self):
        """
        斷開與機器手臂的連接

        Examples:
            | 斷開機器手臂連接 |
        """
        if self.controller is not None:
            self.controller.disconnect()
            self.controller = None
            logger.info("✅ 已斷開機器手臂連接")
        else:
            logger.warn("機器手臂未連接，無需斷開")

    @keyword("回到初始位置")
    def go_to_home_position(self, speed: int = 30):
        """
        移動機器手臂到初始位置 [0, 0, 0, 0, 0, 0]

        Args:
            speed: 移動速度 (1-100)，預設 30

        Examples:
            | 回到初始位置 |      # 使用預設速度 30
            | 回到初始位置 | 50 |  # 使用速度 50

        Raises:
            RuntimeError: 如果機器手臂未連接或移動失敗
        """
        self._ensure_connected()
        self.controller.go_to_home(speed)
        logger.info("✅ 已回到初始位置")

    # ==================== 內部輔助方法 ====================

    def _ensure_connected(self):
        """確保機器手臂已連接"""
        if self.controller is None or not self.controller.is_connected():
            raise RuntimeError(
                "機器手臂未連接。請先使用「連接機器手臂」關鍵字建立連接。"
            )

    def _press_button(self, button_id: str, custom_duration: Optional[float] = None):
        """
        通用按壓按鈕邏輯

        Args:
            button_id: 按鈕 ID
            custom_duration: 自定義按壓時間（秒），如果為 None 則使用配置中的時間
        """
        self._ensure_connected()

        # 獲取按鈕配置
        config = self._get_button_config(button_id)
        button_name = config.get('name', button_id)

        logger.info(f"開始按壓按鈕: {button_name} ({button_id})")

        # 1. 移動到按鈕上方 (抬起位置)，確保安全起點
        logger.debug(f"移動到按鈕上方: {config['up_angles']}")
        self.controller.send_angles(config['up_angles'], config['speed'])
        self.controller.wait_for_movement()

        # 移動到按下位置
        logger.debug(f"下壓按鈕: {config['down_angles']}")
        self.controller.send_angles(config['down_angles'], config['speed'])
        self.controller.wait_for_movement()

        # 保持按壓
        duration = custom_duration if custom_duration is not None else config['press_duration']
        logger.debug(f"保持按壓 {duration} 秒")
        time.sleep(duration)

        # 移動到抬起位置
        logger.debug(f"抬起手臂: {config['up_angles']}")
        self.controller.send_angles(config['up_angles'], config['speed'])
        self.controller.wait_for_movement()

        # 抬起後等待
        time.sleep(config['lift_duration'])

        logger.info(f"✅ 完成按壓按鈕: {button_name}")
        
        # 標記操作成功
        self._last_operation_success = True


    # ==================== BDD Given 關鍵字 ====================

    @keyword("Given 機器手臂已正確連接到控制面板")
    def given_robot_arm_connected_to_panel(self, host: Optional[str] = None, port: Optional[int] = None, speed: int = 30) -> bool:
        """
        Given: 機器手臂已正確連接到控制面板

        前置條件：驗證機器手臂連接狀態並回到初始位置，確保系統準備就緒

        Args:
            host: 機器手臂 IP 地址（選填，預設從配置讀取）
            port: Socket 端口（選填，預設從配置讀取）
            speed: 回到初始位置的速度 (1-100)，預設 30

        Returns:
            bool: 連接是否成功

        Examples:
            | Given | 機器手臂已正確連接到控制面板 |                           # 使用預設速度 30
            | Given | 機器手臂已正確連接到控制面板 | 192.168.1.100 |          # 指定 IP，速度 30
            | Given | 機器手臂已正確連接到控制面板 | 192.168.1.100 | 9000 |   # 指定 IP 和端口，速度 30
            | Given | 機器手臂已正確連接到控制面板 | ${NONE} | ${NONE} | 50 | # 預設連接，速度 50

        Raises:
            ConnectionError: 如果連接失敗
            RuntimeError: 如果無法回到初始位置
        """
        try:
            # 連接機器手臂
            self.connect_robot_arm(host, port)

            # 回到初始位置（安全起點）
            self.go_to_home_position(speed=speed)

            logger.info(f"✓ 機器手臂已連接並位於初始位置（速度: {speed}）")
            self._last_operation_success = True
            return True

        except Exception as e:
            logger.error(f"✗ 機器手臂連接失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword('Given 控制面板電源狀態為 "${power_state}"')
    def given_panel_power_state(self, power_state: str) -> bool:
        """
        Given: 控制面板電源狀態為指定狀態

        前置條件：確認被測控制面板的電源狀態

        Args:
            power_state: 電源狀態（ON/OFF）

        Returns:
            bool: 驗證是否成功

        Examples:
            | Given | 控制面板電源狀態為 "ON" |
            | Given | 控制面板電源狀態為 "OFF" |

        Note:
            目前為日誌記錄，未來可整合視覺檢測或其他驗證方式
        """
        logger.info(f"確認控制面板電源狀態: {power_state}")

        # TODO: 可以整合 IPCamLightDetection 進行視覺驗證
        # 例如：檢測面板指示燈是否亮起

        self._last_operation_success = True
        return True

    @keyword("Given 機器手臂系統處於待命狀態")
    def given_robot_arm_in_standby(self) -> bool:
        """
        Given: 機器手臂系統處於待命狀態

        前置條件：確認機器手臂在安全待命位置（初始位置）

        Returns:
            bool: 驗證是否成功

        Examples:
            | Given | 機器手臂系統處於待命狀態 |

        Raises:
            RuntimeError: 如果機器手臂未連接
        """
        self._ensure_connected()

        # 檢查是否在初始位置附近
        current_angles = self.controller.get_angles()
        logger.debug(f"當前角度: {current_angles}")

        # 簡單驗證（檢查是否接近 [0, 0, 0, 0, 0, 0]）
        home_position = [0, 0, 0, 0, 0, 0]
        tolerance = 5.0  # 允許 5 度誤差

        is_at_home = all(
            abs(current - home) <= tolerance
            for current, home in zip(current_angles, home_position)
        )

        if is_at_home:
            logger.info("✓ 機器手臂處於待命狀態（初始位置）")
            self._last_operation_success = True
            return True
        else:
            logger.warn(f"⚠️  機器手臂不在待命位置，當前角度: {current_angles}")
            logger.info("正在移動到待命位置...")
            self.go_to_home_position()
            self._last_operation_success = True
            return True

    # ==================== BDD Given 關鍵字 - 環境管理 (v4.0.0) ====================

    @keyword('Given 測試環境設定為 "${environment}"')
    def given_test_environment_is(self, environment: str):
        """Given: 測試環境設定為指定環境

        設定測試環境，並智能地初始化視覺分析模組。
        如果機器手臂已連接，則使用共享 Socket；否則，使用獨立連接。

        Args:
            environment: 環境名稱 ("taipei_lab" | "taoyuan_lab" | "rv_car")

        Examples:
            | Given | 測試環境設定為 "taipei_lab" |
            | Given | 測試環境設定為 "taoyuan_lab" |

        Raises:
            ValueError: 未知環境名稱
        """
        logger.info(f"正在設定測試環境: {environment}")

        # 取得環境配置
        self.env_config = EnvironmentConfig.get_environment(environment)
        self.current_environment = environment

        # 智能初始化視覺模組
        shared_socket = None
        if self.controller and self.controller.is_connected():
            try:
                shared_socket = self.controller.socket
                logger.info("檢測到已存在的控制器連接，視覺模組將使用共享 Socket。")
            except Exception as e:
                logger.warning(f"無法從控制器取得共享 Socket: {e}。視覺模組將使用獨立連接。")

        # 初始化影像源管理器 (可能帶有共享 socket)
        self.image_source_manager = ImageSourceManager(shared_socket=shared_socket)

        # 取得影像源配置並設定
        self.image_source_config = EnvironmentConfig.get_image_source_config(environment)
        self.image_source_manager.set_image_source(
            self.image_source_config["type"],
            self.image_source_config
        )

        # 初始化本機視覺分析器
        self.local_vision = LocalVisionAnalyzer(self.image_source_manager)

        logger.info(f"✅ 測試環境已切換至: {self.env_config['name']}")
        logger.info(f"   影像源: {self.image_source_config['type']}")
        if shared_socket:
            logger.info("   視覺模組狀態: 使用共享 Socket")
        else:
            logger.info("   視覺模組狀態: 將建立獨立連接")

    @keyword('Given 面板類型設定為 "${panel_type}"')
    def given_panel_type_is(self, panel_type: str):
        """Given: 面板類型設定為指定型號

        設定面板類型並載入對應的按鈕配置。

        Args:
            panel_type: 面板型號 ("3510a" | "3611a" | "3611c")

        Examples:
            | Given | 面板類型設定為 "3611a" |
            | Given | 面板類型設定為 "3611c" |

        Raises:
            RuntimeError: 尚未設定測試環境
            ValueError: 當前環境不支援該面板類型
        """
        if self.current_environment is None or self.env_config is None:
            raise RuntimeError(
                "尚未設定測試環境，請先使用 'Given 測試環境設定為 \"${environment}\"' 關鍵字"
            )

        # 驗證面板類型
        if panel_type not in self.env_config["panel_types"]:
            raise ValueError(
                f"當前環境 '{self.current_environment}' 不支援面板類型: {panel_type}\n"
                f"支援的面板: {', '.join(self.env_config['panel_types'])}"
            )

        self.current_panel_type = panel_type

        # 載入對應的按鈕配置
        config_path = self.env_config["button_config_path"]
        self.panel_button_config = self._load_panel_button_config(config_path, panel_type)

        logger.info(f"✅ 面板類型已設定為: {panel_type}")
        logger.info(f"   載入配置: {config_path}")
        logger.info(f"   按鈕數量: {len(self.panel_button_config)}")

    def _load_panel_button_config(self, config_path: str, panel_type: str) -> Dict[str, Any]:
        """載入面板按鈕配置（從 YAML 檔案）

        Args:
            config_path: YAML 配置檔案路徑
            panel_type: 面板類型

        Returns:
            dict: 按鈕配置字典

        Raises:
            FileNotFoundError: 配置檔案不存在
            ValueError: 面板類型不存在於配置中
        """
        # 支援相對路徑和絕對路徑
        config_file = Path(config_path)
        if not config_file.is_absolute():
            # 相對於專案根目錄
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / config_path

        if not config_file.exists():
            raise FileNotFoundError(f"配置檔案不存在: {config_file}")

        # 載入 YAML 配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 取得面板配置
        # 檢查新格式（有 panels 結構）還是舊格式（直接的 buttons）
        if "panels" in config_data and panel_type in config_data["panels"]:
            # 新格式：支援多面板
            panel_config = config_data["panels"][panel_type]
            result = {
                "buttons": panel_config.get("buttons", {}),
                "physical_lights": config_data.get("physical_lights", {})
            }
        elif "buttons" in config_data:
            # 舊格式（現有格式）：單一面板配置
            # 驗證面板類型是否匹配
            if "environment" in config_data and config_data["environment"].get("panel_type") != panel_type:
                raise ValueError(
                    f"配置檔案的面板類型 '{config_data['environment'].get('panel_type')}' "
                    f"與請求的面板類型 '{panel_type}' 不匹配"
                )
            
            result = {
                "buttons": config_data.get("buttons", {}),
                "environment_lights": config_data.get("environment_lights", {})
            }
        else:
            raise ValueError(f"配置檔案中找不到面板類型或按鈕配置")

        return result

    # ==================== BDD When 關鍵字 ====================

    @keyword('When 用戶透過機器手臂開啟第 "${light_number}" 號燈光')
    def when_user_turns_on_light_via_robot_arm(self, light_number: str) -> bool:
        """
        When: 用戶透過機器手臂開啟指定編號的燈光

        執行動作：控制機器手臂按壓對應的燈光按鈕

        Args:
            light_number: 燈光編號（1-8）

        Returns:
            bool: 操作是否成功

        Examples:
            | When | 用戶透過機器手臂開啟第 "1" 號燈光 |
            | When | 用戶透過機器手臂開啟第 "3" 號燈光 |

        Raises:
            ValueError: 如果燈光編號無效
            RuntimeError: 如果機器手臂未連接
        """
        try:
            # 驗證燈光編號
            light_num = int(light_number)
            if not 1 <= light_num <= 8:
                raise ValueError(f"燈光編號必須在 1-8 之間，收到: {light_number}")

            button_id = f'light{light_num}'
            logger.info(f"透過機器手臂開啟第 {light_num} 號燈光")

            self._press_button(button_id)
            self._last_operation_success = True
            return True

        except Exception as e:
            logger.error(f"✗ 開啟燈光失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword("When 用戶透過機器手臂切換藍牙連接")
    def when_user_toggles_bluetooth_via_robot_arm(self) -> bool:
        """
        When: 用戶透過機器手臂切換藍牙連接

        執行動作：控制機器手臂按壓藍牙按鈕

        Returns:
            bool: 操作是否成功

        Examples:
            | When | 用戶透過機器手臂切換藍牙連接 |

        Raises:
            RuntimeError: 如果機器手臂未連接
        """
        try:
            logger.info("透過機器手臂切換藍牙連接")
            self._press_button('bluetooth')
            self._last_operation_success = True
            return True

        except Exception as e:
            logger.error(f"✗ 切換藍牙失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword('When 用戶透過機器手臂啟動 "${device_name}" 設備')
    def when_user_activates_device_via_robot_arm(self, device_name: str) -> bool:
        """
        When: 用戶透過機器手臂啟動指定設備

        執行動作：根據設備名稱控制機器手臂按壓對應按鈕

        Args:
            device_name: 設備名稱（支援：熱水器、空調、瓦斯、水泵、水箱加熱器、門鎖）

        Returns:
            bool: 操作是否成功

        Examples:
            | When | 用戶透過機器手臂啟動 "熱水器" 設備 |
            | When | 用戶透過機器手臂啟動 "空調" 設備 |
            | When | 用戶透過機器手臂啟動 "瓦斯" 設備 |

        Raises:
            ValueError: 如果設備名稱未知
            RuntimeError: 如果機器手臂未連接
        """
        # 設備名稱映射到按鈕 ID
        device_mapping = {
            '熱水器': 'water_heater',
            '空調': 'hvac',
            '瓦斯': 'gas',
            '水泵': 'water_pump',
            '水箱加熱器': 'tanker_heater',
            '門鎖': 'door_lock',
            'AUX1': 'aux1',
            'AUX2': 'aux2',
            'Select': 'select'
        }

        try:
            button_id = device_mapping.get(device_name)
            if not button_id:
                supported = ', '.join(device_mapping.keys())
                raise ValueError(f"未知的設備名稱: {device_name}。支援的設備: {supported}")

            logger.info(f"透過機器手臂啟動設備: {device_name} (按鈕: {button_id})")
            self._press_button(button_id)
            self._last_operation_success = True
            return True

        except Exception as e:
            logger.error(f"✗ 啟動設備失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword('When 用戶透過機器手臂長按 "${button_type}" 按鈕 "${seconds}" 秒')
    def when_user_long_presses_button_via_robot_arm(self, button_type: str, seconds: str) -> bool:
        """
        When: 用戶透過機器手臂長按指定按鈕

        執行動作：控制機器手臂長按按鈕指定時間

        Args:
            button_type: 按鈕類型（縮回/伸展）
            seconds: 按壓秒數

        Returns:
            bool: 操作是否成功

        Examples:
            | When | 用戶透過機器手臂長按 "縮回" 按鈕 "7" 秒 |
            | When | 用戶透過機器手臂長按 "伸展" 按鈕 "10" 秒 |

        Raises:
            ValueError: 如果按鈕類型未知或秒數無效
            RuntimeError: 如果機器手臂未連接
        """
        button_mapping = {
            '縮回': 'retract',
            '伸展': 'extend',
            'Retract': 'retract',
            'Extend': 'extend'
        }

        try:
            button_id = button_mapping.get(button_type)
            if not button_id:
                supported = ', '.join(button_mapping.keys())
                raise ValueError(f"未知的按鈕類型: {button_type}。支援的類型: {supported}")

            duration = float(seconds)
            if duration <= 0:
                raise ValueError(f"按壓秒數必須大於 0，收到: {seconds}")

            logger.info(f"透過機器手臂長按 {button_type} 按鈕 {duration} 秒")
            self._press_button(button_id, custom_duration=duration)
            self._last_operation_success = True
            return True

        except Exception as e:
            logger.error(f"✗ 長按按鈕失敗: {e}")
            self._last_operation_success = False
            raise

    # ==================== BDD When 關鍵字 - 多色彩檢測 (v4.0.0) ====================

    @keyword('When 用戶檢測面板按鈕 "${button_id}" 的顏色')
    def when_user_detects_panel_button_color(self, button_id: str, save_debug_image: bool = False, step_prefix: str = "") -> Dict[str, Any]:
        """When: 用戶檢測面板按鈕的顏色

        執行動作：檢測指定面板按鈕的 LED 顏色（本機視覺檢測）

        支援顏色: 藍/白/紅/綠/黃/橙/紫/關閉

        Args:
            button_id: 按鈕 ID（定義在環境配置中，如 "light1", "bluetooth"）
            save_debug_image: 是否儲存除錯影像
            step_prefix: 步驟命名前綴 (例如: "step2_before")

        Returns:
            dict: 檢測結果字典，包含:
                - color (str): 檢測到的顏色
                - brightness (int): 亮度級別 (0-100)
                - confidence (float): 檢測信心度 (0.0-1.0)
                - hsv_mean (tuple): HSV 平均值
                - brightness_value (float): 原始亮度值 (0-255)
                - light_state (str): 燈光狀態 ("on" | "off")

        Examples:
            | When | 用戶檢測面板按鈕 "light1" 的顏色 |
            | When | 用戶檢測面板按鈕 "bluetooth" 的顏色 |

        Raises:
            RuntimeError: 尚未設定測試環境或面板類型
            ValueError: 按鈕不存在
            RuntimeError: 檢測失敗

        Note:
            檢測結果會儲存在 self._last_detection_result，供 Then 關鍵字驗證使用
        """
        # 驗證前置條件
        if self.current_environment is None or self.current_panel_type is None:
            raise RuntimeError(
                "尚未設定測試環境或面板類型，請先使用:\n"
                "  'Given 測試環境設定為 \"${environment}\"'\n"
                "  'Given 面板類型設定為 \"${panel_type}\"'"
            )

        # 取得按鈕配置
        button_config = self._get_button_config(button_id)

        logger.info(f"📸 正在檢測面板按鈕 '{button_id}' 的顏色...")

        # 移動機器手臂到觀測角度（如果需要且已連接機器手臂）
        if "vision" in button_config and "observe_angles" in button_config["vision"] and self.controller is not None:
            try:
                observe_angles = button_config["vision"]["observe_angles"]
                logger.debug(f"移動到觀測角度: {observe_angles}")
                self.controller.send_angles(observe_angles, 30)
                time.sleep(2)  # 等待穩定
            except Exception as e:
                logger.warning(f"移動到觀測角度失敗: {e}，繼續使用當前角度檢測")

        # 準備 ROI 配置（單一按鈕）
        if "vision" in button_config and "roi" in button_config["vision"]:
            roi_config = {button_id: button_config["vision"]["roi"]}
        else:
            raise ValueError(f"按鈕 '{button_id}' 沒有配置 ROI 視覺檢測資訊")

        # 本機執行視覺檢測
        try:
            results = self.local_vision.detect_panel_light(
                panel_type=self.current_panel_type,
                roi_config=roi_config,
                image_source_config=self.image_source_manager.get_current_source()["config"],
                num_frames=5,
                warmup_frames=20,
                save_debug_images=save_debug_image,  # 根據參數決定是否儲存除錯影像
                step_prefix=step_prefix  # 傳遞步驟前綴
            )

            # 取得單一按鈕結果
            result = results[button_id]

            # 儲存結果供 Then 關鍵字驗證
            self._last_detection_result = result

            logger.info(
                f"✅ 檢測完成: 顏色={result['color']}, "
                f"亮度={result['brightness']}%, "
                f"信心度={result['confidence']:.2f}, "
                f"狀態={result['light_state']}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ 視覺檢測失敗: {e}")
            raise RuntimeError(f"無法檢測按鈕 '{button_id}' 的顏色: {e}")

    def _get_button_config(self, button_id: str) -> Dict[str, Any]:
        """取得按鈕配置（輔助方法）

        Args:
            button_id: 按鈕 ID

        Returns:
            dict: 按鈕配置字典

        Raises:
            ValueError: 按鈕不存在
        """
        if self.panel_button_config is None:
            raise RuntimeError("尚未載入面板按鈕配置")

        buttons = self.panel_button_config.get("buttons", {})

        if button_id not in buttons:
            available_buttons = ", ".join(buttons.keys())
            raise ValueError(
                f"按鈕 '{button_id}' 不存在於當前面板 '{self.current_panel_type}'。\n"
                f"可用按鈕: {available_buttons}"
            )

        return buttons[button_id]

    @keyword('When 用戶檢測實體燈光亮度 "${light_id}"')
    def when_user_detects_physical_light_brightness(self, light_id: str, save_debug_image: bool = False, step_prefix: str = "") -> Dict[str, Any]:
        """When: 用戶檢測實體燈光亮度

        執行動作：檢測實體燈光的亮度級別（本機視覺檢測）

        支援 11 級亮度: 0%, 10%, 20%, ..., 100%

        Args:
            light_id: 燈光 ID（定義在環境配置中，如 "ceiling_light_1", "desk_lamp"）
            save_debug_image: 是否儲存除錯影像
            step_prefix: 步驟命名前綴 (例如: "step3_before")

        Returns:
            dict: 檢測結果字典，包含:
                - light_state (str): 燈光狀態 ("on" | "off")
                - brightness_level (int): 亮度級別 (0-100)
                - brightness_value (float): 原始亮度值 (0-255)
                - confidence (float): 檢測信心度 (0.0-1.0)

        Examples:
            | When | 用戶檢測實體燈光亮度 "ceiling_light_1" |
            | When | 用戶檢測實體燈光亮度 "desk_lamp" |

        Raises:
            RuntimeError: 尚未設定測試環境或面板類型
            ValueError: 燈光不存在
            RuntimeError: 檢測失敗

        Note:
            檢測結果會儲存在 self._last_detection_result，供 Then 關鍵字驗證使用
        """
        # 驗證前置條件
        if self.current_environment is None:
            raise RuntimeError(
                "尚未設定測試環境，請先使用 'Given 測試環境設定為 \"${environment}\"'"
            )

        # 取得燈光配置
        light_config = self._get_light_config(light_id)

        logger.info(f"💡 正在檢測實體燈光 '{light_id}' 的亮度...")

        # 移動機器手臂到觀測角度（如果需要且已連接機器手臂）
        if "observe_angles" in light_config and self.controller is not None:
            try:
                observe_angles = light_config["observe_angles"]
                # 檢查是否需要移動（觀測角度不是 [0,0,0,0,0,0]）
                if any(angle != 0 for angle in observe_angles):
                    logger.debug(f"移動到觀測角度: {observe_angles}")
                    self.controller.send_angles(observe_angles, 30)
                    time.sleep(2)  # 等待穩定
            except Exception as e:
                logger.warning(f"移動到觀測角度失敗: {e}，繼續使用當前角度檢測")

        # 本機執行亮度檢測
        try:
            # 根據燈光配置中的 camera_id 取得對應的影像源配置
            camera_id = light_config.get("camera_id")
            if camera_id:
                # 使用指定的 RTSP Camera
                from config.robot_arm.environment_config import EnvironmentConfig
                image_source_config = EnvironmentConfig.get_image_source_config(
                    self.current_environment,
                    camera_id=camera_id
                )
                logger.debug(f"使用 RTSP Camera: {camera_id} ({image_source_config.get('url', 'N/A')})")
            else:
                # 使用當前影像源（Socket）
                image_source_config = self.image_source_manager.get_current_source()["config"]
                logger.debug(f"使用當前影像源: {image_source_config['type']}")

            detection_result, _, _ = self.local_vision.detect_physical_light_brightness(
                roi_config=light_config["roi"],
                image_source_config=image_source_config,
                num_frames=5,
                warmup_frames=20,
                save_debug_images=save_debug_image,  # 根據參數決定是否儲存除錯影像
                step_prefix=step_prefix  # 傳遞步驟前綴
            )

            # 儲存結果供 Then 關鍵字驗證
            self._last_detection_result = detection_result

            logger.info(
                f"✅ 檢測完成: 亮度={detection_result['brightness_level']}%, "
                f"原始值={detection_result['brightness_value']:.1f}, "
                f"信心度={detection_result['confidence']:.2f}, "
                f"狀態={detection_result['light_state']}"
            )

            return detection_result

        except Exception as e:
            logger.error(f"❌ 亮度檢測失敗: {e}")
            raise RuntimeError(f"無法檢測燈光 '{light_id}' 的亮度: {e}")

    def _get_light_config(self, light_id: str) -> Dict[str, Any]:
        """取得燈光配置（輔助方法）

        Args:
            light_id: 燈光 ID

        Returns:
            dict: 燈光配置字典

        Raises:
            ValueError: 燈光不存在
        """
        if self.current_environment is None:
            raise RuntimeError("尚未設定測試環境")

        # 直接從已載入的面板配置中取得環境燈光
        if self.panel_button_config is None:
            raise RuntimeError("尚未載入面板按鈕配置")

        environment_lights = self.panel_button_config.get("environment_lights", {})

        if light_id not in environment_lights:
            available_lights = ", ".join(environment_lights.keys())
            raise ValueError(
                f"燈光 '{light_id}' 不存在於當前環境 '{self.current_environment}'。\n"
                f"可用燈光: {available_lights}"
            )

        return environment_lights[light_id]

    # ==================== BDD Then 關鍵字 ====================

    @keyword("Then 機器手臂操作應該成功完成")
    def then_robot_arm_operation_should_complete_successfully(self) -> bool:
        """
        Then: 機器手臂操作應該成功完成

        預期結果：驗證機器手臂完成動作並無錯誤

        Returns:
            bool: 驗證是否通過

        Examples:
            | Then | 機器手臂操作應該成功完成 |

        Raises:
            AssertionError: 如果操作未成功完成
            RuntimeError: 如果機器手臂未連接
        """
        self._ensure_connected()

        # 檢查機器手臂是否正在移動
        if self.controller.is_moving():
            raise AssertionError("機器手臂仍在移動中，操作未完成")

        # 檢查最後一次操作是否成功
        if not self._last_operation_success:
            raise AssertionError("最後一次操作標記為失敗")

        logger.info("✓ 機器手臂操作成功完成")
        return True

    @keyword('Then 控制面板應該顯示 "${expected_state}" 狀態')
    def then_panel_should_display_state(self, expected_state: str) -> bool:
        """
        Then: 控制面板應該顯示指定狀態

        預期結果：驗證控制面板狀態變化（目前為日誌記錄，未來可整合視覺檢測）

        Args:
            expected_state: 預期狀態描述

        Returns:
            bool: 驗證是否通過

        Examples:
            | Then | 控制面板應該顯示 "燈光已開啟" 狀態 |
            | Then | 控制面板應該顯示 "藍牙已連接" 狀態 |
            | Then | 控制面板應該顯示 "設備已啟動" 狀態 |

        Note:
            目前為日誌記錄驗證
            TODO: 可整合 IPCamLightDetection 進行實際視覺驗證
        """
        logger.info(f"驗證控制面板狀態: {expected_state}")

        # TODO: 整合視覺檢測
        # 例如：使用 IPCamLightDetection 檢測面板指示燈變化
        # from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
        # detector = IPCamLightDetection()
        # brightness = detector.get_current_brightness()
        # if brightness > threshold:
        #     logger.info("✓ 面板狀態變化已確認（視覺檢測）")

        logger.info(f"✓ 控制面板預期狀態: {expected_state}")
        return True

    # ==================== BDD Then 關鍵字 - 多色彩檢測 (v4.0.0) ====================

    @keyword('Then 面板按鈕顏色應該為 "${expected_color}"')
    def then_panel_button_color_should_be(self, expected_color: str):
        """Then: 面板按鈕顏色應該為指定顏色

        預期結果：驗證面板按鈕的 LED 顏色是否符合預期

        Args:
            expected_color: 預期顏色 ("blue", "white", "red", "green", "yellow", "orange", "purple", "off")

        Examples:
            | Then | 面板按鈕顏色應該為 "blue" |
            | Then | 面板按鈕顏色應該為 "white" |
            | Then | 面板按鈕顏色應該為 "off" |

        Raises:
            RuntimeError: 尚未執行檢測
            AssertionError: 顏色不符預期

        Note:
            此關鍵字會驗證最後一次檢測的結果（透過 When 用戶檢測... 儲存）
        """
        if self._last_detection_result is None:
            raise RuntimeError(
                "尚未執行檢測，請先使用 'When 用戶檢測面板按鈕 \"${button_id}\" 的顏色' 關鍵字"
            )

        actual_color = self._last_detection_result.get("color")
        confidence = self._last_detection_result.get("confidence", 0.0)
        brightness = self._last_detection_result.get("brightness", 0)
        hsv_mean = self._last_detection_result.get("hsv_mean")

        if actual_color != expected_color:
            raise AssertionError(
                f"❌ 面板按鈕顏色不符預期！\n"
                f"   預期顏色: {expected_color}\n"
                f"   實際顏色: {actual_color}\n"
                f"   檢測信心度: {confidence:.2f}\n"
                f"   亮度級別: {brightness}%\n"
                f"   HSV 平均值: {hsv_mean}"
            )

        logger.info(
            f"✅ 面板按鈕顏色驗證通過: {actual_color} "
            f"(信心度: {confidence:.2f}, 亮度: {brightness}%)"
        )

    @keyword('Then 實體燈光亮度應該為 "${expected_level}" %')
    def then_physical_light_brightness_should_be(self, expected_level: str):
        """Then: 實體燈光亮度應該為指定級別

        預期結果：驗證實體燈光亮度是否符合預期（允許 ±10% 誤差）

        Args:
            expected_level: 預期亮度百分比 (0-100)

        Examples:
            | Then | 實體燈光亮度應該為 "0" % |
            | Then | 實體燈光亮度應該為 "50" % |
            | Then | 實體燈光亮度應該為 "100" % |

        Raises:
            RuntimeError: 尚未執行檢測
            AssertionError: 亮度不符預期（誤差超過 ±10%）

        Note:
            此關鍵字會驗證最後一次檢測的結果（透過 When 用戶檢測... 儲存）
            允許 ±10% 的誤差範圍（例如預期 50%，實際 45%-55% 都算通過）
        """
        if self._last_detection_result is None:
            raise RuntimeError(
                "尚未執行檢測，請先使用 'When 用戶檢測實體燈光亮度 \"${light_id}\"' 關鍵字"
            )

        expected_level = int(expected_level)
        actual_level = self._last_detection_result.get("brightness_level")
        confidence = self._last_detection_result.get("confidence", 0.0)
        brightness_value = self._last_detection_result.get("brightness_value", 0)
        light_state = self._last_detection_result.get("light_state", "unknown")

        # 允許 ±10% 誤差
        error_margin = 10
        error = abs(actual_level - expected_level)

        if error > error_margin:
            raise AssertionError(
                f"❌ 實體燈光亮度不符預期！\n"
                f"   預期亮度: {expected_level}%\n"
                f"   實際亮度: {actual_level}%\n"
                f"   誤差: {error}% (允許 ±{error_margin}%)\n"
                f"   原始亮度值: {brightness_value:.1f}/255\n"
                f"   檢測信心度: {confidence:.2f}\n"
                f"   燈光狀態: {light_state}"
            )

        logger.info(
            f"✅ 實體燈光亮度驗證通過: {actual_level}% "
            f"(預期: {expected_level}%, 誤差: {error}%, 信心度: {confidence:.2f})"
        )

    # ==================== BDD And 關鍵字 ====================

    @keyword("And 機器手臂應該返回待命位置")
    def and_robot_arm_should_return_to_standby(self, speed: int = 30) -> bool:
        """
        And: 機器手臂應該返回待命位置

        附加驗證：確保機器手臂安全返回初始位置

        Args:
            speed: 移動速度 (1-100)，預設 30

        Returns:
            bool: 操作是否成功

        Examples:
            | And | 機器手臂應該返回待命位置 |      # 使用預設速度 30
            | And | 機器手臂應該返回待命位置 | 50 |  # 使用速度 50
            | And | 機器手臂應該返回待命位置 | 80 |  # 使用速度 80

        Raises:
            RuntimeError: 如果機器手臂未連接或移動失敗
        """
        try:
            self.go_to_home_position(speed=speed)
            logger.info(f"✓ 機器手臂已返回待命位置（速度: {speed}）")
            return True

        except Exception as e:
            logger.error(f"✗ 返回待命位置失敗: {e}")
            raise

    @keyword("And 系統應該記錄完整操作歷程")
    def and_system_should_log_operation_history(self) -> bool:
        """
        And: 系統應該記錄完整操作歷程

        附加驗證：記錄操作時間和結果（目前為日誌記錄，未來可整合 TestLink）

        Returns:
            bool: 記錄是否成功

        Examples:
            | And | 系統應該記錄完整操作歷程 |

        Note:
            目前為日誌記錄
            TODO: 可整合 TestLink API 進行測試結果回報
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"操作記錄時間: {timestamp}")
        logger.info(f"操作狀態: {'成功' if self._last_operation_success else '失敗'}")

        # TODO: 整合 TestLink 回報
        # from libraries.testlink_integration.TestLinkIntegration import TestLinkIntegration
        # testlink = TestLinkIntegration()
        # testlink.report_test_result(...)

        logger.info("✓ 操作歷程已記錄")
        return True

    @keyword("And 暫存檔案應該正確清理")
    def and_temp_files_should_be_cleaned(self) -> bool:
        """
        And: 暫存檔案應該正確清理

        附加驗證：清理測試過程中產生的暫存檔案

        Returns:
            bool: 清理是否成功

        Examples:
            | And | 暫存檔案應該正確清理 |

        Note:
            目前為日誌記錄
            機器手臂測試通常不產生暫存檔案，此關鍵字主要用於統一 Teardown
        """
        logger.info("檢查暫存檔案...")
        # 機器手臂測試通常不產生暫存檔案
        logger.info("✓ 暫存檔案清理完成（無需清理）")
        return True

    # ==================== 視覺檢測關鍵字 (v3.0.0新增) ====================

    def _send_vision_command(self, command: dict, timeout: float = 30.0) -> dict:
        """
        發送視覺檢測命令到伺服器

        Args:
            command: JSON 命令字典
            timeout: 等待回應的超時時間（秒），預設 30 秒

        Returns:
            伺服器回應的字典

        Raises:
            RuntimeError: 如果機器手臂未連接或命令執行失敗
        """
        self._ensure_connected()

        try:
            import socket as sock_module

            # 設定 socket timeout
            original_timeout = self.controller.socket.gettimeout()
            self.controller.socket.settimeout(timeout)

            try:
                # 使用底層 socket 發送 JSON 命令
                cmd_str = json.dumps(command, ensure_ascii=False)
                logger.debug(f"發送視覺命令: {cmd_str[:200]}...")
                self.controller.socket.sendall(cmd_str.encode('utf-8'))

                # 接收回應
                response = b""
                start_time = time.time()

                while True:
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        raise sock_module.timeout(f"接收回應超時（{timeout}秒）")

                    try:
                        chunk = self.controller.socket.recv(65536)
                        if not chunk:
                            # 連接關閉，嘗試解析已接收的資料
                            if response:
                                break
                            else:
                                raise RuntimeError("連接關閉，未收到任何回應")

                        response += chunk

                        # 嘗試解析 JSON
                        try:
                            result = json.loads(response.decode('utf-8'))
                            logger.debug(f"收到視覺檢測結果: {result.get('status')}")
                            return result
                        except json.JSONDecodeError:
                            # JSON 不完整，繼續接收
                            continue

                    except sock_module.timeout:
                        # Socket timeout，檢查是否已收到完整資料
                        if response:
                            try:
                                result = json.loads(response.decode('utf-8'))
                                logger.debug(f"收到視覺檢測結果（timeout 後）: {result.get('status')}")
                                return result
                            except json.JSONDecodeError:
                                pass
                        # 未收到完整資料，繼續等待
                        continue

                # 迴圈結束，嘗試最後一次解析
                if response:
                    result = json.loads(response.decode('utf-8'))
                    return result
                else:
                    raise RuntimeError("未收到伺服器回應")

            finally:
                # 恢復原始 timeout
                self.controller.socket.settimeout(original_timeout)

        except sock_module.timeout as e:
            logger.error(f"視覺命令執行逾時: {e}")
            raise RuntimeError(f"視覺命令執行逾時: {e}")
        except Exception as e:
            logger.error(f"視覺命令執行失敗: {e}")
            raise RuntimeError(f"視覺命令執行失敗: {e}")

    @keyword('When 用戶檢測第 "${button_id}" 按鈕的燈光狀態')
    def when_user_detects_button_light_state(self, button_id: str, save_debug_image: bool = False) -> dict:
        """
        When: 用戶檢測指定按鈕的燈光狀態（本機化視覺檢測）

        執行動作：透過本機 LocalVisionAnalyzer 檢測按鈕的 LED 狀態

        Args:
            button_id: 按鈕 ID（例如：light1, bluetooth, door_lock）
            save_debug_image: 是否儲存除錯影像（預設：False）

        Returns:
            dict: 檢測結果
                {
                    "color": "blue" | "white" | "red" | "green" | "yellow" | "orange" | "purple" | "off" | "unknown",
                    "brightness_level": 0-100,
                    "confidence": 0.0-1.0,
                    "raw_brightness": 0-255
                }

        Examples:
            | When | 用戶檢測第 "light1" 按鈕的燈光狀態 |
            | When | 用戶檢測第 "light1" 按鈕的燈光狀態 | save_debug_image=True |

        Raises:
            RuntimeError: 如果檢測失敗
            ValueError: 如果環境未設定或按鈕不存在
        """
        try:
            # 確保環境已設定
            if not self.current_environment:
                raise ValueError("尚未設定測試環境，請先執行 'Given 當前測試環境為'")

            # 確保本機視覺分析器已初始化
            if not self.local_vision:
                raise RuntimeError("本機視覺分析器未初始化")

            # 從環境配置載入按鈕 ROI
            try:
                from config.robot_arm.config_loader import ConfigLoader
            except ImportError:
                # 回退到相對匯入
                import sys
                from pathlib import Path
                config_dir = Path(__file__).parent.parent.parent / 'config' / 'robot_arm'
                if str(config_dir) not in sys.path:
                    sys.path.insert(0, str(config_dir.parent))
                from robot_arm.config_loader import ConfigLoader

            config_loader = ConfigLoader(self.current_environment)
            button_config = config_loader.get_button(button_id)

            if not button_config or 'vision' not in button_config:
                raise ValueError(f"按鈕 '{button_id}' 未校準視覺檢測 ROI")

            roi_config = button_config['vision']['roi']

            # 檢測按鈕狀態（使用 LocalVisionAnalyzer.detect_single_button）
            detection_result = self.local_vision.detect_single_button(
                button_id=button_id,
                roi_config=roi_config,
                image_source_config=self.image_source_config,
                save_debug_image=save_debug_image
            )

            logger.info(f"✓ 檢測完成 - "
                       f"顏色: {detection_result['color']}, "
                       f"亮度: {detection_result['brightness_level']}%, "
                       f"信心度: {detection_result['confidence']:.2f}")

            # 儲存檢測結果供後續驗證使用
            self._last_detection_result = detection_result
            self._last_operation_success = True

            return detection_result

        except Exception as e:
            logger.error(f"✗ 按鈕檢測失敗: {e}")
            self._last_operation_success = False
            raise

    # ========== 已棄用的 Keyword（v4.0.0 移除） ==========
    # 以下 Keyword 已被 when_user_detects_button_light_state(save_debug_image=True) 取代
    # - When 用戶檢測第 "${button_id}" 按鈕的燈光狀態並儲存ROI圖像
    # - When 用戶檢測第 "${button_id}" 按鈕的燈光狀態並儲存完整圖像

    @keyword('Then 按鈕燈光應該為 "${expected_color}" 色')
    def then_button_light_should_be_color(self, expected_color: str) -> bool:
        """
        Then: 按鈕燈光應該為指定顏色

        預期結果：驗證視覺檢測結果符合預期顏色

        Args:
            expected_color: 預期顏色（blue/white/red/green/yellow/orange/purple/off）

        Returns:
            bool: 驗證是否通過

        Examples:
            | Then | 按鈕燈光應該為 "blue" 色 |
            | Then | 按鈕燈光應該為 "white" 色 |
            | Then | 按鈕燈光應該為 "red" 色 |
            | Then | 按鈕燈光應該為 "off" 色 |

        Raises:
            AssertionError: 如果檢測結果不符合預期
            RuntimeError: 如果沒有檢測結果可用
        """
        if not hasattr(self, '_last_detection_result'):
            raise RuntimeError("沒有可用的檢測結果。請先執行視覺檢測。")

        result = self._last_detection_result
        actual_color = result['color']

        if actual_color != expected_color:
            raise AssertionError(
                f"按鈕顏色不符合預期。\n"
                f"  預期: {expected_color}\n"
                f"  實際: {actual_color}\n"
                f"  亮度: {result.get('brightness_level', result.get('raw_brightness', 'N/A'))}%\n"
                f"  信心度: {result['confidence']:.2f}"
            )

        logger.info(f"✓ 按鈕顏色驗證通過: {expected_color} (信心度: {result['confidence']:.2f})")
        return True

    # ========== 已棄用的驗證 Keyword（v4.0.0 移除） ==========
    # Then 按鈕燈光應該為 "${expected_state}" 狀態（改用 Then 按鈕燈光應該為 "${expected_color}" 色）
    # 本機化版本使用 color="off" 來表示關閉狀態，不再使用 light="on/off"

    @keyword('When 用戶檢測多個按鈕的燈光狀態')
    def when_user_detects_multiple_buttons(self, button_ids: List[str]) -> List[Dict]:
        """
        When: 用戶檢測多個按鈕的燈光狀態

        執行動作：批次檢測多個按鈕的 LED 狀態

        Args:
            button_ids: 按鈕 ID 列表

        Returns:
            List[Dict]: 檢測結果列表

        Examples:
            | ${buttons}= | Create List | light1 | light2 | light3 |
            | When | 用戶檢測多個按鈕的燈光狀態 | ${buttons} |

        Raises:
            RuntimeError: 如果任一按鈕檢測失敗
        """
        results = []

        for button_id in button_ids:
            try:
                result = self.when_user_detects_button_light_state(button_id)
                results.append({
                    'button_id': button_id,
                    'result': result,
                    'success': True
                })
            except Exception as e:
                logger.error(f"檢測按鈕 {button_id} 失敗: {e}")
                results.append({
                    'button_id': button_id,
                    'error': str(e),
                    'success': False
                })

        # 儲存批次檢測結果
        self._last_batch_detection_results = results

        # 統計成功率
        total = len(results)
        success = sum(1 for r in results if r['success'])
        logger.info(f"批次檢測完成: {success}/{total} 成功")

        return results

    @keyword('When 用戶等待按鈕 "${button_id}" 變為 "${expected_color}" 色')
    def when_user_waits_for_button_color_change(self, button_id: str, expected_color: str,
                                                  timeout: int = 30, interval: float = 1.0) -> bool:
        """
        When: 用戶等待按鈕變為指定顏色

        執行動作：輪詢檢測按鈕狀態，直到達到預期顏色或超時

        Args:
            button_id: 按鈕 ID
            expected_color: 預期顏色（blue/white/off）
            timeout: 超時時間（秒），預設 30
            interval: 檢測間隔（秒），預設 1.0

        Returns:
            bool: 是否在超時前達到預期顏色

        Examples:
            | When | 用戶等待按鈕 "light1" 變為 "blue" 色 |
            | When | 用戶等待按鈕 "bluetooth" 變為 "white" 色 | 60 | 2.0 |

        Raises:
            TimeoutError: 如果超時仍未達到預期顏色
        """
        start_time = time.time()
        logger.info(f"開始等待按鈕 '{button_id}' 變為 '{expected_color}' 色 (超時: {timeout}秒)")

        while (time.time() - start_time) < timeout:
            try:
                result = self.when_user_detects_button_light_state(button_id)
                actual_color = result['color']

                if actual_color == expected_color:
                    elapsed = time.time() - start_time
                    logger.info(f"✓ 按鈕已變為 '{expected_color}' 色 (耗時: {elapsed:.1f}秒)")
                    return True

                logger.debug(f"當前顏色: {actual_color}, 繼續等待...")
                time.sleep(interval)

            except Exception as e:
                logger.warn(f"檢測過程出現錯誤: {e}, 繼續嘗試...")
                time.sleep(interval)

        # 超時
        elapsed = time.time() - start_time
        raise TimeoutError(
            f"超時 ({elapsed:.1f}秒)：按鈕 '{button_id}' 未變為 '{expected_color}' 色"
        )

    @keyword('When 用戶連接到機器手臂')
    def when_user_connects_to_robot_arm(self, host: str = "10.42.0.180", port: int = 9000):
        """
        When: 用戶連接到機器手臂（簡化版）

        執行動作：連接到指定的機器手臂伺服器

        Args:
            host: 伺服器 IP（預設 10.42.0.180）
            port: 伺服器端口（預設 9000）

        Example:
            | When | 用戶連接到機器手臂 | 10.42.0.180 | 9000 |
            | When | 用戶連接到機器手臂 |  # 使用預設值
        """
        return self.connect_robot_arm(host, port)

    @keyword('When 用戶中斷與機器手臂的連接')
    def when_user_disconnects_from_robot_arm(self):
        """
        When: 用戶中斷與機器手臂的連接（簡化版）

        執行動作：斷開與機器手臂的連接

        Example:
            | When | 用戶中斷與機器手臂的連接 |
        """
        return self.disconnect_robot_arm()

    @keyword('When 用戶按壓第 "${button_id}" 按鈕')
    def when_user_presses_button(self, button_id: str):
        """
        When: 用戶按壓指定按鈕

        執行動作：按壓指定 ID 的按鈕（使用配置中的預設參數）

        Args:
            button_id: 按鈕 ID（例如 light1, light2 等）

        Example:
            | When | 用戶按壓第 "light1" 按鈕 |
            | When | 用戶按壓第 "bluetooth" 按鈕 |

        Raises:
            ValueError: 如果按鈕 ID 不存在
        """
        return self._press_button(button_id)

    @keyword('When 用戶按壓第 "${button_id}" 按鈕持續 "${duration}" 秒')
    def when_user_presses_button_with_duration(self, button_id: str, duration: str):
        """
        When: 用戶按壓指定按鈕並持續指定時間

        執行動作：按壓指定 ID 的按鈕並保持指定時間

        Args:
            button_id: 按鈕 ID（例如 light1, light2 等）
            duration: 按壓持續時間（秒）

        Example:
            | When | 用戶按壓第 "light2" 按鈕持續 "0.5" 秒 |
            | When | 用戶按壓第 "power" 按鈕持續 "2.0" 秒 |

        Raises:
            ValueError: 如果按鈕 ID 不存在或時間格式錯誤
        """
        return self._press_button(button_id, custom_duration=float(duration))

    @keyword('Then 上一步操作應該成功')
    def then_last_operation_should_succeed(self) -> bool:
        """
        Then: 上一步操作應該成功（簡化版）

        預期結果：驗證最後一次操作成功

        Returns:
            bool: 驗證是否通過

        Example:
            | Then | 上一步操作應該成功 |

        Raises:
            AssertionError: 如果操作失敗
        """
        if not self._last_operation_success:
            raise AssertionError("最後一次操作失敗")

        logger.info("✓ 上一步操作成功")
        return True

    @keyword('取得最後檢測結果')
    def get_last_detection_result(self) -> dict:
        """
        取得最後一次視覺檢測結果

        Returns:
            dict: 包含 color, brightness, confidence 的檢測結果

        Example:
            | ${result}= | 取得最後檢測結果 |
            | Log | 顏色: ${result}[color] |
            | Log | 亮度: ${result}[brightness] |
            | Log | 信心度: ${result}[confidence] |

        Raises:
            RuntimeError: 如果沒有可用的檢測結果
        """
        if self._last_detection_result is None:
            raise RuntimeError("沒有可用的檢測結果。請先執行視覺檢測。")

        return self._last_detection_result

    @keyword('取得批次檢測結果')
    def get_batch_detection_results(self) -> List[Dict]:
        """
        取得最後一次批次檢測結果

        Returns:
            List[Dict]: 批次檢測結果列表

        Example:
            | ${results}= | 取得批次檢測結果 |
            | FOR | ${result} | IN | @{results} |
            |     | Log | ${result}[button_id]: ${result}[result][color] |
            | END |

        Raises:
            RuntimeError: 如果沒有可用的批次檢測結果
        """
        if self._last_batch_detection_results is None:
            raise RuntimeError("沒有可用的批次檢測結果。請先執行批次檢測。")

        return self._last_batch_detection_results

    # ==================== 新增關鍵字 - 面板觀測位置管理 ====================

    @keyword("移動到面板觀測位置")
    def move_to_panel_observation_position(self, button_id: str):
        """移動機器手臂到指定按鈕的面板觀測位置

        Args:
            button_id: 按鈕 ID（如 "light1", "light2" 等）

        Raises:
            RuntimeError: 機器手臂未連接或移動失敗
            ValueError: 按鈕不存在或沒有配置觀測角度

        Example:
            | 移動到面板觀測位置 | light2 |
        """
        self._ensure_connected()

        # 取得按鈕配置
        button_config = self._get_button_config(button_id)

        if "vision" not in button_config or "observe_angles" not in button_config["vision"]:
            raise ValueError(f"按鈕 '{button_id}' 沒有配置觀測角度")

        observe_angles = button_config["vision"]["observe_angles"]
        logger.info(f"🤖 移動到按鈕 '{button_id}' 的面板觀測位置: {observe_angles}")

        try:
            self.controller.send_angles(observe_angles, 30)  # 使用較慢速度確保精確定位
            self.controller.wait_for_movement()
            logger.info(f"✅ 已成功移動到面板觀測位置")
        except Exception as e:
            logger.error(f"❌ 移動到面板觀測位置失敗: {e}")
            raise RuntimeError(f"移動到面板觀測位置失敗: {e}")

    # ==================== 新增關鍵字 - 完整反饋結果比較 ====================

    @keyword("比較完整反饋結果")
    def compare_complete_feedback_results(self, before_panel: Dict, after_panel: Dict, 
                                        before_environment: Dict, after_environment: Dict):
        """比較面板LED和環境燈光的完整反饋結果

        Args:
            before_panel: 按壓前面板LED檢測結果
            after_panel: 按壓後面板LED檢測結果  
            before_environment: 按壓前環境燈光檢測結果
            after_environment: 按壓後環境燈光檢測結果

        Example:
            | 比較完整反饋結果 | ${before_panel_result} | ${after_panel_result} | ${before_env_result} | ${after_env_result} |
        """
        # 計算面板LED變化
        panel_color_changed = before_panel.get('color') != after_panel.get('color')
        panel_brightness_diff = after_panel.get('brightness', 0) - before_panel.get('brightness', 0)
        panel_brightness_change_percent = abs(panel_brightness_diff)

        # 計算環境燈光變化 - 安全地處理可能的字串值
        before_env_brightness = before_environment.get('brightness_level', 0)
        after_env_brightness = after_environment.get('brightness_level', 0)
        
        # 確保為數字類型
        if isinstance(before_env_brightness, str):
            try:
                before_env_brightness = float(before_env_brightness)
            except:
                before_env_brightness = 0
        if isinstance(after_env_brightness, str):
            try:
                after_env_brightness = float(after_env_brightness)
            except:
                after_env_brightness = 0
                
        env_brightness_diff = after_env_brightness - before_env_brightness
        env_brightness_change_percent = abs(env_brightness_diff)
        env_level_changed = before_environment.get('level') != after_environment.get('level')

        # 顯示詳細比較結果
        logger.console(f"\n{'=' * 80}")
        logger.console(f"🔍 完整按壓反饋結果分析")
        logger.console(f"{'=' * 80}")
        
        logger.console(f"\n📱 【面板LED狀態】")
        logger.console(f"   按壓前: 顏色={before_panel.get('color')}, 亮度={before_panel.get('brightness')}%, 信心度={before_panel.get('confidence')}")
        logger.console(f"   按壓後: 顏色={after_panel.get('color')}, 亮度={after_panel.get('brightness')}%, 信心度={after_panel.get('confidence')}")
        logger.console(f"   變化: 顏色變化={'是' if panel_color_changed else '否'}, 亮度變化={panel_brightness_diff}% (絕對值 {panel_brightness_change_percent:.2f}%)")
        
        logger.console(f"\n💡 【環境燈光狀態】")
        logger.console(f"   按壓前: 亮度={before_env_brightness}%, 等級={before_environment.get('level')}")
        logger.console(f"   按壓後: 亮度={after_env_brightness}%, 等級={after_environment.get('level')}")
        logger.console(f"   變化: 等級變化={'是' if env_level_changed else '否'}, 亮度變化={env_brightness_diff}% (絕對值 {env_brightness_change_percent:.2f}%)")

        # 綜合判斷
        logger.console(f"\n📊 【變化分析】")
        panel_significant_change = panel_color_changed or panel_brightness_change_percent > 20
        env_significant_change = env_level_changed or env_brightness_change_percent > 20
        
        if panel_significant_change and env_significant_change:
            logger.console(f"   ✅ 按壓效果: 面板LED和環境燈光都有顯著變化")
        elif panel_significant_change:
            logger.console(f"   🟡 按壓效果: 僅面板LED有顯著變化，環境燈光變化不明顯")
        elif env_significant_change:
            logger.console(f"   🟡 按壓效果: 僅環境燈光有顯著變化，面板LED變化不明顯")
        else:
            logger.console(f"   ⚠️  按壓效果: 面板LED和環境燈光變化都不明顯")

        logger.console(f"\n📸 【截圖統計】")
        logger.console(f"   預期產生圖像: 共8張")
        logger.console(f"   - Socket 完整圖片: 2張 (按壓前/後)")
        logger.console(f"   - Socket ROI 圖片: 2張 (按壓前/後)")
        logger.console(f"   - RTSP 完整圖片: 2張 (按壓前/後)")  
        logger.console(f"   - RTSP ROI 圖片: 2張 (按壓前/後)")
        logger.console(f"   圖片儲存位置: output/debug_images/")

        logger.console(f"{'=' * 80}\n")

        # 儲存結果到測試報告
        panel_summary = f"面板: {before_panel.get('color')} → {after_panel.get('color')} (亮度 {before_panel.get('brightness')}% → {after_panel.get('brightness')}%)"
        env_summary = f"環境: {before_environment.get('level')} → {after_environment.get('level')} (亮度 {before_env_brightness}% → {after_env_brightness}%)"
        
        from robot.api import logger as robot_logger
        robot_logger.info(f"完整反饋測試結果 | {panel_summary} | {env_summary}")

        # 設定測試訊息
        test_message = f"完整反饋: {panel_summary} | {env_summary}"
        try:
            from robot.libraries.BuiltIn import BuiltIn
            BuiltIn().set_test_message(test_message)
        except:
            pass  # 如果不在 Robot Framework 環境中執行，忽略錯誤


# 測試用例
if __name__ == "__main__":
    print("RobotArmKeywords 關鍵字庫 v3.0.0 - BDD 風格 + 視覺檢測")
    print("=" * 70)
    print("採用雙層架構設計（Voice Control 模式）")
    print("所有關鍵字遵循 Gherkin 語法（Given-When-Then-And）")
    print("=" * 70)
    print()

    # 列出所有關鍵字
    keywords_lib = RobotArmKeywords()

    print("📦 【連接管理關鍵字】(3個)")
    print("  1. 連接機器手臂")
    print("  2. 斷開機器手臂連接")
    print("  3. 回到初始位置")
    print()

    print("✅ 【BDD Given 關鍵字】(3個) - 前置條件驗證")
    print("  1. Given 機器手臂已正確連接到控制面板")
    print("  2. Given 控制面板電源狀態為 \"${power_state}\"")
    print("  3. Given 機器手臂系統處於待命狀態")
    print()

    print("⚡ 【BDD When 關鍵字】(10個) - 執行動作")
    print("  1. When 用戶透過機器手臂開啟第 \"${light_number}\" 號燈光")
    print("  2. When 用戶透過機器手臂切換藍牙連接")
    print("  3. When 用戶透過機器手臂啟動 \"${device_name}\" 設備")
    print("  4. When 用戶透過機器手臂長按 \"${button_type}\" 按鈕 \"${seconds}\" 秒")
    print("  5. When 用戶連接到機器手臂 [簡化版]")
    print("  6. When 用戶中斷與機器手臂的連接 [簡化版]")
    print("  7. When 用戶按壓第 \"${button_id}\" 按鈕 [簡化版]")
    print("  8. When 用戶檢測第 \"${button_id}\" 按鈕的燈光狀態 [視覺檢測]")
    print("  9. When 用戶檢測多個按鈕的燈光狀態 [視覺檢測]")
    print("  10. When 用戶等待按鈕 \"${button_id}\" 變為 \"${expected_color}\" 色 [視覺檢測]")
    print()

    print("🎯 【BDD Then 關鍵字】(5個) - 預期結果驗證")
    print("  1. Then 機器手臂操作應該成功完成")
    print("  2. Then 上一步操作應該成功 [簡化版]")
    print("  3. Then 控制面板應該顯示 \"${expected_state}\" 狀態")
    print("  4. Then 按鈕燈光應該為 \"${expected_color}\" 色 [視覺檢測]")
    print("  5. Then 按鈕燈光應該為 \"${expected_state}\" 狀態 [視覺檢測]")
    print()

    print("➕ 【BDD And 關鍵字】(3個) - 附加驗證")
    print("  1. And 機器手臂應該返回待命位置")
    print("  2. And 系統應該記錄完整操作歷程")
    print("  3. And 暫存檔案應該正確清理")
    print()

    print("🔧 【輔助關鍵字】(2個) - 結果存取")
    print("  1. 取得最後檢測結果")
    print("  2. 取得批次檢測結果")
    print()

    print("=" * 70)
    print("📊 關鍵字統計：")
    print("  - 傳統關鍵字: 3 個（連接管理）")
    print("  - BDD 關鍵字: 24 個（Given 3 + When 10 + Then 5 + And 3）")
    print("  - 簡化版關鍵字: 3 個（連接、斷開、按壓）")
    print("  - 輔助關鍵字: 2 個（取得檢測結果）")
    print("  - ✅ 總計: 26 個關鍵字")
    print("  - 🆕 Phase 3 新增: 10 個（5 個視覺檢測 BDD + 3 個簡化版 + 2 個輔助）")
    print("=" * 70)
    print()
    print("🔗 支援的設備名稱（When 用戶透過機器手臂啟動設備）：")
    print("  熱水器, 空調, 瓦斯, 水泵, 水箱加熱器, 門鎖, AUX1, AUX2, Select")
    print()
    print("💡 支援的按鈕類型（When 長按按鈕）：")
    print("  縮回, 伸展, Retract, Extend")
    print()
    print("👁️ 視覺檢測支援的顏色/狀態：")
    print("  顏色: blue, white, off")
    print("  狀態: on, off")
    print()
    print("=" * 70)
