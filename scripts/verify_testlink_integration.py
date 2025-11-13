#!/usr/bin/env python3
"""
TestLink 整合模組驗證腳本
========================

快速驗證 TestLink 整合模組的安裝和配置是否正確。

執行方式：
    python scripts/verify_testlink_integration.py

作者: Robot Framework Automation Team
日期: 2025-11-10
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_section(title):
    """印出區塊標題"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def verify_imports():
    """驗證模組匯入"""
    print_section("1. 驗證模組匯入")

    try:
        from libraries.testlink_integration import TestLinkConnector
        print("✅ TestLinkConnector 匯入成功")

        from libraries.testlink_integration.api_client import TestLinkAPIClient
        print("✅ TestLinkAPIClient 匯入成功")

        from config import testlink_config
        print("✅ testlink_config 匯入成功")

        return True
    except Exception as e:
        print(f"❌ 模組匯入失敗: {e}")
        return False


def verify_config():
    """驗證配置"""
    print_section("2. 驗證配置系統")

    try:
        from config.testlink_config import (
            TESTLINK_API_URL,
            TESTLINK_API_KEY,
            TESTLINK_PROJECT_NAME,
            get_config_summary,
        )

        print(f"API URL: {TESTLINK_API_URL}")
        print(f"API Key: {'已設定' if TESTLINK_API_KEY else '❌ 未設定'}")
        print(f"專案名稱: {TESTLINK_PROJECT_NAME}")

        print("\n配置摘要:")
        summary = get_config_summary()
        for key, value in summary.items():
            print(f"  - {key}: {value}")

        if not TESTLINK_API_KEY:
            print("\n⚠️ 警告: TESTLINK_API_KEY 未設定")
            print("請在 .env 檔案中設定 TESTLINK_API_KEY")
            return False

        print("\n✅ 配置系統驗證成功")
        return True

    except Exception as e:
        print(f"❌ 配置驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_robot_keywords():
    """驗證 Robot Framework 關鍵字"""
    print_section("3. 驗證 Robot Framework 關鍵字")

    try:
        keywords_file = project_root / 'resources' / 'testlink_keywords.robot'

        if not keywords_file.exists():
            print(f"❌ 關鍵字檔案不存在: {keywords_file}")
            return False

        print(f"✅ 關鍵字檔案存在: {keywords_file}")

        # 讀取並計算關鍵字數量
        with open(keywords_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 簡單計算 Given/When/Then/And 關鍵字數量
        given_count = content.count('Given ')
        when_count = content.count('When ')
        then_count = content.count('Then ')
        and_count = content.count('And ')

        print(f"\n關鍵字統計:")
        print(f"  - Given 關鍵字: {given_count}")
        print(f"  - When 關鍵字: {when_count}")
        print(f"  - Then 關鍵字: {then_count}")
        print(f"  - And 關鍵字: {and_count}")

        print("\n✅ Robot Framework 關鍵字驗證成功")
        return True

    except Exception as e:
        print(f"❌ 關鍵字驗證失敗: {e}")
        return False


def verify_test_connection():
    """測試連接（需要 TestLink 服務運行）"""
    print_section("4. 測試 TestLink 連接（選擇性）")

    try:
        from libraries.testlink_integration.api_client import TestLinkAPIClient
        from config.testlink_config import TESTLINK_API_KEY

        if not TESTLINK_API_KEY:
            print("⚠️ API Key 未設定，跳過連接測試")
            return True

        print("嘗試連接到 TestLink...")
        client = TestLinkAPIClient()

        try:
            client.connect()
            print("✅ 成功連接到 TestLink")

            # 測試取得專案列表
            projects = client.get_projects()
            print(f"✅ 取得專案列表成功，共 {len(projects)} 個專案")

            if projects:
                print("\n專案列表:")
                for project in projects[:3]:  # 只顯示前 3 個
                    print(f"  - {project.get('name', 'Unknown')} (ID: {project.get('id', 'N/A')})")

            return True

        except ConnectionError as e:
            print(f"⚠️ 無法連接到 TestLink: {e}")
            print("這是正常的，如果 TestLink 服務未運行")
            return True  # 不算錯誤

    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_files_structure():
    """驗證檔案結構"""
    print_section("5. 驗證檔案結構")

    required_files = [
        'libraries/testlink_integration/__init__.py',
        'libraries/testlink_integration/TestLinkConnector.py',
        'libraries/testlink_integration/api_client/__init__.py',
        'libraries/testlink_integration/api_client/testlink_api.py',
        'libraries/testlink_integration/README.md',
        'config/testlink_config.py',
        'resources/testlink_keywords.robot',
        '.env.example',
    ]

    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (不存在)")
            all_exist = False

    if all_exist:
        print("\n✅ 檔案結構完整")
    else:
        print("\n❌ 部分檔案缺失")

    return all_exist


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        TestLink 整合模組驗證工具                             ║
║        Version 1.0.0                                         ║
╚══════════════════════════════════════════════════════════════╝
    """)

    results = {
        '模組匯入': verify_imports(),
        '配置系統': verify_config(),
        'Robot 關鍵字': verify_robot_keywords(),
        '檔案結構': verify_files_structure(),
        'TestLink 連接': verify_test_connection(),
    }

    # 總結
    print_section("驗證總結")

    for check, passed in results.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{check}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有驗證項目通過！TestLink 整合模組已就緒。")
        print("\n下一步:")
        print("1. 確保 TestLink 服務正在運行")
        print("2. 在 .env 檔案中配置 TestLink 連接資訊")
        print("3. 執行測試: robot tests/testlink_integration/")
        return 0
    else:
        print("⚠️ 部分驗證項目失敗，請檢查上述錯誤訊息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
