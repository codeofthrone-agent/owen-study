"""
TestLink Connector 單元測試
==========================

測試 TestLinkConnector 類別的核心功能。

執行方式：
    pytest libraries/testlink_integration/tests/test_connector.py -v

作者: Robot Framework Automation Team
日期: 2025-11-10
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from libraries.testlink_integration.TestLinkConnector import TestLinkConnector


@pytest.fixture
def connector():
    """建立 TestLinkConnector 實例"""
    return TestLinkConnector()


@pytest.fixture
def mock_api_client():
    """建立 Mock API Client"""
    mock_client = Mock()
    mock_client.connect.return_value = True
    mock_client.check_connection.return_value = True
    return mock_client


class TestTestLinkConnectorInit:
    """測試 TestLinkConnector 初始化"""

    def test_init_creates_instance(self, connector):
        """測試實例建立"""
        assert connector is not None
        assert connector.api_client is None
        assert connector.project is None
        assert connector.test_plan is None
        assert connector.build is None

    def test_library_metadata(self, connector):
        """測試 Library 元數據"""
        assert hasattr(connector, 'ROBOT_LIBRARY_SCOPE')
        assert hasattr(connector, 'ROBOT_LIBRARY_VERSION')
        assert connector.ROBOT_LIBRARY_SCOPE == 'GLOBAL'


class TestConnection:
    """測試連接功能"""

    @patch('libraries.testlink_integration.TestLinkConnector.TestLinkAPIClient')
    @patch('libraries.testlink_integration.TestLinkConnector.validate_config')
    def test_connect_to_testlink_success(self, mock_validate, mock_api_class, connector):
        """測試成功連接到 TestLink"""
        # 設定 mock
        mock_validate.return_value = True
        mock_api = Mock()
        mock_api.connect.return_value = True
        mock_api.get_project_by_name.return_value = {'id': '1', 'name': 'Test Project'}
        mock_api.get_test_plan_by_name.return_value = {'id': '1', 'name': 'Test Plan'}
        mock_api.get_builds.return_value = []
        mock_api.create_build.return_value = {'id': '1', 'name': 'Build 1.0'}
        mock_api_class.return_value = mock_api

        # 執行測試
        result = connector.connect_to_testlink()

        # 驗證
        assert result is True
        assert connector.api_client is not None
        assert connector.project is not None
        assert connector.test_plan is not None
        assert connector.build is not None

    def test_ensure_connected_raises_when_not_connected(self, connector):
        """測試未連接時拋出異常"""
        with pytest.raises(RuntimeError, match="尚未連接到 TestLink"):
            connector._ensure_connected()

    @patch('libraries.testlink_integration.TestLinkConnector.TestLinkAPIClient')
    def test_check_testlink_connection(self, mock_api_class, connector):
        """測試連接狀態檢查"""
        # 設定 mock
        mock_api = Mock()
        mock_api.check_connection.return_value = True
        connector.api_client = mock_api

        # 執行測試
        result = connector.check_testlink_connection()

        # 驗證
        assert result is True
        mock_api.check_connection.assert_called_once()


class TestReportResult:
    """測試結果回報功能"""

    def setup_method(self):
        """設定測試方法"""
        self.mock_api = Mock()
        self.mock_api.get_test_case_by_external_id.return_value = {
            'testcase_id': '123',
            'name': 'Test Case 1'
        }
        self.mock_api.report_test_result.return_value = {'status': 'ok'}

    def test_report_test_result_success(self, connector):
        """測試成功回報測試結果"""
        # 設定 connector
        connector.api_client = self.mock_api
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        connector.build = {'id': '1', 'name': 'Build 1.0'}

        # 執行測試
        result = connector.report_test_result('TEST-001', 'PASS')

        # 驗證
        assert result == {'status': 'ok'}
        self.mock_api.get_test_case_by_external_id.assert_called_once_with('TEST-001')
        self.mock_api.report_test_result.assert_called_once()

    def test_report_test_result_with_notes(self, connector):
        """測試回報測試結果並附註"""
        connector.api_client = self.mock_api
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        connector.build = {'id': '1', 'name': 'Build 1.0'}

        result = connector.report_test_result('TEST-001', 'FAIL', notes='測試失敗')

        assert result == {'status': 'ok'}
        # 驗證 notes 有傳入
        call_args = self.mock_api.report_test_result.call_args
        assert call_args[1]['notes'] == '測試失敗'

    def test_report_test_result_invalid_status(self, connector):
        """測試無效的測試狀態"""
        connector.api_client = self.mock_api
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        connector.build = {'id': '1', 'name': 'Build 1.0'}

        with pytest.raises(ValueError, match="無效的測試狀態"):
            connector.report_test_result('TEST-001', 'INVALID_STATUS')

    def test_report_test_result_test_case_not_found(self, connector):
        """測試案例不存在"""
        connector.api_client = self.mock_api
        connector.api_client.get_test_case_by_external_id.return_value = None
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        connector.build = {'id': '1', 'name': 'Build 1.0'}

        with pytest.raises(ValueError, match="找不到測試案例"):
            connector.report_test_result('TEST-999', 'PASS')


class TestBatchReport:
    """測試批次回報功能"""

    def setup_method(self):
        """設定測試方法"""
        self.mock_api = Mock()

    def test_batch_report_all_success(self, connector):
        """測試批次回報全部成功"""
        # Mock report_test_result 方法
        connector.report_test_result = Mock(return_value={'status': 'ok'})

        test_results = [
            {'test_case_id': 'TEST-001', 'status': 'PASS'},
            {'test_case_id': 'TEST-002', 'status': 'FAIL'},
            {'test_case_id': 'TEST-003', 'status': 'PASS'},
        ]

        stats = connector.batch_report_test_results(test_results)

        assert stats['success'] == 3
        assert stats['failed'] == 0

    def test_batch_report_partial_failure(self, connector):
        """測試批次回報部分失敗"""
        # Mock report_test_result 方法（第二個會失敗）
        def side_effect(test_case_id, status, notes='', duration=0):
            if test_case_id == 'TEST-002':
                raise Exception('測試失敗')
            return {'status': 'ok'}

        connector.report_test_result = Mock(side_effect=side_effect)

        test_results = [
            {'test_case_id': 'TEST-001', 'status': 'PASS'},
            {'test_case_id': 'TEST-002', 'status': 'FAIL'},
            {'test_case_id': 'TEST-003', 'status': 'PASS'},
        ]

        stats = connector.batch_report_test_results(test_results)

        assert stats['success'] == 2
        assert stats['failed'] == 1


class TestQueryFunctions:
    """測試查詢功能"""

    def setup_method(self):
        """設定測試方法"""
        self.mock_api = Mock()

    def test_get_test_case_info(self, connector):
        """測試取得測試案例資訊"""
        connector.api_client = self.mock_api
        self.mock_api.get_test_case_by_external_id.return_value = {
            'testcase_id': '123',
            'name': 'Test Case 1'
        }

        info = connector.get_test_case_info('TEST-001')

        assert info is not None
        assert info['testcase_id'] == '123'
        assert info['name'] == 'Test Case 1'

    def test_get_last_execution_result(self, connector):
        """測試取得最後執行結果"""
        connector.api_client = self.mock_api
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        self.mock_api.get_last_execution_result.return_value = {
            'status': 'p',
            'execution_ts': '2025-11-10 10:00:00'
        }

        result = connector.get_last_execution_result('TEST-001')

        assert result is not None
        assert result['status'] == 'p'

    def test_get_current_project_info(self, connector):
        """測試取得當前專案資訊"""
        connector.api_client = Mock()  # 只要不是 None
        connector.project = {'id': '1', 'name': 'Test Project'}
        connector.test_plan = {'id': '1', 'name': 'Test Plan'}
        connector.build = {'id': '1', 'name': 'Build 1.0'}

        info = connector.get_current_project_info()

        assert info['project_name'] == 'Test Project'
        assert info['test_plan_name'] == 'Test Plan'
        assert info['build_name'] == 'Build 1.0'


class TestStatusMapping:
    """測試狀態映射"""

    def test_status_mapping_exists(self):
        """測試狀態映射存在"""
        from config.testlink_config import STATUS_MAPPING

        assert 'PASS' in STATUS_MAPPING
        assert 'FAIL' in STATUS_MAPPING
        assert 'BLOCKED' in STATUS_MAPPING
        assert 'SKIP' in STATUS_MAPPING

        assert STATUS_MAPPING['PASS'] == 'p'
        assert STATUS_MAPPING['FAIL'] == 'f'
        assert STATUS_MAPPING['BLOCKED'] == 'b'
        assert STATUS_MAPPING['SKIP'] == 'b'
