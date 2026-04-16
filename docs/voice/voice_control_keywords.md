# 關鍵字文件: VoiceControlKeywords

**版本:** 1.0.0
**範疇:** GLOBAL

---

## 函式庫介紹

語音控制關鍵字庫

整合 TTS 與 Scarlett 4i4 硬體控制，提供：
1. 文字轉語音並輸出到指定聲道
2. TTS 引擎切換（gtts, pyttsx3）
3. 語言與語速控制
4. 多聲道測試功能

---

## 關鍵字

### 播放文字到聲道
將文字轉換為語音並播放到 Scarlett 4i4 的指定聲道

這是核心關鍵字，整合了 TTS 生成與硬體聲道控制

**參數:**
| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `text`: str | (無) | 要播放的文字內容 |
| `channel`: int | (無) | 目標聲道 (1-4)<br>1 = 物理輸出 1（左前）<br>2 = 物理輸出 2（右前）<br>3 = 物理輸出 3（左後/AUX 1）<br>4 = 物理輸出 4（右後/AUX 2） |
| `language`: str | `en` | 語言代碼（en, zh-TW, ja） |
| `duration`: int | `5` | 播放時長（秒） |

**回傳:**
`bool` - 播放是否成功

**範例:**
```robotframework
| 播放文字到聲道 | Hello World | 1 |
| 播放文字到聲道 | 測試語音 | 3 | zh-TW |
| 播放文字到聲道 | テスト | 4 | ja | 10 |
```

---

### 設定 TTS 引擎
切換 TTS 引擎

**參數:**
| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `engine_name`: str | (無) | 引擎名稱<br>gtts = Google TTS（線上，品質高）<br>pyttsx3 = 離線 TTS（離線，速度快） |

**回傳:**
`bool` - 切換是否成功

**範例:**
```robotframework
| 設定 TTS 引擎 | gtts |
| 設定 TTS 引擎 | pyttsx3 |
```

---

### 設定 TTS 語言
設定 TTS 語言

**參數:**
| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `language`: str | (無) | 語言代碼 (en, zh-TW, zh-CN, ja, ko) |

**回傳:**
`bool` - 設定是否成功

**範例:**
```robotframework
| 設定 TTS 語言 | en |
| 設定 TTS 語言 | zh-TW |
```

---

### 設定 TTS 語速
設定 TTS 語速

**參數:**
| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `speed`: float | (無) | 語速（words per minute）<br>120 = 慢速<br>180 = 標準速度（預設）<br>250 = 快速 |

**回傳:**
`bool` - 設定是否成功

**範例:**
```robotframework
| 設定 TTS 語速 | 150 |
| 設定 TTS 語速 | 200 |
```

---

### 播放語音到所有聲道
依序播放文字到所有 4 個聲道（測試用）

**參數:**
| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `text`: str | (無) | 要播放的文字 |
| `language`: str | `en` | 語言代碼 |
| `duration`: int | `3` | 每個聲道播放時長（秒） |

**回傳:**
`Dict[int, bool]` - 字典，鍵為聲道號，值為是否成功

**範例:**
```robotframework
| 播放語音到所有聲道 | Channel Test |
| 播放語音到所有聲道 | 聲道測試 | zh-TW | 2 |
```

---

### 取得 TTS 引擎資訊
獲取 TTS 引擎資訊

**回傳:**
`Dict[str, Any]` - 包含引擎資訊的字典

**範例:**
```robotframework
| ${info}= | 取得 TTS 引擎資訊 |
| Log | 主要引擎: ${info['primary_engine']} |
```

---

### 取得可用音訊設備
獲取可用的音訊輸出設備列表

**回傳:**
`list` - 設備名稱列表

**範例:**
```robotframework
| ${sinks}= | 取得可用音訊設備 |
| Log Many | @{sinks} |
```

---

### 檢查 Scarlett 設備
檢查 Scarlett 4i4 設備是否可用

**回傳:**
`bool` - 設備是否可用

**範例:**
```robotframework
| ${available}= | 檢查 Scarlett 設備 |
| Should Be True | ${available} | msg=Scarlett 設備不可用 |
```

---

### 清理語音控制資源
清理語音控制資源（暫存檔案等）

**回傳:**
`bool` - 清理是否成功

**範例:**
```robotframework
| 清理語音控制資源 |
```
