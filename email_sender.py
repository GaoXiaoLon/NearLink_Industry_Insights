import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.image import MIMEImage
from email.utils import formatdate
from utils.logger import get_logger


class EmailSender:
    def __init__(self, config):
        """
        初始化邮件发送器

        :param config: 配置字典，包含email部分的SMTP配置
        """
        self.config = config.get('email', {})
        self.logger = get_logger("email")
        self.logger.info("初始化邮件发送器，SMTP服务器: %s:%d",
                         self.config.get('smtp_server'),
                         self.config.get('smtp_port'))

    def send(self, report):
        """
        发送邮件

        :param report: 邮件正文内容
        :return: 是否发送成功
        """
        try:
            # 获取配置参数
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port')
            from_addr = self.config.get('sender')
            to_addr = self.config.get('recipient')
            password = self.config.get('password')

            self.logger.debug("开始准备发送邮件，发件人: %s, 收件人: %s", from_addr, to_addr)

            # 创建SMTP连接
            self.logger.debug("正在连接SMTP服务器 %s:%d...", smtp_server, smtp_port)
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                self.logger.debug("SMTP服务器响应: %s", server.ehlo())

                # 启用TLS加密
                self.logger.debug("启动TLS加密...")
                server.starttls()
                self.logger.debug("TLS加密已建立")

                # 登录SMTP服务器
                self.logger.debug("正在进行SMTP认证...")
                server.login(from_addr, password)
                self.logger.info("SMTP认证成功，用户: %s", from_addr)

                # 构建邮件
                msg = MIMEText(report, 'plain', 'utf-8')
                msg['From'] = Header(from_addr, 'utf-8')
                msg['To'] = Header(to_addr, 'utf-8')
                msg['Subject'] = Header('每日报告', 'utf-8')
                msg['Date'] = formatdate()

                self.logger.debug("邮件内容构建完成，正文长度: %d 字节", len(report))

                # 发送邮件
                server.sendmail(from_addr, [to_addr], msg.as_string())
                self.logger.info("邮件发送成功，收件人: %s", to_addr)

                return True

        except smtplib.SMTPConnectError as e:
            self.logger.error("SMTP连接失败: %s", str(e))
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error("SMTP认证失败: %s", str(e))
        except smtplib.SMTPException as e:
            self.logger.error("SMTP协议错误: %s", str(e))
        except Exception as e:
            self.logger.error("邮件发送过程中发生未知错误: %s", str(e), exc_info=True)

        return False

    def send_test_email(self):
        """
        发送测试邮件
        :return: 是否发送成功
        """
        test_content = """
        ====== SMTP服务测试邮件 ======

        这是一封来自系统的测试邮件，用于验证SMTP配置是否正确。

        服务器: {server}:{port}
        发件人: {sender}
        收件人: {recipient}
        发送时间: {time}

        如果您收到此邮件，说明SMTP服务配置正确！
        """.format(
            server=self.config.get('smtp_server'),
            port=self.config.get('smtp_port'),
            sender=self.config.get('from_addr'),
            recipient=self.config.get('to_addr'),
            time=formatdate()
        )

        return self.send(test_content)


if __name__ == "__main__":
    # 测试代码
    import json
    from utils.logger import get_logger

    get_logger("email")  # 初始化日志

    # 加载配置
    with open('config/default.json') as f:
        config = json.load(f)

    sender = EmailSender(config)

    if sender.send_test_email():
        print("测试邮件发送成功！请检查收件箱。")
    else:
        print("测试邮件发送失败，请查看日志文件。")