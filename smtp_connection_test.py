# smtp_163_test_enhanced.py
import smtplib
import socket
from email.mime.text import MIMEText
from getpass import getpass


def test_smtp_163_connection():
    print("=== 163邮箱SMTP连接测试（增强版） ===")

    config = {
        'smtp_server': 'smtp.163.com',
        'smtp_port': 465,
        'username': input("请输入163邮箱地址: ").strip(),
        'password': input("请输入SMTP授权码(输入时将可见): ").strip(),
        'recipient': input("请输入测试收件人邮箱: ").strip(),
        'timeout': 10  # 设置超时时间为10秒
    }
    config['sender'] = config['username']

    # 构建测试邮件
    msg = MIMEText("SMTP连接测试邮件内容", 'plain', 'utf-8')
    msg['From'] = config['sender']
    msg['To'] = config['recipient']
    msg['Subject'] = 'Python SMTP测试邮件'

    try:
        print(f"\n尝试连接 {config['smtp_server']}:{config['smtp_port']}...")

        # 创建连接（增加超时设置）
        server = smtplib.SMTP_SSL(
            host=config['smtp_server'],
            port=config['smtp_port'],
            timeout=config['timeout']
        )
        print("✓ 成功连接到SMTP服务器")

        # 调试：查看SMTP欢迎信息
        print("服务器响应:", server.docmd("EHLO client")[1].decode())

        # 登录
        print("正在进行登录验证...")
        server.login(config['username'], config['password'])
        print("✓ 登录成功")

        # 发送邮件
        print(f"发送邮件至 {config['recipient']}...")
        server.sendmail(config['sender'], config['recipient'], msg.as_string())
        print("✓ 邮件发送成功")

        server.quit()
        print("\n测试成功！请检查收件箱（包括垃圾邮件箱）")

    except socket.timeout:
        print("× 连接超时！可能原因：")
        print("- 网络不稳定")
        print("- 防火墙阻止了连接")
        print("- SMTP服务器地址或端口错误")

    except smtplib.SMTPConnectError as e:
        print(f"× 连接失败: {e}")
        print("请检查：")
        print("- 是否使用正确的端口（465/994）")
        print("- 本地网络是否正常")

    except smtplib.SMTPAuthenticationError:
        print("× 认证失败！请确认：")
        print("- 使用的是SMTP授权码（不是邮箱密码）")
        print("- 邮箱已开启SMTP服务")

    except Exception as e:
        print(f"× 发生未知错误: {type(e).__name__}: {e}")


if __name__ == '__main__':
    test_smtp_163_connection()
    input("\n按 Enter 键退出...")