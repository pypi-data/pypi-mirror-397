from typing import Optional, Union, List, Dict, Type, TypedDict, Any, Callable
import json

from attr import define, field

from AioSpider.orm.validators import (
    optional,
    instance_of,
    and_validator,
    is_non_negative,
    le,
    iterable_element_of
)
from .field import Field, on_setattr
from .string_field import CharField

__all__ = [
    'TextField', 'MediumTextField', 'LongTextField', 'ListField', 'JSONField'
]


class JSONFieldStructure(TypedDict, total=False):
    value: Any
    default: Any
    fields: Dict[str, Field]


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class TextField(CharField):
    max_length: int = field(
        default=65535, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(65535))
    )
    _required_default_to_db: bool = field(default=False, validator=instance_of(bool))

    def _get_mysql_type(self) -> str:
        """
        获取MySQL数据库对应的字段类型。
        """
        if self.max_length <= 55535:
            return "TEXT"
        elif self.max_length <= 16777215:
            return "MEDIUMTEXT"
        elif self.max_length <= 4294967295:
            return "LONGTEXT"
        else:
            raise ValueError(f"max_length 不允许超过 4294967295")
    
    def _get_sqlite_type(self) -> str:
        """
        获取SQLite数据库对应的字段类型。
        """
        return "TEXT"


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class MediumTextField(TextField):
    max_length: int = field(
        default=16777215, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(16777215))
    )


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class LongTextField(TextField):
    """
    长文本字段类，用于处理和验证长文本数据。

    属性:
        max_length (int): 文本的最大长度，默认为4294967295 (2^32 - 1)
    """
    max_length: int = field(
        default=4294967295, repr=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative(), le(4294967295))
    )


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class ListField(Field):
    """
    列表字段类，用于处理和验证列表类型的数据。

    属性:
        value (Optional[List]): 字段的值，默认为None
        default (Optional[List]): 默认值，默认为None
        item_type (Optional[Type]): 列表元素的类型，默认为None
        join (str): 用于连接列表元素的字符串，默认为'、'
        max_length (Optional[int]): 列表的最大长度，默认为None
        min_length (Optional[int]): 列表的最小长度，默认为None
    """
    value: Optional[List] = field(
        default=None, repr=True, kw_only=True, validator=optional(instance_of(list)), on_setattr=on_setattr
    )
    default: Union[None, List, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(list))
    )
    item_type: Optional[Type] = field(default=str, repr=True, kw_only=True)
    join: str = field(default='、', repr=True, kw_only=True, validator=instance_of(str))

    def _init_default(self):
        """初始化默认值。如果字段不允许为空且默认值为None，则设置默认值为空列表。"""
        if not self.null and self.default is None:
            self.default = []

    def _init_validators(self):
        validators = super()._init_validators()
        if self.item_type:
            validators += (iterable_element_of(self.item_type), )
        return validators

    def to_string(self):
        return self.join.join(map(str, self.value or []))


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class JSONField(Field):
    """
    JSON字段类，支持使用其他Field类型定义嵌套字段。

    属性:
        value (Optional[Union[List[Dict], Dict]]): 字段的值，默认为None
        default (Optional[Union[List[Dict], Dict]]): 默认值，默认为None
        fields (Dict[str, Field]): 用于定义JSON中特定字段的Field实例
    """
    value: JSONFieldStructure = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(dict, list))
    )
    default: Union[None, List[Dict], Dict, Callable] = field(
        default=None, repr=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(dict, list))
    )
    fields: Dict[str, Field] = field(factory=dict, repr=True, kw_only=True)

    def _init_default(self):
        if not self.null and self.default is None:
            self.default = {}

    def _set_value(self, value: Union[List[Dict], Dict]) -> Union[List[Dict], Dict]:
        """设置字段值，并对每个定义的字段进行验证和转换。"""

        if isinstance(value, dict):
            self._process_dict(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    self._process_dict(item)
        return value

    def _process_dict(self, data: Dict):
        for field_name, field_instance in self.fields.items():
            if field_name in data:
                field_instance.value = data[field_name]

    def to_string(self) -> str:
        """将字段值转换为字符串表示。"""
        return json.dumps(self.value, ensure_ascii=False)

    def from_string(self, value: str) -> None:
        """从字符串表示解析字段值。"""
        self.value = json.loads(value)
