import time
import sys
import asyncio
from enum import Enum
from functools import partial
from typing import List, Dict, Any
from pathlib import Path

from loguru import logger
from AioSpider.objects import (
    Attribute,
    Color,
    Style,
    LogLevel,
    RobotData,
    NoticePlatformType,
    NoticeType
)
from AioSpider.exceptions import SettingsConfigException

from .dingding import DingDingGroupRobot
from .wechat import WeChatGroupRobot
from .email import EmailRobot
from .message import NoticeMessage


class NotificationRobotContext:

    def __init__(self, robot_data: RobotData):
        self.robot_data = robot_data
        self.robot = self._init_robot()
        self.last_send_time = 0
        self.send_count = 0

    def _init_robot(self):
        robot_types = {
            NoticePlatformType.dingding: DingDingGroupRobot,
            NoticePlatformType.wechat: WeChatGroupRobot,
            NoticePlatformType.email: EmailRobot
        }
        robot_class = robot_types.get(self.robot_data.type)
        return robot_class(smtp=self.robot_data.smtp, port=self.robot_data.port, token=self.robot_data.token, sender=self.robot_data.sender, receiver=self.robot_data.receiver) if robot_class else None

    async def send_msg(self, message):
        current_time = time.time()
        if current_time - self.last_send_time <= self.robot_data.interval:
            return
        if current_time - self.last_send_time < 60 and self.send_count >= self.robot_data.max_per_minute:
            return
        await self.robot.send_text(subject='爬虫预警', body=message)
        self.last_send_time = current_time
        self.send_count += 1


class CustomLogger:

    def __init__(self, engine, config: Any):
        self.engine = engine
        self.config = config
        self._remove_default_levels()
        self._setup_custom_levels()

    def _remove_default_levels(self):
        logger.remove()
        logger._core.levels.clear()

    def _setup_custom_levels(self):
        for level in LogLevel:
            logger.level(level.name, no=level.value)
            setattr(logger, level.name.lower(), partial(self._level, level=level))
        logger.debug = logger.info = logger.warning = logger.error = logger.trace = logger.critical = logger.exception = None

    def init_log(self):
        if not (hasattr(self.config, 'Console') and hasattr(self.config, 'File')):
            raise SettingsConfigException('日志类型配置错误')

        if self.config.Console.enabled:
            self._add_console(self.config.Console)

        if self.config.File.enabled:
            self._add_file(self.engine.spider.name, self.config.File)

        robot_datas = [
            getattr(self.config.Robot, attr) for attr in dir(self.config.Robot)
            if isinstance(getattr(self.config.Robot, attr), RobotData) and getattr(self.config.Robot, attr).enabled
        ]
        for robot_data in robot_datas:
            self._add_robot(robot_data)

        if self.config.Database.enabled:
            self._add_database(self.config.Database.model, self.config.Database.level)

    def _add_robot(self, robot_data: RobotData):
        def robot_sink(message, robot: NotificationRobotContext):
            """同步包装器，用于在loguru的线程环境中执行异步邮件发送"""
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(robot.send_msg(message))

        context_sink = partial(robot_sink, robot=NotificationRobotContext(robot_data))
        logger.add(context_sink, level=robot_data.level.value, format=self._build_robot_format(robot_data.receiver), enqueue=True)

    def _build_robot_format(self, receiver: List[str]):
        def formattere(record, receiver: str):
            return str(NoticeMessage(
                notice_time=record['time'].strftime('%Y-%m-%d %H:%M:%S'),
                message=record['message'],
                level=record['level'].name,
                spider_name=self.engine.spider.name,
                task_id=(self.engine.task_model and self.engine.task_model.task_id) or None,
                exception_stack=record.get('exception') or '-',
                contact_list=receiver
            ))

        receiver = ['@all'] if not receiver else [f'@{i}' for i in receiver]
        return partial(formattere, receiver=receiver)

    def _add_console(self, console):
        logger.add(sys.stdout, level=console.level.value, format=self._build_console_format(console), colorize=True)

    def _build_console_format(self, console):
        def formatter(record):
            return self._format_log_message(record, console.format.value, console.time_format.value)

        return formatter

    def _format_log_message(self, record: Dict[str, Any], format_config: List[tuple], time_format: str) -> str:
        fmt = []
        for item, color, style in format_config:
            fmt.append(self._format_attribute(item, color, style, record, time_format))
        return ' <white>|</white> '.join(fmt) + '\n'

    def _format_attribute(
            self, item: Attribute, color: Color, style: Style, record: Dict[str, Any], time_format: str
    ) -> str:
        style_str = f"<{style.value}>" if style else ""
        style_end = f"</{style.value}>" if style else ""

        if item in [Attribute.level, Attribute.message]:
            color = self._get_level_color(color, record['level'].name)

        if isinstance(color, Enum):
            color = color.value

        color_str = f"<{color}>" if color else ""
        color_end = f"</{color}>" if color else ""

        content = self._get_attribute_content(item, record, time_format)

        return f"{color_str}{style_str}{content}{style_end}{color_end}"

    def _get_level_color(self, color: Color, level_name: str) -> str:
        if color is None:
            return 'level'
        if isinstance(color, tuple):
            color = color + (color[-1],) * (7 - len(color))
            level_index = [i.name for i in LogLevel].index(level_name)
            return color[level_index].value
        if isinstance(color, Enum):
            return color.value
        raise ValueError(f'Invalid color value: {color}')

    def _get_attribute_content(self, item: Attribute, record: Dict[str, Any], time_format: str) -> str:
        attribute_formats = {
            Attribute.time: f"{{time:{time_format}}}",
            Attribute.module: "{module:^8}",
            Attribute.function: "{function:^8}",
            Attribute.line: "{line:>3}",
            Attribute.level: "{level:7}"
        }
        return attribute_formats.get(item, f"{{{item.value}}}")

    def _add_file(self, name: str, file):
        file_dir = Path(file.path) / name
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = file_dir / "{time}.log"

        size = f"{int(file.size)}B" if isinstance(file.size, (int, float)) else file.size
        kwargs = {
            'sink': file_path,
            'level': file.level.value,
            'format': self._build_file_format([i.value for i, _, _ in file.format.value], file.time_format.value),
            'rotation': size,
            'retention': file.retention,
            'compression': 'zip' if file.compression else None,
            'mode': file.mode.value,
            'encoding': file.encoding,
            'backtrace': True,
            'diagnose': True,
        }

        logger.add(**{k: v for k, v in kwargs.items() if v is not None})

    def _build_file_format(self, format_list: List[str], date_format: str) -> str:
        if all(item in format_list for item in ['module', 'function', 'line']):
            format_list = [item for item in format_list if item not in ['module', 'function', 'line']]
            format_list.insert(format_list.index('message'), 'module}:{function}:{line')

        return ' | '.join(
            f'{{{item}}}' if item != Attribute.time.value else f'{{time:{date_format}}}'
            for item in format_list
        )

    def _add_database(self, model: str, level: LogLevel):
        def get_notice_model(model_name: str):
            models = self.engine.models
            for model in models:
                if model.__name__ == model_name:
                    return model
            raise ValueError(f'找不到预警模型: {model_name}')

        def database_sink(message, model_name):
            kw = dict(zip(
                ['notice_time', 'message', 'level', 'spider_name', 'task_id', 'exception_stack'],
                message.split('$$')
            ))
            if kw['task_id'] == '-':
                kw['task_id'] = '-' * 36

            data = NoticeMessage(**kw).get_notice_data()

            model = get_notice_model(model_name)
            if data.get('level') in ['LEVEL1', 'LEVEL2', 'LEVEL3']:
                data['type'] = NoticeType.notice
            else:
                data['type'] = NoticeType.warning
            model.create(source='AioSpider', **data)

        context_sink = partial(database_sink, model_name=model)
        logger.add(context_sink, level=level.value, format=self._build_database_format)

    def _build_database_format(self, record: Dict[str, Any]):
        return '$$'.join([
            record['time'].strftime('%Y-%m-%d %H:%M:%S'),
            record['message'],
            record['level'].name,
            self.engine.spider.name,
            (self.engine.task_model and self.engine.task_model.task_id) or '-',
            record.get('exception') or '-',
        ])

    def _level(self, level: LogLevel, msg: str, *args, **kwargs):
        logger.opt(depth=1).log(level.name, msg, *args, **kwargs)
