## Context

目前專案已有基礎的 Android 測試架構：
- `libraries/mobile_testing/common/CustomAppiumKeywords.py`：封裝 Appium 基本操作（點擊、輸入、滑動、截圖）
- `resources/mobile_keywords.robot`：Robot Framework BDD 關鍵字資源檔
- `config/mobile/appium_config.py`：Appium 配置管理（已支援 iOS 真機配置）
- `config/mobile/ios_config.py`：iOS 專屬配置與設備管理
- `tests/mobile/android/android_app_test.robot`：基礎 Android 測試案例

現有架構的限制：
1. **缺少系統層級控制**：只有 UI 元素操作，無法控制藍牙、WiFi、音量等硬體功能
2. **使用舊版 Appium API**：滑動等手勢操作使用 `driver.swipe()` 而非 Appium 2.x 的 `mobile:` 命令
3. **缺少 Android 專屬配置**：`appium_config.py` 的 Android 配置較簡略，無 ADB 相關設定
4. **混用中英文關鍵字**：部分測試案例仍使用英文關鍵字（如 `android_app_test.robot` 後半段）
5. **無跨平台系統控制抽象**：既有的 `CustomAppiumKeywords.py` 雖支援跨平台 UI 操作，但系統層級控制（藍牙/WiFi/音量）完全缺失

目標裝置：
- **Android 16**（最新版本），實體裝置
- 單一裝置控制（但需支援 Android + iOS 同時連接的情境）

語音輸入場景：
- App 內建語音輸入功能，使用者透過語音命令控制 IoT 設備
- 實際語音指令範例：開啟/關閉環境燈光、雨遮控制、風扇空調開關
- 測試流程：觸發 App 語音輸入 → 播放語音指令（透過既有的 VoiceControlKeywords / Scarlett 4i4）→ 驗證 App 回應與設備狀態變化

約束條件：
- 必須遵循專案既有的 BDD 中文關鍵字規範
- 目標 Android 16 實體裝置（非模擬器）
- 需透過 USB 調試連接，ADB 必須已授權
- 部分功能（藍牙）在非 root 裝置有限制
- Appium server `--relaxed-security` 狀態未知，需在啟動腳本中確保啟用
- **架構必須支援後續 iOS 擴展，避免重構**

## Goals / Non-Goals

**Goals:**
- **設計跨平台抽象架構**：BDD 關鍵字層平台無關，底層透過策略模式分發至 Android/iOS 實作
- 新增完整的 Android 實體裝置系統層級控制能力（本次實作重點）
- iOS 實作預留 stub（拋出 NotImplementedError），後續可逐步補齊
- 所有新增功能提供中文 BDD 關鍵字，遵循 Given-When-Then 規範
- 支援 10 項核心功能：藍牙控制、語音輸入、滑動、點擊、長按、輸入文字、音量調整、滑掉 App、App 置於背景、關閉網路
- 升級手勢操作至 Appium 2.x `mobile:` API
- 提供完整的錯誤處理與日誌記錄

**Non-Goals:**
- 不實作藍牙配對功能（需要 root 權限或複雜 UI 自動化）
- 不實作語音辨識結果直接注入（Appium 不支援）
- **不實作 iOS 系統控制的完整邏輯**（僅預留 stub 與介面）
- 不實作 Android 模擬器專屬功能（如 GPS 模擬）
- 不重構現有 `CustomAppiumKeywords.py`（保持向後兼容）

## Decisions

### Decision 1: 跨平台策略模式架構（核心決策）

**選擇：** 三層架構 — BDD 關鍵字層（平台無關）→ 平台分發層 → 平台實作層

**替代方案：**
- A) 先只做 Android，iOS 進來再重構 → 需改測試案例和關鍵字，重構成本高
- B) 用 if/else 在每個方法中判斷平台 → 程式碼耦合，難維護
- C) **策略模式 + 抽象基類** → 關注點分離，擴展只需新增實作類別

**理由：** 策略模式額外工作量約半天（定義基類 + iOS stub），但避免 iOS 進來時的全面重構。測試案例完全不需修改。

**架構圖：**
```
┌──────────────────────────────────────────────────┐
│  BDD 關鍵字層（平台無關）                            │
│  resources/device_control_keywords.robot           │
│  When 使用者關閉 WiFi                               │
│  When 使用者將應用程式置於背景                        │
├──────────────────────────────────────────────────┤
│  統一入口 + 平台分發層                               │
│  libraries/mobile_testing/DeviceControlKeywords.py │
│  根據 current_platform 分發至對應實作                │
├────────────────────┬─────────────────────────────┤
│  Android 實作       │  iOS 實作                     │
│  android/           │  ios/                         │
│  AndroidDevice      │  IOSDevice                    │
│  Control.py         │  Control.py（stub）            │
│  AndroidGesture.py  │  IOSGesture.py（stub）         │
└────────────────────┴─────────────────────────────┘
```

**檔案結構：**
```
libraries/mobile_testing/
├── common/
│   └── CustomAppiumKeywords.py          # 既有（保持不變）
├── base/
│   ├── __init__.py
│   ├── device_control_base.py           # 抽象基類（ABC）
│   └── gesture_control_base.py          # 手勢抽象基類（ABC）
├── android/
│   ├── __init__.py
│   ├── AndroidDeviceControl.py          # Android 系統控制實作
│   └── AndroidGestureControl.py         # Android 手勢實作
├── ios/
│   ├── __init__.py
│   ├── IOSDeviceControl.py              # iOS 系統控制（stub）
│   └── IOSGestureControl.py             # iOS 手勢（stub）
├── DeviceControlKeywords.py             # 統一入口（Robot Framework Library）
├── GestureControlKeywords.py            # 統一手勢入口（Robot Framework Library）
└── README.md
```

**抽象基類設計：**
```python
# base/device_control_base.py
from abc import ABC, abstractmethod

class DeviceControlBase(ABC):
    """裝置系統控制抽象基類 - 定義跨平台統一介面"""

    def __init__(self, driver):
        self.driver = driver

    # === 藍牙控制 ===
    @abstractmethod
    def enable_bluetooth(self): ...
    @abstractmethod
    def disable_bluetooth(self): ...

    # === 網路控制 ===
    @abstractmethod
    def enable_wifi(self): ...
    @abstractmethod
    def disable_wifi(self): ...
    @abstractmethod
    def enable_mobile_data(self): ...
    @abstractmethod
    def disable_mobile_data(self): ...
    @abstractmethod
    def enable_airplane_mode(self): ...
    @abstractmethod
    def disable_airplane_mode(self): ...

    # === 音量控制 ===
    @abstractmethod
    def volume_up(self): ...
    @abstractmethod
    def volume_down(self): ...
    @abstractmethod
    def volume_mute(self): ...
    @abstractmethod
    def set_media_volume(self, level: int): ...

    # === App 生命週期 ===
    @abstractmethod
    def background_app(self, seconds: int = -1): ...
    @abstractmethod
    def activate_app(self, package_or_bundle: str): ...
    @abstractmethod
    def dismiss_from_recents(self): ...
    @abstractmethod
    def force_stop_app(self, package_or_bundle: str): ...
```

**統一入口設計：**

> **Driver 注入策略：** Robot Framework 使用者不直接操作 WebDriver 物件。
> `DeviceControlKeywords` SHALL 透過 `BuiltIn().get_library_instance()` 自動從
> 已載入的 AppiumLibrary 或 CustomAppiumKeywords 取得 driver，使用者只需傳入 platform。

```python
# DeviceControlKeywords.py
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

class DeviceControlKeywords:
    """跨平台裝置控制 - Robot Framework Library"""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._impl = None

    def _get_driver(self):
        """從已載入的 AppiumLibrary 或 CustomAppiumKeywords 自動取得 driver"""
        # 優先從 AppiumLibrary 取得（標準用法）
        try:
            appium_lib = BuiltIn().get_library_instance('AppiumLibrary')
            return appium_lib._current_application()
        except RuntimeError:
            pass
        # 回退：從 CustomAppiumKeywords 取得
        try:
            custom_lib = BuiltIn().get_library_instance('CustomAppiumKeywords')
            return custom_lib.driver
        except RuntimeError:
            pass
        raise RuntimeError(
            "無法取得 WebDriver。請確保已載入 AppiumLibrary 或 "
            "CustomAppiumKeywords，且已開啟應用程式。"
        )

    def _get_impl(self) -> 'DeviceControlBase':
        if self._impl is None:
            raise RuntimeError("尚未初始化，請先呼叫 '初始化裝置控制'")
        return self._impl

    @keyword("初始化裝置控制")
    def init_device_control(self, platform: str):
        """初始化裝置控制，自動從 AppiumLibrary 取得 driver。
        使用者只需傳入 platform（android/ios），不需手動傳入 driver。
        """
        driver = self._get_driver()
        if platform.lower() == 'android':
            self._impl = AndroidDeviceControl(driver)
        elif platform.lower() == 'ios':
            self._impl = IOSDeviceControl(driver)
        else:
            raise ValueError(f"不支援的平台: {platform}（支援: android, ios）")

    @keyword("關閉 WiFi")
    def disable_wifi(self):
        self._get_impl().disable_wifi()

    # ... 其餘關鍵字同理
```

**Robot Framework 使用範例：**
```robotframework
*** Settings ***
Library    AppiumLibrary
Library    libraries/mobile_testing/DeviceControlKeywords.py

*** Test Cases ***
Scenario: 關閉 WiFi 後驗證網路斷開
    Given 使用者已準備好移動應用程式    android    appPackage=com.example.app
    And 裝置控制已初始化    android
    When 使用者關閉 WiFi
    Then WiFi 應該為關閉狀態
```

### Decision 2: ADB Shell 命令透過 Appium `mobile: shell` 執行

**選擇：** 透過 `driver.execute_script('mobile: shell', {...})` 執行 ADB 命令

**替代方案：**
- A) 直接使用 `subprocess` 呼叫 ADB → 需要知道 ADB 路徑，且繞過 Appium session
- B) 使用 `adb_shell` Python 套件 → 額外依賴，且需要獨立的 ADB 連接

**理由：** `mobile: shell` 是 UiAutomator2 driver 原生支援的功能，透過既有的 Appium session 執行，不需額外的連接或依賴。需在 capabilities 中設定 `appium:relaxSecurityPolicy: true` 或啟動 Appium 時加上 `--relaxed-security` flag。此方式僅適用於 Android；iOS 的系統控制需透過 XCUITest 專屬 API 或 Siri/Settings UI 自動化。

### Decision 3: 手勢操作升級至 Appium 2.x mobile: 命令

**選擇：** 新增的手勢操作全部使用 `mobile: swipeGesture`、`mobile: longClickGesture` 等 Appium 2.x API

**替代方案：**
- A) 繼續使用 `driver.swipe()` → 已在 Appium 2.x 中被棄用
- B) 使用 W3C Actions API → 太底層，程式碼複雜度高

**理由：** `mobile:` 命令是 Appium 2.x 推薦的手勢操作方式，語義清晰、參數直觀。Android 和 iOS 各自的 driver 都支援類似的 `mobile:` 命令（UiAutomator2 / XCUITest），但命令名稱和參數可能不同，這正好透過策略模式在各自的實作類別中處理。

### Decision 4: 配置管理策略

**選擇：** 新增 `config/mobile/android_config.py`，管理 Android 裝置專屬設定。後續 iOS 擴展時，`ios_config.py` 已存在可直接擴充。

**內容包含：**
- ADB 設定（relaxed security flag）
- 已連接裝置自動偵測（透過 `adb devices`）
- 預設逾時與重試設定
- 裝置資訊快取

**理由：** 遵循專案統一配置管理原則（`config/` 目錄），與既有的 `ios_config.py` 對稱。

### Decision 5: 錯誤處理與回退策略

**選擇：** 採用「主方案 + 回退方案」模式

**具體策略：**
- 藍牙控制：ADB `svc bluetooth` → 回退至 UI 自動化 Settings
- 飛航模式：ADB `settings put global airplane_mode_on` → 回退至 `toggle_airplane_mode()`
- 音量控制：`press_keycode()` → 回退至 ADB `media volume`
- 所有操作 SHALL 記錄執行方式與結果至日誌
- **iOS stub 拋出 `NotImplementedError`**，附帶功能名稱和「尚未實作」訊息

**理由：** Android 裝置碎片化嚴重，不同品牌/版本行為不一致。回退策略確保最大裝置兼容性。iOS stub 明確告知使用者該功能尚未實作，而非靜默失敗。

### Decision 6: TDD 開發流程

**選擇：** 架構層（抽象基類、平台分發、iOS stub）採用嚴格 TDD（Red → Green → Refactor）；Android 實作層採用 mock-based 單元測試 + 人類協作實機驗證。

**替代方案：**
- A) 全部不用 TDD，實作完再補測試 → 架構層是純邏輯，非常適合 TDD，不用太可惜
- B) 全部嚴格 TDD 包含 Android 實作 → 系統控制依賴實體裝置，無法在 CI 中自動化驗證

**理由：** 架構層佔約 40% 工作量且為純邏輯（不依賴硬體），TDD 能確保平台分發、錯誤處理等核心邏輯的正確性。Android 實作層用 mock driver 驗證 API 呼叫參數是否正確（如 `execute_script('mobile: shell', {'command': 'svc wifi disable'})`），實機行為由人類在實體裝置上驗證。

**TDD 測試檔案：**
```
tests/
├── test_device_control_base.py       # 抽象基類測試
├── test_platform_dispatch.py         # 平台分發測試
├── test_gesture_dispatch.py          # 手勢分發測試
├── test_ios_stub.py                  # iOS stub 測試
├── test_android_device_control.py    # Android 系統控制 mock 測試
└── test_android_gesture_control.py   # Android 手勢 mock 測試
```

**開發順序：**
```
Step 1: 寫架構層測試（RED）
Step 2: 實作架構層（GREEN）
Step 3: 寫 Android mock 測試（RED）
Step 4-6: 實作 Android（GREEN）+ 🧑‍💻 人類實機驗證
```

### Decision 7: 人類協作階段劃分

**選擇：** 第 4（Android 環境設定）、5（系統控制實作）、6（手勢實作）、7（語音輸入）階段標記為需人類協作。

**理由：**
- 環境設定需人類連接實體裝置、確認 ADB 授權
- 系統控制（藍牙/WiFi/音量）必須在實體裝置上驗證行為
- 手勢操作需人類目視確認觸控結果
- 語音輸入需 Scarlett 4i4 音訊硬體配合

**AI 可獨立完成的部分：** Step 1-3（TDD 測試 + 架構實作）、Step 8-10（BDD 關鍵字 + 測試案例 + 文件）

### Decision 8: iOS Stub 設計原則

**選擇：** iOS 實作類別繼承抽象基類，所有方法統一拋出 `NotImplementedError("iOS {功能名稱} 尚未實作")`

**理由：**
- 確保抽象基類的完整性（所有抽象方法都有實作）
- 使用者嘗試在 iOS 上執行未實作功能時，得到明確的錯誤訊息
- 後續補齊 iOS 實作時，只需逐一替換 stub 方法，不影響其他已完成的功能
- Robot Framework 測試案例可透過 `[Tags]  android-only` 標記暫時跳過 iOS 不支援的測試

**iOS 後續實作路徑（參考）：**
| Android 功能 | iOS 對應方式 |
|---|---|
| ADB `svc bluetooth` | XCUITest `mobile: pressButton` (Settings UI) |
| ADB `svc wifi` | XCUITest Settings UI 自動化 |
| `press_keycode(24/25)` | `mobile: pressButton` (volumeUp/volumeDown) |
| `background_app(-1)` | `background_app(-1)`（iOS 行為正常） |
| `terminate_app()` | `terminate_app()`（跨平台一致） |
| ADB Intent 語音 | Siri 整合或 App 內按鈕 |

## Risks / Trade-offs

**[Risk] Android 碎片化導致 ADB 命令不通用**
→ Mitigation: 每個系統控制功能提供至少兩種實作方式（ADB + UI 自動化回退），並在日誌中記錄失敗原因

**[Risk] `mobile: shell` 需要 relaxed security 模式**
→ Mitigation: 在文件中明確說明 Appium 啟動參數要求，並在配置驗證階段檢查此設定

**[Risk] 非 root 裝置部分功能受限**
→ Mitigation: 在 proposal 和文件中已明確標示限制。藍牙配對、部分網路控制可能需要 root。提供清晰的功能限制矩陣。

**[Risk] `background_app()` 在 Android 上會重啟 App**
→ Mitigation: 強制使用 `background_app(-1)` + `activate_app()` 組合，在關鍵字實作中封裝此行為

**[Risk] 語音輸入無法程式化驗證結果**
→ Mitigation: 提供「等待文字變化」作為間接驗證方式，在文件中說明此限制

**[Trade-off] 跨平台架構前期投入 vs 後期重構成本**
→ 選擇前期投入。額外約半天工作量（抽象基類 + iOS stub），但 iOS 擴展時零重構成本。BDD 關鍵字層和測試案例完全不需修改。

**[Trade-off] 統一入口 Library vs 平台獨立 Library**
→ 選擇統一入口。使用者在 Robot Framework 中只需 import 一個 Library（`DeviceControlKeywords`），不需關心底層平台。缺點是多一層間接調用。

## Open Questions（已解決）

1. ~~**Appium server 的 `--relaxed-security` flag 是否已在現有測試環境中啟用？**~~ → 狀態未知，需在 Task 1.3 中確保啟動腳本加入 `--relaxed-security` flag。
2. ~~**目標 Android 裝置的具體型號和 Android 版本？**~~ → **Android 16**，需確保 Appium UiAutomator2 driver 支援最新版本。
3. ~~**是否需要支援多裝置同時控制？**~~ → 不需要單一平台多裝置，但需支援 **Android + iOS 同時連接**（各一台）。
4. ~~**語音輸入測試的實際場景是什麼？**~~ → App 內建語音輸入控制 IoT 設備（燈光/雨遮/風扇/空調）。測試整合既有 VoiceControlKeywords（Scarlett 4i4 播放語音指令）→ App 語音辨識 → 驗證設備狀態變化。
5. ~~**是否需要同時支援 iOS？**~~ → 架構層一開始就設計跨平台（策略模式），Android 先實作，iOS 預留 stub 後續擴展。
