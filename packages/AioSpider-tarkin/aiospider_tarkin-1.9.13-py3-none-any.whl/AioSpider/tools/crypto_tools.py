import uuid
import hmac
import base64
import binascii
import hashlib
from typing import Any, Union, Callable

import rsa
from Crypto.Cipher import AES, DES

from AioSpider.objects import PaddingMode

__all__ = [
    'calculate_md5', 
    'calculate_hmac', 
    'calculate_sha1', 
    'calculate_sha256', 
    'calculate_sha512', 
    'generate_uuid', 
    'des_encrypt', 
    'aes_ecb_encrypt', 
    'aes_ecb_decrypt', 
    'rsa_encrypt_hex', 
    'rsa_encrypt_base64'
]


def calculate_md5(data: Any) -> str:
    """计算md5值"""
    if isinstance(data, str):
        return hashlib.md5(data.encode('utf-8', 'ignore')).hexdigest()
    if isinstance(data, bytes):
        return hashlib.md5(data).hexdigest()
    return hashlib.md5(str(data).encode()).hexdigest()


def calculate_hmac(key: Union[str, bytes], message: Union[str, bytes], hash_function: Callable = hashlib.md5) -> str:
    """计算hmac值"""
    key = key.encode() if isinstance(key, str) else key
    message = message.encode() if isinstance(message, str) else message
    return hmac.new(key, message, hash_function).hexdigest()


def calculate_sha1(data: Any) -> str:
    """计算sha1值"""
    if isinstance(data, str):
        data = data.encode()
    elif not isinstance(data, bytes):
        data = str(data).encode()
    return hashlib.sha1(data).hexdigest()


def calculate_sha256(data: Any) -> str:
    """计算sha256值"""
    if isinstance(data, str):
        data = data.encode()
    elif not isinstance(data, bytes):
        data = str(data).encode()
    return hashlib.sha256(data).hexdigest()


def calculate_sha512(data: Any) -> str:
    """计算sha512值"""
    if isinstance(data, str):
        data = data.encode()
    elif not isinstance(data, bytes):
        data = str(data).encode()
    return hashlib.sha512(data).hexdigest()


def generate_uuid(text: str = None, mode: int = 1, namespace: uuid.UUID = uuid.NAMESPACE_DNS) -> str:
    """
    生成 UUID 字符串
    Args:
        text: 字符串
        mode: 模式
            1: 根据当前的时间戳和 MAC 地址生成
            2: 根据 MD5 生成
            3: 根据随机数生成
            4. 根据 SHA1 生成
        namespace: 命名空间，有四个可选值：NAMESPACE_DNS、NAMESPACE_URL、NAMESPACE_OID、NAMESPACE_X500
    Return:
        uuid 字符串
    """
    if mode in [2, 4] and text is None:
        raise ValueError("mode为2或4时，text参数不能为None")
    
    uuid_generators = {
        1: uuid.uuid1,
        2: lambda: uuid.uuid3(namespace, text),
        3: uuid.uuid4,
        4: lambda: uuid.uuid5(namespace, text)
    }

    generated_uuid = uuid_generators.get(mode, uuid.uuid1)()
    return str(generated_uuid)


class AESEncryptorECB:
    """
    AES 加密
    Args:
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8

    使用示例:
    >>> aes = AESEncryptorECB(
    >>>     key='yg5qV3fSqSuDzzSd', padding=PaddingMode.PKCS7Padding
    >>> )
    >>> plaintext = '{"x":114.7,"y":5}'
    >>> encrypted_data = aes.encrypt(plaintext)
    >>> print("密文：", encrypted_data.to_base64())
    >>> decrypted_data = aes.decrypt(encrypted_data)
    >>> print("明文：", decrypted_data)
    """

    class EncryptedData:

        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            self.data = data or bytes()
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

    def __init__(self, key: Union[str, bytes], padding: int = 0, encoding: str = "utf-8"):
        self.aes = AES.new(key.encode() if isinstance(key, str) else key, AES.MODE_ECB)
        self.encoding = encoding
        self.padding = padding

    @staticmethod
    def _zero_pad(data):
        return data + b'\x00' * (16 - len(data) % 16)

    @staticmethod
    def _pkcs7_pad(data):
        pad_size = 16 - len(data) % 16
        return data + bytes([pad_size]) * pad_size

    @staticmethod
    def _strip_zero_padding(data):
        return data.rstrip(b'\x00')

    @staticmethod
    def _strip_pkcs7_padding(data):
        return data[:-data[-1]]

    def _apply_padding(self, data):
        padding_methods = {
            PaddingMode.NoPadding: self._zero_pad,
            PaddingMode.ZeroPadding: self._zero_pad,
            PaddingMode.PKCS7Padding: self._pkcs7_pad
        }
        return padding_methods.get(self.padding, lambda x: x)(data)

    def _remove_padding(self, data):
        unpadding_methods = {
            PaddingMode.NoPadding: self._strip_zero_padding,
            PaddingMode.ZeroPadding: self._strip_zero_padding,
            PaddingMode.PKCS7Padding: self._strip_pkcs7_padding
        }
        return unpadding_methods.get(self.padding, lambda x: x)(data)

    def encrypt(self, data: Union[str, bytes]) -> EncryptedData:
        data = data.encode(self.encoding) if isinstance(data, str) else data
        encrypted_data = self.aes.encrypt(self._apply_padding(data))
        return self.EncryptedData(encrypted_data)

    def decrypt(self, data: Union[EncryptedData, bytes]) -> str:
        data = base64.b64decode(data.to_base64() if isinstance(data, self.EncryptedData) else data)
        decrypted_data = self._remove_padding(self.aes.decrypt(data))
        return decrypted_data.decode(self.encoding)


class AESEncryptorCBC:
    """
    AES CBC模式加密
    Args:
        key: 秘钥
        iv: 初始化向量
        encoding: 编码格式，默认为 utf-8

    使用示例:
    >>> aes = AESEncryptorCBC(
    >>>     key='ed98b0a439f15b6acb4088b22323c360', iv='cb4088b22323c360'
    >>> )
    >>> plaintext = '{"x":114.7,"y":5}'
    >>> encrypted_data = aes.encrypt(plaintext)
    >>> print("密文：", encrypted_data.to_base64())
    >>> decrypted_data = aes.decrypt(encrypted_data)
    >>> print("明文：", decrypted_data)
    """

    class EncryptedData:

        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            self.data = data or bytes()
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

    def __init__(self, key: Union[str, bytes], iv: Union[str, bytes], encoding='utf-8'):
        self.key = key.encode(encoding) if isinstance(key, str) else key
        self.iv = iv.encode(encoding) if isinstance(iv, str) else iv
        self.encoding = encoding

    @staticmethod
    def _pkcs7_pad(content):
        """使用PKCS7填充"""
        padding = 16 - len(content) % 16
        return content + chr(padding) * padding

    def encrypt(self, content: str) -> EncryptedData:
        """AES加密"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_content = self._pkcs7_pad(content)
        encrypted_bytes = cipher.encrypt(padded_content.encode(self.encoding))
        return self.EncryptedData(encrypted_bytes)

    def decrypt(self, content: Union[str, bytes, EncryptedData]) -> str:
        """AES解密"""
        if isinstance(content, self.EncryptedData):
            content = content.to_base64()
        content = base64.b64decode(content)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_text = cipher.decrypt(content)
        return decrypted_text[:-decrypted_text[-1]].decode(self.encoding)


class DESEncryptor:
    """
    DES 加密
    Args:
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        iv: 初始化向量（仅在CBC模式下使用）
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8

    使用示例:
    >>> des = DESEncryptor(
    >>>     key='12345678', mode=DES.MODE_ECB, padding=PaddingMode.PKCS7Padding
    >>> )
    >>> plaintext = '{"x":114.7,"y":5}'
    >>> encrypted_data = des.encrypt(plaintext)
    >>> print("密文：", encrypted_data.to_base64())
    >>> decrypted_data = des.decrypt(encrypted_data)
    >>> print("明文：", decrypted_data)
    """

    class EncryptedData:
        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            self.data = data or bytes()
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

    def __init__(self, key: Union[str, bytes], mode: int, iv: Union[str, bytes] = None, padding: int = PaddingMode.PKCS7Padding, encoding: str = "utf-8"):
        self.key = key.encode(encoding) if isinstance(key, str) else key
        self.mode = mode
        self.iv = iv.encode(encoding) if isinstance(iv, str) else iv
        self.padding = padding
        self.encoding = encoding
        self.des = DES.new(self.key, self.mode, self.iv) if self.mode == DES.MODE_CBC else DES.new(self.key, self.mode)

    def _apply_padding(self, data):
        padding_methods = {
            PaddingMode.NoPadding: lambda x: x,
            PaddingMode.ZeroPadding: lambda x: x + b'\x00' * (8 - len(x) % 8),
            PaddingMode.PKCS7Padding: lambda x: x + bytes([8 - len(x) % 8]) * (8 - len(x) % 8)
        }
        return padding_methods.get(self.padding, lambda x: x)(data)

    def _remove_padding(self, data):
        unpadding_methods = {
            PaddingMode.NoPadding: lambda x: x,
            PaddingMode.ZeroPadding: lambda x: x.rstrip(b'\x00'),
            PaddingMode.PKCS7Padding: lambda x: x[:-x[-1]]
        }
        return unpadding_methods.get(self.padding, lambda x: x)(data)

    def encrypt(self, data: Union[str, bytes]) -> EncryptedData:
        data = data.encode(self.encoding) if isinstance(data, str) else data
        encrypted_data = self.des.encrypt(self._apply_padding(data))
        return self.EncryptedData(encrypted_data)

    def decrypt(self, data: Union[EncryptedData, bytes]) -> str:
        data = base64.b64decode(data.to_base64() if isinstance(data, self.EncryptedData) else data)
        decrypted_data = self._remove_padding(self.des.decrypt(data))
        return decrypted_data.decode(self.encoding)
    

def des_encrypt(
        *, text: Union[str, bytes], key: Union[str, bytes], mode: int, iv: Union[str, bytes] = None, 
        padding: int = PaddingMode.PKCS7Padding, encoding: str = "utf-8"
) -> str:
    des = DESEncryptor(key=key, mode=mode, iv=iv, padding=padding, encoding=encoding)
    return des.encrypt(text).to_base64()


class RSAEncryptor:
    """
    RSA 加密
    Args:
        public_key: 公钥
        mode: 模长

    使用示例:
    >>> rsa = RSAEncryptor(
    >>>     public_key = 'd3bcef1f00424f3261c89323fa8cdfa12bbac400d9fe8bb627e8d27a44bd5d59dce559135d678a8143beb5b8d'
                            '7056c4e1f89c4e1f152470625b7b41944a97f02da6f605a49a93ec6eb9cbaf2e7ac2b26a354ce69eb265953d2'
                            'c29e395d6d8c1cdb688978551aa0f7521f290035fad381178da0bea8f9e6adce39020f513133fb',
    >>>     mode=AES.MODE_ECB
    >>> )
    >>> encrypted_hex = rsa.to_hex('123456')       # 返回16进制密文
    >>> encrypted_base64 = rsa.to_base64('123456')    # 返回base64密文
    """

    def __init__(self, public_key: str, mode: str):
        self.public_key = public_key
        self.mode = mode

    def encrypt(self, msg: Union[str, bytes]) -> bytes:
        key = rsa.PublicKey(int(self.public_key, 16), int(self.mode, 16))
        return rsa.encrypt(msg.encode() if isinstance(msg, str) else msg, key)

    def to_hex(self, msg: Union[str, bytes]) -> str:
        return self.encrypt(msg).hex()

    def to_base64(self, msg: Union[str, bytes]) -> str:
        return base64.b64encode(self.encrypt(msg)).decode()


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
    aes = AESEncryptorECB(key=key, padding=padding, encoding=encoding)
    return aes.encrypt(text).to_base64()


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
        AES 解密后的明文
    """
    aes = AESEncryptorECB(key=key, padding=padding, encoding=encoding)
    return aes.decrypt(text)


def rsa_encrypt_hex(*, public_key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    RSA 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的16进制密文
    """
    rsa = RSAEncryptor(public_key=public_key, mode=mode)
    return rsa.to_hex(msg)


def rsa_encrypt_base64(*, public_key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    RSA 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的base64密文
    """
    rsa = RSAEncryptor(public_key=public_key, mode=mode)
    return rsa.to_base64(msg)

