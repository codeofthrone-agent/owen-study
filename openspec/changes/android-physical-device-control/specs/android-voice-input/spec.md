## ADDED Requirements

### Requirement: 觸發 App 內語音輸入
系統 SHALL 提供自動化點擊應用程式內麥克風/語音輸入按鈕的能力，觸發 App 內建的語音輸入功能。此功能用於測試 IoT 設備語音控制場景（如：開啟環境燈光、雨遮控制、風扇空調開關）。

#### Scenario: 點擊麥克風按鈕觸發語音輸入
- **WHEN** 使用者執行「點擊語音輸入按鈕」關鍵字並傳入按鈕定位器
- **THEN** 系統等待按鈕出現並點擊
- **THEN** 應用程式 SHALL 進入語音輸入模式（麥克風啟動）

#### Scenario: 透過 Accessibility ID 觸發語音輸入
- **WHEN** 使用者執行「點擊語音輸入按鈕」關鍵字並傳入 accessibility_id 定位器
- **THEN** 系統 SHALL 透過 Accessibility ID 定位並點擊語音輸入按鈕

### Requirement: 語音播放前硬體就緒檢查
系統 SHALL 在播放語音指令前檢查 Scarlett 4i4 音訊硬體是否就緒。若硬體未連接或虛擬設備未建立，系統 MUST 立即報錯而非靜默失敗。

#### Scenario: 硬體就緒檢查通過
- **WHEN** 使用者執行語音指令播放前
- **THEN** 系統 SHALL 透過 VoiceControlKeywords 檢查 Scarlett 4i4 連接狀態
- **THEN** 確認 PipeWire 虛擬音訊設備已建立
- **THEN** 檢查通過後才開始播放

#### Scenario: 硬體未就緒時報錯
- **WHEN** Scarlett 4i4 未連接或 PipeWire 路由未設定
- **THEN** 系統 SHALL 拋出 RuntimeError 並附帶診斷訊息（如「Scarlett 4i4 未偵測到，請檢查 USB 連接」或「PipeWire 虛擬設備未建立，請執行 setup_pipewire_routing_v3.sh」）
- **THEN** SHALL 跳過語音播放步驟，避免後續無意義的等待

### Requirement: 語音觸發與播放的同步策略
系統 SHALL 確保 App 語音輸入啟動（麥克風開始聆聽）與 Scarlett 4i4 語音播放之間的時序正確。系統 MUST 在觸發 App 語音輸入後等待指定延遲時間，確保 App 麥克風就緒後再開始播放。

#### Scenario: 觸發語音輸入後等待再播放
- **WHEN** 使用者執行「觸發語音輸入並播放指令」組合關鍵字
- **THEN** 系統 SHALL 先點擊語音輸入按鈕
- **THEN** 等待可配置的延遲時間（預設 1.5 秒，透過參數 `mic_ready_delay` 調整）
- **THEN** 確認 App 語音輸入 UI 已出現（如麥克風動畫、聆聽指示器）
- **THEN** 才開始透過 Scarlett 4i4 播放語音指令

#### Scenario: App 語音輸入 UI 未出現時重試
- **WHEN** 點擊語音輸入按鈕後，語音輸入 UI 在延遲時間內未出現
- **THEN** 系統 SHALL 重試點擊語音輸入按鈕（最多重試 `max_retries` 次，預設 2 次）
- **THEN** 若重試後仍未出現 SHALL 拋出 TimeoutError 並附帶「App 語音輸入未啟動，已重試 {n} 次」

### Requirement: 整合語音播放觸發 IoT 控制
系統 SHALL 支援與既有 VoiceControlKeywords（Scarlett 4i4）整合，在 App 語音輸入啟動後，透過外部音訊設備播放語音指令，實現端到端的語音控制測試。測試流程為：硬體檢查 → 觸發 App 語音輸入 → 等待麥克風就緒 → 播放語音指令（透過 Scarlett 4i4 輸出至裝置麥克風）→ 等待 App 回應 → 驗證結果。

#### Scenario: 語音指令控制 IoT 設備
- **WHEN** 使用者觸發 App 語音輸入後，透過 VoiceControlKeywords 播放語音指令（如「開啟客廳燈光」）
- **THEN** App SHALL 接收到語音輸入並辨識指令
- **THEN** 系統 SHALL 可透過後續驗證步驟確認 IoT 設備狀態變化

#### Scenario: 語音指令後等待 App 回應
- **WHEN** 語音指令播放完成後
- **THEN** 系統 SHALL 等待 App UI 顯示指令執行結果（如 Toast 訊息、狀態文字變更）
- **THEN** 等待逾時時間 SHALL 可由使用者指定（預設 10 秒）

### Requirement: 觸發系統語音搜尋
系統 SHALL 提供透過 Android Intent 觸發系統級語音搜尋的能力，作為備用方案，使用 ADB 啟動 `android.intent.action.VOICE_COMMAND`。

#### Scenario: 啟動系統語音搜尋
- **WHEN** 使用者執行「觸發系統語音搜尋」關鍵字
- **THEN** 系統透過 ADB `am start -a android.intent.action.VOICE_COMMAND` 啟動語音搜尋
- **THEN** 裝置 SHALL 顯示系統語音輸入介面

### Requirement: 語音輸入結果驗證
系統 SHALL 提供驗證語音輸入結果的能力，透過等待指定元素出現或文字變化來確認語音指令是否成功執行。

#### Scenario: 驗證 App 顯示語音辨識結果
- **WHEN** 使用者執行「等待語音輸入結果」關鍵字並傳入結果顯示區域定位器與逾時時間
- **THEN** 系統 SHALL 等待指定元素的文字內容發生變化
- **THEN** 若在逾時時間內偵測到文字變化，SHALL 返回辨識結果文字

#### Scenario: 驗證語音指令執行成功
- **WHEN** 使用者執行「語音指令結果應包含」關鍵字並傳入預期回應文字（如「燈光已開啟」）
- **THEN** 系統 SHALL 比對 App 顯示的回應是否包含預期文字
- **THEN** 若不包含 SHALL 拋出 AssertionError 並附上實際顯示內容

### Requirement: 語音控制逾時與錯誤處理
系統 SHALL 為語音控制流程的每個階段定義明確的逾時時間與錯誤訊息，避免測試因無回應而無限等待。

#### Scenario: 語音辨識逾時
- **WHEN** 語音指令播放後，App 在逾時時間內未顯示任何辨識結果
- **THEN** 系統 SHALL 拋出 TimeoutError 並附帶「語音辨識逾時：App 在 {timeout} 秒內未回應，可能原因：1) 麥克風未接收到聲音 2) App 語音辨識失敗 3) 音訊輸出通道不正確」

#### Scenario: 語音辨識結果不符預期
- **WHEN** App 回傳辨識結果但與預期指令不符
- **THEN** 系統 SHALL 拋出 AssertionError 並附帶「語音辨識結果不符：預期包含 '{expected}'，實際為 '{actual}'。建議檢查音訊輸出音量與麥克風距離。」
