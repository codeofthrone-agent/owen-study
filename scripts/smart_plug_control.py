#!/usr/bin/env python3
"""
SwitchBot 智慧插座控制硬編碼脚本 (Standalone Script)

開發用途: 快速控制指定的 SwitchBot 智慧插座，無需環境變數配置。
日期: 2026-04-09
功能: 支援開啟、關閉、查詢狀態與切換插座電源。
使用方式: python scripts/smart_plug_control.py [on|off|status|toggle]
"""

import sys
import time
import requests
import hmac
import hashlib
import base64
import uuid
import json

# ==========================================
# 硬編碼配置 (Hard-coded Credentials)
# ==========================================
TOKEN = '94e1ac14c55ec739caef6491fb96e2fd420ddd49ca4dc7844a79848a26c1fa6e460f7298dd43629760fc1494a707b153'
SECRET = 'b3d8488be6dc200dcf4acfab65053957'
DEVICE_ID = '3C84279C35E2'
# ==========================================

def get_sign(token: str, secret: str, timestamp: int, nonce: str) -> str:
    """
    產生 SwitchBot API 簽名
    Generate SwitchBot API signature using HMAC-SHA256
    """
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
    """
    取得設備狀態
    Get current device status from SwitchBot API
    """
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

def send_device_command(device_id: str, command: str, parameter: str = 'default') -> dict:
    """
    傳送命令到設備
    Send a command (turnOn/turnOff) to the SwitchBot device
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
        'parameter': parameter,
        'commandType': 'command'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        return {'statusCode': 500, 'message': str(e)}

def control_plug(action='status'):
    """
    核心控制邏輯
    Core control logic for the smart plug
    """
    try:
        if action == 'on':
            result = send_device_command(DEVICE_ID, 'turnOn')
            if result.get('statusCode') == 100:
                print(f"✨ \033[92m成功:\033[0m 插座已開啟 (ON)")
                return True
            else:
                print(f"❌ \033[91m錯誤:\033[0m {result.get('message', '未知錯誤')}")
                return False
            
        elif action == 'off':
            result = send_device_command(DEVICE_ID, 'turnOff')
            if result.get('statusCode') == 100:
                print(f"✨ \033[94m成功:\033[0m 插座已關閉 (OFF)")
                return True
            else:
                print(f"❌ \033[91m錯誤:\033[0m {result.get('message', '未知錯誤')}")
                return False
            
        elif action == 'status':
            status_result = get_device_status(DEVICE_ID)
            if status_result.get('statusCode') == 100:
                status_data = status_result.get('body', {})
                power_state = status_data.get('power', 'unknown')
                
                print(f"\n💎 \033[1mSwitchBot 智慧插座狀態清單\033[0m")
                print(f"{"="*40}")
                print(f"🆔 設備 ID: {DEVICE_ID}")
                
                state_color = "\033[92m" if power_state.lower() == 'on' else "\033[94m"
                print(f"🔌 電源狀態: {state_color}{power_state.upper()}\033[0m")
                
                for key, value in status_data.items():
                    if key != 'power':
                        print(f"📈 {key}: {value}")
                print(f"{"="*40}\n")
                return power_state
            else:
                print(f"❌ \033[91m錯誤:\033[0m {status_result.get('message', '未知錯誤')}")
                return None
            
        elif action == 'toggle':
            status_result = get_device_status(DEVICE_ID)
            if status_result.get('statusCode') == 100:
                current_power = status_result.get('body', {}).get('power', 'unknown')
                new_action = 'off' if current_power.lower() == 'on' else 'on'
                print(f"🔄 偵測到目前狀態為 {current_power.upper()}，正在切換為 {new_action.upper()}...")
                return control_plug(new_action)
            else:
                print(f"❌ \033[91m錯誤:\033[0m 無法取得狀態以進行切換")
                return False
        else:
            print(f"❌ \033[91m未知操作:\033[0m {action}")
            return None
            
    except Exception as e:
        print(f"💥 \033[91m拋出異常:\033[0m {str(e)}")
        return None

def main():
    """主程式進入點"""
    # 支援彩色終端輸出 (ANSI Colors)
    print("\n\033[1;36m⚡ SwitchBot Plug Professional Controller ⚡\033[0m")
    print("\033[36m" + "━" * 40 + "\033[0m")
    
    action = 'status'
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    
    control_plug(action)

if __name__ == "__main__":
    main()
