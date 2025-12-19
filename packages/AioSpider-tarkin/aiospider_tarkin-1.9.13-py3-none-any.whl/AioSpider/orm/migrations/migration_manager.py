from typing import List, Optional, Dict, Any

from .base_migration import Migration
from .column_migrations import (
    AddColumnMigration,
    RemoveColumnMigration,
    ChangeColumnTypeMigration,
    ChangeColumnPrecisionMigration,
    ChangeDefaultValueMigration,
    ChangeNullableMigration,
    ChangeColumnLengthMigration,
    ChangeAutoIncrementAndSignedMigration,
    ChangeTimestampMigration,
)
from .key_migrations import (
    AddPrimaryKeyMigration,
    RemovePrimaryKeyMigration,
    AddUniqueKeyMigration,
    RemoveUniqueKeyMigration,
    AddIndexMigration,
    RemoveIndexMigration,
    AddCompositeUniqueKeyMigration,
    RemoveCompositeUniqueKeyMigration,
    AddCompositeIndexMigration,
    RemoveCompositeIndexMigration
)
from .schema_comparator import SchemaComparator
from ..fields import StampField, DateTimeField

__all__ = ['MigrationManager']


class MigrationManager:

    def __init__(self, model):
        self.model = model
        self.db_adapter = self.model.objects.db_adapter
        self.table_name = self.model.table_name
        self.migrations: List[Migration] = []

    @classmethod
    def from_model(cls, model):
        return cls(model)

    def apply_schema_changes(self):

        if self.model.Meta.read_only:
            return

        comparator = SchemaComparator(self.model)
        schema_differences = comparator.compare_schemas()
        self._process_field_changes(schema_differences)
        self._process_index_changes(schema_differences['modify_indexes'])
        print(self.migrations)
        # self.apply_migrations()

    def add_migration(self, migration: Migration):
        self.migrations.append(migration)

    def apply_migrations(self):
        for migration in self.migrations:
            migration.apply(self.db_adapter)
            print(f'{migration.name} 迁移成功')

    def rollback_migrations(self, migrations: Optional[List[Migration]] = None):
        migrations = migrations or self.migrations
        for migration in reversed(migrations):
            migration.rollback(self.db_adapter)
            self._remove_migration_record(migration)

    def _remove_migration_record(self, migration: Migration):
        sql = "DELETE FROM migrations WHERE name = %s;"
        self.db_adapter.execute(sql, (migration.name,))

    def _process_field_changes(self, differences: Dict[str, Any]):
        for added_field in differences["added_fields"]:
            self.add_migration(
                AddColumnMigration(
                    self.table_name,
                    added_field['Field'],
                    added_field['Type'],
                    added_field['Comment']
                )
            )

        for removed_field in differences["removed_fields"]:
            self.add_migration(
                RemoveColumnMigration(
                    self.table_name,
                    removed_field['Field']
                )
            )

        for modified_field in differences["modified_fields"]:
            self._process_modified_field(modified_field)

    def _process_modified_field(self, modified_field: Dict[str, Any]):
        table_def = modified_field['table_definition']
        model_def = modified_field['model_definition']
        field_name = modified_field['field_name']

        self._process_type_changes(field_name, table_def, model_def)
        self._process_default_value_change(field_name, table_def, model_def)
        self._process_nullable_change(field_name, table_def, model_def)
        self._process_auto_increment_and_signed_change(field_name, table_def, model_def)
        self._process_timestamp_change(field_name, table_def, model_def)
        self._process_key_change(field_name, table_def, model_def)

    def _process_type_changes(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if table_def['Type'] != model_def['Type']:
            table_base_type = table_def['Type'].split('(')[0].lower()
            model_base_type = model_def['Type'].split('(')[0].lower()

            if table_base_type != model_base_type:
                self.add_migration(
                    ChangeColumnTypeMigration(
                        self.table_name,
                        field_name,
                        model_def['Type'],
                        model_def['Comment']
                    )
                )
            else:
                self._process_type_modifiers(field_name, table_def, model_def)

    def _process_type_modifiers(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if '(' in table_def['Type'] and '(' in model_def['Type']:
            table_modifiers = table_def['Type'].split('(')[1].split(')')[0]
            model_modifiers = model_def['Type'].split('(')[1].split(')')[0]
            if table_modifiers != model_modifiers:
                if ',' in table_modifiers and ',' in model_modifiers:
                    self._process_precision_change(
                        field_name,
                        table_modifiers,
                        model_modifiers,
                        model_def['Type'].split('(')[0],
                        model_def['Comment']
                    )
                else:
                    self._process_length_change(
                        field_name,
                        model_def['Type'].split('(')[0],
                        int(model_modifiers),
                        model_def['Comment']
                    )
        elif '(' in table_def['Type'] or '(' in model_def['Type']:
            self.add_migration(
                ChangeColumnTypeMigration(
                    self.table_name,
                    field_name,
                    model_def['Type'],
                    model_def['Comment']
                )
            )

    def _process_precision_change(
            self,
            field_name: str,
            table_modifiers: str,
            model_modifiers: str,
            field_type: str,
            comment: str
    ):
        table_length, table_precision = map(int, table_modifiers.split(','))
        model_length, model_precision = map(int, model_modifiers.split(','))
        if table_length != model_length:
            self.add_migration(
                ChangeColumnLengthMigration(
                    self.table_name,
                    field_name,
                    field_type,
                    model_length,
                    comment
                )
            )
        if table_precision != model_precision:
            self.add_migration(
                ChangeColumnPrecisionMigration(
                    self.table_name,
                    field_name,
                    field_type,
                    model_precision,
                    comment
                )
            )

    def _process_length_change(
            self,
            field_name: str,
            field_type: str,
            new_length: int,
            comment: str
    ):
        self.add_migration(
            ChangeColumnLengthMigration(
                self.table_name, field_name, field_type, new_length, comment
            )
        )

    def _process_default_value_change(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if table_def['Default'] != model_def['Default']:
            self.add_migration(
                ChangeDefaultValueMigration(
                    self.table_name, field_name, model_def['Default'], model_def['Comment']
                )
            )

    def _process_nullable_change(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if table_def['Null'] != model_def['Null']:
            self.add_migration(
                ChangeNullableMigration(
                    self.table_name, field_name, model_def['Type'], model_def['Null'], 
                    model_def['Default'], model_def['Comment']
                )
            )

    def _process_auto_increment_and_signed_change(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        table_auto_increment = 'AUTO_INCREMENT' in table_def['Extra']
        model_auto_increment = 'AUTO_INCREMENT' in model_def['Extra']
        table_unsigned = 'UNSIGNED' in table_def['Type']
        model_unsigned = 'UNSIGNED' in model_def['Type']
        
        if table_auto_increment != model_auto_increment or table_unsigned != model_unsigned:
            self.add_migration(
                ChangeAutoIncrementAndSignedMigration(
                    self.table_name, 
                    field_name, 
                    model_auto_increment, 
                    model_unsigned, 
                    model_def['Comment']
                )
            )

    def _process_timestamp_change(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if isinstance(self.model.fields[field_name], (StampField, DateTimeField)):
            table_auto_update = 'ON UPDATE CURRENT_TIMESTAMP' in table_def['Extra']
            model_auto_update = 'ON UPDATE CURRENT_TIMESTAMP' in model_def['Extra']
            if table_auto_update != model_auto_update:
                self.add_migration(
                    ChangeTimestampMigration(
                        self.table_name, field_name, table_def['Type'],table_def['Null'],
                        model_auto_update, model_def['Comment']
                    )
                )

    def _process_key_change(self, field_name: str, table_def: Dict[str, Any], model_def: Dict[str, Any]):
        if table_def['Key'] != model_def['Key']:
            self._remove_old_key(field_name, table_def['Key'])
            self._add_new_key(field_name, model_def['Key'])

    def _remove_old_key(self, field_name: str, old_key: str):
        if old_key == 'PRI':
            self.add_migration(RemovePrimaryKeyMigration(self.table_name, field_name))
        elif old_key == 'UNI':
            self.add_migration(RemoveUniqueKeyMigration(self.table_name, field_name))
        elif old_key == 'MUL' and not any(field_name in idx for idx in self.model.Meta.composite_indexes or []):
            self.add_migration(RemoveIndexMigration(self.table_name, field_name))

    def _add_new_key(self, field_name: str, new_key: str):
        if new_key == 'PRI':
            self.add_migration(AddPrimaryKeyMigration(self.table_name, field_name))
        elif new_key == 'UNI':
            self.add_migration(AddUniqueKeyMigration(self.table_name, field_name))
        elif new_key == 'MUL' and not any(field_name in idx for idx in self.model.Meta.composite_indexes or []):
            self.add_migration(AddIndexMigration(self.table_name, field_name))

    def _process_index_changes(self, current_indexes):
        self._process_composite_unique_changes(current_indexes)
        self._process_composite_index_changes(current_indexes)

    def _process_composite_unique_changes(self, current_indexes):
        table_composite_unique = {index_name: tuple(fields) for index_name, fields in current_indexes.get('unique', {}).items()}
        model_composite_unique = set(tuple(idx) for idx in self.model.Meta.composite_unique_indexes or [])

        for index_name, removed_unique in table_composite_unique.items():
            if removed_unique not in model_composite_unique:
                self.add_migration(
                    RemoveCompositeUniqueKeyMigration(self.table_name, list(removed_unique), index_name)
                )

        for added_unique in model_composite_unique - set(table_composite_unique.values()):
            self.add_migration(
                AddCompositeUniqueKeyMigration(self.table_name, list(added_unique))
            )

    def _process_composite_index_changes(self, current_indexes):
        table_composite_index = {index_name: tuple(fields) for index_name, fields in current_indexes.get('index', {}).items()}
        model_composite_index = set(tuple(idx) for idx in self.model.Meta.composite_indexes or [])

        for index_name, removed_index in table_composite_index.items():
            if removed_index not in model_composite_index:
                self.add_migration(
                    RemoveCompositeIndexMigration(self.table_name, list(removed_index), index_name)
                )

        for added_index in model_composite_index - set(table_composite_index.values()):
            self.add_migration(
                AddCompositeIndexMigration(self.table_name, list(added_index))
            )
