"""
環境配置管理 (Environment Configuration Manager)

功能:
- 管理多環境配置（台北實驗室、桃園實驗室、RV Car）
- 提供環境切換介面
- 載入環境專屬配置
- 支援環境專屬 HSV 調整
- 支援多 IP Camera 配置（✨ v4.1.0 新增）
- 支援 RTSP 認證（✨ v4.2.0 新增）

作者: Robot Automation Team
日期: 2025-11-19
版本: v4.2.0

支援環境:
- taipei_lab: 台北實驗室（多 RTSP Camera + Socket 機器手臂）
- taoyuan_lab: 桃園實驗室（Socket 影像源）
- rv_car: RV Car 測試環境（Socket 影像源）

環境映射:
- taipei_lab ↔ laboratory (ipcam_config.yaml)
- rv_car ↔ rv_vehicle (ipcam_config.yaml)

Example:
    >>> from config.robot_arm.environment_config import EnvironmentConfig
    >>>
    >>> # 列出所有環境
    >>> envs = EnvironmentConfig.list_environments()
    >>> print(envs)
    ['taipei_lab', 'taoyuan_lab', 'rv_car']
    >>>
    >>> # 取得特定環境配置
    >>> config = EnvironmentConfig.get_environment("taipei_lab")
    >>> print(config["name"])
    '台北實驗室'
    >>>
    >>> # 取得環境的所有 Camera (✨ v4.1.0 新增)
    >>> cameras = EnvironmentConfig.get_cameras("taipei_lab")
    >>> print(len(cameras))  # 3 個 Camera
    3
"""

import copy
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from config.ipcam_config import get_all_cameras

# 載入 .env 檔案以取得 RTSP 認證資訊
load_dotenv()


class EnvironmentConfig:
    """環境配置管理

    管理多個測試環境的配置，包括影像源、機器手臂連接資訊、
    面板類型、按鈕配置檔案路徑等。

    Attributes:
        ENVIRONMENTS (dict): 所有環境配置的字典

    支援環境:
        - taipei_lab: 台北實驗室
        - taoyuan_lab: 桃園實驗室
        - rv_car: RV Car 測試環境

    Example:
        >>> config = EnvironmentConfig.get_environment("taipei_lab")
        >>> print(config["image_source"])
        'rtsp'
        >>> print(config["robot_arm_host"])
        '10.42.0.180'
    """

    # 環境名稱映射（對應 ipcam_config.yaml）
    ENVIRONMENT_MAPPING: Dict[str, Dict[str, str]] = {
        "taipei_lab": {
            "ipcam_env": "taipei_lab",
            "display_name": "台北實驗室",
            "location": "Taipei Laboratory"
        },
        "taoyuan_lab": {
            "ipcam_env": None,  # 桃園沒有 IP Camera
            "display_name": "桃園實驗室",
            "location": "Taoyuan Laboratory"
        },
        "rv_car": {
            "ipcam_env": "rv_car",
            "display_name": "RV Car 測試環境",
            "location": "RV Vehicle"
        }
    }

    ENVIRONMENTS: Dict[str, Dict[str, Any]] = {
        "taipei_lab": {
            "name": "台北實驗室",
            "ipcam_environment": "taipei_lab",  # ✨ 新增：對應 ipcam_config.yaml

            # ✨ 修改：支援多 Camera (動態從 ipcam_config 載入)
            "cameras": [],  # 移除硬編碼，改由 get_cameras 動態載入
            "default_camera": "level1",  # ✨ 新增：預設使用的 Camera

            # 機器手臂配置（使用 Socket 影像源）
            "image_source": "mixed",  # ✨ 修改：混合模式（RTSP + Socket）
            "robot_arm_host": "192.168.165.100",
            "robot_arm_port": 9000,
            "robot_arm_http_port": 8000,  # ✨ 新增：HTTP API Port
            "robot_arm_image_source": "http",  # Switched to http per user request

            "panel_types": ["3510a", "3611a", "3611c"],
            "button_config_path": "config/robot_arm/taipei_lab_buttons.yaml",
            "hsv_adjustments": {
                # 環境專屬 HSV 調整（台北實驗室光源特性）
                "blue": {
                    "lower": [95, 50, 50],
                    "upper": [135, 255, 255]
                }
            },
            "description": "台北實驗室，支援多 RTSP Camera 和 Socket 機器手臂影像源"
        },
        "taoyuan_lab": {
            "name": "桃園實驗室",
            "ipcam_environment": None,  # 無 IP Camera
            "cameras": [],  # 空列表
            "default_camera": None,

            "image_source": "http",  # ✨ 修改：使用 HTTP 影像源 (v4.2.0)
            "robot_arm_host": "192.168.1.100",
            "robot_arm_port": 9000,
            "robot_arm_http_port": 8000,
            "robot_arm_image_source": "http",

            "panel_types": ["3510a", "3611a"],
            "button_config_path": "config/robot_arm/taoyuan_lab_buttons.yaml",
            "hsv_adjustments": {},
            "description": "桃園實驗室，使用 Socket 影像源（從機器手臂 Server 請求影像）"
        },
        "rv_car": {
            "name": "RV Car 測試環境",
            "ipcam_environment": "rv_car",
            "cameras": [],  # TODO: 待補充 RV Car Camera 配置
            "default_camera": None,

            "image_source": "http",  # ✨ 修改：使用 HTTP 影像源 (v4.2.0)
            "robot_arm_host": "192.168.166.189",
            "robot_arm_port": 9000,
            "robot_arm_http_port": 8000,
            "robot_arm_image_source": "http",

            "panel_types": ["3611a", "3611c"],
            "button_config_path": "config/robot_arm/rv_car_buttons.yaml",
            "hsv_adjustments": {},
            "description": "RV Car 車載測試環境，使用 Socket 影像源"
        }
    }

    @staticmethod
    def get_environment(env_name: str) -> Dict[str, Any]:
        """取得環境配置

        Args:
            env_name: 環境名稱 ("taipei_lab" | "taoyuan_lab" | "rv_car")

        Returns:
            dict: 環境配置字典，包含以下欄位：
                - name (str): 環境顯示名稱
                - image_source (str): 影像源類型 ("rtsp" | "socket")
                - rtsp_url (str): RTSP URL（僅 RTSP 影像源）
                - robot_arm_host (str): 機器手臂主機位址
                - robot_arm_port (int): 機器手臂端口
                - panel_types (list): 支援的面板類型
                - button_config_path (str): 按鈕配置檔案路徑
                - hsv_adjustments (dict): HSV 調整參數（選填）
                - description (str): 環境描述

        Raises:
            ValueError: 未知環境名稱

        Example:
            >>> config = EnvironmentConfig.get_environment("taipei_lab")
            >>> print(config["name"])
            '台北實驗室'
            >>> print(config["image_source"])
            'rtsp'
            >>> print(config["panel_types"])
            ['3510a', '3611a', '3611c']
        """
        if env_name not in EnvironmentConfig.ENVIRONMENTS:
            available = ", ".join(EnvironmentConfig.ENVIRONMENTS.keys())
            raise ValueError(
                f"未知環境: {env_name}\n"
                f"可用環境: {available}"
            )

        # 返回深拷貝，避免外部修改影響原始配置
        return copy.deepcopy(EnvironmentConfig.ENVIRONMENTS[env_name])

    @staticmethod
    def list_environments() -> List[str]:
        """列出所有環境名稱

        Returns:
            list[str]: 環境名稱列表

        Example:
            >>> envs = EnvironmentConfig.list_environments()
            >>> print(envs)
            ['taipei_lab', 'taoyuan_lab', 'rv_car']
        """
        return list(EnvironmentConfig.ENVIRONMENTS.keys())

    @staticmethod
    def validate_environment(env_name: str) -> bool:
        """驗證環境是否存在

        Args:
            env_name: 環境名稱

        Returns:
            bool: 環境是否存在

        Example:
            >>> if EnvironmentConfig.validate_environment("taipei_lab"):
            ...     print("環境存在")
            環境存在
            >>> EnvironmentConfig.validate_environment("unknown")
            False
        """
        return env_name in EnvironmentConfig.ENVIRONMENTS

    @staticmethod
    def get_cameras(env_name: str) -> List[Dict[str, Any]]:
        """取得環境的所有 Camera 配置 (✨ v4.1.0 新增, v4.2.0 支援認證)

        Args:
            env_name: 環境名稱

        Returns:
            list[dict]: Camera 配置列表，每個 Camera 包含：
                - id (str): Camera 識別碼
                - ip (str): IP 地址
                - port (int): 端口
                - protocol (str): 協議 (rtsp)
                - stream_path (str): 串流路徑
                - transport (str): 傳輸協議 (udp/tcp)
                - rtsp_url (str): 完整 RTSP URL（✨ v4.2.0 包含認證資訊）
                - description (str): 描述
                - purpose (str): 用途

        Example:
            >>> cameras = EnvironmentConfig.get_cameras("taipei_lab")
            >>> print(len(cameras))
            3
            >>> print(cameras[0]["id"])
            'level1'
            >>> print(cameras[0]["rtsp_url"])
            'rtsp://thortron_qa:WHtYpiU6lh_McQf@192.168.165.184:554/live0'
        """
        # ✨ v4.2.0: 改從 ipcam_config 動態載入
        env_config = EnvironmentConfig.get_environment(env_name)
        ipcam_env = env_config.get("ipcam_environment")
        cameras = []

        if ipcam_env:
            try:
                # 從 ipcam_config 取得配置字典
                cam_dict = get_all_cameras(ipcam_env)
                
                # 轉換為列表格式並加入 id
                for cam_id, cam_data in cam_dict.items():
                    cam_copy = copy.deepcopy(cam_data)
                    cam_copy["id"] = cam_id
                    
                    # 確保有 rtsp_url (如果 ipcam_config 沒提供，這裡構建)
                    # ipcam_config.yaml 通常只有 ip, port, stream_path
                    # 我們需要構建完整的 rtsp_url
                    
                    ip = cam_copy.get("ip")
                    port = cam_copy.get("port", 554)
                    stream_path = cam_copy.get("stream_path", "/live0")
                    protocol = cam_copy.get("protocol", "rtsp")
                    transport = cam_copy.get("transport", "tcp")  # 預設 TCP，但 ipcam_config 可覆蓋為 udp
                    
                    # 處理路徑開頭的斜線
                    if stream_path and not stream_path.startswith("/"):
                        stream_path = f"/{stream_path}"
                        
                    # 取得認證資訊 (優先使用 YAML 中的，否則使用環境變數)
                    username = cam_copy.get("username") or os.getenv("IPCAM_USERNAME", "")
                    password = cam_copy.get("password") or os.getenv("IPCAM_PASSWORD", "")
                    
                    if protocol == "rtsp":
                        if username and password:
                            cam_copy["rtsp_url"] = f"rtsp://{username}:{password}@{ip}:{port}{stream_path}"
                        else:
                            cam_copy["rtsp_url"] = f"rtsp://{ip}:{port}{stream_path}"
                    
                    cameras.append(cam_copy)
                    
            except ValueError:
                # 環境不存在於 ipcam_config，保持空列表
                pass
        
        # 如果 ipcam_config 沒找到，嘗試使用 env_config 中的（相容性保留，雖然我們清空了）
        if not cameras:
            cameras = copy.deepcopy(env_config.get("cameras", []))

        return cameras

    @staticmethod
    def get_camera(env_name: str, camera_id: str) -> Dict[str, Any]:
        """取得特定 Camera 配置 (✨ v4.1.0 新增)

        Args:
            env_name: 環境名稱
            camera_id: Camera 識別碼 (level1, level2, motor 等)

        Returns:
            dict: Camera 配置

        Raises:
            ValueError: Camera 不存在

        Example:
            >>> camera = EnvironmentConfig.get_camera("taipei_lab", "level1")
            >>> print(camera["rtsp_url"])
            'rtsp://192.168.165.184:554/live0'
        """
        cameras = EnvironmentConfig.get_cameras(env_name)

        for camera in cameras:
            if camera["id"] == camera_id:
                return copy.deepcopy(camera)

        available_ids = [cam["id"] for cam in cameras]
        raise ValueError(
            f"Camera '{camera_id}' 不存在於環境 '{env_name}'\n"
            f"可用 Camera: {', '.join(available_ids) if available_ids else '無'}"
        )

    @staticmethod
    def get_default_camera(env_name: str) -> Optional[Dict[str, Any]]:
        """取得環境的預設 Camera (✨ v4.1.0 新增)

        Args:
            env_name: 環境名稱

        Returns:
            dict | None: 預設 Camera 配置，如果沒有 Camera 則返回 None

        Example:
            >>> camera = EnvironmentConfig.get_default_camera("taipei_lab")
            >>> print(camera["id"])
            'level1'
        """
        env_config = EnvironmentConfig.get_environment(env_name)
        default_id = env_config.get("default_camera")

        if default_id is None:
            cameras = env_config.get("cameras", [])
            return copy.deepcopy(cameras[0]) if cameras else None

        return EnvironmentConfig.get_camera(env_name, default_id)

    @staticmethod
    def get_image_source_config(env_name: str, camera_id: Optional[str] = None) -> Dict[str, Any]:
        """取得環境的影像源配置 (✨ v4.1.0 更新)

        根據環境類型返回對應的影像源配置，可直接用於 ImageSourceManager。

        Args:
            env_name: 環境名稱
            camera_id: Camera 識別碼 (可選，用於多 Camera 環境)

        Returns:
            dict: 影像源配置字典，格式依影像源類型而定：
                - RTSP: {"type": "rtsp", "url": "rtsp://...", "timeout": 10, "transport": "udp"}
                - Socket: {"type": "socket", "host": "...", "port": 9000, "num_frames": 5}
                - HTTP: {"type": "http", "host": "...", "port": 8000, "num_frames": 5}

        Raises:
            ValueError: 未知環境名稱或 Camera 不存在

        Example:
            >>> # 取得預設 Camera (taipei_lab)
            >>> config = EnvironmentConfig.get_image_source_config("taipei_lab")
            >>> print(config)
            {'type': 'rtsp', 'url': 'rtsp://192.168.165.184:554/live0', 'timeout': 10}
            >>>
            >>> # 取得特定 Camera
            >>> config = EnvironmentConfig.get_image_source_config("taipei_lab", "level2")
            >>> print(config["url"])
            'rtsp://192.168.165.127:554/live0'
            >>>
            >>> # Socket 影像源 (taoyuan_lab)
            >>> config = EnvironmentConfig.get_image_source_config("taoyuan_lab")
            >>> print(config)
            {'type': 'socket', 'host': '192.168.1.100', 'port': 9000, 'num_frames': 5}
        """
        env_config = EnvironmentConfig.get_environment(env_name)

        # 優先順序：
        # 1. 如果明確指定了 Camera ID，使用該 Camera 的 RTSP
        # 2. 如果未指定 Camera ID：
        #    - 對於混合模式環境（taipei_lab），預設使用 Socket（控制面板按鈕檢測）
        #    - 對於純 RTSP 環境，使用預設 Camera
        #    - 對於純 Socket 環境（taoyuan_lab, rv_car），使用 Socket

        # 如果明確指定了 Camera ID，使用該 RTSP Camera
        if camera_id is not None:
            camera = EnvironmentConfig.get_camera(env_name, camera_id)
            if camera is not None:
                return {
                    "type": "rtsp",
                    "url": camera["rtsp_url"],
                    "url": camera["rtsp_url"],
                    "timeout": 10,
                    "transport": camera.get("transport", "tcp"),
                    "camera_id": camera["id"],
                    "description": camera.get("description", "")
                }

        # 未指定 Camera ID 的情況
        image_source = env_config.get("image_source")

        # 混合模式：預設使用 Robot Arm Image Source（用於控制面板按鈕檢測）
        # 純 Socket/HTTP 模式：使用 Robot Arm Image Source
        if image_source in ["mixed", "socket", "http"]:
            arm_source = env_config.get("robot_arm_image_source", "socket")
            
            if arm_source == "http":
                return {
                    "type": "http",
                    "host": env_config["robot_arm_host"],
                    "port": env_config.get("robot_arm_http_port", 8000),
                    "num_frames": 5
                }
            else:
                return {
                    "type": "socket",
                    "host": env_config["robot_arm_host"],
                    "port": env_config["robot_arm_port"],
                    "num_frames": 5
                }

        # 純 RTSP 模式：使用預設 Camera
        camera = EnvironmentConfig.get_default_camera(env_name)
        if camera is not None:
            return {
                "type": "rtsp",
                "url": camera["rtsp_url"],
                "url": camera["rtsp_url"],
                "timeout": 10,
                "transport": camera.get("transport", "tcp"),
                "camera_id": camera["id"],
                "description": camera.get("description", "")
            }

        # 回退：使用 Socket (或 HTTP 如果配置了)
        arm_source = env_config.get("robot_arm_image_source", "socket")
        if arm_source == "http":
            return {
                "type": "http",
                "host": env_config["robot_arm_host"],
                "port": env_config.get("robot_arm_http_port", 8000),
                "num_frames": 5
            }
        else:
            return {
                "type": "socket",
                "host": env_config["robot_arm_host"],
                "port": env_config["robot_arm_port"],
                "num_frames": 5
            }


if __name__ == "__main__":
    # 簡單測試
    print("=== 測試 EnvironmentConfig v4.1.0 ===\n")

    # 測試列出所有環境
    print("所有環境:")
    for env in EnvironmentConfig.list_environments():
        print(f"  - {env}")

    print("\n" + "=" * 50 + "\n")

    # 測試取得每個環境配置
    for env_name in EnvironmentConfig.list_environments():
        config = EnvironmentConfig.get_environment(env_name)
        print(f"環境: {env_name}")
        print(f"  名稱: {config['name']}")
        print(f"  影像源: {config['image_source']}")
        print(f"  機器手臂: {config['robot_arm_host']}:{config['robot_arm_port']}")
        print(f"  面板類型: {', '.join(config['panel_types'])}")
        print(f"  配置檔案: {config['button_config_path']}")
        print(f"  描述: {config['description']}")

        # ✨ 測試取得 Camera 列表
        cameras = EnvironmentConfig.get_cameras(env_name)
        if cameras:
            print(f"  Cameras: {len(cameras)} 個")
            for cam in cameras:
                print(f"    - {cam['id']}: {cam['description']} ({cam['rtsp_url']})")

            # 測試取得預設 Camera
            default_cam = EnvironmentConfig.get_default_camera(env_name)
            if default_cam:
                print(f"  預設 Camera: {default_cam['id']}")
        else:
            print(f"  Cameras: 無")

        # 測試取得影像源配置（預設）
        img_config = EnvironmentConfig.get_image_source_config(env_name)
        print(f"  預設影像源: {img_config['type']}")
        if img_config['type'] == 'rtsp':
            print(f"    RTSP URL: {img_config['url']}")
        else:
            print(f"    Socket: {img_config['host']}:{img_config['port']}")

        print()

    # ✨ 測試多 Camera 存取
    print("=" * 50)
    print("\n=== 測試多 Camera 存取 ===\n")

    if EnvironmentConfig.get_cameras("taipei_lab"):
        print("taipei_lab Camera 列表:")
        for cam in EnvironmentConfig.get_cameras("taipei_lab"):
            print(f"  - {cam['id']}: {cam.get('purpose', 'N/A')}")

        # 測試取得特定 Camera
        print("\n取得 level2 Camera:")
        level2 = EnvironmentConfig.get_camera("taipei_lab", "level2")
        print(f"  URL: {level2['rtsp_url']}")
        print(f"  用途: {level2.get('purpose', 'N/A')}")

        # 測試取得影像源配置（指定 Camera）
        print("\n取得 motor Camera 的影像源配置:")
        motor_config = EnvironmentConfig.get_image_source_config("taipei_lab", "motor")
        print(f"  Type: {motor_config['type']}")
        print(f"  URL: {motor_config['url']}")
        print(f"  Camera ID: {motor_config['camera_id']}")

    print("\n" + "=" * 50)
    print("✅ EnvironmentConfig v4.1.0 測試通過")
