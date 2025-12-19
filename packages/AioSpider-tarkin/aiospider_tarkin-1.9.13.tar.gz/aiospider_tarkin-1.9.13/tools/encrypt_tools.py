import uuid
import hmac
import base64
import binascii
import hashlib
from typing import Any, Union, Callable

import rsa
from Crypto.Cipher import AES

from AioSpider.constants import PaddingMode, AES


def make_md5(item: Any) -> str:
    """
    计算md5值
    Args:
        item: md5 待计算值
    Return:
        哈希值 Any
    """

    if isinstance(item, str):
        return hashlib.md5(item.encode('utf-8', 'ignore')).hexdigest()

    if isinstance(item, bytes):
        return hashlib.md5(item).hexdigest()

    return hashlib.md5(str(item).encode()).hexdigest()


def make_hmac(key: Union[str, bytes], msg: Union[str, bytes], mode: Callable = hashlib.md5) -> str:
    """
    计算hmac值
    Args:
        item: hmac 待计算值
    Return:
        哈希值hmac
    """

    if isinstance(key, str):
        key = key.encode()

    if isinstance(msg, str):
        msg = msg.encode()

    return hmac.new(key, msg, mode).hexdigest()


def make_sha1(item: Any) -> str:
    """
    计算sha1值
    Args:
        item: hash 待计算值
    Return:
        sha1值 Any
    """

    if isinstance(item, str):
        return hashlib.sha1(item.encode()).hexdigest()

    if isinstance(item, bytes):
        return hashlib.sha1(item).hexdigest()

    return hashlib.sha1(str(item).encode()).hexdigest()


def make_sha256(item: Any) -> str:
    """
    计算sha256值
    Args:
        item: hash 待计算值
    Return:
        sha256值 Any
    """

    if isinstance(item, str):
        return hashlib.sha256(item.encode()).hexdigest()

    if isinstance(item, bytes):
        return hashlib.sha256(item).hexdigest()

    return hashlib.sha256(str(item).encode()).hexdigest()


def make_uuid(string: str = None, mode: int = 1, namespace: uuid.UUID = uuid.NAMESPACE_DNS) -> str:
    """
    生成 UUID 字符串
    Args:
        string: 字符串
        mode: 模式
            1: 根据当前的时间戳和 MAC 地址生成
            2: 根据 MD5 生成
            3: 根据随机数生成
            4. 根据 SHA1 生成
        namespace: 命名空间，有四个可选值：NAMESPACE_DNS、NAMESPACE_URL、NAMESPACE_OID、NAMESPACE_X500
    Return:
        uuid 字符串
    """

    if mode == 1:
        uid = uuid.uuid1()
    elif mode == 2:
        uid = uuid.uuid3(namespace, str(string))
    elif mode == 2:
        uid = uuid.uuid4()
    elif mode == 2:
        uid = uuid.uuid5(namespace, str(string))
    else:
        uid = uuid.uuid1()

    return str(uid).replace('-', '')


class AESCryptorECB:
    """
    AES 加密
    Args:
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8

    使用示例：
    >>> aes = AESCryptorECB(
    >>>     key='yg5qV3fSqSuDzzSd', padding=PaddingMode.PKCS7Padding
    >>> )
    >>> enc_str = '{"x":114.7,"y":5}'
    >>> rData = aes.encrypt(enc_str)
    >>> print("密文：", rData.to_base64())
    >>> dec_data = aes.decrypt(rData)
    >>> print("明文：", dec_data)
    """

    class MetaData:

        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            if data is None:
                data = bytes()

            self.data = data
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

    def __init__(self, key: str, padding: int = 0, encoding: str = "utf-8"):

        key = key.encode() if isinstance(key, str) else key

        self.aes = AES.new(key, AES.MODE_ECB)

        self.encoding = encoding
        self.padding = padding

    @staticmethod
    def set_zero_padding(data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    @staticmethod
    def set_pkcs7_padding(data):
        size = 16 - len(data) % 16
        if size == 0:
            size = 16
        return data + size.to_bytes(1, 'little') * size

    @staticmethod
    def strip_zero_padding(data):
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    @staticmethod
    def strip_pkcs7_padding(data):
        size = data[-1]
        return data.rstrip(size.to_bytes(1, 'little'))

    def set_padding(self, data):
        if self.padding == PaddingMode.NoPadding:
            return self.set_zero_padding(data)
        elif self.padding == PaddingMode.ZeroPadding:
            return self.set_zero_padding(data)
        elif self.padding == PaddingMode.PKCS7Padding:
            return self.set_pkcs7_padding(data)
        else:
            raise Exception("不支持Padding")

    def strip_padding(self, data):
        if self.padding == PaddingMode.NoPadding:
            return self.strip_zero_padding(data)
        elif self.padding == PaddingMode.ZeroPadding:
            return self.strip_zero_padding(data)
        elif self.padding == PaddingMode.PKCS7Padding:
            return self.strip_pkcs7_padding(data)
        else:
            raise Exception("不支持Padding")

    def encrypt(self, data: Union[str, bytes]) -> MetaData:

        if isinstance(data, str):
            data = data.encode(self.encoding)

        enc_data = self.aes.encrypt(self.set_padding(data))
        return self.MetaData(enc_data)

    def decrypt(self, data: Union[MetaData, bytes]) -> str:

        if isinstance(data, self.MetaData):
            data = data.to_base64()

        data = base64.b64decode(data)
        decrypt_data = self.strip_padding(self.aes.decrypt(data))
        return decrypt_data.decode(self.encoding)


class AESEncryptCBC:
    """
    AES CBC模式加密
    Args:
        key: 秘钥
        iv: 偏移量
        encoding: 编码格式，默认为 utf-8

    使用示例：
    >>> aes = AESEncryptCBC(
    >>>     key='ed98b0a439f15b6acb4088b22323c360', iv='cb4088b22323c360'
    >>> )
    >>> enc_str = '{"x":114.7,"y":5}'
    >>> rData = aes.encrypt(enc_str)
    >>> print("密文：", rData.to_base64())
    >>> dec_data = aes.decrypt(rData)
    >>> print("明文：", dec_data)
    """

    class MetaData:

        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            if data is None:
                data = bytes()

            self.data = data
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

    def __init__(self, key: Union[str, bytes], iv: Union[str, bytes], encoding='utf-8'):

        if isinstance(key, str):
            key = key.encode(encoding)

        if isinstance(iv, str):
            iv = iv.encode(encoding)

        self.key = key
        self.iv = iv
        self.encoding = encoding

    def pkcs7padding(self, content):
        """使用PKCS7填充"""

        padding = 16 - len(content) % 16
        padding_text = chr(padding) * padding
        return content + padding_text

    def encrypt(self, content: str) -> MetaData:
        """AES加密"""

        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        content_padding = self.pkcs7padding(content)
        encrypt_bytes = cipher.encrypt(content_padding.encode(self.encoding))
        return self.MetaData(encrypt_bytes)

    def decrypt(self, content: Union[str, bytes, MetaData]) -> str:
        """AES解密"""

        if isinstance(content, self.MetaData):
            content = content.to_base64()

        content = base64.b64decode(content)

        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        text = cipher.decrypt(content)
        text = text.rstrip(text[-1].to_bytes(1, 'little')).decode(self.encoding)

        return text


class RSACryptor:
    """
    RSA 加密
    Args:
        public_key: 公钥
        mode: 模长

    使用示例：
    >>> rsa = RSACryptor(
    >>>     public_key = 'd3bcef1f00424f3261c89323fa8cdfa12bbac400d9fe8bb627e8d27a44bd5d59dce559135d678a8143beb5b8d‘
    >>>                  ’7056c4e1f89c4e1f152470625b7b41944a97f02da6f605a49a93ec6eb9cbaf2e7ac2b26a354ce69eb265953d2‘
    >>>                  ’c29e395d6d8c1cdb688978551aa0f7521f290035fad381178da0bea8f9e6adce39020f513133fb‘, 
    >>>     mode=AES.MODE_ECB
    >>> )
    >>> enc_str = rsa.to_hen('123456')       # 返回16进制密文
    >>> enc_str = rsa.to_base64('123456')    # 返回base64密文
    """

    def __init__(self, public_key: str, mode: str):
        self.public_key = public_key
        self.mode = mode

    def encrypt(self, msg: Union[str, bytes]) -> bytes:
        key = rsa.PublicKey(int(self.public_key, 16), int(self.mode, 16))
        return rsa.encrypt(msg.encode(), key)

    def to_hen(self, msg: Union[str, bytes]) -> str:
        enc_text = self.encrypt(msg)
        return enc_text.hex()

    def to_base64(self, msg: Union[str, bytes]) -> str:
        enc_text = self.encrypt(msg)
        return base64.b64encode(enc_text).decode()


def aes_ecb_encrypt(
        *, text: Union[str, bytes, dict], key: str, padding: int = PaddingMode.PKCS7Padding, 
        encoding: str = "utf-8"
) -> str:
    """
    AES ECB 加密
    Args:
        text: 待加密字符串
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        iv: 偏移量
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8
    Return:
        AES 加密后的base64密文
    """

    aes = AESCryptorECB(key=key, padding=padding, encoding=encoding)
    meta_data = aes.encrypt(text)

    return meta_data.to_base64()


def aes_ecb_decrypt(
        *, text: str, key: str, padding: int = PaddingMode.PKCS7Padding, encoding: str = "utf-8"
) -> str:
    """
    AES ECB 解密
    Args:
        text: 待解密字符串
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        iv: 偏移量
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8
    Return:
        AES 加密后的base64密文
    """

    aes = AESCryptorECB(key=key, padding=padding, encoding=encoding)
    return aes.decrypt(text)


def rsa_encrypt_hen(*, public_key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    AES 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的16进制密文
    """

    rsa = RSACryptor(public_key=public_key, mode=mode)
    return rsa.to_hen('123456')


def rsa_encrypt_base64(*, public_key: str, key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    AES 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的base64密文
    """

    rsa = RSACryptor(public_key=public_key, mode=mode)
    return rsa.to_base64('123456')

