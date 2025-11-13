"""
TestLink Integration Library
============================

這個套件提供與 TestLink 測試管理系統的整合功能。

主要功能：
- TestLink API 連接與認證
- 測試結果回報
- 測試案例同步
- 測試計畫管理

使用範例：
    from libraries.testlink_integration import TestLinkConnector

    connector = TestLinkConnector()
    connector.connect_to_testlink()
    connector.report_test_result(case_id, status)

作者: Robot Framework Automation Team
版本: 1.0.0
日期: 2025-11-10
"""

from .TestLinkConnector import TestLinkConnector

__version__ = "1.0.0"
__all__ = ["TestLinkConnector"]
