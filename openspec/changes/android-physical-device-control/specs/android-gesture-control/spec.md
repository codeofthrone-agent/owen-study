## ADDED Requirements

### Requirement: 長按手勢
系統 SHALL 提供對 Android 裝置元素或座標執行長按操作的能力，使用 Appium 2.x `mobile: longClickGesture` API。

#### Scenario: 長按指定元素
- **WHEN** 使用者執行「長按元素」關鍵字並傳入元素定位器與持續時間（毫秒）
- **THEN** 系統使用 `mobile: longClickGesture` 對該元素執行長按
- **THEN** 長按持續時間 SHALL 為使用者指定的毫秒數（預設 1000ms）

#### Scenario: 長按指定座標
- **WHEN** 使用者執行「長按座標」關鍵字並傳入 X、Y 座標與持續時間
- **THEN** 系統使用 `mobile: longClickGesture` 對該座標執行長按

### Requirement: 精確滑動手勢
系統 SHALL 升級滑動功能至 Appium 2.x `mobile: swipeGesture` API，支援四方向滑動（上/下/左/右）與滑動距離百分比控制。

#### Scenario: 向指定方向滑動螢幕
- **WHEN** 使用者執行「滑動螢幕」關鍵字並傳入方向（up/down/left/right）與百分比
- **THEN** 系統使用 `mobile: swipeGesture` 執行滑動
- **THEN** 滑動距離 SHALL 為螢幕尺寸的指定百分比（預設 75%）

#### Scenario: 在指定區域內滑動
- **WHEN** 使用者執行「在區域內滑動」關鍵字並傳入邊界座標（left, top, width, height）、方向與百分比
- **THEN** 系統使用 `mobile: swipeGesture` 在指定矩形區域內執行滑動

### Requirement: 座標點擊
系統 SHALL 提供在螢幕指定座標執行點擊的能力，使用 Appium 2.x `mobile: clickGesture` API。

#### Scenario: 點擊指定座標
- **WHEN** 使用者執行「點擊座標」關鍵字並傳入 X、Y 座標
- **THEN** 系統使用 `mobile: clickGesture` 在該座標執行點擊

### Requirement: 雙擊手勢
系統 SHALL 提供對元素或座標執行雙擊操作的能力，使用 Appium 2.x `mobile: doubleClickGesture` API。

#### Scenario: 雙擊指定元素
- **WHEN** 使用者執行「雙擊元素」關鍵字並傳入元素定位器
- **THEN** 系統使用 `mobile: doubleClickGesture` 對該元素執行雙擊

### Requirement: 拖曳手勢
系統 SHALL 提供在螢幕上執行拖曳操作的能力，使用 Appium 2.x `mobile: dragGesture` API。

#### Scenario: 拖曳元素到指定位置
- **WHEN** 使用者執行「拖曳元素」關鍵字並傳入元素定位器與目標座標
- **THEN** 系統使用 `mobile: dragGesture` 將元素拖曳至目標位置
