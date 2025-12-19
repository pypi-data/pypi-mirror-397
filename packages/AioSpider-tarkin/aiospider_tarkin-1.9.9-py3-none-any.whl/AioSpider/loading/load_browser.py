__all__ = ['LoadBrowser']


class LoadBrowser:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance.init_browser(*args, **kwargs)

    def _init_browser_instance(self, event_engine, browser_config, browser_type):

        from AioSpider.objects import BrowserType
        from AioSpider.browser import Browser
        from AioSpider.tools import chromium_instance, firefox_instance

        headless = browser_config.headless
        log_level = browser_config.LogLevel
        disable_images = browser_config.DisableImages
        disable_javascript = browser_config.DisableJavaScript
        extension_path = browser_config.ExtensionPath
        proxy = browser_config.Proxy
        options = browser_config.Options
        user_agent = browser_config.UserAgent
        download_path = browser_config.DownloadPath
        profile_path = browser_config.ProfilePath

        if browser_type == BrowserType.chromium:
            return Browser(
                event_engine,
                chromium_instance(
                    headless=headless,
                    proxy=proxy, options=options, extension_path=extension_path, user_agent=user_agent,
                    download_path=download_path, profile_path=profile_path, disable_images=disable_images,
                    disable_javascript=disable_javascript, log_level=log_level
                )
            )
        elif browser_type == BrowserType.firefox:
            return Browser(
                event_engine,
                firefox_instance(
                    headless=headless,
                    proxy=proxy, options=options, extension_path=extension_path, user_agent=user_agent,
                    download_path=download_path, profile_path=profile_path, disable_images=disable_images
                )
            )
        else:
            return None

    def init_browser(self, event_engine, settings):

        if settings.BrowserConfig.Chromium.enabled:
            browser_config = settings.BrowserConfig.Chromium
            browser_type = "chromium"
        elif settings.BrowserConfig.Firefox.enabled:
            browser_config = settings.BrowserConfig.Firefox
            browser_type = "firefox"
        else:
            browser_config = None
            browser_type = None

        if browser_config:
            browser = self._init_browser_instance(event_engine, browser_config, browser_type)
            browser.implicitly_wait(settings.BrowserConfig.Firefox.ImplicitlyWait)
            return browser
        else:
            return None
