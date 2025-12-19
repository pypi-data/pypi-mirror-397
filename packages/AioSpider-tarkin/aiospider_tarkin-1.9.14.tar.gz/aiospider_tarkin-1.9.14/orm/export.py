from .models import Model


class SQLExporter:
    def __init__(self, model: Model):
        self.model = model

    def export(self, file_path: str):
        sql_statements = []
        sql_statements.append(self._generate_create_table_sql())
        sql_statements.append(self._generate_insert_statements())

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_statements))

    def _generate_create_table_sql(self) -> str:
        field_definitions = [f"`{field.column}` {field.to_sql_type()}" for field in self.model.fields.values()]
        create_table_sql = f"CREATE TABLE `{self.model.Meta.table_name}` (\n"
        create_table_sql += ",\n".join(field_definitions)
        create_table_sql += "\n);"
        return create_table_sql

    def _generate_insert_statements(self) -> str:
        records = self.model.objects.all()
        insert_statements = []
        for record in records:
            values = [f"'{getattr(record, field.name)}'" for field in self.model.fields.values()]
            insert_sql = f"INSERT INTO `{self.model.Meta.table_name}` VALUES ({', '.join(values)});"
            insert_statements.append(insert_sql)
        return "\n".join(insert_statements)
