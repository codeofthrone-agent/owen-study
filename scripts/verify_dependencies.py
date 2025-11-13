#!/usr/bin/env python3
"""
依賴套件驗證腳本
檢查所有必要的 Python 套件是否已正確安裝並可以導入
"""

import sys
import importlib
from typing import List, Tuple, Dict

def check_imports() -> Dict[str, bool]:
    """檢查所有重要的導入"""
    import_tests = {
        # Robot Framework 核心
        'robot': True,
        'robot.api': True,
        'robot.libraries': True,
        
        # 移動測試
        'appium': True,
        'appium.webdriver': True,
        
        # 音訊處理
        'pyaudio': True,
        'numpy': True,
        'pygame': True,
        
        # TTS 引擎
        'gtts': True,
        'pyttsx3': True,
        
        # 系統工具
        'requests': True,
        'dotenv': True,
        
        # 測試工具
        'pytest': True,
        
        # 標準庫 (確認)
        'os': True,
        'sys': True,
        'json': True,
        'time': True,
        'pathlib': True,
        'hmac': True,
        'base64': True,
        'hashlib': True
    }
    
    results = {}
    
    for module_name, required in import_tests.items():
        try:
            importlib.import_module(module_name)
            results[module_name] = True
            print(f"✅ {module_name:<20} - 導入成功")
        except ImportError as e:
            results[module_name] = False
            status = "❌ 必要" if required else "⚠️  可選"
            print(f"{status} {module_name:<20} - 導入失敗: {e}")
        except Exception as e:
            results[module_name] = False
            print(f"❌ {module_name:<20} - 未知錯誤: {e}")
    
    return results

def check_robot_framework_libraries():
    """檢查 Robot Framework 相關庫"""
    print("\n🤖 Robot Framework 庫檢查:")
    
    rf_libraries = [
        'AppiumLibrary',
        'SeleniumLibrary', 
        'RequestsLibrary'
    ]
    
    for lib in rf_libraries:
        try:
            importlib.import_module(f"robot.libraries.{lib}")
            print(f"✅ {lib:<20} - 可用")
        except ImportError:
            # 嘗試從其他路徑導入
            try:
                if lib == 'AppiumLibrary':
                    importlib.import_module('AppiumLibrary')
                elif lib == 'RequestsLibrary':
                    importlib.import_module('RequestsLibrary')
                print(f"✅ {lib:<20} - 可用 (外部安裝)")
            except ImportError:
                print(f"❌ {lib:<20} - 不可用")

def check_custom_modules():
    """檢查自定義模組"""
    print("\n🔧 自定義模組檢查:")
    
    # 添加專案根目錄到 Python 路徑
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    custom_modules = [
        'config.voice_config',
        'config.switchbot_config',
        'libraries.local_voice_verifying.LocalVoiceVerifyingLibrary',
        'libraries.switchbot_smartplug_control.SwitchBotSmartPlugLibrary',
        'libraries.mobile_testing.common.appium_library'
    ]
    
    for module in custom_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module:<50} - 導入成功")
        except ImportError as e:
            print(f"❌ {module:<50} - 導入失敗: {e}")
        except Exception as e:
            print(f"⚠️  {module:<50} - 其他錯誤: {e}")

def main():
    """主函數"""
    print("🔍 Python 依賴套件驗證")
    print("=" * 60)
    print(f"Python 版本: {sys.version}")
    print(f"執行路徑: {sys.executable}")
    print("=" * 60)
    
    print("\n📦 核心套件檢查:")
    results = check_imports()
    
    check_robot_framework_libraries()
    check_custom_modules()
    
    # 統計結果
    total_tests = len(results)
    successful_tests = sum(results.values())
    
    print("\n" + "=" * 60)
    print(f"📊 檢查結果: {successful_tests}/{total_tests} 套件可用")
    
    if successful_tests == total_tests:
        print("🎉 所有必要的套件都已正確安裝！")
        return 0
    else:
        failed_modules = [name for name, success in results.items() if not success]
        print(f"❌ 失敗的套件: {', '.join(failed_modules)}")
        print("\n💡 安裝建議:")
        print("   uv pip install -r requirements.txt")
        print("   或: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
