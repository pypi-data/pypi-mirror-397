from datetime import datetime, date, time
from enum import Enum


def convert_value(value):
    if value is None:
        return  None
    elif isinstance(value, (int, float, str, bytes, bool)):
        return value
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, time):
        return value.strftime('%H:%M:%S')
    elif isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, Enum):
        return value.value
    else:
        return str(value)


def replace_null_from_string(string: str):
    return string.replace('None', 'NULL')
