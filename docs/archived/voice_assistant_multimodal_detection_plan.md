# 語音助手多感官檢測完整方案

## 🎯 修正後的設計原則

### 核心需求（已修正）

> **語音助手必須同時具備「視覺回應」AND「聽覺回應」才算正確運作**

**完整驗證標準：**
1. ✅ **視覺回應** - 螢幕必須亮起/顯示變化
2. ✅ **聽覺回應** - 必須播放 "登登" 提示音
3. ✅ **綜合判定** - 兩者都通過才算成功

---

## 🎬 完整測試場景

```
步驟 1: PC 透過 Scarlett 4i4 聲道 1 播放 "Hey Power Pro"
        ↓
步驟 2: 語音助手聽到喚醒詞
        ↓
步驟 3: 語音助手必須同時：
        - 螢幕亮起/變化 (視覺回應)
        - 播放 "登登" 提示音 (聽覺回應)
        ↓
步驟 4: IP Camera RTSP 串流同時擷取：
        - 影像：檢測螢幕亮度變化
        - 音訊：檢測 "登登" 提示音
        ↓
步驟 5: 驗證邏輯：視覺 AND 聽覺
        - vision_detected = True
        - audio_detected = True
        - overall_success = (vision_detected AND audio_detected)
```

---

## 📐 修正後的核心程式碼

### VoiceAssistantDetection 核心邏輯（修正）

```python
def test_voice_assistant_response(
    self,
    wake_word: str,
    camera_env: str,
    camera_name: str,
    reference_sound: str = "登登",
    timeout: int = 10,
    require_both: bool = True  # 新增：是否要求兩者都通過
) -> dict:
    """
    完整的語音助手回應測試

    Args:
        wake_word: 喚醒詞（如 "Hey Power Pro"）
        camera_env: IP Camera 環境
        camera_name: IP Camera 名稱
        reference_sound: 參考聲音名稱（如 "登登"）
        timeout: 超時時間（秒）
        require_both: 是否要求視覺和聽覺都通過（預設：True）

    Returns:
        檢測結果字典：
        {
            'wake_word_sent': bool,       # 喚醒詞是否成功發送
            'vision_detected': bool,      # 視覺檢測結果
            'audio_detected': bool,       # 聽覺檢測結果
            'overall_success': bool,      # 綜合判定結果
            'vision_brightness': float,   # 視覺亮度值
            'audio_confidence': float,    # 聽覺信心度
            'require_both': bool,         # 驗證模式
            'failure_reason': str         # 失敗原因（如有）
        }
    """
    results = {
        'wake_word_sent': False,
        'vision_detected': False,
        'audio_detected': False,
        'overall_success': False,
        'vision_brightness': 0,
        'audio_confidence': 0.0,
        'require_both': require_both,
        'failure_reason': None
    }

    try:
        # 1. 連接 IP Camera
        logger.info(f"連接 IP Camera: {camera_env}/{camera_name}")
        self.vision_detector.connect_camera(camera_env, camera_name)
        rtsp_url = self.vision_detector.rtsp_url
        self.audio_detector = IPCamAudioDetection(rtsp_url)

        # 2. 獲取初始亮度（視覺基準線）
        initial_brightness = self.vision_detector.get_current_brightness()
        logger.info(f"初始亮度: {initial_brightness}")

        # 3. 播放喚醒詞 (透過 Scarlett 聲道 1)
        logger.info(f"播放喚醒詞: {wake_word}")
        success = self.voice_control.speak_text_to_channel(
            text=wake_word,
            channel=1,
            language='en',
            duration=3
        )
        results['wake_word_sent'] = success

        if not success:
            results['failure_reason'] = "喚醒詞發送失敗"
            return results

        # 4. 同時啟動音訊檢測（背景執行）
        logger.info("啟動音訊檢測（背景執行）")
        audio_thread = threading.Thread(
            target=self._detect_audio_background,
            args=(reference_sound, timeout, results)
        )
        audio_thread.daemon = True
        audio_thread.start()

        # 5. 視覺檢測（前景執行，等待螢幕變亮）
        logger.info("開始視覺檢測（等待螢幕變亮）")
        vision_detected, final_brightness = self.vision_detector.wait_for_brightness_change(
            initial_brightness=initial_brightness,
            increase_threshold=50,  # 亮度增加 50 以上視為變亮
            timeout=timeout
        )
        results['vision_detected'] = vision_detected
        results['vision_brightness'] = final_brightness

        # 6. 等待音訊檢測完成
        logger.info("等待音訊檢測完成")
        audio_thread.join(timeout=timeout + 2)

        # 7. 綜合判定（修正：AND 邏輯）
        if require_both:
            # 模式 A：兩者都要通過
            results['overall_success'] = (
                results['vision_detected'] AND results['audio_detected']
            )

            # 記錄失敗原因
            if not results['overall_success']:
                reasons = []
                if not results['vision_detected']:
                    reasons.append("視覺檢測失敗（螢幕未變亮）")
                if not results['audio_detected']:
                    reasons.append("聽覺檢測失敗（未偵測到提示音）")
                results['failure_reason'] = " & ".join(reasons)
        else:
            # 模式 B：任一通過即可（備用模式，供除錯使用）
            results['overall_success'] = (
                results['vision_detected'] or results['audio_detected']
            )

            if not results['overall_success']:
                results['failure_reason'] = "視覺和聽覺檢測都失敗"

        # 8. 記錄詳細結果
        logger.info("=" * 50)
        logger.info("語音助手檢測結果:")
        logger.info(f"  喚醒詞發送: {'✓' if results['wake_word_sent'] else '✗'}")
        logger.info(f"  視覺檢測: {'✓' if results['vision_detected'] else '✗'} (亮度: {results['vision_brightness']:.1f})")
        logger.info(f"  聽覺檢測: {'✓' if results['audio_detected'] else '✗'} (信心度: {results['audio_confidence']:.3f})")
        logger.info(f"  驗證模式: {'兩者都要通過 (AND)' if require_both else '任一通過即可 (OR)'}")
        logger.info(f"  綜合判定: {'✓ 成功' if results['overall_success'] else '✗ 失敗'}")
        if results['failure_reason']:
            logger.warning(f"  失敗原因: {results['failure_reason']}")
        logger.info("=" * 50)

        return results

    except Exception as e:
        logger.error(f"語音助手檢測執行失敗: {e}")
        results['failure_reason'] = f"執行異常: {str(e)}"
        return results

def _detect_audio_background(self, reference_sound: str,
                            timeout: int, results: dict):
    """背景執行音訊檢測"""
    try:
        logger.info(f"音訊檢測開始（參考聲音: {reference_sound}, 超時: {timeout}秒）")

        detected, confidence = self.audio_detector.detect_sound_in_rtsp(
            reference_sound=reference_sound,
            duration=timeout,
            threshold=0.75
        )

        results['audio_detected'] = detected
        results['audio_confidence'] = confidence

        logger.info(f"音訊檢測完成: {'✓ 檢測到' if detected else '✗ 未檢測到'} (信心度: {confidence:.3f})")

    except Exception as e:
        logger.error(f"音訊檢測執行失敗: {e}")
        results['audio_detected'] = False
        results['audio_confidence'] = 0.0
```

---

## 📋 Robot Framework 關鍵字（修正）

**檔案：** `resources/voice_assistant_keywords.robot`

```robotframework
*** Keywords ***
測試語音助手完整回應
    [Documentation]    測試語音助手是否同時具備視覺和聽覺回應
    ...
    ...    驗證邏輯：視覺 AND 聽覺都必須通過
    ...
    ...    參數：
    ...    - 喚醒詞: 要播放的喚醒詞（如 "Hey Power Pro"）
    ...    - 環境: IP Camera 環境名稱
    ...    - 攝影機: IP Camera 名稱
    ...    - 參考聲音: 要檢測的提示音（預設: 登登）
    ...    - 超時: 檢測超時時間（秒）
    ...
    ...    回傳：檢測結果字典
    [Arguments]    ${喚醒詞}    ${環境}    ${攝影機}    ${參考聲音}=登登    ${超時}=10

    Log    開始測試語音助手完整回應
    Log    喚醒詞: ${喚醒詞}
    Log    IP Camera: ${環境}/${攝影機}
    Log    參考聲音: ${參考聲音}
    Log    超時時間: ${超時}秒

    ${結果}=    Test Voice Assistant Response
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    reference_sound=${參考聲音}
    ...    timeout=${超時}
    ...    require_both=True

    RETURN    ${結果}

驗證語音助手完整回應成功
    [Documentation]    驗證語音助手同時具備視覺和聽覺回應
    ...
    ...    驗證標準：
    ...    1. 喚醒詞成功發送
    ...    2. 視覺檢測通過（螢幕變亮）
    ...    3. 聽覺檢測通過（偵測到提示音）
    ...    4. 綜合判定為成功
    [Arguments]    ${結果}

    # 1. 驗證喚醒詞發送
    Should Be True    ${結果['wake_word_sent']}
    ...    msg=喚醒詞發送失敗

    # 2. 驗證視覺回應
    Should Be True    ${結果['vision_detected']}
    ...    msg=視覺檢測失敗：螢幕未變亮（亮度: ${結果['vision_brightness']}）

    # 3. 驗證聽覺回應
    Should Be True    ${結果['audio_detected']}
    ...    msg=聽覺檢測失敗：未偵測到提示音（信心度: ${結果['audio_confidence']}）

    # 4. 驗證綜合判定
    Should Be True    ${結果['overall_success']}
    ...    msg=語音助手回應失敗：${結果.get('failure_reason', '未知原因')}

    # 5. 驗證信心度
    Should Be True    ${結果['audio_confidence']} > 0.7
    ...    msg=聽覺信心度過低：${結果['audio_confidence']}

    Log    ✓ 語音助手完整回應驗證通過
    Log    視覺亮度: ${結果['vision_brightness']}
    Log    聽覺信心度: ${結果['audio_confidence']}

記錄檢測詳細資料
    [Documentation]    記錄語音助手檢測的詳細結果
    [Arguments]    ${結果}

    Log    ========================================
    Log    語音助手檢測詳細結果
    Log    ========================================

    # 基本資訊
    Log    喚醒詞發送: ${'✓ 成功' if ${結果['wake_word_sent']} else '✗ 失敗'}
    Log    驗證模式: ${'兩者都要通過 (AND)' if ${結果['require_both']} else '任一通過即可 (OR)'}

    # 視覺檢測
    Log    ----------------------------------------
    Log    視覺檢測結果:
    Log    - 狀態: ${'✓ 檢測到變化' if ${結果['vision_detected']} else '✗ 未檢測到變化'}
    Log    - 亮度值: ${結果['vision_brightness']}

    # 聽覺檢測
    Log    ----------------------------------------
    Log    聽覺檢測結果:
    Log    - 狀態: ${'✓ 檢測到提示音' if ${結果['audio_detected']} else '✗ 未檢測到提示音'}
    Log    - 信心度: ${結果['audio_confidence']}

    # 綜合判定
    Log    ----------------------------------------
    Log    綜合判定: ${'✓ 成功' if ${結果['overall_success']} else '✗ 失敗'}

    Run Keyword If    '${結果.get('failure_reason')}' != 'None'
    ...    Log    失敗原因: ${結果['failure_reason']}    WARN

    Log    ========================================

驗證視覺和聽覺都有回應
    [Documentation]    明確驗證視覺和聽覺都有檢測到（別名關鍵字）
    [Arguments]    ${結果}

    驗證語音助手完整回應成功    ${結果}
```

---

## 🧪 測試案例（修正）

**檔案：** `tests/voice_assistant/multimodal_detection_test.robot`

```robotframework
*** Settings ***
Documentation    語音助手多感官檢測整合測試（視覺 AND 聽覺驗證）
Resource         ../../resources/voice_assistant_keywords.robot
Resource         ../../resources/voice_control_keywords.robot

Suite Setup      Suite 初始化
Suite Teardown   Suite 清理

*** Variables ***
${喚醒詞}           Hey Power Pro
${環境}             laboratory
${攝影機}           level1
${參考聲音}         登登
${超時時間}         10

*** Test Cases ***
Scenario: 測試語音助手完整回應（視覺 AND 聽覺）
    [Documentation]    測試語音助手是否同時具備視覺和聽覺回應
    ...
    ...    驗證標準：
    ...    1. 螢幕必須變亮（視覺回應）
    ...    2. 必須播放提示音（聽覺回應）
    ...    3. 兩者都通過才算成功
    [Tags]    voice_assistant    multimodal    critical

    Given Scarlett 音訊設備已就緒
    And IP Camera 已連接並正常運作

    When ${結果}=    測試語音助手完整回應
    ...    喚醒詞=${喚醒詞}
    ...    環境=${環境}
    ...    攝影機=${攝影機}
    ...    參考聲音=${參考聲音}
    ...    超時=${超時時間}

    Then 驗證語音助手完整回應成功    ${結果}
    And 記錄檢測詳細資料    ${結果}

    # 進階驗證
    And 視覺亮度應該明顯增加    ${結果}
    And 聽覺信心度應該充足    ${結果}

Scenario: 測試不同喚醒詞的回應
    [Documentation]    測試語音助手對不同喚醒詞的完整回應
    [Tags]    voice_assistant    wake_words

    @{喚醒詞列表}=    Create List
    ...    Hey Power Pro
    ...    Hello Assistant
    ...    Wake Up Device

    FOR    ${測試喚醒詞}    IN    @{喚醒詞列表}
        Log    測試喚醒詞: ${測試喚醒詞}    console=yes

        ${結果}=    測試語音助手完整回應
        ...    喚醒詞=${測試喚醒詞}
        ...    環境=${環境}
        ...    攝影機=${攝影機}

        驗證語音助手完整回應成功    ${結果}
        記錄檢測詳細資料    ${結果}

        Sleep    3s    reason=等待語音助手恢復待命狀態
    END

Scenario: 測試連續多次喚醒
    [Documentation]    測試語音助手連續多次喚醒的穩定性
    [Tags]    voice_assistant    stability

    ${測試次數}=    Set Variable    3

    FOR    ${次數}    IN RANGE    1    ${測試次數+1}
        Log    第 ${次數} 次測試    console=yes

        ${結果}=    測試語音助手完整回應
        ...    喚醒詞=${喚醒詞}
        ...    環境=${環境}
        ...    攝影機=${攝影機}

        驗證語音助手完整回應成功    ${結果}

        Run Keyword If    ${次數} < ${測試次數}
        ...    Sleep    5s    reason=等待語音助手恢復

        Log    第 ${次數} 次測試完成    console=yes
    END

Scenario: 驗證視覺檢測獨立運作（除錯用）
    [Documentation]    僅測試視覺檢測功能（除錯模式）
    [Tags]    voice_assistant    vision_debug

    # 使用特殊模式：只驗證視覺
    ${結果}=    Test Voice Assistant Response
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    require_both=False

    Should Be True    ${結果['vision_detected']}
    ...    msg=視覺檢測失敗

    記錄檢測詳細資料    ${結果}

Scenario: 驗證聽覺檢測獨立運作（除錯用）
    [Documentation]    僅測試聽覺檢測功能（除錯模式）
    [Tags]    voice_assistant    audio_debug

    # 使用特殊模式：只驗證聽覺
    ${結果}=    Test Voice Assistant Response
    ...    wake_word=${喚醒詞}
    ...    camera_env=${環境}
    ...    camera_name=${攝影機}
    ...    require_both=False

    Should Be True    ${結果['audio_detected']}
    ...    msg=聽覺檢測失敗

    記錄檢測詳細資料    ${結果}

*** Keywords ***
Suite 初始化
    [Documentation]    Suite 級別初始化
    Log    ========================================    console=yes
    Log    語音助手多感官檢測測試開始              console=yes
    Log    ========================================    console=yes

    # 檢查 Scarlett 設備
    ${scarlett_ok}=    檢查 Scarlett 設備
    Run Keyword If    not ${scarlett_ok}
    ...    Fatal Error    Scarlett 4i4 設備不可用

    # 驗證 IP Camera 連線
    驗證 IP Camera 可用    ${環境}    ${攝影機}

    Log    測試環境準備完成    console=yes

Suite 清理
    [Documentation]    Suite 級別清理
    清理語音控制資源

    Log    ========================================    console=yes
    Log    語音助手多感官檢測測試完成              console=yes
    Log    ========================================    console=yes

Scarlett 音訊設備已就緒
    [Documentation]    確認 Scarlett 4i4 設備就緒
    ${available}=    檢查 Scarlett 設備
    Should Be True    ${available}
    ...    msg=Scarlett 4i4 設備不可用

IP Camera 已連接並正常運作
    [Documentation]    確認 IP Camera 連線正常
    驗證 IP Camera 可用    ${環境}    ${攝影機}

驗證 IP Camera 可用
    [Documentation]    驗證 IP Camera 連線並可擷取影像
    [Arguments]    ${環境}    ${攝影機}

    # 這裡可以呼叫 IPCamLightDetection 驗證
    Log    驗證 IP Camera: ${環境}/${攝影機}

視覺亮度應該明顯增加
    [Documentation]    驗證視覺亮度增加幅度
    [Arguments]    ${結果}

    Should Be True    ${結果['vision_brightness']} > 100
    ...    msg=亮度增加不明顯: ${結果['vision_brightness']}

聽覺信心度應該充足
    [Documentation]    驗證聽覺檢測信心度
    [Arguments]    ${結果}

    Should Be True    ${結果['audio_confidence']} > 0.75
    ...    msg=信心度不足: ${結果['audio_confidence']}
```

---

## 📊 驗證邏輯對比表

| 場景 | 視覺檢測 | 聽覺檢測 | 驗證邏輯 | 結果 |
|------|---------|---------|---------|------|
| **正常運作** | ✓ 通過 | ✓ 通過 | AND | ✓ **成功** |
| **視覺失敗** | ✗ 失敗 | ✓ 通過 | AND | ✗ **失敗**（螢幕未亮） |
| **聽覺失敗** | ✓ 通過 | ✗ 失敗 | AND | ✗ **失敗**（無提示音） |
| **兩者都失敗** | ✗ 失敗 | ✗ 失敗 | AND | ✗ **失敗**（無回應） |

---

## 🎯 失敗原因診斷

```python
# 自動診斷失敗原因
if not results['overall_success']:
    if not results['vision_detected']:
        logger.error("視覺檢測失敗：可能原因")
        logger.error("  1. 螢幕未顯示回應")
        logger.error("  2. 亮度閾值設定過高")
        logger.error("  3. IP Camera 角度不佳")

    if not results['audio_detected']:
        logger.error("聽覺檢測失敗：可能原因")
        logger.error("  1. 提示音未播放")
        logger.error("  2. IP Camera 麥克風未收音")
        logger.error("  3. 參考聲音檔案不正確")
        logger.error("  4. 檢測閾值設定過高")
```

---

## ✅ 修正檢查清單

- [x] ✅ 修正驗證邏輯為 AND（視覺 AND 聽覺）
- [x] ✅ 新增 `require_both` 參數（預設 True）
- [x] ✅ 新增 `failure_reason` 詳細失敗原因
- [x] ✅ 更新 Robot 關鍵字文檔
- [x] ✅ 更新測試案例說明
- [x] ✅ 新增除錯模式測試案例
- [x] ✅ 新增失敗原因診斷邏輯

---

## 🚀 下一步實作

現在設計方案已修正完成，可以開始實作：

1. **建立 IPCamAudioDetection 模組**
2. **建立 VoiceAssistantDetection 整合模組**
3. **更新 Robot Framework 關鍵字**
4. **建立測試案例**
5. **重構 LocalVoiceVerifyingLibrary**

**請確認此修正後的方案是否符合需求？我可以立即開始實作！**
