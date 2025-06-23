"""
SwitchBot 智慧插座控制腳本

基於參考專案 codeofthrone/switchbot_smartplug_control 開發
提供命令列介面控制 SwitchBot 智慧插座
"""
import os
import sys
import logging
import time
import requests
import hmac
import hashlib
import base64
import uuid
import json
from pathlib import Path

# 嘗試載入統一配置系統
try:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sys.path.insert(0, str(project_root))
    
    from config.switchbot_config import (
        SWITCHBOT_CREDENTIALS,
        SWITCHBOT_API_CONFIG,
        validate_switchbot_config
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# 嘗試載入相依套件
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# 現在使用直接 HTTP API 而不是 pyswitchbot SDK
REQUESTS_AVAILABLE = True

# 載入環境設定
if not CONFIG_AVAILABLE and DOTENV_AVAILABLE:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    load_dotenv(current_dir / '.env')
    load_dotenv(project_root / '.env')

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 從統一配置或環境變數讀取設定
if CONFIG_AVAILABLE:
    TOKEN = SWITCHBOT_CREDENTIALS['token']
    SECRET = SWITCHBOT_CREDENTIALS['secret']
    DEVICE_ID = SWITCHBOT_CREDENTIALS['device_id']
else:
    TOKEN = os.getenv('TOKEN') or os.getenv('SWITCHBOT_TOKEN')
    SECRET = os.getenv('SECRET') or os.getenv('SWITCHBOT_SECRET')
    DEVICE_ID = os.getenv('DEVICE_ID') or os.getenv('SWITCHBOT_DEVICE_ID')

def check_requirements():
    """檢查必要的環境設定和套件"""
    issues = []
    
    # 檢查環境變數
    if not TOKEN:
        issues.append("SWITCHBOT_TOKEN 環境變數未設定")
    if not SECRET:
        issues.append("SWITCHBOT_SECRET 環境變數未設定")
    if not DEVICE_ID:
        issues.append("SWITCHBOT_DEVICE_ID 環境變數未設定")
    
    if issues:
        print("❌ 設定檢查失敗:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        print("🔧 修復建議:")
        
        if not TOKEN or not SECRET or not DEVICE_ID:
            print("   1. 設定環境變數:")
            print("      - 複製 .env.example 為 .env")
            print("      - 編輯 .env 檔案，填入您的 API 認證資訊")
            print("      - 執行 python get_device_id.py 取得設備 ID")
        
        return False
    
    return True

def get_sign(token: str, secret: str, timestamp: int, nonce: str) -> str:
    """
    產生 SwitchBot API 簽名
    
    根據 SwitchBot API 文檔 Python 3 範例的正確簽名方法：
    string_to_sign = token + timestamp + nonce
    signature = base64(hmac_sha256(secret, string_to_sign))
    
    Args:
        token: SwitchBot API Token
        secret: SwitchBot API Secret  
        timestamp: 時間戳記 (毫秒)
        nonce: 隨機 UUID
        
    Returns:
        Base64 編碼的簽名字串
    """
    # 按照 SwitchBot API 文檔 Python 3 範例
    string_to_sign = f'{token}{timestamp}{nonce}'
    string_to_sign_bytes = string_to_sign.encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    
    signature = base64.b64encode(
        hmac.new(
            secret_bytes, 
            msg=string_to_sign_bytes, 
            digestmod=hashlib.sha256
        ).digest()
    )
    return signature.decode('utf-8')

def get_device_status(device_id: str = None) -> dict:
    """
    取得設備狀態
    
    Args:
        device_id: 設備 ID，預設使用環境變數中的設定
        
    Returns:
        dict: 設備狀態資訊
    """
    target_device_id = device_id or DEVICE_ID
    if not target_device_id:
        raise ValueError("未提供設備 ID")
        
    url = f"https://api.switch-bot.com/v1.1/devices/{target_device_id}/status"
    t = int(time.time() * 1000)
    nonce = str(uuid.uuid4())
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN,
        't': str(t),
        'sign': get_sign(TOKEN, SECRET, t, nonce),
        'nonce': nonce
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        logger.error(f"取得設備狀態失敗: {e}")
        return {'statusCode': 500, 'message': str(e)}

def send_device_command(device_id: str, command: str, parameter: str = None) -> dict:
    """
    傳送命令到設備
    
    Args:
        device_id: 設備 ID
        command: 控制命令 (turnOn, turnOff)
        parameter: 命令參數 (可選)
        
    Returns:
        dict: API 回應結果
    """
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/commands"
    t = int(time.time() * 1000)
    nonce = str(uuid.uuid4())
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN,
        't': str(t),
        'sign': get_sign(TOKEN, SECRET, t, nonce),
        'nonce': nonce
    }
    
    payload = {
        'command': command,
        'commandType': 'command'
    }
    
    if parameter:
        payload['parameter'] = parameter
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        logger.error(f"傳送設備命令失敗: {e}")
        return {'statusCode': 500, 'message': str(e)}

def control_plug(action='status'):
    """
    控制智慧插座
    
    Args:
        action: 操作類型 ('on', 'off', 'status', 'toggle')
        
    Returns:
        操作結果或狀態
    """
    try:
        if action == 'on':
            # 開啟插座
            result = send_device_command(DEVICE_ID, 'turnOn')
            if result.get('statusCode') == 100:
                logger.info(f"✅ 插座 {DEVICE_ID} 已開啟")
                print(f"✅ 插座已開啟")
                
                # 等待狀態更新並驗證
                time.sleep(2)
                status_result = get_device_status(DEVICE_ID)
                if status_result.get('statusCode') == 100:
                    power_state = status_result.get('body', {}).get('power', 'unknown')
                    print(f"📊 目前狀態: {power_state}")
                
                return True
            else:
                print(f"❌ 開啟插座失敗: {result.get('message', '未知錯誤')}")
                return False
            
        elif action == 'off':
            # 關閉插座
            result = send_device_command(DEVICE_ID, 'turnOff')
            if result.get('statusCode') == 100:
                logger.info(f"✅ 插座 {DEVICE_ID} 已關閉")
                print(f"✅ 插座已關閉")
                
                # 等待狀態更新並驗證
                time.sleep(2)
                status_result = get_device_status(DEVICE_ID)
                if status_result.get('statusCode') == 100:
                    power_state = status_result.get('body', {}).get('power', 'unknown')
                    print(f"📊 目前狀態: {power_state}")
                
                return True
            else:
                print(f"❌ 關閉插座失敗: {result.get('message', '未知錯誤')}")
                return False
            
        elif action == 'status':
            # 取得目前狀態
            status_result = get_device_status(DEVICE_ID)
            if status_result.get('statusCode') == 100:
                status_data = status_result.get('body', {})
                power_state = status_data.get('power', 'unknown')
                
                # 顯示詳細狀態
                print(f"📊 插座狀態資訊:")
                print(f"   🆔 設備 ID: {DEVICE_ID}")
                print(f"   🔌 電源狀態: {power_state}")
                
                # 顯示其他可用的狀態資訊
                for key, value in status_data.items():
                    if key != 'power':
                        print(f"   📈 {key}: {value}")
                
                logger.info(f"插座 {DEVICE_ID} 狀態: {power_state}")
                return power_state
            else:
                print(f"❌ 取得狀態失敗: {status_result.get('message', '未知錯誤')}")
                return None
            
        elif action == 'toggle':
            # 切換狀態
            status_result = get_device_status(DEVICE_ID)
            if status_result.get('statusCode') == 100:
                current_power = status_result.get('body', {}).get('power', 'unknown')
                
                if current_power.lower() == 'on':
                    result = send_device_command(DEVICE_ID, 'turnOff')
                    if result.get('statusCode') == 100:
                        print("🔄 插座已從開啟切換為關閉")
                        return True
                else:
                    result = send_device_command(DEVICE_ID, 'turnOn')
                    if result.get('statusCode') == 100:
                        print("🔄 插座已從關閉切換為開啟")
                        return True
                        
                print(f"❌ 切換狀態失敗: {result.get('message', '未知錯誤')}")
                return False
            else:
                print(f"❌ 無法取得目前狀態進行切換: {status_result.get('message', '未知錯誤')}")
                return False
                
        else:
            print(f"❌ 未知操作: {action}")
            print_usage()
            return None
            
    except Exception as e:
        error_msg = f"❌ 操作失敗: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
        
        # 提供除錯建議
        if "401" in str(e) or "Unauthorized" in str(e):
            print("💡 建議: 檢查 Token 和 Secret 是否正確")
        elif "152" in str(e) or "Device not found" in str(e):
            print("💡 建議: 檢查設備 ID 是否正確，執行 get_device_id.py 確認")
        elif "161" in str(e) or "offline" in str(e):
            print("💡 建議: 設備可能離線，檢查設備網路連線")
        
        return None

def print_usage():
    """顯示使用說明"""
    script_name = os.path.basename(__file__)
    print(f"\n📖 使用方式:")
    print(f"   python {script_name} [操作]")
    print(f"\n🎮 可用操作:")
    print(f"   on      - 開啟插座")
    print(f"   off     - 關閉插座")
    print(f"   status  - 查詢狀態 (預設)")
    print(f"   toggle  - 切換狀態")
    print(f"\n📝 範例:")
    print(f"   python {script_name}")          # 查詢狀態
    print(f"   python {script_name} on")       # 開啟插座
    print(f"   python {script_name} off")      # 關閉插座
    print(f"   python {script_name} toggle")   # 切換狀態

def main():
    """主程式"""
    print("🔌 SwitchBot 智慧插座控制工具")
    print("=" * 40)
    
    # 檢查環境設定
    if not check_requirements():
        sys.exit(1)
    
    # 預設操作為狀態查詢
    action = 'status'
    
    # 從命令列參數取得操作
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    
    # 顯示操作資訊
    action_names = {
        'on': '開啟插座',
        'off': '關閉插座', 
        'status': '查詢狀態',
        'toggle': '切換狀態'
    }
    
    print(f"🎯 執行操作: {action_names.get(action, action)}")
    print("-" * 40)
    
    # 執行操作
    try:
        result = control_plug(action)
        
        if action == 'status' and result:
            # 狀態查詢成功
            status_emoji = "🟢" if result.lower() == "on" else "🔴" if result.lower() == "off" else "⚪"
            print(f"\n{status_emoji} 插座目前為: {result.upper()}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中止操作")
    except Exception as e:
        print(f"\n❌ 程式執行失敗: {e}")

if __name__ == "__main__":
    main()
