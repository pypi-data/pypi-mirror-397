import re
import time
import hashlib
import random
from typing import Optional

import requests
import pydash

__all__ = [
    'translate',
    'google_translate',
    'youdao_translate'
]


def generate_baidu_translate_sign(query: str) -> str:

    def truncate_text(text: str, max_length: int = 30) -> str:
        if len(text) > max_length:
            return text[:10] + text[len(text) // 2 - 5: len(text) // 2 + 5] + text[-10:]
        return text
    
    def shift_bits(num: int, shift_str: str) -> int:
        for i in range(0, len(shift_str) - 2, 3):
            shift = ord(shift_str[i + 2]) - 87 if 'a' <= shift_str[i + 2] else int(shift_str[i + 2])
            result = num >> shift if '+' == shift_str[i + 1] else num << shift
            num = (num + result) & 0xFFFFFFFF if '+' == shift_str[i] else num ^ result
        return num
    
    def encode_text(text: str) -> list:
        encoded = []
        for char in text:
            code = ord(char)
            if code < 128:
                encoded.append(code)
            else:
                if code < 2048:
                    encoded.append((code >> 6) | 192)
                elif 0xD800 <= code <= 0xDBFF and len(text) > 1 and 0xDC00 <= ord(text[1]) <= 0xDFFF:
                    code = 0x10000 + ((code & 0x3FF) << 10) + (ord(text[1]) & 0x3FF)
                    encoded.extend([(code >> 18) | 240, ((code >> 12) & 0x3F) | 128])
                    text = text[1:]
                else:
                    encoded.append((code >> 12) | 224)
                encoded.extend([((code >> 6) & 0x3F) | 128, (code & 0x3F) | 128])
        return encoded

    truncated_query = truncate_text(query)
    base, multiplier = 320305, 131321201
    encoded_query = encode_text(truncated_query)

    result = base
    shift_str1, shift_str2 = "+-a^+6", "+-3^+b+-f"

    for code in encoded_query:
        result = shift_bits(result + code, shift_str1)

    result = shift_bits(result, shift_str2) ^ multiplier
    if result < 0:
        result = 0x80000000 + (result & 0x7FFFFFFF)
    result %= 1000000

    return f"{result}.{result ^ base}"


class BaiduTranslator:
    _token: Optional[str] = None
    _sign: Optional[str] = None
    _source_language: Optional[str] = None

    def __init__(self, query: str):
        self.query = query
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/110.0.0.0 Safari/537.36',
        })

    @property
    def token(self) -> Optional[str]:
        if self._token is None:
            response = self.session.get("https://fanyi.baidu.com")
            token_match = re.search(r"token: '(.*?)',", response.text, re.S)
            self._token = token_match.group(1) if token_match else None
        return self._token

    @property
    def sign(self) -> str:
        if self._sign is None:
            self._sign = generate_baidu_translate_sign(self.query)
        return self._sign

    @property
    def detect_language(self) -> str:
        if self._source_language is None:
            response = self.session.post("https://fanyi.baidu.com/langdetect", data={"query": self.query})
            self._source_language = pydash.get(response.json(), 'lan', 'en')
        return self._source_language

    def translate(self) -> str:
        source_lang = self.detect_language
        target_lang = "zh" if source_lang != "zh" else "en"

        url = "https://fanyi.baidu.com/v2transapi"
        params = {"from": source_lang, "to": target_lang}
        data = {
            "from": source_lang, "to": target_lang, "query": self.query, "simple_means_flag": "3",
            "transtype": "realtime", "sign": self.sign, "token": self.token, "domain": "common"
        }

        max_attempts = 100
        for _ in range(max_attempts):
            response = self.session.post(url, params=params, data=data)
            translation = pydash.get(response.json(), 'trans_result.data[0].dst', '')
            if translation:
                return translation
            time.sleep(0.5)

        return ''


def translate(query: str) -> str:
    """百度翻译函数"""
    return BaiduTranslator(query).translate()


class GoogleTranslator:
    """谷歌翻译接口"""

    def __init__(self, query: str):
        self.query = query
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/110.0.0.0 Safari/537.36',
        })

    def detect_language(self) -> str:
        """检测源语言"""
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "en",
            "dt": "t",
            "q": self.query
        }
        response = self.session.get(url, params=params)
        return response.json()[2]

    def translate(self) -> str:
        """执行翻译"""
        source_lang = self.detect_language()
        target_lang = "zh-CN" if source_lang != "zh-CN" else "en"

        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": self.query
        }

        max_attempts = 3
        for _ in range(max_attempts):
            try:
                response = self.session.get(url, params=params)
                translation = response.json()[0][0][0]
                if translation:
                    return translation
            except Exception as e:
                print(f"谷歌翻译出错: {e}")
                time.sleep(0.5)

        return ''


def google_translate(query: str) -> str:
    """谷歌翻译函数"""
    return GoogleTranslator(query).translate()


class YoudaoTranslator:
    """有道翻译接口"""

    def __init__(self, query: str):
        self.query = query
        self.url = "https://fanyi.youdao.com/translate_o"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://fanyi.youdao.com/",
            "Cookie": "OUTFOX_SEARCH_USER_ID=-2022895048@10.168.8.76;",
        })

    def _get_sign(self):
        """生成sign参数"""
        t = str(int(time.time() * 1000))
        salt = t + str(random.randint(0, 9))
        sign = hashlib.md5(("fanyideskweb" + self.query + salt + "Ygy_4c=r#e#4EX^NUGUc5").encode()).hexdigest()
        return t, salt, sign

    def translate(self) -> str:
        """执行翻译"""
        t, salt, sign = self._get_sign()
        data = {
            "i": self.query,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": salt,
            "sign": sign,
            "lts": t,
            "bv": "5.0",
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTlME",
        }

        max_attempts = 3
        for _ in range(max_attempts):
            try:
                response = self.session.post(self.url, data=data)
                result = response.json()
                translation = result['translateResult'][0][0]['tgt']
                if translation:
                    return translation
            except Exception as e:
                print(f"有道翻译出错: {e}")
                time.sleep(0.5)

        return ''


def youdao_translate(query: str) -> str:
    """有道翻译函数"""
    return YoudaoTranslator(query).translate()

