import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
import ssl

class EmailSender:
    def __init__(self, 
                 smtp_server: str, 
                 smtp_port: int, 
                 username: str, 
                 password: str,
                 sender: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender = sender
        self.logger = logging.getLogger(__name__)

    def send_email(self, 
                  receivers: List[str], 
                  subject: str, 
                  content: str, 
                  html_content: Optional[str] = None) -> bool:
        """发送邮件"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ', '.join(receivers)

            # 添加纯文本内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # 如果有HTML内容，添加HTML版本
            if html_content:
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 创建SSL上下文
            context = ssl.create_default_context()

            # 连接SMTP服务器并发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)

            self.logger.info(f"邮件发送成功: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}")
            return False

    def send_report(self, 
                   receivers: List[str], 
                   report_data: dict) -> bool:
        """发送监控报告"""
        subject = f"星闪行业洞察报告 - {report_data.get('date', '')}"
        
        # 纯文本内容
        content = f"""
星闪行业洞察报告
日期: {report_data.get('date', '')}

监控关键词: {', '.join(report_data.get('keywords', []))}

发现的新内容:
{self._format_findings(report_data.get('findings', []))}

统计信息:
{self._format_statistics(report_data.get('statistics', {}))}
        """

        # HTML内容
        html_content = f"""
        <html>
        <body>
            <h1>星闪行业洞察报告</h1>
            <p>日期: {report_data.get('date', '')}</p>
            
            <h2>监控关键词</h2>
            <p>{', '.join(report_data.get('keywords', []))}</p>
            
            <h2>发现的新内容</h2>
            {self._format_findings_html(report_data.get('findings', []))}
            
            <h2>统计信息</h2>
            {self._format_statistics_html(report_data.get('statistics', {}))}
        </body>
        </html>
        """

        return self.send_email(receivers, subject, content, html_content)

    def _format_findings(self, findings: List[dict]) -> str:
        """格式化发现内容（纯文本）"""
        if not findings:
            return "无新发现"
        
        formatted = ""
        for finding in findings:
            formatted += f"- {finding.get('title', '')}\n"
            formatted += f"  来源: {finding.get('source', '')}\n"
            formatted += f"  时间: {finding.get('time', '')}\n\n"
        return formatted

    def _format_findings_html(self, findings: List[dict]) -> str:
        """格式化发现内容（HTML）"""
        if not findings:
            return "<p>无新发现</p>"
        
        html = "<ul>"
        for finding in findings:
            html += f"""
            <li>
                <strong>{finding.get('title', '')}</strong><br>
                来源: {finding.get('source', '')}<br>
                时间: {finding.get('time', '')}
            </li>
            """
        html += "</ul>"
        return html

    def _format_statistics(self, statistics: dict) -> str:
        """格式化统计信息（纯文本）"""
        formatted = ""
        for key, value in statistics.items():
            formatted += f"{key}: {value}\n"
        return formatted

    def _format_statistics_html(self, statistics: dict) -> str:
        """格式化统计信息（HTML）"""
        html = "<ul>"
        for key, value in statistics.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        return html
