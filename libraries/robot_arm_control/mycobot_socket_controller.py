"""
MyCobot Socket Controller - MyCobot 280 Socket 控制核心
基於 pymycobot 的 TCP/IP Socket 連接控制機器手臂
"""

import time
from typing import List, Optional
from loguru import logger

from pymycobot import MyCobot280Socket


class MyCobotSocketController:
    """
    MyCobot 280 Socket 控制器

    功能：
    - TCP/IP Socket 連接管理
    - 發送角度指令
    - 讀取當前狀態
    - 等待移動完成
    - 電源管理
    """

    def __init__(self, host: str, port: int = 9000, timeout: float = 10.0):
        """
        初始化 Socket 控制器

        Args:
            host: MyCobot 280 的 IP 地址
            port: Socket 端口，預設 9000
            timeout: 連接超時時間（秒）

        Raises:
            ImportError: 如果 pymycobot 未安裝
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.mc: Optional[MyCobot280Socket] = None
        self._connected = False

        logger.info(f"初始化 MyCobotSocketController: {host}:{port}")

    @property
    def socket(self):
        """
        取得底層 socket 對象（用於視覺檢測等自訂命令）

        Returns:
            socket.socket: 底層 TCP socket

        Raises:
            RuntimeError: 如果機器手臂未連接
        """
        if not self._connected or not self.mc:
            raise RuntimeError("機器手臂未連接，無法取得 socket")

        # pymycobot 的 MyCobot280Socket 內部有 sock 屬性
        if hasattr(self.mc, 'sock'):
            return self.mc.sock
        else:
            raise RuntimeError("pymycobot 對象沒有 sock 屬性，可能版本不相容")


    def connect(self) -> bool:
        """
        連接到機器手臂

        Returns:
            True 如果連接成功

        Raises:
            ConnectionError: 如果無法連接到機器手臂
            RuntimeError: 如果連接測試失敗
        """
        try:
            logger.info(f"正在連接到機器手臂 {self.host}:{self.port}...")
            self.mc = MyCobot280Socket(self.host, self.port)

            # 測試連接是否成功（嘗試讀取角度，增加重試機制）
            max_retries = 3
            for i in range(max_retries):
                logger.debug(f"連接測試，第 {i + 1}/{max_retries} 次嘗試讀取角度...")
                test_angles = self.mc.get_angles()

                # 檢查回傳值是否為有效的角度列表
                if isinstance(test_angles, list) and len(test_angles) == 6:
                    # 成功讀取，跳出循環
                    logger.info(f"✅ 成功讀取角度: {[f'{a:.2f}' for a in test_angles]}")
                    break
                elif test_angles == -1:
                    # 返回 -1 表示伺服馬達未上電，但連接正常
                    logger.warning(f"⚠️ 第 {i + 1} 次讀取角度返回 -1（伺服馬達可能未上電）")
                    # 先嘗試上電
                    logger.info("🔌 嘗試自動上電...")
                    self.mc.power_on()
                    time.sleep(1.5)  # 等待上電完成
                else:
                    logger.warning(f"⚠️ 第 {i + 1} 次讀取角度失敗，收到: {test_angles}。等待 1 秒後重試...")
                    time.sleep(1)
            else:
                # 如果重試多次後仍然失敗，但如果最後一次是 -1，則認為連接成功但未上電
                if test_angles == -1:
                    logger.warning(
                        f"⚠️ 連接成功但伺服馬達未上電 (收到 -1)。\n"
                        f"   將允許連接並可使用 power_on() 手動上電。"
                    )
                    self._connected = True
                    logger.info(f"✅ 已連接到機器手臂 {self.host}:{self.port}（未上電狀態）")
                    return True
                else:
                    # 其他錯誤情況
                    raise RuntimeError(
                        f"連接測試失敗: 重試 {max_retries} 次後仍無法讀取有效的角度資料。\n"
                        f"   最後收到的資料: {test_angles}\n"
                        f"請重點檢查:\n"
                        f"  1. MyCobot 280 Jetson Nano 上的 Server_280.py 是否正常運行且未卡住\n"
                        f"  2. 檢查 MyCobot 280 Jetson Nano 與機器手臂之間的 USB/序列埠連接\n"
                        f"  3. 嘗試重啟 MyCobot 280 Jetson Nano 上的 Server_280.py 腳本\n"
                        f"  4. 檢查網路連接是否正常"
                    )

            self._connected = True
            logger.info(f"✅ 成功連接到機器手臂 {self.host}:{self.port}")
            logger.info(f"   當前角度: {[f'{a:.2f}' for a in test_angles]}")
            return True

        except Exception as e:
            self._connected = False
            logger.error(f"❌ 連接失敗: {e}")
            raise ConnectionError(
                f"無法連接到機器手臂 {self.host}:{self.port}\n"
                f"錯誤: {e}\n"
                f"請確認:\n"
                f"  1. 機器手臂電源已開啟\n"
                f"  2. MyCobot 280 Jetson Nano Server_280.py 正在運行\n"
                f"  3. 網路連接正常\n"
                f"  4. IP 和端口配置正確"
            ) from e

    def disconnect(self) -> None:
        """斷開與機器手臂的連接"""
        if self.mc is not None:
            try:
                # pymycobot 的 Socket 連接會自動關閉
                logger.info(f"斷開與機器手臂的連接: {self.host}:{self.port}")
                self.mc = None
                self._connected = False
            except Exception as e:
                logger.error(f"斷開連接時發生錯誤: {e}")

    def is_connected(self) -> bool:
        """
        檢查是否已連接

        Returns:
            True 如果已連接，否則 False
        """
        return self._connected and self.mc is not None

    def send_angles(self, angles: List[float], speed: int) -> bool:
        """
        發送角度指令到機器手臂

        Args:
            angles: 6 個關節角度列表 [J1, J2, J3, J4, J5, J6]，單位：度
            speed: 移動速度 (1-100)

        Returns:
            True 如果指令發送成功

        Raises:
            RuntimeError: 如果機器手臂未連接
            ValueError: 如果參數無效
        """
        if not self.is_connected():
            raise RuntimeError("機器手臂未連接，無法發送角度指令")

        if len(angles) != 6:
            raise ValueError(f"角度數量錯誤: 期望 6 個，實際 {len(angles)} 個")

        if not (1 <= speed <= 100):
            raise ValueError(f"速度超出範圍: {speed}（應在 1-100 之間）")

        try:
            logger.debug(f"發送角度指令: {[f'{a:.2f}' for a in angles]}, 速度: {speed}")
            self.mc.send_angles(angles, speed)
            return True

        except Exception as e:
            logger.error(f"發送角度指令失敗: {e}")
            raise RuntimeError(f"發送角度指令失敗: {e}") from e

    def get_angles(self) -> List[float]:
        """
        讀取當前關節角度

        Returns:
            6 個關節角度列表

        Raises:
            RuntimeError: 如果機器手臂未連接或讀取失敗
        """
        if not self.is_connected():
            raise RuntimeError("機器手臂未連接，無法讀取角度")

        try:
            angles = self.mc.get_angles()
            # 檢查 angles 是否為列表或元組
            if angles is not None and isinstance(angles, (list, tuple)) and len(angles) == 6:
                return list(angles)
            else:
                raise RuntimeError(f"讀取到的角度數據異常: {angles} (type: {type(angles)})")

        except Exception as e:
            logger.error(f"讀取角度失敗: {e}")
            raise RuntimeError(f"讀取角度失敗: {e}") from e

    def is_moving(self) -> bool:
        """
        檢查機器手臂是否正在移動

        Returns:
            True 如果正在移動，否則 False

        Raises:
            RuntimeError: 如果檢查失敗
        """
        if not self.is_connected():
            return False

        try:
            # pymycobot 的 is_moving() 方法
            # 返回 1 表示正在移動，0 表示已停止
            moving_status = self.mc.is_moving()
            return bool(moving_status)

        except Exception as e:
            logger.error(f"檢查移動狀態失敗: {e}")
            raise RuntimeError(f"檢查移動狀態失敗: {e}") from e

    def wait_for_movement(self, timeout: float = 30.0, check_interval: float = 0.1) -> bool:
        """
        等待機器手臂移動完成

        Args:
            timeout: 最大等待時間（秒），預設 30 秒
            check_interval: 檢查間隔（秒），預設 0.1 秒

        Returns:
            True 如果在超時前停止，False 如果超時

        Raises:
            RuntimeError: 如果機器手臂未連接
        """
        if not self.is_connected():
            raise RuntimeError("機器手臂未連接，無法等待移動完成")

        start_time = time.time()
        logger.debug(f"等待機器手臂移動完成（超時: {timeout} 秒）...")

        while self.is_moving():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.warning(f"⚠️ 等待移動完成超時（{timeout} 秒）")
                return False

            time.sleep(check_interval)

        elapsed = time.time() - start_time
        logger.debug(f"✅ 移動完成（耗時: {elapsed:.2f} 秒）")
        return True

    def go_to_home(self, speed: int = 30) -> bool:
        """
        移動到初始位置 [0, 0, 0, 0, 0, 0]

        Args:
            speed: 移動速度 (1-100)，預設 30

        Returns:
            True 如果成功

        Raises:
            RuntimeError: 如果移動失敗
        """
        logger.info("移動到初始位置 [0, 0, 0, 0, 0, 0]...")
        home_position = [0, 0, 0, 0, 0, 0]

        self.send_angles(home_position, speed)

        # 等待移動完成
        if not self.wait_for_movement():
            raise RuntimeError("移動到初始位置超時")

        logger.info("✅ 已到達初始位置")
        return True

    def power_on(self) -> bool:
        """
        開啟伺服馬達電源

        Returns:
            True 如果成功

        Raises:
            RuntimeError: 如果機器手臂未連接或操作失敗
        """
        if not self.is_connected():
            raise RuntimeError("機器手臂未連接，無法開啟電源")

        try:
            logger.info("開啟伺服馬達電源...")
            self.mc.power_on()
            time.sleep(1)  # 等待電源穩定
            logger.info("✅ 伺服馬達電源已開啟")
            return True

        except Exception as e:
            logger.error(f"開啟電源失敗: {e}")
            raise RuntimeError(f"開啟電源失敗: {e}") from e

    def power_off(self) -> bool:
        """
        關閉伺服馬達電源

        Returns:
            True 如果成功

        Raises:
            RuntimeError: 如果機器手臂未連接或操作失敗
        """
        if not self.is_connected():
            raise RuntimeError("機器手臂未連接，無法關閉電源")

        try:
            logger.info("關閉伺服馬達電源...")
            self.mc.power_off()
            logger.info("✅ 伺服馬達電源已關閉")
            return True

        except Exception as e:
            logger.error(f"關閉電源失敗: {e}")
            raise RuntimeError(f"關閉電源失敗: {e}") from e

    def is_power_on(self) -> bool:
        """
        檢查伺服馬達電源狀態

        Returns:
            True 如果電源已開啟，否則 False

        Raises:
            RuntimeError: 如果檢查失敗
        """
        if not self.is_connected():
            return False

        try:
            # pymycobot 的 is_power_on() 方法
            # 返回 1 表示電源已開，0 表示電源關閉
            power_status = self.mc.is_power_on()
            return bool(power_status)

        except Exception as e:
            logger.error(f"檢查電源狀態失敗: {e}")
            raise RuntimeError(f"檢查電源狀態失敗: {e}") from e


# 簡單的使用範例和測試
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 將專案根目錄加入 sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))

    from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader

    print("MyCobotSocketController 測試")
    print("=" * 60)

    try:
        # 從配置文件讀取連接設定
        config_loader = ButtonConfigLoader()
        socket_config = config_loader.get_socket_config()

        HOST = socket_config['host']
        PORT = socket_config['port']

        print(f"從配置讀取: {HOST}:{PORT}")
        print(f"嘗試連接到機器手臂...")
        print()

        # 創建控制器
        controller = MyCobotSocketController(HOST, PORT)

        # 測試連接
        controller.connect()
        print("✅ 連接成功！")

        # 讀取當前角度
        angles = controller.get_angles()
        print(f"當前角度: {[f'{a:.2f}' for a in angles]}")

        # 檢查電源狀態
        if controller.is_power_on():
            print("電源狀態: 已開啟")
        else:
            print("電源狀態: 已關閉")
            print("正在開啟電源...")
            controller.power_on()

        # 斷開連接
        controller.disconnect()
        print("✅ 已斷開連接")

    except ConnectionError as e:
        print(f"❌ 連接錯誤:\n{e}")
    except RuntimeError as e:
        print(f"❌ 運行錯誤:\n{e}")
    except Exception as e:
        print(f"❌ 未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
