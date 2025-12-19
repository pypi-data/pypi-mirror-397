from abc import ABC, abstractmethod
from typing import List

from AioSpider.objects import DataBaseType
from AioSpider.exceptions import TableBuilderError

__all__ = ['TableBuilderFactory']


class AbstractTableBuilder(ABC):

    def __init__(self, model):
        self.model = model
        self.table_name = self.model.table_name

    @abstractmethod
    def build_table_sql(self) -> str:
        pass


class MySQLTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        charset = self.model.Meta.data_meta.charset
        engine = self.model.Meta.data_meta.engine
        comment = self.model.__doc__ or ''

        sql = f"CREATE TABLE IF NOT EXISTS `{self.table_name}` (\n"
        sql += ",\n".join(field_definitions)
        if index_definitions:
            sql += ',\n' + ",\n".join(index_definitions)

        sql += f"\n) ENGINE={engine} DEFAULT CHARSET={charset} COMMENT='{comment}';"
        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field in self.model.fields.values():
            field_definitions.append('    ' + field.to_mysql())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(f"    INDEX `idx_{field.column}` (`{field.column}`)")
            elif field.unique:
                index_definitions.append(f"    UNIQUE INDEX `udx_{field.column}` (`{field.column}`)")

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(f"    INDEX `{index_name}` ({index_fields})")

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(f"    UNIQUE INDEX `{index_name}` ({index_fields})")

        return index_definitions


class SQLiteTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        sql = f"CREATE TABLE IF NOT EXISTS `{self.table_name}` (\n"
        sql += ",\n".join(field_definitions)
        sql += "\n);"

        for index in index_definitions:
            sql += f"\n{index}"

        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field in self.model.fields.values():
            field_definitions.append('    ' + field.to_sqlite())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(
                    f"CREATE INDEX IF NOT EXISTS `idx_{self.model.table_name}_{field.column}` ON "
                    f"`{self.table_name}` (`{field.column}`);"
                )
            elif field.unique:
                index_definitions.append(
                    f"CREATE UNIQUE INDEX IF NOT EXISTS `udx_{self.model.table_name}_{field.column}` ON "
                    f"`{self.table_name}` (`{field.column}`);"
                )

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{self.model.table_name}_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(
                f"CREATE INDEX IF NOT EXISTS `{index_name}` ON `{self.table_name}` ({index_fields});"
            )

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{self.model.table_name}_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(
                f"CREATE UNIQUE INDEX IF NOT EXISTS `{index_name}` ON `{self.table_name}` ({index_fields});"
            )

        return index_definitions


class OracleTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        sql = f"CREATE TABLE {self.table_name} (\n"
        sql += ",\n".join(field_definitions)
        sql += "\n);"

        for index in index_definitions:
            sql += f"\n{index}"

        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field in self.model.fields.values():
            field_definitions.append('    ' + field.to_oracle())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(f"CREATE INDEX `idx_{field.column}` ON `{self.table_name}` (`{field.column}`);")
            elif field.unique:
                index_definitions.append(
                    f"CREATE UNIQUE INDEX `udx_{field.column}` ON `{self.table_name}` (`{field.column}`);")

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{'_'.join(index)}"
            index_fields = ', '.join(f'"{field}"' for field in index)
            index_definitions.append(f"CREATE INDEX {index_name} ON {self.table_name} ({index_fields});")

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{'_'.join(index)}"
            index_fields = ', '.join(f'"{field}"' for field in index)
            index_definitions.append(f"CREATE UNIQUE INDEX {index_name} ON {self.table_name} ({index_fields});")

        return index_definitions


class SQLServerTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        sql = f"CREATE TABLE {self.table_name} (\n"
        sql += ",\n".join(field_definitions)
        sql += "\n);"

        for index in index_definitions:
            sql += f"\n{index}"

        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field in self.model.fields.values():
            field_definitions.append('    ' + field.to_sqlserver())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(f"CREATE INDEX `idx_{field.column}` ON `{self.table_name}` (`{field.column}`);")
            elif field.unique:
                index_definitions.append(
                    f"CREATE UNIQUE INDEX `udx_{field.column}` ON `{self.table_name}` (`{field.column}`);")

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{'_'.join(index)}"
            index_fields = ', '.join(f'[{field}]' for field in index)
            index_definitions.append(f"CREATE INDEX {index_name} ON {self.table_name} ({index_fields});")

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or tuple():
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{'_'.join(index)}"
            index_fields = ', '.join(f'[{field}]' for field in index)
            index_definitions.append(f"CREATE UNIQUE INDEX {index_name} ON {self.table_name} ({index_fields});")

        return index_definitions


class PostgreSQLTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} (\n"
        sql += ",\n".join(field_definitions)
        sql += "\n);"

        for index in index_definitions:
            sql += f"\n{index}"

        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field in self.model.fields.values():
            field_definitions.append('    ' + field.to_postgresql())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(f"CREATE INDEX `idx_{field.column}` ON `{self.table_name}` (`{field.column}`);")
            elif field.unique:
                index_definitions.append(
                    f"CREATE UNIQUE INDEX `udx_{field.column}` ON `{self.table_name}` (`{field.column}`);")

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or []:
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{'_'.join(index)}"
            index_fields = ', '.join(f'"{field}"' for field in index)
            index_definitions.append(f"CREATE INDEX {index_name} ON {self.table_name} ({index_fields});")

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or []:
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{'_'.join(index)}"
            index_fields = ', '.join(f'"{field}"' for field in index)
            index_definitions.append(f"CREATE UNIQUE INDEX {index_name} ON {self.table_name} ({index_fields});")

        return index_definitions


class MariaDBTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        field_definitions = self._generate_field_definitions()
        index_definitions = self._generate_index_definitions()

        charset = self.model.Meta.data_meta.charset
        engine = self.model.Meta.data_meta.engine
        comment = self.model.__doc__ or ''

        sql = f"CREATE TABLE IF NOT EXISTS `{self.table_name}` (\n"
        sql += ",\n".join(field_definitions)
        if index_definitions:
            sql += ',\n' + ",\n".join(index_definitions)

        sql += f"\n) ENGINE={engine} DEFAULT CHARSET={charset} COMMENT='{comment}';"
        return sql

    def _generate_field_definitions(self) -> List[str]:
        field_definitions = []
        for field_name, field in self.model.fields.items():
            if not field.is_created:
                continue
            field_definitions.append('    ' + field.to_mariadb())
        return field_definitions

    def _generate_index_definitions(self) -> List[str]:
        index_definitions = []

        # 添加单字段索引
        for field in self.model.fields.values():
            if field.index:
                index_definitions.append(f"CREATE INDEX `idx_{field.column}` ON `{self.table_name}` (`{field.column}`);")
            elif field.unique:
                index_definitions.append(
                    f"CREATE UNIQUE INDEX `udx_{field.column}` ON `{self.table_name}` (`{field.column}`);")

        # 添加复合索引
        for index in self.model.Meta.composite_indexes or []:
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"idx_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(f"    INDEX `{index_name}` ({index_fields})")

        # 添加复合唯一索引
        for index in self.model.Meta.composite_unique_indexes or []:
            if not isinstance(index, tuple):
                raise TableBuilderError(
                    f'{self.model.__class__} 模型联合唯一索引构建失败！模型联合唯一索引必须设置为嵌套元组(Tuple[Tuple[str, ...], ...]）类型'
                    f'（值：{self.model.Meta.composite_unique_indexes}）'
                )
            index_name = f"udx_{'_'.join(index)}"
            index_fields = ', '.join(f'`{field}`' for field in index)
            index_definitions.append(f"    UNIQUE INDEX `{index_name}` ({index_fields})")

        return index_definitions


class MongoDBTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        # MongoDB does not use SQL for table creation
        return "MongoDB does not use SQL for table creation."


class RedisTableBuilder(AbstractTableBuilder):

    def build_table_sql(self) -> str:
        # Redis does not use SQL for table creation
        return "Redis does not use SQL for table creation."


class TableBuilderFactory:

    def __init__(self, model):
        self.model = model
        self.builder = self._select_builder()

    def _select_builder(self):
        db_type = self.model.Meta.database_type
        if db_type == DataBaseType.mysql:
            return MySQLTableBuilder(self.model)
        elif db_type == DataBaseType.sqlite:
            return SQLiteTableBuilder(self.model)
        elif db_type == DataBaseType.oracle:
            return OracleTableBuilder(self.model)
        elif db_type == DataBaseType.sqlserver:
            return SQLServerTableBuilder(self.model)
        elif db_type == DataBaseType.postgresql:
            return PostgreSQLTableBuilder(self.model)
        elif db_type == DataBaseType.mariadb:
            return MariaDBTableBuilder(self.model)
        elif db_type == DataBaseType.mongodb:
            return MongoDBTableBuilder(self.model)
        elif db_type == DataBaseType.redis:
            return RedisTableBuilder(self.model)
        elif db_type == DataBaseType.csv:
            pass
        elif db_type == DataBaseType.file:
            pass
        else:
            raise ValueError(f"不支持的数据库类型: {self.model.Meta.database_type}")

    def build(self):
        return self.builder.build_table_sql()

    def __getattr__(self, item):
        if hasattr(self.builder, item):
            return getattr(self.builder, item)
        raise AttributeError(f"'{self.__class__.__name__}' 没有 '{item}' 方法或属性")
