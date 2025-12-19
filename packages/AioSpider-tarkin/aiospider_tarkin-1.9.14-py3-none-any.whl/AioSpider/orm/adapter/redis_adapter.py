from typing import Any, List, Dict, Optional, Tuple
from redis import Redis
from .adapter import DatabaseAdapter


class RedisAdapter(DatabaseAdapter):
    def __init__(self, host: str, port: int = 6379, db: int = 0, password: Optional[str] = None):
        super().__init__()
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client = None

    def connect(self) -> None:
        self.client = Redis(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)

    def disconnect(self) -> None:
        if self.client:
            self.client.close()

    def execute(self, command: str, *args) -> Any:
        return self.client.execute_command(command, *args)

    def fetch_one(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def fetch_all(self, pattern: str) -> List[str]:
        keys = self.client.keys(pattern)
        return self.client.mget(keys)

    def count(self, pattern: str) -> int:
        return len(self.client.keys(pattern))

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0

    def get_or_create(self, key: str, default: Any) -> Tuple[Any, bool]:
        value = self.client.get(key)
        if value is None:
            self.client.set(key, str(default))
            return default, True
        return value, False

    def bulk_create(self, items: Dict[str, Any]) -> List[bool]:
        return self.client.mset(items)

    def bulk_update(self, items: Dict[str, Any]) -> List[bool]:
        return self.client.mset(items)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        return self.client.set(key, value, ex=ex)

    def delete(self, *keys: str) -> int:
        return self.client.delete(*keys)

    def increment(self, key: str, amount: int = 1) -> int:
        return self.client.incr(key, amount)

    def decrement(self, key: str, amount: int = 1) -> int:
        return self.client.decr(key, amount)

    def expire(self, key: str, seconds: int) -> bool:
        return self.client.expire(key, seconds)
