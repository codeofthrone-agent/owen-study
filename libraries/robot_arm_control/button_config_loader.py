"""
Button Config Loader - YAML 配置文件載入器
用於載入和管理 MyCobot 280 按鈕位置配置
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger


class ButtonConfigLoader:
    """
    按鈕配置載入器

    功能：
    - 從 YAML 文件載入按鈕配置
    - 驗證配置完整性
    - 提供配置查詢接口
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置載入器

        Args:
            config_path: YAML 配置文件路徑。如果為 None，使用預設路徑
        """
        if config_path is None:
            # 預設配置文件路徑
            project_root = Path(__file__).resolve().parent.parent.parent
            config_path = project_root / "config" / "robot_arm" / "taipei_lab_buttons.yaml"

        self.config_path = Path(config_path)
        self.config: Dict = {}
        self._load_config()

    def _load_config(self) -> None:
        """從 YAML 文件載入配置"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            logger.info(f"成功載入配置文件: {self.config_path}")
            self._validate_config()

        except yaml.YAMLError as e:
            logger.error(f"YAML 解析錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"載入配置文件失敗: {e}")
            raise

    def _validate_config(self) -> None:
        """驗證配置文件的完整性"""
        required_keys = ['connection', 'defaults', 'buttons']

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必要欄位: {key}")

        # 驗證連接配置
        if 'socket' not in self.config['connection']:
            raise ValueError("配置文件缺少 socket 連接配置")

        socket_config = self.config['connection']['socket']
        if 'host' not in socket_config or 'port' not in socket_config:
            raise ValueError("socket 連接配置缺少 host 或 port")

        # 驗證按鈕配置
        if not self.config['buttons']:
            raise ValueError("配置文件沒有定義任何按鈕")

        button_count = len(self.config['buttons'])
        logger.info(f"配置驗證通過，共 {button_count} 個按鈕")

    def get_button_config(self, button_id: str) -> Dict:
        """
        獲取指定按鈕的配置

        Args:
            button_id: 按鈕 ID (例如: 'bluetooth', 'light1', 'retract')

        Returns:
            按鈕配置字典，包含 name, description, down_angles, up_angles 等

        Raises:
            KeyError: 如果按鈕 ID 不存在
        """
        if button_id not in self.config['buttons']:
            available_buttons = ', '.join(self.config['buttons'].keys())
            raise KeyError(
                f"按鈕 ID '{button_id}' 不存在。"
                f"可用的按鈕: {available_buttons}"
            )

        button_config = self.config['buttons'][button_id].copy()

        # 合併預設值（如果按鈕配置中沒有指定）
        defaults = self.config['defaults']
        for key, value in defaults.items():
            if key not in button_config:
                button_config[key] = value

        return button_config

    def get_connection_config(self) -> Dict:
        """
        獲取連接配置

        Returns:
            連接配置字典，包含 socket 和 serial 配置
        """
        return self.config['connection']

    def get_socket_config(self) -> Dict:
        """
        獲取 Socket 連接配置

        Returns:
            Socket 配置字典 {'host': str, 'port': int}
        """
        return self.config['connection']['socket']

    def get_defaults(self) -> Dict:
        """
        獲取全局預設值

        Returns:
            預設配置字典
        """
        return self.config['defaults']

    def list_all_buttons(self) -> List[str]:
        """
        列出所有可用的按鈕 ID

        Returns:
            按鈕 ID 列表
        """
        return list(self.config['buttons'].keys())

    def get_button_info(self, button_id: str) -> Dict:
        """
        獲取按鈕的基本信息（不包含角度數據）

        Args:
            button_id: 按鈕 ID

        Returns:
            包含 name 和 description 的字典
        """
        config = self.get_button_config(button_id)
        return {
            'id': button_id,
            'name': config.get('name', button_id),
            'description': config.get('description', ''),
            'press_duration': config.get('press_duration', 1.0),
            'count': config.get('count', 1)
        }

    def is_long_press_button(self, button_id: str) -> bool:
        """
        判斷按鈕是否為長按按鈕

        Args:
            button_id: 按鈕 ID

        Returns:
            True 如果 press_duration >= 5 秒，否則 False
        """
        config = self.get_button_config(button_id)
        return config.get('press_duration', 1.0) >= 5.0

    def reload_config(self) -> None:
        """重新載入配置文件"""
        logger.info("重新載入配置文件...")
        self._load_config()


# 簡單的使用範例和測試
if __name__ == "__main__":
    try:
        # 初始化配置載入器
        loader = ButtonConfigLoader()

        # 測試獲取所有按鈕
        print(f"共有 {len(loader.list_all_buttons())} 個按鈕")
        print(f"按鈕列表: {', '.join(loader.list_all_buttons())}")
        print()

        # 測試獲取特定按鈕配置
        bluetooth_config = loader.get_button_config('bluetooth')
        print("藍牙按鈕配置:")
        print(f"  名稱: {bluetooth_config['name']}")
        print(f"  說明: {bluetooth_config['description']}")
        print(f"  按下角度: {bluetooth_config['down_angles']}")
        print(f"  抬起角度: {bluetooth_config['up_angles']}")
        print(f"  速度: {bluetooth_config['speed']}")
        print(f"  按壓時間: {bluetooth_config['press_duration']} 秒")
        print()

        # 測試獲取 Socket 配置
        socket_config = loader.get_socket_config()
        print("Socket 連接配置:")
        print(f"  主機: {socket_config['host']}")
        print(f"  端口: {socket_config['port']}")
        print()

        # 測試長按按鈕判斷
        print("長按按鈕檢測:")
        for button_id in ['bluetooth', 'retract', 'extend']:
            is_long_press = loader.is_long_press_button(button_id)
            button_info = loader.get_button_info(button_id)
            print(f"  {button_info['name']}: {'長按' if is_long_press else '點擊'} "
                  f"(按壓時間: {button_info['press_duration']} 秒)")

        print("\n✅ 配置載入器測試成功！")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
