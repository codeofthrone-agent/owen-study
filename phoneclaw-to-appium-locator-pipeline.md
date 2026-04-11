# PhoneClaw → Appium Locator Pipeline（Android 採點輔助，iOS 維持 Appium）

> 目標：避免維護兩套腳本。  
> 原則：**PhoneClaw 用來採點與產草稿，最終都收斂到同一套 Robot/Appium canonical steps。**

---

## 1) 架構定位

- Android：PhoneClaw 負責探索 UI、抓點位/文字、輸出 locator 候選
- iOS：維持 Appium/XCUITest locator
- 測試流程：共用一份 canonical keyword/test steps（不分叉）

```
TestLink Step
   ↓ (mapping)
Canonical Action (single source of truth)
   ↓
Platform Adapter
  ├─ Android adapter (PhoneClaw 採點資料 + Appium 實作)
  └─ iOS adapter (Appium/XCUITest 實作)
```

---

## 2) 採點資料契約（CSV/JSON）

建議檔名：`android-locator-candidates.csv`

| 欄位 | 必填 | 說明 |
|---|---|---|
| screen_name | ✅ | 畫面/流程名稱（如 login_screen） |
| element_alias | ✅ | 元件語意名（如 login_button） |
| view_id | ❌ | Android resource-id（優先） |
| content_desc | ❌ | 無障礙描述（次優先） |
| visible_text | ❌ | 畫面可見文字 |
| class_name | ❌ | 元件 class |
| index | ❌ | 同類元件序號 |
| bounds | ❌ | 區域座標（可做驗證） |
| tap_x | ❌ | 座標 fallback X |
| tap_y | ❌ | 座標 fallback Y |
| source_run_id | ❌ | 採點來源 run id |
| confidence | ✅ | `high/medium/low` |
| notes | ❌ | 補充 |

---

## 3) Locator 優先序（Android）

1. `view_id` → Appium `id`
2. `content_desc` → Appium `accessibility id`
3. `visible_text` → XPath / UiSelector
4. `class_name + index` → fallback
5. `tap_x/tap_y` → 最後 fallback（不建議常態使用）

---

## 4) PhoneClaw 可用能力（用於採點）

可利用（依專案 README/腳本）：
- `clickElementByViewId(...)`
- `clickNodesByContentDescription(...)`
- `isTextPresentOnScreen(...)`
- `magicScraper(...)`
- `findNodeByClassNameAndIndex(...)`
- `simulateClick(x,y)`（fallback）

> 實務：採點腳本應先「讀」再「點」，避免只留下座標而缺穩定 locator。

---

## 5) Robot/Appium 對接範例

### 5.1 Canonical keyword（不分平台）

- `點擊元素    login_button`
- `輸入文字    email_field    ${email}`
- `驗證元素可見    wifi_status_label`

### 5.2 平台 selector map（示意）

```yaml
login_button:
  android:
    by: id
    value: com.app:id/btn_login
  ios:
    by: accessibility_id
    value: login_button

email_field:
  android:
    by: id
    value: com.app:id/input_email
  ios:
    by: iOSNsPredicate
    value: "name == 'email_field'"
```

---

## 6) 與你現有對齊工作的整合

- `step-mapping-split-prefill-v2.csv`：維持 canonical action mapping
- 新增 `element_alias` 欄位：把 step 映射到可重用的 UI 元件名稱
- 再由 adapter 注入 android/ios locator

建議新增欄位：
- `canonical_action`
- `element_alias`
- `android_locator_by` / `android_locator_value`
- `ios_locator_by` / `ios_locator_value`

---

## 7) 落地步驟（建議）

1. 先挑 20 個高頻動作（點擊/輸入/檢查）建立 `element_alias` 清單
2. 用 PhoneClaw 產出 Android locator candidates（至少每個 alias 一組 high confidence）
3. iOS 用 Appium Inspector 補齊對應 locator
4. 跑同一支 testcase，驗證 Android/iOS adapter 都可通過
5. 對 failed locator 回寫到 candidates（但本階段若受限 read-only，先寫 repo 檔）

---

## 8) 風險與防呆

- 不要把 `tap_x/tap_y` 當主 locator（易碎）
- 避免 TestLink step 直接綁平台細節（應綁 canonical action）
- 每次改版先跑 smoke locator health check

---

*本文件是 Android PhoneClaw 採點與 Appium 腳本整合的實作藍圖。*