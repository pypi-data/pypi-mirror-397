from typing import Union, List

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from loguru import logger
from AioSpider.exceptions import NoticeException, StatusTags


class Email:

    def __init__(self, smtp: str, port: int, sender: str, token: str, receiver: Union[str, List[str]], *args, **lwargs):

        self.smtp = smtp
        self.port = port
        self.sender = sender
        self.token = token

        if isinstance(receiver, str):
            self.receiver = [receiver]
        else:
            self.receiver = receiver

        self._server = None

    @property
    def server(self):
        if self._server is None:
            try:
                self._server = smtplib.SMTP(self.smtp, self.port, timeout=3)
                # 开启TLS加密，确保邮件内容安全传输
                self._server.starttls()
                self._server.login(self.sender, self.token)
            except Exception:
                raise NoticeException(status=StatusTags.StmpConnectError)
        return self._server

    def close(self):
        self.server.quit()

    def send_text(self, subject, body, attach: Union[bytes, List[bytes]] = None):

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

        self.server.sendmail(self.sender, self.receiver, msg.as_string())
        logger.info("邮件发送成功")
