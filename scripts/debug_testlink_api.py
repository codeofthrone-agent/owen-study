#!/usr/bin/env python3
"""
TestLink API 除錯腳本
查看 API 實際回傳的資料結構

執行方式:
    python scripts/debug_testlink_api.py
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libraries.testlink_integration.api_client.testlink_api import TestLinkAPIClient
from config.testlink_config import TESTLINK_API_KEY
import json


def main():
    print("=" * 60)
    print("TestLink API 除錯工具")
    print("=" * 60)

    if not TESTLINK_API_KEY:
        print("❌ TESTLINK_API_KEY 未設定")
        print("請在 .env 檔案中設定 TESTLINK_API_KEY")
        return 1

    try:
        # 建立 API 客戶端
        print("\n1. 建立 API 連接...")
        client = TestLinkAPIClient()
        client.connect()
        print("✅ 連接成功")

        # 測試案例 ID
        test_case_id = "CCU-123"

        print(f"\n2. 查詢測試案例: {test_case_id}")
        test_case = client.get_test_case_by_external_id(test_case_id)

        if not test_case:
            print(f"❌ 找不到測試案例: {test_case_id}")
            return 1

        print("\n3. API 回應資料結構:")
        print("-" * 60)
        print(json.dumps(test_case, indent=2, ensure_ascii=False))
        print("-" * 60)

        print("\n4. 可用的欄位名稱:")
        if isinstance(test_case, dict):
            for key in test_case.keys():
                print(f"  - {key}: {type(test_case[key]).__name__}")

        # 嘗試找到 ID 欄位
        print("\n5. 尋找可能的 ID 欄位:")
        possible_id_fields = ['testcase_id', 'id', 'case_id', 'tc_id', 'tcid']
        for field in possible_id_fields:
            if field in test_case:
                print(f"  ✅ 找到: {field} = {test_case[field]}")

        return 0

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
