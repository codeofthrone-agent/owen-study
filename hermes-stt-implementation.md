# Hermes STT 實作說明（目前環境）

更新時間：2026-05-06

## TL;DR
目前 Hermes 的正式 STT 管線是：
- `stt.provider: local`
- `stt.local.model: base`
- 引擎：`faster-whisper`

另外你也有一條自訂 STT 腳本管線（`mlx-whisper`）：
- 模型：`mlx-community/whisper-large-v3-mlx`
- 腳本：`~/.hermes/scripts/stt.py`

---

## 1) Hermes 內建 STT（主要生產路線）

### 設定值（多 profile 一致）
在以下設定檔都看到同樣配置：
- `~/.hermes/config.yaml`
- `~/.hermes/profiles/car-auction/config.yaml`
- `~/.hermes/profiles/tcbas/config.yaml`

設定片段：
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: base
```

### 程式實作（核心流程）
- 入口：`~/.hermes/hermes-agent/tools/transcription_tools.py`
- 函式：`transcribe_audio(file_path, model=None)`
- provider 判斷：`provider == "local"` 時走 `_transcribe_local(...)`
- 本地模型載入：`faster_whisper.WhisperModel(model_name, device="auto")`
- 若 CUDA/驅動問題：自動 fallback 到 CPU int8

=> 也就是 Hermes 目前實際會先嘗試本機最佳裝置，再必要時退回 CPU，保證可用性。

### 聲音入口
- Voice mode（CLI）與各平台語音訊息（如 Discord）最終都會走 STT provider 判斷。
- `stt.enabled: true` 才會啟用自動轉錄。

---

## 2) 自訂 STT 腳本路線（你另外維運的一條）

### 腳本與模型
- `~/.hermes/scripts/stt.py`
  - 明確指定：`path_or_hf_repo = "mlx-community/whisper-large-v3-mlx"`
- `~/.hermes/scripts/voice-cmd.py`
  - 用 `mlx_whisper.transcribe(...)` 做轉錄

### 這條路線的定位
- 優點：你可以固定用 `whisper-large-v3-mlx`（中英混合辨識通常更強）。
- 差異：這不是 Hermes gateway 預設 `stt.provider=local(base)` 那條內建管線，而是額外腳本工具流。

---

## 3) 目前環境可用性

已確認 venv 可 import：
- `faster_whisper = True`
- `mlx_whisper = True`

代表兩條 STT 路線目前都可執行。

---

## 4) 建議（避免混淆）

如果你想「全 Hermes agent 一律用 large-v3-mlx」，建議二選一：
1. **統一走內建 provider**（維持 `faster-whisper`，但把 `stt.local.model` 調整到你要的等級）
2. **統一改成 local_command**，把 Hermes STT 指到你的 `~/.hermes/scripts/stt.py`

目前狀態是雙軌並存：
- 內建主路：faster-whisper/base
- 自訂路：mlx-whisper/large-v3-mlx

這不是錯，但團隊協作時容易「以為在用同一模型」。
