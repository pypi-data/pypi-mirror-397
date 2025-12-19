try:
    from ddddocr import DdddOcr
except:
    logger.warning("未安装ddddocr库")


def ocr_character_code(content):
    return DdddOcr(show_ad=False).classification(content)
