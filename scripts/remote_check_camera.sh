#!/bin/bash
# 遠端檢查 Jetson Nano 攝影機狀態
# 用途：透過 SSH 檢查 Jetson Nano 上的攝影機設備

JETSON_IP="10.42.0.180"
JETSON_USER="${JETSON_USER:-jetson}"  # 預設使用者名稱

echo "=========================================="
echo "遠端攝影機診斷工具"
echo "=========================================="
echo "目標主機: ${JETSON_USER}@${JETSON_IP}"
echo ""

# 檢查 SSH 連接
echo "1. 檢查 SSH 連接..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes ${JETSON_USER}@${JETSON_IP} exit 2>/dev/null; then
    echo "   ✅ SSH 連接正常"
else
    echo "   ❌ SSH 連接失敗"
    echo ""
    echo "請確認："
    echo "1. Jetson Nano SSH 服務已啟動"
    echo "2. 已設定 SSH 金鑰（免密碼登入）"
    echo "3. 使用者名稱正確（預設: jetson）"
    echo ""
    echo "設定 SSH 金鑰方法："
    echo "   ssh-copy-id ${JETSON_USER}@${JETSON_IP}"
    echo ""
    echo "或手動指定使用者："
    echo "   JETSON_USER=your_username $0"
    exit 1
fi
echo ""

# 檢查攝影機設備
echo "2. 檢查攝影機設備..."
echo "----------------------------------------"
ssh ${JETSON_USER}@${JETSON_IP} "ls -l /dev/video*" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "   ✅ 發現攝影機設備"
else
    echo "   ❌ 找不到攝影機設備"
    echo "   請檢查："
    echo "   - USB 攝影機是否已連接"
    echo "   - CSI 攝影機排線是否正確安裝"
fi
echo ""

# 檢查 robot_arm_server.py 運行狀態
echo "3. 檢查 robot_arm_server.py 運行狀態..."
echo "----------------------------------------"
SERVER_PID=$(ssh ${JETSON_USER}@${JETSON_IP} "pgrep -f 'robot_arm_server.py'" 2>/dev/null)
if [ -n "$SERVER_PID" ]; then
    echo "   ✅ robot_arm_server.py 正在運行 (PID: $SERVER_PID)"

    # 檢查是否有 --enable-vision 參數
    echo ""
    echo "   檢查啟動參數:"
    ssh ${JETSON_USER}@${JETSON_IP} "ps aux | grep robot_arm_server.py | grep -v grep"
    echo "----------------------------------------"

    if ssh ${JETSON_USER}@${JETSON_IP} "ps aux | grep robot_arm_server.py | grep -v grep | grep -q -- '--enable-vision'"; then
        echo "   ✅ 視覺檢測功能已啟用 (--enable-vision)"
    else
        echo "   ⚠️  視覺檢測功能未啟用"
        echo "   請重新啟動伺服器並加入 --enable-vision 參數："
        echo "   python3 scripts/robot_arm_server.py --enable-vision --host 10.42.0.180 --port 9000"
    fi
else
    echo "   ❌ robot_arm_server.py 未運行"
    echo "   請在 Jetson Nano 上啟動："
    echo "   python3 scripts/robot_arm_server.py --enable-vision --host 10.42.0.180 --port 9000"
fi
echo ""

# 測試攝影機擷取
echo "4. 測試攝影機擷取（需要 OpenCV）..."
ssh ${JETSON_USER}@${JETSON_IP} "python3 -c '
import cv2
import sys

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print(\"   ❌ 無法開啟攝影機\")
    sys.exit(1)

ret, frame = cap.read()
cap.release()

if ret:
    print(f\"   ✅ 成功擷取影像 (解析度: {frame.shape[1]}x{frame.shape[0]})\")
else:
    print(\"   ❌ 無法擷取影像\")
    sys.exit(1)
'" 2>/dev/null

echo ""
echo "=========================================="
echo "診斷完成"
echo "=========================================="
