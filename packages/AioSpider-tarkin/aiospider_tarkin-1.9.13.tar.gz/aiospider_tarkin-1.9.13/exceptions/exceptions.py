class AioException(Exception):

    def __init__(self, msg: str, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args)

    def __str__(self):
        return f'{self.msg}'

    __repr__ = __str__


class SettingsConfigException(AioException):
    pass


class MiddlerwareException(AioException):
    pass


class RequestException(AioException):
    pass


class BloomFilterException(AioException):
    pass


class SpiderExeption(AioException):
    pass


class CmdConmandException(AioException):
    pass


class NoticeException(AioException):
    pass
