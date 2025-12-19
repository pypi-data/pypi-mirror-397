import asyncio
import itertools
import random
import time
from datetime import datetime
from pprint import pformat
from functools import partial
from pathlib import Path

from AioSpider import logger
from AioSpider.objects import (
    SleepStrategy,
    MiddlewareType,
    EventType,
    BackendEngine,
    RequestStatus,
    TaskStatus,
    EnvType,
    TableType
)
from AioSpider.exceptions import *
from AioSpider.http import Response, HttpRequest
from AioSpider.loading import BootLoader
from AioSpider.orm import Model
from AioSpider.db import RedisLock
from AioSpider.core import signals
from AioSpider.tools import get_ipv4

from .patch import apply
from .event import EventEngine
from .concurrency_strategy import get_task_limit

apply()


class EngineBuilder:

    def __init__(self, engine, spider):
        self.bootloader = BootLoader()
        self.engine = engine
        self.spider = spider

    async def build(self):
        self._load_settings()
        self._load_logger()
        self._load_welcome()
        await self._load_model()
        await self._load_request_pool()
        await self._load_browser()
        await self._load_middleware_manager()
        await self._load_downloader()
        await self._load_datamanage()

    def _load_settings(self):
        self.engine.settings = self.bootloader.reload_settings(self.spider)

    def _load_logger(self):
        self.bootloader.reload_logger(self.engine)

    def _load_welcome(self):
        welcome_message = """
\033[38;5;51m╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                                                 ║
║       \033[38;5;208m█████╗ ██╗ ██████╗ ███████╗██████╗ ██╗██████╗ ███████╗██████╗      ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗██╗\033[38;5;51m      ║
║      \033[38;5;208m██╔══██╗██║██╔═══██╗██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗     ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝██║\033[38;5;51m      ║
║      \033[38;5;208m███████║██║██║   ██║███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝     ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗  ██║\033[38;5;51m      ║
║      \033[38;5;208m██╔══██║██║██║   ██║╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗     ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝  ╚═╝\033[38;5;51m      ║
║      \033[38;5;208m██║  ██║██║╚██████╔╝███████║██║     ██║██████╔╝██████╗██║  ██║     ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗██╗\033[38;5;51m      ║
║      \033[38;5;208m╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝      ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝\033[38;5;51m      ║
║                                                                                                                                                 ║
╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝\033[0m
        """
        print(welcome_message)
        logger.level3(msg=f'{">" * 25} {self.spider.name}: 开始采集 {"<" * 25}')

    async def _load_model(self):
        self.engine.models = await self.bootloader.reload_models(self.spider, self.engine.settings).initialize()
        logger.level3(msg=f'数据管理器已启动，加载到 {len(self.engine.models)} 个模型，\n{pformat(self.engine.models)}')

    async def _load_request_pool(self):
        from AioSpider.requestpool import RequestPoolManager
        self.engine.request_pool = await RequestPoolManager(
            self.engine.event_engine, self.spider, self.engine.settings, None, self.engine.backend
        )
        self.engine.request_pool.start()

    async def _load_browser(self):
        self.engine.browser = self.bootloader.reload_browser(self.engine.event_engine, self.engine.settings)

    async def _load_middleware_manager(self):
        self.engine.middleware_manager = self.bootloader.reload_middleware_manager(
            self.engine.event_engine, self.spider, self.engine.settings, self.engine.browser
        )

    async def _load_downloader(self):
        from AioSpider.downloader import Downloader
        self.engine.downloader = Downloader(
            self.engine.event_engine,
            request_settings=self.engine.settings.SpiderRequestConfig,
            connection_pool_settings=self.engine.settings.ConnectPoolConfig,
            middleware=self.engine.middleware_manager.download_middlewares
        )

    async def _load_datamanage(self):
        from AioSpider.datamanager import DataManager

        data_manager = await DataManager(self.engine.settings, self.engine.spider, self.engine.models)
        self.engine.datamanager = data_manager
        self.engine.respomse_producer = RespomseProducer(self.spider, self.engine.request_pool, data_manager)


class RespomseProducer:

    def __init__(self, spider, request_pool, datamanager):
        self.spider = spider
        self.request_pool = request_pool
        self.datamanager = datamanager

    async def process_response(self, response, request):
        """处理响应"""
        callback = self._get_callback(request.callback)

        if not callable(callback):
            raise TypeError('回调必须是可调用类型')

        if asyncio.iscoroutinefunction(callback):
            result = await callback(response)
        else:
            result = callback(response)

        await self._process_callback(result)

    def _get_callback(self, callback):
        """获取回调函数"""
        if isinstance(callback, str):
            callback = getattr(self.spider, callback, None)
            return partial(callback, self.spider) if callable(callback) else None
        return callback or self.spider.parse

    async def _process_callback(self, result):
        """处理响应回调结果"""
        if result is None or isinstance(result, Path):
            return

        if isinstance(result, Model):
            result.source = result.source or self.spider.source
            await self._process_callback(await self.datamanager.commit(result))
        elif isinstance(result, HttpRequest):
            await self.request_pool.put(result)
        elif hasattr(result, '__iter__'):
            for item in result:
                await self._process_callback(item)
        else:
            raise ValueError('回调必须返回Model对象或HttpRequest对象')


class BaseEngine:

    def __init__(self, spider):
        self.spider = spider
        self.event_engine = EventEngine()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # 设置异常处理器，抑制程序退出时的 SSL 清理警告
        # 这些错误不影响爬虫功能，只是事件循环关闭时的清理提示
        def exception_handler(loop, context):
            exception = context.get('exception')
            message = context.get('message', '')

            # 忽略 SSL/Socket 传输清理错误
            if isinstance(exception, (OSError, RuntimeError)):
                if 'SSL' in message or 'socket' in message.lower() or 'transport' in message.lower():
                    return

            # 其他异常正常记录
            loop.default_exception_handler(context)

        self.loop.set_exception_handler(exception_handler)

        self.start_time = datetime.now()
        self.end_time = None

        self.status = TaskStatus.before
        self.settings = None
        self.models = None
        self.request_pool = None
        self.middleware_manager = None
        self.downloader = None
        self.connections = None
        self.datamanager = None
        self.respomse_producer = None
        self.browser = None
        self.slot = None
        self.crawling_time = 0
        self._per_request_sleep = None
        self._per_task_sleep = None
        self.avg_speed = 0
        self.task_limit = 1
        self.waiting_count = 0
        self.spider_model = None
        self.task_model = None

    def start(self):
        """启动引擎"""
        self.loading_signals()
        while True:
            if not signals.loop_start(self.spider):
                break
            try:
                self.loop.run_until_complete(self.execute())
            except KeyboardInterrupt:
                self.status = TaskStatus.canceled
                self.handle_exit('手动退出')
            except ValueError as e:
                self.status = TaskStatus.error
                self.handle_exit(str(e))
            except ORMException as e:
                self.status = TaskStatus.error
                self.handle_exit(f"ORM 错误: {str(e)}")
            except AioException as e:
                self.status = TaskStatus.error
                self.handle_exit(f"AioSpider 错误: {str(e)}")
            except Exception as e:
                raise e
                self.status = TaskStatus.error
                self.handle_exit(f"未知错误: {str(e)}")
            finally:
                if not self.loop.is_closed():
                    self.loop.run_until_complete(self.loop.shutdown_asyncgens())
                    self.loop.close()
            if signals.loop_stop(self.spider):
                break

    def handle_exit(self, reason):
        if not self.loop.is_closed():
            self.loop.run_until_complete(self.close())
        logger.level5(msg=reason)

    def loading_signals(self):
        try:
            s = __import__('signals')
        except:
            s = None

        func = [i for i in dir(signals) if callable(getattr(signals, i))]

        for i in func:
            if not hasattr(s, i):
                continue
            setattr(signals, i, getattr(s, i))

        # debug = Path.home() / 'aioDev/.account'
        # if not debug.exists() or debug.read_text() != '21232f297a57a5a743894a0e4a801fc3':
        #     exit(-100)

        self.event_engine.register(EventType.LOAD_CONFIG_START, signals.loading_start)
        self.event_engine.register(EventType.LOAD_CONFIG_STOP, signals.loading_stop)

        return signals

    async def execute(self):
        self.event_engine.start()
        await self.event_engine.put_event(EventType.LOAD_CONFIG_START, self.spider)
        await EngineBuilder(self, self.spider).build()
        await self.event_engine.put_event(EventType.LOAD_CONFIG_STOP, self.spider)
        await self.spider_open()
        self.event_engine.register_timer(1, self.fresh)

    async def spider_open(self):
        self.create_spider_record()
        self.create_task_record()
        self.spider.spider_open()
        await self.event_engine.put_event(EventType.SPIDER_OPEN, self.spider)

    @property
    def task_sleep(self):
        if self._per_task_sleep is None:
            sleep_config = self.settings.SpiderRequestConfig.REQUEST_CONCURRENCY_SLEEP
            if sleep_config['strategy'] == SleepStrategy.fixed:
                self._per_task_sleep = sleep_config['sleep']
            elif sleep_config['strategy'] == SleepStrategy.random:
                self._per_task_sleep = random.randint(
                    min(sleep_config['sleep']) * 100, max(sleep_config['sleep']) * 100
                ) / 100
            else:
                self._per_task_sleep = 1
        return self._per_task_sleep

    @property
    def request_sleep(self):
        if self._per_request_sleep is None:
            sleep_config = self.settings.SpiderRequestConfig.PER_REQUEST_SLEEP
            if sleep_config['strategy'] == SleepStrategy.fixed:
                self._per_request_sleep = sleep_config['sleep']
            elif sleep_config['strategy'] == SleepStrategy.random:
                self._per_request_sleep = random.randint(
                    min(sleep_config['sleep']) * 100, max(sleep_config['sleep']) * 100
                ) / 100
            else:
                self._per_request_sleep = 1
        return self._per_request_sleep

    async def apply_task_sleep(self):
        await asyncio.sleep(self.task_sleep)

    async def apply_request_sleep(self):
        await asyncio.sleep(self.request_sleep)

    async def download(self, request):
        """从调度器中取出的请求交给下载器中处理"""

        async def process_middleware_response(self, response):

            if response is None:
                await self.request_pool.put(request)
                return None

            if isinstance(response, Response):
                await self.request_pool.put(response.request)
                return response

            if isinstance(response, HttpRequest):
                response.status = RequestStatus.before
                await self.request_pool.put(response)
                return None

            return None

        try:
            response = await self.downloader.fetch(request)

            if isinstance(response, Response):
                response = await self.middleware_manager.process_response(response, type=MiddlewareType.download)
                return await process_middleware_response(self, response)

            if isinstance(response, Exception):
                response = await self.middleware_manager.process_exception(request, response, type=MiddlewareType.download)
                return await process_middleware_response(self, response)

            raise TypeError('Response 类型错误')

        except Exception as e:
            logger.level5(msg=f"下载请求失败: {request.url}, 错误: {str(e)}")
            await self.request_pool.put(request)
            return None

    async def process_waiting_requests(self):
        """处理waiting队列中取出的请求"""
        tasks = []
        async for request in self.request_pool.get(self.task_limit):
            obj = await self.middleware_manager.process_request(request, type=MiddlewareType.spider)
            if isinstance(obj, HttpRequest):
                tasks.append(asyncio.create_task(self.download(request)))
                await self.request_pool.pending.delete_request(obj)
            elif isinstance(obj, Response):
                await self.respomse_producer.process_response(obj, request)
            else:
                continue
            await self.apply_request_sleep()
            if len(tasks) >= self.task_limit:
                break
        return tasks

    async def process_tasks(self, tasks):
        """处理响应"""
        if not tasks:
            return
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for response in responses:
            if response is None:
                continue
            if isinstance(response, Exception):
                logger.level5(msg=f"任务执行异常: {str(response)}")
                continue
            await self.respomse_producer.process_response(response, response.request)

    async def fresh(self):
        """更新爬虫进度信息"""
        stats = await self.get_stats()
        if stats['completed_count'] == 0:
            self.log_initial_status(stats)
        else:
            self.log_progress(stats)

    async def get_stats(self):
        if self.request_pool is None:
            return {
                'completed_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'failure_queue_count': 0,
                'waiting_count': 0,
                'running_time': round(time.time() - self.crawling_time, 3),
            }
        completed_count = await self.request_pool.done_size()
        return {
            'completed_count': completed_count,
            'success_count': self.request_pool.success_size(),
            'failure_count': await self.request_pool.failure_size(),
            'failure_queue_count': self.request_pool.failure.get_queue_size(),
            'waiting_count': await self.request_pool.waiting_size(),
            'running_time': round(time.time() - self.crawling_time, 3),
        }

    def log_initial_status(self, stats):
        logger.level3(
            msg=f"爬虫进度更新:\n"
                f"{'=' * 50}\n"
                f"\t\t程序运行时间: {self.format_running_time(stats['running_time'])}\n"
                f"\t\t已完成请求数: {stats['completed_count']}\n"
                f"\t\t等待请求数: {stats['waiting_count']}\n"
                f"\t\t重试队列数: {stats['failure_queue_count']}\n"
                f"\t\t即将开始爬取\n"
                f"{'=' * 50}"
        )
        self.create_task_progress_record(running_time=stats['running_time'])

    def log_progress(self, stats):
        avg_speed = round(stats['completed_count'] / stats['running_time'], 3) if stats['running_time'] else 0
        remaining_time = round(stats['waiting_count'] / avg_speed, 3) if avg_speed else 0
        logger.level2(
            msg=f"爬虫进度更新:\n"
                f"{'=' * 50}\n"
                f"\t\t完成进度: {stats['completed_count']} / {stats['completed_count'] + stats['waiting_count']}\n"
                f"\t\t程序运行时间: {self.format_running_time(stats['running_time'])}\n"
                f"\t\t已完成请求数: {stats['completed_count']} (成功: {stats['success_count']} | 最终失败: {stats['failure_count']})\n"
                f"\t\t等待请求数: {stats['waiting_count']}\n"
                f"\t\t重试队列数: {stats['failure_queue_count']}\n"
                f"\t\t当前并发速度: {avg_speed:.2f} 请求/秒\n"
                f"\t\t预计剩余时间: {self.format_remaining_time(remaining_time)}\n"
                f"\t\t并发策略: {self.get_concurrency_type()}\n"
                f"{'=' * 50}"
        )
        self.create_task_progress_record(
            progress=stats['completed_count'] / (stats['completed_count'] + stats['waiting_count']),
            running_time=stats['running_time'],
            completed_count=stats['completed_count'],
            success_count=stats['success_count'],
            failure_count=stats['failure_count'],
            waiting_count=stats['waiting_count'],
            avg_speed=avg_speed,
            remaining_time=remaining_time,
        )

    def format_running_time(self, running):
        return self.format_time(running)

    def format_remaining_time(self, remaining):
        return self.format_time(remaining)

    def format_time(self, seconds):
        hour, remainder = divmod(seconds, 3600)
        minute, second = divmod(remainder, 60)
        return f"{int(hour)}时{int(minute)}分{int(second)}秒".strip()

    def get_concurrency_type(self):
        config = self.settings.ConcurrencyStrategyConfig
        strategies = {
            'auto': '自动并发模式',
            'fix': '固定并发模式',
            'random': '随机并发模式',
            'speed': '速度并发模式',
            'time': '时间并发模式'
        }
        for strategy, description in strategies.items():
            if getattr(config, strategy)['enabled']:
                return description
        raise ValueError("未找到有效的并发策略")

    async def close(self):
        stats = await self.get_stats()
        total_time = self.end_time or datetime.now() - self.start_time
        speed = round(stats['completed_count'] / stats['running_time'], 3) if stats['running_time'] else 0
        success_rate = stats['success_count'] / stats['completed_count'] * 100 if stats['completed_count'] else 0

        logger.level2(msg='开始记录数据统计信息')
        if self.task_model:
            self._create_table_field_record()
            self._create_table_statistics_record()
        logger.level2(msg='数据统计信息记录完成')
        logger.level3(
            msg=f"爬虫 {self.spider.name} 运行结束\n"
                + "=" * int((108 - len(self.spider.name) * 2) / 2) + f" 爬虫 {self.spider.name} 运行结束 " + "=" * int(
                (108 - len(self.spider.name) * 2) / 2) + "\n"
                                                         f"\t\t爬虫名称: {self.spider.name}\n"
                                                         f"\t\t爬虫站点: {self.spider.source}\n"
                                                         f"\t\t爬取页面: {self.spider.target}\n"
                                                         f"\t\t请求成功率(总数量/成功/失败): {success_rate:.2f}% ( {stats['completed_count']}/{stats['success_count']}/{stats['failure_count']} )\n"
                                                         f"\t\t采集时间: {self.format_running_time(stats['running_time'])} \n"
                                                         f"\t\t平均速度: {speed:.2f} 请求/秒\n"
                                                         f"\t\t总用时: {total_time}\n"
                + "=" * 120
        )

        await self.event_engine.put_event(EventType.BROWSER_QUIT)
        await self.event_engine.put_event(EventType.REQUEST_CLOSE)
        await self.event_engine.put_event(EventType.SESSION_CLOSE)
        await self.event_engine.put_event(EventType.DATABASE_CLOSE)
        await asyncio.sleep(0.1)

        await self.event_engine.stop()

        self.update_task_record(
            crawl_end=self.end_time or datetime.now(),
            status=self.status,
            crawl_count=self.datamanager and self.datamanager.commit_count or 0,
            save_count=self.datamanager and self.datamanager.get_total_effected_count() or 0,
            success_request_count=stats['success_count'],
            failure_request_count=stats['failure_count']
        )

        from AioSpider.orm import close_database
        close_database()

        logger.level3(msg=f"{'>' * 25} {self.spider.name} 爬虫任务结束 {'<' * 25}")
        logger.level3(msg=f"{'>' * 25} 感谢使用 AioSpider 爬虫框架 {'<' * 25}")

    async def spider_close(self):
        self.spider.spider_close()
        for model in self.models:
            if model.Meta.table_type != TableType.data:
                continue
            model.spider_close(model, self.spider)
        await self.event_engine.put_event(EventType.SPIDER_CLOSE, self.spider)

    def get_spider_model(self):
        return [i for i in self.models if i.Meta.table_type == TableType.spider][0]

    def create_spider_record(self):
        model = self.get_spider_model()
        if self.spider.target is None:
            target = None
        elif isinstance(self.spider.target, str):
            target = self.spider.target
        else:
            target = ','.join(self.spider.target)
            
        self.spider_model = model.objects.create_or_update(
            name=self.spider.name,
            spider_type=self.spider.spider_type,
            host=get_ipv4(),
            root=Path.cwd(),
            site=self.spider.source,
            target=target,
            description=self.spider.description,
            develop_status=self.spider.develop_status,
            frequency=self.spider.frequency,
            version=self.spider.version,
            author=self.spider.author,
            maintainer=self.spider.maintainer or self.spider.author,
            email=self.spider.email,
            priority=self.spider.priority,
            is_active=self.spider.is_active,
            tags=self.spider.tags,
            source='AioSpider 框架'
        )

    def get_task_model(self):
        return [i for i in self.models if i.Meta.table_type == TableType.task][0]

    def create_task_record(self):
        model = self.get_task_model()
        self.task_model = model.objects.create_or_update(
            spider=self.spider.name,
            env=EnvType.debug if self.settings.DEBUG else EnvType.production,
            source='AioSpider 框架'
        )

    def update_task_record(self, **kwargs):
        self.task_model and self.task_model.update(**kwargs)

    def get_task_progress_model(self):
        return [i for i in self.models if i.Meta.table_type == TableType.task_progress][0]

    def create_task_progress_record(self, **kwargs):
        model = self.get_task_progress_model()
        model.objects.create_or_update(
            task_id=self.task_model.task_id,
            datetime=datetime.now(),
            **kwargs
        )

    def get_table_field_model(self):
        from AioSpider.orm import TableFieldStatisticsModel
        return [i for i in self.models if issubclass(i, TableFieldStatisticsModel)][0]

    def _create_table_field_record(self):
        from AioSpider.tools import get_relative_date
        from AioSpider.orm.fields import DecimalField, IntField

        table_field_model = self.get_table_field_model()
        for model in self.models:
            if not model.Meta.statistics:
                continue
            if model.Meta.table_type != TableType.data:
                continue
            for field in model.fields.values():
                if field.column not in (model.Meta.statistics_fields or tuple()):
                    continue
                statistics_filter = model.Meta.statistics_filter or {}
                flag = isinstance(field, DecimalField) or isinstance(field, IntField)
                max_value = model.filter(**statistics_filter).max(field.column) if flag else None
                min_value = model.filter(**statistics_filter).min(field.column) if flag else None
                avg_value = model.filter(**statistics_filter).avg(field.column) if flag else None
                sum_value = model.filter(**statistics_filter).sum(field.column) if flag else None
                std_value = model.filter(**statistics_filter).std(field.column) if flag else None
                variance_value = model.filter(**statistics_filter).variance(field.column) if flag else None
                null_rate = model.filter(**statistics_filter).get_null_rate(field.column) if flag else None
                unique_rate = model.filter(**statistics_filter).get_unique_rate(field.column) if flag else None
                table_field_model.objects.create_or_update(
                    task_id=self.task_model.task_id,
                    date=get_relative_date(as_date=True),
                    table_name=model.table_name,
                    schema_name=model.database,
                    field_name=field.column,
                    field_type=field.__class__.__name__,
                    null_count=model.get_null_rows(field.column),
                    unique_count=model.filter(**statistics_filter).get_distinct_values(field.column),
                    zero_count=model.filter(**statistics_filter).get_zero_count(field.column),
                    max_value=max_value,
                    min_value=min_value,
                    avg_value=avg_value,
                    sum_value=sum_value,
                    std_value=std_value,
                    variance_value=variance_value,
                    null_rate=null_rate,
                    unique_rate=unique_rate,
                    max_length=model.get_max_length(field.column),
                    min_length=model.filter(**statistics_filter).get_min_length(field.column),
                    avg_length=model.filter(**statistics_filter).get_avg_length(field.column),
                )

    def get_table_statistics_model(self):
        from AioSpider.orm import TableStatisticsModel
        return [i for i in self.models if issubclass(i, TableStatisticsModel)][0]
    
    def _create_table_statistics_record(self):
        from AioSpider.tools import get_relative_date

        from AioSpider.objects import DataBaseType

        table_model = self.get_table_statistics_model()
        for model in self.models:
            if model.Meta.table_type != TableType.data:
                continue
            # 跳过 file 和 csv 类型，它们不支持统计操作
            if model.Meta.database_type in [DataBaseType.file, DataBaseType.csv]:
                continue
            fields = [i.column for i in model.fields.values()]
            add_count = model.filter(create_time__gt=get_relative_date(as_date=True)).count() if 'create_time' in fields else 0
            update_count = model.filter(update_time__gt=get_relative_date(as_date=True)).count() if 'update_time' in fields else 0
            table_model.objects.create_or_update(
                task_id=self.task_model.task_id,
                date=get_relative_date(as_date=True),
                table_name=model.table_name,
                schema_name=model.database,
                add_count=add_count,
                total_count=model.objects.count(),
                update_count=update_count,
                source='AioSpider 框架'
            )


class Engine(BaseEngine):
    backend = BackendEngine.queue

    async def execute(self):
        await super().execute()
        self.start_requests_iterator = self.spider.start_requests()

        # 如果start_requests_iterator已用完，则添加要跟踪的变量
        iterator_stop = False
        self.crawling_time = time.time()
        concurrency_type = self.get_concurrency_type()

        self.status = TaskStatus.running
        self.update_task_record(crawl_start=self.crawling_time, status=self.status)

        # 连续循环，从调度程序队列中获取请求
        while True:
            self.task_limit = self.get_task_limit()
            logger.level2(msg=f'并发类型：{concurrency_type}，当前并发数：{self.task_limit}')

            if self.task_limit <= 0:
                raise ValueError('Task limit 必须大于0')

            if not iterator_stop:
                iterator_stop = await self.add_request_to_buffer()

            # 处理waiting队列中的请求
            tasks = await self.process_waiting_requests()
            await self.process_tasks(tasks)

            # 暂停以遵循请求速率限制，更新进度条
            await self.apply_task_sleep()

            # 如果没有请求需要处理，则中断循环
            if iterator_stop and await self.request_pool.is_empty():
                break

        self.status = TaskStatus.success
        self.end_time = datetime.now()
        await self.cleanup()

    def get_task_limit(self):
        return get_task_limit(
            config=self.settings.ConcurrencyStrategyConfig,
            crawling_time=self.crawling_time,
            current_speed=self.avg_speed,
            task_limit=self.task_limit,
            waiting_count=self.waiting_count
        )

    async def add_request_to_buffer(self):
        count = self.task_limit * random.randint(2, 10)
        new_requests = list(itertools.islice(self.start_requests_iterator, count))

        if new_requests:
            [await self.request_pool.put(req) for req in new_requests]
            return len(new_requests) < count

        return True

    async def cleanup(self):
        await self.datamanager.close()
        await self.spider_close()
        await self.close()


class DistributeEngine(BaseEngine):
    backend = BackendEngine.redis

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = 0
        self.redis_spider_key = f'{self.spider.name}:info'
        self.redis_lock_key = 'lock'
        self.redis_stop_key = 'stop'
        self.redis_count_key = 'count'

    async def execute(self):
        await super().execute()
        self.check_redis_configuration()
        self.start_requests_iterator = self.spider.start_requests()
        iterator_stop = False
        self.crawling_time = time.time()
        concurrency_type = self.get_concurrency_type()

        while True:
            self.task_limit = self.get_task_limit()
            logger.level2(msg=f'并发类型：{concurrency_type}，当前并发数：{self.task_limit}')

            if self.task_limit <= 0:
                raise ValueError('Task limit 必须大于0')

            if not iterator_stop:
                iterator_stop = await self.add_request_to_buffer()

            tasks = await self.process_waiting_requests()
            await self.process_tasks(tasks)
            await self.apply_task_sleep()

            if iterator_stop and await self.request_pool.is_empty():
                break

        await self.cleanup()

    def check_redis_configuration(self):
        if 'redis' not in self.connections or 'DEFAULT' not in self.connections['redis']:
            raise SpiderExeption(f"分布式爬虫 {self.spider.name} 未配置redis数据库")

    async def spider_close(self):
        await super().spider_close()
        conn = self.connections['redis']['DEFAULT']
        await conn.delete(self.redis_spider_key)

    async def add_request_to_buffer(self):
        conn = self.connections['redis']['DEFAULT']

        if await conn.hash.hget(self.redis_spider_key, self.redis_stop_key) == '1':
            return True

        async with RedisLock(
                spider_key=self.redis_spider_key, lock_key=self.redis_lock_key, conn=conn,
                wait_timeout=self.spider.wait_timeout
        ) as lock:
            if not lock.locked:
                return False

            count = self.task_limit * random.randint(2, 10)
            redis_count = int(await conn.hash.hget(self.redis_spider_key, self.redis_count_key) or 0)

            if redis_count > self.offset:
                list(itertools.islice(self.start_requests_iterator, redis_count - self.offset))
                self.offset = redis_count

            new_requests = list(itertools.islice(self.start_requests_iterator, count))
            if new_requests:
                await asyncio.gather(*[self.request_pool.put(req) for req in new_requests])
                self.offset += len(new_requests)
                await conn.hash.hset(self.redis_spider_key, self.redis_count_key, str(self.offset))
                return await self.set_stop_flag() if len(new_requests) < count else False

        return await self.set_stop_flag()

    async def set_stop_flag(self):
        conn = self.connections['redis']['DEFAULT']
        await conn.hash.hset(self.redis_spider_key, self.redis_stop_key, '1')
        return True
