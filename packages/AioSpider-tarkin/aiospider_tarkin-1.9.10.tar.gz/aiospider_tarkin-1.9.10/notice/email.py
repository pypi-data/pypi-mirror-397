import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Union, List

from loguru import logger
import aiosmtplib
from AioSpider.exceptions import NoticeException
from .robot import GroupRobot


class EmailRobot(GroupRobot):

    def __init__(self, smtp: str, port: int, sender: str, token: str, receiver: Union[str, List[str]], *args, **kwargs):
        super().__init__(access_token=token)
        self.smtp = smtp
        self.port = port
        self.sender = sender

        if isinstance(receiver, str):
            self.receiver = [receiver]
        else:
            self.receiver = receiver

    async def send_request(self, msg):
        for t in range(self.max_retry):
            try:
                async with aiosmtplib.SMTP(hostname=self.smtp.value, port=self.port, use_tls=True, timeout=3) as server:
                    # await server.starttls()
                    await server.login(self.sender, self.access_token)
                    await server.send_message(msg, sender=self.sender, recipients=self.receiver)
                return
            except Exception as e:
                logger.level5(msg=f"邮件服务器连接失败，第{t}/{self.max_retry}次，异常信息：{str(e)}")
                await asyncio.sleep(1)
        raise NoticeException('邮件服务器连接失败')

    async def close(self):
        if self._server:
            await self._server.quit()

    async def send_text(self, subject, body, attach: Union[bytes, List[bytes]] = None):
        # 构建邮件内容
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ','.join(self.receiver)
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain'))

        if isinstance(attach, bytes):
            attach = [attach]

        if attach is not None:
            for x in attach:
                image_mime = MIMEImage(x)
                msg.attach(image_mime)

        await self.send_request(msg)
        logger.level3(msg="邮件发送成功")
