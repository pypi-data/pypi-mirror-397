from abc import ABC, abstractmethod
from .converst_value import convert_value, replace_null_from_string

__all__ = ['F', 'Q']


class Field(ABC):
    @abstractmethod
    def get_sql_and_params(self, placeholder="%s"):
        pass


class F(Field):
    def __init__(self, field):
        self.field = field
        self.connector = None
        self.right = None

    def __add__(self, other):
        return self._combine(other, '+')

    def __sub__(self, other):
        return self._combine(other, '-')

    def __mul__(self, other):
        return self._combine(other, '*')

    def __truediv__(self, other):
        return self._combine(other, '/')

    def __gt__(self, other):
        return self._combine(other, '>')

    def __ge__(self, other):
        return self._combine(other, '>=')

    def __lt__(self, other):
        return self._combine(other, '<')

    def __le__(self, other):
        return self._combine(other, '<=')

    def __eq__(self, other):
        return self._combine(other, '==')

    def _combine(self, other, connector):
        self.right = other
        self.connector = connector
        return self
    
    def get_sql_and_params(self, placeholder="%s"):
        sql_parts = f"`{self.field}` {self.connector} {placeholder}"
        params = (self.right, )
        return sql_parts, [convert_value(i) for i in params]


class Q(Field):
    def __init__(self, **kwargs):
        self.children = list(kwargs.items())
        self.connector = 'AND'
        self.negated = False

    def __or__(self, other):
        return self._combine(other, 'OR')

    def __and__(self, other):
        return self._combine(other, 'AND')

    def __invert__(self):
        q = Q()
        q.negated = not self.negated
        q.children = [self]
        return q

    def _combine(self, other, connector):
        if not isinstance(other, Q):
            raise TypeError(f"{other!r} 不是 Q 对象")
        q = Q()
        q.connector = connector
        q.children = [self, other]
        return q

    def _format_condition(self, key, value, placeholder):
        if '__' in key:
            field, operator = key.rsplit('__', 1)
            operators = {
                'gt': ('>', value),
                'lt': ('<', value),
                'gte': ('>=', value),
                'lte': ('<=', value),
                'contains': ('LIKE', f"%{value}%"),
                'isnull': (f"IS {'NULL' if value else 'NOT NULL'}", None),
                'startswith': ('LIKE', f"{value}%"),
                'endswith': ('LIKE', f"%{value}"),
                'ne': ('!=', value),
            }
            if operator in operators:
                op, val = operators[operator]
                return (f"`{field}` {op} {placeholder}", val) if val is not None else  (f"`{field}` {op}", val)
            if operator == 'in':
                return (
                    f"`{field}` {operator} {replace_null_from_string(str(tuple(value)))}", None
                )
        return f"`{key}` = {placeholder}", value

    def get_sql_and_params(self, placeholder="%s"):
        sql_parts = []
        params = []
        for child in self.children:
            if isinstance(child, Q):
                child_sql, child_params = child.get_sql_and_params(placeholder)
                sql_parts.append(f"({child_sql})")
                params.extend(child_params)
            else:
                key, value = child
                sql, param = self._format_condition(key, value, placeholder)
                sql_parts.append(sql)
                if param is not None:
                    params.extend(param if isinstance(param, (list, tuple)) else [param])
        
        joined = f" {self.connector} ".join(sql_parts)
        if self.negated:
            joined = f"NOT ({joined})"

        return joined, [convert_value(i) for i in params]
