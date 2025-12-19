import re
from collections import defaultdict
from typing import Dict, List, Any

from AioSpider.objects import DataBaseType
from ..fields import (
    DecimalField,
    FloatField,
    DoubleField,
    StampField,
    DateField,
    DateTimeField,
    TimeField,
    CharField,
    HashField,
    PathField,
    ExtensionNameField,
    IPAddressField,
    UUIDField,
    EmailField,
    PhoneNumberField,
    URLField,
    IntField,
    TinyIntField,
    SmallIntField,
    MediumIntField,
    BigIntField,
    AutoIntField,
    BooleanField,
    TextField,
    MediumTextField,
    LongTextField,
    ListField,
    JSONField,
    TinyBlobField,
    BlobField,
    MediumBlobField,
    LongBlobField,
    PriceField,
    EnumField,
)


class SchemaComparator:
    def __init__(self, model):
        self.model = model
        self.table_name = model.table_name

    def get_table_schema(self) -> List[Dict[str, Any]]:
        if self.model.Meta.database_type == DataBaseType.mysql:
            return [
                {
                    'Field': i['Field'], 'Type': i['Type'].upper(), 'Null': i['Null'] == 'YES', 'Key': i['Key'],
                    'Default': i['Default'], 'Extra': i['Extra'].upper()
                }
                for i in self.model.objects.fetch(f"DESCRIBE `{self.table_name}`;")
            ]
        elif self.model.Meta.database_type == DataBaseType.sqlite:
            table_info = self.model.objects.fetch(f"PRAGMA table_info(`{self.table_name}`);")
            return [
                {
                    'Field': i['name'], 'Type': i['type'].upper(), 'Null': not i['notnull'],
                    'Key': 'PRI' if i['pk'] else '', 'Default': i['dflt_value'],
                    'Extra': 'AUTO_INCREMENT' if i['pk'] and i['type'].lower() == 'integer' else ''
                }
                for i in table_info
            ]
        else:
            raise ValueError(f"Unsupported database type: {self.model.Meta.database_type}")

    @staticmethod
    def get_field_type_and_extra(field):
        mapping = {
            AutoIntField: ('INT', 'AUTO_INCREMENT'),
            DecimalField: ('DECIMAL', ''),
            FloatField: ('FLOAT', ''),
            DoubleField: ('DOUBLE', ''),
            StampField: (
                'TIMESTAMP', 'ON UPDATE CURRENT_TIMESTAMP' if isinstance(field, StampField) and field.auto_now else ''
            ),
            DateField: ('DATE', ''),
            DateTimeField: (
                'DATETIME', 'ON UPDATE CURRENT_TIMESTAMP' if isinstance(field, DateTimeField) and field.auto_now else ''
            ),
            TimeField: ('TIME', ''),
            CharField: ('VARCHAR', ''),
            HashField: ('CHAR', ''),
            PathField: ('VARCHAR', ''),
            ExtensionNameField: ('VARCHAR', ''),
            TinyBlobField: ('TINYBLOB', ''),
            BlobField: ('BLOB', ''),
            MediumBlobField: ('MEDIUMBLOB', ''),
            LongBlobField: ('LONGBLOB', ''),
            IPAddressField: ('VARCHAR', ''),
            UUIDField: ('CHAR', ''),
            EmailField: ('VARCHAR', ''),
            PhoneNumberField: ('VARCHAR', ''),
            URLField: ('VARCHAR', ''),
            IntField: ('INT', ''),
            TinyIntField: ('TINYINT', ''),
            SmallIntField: ('SMALLINT', ''),
            MediumIntField: ('MEDIUMINT', ''),
            BigIntField: ('BIGINT', ''),
            BooleanField: ('TINYINT', ''),
            TextField: ('TEXT', ''),
            MediumTextField: ('MEDIUMTEXT', ''),
            LongTextField: ('LONGTEXT', ''),
            ListField: ('TEXT', ''),
            PriceField: ('VARCHAR', ''),
            JSONField: ('JSON', ''),
            EnumField: ('VARCHAR', ''),
        }
        field_type, extra = mapping[type(field)]
        
        if isinstance(field, (IntField, TinyIntField, SmallIntField, MediumIntField, BigIntField)):
            field_type += f"({field.max_length})" if field.max_length else "(11)"
            if field.unsigned:
                field_type += " UNSIGNED"
        elif isinstance(field, CharField):
            field_type += f"({field.max_length})" if field.max_length is not None else "(255)"
        elif isinstance(field, DecimalField):
            field_type += f"({field.max_length},{field.precision})"
        elif isinstance(field, BooleanField):
            field_type += "(1)"
        
        return field_type, extra

    @staticmethod
    def get_field_type_default(field):
        if not field._required_default_to_db:
            return None
        if (isinstance(field, StampField) or isinstance(field, DateTimeField)) and field.auto_add:
            return 'CURRENT_TIMESTAMP'
        if field.default is None:
            return field.default
        return field.default

    def get_field_index_type(self, field):
        if field.primary:
            return 'PRI'
        if field.unique:
            return 'UNI'
        if field.index:
            return 'MUL'
        for i in (self.model.Meta.composite_unique_indexes or ()):
            if field.column == i[0]:
                return 'MUL'
        for i in (self.model.Meta.composite_indexes or ()):
            if field.column == i[0]:
                return 'MUL'
        return ''

    def get_model_schema(self) -> List[Dict[str, Any]]:
        schema = []
        for field in self.model.fields.values():
            field_type, extra = self.get_field_type_and_extra(field)
            schema.append({
                "Field": field.column,
                "Type": field_type,
                "Null": field.null,
                "Key": self.get_field_index_type(field),
                "Default": self.get_field_type_default(field),
                "Extra": extra,
                "Comment": field.name
            })
        return schema

    def get_indexes_schema(self):
        if self.model.Meta.database_type == DataBaseType.mysql:
            indexes = defaultdict(list)
            query = f"""
                SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{self.table_name}'
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """
            results = self.model.objects.fetch(query)

            for row in results:
                index_type = 'unique' if not row['NON_UNIQUE'] else 'index'
                indexes[index_type].append((row['INDEX_NAME'], row['COLUMN_NAME']))

            return {k: self._group_indexes(v) for k, v in indexes.items()}
        elif self.model.Meta.database_type == DataBaseType.sqlite:
            indexes = defaultdict(list)
            query = f"""
                SELECT name AS INDEX_NAME, sql
                FROM sqlite_master
                WHERE type = 'index' AND tbl_name = '{self.table_name}'
            """
            results = self.model.objects.fetch(query)

            for row in results:
                index_name = row['INDEX_NAME']
                sql = row['sql']
                columns = re.findall(r'\((.*?)\)', sql)[0].split(',')
                columns = [col.strip() for col in columns]
                index_type = 'unique' if 'UNIQUE' in sql.upper() else 'index'
                for column in columns:
                    indexes[index_type].append((index_name, column))

            return {k: self._group_indexes(v) for k, v in indexes.items()}
        else:
            raise ValueError(f"不支持该数据库类型: {self.model.database_type}")

    @staticmethod
    def _group_indexes(index_data):
        grouped = defaultdict(list)
        for index_name, column_name in index_data:
            grouped[index_name].append(column_name)
        return {k: v for k, v in grouped.items() if len(v) > 1}

    def compare_schemas(self) -> Dict[str, Any]:
        table_schema = self.get_table_schema()
        model_schema = self.get_model_schema()

        differences = {
            "added_fields": [],
            "removed_fields": [],
            "modified_fields": [],
            'modify_indexes': self.get_indexes_schema()
        }

        table_fields = {field["Field"]: field for field in table_schema}
        model_fields = {field["Field"]: field for field in model_schema}

        for field_name, model_field in model_fields.items():
            if field_name not in table_fields:
                differences["added_fields"].append(model_field)
            elif model_field != table_fields[field_name]:
                differences["modified_fields"].append({
                    "field_name": field_name,
                    "table_definition": table_fields[field_name],
                    "model_definition": model_field,
                })

        for field_name in table_fields:
            if field_name not in model_fields:
                differences["removed_fields"].append(table_fields[field_name])

        return differences
