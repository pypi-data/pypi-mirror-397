import time
import asyncio

from AioSpider import logger


class RedisLock:

    def __init__(self, spider_key, lock_key, conn, wait_timeout: int = 0, lock_timeout: int = 12 * 60 * 60):
        """
        redis超时锁
        Args:
            key: 存储锁的key
            redis_cli: redis连接对象
            wait_timeout: 等待加锁超时时间，为0时则不等待加锁，加锁失败
            lock_timeout: 加锁超时时间
        用法示例:
        with RedisLock(key="test") as _lock:
            if _lock.locked:
                # 用来判断是否加上了锁
                # do somethings
        """
        self.conn = conn
        self.redis_spider_key = spider_key
        self.lock_key = lock_key
        self.wait_timeout = wait_timeout
        self.lock_timeout = lock_timeout
        self.locked = False

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()

    async def acquire(self):

        start = time.time()
        while True:
            try:
                # 尝试加锁
                if await self.conn.hash.hset(self.redis_spider_key, self.lock_key, int(time.time())):
                    self.locked = True
                    break
                
                # 判断是否超时
                if self.wait_timeout > 0 and (time.time() - start) > self.wait_timeout:
                    logger.level3(msg="加锁等待超时...")
                    break

                stamp = await self.conn.hash.hget(self.redis_spider_key, self.lock_key)
                stamp = int(stamp) if stamp is not None else 0

                if stamp + self.lock_timeout < time.time():
                    logger.level3(msg="锁时间已超时...")
                    break

                logger.level2(msg=f"等待加锁 wait: {round(time.time() - start, 2)}s")
                await asyncio.sleep(5 if self.wait_timeout >= 10 else 1)

            except Exception as e:
                logger.level5(msg=f"Error in acquiring lock: {e}")
                break

    async def release(self):
        if self.locked:
            await self.conn.hash.hdel(self.redis_spider_key, self.lock_key)
            self.locked = False
