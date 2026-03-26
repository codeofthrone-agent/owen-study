"""
RV 車空間擴展偵測 Robot Framework 關鍵字
開發日期: 2026-03-26

提供用於 BDD (Behavior-Driven Development) 測試案例之關鍵字。
利用 IPCamExpansionDetection 來判斷目前車廂的立體深度狀態。
"""

from robot.api.deco import keyword
from loguru import logger
from libraries.rv_space_detection.IPCamExpansionDetection import IPCamExpansionDetection

class IPCamExpansionKeywords:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self):
        self.detector = IPCamExpansionDetection()

    @keyword('Given 攝影機開始鎖定擴展目標 "${target_name}"')
    def given_camera_locking_on_target(self, target_name: str):
        """
        Given: 初始化並綁定指定的擴充空間標籤
        
        連接攝影機至特定的擴展物件，該物件需預先登記在 config/ipcam_config.yaml
        的 space_expansion 區塊中（例如 slide_out_wall 或 awning）。
        
        Arguments:
        - target_name: 設定檔中定義的目標名稱字串
        
        Prerequisites:
        - 攝影機網路必須正常，且 yaml 設定與實體的標籤匹配
        
        Examples:
        | Given 攝影機開始鎖定擴展目標 | slide_out_wall |
        """
        logger.info(f"RobotKeyword: 開始鎖定目標 {target_name}")
        self.detector.connect_for_expansion_target(target_name)

    @keyword('Then RV車內部空間應該已完全 "${state}"')
    def then_rv_space_should_be_in_state(self, state: str):
        """
        Then: 驗證指定空間的展延或收合狀態
        
        透過攝影畫格即時擷取特定的 ArUco 標籤面積，並比較預設的基準值。
        如果計算值沒有落在配置的誤差閾值之內，則自動觸發 Test Fail。
        
        Arguments:
        - state: 要驗證的預期物理狀態 (支援 '收合' 或是 '展開')
        
        Prerequisites:
        - 必須在先前執行 `Given 攝影機開始鎖定擴展目標`
        
        Examples:
        | Then RV車內部空間應該已完全 | 展開 |
        | Then RV車內部空間應該已完全 | 收合 |
        """
        status_map = {
            "收合": "collapsed",
            "展開": "expanded"
        }
        
        if state not in status_map:
            raise ValueError("狀態字串有誤：只能輸入 '收合' 或者是 '展開'。")
        
        logger.info(f"RobotKeyword: 正在驗證空間是否已達 '{state}' 狀態...")
        # 呼叫底層，如果不符合預期則會拋出 AssertionError
        self.detector.verify_expansion_state(status_map[state])

    @keyword('When 中斷擴展偵測的攝影機連線')
    def when_disconnect_expansion_detection(self):
        """
        When: 中斷背景串流截取
        
        當單次驗證完成後，手動呼叫此方法釋放攝影機的連線與網路資源。
        
        Examples:
        | When 中斷擴展偵測的攝影機連線 |
        """
        logger.info("RobotKeyword: 斷開標籤空間偵測連線")
        self.detector.disconnect()

    def __del__(self):
        try:
            self.detector.disconnect()
        except Exception:
            pass
