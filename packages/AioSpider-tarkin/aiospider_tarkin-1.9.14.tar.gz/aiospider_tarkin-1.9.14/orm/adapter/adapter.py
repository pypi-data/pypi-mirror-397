from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Union

__all__ = ['DatabaseAdapter', 'AsyncDatabaseAdapter']


class DatabaseAdapter(ABC):
    """数据库适配器"""

    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> "DatabaseAdapter":
        """从配置文件中创建数据库适配器"""
        pass

    @abstractmethod
    def connect(self) -> None:
        """连接数据库"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭数据库"""
        pass

    @abstractmethod
    def execute(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Any:
        """执行SQL语句"""
        pass

    @abstractmethod
    def execute_many(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Any:
        """执行多条SQL语句"""
        pass

    @abstractmethod
    def fetch_one(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Optional[Dict[str, Any]]:
        """执行SQL语句并返回一条记录"""
        pass

    @abstractmethod
    def fetch_all(self, sql: str, params: Optional[Union[List, Dict]] = None) -> List[Dict[str, Any]]:
        """执行SQL语句并返回所有记录"""
        pass


class AsyncDatabaseAdapter(ABC):
    """异步数据库适配器"""

    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> "AsyncDatabaseAdapter":
        """从配置文件中创建异步数据库适配器"""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """连接数据库"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭数据库"""
        pass

    @abstractmethod
    async def execute(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Any:
        """执行SQL语句"""
        pass

    @abstractmethod
    async def execute_many(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Any:
        """执行多条SQL语句"""
        pass

    @abstractmethod
    async def fetch_one(self, sql: str, params: Optional[Union[List, Dict]] = None) -> Optional[Dict[str, Any]]:
        """执行SQL语句并返回一条记录"""
        pass

    @abstractmethod
    async def fetch_all(self, sql: str, params: Optional[Union[List, Dict]] = None) -> List[Dict[str, Any]]:
        """执行SQL语句并返回所有记录"""
        pass
