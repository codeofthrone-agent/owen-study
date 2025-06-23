"""
Appium 基礎庫 - 提供移動設備測試的核心功能

此模組封裝了 Appium 的基本操作，提供統一的 API 介面用於 iOS 和 Android 測試。
包含設備連接、應用管理、元素操作等核心功能。

Author: Robot Framework Team
Date: 2025-06-23
"""

import time
import os
from typing import Optional, Dict, Any, List, Tuple
from appium import webdriver
try:
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    # 使用 Selenium 的 By 作為替代
    from selenium.webdriver.common.by import By as AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from robot.api.deco import keyword
from robot.api import logger

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.mobile.appium_config import appium_config


class AppiumLibrary:
    """Appium 測試庫基礎類別"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """初始化 Appium 測試庫"""
        self.driver: Optional[webdriver.Remote] = None
        self.wait: Optional[WebDriverWait] = None
        self.default_timeout = 10
        self.current_platform = None
        logger.info("Appium 測試庫初始化完成")
    
    @keyword("Open Application")
    def open_application(self, platform: str, **kwargs) -> None:
        """
        開啟移動應用程式
        
        Args:
            platform (str): 平台名稱 ('ios' 或 'android')
            **kwargs: 額外的能力配置
        
        Example:
            | Open Application | ios | bundleId=com.example.app |
            | Open Application | android | appPackage=com.example.app | appActivity=.MainActivity |
        """
        try:
            # 驗證配置
            if not appium_config.validate_config(platform):
                raise ValueError(f"平台 {platform} 的配置不完整")
            
            # 獲取能力配置
            capabilities = appium_config.get_capability(platform, **kwargs)
            server_url = appium_config.get_server_url()
            
            logger.info(f"連接 Appium 伺服器: {server_url}")
            logger.info(f"使用能力配置: {capabilities}")
            
            # 建立 WebDriver 連接
            self.driver = webdriver.Remote(server_url, capabilities)
            self.wait = WebDriverWait(self.driver, self.default_timeout)
            self.current_platform = platform.lower()
            
            logger.info(f"成功開啟 {platform} 應用程式")
            
        except Exception as e:
            logger.error(f"開啟應用程式失敗: {str(e)}")
            raise
    
    @keyword("Close Application")
    def close_application(self) -> None:
        """
        關閉當前應用程式
        
        Example:
            | Close Application |
        """
        try:
            if self.driver:
                self.driver.quit()
                logger.info("應用程式已關閉")
            else:
                logger.warn("沒有活動的應用程式連接")
        except Exception as e:
            logger.error(f"關閉應用程式失敗: {str(e)}")
        finally:
            self.driver = None
            self.wait = None
            self.current_platform = None
    
    @keyword("Click Element")
    def click_element(self, locator: str, timeout: Optional[int] = None) -> None:
        """
        點擊元素
        
        Args:
            locator (str): 元素定位器
            timeout (int, optional): 等待超時時間（秒）
        
        Example:
            | Click Element | id=submit_button |
            | Click Element | xpath=//button[@text='提交'] | timeout=15 |
        """
        element = self._find_element(locator, timeout)
        element.click()
        logger.info(f"已點擊元素: {locator}")
    
    @keyword("Input Text")
    def input_text(self, locator: str, text: str, timeout: Optional[int] = None) -> None:
        """
        在元素中輸入文字
        
        Args:
            locator (str): 元素定位器
            text (str): 要輸入的文字
            timeout (int, optional): 等待超時時間（秒）
        
        Example:
            | Input Text | id=username | testuser |
            | Input Text | xpath=//input[@name='password'] | mypassword | timeout=10 |
        """
        element = self._find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        logger.info(f"已在元素 {locator} 中輸入文字: {text}")
    
    @keyword("Get Text")
    def get_text(self, locator: str, timeout: Optional[int] = None) -> str:
        """
        獲取元素文字內容
        
        Args:
            locator (str): 元素定位器
            timeout (int, optional): 等待超時時間（秒）
        
        Returns:
            str: 元素的文字內容
        
        Example:
            | ${text}= | Get Text | id=message |
            | Should Be Equal | ${text} | 登入成功 |
        """
        element = self._find_element(locator, timeout)
        text = element.text
        logger.info(f"獲取元素 {locator} 的文字: {text}")
        return text
    
    @keyword("Element Should Be Visible")
    def element_should_be_visible(self, locator: str, timeout: Optional[int] = None) -> None:
        """
        驗證元素是否可見
        
        Args:
            locator (str): 元素定位器
            timeout (int, optional): 等待超時時間（秒）
        
        Example:
            | Element Should Be Visible | id=welcome_message |
        """
        element = self._find_element(locator, timeout)
        if not element.is_displayed():
            raise AssertionError(f"元素 {locator} 不可見")
        logger.info(f"元素 {locator} 可見")
    
    @keyword("Wait Until Element Is Visible")
    def wait_until_element_is_visible(self, locator: str, timeout: Optional[int] = None) -> None:
        """
        等待元素變為可見
        
        Args:
            locator (str): 元素定位器
            timeout (int, optional): 等待超時時間（秒）
        
        Example:
            | Wait Until Element Is Visible | id=loading_spinner | timeout=30 |
        """
        self._find_element(locator, timeout)
        logger.info(f"元素 {locator} 已變為可見")
    
    @keyword("Swipe")
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000) -> None:
        """
        在螢幕上滑動
        
        Args:
            start_x (int): 起始 X 座標
            start_y (int): 起始 Y 座標
            end_x (int): 結束 X 座標
            end_y (int): 結束 Y 座標
            duration (int): 滑動持續時間（毫秒）
        
        Example:
            | Swipe | 200 | 500 | 200 | 300 | duration=1500 |
        """
        self._ensure_driver()
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        logger.info(f"滑動從 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
    
    @keyword("Scroll Down")
    def scroll_down(self, duration: int = 1000) -> None:
        """
        向下滾動螢幕
        
        Args:
            duration (int): 滾動持續時間（毫秒）
        
        Example:
            | Scroll Down |
            | Scroll Down | duration=1500 |
        """
        self._ensure_driver()
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 3 // 4
        end_y = size['height'] // 4
        
        self.swipe(start_x, start_y, start_x, end_y, duration)
        logger.info("向下滾動螢幕")
    
    @keyword("Scroll Up")
    def scroll_up(self, duration: int = 1000) -> None:
        """
        向上滾動螢幕
        
        Args:
            duration (int): 滾動持續時間（毫秒）
        
        Example:
            | Scroll Up |
            | Scroll Up | duration=1500 |
        """
        self._ensure_driver()
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] // 4
        end_y = size['height'] * 3 // 4
        
        self.swipe(start_x, start_y, start_x, end_y, duration)
        logger.info("向上滾動螢幕")
    
    @keyword("Take Screenshot")
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        擷取螢幕截圖
        
        Args:
            filename (str, optional): 截圖檔案名稱，不提供時自動生成
        
        Returns:
            str: 截圖檔案路徑
        
        Example:
            | Take Screenshot |
            | Take Screenshot | filename=error_screen.png |
        """
        self._ensure_driver()
        
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = os.path.join(self._get_screenshot_dir(), filename)
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"截圖已儲存: {screenshot_path}")
        
        return screenshot_path
    
    @keyword("Get Current Activity")
    def get_current_activity(self) -> str:
        """
        獲取當前 Android Activity（僅 Android）
        
        Returns:
            str: 當前 Activity 名稱
        
        Example:
            | ${activity}= | Get Current Activity |
        """
        self._ensure_driver()
        if self.current_platform != 'android':
            raise RuntimeError("此功能僅支援 Android 平台")
        
        activity = self.driver.current_activity
        logger.info(f"當前 Activity: {activity}")
        return activity
    
    def _find_element(self, locator: str, timeout: Optional[int] = None) -> WebElement:
        """
        查找元素的內部方法
        
        Args:
            locator (str): 元素定位器
            timeout (int, optional): 等待超時時間
        
        Returns:
            WebElement: 找到的元素
        
        Raises:
            TimeoutException: 當元素在超時時間內未找到
        """
        self._ensure_driver()
        
        timeout = timeout or self.default_timeout
        by, value = self._parse_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            raise TimeoutException(f"在 {timeout} 秒內未找到元素: {locator}")
    
    def _parse_locator(self, locator: str) -> Tuple[str, str]:
        """
        解析定位器字符串
        
        Args:
            locator (str): 定位器字符串（如: "id=myid", "xpath=//div"）
        
        Returns:
            Tuple[str, str]: (定位方法, 定位值)
        """
        if '=' not in locator:
            raise ValueError(f"無效的定位器格式: {locator}")
        
        by, value = locator.split('=', 1)
        
        locator_map = {
            'id': AppiumBy.ID,
            'xpath': AppiumBy.XPATH,
            'name': AppiumBy.NAME,
            'class': AppiumBy.CLASS_NAME,
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'android_uiautomator': AppiumBy.ANDROID_UIAUTOMATOR,
            'ios_predicate': AppiumBy.IOS_PREDICATE,
            'ios_class_chain': AppiumBy.IOS_CLASS_CHAIN,
        }
        
        if by not in locator_map:
            raise ValueError(f"不支援的定位方法: {by}")
        
        return locator_map[by], value
    
    def _ensure_driver(self) -> None:
        """確保 WebDriver 已初始化"""
        if not self.driver:
            raise RuntimeError("應用程式尚未開啟，請先使用 'Open Application' 關鍵字")
    
    def _get_screenshot_dir(self) -> str:
        """獲取截圖目錄路徑"""
        screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        return screenshot_dir
