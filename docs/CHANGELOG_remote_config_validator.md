# RemoteSystemConfigValidator 更新日誌

## v1.1.0 (2025-11-11)

### 新增功能

#### 🎯 重複執行錯誤檢測
- **新增錯誤模式**: `duplicate_execution`
- **檢測場景**: 同一行出現兩次 `/uvoice/start_uvoice.sh`
- **問題範例**: `/uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh`
- **原因**: 通常由 sed 替換錯誤造成

#### 🔧 改進 sed 修正策略
**v1.0.0 策略（舊）:**
```python
# 單一 sed 替換命令
fix_cmd = (
    f"sed -i 's|^\\([ \\t]*\\)/uvoice/start_uvoice\\.sh.*$|\\1{correct_config}|' "
    f"{config_path}"
)
```

**問題:**
- 正規表達式 `.*$` 無法正確匹配整行
- 導致產生重複執行的錯誤配置

**v1.1.0 策略（新）:**
```python
# 兩步驟 sed 操作
# 步驟 1: 刪除所有包含 start_uvoice.sh 的行
delete_cmd = f"sed -i '/\\/uvoice\\/start_uvoice\\.sh/d' {config_path}"

# 步驟 2: 在 bt_gatt_server 之後插入正確配置
insert_cmd = f"sed -i '/bt_gatt_server/a\\\\\\t{correct_config}' {config_path}"
```

**優點:**
- ✅ 徹底移除所有錯誤配置，避免殘留
- ✅ 精確插入位置，保持縮排
- ✅ 不受原配置格式影響
- ✅ 支援重複執行錯誤修正

### 新增工具

#### 📦 輔助腳本
1. **`scripts/restore_emmc_backup.py`**
   - 恢復備份的配置檔案
   - 用於修正失敗後的回滾操作

2. **`scripts/check_current_config.py`**
   - 檢查目前遠端設備的配置
   - 顯示完整配置和 start_uvoice 相關行

3. **`scripts/quick_fix_emmc.sh`**
   - 一鍵修正腳本（Shell 版本）
   - 自動處理虛擬環境啟用

### 測試結果

#### ✅ 支援的錯誤模式修正
- `duplicate_execution` - 重複執行（新增）
- `output_to_null` - 輸出到 /dev/null
- `no_redirect` - 沒有重導向
- `no_background` - 沒有背景執行

#### ✅ 測試案例
1. **重複執行修正測試**
   - 原始: `/uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh`
   - 修正後: `/uvoice/start_uvoice.sh > /dev/ttyS0 &`
   - 狀態: ✅ 通過

2. **無背景執行修正測試**
   - 原始: `/uvoice/start_uvoice.sh`
   - 修正後: `/uvoice/start_uvoice.sh > /dev/ttyS0 &`
   - 狀態: ✅ 通過

### 文檔更新

#### 📚 更新的文檔
1. **`docs/remote_config_validator_guide.md`**
   - 新增重複執行錯誤說明
   - 新增 sed 修正策略改進章節
   - 更新版本號為 v1.1.0

2. **`scripts/README_validate_remote_uart_config.md`**
   - 新增重複執行錯誤故障排除
   - 新增輔助工具使用說明
   - 更新功能特色列表

3. **`docs/CHANGELOG_remote_config_validator.md`** (新增)
   - 完整的更新日誌

### 版本號更新

- **RemoteSystemConfigValidator**: `1.0.0` → `1.1.0`
- **SerialLogParser**: `1.2.0` → `1.2.1` (整合新版 RemoteSystemConfigValidator)

### Bug 修正

#### 🐛 修正的問題
1. **sed 替換導致配置重複**
   - **問題**: 使用 `.*$` 正規表達式無法正確匹配完整行
   - **影響**: 產生 `/uvoice/start_uvoice.sh > /dev/ttyS0    /uvoice/start_uvoice.sh` 錯誤配置
   - **修正**: 改用兩步驟 sed 操作（刪除 + 插入）

2. **錯誤配置無法檢測**
   - **問題**: v1.0.0 無法檢測重複執行的錯誤
   - **影響**: 修正失敗後無法再次檢測
   - **修正**: 新增 `duplicate_execution` 錯誤模式

### 向下相容性

✅ **完全向下相容**
- API 介面無變更
- Robot Framework 關鍵字無變更
- 僅內部實作改進

### 升級指南

無需特別操作，直接使用即可：

```bash
# 更新程式碼
git pull

# 執行驗證
uv run python3 scripts/validate_remote_uart_config.py
```

如果之前有配置錯誤，新版本會自動檢測並修正。

---

## v1.0.0 (2025-11-11)

### 初始版本

#### ✨ 核心功能
- UART 串列埠通訊
- 遠端命令執行
- 配置檢查（3 種錯誤模式）
- 自動修正
- 重開機提示
- Robot Framework 整合

#### 📋 支援的錯誤模式
- `output_to_null` - 輸出到 /dev/null
- `no_redirect` - 沒有重導向
- `no_background` - 沒有背景執行

#### 🔧 標記式回應解析
- 唯一標記生成
- 精確命令完成判斷
- 避免超時截斷

#### 📚 文檔
- 完整使用指南
- Python API 文檔
- Robot Framework 範例
- 故障排除指南

---

**維護者**: Robot Automation Team
**聯絡方式**: 專案 GitHub Issues
