#!/usr/bin/env python3
"""
測試 LocalVoiceVerifyingLibrary 初始化過程
"""
import sys
import os

# 添加 library 路徑
library_path = os.path.join(os.path.dirname(__file__), 'libraries', 'local_voice_verifying')
sys.path.insert(0, library_path)

def test_imports():
    """測試匯入功能"""
    print("=== 測試匯入功能 ===")
    try:
        print("1. 測試 voice_config 匯入...")
        # 嘗試從新的 config 套件匯入
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            from config.voice_config import ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG
        except ImportError:
            from voice_config import ROBOT_CONFIG, AUDIO_CONFIG, TTS_CONFIG
        print("   ✓ voice_config 匯入成功")
    except Exception as e:
        print(f"   ✗ voice_config 匯入失敗: {e}")
        return False
    
    try:
        print("2. 測試 voice_tts_manager 匯入...")
        from voice_tts_manager import TTSManager
        print("   ✓ voice_tts_manager 匯入成功")
    except Exception as e:
        print(f"   ✗ voice_tts_manager 匯入失敗: {e}")
        return False
    
    try:
        print("3. 測試 voice_audio_recorder 匯入...")
        from voice_audio_recorder import AudioRecorder
        print("   ✓ voice_audio_recorder 匯入成功")
    except Exception as e:
        print(f"   ✗ voice_audio_recorder 匯入失敗: {e}")
        return False
    
    try:
        print("4. 測試 voice_sound_detector 匯入...")
        from voice_sound_detector import SoundDetector
        print("   ✓ voice_sound_detector 匯入成功")
    except Exception as e:
        print(f"   ✗ voice_sound_detector 匯入失敗: {e}")
        return False
    
    return True

def test_individual_module_init():
    """測試個別模組初始化"""
    print("\n=== 測試個別模組初始化 ===")
    
    try:
        print("1. 初始化 TTSManager...")
        from voice_tts_manager import TTSManager
        tts = TTSManager()
        print("   ✓ TTSManager 初始化成功")
    except Exception as e:
        print(f"   ✗ TTSManager 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("2. 初始化 AudioRecorder...")
        from voice_audio_recorder import AudioRecorder
        recorder = AudioRecorder()
        print("   ✓ AudioRecorder 初始化成功")
    except Exception as e:
        print(f"   ✗ AudioRecorder 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("3. 初始化 SoundDetector...")
        from voice_sound_detector import SoundDetector
        detector = SoundDetector()
        print("   ✓ SoundDetector 初始化成功")
    except Exception as e:
        print(f"   ✗ SoundDetector 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_library_init():
    """測試 Library 完整初始化"""
    print("\n=== 測試 Library 完整初始化 ===")
    
    try:
        print("初始化 LocalVoiceVerifyingLibrary...")
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        library = LocalVoiceVerifyingLibrary()
        print(f"   初始化狀態: {library.is_initialized}")
        
        if library.is_initialized:
            print("   ✓ LocalVoiceVerifyingLibrary 初始化成功")
            return True
        else:
            print("   ✗ LocalVoiceVerifyingLibrary 初始化失敗 (is_initialized=False)")
            return False
            
    except Exception as e:
        print(f"   ✗ LocalVoiceVerifyingLibrary 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("開始測試 LocalVoiceVerifyingLibrary 初始化...")
    
    # 測試匯入
    if not test_imports():
        print("\n❌ 匯入測試失敗，停止後續測試")
        return
    
    # 測試個別模組初始化
    if not test_individual_module_init():
        print("\n❌ 個別模組初始化測試失敗，停止後續測試")
        return
    
    # 測試完整 Library 初始化
    if not test_library_init():
        print("\n❌ Library 初始化測試失敗")
        return
    
    print("\n✅ 所有測試通過！")

if __name__ == "__main__":
    main()
