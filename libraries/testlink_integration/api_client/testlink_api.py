"""
TestLink API Client
===================

提供 TestLink XML-RPC API 的低階封裝與直接呼叫功能。

這個模組使用 requests 直接與 TestLink XML-RPC API 通訊，
避免依賴可能過時或不相容的第三方函式庫。

參考文件：
    TestLink API 文檔: https://testlink.org/api/

作者: Robot Framework Automation Team
日期: 2025-11-10
"""

import time
import xmlrpc.client
from typing import Dict, List, Optional, Any
from loguru import logger

from config.testlink_config import (
    TESTLINK_API_URL,
    TESTLINK_API_KEY,
    API_TIMEOUT,
    API_RETRY_COUNT,
    API_RETRY_DELAY,
)


class TestLinkAPIClient:
    """
    TestLink API 客戶端

    使用 XML-RPC 協議與 TestLink 通訊。

    Attributes:
        api_url (str): TestLink API 端點 URL
        api_key (str): TestLink API 金鑰
        server (xmlrpc.client.ServerProxy): XML-RPC 伺服器代理
    """

    def __init__(self, api_url: str = None, api_key: str = None):
        """
        初始化 TestLink API 客戶端

        Args:
            api_url (str, optional): TestLink API URL，預設從配置讀取
            api_key (str, optional): TestLink API Key，預設從配置讀取
        """
        self.api_url = api_url or TESTLINK_API_URL
        self.api_key = api_key or TESTLINK_API_KEY
        self.server = None

        if not self.api_key:
            logger.warning("TestLink API Key 未設定，部分功能將無法使用")

        logger.info(f"TestLink API Client 已初始化: {self.api_url}")

    def connect(self) -> bool:
        """
        建立與 TestLink 的連接

        Returns:
            bool: 連接是否成功

        Raises:
            ConnectionError: 當無法連接到 TestLink 時
        """
        try:
            # 建立 XML-RPC ServerProxy
            self.server = xmlrpc.client.ServerProxy(
                self.api_url,
                verbose=False,
                allow_none=True
            )

            # 測試連接 - 呼叫 ping 或 about
            about = self.server.tl.about()
            logger.info(f"成功連接到 TestLink: {about}")
            return True

        except Exception as e:
            error_msg = f"無法連接到 TestLink: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def _call_api(self, method: str, params: Dict[str, Any]) -> Any:
        """
        呼叫 TestLink API 方法（帶重試機制）

        Args:
            method (str): API 方法名稱
            params (dict): API 參數

        Returns:
            Any: API 回應結果

        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        if not self.server:
            raise RuntimeError("尚未連接到 TestLink，請先呼叫 connect()")

        # 自動添加 API key
        params['devKey'] = self.api_key

        for attempt in range(API_RETRY_COUNT):
            try:
                logger.debug(f"呼叫 TestLink API: {method}, 參數: {params}")

                # 呼叫 API
                api_method = getattr(self.server.tl, method)
                result = api_method(params)

                logger.debug(f"API 回應: {result}")
                return result

            except Exception as e:
                logger.warning(f"API 呼叫失敗 (嘗試 {attempt + 1}/{API_RETRY_COUNT}): {e}")

                if attempt < API_RETRY_COUNT - 1:
                    time.sleep(API_RETRY_DELAY)
                else:
                    error_msg = f"API 呼叫失敗: {method}, 錯誤: {e}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

    # ========================================================================
    # 專案相關 API
    # ========================================================================

    def get_projects(self) -> List[Dict]:
        """
        取得所有專案列表

        Returns:
            List[Dict]: 專案列表
        """
        return self._call_api('getProjects', {})

    def get_project_by_name(self, project_name: str) -> Optional[Dict]:
        """
        根據名稱取得專案

        Args:
            project_name (str): 專案名稱

        Returns:
            Optional[Dict]: 專案資訊，若不存在則回傳 None
        """
        projects = self.get_projects()
        for project in projects:
            if project.get('name') == project_name:
                return project
        return None

    # ========================================================================
    # 測試計畫相關 API
    # ========================================================================

    def get_test_plans(self, project_id: int) -> List[Dict]:
        """
        取得專案的所有測試計畫

        Args:
            project_id (int): 專案 ID

        Returns:
            List[Dict]: 測試計畫列表
        """
        params = {'testprojectid': project_id}
        return self._call_api('getProjectTestPlans', params)

    def get_test_plan_by_name(self, project_id: int, plan_name: str) -> Optional[Dict]:
        """
        根據名稱取得測試計畫

        Args:
            project_id (int): 專案 ID
            plan_name (str): 測試計畫名稱

        Returns:
            Optional[Dict]: 測試計畫資訊
        """
        plans = self.get_test_plans(project_id)
        for plan in plans:
            if plan.get('name') == plan_name:
                return plan
        return None

    # ========================================================================
    # Build 相關 API
    # ========================================================================

    def get_builds(self, test_plan_id: int) -> List[Dict]:
        """
        取得測試計畫的所有 Builds

        Args:
            test_plan_id (int): 測試計畫 ID

        Returns:
            List[Dict]: Build 列表
        """
        params = {'testplanid': test_plan_id}
        return self._call_api('getBuildsForTestPlan', params)

    def get_latest_build(self, test_plan_id: int) -> Optional[Dict]:
        """
        取得測試計畫的最新 Build

        Args:
            test_plan_id (int): 測試計畫 ID

        Returns:
            Optional[Dict]: 最新 Build 資訊
        """
        builds = self.get_builds(test_plan_id)
        if builds:
            # 根據 id 排序，取最新的
            return max(builds, key=lambda b: int(b.get('id', 0)))
        return None

    def create_build(self, test_plan_id: int, build_name: str, notes: str = "") -> Dict:
        """
        建立新的 Build

        Args:
            test_plan_id (int): 測試計畫 ID
            build_name (str): Build 名稱
            notes (str, optional): Build 說明

        Returns:
            Dict: 建立的 Build 資訊
        """
        params = {
            'testplanid': test_plan_id,
            'buildname': build_name,
            'buildnotes': notes,
        }
        return self._call_api('createBuild', params)

    # ========================================================================
    # 測試套件相關 API
    # ========================================================================

    def get_first_level_test_suites(self, project_id: int) -> List[Dict]:
        """
        取得專案的第一層測試套件

        Args:
            project_id (int): 專案 ID

        Returns:
            List[Dict]: 第一層測試套件列表，每個元素包含 id, name 等欄位

        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        params = {'testprojectid': project_id}
        result = self._call_api('getFirstLevelTestSuitesForTestProject', params)

        # API 在無資料時可能回傳錯誤格式
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and 'code' in first and 'message' in first:
                logger.warning(f"取得第一層測試套件失敗: {first['message']}")
                return []

        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"取得第一層測試套件失敗: {result['message']}")
            return []

        return result if isinstance(result, list) else []

    def get_test_suites_for_test_plan(self, test_plan_id: int) -> List[Dict]:
        """
        取得測試計畫中的所有測試套件

        Args:
            test_plan_id (int): 測試計畫 ID

        Returns:
            List[Dict]: 測試套件列表

        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        params = {'testplanid': test_plan_id}
        result = self._call_api('getTestSuitesForTestPlan', params)

        # API 在無資料時可能回傳錯誤格式
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and 'code' in first and 'message' in first:
                logger.warning(f"取得測試計畫套件失敗: {first['message']}")
                return []

        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"取得測試計畫套件失敗: {result['message']}")
            return []

        # API 可能回傳 dict（以 suite_id 為 key），統一轉為 list
        if isinstance(result, dict):
            return list(result.values())

        return result if isinstance(result, list) else []

    # ========================================================================
    # 測試案例相關 API
    # ========================================================================

    def get_test_case_by_external_id(self, external_id: str) -> Optional[Dict]:
        """
        根據外部 ID 取得測試案例

        Args:
            external_id (str): 測試案例外部 ID (例如: PROJECT-123)

        Returns:
            Optional[Dict]: 測試案例資訊
        """
        params = {'testcaseexternalid': external_id}
        result = self._call_api('getTestCase', params)

        # API 回傳可能是 list，取第一個
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            # 檢查是否為錯誤回應
            if isinstance(first_result, dict) and 'code' in first_result and 'message' in first_result:
                logger.warning(f"TestLink API 錯誤: {first_result['message']}")
                return None
            return first_result

        # 檢查單一回應是否為錯誤
        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"TestLink API 錯誤: {result['message']}")
            return None

        return result

    def get_test_cases_for_test_plan(
        self,
        test_plan_id: int,
        build_id: int = None,
        get_step_info: bool = True,
        execution_type: int = None,
        execute_status: str = None,
    ) -> Dict:
        """
        取得測試計畫中的所有測試案例（支援 build 篩選、含步驟）

        Args:
            test_plan_id (int): 測試計畫 ID
            build_id (int, optional): Build ID，用於篩選特定 build 的測試案例
            get_step_info (bool): 是否取得步驟資訊，預設 True
            execution_type (int, optional): 執行類型篩選（1=手動, 2=自動）
            execute_status (str, optional): 執行狀態篩選（如 'p', 'f', 'b', 'n'）

        Returns:
            Dict: 測試案例字典，以測試案例 ID 為 key

        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        params = {
            'testplanid': test_plan_id,
            'getstepinfo': get_step_info,
        }

        if build_id is not None:
            params['buildid'] = build_id

        if execution_type is not None:
            params['executiontype'] = execution_type

        if execute_status is not None:
            params['executestatus'] = execute_status

        result = self._call_api('getTestCasesForTestPlan', params)

        # API 在無資料時可能回傳錯誤格式
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and 'code' in first and 'message' in first:
                logger.warning(f"取得測試計畫案例失敗: {first['message']}")
                return {}

        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"取得測試計畫案例失敗: {result['message']}")
            return {}

        return result if isinstance(result, dict) else {}

    def get_test_cases_for_test_suite(
        self,
        test_suite_id: int,
        deep: bool = True,
        detail: str = 'full',
    ) -> List[Dict]:
        """
        取得測試套件中的所有測試案例（含巢狀子套件）

        Args:
            test_suite_id (int): 測試套件 ID
            deep (bool): 是否包含子套件中的測試案例，預設 True
            detail (str): 回傳詳細程度，'full' 回傳含 steps，預設 'full'

        Returns:
            List[Dict]: 測試案例列表，detail='full' 時包含 steps 欄位

        Raises:
            RuntimeError: 當 API 呼叫失敗時
        """
        params = {
            'testsuiteid': test_suite_id,
            'deep': deep,
            'details': detail,
        }

        result = self._call_api('getTestCasesForTestSuite', params)

        # API 在無資料時可能回傳錯誤格式
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and 'code' in first and 'message' in first:
                logger.warning(f"取得測試套件案例失敗: {first['message']}")
                return []

        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"取得測試套件案例失敗: {result['message']}")
            return []

        return result if isinstance(result, list) else []

    def get_test_case_steps(self, external_id: str) -> List[Dict]:
        """
        取得指定測試案例的完整步驟列表

        內部呼叫 get_test_case_by_external_id，提取 steps 欄位。

        Args:
            external_id (str): 測試案例外部 ID (例如: PROJECT-123)

        Returns:
            List[Dict]: 步驟列表，每個元素包含:
                - step_number (int): 步驟編號
                - actions (str): 步驟動作文字
                - expected_results (str): 預期結果文字
                - execution_type (int): 執行類型（1=手動, 2=自動）

        Raises:
            ValueError: 當找不到指定測試案例時
        """
        test_case = self.get_test_case_by_external_id(external_id)
        if not test_case:
            raise ValueError(f"找不到測試案例: {external_id}")

        raw_steps = test_case.get('steps', [])
        steps = []

        for step in raw_steps:
            steps.append({
                'step_number': int(step.get('step_number', 0)),
                'actions': step.get('actions', ''),
                'expected_results': step.get('expected_results', ''),
                'execution_type': int(step.get('execution_type', 1)),
            })

        # 依步驟編號排序
        steps.sort(key=lambda s: s['step_number'])

        logger.info(f"取得測試案例 {external_id} 的 {len(steps)} 個步驟")
        return steps

    # ========================================================================
    # 測試結果相關 API
    # ========================================================================

    def report_test_result(
        self,
        test_case_id: int,
        test_plan_id: int,
        build_id: int,
        status: str,
        notes: str = "",
        duration: float = 0,
        platform_id: int = None,
    ) -> Dict:
        """
        回報測試結果

        Args:
            test_case_id (int): 測試案例 ID
            test_plan_id (int): 測試計畫 ID
            build_id (int): Build ID
            status (str): 測試狀態 ('p'=passed, 'f'=failed, 'b'=blocked)
            notes (str, optional): 測試備註
            duration (float, optional): 執行時間（分鐘）
            platform_id (int, optional): 平台 ID

        Returns:
            Dict: API 回應結果
        """
        params = {
            'testcaseid': test_case_id,
            'testplanid': test_plan_id,
            'buildid': build_id,
            'status': status,
            'notes': notes,
        }

        if duration > 0:
            params['execduration'] = duration

        if platform_id:
            params['platformid'] = platform_id

        return self._call_api('reportTCResult', params)

    def get_last_execution_result(
        self,
        test_plan_id: int,
        test_case_id: int = None,
        test_case_external_id: str = None,
    ) -> Optional[Dict]:
        """
        取得測試案例的最後執行結果

        Args:
            test_plan_id (int): 測試計畫 ID
            test_case_id (int, optional): 測試案例內部 ID
            test_case_external_id (str, optional): 測試案例外部 ID

        Returns:
            Optional[Dict]: 最後執行結果
        """
        params = {'testplanid': test_plan_id}

        if test_case_id:
            params['testcaseid'] = test_case_id
        elif test_case_external_id:
            params['testcaseexternalid'] = test_case_external_id
        else:
            raise ValueError("必須提供 test_case_id 或 test_case_external_id")

        result = self._call_api('getLastExecutionResult', params)

        # API 回傳可能是 list，取第一個
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            # 檢查是否為錯誤回應
            if isinstance(first_result, dict) and 'code' in first_result and 'message' in first_result:
                logger.warning(f"TestLink API 錯誤: {first_result['message']}")
                return None
            return first_result

        # 檢查單一回應是否為錯誤
        if isinstance(result, dict) and 'code' in result and 'message' in result:
            logger.warning(f"TestLink API 錯誤: {result['message']}")
            return None

        return result

    # ========================================================================
    # 系統相關 API
    # ========================================================================

    def check_connection(self) -> bool:
        """
        檢查 TestLink 連接狀態

        Returns:
            bool: 連接是否正常
        """
        try:
            self._call_api('ping', {})
            return True
        except Exception as e:
            logger.error(f"TestLink 連接檢查失敗: {e}")
            return False

    def get_full_path(self, node_id: int) -> str:
        """
        取得節點的完整路徑

        Args:
            node_id (int): 節點 ID

        Returns:
            str: 節點完整路徑
        """
        params = {'nodeid': node_id}
        return self._call_api('getFullPath', params)
