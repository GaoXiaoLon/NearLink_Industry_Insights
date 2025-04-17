from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import sys
import os
import time
import random
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.network import NetworkTool
from services.storage import Storage
from services.email_sender import EmailSender
from config.config_manager import ConfigManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Monitor:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.network = NetworkTool()
        self.storage = Storage()
        self.logger = logging.getLogger(__name__)
        
        # 初始化邮件发送器
        email_config = config_manager.get('email', {})
        if not email_config:
            self.logger.warning("未找到邮件配置")
            self.email_sender = None
        else:
            try:
                self.email_sender = EmailSender(
                    smtp_server=email_config['smtp_server'],
                    smtp_port=email_config['smtp_port'],
                    username=email_config['username'],
                    password=email_config['password'],
                    sender=email_config['sender']
                )
            except KeyError as e:
                self.logger.error(f"邮件配置不完整: {str(e)}")
                self.email_sender = None

    def _setup_driver(self):
        """设置Chrome浏览器选项"""
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 暂时注释掉无头模式，方便调试
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 添加固定的User-Agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def _search_baidu(self, keyword: str) -> List[Dict[str, Any]]:
        """从百度搜索获取信息"""
        driver = None
        try:
            self.logger.info(f"开始从百度搜索关键词: {keyword}")
            
            # 设置浏览器
            driver = self._setup_driver()
            
            # 访问百度首页
            driver.get("https://www.baidu.com")
            time.sleep(random.uniform(1, 2))
            
            # 输入搜索关键词
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "kw"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            time.sleep(random.uniform(0.5, 1))
            
            # 点击搜索按钮
            search_button = driver.find_element(By.ID, "su")
            search_button.click()
            
            # 等待搜索结果加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            time.sleep(random.uniform(2, 3))
            
            # 解析搜索结果
            results = []
            result_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class*="result c-container"]')
            self.logger.info(f"找到 {len(result_elements)} 条搜索结果")
            
            for element in result_elements:
                try:
                    # 获取标题和链接
                    title_elem = element.find_element(By.CSS_SELECTOR, 'h3.t a')
                    title = title_elem.text.strip()
                    url = title_elem.get_attribute('href')
                    
                    # 获取描述
                    try:
                        desc_elem = element.find_element(By.CSS_SELECTOR, 'div[class*="c-abstract"]')
                        description = desc_elem.text.strip()
                    except NoSuchElementException:
                        try:
                            desc_elem = element.find_element(By.CSS_SELECTOR, 'div[class*="c-span-last"]')
                            description = desc_elem.text.strip()
                        except NoSuchElementException:
                            description = ""
                    
                    # 获取来源
                    try:
                        source_elem = element.find_element(By.CSS_SELECTOR, 'span[class*="c-showurl"]')
                        source = source_elem.text.strip()
                    except NoSuchElementException:
                        try:
                            source_elem = element.find_element(By.CSS_SELECTOR, 'span[class*="c-color-gray"]')
                            source = source_elem.text.strip()
                        except NoSuchElementException:
                            source = "未知来源"
                    
                    # 获取时间
                    try:
                        time_elem = element.find_element(By.CSS_SELECTOR, 'span[class*="c-color-gray2"]')
                        pub_time = time_elem.text.strip()
                    except NoSuchElementException:
                        pub_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    result = {
                        'title': title,
                        'url': url,
                        'source': source,
                        'time': pub_time,
                        'description': description,
                        'keyword': keyword
                    }
                    
                    self.logger.info(f"找到内容: {title}")
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"解析内容失败: {str(e)}")
                    continue
            
            if not results:
                self.logger.warning("未找到任何搜索结果")
            
            return results
            
        except Exception as e:
            self.logger.error(f"百度搜索失败: {str(e)}", exc_info=True)
            return []
        finally:
            if driver:
                driver.quit()

    def _search_bing(self, keyword: str) -> List[Dict[str, Any]]:
        """从Bing搜索获取信息"""
        driver = None
        try:
            self.logger.info(f"开始从Bing搜索关键词: {keyword}")
            
            # 设置浏览器
            driver = self._setup_driver()
            
            # 访问Bing首页
            driver.get("https://www.bing.com")
            time.sleep(random.uniform(1, 2))
            
            # 输入搜索关键词
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sb_form_q"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            time.sleep(random.uniform(0.5, 1))
            
            # 点击搜索按钮
            search_button = driver.find_element(By.ID, "search_icon")
            search_button.click()
            
            # 等待搜索结果加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "b_algo"))
            )
            time.sleep(random.uniform(2, 3))
            
            # 解析搜索结果
            results = []
            result_elements = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo')
            self.logger.info(f"找到 {len(result_elements)} 条搜索结果")
            
            for element in result_elements:
                try:
                    # 获取标题和链接
                    title_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
                    title = title_elem.text.strip()
                    url = title_elem.get_attribute('href')
                    
                    # 获取描述
                    try:
                        desc_elem = element.find_element(By.CSS_SELECTOR, 'div.b_caption p')
                        description = desc_elem.text.strip()
                    except NoSuchElementException:
                        description = ""
                    
                    # 获取来源
                    try:
                        source_elem = element.find_element(By.CSS_SELECTOR, 'div.b_attribution cite')
                        source = source_elem.text.strip()
                    except NoSuchElementException:
                        source = "未知来源"
                    
                    # 获取时间
                    try:
                        time_elem = element.find_element(By.CSS_SELECTOR, 'div.b_attribution span')
                        pub_time = time_elem.text.strip()
                    except NoSuchElementException:
                        pub_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    result = {
                        'title': title,
                        'url': url,
                        'source': source,
                        'time': pub_time,
                        'description': description,
                        'keyword': keyword
                    }
                    
                    self.logger.info(f"找到内容: {title}")
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"解析内容失败: {str(e)}")
                    continue
            
            if not results:
                self.logger.warning("未找到任何搜索结果")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bing搜索失败: {str(e)}", exc_info=True)
            return []
        finally:
            if driver:
                driver.quit()

    def _monitor_sources(self, sources: List[str], keywords: List[str]) -> List[Dict[str, Any]]:
        """监控指定来源"""
        self.logger.info("开始监控任务")
        self.logger.info(f"监控关键词: {keywords}")
        
        findings = []
        
        # 从搜索引擎获取信息
        for keyword in keywords:
            self.logger.info(f"开始搜索关键词: {keyword}")
            
            # 从Bing获取信息
            self.logger.info("开始Bing搜索...")
            bing_results = self._search_bing(keyword)
            self.logger.info(f"Bing搜索完成，获取到 {len(bing_results)} 条结果")
            
            # 从百度获取信息
            self.logger.info("开始百度搜索...")
            baidu_results = self._search_baidu(keyword)
            self.logger.info(f"百度搜索完成，获取到 {len(baidu_results)} 条结果")
            
            # 合并结果
            all_results = bing_results + baidu_results
            
            # 按标题排序
            sorted_results = sorted(all_results, 
                                 key=lambda x: x.get('title', ''))
            
            # 只保留最新的10条
            sorted_results = sorted_results[:10]
            
            if not sorted_results:
                self.logger.warning("未获取到任何结果")
            else:
                self.logger.info(f"获取到 {len(sorted_results)} 条结果")
                for result in sorted_results:
                    self.logger.info(f"标题: {result.get('title', '')}")
                    self.logger.info(f"链接: {result.get('url', '')}")
                    self.logger.info("---")
            
            findings.extend(sorted_results)
            
            # 如果已经收集到足够的数量，就停止搜索
            if len(findings) >= 10:
                self.logger.info("已收集到足够的搜索结果，停止搜索")
                break
            
            # 添加延时，避免请求过于频繁
            self.logger.info("等待2秒后继续...")
            time.sleep(2)
        
        # 确保最终结果不超过10条，并按标题排序
        findings = sorted(findings, 
                        key=lambda x: x.get('title', ''))[:10]
        
        if not findings:
            self.logger.warning("所有搜索引擎均未获取到数据")
        else:
            self.logger.info(f"监控任务完成，共获取 {len(findings)} 条信息")
            
            # 准备报告数据
            report_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'keywords': keywords,
                'findings': findings,
                'statistics': {
                    'total_findings': len(findings),
                    'sources': list(set(f.get('source', '') for f in findings))
                }
            }
            
            # 发送报告
            if self.email_sender:
                receivers = self.config.get('email.receivers', [])
                if receivers:
                    self.email_sender.send_report(receivers, report_data)
                    self.logger.info("报告发送成功")
                else:
                    self.logger.warning("未设置收件人邮箱，跳过发送报告")
            else:
                self.logger.warning("邮件发送器未初始化，跳过发送报告")
        
        return findings

    def run_monitor(self) -> None:
        """运行监控任务"""
        try:
            self.logger.info("开始执行监控任务")
            
            # 获取配置
            keywords = self.config.get('monitor.keywords', [])
            self.logger.info(f"获取到监控关键词: {keywords}")
            
            # 执行监控
            self.logger.info("开始执行监控...")
            findings = self._monitor_sources([], keywords)
            self.logger.info(f"监控完成，获取到 {len(findings)} 条信息")
            
            # 保存结果
            date = datetime.now().strftime("%Y-%m-%d")
            self.logger.info(f"正在保存结果到 {date}...")
            self.storage.save_findings(date, findings)
            self.logger.info("结果保存完成")
            
            # 生成统计数据
            self.logger.info("正在生成统计数据...")
            statistics = self._generate_statistics(findings)
            self.storage.save_statistics(date, statistics)
            self.logger.info("统计数据生成完成")
            
            # 发送报告
            self.logger.info("正在发送报告...")
            self._send_report(date, findings, statistics)
            self.logger.info("报告发送完成")
            
            self.logger.info("监控任务执行完成")
        except Exception as e:
            self.logger.error(f"监控任务执行失败: {str(e)}", exc_info=True)
            raise

    def _extract_new_content(self, 
                           content: str, 
                           source: str, 
                           keywords: List[str]) -> List[Dict[str, Any]]:
        """提取新内容"""
        findings = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找包含关键词的文章
        for keyword in keywords:
            # 查找包含关键词的链接
            links = soup.find_all('a', href=True, 
                                string=lambda text: text and keyword.lower() in text.lower())
            
            for link in links:
                title = link.get_text().strip()
                url = link['href']
                
                # 检查是否已经存在
                if not self._is_existing_content(url):
                    findings.append({
                        'title': title,
                        'url': url,
                        'source': source,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'keyword': keyword
                    })
        
        return findings

    def _is_existing_content(self, url: str) -> bool:
        """检查内容是否已存在"""
        recent_findings = self.storage.get_recent_findings(days=7)
        return any(finding.get('url') == url for finding in recent_findings)

    def _generate_statistics(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成统计数据"""
        statistics = {
            'total_findings': len(findings),
            'sources_count': len(set(f['source'] for f in findings)),
            'keywords_count': len(set(f['keyword'] for f in findings)),
        }
        
        # 按关键词统计
        keyword_stats = {}
        for finding in findings:
            keyword = finding['keyword']
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
        statistics['keyword_stats'] = keyword_stats
        
        return statistics

    def _send_report(self, 
                    date: str, 
                    findings: List[Dict[str, Any]], 
                    statistics: Dict[str, Any]) -> None:
        """发送监控报告"""
        try:
            if not self.email_sender:
                self.logger.warning("邮件发送器未初始化，跳过发送报告")
                return
                
            report_data = {
                'date': date,
                'keywords': self.config.get('monitor.keywords', []),
                'findings': findings,
                'statistics': statistics
            }
            
            # 获取收件人列表
            receivers = self.config.get('email.receivers', [])
            if not receivers:
                self.logger.warning("未设置收件人邮箱，跳过发送报告")
                return
                
            self.email_sender.send_report(receivers, report_data)
        except Exception as e:
            self.logger.error(f"发送报告失败: {str(e)}")

    def test_collect(self) -> None:
        """测试采集功能"""
        try:
            self.logger.info("开始执行测试采集")
            self.logger.info("开始测试采集数据...")
            
            # 获取配置
            keywords = self.config.get('monitor.keywords', [])
            self.logger.info(f"监控关键词: {keywords}")
            
            # 执行监控
            findings = self._monitor_sources([], keywords)
            
            if findings:
                # 生成统计数据
                statistics = self._generate_statistics(findings)
                
                # 准备报告数据
                report_data = {
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'keywords': keywords,
                    'findings': findings,
                    'statistics': statistics
                }
                
                # 发送报告
                if self.email_sender:
                    receivers = self.config.get('email.receivers', [])
                    if receivers:
                        self.email_sender.send_report(receivers, report_data)
                        self.logger.info("测试报告发送成功")
                    else:
                        self.logger.warning("未设置收件人邮箱，跳过发送报告")
                else:
                    self.logger.warning("邮件发送器未初始化，跳过发送报告")
            
            self.logger.info("测试采集完成")
            
        except Exception as e:
            self.logger.error(f"测试采集失败: {str(e)}")
            raise
