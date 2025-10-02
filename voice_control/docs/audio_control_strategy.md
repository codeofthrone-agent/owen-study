# [歷史文件] 技術研究報告: Focusrite Scarlett 4i4 Linux 自動化控制

> **注意**: 本文件記錄的是專案初期的技術研究與設計草案。最終的成功解決方案並**沒有**採用本文件設想的 Python `pyalsaaudio` 方案，而是走向了 `alsa-scarlett-gui` + PipeWire 進階路由的路線。
> 
> **關於最終的、可運作的解決方案，請參考根目錄下的 `README.md` 或 `Audio_Troubleshooting_Report.md`。**

- **相關 Spike 任務**: 調查 Focusrite Scarlett 4i4 在 Linux 環境下的控制與自動化

---

## 1. 研究目標

本研究旨在尋找一個在 Linux (Ubuntu 24) 環境下，能夠透過程式碼（最好是 Python）對 Focusrite Scarlett 4i4 音效卡進行精確輸出控制的方法，特別是獨立控制多個物理輸出通道的左右聲道。

## 2. 調查發現摘要

1.  **核心驅動已內建**: 適用於 Scarlett (Gen 2/3/4) 的 `scarlett2` 核心驅動程式已包含在現代 Linux 核心中。這意味著硬體的大部分進階功能（如內部混音、路由）都已透過 ALSA (Advanced Linux Sound Architecture) 子系統暴露給作業系統。

2.  **存在開源控制軟體**: 社群開發的 `alsa-scarlett-gui` 專案是一個功能完整的圖形化介面，證明了在 Linux 上對 Scarlett 進行完全控制是可行的。

3.  **核心控制機制**: 經分析，`alsa-scarlett-gui` 是透過直接呼叫 ALSA 的 C 函式庫 (`libasound`) API 來實現控制，而非透過外部命令列工具。

4.  **控制項的識別**: 系統內建的 `amixer` 命令列工具可以被用來查詢指定音效卡所有可用的 ALSA 控制項。指令為 `amixer -c <card_index> contents`。雖然這些控制項數量龐大且命名複雜，但它們是實現精確控制的關鍵。

5.  **理想的 Python 函式庫**: 我們找到了 `pyalsaaudio` 這個 Python 套件。它是一個對 `libasound` 的直接綁定，允許我們透過 Python API 直接、高效地操作 ALSA 控制項，是實現自動化的最佳選擇。

## 3. 最終技術方案決策 (初期設想)

基於以上研究，我們制定了主要方案和備用方案。

### 3.1 主要方案 (Primary Plan): 使用 `pyalsaaudio` 函式庫

- **描述**: 我們將在 Python 專案中引入 `pyalsaaudio` 函式庫。我們將編寫一個高層次的封裝類 (Wrapper Class)，該類別負責初始化時找到 Scarlett 音效卡，並提供簡單易用的方法（如 `set_volume`, `mute_channel`），內部則呼叫 `pyalsaaudio` 的 API 來操作對應的 ALSA 控制項。
- **優點**: 
    - **穩定高效**: 直接 API 呼叫，沒有解析命令列輸出的開銷和不穩定性。
    - **程式碼優雅**: Pythonic 的介面，易於整合和維護。
    - **錯誤處理**: 可以更好地捕捉和處理來自 ALSA 驅動的錯誤。

### 3.2 備用方案 (Backup Plan): 使用 `subprocess` 呼叫 `amixer`

- **描述**: 如果在開發過程中，發現 `pyalsaaudio` 存在 Bug、不穩定，或無法操作某個特定的 Scarlett 控制項，我們將啟用此備案。
- **實現**: 我們將編寫一個輔助函式，透過 Python 的 `subprocess.run()` 來執行 `amixer -c <card_index> cset name='Control Name' <value>` 這樣的命令。
- **缺點**: 
    - **較為脆弱**: 需要解析 `amixer` 的文字輸出，如果工具版本或系統語言變更，可能導致解析失敗。
    - **效率較低**: 每次操作都需要啟動一個新的系統進程。

## 4. 下一步 (舊)

基於此研究報告，下一步是執行原計畫的「檢查點 4」，即基於主要方案 (`pyalsaaudio`) 設計一個高層次的 Python API.

---

## 5. 高層次 API 設計草案 (檢查點 4 產出)

### 5.1 設計目標

創建一個名為 `ScarlettController` 的 Python Class，封裝所有與 `pyalsaaudio` 相關的複雜底層操作，並向外提供一個非常簡單、直觀的 API。使用者在呼叫它時，應該只需要關心「做什麼」（例如：設定第3/4路輸出的音量），而不需要關心「如何做」（例如：如何找到音效卡索引、如何呼叫 ALSA 的 C-API）。

### 5.2 `ScarlettController` 類別設計

- **`__init__(self, card_name="Scarlett")`**:
    - 建構函式在初始化時，會自動在系統中搜尋包含 `card_name` 的音效卡，並儲存其索引 (`card_index`)。如果找不到，則會拋出 `IOError`。
    - 它還會讀取該卡所有可用的控制項，存入一個內部列表，以便後續快速查詢。

- **`get_controls(self) -> list`**:
    - 一個輔助方法，返回此音效卡所有可用的混音器控制項名稱列表，方便調試。

- **`set_volume(self, control: str, volume: int, channel: str = 'both')`**:
    - `control` (str): ALSA 控制項的名稱，例如 `'PCM'` 或 `'Line'`。
    - `volume` (int): 0 到 100 的整數。
    - `channel` (str): `'both'`, `'left'`, 或 `'right'`，用於指定要設定的聲道。

- **`get_volume(self, control: str) -> tuple`**:
    - 獲取指定控制項的音量，返回一個包含 `(左聲道音量, 右聲道音量)` 的元組。

- **`set_mute(self, control: str, mute: bool, channel: str = 'both')`**:
    - 設定指定控制項和聲道的靜音狀態。`mute` 為 `True` 表示靜音。

- **`get_mute(self, control: str) -> tuple`**:
    - 獲取指定控制項的靜音狀態，返回一個包含 `(左聲道是否靜音, 右聲道是否靜音)` 的布林元組。

### 5.3 程式碼結構草稿

```python
import alsaaudio

class ScarlettController:
    """
    一個用於控制 Focusrite Scarlett 音效卡 ALSA Mixers 的高層次封裝類。
    """
    def __init__(self, card_name: str = "Scarlett"):
        """
        初始化控制器，自動尋找指定的音效卡。
        :param card_name: 音效卡名稱的一部分，用於搜尋。
        """
        self.card_index = self._find_card_index(card_name)
        if self.card_index == -1:
            raise IOError(f"找不到名稱包含 '{card_name}' 的音效卡。 সন")
        
        self.controls = alsaaudio.mixers(cardindex=self.card_index)
        print(f"成功連接到 '{card_name}' (Card Index: {self.card_index})")

    def _find_card_index(self, card_name: str) -> int:
        "在系統中尋找指定的音效卡並返回其索引。"
        for i, card in enumerate(alsaaudio.cards()):
            if card_name in card:
                return i
        return -1

    def get_controls(self) -> list:
        "返回此音效卡所有可用的混音器控制項名稱。"
        return self.controls

    def set_volume(self, control: str, volume: int, channel: str = 'both'):
        """
        設定指定控制項的音量。
        :param control: ALSA 控制項的名稱。
        :param volume: 0-100 的整數。
        :param channel: 'both', 'left', 或 'right'。
        """
        if control not in self.controls:
            raise ValueError(f"控制項 '{control}' 不存在。可用的控制項: {self.controls}")
        if not 0 <= volume <= 100:
            raise ValueError("音量必須在 0 到 100 之間。 সন")

        mixer = alsaaudio.Mixer(control=control, cardindex=self.card_index)
        
        vol_map = {
            'both': (volume, volume),
            'left': (volume, None),
            'right': (None, volume)
        }
        ch = vol_map.get(channel.lower())
        if ch is None:
            raise ValueError("聲道參數必須是 'both', 'left', 或 'right'。 সন")
        
        # setvolume(value, channel_id), 0 for left, 1 for right
        if ch[0] is not None:
            mixer.setvolume(ch[0], 0)
        if ch[1] is not None:
            mixer.setvolume(ch[1], 1)
        print(f"已設定控制項 '{control}' 的音量為 {volume} (聲道: {channel})")

    # ... get_volume, set_mute, get_mute 等方法的實現 ...

if __name__ == '__main__':
    try:
        # 假設 'Scarlett' 是 aplay -l 中看到的名稱
        scarlett = ScarlettController(card_name="Scarlett")
        
        print("\n可用的控制項:")
        print(scarlett.get_controls())
        
        # 假設我們從 amixer contents 中發現了一個名為 'Line Playback' 的控制項
        # 來控制 Line Out 3/4
        # 這是一個示意名稱，需要用真實名稱替換
        TARGET_CONTROL = 'Line Playback' 

        if TARGET_CONTROL in scarlett.get_controls():
            print(f"\n--- 正在操作 '{TARGET_CONTROL}' ---")
            # 將 Line Out 3/4 的左聲道(Line 3)音量設為 80%
            scarlett.set_volume(TARGET_CONTROL, 80, channel='left')
            # 將 Line Out 3/4 的右聲道(Line 4)音量設為 50%
            scarlett.set_volume(TARGET_CONTROL, 50, channel='right')
        else:
            print(f"\n錯誤: 找不到名為 '{TARGET_CONTROL}' 的控制項。請從上面的列表中選擇一個。 সন")

    except (IOError, ValueError) as e:
        print(f"發生錯誤: {e}")
```