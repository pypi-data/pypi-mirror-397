from abc import ABC, abstractmethod

from AioSpider.orm.adapter import DatabaseAdapter

__all__ = ['Migration', 'ColumnMigration']


class Migration(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def apply(self, db_adapter: DatabaseAdapter) -> None:
        pass

    @abstractmethod
    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        pass

    def __str__(self):
        return f"{self.__class__.__name__} <{self.name}>"

    __repr__ = __str__


class ColumnMigration(Migration):

    def __init__(self, table_name: str, column_name: str, operation: str, comment: str = None):
        if comment:
            name = f"{operation} on {comment}<{column_name}> in {table_name}"
        else:
            name = f"{operation} on {column_name} in {table_name}"
        super().__init__(name)
        self.table_name = table_name
        self.comment = comment
        self.column_name = column_name

    @abstractmethod
    def apply(self, db_adapter: DatabaseAdapter) -> None:
        pass

    @abstractmethod
    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        pass


class KeyMigration(Migration):

    def __init__(self, table_name: str, column_name: str, operation: str):
        super().__init__(f"{operation} on {column_name} in {table_name}")
        self.table_name = table_name
        self.column_name = column_name

    @abstractmethod
    def apply(self, db_adapter: DatabaseAdapter) -> None:
        pass

    @abstractmethod
    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        pass
