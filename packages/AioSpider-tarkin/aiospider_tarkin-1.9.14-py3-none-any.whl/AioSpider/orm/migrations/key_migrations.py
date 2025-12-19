from typing import List

from AioSpider.orm.adapter import DatabaseAdapter
from .base_migration import KeyMigration

__all__ = [
    "AddPrimaryKeyMigration",
    "RemovePrimaryKeyMigration",
    "AddUniqueKeyMigration",
    "RemoveUniqueKeyMigration",
    "AddForeignKeyMigration",
    "RemoveForeignKeyMigration",
    "AddIndexMigration",
    "RemoveIndexMigration",
    "AddCompositeUniqueKeyMigration",
    "RemoveCompositeUniqueKeyMigration",
    "AddCompositeIndexMigration",
    "RemoveCompositeIndexMigration"
]


class AddPrimaryKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, "Add primary key")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (`{self.column_name}`);"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY (`{self.column_name}`);"
        db_adapter.execute(sql)


class RemovePrimaryKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, "Remove primary key")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP PRIMARY KEY (`{self.column_name}`);"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (`{self.column_name}`);"
        db_adapter.execute(sql)


class AddUniqueKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, f"Add unique key")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `udx_{self.column_name}` UNIQUE (`{self.column_name}`);"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP INDEX `udx_{self.column_name}`;"

        db_adapter.execute(sql)


class RemoveUniqueKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, f"Remove unique key")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP INDEX `udx_{self.column_name}`;"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `udx_{self.column_name}` UNIQUE (`{self.column_name}`);"
        db_adapter.execute(sql)


class AddForeignKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str, ref_table: str, ref_column: str):
        super().__init__(table_name, column_name, "Add foreign key")
        self.ref_table = ref_table
        self.ref_column = ref_column

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `fk_{self.column_name}` FOREIGN KEY (`{self.column_name}`) REFERENCES {self.ref_table}(`{self.ref_column}`);"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP FOREIGN KEY `fk_{self.column_name}`;"
        db_adapter.execute(sql)


class RemoveForeignKeyMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str, ref_table: str, ref_column: str):
        super().__init__(table_name, column_name, "Remove foreign key")
        self.ref_table = ref_table
        self.ref_column = ref_column

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP FOREIGN KEY `fk_{self.column_name}`;"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `fk_{self.column_name}` FOREIGN KEY (`{self.column_name}`) REFERENCES {self.ref_table}(`{self.ref_column}`);"
        db_adapter.execute(sql)


class AddIndexMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, "Add index")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"CREATE INDEX `idx_{self.column_name}` ON {self.table_name} (`{self.column_name}`);"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"DROP INDEX `idx_{self.column_name}` ON {self.table_name};"
        db_adapter.execute(sql)


class RemoveIndexMigration(KeyMigration):

    def __init__(self, table_name: str, column_name: str):
        super().__init__(table_name, column_name, "Remove index")

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"DROP INDEX `idx_{self.column_name}` ON {self.table_name};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"CREATE INDEX `idx_{self.column_name}` ON {self.table_name} (`{self.column_name}`);"
        db_adapter.execute(sql)


class AddCompositeUniqueKeyMigration(KeyMigration):

    def __init__(self, table_name: str, columns: List[str]):
        super().__init__(table_name, ', '.join([f'`{i}`' for i in columns]), "Add composite unique key")
        self.key_name = f"udx_{'_'.join(columns)}"

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `{self.key_name}` UNIQUE ({self.column_name});"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP INDEX `{self.key_name}`;"
        db_adapter.execute(sql)


class RemoveCompositeUniqueKeyMigration(KeyMigration):

    def __init__(self, table_name: str, columns: List[str], index_name: str):
        super().__init__(table_name, '、'.join([f'`{i}`' for i in columns]), "Remove composite unique key")
        self.index_name = index_name

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} DROP INDEX `{self.index_name}`;"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"ALTER TABLE {self.table_name} ADD CONSTRAINT `{self.index_name}` UNIQUE ({self.column_name});"
        db_adapter.execute(sql)


class AddCompositeIndexMigration(KeyMigration):

    def __init__(self, table_name: str, columns: List[str]):
        super().__init__(table_name, '、'.join([f'`{i}`' for i in columns]), "Add composite index")
        self.index_name = f"idx_{table_name}_{'_'.join(columns)}"

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"CREATE INDEX `{self.index_name}` ON {self.table_name} ({self.column_name});"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"DROP INDEX `{self.index_name}` ON {self.table_name};"
        db_adapter.execute(sql)


class RemoveCompositeIndexMigration(KeyMigration):

    def __init__(self, table_name: str, columns: List[str], index_name: str):
        super().__init__(table_name, '、'.join([f'`{i}`' for i in columns]), "Remove composite index")
        self.index_name = index_name

    def apply(self, db_adapter: DatabaseAdapter):
        sql = f"DROP INDEX `{self.index_name}` ON {self.table_name};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter):
        sql = f"CREATE INDEX `{self.index_name}` ON {self.table_name} ({self.column_name});"
        db_adapter.execute(sql)
