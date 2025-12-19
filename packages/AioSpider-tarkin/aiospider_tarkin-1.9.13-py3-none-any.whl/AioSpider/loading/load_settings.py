__all__ = ['LoadSettings']


class LoadSettings:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__()
        return instance.read_settings(*args, **kwargs)

    def __init__(self):
        self._usr_sts = None

    @property
    def usr_sts(self):
        if self._usr_sts is None:
            try:
                self._usr_sts = __import__('settings')
            except ImportError:
                self._usr_sts = None
        return self._usr_sts

    def read_settings(self, spider):
        """读取配置"""

        from AioSpider import settings

        if self.usr_sts:
            self.load_debug(settings)
            self.load_path(settings)
            self.load_logging(settings)
            self.load_server(settings)
            self.load_spider_request(settings, spider)
            self.load_concurrency_strategy(settings, spider)
            self.load_connect_pool(settings, spider)
            self.load_request_proxy(settings, spider)
            self.load_middleware(settings)
            self.load_data_filter(settings, spider)
            self.load_request_filter(settings, spider)
            self.load_browser(settings, spider)
            self.load_database(settings)

        return settings

    def _get_attrs(self, config):
        for i in dir(config):
            if i.startswith('__') or i.startswith('__'):
                continue
            yield i

    def load_debug(self, sys):
        if hasattr(self.usr_sts, 'DEBUG'):
            setattr(sys, 'DEBUG', getattr(self.usr_sts, 'DEBUG', False))

    def load_path(self, sys):
        if hasattr(self.usr_sts, 'AioSpiderPath'):
            setattr(sys, 'AioSpiderPath', getattr(self.usr_sts, 'AioSpiderPath', None))

    def load_logging(self, sys):
        if not hasattr(self.usr_sts, 'LoggingConfig'):
            return

        for c in ['Console', 'File', 'Robot', 'Database']:
            if hasattr(self.usr_sts.LoggingConfig, c) and hasattr(sys.LoggingConfig, c):
                user_config = getattr(self.usr_sts.LoggingConfig, c)
                sys_config = getattr(sys.LoggingConfig, c)
                for k, v in user_config.__dict__.items():
                    if not k.startswith('__'):
                        setattr(sys_config, k, v)

    def load_server(self, sys):

        if not hasattr(self.usr_sts, 'ServerConfig'):
            return

        for c in ['master', 'slaver']:
            for k, v in getattr(self.usr_sts.ServerConfig, c, {}).items():
                config = getattr(sys.ServerConfig, c, {})
                config[k] = v

    def load_spider_request(self, sys, spider):

        def update_config(target, source):

            for attr in self._get_attrs(source):
                    
                target_config = getattr(target, attr, {})
                source_config = getattr(source, attr)

                if isinstance(source_config, dict):
                    target_config.update(source_config)
                else:
                    setattr(target, attr, source_config)

        if hasattr(spider, 'SpiderRequestConfig'):
            if hasattr(self.usr_sts, 'SpiderRequestConfig'):
                update_config(self.usr_sts.SpiderRequestConfig, spider.SpiderRequestConfig)
            else:
                self.usr_sts.SpiderRequestConfig = spider.SpiderRequestConfig

        if hasattr(self.usr_sts, 'SpiderRequestConfig'):
            update_config(sys.SpiderRequestConfig, self.usr_sts.SpiderRequestConfig)

    def load_concurrency_strategy(self, sys, spider):

        def update_config(target, source):
            for attr in self._get_attrs(source):
                target_config = getattr(target, attr, {})
                source_config = getattr(source, attr)
                target_config.update(source_config)

        if hasattr(spider, 'ConcurrencyStrategyConfig'):
            if hasattr(self.usr_sts, 'ConcurrencyStrategyConfig'):
                update_config(self.usr_sts.ConcurrencyStrategyConfig, spider.ConcurrencyStrategyConfig)
            else:
                self.usr_sts.ConcurrencyStrategyConfig = spider.ConcurrencyStrategyConfig

        if hasattr(self.usr_sts, 'ConcurrencyStrategyConfig'):
            update_config(sys.ConcurrencyStrategyConfig, self.usr_sts.ConcurrencyStrategyConfig)

        # 互斥
        exclude = None
        for attr in self._get_attrs(sys.ConcurrencyStrategyConfig):
            if getattr(sys.ConcurrencyStrategyConfig, attr)['enabled']:
                exclude = attr
                break

        for attr in self._get_attrs(sys.ConcurrencyStrategyConfig):
            if exclude == attr:
                continue
            getattr(sys.ConcurrencyStrategyConfig, attr)['enabled'] = False

    def load_connect_pool(self, sys, spider):

        if not hasattr(self.usr_sts, 'ConnectPoolConfig'):
            return

        for c in ['Aiohttp', 'Requests', 'Httpx']:
            if hasattr(self.usr_sts.ConnectPoolConfig, c) and hasattr(sys.ConnectPoolConfig, c):
                user_config = getattr(self.usr_sts.ConnectPoolConfig, c)
                sys_config = getattr(sys.ConnectPoolConfig, c)
                for k, v in user_config.__dict__.items():
                    if not k.startswith('__'):
                        setattr(sys_config, k, v)

        if not hasattr(spider, 'ConnectPoolConfig'):
            return

        for c in ['Aiohttp', 'Request', 'Httpx']:
            if hasattr(spider.ConnectPoolConfig, c) and hasattr(sys.ConnectPoolConfig, c):
                user_config = getattr(spider.ConnectPoolConfig, c)
                sys_config = getattr(sys.ConnectPoolConfig, c)
                for k, v in user_config.__dict__.items():
                    if not k.startswith('__'):
                        setattr(sys_config, k, v)

    def load_request_proxy(self, sys, spider):

        def update_config(target, source):
            for attr in self._get_attrs(source):

                target_config = getattr(target, attr, {})
                source_config = getattr(source, attr)

                if isinstance(source_config, dict):
                    target_config.update(source_config)
                else:
                    setattr(target, attr, source_config)

        if hasattr(spider, 'RequestProxyConfig'):
            if hasattr(self.usr_sts, 'RequestProxyConfig'):
                update_config(self.usr_sts.RequestProxyConfig, spider.RequestProxyConfig)
            else:
                self.usr_sts.RequestProxyConfig = spider.RequestProxyConfig

        if hasattr(self.usr_sts, 'RequestProxyConfig'):
            update_config(sys.RequestProxyConfig, self.usr_sts.RequestProxyConfig)

    def load_middleware(self, sys):
        if hasattr(self.usr_sts, 'MIDDLEWARE'):
            setattr(sys, 'MIDDLEWARE', self.usr_sts.MIDDLEWARE)

    def load_data_filter(self, sys, spider):

        def update_config(target, source):
            for attr in self._get_attrs(source):
                setattr(target, attr, getattr(source, attr, None))

        if hasattr(spider, 'DataFilterConfig'):
            if hasattr(self.usr_sts, 'DataFilterConfig'):
                update_config(self.usr_sts.DataFilterConfig, spider.DataFilterConfig)
            else:
                self.usr_sts.DataFilterConfig = spider.DataFilterConfig

        if hasattr(self.usr_sts, 'DataFilterConfig'):
            update_config(sys.DataFilterConfig, self.usr_sts.DataFilterConfig)

    def load_request_filter(self, sys, spider):

        def update_config(target, source):
            for attr in self._get_attrs(source):
                setattr(target, attr, getattr(source, attr, None))

        if hasattr(spider, 'RequestFilterConfig'):
            if hasattr(self.usr_sts, 'RequestFilterConfig'):
                update_config(self.usr_sts.RequestFilterConfig, spider.RequestFilterConfig)
            else:
                self.usr_sts.RequestFilterConfig = spider.RequestFilterConfig

        if hasattr(self.usr_sts, 'RequestFilterConfig'):
            update_config(sys.RequestFilterConfig, self.usr_sts.RequestFilterConfig)

    def merge_config_attrs(self, new_config, old_config):
        """合并新旧配置属性"""

        if new_config is None:
            return
        for k in [i for i in dir(new_config) if not i.startswith('__')]:
            if not hasattr(old_config, k):
                setattr(old_config, k, getattr(new_config, k))
            elif isinstance(getattr(old_config, k), dict):
                getattr(old_config, k).update(getattr(new_config, k))
            elif callable(getattr(old_config, k)):
                self.merge_config_attrs(getattr(new_config, k), getattr(old_config, k))
            else:
                setattr(old_config, k, getattr(new_config, k))

    def load_database(self, sys):
        from AioSpider.objects import DataBaseType

        def _update_connect_config(target_config, new_connect):
            connect = getattr(target_config, 'connect')
            existing_aliases = {c.alias for c in connect}
            
            for new_conn in new_connect:
                if new_conn.alias in existing_aliases:
                    connect = [c for c in connect if c.alias != new_conn.alias]
                connect.append(new_conn)
            
            setattr(target_config, 'connect', connect)

        def update_config(target, source):
            for db_type in DataBaseType:
                target_config = getattr(target, db_type.value, None)
                source_config = getattr(source, db_type.value, None)

                if target_config is None or source_config is None:
                    continue

                for k, v in vars(source_config).items():
                    if k.startswith('__'):
                        continue
                    
                    if k == 'connect':
                        _update_connect_config(target_config, v)
                    else:
                        setattr(target_config, k, v)

        if hasattr(self.usr_sts, 'DataBaseConfig'):
            update_config(sys.DataBaseConfig, self.usr_sts.DataBaseConfig)

        return sys

    def load_browser(self, sys, spider):
        """合并浏览器配置"""

        def update_config(target, source):
            for attr in self._get_attrs(source):
                x = getattr(source, attr)
                y = getattr(target, attr)
                for i in self._get_attrs(x):
                    setattr(y, i, getattr(x, i, None))

        def other_browser_name(browser_name):
            return 'Firefox' if browser_name == 'Chromium' else 'Chromium'

        if hasattr(spider, 'BrowserConfig'):
            if hasattr(self.usr_sts, 'BrowserConfig'):
                update_config(self.usr_sts.BrowserConfig, spider.BrowserConfig)
            else:
                self.usr_sts.BrowserConfig = spider.BrowserConfig

        if hasattr(self.usr_sts, 'BrowserConfig'):
            update_config(sys.BrowserConfig, self.usr_sts.BrowserConfig)

        for browser_name in ('Chromium', 'Firefox'):
            new_browser = getattr(sys.BrowserConfig, browser_name)
            # 如果启用了一个浏览器，则禁用另一个
            if getattr(new_browser, 'enabled', False):
                setattr(getattr(sys.BrowserConfig, other_browser_name(browser_name)), 'enabled', False)
