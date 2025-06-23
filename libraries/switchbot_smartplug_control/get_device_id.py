"""
SwitchBot 設備 ID 取得工具

基於參考專案 codeofthrone/switchbot_smartplug_control 開發
用於列出所有 SwitchBot 設備及其 ID，方便後續的設備控制
"""
import requests
import hmac
import hashlib
import base64
import time
import json
import os
import sys
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

# 嘗試載入 python-dotenv (回退方案)
if not CONFIG_AVAILABLE:
    try:
        from dotenv import load_dotenv
        # 載入當前目錄和父目錄的 .env 檔案
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        
        load_dotenv(current_dir / '.env')
        load_dotenv(project_root / '.env')
        DOTENV_AVAILABLE = True
    except ImportError:
        DOTENV_AVAILABLE = False
        print("注意: python-dotenv 未安裝，將直接從環境變數讀取設定")

# 從統一配置或環境變數讀取設定
if CONFIG_AVAILABLE:
    TOKEN = SWITCHBOT_CREDENTIALS['token']
    SECRET = SWITCHBOT_CREDENTIALS['secret']
else:
    TOKEN = os.getenv('TOKEN') or os.getenv('SWITCHBOT_TOKEN')
    SECRET = os.getenv('SECRET') or os.getenv('SWITCHBOT_SECRET')

def check_requirements():
    """檢查必要的環境設定"""
    if not TOKEN or not SECRET:
        print("❌ 錯誤: 缺少必要的環境變數")
        print("📋 請設定以下環境變數:")
        print("   - SWITCHBOT_TOKEN: 您的 SwitchBot API Token")
        print("   - SWITCHBOT_SECRET: 您的 SwitchBot API Secret")
        print()
        print("🔧 設定方式:")
        print("   1. 複製 .env.example 為 .env")
        print("   2. 編輯 .env 檔案，填入您的 API 認證資訊")
        print("   3. 或者直接設定環境變數:")
        print("      export SWITCHBOT_TOKEN='your_token_here'")
        print("      export SWITCHBOT_SECRET='your_secret_here'")
        print()
        print("🔑 如何取得 API 認證資訊:")
        print("   1. 開啟 SwitchBot App")
        print("   2. 進入「個人檔案」>「偏好設定」")
        print("   3. 點擊「App 版本」10次開啟開發者選項")
        print("   4. 複製 Token 和 Secret")
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

def get_devices():
    """
    取得所有 SwitchBot 設備
    
    Returns:
        dict: API 回應結果
    """
    import uuid
    
    url = "https://api.switch-bot.com/v1.1/devices"
    t = int(time.time() * 1000)
    nonce = str(uuid.uuid4())
    sign = get_sign(TOKEN, SECRET, t, nonce)
    
    headers = {
        "Authorization": TOKEN,
        "sign": sign,
        "nonce": nonce,
        "t": str(t),
        "Content-Type": "application/json; charset=utf8"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API 請求失敗: {e}")
        return {"statusCode": 500, "message": str(e)}

def format_device_list(devices, title):
    """
    格式化設備清單顯示
    
    Args:
        devices: 設備清單
        title: 標題
    """
    if not devices:
        return
        
    print(f"\n🔌 {title} ({len(devices)} 個):")
    print("=" * 60)
    
    for i, device in enumerate(devices, 1):
        device_id = device.get("deviceId", "N/A")
        device_name = device.get("deviceName", "未命名")
        device_type = device.get("deviceType") or device.get("remoteType", "未知類型")
        
        print(f"{i:2d}. 📱 名稱: {device_name}")
        print(f"    🆔 ID: {device_id}")
        print(f"    🏷️  類型: {device_type}")
        print("-" * 60)

def save_device_config(devices, infrared_devices):
    """
    儲存設備配置到檔案
    
    Args:
        devices: 一般設備清單
        infrared_devices: 紅外線設備清單
    """
    try:
        config_file = Path(__file__).parent / "devices_config.json"
        
        config_data = {
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "devices": devices,
            "infrared_devices": infrared_devices,
            "total_count": len(devices) + len(infrared_devices)
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 設備配置已儲存至: {config_file}")
        
    except Exception as e:
        print(f"⚠️  儲存設備配置失敗: {e}")

def main():
    """主程式"""
    print("🔍 SwitchBot 設備 ID 取得工具")
    print("=" * 50)
    
    # 檢查環境設定
    if not check_requirements():
        sys.exit(1)
    
    print("🔗 正在連接 SwitchBot API...")
    
    try:
        result = get_devices()
        
        if result.get("statusCode") == 100:
            body = result.get("body", {})
            devices = body.get("deviceList", [])
            infrared_devices = body.get("infraredRemoteList", [])
            
            print("✅ API 連接成功!")
            
            # 顯示一般設備
            if devices:
                format_device_list(devices, "智慧設備")
            
            # 顯示紅外線設備  
            if infrared_devices:
                format_device_list(infrared_devices, "紅外線遙控設備")
            
            # 顯示總結
            total_devices = len(devices) + len(infrared_devices)
            print(f"\n📊 總結:")
            print(f"   🔌 智慧設備: {len(devices)} 個")
            print(f"   📡 紅外線設備: {len(infrared_devices)} 個")
            print(f"   📱 總計: {total_devices} 個設備")
            
            # 儲存配置
            if total_devices > 0:
                save_device_config(devices, infrared_devices)
                
                # 建議後續步驟
                print(f"\n🎯 後續步驟:")
                print(f"   1. 複製需要的設備 ID")
                print(f"   2. 更新 .env 檔案中的 SWITCHBOT_DEVICE_ID")
                print(f"   3. 使用 plug_control.py 或 Robot Framework 測試控制設備")
            else:
                print("\n⚠️  未找到任何設備，請檢查:")
                print("   1. SwitchBot App 中是否已新增設備")
                print("   2. 設備是否正常連線")
                print("   3. API Token 和 Secret 是否正確")
                
        else:
            error_code = result.get("statusCode", "未知")
            error_msg = result.get("message", "未知錯誤")
            print(f"❌ API 錯誤 ({error_code}): {error_msg}")
            
            # 常見錯誤提示
            if error_code == 401:
                print("💡 建議: 檢查 Token 和 Secret 是否正確")
            elif error_code == 429:
                print("💡 建議: API 請求過於頻繁，請稍後再試")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中止操作")
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        print("💡 請檢查網路連線和 API 認證資訊")

if __name__ == "__main__":
    main()
