"""Android 環境設定與裝置管理工具。

Stage 4 需求：
- ADB 設定與健康檢查
- 已連接裝置自動偵測（透過 `adb devices`）
- Appium `--relaxed-security` 啟動參數驗證
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


class ADBCommandError(RuntimeError):
    """當 `adb` 指令執行失敗時拋出的錯誤。"""


def _resolve_adb_path() -> str:
    """決定應使用的 adb 執行檔路徑。"""

    env_path = os.getenv("ADB_PATH")
    if env_path:
        return env_path
    which_result = shutil.which("adb")
    if which_result:
        return which_result
    # 預設回退至 `adb`，讓 subprocess 交給 PATH
    return "adb"


@dataclass
class AndroidDevice:
    """Android 裝置資訊。"""

    serial: str
    status: str
    model: str = "Unknown"
    android_version: str = "Unknown"
    device_name: str = "Unknown"


class AndroidDeviceManager:
    """負責管理已連接的 Android 裝置與 ADB 指令。"""

    def __init__(self, adb_path: Optional[str] = None, timeout: int = 10):
        self.adb_path = adb_path or _resolve_adb_path()
        self.timeout = timeout
        self._cached_devices: List[AndroidDevice] = []

    # ------------------------------------------------------------------
    # ADB 相關
    # ------------------------------------------------------------------

    def ensure_adb_available(self) -> bool:
        """檢查 adb 是否可用，若不可用則回傳 False。"""

        try:
            result = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_adb(self, *args: str) -> subprocess.CompletedProcess[str]:
        """執行 adb 指令並回傳結果。"""

        if not self.ensure_adb_available():
            raise ADBCommandError("adb 不可用，請確認已安裝並設定 PATH/ADB_PATH")
        cmd = [self.adb_path, *args]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:  # pragma: no cover - 需實機
            raise ADBCommandError(f"ADB 指令逾時: {' '.join(cmd)}") from exc
        if result.returncode != 0:
            raise ADBCommandError(
                f"ADB 指令失敗: {' '.join(cmd)}\nSTDERR: {result.stderr.strip()}"
            )
        return result

    # ------------------------------------------------------------------
    # 裝置偵測
    # ------------------------------------------------------------------

    def list_connected_devices(self) -> List[AndroidDevice]:
        """透過 `adb devices` 取得所有連線裝置。"""

        try:
            result = self._run_adb("devices", "-l")
        except ADBCommandError:
            return []

        devices: List[AndroidDevice] = []
        for line in result.stdout.splitlines()[1:]:  # 第一行是 header
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            serial, status = parts[0], parts[1]
            model = "Unknown"
            device_name = serial
            version = "Unknown"
            for token in parts[2:]:
                if token.startswith("model:"):
                    model = token.split(":", 1)[1]
                elif token.startswith("device:"):
                    device_name = token.split(":", 1)[1]
                elif token.startswith("transport_id"):
                    continue
            # 嘗試取得 Android 版本
            if status == "device":
                version = self.get_prop(serial, "ro.build.version.release") or "Unknown"
            devices.append(
                AndroidDevice(
                    serial=serial,
                    status=status,
                    model=model,
                    device_name=device_name,
                    android_version=version,
                )
            )
        self._cached_devices = devices
        return devices

    def get_primary_device(self) -> Optional[AndroidDevice]:
        """回傳第一個可用裝置。"""

        devices = self.list_connected_devices()
        return devices[0] if devices else None

    def wait_for_device(self, timeout: int = 60) -> bool:
        """等待至少一台裝置連線。"""

        start = time.time()
        while time.time() - start < timeout:
            if self.list_connected_devices():
                return True
            time.sleep(2)
        return False

    def get_prop(self, serial: str, prop: str) -> str:
        """取得指定裝置的系統屬性。"""

        try:
            result = self._run_adb("-s", serial, "shell", "getprop", prop)
            return result.stdout.strip()
        except ADBCommandError:
            return ""

    # ------------------------------------------------------------------
    # Appium relaxed security 驗證
    # ------------------------------------------------------------------

    @staticmethod
    def is_relaxed_security_enabled() -> bool:
        """檢查目前環境變數是否已啟用 --relaxed-security。"""

        explicit_flag = os.getenv("APPIUM_RELAXED_SECURITY")
        if explicit_flag and explicit_flag.lower() in {"1", "true", "yes"}:
            return True

        additional = os.getenv("APPIUM_SERVER_FLAGS", "")
        if "--relaxed-security" in additional:
            return True

        return False

    @staticmethod
    def validate_relaxed_security() -> None:
        """若尚未啟用 relaxed security，給予明確警告。"""

        if not AndroidDeviceManager.is_relaxed_security_enabled():
            warning = (
                "警告: Appium 需以 --relaxed-security 啟動才能使用 `mobile: shell`"
            )
            print(warning)


# ----------------------------------------------------------------------
# 模組級便利函式
# ----------------------------------------------------------------------

android_device_manager = AndroidDeviceManager()


def get_android_capabilities() -> Dict[str, str]:
    """提供基礎 Android 能力設定（可由 AppiumConfig 覆用）。"""

    return {
        'platformName': 'Android',
        'automationName': 'UiAutomator2',
        'deviceName': os.getenv('ANDROID_DEVICE_NAME', 'Android Device'),
        'platformVersion': os.getenv('ANDROID_PLATFORM_VERSION', '13'),
        'appPackage': os.getenv('ANDROID_APP_PACKAGE', ''),
        'appActivity': os.getenv('ANDROID_APP_ACTIVITY', ''),
        'udid': os.getenv('ANDROID_UDID', ''),
        'newCommandTimeout': int(os.getenv('ANDROID_CMD_TIMEOUT', '60')),
        'autoGrantPermissions': True,
        'noReset': os.getenv('ANDROID_NO_RESET', 'false').lower() == 'true',
    }


def summarize_environment() -> Dict[str, Optional[str]]:
    """回傳 Android 測試環境摘要，方便紀錄或除錯。"""

    primary = android_device_manager.get_primary_device()
    return {
        'adb_path': android_device_manager.adb_path,
        'relaxed_security': str(AndroidDeviceManager.is_relaxed_security_enabled()),
        'primary_device': primary.serial if primary else None,
        'primary_model': primary.model if primary else None,
    }
