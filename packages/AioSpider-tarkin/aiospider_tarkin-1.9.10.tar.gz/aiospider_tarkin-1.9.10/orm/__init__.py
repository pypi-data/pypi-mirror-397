from .fields import (
    Field,
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
    LongBlobField
)
from .models import (
    Model,
    PdfFileModel,
    XlsxFileModel,
    ImageModel,
    ABCModel,
    SQLiteModel,
    MySQLModel,
    MongoModel,
    FileModel,
    CSVModel,
    RedisModel,
    NoticeModel,
    TableModel,
    TableStatisticsModel,
    TableFieldStatisticsModel,
    SpiderModel,
    TaskModel,
    TaskProgressModel,
    ProxyPoolModel,
    UsersModel,
    QuerySet,
    AsyncQuerySet
)
from .builder.aggregates import *
from .builder.joins import *

def close_database():
    import asyncio
    from AioSpider.orm.adapter.factory import AsyncDatabaseAdapterFactory, DatabaseAdapterFactory
    
    DatabaseAdapterFactory.close()
    asyncio.get_event_loop().run_until_complete(AsyncDatabaseAdapterFactory.close())
