"""
TestLink 配置管理模組
===================

統一管理 TestLink 連接的所有配置參數。

配置優先順序：
1. 系統環境變數 (最高優先)
2. 專案根目錄 .env 檔案
3. 配置檔案中的預設值

環境變數：
    TESTLINK_API_URL: TestLink API 端點 URL
    TESTLINK_API_KEY: TestLink API 金鑰
    TESTLINK_PROJECT_NAME: 專案名稱（選填）
    TESTLINK_TEST_PLAN_NAME: 測試計畫名稱（選填）
    TESTLINK_BUILD_NAME: Build 名稱（選填）

作者: Robot Framework Automation Team
日期: 2025-11-10
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# 載入專案根目錄的 .env 檔案
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(env_path, override=True)
    logger.info(f"已載入 TestLink 環境配置: {env_path}")
else:
    logger.warning(f"未找到 .env 檔案: {env_path}")

# ============================================================================
# TestLink API 連接配置
# ============================================================================

TESTLINK_API_URL = os.getenv(
    'TESTLINK_API_URL',
    'http://localhost/testlink/lib/api/xmlrpc/v1/xmlrpc.php'
)

TESTLINK_API_KEY = os.getenv(
    'TESTLINK_API_KEY',
    ''  # 必須從環境變數提供
)

# ============================================================================
# TestLink 專案配置
# ============================================================================

TESTLINK_PROJECT_NAME = os.getenv(
    'TESTLINK_PROJECT_NAME',
    'Robot Automation Project'
)

TESTLINK_TEST_PLAN_NAME = os.getenv(
    'TESTLINK_TEST_PLAN_NAME',
    'Automated Test Plan'
)

TESTLINK_BUILD_NAME = os.getenv(
    'TESTLINK_BUILD_NAME',
    'Build 1.0'
)

# ============================================================================
# TestLink API 配置
# ============================================================================

# API 連接逾時設定（秒）
API_TIMEOUT = int(os.getenv('TESTLINK_API_TIMEOUT', '30'))

# API 重試次數
API_RETRY_COUNT = int(os.getenv('TESTLINK_API_RETRY_COUNT', '3'))

# API 重試延遲（秒）
API_RETRY_DELAY = int(os.getenv('TESTLINK_API_RETRY_DELAY', '2'))

# ============================================================================
# 測試結果映射
# ============================================================================

# Robot Framework 測試狀態對應到 TestLink 狀態
# TestLink 狀態: p (passed), f (failed), b (blocked)
STATUS_MAPPING = {
    'PASS': 'p',
    'FAIL': 'f',
    'BLOCKED': 'b',
    'SKIP': 'b',
}

# ============================================================================
# 日誌配置
# ============================================================================

LOG_LEVEL = os.getenv('TESTLINK_LOG_LEVEL', 'INFO')
LOG_FILE = project_root / 'logs' / 'testlink_integration.log'

# 確保日誌目錄存在
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 配置驗證函數
# ============================================================================

def validate_config():
    """
    驗證 TestLink 配置是否完整

    Returns:
        bool: 配置是否有效

    Raises:
        ValueError: 當必要配置缺失時
    """
    errors = []

    if not TESTLINK_API_URL:
        errors.append("TESTLINK_API_URL 未設定")

    if not TESTLINK_API_KEY:
        errors.append("TESTLINK_API_KEY 未設定")

    if errors:
        error_msg = "TestLink 配置錯誤:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("TestLink 配置驗證通過")
    return True


def get_config_summary():
    """
    取得配置摘要（隱藏敏感資訊）

    Returns:
        dict: 配置摘要
    """
    return {
        'api_url': TESTLINK_API_URL,
        'api_key': f"{TESTLINK_API_KEY[:8]}..." if TESTLINK_API_KEY else "未設定",
        'project_name': TESTLINK_PROJECT_NAME,
        'test_plan_name': TESTLINK_TEST_PLAN_NAME,
        'build_name': TESTLINK_BUILD_NAME,
        'timeout': API_TIMEOUT,
        'retry_count': API_RETRY_COUNT,
    }


# ============================================================================
# 模組初始化時的配置檢查
# ============================================================================

if __name__ == "__main__":
    # 當直接執行此模組時，顯示配置摘要
    import json
    print("TestLink 配置摘要:")
    print(json.dumps(get_config_summary(), indent=2, ensure_ascii=False))

    try:
        validate_config()
        print("\n✅ 配置驗證成功")
    except ValueError as e:
        print(f"\n❌ 配置驗證失敗: {e}")
