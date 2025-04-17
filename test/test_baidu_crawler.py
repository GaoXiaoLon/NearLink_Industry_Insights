from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import json
import os
from datetime import datetime
import time
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_baidu_crawler')

def get_random_user_agent():
    """获取随机User-Agent"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def setup_driver():
    """设置Chrome浏览器选项"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 暂时注释掉无头模式，方便调试
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 添加随机User-Agent
    chrome_options.add_argument(f'user-agent={get_random_user_agent()}')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def search_baidu(keyword: str) -> list:
    """使用Selenium从百度搜索获取信息"""
    driver = None
    try:
        logger.info(f"开始从百度搜索关键词: {keyword}")
        
        # 设置浏览器
        driver = setup_driver()
        
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
        
        # 确保test目录存在
        os.makedirs('test', exist_ok=True)
        
        # 保存页面源码
        html_path = os.path.join('test', 'baidu_search_result.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"已保存HTML到: {html_path}")
        
        # 解析搜索结果
        results = []
        result_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class*="result c-container"]')
        logger.info(f"找到 {len(result_elements)} 条搜索结果")
        
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
                    description = ""
                
                # 获取来源
                try:
                    source_elem = element.find_element(By.CSS_SELECTOR, 'span[class*="c-showurl"]')
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
                    'description': description
                }
                
                logger.info(f"找到内容: {title}")
                results.append(result)
                
            except Exception as e:
                logger.warning(f"解析内容失败: {str(e)}")
                continue
        
        if not results:
            logger.warning("未找到任何搜索结果")
        
        # 保存结果到文件
        json_path = os.path.join('test', 'baidu_search_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存结果到: {json_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"百度搜索失败: {str(e)}", exc_info=True)
        return []
    finally:
        if driver:
            driver.quit()

def main():
    keyword = "星闪"
    results = search_baidu(keyword)
    
    if results:
        logger.info(f"成功获取 {len(results)} 条内容")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. 标题: {result['title']}")
            logger.info(f"   链接: {result['url']}")
            logger.info(f"   来源: {result['source']}")
            logger.info(f"   时间: {result['time']}")
            if result['description']:
                logger.info(f"   描述: {result['description']}")
    else:
        logger.warning("未获取到任何内容")

if __name__ == "__main__":
    main() 