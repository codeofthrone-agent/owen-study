#!/bin/bash

# 設定預設執行時間為 8 小時 (秒)
DURATION=${1:-28800} 
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

# 建立基礎結果目錄
BASE_OUTPUT_DIR="results/stress_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BASE_OUTPUT_DIR"

echo "========== 開始 8 小時壓力測試 =========="
echo "預計執行時間: $((DURATION / 3600)) 小時"
echo "結果存放目錄: $BASE_OUTPUT_DIR"
echo "========================================"

# 設定休息機制：每工作 1 小時 (3600秒)，休息 15 分鐘 (900秒)
WORK_INTERVAL=3600
REST_DURATION=900
NEXT_REST_TIME=$((START_TIME + WORK_INTERVAL))

count=1
while [ $(date +%s) -lt $END_TIME ]; do
    # 檢查是否達到休息時間
    current_timestamp=$(date +%s)
    if [ $current_timestamp -ge $NEXT_REST_TIME ]; then
        echo "========================================"
        echo "🕒 已工作 1 小時，開始休息 15 分鐘..."
        echo "   休息開始時間: $(date)"
        sleep $REST_DURATION
        echo "   休息結束時間: $(date)"
        echo "========================================"
        
        # 更新下一次休息時間 (重置工作計時)
        # 注意：如果您希望壓力測試的總"工作"時間固定，則 END_TIME 應該也要順延。
        # 但這裡假設 DURATION 是總掛機時間，因此休息時間包含在內。
        # 如果要順延 END_TIME 請取消註解下一行：
        # END_TIME=$((END_TIME + REST_DURATION))
        
        NEXT_REST_TIME=$(( $(date +%s) + WORK_INTERVAL ))
    fi

    current_time=$(date +%Y%m%d_%H%M%S)
    output_dir="$BASE_OUTPUT_DIR/run_${count}_${current_time}"
    
    echo "正在執行第 $count 輪測試... (開始時間: $(date))"
    
    # 執行 Robot Framework 測試 (使用 uv run)
    # --outputdir 指定每次執行的獨立輸出目錄，避免覆蓋
    uv run robot --outputdir "$output_dir" tests/robot_arm/test_tapei_buttons.robot
    
    # 檢查測試是否成功 (可選：若失敗是否中斷？目前設定為繼續跑)
    if [ $? -eq 0 ]; then
        echo "第 $count 輪測試: PASS"
    else
        echo "第 $count 輪測試: FAIL"
        # 如果希望失敗即停止，請取消註解下一行
        # break
    fi
    
    echo "----------------------------------------"
    ((count++))
    
    # 短暫休息，避免過度密集 (可選)
    sleep 5
done

echo "========== 壓力測試結束 =========="
echo "總執行輪數: $((count - 1))"
echo "結束時間: $(date)"
