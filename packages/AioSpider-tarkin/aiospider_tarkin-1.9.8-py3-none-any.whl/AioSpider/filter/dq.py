from AioSpider.exceptions import BloomFilterException


class DqueueFilter:

    def __init__(self, capacity, max_capacity=float('inf')):

        self.capacity = capacity
        self.max_capacity = max_capacity
        self._bloom = None
        self.y = 0
        self.count = 0

    @property
    def bloom(self):

        if self._bloom is None:
            self._bloom = [set()]

        if self.count // self.capacity != self.y:
            if self.count >= self.max_capacity:
                assert self.capacity >= self.count, BloomFilterException('数据大小已经超出了布隆过滤器容量')
            self._bloom.append(set())
            self.y += 1

        return self._bloom[self.y]

    def add(self, item):
        self.bloom.add(item)
        self.count += 1

    def add_many(self, items):
        for item in items:
            self.add(item)

    def __contains__(self, item):
        return any(item in st for st in self._bloom) if self._bloom is not None else False

    def __len__(self):
        return self.count