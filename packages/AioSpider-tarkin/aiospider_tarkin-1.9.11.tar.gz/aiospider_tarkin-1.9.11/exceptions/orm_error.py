from typing import Any, Optional, Union
from . import AioException


class ORMException(AioException):
    """ORM系统的基础异常类"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FieldException(ORMException):
    """字段相关错误的基础异常类"""

    def __init__(self, message: Optional[str] = None):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ValidationError(FieldException):
    """验证错误时引发的异常"""

    def __init__(self, validator_name: str, message: Optional[str] = None):
        self.validator_name = validator_name
        super().__init__(message or f"验证器 {validator_name} 验证失败")

    def __str__(self):
        return f"{self.validator_name} 验证失败，{self.message}"


class FieldValueValidatorError(ValidationError):
    """字段值无效时引发的异常"""

    def __init__(self, field_name: str, value: Any, rule: str, validator_name: str):
        message = f"{field_name} 字段值校验失败，{value!r} 不满足 {rule!r} 规则"
        super().__init__(validator_name, message)


class FieldTypeValidatorError(ValidationError):
    """字段类型不正确时引发的异常"""

    def __init__(self, field_name: str, value: Any, expected_type: Union[str, tuple], validator_name: str):
        if isinstance(expected_type, str):
            expected_type_names = expected_type.__name__
        else:
            expected_type_names = '、'.join([i.__name__ for i in expected_type])
        message = f"{field_name} 字段校验值必须是 {expected_type_names!r} 类型（值：{value}，当前类型：{type(value).__name__!r}）"
        super().__init__(validator_name, message)


class ConverterError(FieldException):
    """转换错误时引发的异常"""

    def __init__(self, field_name: str, value: Any, message: Optional[str] = None):
        self.field_name = field_name
        super().__init__(message or f"{value!r} 该值无法正确转换")

    def __str__(self):
        return f"{self.field_name} 字段转换失败，错误信息：{self.message}"


class DatabaseError(ORMException):
    """数据库操作相关异常"""

    def __init__(self, operation: str, details: str):
        super().__init__(f"数据库操作 '{operation}' 失败: {details}")


class TableBuilderError(ORMException):
    """建表构建相关异常"""
    pass


class QueryBuilderError(ORMException):
    """查询构建相关异常"""
    pass


class ModelError(ORMException):
    """模型相关异常"""
    pass


class AdapterError(ORMException):
    """数据库适配器相关异常"""
    pass
