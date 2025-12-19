from typing import Any, List, Dict, Optional
from pymongo import MongoClient
from .adapter import DatabaseAdapter


class MongoAdapter(DatabaseAdapter):

    def __init__(
            self, host: str, database: str = None, auth_db: str = 'admin', username: Optional[str] = None, 
            password: Optional[str] = None, port: int = 27017, ssl: bool = True
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.auth_db = auth_db
        self.username = username
        self.password = password
        self.client = None
        self.db = None

    def connect(self) -> None:
        self.client = MongoClient(
            host=self.host, port=self.port, username=self.username, password=self.password, authSource=self.auth_db
        )
        self.db = self.client[self.database]

    def close(self):
        self.client.close()
        print(f'mongodb连接{self.database}数据库连接已关闭')

    def execute(self, collection: str, operation: str, *args, **kwargs) -> Any:
        return getattr(self.db[collection], operation)(*args, **kwargs)
    
    def execute_many(self, collection: str, operation: str, *args, **kwargs) -> Any:
        return getattr(self.db[collection], operation)(*args, **kwargs)

    def fetch_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.db[collection].find_one(filter)

    def fetch_all(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return list(self.db[collection].find(filter or {}))
