import asyncio
from typing import List, Optional, Dict

from loguru import logger
import aiohttp

from AioSpider.exceptions import NoticeException
from ..robot import GroupRobot

class DingDingGroupRobot(GroupRobot):
    """
    钉钉群机器人
    @document: https://open.dingtalk.com/document/group/message-types-and-data-format
    """

    def __init__(self, access_token: str):
        super().__init__(access_token=access_token)
        self.access_token = access_token
        self._base_url = 'https://oapi.dingtalk.com/robot/send'

    async def send_request(self, data: dict):
        for t in range(self.max_retry):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self._base_url, 
                        headers={"Content-Type": "application/json; charset=utf-8"},
                        params={'access_token': self.access_token}, 
                        json=data
                    ) as response:
                        data = await response.json()
                        if data.get('errcode') == 0:
                            return data
                        raise NoticeException(f"钉钉群机器人消息发送失败，错误信息：{data.get('errmsg')}")
            except aiohttp.ClientError as e:
                logger.level5(msg=f"钉钉群机器人消息发送失败，第{t}/{self.max_retry}次，异常信息：{str(e)}")
                await asyncio.sleep(1)
        raise NoticeException('钉钉群机器人消息发送失败')

    async def send_text(
            self, content: str, 
            at_mobiles: Optional[List[str]] = None, 
            at_users: Optional[List[str]] = None,
            at_all: bool = False
    ):
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_users or [],
                "isAtAll": at_all
            }
        }
        return await self.send_request(data)

    async def send_link(self, title: str, text: str, message_url: str, pic_url: Optional[str] = None):
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url or '',
                "messageUrl": message_url
            }
        }
        return await self.send_request(data)

    async def send_markdown(
            self, title: str, text: str, at_mobiles: Optional[List[str]] = None, at_user_ids: Optional[List[str]] = None,
            is_at_all: bool = False
    ):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_user_ids or [],
                "isAtAll": is_at_all
            }
        }
        return await self.send_request(data)

    async def send_action_card(self, title: str, text: str, btns: List[Dict[str, str]], btn_orientation: str = "0", hide_avatar: str = "0"):
        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btnOrientation": btn_orientation,
                "hideAvatar": hide_avatar,
                "btns": btns
            }
        }
        return await self.send_request(data)

    async def send_feed_card(self, links: List[Dict[str, str]]):
        data = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": links
            }
        }
        return await self.send_request(data)

    async def send_single_btn_action_card(self, title: str, text: str, single_title: str, single_url: str):
        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "singleTitle": single_title,
                "singleURL": single_url
            }
        }
        return await self.send_request(data)

    async def send_multi_btn_action_card(self, title: str, text: str, btns: List[Dict[str, str]], btn_orientation: str = "0", hide_avatar: str = "0"):
        return await self.send_action_card(title, text, btns, btn_orientation, hide_avatar)
