# baidu_spark_crawler.py
import os
import time
import logging
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaiduSparkCrawler:
    def __init__(self, output_dir: str = "data/baidu_results"):
        """
        百度星闪内容爬虫
        
        :param output_dir: 结果存储目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://www.baidu.com/s?wd={}&pn={}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def search_keyword(self, keyword: str, pages: int = 5) -> List[Dict]:
        """
        搜索指定关键词
        
        :param keyword: 搜索关键词
        :param pages: 要爬取的页数
        :return: 结果列表
        """
        results = []
        encoded_keyword = urllib.parse.quote(keyword)
        
        for page in range(pages):
            try:
                url = self.base_url.format(encoded_keyword, page * 10)
                logger.info(f"正在爬取第 {page + 1} 页: {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                page_results = self._parse_page(response.text)
                results.extend(page_results)
                
                logger.info(f"本页获取到 {len(page_results)} 条结果")
                time.sleep(random.uniform(1, 3))  # 随机延迟防止封禁
                
            except Exception as e:
                logger.error(f"第 {page + 1} 页爬取失败: {str(e)}")
                continue
                
        return results

    def _parse_page(self, html: str) -> List[Dict]:
        """解析百度搜索结果页"""
        soup = BeautifulSoup(html, 'lxml')
        items = []
        
        for result in soup.find_all('div', class_='result'):
            try:
                title_tag = result.find('h3', class_='t')
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                link = title_tag.find('a')['href']
                
                # 获取真实链接（百度跳转链接）
                real_link = self._get_real_url(link)
                
                # 获取摘要
                abstract = result.find('div', class_='c-abstract')
                abstract = abstract.get_text(strip=True) if abstract else ""
                
                # 获取来源和时间
                source_tag = result.find('div', class_='c-span-last')
                if source_tag:
                    source_info = source_tag.find('span', class_='c-color-gray')
                    source = source_info.get_text(strip=True) if source_info else ""
                    date = source_tag.find('span', class_='c-color-gray2')
                    date = date.get_text(strip=True) if date else ""
                else:
                    source = date = ""
                
                items.append({
                    'title': title,
                    'link': real_link,
                    'abstract': abstract,
                    'source': source,
                    'date': date,
                    'crawl_time': time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                logger.warning(f"解析结果条目失败: {str(e)}")
                continue
                
        return items

    def _get_real_url(self, redirect_url: str) -> str:
        """获取百度跳转后的真实URL"""
        try:
            resp = self.session.head(redirect_url, allow_redirects=True, timeout=5)
            return resp.url
        except:
            return redirect_url

    def save_results(self, results: List[Dict], filename: str = None) -> Path:
        """保存结果到CSV文件"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"baidu_spark_{timestamp}.csv"
            
        df = pd.DataFrame(results)
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False, encoding='utf_8_sig')  # 中文编码
        
        logger.info(f"结果已保存到: {filepath}")
        return filepath

    def run(self, keywords: List[str] = None, pages: int = 3):
        """执行爬虫任务"""
        keywords = keywords or ["星闪", "星闪技术", "星闪联盟"]
        
        all_results = []
        for keyword in keywords:
            logger.info(f"开始搜索关键词: {keyword}")
            results = self.search_keyword(keyword, pages=pages)
            all_results.extend(results)
            time.sleep(2)
            
        if all_results:
            self.save_results(all_results)

if __name__ == "__main__":
    # 使用示例
    crawler = BaiduSparkCrawler()
    
    # 自定义搜索参数
    crawler.run(
        keywords=["星闪", "SparkLink"],  # 搜索关键词列表
        pages=3  # 每个关键词爬取的页数
    )