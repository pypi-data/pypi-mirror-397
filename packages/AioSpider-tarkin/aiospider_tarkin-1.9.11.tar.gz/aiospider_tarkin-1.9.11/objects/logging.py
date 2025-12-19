from enum import Enum

__all__ = [
    'LogLevel', 
    'TimeFormater', 
    'Attribute', 
    'Color', 
    'Style', 
    'Formater'
]


class LogLevel(Enum):
    """日志等级常量"""

    LEVEL1 = 5
    LEVEL2 = 10
    LEVEL3 = 20
    LEVEL4 = 30
    LEVEL5 = 40
    LEVEL6 = 50
    LEVEL7 = 60


class TimeFormater(Enum):
    """
    支持自定义格式
        +------------------------+---------+----------------------------------------+
        |                        | Token   | Output                                 |
        +========================+=========+========================================+
        | Year                   | YYYY    | 2000, 2001, 2002 ... 2012, 2013        |
        |                        +---------+----------------------------------------+
        |                        | YY      | 00, 01, 02 ... 11, 12                  |
        +------------------------+---------+----------------------------------------+
        | Quarter                | Q       | 1 2 3 4                                |
        +------------------------+---------+----------------------------------------+
        | Month                  | MMMM    | January, February, March ...           |
        |                        +---------+----------------------------------------+
        |                        | MMM     | Jan, Feb, Mar ...                      |
        |                        +---------+----------------------------------------+
        |                        | MM      | 01, 02, 03 ... 11, 12                  |
        |                        +---------+----------------------------------------+
        |                        | M       | 1, 2, 3 ... 11, 12                     |
        +------------------------+---------+----------------------------------------+
        | Day of Year            | DDDD    | 001, 002, 003 ... 364, 365             |
        |                        +---------+----------------------------------------+
        |                        | DDD     | 1, 2, 3 ... 364, 365                   |
        +------------------------+---------+----------------------------------------+
        | Day of Month           | DD      | 01, 02, 03 ... 30, 31                  |
        |                        +---------+----------------------------------------+
        |                        | D       | 1, 2, 3 ... 30, 31                     |
        +------------------------+---------+----------------------------------------+
        | Day of Week            | dddd    | Monday, Tuesday, Wednesday ...         |
        |                        +---------+----------------------------------------+
        |                        | ddd     | Mon, Tue, Wed ...                      |
        |                        +---------+----------------------------------------+
        |                        | d       | 0, 1, 2 ... 6                          |
        +------------------------+---------+----------------------------------------+
        | Days of ISO Week       | E       | 1, 2, 3 ... 7                          |
        +------------------------+---------+----------------------------------------+
        | Hour                   | HH      | 00, 01, 02 ... 23, 24                  |
        |                        +---------+----------------------------------------+
        |                        | H       | 0, 1, 2 ... 23, 24                     |
        |                        +---------+----------------------------------------+
        |                        | hh      | 01, 02, 03 ... 11, 12                  |
        |                        +---------+----------------------------------------+
        |                        | h       | 1, 2, 3 ... 11, 12                     |
        +------------------------+---------+----------------------------------------+
        | Minute                 | mm      | 00, 01, 02 ... 58, 59                  |
        |                        +---------+----------------------------------------+
        |                        | m       | 0, 1, 2 ... 58, 59                     |
        +------------------------+---------+----------------------------------------+
        | Second                 | ss      | 00, 01, 02 ... 58, 59                  |
        |                        +---------+----------------------------------------+
        |                        | s       | 0, 1, 2 ... 58, 59                     |
        +------------------------+---------+----------------------------------------+
        | Fractional Second      | S       | 0 1 ... 8 9                            |
        |                        +---------+----------------------------------------+
        |                        | SS      | 00, 01, 02 ... 98, 99                  |
        |                        +---------+----------------------------------------+
        |                        | SSS     | 000 001 ... 998 999                    |
        |                        +---------+----------------------------------------+
        |                        | SSSS... | 000[0..] 001[0..] ... 998[0..] 999[0..]|
        |                        +---------+----------------------------------------+
        |                        | SSSSSS  | 000000 000001 ... 999998 999999        |
        +------------------------+---------+----------------------------------------+
        | AM / PM                | A       | AM, PM                                 |
        +------------------------+---------+----------------------------------------+
        | Timezone               | Z       | -07:00, -06:00 ... +06:00, +07:00      |
        |                        +---------+----------------------------------------+
        |                        | ZZ      | -0700, -0600 ... +0600, +0700          |
        |                        +---------+----------------------------------------+
        |                        | zz      | EST CST ... MST PST                    |
        +------------------------+---------+----------------------------------------+
        | Seconds timestamp      | X       | 1381685817, 1234567890.123             |
        +------------------------+---------+----------------------------------------+
        | Microseconds timestamp | x       | 1234567890123                          |
        +------------------------+---------+----------------------------------------+

    """

    A = 'YYYY-MM-DD HH:mm:ss.SSS'
    B = 'YYYY/MM/DD HH:mm:ss.SSS'
    C = 'YYYY-MM-DD HH:mm:ss'
    D = 'YYYY/MM/DD HH:mm:ss'


class Attribute(Enum):
    time = 'time'
    name = 'name'
    file = 'file'
    module = 'module'
    function = 'function'
    level = 'level'
    line = 'line'
    message = 'message'
    process = 'process'
    thread = 'thread'
    extra = 'extra'
    exception = 'exception'
    elapsed = 'elapsed'


class Color(Enum):
    """颜色常量"""

    black = 'black'
    blue = 'blue'
    cyan = 'cyan'
    green = 'green'
    magenta = 'magenta'
    red = 'red'
    white = 'white'
    yellow = 'yellow'


class Style(Enum):
    """样式常量"""

    bold = 'bold'
    dim = 'dim'
    normal = 'normal'
    italic = 'italic'
    underline = 'underline'
    strike = 'strike'
    reverse = 'reverse'
    blink = 'blink'
    hide = 'hide'


class Formater(Enum):
    """日志格式化常量"""

    A = [
        (Attribute.time, Color.cyan, Style.bold),
        (Attribute.level, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), Style.bold),
        (Attribute.module, Color.magenta, Style.bold), (Attribute.function, Color.magenta, Style.bold),
        (Attribute.line, Color.magenta, Style.bold),
        (Attribute.message, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), None)
    ]
    B = [
        (Attribute.process, Color.yellow, Style.bold), (Attribute.thread, Color.yellow, Style.bold),
        (Attribute.time, Color.cyan, Style.bold),
        (Color.cyan, Attribute.level, (Color.blue, Color.green, Color.yellow, Color.red), Style.bold),
        (Attribute.module, Color.magenta, Style.bold), (Attribute.function, Color.magenta, Style.bold),
        (Attribute.line, Color.magenta, Style.bold),
        (Color.cyan, Attribute.message, (Color.blue, Color.green, Color.yellow, Color.red), None)
    ]
    C = [
        (Attribute.time, Color.cyan, Style.bold),
        (Attribute.level, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), Style.bold),
        (Attribute.file, Color.yellow, Style.bold), (Attribute.line, Color.magenta, Style.bold),
        (Attribute.message, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), None)
    ]
    D = [
        (Attribute.name, Color.green, Style.bold), (Attribute.elapsed, Color.yellow, Style.bold),
        (Attribute.time, Color.cyan, Style.bold),
        (Attribute.level, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), Style.bold),
        (Attribute.file, Color.yellow, Style.bold), (Attribute.line, Color.magenta, Style.bold),
        (Attribute.message, (Color.cyan, Color.blue, Color.green, Color.yellow, Color.red), None),
        (Attribute.exception, Color.red, Style.bold),
        (Attribute.extra, Color.cyan, None)
    ]

