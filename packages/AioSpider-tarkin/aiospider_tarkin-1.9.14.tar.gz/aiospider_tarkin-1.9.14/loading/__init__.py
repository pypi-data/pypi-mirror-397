from .load_settings import LoadSettings
from .load_browser import LoadBrowser
from .load_middleware import LoadMiddleware
from .load_models import LoadModels
from AioSpider.notice import CustomLogger


class BootLoader:

    def reload_settings(self, spider):
        return LoadSettings(spider)

    def reload_logger(self, engine):
        if hasattr(engine.settings, 'LoggingConfig'):
            config = engine.settings.LoggingConfig
        else:
            from AioSpider import settings
            config = settings.LoggingConfig
        CustomLogger(engine, config).init_log()

    def reload_middleware_manager(self, event_engine, spider, settings, browser):
        return LoadMiddleware(event_engine, spider, settings, browser)
    
    def reload_browser(self, event_engine, settings):
        return LoadBrowser(event_engine, settings)
    
    def reload_models(self, spider, settings):
        return LoadModels(spider, settings.DataBaseConfig)
