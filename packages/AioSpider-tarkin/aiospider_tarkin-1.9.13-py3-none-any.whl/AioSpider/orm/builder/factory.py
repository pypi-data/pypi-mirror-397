from .table_builder import *
from .insert_builder import *
from .delete_builder import *
from .update_builder import *
from .query_builder import *

__all__ = ['BuilderFactory']


class BuilderFactory:

    def __init__(self, model):
        self.model = model

    def _get_builder(self, builder_class):
        return builder_class(self.model)

    def get_table_builder(self):
        return self._get_builder(TableBuilderFactory)

    def get_insert_builder(self):
        return self._get_builder(InsertBuilderFactory)

    def get_delete_builder(self):
        return self._get_builder(DeleteBuilderFactory)

    def get_update_builder(self):
        return self._get_builder(UpdateBuilderFactory)

    def get_query_builder(self):
        return self._get_builder(QueryBuilderFactory)