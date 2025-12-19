from typing import Union

from AioSpider.objects import DataFilterMethod
from AioSpider.exceptions import BloomFilterException
from AioSpider.filter import AutoBloomFilter, DqueueFilter


class DataFilter:

    def __init__(self, enabled, method, capacity, max_capacity, error_rate):
        self.bloom = {}
        self.enabled = enabled
        self.method = method
        self.capacity = capacity
        self.max_capacity = max_capacity
        self.error_rate = error_rate

    def add_table_to_bloom(self, table: str):
        if self.method == DataFilterMethod.dqset:
            self.bloom[table] = DqueueFilter(
                capacity=self.capacity, max_capacity=self.max_capacity
            )
        elif self.method == DataFilterMethod.bloom:
            self.bloom[table] = AutoBloomFilter(
                capacity=self.capacity, max_capacity=self.max_capacity, error_rate=self.error_rate
            )
        else:
            raise BloomFilterException(f'无效的数据过滤方法，method: {self.method}')

    def contains(self, table: str, items: Union[str, list]):
        
        # 判断是否开启数据过滤
        if not self.enabled:
            return False

        if table not in self.bloom:
            self.add_table_to_bloom(table)
        
        # 判断数据是否存在
        if items in self.bloom[table]:
            return True
            
        self.bloom[table].add(items)
        
        return False
