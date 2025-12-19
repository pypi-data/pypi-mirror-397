from typing import Callable, Dict, List, Optional, Union, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from AioSpider.objects import By, EventType

__all__ = ['Browser']


class Browser:

    def __init__(self, event_engine, webdriver):
        self.driver = webdriver
        self.event_engine = event_engine
        self.event_engine.register(EventType.BROWSER_QUIT, self.quit_browser)

    def navigate_to(self, url: str) -> None:
        """导航到指定URL"""
        self.driver.get(url)

    def refresh_page(self) -> None:
        """刷新当前页面"""
        self.driver.refresh()

    def execute_javascript(self, script: str, *args) -> Union[None, Dict, List, str]:
        """执行JavaScript代码"""
        return self.driver.execute_script(script, *args)

    def get_all_cookies(self) -> Dict[str, str]:
        """获取所有cookies"""
        return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}

    def find_single_element(self, locator: str, by: By = By.CSS_SELECTOR) -> Optional[object]:
        """查找单个元素"""
        return self.driver.find_element(by=by, value=locator)

    def find_multiple_elements(self, locator: str, by: By = By.CSS_SELECTOR) -> List[object]:
        """查找多个元素"""
        return self.driver.find_elements(by=by, value=locator)

    def get_current_page_source(self) -> str:
        """获取当前页面源代码"""
        return self.driver.page_source

    def set_implicit_wait(self, timeout: int) -> None:
        """设置隐式等待时间"""
        self.driver.implicitly_wait(timeout)

    def wait_for_condition(
            self, 
            condition: Callable, 
            timeout: int = 10, 
            poll_frequency: float = 0.5, 
            error_message: str = None
    ) -> Any:
        """等待直到满足特定条件"""
        return WebDriverWait(self.driver, timeout, poll_frequency).until(condition, error_message)

    def quit_browser(self) -> None:
        """退出浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def switch_to_frame(self, frame_reference: Union[str, int, object]) -> None:
        """切换到指定的frame"""
        self.driver.switch_to.frame(frame_reference)

    def switch_to_default_content(self) -> None:
        """切换回主文档"""
        self.driver.switch_to.default_content()

    def take_screenshot(self, filename: str) -> None:
        """截取当前页面截图"""
        self.driver.save_screenshot(filename)

    def scroll_to_element(self, element: object) -> None:
        """滚动到指定元素"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def hover_over_element(self, element: object) -> None:
        """鼠标悬停在指定元素上"""
        ActionChains(self.driver).move_to_element(element).perform()

    def drag_and_drop(self, source_element: object, target_element: object) -> None:
        """拖拽元素"""
        ActionChains(self.driver).drag_and_drop(source_element, target_element).perform()

    def open_new_tab(self, url: str) -> None:
        """打开新标签页并导航到指定URL"""
        self.driver.execute_script(f"window.open('{url}', '_blank');")

    def switch_to_tab(self, tab_index: int) -> None:
        """切换到指定索引的标签页"""
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def switch_to_tab_by_url(self, url: str) -> None:
        """切换到指定URL的标签页"""
        self.driver.switch_to.window(self.driver.window_handles[url])
    
    def close_current_tab(self) -> None:
        """关闭当前标签页"""
        self.driver.close()

    def get_all_windows(self) -> List[str]:
        """获取所有窗口句柄"""
        return self.driver.window_handles
    
    def get_current_window(self) -> str:
        """获取当前窗口句柄"""
        return self.driver.current_window_handle

    def clear_browser_data(self) -> None:
        """清除浏览器数据（cookies、缓存等）"""
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

    def wait_for_page_load(self, timeout: int = 30) -> None:
        """等待页面加载完成"""
        self.wait_for_condition(
            lambda d: d.execute_script("return document.readyState") == "complete",
            timeout=timeout,
            error_message="页面加载超时"
        )
    
    def wait_for_element_visible(self, locator: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
        """等待元素可见"""
        self.wait_for_condition(
            lambda d: d.find_element(by=by, value=locator).is_displayed(),
            timeout=timeout,
            error_message="元素不可见"
        )
    
    def wait_for_element_clickable(self, locator: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
        """等待元素可点击"""
        self.wait_for_condition(
            lambda d: d.find_element(by=by, value=locator).is_enabled(),
            timeout=timeout,
            error_message="元素不可点击"
        )

    def wait_for_element_present(self, locator: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
        """等待元素存在"""
        self.wait_for_condition(
            lambda d: d.find_element(by=by, value=locator),
            timeout=timeout,
            error_message="元素不存在"
        )
    
    def wait_for_element_not_present(self, locator: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
        """等待元素不存在"""
        self.wait_for_condition(
            lambda d: not d.find_element(by=by, value=locator),
            timeout=timeout,
            error_message="元素仍然存在"
        )

    def wait_for_alert_present(self, timeout: int = 10) -> None:
        """等待弹窗出现"""
        self.wait_for_condition(
            lambda d: d.switch_to.alert,
            timeout=timeout,
            error_message="弹窗未出现"
        )

    def wait_for_alert_not_present(self, timeout: int = 10) -> None:
        """等待弹窗消失"""
        self.wait_for_condition(
            lambda d: not d.switch_to.alert,
            timeout=timeout,
            error_message="弹窗仍然存在"
        )

    def wait_for_title_contains(self, title_substring: str, timeout: int = 10) -> None:
        """等待标题包含特定子字符串"""
        self.wait_for_condition(
            lambda d: title_substring in d.title,
            timeout=timeout,
            error_message="标题不包含特定子字符串"
        )
    
    def wait_for_title_not_contains(self, title_substring: str, timeout: int = 10) -> None:
        """等待标题不包含特定子字符串"""
        self.wait_for_condition(
            lambda d: title_substring not in d.title,
            timeout=timeout,
            error_message="标题仍然包含特定子字符串"
        )
        
