from typing import Dict, Type

from AioSpider.objects import DataBaseType
from AioSpider.orm.config import Configuration

from .adapter import DatabaseAdapter, AsyncDatabaseAdapter
from .mysql_adapter import MySQLAdapter, AsyncMySQLAdapter
from .sqlite_adapter import SQLiteAdapter, AsyncSQLiteAdapter
from .maria_adapte import MariaDBAdapter, AsyncMariaDBAdapter
from .oracle_adapter import OracleAdapter, AsyncOracleAdapter
from .sqlserver_adapter import SQLServerAdapter, AsyncSQLServerAdapter
from .postgresql_adapter import PostgreSQLAdapter, AsyncPostgreSQLAdapter
from .redis_adapter import RedisAdapter
from .mongo_adapter import MongoAdapter

__all__ = ['DatabaseAdapterFactory', 'AsyncDatabaseAdapterFactory']


class DatabaseAdapterFactory:
    _instance = None
    _adapter_map: Dict[DataBaseType, Type[DatabaseAdapter]] = {
        DataBaseType.mysql: MySQLAdapter,
        DataBaseType.sqlite: SQLiteAdapter,
        DataBaseType.mariadb: MariaDBAdapter,
        DataBaseType.oracle: OracleAdapter,
        DataBaseType.sqlserver: SQLServerAdapter,
        DataBaseType.postgresql: PostgreSQLAdapter,
        DataBaseType.mongodb: MongoAdapter,
        DataBaseType.redis: RedisAdapter,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}
        return cls._instance

    @classmethod
    def create_adapter(cls, db_type: DataBaseType, db: str) -> DatabaseAdapter:
        instance = cls()

        if db_type in instance.connections and db in instance.connections[db_type]:
            return instance.connections[db_type][db]

        adapter_class = cls._adapter_map.get(db_type)

        if db_type in [DataBaseType.csv, DataBaseType.file]:
            return None

        if not adapter_class:
            raise TypeError(f'不支持 {db_type.value} 数据库类型')

        config = Configuration.get_db_config(db_type, db)
        adapter = adapter_class.from_config(config.get_data())
        adapter.connect()

        if db_type not in instance.connections:
            instance.connections[db_type] = {}
        instance.connections[db_type][db] = adapter

        return adapter

    @classmethod
    def close(cls):
        if hasattr(cls._instance, 'connections'):
            for connection  in cls._instance.connections.values():
                for adapter in connection.values():
                    adapter.close()
        cls._instance = None


class AsyncDatabaseAdapterFactory:
    _instance = None
    _adapter_map: Dict[DataBaseType, Type[AsyncDatabaseAdapter]] = {
        DataBaseType.mysql: AsyncMySQLAdapter,
        DataBaseType.sqlite: AsyncSQLiteAdapter,
        DataBaseType.mariadb: AsyncMariaDBAdapter,
        DataBaseType.oracle: AsyncOracleAdapter,
        DataBaseType.sqlserver: AsyncSQLServerAdapter,
        DataBaseType.postgresql: AsyncPostgreSQLAdapter,
        DataBaseType.mongodb: MongoAdapter,
        DataBaseType.redis: RedisAdapter,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}
        return cls._instance

    @classmethod
    async def create_adapter(cls, db_type: DataBaseType, db: str) -> AsyncDatabaseAdapter:
        instance = cls()

        if db_type in instance.connections and db in instance.connections[db_type]:
            return instance.connections[db_type][db]

        adapter_class = cls._adapter_map.get(db_type)
        if not adapter_class:
            raise TypeError(f'不支持 {db_type.value} 数据库类型')
        
        if db_type in [DataBaseType.csv, DataBaseType.file]:
            return None

        config = Configuration.get_db_config(db_type, db)
        adapter = adapter_class.from_config(config.get_data())
        await adapter.connect()

        if db_type not in instance.connections:
            instance.connections[db_type] = {}
        instance.connections[db_type][db] = adapter

        return adapter

    @classmethod
    async def close(cls):
        if hasattr(cls._instance, 'connections'):
            for connection  in cls._instance.connections.values():
                for adapter in connection.values():
                    await adapter.close()
        cls._instance = None
