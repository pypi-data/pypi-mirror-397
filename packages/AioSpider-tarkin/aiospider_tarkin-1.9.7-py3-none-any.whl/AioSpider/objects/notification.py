from dataclasses import dataclass, field
from enum import Enum

from .logging import LogLevel

__all__ = [
    'RobotData',
    'DingDingRobotData',
    'WechatRobotData',
    'EmailRobotData',
    'EmailSmtp',
    'EmailPort',
    'NoticePlatformType',
    'NoticeType'
]


class EmailSmtp(Enum):
    smtp_qq = 'smtp.qq.com'
    smtp_163 = 'smtp.163.com'
    smtp_126 = 'smtp.126.com'
    smtp_139 = 'smtp.139.com'
    smtp_gmail = 'smtp.gmail.com'
    smtp_outlook = 'smtp.outlook.com'
    smtp_yahoo = 'smtp.mail.yahoo.com'
    smtp_hotmail = 'smtp.live.com'


class EmailPort(Enum):
    port_25 = 25
    port_465 = 465
    port_587 = 587
    port_994 = 994
    port_995 = 995


class NoticePlatformType(Enum):
    database = 'database'
    dingding = 'dingding'
    wechat = 'wechat'
    email = 'email'


class NoticeType(Enum):
    notice = '通知'
    warning = '预警'


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, slots=True)
class RobotData:
    enabled: bool                                           # 是否启用
    name: str = field(default=None)                         # 钉钉机器人名称
    type: NoticePlatformType                                # 机器人类型
    level: LogLevel = field(default=LogLevel.LEVEL4)        # 日志等级
    token: str                                              # 机器人token / 邮箱授权码
    sender: str = field(default='AioSpider')                # 通知人
    receiver: list = field(default_factory=list)            # 接收者 将会在群内@此人, 支持列表，可指定多人
    interval: int = field(default=60)                       # 报警时间间隔，防止刷屏
    max_per_minute: int = field(default=20)                 # 每分钟最大发送次数

    def __set__(self, owner, value: str) -> None:
        self.name = self.name or value


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, slots=True)
class DingDingRobotData(RobotData):
    type: NoticePlatformType = field(default=NoticePlatformType.dingding)


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, slots=True)
class WechatRobotData(RobotData):
    type: NoticePlatformType = field(default=NoticePlatformType.wechat)


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, slots=True)
class EmailRobotData(RobotData):
    type: NoticePlatformType = field(default=NoticePlatformType.email)
    smtp: EmailSmtp = field(default=EmailSmtp.smtp_qq)
    port: EmailPort = field(default=EmailPort.port_587)
    sender: str
