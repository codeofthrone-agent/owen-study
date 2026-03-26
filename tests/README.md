# 測試目錄結構與規範 (Tests Directory Structure & Guidelines)

此目錄存放專案的所有測試腳本，分為三個核心層次以優化測試效率與維護性。

---

## 📂 目錄結構

```text
tests/
├── unit/                              # 單元測試 (Unit Tests) — 0 個硬體
│   ├── api/                           # - API 伺服器邏輯測試
│   ├── mobile/                        # - 行動裝置控制抽象層測試
│   └── robot_arm/                     # - 手臂協議與配置解析測試
│
├── integration/                       # 整合測試 (Integration Tests) — 1 個硬體
│   ├── ipcam_testing/                 # - 單台 IP Camera 功能驗證
│   ├── mobile/                        # - 單台 Android 手機 Appium 流程
│   ├── power_management/              # - 單台 SwitchBot 智慧插座控制
│   ├── robot_arm/                     # - 單台 MyCobot 手臂動作校準
│   ├── system_maintenance/            # - 系統狀態與磁碟檢查
│   └── voice_control/                 # - 單一音訊設備 (Scarlett) TTS 播放
│
└── e2e/                               # 端對端測試 (End-to-End Tests) — 多個硬體聯動
    ├── login_test.robot               # - 跨平台登錄流程 (多設備)
    ├── robot_arm/                     # - Arm + Cam 二合一視覺整合
    │   └── vision_integration_test.robot
    └── multimodal/                    # - 語音 + UART + 視覺 + 手臂聯動
        ├── multimodal_detection_test.robot
        ├── multimodal_uart_detection_test.robot
        ├── remote_config_validation_test.robot
        ├── uart_audio_detection_test.robot
        └── asrpro/                    # - ASR Pro 語音指令與多感官整合
```

---

## ⚖️ 分類與規範 (Classification Rules)

### 1. 單元測試 (Unit Tests)
- **存放路徑**: `tests/unit/`
- **測試工具**: `pytest`
- **定義範圍**: 純函式邏輯、演算法、通訊協議編解碼。
- **限制條件**: 
  - ❌ 禁止依賴真實硬體 (攝影機、手臂等)。
  - ❌ 禁止依賴外部網路服務。
  - ✅ 必須使用 **MagicMock** 或 **Mock** 模擬所有外部依賴。
- **目標**: 執行速度極快，用於本地開發頻繁驗證。

### 2. 整合測試 (Integration Tests)
- **存放路徑**: `tests/integration/`
- **測試工具**: `Robot Framework`
- **定義範圍**: **單一硬體**功能驗證（如：只有手臂、只有 IP Cam、只有音訊設備）。
- **限制條件**:
  - ✅ 必須連接**一台**真實硬體設備。
  - ❌ 禁止涉及多裝置跨模組聯動場景。
- **目標**: 驗證單一硬體與對應 Library 的介面契約是否正確。

### 3. 端對端測試 (E2E Tests)
- **存放路徑**: `tests/e2e/`
- **測試工具**: `Robot Framework`
- **定義範圍**: **多個硬體同時聯動**的跨模組場景（如：語音 + UART + 攝影機 + 手臂）。
- **限制條件**:
  - ✅ **必須同時連接多台真實硬體**。
  - ✅ 執行前需確認所有硬體狀態與校準。
- **目標**: 最後一道防線，驗證多裝置整合是否達到預期使用場景。

---

## 🚀 執行指令 (Execution Commands)

### 執行單元測試
```bash
uv run pytest tests/unit/
```

### 執行整合測試
```bash
uv run robot tests/integration/
```

### 執行端對端測試 (依標籤過濾)
```bash
# 執行冒煙測試 (重要場景)
uv run robot --include smoke tests/e2e/

# 執行特定領域 (例如多感官)
uv run robot tests/e2e/multimodal/
```

---

## ✍️ 注意事項
- **路徑引用**: 所有 `.robot` 文件必須使用相對路徑引用 `../../../resources/` 下的關鍵字庫。
- **環境配置**: 部份 E2E 測試依賴 `.env` 內的硬體路徑 (如 SERIAL_PORT)，請確保環境變數已正確設定。
