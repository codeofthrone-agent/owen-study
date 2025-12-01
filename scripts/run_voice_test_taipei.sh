#!/bin/bash

# 設定專案根目錄
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 產生時間戳記
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="output/run_${TIMESTAMP}"

# 建立輸出目錄
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  執行語音控制測試 (Taipei Lab)"
echo "  輸出目錄: $OUTPUT_DIR"
echo "========================================"

# 執行測試
uv run robot --outputdir "$OUTPUT_DIR" tests/test_voice_commands_taipei.robot

EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 測試完成"
else
    echo "❌ 測試失敗"
fi
echo "========================================"
echo "報告位置: $OUTPUT_DIR/report.html"
echo "日誌位置: $OUTPUT_DIR/log.html"

exit $EXIT_CODE
