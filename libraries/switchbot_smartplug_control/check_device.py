"""
SwitchBot 設備檢查工具

基於參考專案 codeofthrone/switchbot_smartplug_control 開發
用於檢查設備詳細資訊和可用方法
"""
import os
import sys
import inspect
from pathlib import Path
import requests
import hmac
import hashlib
import base64
import uuid
import time

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

# 我們現在使用直接 HTTP API 而不是 pyswitchbot SDK
REQUESTS_AVAILABLE = True

# 載入環境設定
if not CONFIG_AVAILABLE and DOTENV_AVAILABLE:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    load_dotenv(current_dir / '.env')
    load_dotenv(project_root / '.env')

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
    """檢查必要的環境設定"""
    if not all([TOKEN, SECRET, DEVICE_ID]):
        print("❌ 錯誤: 缺少必要的環境變數")
        print("📋 請設定以下環境變數:")
        print("   - SWITCHBOT_TOKEN")
        print("   - SWITCHBOT_SECRET") 
        print("   - SWITCHBOT_DEVICE_ID")
        print()
        print("🔧 設定方式:")
        print("   1. 複製 .env.example 為 .env")
        print("   2. 編輯 .env 檔案，填入您的認證資訊")
        print("   3. 執行 get_device_id.py 取得設備 ID")
        return False
    
    return True

def analyze_device():
    """分析設備詳細資訊"""
    try:
        print("🔗 正在連接 SwitchBot API...")
        
        # 先取得所有設備資訊，驗證設備是否存在
        print("📋 取得設備列表...")
        devices_result = get_devices()
        
        if devices_result.get('statusCode') != 100:
            print(f"❌ 無法取得設備列表: {devices_result.get('message', '未知錯誤')}")
            return False
        
        # 找到目標設備
        target_device = None
        device_list = devices_result.get('body', {}).get('deviceList', [])
        
        for device in device_list:
            if device.get('deviceId') == DEVICE_ID:
                target_device = device
                break
        
        if not target_device:
            print(f"❌ 設備 {DEVICE_ID} 不在設備列表中")
            print("📋 可用設備:")
            for device in device_list:
                print(f"   🆔 {device.get('deviceId')} - {device.get('deviceName')} ({device.get('deviceType')})")
            return False
        
        print("✅ 設備找到!")
        print("=" * 60)
        
        # 設備基本資訊
        print("📱 設備基本資訊:")
        print(f"   🆔 設備 ID: {target_device.get('deviceId')}")
        print(f"   📝 設備名稱: {target_device.get('deviceName')}")
        print(f"   🏷️  設備類型: {target_device.get('deviceType')}")
        print(f"   🏠 Hub 設備 ID: {target_device.get('hubDeviceId', 'N/A')}")
        print(f"   � 雲端服務: {target_device.get('enableCloudService', 'N/A')}")
        
        # 取得設備狀態
        print("\n📊 設備狀態:")
        print("-" * 60)
        
        status_result = get_device_status(DEVICE_ID)
        if status_result.get('statusCode') == 100:
            status_data = status_result.get('body', {})
            
            print("✅ 狀態查詢成功:")
            for key, value in status_data.items():
                if key == 'power':
                    emoji = "🔌" if value == 'on' else "⚫"
                    print(f"   {emoji} {key}: {value}")
                elif key == 'voltage':
                    print(f"   ⚡ {key}: {value} V")
                elif key == 'electricCurrent':
                    print(f"   🔋 {key}: {value} mA")
                elif key == 'electricityOfDay':
                    print(f"   📊 {key}: {value} Wh (今日用電)")
                elif key == 'weight':
                    print(f"   ⚖️  {key}: {value} W (功率)")
                else:
                    print(f"   � {key}: {value}")
        else:
            print(f"❌ 狀態查詢失敗: {status_result.get('message', '未知錯誤')}")
        
        # API 連接測試
        print("\n🧪 API 連接測試:")
        print("-" * 60)
        
        # 測試開關命令
        print("⚠️  注意: 以下測試會實際控制設備!")
        confirmation = input("是否繼續測試開關命令? (y/N): ").lower().strip()
        
        if confirmation in ['y', 'yes']:
            print("🔄 測試開關命令...")
            
            # 取得目前狀態
            current_status = get_device_status(DEVICE_ID)
            if current_status.get('statusCode') == 100:
                current_power = current_status.get('body', {}).get('power', 'unknown')
                print(f"� 目前狀態: {current_power}")
                
                # 暫時切換狀態然後恢復
                if current_power == 'on':
                    print("🔄 測試: 關閉 -> 開啟")
                    off_result = send_device_command(DEVICE_ID, 'turnOff')
                    if off_result.get('statusCode') == 100:
                        print("✅ 關閉命令成功")
                        time.sleep(3)  # 等待狀態更新
                        
                        on_result = send_device_command(DEVICE_ID, 'turnOn')
                        if on_result.get('statusCode') == 100:
                            print("✅ 開啟命令成功，狀態已恢復")
                        else:
                            print(f"❌ 開啟命令失敗: {on_result.get('message')}")
                    else:
                        print(f"❌ 關閉命令失敗: {off_result.get('message')}")
                
                elif current_power == 'off':
                    print("🔄 測試: 開啟 -> 關閉")
                    on_result = send_device_command(DEVICE_ID, 'turnOn')
                    if on_result.get('statusCode') == 100:
                        print("✅ 開啟命令成功")
                        time.sleep(3)  # 等待狀態更新
                        
                        off_result = send_device_command(DEVICE_ID, 'turnOff')
                        if off_result.get('statusCode') == 100:
                            print("✅ 關閉命令成功，狀態已恢復")
                        else:
                            print(f"❌ 關閉命令失敗: {off_result.get('message')}")
                    else:
                        print(f"❌ 開啟命令失敗: {on_result.get('message')}")
        else:
            print("⏭️  跳過開關測試")
        
        print("\n✅ 設備分析完成!")
        return True
        
    except Exception as e:
        print(f"❌ 設備分析失敗: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 設備檢查失敗: {e}")
        
        # 提供除錯建議
        if "401" in str(e) or "Unauthorized" in str(e):
            print("💡 建議: 檢查 Token 和 Secret 是否正確")
        elif "152" in str(e) or "Device not found" in str(e):
            print("💡 建議: 檢查設備 ID 是否正確")
            print("   執行 python get_device_id.py 確認設備清單")
        elif "timeout" in str(e).lower():
            print("💡 建議: 檢查網路連線")

def get_sign(token: str, secret: str, timestamp: int, nonce: str) -> str:
    """產生 SwitchBot API 簽名"""
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

def get_device_status(device_id: str) -> dict:
    """取得設備狀態"""
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/status"
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
        return {'statusCode': 500, 'message': str(e)}

def get_devices():
    """取得所有設備"""
    url = "https://api.switch-bot.com/v1.1/devices"
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
        return {'statusCode': 500, 'message': str(e)}

def send_device_command(device_id: str, command: str, parameter: str = None) -> dict:
    """傳送命令到設備"""
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
        return {'statusCode': 500, 'message': str(e)}

def main():
    """主程式"""
    print("🔍 SwitchBot 設備檢查工具")
    print("=" * 50)
    
    # 檢查環境設定
    if not check_requirements():
        sys.exit(1)
    
    # 執行設備分析
    try:
        analyze_device()
    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中止操作")
    except Exception as e:
        print(f"\n❌ 程式執行失敗: {e}")

if __name__ == "__main__":
    main()
