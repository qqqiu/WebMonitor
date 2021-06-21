import logging
import smtplib
import traceback
import requests
from PIL import Image
from io import BytesIO
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage

from setting.models import SystemMailSetting
from task.utils.notification.notification import Notification

logger = logging.getLogger('main')


class MailNotification(Notification):
    def __init__(self):
        try:
            setting = SystemMailSetting.objects.first()
        except Exception:
            logger.error('没有设置系统邮箱，无法发送邮件通知')
            logger.error(traceback.format_exc())
            raise Exception('没有设置系统邮箱，无法发送邮件通知')

        self.mail_server = setting.mail_server
        self.mail_port = setting.mail_port
        self.mail_username = setting.mail_username
        self.mail_sender = setting.mail_sender
        self.mail_password = setting.mail_password

    def send(self, to, header, content, img_url=''):
        if to == '默认':
            logger.error('没有设置通知邮箱，无法发送邮件通知')
            raise Exception('没有设置通知邮箱，无法发送邮件通知')

        msgRoot = MIMEMultipart()
        msgRoot['To'] = Header(to, 'utf-8')
        msgRoot['From'] = Header('新商品上架啦！', 'utf-8')
        msgRoot['Subject'] = Header(header, 'utf-8')

        if img_url != '':
            content = content + '<p><img src="cid:item_img"></p>'
            response = requests.get(img_url)
            img = MIMEImage(response.content)
            img.add_header('Content-ID', '<item_img>')  # 给一个content Id 供后面html内容引用
            msgRoot.attach(img)

        print(content)
        message = MIMEText(content, 'html', 'utf-8')
        msgRoot.attach(message)

        smtpObj = smtplib.SMTP_SSL(self.mail_server, self.mail_port)
        smtpObj.connect(self.mail_server, self.mail_port)
        smtpObj.login(self.mail_username, self.mail_password)
        smtpObj.sendmail(self.mail_sender, to, msgRoot.as_string())
