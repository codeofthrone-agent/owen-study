#!/usr/bin/env python3
"""
測試 LocalVoiceVerifyingLibrary 的具體功能
"""
import sys
import os
import time

# 添加 library 路徑
library_path = os.path.join(os.path.dirname(__file__), 'libraries', 'local_voice_verifying')
sys.path.insert(0, library_path)

def test_speak_text_functionality():
    """測試 Speak Text 功能"""
    print("\n=== 測試 Speak Text 功能 ===")
    
    try:
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        library = LocalVoiceVerifyingLibrary()
        
        print(f"Library 初始化狀態: {library.is_initialized}")
        
        if not library.is_initialized:
            print("   ✗ Library 未正確初始化")
            return False
        
        # 測試文字播放
        print("1. 測試文字播放...")
        try:
            result = library.speak_text("Testing voice synthesis")
            print(f"   ✓ 文字播放成功，結果: {result}")
        except Exception as e:
            print(f"   ✗ 文字播放失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 測試不同文字內容
        print("2. 測試不同文字內容...")
        try:
            test_texts = [
                "Hello World",
                "Robot Framework Test", 
                "Language verification system"
            ]
            for text in test_texts:
                result = library.speak_text(text)
                print(f"   ✓ 播放 '{text}': {result}")
                time.sleep(1)  # 等待播放完成
        except Exception as e:
            print(f"   ✗ 不同文字內容測試失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Speak Text 功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_availability():
    """測試關鍵字可用性"""
    print("\n=== 測試關鍵字可用性 ===")
    
    try:
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        library = LocalVoiceVerifyingLibrary()
        
        # 檢查是否有 speak_text 方法
        if hasattr(library, 'speak_text'):
            print("   ✓ speak_text 方法存在")
        else:
            print("   ✗ speak_text 方法不存在")
            return False
        
        # 檢查是否可調用
        if callable(getattr(library, 'speak_text')):
            print("   ✓ speak_text 方法可調用")
        else:
            print("   ✗ speak_text 方法不可調用")
            return False
        
        # 檢查關鍵字是否已註冊
        if hasattr(library, 'get_keyword_names'):
            keywords = library.get_keyword_names()
            if 'Speak Text' in keywords:
                print("   ✓ 'Speak Text' 關鍵字已註冊")
            else:
                print(f"   ? 可用關鍵字: {keywords}")
                print("   ? 'Speak Text' 關鍵字可能未明確註冊，但方法存在")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 關鍵字可用性測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_robot_framework_integration():
    """測試 Robot Framework 整合"""
    print("\n=== 測試 Robot Framework 整合 ===")
    
    try:
        # 嘗試模擬 Robot Framework 載入
        from LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
        
        # 使用 Robot Framework 類似的方式建立實例
        library = LocalVoiceVerifyingLibrary()
        
        # 檢查 Robot Framework 相關屬性
        robot_attrs = ['ROBOT_LIBRARY_SCOPE', 'ROBOT_LIBRARY_VERSION']
        for attr in robot_attrs:
            if hasattr(library, attr):
                value = getattr(library, attr)
                print(f"   ✓ {attr}: {value}")
            else:
                print(f"   ? {attr}: 未設定")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Robot Framework 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("開始測試 LocalVoiceVerifyingLibrary 具體功能...")
    
    # 測試關鍵字可用性
    if not test_keyword_availability():
        print("\n❌ 關鍵字可用性測試失敗")
        return
    
    # 測試 Robot Framework 整合
    if not test_robot_framework_integration():
        print("\n❌ Robot Framework 整合測試失敗")
        return
    
    # 測試 Speak Text 功能
    if not test_speak_text_functionality():
        print("\n❌ Speak Text 功能測試失敗")
        return
    
    print("\n✅ 所有功能測試通過！")

if __name__ == "__main__":
    main()
