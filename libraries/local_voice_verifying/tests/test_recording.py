#!/usr/bin/env python3
"""
測試 AudioRecorder 錄音功能
"""
import sys
import os
import time

# 添加 library 路徑
library_path = os.path.join(os.path.dirname(__file__), 'libraries', 'local_voice_verifying')
sys.path.insert(0, library_path)

def test_audio_recorder():
    """測試音訊錄製器"""
    print("=== 測試 AudioRecorder ===")
    
    try:
        from voice_audio_recorder import AudioRecorder
        recorder = AudioRecorder()
        
        print("1. 檢查錄製器初始化...")
        print(f"   錄製器狀態: 初始化完成")
        print(f"   取樣率: {recorder.sample_rate}")
        print(f"   聲道數: {recorder.channels}")
        
        print("2. 開始錄音...")
        success = recorder.start_recording()
        print(f"   開始錄音結果: {success}")
        
        if success:
            print("3. 錄音 3 秒...")
            time.sleep(3)
            
            print("4. 停止錄音...")
            stop_success = recorder.stop_recording()
            print(f"   停止錄音結果: {stop_success}")
            
            print("5. 檢查音訊數據...")
            audio_data = recorder.get_audio_data()
            print(f"   音訊數據長度: {len(audio_data)}")
            print(f"   音訊數據類型: {type(audio_data)}")
            
            if len(audio_data) > 0:
                print("6. 保存音訊檔案...")
                file_path = recorder.save_audio("test_recording.wav")
                print(f"   檔案路徑: {file_path}")
                return file_path is not None
            else:
                print("   ✗ 沒有音訊數據")
                return False
        else:
            print("   ✗ 無法開始錄音")
            return False
            
    except Exception as e:
        print(f"   ✗ AudioRecorder 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_library_recording():
    """測試 Library 錄音功能"""
    print("\n=== 測試 Library 錄音功能 ===")
    
    try:
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        library = LocalVoiceVerifyingLibrary()
        
        print("1. 開始錄音...")
        start_result = library.start_voice_recording(3)
        print(f"   開始錄音結果: {start_result}")
        
        print("2. 等待錄音完成...")
        time.sleep(4)  # 錄音 3 秒 + 1 秒緩衝
        
        print("3. 停止錄音...")
        file_path = library.stop_voice_recording()
        print(f"   錄音檔案路徑: {file_path}")
        
        return file_path is not None and file_path != ""
        
    except Exception as e:
        print(f"   ✗ Library 錄音測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("開始測試錄音功能...")
    
    # 測試 AudioRecorder
    if not test_audio_recorder():
        print("\n❌ AudioRecorder 測試失敗")
        return
    
    # 測試 Library 錄音功能
    if not test_library_recording():
        print("\n❌ Library 錄音測試失敗")
        return
    
    print("\n✅ 所有錄音測試通過！")

if __name__ == "__main__":
    main()
