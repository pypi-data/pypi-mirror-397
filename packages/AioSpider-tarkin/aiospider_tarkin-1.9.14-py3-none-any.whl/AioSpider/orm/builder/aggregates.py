__all__ = [
    'Aggregate',
    'Count', 
    'Sum', 
    'Avg', 
    'Max', 
    'Min', 
    'Distinct', 
    'Std', 
    'Variance', 
    'GroupConcat', 
    'Length'
]


class Aggregate:
    def __init__(self, function, field):
        self.function = function
        self.field = field

    def __str__(self):
        if self.field != '*':
            if isinstance(self.field, Aggregate):
                return f"{self.function}({self.field})"
            else:
                return f"{self.function}(`{self.field}`)"
        else:
            return f"{self.function}({self.field})"


class Count(Aggregate):
    def __init__(self, field="*"):
        super().__init__("COUNT", field)


class Sum(Aggregate):
    def __init__(self, field):
        super().__init__("SUM", field)


class Avg(Aggregate):
    def __init__(self, field):
        super().__init__("AVG", field)


class Max(Aggregate):
    def __init__(self, field):
        super().__init__("MAX", field)


class Min(Aggregate):
    def __init__(self, field):
        super().__init__("MIN", field)


class Distinct(Aggregate):
    def __init__(self, field):
        super().__init__("DISTINCT", field)


class Std(Aggregate):
    def __init__(self, field):
        super().__init__("STD", field)


class Variance(Aggregate):
    def __init__(self, field):
        super().__init__("VARIANCE", field)


class Length(Aggregate):
    def __init__(self, field):
        super().__init__("LENGTH", field)


class GroupConcat(Aggregate):
    def __init__(self, field, separator=","):
        super().__init__("GROUP_CONCAT", field)
        self.separator = separator

    def __str__(self):
        if self.field != '*':
            return f"GROUP_CONCAT(`{self.field}` SEPARATOR '{self.separator}')"
        else:
            return f"GROUP_CONCAT({self.field} SEPARATOR '{self.separator}')"