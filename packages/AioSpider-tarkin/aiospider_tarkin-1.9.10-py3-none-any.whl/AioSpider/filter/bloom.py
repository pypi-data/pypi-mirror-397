import math
import hashlib
import bitarray
from io import BytesIO
from struct import unpack, pack

import redis
from AioSpider.exceptions import BloomFilterException


def range_fn(*args):
    return range(*args)


def is_string_io(instance):
    return isinstance(instance, BytesIO)


def make_hash_funcs(num_slices, num_bits):

    def _make_hash_funcs(key):
        key = key.encode('utf-8') if isinstance(key, str) else str(key).encode('utf-8')
        i = 0
        for salt in salts:
            h = salt.copy()
            h.update(key)
            for uint in unpack(fmt, h.digest()):
                yield uint % num_bits
                i += 1
                if i >= num_slices:
                    return

    fmt_code, chunk_size = ('Q', 8) if num_bits >= (1 << 31) else ('I', 4) if num_bits >= (1 << 15) else ('H', 2)
    total_hash_bits = 8 * num_slices * chunk_size
    hashfn = hashlib.sha512 if total_hash_bits > 384 else hashlib.sha384 if total_hash_bits > 256 else hashlib.sha256 if total_hash_bits > 160 else hashlib.sha1 if total_hash_bits > 128 else hashlib.md5
    fmt = fmt_code * (hashfn().digest_size // chunk_size)
    num_salts = (num_slices + len(fmt) - 1) // len(fmt)
    salts = tuple(hashfn(hashfn(pack('I', i)).digest()) for i in range_fn(num_salts))

    return _make_hash_funcs


class BaseBloomFilter:

    def _setup(self, error_rate, num_slices, bits_per_slice, capacity, count):
        self.error_rate = error_rate
        self.num_slices = num_slices
        self.bits_per_slice = bits_per_slice
        self.capacity = capacity
        self.num_bits = num_slices * bits_per_slice
        self.count = count
        self.make_hashes = make_hash_funcs(self.num_slices, self.bits_per_slice)


class BloomFilter(BaseBloomFilter):

    FILE_FMT = b'<dQQQQ'

    def __init__(self, capacity, error_rate=0.001):
        if not (0 < error_rate < 1):
            raise BloomFilterException('布隆过滤器 error rate 必须再0和1之间')
        if not capacity > 0:
            raise BloomFilterException('布隆过滤器 Capacity 容量必须大于0')

        num_slices = int(math.ceil(math.log(1.0 / error_rate, 2)))
        bits_per_slice = int(math.ceil(
            (capacity * abs(math.log(error_rate))) / (num_slices * (math.log(2) ** 2)))
        )
        self._setup(error_rate, num_slices, bits_per_slice, capacity, 0)
        self.bitarray = bitarray.bitarray(self.num_bits, endian='little')
        self.bitarray.setall(False)

    def __contains__(self, key):
        bits_per_slice = self.bits_per_slice
        bitarray = self.bitarray
        hashes = self.make_hashes(key)
        offset = 0
        for k in hashes:
            if not bitarray[offset + k]:
                return False
            offset += bits_per_slice
        return True

    def __len__(self):
        return self.count

    def add(self, key, skip_check=False):

        bitarray = self.bitarray
        bits_per_slice = self.bits_per_slice
        hashes = self.make_hashes(key)
        found_all_bits = True
        assert self.capacity >= self.count, BloomFilterException('数据大小已经超出了布隆过滤器容量')

        offset = 0
        for k in hashes:
            if not skip_check and found_all_bits and not bitarray[offset + k]:
                found_all_bits = False

            self.bitarray[offset + k] = True
            offset += bits_per_slice

        if skip_check:
            self.count += 1
            return False
        elif not found_all_bits:
            self.count += 1
            return False
        else:
            return True

    def add_many(self, keys: list, skip_check=False):
        for k in keys:
            self.add(k, skip_check=skip_check)

    def clear(self):
        self.bitarray.clear()


class RedisBloomFilter(BaseBloomFilter):

    def __init__(
            self, capacity, error_rate=0.001, redis_host='localhost', redis_port=6379, redis_db=0,
            key_prefix='bloom_filter'
    ):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        num_slices = int(math.ceil(math.log(1.0 / error_rate, 2)))
        bits_per_slice = int(math.ceil(
            (capacity * abs(math.log(error_rate))) / (num_slices * (math.log(2) ** 2)))
        )
        self._setup(error_rate, num_slices, bits_per_slice, capacity, 0)
        self.key_prefix = key_prefix
        self.make_hashes = make_hash_funcs(self.num_slices, self.bits_per_slice)

    def __contains__(self, key):
        hashes = self.make_hashes(key)
        for i, h in enumerate(hashes):
            if not self.redis.getbit(f"{self.key_prefix}:{i}", h):
                return False
        return True

    def add(self, key):
        exists = key in self
        if not exists:
            hashes = self.make_hashes(key)
            for i, h in enumerate(hashes):
                self.redis.setbit(f"{self.key_prefix}:{i}", h, 1)
        return exists


class AutoBloomFilter:

    def __init__(self, capacity, error_rate=0.001, max_capacity=float('inf')):

        self.capacity = capacity
        self.error_rate = error_rate
        self.max_capacity = max_capacity
        self._bloom = None
        self.y = 0
        self.count = 0

    @property
    def bloom(self):

        if self._bloom is None:
            self._bloom = [BloomFilter(capacity=self.capacity, error_rate=self.error_rate)]

        if self.count // self.capacity != self.y:
            assert self.capacity >= self.count, BloomFilterException('数据大小已经超出了布隆过滤器容量')
            self._bloom.append(BloomFilter(capacity=self.capacity, error_rate=self.error_rate))
            self.y += 1

        return self._bloom[self.y]

    def add(self, items):
        if isinstance(items, list):
            for item in items:
                self.bloom.add(item)
                self.count += 1
        else:
            self.bloom.add(items)
            self.count += 1

    def __contains__(self, item):
        return any(item in bf for bf in self._bloom) if self._bloom is not None else False

    def __len__(self):
        return self.count
