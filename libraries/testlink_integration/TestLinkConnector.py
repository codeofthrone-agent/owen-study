"""
TestLink Connector - Robot Framework Library
============================================

提供 TestLink 整合的高階介面，作為 Robot Framework Library 使用。

這個類別封裝了 TestLink API 的複雜性，提供簡潔易用的方法給
Robot Framework 關鍵字使用。

使用範例：
    Library    libraries.testlink_integration.TestLinkConnector

    *** Test Cases ***
    測試 TestLink 整合
        連接到 TestLink
        回報測試結果    TEST-001    PASS    測試通過

作者: Robot Framework Automation Team
日期: 2025-11-10
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from robot.api import logger as robot_logger
from robot.api.deco import keyword

# 支援兩種匯入方式：
# 1. 作為模組匯入: Library    libraries.testlink_integration.TestLinkConnector
# 2. 作為檔案匯入: Library    ../libraries/testlink_integration/TestLinkConnector.py
try:
    # 方式 1: 絕對匯入（作為模組）
    from config.testlink_config import (
        TESTLINK_PROJECT_NAME,
        TESTLINK_TEST_PLAN_NAME,
        TESTLINK_BUILD_NAME,
        STATUS_MAPPING,
        validate_config,
        get_config_summary,
        LOG_FILE,
    )
    from libraries.testlink_integration.api_client.testlink_api import TestLinkAPIClient
except ImportError:
    # 方式 2: 將當前目錄和專案根目錄加入 sys.path，然後直接匯入
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # 回到專案根目錄
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from config.testlink_config import (
        TESTLINK_PROJECT_NAME,
        TESTLINK_TEST_PLAN_NAME,
        TESTLINK_BUILD_NAME,
        STATUS_MAPPING,
        validate_config,
        get_config_summary,
        LOG_FILE,
    )
    from api_client.testlink_api import TestLinkAPIClient


class TestLinkConnector:
    """
    TestLink 連接器 - Robot Framework Library

    提供與 TestLink 測試管理系統整合的高階功能。

    Attributes:
        ROBOT_LIBRARY_SCOPE (str): Robot Framework Library 作用域
        ROBOT_LIBRARY_VERSION (str): Library 版本號
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self):
        """初始化 TestLink Connector"""
        self.api_client = None
        self.project = None
        self.test_plan = None
        self.build = None

        # 設定 loguru 日誌
        logger.add(
            LOG_FILE,
            rotation="10 MB",
            retention="30 days",
            level="DEBUG",
            encoding="utf-8",
        )

        logger.info("TestLinkConnector 已初始化")

    # ========================================================================
    # 內部輔助方法
    # ========================================================================

    def _ensure_connected(self):
        """確保已連接到 TestLink"""
        if not self.api_client:
            raise RuntimeError("尚未連接到 TestLink，請先呼叫「連接到 TestLink」關鍵字")

    def _log_info(self, message: str):
        """同時記錄到 loguru 和 Robot Framework"""
        logger.info(message)
        robot_logger.info(message)

    def _log_warn(self, message: str):
        """記錄警告訊息"""
        logger.warning(message)
        robot_logger.warn(message)

    def _log_error(self, message: str):
        """記錄錯誤訊息"""
        logger.error(message)
        robot_logger.error(message)

    # ========================================================================
    # 連接與初始化
    # ========================================================================

    @keyword("連接到 TestLink")
    def connect_to_testlink(
        self,
        project_name: str = None,
        test_plan_name: str = None,
        build_name: str = None,
    ) -> bool:
        """
        連接到 TestLink 並初始化專案、測試計畫、Build

        Args:
            project_name (str, optional): 專案名稱，預設從配置讀取
            test_plan_name (str, optional): 測試計畫名稱，預設從配置讀取
            build_name (str, optional): Build 名稱，預設從配置讀取

        Returns:
            bool: 連接是否成功

        Examples:
            | 連接到 TestLink |
            | 連接到 TestLink | project_name=我的專案 |
            | 連接到 TestLink | project_name=我的專案 | test_plan_name=Sprint 1 |
        """
        try:
            # 驗證配置
            validate_config()
            self._log_info(f"TestLink 配置: {get_config_summary()}")

            # 使用提供的參數或配置預設值
            project_name = project_name or TESTLINK_PROJECT_NAME
            test_plan_name = test_plan_name or TESTLINK_TEST_PLAN_NAME
            build_name = build_name or TESTLINK_BUILD_NAME

            # 建立 API 客戶端
            self.api_client = TestLinkAPIClient()
            self.api_client.connect()
            self._log_info("✅ 成功連接到 TestLink")

            # 取得專案
            self.project = self.api_client.get_project_by_name(project_name)
            if not self.project:
                raise ValueError(f"找不到專案: {project_name}")
            self._log_info(f"✅ 找到專案: {self.project['name']} (ID: {self.project['id']})")

            # 取得測試計畫
            project_id = int(self.project['id'])
            self.test_plan = self.api_client.get_test_plan_by_name(project_id, test_plan_name)
            if not self.test_plan:
                raise ValueError(f"找不到測試計畫: {test_plan_name}")
            self._log_info(f"✅ 找到測試計畫: {self.test_plan['name']} (ID: {self.test_plan['id']})")

            # 取得或建立 Build
            test_plan_id = int(self.test_plan['id'])
            builds = self.api_client.get_builds(test_plan_id)

            # 嘗試找到同名 Build
            self.build = None
            for b in builds:
                if b.get('name') == build_name:
                    self.build = b
                    break

            # 如果沒找到，建立新 Build
            if not self.build:
                self._log_info(f"建立新 Build: {build_name}")
                self.build = self.api_client.create_build(
                    test_plan_id,
                    build_name,
                    f"由 Robot Framework 自動建立於 {logger._core.handlers[0]._sink._file.name}"
                )

            self._log_info(f"✅ 使用 Build: {self.build['name']} (ID: {self.build['id']})")

            return True

        except Exception as e:
            self._log_error(f"❌ 連接 TestLink 失敗: {e}")
            raise

    @keyword("檢查 TestLink 連接狀態")
    def check_testlink_connection(self) -> bool:
        """
        檢查 TestLink 連接狀態

        Returns:
            bool: 連接是否正常

        Examples:
            | ${status}= | 檢查 TestLink 連接狀態 |
            | Should Be True | ${status} |
        """
        try:
            self._ensure_connected()
            is_connected = self.api_client.check_connection()

            if is_connected:
                self._log_info("✅ TestLink 連接正常")
            else:
                self._log_warn("⚠️ TestLink 連接異常")

            return is_connected

        except Exception as e:
            self._log_error(f"❌ 檢查連接失敗: {e}")
            return False

    # ========================================================================
    # 測試結果回報
    # ========================================================================

    @keyword("回報測試結果到 TestLink")
    def report_test_result(
        self,
        test_case_external_id: str,
        status: str,
        notes: str = "",
        duration: float = 0,
    ) -> Dict[str, Any]:
        """
        回報測試結果到 TestLink

        Args:
            test_case_external_id (str): 測試案例外部 ID (例如: PROJECT-001)
            status (str): 測試狀態 (PASS, FAIL, BLOCKED, SKIP)
            notes (str, optional): 測試備註
            duration (float, optional): 執行時間（分鐘）

        Returns:
            Dict: API 回應結果

        Examples:
            | 回報測試結果到 TestLink | TEST-001 | PASS |
            | 回報測試結果到 TestLink | TEST-002 | FAIL | notes=斷言失敗 |
            | 回報測試結果到 TestLink | TEST-003 | PASS | notes=測試通過 | duration=2.5 |
        """
        try:
            self._ensure_connected()

            # 取得測試案例資訊
            test_case = self.api_client.get_test_case_by_external_id(test_case_external_id)
            if not test_case:
                raise ValueError(f"找不到測試案例: {test_case_external_id}")

            # 轉換狀態
            testlink_status = STATUS_MAPPING.get(status.upper())
            if not testlink_status:
                raise ValueError(f"無效的測試狀態: {status}，有效值: {list(STATUS_MAPPING.keys())}")

            # 回報結果
            test_case_id = int(test_case['testcase_id'])
            test_plan_id = int(self.test_plan['id'])
            build_id = int(self.build['id'])

            result = self.api_client.report_test_result(
                test_case_id=test_case_id,
                test_plan_id=test_plan_id,
                build_id=build_id,
                status=testlink_status,
                notes=notes,
                duration=float(duration),
            )

            self._log_info(
                f"✅ 測試結果已回報: {test_case_external_id} -> {status} "
                f"(TestLink 狀態: {testlink_status})"
            )

            return result

        except Exception as e:
            self._log_error(f"❌ 回報測試結果失敗: {e}")
            raise

    @keyword("批次回報測試結果到 TestLink")
    def batch_report_test_results(
        self,
        test_results: list
    ) -> Dict[str, int]:
        """
        批次回報多個測試結果到 TestLink

        Args:
            test_results (list): 測試結果列表，每個元素為 dict，包含:
                - test_case_id (str): 測試案例外部 ID
                - status (str): 測試狀態
                - notes (str, optional): 測試備註
                - duration (float, optional): 執行時間

        Returns:
            Dict[str, int]: 統計資訊 {'success': 成功數, 'failed': 失敗數}

        Examples:
            | ${results}= | Create List |
            | ...         | ${{ {'test_case_id': 'TEST-001', 'status': 'PASS'} }} |
            | ...         | ${{ {'test_case_id': 'TEST-002', 'status': 'FAIL', 'notes': '錯誤'} }} |
            | 批次回報測試結果到 TestLink | ${results} |
        """
        stats = {'success': 0, 'failed': 0}

        for result in test_results:
            try:
                self.report_test_result(
                    test_case_external_id=result['test_case_id'],
                    status=result['status'],
                    notes=result.get('notes', ''),
                    duration=result.get('duration', 0),
                )
                stats['success'] += 1
            except Exception as e:
                self._log_error(f"批次回報失敗: {result.get('test_case_id')}, 錯誤: {e}")
                stats['failed'] += 1

        self._log_info(f"批次回報完成: 成功 {stats['success']}, 失敗 {stats['failed']}")
        return stats

    # ========================================================================
    # 查詢功能
    # ========================================================================

    @keyword("取得測試案例資訊")
    def get_test_case_info(self, test_case_external_id: str) -> Optional[Dict]:
        """
        取得測試案例資訊

        Args:
            test_case_external_id (str): 測試案例外部 ID

        Returns:
            Optional[Dict]: 測試案例資訊

        Examples:
            | ${info}= | 取得測試案例資訊 | TEST-001 |
            | Log | ${info} |
        """
        try:
            self._ensure_connected()
            test_case = self.api_client.get_test_case_by_external_id(test_case_external_id)

            if test_case:
                self._log_info(f"✅ 找到測試案例: {test_case_external_id}")
            else:
                self._log_warn(f"⚠️ 找不到測試案例: {test_case_external_id}")

            return test_case

        except Exception as e:
            self._log_error(f"❌ 取得測試案例失敗: {e}")
            raise

    @keyword("取得最後執行結果")
    def get_last_execution_result(self, test_case_external_id: str) -> Optional[Dict]:
        """
        取得測試案例的最後執行結果

        Args:
            test_case_external_id (str): 測試案例外部 ID

        Returns:
            Optional[Dict]: 最後執行結果

        Examples:
            | ${result}= | 取得最後執行結果 | TEST-001 |
            | Log | 最後執行狀態: ${result['status']} |
        """
        try:
            self._ensure_connected()
            test_plan_id = int(self.test_plan['id'])

            result = self.api_client.get_last_execution_result(
                test_plan_id=test_plan_id,
                test_case_external_id=test_case_external_id,
            )

            if result:
                self._log_info(f"✅ 取得最後執行結果: {test_case_external_id}")
            else:
                self._log_warn(f"⚠️ 無執行記錄: {test_case_external_id}")

            return result

        except Exception as e:
            self._log_error(f"❌ 取得執行結果失敗: {e}")
            raise

    @keyword("取得當前專案資訊")
    def get_current_project_info(self) -> Dict[str, str]:
        """
        取得當前連接的專案資訊

        Returns:
            Dict[str, str]: 專案資訊摘要

        Examples:
            | ${info}= | 取得當前專案資訊 |
            | Log | 專案名稱: ${info['project_name']} |
        """
        self._ensure_connected()

        info = {
            'project_name': self.project.get('name', '') if self.project else '',
            'project_id': self.project.get('id', '') if self.project else '',
            'test_plan_name': self.test_plan.get('name', '') if self.test_plan else '',
            'test_plan_id': self.test_plan.get('id', '') if self.test_plan else '',
            'build_name': self.build.get('name', '') if self.build else '',
            'build_id': self.build.get('id', '') if self.build else '',
        }

        self._log_info(f"當前專案資訊: {info}")
        return info
