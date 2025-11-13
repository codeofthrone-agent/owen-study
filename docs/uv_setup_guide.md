# UV 套件管理使用指南

## 📖 關於 UV

**UV** 是由 Astral 開發的超快速 Python 套件管理工具，作為 pip、pip-tools、pipenv 的現代化替代方案。

### 主要優勢

⚡ **極致效能** - 比 pip 快 10-100 倍
🔒 **可靠性** - 完整的依賴解析與鎖定
🎯 **簡潔易用** - 單一工具取代多個套件管理工具
📦 **虛擬環境整合** - 自動管理虛擬環境
🚀 **現代化** - 使用 Rust 開發，支援最新 Python 標準

---

## 🚀 安裝 UV

### Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 驗證安裝

```bash
uv --version
```

---

## 💻 基本使用

### 1. 建立虛擬環境

```bash
# 在專案根目錄建立虛擬環境
uv venv

# 自訂虛擬環境名稱
uv venv .venv-dev

# 指定 Python 版本
uv venv --python 3.12
```

### 2. 啟動虛擬環境

#### Linux / macOS

```bash
source .venv/bin/activate
```

#### Windows

```powershell
.venv\Scripts\activate
```

### 3. 安裝套件

```bash
# 從 requirements.txt 安裝
uv pip install -r requirements.txt

# 安裝單一套件
uv pip install opencv-python

# 安裝多個套件
uv pip install opencv-python pyyaml loguru

# 安裝特定版本
uv pip install robotframework==7.3.1
```

### 4. 直接執行（無需啟動環境）

```bash
# uv run 會自動管理虛擬環境
uv run python3 scripts/quick_multi_light_test.py
uv run robot tests/ipcam_testing/multi_light_array_test.robot
uv run pytest tests/
```

---

## 🔧 專案特定指令

### 初始化專案環境

```bash
# 第一次設置專案
cd /home/thortron/Tools/robot-multiplatform-automation

# 建立虛擬環境
uv venv

# 啟動環境
source .venv/bin/activate

# 安裝所有依賴
uv pip install -r requirements.txt

# 設定 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 執行測試

```bash
# 使用 uv run（推薦）
uv run robot tests/

# 或啟動環境後執行
source .venv/bin/activate
robot tests/
```

### 執行多燈號陣列偵測

```bash
# 快速測試
uv run python3 scripts/quick_multi_light_test.py

# 視覺化工具
uv run python3 scripts/visualize_light_array.py --interactive

# Robot Framework 測試
uv run robot tests/ipcam_testing/multi_light_array_test.robot
```

---

## 📦 套件管理

### 安裝新套件

```bash
# 安裝並更新 requirements.txt
uv pip install new-package

# 手動加入 requirements.txt
echo "new-package>=1.0.0" >> requirements.txt
uv pip install -r requirements.txt
```

### 更新套件

```bash
# 更新單一套件
uv pip install --upgrade opencv-python

# 更新所有套件
uv pip install --upgrade -r requirements.txt
```

### 移除套件

```bash
uv pip uninstall package-name
```

### 查看已安裝套件

```bash
uv pip list
```

---

## 🔄 從 Pipenv 遷移到 UV

### 步驟 1: 匯出依賴

```bash
# 從 Pipfile 產生 requirements.txt（如果尚未建立）
pipenv requirements > requirements.txt
```

### 步驟 2: 建立 UV 環境

```bash
# 建立虛擬環境
uv venv

# 啟動環境
source .venv/bin/activate

# 安裝依賴
uv pip install -r requirements.txt
```

### 步驟 3: 驗證

```bash
# 執行測試確認環境正確
uv run robot tests/

# 或
source .venv/bin/activate
robot tests/
```

### 步驟 4: 清理 (可選)

```bash
# 移除 Pipenv 環境（確認 UV 環境正常後）
pipenv --rm

# 可選：保留 Pipfile 作為參考
# 或移除：rm Pipfile Pipfile.lock
```

---

## ⚡ 效能比較

### 安裝速度對比

| 工具 | 安裝 requirements.txt (40 個套件) |
|------|-----------------------------------|
| **uv** | ~5 秒 ⚡ |
| pipenv | ~120 秒 |
| pip | ~45 秒 |

### 依賴解析速度

| 工具 | 解析複雜依賴 |
|------|--------------|
| **uv** | ~1 秒 ⚡ |
| pipenv | ~30 秒 |
| pip | ~10 秒 |

---

## 🎯 最佳實踐

### 1. 使用 uv run

```bash
# ✅ 推薦：自動管理環境
uv run python3 script.py
uv run robot tests/

# ❌ 避免：需要手動啟動環境
source .venv/bin/activate
python3 script.py
```

### 2. 鎖定版本

在 `requirements.txt` 中指定版本範圍：

```txt
# ✅ 推薦：指定最小版本
robotframework>=7.3.1
opencv-python>=4.5.0

# ⚠️  謹慎：完全鎖定版本（僅在必要時）
robotframework==7.3.1

# ❌ 避免：無版本限制
robotframework
```

### 3. 定期更新

```bash
# 每週或每月更新套件
uv pip install --upgrade -r requirements.txt

# 測試更新後的環境
uv run robot tests/
```

### 4. 環境隔離

```bash
# 為不同用途建立不同環境
uv venv .venv-dev      # 開發環境
uv venv .venv-test     # 測試環境
uv venv .venv-prod     # 生產環境
```

---

## 🐛 常見問題

### 問題 1: uv 找不到 Python

**症狀：** `error: No Python installations found`

**解決方案：**
```bash
# 安裝 Python 3.12
sudo apt install python3.12 python3.12-venv

# 指定 Python 路徑
uv venv --python /usr/bin/python3.12
```

### 問題 2: 權限錯誤

**症狀：** `Permission denied`

**解決方案：**
```bash
# 不要使用 sudo
# 確保目錄權限正確
chmod -R u+w .venv
```

### 問題 3: 虛擬環境衝突

**症狀：** 套件版本不符

**解決方案：**
```bash
# 刪除舊環境
rm -rf .venv

# 重新建立
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 問題 4: PYTHONPATH 未設定

**症狀：** `ModuleNotFoundError: No module named 'config'`

**解決方案：**
```bash
# 設定 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 或加入 .bashrc/.zshrc
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
```

---

## 📚 進階使用

### 使用 pyproject.toml (可選)

UV 支援現代 Python 專案標準：

```toml
# pyproject.toml
[project]
name = "robot-multiplatform-automation"
version = "1.1.0"
requires-python = ">=3.12"
dependencies = [
    "robotframework>=7.3.1",
    "opencv-python>=4.5.0",
    # ...
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

安裝方式：

```bash
# 安裝專案依賴
uv pip install -e .

# 安裝開發依賴
uv pip install -e ".[dev]"
```

### 建立鎖定檔案

```bash
# 產生精確版本鎖定
uv pip freeze > requirements-lock.txt

# 使用鎖定檔案安裝
uv pip install -r requirements-lock.txt
```

---

## 🔗 相關資源

- **UV 官方文檔:** https://docs.astral.sh/uv/
- **GitHub 專案:** https://github.com/astral-sh/uv
- **專案 README:** [../README.md](../README.md)
- **CLAUDE.md:** [../CLAUDE.md](../CLAUDE.md)

---

## 📝 版本資訊

- **文件版本：** 1.0.0
- **最後更新：** 2025-11-06
- **UV 版本：** 0.1.x+
- **適用專案：** Robot Framework 多平台自動化測試系統

---

## 🎉 總結

UV 提供了：

✅ 極快的套件安裝速度
✅ 簡潔的命令列介面
✅ 自動虛擬環境管理
✅ 完整的依賴解析
✅ 與現有工具相容

**建議：** 對於新專案或現有專案升級，UV 是比 pipenv 更現代化的選擇。
