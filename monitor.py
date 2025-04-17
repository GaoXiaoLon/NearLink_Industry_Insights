import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import schedule
from datetime import datetime
from email_sender import EmailSender
from report_generator import ReportGenerator
from utils.logger import get_logger


class SparkIndustryMonitor:
    def __init__(self, config):
        self.config = config
        self.email_sender = EmailSender(config)
        self.report_generator = ReportGenerator()
        self.logger = get_logger("monitor")
        self.running = False

        # 设置搜索参数
        self.search_engines = {
            'baidu': "https://www.baidu.com/s?wd={query}",
            'sogou': "https://www.sogou.com/web?query={query}",
            'bing': "https://www.bing.com/search?q={query}"
        }

    def fetch_news(self):
        """从多个搜索引擎获取星闪行业新闻"""
        articles = []
        keywords = self.config.get('monitor', {}).get('keywords', ['星闪'])

        for engine, url_template in self.search_engines.items():
            if engine not in self.config.get('monitor', {}).get('sources', []):
                continue

            for keyword in keywords:
                try:
                    query = f"{keyword} 行业动态 {datetime.today().strftime('%Y年%m月%d日')}"
                    url = url_template.format(query=requests.utils.quote(query))

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles.extend(self._parse_results(soup, engine))

                except Exception as e:
                    self.logger.error(f"从 {engine} 获取 '{keyword}' 失败: {str(e)}")

        return articles

    def _parse_results(self, soup, source):
        """解析搜索结果"""
        results = []

        # 百度结果解析
        if source == 'baidu':
            for item in soup.select('.result.c-container'):
                title_elem = item.select_one('h3 a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem['href']
                    desc = item.select_one('.c-abstract') or item.select_one('.content-right_8Zs40')
                    desc = desc.get_text(strip=True) if desc else "无描述"
                    results.append({
                        'title': title,
                        'url': url,
                        'description': desc,
                        'source': '百度',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

        # 搜狗结果解析
        elif source == 'sogou':
            for item in soup.select('.results .vrwrap'):
                title_elem = item.select_one('h3 a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem['href']
                    desc = item.select_one('.str-pd-box') or item.select_one('.text-layout')
                    desc = desc.get_text(strip=True) if desc else "无描述"
                    results.append({
                        'title': title,
                        'url': url,
                        'description': desc,
                        'source': '搜狗',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

        return results

    def generate_daily_report(self):
        """生成每日报告"""
        try:
            self.logger.info("开始生成每日报告...")
            articles = self.fetch_news()
            if not articles:
                self.logger.warning("未获取到任何新闻数据")
                return None

            report = self.report_generator.generate(articles)
            self.logger.info(f"报告生成成功，共 {len(articles)} 条数据")
            return report
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            return None

    def send_daily_report(self):
        """发送每日报告"""
        report = self.generate_daily_report()
        if report:
            success = self.email_sender.send(report)
            if success:
                self.logger.info("邮件发送成功")
            else:
                self.logger.error("邮件发送失败")

    def start_service(self):
        """启动监测服务"""
        self.running = True
        schedule_time = self.config.get('monitor', {}).get('schedule_time', '09:00')

        self.logger.info(f"启动监测服务，计划每天 {schedule_time} 执行")
        schedule.every().day.at(schedule_time).do(self.send_daily_report)

        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def stop_service(self):
        """停止监测服务"""
        self.running = False
        self.logger.info("监测服务已停止")