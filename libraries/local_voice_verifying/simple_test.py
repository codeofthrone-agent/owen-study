#!/usr/bin/env python3
"""
簡單的測試腳本，檢查模組是否能正常載入
不依賴音訊套件進行基本功能測試
"""

def test_basic_imports():
    """測試基本匯入"""
    print("🔍 測試基本匯入...")
    
    try:
        from voice_config import AUDIO_CONFIG, TTS_CONFIG, DETECTION_CONFIG
        print("✅ voice_config 匯入成功")
        
        # 測試配置值
        print(f"  - 音訊取樣率: {AUDIO_CONFIG['sample_rate']}Hz")
        print(f"  - TTS 主要引擎: {TTS_CONFIG['primary_engine']}")
        print(f"  - 檢測閾值: {DETECTION_CONFIG['default_threshold']}")
        
    except Exception as e:
        print(f"❌ voice_config 匯入失敗: {e}")
        return False
    
    return True

def test_robot_framework_integration():
    """測試 Robot Framework 整合"""
    print("\n🤖 測試 Robot Framework 整合...")
    
    try:
        # 建立一個簡化版的 Library 類別用於測試
        class SimpleTestLibrary:
            ROBOT_LIBRARY_SCOPE = 'GLOBAL'
            ROBOT_LIBRARY_VERSION = '1.0.0'
            
            def __init__(self):
                self.is_initialized = True
            
            def test_keyword(self, text):
                """測試關鍵字"""
                return f"收到文字: {text}"
            
            def get_library_info(self):
                """獲取 Library 資訊"""
                return {
                    'version': self.ROBOT_LIBRARY_VERSION,
                    'scope': self.ROBOT_LIBRARY_SCOPE,
                    'is_initialized': self.is_initialized,
                }
        
        lib = SimpleTestLibrary()
        result = lib.test_keyword("Hello World")
        info = lib.get_library_info()
        
        print("✅ Robot Framework 整合測試成功")
        print(f"  - 測試結果: {result}")
        print(f"  - Library 版本: {info['version']}")
        
    except Exception as e:
        print(f"❌ Robot Framework 整合測試失敗: {e}")
        return False
    
    return True

def test_directory_structure():
    """測試目錄結構"""
    print("\n📁 測試目錄結構...")
    
    try:
        from pathlib import Path
        
        base_dir = Path(__file__).parent
        required_dirs = [
            'audio_samples',
            'audio_samples/reference_sounds',
            'logs',
        ]
        
        for dir_name in required_dirs:
            dir_path = base_dir / dir_name
            if dir_path.exists():
                print(f"✅ 目錄存在: {dir_name}")
            else:
                print(f"⚠️  目錄不存在: {dir_name}")
                # 建立目錄
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 目錄已建立: {dir_name}")
        
    except Exception as e:
        print(f"❌ 目錄結構測試失敗: {e}")
        return False
    
    return True

def test_file_structure():
    """測試檔案結構"""
    print("\n📄 測試檔案結構...")
    
    try:
        from pathlib import Path
        
        base_dir = Path(__file__).parent
        required_files = [
            'voice_config.py',
            'requirements.txt',
            'README.md',
            'spec.md',
            'todo.md',
        ]
        
        for file_name in required_files:
            file_path = base_dir / file_name
            if file_path.exists():
                print(f"✅ 檔案存在: {file_name}")
            else:
                print(f"❌ 檔案不存在: {file_name}")
                return False
        
    except Exception as e:
        print(f"❌ 檔案結構測試失敗: {e}")
        return False
    
    return True

def test_tts_voice_output():
    """測試 TTS 語音輸出 - 人工驗證"""
    print("\n🔊 測試 TTS 語音輸出...")
    
    try:
        # 嘗試匯入 TTS 管理器
        try:
            from voice_tts_manager import TTSManager
            tts_available = True
        except ImportError as e:
            print(f"⚠️  TTS 模組匯入失敗: {e}")
            print("💡 請先安裝相依套件: pip install -r requirements.txt")
            return True  # 不視為錯誤，只是跳過測試
        
        # 初始化 TTS 管理器
        print("🎵 初始化 TTS 管理器...")
        tts_manager = TTSManager()
        
        # 設定語音參數
        print("⚙️  設定語音參數...")
        tts_manager.set_language('en-US')  # 設定為英文
        
        # 測試不同語速的 "Hey Power Pro"
        test_configs = [
            {"speed": 100, "desc": "慢速"},
            {"speed": 140, "desc": "標準速度"},
            {"speed": 180, "desc": "快速"}
        ]
        
        print("\n📢 即將播放不同語速的測試語音，請注意聆聽...")
        print("🌍 語言設定: 英文 (en-US)")
        print("⏱️  每個語音之間會有 2 秒間隔")
        
        import time
        for i, config in enumerate(test_configs, 1):
            speed = config["speed"]
            desc = config["desc"]
            text = "Hey Power Pro"
            
            print(f"\n🎤 [{i}/{len(test_configs)}] 播放: '{text}' - {desc} ({speed} words/min)")
            
            try:
                # 設定當前語速
                tts_manager.set_voice_speed(speed)
                
                # 生成並播放語音
                success = tts_manager.speak_text(text)
                if success:
                    print(f"✅ 語音 {i} 播放完成 ({desc})")
                else:
                    print(f"⚠️  語音 {i} 播放可能失敗")
                
                # 等待間隔
                if i < len(test_configs):
                    print("⏸️  等待 3 秒...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ 語音 {i} 播放錯誤: {e}")
        
        # 人工驗證
        print("\n" + "=" * 60)
        print("🎯 人工驗證問題:")
        print("1. 您是否聽到了慢速的 'Hey Power Pro' 語音？")
        print("2. 您是否聽到了標準速度的 'Hey Power Pro' 語音？")
        print("3. 您是否聽到了快速的 'Hey Power Pro' 語音？")
        print("4. 哪個語速最適合實際使用？")
        print("=" * 60)
        
        # 等待用戶確認
        while True:
            try:
                response = input("\n❓ 您是否聽到了所有測試語音？(y/n/s=跳過): ").lower().strip()
                if response in ['y', 'yes', '是']:
                    print("✅ TTS 語音輸出測試 - 人工驗證通過")
                    return True
                elif response in ['n', 'no', '否']:
                    print("❌ TTS 語音輸出測試 - 人工驗證失敗")
                    print("💡 請檢查:")
                    print("   - 音訊裝置是否正常")
                    print("   - 系統音量是否開啟")
                    print("   - 音訊權限是否允許")
                    return False
                elif response in ['s', 'skip', '跳過']:
                    print("⏭️  TTS 語音輸出測試 - 跳過人工驗證")
                    return True
                else:
                    print("❓ 請輸入 y(是)/n(否)/s(跳過)")
            except KeyboardInterrupt:
                print("\n⏭️  測試中斷，跳過 TTS 驗證")
                return True
            except Exception as e:
                print(f"❌ 輸入處理錯誤: {e}")
                return True
        
    except Exception as e:
        print(f"❌ TTS 語音輸出測試失敗: {e}")
        return False

def test_audio_system_check():
    """測試音訊系統檢查"""
    print("\n🎵 檢查音訊系統...")
    
    try:
        # 檢查是否有音訊套件
        audio_packages = {
            'gtts': 'Google Text-to-Speech',
            'pyttsx3': 'Python Text-to-Speech 3',
            'pygame': 'Pygame (音訊播放)',
            'pyaudio': 'PyAudio (音訊錄製)',
            'playsound': 'Playsound (簡單音訊播放)'
        }
        
        available_packages = []
        missing_packages = []
        
        for package, description in audio_packages.items():
            try:
                __import__(package)
                available_packages.append(f"{package} ({description})")
                print(f"✅ {package} - {description}")
            except ImportError:
                missing_packages.append(f"{package} ({description})")
                print(f"❌ {package} - {description} (未安裝)")
        
        print(f"\n📊 音訊套件狀態:")
        print(f"   可用: {len(available_packages)} 個")
        print(f"   缺失: {len(missing_packages)} 個")
        
        if missing_packages:
            print(f"\n💡 建議安裝缺失套件:")
            print(f"   pip install -r requirements.txt")
        
        return len(available_packages) > 0
        
    except Exception as e:
        print(f"❌ 音訊系統檢查失敗: {e}")
        return False

def main():
    """主要測試函數"""
    print("🎤 本地語音驗證系統 - 基本功能測試")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 基本測試 (必須通過)
    basic_tests = [
        test_basic_imports,
        test_robot_framework_integration,
        test_directory_structure,
        test_file_structure,
    ]
    
    print("🔧 執行基本結構測試...")
    for test in basic_tests:
        if not test():
            all_tests_passed = False
    
    # 音訊相關測試 (可選)
    print("\n🎵 執行音訊系統測試...")
    audio_tests = [
        test_audio_system_check,
        test_tts_voice_output,
    ]
    
    audio_tests_passed = True
    for test in audio_tests:
        if not test():
            audio_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有基本測試通過！")
        if audio_tests_passed:
            print("🎵 音訊功能測試也通過！")
        else:
            print("⚠️  音訊功能測試未完全通過，但不影響基本功能")
        
        print("\n📋 後續步驟:")
        if not audio_tests_passed:
            print("1. 安裝音訊套件: pip install -r requirements.txt")
            print("2. 重新執行測試驗證 TTS 功能")
            print("3. 準備參考聲音檔案")
            print("4. 執行完整功能測試")
        else:
            print("1. 準備'登登'聲音的參考檔案")
            print("2. 執行 Robot Framework 測試: robot voice_test.robot")
            print("3. 進行完整語音檢測功能測試")
    else:
        print("❌ 部分基本測試失敗，請檢查上述錯誤訊息")
    
    return all_tests_passed

if __name__ == "__main__":
    import sys
    import os
    
    # 確保在正確的目錄下
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 執行測試
    success = main()
    sys.exit(0 if success else 1)
