*** Settings ***
Documentation    測試 RV 車內部空間 (如 Slide-out 艙壁或 Awning 天棚) 的擴展與收合極端狀態判定
...              使用 OpenCV ArUco Marker 電腦視覺面積深度追蹤技術來計算物理距離
Library          ../../libraries/rv_space_detection/IPCamExpansionKeywords.py

*** Test Cases ***
驗證 RV車 Slide-out 艙已完全向外展開
    [Documentation]    測試當 RV 車艙門向外推到底時，標籤深度面積應符合設定之 expanded_area 基準值
    [Tags]             rv_expansion    camera_vision    smoke
    
    Given 攝影機開始鎖定擴展目標    slide_out_wall
    # 實務測試上，這裡可能會加入硬體按鈕啟動的 Keywords，例如：
    # When 啟動 RV車向外擴展開關
    # And 等待擴展馬達動作完畢
    Then RV車內部空間應該已完全    展開
    [Teardown]    When 中斷擴展偵測的攝影機連線


驗證 RV車 Slide-out 艙已完全向內收縮
    [Documentation]    測試當艙室收合回車體內部時，標籤距離靠近鏡頭而面積增加，應符合 collapsed_area 基準值
    [Tags]             rv_expansion    camera_vision
    
    Given 攝影機開始鎖定擴展目標    slide_out_wall
    # When 啟動 RV車向內收合開關
    # And 等待收合馬達動作完畢
    Then RV車內部空間應該已完全    收合
    [Teardown]    When 中斷擴展偵測的攝影機連線
