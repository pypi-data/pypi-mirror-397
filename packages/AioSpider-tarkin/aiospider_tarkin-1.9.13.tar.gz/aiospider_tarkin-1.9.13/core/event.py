import asyncio
import time
from collections import defaultdict
from typing import Callable, Dict, List, Union

from AioSpider.objects import Priority, EventType

class Event:

    def __init__(self, type: EventType, *args):
        self.type = type
        self.args = args

    def __str__(self):
        return f"Event<type={self.type}, args={self.args}>"

    __repr__ = __str__


class Handler:

    def __init__(self, func: Callable, priority: Priority = Priority.NORMAL):
        self.func = func
        self.priority = priority

    async def call(self, event: Event):
        if asyncio.iscoroutinefunction(self.func):
            await self.func(*event.args)
        else:
            self.func(*event.args)
    
    def __str__(self):
        return f"Handler<func={self.func}, priority={self.priority}>"

    __repr__ = __str__


class EventEngine:

    def __init__(self):
        self._handlers: Dict[EventType, List[Handler]] = defaultdict(list)
        self._general_handlers: List[Handler] = []
        self._event_queue = asyncio.Queue()
        self._active = False
        self._timer_tasks = []
        self.task = None

    def start(self):
        """启动事件引擎"""
        self._active = True
        self.task = asyncio.create_task(self._run())

    async def stop(self):
        """停止事件引擎"""
        self._active = False
        for task in self._timer_tasks:
            task.cancel()
        if self.task:
            self.task.cancel()
        while not self._event_queue.empty():
            event = await self._event_queue.get()
            await self._process(event)
        print("事件引擎已停止，所有待处理事件已完成")

    async def _run(self):
        """引擎运行主循环"""
        while self._active:
            try:
                print("正在等待获取事件...")
                event = await self._event_queue.get()
                await self._process(event)
                await asyncio.sleep(0.001)
            except Exception as e:
                print(f"事件处理失败，错误信息：{e}")

    async def _process(self, event: Event):
        """处理事件"""
        handlers = self._handlers[event.type]
        for handler in self._general_handlers + handlers:
            try:
                await handler.call(event)
            except Exception as e:
                print(f"事件处理器执行失败，事件：{event}，处理器：{handler}，错误信息：{e}")

    def register(self, type: EventType, handler: Callable, priority: Priority = Priority.NORMAL):
        """注册特定类型的事件处理器"""
        self._handlers[type].append(Handler(handler, priority))
        self._handlers[type].sort(key=lambda h: h.priority.value, reverse=True)

    def unregister(self, type: EventType, handler: Callable):
        """注销特定类型的事件处理器"""
        self._handlers[type] = [h for h in self._handlers[type] if h.func != handler]

    def register_general(self, handler: Callable, priority: Priority = Priority.NORMAL):
        """注册通用事件处理器"""
        self._general_handlers.append(Handler(handler, priority))
        self._general_handlers.sort(key=lambda h: h.priority.value, reverse=True)

    def unregister_general(self, handler: Callable):
        """注销通用事件处理器"""
        self._general_handlers = [h for h in self._general_handlers if h.func != handler]

    async def put_event(self, event: Union[Event, EventType], *args):
        """发送事件"""
        if isinstance(event, EventType):
            event = Event(event, *args)
        await self._event_queue.put(event)

    def register_timer(self, interval: float, handler: Callable, *args):
        """注册定时事件"""
        async def timer_task():
            while self._active:
                await asyncio.sleep(interval)
                await self.put_event(EventType.TIMER, *args)
                await handler(*args)
        
        task = asyncio.create_task(timer_task())
        self._timer_tasks.append(task)
        return task
