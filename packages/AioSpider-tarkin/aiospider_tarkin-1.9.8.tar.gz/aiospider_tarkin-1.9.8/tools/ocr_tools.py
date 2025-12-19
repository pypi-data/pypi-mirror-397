import base64
from typing import Union
from pathlib import Path

__all__ = [
    'recognize_from_base64',
    'recognize_from_image',
    'recognize_from_bytes',
    'recognize_from_url',
    'recognize_multiple',
    'recognize_with_custom_model',
    'train_custom_model',
]

ddddocr = None


def load_ddddocr():
    global ddddocr
    if ddddocr is None:
        try:
            import ddddocr
        except ImportError:
            raise ImportError("ddddocr 模块未安装，请先安装 ddddocr 模块[pip install ddddocr]")


def recognize_from_base64(base64_string: str) -> str:
    """从base64编码的图片中识别验证码"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    return ocr.classification(base64.b64decode(base64_string))


def recognize_from_image(image_path: Union[str, Path]) -> str:
    """从图片文件中识别验证码"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open(image_path, 'rb') as f:
        return ocr.classification(f.read())


def recognize_from_bytes(image_bytes: bytes) -> str:
    """从图片字节数据中识别验证码"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    return ocr.classification(image_bytes)


def recognize_from_url(image_url: str) -> str:
    """从图片URL中识别验证码"""
    import requests
    response = requests.get(image_url)
    return recognize_from_bytes(response.content)


def recognize_multiple(image_list: list) -> list:
    """批量识别多个验证码图片"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    return [ocr.classification(img) for img in image_list]


def recognize_with_custom_model(image_bytes: bytes, model_path: str) -> str:
    """使用自定义模型识别验证码"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False, model_path=model_path)
    return ocr.classification(image_bytes)


def train_custom_model(train_data_dir: str, output_model_path: str) -> None:
    """训练自定义验证码识别模型"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr.train(train_data_dir, output_model_path)


def preprocess_image(image_bytes: bytes) -> bytes:
    """预处理验证码图片"""
    load_ddddocr()
    ocr = ddddocr.DdddOcr(show_ad=False)
    return ocr.pre_process(image_bytes)


def detect_objects(image_bytes: bytes) -> list:
    """检测图片中的对象"""
    load_ddddocr()
    det = ddddocr.DdddOcr(det=True, show_ad=False)
    return det.detection(image_bytes)


def slide_match(target_bytes: bytes, background_bytes: bytes) -> dict:
    """滑动验证码匹配"""
    load_ddddocr()
    slide = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    return slide.slide_match(target_bytes, background_bytes)
