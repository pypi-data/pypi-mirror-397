import asyncio
import base64
import hashlib
from pathlib import Path
from typing import Optional, List, Union

import aiohttp
from loguru import logger

from AioSpider.exceptions import NoticeException
from ..robot import GroupRobot


class CardSource:
    """
    卡片来源样式信息，不需要来源样式可不填写
    Args:
        icon: 来源图片的 url，非必填项
        desc: 来源图片的描述，建议不超过13个字，非必填项
        color: 来源文字的颜色，目前支持：0 灰色，1 黑色，2 红色，3 绿色，非必填项，默认为0
    """

    def __init__(self, icon: str = None, desc: str = None, color: int = 0):
        self.icon = icon or ''
        self.desc = desc or ''
        self.color = color

    @property
    def to_dict(self):
        return {"icon_url": self.icon, "desc": self.desc, "desc_color": self.color}


class CardMainTitle:
    """
    模版卡片的主要内容，包括一级标题和标题辅助信息
    Args:
        title: 一级标题，建议不超过26个字，非必填项
        desc: 标题辅助信息，建议不超过30个字，非必填项
    """

    def __init__(self, title: str = None, desc: str = None):
        self.title = title or ''
        self.desc = desc or ''

    @property
    def to_dict(self):
        return {"title": self.title, "desc": self.desc}


class HorizonContent:
    """
    嵌套字典二级标题+文本列表
    Args:
        type: 链接类型，非必填项
            0: 普通文本
            1: 跳转url
            2: 下载附件
            3: @员工
        key: 二级标题，建议不超过5个字，必填项
        url: 链接跳转的url，type是1时必填，非必填项
        value: 二级文本，如果type是2，该字段代表文件名称（要包含文件类型），建议不超过26个字，非必填项
        media_id: 附件的media_id，type是2时必填，非必填项
        user_id: 被@的成员的userid，type是3时必填，非必填项
    """

    def __init__(self, type: int = 0, key: str = None, **kwargs):
        self.type = type
        self.key = key or ''
        self.url = kwargs.get('url', '')
        self.value = kwargs.get('value', '')
        self.media_id = kwargs.get('media_id', '')
        self.user_id = kwargs.get('user_id', '')

        if self.type == 1 and not self.url:
            raise Exception('type 参数为1时，必填出入url参数')
        elif self.type == 2:
            if not self.value or not self.media_id:
                raise Exception('type 参数为2时，必填出入value和media_id参数')
        elif self.type == 3 and not self.user_id:
            raise Exception('type 参数为3时，必填出入user_id参数')

    @property
    def to_dict(self):
        return {
            "type": self.type, "keyname": self.key, "value": self.value, "url": self.url,
            "media_id": self.media_id, "userid": self.user_id
        }


class CardJump:
    """
    跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
    Args:
        type: 跳转链接类型
            0: 不跳转
            1: 跳转url
            2: 跳转小程序，非必填项
        title: 文案内容，建议不超过13个字，必填项
        url: 跳转链接的url，type是1时必填
        appid: 跳转链接的小程序的appid，type是2时必填
        page_path: 跳转链接的小程序的page_path，type是2时选填
    """

    def __init__(self, type: int = 0, title: str = None, **kwargs):
        self.type = type
        self.title = title or ''
        self.url = kwargs.get('url', '')
        self.appid = kwargs.get('appid', '')
        self.page_path = kwargs.get('page_path', '')

        if self.type == 1 and not self.url:
            raise Exception('type 参数为1时，必填出入url参数')
        elif self.type == 2 and not self.appid:
            raise Exception('type 参数为2时，必填出入appid参数')

    @property
    def to_dict(self):
        return {
            "type": self.type, "title": self.title, "url": self.url,
            "appid": self.appid, "pagepath": self.page_path
        }


class CardAction:
    """
    点击卡片的跳转事件
    Args:
        type: 片跳转类型, 必填项
            1: 跳转url
            2: 打开小程序
        url: 跳转url，type是1时必填
        appid: 跳转小程序的appid，type是2时必填
        page_path: 跳转的小程序的pagepath，type是2时选填，非必填项
    """

    def __init__(self, type: int, **kwargs):
        self.type = type
        self.url = kwargs.get('url', '')
        self.appid = kwargs.get('appid', '')
        self.page_path = kwargs.get('page_path', '')

        if self.type == 1 and not self.url:
            raise Exception('type 参数为1时，必填出入url参数')
        elif self.type == 2 and not self.appid:
            raise Exception('type 参数为2时，必填出入appid参数')

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path
        }


class EmphasisContent:
    """
    关键数据样式
    Args:
        title: 内容，建议不超过10个字，非必填项
        desc: 关键数据样式的数据描述内容，建议不超过15个字，非必填项
    """

    def __init__(self, title: str = None, desc: str = None):
        self.title = title or ''
        self.desc = desc or ''

    @property
    def to_dict(self):
        return {"title": self.title, "desc": self.desc}


class QuoteText:
    """
    关键数据样式
    Args:
        type: 引用文献样式区域点击事件，默认为0
            0: 没有点击事件
            1: 跳转 url
            2: 跳转小程序
        title: 标题，非必填项
        quote_text: 引用文案，非必填项
        url: 点击跳转的 url，type是1时必填
        appid: 点击跳转的小程序的 appid，type是2时必填
        page_path: 点击跳转的小程序的 page_path，type是2时选填
    """

    def __init__(self, *, type: int = 0, title: str = None, quote_text: str = None, **kwargs):
        self.type = type
        self.title = title or ''
        self.quote_text = quote_text or ''
        self.url = kwargs.get('url', '')
        self.appid = kwargs.get('appid', '')
        self.page_path = kwargs.get('page_path', '')

        if self.type == 1 and not self.url:
            raise Exception('type 参数为1时，必填出入url参数')
        elif self.type == 2 and not self.appid:
            raise Exception('type 参数为2时，必填出入appid参数')

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path,
            "title": self.title, "quote_area": self.quote_text,
        }


class Article:
    """
    图文消息列表
    Args:
        title：标题，不超过512个字节，超过会自动截断
        description：描述，不超过128个字节，超过会自动截断
        url：点击后跳转的链接
        pic_url：图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图1068 * 455，小图150 * 150
    """

    def __init__(self, title: str, url: str, description: str = None, pic_url: str = None):
        self.title = title
        self.url = url
        self.description = description or ''
        self.pic_url = pic_url or ''

    @property
    def to_dict(self):
        return {
            "title": self.title, "description": self.description, "url": self.url, "picurl": self.pic_url
        }


class CardImage:
    """
    图片样式
    Args:
        url：图片的url
        aspect_ratio：图片的宽高比，宽高比要小于2.25，大于1.3，不填该参数默认1.3
    """

    def __init__(self, url: str, aspect_ratio: float = 1.3):
        self.url = url
        self.aspect_ratio = aspect_ratio

    @property
    def to_dict(self):
        return {
            "url": self.url, "aspect_ratio": self.aspect_ratio
        }


class ImageText:
    """
    左图右文样式
    Args:
        type: 左图右文样式区域点击事件
            0: 没有点击事件
            1: 跳转url
            2: 跳转小程序
        url: 图片的宽高比，点击跳转的url，type是1时必填
        appid: 点击跳转的小程序的appid，必须是与当前应用关联的小程序，type是2时必填
        page_path: 点击跳转的小程序的page_path，type是2时选填
        title: 标题
        desc: 描述
        image_url: 图片url
    """

    def __init__(self, *, image_url, type: int = 0, title: str = None, desc: str = None, **kwargs):
        self.image_url = image_url
        self.type = type
        self.desc = desc
        self.title = title or ''
        self.url = kwargs.get('url', '')
        self.appid = kwargs.get('appid', '')
        self.page_path = kwargs.get('page_path', '')

        if self.type == 1 and not self.url:
            raise Exception('type 参数为1时，必填出入url参数')
        elif self.type == 2 and not self.appid:
            raise Exception('type 参数为2时，必填出入appid参数')

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path,
            "title": self.title, 'image_url': self.image_url,
            'desc': self.desc
        }


class VerticalContent:
    """
    卡片二级垂直内容
    Args:
        title: 卡片二级标题，建议不超过26个字
        desc: 二级普通文本，建议不超过112个字
    """

    def __init__(self, *, title: str = None, desc: str = None):
        self.desc = desc or ''
        self.title = title or ''

    @property
    def to_dict(self):
        return {"title": self.title, 'desc': self.desc}


class WeChatGroupRobot(GroupRobot):
    """
    企业微信群聊机器人
    @document: https://developer.work.weixin.qq.com/document/path/99110
    """

    def __init__(self, access_token: str):
        super().__init__(access_token=access_token)
        self.access_token = access_token
        self._base_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send'

    async def send_request(self, data: dict):
        for t in range(self.max_retry):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url=self._base_url,
                        headers={"Content-Type": "application/json; charset=utf-8"},
                        params={'key': self.access_token},
                        json=data
                    ) as response:
                        return await response.json()
            except aiohttp.ClientError as e:
                logger.level5(msg=f"企业微信群聊机器人消息发送失败，第{t}/{self.max_retry}次，异常信息：{str(e)}")
                await asyncio.sleep(1)
        raise NoticeException('企业微信群聊机器人消息发送失败')

    async def send_text(
            self,
            content: str, 
            at_mobiles: Optional[List[str]] = None,
            at_users: Optional[List[str]] = None, 
            at_all: bool = False
    ):
        """
        发送文本消息
        Args:
            content: 消息内容
            mentioned_list: userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人。如：['zhangsan', '@all']
            mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        Return:
            content | False
        """
        if at_all:
            at_users = ['@所有人']
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": at_users,
                "mentioned_mobile_list": at_mobiles
            }
        }
        return await self.send_request(data)

    async def send_news(self, articles: List[dict]):
        """发送图文消息"""
        data = {
            "msgtype": "news",
            "news": {"articles": articles}
        }
        return await self.send_request(data)

    async def send_voice(self, media_id: str):
        """发送语音消息"""
        data = {
            "msgtype": "voice",
            "voice": {"media_id": media_id}
        }
        return await self.send_request(data)

    async def send_text_card(
            self, *, main_title: CardMainTitle, action: CardAction, horizon_contents: Optional[List[HorizonContent]] = None,
            jump_list: Optional[List[CardJump]] = None, source: CardSource = None, emphasis_content: EmphasisContent = None,
            quote_text: QuoteText = None, sub_title: str = None
    ):
        """
        发送模板消息卡片
        Args:
            main_title:	模版卡片的主要内容，包括一级标题和标题辅助信息，
            horizon_contents: 二级标题 + 文本列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过6
            action: 点击卡片的跳转事件
            jump_list: 跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
            source: 卡片来源，非必填项
            emphasis_content: 关键数据
            quote_text:	引用文献样式，建议不与关键数据共用
            sub_title:	二级普通文本，建议不超过112个字。模版卡片主要内容的一级标题main_title.title和二级普通文本sub_title_text必须有一项填写
        """
        data = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "text_notice",
                "source": source.to_dict if source else {},
                "main_title": main_title.to_dict,
                "emphasis_content": emphasis_content.to_dict if emphasis_content else {},
                "quote_area": quote_text.to_dict if quote_text else {},
                "sub_title_text": sub_title or '',
                "horizontal_content_list": [i.to_dict for i in (horizon_contents or [])],
                "jump_list": [i.to_dict for i in (jump_list or [])],
                "card_action": action.to_dict
            }
        }
        return await self.send_request(data)

    async def send_image_card(
            self, main_title: CardMainTitle, action: CardAction, card_image: CardImage = None,
            horizon_contents: Optional[List[HorizonContent]] = None, jump_list: Optional[List[CardJump]] = None,
            source: CardSource = None, quote_text: QuoteText = None, image_text_area: ImageText = None,
            vertical_contents: List[VerticalContent] = None
    ):
        """
        发送模板图片卡片
        Args:
            main_title:	模版卡片的主要内容，包括一级标题和标题辅助信息，
            action: 点击卡片的跳转事件
            card_image: 图片样式
            horizon_contents: 二级标题 + 文本列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过6
            jump_list: 跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
            source: 卡片来源，非必填项
            quote_text:	引用文献样式，建议不与关键数据共用
            image_text_area: 左图右文样式
            vertical_contents: 卡片二级垂直内容，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过4
        """
        data = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "news_notice",
                "source": source.to_dict if source else {},
                "main_title": main_title.to_dict,
                "card_image": card_image.to_dict,
                "image_text_area": image_text_area.to_dict if image_text_area else {},
                "quote_area": quote_text.to_dict if quote_text else {},
                "vertical_content_list": [i.to_dict for i in (vertical_contents or [])],
                "horizontal_content_list": [i.to_dict for i in (horizon_contents or [])],
                "jump_list": [i.to_dict for i in (jump_list or [])],
                "card_action": action.to_dict
            }
        }
        return await self.send_request(data)

    async def send_markdown(self, content: str):
        """
        发送markdown文本消息
        Args:
            content: 消息内容
        Attr:
            标题:
                # 标题一
                ## 标题二
                ### 标题三
                #### 标题四
                ##### 标题五
                ###### 标题六
            加粗: **hello**
            行内代码段: `hello`
            引用: > 引用文字
            字体颜色(只支持3种内置颜色):
                <font color="info">绿色</font>
                <font color="comment">灰色</font>
                <font color="warning">橙红色</font>
        """
        data = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }
        return await self.send_request(data)

    async def send_image(self, path: Union[str, Path] = None, content: bytes = None):
        """
        发送图片
        Args:
            path: 图片路径
            content: 图片内容
        """
        if isinstance(path, str):
            path = Path(path)

        if path is not None and content is None:
            txt = path.read_bytes()
        elif path is None and content is not None:
            txt = content
        else:
            return False

        txt_md5 = hashlib.md5(txt).hexdigest()

        data = {
            "msgtype": "image",
            "image": {"base64": base64.b64encode(txt).decode(), "md5": txt_md5}
        }

        return await self.send_request(data)

    async def send_image_text(self, article_list: List[Article]):
        """
        发送图文消息
        Args:
            article_list: 图文消息，一个图文消息支持1到8条图文
        Return:
            True | False
        """
        article_list = [i.to_dict for i in article_list]

        data = {
            "msgtype": "news", "news": {"articles": article_list}
        }

        return await self.send_request(data)

    async def upload_file(self, path: Union[str, Path]):
        """
        上传文件
        Args:
            path: 文件路径
        Return:
            media_id
        """
        if isinstance(path, str):
            path = Path(path)

        data = {
            'Content-Type': 'application/octet-stream',
            'name': path.stem,
            'filename': path.name,
            'filelength': len(path.read_bytes())
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media',
                params={'key': self.access_token, 'type': 'file'},
                data=data,
                files={'file': path.read_bytes()}
            ) as response:
                data = await response.json()
                return data.get('media_id')

    async def send_file(self, path: Union[str, Path]):
        """
        发送文件
        Args:
            path: 文件路径
        """
        media_id = await self.upload_file(path)
        data = {
            "msgtype": "file",
            "file": {"media_id": media_id}
        }
        return await self.send_request(data)


if __name__ == '__main__':
    # robot = GroupRobot('66b6eb15-fc45-40f9-b07c-81cf8ee900c5')
    robot = GroupRobot('b0ced49e-ee5a-4e9b-ab1f-e00124731076')
    # robot.send_text('世界，你好')
    # robot.send_text_card(
    #     main_title=CardMainTitle(title='预警通知', desc='爬虫结束预警通知'),
    #     action=CardAction(type=1, url="http://47.101.219.184:8887"),
    #     horizon_contents=[
    #         HorizonContent(key='爬虫名称', value='融资融券'),
    #         HorizonContent(key='预警等级', value='融资融券'),
    #         HorizonContent(key='入库数量', value='20000条'),
    #     ],
    #     jump_list=[
    #         CardJump(type=0, title='查看详情')
    #     ],
    #     emphasis_content=EmphasisContent(title='INFO', desc='一般等级通知'),
    #     source= CardSource(
    #         icon="http://47.101.219.184:8887/static/main/tarkin-logo.gif?imageView2/1/w/80/h/80",
    #         desc='踏金数据',
    #         color=0
    #     )
    # )
    # robot.send_file(r'D:\companyspider\spider\新浪公告\baidu.py')
    robot.send_image(r'D:\companyspider\spider\新浪公告\微信截图_20230308132347.png')
