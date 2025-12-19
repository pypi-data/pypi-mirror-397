import time as t
from datetime import datetime, date, time
from typing import Optional, Union, Callable

from attr import define, field

from AioSpider.orm.converters import (
    str_to_date,
    datetime_to_date,
    timestamp_to_date,
    str_to_time,
    datetime_to_time,
    timestamp_to_time,
    str_to_timestamp,
    date_to_timestamp,
    datetime_to_timestamp,
    str_to_datetime,
    date_to_datetime,
    time_to_datetime,
    timestamp_to_datetime,
)
from AioSpider.orm.validators import (
    optional, 
    instance_of, 
    and_validator, 
    is_non_negative,
    or_validator,
    magnitude,
    eq
)

from .field import Field, on_setattr

__all__ = [
    'StampField', 'DateField', 'DateTimeField', 'TimeField'
]


@define(kw_only=True, hash=True, slots=True, str=True, repr=True, eq=True, order=True)
class StampField(Field):
    """
    时间戳字段类，继承自Field类。用于表示和处理时间戳数据。

    属性:
        value (Optional[int]): 时间戳值，默认为None
        auto_now (bool): 是否在创建时自动添加时间戳，默认为False
        auto_add (bool): 是否在更新时自动更新时间戳，默认为False
    """
    value: Optional[int] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(and_validator(instance_of(int), is_non_negative())),
        on_setattr=on_setattr,
    )
    default: Union[None, int, Callable] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(int))
    )
    max_length: int = field(
        default=13, repr=True, order=True, eq=True, kw_only=True,
        validator=and_validator(instance_of(int), is_non_negative())
    )
    auto_now: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    auto_add: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_date: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_datetime: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        """初始化默认值。"""
        if not self.null and self.default is None:
            self.default = 0
        if self.auto_add or self.auto_now:
            self._required_default_to_db = False

    def _init_validators(self) -> list:
        validators = super()._init_validators()
        if self.null:
            validators.append(optional(or_validator(eq(0), magnitude(10), magnitude(13))))
        else:
            validators.append(or_validator(eq(0), magnitude(10), magnitude(13)))
        return validators
    
    def _init_converters(self) -> list:

        converters = super()._init_converters()

        if self.allow_string:
            converters.append(str_to_timestamp())

        if self.allow_date:
            converters.append(date_to_timestamp())
        
        if self.allow_datetime:
            converters.append(datetime_to_timestamp())

        return converters

    def _set_value(self, value: int) -> int:
        if self.auto_now or self.auto_add:
            return int(t.time())
        return value

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "TIMESTAMP"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "TIMESTAMP" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class DateField(Field):
    """
    日期字段类，用于处理和验证日期类型的数据。

    属性:
        value (Optional[date]): 字段的值，默认为None
    """

    value: Optional[date] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(date)), on_setattr=on_setattr,
    )
    default: Union[None, date, Callable] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(date))
    )
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_datetime: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_timestamp: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        """初始化默认值。"""
        if not self.null and self.default is None:
            self.default = datetime.now().date()

    def _init_converters(self) -> list:

        converters = super()._init_converters()

        if self.allow_string:
            converters.append(str_to_date())

        if self.allow_datetime:
            converters.append(datetime_to_date())
        
        if self.allow_timestamp:
            converters.append(timestamp_to_date())

        return converters

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "DATE"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "DATE" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class TimeField(Field):
    value: Optional[time] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(time))
    )
    default: Union[None, time, Callable] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(time))
    )
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_datetime: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_timestamp: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        """初始化默认值。"""
        if not self.null and self.default is None:
            self.default = datetime.now().time()

    def _init_converters(self) -> list:

        converters = super()._init_converters()

        if self.allow_string:
            converters.append(str_to_time())

        if self.allow_datetime:
            converters.append(datetime_to_time())
        
        if self.allow_timestamp:
            converters.append(timestamp_to_time())

        return converters

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "TIME"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "TIME" + (" PRIMARY KEY" if self.primary else "")


@define(kw_only=True, slots=True, str=True, repr=True, auto_exc=True)
class DateTimeField(Field):
    value: Optional[datetime] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        validator=optional(instance_of(datetime)), on_setattr=on_setattr,
    )
    default: Union[None, datetime, Callable] = field(
        default=None, repr=True, order=True, eq=True, kw_only=True,
        converter=lambda x: x() if callable(x) else x,
        validator=optional(instance_of(datetime))
    )
    auto_now: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    auto_add: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_string: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_date: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_time: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))
    allow_timestamp: bool = field(default=False, repr=True, kw_only=True, validator=instance_of(bool))

    def _init_default(self) -> None:
        """初始化默认值。"""
        if not self.null and self.default is None:
            self.default = datetime.now()
        if self.auto_add or self.auto_now:
            self._required_default_to_db = False

    def _init_converters(self) -> list:

        converters = super()._init_converters()

        if self.allow_string:
            converters.append(str_to_datetime())
        
        if self.allow_date:
            converters.append(date_to_datetime())
        
        if self.allow_time:
            converters.append(time_to_datetime())
        
        if self.allow_timestamp:
            converters.append(timestamp_to_datetime())

        return converters

    def _set_value(self, value: datetime) -> datetime:
        if self.auto_now or self.auto_add:
            return datetime.now()
        return value

    def _get_mysql_type(self):
        """
        获取MySQL数据类型。
        """
        return "DATETIME"

    def _get_sqlite_type(self):
        """
        获取SQLite数据类型。
        """
        return "DATETIME" + (" PRIMARY KEY" if self.primary else "")
