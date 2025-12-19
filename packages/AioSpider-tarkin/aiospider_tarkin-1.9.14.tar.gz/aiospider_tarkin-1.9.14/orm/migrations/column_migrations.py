from typing import Any, Dict, Optional

from AioSpider.orm.adapter import DatabaseAdapter
from .base_migration import ColumnMigration

__all__ = [
    "AddColumnMigration",
    "RemoveColumnMigration",
    "RenameColumnMigration",
    "ChangeColumnTypeMigration",
    "ChangeColumnPrecisionMigration",
    "ChangeDefaultValueMigration",
    "ChangeNullableMigration",
    "ChangeColumnLengthMigration",
    "ChangeAutoIncrementAndSignedMigration",
    "ChangeTimestampMigration",
]


class AddColumnMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, column_type: str, comment: str = None):
        super().__init__(table_name, column_name, "Add", comment)
        self.column_type = column_type

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` ADD COLUMN `{self.column_name}` {self.column_type} COMMENT '{self.comment}';"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` DROP COLUMN `{self.column_name}` COMMENT '{self.comment}';"
        db_adapter.execute(sql)


class RemoveColumnMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, comment: str = None):
        super().__init__(table_name, column_name, "Remove", comment)

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` DROP COLUMN `{self.column_name}` COMMENT '{self.comment}';"
        print(sql)
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` ADD COLUMN `{self.column_name}` {self.column_type} COMMENT '{self.comment}';"
        db_adapter.execute(sql)


class RenameColumnMigration(ColumnMigration):

    def __init__(self, table_name: str, old_column_name: str, new_column_name: str, column_type: str, comment: str = None):
        super().__init__(table_name, old_column_name, "Rename", comment)
        self.new_column_name = new_column_name
        self.column_type = column_type

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` CHANGE COLUMN `{self.column_name}` `{self.new_column_name}` {self.column_type} COMMENT '{self.comment}';"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` CHANGE COLUMN `{self.new_column_name}` `{self.column_name}` {self.column_type} COMMENT '{self.comment}';"

        db_adapter.execute(sql)


class ChangeColumnTypeMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, new_type: str, comment: str = None):
        super().__init__(table_name, column_name, "Change type", comment)
        self.new_type = new_type

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.new_type} COMMENT `{self.comment}`;"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type} COMMENT `{self.comment}`;"
        db_adapter.execute(sql)


class ChangeColumnPrecisionMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, column_type: str, new_precision: int, new_scale: Optional[int] = None, comment: str = None):
        super().__init__(table_name, column_name, "Change precision", comment)
        self.column_type = column_type
        self.new_precision = new_precision
        self.new_scale = new_scale

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        precision_str = f"({self.new_precision}" + (f",{self.new_scale}" if self.new_scale is not None else "") + ")"
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type}{precision_str} COMMENT `{self.comment}`;"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        precision_str = f"({self.new_precision}" + (f",{self.new_scale}" if self.new_scale is not None else "") + ")"
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type}{precision_str} COMMENT `{self.comment}`;"
        db_adapter.execute(sql)


class ChangeDefaultValueMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, new_default: Any, comment: str = None):
        super().__init__(table_name, column_name, "Change default value", comment)
        self.new_default = new_default

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` ALTER COLUMN `{self.column_name}` SET DEFAULT {self.new_default} {comment};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` ALTER COLUMN `{self.column_name}` DROP DEFAULT {comment};"
        db_adapter.execute(sql)


class ChangeNullableMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, column_type: str, is_nullable: bool, default: str = None, comment: str = None):
        super().__init__(table_name, column_name, "Change nullable", comment)
        self.column_type = column_type
        self.is_nullable = is_nullable
        self.default = default

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        null_str = "NULL" if self.is_nullable else "NOT NULL"
        default_str = f"DEFAULT {self.default}" if self.default else ""
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type} {null_str} {default_str} {comment};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        null_str = "NOT NULL" if self.is_nullable else "NULL"
        default_str = f"DEFAULT {self.default}" if self.default else ""
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type} {null_str} {default_str} {comment};"
        db_adapter.execute(sql)


class ChangeColumnLengthMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, column_type: str, new_length: int, comment: str = None):
        super().__init__(table_name, column_name, "Change length", comment)
        self.new_length = new_length
        self.column_type = column_type

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type}({self.new_length}) {comment};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        raise NotImplementedError("Rollback for changing column length is not implemented.")


class ChangeAutoIncrementAndSignedMigration(ColumnMigration):

    def __init__(self, table_name: str, column_name: str, is_auto_increment: bool, is_unsigned: bool, comment: str = None):
        super().__init__(table_name, column_name, "Change auto increment and signed", comment)
        self.is_auto_increment = is_auto_increment
        self.is_unsigned = is_unsigned

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        auto_inc_str = "AUTO_INCREMENT" if self.is_auto_increment else ""
        signed_str = "UNSIGNED" if self.is_unsigned else ""
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` INT {signed_str} {auto_inc_str} {comment};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        auto_inc_str = "" if self.is_auto_increment else "AUTO_INCREMENT"
        signed_str = "" if self.is_unsigned else "UNSIGNED"
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` INT {auto_inc_str} {signed_str} {comment};"
        db_adapter.execute(sql)


class ChangeTimestampMigration(ColumnMigration):

    def __init__(
            self, table_name: str, column_name: str, column_type: str, is_nullable: bool, is_auto_update: bool,
            comment: str = None
    ):
        super().__init__(table_name, column_name, "Change timestamp", comment)
        self.column_type = column_type
        self.is_nullable = is_nullable
        self.is_auto_update = is_auto_update

    def apply(self, db_adapter: DatabaseAdapter) -> None:
        null_str = "NOT NULL" if self.is_nullable else "NULL"
        update_str = "ON UPDATE CURRENT_TIMESTAMP" if self.is_auto_update else ""
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {self.column_type} {null_str} DEFAULT CURRENT_TIMESTAMP {update_str} {comment};"
        db_adapter.execute(sql)

    def rollback(self, db_adapter: DatabaseAdapter) -> None:
        update_str = "" if self.is_auto_update else "ON UPDATE CURRENT_TIMESTAMP"
        comment = f"COMMENT '{self.comment}'" if self.comment else ""
        sql = f"ALTER TABLE `{self.table_name}` MODIFY COLUMN `{self.column_name}` {{self.column_type}} DEFAULT CURRENT_TIMESTAMP {update_str} {comment};"
        db_adapter.execute(sql)

