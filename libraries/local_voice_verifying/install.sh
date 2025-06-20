#!/bin/bash

# 本地語音驗證系統安裝腳本
# 適用於 macOS 系統

echo "🎤 本地語音驗證系統安裝腳本"
echo "=================================="

# 檢查 Python 版本
echo "📋 檢查 Python 版本..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python 版本符合要求: $python_version"
else
    echo "❌ Python 版本過舊: $python_version，需要 $required_version 或更新版本"
    exit 1
fi

# 檢查是否在專案目錄下
if [ ! -f "libraries/local_voice_verifying/requirements.txt" ]; then
    echo "❌ 請在專案根目錄下執行此腳本"
    exit 1
fi

# 建立虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo "🔧 建立 Python 虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "🔧 啟動虛擬環境..."
source venv/bin/activate

# 更新 pip
echo "📦 更新 pip..."
pip install --upgrade pip

# 檢查 macOS 系統相依性
echo "🍎 檢查 macOS 系統相依性..."

# 檢查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未偵測到 Homebrew，請先安裝 Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
else
    echo "✅ Homebrew 已安裝"
fi

# 安裝 portaudio (pyaudio 需要)
echo "🔧 安裝 portaudio..."
brew install portaudio

# 安裝 Python 套件
echo "📦 安裝 Python 套件..."
cd libraries/local_voice_verifying

# 特殊處理 pyaudio 安裝
echo "🔧 安裝 pyaudio..."
pip install pyaudio

# 安裝其他套件
echo "📦 安裝其他相依套件..."
pip install -r requirements.txt

cd ../..

# 建立必要目錄
echo "📁 建立必要目錄..."
mkdir -p libraries/local_voice_verifying/audio_samples/reference_sounds
mkdir -p libraries/local_voice_verifying/audio_samples/recorded
mkdir -p libraries/local_voice_verifying/audio_samples/temp
mkdir -p libraries/local_voice_verifying/logs
mkdir -p libraries/local_voice_verifying/test_data
mkdir -p libraries/local_voice_verifying/models

# 設定權限
echo "🔐 設定檔案權限..."
chmod +x libraries/local_voice_verifying/*.py

# 測試安裝
echo "🧪 測試安裝..."
python3 -c "
try:
    from libraries.local_voice_verifying.LocalVoiceVerifyingLibrary import LocalVoiceVerifyingLibrary
    lib = LocalVoiceVerifyingLibrary()
    info = lib.get_library_info()
    print('✅ Library 載入成功')
    print(f'   版本: {info.get(\"version\", \"未知\")}')
    print(f'   初始化狀態: {info.get(\"is_initialized\", False)}')
    lib.cleanup_audio_resources()
except ImportError as e:
    print(f'❌ 套件匯入失敗: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Library 初始化失敗: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 安裝完成！"
    echo ""
    echo "📋 後續步驟:"
    echo "1. 將參考聲音檔案放置到 libraries/local_voice_verifying/audio_samples/reference_sounds/"
    echo "2. 確保麥克風權限已開啟（系統偏好設定 → 安全性與隱私 → 隱私權 → 麥克風）"
    echo "3. 執行測試: robot tests/physical_interaction/voice_test.robot"
    echo ""
    echo "🔧 使用方式:"
    echo "  # 啟動虛擬環境"
    echo "  source venv/bin/activate"
    echo "  "
    echo "  # 執行 Robot Framework 測試"
    echo "  robot tests/physical_interaction/voice_test.robot"
    echo ""
else
    echo "❌ 安裝過程中發生錯誤，請檢查上述訊息"
    exit 1
fi
