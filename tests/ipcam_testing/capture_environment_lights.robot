*** Settings ***
Documentation    擷取三個 RTSP IP Camera 的環境燈光圖片
...
...              此測試案例會擷取實驗室三個 IP Camera 的所有環境燈光圖片:
...              - Level1 Camera: 12 個燈泡
...              - Level2 Camera: 12 個燈泡
...              - Motor Camera: 7 個區域
...
...              **擷取內容:**
...              - Full Image: 包含所有 ROI 標註的完整影像
...              - ROI Images: 每個燈光的單獨 ROI 裁切圖
...
...              **輸出位置:**
...              - output/debug_images/

Library          ../../libraries/robot_arm_control/RobotArmKeywords.py
Library          OperatingSystem
Resource         ../../resources/common_keywords.robot

Suite Setup      測試環境初始化
Suite Teardown   測試環境清理

Test Tags        ipcam    environment_light    image_capture


*** Variables ***
${ENVIRONMENT}      taipei_lab
${OUTPUT_DIR}       ${CURDIR}/../../output/debug_images


*** Test Cases ***
測試案例 01: 擷取 Level1 Camera 所有燈光圖片
    [Documentation]    擷取 Level1 IP Camera 的 12 個燈泡圖片
    ...
    ...    **Camera 資訊:**
    ...    - IP: 192.168.165.184
    ...    - 燈泡數量: 12 (3行 x 4列)
    ...
    ...    **輸出檔案:**
    ...    - Full image (含標註): level1_light_*_full_*.jpg
    ...    - ROI images: level1_light_*_roi_*.jpg
    [Tags]    level1    camera

    Log    === 開始擷取 Level1 Camera 燈光圖片 ===    console=True

    # 檢測 Level1 的 12 個燈泡
    When 用戶檢測實體燈光亮度 "level1_light_1"    save_debug_image=True    step_prefix=level1_light_1
    When 用戶檢測實體燈光亮度 "level1_light_2"    save_debug_image=True    step_prefix=level1_light_2
    When 用戶檢測實體燈光亮度 "level1_light_3"    save_debug_image=True    step_prefix=level1_light_3
    When 用戶檢測實體燈光亮度 "level1_light_4"    save_debug_image=True    step_prefix=level1_light_4
    When 用戶檢測實體燈光亮度 "level1_light_5"    save_debug_image=True    step_prefix=level1_light_5
    When 用戶檢測實體燈光亮度 "level1_light_6"    save_debug_image=True    step_prefix=level1_light_6
    When 用戶檢測實體燈光亮度 "level1_light_7"    save_debug_image=True    step_prefix=level1_light_7
    When 用戶檢測實體燈光亮度 "level1_light_8"    save_debug_image=True    step_prefix=level1_light_8
    When 用戶檢測實體燈光亮度 "level1_light_9"    save_debug_image=True    step_prefix=level1_light_9
    When 用戶檢測實體燈光亮度 "level1_light_10"   save_debug_image=True    step_prefix=level1_light_10
    When 用戶檢測實體燈光亮度 "level1_light_11"   save_debug_image=True    step_prefix=level1_light_11
    When 用戶檢測實體燈光亮度 "level1_light_12"   save_debug_image=True    step_prefix=level1_light_12

    Log    ✅ Level1 Camera 燈光圖片擷取完成 (12 個燈泡)    console=True


測試案例 02: 擷取 Level2 Camera 所有燈光圖片
    [Documentation]    擷取 Level2 IP Camera 的 12 個燈泡圖片
    ...
    ...    **Camera 資訊:**
    ...    - IP: 192.168.165.127
    ...    - 燈泡數量: 12 (3行 x 4列)
    ...
    ...    **輸出檔案:**
    ...    - Full image (含標註): level2_light_*_full_*.jpg
    ...    - ROI images: level2_light_*_roi_*.jpg
    [Tags]    level2    camera

    Log    === 開始擷取 Level2 Camera 燈光圖片 ===    console=True

    # 檢測 Level2 的 12 個燈泡
    When 用戶檢測實體燈光亮度 "level2_light_1"    save_debug_image=True    step_prefix=level2_light_1
    When 用戶檢測實體燈光亮度 "level2_light_2"    save_debug_image=True    step_prefix=level2_light_2
    When 用戶檢測實體燈光亮度 "level2_light_3"    save_debug_image=True    step_prefix=level2_light_3
    When 用戶檢測實體燈光亮度 "level2_light_4"    save_debug_image=True    step_prefix=level2_light_4
    When 用戶檢測實體燈光亮度 "level2_light_5"    save_debug_image=True    step_prefix=level2_light_5
    When 用戶檢測實體燈光亮度 "level2_light_6"    save_debug_image=True    step_prefix=level2_light_6
    When 用戶檢測實體燈光亮度 "level2_light_7"    save_debug_image=True    step_prefix=level2_light_7
    When 用戶檢測實體燈光亮度 "level2_light_8"    save_debug_image=True    step_prefix=level2_light_8
    When 用戶檢測實體燈光亮度 "level2_light_9"    save_debug_image=True    step_prefix=level2_light_9
    When 用戶檢測實體燈光亮度 "level2_light_10"   save_debug_image=True    step_prefix=level2_light_10
    When 用戶檢測實體燈光亮度 "level2_light_11"   save_debug_image=True    step_prefix=level2_light_11
    When 用戶檢測實體燈光亮度 "level2_light_12"   save_debug_image=True    step_prefix=level2_light_12

    Log    ✅ Level2 Camera 燈光圖片擷取完成 (12 個燈泡)    console=True


測試案例 03: 擷取 Motor Camera 所有區域圖片
    [Documentation]    擷取 Motor IP Camera 的 7 個區域圖片
    ...
    ...    **Camera 資訊:**
    ...    - IP: 10.42.0.39
    ...    - 區域數量: 7
    ...
    ...    **輸出檔案:**
    ...    - Full image (含標註): motor_area_*_full_*.jpg
    ...    - ROI images: motor_area_*_roi_*.jpg
    [Tags]    motor    camera

    Log    === 開始擷取 Motor Camera 區域圖片 ===    console=True

    # 檢測 Motor 的 7 個區域
    When 用戶檢測實體燈光亮度 "motor_area_1"    save_debug_image=True    step_prefix=motor_area_1
    When 用戶檢測實體燈光亮度 "motor_area_2"    save_debug_image=True    step_prefix=motor_area_2
    When 用戶檢測實體燈光亮度 "motor_area_3"    save_debug_image=True    step_prefix=motor_area_3
    When 用戶檢測實體燈光亮度 "motor_area_4"    save_debug_image=True    step_prefix=motor_area_4
    When 用戶檢測實體燈光亮度 "motor_area_5"    save_debug_image=True    step_prefix=motor_area_5
    When 用戶檢測實體燈光亮度 "motor_area_6"    save_debug_image=True    step_prefix=motor_area_6
    When 用戶檢測實體燈光亮度 "motor_area_7"    save_debug_image=True    step_prefix=motor_area_7

    Log    ✅ Motor Camera 區域圖片擷取完成 (7 個區域)    console=True


測試案例 04: 完整報告 - 所有 Camera 統計
    [Documentation]    產生所有 Camera 的完整統計報告
    ...
    ...    **統計資訊:**
    ...    - 總 Camera 數: 3
    ...    - 總燈光/區域數: 31 (12+12+7)
    ...    - 擷取圖片數: 62 (31 full + 31 roi)
    [Tags]    report    summary

    Log    === 擷取完成統計報告 ===    console=True
    Log    🎥 Camera 統計:    console=True
    Log    - Level1 Camera: 12 個燈泡    console=True
    Log    - Level2 Camera: 12 個燈泡    console=True
    Log    - Motor Camera: 7 個區域    console=True
    Log    📊 總計:    console=True
    Log    - 總 Camera: 3    console=True
    Log    - 總燈光/區域: 31    console=True
    Log    - Full Images: 31 (含 ROI 標註)    console=True
    Log    - ROI Images: 31    console=True
    Log    📁 輸出位置: ${OUTPUT_DIR}    console=True
    Log    ✅ 所有圖片擷取完成!    console=True


*** Keywords ***
測試環境初始化
    [Documentation]    初始化測試環境

    Log    === 初始化環境燈光圖片擷取測試 ===    console=True
    Log    目標環境: ${ENVIRONMENT}    console=True

    # 設定測試環境
    Given 測試環境設定為 "${ENVIRONMENT}"
    
    # 設定面板類型 (載入環境燈光配置)
    Given 面板類型設定為 "3611a"

    # 確認輸出目錄存在
    Create Directory    ${OUTPUT_DIR}
    Log    輸出目錄已建立: ${OUTPUT_DIR}    console=True


測試環境清理
    [Documentation]    清理測試環境

    Log    === 清理測試資源 ===    console=True
    Log    ✅ 環境燈光圖片擷取測試執行完成    console=True
