import os
import sys
from typing import Union
from pathlib import Path
from functools import lru_cache

from .file_tools import create_directory

__all__ = [
    'firefox_instance', 
    'chromium_instance',
    'edge_instance', 
    'ie_instance', 
    'opera_instance', 
    'ff_instance', 
    'safari_instance', 
    'playwright_instance'
]


def import_chrome():
    global webdriver, Service, ChromeOptions, ChromeDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options as ChromeOptions
    if 'ChromeDriverManager' not in globals():
        from webdriver_manager.chrome import ChromeDriverManager


def import_firefox():
    global webdriver, Service, FirefoxOptions, GeckoDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
    if 'GeckoDriverManager' not in globals():
        from webdriver_manager.firefox import GeckoDriverManager


def import_edge():
    global webdriver, Service, EdgeOptions, EdgeChromiumDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options as EdgeOptions
    if 'EdgeChromiumDriverManager' not in globals():
        from webdriver_manager.microsoft import EdgeChromiumDriverManager


def import_ie():
    global webdriver, Service, IeOptions, IEDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.ie.service import Service
        from selenium.webdriver.ie.options import Options as IeOptions
    if 'IEDriverManager' not in globals():
        from webdriver_manager.microsoft import IEDriverManager


def import_opera():
    global webdriver, Service, OperaOptions, OperaDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options as OperaOptions
    if 'OperaDriverManager' not in globals():
        from webdriver_manager.opera import OperaDriverManager


def import_ff():
    global webdriver, Service, FirefoxOptions, FfDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
    if 'GeckoDriverManager' not in globals():
        from webdriver_manager.firefox import GeckoDriverManager as FfDriverManager


def import_safari():
    global webdriver, Service, SafariOptions, SafariDriverManager
    if 'webdriver' not in globals():
        from selenium import webdriver
        from selenium.webdriver.safari.service import Service
        from selenium.webdriver.safari.options import Options as SafariOptions
    if 'SafariDriverManager' not in globals():
        from webdriver_manager.firefox import GeckoDriverManager as SafariDriverManager


def import_playwright():
    global sync_playwright
    if 'sync_playwright' not in globals():
        from playwright.sync_api import sync_playwright


@lru_cache(maxsize=None)
def to_str(path: Union[str, Path]) -> str:
    return str(path) if path is not None else None


def setup_proxy(profile, proxy):
    if proxy is None:
        return
    
    proxy_type = 'http'
    if '://' in proxy:
        proxy_type, proxy = proxy.split('://')
        proxy_type = proxy_type.lower()
    
    proxy_host, proxy_port = proxy.split(':')
    proxy_port = int(proxy_port)
    
    if proxy_type in ("http", "https", "socks"):
        profile.set_preference('network.proxy.type', 1)
        proxy_preferences = {
            "http": {
                'network.proxy.http': proxy_host, 'network.proxy.http_port': proxy_port,
                'network.proxy.ssl': proxy_host, 'network.proxy.ssl_port': proxy_port
            },
            "https": {
                'network.proxy.https': proxy_host, 'network.proxy.https_port': proxy_port,
                'network.proxy.ssl': proxy_host, 'network.proxy.ssl_port': proxy_port
            },
            "socks": {
                'network.proxy.socks': proxy_host, 'network.proxy.socks_port': proxy_port
            }
        }
        for key, value in proxy_preferences[proxy_type].items():
            profile.set_preference(key, value)


def firefox_instance(
    headless: bool = False,
    proxy: str = None,
    options: dict = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
    profile_path: Union[Path, str] = None,
    disable_images: bool = False,
):
    import_firefox()

    options = options or {}
    profile_path = to_str(profile_path) or str(Path(fr'{os.getenv("AppData")}') / r'Mozilla/Firefox/Profiles/8qrydh7k.default-release-1')
    create_directory(profile_path, auto=False)

    firefox_options = FirefoxOptions()
    profile = webdriver.FirefoxProfile(profile_path)

    if headless:
        firefox_options.add_argument("--headless")
    if user_agent:
        firefox_options.add_argument(f'--user-agent={user_agent}')
    if extension_path:
        firefox_options.add_extension(to_str(extension_path))
    if disable_images:
        profile.set_preference("permissions.default.image", 2)
    if download_path:
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", to_str(download_path))
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "binary/octet-stream")

    setup_proxy(profile, proxy)

    for k, v in options.items():
        profile.set_preference(k, v)

    profile.set_preference("network.http.use-cache", True)
    profile.set_preference("browser.cache.memory.enable", True)
    profile.set_preference("browser.cache.disk.enable", True)
    profile.update_preferences()

    service = Service(GeckoDriverManager().install())
    firefox_options.profile = profile

    return webdriver.Firefox(service=service, options=firefox_options)


def chromium_instance(
        headless: bool = False,
        proxy: str = None, 
        options: list = None, 
        extension_path: Union[str, Path] = None, 
        user_agent: str = None,
        download_path: Union[str, Path] = None, 
        profile_path: Union[Path, str] = None, 
        disable_images: bool = False,
        disable_javascript: bool = False, 
        log_level: int = 3
):
    import_chrome()

    options = options or []
    profile_path = to_str(profile_path) or str(Path(os.getenv("AppData")).parent / r'Local\Google\Chrome\User Data\Default')
    create_directory(profile_path, auto=False)

    chrome_options = ChromeOptions()
    download_path = to_str(download_path or '')

    prefs = {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': False,
        'safebrowsing.disable_download_protection': True,
        'profile.default_content_setting_values': {}
    }

    if headless:
        chrome_options.add_argument("--headless")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')
    if extension_path:
        chrome_options.add_extension(to_str(extension_path))
    if disable_javascript:
        prefs['profile.default_content_setting_values']['javascript'] = 2
    if disable_images:
        prefs['profile.default_content_setting_values']['images'] = 2

    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    chrome_options.add_argument(f"log-level={log_level}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-data-dir={profile_path}")

    for o in options:
        chrome_options.add_argument(o)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options, service=service)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
    driver.execute("send_command", params)

    return driver


def edge_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    profile_path: Union[Path, str] = None,
    download_path: Union[str, Path] = None
):
    import_edge()

    options = options or []
    profile_path = to_str(profile_path) or str(Path(os.getenv("AppData")).parent / r'Local\Microsoft\Edge\User Data\Default')
    create_directory(profile_path, auto=False)

    edge_options = EdgeOptions()
    profile = webdriver.EdgeProfile(profile_path)

    download_path = to_str(download_path or '')
    prefs = {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
    }

    if headless:
        edge_options.add_argument("--headless")
    if proxy:
        edge_options.add_argument(f"--proxy-server={proxy}")
    if user_agent:
        edge_options.add_argument(f'--user-agent={user_agent}')
    if extension_path:
        edge_options.add_extension(to_str(extension_path))

    edge_options.add_experimental_option('prefs', prefs)

    service = Service(EdgeChromiumDriverManager().install())
    edge_options.profile = profile

    return webdriver.Edge(options=edge_options, service=service)


def ie_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
):
    import_ie()

    ie_options = webdriver.IeOptions()

    if headless:
        ie_options.add_argument('-headless')
    if proxy:
        ie_options.add_argument(f'proxy-server={proxy}')
    if user_agent:
        ie_options.add_argument(f'user-agent={user_agent}')
    if download_path:
        ie_options.add_argument(f'download.default_directory={to_str(download_path)}')
    
    if options:
        for option in options:
            ie_options.add_argument(option)

    if extension_path:
        ie_options.add_extension(to_str(extension_path))

    service = Service(IEDriverManager().install())
    driver = webdriver.Ie(service=service, options=ie_options)

    return driver


def opera_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
):
    import_opera()

    opera_options = webdriver.ChromeOptions()
    opera_options.add_experimental_option('w3c', True)

    if headless:
        opera_options.add_argument('--headless')
    if proxy:
        opera_options.add_argument(f'--proxy-server={proxy}')
    if user_agent:
        opera_options.add_argument(f'--user-agent={user_agent}')
    if download_path:
        prefs = {
            'download.default_directory': to_str(download_path),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True
        }
        opera_options.add_experimental_option('prefs', prefs)
    
    if options:
        for option in options:
            opera_options.add_argument(option)

    if extension_path:
        opera_options.add_extension(to_str(extension_path))

    service = Service(OperaDriverManager().install())
    driver = webdriver.Opera(options=opera_options, service=service)

    return driver


def ff_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
    profile_path: Union[Path, str] = None,
    disable_images: bool = False,
    disable_javascript: bool = False,
    log_level: int = 3
):
    import_ff()

    options = options or []
    profile_path = to_str(profile_path) or str(Path(os.getenv("HOME")) / ".mozilla/firefox/default")
    create_directory(profile_path, auto=False)

    ff_options = FirefoxOptions()
    profile = webdriver.FirefoxProfile(profile_path)

    if headless:
        ff_options.add_argument("-headless")
    if proxy:
        proxy_parts = proxy.split("://")
        if len(proxy_parts) > 1:
            proxy_type, proxy_address = proxy_parts
        else:
            proxy_type, proxy_address = "http", proxy_parts[0]
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference(f"network.proxy.{proxy_type}", proxy_address.split(":")[0])
        profile.set_preference(f"network.proxy.{proxy_type}_port", int(proxy_address.split(":")[1]))
    if user_agent:
        profile.set_preference("general.useragent.override", user_agent)
    if download_path:
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", to_str(download_path))
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel")
    if disable_images:
        profile.set_preference("permissions.default.image", 2)
    if disable_javascript:
        profile.set_preference("javascript.enabled", False)

    for option in options:
        ff_options.add_argument(option)

    if extension_path:
        ff_options.add_argument(f"-profile {to_str(extension_path)}")

    profile.set_preference("webdriver.log.level", log_level)
    profile.update_preferences()

    service = Service(GeckoDriverManager().install())
    ff_options.profile = profile

    return webdriver.Firefox(service=service, options=ff_options)


def safari_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
):
    import_safari()

    if not sys.platform.startswith('darwin'):
        raise EnvironmentError("Safari浏览器只支持在macOS系统上运行")

    safari_options = webdriver.SafariOptions()

    if headless:
        # Safari不支持无头模式，这里会抛出警告
        print("警告：Safari不支持无头模式，将忽略headless参数")

    if proxy:
        # Safari不支持直接设置代理，需要在系统级别设置
        print("警告：Safari不支持通过WebDriver直接设置代理，请在系统设置中配置代理")

    if user_agent:
        # Safari不支持直接设置User-Agent，这里会抛出警告
        print("警告：Safari不支持通过WebDriver直接设置User-Agent")

    if download_path:
        # Safari不支持直接设置下载路径，这里会抛出警告
        print("警告：Safari不支持通过WebDriver直接设置下载路径，请在Safari浏览器设置中配置")

    if options:
        for option in options:
            # Safari支持的选项有限，这里简单地添加所有选项，但可能有些选项不会生效
            safari_options.add_argument(option)

    if extension_path:
        # Safari不支持通过WebDriver加载扩展，这里会抛出警告
        print("警告：Safari不支持通过WebDriver加载扩展")

    # 确保Safari的开发者模式已启用
    os.system("defaults write com.apple.Safari IncludeDevelopMenu -bool true")
    os.system("defaults write com.apple.Safari AllowRemoteAutomation -bool true")

    return webdriver.Safari(options=safari_options)


def playwright_instance(
    headless: bool = False,
    proxy: str = None,
    options: list = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
    browser_type: str = 'chromium'
):
    import_playwright()

    playwright = sync_playwright().start()
    
    browser_types = {
        'chromium': playwright.chromium,
        'firefox': playwright.firefox,
        'webkit': playwright.webkit
    }
    
    launch_options = {
        'headless': headless
    }
    
    if proxy:
        launch_options['proxy'] = {
            'server': proxy
        }
    
    if user_agent:
        launch_options['user_agent'] = user_agent
    
    if download_path:
        launch_options['downloads_path'] = str(download_path)
    
    if options:
        for option in options:
            key, value = option.split('=')
            launch_options[key.strip()] = value.strip()
    
    browser = browser_types[browser_type].launch(**launch_options)
    
    context = browser.new_context()
    
    if extension_path:
        context.add_init_script(path=str(extension_path))
    
    page = context.new_page()
    
    return {
        'playwright': playwright,
        'browser': browser,
        'context': context,
        'page': page
    }
