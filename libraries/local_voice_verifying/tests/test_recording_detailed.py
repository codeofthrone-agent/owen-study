#!/usr/bin/env python3
"""
詳細測試 Library 錄音功能
"""
import sys
import os
import time

# 添加 library 路徑
library_path = os.path.join(os.path.dirname(__file__), 'libraries', 'local_voice_verifying')
sys.path.insert(0, library_path)

def test_library_recording_detailed():
    """詳細測試 Library 錄音功能"""
    print("=== 詳細測試 Library 錄音功能 ===")
    
    try:
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        library = LocalVoiceVerifyingLibrary()
        
        print(f"1. 檢查 Library 初始化狀態: {library.is_initialized}")
        
        if not library.is_initialized:
            print("   ✗ Library 未正確初始化")
            return False
        
        # 檢查 audio_recorder 是否存在
        if hasattr(library, 'audio_recorder'):
            print("2. ✓ audio_recorder 屬性存在")
            print(f"   audio_recorder 類型: {type(library.audio_recorder)}")
        else:
            print("2. ✗ audio_recorder 屬性不存在")
            return False
        
        # 檢查錄音狀態
        print(f"3. 檢查初始錄音狀態: {library.audio_recorder.is_recording}")
        
        print("4. 開始錄音...")
        start_result = library.start_voice_recording(3)
        print(f"   開始錄音結果: {start_result}")
        
        # 檢查錄音狀態
        print(f"5. 檢查錄音中狀態: {library.audio_recorder.is_recording}")
        
        print("6. 等待錄音完成...")
        time.sleep(4)  # 錄音 3 秒 + 1 秒緩衝
        
        # 檢查錄音狀態
        print(f"7. 錄音完成前狀態: {library.audio_recorder.is_recording}")
        
        print("8. 停止錄音...")
        
        # 直接呼叫 Library 的 stop_voice_recording 方法
        file_path = library.stop_voice_recording()
        print(f"   錄音檔案路徑: {file_path}")
        
        if file_path:
            print("   ✓ 錄音檔案保存成功")
            
            # 檢查檔案是否存在
            if os.path.exists(file_path):
                print(f"       ✓ 檔案確實存在: {file_path}")
                
                # 檢查檔案大小
                file_size = os.path.getsize(file_path)
                print(f"       檔案大小: {file_size} bytes")
                
                return True
            else:
                print(f"       ✗ 檔案不存在: {file_path}")
                return False
        else:
            print("   ✗ 錄音檔案保存失敗")
            return False
        
    except Exception as e:
        print(f"   ✗ 詳細測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("開始詳細測試錄音功能...")
    
    if test_library_recording_detailed():
        print("\n✅ 詳細錄音測試通過！")
    else:
        print("\n❌ 詳細錄音測試失敗")

if __name__ == "__main__":
    main()
