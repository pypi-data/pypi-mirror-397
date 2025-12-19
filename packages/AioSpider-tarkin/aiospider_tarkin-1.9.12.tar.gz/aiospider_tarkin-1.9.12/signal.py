import asyncio
import inspect
from collections import defaultdict

from AioSpider.tools.tools import singleton


@singleton
class Signal:

    signals = defaultdict(list)

    def connect(self, signal, handler=None, *args, **kwargs):
        if handler is not None:
            self.signals[signal].append((handler, args, kwargs))
    
    async def emit(self, signal, **kwargs):
        for handler, args, kw in self.signals[signal]:
            await handler(*args, **kw, **kwargs) if inspect.iscoroutinefunction(handler) else handler(*args, **kw, **kwargs)

    def disconnect_signal(self, signal):
        """断开信号与槽的连接"""
        self.signals.pop(signal, None)
