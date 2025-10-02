#!/bin/bash
# Robot Framework 测试运行脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  音频播放 Robot Framework 测试"
echo "========================================"
echo ""

# 检查 Robot Framework 是否安装
if ! command -v robot &> /dev/null; then
    echo "❌ 错误: Robot Framework 未安装"
    echo "请运行: pip3 install robotframework"
    exit 1
fi

echo "✅ Robot Framework 已安装"
echo ""

# 显示使用说明
show_usage() {
    echo "使用方法:"
    echo "  $0                    # 运行基础测试"
    echo "  $0 advanced           # 运行高级测试"
    echo "  $0 all                # 运行所有测试"
    echo "  $0 tag <标签名>       # 运行特定标签的测试"
    echo ""
    echo "可用标签:"
    echo "  channel-1, channel-2, channel-3, channel-4"
    echo "  all-channels, setup, routing, playback, negative, stress"
}

# 根据参数运行不同的测试
case "${1:-basic}" in
    basic)
        echo "运行基础测试套件..."
        robot --outputdir "$SCRIPT_DIR/reports" "$SCRIPT_DIR/audio_test.robot"
        ;;
    advanced)
        echo "运行高级测试套件..."
        robot --outputdir "$SCRIPT_DIR/reports" "$SCRIPT_DIR/advanced_audio_test.robot"
        ;;
    all)
        echo "运行所有测试套件..."
        robot --outputdir "$SCRIPT_DIR/reports" "$SCRIPT_DIR/audio_test.robot" "$SCRIPT_DIR/advanced_audio_test.robot"
        ;;
    tag)
        if [ -z "$2" ]; then
            echo "错误: 请指定标签名"
            show_usage
            exit 1
        fi
        echo "运行标签为 '$2' 的测试..."
        robot --outputdir "$SCRIPT_DIR/reports" --include "$2" "$SCRIPT_DIR/advanced_audio_test.robot"
        ;;
    help|-h|--help)
        show_usage
        exit 0
        ;;
    *)
        echo "错误: 未知选项 '$1'"
        show_usage
        exit 1
        ;;
esac

EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 测试完成"
else
    echo "❌ 测试失败"
fi
echo "========================================"
echo ""
echo "查看详细报告: $SCRIPT_DIR/reports/report.html"
echo "查看日志: $SCRIPT_DIR/reports/log.html"

exit $EXIT_CODE
