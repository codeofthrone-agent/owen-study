# 機器手臂視覺檢測測試案例說明

**文檔版本：** v1.0.0
**建立日期：** 2025-11-13
**Phase:** Phase 3 - Robot Framework 整合

---

## 📋 測試檔案概覽

本目錄包含三個視覺檢測測試檔案，涵蓋不同測試需求：

### 1. `vision_quick_test.robot` - 快速煙霧測試
**用途：** 開發階段快速驗證，CI/CD 流程整合
**測試案例數：** 2
**執行時間：** < 30 秒
**適用場景：**
- 快速驗證視覺檢測功能是否正常
- 每次修改後的冒煙測試
- CI/CD 流水線的健康檢查

**測試內容：**
- ✅ 單一按鈕檢測（Light1）
- ✅ 批次檢測（Light1-3）

**執行方式：**
```bash
robot tests/robot_arm/vision_quick_test.robot
```

---

### 2. `vision_detection_test.robot` - 完整功能測試
**用途：** 完整的視覺檢測功能驗證
**測試案例數：** 10
**執行時間：** 5-10 分鐘
**適用場景：**
- 全面測試視覺檢測功能
- 回歸測試
- 發布前的驗證測試

**測試內容：**

#### 基礎檢測測試（3 個）
1. **測試案例 01** - 檢測單一按鈕的燈光狀態（Light1）
2. **測試案例 02** - 驗證按鈕燈光顏色為藍色
3. **測試案例 03** - 驗證按鈕燈光狀態為關閉

#### 批次檢測測試（2 個）
4. **測試案例 04** - 批次檢測多個按鈕的燈光狀態（3 個）
5. **測試案例 05** - 檢測所有燈光按鈕（Light1-8）

#### 整合測試（2 個）
6. **測試案例 06** - 按壓按鈕後驗證燈光切換（Light1）
7. **測試案例 07** - 等待按鈕變為藍色（輪詢檢測）

#### 負面測試（3 個）
8. **測試案例 08** - 輪詢等待超時測試
9. **測試案例 09** - 檢測未校準按鈕
10. **測試案例 10** - 連續檢測穩定性測試（10 次）

**執行方式：**
```bash
# 執行所有測試
robot tests/robot_arm/vision_detection_test.robot

# 執行特定標籤
robot --include vision tests/robot_arm/vision_detection_test.robot
robot --include negative tests/robot_arm/vision_detection_test.robot
robot --include stability tests/robot_arm/vision_detection_test.robot
```

**測試標籤：**
- `vision` - 所有視覺檢測測試
- `single` - 單一按鈕檢測
- `batch` - 批次檢測
- `polling` - 輪詢機制
- `timeout` - 超時測試
- `negative` - 負面測試
- `error` - 錯誤處理
- `stability` - 穩定性測試
- `stress` - 壓力測試

---

### 3. `vision_integration_test.robot` - 整合場景測試
**用途：** 真實使用場景的端到端測試
**測試案例數：** 5
**執行時間：** 5-8 分鐘
**適用場景：**
- 驗證視覺檢測與按鈕控制的整合
- 模擬真實使用流程
- 系統整合測試

**測試場景：**

1. **場景 01** - Light1 按鈕完整切換流程
   - 檢測初始狀態 → 按壓按鈕 → 檢測新狀態 → 驗證改變

2. **場景 02** - 批次檢測後批次切換
   - 批次檢測 Light1-3 → 依序按壓 → 批次檢測 → 驗證全部改變

3. **場景 03** - 按壓後輪詢等待特定顏色
   - 按壓按鈕 → 輪詢等待藍色 → 驗證成功

4. **場景 04** - 多次切換穩定性測試
   - 連續切換 Light1 按鈕 5 次，驗證穩定性

5. **場景 05** - 錯誤恢復測試
   - 觸發錯誤（檢測未校準按鈕）→ 驗證系統恢復

**執行方式：**
```bash
robot tests/robot_arm/vision_integration_test.robot
```

---

## 🔧 前置條件

所有測試執行前需要確認：

### 硬體需求
- ✅ MyCobot 280 機器手臂已連接到 Jetson Nano
- ✅ 機器手臂已上電（power_on）
- ✅ 攝影機已連接（/dev/video0）
- ✅ Jetson Nano 可透過網路訪問（預設 IP: 10.42.0.180）

### 軟體需求
- ✅ Jetson Nano 上的 `robot_arm_server.py` 已啟動
- ✅ 視覺檢測系統已啟用（--enable-vision）
- ✅ 所有測試按鈕已完成 ROI 校準

### ROI 校準確認
```bash
# 檢查配置檔案
cat config/robot_arm/button_positions.yaml | grep -A 10 "vision:"

# 執行校準（如需要）
python3 scripts/calibrate_button_roi.py
```

---

## 📊 測試報告

### 執行所有測試並產生報告
```bash
# 執行所有視覺檢測測試
robot --outputdir results/vision_detection \
      --loglevel DEBUG \
      tests/robot_arm/vision_*test.robot

# 查看報告
firefox results/vision_detection/report.html
```

### 只執行快速測試（CI/CD）
```bash
robot --outputdir results/quick_test \
      tests/robot_arm/vision_quick_test.robot
```

---

## 🎯 測試覆蓋範圍

### 關鍵字覆蓋

| 關鍵字 | Quick | Detection | Integration |
|--------|-------|-----------|-------------|
| `When 用戶檢測第 "${button_id}" 按鈕的燈光狀態` | ✅ | ✅ | ✅ |
| `Then 按鈕燈光應該為 "${expected_color}" 色` | ❌ | ✅ | ❌ |
| `Then 按鈕燈光應該為 "${expected_state}" 狀態` | ❌ | ✅ | ❌ |
| `When 用戶檢測多個按鈕的燈光狀態` | ✅ | ✅ | ✅ |
| `When 用戶等待按鈕 "${button_id}" 變為 "${color}" 色` | ❌ | ✅ | ✅ |
| `取得最後檢測結果` | ❌ | ❌ | ✅ |
| `取得批次檢測結果` | ❌ | ❌ | ✅ |

### 測試類型覆蓋

| 測試類型 | Quick | Detection | Integration |
|----------|-------|-----------|-------------|
| 冒煙測試 | ✅ | ❌ | ❌ |
| 功能測試 | ❌ | ✅ | ❌ |
| 整合測試 | ❌ | ✅ | ✅ |
| 負面測試 | ❌ | ✅ | ✅ |
| 穩定性測試 | ❌ | ✅ | ✅ |
| 場景測試 | ❌ | ❌ | ✅ |

---

## 🐛 故障排除

### 問題 1: 連接失敗
**錯誤訊息：**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**解決方案：**
```bash
# 1. 確認伺服器正在運行
ssh user@10.42.0.180
ps aux | grep robot_arm_server

# 2. 重新啟動伺服器
python3 scripts/robot_arm_server.py --host 10.42.0.180 --port 9000
```

---

### 問題 2: ROI 未校準
**錯誤訊息：**
```
ValueError: 按鈕 'light1' 未校準視覺檢測 ROI
```

**解決方案：**
```bash
# 執行 ROI 校準工具
python3 scripts/calibrate_button_roi.py

# 或只校準特定按鈕
python3 scripts/calibrate_button_roi.py --skip-existing
```

---

### 問題 3: 視覺檢測失敗
**錯誤訊息：**
```
RuntimeError: 檢測失敗: 視覺檢測系統未啟用
```

**解決方案：**
```bash
# 確認攝影機連接
ls -l /dev/video0

# 重新啟動伺服器並啟用視覺系統
python3 scripts/robot_arm_server.py --enable-vision
```

---

### 問題 4: 測試結果不穩定
**症狀：** 同一按鈕多次檢測結果不一致

**可能原因：**
- LED PWM 頻率干擾
- 環境光線變化
- ROI 選擇不當

**解決方案：**
```bash
# 1. 調整多幀平均數量（預設 5）
# 編輯 RobotArmKeywords.py
# command = {"command": "detect_button", "num_frames": 10}  # 增加到 10

# 2. 重新校準 ROI（確保完整包含按鈕）
python3 scripts/calibrate_button_roi.py

# 3. 調整亮度閾值
# 編輯 config/robot_arm/button_positions.yaml
# brightness_threshold: 120  # 原為 100
```

---

## 📚 相關文檔

- [視覺檢測設計文檔](../../docs/robot_arm_vision_detection_design.md)
- [ROI 校準操作指南](../../docs/robot_arm_vision_calibration_guide.md)
- [機器手臂伺服器使用指南](../../docs/robot_arm_server_usage.md)
- [按鈕配置說明](../../libraries/robot_arm_control/BUTTON_SETUP_GUIDE.md)
- [RobotArmKeywords 文檔](../../libraries/robot_arm_control/README.md)

---

## 🎓 最佳實踐

### 1. 測試執行順序
建議按以下順序執行：
1. **快速測試** - 確認基本功能正常
2. **功能測試** - 完整驗證所有功能
3. **整合測試** - 驗證真實使用場景

### 2. 持續整合（CI/CD）
```yaml
# .github/workflows/vision-detection-test.yml
- name: Run Vision Detection Tests
  run: |
    robot --outputdir results/ci \
          --loglevel INFO \
          tests/robot_arm/vision_quick_test.robot
```

### 3. 本地開發流程
```bash
# 1. 修改 RobotArmKeywords.py
vim libraries/robot_arm_control/RobotArmKeywords.py

# 2. 執行快速測試
robot tests/robot_arm/vision_quick_test.robot

# 3. 如果通過，執行完整測試
robot tests/robot_arm/vision_detection_test.robot

# 4. 最後執行整合測試
robot tests/robot_arm/vision_integration_test.robot
```

---

## 📈 未來規劃

### Phase 4 計劃
- [ ] 顏色檢測準確度優化
- [ ] 多相機支援（雙目視覺）
- [ ] 深度學習模型整合（YOLO 按鈕檢測）
- [ ] 自動 ROI 校準（無需手動框選）
- [ ] 性能壓力測試（100+ 按鈕）

---

**文檔維護：** 如有問題或建議，請更新此文檔並記錄變更日期。
