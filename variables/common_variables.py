import os
import json

# 環境變數
ENV = os.getenv('TEST_ENV', 'dev')

# 根據環境載入不同的配置
def get_config():
    if ENV == 'dev':
        return {
            'BASE_URL_API': 'http://dev.api.example.com',
            'BASE_URL_WEB': 'http://dev.web.example.com',
            'APPIUM_SERVER_URL': 'http://localhost:4723/wd/hub',
            'ADMIN_USERNAME': 'dev_admin',
            'ADMIN_PASSWORD': 'dev_password'
        }
    elif ENV == 'staging':
        return {
            'BASE_URL_API': 'http://staging.api.example.com',
            'BASE_URL_WEB': 'http://staging.web.example.com',
            'APPIUM_SERVER_URL': 'http://remote.appium.server/wd/hub',
            'ADMIN_USERNAME': 'staging_admin',
            'ADMIN_PASSWORD': 'staging_password'
        }
    else:
        return {}

CONFIG = get_config()

# 測試用戶數據 (可以從外部文件載入)
def load_users_from_json(file_path='variables/users.json'):
    # 確保文件路徑是絕對路徑，或者相對於 Robot Framework 執行目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(current_dir, file_path)
    
    if not os.path.exists(full_file_path):
        print(f"Warning: {full_file_path} not found. Returning empty user list.")
        return []

    with open(full_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

USERS = load_users_from_json()


