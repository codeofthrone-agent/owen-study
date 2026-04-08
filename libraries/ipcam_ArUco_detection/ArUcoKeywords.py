#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Camera ArUco Detection Keywords
"""
import sys
from pathlib import Path
from typing import Dict, Optional, List
from robot.api.deco import keyword
from robot.api import logger

# 支援模組與路徑兩種匯入方式，與專案其他 library 保持一致
current_dir = Path(__file__).parent
try:
    from libraries.ipcam_ArUco_detection.ArUcoSpaceDetection import ArUcoSpaceDetection
except ImportError:
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from ArUcoSpaceDetection import ArUcoSpaceDetection

try:
    from config.robot_arm.config_loader import ConfigLoader
    from config.robot_arm.environment_config import EnvironmentConfig
except ImportError:
    # 僅在檔案路徑匯入時注入專案根目錄，避免常態污染 sys.path
    project_root = current_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from config.robot_arm.config_loader import ConfigLoader
    from config.robot_arm.environment_config import EnvironmentConfig

class ArUcoKeywords:
    """
    Keywords for IP Camera ArUco Space Detection
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # 儲存多個攝影機實體: {camera_name: ArUcoSpaceDetection_instance}
        self.detectors: Dict[str, ArUcoSpaceDetection] = {}
        self.config_loader = None
        self.current_environment = None

    @property
    def detector(self) -> 'ArUcoSpaceDetection':
        """
        取得預設攝影機實體 (為了向後相容)
        如果有多個攝影機，返回第一個；如果沒有，返回一個未連接的實體
        """
        if not self.detectors:
            return ArUcoSpaceDetection()
        return next(iter(self.detectors.values()))

    @keyword('Given 專屬攝影機已連線 "${environment}" "${camera_name}"')
    def given_camera_is_connected(self, environment: str, camera_name: str):
        """
        Given: 確認專屬攝影機已成功連線並初始化 ArUco 辨識
        Given: Confirm the specific camera is connected and ArUco detection is initialized
        
        此關鍵字負責初始化指定環境中的 IP Camera 影像串流與 ArUco 設定連線。
        This keyword initializes the IP Camera video stream and ArUco configuration in the specified environment.
        
        Arguments:
        - environment: 攝影機所在的環境名稱 (例如: 'rv_car')
        - camera_name: 攝影機識別名稱 (例如: 'camera3')
        
        Prerequisites:
        - 攝影機必須在網路上可訪問，且 yaml 設定檔內包含對應此攝影機之 RTSP URL 與相關 ArUco 參數配置。
        
        Examples:
        | Given | 專屬攝影機已連線 "rv_car" "camera3" |
        
        Returns:
            None
        """
        self.current_environment = environment
        
        if self.config_loader is None:
             self.config_loader = ConfigLoader(environment)

        if camera_name not in self.detectors:
            new_detector = ArUcoSpaceDetection()
            logger.info(f"正在連接攝影機: {environment} / {camera_name}")
            new_detector.connect_camera(environment, camera_name)
            self.detectors[camera_name] = new_detector
            logger.info(f"成功連接攝影機: {camera_name}")
        else:
            logger.info(f"攝影機 {camera_name} 已經連線，跳過初始化。")

    @keyword("When 取得當前車內空間狀態")
    def when_get_current_space_state(self) -> str:
        """
        When: 擷取並辨識目前空間的擴充/收合狀態
        When: Get current space state based on ArUco marker
        
        此關鍵字透過最新擷取的影像畫面，根據設定之信心水準與滑動視窗計算，判定目前空間所處的狀態（例如: "open", "close", "moving" 或 "unknown"）。
        This keyword grabs the latest image frame and calculates the space state based on settings like confidence threshold and sliding windows.
        
        Arguments:
        - 無 (使用預設或第一個連接的攝影機)
        
        Prerequisites:
        - 必須先透過 'Given 專屬攝影機已連線' 完成攝影機連接操作。
        
        Examples:
        | When | 取得當前車內空間狀態 |
        
        Returns:
            str: 狀態字串 (如 'open', 'close', 'moving' 等)
        """
        if not self.detectors:
            raise RuntimeError("尚未連接攝影機，請先使用 'Given 專屬攝影機已連線'")
        
        state = self.detector.get_current_space_state()
        logger.info(f"當前車內空間狀態為: {state}")
        return state

    @keyword('When 觀察並記錄空間動態 "${duration_sec}" 秒')
    def when_monitor_space_changes(self, duration_sec: str) -> List[str]:
        """
        When: 持續監控畫面動態狀態轉換
        When: Monitor and record space dynamic state changes
        
        此關鍵字在指定秒數內，持續辨識空間狀態，並將這段時間內的狀態變化依時間順序記錄下來。這對於驗證擴充或收合的漸變過程非常有用。
        This keyword continuously monitors space states and records the state changes over the given duration. Useful for capturing the progression of expansion/retraction.
        
        Arguments:
        - duration_sec: 欲觀察的持續時間（秒）(例如: '5')
        
        Prerequisites:
        - 必須先透過 'Given 專屬攝影機已連線' 完成攝影機連接。
        
        Examples:
        | When | 觀察並記錄空間動態 "5" 秒 |
        
        Returns:
            list[str]: 一段時間內的狀態列表，例如 ['close', 'moving', 'open']
        """
        if not self.detectors:
            raise RuntimeError("尚未連接攝影機，請先使用 'Given 專屬攝影機已連線'")
            
        duration = int(duration_sec)
        logger.info(f"開始觀察動態，持續 {duration} 秒...")
        history = self.detector.monitor_space_changes(duration)
        logger.info(f"觀察結果紀錄: {history}")
        return history

    @keyword("And 斷開攝影機連線")
    def and_disconnect_camera(self):
        """
        And: 安全釋放資源，切斷即時 RTSP 影像連線
        And: Stop connection and release resources safely
        
        此關鍵字負責關閉所有已經連線的攝影機資源並釋放記憶體。
        This keyword stops and disconnects all established camera streams and clears up resources.
        
        Arguments:
        - 無
        
        Prerequisites:
        - 無 (即使未連線也可安全呼叫)
        
        Examples:
        | And | 斷開攝影機連線 |
        
        Returns:
            None
        """
        if self.detectors:
            for cam_name, detector in self.detectors.items():
                logger.info(f"正在斷開攝影機 {cam_name}...")
                detector.disconnect()
            self.detectors.clear()
            logger.info("已經安全斷開所有攝影機連線。")
        else:
            logger.info("無攝影機連接，無需斷開。")

    @keyword('Then 車內空間狀態應該為 "${expected_state}"')
    def then_space_state_should_be(self, expected_state: str):
        """
        Then: 驗證車內空間狀態應符合預期狀態
        Then: Verify the current space state matches the expected state
        
        此關鍵字會立刻取得車內空間狀態，並與預期字串做比對。如果不吻合，將拋出 AssertionError 中止測試。
        This keyword asserts the current space status matches the passed-in expected state. Fails the test specifically if they diverge.
        
        Arguments:
        - expected_state: 預期的狀態字串 (如: 'open', 'close', 'moving', 'unknown')
        
        Prerequisites:
        - 攝影機已連線。
        
        Examples:
        | Then | 車內空間狀態應該為 "open" |
        
        Returns:
            None
        """
        if not self.detectors:
            raise AssertionError("尚未連接攝影機，無法進行狀態驗證。請先執行 'Given 專屬攝影機已連線'。")
        
        actual_state = self.detector.get_current_space_state()
        if actual_state != expected_state:
            raise AssertionError(f"空間狀態不符！預期狀態為: {expected_state}，但實際為: {actual_state}")
        logger.info(f"驗證通過：車內空間狀態正確為 {expected_state}")

    @keyword('Then 動態觀察狀態應包含 "${expected_state}"')
    def then_space_movement_should_include(self, expected_state: str, history: List[str] = None):
        """
        Then: 驗證觀察紀錄中應包含指定狀態
        Then: Verify the monitoring history includes the expected state
        
        此關鍵字會檢查前一步驟 (When 觀察並記錄空間動態) 所回傳的歷史紀錄，驗證是否包含期望的狀態。
        This keyword verifies if the previously retrieved history of states includes the expected specific state.
        
        Arguments:
        - expected_state: 預期的狀態字串 (如: 'moving', 'open')
        - history (可選): 必須是上一動作的觀察結果。
        
        Prerequisites:
        - 必須有來自 'When 觀察並記錄空間動態' 的回傳清單作為 history 傳入。
        
        Examples:
        | ${history}= | When 觀察並記錄空間動態 "5" 秒 |
        | Then | 動態觀察狀態應包含 "moving" | ${history} |
        
        Returns:
            None
        """
        if history is None or not isinstance(history, list):
            raise AssertionError("未提供正確的動態觀察歷史紀錄 (history)。請確定有從 When 觀察關鍵字接收回傳值，並正確傳入本關鍵字。")
        
        if expected_state not in history:
            raise AssertionError(f"動態觀察紀錄驗證失敗！預期應出現狀態 {expected_state}，但僅有: {history}")
        
        logger.info(f"驗證通過：動態過程中成功包含了 {expected_state} 狀態。")
