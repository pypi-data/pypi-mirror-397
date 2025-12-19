import importlib
from typing import Dict, Any

from AioSpider import settings
from AioSpider.objects import DataBaseType, ConnectionData

DATABASE_TYPE_MAPPING = {
    'Sqlite': DataBaseType.sqlite,
    'Mysql': DataBaseType.mysql,
    'Mariadb': DataBaseType.mariadb,
    'Postgresql': DataBaseType.postgresql,
    'Sqlserver': DataBaseType.sqlserver,
    'Oracle': DataBaseType.oracle,
    'Mongodb': DataBaseType.mongodb,
    'Redis': DataBaseType.redis,
    'Csv': DataBaseType.csv,
    "File": DataBaseType.file
}


def extract_db_config(config: Any) -> Dict[DataBaseType, ConnectionData]:
    """提取数据库配置"""
    return {
        DATABASE_TYPE_MAPPING[k]: getattr(config, k, None)
        for k in DATABASE_TYPE_MAPPING
        if getattr(config, k, None) and getattr(getattr(config, k), 'enabled', False)
    }


def get_config():
    default_sts = extract_db_config(getattr(settings, 'DataBaseConfig'))

    try:
        sts = importlib.import_module('settings')
    except ImportError:
        print('当前项目未找到 settings.py 配置文件')
        return default_sts

    if hasattr(sts, 'DataBaseConfig'):
        default_sts.update(extract_db_config(getattr(sts, 'DataBaseConfig')))

    return default_sts


class Configuration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    @classmethod
    def get_db_config(cls, db_type: DataBaseType, db: str) -> ConnectionData:
        return cls().config[db_type][db]

    def _load_config(self):
        config = get_config()
        self.config =  {
            db_type: {cfg.alias: cfg for cfg in getattr(conf, 'connect', [])}
            for db_type, conf in config.items()
            if db_type in config
        }
