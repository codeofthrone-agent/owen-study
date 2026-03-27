"""
語音助理多模態檢測模組 - VoiceAssistantDetection

整合語音輸出、視覺檢測與 UART 日誌檢測，提供語音助理互動測試框架。

主要功能:
    1.  **觸發 (Trigger)**: 透過 `voice_control` 模組播放喚醒詞或指令。
    2.  **檢測 (Detect)**:
        -   **視覺**: 使用 `ipcam_light_detection` 模組檢測螢幕亮度變化（助理啟動的視覺回饋）。
        -   **聽覺**: 使用 `SerialLogParser` 解析 UART 日誌，檢測語音播放狀態。
    3.  **驗證 (Validate)**: 根據 AND 邏輯（視覺與聽覺都需成功）回報測試結果。

使用場景:
    -   自動化測試智慧音箱、語音助理等設備。
    -   驗證語音指令的端到端回應。
    -   在持續整合 (CI) 流程中進行回歸測試。

Robot Framework 使用範例:
    *** Settings ***
    Library    libraries/multimodal_detection/VoiceAssistantDetection.py

    *** Test Cases ***
    測試語音助理回應
        ${result}=    測試語音助理回應
        ...    wake_word=Hey Assistant
        ...    camera_env=living_room
        ...    camera_name=main_cam
        ...    scarlett_channel=1
        ...    uart_port=/dev/ttyS0

        Should Be True    ${result}[overall_success]    msg=語音助理回應測試失敗: ${result}[failure_reason]
        Log    視覺檢測: ${result}[vision_detected]
        Log    聽覺檢測: ${result}[audio_detected]
"""

import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
import os
from dotenv import load_dotenv

# 從 .env 檔案載入環境變數
load_dotenv()

# Robot Framework 支援
try:
    from robot.api.deco import keyword
    ROBOT_AVAILABLE = True
except ImportError:
    ROBOT_AVAILABLE = False
    def keyword(name=None, tags=None):
        def decorator(func):
            return func
        return decorator

# 匯入專案的模組
try:
    from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords
    from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
    from libraries.multimodal_detection.SerialLogParser import SerialLogParser
    from config.ipcam_config import get_camera_url
except ImportError as e:
    import sys
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from libraries.voice_control.VoiceControlKeywords import VoiceControlKeywords
        from libraries.ipcam_light_detection.IPCamLightDetection import IPCamLightDetection
        from libraries.multimodal_detection.SerialLogParser import SerialLogParser
        from config.ipcam_config import get_camera_url
    except ImportError as inner_e:
        logger.error(f"無法匯入必要的模組: {inner_e}")
        raise


class VoiceAssistantDetection:
    """
    語音助理多模態檢測 Library

    整合語音輸出、視覺檢測與 UART 日誌檢測。
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '3.1.0'  # 支援 .env 設定 UART Port

    def __init__(self):
        """初始化所有必要的檢測模組"""
        logger.info("初始化 VoiceAssistantDetection 模組...")

        self.voice_control = VoiceControlKeywords()
        self.light_detector = IPCamLightDetection()
        self.serial_parser: Optional[SerialLogParser] = None

        logger.info("所有子模組初始化完成")

    @keyword("測試語音助理回應")
    def test_voice_assistant_response(
        self,
        wake_word: str,
        camera_env: str,
        camera_name: str,
        uart_port: Optional[str] = None,
        uart_baudrate: int = 115200,
        scarlett_channel: int = 1,
        detection_timeout: int = 10,
        require_both: bool = True
    ) -> Dict[str, Any]:
        """
        執行語音助理多模態回應測試。

        流程:
        1.  連接 UART 並啟動背景監控。
        2.  透過 Scarlett 播放喚醒詞。
        3.  同時開始視覺（螢幕亮度）和聽覺（UART 日誌）檢測。
        4.  等待檢測完成或超時。
        5.  回報詳細的測試結果。

        參數:
            wake_word (str): 要播放的喚醒詞或指令。
            camera_env (str): IP 攝影機的環境配置 (如 'laboratory')。
            camera_name (str): IP 攝影機的名稱配置 (如 'level1')。
            uart_port (Optional[str]): UART 串列埠路徑。若為 None，則從環境變數 `UART_PORT` 讀取，預設為 '/dev/ttyUSB0'。
            uart_baudrate (int): UART 鮑率（預設 115200）。
            scarlett_channel (int): 播放喚醒詞的 Scarlett 聲道 (1-4)。
            detection_timeout (int): 檢測的超時時間（秒）。
            require_both (bool): 是否要求視覺和聽覺都成功（AND 邏輯）。

        回傳:
            (dict): 一個包含詳細結果的字典。
                - `overall_success` (bool): 整體測試是否成功。
                - `vision_detected` (bool | None): 視覺是否檢測成功。
                - `audio_detected` (bool | None): 聽覺是否檢測成功。
                - `vision_details` (str): 視覺檢測詳細資訊。
                - `audio_details` (str): 聽覺檢測詳細資訊（播放的檔案名稱）。
                - `failure_reason` (str): 失敗原因的摘要。
        """
        # 解析 UART Port
        final_uart_port = uart_port if uart_port is not None else os.getenv('UART_PORT', '/dev/ttyUSB0')

        logger.info("=" * 60)
        logger.info("開始語音助理多模態回應測試")
        logger.info(f"喚醒詞: '{wake_word}', 聲道: {scarlett_channel}")
        logger.info(f"攝影機: {camera_env}/{camera_name}")
        logger.info(f"UART: {final_uart_port} @ {uart_baudrate} (來源: {'參數' if uart_port else '環境變數或預設值'})")
        logger.info(f"超時: {detection_timeout}s")
        logger.info(f"驗證邏輯: {'AND (視覺與聽覺)' if require_both else 'OR (視覺或聽覺)'}")
        logger.info("=" * 60)

        # 準備結果字典
        result = {
            "overall_success": False,
            "vision_detected": None,
            "audio_detected": None,
            "vision_details": "Not run",
            "audio_details": "Not run",
            "failure_reason": "",
        }

        # -- 檢測線程的目標函數 --
        def vision_detection_thread():
            try:
                logger.info("[視覺線程] 開始等待燈光變化...")
                detected = self.light_detector.wait_for_light_change('on', timeout=detection_timeout)
                result["vision_detected"] = detected
                if detected:
                    brightness = self.light_detector.get_current_brightness()
                    result["vision_details"] = f"Success, brightness: {brightness:.2f}"
                    logger.info(f"[視覺線程] ✓ 成功檢測到螢幕變亮 (亮度: {brightness:.2f})")
                else:
                    result["vision_details"] = "Failure: Timeout"
                    logger.warning("[視覺線程] ✗ 等待螢幕變亮超時")
            except Exception as e:
                result["vision_detected"] = False
                result["vision_details"] = f"Error: {e}"
                logger.error(f"[視覺線程] 發生錯誤: {e}")

        try:
            # -- 步驟 1: 設定檢測模組 --
            logger.info("步驟 1: 設定檢測模組")
            self.light_detector.connect_camera(camera_env, camera_name)

            # 初始化 UART 解析器
            self.serial_parser = SerialLogParser(port=final_uart_port, baudrate=uart_baudrate)
            if not self.serial_parser.connect():
                result["audio_detected"] = False
                result["audio_details"] = "Error: Failed to connect UART"
                result["failure_reason"] = "UART 連接失敗"
                if require_both:
                    return result

            # 取得初始亮度
            initial_brightness = self.light_detector.get_current_brightness()
            logger.info(f"初始亮度: {initial_brightness:.1f}")

            # -- 步驟 2: 啟動 UART 背景監控 --
            logger.info("步驟 2: 啟動 UART 背景監控")
            if not self.serial_parser.start_monitoring():
                result["audio_detected"] = False
                result["audio_details"] = "Error: Failed to start UART monitoring"
                result["failure_reason"] = "UART 監控啟動失敗"
                if require_both:
                    return result

            logger.info("✓ UART 背景監控已啟動")
            time.sleep(0.5)  # 等待監控穩定

            # -- 步驟 3: 播放喚醒詞 --
            logger.info("步驟 3: 播放喚醒詞以觸發助理")
            self.voice_control.speak_text_to_channel(wake_word, scarlett_channel)
            logger.info("✓ 喚醒詞播放完成")

            # -- 步驟 4: 啟動視覺檢測線程（前景） --
            logger.info("步驟 4: 啟動視覺檢測線程")
            v_thread = threading.Thread(target=vision_detection_thread)
            v_thread.start()

            # -- 步驟 5: 等待檢測完成 --
            logger.info("步驟 5: 等待檢測完成...")

            # 等待視覺檢測
            v_thread.join(timeout=detection_timeout + 2)

            if v_thread.is_alive():
                logger.error("視覺檢測線程超時")
                result["vision_detected"] = False
                result["vision_details"] = "Failure: Thread timed out"

            # -- 步驟 6: 檢查 UART 日誌是否檢測到播放 --
            logger.info("步驟 6: 檢查 UART 日誌")
            audio_detected, audio_filename = self.serial_parser.check_playing_detected(timeout=2.0)

            result["audio_detected"] = audio_detected
            if audio_detected:
                result["audio_details"] = f"Detected: {audio_filename}"
                logger.info(f"✓ 檢測到語音播放: {audio_filename}")
            else:
                result["audio_details"] = "Not detected"
                logger.warning("✗ 未檢測到語音播放")

            # -- 步驟 7: 驗證結果 --
            logger.info("步驟 7: 驗證最終結果")
            vision_success = result["vision_detected"] is True
            audio_success = result["audio_detected"] is True

            if require_both:
                result["overall_success"] = vision_success and audio_success
            else:
                result["overall_success"] = vision_success or audio_success

            # 產生失敗原因
            failure_reasons = []
            if not result["overall_success"]:
                if not vision_success:
                    failure_reasons.append("視覺檢測失敗 (螢幕未變亮或超時)")
                if not audio_success:
                    failure_reasons.append("聽覺檢測失敗 (UART 日誌未檢測到播放)")
            result["failure_reason"] = " & ".join(failure_reasons)

            logger.info("-" * 60)
            logger.info("多模態測試結果:")
            logger.info(f"  - 視覺檢測: {'✓ 成功' if vision_success else '✗ 失敗'} ({result['vision_details']})")
            logger.info(f"  - 聽覺檢測: {'✓ 成功' if audio_success else '✗ 失敗'} ({result['audio_details']})")
            logger.info(f"  - 整體結果: {'✓ 成功' if result['overall_success'] else '✗ 失敗'}")
            if result["failure_reason"]:
                logger.warning(f"  - 失敗原因: {result['failure_reason']}")
            logger.info("-" * 60)

        except Exception as e:
            logger.error(f"多模態測試執行期間發生未預期錯誤: {e}")
            result["failure_reason"] = f"An unexpected error occurred: {e}"
            import traceback
            logger.error(traceback.format_exc())

        finally:
            # 清理資源
            self.voice_control.cleanup_voice_control_resources()
            self.light_detector.disconnect()

            if self.serial_parser:
                try:
                    self.serial_parser.stop_monitoring()
                    self.serial_parser.disconnect()
                except Exception as e:
                    logger.warning(f"UART 清理時發生錯誤: {e}")

            logger.info("資源清理完成")

        return result

if __name__ == "__main__":
    # 這是一個測試腳本，需要實際的硬體和配置才能運行
    print("="*50)
    print("VoiceAssistantDetection 測試腳本")
    print("="*50)
    print("注意: 此腳本需要連接到實際的攝影機和 Scarlett 音效卡才能正常運作。")
    print("請確保 `config/ipcam_config.py` 和相關硬體已正確設定。")
    print("UART Port 可透過 .env 檔案中的 `UART_PORT` 變數設定。")

    try:
        # 建立檢測器實例
        assistant_detector = VoiceAssistantDetection()

        # 模擬測試參數
        # uart_port 現在是可選的
        test_params = {
            "wake_word": "Hey Power Pro",
            "camera_env": "laboratory",
            "camera_name": "level1",
            # "uart_port": "/dev/ttyS0", # 可以取消註解以覆寫 .env 或預設值
            "uart_baudrate": 115200,
            "scarlett_channel": 1,
            "detection_timeout": 10,
            "require_both": True,
        }

        print("\n即將執行模擬測試...")
        print(f"參數: {test_params}")
        print("\n" + "-"*50)

        # 執行測試
        # 在實際運行中，這會觸發硬體操作
        # 此處僅為演示，可能會因為缺少硬體而失敗
        try:
            final_result = assistant_detector.test_voice_assistant_response(**test_params)
            print("\n測試執行完成。")
            print("最終結果:")
            import json
            print(json.dumps(final_result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"\n測試執行出錯: {e}")
            print("這在沒有連接硬體的情況下是正常的。")

    except Exception as e:
        print(f"\n初始化失敗: {e}")

    print("\n" + "="*50)
    print("測試腳本結束")
    print("="*50)
