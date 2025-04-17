import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate
from utils.logger import get_logger


class EmailSender:
    def __init__(self, config):
        self.config = config.get('email', {})
        self.logger = get_logger("email")

    def send(self, report_html):
        """发送邮件"""
        if not self.config:
            self.logger.error("邮件配置未初始化")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.config.get('sender')
        msg['To'] = self.config.get('recipient')
        msg['Subject'] = self.config.get('subject', '星闪行业日报')
        msg['Date'] = formatdate(localtime=True)

        # 添加HTML内容
        msg.attach(MIMEText(report_html, 'html', 'utf-8'))

        try:
            with smtplib.SMTP(
                    self.config.get('smtp_server'),
                    self.config.get('smtp_port', 587)
            ) as server:
                server.starttls()
                server.login(
                    self.config.get('username'),
                    self.config.get('password')
                )
                server.send_message(msg)
            self.logger.info("邮件发送成功")
            return True
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}")
            return False