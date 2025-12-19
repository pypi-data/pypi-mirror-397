import asyncio
from datetime import datetime
from typing import List, Union, Optional, TypeVar, Iterator

import pymongo
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from AioSpider import logger
from AioSpider.exceptions import ConnectionException, StatusTags, AioValueError
from AioSpider.db.abc import AsyncABC


DataType = TypeVar('RType', list, dict, pd.DataFrame, Iterator)


class AsyncMongoAPI(AsyncABC):
    """
    初始化
    Params:
        host: MongoDB的主机名，默认为localhost
        port: MongoDB的端口，默认为27017
        db: 数据库
        auth_db: 用于验证的数据库，默认是admin数据库
        username: 用于连接的MongoDB用户名
        password: 对应的密码
        max_connect_size: 连接池的最大连接数，默认为100
        min_connect_size: 连接池的最小连接数，默认为0
        max_idle_time: MongoDB连接池的最大空闲时间（以毫秒为单位）。在指定的时间内，如果连接处于空闲状态，它可以被关闭并从连接池中删除。
    """

    def __init__(
            self, host: Optional[str] = None, port: int = 27017, db: Optional[str] = None, auth_db: str = 'admin',
            username: Optional[str] = None, password: Optional[str] = None, max_connect_size: int = 100,
            min_connect_size: int = 0, max_idle_time: int = 0
    ):
        super(AsyncMongoAPI, self).__init__()
        self.client = None
        if not isinstance(port, int):
            try:
                port = int(port)
            except ValueError:
                raise AioValueError(status=StatusTags.InvalidMongoConnetPort)
        assert isinstance(max_connect_size, int), AioValueError(status=StatusTags.InvalidMongoConnetMaxsize)
        assert isinstance(min_connect_size, int), AioValueError(status=StatusTags.InvalidMongoConnetMinsize)
        assert max_connect_size >= min_connect_size, AioValueError(status=StatusTags.InvalidMongoConnetSize)
        assert isinstance(max_idle_time,  int), AioValueError(status=StatusTags.InvalidMongoConnetTimeout)
        if max_idle_time == 0:
            max_idle_time = None
        else:
            max_idle_time *= 1000
        self.kw = {
            'host': host, 'port': port, 'username': username, 'password': password, 'authSource': auth_db,
            'maxPoolSize': max_connect_size, 'minPoolSize': min_connect_size, 'maxIdleTimeMS': max_idle_time
        }
        self.database = db
        self._db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(**self.kw)
        except:
            raise ConnectionException(status=StatusTags.MongoConnetError)
        return self

    @property
    def db(self):
        if self._db is None:
            self._db = self.client[self.database]
        return self._db

    async def close(self):
        """
        关闭MongoDB数据库连接
        """
        self.client.close()
        logger.info(f'mongodb连接{self.database}数据库连接已关闭')

    async def insert(self, table: str, items: Union[dict, List], where=None, auto_update: bool = False):
        """
        插入多条记录
        Params:
            table: 集合名称
            documents: 文档列表
            auto_update: 是否自动跟新
        Return:
            插入文档的ID列表
        """

        col = self.db[table]

        if isinstance(items, dict):
            items = [items]
            
        items = [
            {k: v if isinstance(v, (str, int, float, datetime)) else str(v) for k, v in i.items()} for i in items
        ]

        if auto_update and where:
            documents = []
            for item in items:
                documents.append(
                    pymongo.UpdateOne(
                        filter={k: v for k, v in item.items() if k in where},
                        update={"$set": item},
                        upsert=True
                    )
                )
            if documents:
                result = await col.bulk_write(documents)
                return result.upserted_count
        else:
            result = await col.insert_many(items)
            return result.inserted_ids

    async def find(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            rtype: DataType = 'list', sql=None
    ):
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                limit: 数量
                offset: 偏移量
                desc: 是否倒序
                group: 分组
                having: 筛选分组后的各组数据
                order: 排序约束
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                rtype: 返回类型
        """
        col = self.db[table]
        cursor = col.find(where, field)

        if order is not None:
            if isinstance(order, list):
                for i in order:
                    cursor = cursor.sort(i, int(desc))
            else:
                cursor = cursor.sort(order, int(desc))

        if offset is not None:
            cursor = cursor.skip(offset)

        if limit is not None:
            cursor = cursor.limit(limit)

        if rtype == 'list':
            result = []
            async for i in cursor:
                result.append(i)
            # return result
        elif rtype == 'dict':
            async for i in cursor:
                yield i
                break
        elif rtype == 'pd':
            result = []
            async for i in cursor:
                result.append(i)
            # return result
            # return pd.DataFrame(await cursor.to_list())
        else:
            async for i in cursor:
                yield i

    async def update(self, table: str, where: dict, items: Union[dict, list]):
        """
        更新多条记录
        Params:
            table: 表名
            where: 查询条件
            items: 更新数据
        Return:
            返回被修改的文档数量
        """

        col = self.db[table]

        if isinstance(dict):
            items = [items]

        result = await col.update_many(where, items)
        return result.modified_count

    async def delete(self, collection: str, filter: dict):
        """
        删除一条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
        Return:
            返回被删除的文档数量
        """
        col = self.db[collection]
        result = await col.delete_one(filter)
        return result.deleted_count

    async def delete_many(self, collection: str, filter: dict):
        """
        删除多条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
        Return:
            返回被删除的文档数量
        """
        col = self.db[collection]
        result = await col.delete_many(filter)
        return result.deleted_count


