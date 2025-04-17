import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import urlparse
import random

class NetworkTool:
    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.user_agent = user_agent or self._get_random_user_agent()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        })

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        return random.choice(user_agents)

    def get_page_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"获取页面内容失败: {url}, 错误: {str(e)}")
            return None

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """从HTML中提取链接"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http'):
                links.append(href)
            elif href.startswith('/'):
                parsed_url = urlparse(base_url)
                links.append(f"{parsed_url.scheme}://{parsed_url.netloc}{href}")
        return links

    def search_keywords(self, html: str, keywords: List[str]) -> Dict[str, int]:
        """在HTML中搜索关键词"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        results = {}
        for keyword in keywords:
            count = text.lower().count(keyword.lower())
            if count > 0:
                results[keyword] = count
        return results

    def get_with_retry(self, url: str, max_retries: int = 3, delay: int = 1) -> Optional[requests.Response]:
        """带重试的GET请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"请求失败: {url}, 错误: {str(e)}")
                    return None
                time.sleep(delay * (attempt + 1))
        return None
