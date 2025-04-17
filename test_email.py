import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import json
import os

def test_email_send():
    """测试邮件发送功能"""
    try:
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), "config", "default.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        email_config = config['email']
        
        # 创建邮件内容
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "星闪行业洞察 - 测试邮件"
        msg['From'] = email_config['sender']
        msg['To'] = ', '.join(email_config['receivers'])
        
        # 纯文本内容
        text_content = """
这是一封测试邮件，用于验证邮件发送功能是否正常。

如果您收到这封邮件，说明邮件发送功能工作正常。

星闪行业洞察系统
        """
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        
        # HTML内容
        html_content = """
        <html>
        <body>
            <h1>星闪行业洞察 - 测试邮件</h1>
            <p>这是一封测试邮件，用于验证邮件发送功能是否正常。</p>
            <p>如果您收到这封邮件，说明邮件发送功能工作正常。</p>
            <p>星闪行业洞察系统</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 连接SMTP服务器并发送
        with smtplib.SMTP_SSL(
            email_config['smtp_server'], 
            email_config['smtp_port'], 
            context=context
        ) as server:
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
        
        print("测试邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"测试邮件发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试邮件发送功能...")
    test_email_send() 