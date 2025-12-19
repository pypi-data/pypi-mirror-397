import json
from abc import ABCMeta, abstractmethod
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Union, Any, Callable, Type, List as _List, Dict

import pandas as pd
from redis import Redis
from AioSpider import logger


def escape_strings(value):
    """转移数据类型"""

    if isinstance(value, (Path, datetime, date)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ','.join(escape_strings(item) for item in value)
    if isinstance(value, dict):
        return {k: escape_strings(v) for k, v in value.items()}
    if isinstance(value, bool):
        return int(value)
    return value


class RedisDataType(metaclass=ABCMeta):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_isinstance'):
            cls._isinstance = super().__new__(cls)
        return cls._isinstance

    def __init__(self, pool):
        self._pool: Redis = pool

    @classmethod
    def from_redis(cls, pool):
        self = cls(pool)
        return self


class String(RedisDataType):

    def setnx(self, name, value):
        """设置值，只有name不存在时，执行设置操作"""
        return self._pool.setnx(name, value)

    def setex(self, name, time, value):
        """设置键值对和过期时间"""
        return self._pool.setex(name, time, value)

    def psetex(self, name, time_ms, value):
        """设置键值对和毫秒过期时间"""
        return self._pool.psetex(name, time_ms, value)

    def mget(self, keys, *args):
        """批量获取"""
        return self._pool.mget(keys, *args)

    def getset(self, name, value):
        """设置新值并获取原来的值"""
        return self._pool.getset(name, value)

    def getrange(self, name, start, end):
        """
        获取子序列（根据字节获取，非字符）
        Args:
            name: 键
            start: 起始位置（字节）
            end: 结束位置（字节）
        """
        return self._pool.getrange(name, start, end)

    def setrange(self, name, offset, value):
        """修改字符串内容，从指定字符串索引开始向后替换（新值太长时，则向后添加）"""
        return self._pool.setrange(name, offset, value)

    def setbit(self, name, offset, value):
        """对 name 对应值的二进制表示的位进行操作"""
        return self._pool.setbit(name, offset, value)

    def getbit(self, name, offset):
        """获取name对应的值的二进制表示中的某位的值 （0或1）"""
        return self._pool.getbit(name, offset)

    def bitcount(self, key, start=None, end=None):
        """获取name对应的值的二进制表示中 1 的个数"""
        return self._pool.bitcount(key, start=start, end=end)

    def bitop(self, operation, dest, *keys):
        """获取多个值，并将值做位运算，将最后的结果保存至新的name对应的值"""
        return self._pool.bitop(operation, dest, *keys)

    def strlen(self, name):
        """返回name对应值的字节长度（一个汉字3个字节）"""
        return self._pool.strlen(name)

    def incr(self, name, amount=1):
        """自增 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自增"""
        return self._pool.incr(name, amount=amount)

    def incrbyfloat(self, name, amount=1.0):
        """自增 name对应的值，当name不存在时，则创建name＝amount，否则，则自增"""
        return self._pool.incrbyfloat(name, amount=amount)

    def decr(self, name, amount=1):
        """自减 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自减"""
        return self._pool.decr(name, amount=amount)

    def append(self, key, value):
        """在redis name对应的值后面追加内容"""
        return self._pool.append(key, value)


class Set(RedisDataType):

    def sadd(self, name, *values):
        """添加元素"""
        return self._pool.sadd(name, *values)

    def scard(self, name):
        """获取元素个数"""
        return self._pool.scard(name)

    def smembers(self, name):
        """获取集合中所有的成员"""
        return self._pool.smembers(name)

    def sscan(self, name, cursor=0, match=None, count=None):
        """获取集合中所有的成员--元组形式"""
        return self._pool.sscan(name, cursor=cursor, match=match, count=count)

    def sscan_iter(self, name, match=None, count=None):
        """获取集合中所有的成员--迭代器的方式"""
        return self._pool.sscan_iter(name, match=match, count=count)

    def sdiff(self, keys, *args):
        """差集"""
        return self._pool.sdiff(keys, *args)

    def sdiffstore(self, dest, keys, *args):
        """获取keys对应集合的差集，再将其新加入到dest对应的集合中"""
        return self._pool.sdiffstore(dest, keys, *args)

    def sinter(self, keys, *args):
        """交集"""
        return self._pool.sinter(keys, *args)

    def sinterstore(self, dest, keys, *args):
        """获取keys对应集合的并集，再将其加入到dest对应的集合中"""
        return self._pool.sinterstore(dest, keys, *args)

    def sunion(self, keys, *args):
        """并集"""
        return self._pool.sunion(keys, *args)

    def sunionstore(self, dest, keys, *args):
        """获取keys对应的集合的并集，并将结果保存到dest对应的集合中"""
        return self._pool.sunionstore(dest, keys, *args)

    def sismember(self, name, value):
        """判断是否是集合的成员"""
        return self._pool.sismember(name, value)

    def smove(self, src, dst, value):
        """将某个成员从一个集合中移动到另外一个集合"""
        return self._pool.smove(src, dst, value)

    def spop(self, name, count: int = None):
        """随机删除并且返回被删除值"""
        return self._pool.spop(name, count)

    def srem(self, name, *values):
        """指定值删除"""
        return self._pool.srem(name, *values)


class OrderSet(RedisDataType):

    def zrange(
            self, name, start: int, end: int, desc: bool = False, withscores: bool = False,
            score_cast_func: Union[Type, Callable] = float
    ):
        return self._pool.zrange(
            name, start, end, desc=desc, withscores=withscores, score_cast_func=score_cast_func
        )
    
    def zadd(self, name, mapping, **kwargs):
        return self._pool.zadd(name, mapping, **kwargs)

    def zcard(self, name):
        """获取有序集合元素个数 类似于len"""
        return self._pool.zcard(name)

    def zcount(self, name, min, max):
        """获取name对应的有序集合中分数 在 [min,max] 之间的个数"""
        return self._pool.zcount(name, min, max)

    def zincrby(self, name, amount: float, value):
        """自增"""
        return self._pool.zincrby(name, amount, value)

    def zrank(self, name, value):
        """获取值的索引号"""
        return self._pool.zrank(name, value)
    
    def zrem(self, name, *value):
        """获取值的索引号"""
        return self._pool.zrem(name, *value)

    def zremrangebyrank(self, name, min: int, max: int):
        """删除--根据排行范围删除，按照索引号来删除"""
        return self._pool.zremrangebyrank(name, min, max)

    def zremrangebyscore(self, name, min, max):
        """删除--根据分数范围删除"""
        return self._pool.zremrangebyscore(name, min, max)

    def zscore(self, name, value):
        """获取值对应的分数"""
        return self._pool.zscore(name, value)


class List(RedisDataType):

    def lpush(self, name, *values):
        """从左边新增加元素--没有就新建"""
        return self._pool.lpush(name, *values)

    def rpush(self, name, *values):
        """从右边新增加元素--没有就新建"""
        return self._pool.rpush(name, *values)

    def lpushx(self, name, value):
        """往已经有的name的列表的左边添加元素，没有的话无法创建"""
        return self._pool.lpushx(name, value)

    def rpushx(self, name, *value):
        """往已经有的name的列表的右边添加元素，没有的话无法创建"""
        return self._pool.rpushx(name, *value)

    def linsert(self, name, where, refvalue, value):
        """固定索引号位置插入元素"""
        return self._pool.linsert(name, where, refvalue, value)

    def lset(self, keys, index: int, value):
        """指定索引号进行修改"""
        return self._pool.lset(keys, index, value)

    def lrem(self, name, count: int, value):
        """指定值进行删除"""
        return self._pool.lrem(name, count, value)

    def lpop(self, name):
        """在name对应的列表的左侧获取第一个元素并在列表中移除，返回值则是第一个元素"""
        return self._pool.lpop(name)

    def ltrim(self, name, start: int, end: int):
        """在name对应的列表中移除没有在start-end索引之间的值"""
        return self._pool.ltrim(name, start, end)

    def lindex(self,  name, index):
        """根据索引号取值"""
        return self._pool.lindex(name, index)

    def rpoplpush(self, src, dst):
        """从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边"""
        return self._pool.rpoplpush(src, dst)

    def brpoplpush(self, src, dst, timeout: int = 0):
        """从一个列表的右侧移除一个元素并将其添加到另一个列表的左侧"""
        return self._pool.brpoplpush(src, dst, timeout)

    def blpop(self, keys, timeout: int = 0):
        """一次移除多个列表，将多个列表排列，按照从左到右去pop对应列表的元素"""
        return self._pool.blpop(keys, timeout)

    def brpop(self, keys, timeout: int = 0):
        """一次移除多个列表，将多个列表排列,按照从右像左去移除各个列表内的元素"""
        return self._pool.brpop(keys, timeout)

    def llen(self, name):
        """获取列表长度"""
        return self._pool.llen(name)

    def list_iter(self, name):
        """列表增量迭代"""
        for index in range(self.llen(name)):
            yield self.lindex(name, index)


class Hash(RedisDataType):

    def find(self, *, name: str, limit: Optional[int] = None, offset: Optional[int] = None):
        if limit is None and offset is None:
            data = []
            for k, v in self.hgetall(name).items():
                x = json.loads(v)
                x['id'] = k
                data.append(x)
            return sorted(data, key=lambda x: x['id'])
        if limit is None and offset is not None:
            count = self.hlen(name)
            data = []
            for k, v in self._pool.hmget(name, [i for i in range(offset, count + 1)]).items():
                x = json.loads(v)
                x['id'] = k
                data.append(x)
            return sorted(data, key=lambda x: x['id'])
        if limit is not None and offset is None:
            data = []
            for k, v in self._pool.hmget(name, [i for i in range(1, limit + 1)]).items():
                x = json.loads(v)
                x['id'] = k
                data.append(x)
            return sorted(data, key=lambda x: x['id'])
        return []
    
    def insert(self, name, items=None):

        if isinstance(items, dict):
            items = [items]

        keys = self.hkeys(name)
        if keys:
            try:
                last_id = max([int(i) for i in keys])
            except ValueError:
                last_id = 0
            items = {last_id + i + 1: json.dumps(escape_strings(v)) for i, v in enumerate(items)}
        else:
            items = {i + 1: json.dumps(escape_strings(v)) for i, v in enumerate(items)}
        return self.hmset(name, items)
    
    def update(self, name: str, data: dict, item: dict):
        ids = [i.pop('id') for i in data]
        for i in data:
            for k, v in item.items():
                i[k] = v
        data = [{k: json.dumps(escape_strings(v)) for k, v in i.items()} for i in data]
        self.hdel(name, *ids)
        return self.hmset(name, {k: json.dumps(v) for k, v in zip(ids, data)})
    
    def delete(self, name, items=None):
        pass
    
    def hset(self, name, key=None, value=None):
        if not isinstance(key, str):
            key = str(key)
        if not isinstance(value, str):
            value = str(value)
        return self._pool.hset(name, key, value)

    def hmset(self, name, mapping):
        return self._pool.hmset(name, mapping)

    def hget(self, name, key):
        """取出所有的键值对"""
        return self._pool.hget(name, key)

    def hmget(self, name, keys):
        """取出所有的键值对"""
        return self._pool.hmget(name, keys)

    def hgetall(self, name):
        """取出所有的键值对"""
        return self._pool.hgetall(name)

    def hlen(self, name):
        """得到所有键值对的格式 hash长度"""
        return self._pool.hlen(name)

    def hdel(self, name, *keys):
        """得到所有键值对的格式 hash长度"""
        return self._pool.hdel(name, *keys)

    def hkeys(self, name):
        """得到所有的keys（类似字典的取所有keys）"""
        return self._pool.hkeys(name)

    def hvals(self, name):
        """得到所有的value（类似字典的取所有value）"""
        return self._pool.hvals(name)

    def hexists(self, name, key):
        """断成员是否存在（类似字典的in）"""
        return self._pool.hexists(name, key)

    def hincrbyfloat(self, name, key, amount: float = 1.0):
        """自增自减浮点数(将key对应的value--浮点数 自增1.0或者2.0，或者别的浮点数 负数就是自减)"""
        return self._pool.hincrbyfloat(name, key, amount=amount)

    def hscan(self, name, cursor: int = 0, match=None, count: Optional[int] = None):
        """取值查看--分片读取"""
        return self._pool.hscan(name, cursor=cursor, match=match, count=count)

    def hscan_iter(self, name, match=None, count: Optional[int] = None):
        """利用yield封装hscan创建生成器，实现分批去redis中获取数据"""
        return self._pool.hscan_iter(name, match=match, count=count)


class SyncRdisAPI:

    def __init__(
            self, *, host: str, port: int = 6379, username: Optional[str] = None, password: Optional[str] = None,
            db: [int, str] = 0, encoding: str = "utf-8", max_connections: Optional[int] = None
    ):
        super().__init__()
        self._conn_kwargs = {
            'host': host, 'port': port, 'username': username, 'password': password, 'db': db, 'encoding': encoding, 
            'decode_responses': True, 'retry_on_timeout': True, 'max_connections': max_connections
        }
        self._pool = Redis(**self._conn_kwargs)

    def find(
            self, *, table: str, data_type: str, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None, rtype=None, **kwargs
    ):
        type_instance = getattr(self, data_type, None)
        if type_instance:
            data = type_instance.find(name=table, offset=offset, limit=limit)
            if data:
                if field:
                    if isinstance(field, str):
                        field = [field]
                    data = [{k: v for k, v in i.items() if k in field} for i in data]
                if where:
                    data = [i for i in data if all([i.get(x) == y for x, y in where.items()])]
                if order:
                    if isinstance(order, str):
                        order = [order]
                    data = sorted(data, key=lambda item: tuple(item[key] for key in order), reverse=desc)
        else:
            data = []

        if rtype == 'list':
            return data
        elif rtype == 'dict':
            return data[0] if data else dict()
        elif rtype == 'pd':
            return pd.DataFrame(data)
        else:
            return iter(data)

    def insert(self, table, data_type, items: list, auto_update: bool = False, **kwargs):
        type_instance = getattr(self, data_type, None)
        if type_instance:
            return type_instance.insert(name=table, items=items)
        return False

    def update(self, table: str, data_type, item: dict, where: Optional[dict] = None):
        type_instance = getattr(self, data_type, None)
        if type_instance:
            data = self.find(table=table, data_type=data_type, where=where, rtype='list')
            if not data:
                return False
            return type_instance.update(name=table, data=data, item=item)
        return False

    @property
    def string(self) -> String:
        return String.from_redis(self._pool)

    @property
    def set(self) -> Set:
        return Set.from_redis(self._pool)

    @property
    def order_set(self) -> OrderSet:
        return OrderSet.from_redis(self._pool)

    @property
    def list(self) -> List:
        return List.from_redis(self._pool)

    @property
    def hash(self) -> Hash:
        return Hash.from_redis(self._pool)

    def delete(self, key):
        """删除"""
        self._pool.delete(key)

    def ttl(self, key):
        """过期时间"""
        self._pool.ttl(key)

    def exists(self, key):
        """检查名字是否存在"""
        self._pool.exists(key)

    def keys(self):
        """模糊匹配"""
        return self._pool.keys()

    def expire(self, key, seconds):
        """设置超时时间"""
        self._pool.expire(key, seconds)

    def rename(self):
        """重命名"""
        self._pool.rename()

    def randomkey(self):
        """随机获取name"""
        self._pool.randomkey()

    def type(self):
        """获取类型"""
        self._pool.type()

    def scan(self):
        """查看所有元素"""
        self._pool.scan()

    def scan_iter(self):
        """查看所有元素--迭代器"""
        self._pool.scan()

    def dbsize(self):
        """前redis包含多少条数据"""
        self._pool.dbsize()

    def save(self):
        """执行"检查点"操作，将数据写回磁盘。保存时阻塞"""
        self._pool.save()

    def flushdb(self):
        """清空所有数据"""
        self._pool.flushdb()

    def close(self):
        """关闭数据库连接"""
        if self._pool is None:
            return 
        self._pool.connection_pool.disconnect()
        logger.level3(msg=f'redis连接{self._conn_kwargs["db"]}数据库连接已关闭')

    def ping(self):
        self._pool.ping()

    def delete(self):
        pass
