"""
Robot Arm Keywords - MyCobot 280 Robot Framework 關鍵字庫
採用 BDD (Gherkin) 風格，提供機器手臂控制的完整測試關鍵字
"""

import time
import sys
import socket
import json
from pathlib import Path
from typing import Optional, Dict, List
from robot.api import logger
from robot.api.deco import keyword

# 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.robot_arm_control.RobotArmKeywords
# 2. 作為檔案匯入: Library    ../../libraries/robot_arm_control/RobotArmKeywords.py
try:
    # 方式 1: 絕對匯入（作為模組）
    from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader
    from libraries.robot_arm_control.mycobot_socket_controller import MyCobotSocketController
except ImportError:
    # 方式 2: 將當前目錄加入 sys.path，然後直接匯入
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from button_config_loader import ButtonConfigLoader
    from mycobot_socket_controller import MyCobotSocketController


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
    ROBOT_LIBRARY_VERSION = '3.0.0'  # v3.0.0: 新增視覺檢測關鍵字

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
        config = self.config_loader.get_button_config(button_id)
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
    def when_user_detects_button_light_state(self, button_id: str) -> dict:
        """
        When: 用戶檢測指定按鈕的燈光狀態（使用視覺檢測）

        執行動作：透過機器手臂末端攝影機檢測按鈕的 LED 狀態

        Args:
            button_id: 按鈕 ID（例如：light1, bluetooth, door_lock）

        Returns:
            dict: 檢測結果
                {
                    "light": "on" | "off",
                    "color": "blue" | "white" | "off",
                    "brightness": 0-255,
                    "confidence": 0.0-1.0
                }

        Examples:
            | When | 用戶檢測第 "light1" 按鈕的燈光狀態 |
            | When | 用戶檢測第 "bluetooth" 按鈕的燈光狀態 |

        Raises:
            RuntimeError: 如果機器手臂未連接或檢測失敗
            ValueError: 如果按鈕 ID 不存在或未校準
        """
        try:
            # 獲取按鈕配置
            button_config = self.config_loader.get_button_config(button_id)

            # 檢查是否有視覺配置
            if 'vision' not in button_config:
                raise ValueError(f"按鈕 '{button_id}' 未校準視覺檢測 ROI。請先執行 calibrate_button_roi.py")

            vision_config = button_config['vision']

            # 準備檢測命令
            command = {
                "command": "detect_button",
                "roi": vision_config['roi'],
                "observe_angles": vision_config.get('observe_angles'),
                "num_frames": 5
            }

            logger.info(f"開始檢測按鈕: {button_config.get('name', button_id)}")

            # 發送命令並接收結果
            result = self._send_vision_command(command)

            if result.get("status") != "success":
                raise RuntimeError(f"檢測失敗: {result.get('message')}")

            detection_result = result['result']
            logger.info(f"✓ 檢測完成 - 燈光: {detection_result['light']}, "
                       f"顏色: {detection_result['color']}, "
                       f"亮度: {detection_result['brightness']}, "
                       f"信心度: {detection_result['confidence']:.2f}")

            # 儲存檢測結果供後續驗證使用
            self._last_detection_result = detection_result
            self._last_operation_success = True

            return detection_result

        except Exception as e:
            logger.error(f"✗ 按鈕檢測失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword('When 用戶檢測第 "${button_id}" 按鈕的燈光狀態並儲存ROI圖像')
    def when_user_detects_button_light_state_and_save_roi(self, button_id: str) -> dict:
        """
        When: 用戶檢測指定按鈕的燈光狀態，並儲存 ROI 圖像以供除錯

        執行動作：與「用戶檢測第...」相同，但會額外儲存 ROI 圖像

        Args:
            button_id: 按鈕 ID

        Returns:
            dict: 檢測結果

        Examples:
            | When | 用戶檢測第 "light1" 按鈕的燈光狀態並儲存ROI圖像 |

        Raises:
            RuntimeError: 如果檢測失敗
        """
        try:
            button_config = self.config_loader.get_button_config(button_id)
            if 'vision' not in button_config:
                raise ValueError(f"按鈕 '{button_id}' 未校準視覺檢測 ROI。")

            vision_config = button_config['vision']

            command = {
                "command": "detect_button",
                "roi": vision_config['roi'],
                "observe_angles": vision_config.get('observe_angles'),
                "num_frames": 5,
                "save_roi": True,
                "button_name": button_id
            }

            logger.info(f"開始檢測按鈕 (儲存ROI): {button_config.get('name', button_id)}")
            result = self._send_vision_command(command)

            if result.get("status") != "success":
                raise RuntimeError(f"檢測失敗: {result.get('message')}")

            detection_result = result['result']
            logger.info(f"✓ 檢測完成 - 燈光: {detection_result['light']}, "
                       f"顏色: {detection_result['color']}")

            self._last_detection_result = detection_result
            self._last_operation_success = True
            return detection_result

        except Exception as e:
            logger.error(f"✗ 按鈕檢測 (儲存ROI) 失敗: {e}")
            self._last_operation_success = False
            raise


    @keyword('When 用戶檢測第 "${button_id}" 按鈕的燈光狀態並儲存完整圖像')
    def when_user_detects_button_light_state_and_save_full_frame(self, button_id: str) -> dict:
        """
        When: 用戶檢測按鈕狀態，並儲存 ROI 和完整的除錯圖像

        執行動作：最強大的除錯模式，儲存 ROI 和標記了 ROI 的完整畫面

        Args:
            button_id: 按鈕 ID

        Returns:
            dict: 檢測結果
        """
        try:
            button_config = self.config_loader.get_button_config(button_id)
            if 'vision' not in button_config:
                raise ValueError(f"按鈕 '{button_id}' 未校準視覺檢測 ROI。")

            vision_config = button_config['vision']

            command = {
                "command": "detect_button",
                "roi": vision_config['roi'],
                "observe_angles": vision_config.get('observe_angles'),
                "num_frames": 5,
                "save_roi": True,
                "save_full_frame": True,
                "button_name": button_id
            }

            logger.info(f"開始檢測按鈕 (儲存完整圖像): {button_config.get('name', button_id)}")
            result = self._send_vision_command(command)

            if result.get("status") != "success":
                raise RuntimeError(f"檢測失敗: {result.get('message')}")

            detection_result = result['result']
            logger.info(f"✓ 檢測完成 - 燈光: {detection_result['light']}, "
                       f"顏色: {detection_result['color']}")

            self._last_detection_result = detection_result
            self._last_operation_success = True
            return detection_result

        except Exception as e:
            logger.error(f"✗ 按鈕檢測 (儲存完整圖像) 失敗: {e}")
            self._last_operation_success = False
            raise

    @keyword('Then 按鈕燈光應該為 "${expected_color}" 色')
    def then_button_light_should_be_color(self, expected_color: str) -> bool:
        """
        Then: 按鈕燈光應該為指定顏色

        預期結果：驗證視覺檢測結果符合預期顏色

        Args:
            expected_color: 預期顏色（blue/white/off）

        Returns:
            bool: 驗證是否通過

        Examples:
            | Then | 按鈕燈光應該為 "blue" 色 |
            | Then | 按鈕燈光應該為 "white" 色 |
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
                f"  亮度: {result['brightness']}\n"
                f"  信心度: {result['confidence']:.2f}"
            )

        logger.info(f"✓ 按鈕顏色驗證通過: {expected_color} (信心度: {result['confidence']:.2f})")
        return True

    @keyword('Then 按鈕燈光應該為 "${expected_state}" 狀態')
    def then_button_light_should_be_state(self, expected_state: str) -> bool:
        """
        Then: 按鈕燈光應該為指定狀態

        預期結果：驗證按鈕燈光開啟或關閉狀態

        Args:
            expected_state: 預期狀態（on/off）

        Returns:
            bool: 驗證是否通過

        Examples:
            | Then | 按鈕燈光應該為 "on" 狀態 |
            | Then | 按鈕燈光應該為 "off" 狀態 |

        Raises:
            AssertionError: 如果檢測結果不符合預期
            RuntimeError: 如果沒有檢測結果可用
        """
        if not hasattr(self, '_last_detection_result'):
            raise RuntimeError("沒有可用的檢測結果。請先執行視覺檢測。")

        result = self._last_detection_result
        actual_state = result['light']

        if actual_state != expected_state:
            raise AssertionError(
                f"按鈕狀態不符合預期。\n"
                f"  預期: {expected_state}\n"
                f"  實際: {actual_state}\n"
                f"  顏色: {result['color']}\n"
                f"  亮度: {result['brightness']}"
            )

        logger.info(f"✓ 按鈕狀態驗證通過: {expected_state}")
        return True

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
