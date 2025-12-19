__all__ = ['Join']


class Join:
    def __init__(self, table, condition, join_type='INNER'):
        self.table = table
        self.condition = condition
        self.join_type = join_type

    def __str__(self):
        return f"{self.join_type} JOIN {self.table} ON {self.condition}"
    
    def is_necessary(self):
        return self.condition.is_valid()
