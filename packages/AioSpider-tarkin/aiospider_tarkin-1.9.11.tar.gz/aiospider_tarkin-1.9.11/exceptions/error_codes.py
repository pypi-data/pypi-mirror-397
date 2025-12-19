class SettingsConfigTags:

    AioSpiderPathMissing = 1000
    MiddlewareLoadingError = 1001
    LogLoadingError = 1002
    ModelLoadingError = 1003
    
    
class MiddlewareTags:
    
    RequestReturnError = 2000
    ResponseReturnError = 2001
    ExceptionReturnError = 2002
    MiddlewareTypeError = 2003


class RequestTags:
    
    InvalidRequestMethod = 3000
    InvalidRequestURL = 3001
    InvalidRequestConfig = 3002
    
    
class SqlTags:
    
    IndexToLong = 4000
    
    
class DataFilterTags:
    
    InvalidFilterMethod = 5000
    InvalidFilterErrorRate = 5001
    InvalidFilterCapacity = 5002
    InvalidFilterCapacityLimit = 5003
    
    
class SpiderTags:
    
    InvalidParams = 6000
    
    
class DatabaseTags:
    
    RedisDatabaseMissing = 7000
    RedisDatabaseMissingDefault = 7001
    MongoConnetError = 7002
    InvalidMongoConnetPort = 7003
    InvalidMongoConnetMaxsize = 7004
    InvalidMongoConnetMinsize = 7005
    InvalidMongoConnetSize = 7006
    InvalidMongoConnetTimeout = 7007
    MysqlConnetError = 7008
    SqlWhereError = 7009
    SqlHavingError = 7010
    SqlOrderError = 7011
    SqlFieldError = 7012
    SqlFieldTypeError = 7013
    LodingConfigError = 7014
    MissingEngineError = 7015
    DataReturnTypeError = 7016


class CmdComandTags:

    InvalidProxyComandArgs = 8000
    InvalidMakeComandArgs = 8001
    MissingMakeComandInFilePath = 8002
    MakeComandSqlError = 8003
    MakeComandSqlTableError = 8004
    MakeComandSqlFieldError = 8005
    InvalidCreateComandArgs = 8006
    CreateComandProjectName = 8007
    CreateComandSpiderName = 8008
    InvalidServerComandArgs = 8009
    ServerComandRedisError = 8010
    ServerComandInstall = 8011
    
    
class NoticeTags:
    
    StmpConnectError = 9000
    InvalidNoticePlatform = 9001


class StatusTags(
    SettingsConfigTags, MiddlewareTags, RequestTags, SqlTags, DataFilterTags, SpiderTags, DatabaseTags,
    CmdComandTags, NoticeTags
):
    UnSupportPlatform = 0


error_map = {
    StatusTags.UnSupportPlatform: '不支持该操作系统',

    StatusTags.AioSpiderPathMissing: '系统配置中AioSpiderPath参数未配置',
    StatusTags.MiddlewareLoadingError: '%s 中间件加载失败',
    StatusTags.LogLoadingError: '日志类型配置错误',
    StatusTags.ModelLoadingError: 'ORM 类型配置错误',

    StatusTags.RequestReturnError: '中间件返回值错误，中间件的process_request方法返回值必须为 Request/Response/None/False 对象',
    StatusTags.ResponseReturnError: '中间件返回值错误，中间件的process_response方法返回值必须为 Request/Response/None/False 对象',
    StatusTags.ExceptionReturnError: '中间件返回值错误，中间件的process_exception方法返回值必须为 Request/Response/None/False 对象',
    StatusTags.MiddlewareTypeError: '中间件类型错误',
    
    StatusTags.InvalidRequestMethod: '无效的请求方法，AioSpider框架不支持%s请求方法',
    StatusTags.InvalidRequestURL: "无效的 URL: %s",
    StatusTags.InvalidRequestConfig: "请求库配置不正确，请检查配置文件",

    StatusTags.IndexToLong: '指定的索引太长；最大最大长度为767字节, SQL: %s',
    
    StatusTags.InvalidFilterMethod: '无效的数据过滤方法，method: %s',
    StatusTags.InvalidFilterErrorRate: "布隆过滤器 error rate 必须再0和1之间",
    StatusTags.InvalidFilterCapacity: "布隆过滤器 Capacity 容量必须大于0",
    StatusTags.InvalidFilterCapacityLimit: "数据大小已经超出了布隆过滤器容量",
    
    StatusTags.InvalidParams: '无效的%s参数值',

    StatusTags.RedisDatabaseMissing: '%s 分布式爬虫未配置redis数据库',
    StatusTags.RedisDatabaseMissingDefault: '%s 分布式爬虫中redis未配置DEFAULT数据库',
    StatusTags.MongoConnetError: 'mongodb 数据库连接失败',
    StatusTags.InvalidMongoConnetPort: '无效的 mongodb port 连接参数，必须为int类型',
    StatusTags.InvalidMongoConnetMaxsize: '无效的 mongodb max_connect_size 连接参数，必须为int类型',
    StatusTags.InvalidMongoConnetMinsize: '无效的 mongodb min_connect_size 连接参数，必须为int类型',
    StatusTags.InvalidMongoConnetSize: '无效的 mongodb 连接参数，max_connect_size 必须比 min_connect_size 大',
    StatusTags.InvalidMongoConnetTimeout: '无效的 mongodb max_idle_time 连接，参数必须为int类型',
    StatusTags.MysqlConnetError: "'mysql 数据库连接失败",
    StatusTags.InvalidProxyComandArgs: '无效的 aioSpider test 命令参数[aioSpider -help 查看帮助]',
    StatusTags.InvalidMakeComandArgs: '无效的 aioSpider make 命令参数[aioSpider -help 查看帮助]',
    StatusTags.MissingMakeComandInFilePath: 'aioSpider make 命令未输入sql文件路径[aioSpider -help 查看帮助]',
    StatusTags.MakeComandSqlError: 'aioSpider make 输入的建表sql语句错误[aioSpider -help 查看帮助]',
    StatusTags.MakeComandSqlTableError: 'aioSpider make 输入的建表sql语句中未匹配到表名[aioSpider -help 查看帮助]',
    StatusTags.MakeComandSqlFieldError: 'aioSpider make 输入的建表sql语句中没有匹配到字段[aioSpider -help 查看帮助]',
    StatusTags.InvalidCreateComandArgs: '无效的aioSpider create 命令参数[aioSpider -help 查看帮助]',
    StatusTags.CreateComandProjectName: 'aioSpider create -p <name>, Do you forget inout project name?[aioSpider -help 查看帮助]',
    StatusTags.CreateComandSpiderName: 'aioSpider create -s <name>, Do you forget inout spider name?[aioSpider -help 查看帮助]',
    StatusTags.InvalidServerComandArgs: '无效的aioSpider server 命令参数参数[aioSpider -help 查看帮助]',
    StatusTags.ServerComandRedisError: '找不到 redis 服务器[aioSpider -help 查看帮助]',
    StatusTags.ServerComandInstall: 'AioServer 未安装，请执行 pip install AioServer-zly 进行安装',
    StatusTags.SqlWhereError: '构造sql语句时发现 where 参数类型错误，必须为 dict 类型',
    StatusTags.SqlHavingError: '构造sql语句时发现 having 参数类型错误，必须为 dict 类型',
    StatusTags.SqlOrderError: '构造sql语句时发现 order 参数类型错误，必须为 str、list 类型',
    StatusTags.SqlFieldError: '构造sql语句时发现 field 参数类型错误，必须为 str、list 类型',
    StatusTags.SqlFieldTypeError: '构造sql语句时发现字段类型错误',
    StatusTags.LodingConfigError: '没加载到数据库相关配置',
    StatusTags.MissingEngineError: '该模型未设置有数据库引擎',
    StatusTags.DataReturnTypeError: '数据处理返回类型错误，仅支持 Model | dict | iterable 类型',
    
    StatusTags.StmpConnectError: '邮箱服务器连接失败',
    StatusTags.InvalidNoticePlatform: '不支持%s通知预警平台',

}
