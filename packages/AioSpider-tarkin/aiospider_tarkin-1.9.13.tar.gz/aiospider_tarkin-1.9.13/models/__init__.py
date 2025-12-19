__all__ = [
    'Model', 'SQLiteModel', 'CSVModel', 'MySQLModel', 'ImageModel', 'SpiderModel', 'FileModel',
    'ProxyPoolModel', 'TaskModel', 
    'PdfFileModel', 'XlsxFileModel', 'MongoModel', 'TablesModel', 'UsersModel', 'RedisModel'
]

from AioSpider.models.models import (
    Model, SQLiteModel, CSVModel, MySQLModel, FileModel, MongoModel, RedisModel
)
from .custom_model import (
    ImageModel, SpiderModel, ProxyPoolModel, TaskModel, PdfFileModel, XlsxFileModel, TablesModel, UsersModel
)
