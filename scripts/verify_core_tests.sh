#!/bin/bash

# Robot Framework 核心測試套件驗證腳本
# 日期: 2025-06-27
# 目的: 驗證 Robot Framework 語法修復後的測試執行狀態

echo "=== Robot Framework 核心測試套件驗證 ==="
echo "執行時間: $(date)"
echo "測試模式: demo (不需要實際設備)"
echo ""

# 切換到專案目錄
cd /home/thortron/Tools/robot-multiplatform-automation

# 執行核心測試套件
echo "🔄 執行核心 iOS 測試套件..."
robot --variable TEST_MODE:demo \
      --outputdir results/verification \
      --output verification_output.xml \
      --log verification_log.html \
      --report verification_report.html \
      tests/mobile/ios/ios_safari_framework_test.robot \
      tests/mobile/ios/basic_ios_test.robot \
      tests/mobile/ios/simplified_ios_test.robot

# 檢查執行結果
exit_code=$?

echo ""
echo "=== 測試執行結果 ==="
if [ $exit_code -eq 0 ]; then
    echo "✅ 所有核心測試通過！"
    echo "📊 測試報告: results/verification/verification_report.html"
    echo "📋 詳細日誌: results/verification/verification_log.html"
else
    echo "❌ 部分測試失敗，請檢查日誌"
    echo "🔍 錯誤代碼: $exit_code"
fi

echo ""
echo "=== 快速統計 ==="
if [ -f "results/verification/verification_output.xml" ]; then
    echo "測試檔案已生成，詳細結果請查看報告"
else
    echo "⚠️  測試檔案未生成，可能存在配置問題"
fi

echo ""
echo "執行完成時間: $(date)"
